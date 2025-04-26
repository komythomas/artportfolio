from flask import Blueprint

# Définition du Blueprint 'projects'
projects_bp = Blueprint(
    'projects', 
    __name__, 
    template_folder='templates'
)

# Importer routes et formulaires
from . import routes, forms