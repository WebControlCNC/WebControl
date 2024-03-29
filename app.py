from flask import Flask
from flask_mobility import Mobility
from flask_socketio import SocketIO

# from flask_misaka import Misaka

import os, sys

base_dir = "."
if hasattr(sys, "_MEIPASS"):
    base_dir = os.path.join(sys._MEIPASS)

# md = Misaka()

app = Flask(
    __name__,
    static_folder=os.path.join(base_dir, "static"),
    template_folder=os.path.join(base_dir, "templates"),
)
app.debug = True
socketio = SocketIO(app)
mobility = Mobility(app)
# md.init_app(app)
