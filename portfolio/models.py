# portfolio/models.py
from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
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
    slug = Column(String(100), unique=True, nullable=False) 
    
    # Relation inverse pour accéder aux projets depuis une catégorie
    projects = relationship('Project', secondary=project_categories, back_populates='categories')

    def __init__(self, name, **kwargs):
        super(Category, self).__init__(name=name, **kwargs)
        if not self.slug: 
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
    __tablename__ = 'user' 

    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False, index=True) 
    password_hash = Column(String(256), nullable=False) 
    created_at = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False, nullable=False)

    def set_password(self, password):
        """Crée un hash sécurisé du mot de passe et le stocke."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Vérifie si le mot de passe fourni correspond au hash stocké."""
        return check_password_hash(self.password_hash, password)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Permet de définir le mot de passe via user.password = '...' """
        self.set_password(password)

    # 6. Mise à jour de la représentation pour inclure le statut admin
    def __repr__(self):
        return f'<User {self.username} (Admin: {self.is_admin})>'

class Page(db.Model):
    __tablename__ = 'page'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    content = Column(Text, nullable=True) 
    cover_image_path = Column(String(255), nullable=True)
    display_order = Column(Integer, default=0)
    is_visible = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_description = Column(String(255), nullable=True) 

    def __init__(self, title, content="", **kwargs):
        super(Page, self).__init__(title=title, content=content, **kwargs)
        if not self.slug: 
             self.slug = slugify(title)

    def __repr__(self):
        return f'<Page {self.title} ({self.slug})>'

class Item(db.Model):
    """Represents a visual element (image, video?) associated with a Project."""
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    file_path = Column(String(255), nullable=False) 
    alt_text = Column(String(255), nullable=True) 
    display_order = Column(Integer, default=0) 
    project_id = Column(Integer, ForeignKey('project.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    width = Column(Integer, nullable=True)       
    height = Column(Integer, nullable=True)      
    filesize = Column(Integer, nullable=True)    
    mime_type = Column(String(100), nullable=True) 
    
    def __repr__(self):
        # Ajouter les dimensions si elles existent
        dims = f"{self.width}x{self.height}" if self.width and self.height else "Unknown Dims"
        return f'<Item {self.id} ({dims}) for Project {self.project_id}>'


class SiteSetting(db.Model):
    __tablename__ = 'site_setting'
    id = Column(Integer, primary_key=True)
    key = Column(String(50), unique=True, nullable=False) 
    value = Column(Text, nullable=True) 

    def __repr__(self):
        return f'<SiteSetting {self.key}={self.value[:20]}>'

class Project(db.Model):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    feature_image_path = Column(String(255), nullable=True) 
    
    # Metadata
    techniques = Column(String(255), nullable=True)
    year = Column(String(4), nullable=True)
    collection = Column(String(255), nullable=True) # collection/série
    status = Column(String(50), default='draft', nullable=False) # 'published', 'draft', 'archived'
    availability = Column(String(50), default='not_for_sale', nullable=False) # 'available', 'sold', 'not_for_sale', 'commissioned'
    display_in = Column(String(50), default='gallery', nullable=False) # 'gallery', 'commissions', 'both', 'none'

    # NFT Fields (nullable)
    is_nft = Column(Boolean, default=False, nullable=False)
    blockchain_network = Column(String(100), nullable=True)
    contract_address = Column(String(255), nullable=True)
    token_id = Column(String(255), nullable=True)
    creator_wallet = Column(String(255), nullable=True)
    marketplace_url = Column(String(512), nullable=True) # OpenSea, Foundation, etc.

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
    categories = relationship('Category', secondary=project_categories, back_populates='projects') 
    
    @property
    def display_image_path(self):
        """
        Retourne le chemin de l'image principale définie si elle existe,
        sinon retourne le chemin de la première image associée (Item),
        sinon retourne None.
        """
        if self.feature_image_path:
            return self.feature_image_path
        
        if self.items: 
             try:
                 first_item = self.items[0] 
                 return first_item.file_path
             except IndexError:
                  return None
        
        # Si pas d'image principale ET pas d'items
        return None
    

    def __init__(self, title, **kwargs):
        super(Project, self).__init__(title=title, **kwargs)
        if not self.slug: 
            self.slug = slugify(title)
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
        if not self.slug: 
            self.slug = slugify(name)

    def __repr__(self):
        return f'<Tag {self.name}>'