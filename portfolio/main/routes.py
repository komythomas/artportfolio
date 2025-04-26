# portfolio/main/routes.py

from flask import render_template, abort, current_app, request 
from sqlalchemy import or_ 

from . import main_bp
from portfolio.models import Project, Page, Tag, SiteSetting, Item, Category
from portfolio import db 
from sqlalchemy.orm import joinedload


# --- Routes Publiques ---


@main_bp.route('/')
def home():
    """Affiche la page d'accueil."""
    
    return render_template('main/home.html') 

@main_bp.route('/gallery')
def gallery():
    page = request.args.get('page', 1, type=int) 
    per_page = current_app.config.get('ITEMS_PER_PAGE', 12) 

    projects_pagination = Project.query.filter(
        Project.status == 'published',
        or_(Project.display_in == 'gallery', Project.display_in == 'both')
    ).order_by(Project.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('main/gallery.html', 
                           projects_pagination=projects_pagination, 
                           page_title="Gallery",
                           body_class_extra='page-work-grid') 


@main_bp.route('/commissions')
def commissions():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 12) 

    commission_projects_pagination = Project.query.filter(
        Project.status == 'published',
        or_(Project.display_in == 'commissions', Project.display_in == 'both')
    ).order_by(Project.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    commissions_page_content = None
    try: 
        commissions_db_page = Page.query.filter_by(slug='commissions', is_visible=True).first()
        if commissions_db_page: commissions_page_content = commissions_db_page.content
    except Exception as e: current_app.logger.error(f"Error fetching 'commissions' page content: {e}")

    return render_template('main/commissions.html', 
                           projects_pagination=commission_projects_pagination, 
                           page_content=commissions_page_content,
                           page_title="Commissions",
                           body_class_extra='page-work-grid') 


# --- Route dédiée pour la page About (AVEC DEBUGGING) ---
@main_bp.route('/about')
def about():
    """Affiche la page 'About' dédiée."""
    current_app.logger.info("Attempting to access /about route.")
    
    page = Page.query.filter_by(slug='about', is_visible=True).first() 
    
    if page:
        
        current_app.logger.info(f"Page 'about' found and visible (ID: {page.id}). Rendering template.")
        return render_template('main/about.html', 
                               page=page, 
                               page_title=page.title)
    else:
        
        current_app.logger.warning("Query failed for Page with slug='about' AND is_visible=True.")
        page_by_slug_only = Page.query.filter_by(slug='about').first()
        if page_by_slug_only:
             
             current_app.logger.error(f"Page with slug 'about' FOUND (ID: {page_by_slug_only.id}), BUT it is NOT VISIBLE (is_visible={page_by_slug_only.is_visible}). Check admin '/admin/pages'.")
        else:
             
             current_app.logger.error("NO page found with slug 'about' in the database. Please create it in '/admin/pages'.")
        
        abort(404) 

# --- Route dédiée pour la page Contact (AVEC DEBUGGING) --- 
@main_bp.route('/contact')
def contact():
    """Affiche la page 'Contact' dédiée."""
    current_app.logger.info("Attempting to access /contact route.")

    page = Page.query.filter_by(slug='contact', is_visible=True).first() 
    
    if page:
        current_app.logger.info(f"Page 'contact' found and visible (ID: {page.id}). Rendering template.") 
        return render_template('main/contact.html', 
                               page=page, 
                               page_title=page.title)
    else:

        current_app.logger.warning("Query failed for Page with slug='contact' AND is_visible=True.") 
        page_by_slug_only = Page.query.filter_by(slug='contact').first() 
        if page_by_slug_only:
             
             current_app.logger.error(f"Page with slug 'contact' FOUND (ID: {page_by_slug_only.id}), BUT it is NOT VISIBLE (is_visible={page_by_slug_only.is_visible}). Check admin '/admin/pages'.")
        else:
             
             current_app.logger.error("NO page found with slug 'contact' in the database. Please create it in '/admin/pages'.")
        
        abort(404) 

# --- Route générique pour les AUTRES pages dynamiques ---
@main_bp.route('/pages/<slug>') 
def page_detail(slug):
    """Affiche une page dynamique générique par son slug."""
    current_app.logger.info(f"Attempting to access generic page /pages/{slug}")

    if slug in ['about', 'contact']:
        current_app.logger.warning(f"Access to /pages/{slug} denied, use dedicated route /{slug}.")
        abort(404) 
         
    page = Page.query.filter(
        Page.slug == slug,
        Page.is_visible == True
    ).first_or_404() 

    current_app.logger.info(f"Rendering generic page '{slug}' (ID: {page.id})")
    return render_template('main/page_detail.html', 
                           page=page, 
                           page_title=page.title)


# --- Route pour l'affichage détaillé d'un Projet ---
@main_bp.route('/projects/<slug>')
def project_detail(slug):
    project = Project.query.options(
        db.joinedload(Project.items),    
        db.joinedload(Project.tags),     
        db.joinedload(Project.categories)
    ).filter(
        Project.slug == slug,            
        Project.status == 'published'    
    ).first_or_404()                     

    return render_template('main/project_detail.html', 
                           project=project, 
                           page_title=project.title)


# --- Route pour l'archivage par Tag ---
@main_bp.route('/tags/<slug>')
def tag_archive(slug):
    projects_pagination = None
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    return render_template('main/tag_archive.html', 
                            tag=tag, 
                            projects_pagination=projects_pagination, 
                            page_title=f"Tag: {tag.name}"
                            )