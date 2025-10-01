import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(basedir), '.env')
load_dotenv(env_path)


class Config:

    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Admin configuration
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    PAGE_SIZE = 20

    # File upload configuration
    UPLOAD_FOLDER = f"{basedir}/static/uploads"
    DOWNLOAD_PATH = "static/uploads"
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    
    # LLM configuration
    LLM_API_KEY = os.environ.get('LLM_API_KEY')
    LLM_BASE_URL = os.environ.get('LLM_BASE_URL') or 'https://api.openai.com/v1'
    LLM_MODEL = os.environ.get('LLM_MODEL') or 'gpt-3.5-turbo'
    
    # Babel configuration
    LANGUAGES = {
        'en': 'English',
        'zh': '中文'
    }
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(os.path.dirname(basedir), 'translations')
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    CONTEXT_PATH = '/'
    DEBUG = True

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'video-to-text-dev.db')


class TestingConfig(Config):
    CONTEXT_PATH = '/'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'video-to-text-test.db')


class ProductionConfig(Config):
    CONTEXT_PATH = '/webdiagram'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'video-to-text.db')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig

}