# portfolio/projects/forms.py

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, SelectField, URLField, IntegerField # IntegerField ajouté pour display_order
from wtforms.validators import DataRequired, Length, Optional, URL, ValidationError
# Importer les modèles nécessaires pour la validation
from portfolio.models import Project, Tag # Category n'est plus nécessaire ici
# Importer la constante depuis utils
from portfolio.utils import ALLOWED_EXTENSIONS 

# --- Choices for SelectFields (in English) ---
STATUS_CHOICES = [('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived'),]
AVAILABILITY_CHOICES = [('available', 'Available'), ('not_availaible', 'Not availaible'), ('on_request', 'On Request'), ('not_for_sale', 'Not for Sale')]
DISPLAY_IN_CHOICES = [('gallery', 'Gallery'), ('commissions', 'Commissions'), ('both', 'Gallery & Commissions'), ('none', 'Nowhere (Private)')]

class ProjectForm(FlaskForm):
    """Form to create and edit Projects."""
    
    # --- Main Fields ---
    title = StringField(
        'Project Title', 
        validators=[DataRequired("This field is required."), Length(max=255)], 
        render_kw={"placeholder": "Enter a clear and concise title"}
    )                       
    slug = StringField(
        'Slug (URL)', 
        validators=[Optional(), Length(max=255)],
        description="Unique URL identifier (e.g., my-great-project). Leave blank to auto-generate from title.", 
        render_kw={"placeholder": "auto-generated-from-title"}
    )                     
    description = TextAreaField(
        'Description', 
        description="Detailed description of the project, process, available editions (physical, prints, NFTs), etc. Uses rich text formatting.",
        render_kw={"rows": 9, "id": "projectDescriptionEditor"} # ID for TinyMCE
    ) 
    feature_image = FileField(
        'Feature Image (Optional)', 
        description="Upload a specific main image. If empty the first 'Associated Visual' (ordered by 'Order') will be used.", 
        validators=[Optional(), FileAllowed(ALLOWED_EXTENSIONS, 'Allowed image formats: png, jpg, jpeg, gif, webp')]
    )
    
    # --- Metadata ---
    categories = StringField( # Correct: StringField pour Tagify
        'Categories', 
        description="Select or type the project categories. New categories are created automatically.", 
        validators=[Optional()],
        render_kw={"placeholder": "Select or type categories...", "id": "projectCategoriesInput"} # ID pour Tagify
    )                   
    techniques = StringField(
        'Techniques / Medium', 
        validators=[Optional(), Length(max=255)], 
        render_kw={"placeholder": "e.g., Oil on canvas, Digital print, Mixed media, etc."}
    )                        
    year = StringField( # Garder StringField pour flexibilité (ex: "circa 2020") mais valider Length
        'Year', 
        validators=[Optional(), Length(max=50)], # Augmenter un peu max length
        render_kw={"placeholder": "e.g., 2024 or circa 2020"}
    )                       
    collection = StringField(
        'Collection / Series (Optional)', 
        validators=[Optional(), Length(max=255)], 
        render_kw={"placeholder": "e.g., Abstract Dreams Series, Personal Collection, etc."}
    ) 
    
    # --- Management & Display ---
    status = SelectField(
        'Status', 
        choices=STATUS_CHOICES, 
        default='draft', 
        validators=[DataRequired("Status is required.")]
    )
    availability = SelectField(
        'Availability (Overall)', 
        choices=AVAILABILITY_CHOICES, 
        default='not_for_sale', 
        validators=[DataRequired("Availability is required.")],
        description="Overall status. Specify edition details in the description."
    )
    display_in = SelectField(
        'Display In', 
        choices=DISPLAY_IN_CHOICES, 
        default='gallery', 
        validators=[DataRequired("Display location is required.")],
        description="Where should this project primarily appear?"
    )

    # --- Tags ---
    tags = StringField( 
        'Tags', 
        description="Enter relevant keywords separated by commas. New tags are created automatically.",
        validators=[Optional()],
        render_kw={"placeholder": "tag1, tag2, ...", "id": "projectTagsInput"} 
    )

    # --- NFT Fields ---
    is_nft = BooleanField('Is this associated with an NFT?') 
    blockchain_network = StringField(
        'Blockchain', 
        validators=[Optional(), Length(max=100)], 
        render_kw={"placeholder": "e.g., Ethereum, Polygon, Tezos"}
    ) 
    contract_address = StringField(
        'Contract Address', 
        validators=[Optional(), Length(max=255)], 
        render_kw={"placeholder": "e.g., 0x..."}
    ) 
    token_id = StringField( 
        'Token ID / Range / Info', 
        validators=[Optional(), Length(max=255)], 
        render_kw={"placeholder": "e.g., 123 or 1-100"}
    ) 
    creator_wallet = StringField(
        'Creator / Owner Wallet', 
        validators=[Optional(), Length(max=255)], 
        render_kw={"placeholder": "e.g., 0x... or ENS name"}
    ) 
    marketplace_url = URLField(
        'Marketplace URL (Optional)', 
        validators=[Optional(), URL(), Length(max=512)], 
        render_kw={"placeholder": "https://opensea.io/..."}
    ) 

    # --- Submit Button ---
    submit = SubmitField('Save Project') 
    
    # --- Special Methods (Corrected Previously) ---
    def __init__(self, formdata=None, obj=None, editing_project_id=None, **kwargs):
        super(ProjectForm, self).__init__(formdata=formdata, obj=obj, **kwargs) 
        self.editing_project_id = editing_project_id 
        
    def validate_slug(self, field):
        if field.data: 
            project_id_to_exclude = self.editing_project_id 
            query = Project.query.filter(Project.slug == field.data) 
            if project_id_to_exclude: 
                query = query.filter(Project.id != project_id_to_exclude)
            existing_project = query.first()
            if existing_project:
                raise ValidationError('This slug is already used by another project.')

    def validate(self, extra_validators=None):
        initial_validation = super(ProjectForm, self).validate(extra_validators=extra_validators) 
        if not initial_validation: return False
        if self.is_nft.data:
            errors = False
            required_fields = [ ('blockchain_network', self.blockchain_network), ('contract_address', self.contract_address), ('token_id', self.token_id), ('creator_wallet', self.creator_wallet) ]
            for field_name, field_obj in required_fields:
                if not field_obj.data:
                    # Attacher l'erreur au champ spécifique
                    getattr(self, field_name).errors.append('This field is required if "Is this an NFT?" is checked.') 
                    errors = True
            if errors: return False 
        return True