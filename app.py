from flask import Flask
from flask_mobility import Mobility
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)
mobility = Mobility(app)
