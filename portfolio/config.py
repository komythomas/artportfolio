import os
from dotenv import load_dotenv

load_dotenv() 

class Config:

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-replace-in-env') # OK


    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///default_dev.db') # OK (Fallback SQLite)
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 1800,
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
    }
    VERCEL_BLOB_RW_TOKEN = os.getenv('VERCEL_BLOB_RW_TOKEN', 'dev-vercel-blob-token') 
    
    SQLALCHEMY_POOL_TIMEOUT = 30 
    SQLALCHEMY_POOL_RECYCLE = 1800 
    SQLALCHEMY_POOL_SIZE = 10 
    SQLALCHEMY_MAX_OVERFLOW = 20 
    SQLALCHEMY_POOL_PRE_PING = True 
    SQLALCHEMY_MAX_CONNECTIONS = 20 
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't') 
    APP_ROOT = os.path.abspath(os.path.dirname(__file__)) 
    UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')
    ITEMS_PER_PAGE = 9 
    MEDIA_PER_PAGE = 24 
    MAX_IMAGE_WIDTH = 1920
    MAX_IMAGE_HEIGHT = 1920
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216')) 
    IMAGE_QUALITY = 100
    
