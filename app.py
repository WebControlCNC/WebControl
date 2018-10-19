from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request,
    session,
    send_from_directory,
    jsonify,
)
from flask_mobility import Mobility
from flask_mobility.decorators import mobile_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)
mobility = Mobility(app)
