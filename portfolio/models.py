# portfolio/models.py
from . import db
from flask_login import UserMixin
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import re

# Helper function pour générer un slug
def slugify(s):
    s = s.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s

# Table d'association pour la relation Many-to-Many entre Project et Tag
project_tags = Table('project_tags', db.Model.metadata,
    Column('project_id', Integer, ForeignKey('project.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True)
)

# --- NOUVEAU : Table d'association Projet <-> Catégorie ---
project_categories = Table('project_categories', db.Model.metadata,
    Column('project_id', Integer, ForeignKey('project.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', Integer, ForeignKey('category.id', ondelete='CASCADE'), primary_key=True)
)

# --- NOUVEAU : Modèle Category ---
class Category(db.Model):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False) # Pour des URLs de filtrage éventuelles
    
    # Relation inverse pour accéder aux projets depuis une catégorie
    projects = relationship('Project', secondary=project_categories, back_populates='categories')

    def __init__(self, name, **kwargs):
        super(Category, self).__init__(name=name, **kwargs)
        if not self.slug: # Générer le slug automatiquement
            # Assurez-vous que la fonction slugify est importable ici ou définissez-la
            try:
                 from .utils import slugify 
                 self.slug = slugify(name)
            except ImportError:
                 # Fallback simple si utils n'est pas là (ne devrait pas arriver)
                 self.slug = name.lower().replace(' ', '-')


    def __repr__(self):
        return f'<Category {self.name}>'
    
    
class User(db.Model, UserMixin):
    __tablename__ = 'user' # Explicit table name is good practice
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class Page(db.Model):
    __tablename__ = 'page'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    content = Column(Text, nullable=True) # Peut être vide initialement
    cover_image_path = Column(String(255), nullable=True)
    display_order = Column(Integer, default=0)
    is_visible = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_description = Column(String(255), nullable=True) # Limite ~160 chars pour SEO, 255 est sûr pour DB

    def __init__(self, title, content="", **kwargs):
        super(Page, self).__init__(title=title, content=content, **kwargs)
        if not self.slug: # Générer le slug automatiquement si non fourni
             self.slug = slugify(title)

    def __repr__(self):
        return f'<Page {self.title} ({self.slug})>'

class Item(db.Model):
    """Represents a visual element (image, video?) associated with a Project."""
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    file_path = Column(String(255), nullable=False) # Path relatif dans 'static/uploads/'
    alt_text = Column(String(255), nullable=True) # Pour l'accessibilité et SEO
    display_order = Column(Integer, default=0) # Ordre d'affichage dans un projet
    project_id = Column(Integer, ForeignKey('project.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    width = Column(Integer, nullable=True)       # Largeur en pixels
    height = Column(Integer, nullable=True)      # Hauteur en pixels
    filesize = Column(Integer, nullable=True)    # Taille en octets (bytes)
    mime_type = Column(String(100), nullable=True) # Type MIME (ex: 'image/jpeg')
    
    def __repr__(self):
        # Ajouter les dimensions si elles existent
        dims = f"{self.width}x{self.height}" if self.width and self.height else "Unknown Dims"
        return f'<Item {self.id} ({dims}) for Project {self.project_id}>'


class SiteSetting(db.Model):
    __tablename__ = 'site_setting'
    id = Column(Integer, primary_key=True)
    key = Column(String(50), unique=True, nullable=False) # Ex: 'site_name', 'logo_path', 'home_bg_path'
    value = Column(Text, nullable=True) # Utiliser Text pour plus de flexibilité (ex: meta description)

    def __repr__(self):
        return f'<SiteSetting {self.key}={self.value[:20]}>'

class Project(db.Model):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    feature_image_path = Column(String(255), nullable=True) # Image principale du projet
    
    # Metadata
    techniques = Column(String(255), nullable=True)
    year = Column(String(4), nullable=True)
    collection = Column(String(255), nullable=True) # Si partie d'une collection/série
    status = Column(String(50), default='draft', nullable=False) # 'published', 'draft', 'archived'
    availability = Column(String(50), default='not_for_sale', nullable=False) # 'available', 'sold', 'not_for_sale', 'on_request'
    display_in = Column(String(50), default='gallery', nullable=False) # 'gallery', 'commissions', 'both', 'none'

    # NFT Fields (nullable)
    is_nft = Column(Boolean, default=False, nullable=False)
    blockchain_network = Column(String(100), nullable=True)
    contract_address = Column(String(255), nullable=True)
    token_id = Column(String(255), nullable=True)
    creator_wallet = Column(String(255), nullable=True)
    marketplace_url = Column(String(512), nullable=True) # Lien vers OpenSea, Foundation, etc.

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    items = relationship('Item', 
                         backref='project', 
                         cascade="all, delete-orphan", 
                         passive_deletes=True, 
                         order_by='Item.display_order, Item.id', 
                         lazy='select' )
    tags = relationship('Tag', secondary=project_tags, back_populates='projects')
    categories = relationship('Category', secondary=project_categories, back_populates='projects') # lazy='dynamic' peut être utile si beaucoup de catégories
    
    @property
    def display_image_path(self):
        """
        Retourne le chemin de l'image principale définie si elle existe,
        sinon retourne le chemin de la première image associée (Item),
        sinon retourne None.
        """
        if self.feature_image_path:
            # Priorité à l'image principale explicitement définie
            return self.feature_image_path
        
        # Si pas d'image principale, chercher la première Item associée
        # Utiliser la relation triée. Accéder à self.items peut déclencher une requête si lazy='select'.
        if self.items: # Vérifie si la liste (ou la query si dynamic) n'est pas vide
             # self.items[0] fonctionnerait si lazy='joined' ou si déjà chargé.
             # Pour lazy='select', cela charge tous les items. Moins optimal.
             # Une requête ciblée est préférable si performance critique, mais essayons comme ça d'abord.
             try:
                 first_item = self.items[0] # Prend le premier item selon l'order_by de la relation
                 return first_item.file_path
             except IndexError:
                  # Ne devrait pas arriver si self.items est vrai, mais sécurité
                  return None
        
        # Si pas d'image principale ET pas d'items
        return None
    

    def __init__(self, title, **kwargs):
        super(Project, self).__init__(title=title, **kwargs)
        if not self.slug: # Générer le slug automatiquement
            self.slug = slugify(title)
            # Gérer l'unicité du slug (ajouter un suffixe si nécessaire) - logique à affiner potentiellement
            # base_slug = self.slug
            # counter = 1
            # while Project.query.filter_by(slug=self.slug).first():
            #     self.slug = f"{base_slug}-{counter}"
            #     counter += 1
            
    def __repr__(self):
        return f'<Project {self.title} ({self.slug})>'

class Tag(db.Model):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    
    projects = relationship('Project', secondary=project_tags, back_populates='tags')

    def __init__(self, name, **kwargs):
        super(Tag, self).__init__(name=name, **kwargs)
        if not self.slug: # Générer le slug automatiquement
            self.slug = slugify(name)

    def __repr__(self):
        return f'<Tag {self.name}>'