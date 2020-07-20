from flask import Flask
from flask_mobility import Mobility
from flask_socketio import SocketIO
from flask_misaka import Misaka
from flask_sqlalchemy import SQLAlchemy
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)


import os, sys
from logging import DEBUG, StreamHandler, basicConfig, getLogger
base_dir = '.'
if hasattr(sys, '_MEIPASS'):
    base_dir = os.path.join(sys._MEIPASS)




#Variables
db = SQLAlchemy()
login_manager = LoginManager()
md = Misaka()





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



app = Flask(__name__, static_folder=os.path.join(base_dir, 'static'), template_folder=os.path.join(base_dir, 'templates'))

app.debug = True
md.init_app(app)
register_extension(app)
configure_database(app)
configure_loging(app)
#TODO:
#configure_theme(app)
socketio = SocketIO(app)
mobility = Mobility(app)