from flask import Flask
from flask_mobility import Mobility
from flask_socketio import SocketIO
from flask_misaka import Misaka
from flask_sqlalchemy import SQLAlchemy
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)


import os, sys
from os import environ, path
from logging import DEBUG, StreamHandler, basicConfig, getLogger
base_dir = '.'
if hasattr(sys, '_MEIPASS'):
    base_dir = os.path.join(sys._MEIPASS)




#Variables
db = SQLAlchemy()
login_manager = LoginManager()
md = Misaka()


class Config(object):
    """
    """
    #BASE DIR
    basedir = path.abspath(path.dirname(__file__))
    
    #Sqlalchemy
    SECRET_KEY = environ.get('KEY_SECRET', 'love_it') 
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(basedir, 'site_database.db')
    #sqlite:///:memory'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    #theme
    DEFAULT_THEME = None

class ProductionConfig(Config):
    """
    """
    #Developer
    DEBUG = False

    #Security
    SESSION_COOKIE_HTTPPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    #PostgreSQL
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(
        environ.get('LIGHT_DATABASE_USER', 'master'),
        environ.get('LIGHT_DATABASE_PASSWORD', '123'),
        environ.get('LIGHT_DATABASE_HOST', 'db'),
        environ.get('LIGHT_DATABASE_PORT', 5433),
        environ.get('LIGHT_DATABASE_NAME', 'master')
    )

    #OATH2 GOOGLE
    GOOGLE_CLIENT_ID = environ.get('GOOGLE_CLIENT_ID', None)
    GOOGLE_CLIENT_SECRET = environ.get('GOOGLE_CLIENT_SECRET', None)
    GOOGLE_DISCOVERY_URL = (
        "https://accounts.google.com/.well-known/openid-configuration"
    )

class DebugConfig(Config):
    
    DEBUG = True

config_dict = {
    'Debug': DebugConfig, 
    'Production': ProductionConfig,
    'Config': Config
}


def register_extension(app):
    """
    sd
    """
    db.init_app(app)
    login_manager.init_app(app)

def configure_database(app):
    """
    Configure database
    """
    @app.before_first_request
    def initalize_database():
        """
        This function will run once before the first request.
        """
        db.create_all()

    @app.teardown_request
    def shutdown_session(error=None):
        """
        This function will run after a request, if exception occus or not.
        """
        db.session.remove()

def configure_loging(app):
    """
    """
    try:
        basicConfig(filename='logs.log', level = DEBUG)
        logger = getLogger()
        logger.addHandler(StreamHandler())
    except:
        pass

def configure_theme(app):

    """
    """
    #TODO: @app theme
    pass

config_mode_get = environ.get('CONFIG_MODE', 'Debug' ).strip().replace('\'','') #Debug, Config, Production

try:
    config_mode = config_dict[config_mode_get.capitalize()]
    print(config_mode)
except KeyError:
    exit('Error: Invalid CONFIG_MODE enviroment variable.')


app = Flask(__name__, static_folder=os.path.join(base_dir, 'static'), template_folder=os.path.join(base_dir, 'templates'))
app.config.from_object(config_mode)

app.debug = True
md.init_app(app)
register_extension(app)
configure_database(app)
configure_loging(app)
#TODO:
#configure_theme(app)
socketio = SocketIO(app)
mobility = Mobility(app)