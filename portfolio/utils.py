# portfolio/utils.py
import re
import os
import logging
import io 
from werkzeug.utils import secure_filename
from flask import current_app 
from PIL import Image, ExifTags 
from vercel_blob import put as vercel_put, delete as vercel_del


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'ico', 'svg'} 
logger = logging.getLogger(__name__)


# --- Fonctions Helpers ---
def slugify(s):
    """Génère un slug 'propre' à partir d'une chaîne."""
    if not s: return "n-a" 
    s = str(s).lower().strip() 
    s = re.sub(r'[^\w\s-]', '', s) 
    s = re.sub(r'[\s_-]+', '-', s) 
    s = re.sub(r'^-+|-+$', '', s) 
    return s if s else "n-a" 


def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_upload_folder():
    """Récupère le chemin absolu d'un dossier d'upload local défini dans la config (fallback si nécessaire)."""
    # Note: Utiliser avec prudence car Vercel n'a pas de FS persistant simple.
    folder = current_app.config.get('UPLOAD_FOLDER') # Récupère UPLOAD_FOLDER depuis config.py
    if not folder:
        logger.error("Local UPLOAD_FOLDER not set in Flask config! Falling back to instance path.")
        folder = os.path.join(current_app.instance_path, 'local_uploads') # Chemin fallback différent
        if not os.path.exists(folder):
            try: 
                os.makedirs(folder) 
                logger.info(f"Created fallback local upload folder: {folder}")
            except OSError as e: 
                logger.error(f"Failed to create fallback local upload folder {folder}: {e}")
                # En cas d'échec ici, la sauvegarde locale échouera probablement aussi
    return folder


def get_relative_path(filename):
    """Retourne un chemin relatif LOCAL hypothétique 'uploads/filename'."""
    # Attention: Ce n'est PAS le chemin Vercel Blob.
    return f'uploads/{filename}' 


def get_absolute_path(relative_path):
    """Construit le chemin absolu LOCAL sur le serveur."""
    # Attention: Ne fonctionne que pour les fichiers stockés localement.
    if not relative_path or not relative_path.startswith('uploads/'):
        logger.warning(f"Cannot get absolute path for invalid relative path: {relative_path}")
        return None
    filename = os.path.basename(relative_path) 
    return os.path.join(get_upload_folder(), filename) # Utilise le dossier local

# --- Fonction save_file ---

