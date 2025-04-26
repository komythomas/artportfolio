from flask import Blueprint

# Définition du Blueprint 'admin'
admin_bp = Blueprint(
    'admin', 
    __name__, 
    template_folder='templates',
)

from . import routes