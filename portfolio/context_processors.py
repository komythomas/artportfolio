
from flask import current_app
from portfolio.models import SiteSetting

def get_current_images():
    settings = SiteSetting.query.all()
    settings_dict = {s.key: s.value for s in settings}
    return {
        'logo': settings_dict.get('logo_path'),
        'favicon': settings_dict.get('favicon_path'),
        'home_background': settings_dict.get('home_bg_path'),
        'artist_portrait': settings_dict.get('artist_portrait_path')
    }

def inject_current_images():
    return {'current_images': get_current_images()}

# Dans ton app/__init__.py ou là où tu crées l'app Flask :
# from portfolio.context_processors import inject_current_images
# app.context_processor(inject_current_images)
