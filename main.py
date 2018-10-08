#main.py
from app    import app, socketio

from gevent import monkey
monkey.patch_all()

import time
import json
from threading import Thread
from flask import Flask, render_template, current_app, request, flash
from flask_socketio import SocketIO

from background.backgroundTasks import background_stuff #do this after socketio is declared
from DataStructures.data          import   Data
from Connection.serialPort        import   SerialPort
from config                       import   config
from DataStructures.logger                            import   Logger
from DataStructures.loggingQueue                      import   LoggingQueue
from Connection.nonVisibleWidgets import   NonVisibleWidgets
import Queue

app.data = Data()
app.nonVisibleWidgets = NonVisibleWidgets()
app.nonVisibleWidgets.setUpData(app.data)
app.data.config = config
app.data.comport = config.getSettingValue('Maslow Settings', 'COMport')
app.data.gcodeShift =[float(app.data.config.getSettingValue('Advanced Settings','homeX')),float(app.data.config.getSettingValue('Advanced Settings','homeY'))]




#write settings file to disk:
#from settings import settings
#settings = settings.getJSONSettings()
#with open('webcontrol.json', 'w') as outfile:
#    json.dump(settings,outfile, sort_keys=True, indent=4, ensure_ascii=False)

#read settings file from disk:

@app.route('/')
def index():
    current_app._get_current_object()
    thread = socketio.start_background_task(background_stuff, current_app._get_current_object())
    thread.start()
    if not app.data.connectionStatus:
        app.data.serialPort.openConnection()
    return render_template('frontpage.html')

@app.route('/maslowSettings', methods=['GET','POST'])
def maslowSettings():
    if request.method=="GET":
        setValues = config.getJSONSettingSection("Maslow Settings")
        return render_template('settings.html', title="Maslow Settings", settings=setValues)
    else:
        result = request.form
        flash("Submitted")
        config.updateSettings("Maslow Settings", result)
        setValues = config.getJSONSettingSection("Maslow Settings")
        return render_template('settings.html', title="Maslow Settings", settings=setValues)

@app.route('/advancedSettings', methods=['GET','POST'])
def advancedSettings():
    if request.method=="GET":
        setValues = config.getJSONSettingSection("Advanced Settings")
        return render_template('settings.html', title="Advanced Settings", settings=setValues)
    else:
        result = request.form
        flash("Submitted")
        config.updateSettings("Advanced Settings", result)
        setValues = config.getJSONSettingSection("Advanced Settings")
        return render_template('settings.html', title="Advanced Settings", settings=setValues)

@app.route('/webControlSettings', methods=['GET','POST'])
def webControlSettings():
    if request.method=="GET":
        setValues = config.getJSONSettingSection("WebControl Settings")
        return render_template('settings.html', title="WebControl Settings", settings=setValues)
    else:
        result = request.form
        flash("Submitted")
        config.updateSettings("WebControl Settings", result)
        setValues = config.getJSONSettingSection("WebControl Settings")
        return render_template('settings.html', title="WebControl Settings", settings=setValues)


@app.route('/actions')
def actions():
    return render_template('actions.html')

@socketio.on('my event', namespace='/MaslowCNC')
def my_event(msg):
    print msg['data']

@socketio.on('connect', namespace='/MaslowCNC')
def test_connect():
    print "connected"
    print request.sid
    socketio.emit('my response', {'data': 'Connected', 'count': 0})

@socketio.on('disconnect', namespace='/MaslowCNC')
def test_disconnect():
    print('Client disconnected')

@socketio.on('action', namespace='/MaslowCNC')
def command(msg):
    if (msg['data']=='resetChainLengths'):
        app.data.gcode_queue.put("B08 ")
    if (msg['data']=='reportSettings'):
        app.data.gcode_queue.put('$$')

@socketio.on_error_default
def default_error_handler(e):
    print(request.event["message"]) # "my error event"
    print(request.event["args"])    # (data,)1

if __name__ == '__main__':
    app.debug = False
    app.config['SECRET_KEY'] = 'secret!'
    socketio.run(app, use_reloader=False)
