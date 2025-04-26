# portfolio/__init__.py
import os
import math 
from flask import Flask, request, render_template 
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate 
import logging
from .config import Config 
from datetime import datetime
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'admin.login' 
login_manager.login_message = "Please log in to access this page." 
login_manager.login_message_category = 'info' 

migrate = Migrate() 

# --- Filtre Jinja Personnalisé ---
def filesizeformat(value, binary=False):
    """Formats the value like a 'human-readable' file size (i.e. 13 kB, 4.1 MB, 102 Bytes, etc)."""
    try:
        bytes_val = float(value)
    except (TypeError, ValueError, AttributeError) as e:
         logging.warning(f"Could not format value '{value}' as filesize: {e}") 
         return "N/A" 

    base = 1024 if binary else 1000
    prefixes = [
        (base**5, 'P'), (base**4, 'T'), (base**3, 'G'),
        (base**2, 'M'), (base**1, 'k'), (base**0, 'B')
    ]
    if bytes_val == 1: return '1 Byte'
    if bytes_val < base: return f'{int(bytes_val)} Bytes'
    for factor, suffix in prefixes:
        if bytes_val >= factor:
            break
    return f'{bytes_val / factor:.1f} {suffix}B' 

# --- Fonction pour enregistrer les gestionnaires d'erreurs ---
def register_error_handlers(app):
    """Enregistre les gestionnaires pour les erreurs communes."""
    logger = app.logger 
    
    @app.errorhandler(404)
    def page_not_found(e):
        logger.warning(f"Page not found (404): {request.path}")
        try: from .models import SiteSetting; settings = {s.key: s.value for s in SiteSetting.query.all()}
        except: settings = {}
        return render_template('404.html', site_settings=settings), 404 

    @app.errorhandler(500)
    def internal_server_error(e):
         logger.error(f"Internal Server Error (500): {e}", exc_info=True)
         try: 
             db.session.rollback()
             logger.info("Rolled back database session after 500 error.")
         except Exception as db_err:
             logger.error(f"Error during rollback attempt on 500 error: {db_err}")

         try: from .models import SiteSetting; settings = {s.key: s.value for s in SiteSetting.query.all()}
         except: settings = {}
         return render_template('500.html', site_settings=settings),


# --- Application Factory ---
def create_app(config_class=Config):
    """Crée et configure l'instance de l'application Flask."""
    
    app = Flask(__name__, instance_relative_config=True) 
    app.config.from_object(config_class)
    
    app.jinja_env.add_extension('jinja2.ext.do') 
    app.jinja_env.filters['filesizeformat'] = filesizeformat 

    # print("-" * 40)
    # print(f"SECRET KEY LOADED: {app.secret_key}") 
    print(f"CSRF ENABLED IN CONFIG: {app.config.get('WTF_CSRF_ENABLED')}") 
    # print(f"--- DB URI FOR FLASK COMMAND: {app.config.get('SQLALCHEMY_DATABASE_URI')} ---")
    # print("-" * 40)
    print(f"--- VERCEL BLOB TOKEN from Config: {app.config.get('VERCEL_BLOB_RW_TOKEN')} ---")

    app.logger.info(f"Configuration loaded.")

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db) 
    app.logger.info("Flask extensions initialized.")

    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder: 
        if not os.path.exists(upload_folder):
            try:
                os.makedirs(upload_folder)
                app.logger.info(f"Upload folder created at: {upload_folder}")
            except OSError as e:
                app.logger.error(f"Failed to create upload folder {upload_folder}: {e}", exc_info=True)
    else:
        app.logger.warning("UPLOAD_FOLDER not set in configuration. File uploads might fail.")
    
    
    from portfolio.context_processors import inject_current_images
    app.context_processor(inject_current_images)

    # --- Context Processor ---
    @app.context_processor
    def inject_global_template_variables():
        from .models import SiteSetting, Page 
        site_settings_dict = {}
        nav_pages = []
        try:
            settings_list = SiteSetting.query.all() 
            site_settings_dict = {s.key: s.value for s in settings_list}
            site_settings_dict['logo'] = site_settings_dict.get('logo_path')
            nav_pages = Page.query.filter_by(is_visible=True).order_by(Page.display_order, Page.title).all()
        except Exception as e:
             app.logger.error(f"Error fetching data for context processor (DB might not be ready): {e}", exc_info=True)
             site_settings_dict = {}
             nav_pages = []
        return dict(
            site_settings=site_settings_dict, 
            current_year=datetime.utcnow().year,
            navigation_pages=nav_pages 
        )

    from .main import main_bp 
    from .admin import admin_bp 
    from .settings import settings_bp
    from .pages import pages_bp
    from .projects import projects_bp
    app.register_blueprint(main_bp) 
    app.register_blueprint(admin_bp, url_prefix='/admin') 
    app.register_blueprint(settings_bp, url_prefix='/admin/settings') 
    app.register_blueprint(pages_bp, url_prefix='/admin/pages') 
    app.register_blueprint(projects_bp, url_prefix='/admin/projects') 
    app.logger.info("Blueprints registered successfully.")

    register_error_handlers(app) 

    return app

