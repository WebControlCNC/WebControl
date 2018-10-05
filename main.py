#main.py

from gevent import monkey
monkey.patch_all()

import time
from threading import Thread
from flask import Flask, render_template, current_app
from flask_socketio import SocketIO


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
from background.backgroundTasks import background_stuff #do this after socketio is declared



@app.route('/')
def index():
    thread = socketio.start_background_task(background_stuff, current_app._get_current_object())
    thread.start()
    return render_template('frontpage.html')

@app.route('/settings')
def settings():
    from settings import settings
    setValues = settings.getJSONSettingSection("Maslow Settings")
    return render_template('settings.html', settings=setValues)

@app.route('/actions')
def actions():
    return render_template('actions.html')

@socketio.on('my event', namespace='/MaslowCNC')
def my_event(msg):
    print msg['data']

@socketio.on('connect', namespace='/MaslowCNC')
def test_connect():
    socketio.emit('my response', {'data': 'Connected', 'count': 0})

@socketio.on('disconnect', namespace='/MaslowCNC')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app)
