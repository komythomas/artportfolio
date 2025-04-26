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

# Load environment variables from .env file in the project root
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'admin.login'
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = 'info'

migrate = Migrate()

# --- Custom Jinja Filter ---
def filesizeformat(value, binary=False):
    """Formats the value like a 'human-readable' file size (i.e. 13 kB, 4.1 MB, 102 Bytes, etc)."""
    try:
        bytes_val = float(value)
    except (TypeError, ValueError, AttributeError) as e:
         # Use standard logging
         logging.warning(f"Could not format value '{value}' as filesize: {e}")
         return "N/A" # Return N/A for invalid input

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
    # Format to one decimal place and add the suffix
    return f'{bytes_val / factor:.1f} {suffix}B'

# --- Error Handler Registration ---
def register_error_handlers(app):
    """Registers handlers for common HTTP errors."""
    logger = app.logger # Use Flask's app logger

    @app.errorhandler(404)
    def page_not_found(e):
        logger.warning(f"Page not found (404): {request.path}")
        # Attempt to fetch site settings for the error page, handle potential DB errors
        try:
            from .models import SiteSetting
            settings = {s.key: s.value for s in SiteSetting.query.all()}
        except Exception as db_err:
            logger.error(f"Error fetching SiteSettings for 404 page: {db_err}")
            settings = {} # Provide empty settings if DB fails
        return render_template('404.html', site_settings=settings), 404

    @app.errorhandler(500)
    def internal_server_error(e):
         logger.error(f"Internal Server Error (500): {e}", exc_info=True) # Log the full exception
         # Attempt to rollback the session in case of DB errors during the request
         try:
             db.session.rollback()
             logger.info("Rolled back database session after 500 error.")
         except Exception as db_err:
             logger.error(f"Error during rollback attempt on 500 error: {db_err}")

         # Attempt to fetch site settings for the error page
         try:
             from .models import SiteSetting
             settings = {s.key: s.value for s in SiteSetting.query.all()}
         except Exception as db_err:
             logger.error(f"Error fetching SiteSettings for 500 page: {db_err}")
             settings = {}
         # Return the 500 error page template
         return render_template('500.html', site_settings=settings), 500


# --- Application Factory ---
def create_app(config_class=Config):
    """Creates and configures the Flask application instance."""

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Add Jinja extensions and filters
    app.jinja_env.add_extension('jinja2.ext.do')
    app.jinja_env.filters['filesizeformat'] = filesizeformat

    # Use Flask logger instead of print for configuration info
    app.logger.info("Configuration loaded.")
    app.logger.debug(f"CSRF ENABLED IN CONFIG: {app.config.get('WTF_CSRF_ENABLED')}")
    app.logger.debug(f"VERCEL BLOB TOKEN from Config: {'*' * 5 + app.config.get('VERCEL_BLOB_RW_TOKEN', '')[-4:] if app.config.get('VERCEL_BLOB_RW_TOKEN') else 'Not Set'}") # Avoid logging full token

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    app.logger.info("Flask extensions initialized.")


    # Register context processors
    from portfolio.context_processors import inject_current_images
    app.context_processor(inject_current_images)

    @app.context_processor
    def inject_global_template_variables():
        """Injects global variables into templates."""
        from .models import SiteSetting, Page # Import models inside to avoid circular imports
        site_settings_dict = {}
        nav_pages = []
        try:
            # Fetch settings and visible pages for navigation
            settings_list = SiteSetting.query.all()
            site_settings_dict = {s.key: s.value for s in settings_list}
            # Ensure 'logo' key exists, using 'logo_path' if available
            site_settings_dict['logo'] = site_settings_dict.get('logo_path')
            nav_pages = Page.query.filter_by(is_visible=True).order_by(Page.display_order, Page.title).all()
        except Exception as e:
             # Log error if DB isn't ready (e.g., during initial setup/migrations)
             app.logger.error(f"Error fetching data for context processor (DB might not be ready): {e}", exc_info=True)
             site_settings_dict = {} # Default to empty dict
             nav_pages = [] # Default to empty list
        # Return variables to be available in all templates
        return dict(
            site_settings=site_settings_dict,
            current_year=datetime.utcnow().year,
            navigation_pages=nav_pages
        )

    # Register Blueprints
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

    # Register error handlers
    register_error_handlers(app)

    return app