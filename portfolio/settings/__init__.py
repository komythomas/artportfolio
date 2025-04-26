from flask import Blueprint

# Définition du Blueprint 'settings'
settings_bp = Blueprint(
    'settings', 
    __name__, 
    template_folder='templates'
    # Pas besoin de static folder ici a priori
)

# Importer les routes et formulaires après la création du blueprint
from . import routes, forms