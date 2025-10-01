import logging
import os
import sys
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_pagedown import PageDown
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from flask_login import LoginManager
from flask import session, request
from .config import config
from .models import db, User

bootstrap = Bootstrap()
moment = Moment()
pagedown = PageDown()
login_manager = LoginManager()

def get_locale():
    # Check if language is set in session
    try:
        if 'language' in session:
            return session['language']
        # Otherwise use the default locale
        return request.accept_languages.best_match(['en', 'zh']) or 'en'
    except RuntimeError:
        # Working outside of request context, return default
        return 'en'

babel = Babel()


def create_logger(filename, log2console=True, logLevel=logging.INFO, logFolder='./logs'):
    # add log
    logger = logging.getLogger(filename)
    logger.setLevel(logging.INFO)
    formats = '%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s'
    formatter = logging.Formatter(formats)

    logfile = os.path.join(logFolder, filename + '.log')
    directory = os.path.dirname(logfile)
    if not os.path.exists(directory):
        os.makedirs(directory)

    handler = logging.FileHandler(logfile)
    handler.setLevel(logLevel)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if log2console:
        handler2 = logging.StreamHandler(sys.stdout)
        handler2.setFormatter(logging.Formatter(formats))
        handler2.setLevel(logLevel)
        logger.addHandler(handler2)

    return logger



def create_app(app_name, env_name="default"):
    # Get the directory where this file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(current_dir, 'templates')
    static_dir = os.path.join(current_dir, 'static')
    
    app = Flask(app_name, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config[env_name])
    #app.config["SECRET_KEY"] = "secret"
    config[env_name].init_app(app)

    config_name = os.getenv('FLASK_CONFIG') or 'default'

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    pagedown.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    login_manager.init_app(app)
    
    # Configure Flask-Login
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

app = create_app("video_to_text")
logger = create_logger("video_to_text")

# Import views to register routes
from . import views




