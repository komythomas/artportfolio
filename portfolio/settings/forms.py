# portfolio/settings/forms.py

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
# Importer les types de champs nécessaires
from wtforms import StringField, TextAreaField, SubmitField, URLField 
# Importer les validateurs
from wtforms.validators import Optional, Length, Email, URL 
# Importer la constante pour les extensions
from portfolio.utils import ALLOWED_EXTENSIONS 

# Étendre les extensions pour le favicon si besoin (.ico, .svg...)
# Note : Pillow pourrait ne pas gérer .ico pour l'optimisation.
FAVICON_EXTENSIONS = ALLOWED_EXTENSIONS.union({'ico', 'svg'}) 

class SettingsForm(FlaskForm):
    # --- General ---
    site_name = StringField('Site Name', 
                            validators=[Optional(), Length(max=100)],
                            render_kw={"placeholder": "e.g., HSS FineArt"})
    
    # --- Branding / Images ---
    logo = FileField('Site Logo', validators=[
        Optional(), 
        FileAllowed(ALLOWED_EXTENSIONS, 'Images only!')
    ])
    favicon = FileField('Favicon (.ico, .png, .svg)', validators=[
        Optional(), 
        FileAllowed(FAVICON_EXTENSIONS, 'Favicon files only!')
    ]) # Champ Favicon ajouté
    
    # --- Homepage ---
    home_background = FileField('Homepage Background Image', validators=[
        Optional(), 
        FileAllowed(ALLOWED_EXTENSIONS, 'Images only!')
    ])
    
    # --- About Page (si image spécifique) ---
    artist_portrait = FileField('Artist Portrait (for About page)', validators=[
        Optional(), 
        FileAllowed(ALLOWED_EXTENSIONS, 'Images only!')
    ])

    # --- Contact & Social ---
    contact_email = StringField('Contact Email', 
                                validators=[Optional(), Email()],
                                render_kw={"placeholder": "e.g., contact@example.com"})
    contact_phone = StringField('Contact Phone (Optional)', 
                                validators=[Optional(), Length(max=30)])
    contact_address = TextAreaField('Contact Address (Optional)', 
                                    validators=[Optional(), Length(max=200)], 
                                    render_kw={"rows": 3})
    # Social Links
    instagram_url = URLField('Instagram URL', validators=[Optional(), URL()])
    linkedin_url = URLField('LinkedIn URL', validators=[Optional(), URL()])
    facebook_url = URLField('Facebook URL', validators=[Optional(), URL()])
    # Ajoutez d'autres réseaux si besoin (twitter_url, etc.)

    # --- Footer ---
    copyright_text = StringField('Copyright Text', 
                                validators=[Optional(), Length(max=150)],
                                render_kw={"placeholder": f"e.g., © {{{{ current_year }}}} Your Name"}) 
                                # Note: Jinja ne sera pas interprété dans le placeholder

    # --- SEO & Analytics ---
    meta_description = TextAreaField('Default Meta Description (SEO)', 
                                     validators=[Optional(), Length(max=160)], 
                                     render_kw={"rows": 3, "placeholder": "Default site description for search engines (150-160 chars)"})
    analytics_script = TextAreaField('Analytics Script (Optional)', 
                                      validators=[Optional()], 
                                      render_kw={"rows": 5, "placeholder": "Paste your full <script>...</script> tag here"},
                                      description="E.g., Google Analytics tracking code. Will be inserted before closing </head> tag.")

    submit = SubmitField('Save Settings')