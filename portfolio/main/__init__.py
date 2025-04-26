from flask import Blueprint

# Définition du Blueprint 'main'
main_bp = Blueprint(
    'main', 
    __name__, 
    template_folder='templates',
    static_folder='static', # Si vous avez des CSS/JS spécifiques au front
    static_url_path='/main/static' 
)

# Importer les routes après la création du blueprint
from . import routes