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
from functools import wraps
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional # Ajouter Optional pour l'édition

class UserForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=64)]
    )
    password = PasswordField(
        'Password',
        validators=[
            Optional(),
            Length(min=8, message='Password must be at least 8 characters long.')
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            EqualTo('password', message='Passwords must match.')
        ]
    )
    is_admin = BooleanField('Is Administrator?')
    submit = SubmitField('Save User')

    def __init__(self, original_username=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    # --- Méthode Corrigée ---
    def validate_username(self, username): # 'username' est le champ WTForms
        # Si le nom d'utilisateur a changé (édition) ou si on crée un nouvel utilisateur
        if username.data != self.original_username:
            # Utiliser username.data pour obtenir la valeur du champ
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is already taken. Please choose a different one.')


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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False): # Vérifie l'attribut is_admin
            logger.warning(f"Unauthorized admin access attempt by user: {current_user.username if current_user.is_authenticated else 'Anonymous'}")
            flash("You do not have permission to access this page.", "danger")
            if not current_user.is_authenticated:
                return redirect(url_for('admin.login', next=request.url))
            else:
                return redirect(url_for('admin.dashboard')) 
        return f(*args, **kwargs)
    return decorated_function


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

        user = User.query.filter_by(username=username).first() 

        # Vérifier l'utilisateur ET le mot de passe
        if not user or not user.check_password(password):
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
@admin_bp.route('/') 
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


# --- Route pour la Gestion des Utilisateurs ---
@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    try:
        users = User.query.order_by(User.username).all()
    except Exception as e:
        logger.error(f"Error fetching users list: {e}", exc_info=True)
        flash("Could not retrieve the user list due to a database error.", "danger")
        users = []
    # Vérifiez que cette ligne utilise bien 'admin/users_list.html'
    return render_template('admin/user_list.html', users=users, page_title="Manage Users")

@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required 
def create_user():
    """Gère la création d'un nouvel utilisateur."""
    form = UserForm() 
    if form.validate_on_submit():
        try:
            new_user = User(
                username=form.username.data,
                is_admin=form.is_admin.data
            )
            new_user.set_password(form.password.data) 

            db.session.add(new_user)
            db.session.commit()
            logger.info(f"User '{new_user.username}' created successfully by '{current_user.username}'. Admin status: {new_user.is_admin}")
            flash(f"User '{new_user.username}' created successfully!", "success")
            return redirect(url_for('admin.list_users'))
        except Exception as e:
            db.session.rollback() 
            logger.error(f"Error creating user '{form.username.data}': {e}", exc_info=True)
            flash(f"An error occurred while creating the user: {e}", "danger")

    return render_template('admin/user_form.html', form=form, page_title="Create New User", form_action=url_for('admin.create_user'), is_edit=False)


@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required 
def edit_user(user_id):
    """Gère l'édition d'un utilisateur existant."""
    user_to_edit = db.session.get(User, user_id) 
    if not user_to_edit:
        flash(f"User with ID {user_id} not found.", "warning")
        return redirect(url_for('admin.list_users'))

    form = UserForm(original_username=user_to_edit.username)

    if form.validate_on_submit():
        try:
            user_to_edit.username = form.username.data
            user_to_edit.is_admin = form.is_admin.data

            if form.password.data:
                user_to_edit.set_password(form.password.data)
                flash(f"Password for user '{user_to_edit.username}' has been updated.", "info")

            db.session.commit()
            logger.info(f"User '{user_to_edit.username}' (ID: {user_id}) updated successfully by '{current_user.username}'.")
            flash(f"User '{user_to_edit.username}' updated successfully!", "success")
            return redirect(url_for('admin.list_users'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating user '{user_to_edit.username}': {e}", exc_info=True)
            flash(f"An error occurred while updating the user: {e}", "danger")

    elif request.method == 'GET':
        form.username.data = user_to_edit.username
        form.is_admin.data = user_to_edit.is_admin

    # Utilise le même template user_form.html, mais avec des données différentes
    return render_template('admin/user_form.html', form=form, page_title=f"Edit User: {user_to_edit.username}", user_id=user_id, form_action=url_for('admin.edit_user', user_id=user_id), is_edit=True)


@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required 
def delete_user(user_id):
    """Delete a user."""
    # Empêcher la suppression de soi-même
    if user_id == current_user.id:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for('admin.list_users'))

    user_to_delete = db.session.get(User, user_id)
    if not user_to_delete:
        flash(f"User with ID {user_id} not found.", "warning")
        return redirect(url_for('admin.list_users'))

    try:
        username_deleted = user_to_delete.username 
        db.session.delete(user_to_delete)
        db.session.commit()
        logger.info(f"User '{username_deleted}' (ID: {user_id}) deleted successfully by '{current_user.username}'.")
        flash(f"User '{username_deleted}' deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting user ID {user_id}: {e}", exc_info=True)
        flash(f"An error occurred while deleting the user: {e}", "danger")

    return redirect(url_for('admin.list_users'))


# --- FIN DU FICHIER ---