# --- Fonction save_file corrigée ---
def save_file(file, prefix="file"):
    """
    Sauvegarde un fichier uploadé sur Vercel Blob, optimise (si image), 
    extrait les métadonnées et retourne un dictionnaire Vercel Blob enrichi ou None.
    """
    if not file or not file.filename:
        logger.warning("save_file called with no file or filename.")
        return None 
        
    original_filename = file.filename
    if not allowed_file(original_filename): 
        allowed_ext_str = ', '.join(ALLOWED_EXTENSIONS) 
        logger.warning(f"Invalid file type uploaded: {original_filename}. Allowed: {allowed_ext_str}")
        return None 

    # Extraire Métadonnées Originales
    original_mime_type = file.content_type 
    original_filesize = -1
    try: 
        original_pos = file.stream.tell(); file.stream.seek(0, os.SEEK_END)
        original_filesize = file.stream.tell(); file.stream.seek(original_pos) 
    except: pass 
    
    filename = secure_filename(f"{prefix}_{original_filename}")
    blob_pathname = f"uploads/{filename}" 

    processed_data = None
    img_width, img_height = None, None
    is_optimizable_image = filename.rsplit('.', 1)[-1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'tiff'}

    try:
        file.stream.seek(0) 
        if is_optimizable_image:
            img = None
            try:
                img = Image.open(file.stream)
                
                # Rotation EXIF 
                try:
                    pass
                except Exception: pass 
                
                img_width, img_height = img.size 
                
                if img.mode in ('RGBA', 'P'): 
                     pass
                elif img.mode != 'RGB': img = img.convert('RGB')

                img_width_before, img_height_before = img.size 
                max_width = current_app.config.get('MAX_IMAGE_WIDTH', 1920)
                max_height = current_app.config.get('MAX_IMAGE_HEIGHT', 1920)
                if img_width_before > max_width or img_height_before > max_height:
                    img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS) 
                    img_width, img_height = img.size 
                else:
                    img_width, img_height = img_width_before, img_height_before
                
                # --- LOGIQUE FORMAT/KWARGS RÉINTÉGRÉE ---
                save_kwargs = {}
                original_extension = filename.rsplit('.', 1)[-1].lower()
                img_format = 'JPEG' 
                if original_extension == 'png': 
                    img_format = 'PNG'; save_kwargs['optimize'] = True
                elif original_extension == 'gif': 
                    img_format = 'GIF'; save_kwargs['optimize'] = True
                elif original_extension == 'webp': 
                    img_format = 'WEBP'; save_kwargs['quality'] = current_app.config.get('IMAGE_QUALITY', 85)
                else: # jpg, jpeg, bmp, tiff 
                    img_format = 'JPEG'
                    save_kwargs['quality'] = current_app.config.get('IMAGE_QUALITY', 85)
                    save_kwargs['optimize'] = True
                    save_kwargs['progressive'] = True
                # --- FIN LOGIQUE FORMAT/KWARGS ---

                # Sauvegarde en mémoire buffer
                buffer = io.BytesIO()
                img.save(buffer, format=img_format, **save_kwargs) # Utilise img_format et save_kwargs définis
                buffer.seek(0)
                processed_data = buffer.getvalue()  # Fix: get the bytes to upload
                logger.info(f"Image processed in memory: {filename} (Format: {img_format})")

            except Exception as pillow_e:
                logger.error(f"Error processing image '{filename}' with Pillow: {pillow_e}. Uploading original.", exc_info=True)
                file.stream.seek(0) 
                processed_data = file.stream.read()
                img_width, img_height = None, None 
            finally:
                 if img: img.close()
        else:
            file.stream.seek(0)
            processed_data = file.stream.read()
            logger.info(f"Using original stream for non-image: {filename}")

        # --- Upload sur Vercel Blob ---
        blob_token = current_app.config.get('VERCEL_BLOB_RW_TOKEN')
        if not blob_token:
             logger.error("CRITICAL: VERCEL_BLOB_RW_TOKEN is not configured in Flask app!")
             return None 
             
        logger.info(f"Uploading '{blob_pathname}' to Vercel Blob...")
        blob_result = vercel_put(
            blob_pathname, processed_data,
            options={'token': blob_token}
        )
        logger.info(f"Vercel Blob upload successful. URL: {blob_result['url']}")
        
        blob_result['width'] = img_width
        blob_result['height'] = img_height
        blob_result['filesize'] = original_filesize 
        blob_result['mime_type'] = original_mime_type 
        
        return blob_result 

    except Exception as e: 
        logger.error(f"Error during Vercel Blob upload or file processing for '{filename}': {e}", exc_info=True)
        return None


# --- Fonction delete_file  ---
def delete_file(blob_url):
    if not blob_url: return False
    token = current_app.config.get('VERCEL_BLOB_RW_TOKEN')
    if not token: logger.error("VERCEL_BLOB_RW_TOKEN not configured."); return False
    try:
        logger.info(f"Attempting to delete blob URL: {blob_url}")
        vercel_del([blob_url], options={'token': token}) 
        logger.info(f"Blob delete command sent successfully for: {blob_url}")
        return True
    except Exception as e: 
         if 'blob_not_found' in str(e).lower() or '404' in str(e): return True # Considérer comme succès
         else: logger.error(f"Vercel Blob deletion error for URL '{blob_url}': {e}", exc_info=True); return False

