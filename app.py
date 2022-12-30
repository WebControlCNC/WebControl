# from pyjion.wsgi import PyjionWsgiMiddleware

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

# Override the app wsgi_app property
# app.wsgi_app = PyjionWsgiMiddleware(app.wsgi_app)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=False,
    always_connect=True
)
mobility = Mobility(app)
# md.init_app(app)
