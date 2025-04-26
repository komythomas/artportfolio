# portfolio/projects/routes.py
from flask import (render_template, request, redirect, url_for, flash, abort, 
                   jsonify, current_app) 
from flask_login import login_required
import logging
import json 
from sqlalchemy.orm import joinedload 
from sqlalchemy import func, or_ # Assurer que func et or_ sont importés
from portfolio.utils import slugify, save_file, delete_file, get_absolute_path, allowed_file 
from . import projects_bp
from .forms import ProjectForm
from portfolio.models import Project, Item, Tag, Category 
from portfolio import db 
from portfolio.utils import slugify, save_file, delete_file # get_absolute_path n'est plus utilisé ici

logger = logging.getLogger(__name__)

def process_categories(categories_string):
    # ... (code inchangé) ...
    category_objects = []
    if categories_string:
        category_names = {name.strip() for name in categories_string.split(',') if name.strip()}
        category_objects = Category.query.filter(Category.name.in_(category_names)).all()
        found_names = {cat.name for cat in category_objects}
        missing_names = category_names - found_names
        if missing_names:
             logger.warning(f"Unknown categories submitted and ignored: {', '.join(missing_names)}")
    return category_objects 

def process_tags(tags_string):
    # ... (code inchangé) ...
    tag_objects = []
    if tags_string:
        tag_names = [name.strip() for name in tags_string.split(',') if name.strip()]
        processed_slugs = set() 
        for name in tag_names:
            tag_slug = slugify(name)
            if tag_slug and tag_slug not in processed_slugs: 
                tag = Tag.query.filter_by(slug=tag_slug).first()
                if not tag:
                    tag = Tag(name=name) 
                    db.session.add(tag)
                    logger.info(f"New tag '{name}' marked for addition.")
                tag_objects.append(tag)
                processed_slugs.add(tag_slug)
    return tag_objects

@projects_bp.route('/')
@login_required
def list_projects():
    """Displays the list of all projects."""
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('admin/projects/list.html', 
                           projects=projects, 
                           page_title="Project Management")

@projects_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_project():
    """Handles the creation of a new project."""
    if request.method == 'POST':
        form = ProjectForm(request.form) 
    else: 
        form = ProjectForm()
    
    all_tags = Tag.query.order_by(Tag.name).all()
    all_tags_json = json.dumps([tag.name for tag in all_tags])
    all_categories = Category.query.order_by(Category.name).all()
    all_categories_json = json.dumps([cat.name for cat in all_categories])

    if form.validate_on_submit(): 
        project_slug = form.slug.data if form.slug.data else slugify(form.title.data)
        
        if Project.query.filter(Project.slug == project_slug).first():
            flash(f"The slug '{project_slug}' already exists. Please provide one manually or change the title.", "danger")
            return render_template('admin/projects/form.html', form=form, page_title="New Project", project=None, all_tags_json=all_tags_json, all_categories_json=all_categories_json) 

        # Handle feature image upload
        feature_image_url = None # Stockera l'URL Vercel Blob
        feature_image_file = form.feature_image.data 
        if feature_image_file and feature_image_file.filename != '':
            logger.info(f"Attempting to save feature image: {feature_image_file.filename}")
            file_info = save_file(feature_image_file, prefix=f"project_{project_slug}")
            if file_info and file_info.get('url'):
                feature_image_url = file_info['url'] # Récupérer l'URL publique
            else: 
                # save_file a échoué (et a dû flasher/logger une erreur)
                logger.error("save_file failed for feature image during project creation.")
                return render_template('admin/projects/form.html', form=form, page_title="New Project", project=None, all_tags_json=all_tags_json, all_categories_json=all_categories_json)
        else:
            logger.info("No feature image submitted for new project.")

        # Process relationships
        tags = process_tags(form.tags.data)
        categories = process_categories(form.categories.data) 

        # Create Project object
        new_project = Project(
            title=form.title.data, slug=project_slug, description=form.description.data,
            feature_image_path = feature_image_url, # Stocker l'URL Vercel Blob (ou None)
            techniques=form.techniques.data, year=form.year.data, collection=form.collection.data, 
            status=form.status.data, availability=form.availability.data, display_in=form.display_in.data,
            is_nft=form.is_nft.data, blockchain_network=form.blockchain_network.data,
            contract_address=form.contract_address.data, token_id=form.token_id.data,
            creator_wallet=form.creator_wallet.data, marketplace_url=form.marketplace_url.data,
            tags=tags, categories=categories 
        )        
        
        try:
            db.session.add(new_project)
            db.session.commit() 
            logger.info(f"Project created: {new_project.title} (ID: {new_project.id})")
            flash('Project created successfully! Add associated images now.', 'success')
            return redirect(url_for('projects.edit_project', id=new_project.id)) 
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating project: {e}", exc_info=True)
            flash(f"Server error while creating project: {e}", 'danger')
            # Cleanup uploaded file (using URL) if DB commit failed
            if feature_image_url: delete_file(feature_image_url) 
            return render_template('admin/projects/form.html', form=form, page_title="New Project", project=None, all_tags_json=all_tags_json, all_categories_json=all_categories_json)
            
    elif request.method == 'POST' and form.errors: 
        logger.warning(f"Project form validation errors on create: {form.errors}")
        flash("The form contains errors. Please check the fields.", "danger")

    # Render for GET request or after validation errors on POST
    return render_template('admin/projects/form.html', 
                           form=form, page_title="New Project", project=None, 
                           all_tags_json=all_tags_json, all_categories_json=all_categories_json) 

