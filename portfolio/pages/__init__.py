from flask import Blueprint

# Définition du Blueprint 'pages'
pages_bp = Blueprint(
    'pages', 
    __name__, 
    template_folder='templates'
)

# Importer routes et formulaires
from . import routes, forms