from flask import session
from flask_socketio import emit
from __main__ import socketio

import time

def background_stuff(app):
    with app.app_context():
        while True:
            time.sleep(.001)
            t = str(time.clock())
            message = app.data.message
            if (message!=""):
                if (message[0]!="[" and message[0]!="<"):
                    socketio.emit('controllerMessage', {'data':app.data.message }, namespace='/MaslowCNC')
                else:
                    socketio.emit('positionMessage', {'data':app.data.message }, namespace='/MaslowCNC')
                app.data.message = ""

            #print data
            #if hasattr(data, 'controllerMessage'):
                #print "controllerMessage:"+data.controllerMessage
            #socketio.emit('controllerMessage', {'data': 'Test Message'}, namespace='/MaslowCNC')
            #if (main.status["ControllerConnected"]==False):
            #    if (main.settings.COMport!=""):
            #Clock.schedule_interval(self.openConnection, 5)