@projects_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    """Handles editing an existing project."""
    project = Project.query.options(
        joinedload(Project.items), joinedload(Project.tags), joinedload(Project.categories)
    ).get_or_404(id)
    
    form = ProjectForm(formdata=request.form if request.method == 'POST' else None, obj=project, editing_project_id=id)
                       
    if request.method == 'GET':
        form.tags.data = ', '.join([tag.name for tag in project.tags])
        form.categories.data = ', '.join([cat.name for cat in project.categories])

    all_tags = Tag.query.order_by(Tag.name).all()
    all_tags_json = json.dumps([tag.name for tag in all_tags]) 
    all_categories = Category.query.order_by(Category.name).all()
    all_categories_json = json.dumps([cat.name for cat in all_categories])

    if form.validate_on_submit():
        submitted_tags_str = form.tags.data 
        submitted_categories_str = form.categories.data

        # Manual update of simple fields
        project.title = form.title.data
        project.slug = form.slug.data if form.slug.data else slugify(form.title.data)
        project.description = form.description.data
        project.techniques = form.techniques.data
        project.year = form.year.data
        project.collection = form.collection.data
        project.status = form.status.data
        project.availability = form.availability.data
        project.display_in = form.display_in.data
        project.is_nft = form.is_nft.data
        project.blockchain_network = form.blockchain_network.data
        project.contract_address = form.contract_address.data
        project.token_id = form.token_id.data 
        project.creator_wallet = form.creator_wallet.data
        project.marketplace_url = form.marketplace_url.data
        
        # Handle feature image update
        old_feature_image_url = project.feature_image_path # Stocke l'ancienne URL (ou None)
        new_feature_image_url = old_feature_image_url     # Initialise avec l'ancienne
        feature_image_file = form.feature_image.data 

        if feature_image_file and feature_image_file.filename != '':
            logger.info(f"Attempting to save new feature image: {feature_image_file.filename}")
            file_info = save_file(feature_image_file, prefix=f"project_{project.slug}") 
            if file_info and file_info.get('url'): 
                new_feature_image_url = file_info['url'] # Mettre à jour avec la nouvelle URL
                logger.info(f"New feature image URL set to: {new_feature_image_url}")
            else: # Handle save_file error
                logger.error("save_file failed for new feature image during edit.")
                form.tags.data = submitted_tags_str 
                form.categories.data = submitted_categories_str
                return render_template('admin/projects/form.html', form=form, project=project, 
                                       page_title=f"Edit: {project.title}", all_tags_json=all_tags_json, 
                                       all_categories_json=all_categories_json)
        
        # Assign the final URL (new or old)
        project.feature_image_path = new_feature_image_url 

        # Assign relationships
        project.tags = process_tags(submitted_tags_str) 
        project.categories = process_categories(submitted_categories_str) 

        try:
            db.session.commit() 
            # Delete old image *after* successful commit if URL changed AND old URL existed
            if new_feature_image_url != old_feature_image_url and old_feature_image_url:
                 logger.info(f"Deleting old feature image blob: {old_feature_image_url}")
                 delete_file(old_feature_image_url) # Passer l'URL à supprimer
                 
            flash('Project updated successfully!', 'success')
            return redirect(url_for('projects.edit_project', id=project.id)) 
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating project ID {id}: {e}", exc_info=True)
            flash(f'Error updating project: {e}', 'danger')
            # Clean up newly uploaded file if commit failed and URL changed
            if new_feature_image_url != old_feature_image_url and new_feature_image_url: 
                delete_file(new_feature_image_url)
            # Repopulate form before re-rendering
            form.tags.data = submitted_tags_str
            form.categories.data = submitted_categories_str
            return render_template('admin/projects/form.html', form=form, project=project, 
                                   page_title=f"Edit: {project.title}", all_tags_json=all_tags_json, 
                                   all_categories_json=all_categories_json)
            
    elif request.method == 'POST' and form.errors: 
        logger.warning(f"Project form validation errors on edit (ID: {id}): {form.errors}")
        flash("The form contains errors. Please check the fields.", "danger")
        form.tags.data = request.form.get('tags', '') 
        form.categories.data = request.form.get('categories', '') 

    # Render template for GET or POST with errors
    return render_template('admin/projects/form.html', 
                           form=form, project=project, page_title=f"Edit: {project.title}",
                           all_tags_json=all_tags_json, all_categories_json=all_categories_json) 

