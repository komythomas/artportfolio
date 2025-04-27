# run.py 
import logging
from portfolio import create_app, db
from portfolio.models import User, Category
from dotenv import load_dotenv
import os
from flask_migrate import Migrate
from logging.handlers import RotatingFileHandler
import sys
from portfolio.utils import slugify

load_dotenv()

app = create_app()
migrate = Migrate(app, db)
config = app.config

# Configuration logging (production) - Garder tel quel pour le local
if not app.debug and not app.testing:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setLevel(logging.INFO)
    log_formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(log_formatter)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application startup in production mode.')


# --- Fonction pour créer l'utilisateur admin initial (MODIFIÉE) ---
def create_admin_user():
    """Crée l'utilisateur admin initial si non existant, via variables d'env."""
    admin_username = os.getenv('ADMIN_USERNAME')
    admin_password = os.getenv('ADMIN_PASSWORD')

    if not admin_username or not admin_password:
        print("Erreur: Variables d'environnement ADMIN_USERNAME et ADMIN_PASSWORD non définies.", file=sys.stderr)
        return

    try:
        with app.app_context():
            if not User.query.filter_by(username=admin_username).first():
                default_user = User(
                    username=admin_username,
                    is_admin=True  
                )
                default_user.set_password(admin_password)

                db.session.add(default_user)
                db.session.commit()
                app.logger.info(f"Admin user '{admin_username}' created successfully (Admin: True).")
                print(f"Admin user '{admin_username}' created successfully (Admin: True).")
            else:
                app.logger.info(f"Admin user '{admin_username}' already exists.")
    except Exception as e:
        app.logger.error(f"Error creating admin user '{admin_username}': {e}", exc_info=True)
        print(f"Erreur lors de la création de l'utilisateur admin '{admin_username}': {e}", file=sys.stderr)

# --- Fonction pour créer les catégories initiales (Inchangée) ---
def seed_initial_categories():
    """Crée les catégories de base si elles n'existent pas."""
    app.logger.info("Checking for initial categories...")
    initial_categories = ['Painting', 'Mural', 'Print', 'Digital Art', 'Sculpture', 'Installation', 'Other']
    try:
        with app.app_context():
            existing_slugs = {cat.slug for cat in Category.query.all()}
            added = False
            for name in initial_categories:
                slug = slugify(name)
                if slug not in existing_slugs:
                    new_cat = Category(name=name)
                    db.session.add(new_cat)
                    existing_slugs.add(slug)
                    added = True
                    app.logger.info(f"Category '{name}' marked for addition.")
            if added:
                db.session.commit()
                app.logger.info("Initial categories committed.")
            else:
                app.logger.info("All initial categories already exist.")
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error seeding initial categories: {e}", exc_info=True)


# --- Point d'entrée pour l'exécution (Inchangé) ---
if __name__ == '__main__':
    print(f"Debug mode from app.debug: {app.debug}")

    # Exécuter les fonctions de seeding dans le contexte de l'application
    with app.app_context():
        create_admin_user()
        seed_initial_categories()

    # Lancer le serveur de développement Flask (pour le local uniquement)
    app.run(debug=app.debug, host='0.0.0.0', port=5000)

