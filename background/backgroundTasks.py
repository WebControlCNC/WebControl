from flask import session
from flask_socketio import emit
from __main__ import socketio

import time

def background_stuff(app):
    with app.app_context():
        while True:
            time.sleep(1)
            t = str(time.clock())
            socketio.emit('message', {'data': 'This is data', 'time': t}, namespace='/MaslowCNC')