@projects_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_project(id):
    """Deletes a project and its associated files from Vercel Blob."""
    # Utiliser joinedload pour charger les items avant de potentiellement supprimer le projet
    project = Project.query.options(joinedload(Project.items)).get_or_404(id)
    project_title = project.title
    urls_to_delete = []
    if project.feature_image_path: urls_to_delete.append(project.feature_image_path)
    for item in project.items:
        if item.file_path: urls_to_delete.append(item.file_path)
            
    try:
        # Supprimer l'entrée projet de la BDD (cascade devrait supprimer les items liés)
        db.session.delete(project) 
        db.session.commit()
        logger.info(f"Project DB record deleted: {project_title} (ID: {id})")
        
        # Si le commit DB réussit, tenter de supprimer les fichiers du Blob Storage
        if urls_to_delete:
             logger.info(f"Attempting to delete {len(urls_to_delete)} blobs for project {id}")
             delete_file(urls_to_delete) # delete_file dans utils gère la liste d'URLs
             # Note: on ne re-rollback pas si la suppression Blob échoue, mais on log/flash l'erreur
        
        flash(f'Project "{project_title}" deleted successfully.', 'success') 
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting project ID {id} from DB: {e}", exc_info=True)
        flash(f'Database error deleting project "{project_title}": {e}', 'danger') 

    return redirect(url_for('projects.list_projects'))

# === Item (Visuals) Management ===
@projects_bp.route('/<int:id>/items/add', methods=['POST'])
@login_required
def add_project_items(id):
    """Adds one or more images (Items) to an existing project using Vercel Blob."""
    project = Project.query.get_or_404(id)
    uploaded_files = request.files.getlist('project_items') 
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if not uploaded_files or uploaded_files[0].filename == '':
        message = "No file selected."
        if is_ajax: return jsonify(success=False, error=message), 400
        else: flash(message, "warning"); return redirect(url_for('projects.edit_project', id=id))

    newly_added_items_db = [] 
    newly_added_items_info = [] # Pour le retour JSON/logique cleanup
    error_messages = []
    
    for file in uploaded_files:
        if file and allowed_file(file.filename): 
            item_prefix = f"item_project_{project.id}"
            file_info = save_file(file, prefix=item_prefix) # Retourne le dict Vercel Blob + nos métas
            
            if file_info and file_info.get('url'):
                # Créer l'objet Item avec l'URL et les métadonnées
                max_order = db.session.query(func.max(Item.display_order)).filter(Item.project_id == id).scalar()
                new_order = (max_order or 0) + 1
                new_item = Item(
                    # Stocker l'URL publique retournée par Vercel Blob
                    file_path=file_info['url'], 
                    project_id=project.id, display_order=new_order,
                    width=file_info.get('width'), height=file_info.get('height'),
                    filesize=file_info.get('filesize'), mime_type=file_info.get('mime_type')
                )
                db.session.add(new_item)
                newly_added_items_db.append(new_item) # Pour le commit/flush
                newly_added_items_info.append(file_info) # Pour le retour JSON et cleanup
            else: 
                 error_messages.append(f"Error processing/saving '{file.filename}'. Check logs.")
        elif file:
             error_messages.append(f"File type not allowed for '{file.filename}'.")
        
    if newly_added_items_db:
        try:
            db.session.flush() # Obtenir les IDs pour les items ajoutés
            # Préparer les données JSON pour le retour AJAX
            final_item_data = []
            for item, info in zip(newly_added_items_db, newly_added_items_info):
                 final_item_data.append({
                    'id': item.id, # ID réel après flush
                    # 'file_path_url': item.file_path, # C'est déjà l'URL !
                    'url': item.file_path, # Nom plus clair
                    'display_order': item.display_order,
                    'alt_text': item.alt_text or '',
                    'width': item.width, 'height': item.height, 
                    'filesize': item.filesize, 'mime_type': item.mime_type
                 })
            
            db.session.commit() 
            logger.info(f"{len(newly_added_items_db)} items added to project ID {id}")

            if is_ajax:
                 return jsonify(success=True, new_items=final_item_data, errors=error_messages)
            else:
                 flash(f"{len(final_item_data)} image(s) added.", "success")
                 if error_messages: flash("Some image errors occurred: " + "; ".join(error_messages), "warning")
                 return redirect(url_for('projects.edit_project', id=id))
                 
        except Exception as e:
            db.session.rollback() 
            logger.error(f"Error committing new items for project ID {id}: {e}", exc_info=True)
            error_msg = f"Database error adding images: {e}"
            # Cleanup: Supprimer les fichiers déjà uploadés sur Vercel Blob si commit échoue
            urls_to_delete = [info['url'] for info in newly_added_items_info if info and 'url' in info]
            if urls_to_delete:
                logger.info(f"Rolling back: deleting {len(urls_to_delete)} blobs due to DB error.")
                delete_file(urls_to_delete) # delete_file gère la liste
                
            if is_ajax: return jsonify(success=False, error=error_msg, errors=error_messages), 500
            else: flash(error_msg, "danger"); return redirect(url_for('projects.edit_project', id=id))
    else:
        error_msg = "No images were added successfully."
        if error_messages: error_msg += " Errors: " + "; ".join(error_messages)
        if is_ajax: return jsonify(success=False, error=error_msg, errors=error_messages), 400
        else: flash(error_msg, "warning"); return redirect(url_for('projects.edit_project', id=id))

