# portfolio/settings/routes.py

from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
import logging

from . import settings_bp
from .forms import SettingsForm 
from portfolio.models import SiteSetting 
from portfolio import db 
from portfolio.utils import save_file, delete_file, get_absolute_path, allowed_file 

logger = logging.getLogger(__name__)

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def manage_settings():
    form = SettingsForm() 
    
    if form.validate_on_submit(): 
        # --- Bloc POST Succès ---
        logger.info("Settings form submitted and validated.")
        settings_to_update = {} 
        text_fields = [
            'site_name', 'meta_description', 'contact_email', 'contact_phone', 
            'contact_address', 'instagram_url', 'linkedin_url', 'facebook_url', 
            'copyright_text', 'analytics_script' 
        ] 
        file_fields = {
            'logo': 'logo_path', 'home_background': 'home_bg_path', 
            'artist_portrait': 'artist_portrait_path', 'favicon': 'favicon_path'
        }
        
        # Traitement champs texte
        for field_name in text_fields:
            if hasattr(form, field_name):
                 settings_to_update[field_name] = getattr(form, field_name).data

        # Traitement fichiers
        for form_field_name, setting_key in file_fields.items():
            if hasattr(form, form_field_name):
                form_field = getattr(form, form_field_name)
                if form_field.data and hasattr(form_field.data, 'filename') and form_field.data.filename != '':
                    file_info = save_file(form_field.data, prefix=setting_key) 
                    if file_info and file_info.get('url'):
                        old_setting = SiteSetting.query.filter_by(key=setting_key).first()
                        if old_setting and old_setting.value:
                             delete_file(old_setting.value) 
                        settings_to_update[setting_key] = file_info['url'] 
                    elif file_info is None: 
                         return redirect(url_for('settings.manage_settings')) 

        # Mise à jour BDD
        try:
            updated_keys = []
            created_keys = []
            for key, value in settings_to_update.items():
                 setting = SiteSetting.query.filter_by(key=key).first()
                 if setting:
                     if setting.value != value: setting.value = value; updated_keys.append(key)
                 else:
                     setting = SiteSetting(key=key, value=value or ''); db.session.add(setting); created_keys.append(key)
            
            if updated_keys or created_keys:
                db.session.commit()
                logger.info(f"Site settings updated/created: {updated_keys + created_keys}")
                flash('Site settings updated successfully!', 'success')
            else:
                 flash('No changes detected in settings.', 'info')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error updating settings: {e}", exc_info=True)
            flash(f"Database error updating settings: {e}", 'danger')

        return redirect(url_for('settings.manage_settings')) 

    
    logger.debug("Loading current settings for GET request or POST error.")
    settings = SiteSetting.query.all()
    settings_dict = {s.key: s.value for s in settings}

    if request.method == 'GET':
        text_fields_keys = [
            'site_name', 'meta_description', 'contact_email', 'contact_phone', 
            'contact_address', 'instagram_url', 'linkedin_url', 'facebook_url', 
            'copyright_text', 'analytics_script'
        ]
        for key in text_fields_keys:
             if hasattr(form, key):
                 getattr(form, key).data = settings_dict.get(key, '') 
        logger.debug("Form populated with current settings for GET request.")
    elif form.errors: 
         logger.warning(f"Settings form validation errors: {form.errors}")
         flash("The form contains errors. Please check the fields.", "danger")

    current_images = {
        'logo': settings_dict.get('logo_path'), 
        'favicon': settings_dict.get('favicon_path'), 
        'home_background': settings_dict.get('home_bg_path'), 
        'artist_portrait': settings_dict.get('artist_portrait_path') 
    }

    return render_template('admin/settings/form.html', 
                           page_title="Site Settings", 
                           form=form,
                           current_images=current_images) 

    
# --- NOUVELLE ROUTE POUR SUPPRIMER UNE IMAGE DE PARAMÈTRE ---
@settings_bp.route('/delete_image/<setting_key>', methods=['POST'])
@login_required
def delete_setting_image(setting_key):
    """Supprime une image associée à une clé de paramètre spécifique."""
    
    # Clés autorisées pour la suppression d'images (sécurité)
    allowed_image_keys = ['logo_path', 'favicon_path', 'home_bg_path', 'artist_portrait_path']
    if setting_key not in allowed_image_keys:
        flash(f"Invalid setting key specified for deletion.", "danger")
        logger.warning(f"Attempted deletion for invalid setting key: {setting_key}")
        abort(400) # Bad Request

    logger.info(f"Attempting to delete image for setting key: {setting_key}")
    setting = SiteSetting.query.filter_by(key=setting_key).first()

    if setting and setting.value:
        image_relative_path = setting.value
        # Utiliser notre helper pour supprimer le fichier physique
        file_deleted = delete_file(image_relative_path) 
        
        if file_deleted:
            try:
                # Mettre la valeur à None ou vide dans la BDD
                setting.value = None 
                db.session.commit()
                flash(f"Image for '{setting_key.replace('_path','').replace('_',' ').title()}' deleted successfully.", "success")
                logger.info(f"Setting value for '{setting_key}' cleared after file deletion.")
            except Exception as e:
                 db.session.rollback()
                 logger.error(f"Error clearing setting value for '{setting_key}' after file deletion: {e}", exc_info=True)
                 # Le fichier a été supprimé mais pas la référence DB ! Que faire ?
                 # On pourrait essayer de le remettre ? Trop complexe. On informe.
                 flash(f"Image file deleted, but couldn't update database setting for '{setting_key}': {e}", "danger")
        else:
            # delete_file a déjà flashé une erreur s'il y en a eu une
            logger.warning(f"File deletion failed or file not found for setting '{setting_key}' with path '{image_relative_path}'.")
            # Optionnel : essayer quand même de vider la BDD si le fichier n'existe pas ?
            # try:
            #     setting.value = None
            #     db.session.commit()
            #     flash(f"Image file path cleared for setting '{setting_key}' (file was missing).", "warning")
            # except: ...

    elif setting:
        flash(f"No image was set for '{setting_key.replace('_path','').replace('_',' ').title()}'.", "info")
    else:
        flash(f"Setting key '{setting_key}' not found.", "warning")

    # Toujours rediriger vers la page des paramètres
    return redirect(url_for('settings.manage_settings'))