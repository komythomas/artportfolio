from flask import request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
# Importer le modèle Page pour vérifier l'unicité du slug
from portfolio.models import Page
from portfolio.utils import ALLOWED_EXTENSIONS # Utiliser les extensions définies dans utils

class PageForm(FlaskForm):
    title = StringField('Page Title', validators=[DataRequired(), Length(max=255)])
    
    # Le slug peut être optionnel, ou on peut ajouter une validation d'unicité
    slug = StringField('Slug (URL)', 
                       validators=[Optional(), Length(max=255)], 
                       description="Leave blank to auto-generate from title.")
                       
    content = TextAreaField('Main Content', render_kw={"rows": 20, "id": "pageContentEditor"}) 
    
    cover_image = FileField('Cover Image', validators=[
        Optional(),
        FileAllowed(ALLOWED_EXTENSIONS, 'Only images are allowed!')
    ])
    
    display_order = IntegerField('Display Order', default=0, validators=[Optional()])
    
    is_visible = BooleanField('Visible Publicly?', default=True)
    
    meta_description = TextAreaField('Meta Description (SEO)', 
                                     validators=[Optional(), Length(max=255)], # Valider longueur max
                                     render_kw={"rows": 3, "placeholder": "Optimal length: 150-160 characters"},
                                     description="Brief summary for search engines.")
    
    submit = SubmitField('Save Page')

    # Validation personnalisée pour l'unicité du slug (si fourni)
    def validate_slug(self, field):
        if field.data: # Valider seulement si un slug est entré manuellement
            # Récupérer l'id de la page en cours d'édition (si disponible)
            page_id = request.view_args.get('id') if request and request.view_args else None
            
            query = Page.query.filter_by(slug=field.data)
            if page_id: # Exclure la page actuelle de la vérification lors de l'édition
                query = query.filter(Page.id != page_id)
                
            existing_page = query.first()
            if existing_page:
                raise ValidationError('This slug is already in use by another page.')