@projects_bp.route('/items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_project_item(item_id):
    """Deletes a specific image (Item) from DB and Vercel Blob."""
    item = Item.query.get_or_404(item_id)
    project_id = item.project_id 
    blob_url_to_delete = item.file_path # Récupérer l'URL stockée

    # Supprimer l'entrée DB d'abord (ou après ?) - Après pour garder l'URL si Blob échoue?
    # Essayons après.
    
    try:
        # Supprimer l'objet Item de la DB
        db.session.delete(item)
        db.session.commit()
        logger.info(f"Item record deleted from DB: ID {item_id}")
        
        # Si le commit DB réussit, tenter de supprimer le fichier du Blob Storage
        if blob_url_to_delete:
            delete_file(blob_url_to_delete) # Utiliser l'helper qui gère les erreurs Blob
            # Le flash de succès/erreur de delete_file sera affiché
        
        flash("Image record deleted successfully.", "success") # Confirmer suppression DB
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting item ID {item_id} from database: {e}", exc_info=True)
        flash(f"Database error while deleting image record: {e}", "danger")

    return redirect(url_for('projects.edit_project', id=project_id))

@projects_bp.route('/<int:id>/items/update_details', methods=['POST'])
@login_required
def update_project_items_details(id):
    """Updates display order and alt text for a project's items."""
    # Cette route ne gère pas les fichiers, donc elle est OK telle quelle
    project = Project.query.get_or_404(id)
    items_updated = 0
    try:
        i = 0
        while f'item_id_{i}' in request.form:
            item_id = request.form.get(f'item_id_{i}', type=int)
            display_order = request.form.get(f'display_order_{i}', 0, type=int)
            alt_text = request.form.get(f'alt_text_{i}', '')
            if item_id:
                item = Item.query.filter_by(id=item_id, project_id=id).first() 
                if item and (item.display_order != display_order or item.alt_text != alt_text):
                     item.display_order = display_order
                     item.alt_text = alt_text
                     items_updated += 1
                     logger.debug(f"Updating item ID {item_id}: order={display_order}, alt='{alt_text}'")
            i += 1
        if items_updated > 0:
            db.session.commit()
            logger.info(f"{items_updated} item details updated for project ID {id}")
            flash(f"{items_updated} image details updated.", "success")
        else:
             flash("No changes detected in image details.", "info")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating item details for project ID {id}: {e}", exc_info=True)
        flash(f"Error updating item details: {e}", "danger")
    return redirect(url_for('projects.edit_project', id=id))

# --- FIN DU FICHIER ---