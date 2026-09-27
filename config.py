import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'petcare-secret-key-mca-project-2026-super-secure'
    
    # Database Configuration (MySQL with fallback to SQLite for easy local execution)
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'password')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3306')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'petcare_db')
    
    # Check if MySQL preference or sqlite default
    USE_MYSQL = os.environ.get('USE_MYSQL', 'False').lower() in ['true', '1', 't']
    
    if USE_MYSQL:
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    else:
        # Fallback to local SQLite database in root folder
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            f"sqlite:///{os.path.join(BASE_DIR, 'petcare.db')}"
            
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    PET_UPLOADS = os.path.join(UPLOAD_FOLDER, 'pets')
    DOC_UPLOADS = os.path.join(UPLOAD_FOLDER, 'documents')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
    
    # Security & Session Settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    SESSION_PROTECTION = 'strong'
