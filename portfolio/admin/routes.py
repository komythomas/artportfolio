# portfolio/admin/routes.py
import os
from flask import render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
import logging
from sqlalchemy import func, or_ 
from sqlalchemy.orm import joinedload
from . import admin_bp 
from portfolio.models import User, Project, Page, Item, Category, Tag, SiteSetting 
from portfolio import db, login_manager 
from portfolio.utils import delete_file 

logger = logging.getLogger(__name__)


# --- Configuration Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id)) 


@login_manager.unauthorized_handler
def unauthorized():
    """Gère les accès non autorisés."""
    # Message flash traduit
    flash("Please log in to access this page.", "warning") 
    return redirect(url_for('admin.login', next=request.endpoint)) # Passer la page demandée


# --- Routes d'Authentification ---
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Gère la connexion de l'utilisateur admin."""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        # Utiliser first() est correct ici
        user = User.query.filter_by(username=username).first() 

        # Vérifier l'utilisateur ET le mot de passe
        if not user or not check_password_hash(user.password, password):
            # Message flash traduit
            flash('Incorrect username or password.', 'danger') 
            logger.warning(f"Failed login attempt for user: {username}")
            return render_template('admin/login.html', page_title="Admin Login")

        login_user(user, remember=remember)
        logger.info(f"User {username} logged in successfully")
        
        # Rediriger vers 'next' ou dashboard
        next_page = request.args.get('next')
        # Sécurité : S'assurer que next_page est une URL interne (à améliorer si besoin)
        if next_page and not next_page.startswith('/'):
             next_page = url_for('admin.dashboard') 
             
        return redirect(next_page or url_for('admin.dashboard'))

    # Afficher le formulaire de login pour GET
    return render_template('admin/login.html', page_title="Admin Login")


@admin_bp.route('/logout')
@login_required 
def logout():
    """Gère la déconnexion."""
    logger.info(f"User {current_user.username} logged out")
    logout_user()
    # Message flash traduit
    flash('You have been successfully logged out.', 'success') 
    return redirect(url_for('admin.login')) 


# --- Routes Principales Admin ---
@admin_bp.route('/dashboard')
@admin_bp.route('/') # Faire pointer /admin vers le dashboard
@login_required
def dashboard():
    """Affiche le tableau de bord principal de l'admin avec des statistiques et listes."""
    logger.info(f"User {current_user.username} accessing dashboard")
    
    stats = { # Initialiser avec des valeurs par défaut claires
        'projects_total': 0, 'projects_published': 0, 'projects_draft': 0, 'projects_archived': 0,
        'pages_total': 0, 'pages_visible': 0, 'pages_hidden': 0,
        'items_total': 0, 'tags_total': 0, 'categories_total': 0,
        'items_storage_bytes': 0, 'items_missing_alt': 0   
    }
    recent_projects = []
    recent_pages = []
    draft_projects = []
    hidden_pages = []

    try:
        # Requêtes optimisées avec query(Model.id).count()
        stats['projects_total'] = db.session.query(Project.id).count()
        stats['projects_published'] = db.session.query(Project.id).filter_by(status='published').count()
        stats['projects_draft'] = db.session.query(Project.id).filter_by(status='draft').count()
        stats['projects_archived'] = db.session.query(Project.id).filter_by(status='archived').count()
        
        stats['pages_total'] = db.session.query(Page.id).count()
        stats['pages_visible'] = db.session.query(Page.id).filter_by(is_visible=True).count()
        stats['pages_hidden'] = db.session.query(Page.id).filter_by(is_visible=False).count()

        stats['items_total'] = db.session.query(Item.id).count()
        stats['tags_total'] = db.session.query(Tag.id).count()
        stats['categories_total'] = db.session.query(Category.id).count()
        
        total_size = db.session.query(func.sum(Item.filesize)).scalar() 
        stats['items_storage_bytes'] = total_size if total_size is not None else 0
        
        stats['items_missing_alt'] = db.session.query(Item.id).filter(or_(Item.alt_text == None, Item.alt_text == '')).count()

        # Contenu Récent
        recent_projects = Project.query.order_by(Project.updated_at.desc()).limit(5).all()
        recent_pages = Page.query.order_by(Page.updated_at.desc()).limit(5).all()
        
        # Contenu nécessitant attention
        draft_projects = Project.query.filter_by(status='draft').order_by(Project.updated_at.desc()).limit(5).all()
        hidden_pages = Page.query.filter_by(is_visible=False).order_by(Page.updated_at.desc()).limit(5).all()

    except Exception as e:
        logger.error(f"Error fetching data for dashboard: {e}", exc_info=True)
        flash("Could not retrieve some dashboard statistics due to a database error.", "warning")

    return render_template('admin/dashboard.html', 
                           page_title="Admin Dashboard",
                           stats=stats, 
                           recent_projects=recent_projects,
                           recent_pages=recent_pages,
                           draft_projects=draft_projects,
                           hidden_pages=hidden_pages)

   
# --- Route pour la Bibliothèque Média ---
@admin_bp.route('/media')
@login_required
def media_library():
    """Displays a paginated grid of uploaded Item images."""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('MEDIA_PER_PAGE', 24) 

    # Query pour les Items avec projet préchargé
    items_pagination = Item.query.options(
        joinedload(Item.project) 
    ).order_by(
        Item.id.desc() 
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('admin/media_library.html', 
                           items_pagination=items_pagination, 
                           total_items=items_pagination.total,
                           page_title="Media Library")


@admin_bp.route('/media/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_media_item(item_id):
    """Deletes a specific Item and its file from the media library context."""
    item = Item.query.get_or_404(item_id)
    item_path = item.file_path 
    project_id = item.project_id 
    
    # Essayer de supprimer le fichier physique
    file_deleted = delete_file(item.file_path)
    
    if not file_deleted:
         # delete_file a déjà flashé un message si le fichier n'a pas été trouvé
         # On peut choisir de continuer pour supprimer l'entrée DB ou d'arrêter
         logger.warning(f"Could not delete file '{item_path}' but proceeding to delete DB record.")
         # flash(f"Could not delete the file '{os.path.basename(item_path)}', but removed the database entry.", "warning") # Optionnel

    try:
        db.session.delete(item)
        db.session.commit()
        logger.info(f"Item deleted from DB: ID {item_id} (Path: {item_path}, Project: {project_id})")
        flash(f"Image '{os.path.basename(item_path)}' deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting item ID {item_id} from database: {e}", exc_info=True)
        flash(f"Database error while deleting image record: {e}", "danger")

    # Rediriger vers la page de la médiathèque (potentiellement la même page si on passe l'arg page)
    return redirect(url_for('admin.media_library', page=request.args.get('page', 1, type=int)))

# --- FIN DU FICHIER ---