#main.py
from app    import app, socketio

from gevent import monkey
monkey.patch_all()

import time
import json
from threading import Thread
from flask import Flask, jsonify, render_template, current_app, request, flash
from flask_socketio import SocketIO
from werkzeug import secure_filename

from background.backgroundTasks import background_stuff #do this after socketio is declared
from DataStructures.data          import   Data
from Connection.serialPort        import   SerialPort
from config.config                       import   Config
from DataStructures.logger                            import   Logger
from DataStructures.loggingQueue                      import   LoggingQueue
from Connection.nonVisibleWidgets import   NonVisibleWidgets
import Queue

app.data = Data()
app.nonVisibleWidgets = NonVisibleWidgets()
app.nonVisibleWidgets.setUpData(app.data)
app.data.config.computeSettings(None,None,None,True)
app.data.units = app.data.config.getValue('Computed Settings', 'units')
app.data.comport = app.data.config.getValue('Maslow Settings', 'COMport')
if app.data.units == "INCHES":
    scale = 1.0
else:
    scale = 25.4
app.data.gcodeShift =[float(app.data.config.getValue('Advanced Settings','homeX'))/scale,float(app.data.config.getValue('Advanced Settings','homeY'))/scale]



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
    if request.method=="POST":
        result = request.form
        app.data.config.updateSettings("Maslow Settings", result)
        setValues = app.data.config.getJSONSettingSection("Maslow Settings")
        message = {'status': 200}
        resp = jsonify(message)
        resp.status_code = 200
        return resp

@app.route('/advancedSettings', methods=['GET','POST'])
def advancedSettings():
    if request.method=="POST":
        result = request.form
        app.data.config.updateSettings("Advanced Settings", result)
        setValues = app.data.config.getJSONSettingSection("Advanced Settings")
        message = {'status': 200}
        resp = jsonify(message)
        resp.status_code = 200
        return resp

@app.route('/webControlSettings', methods=['GET','POST'])
def webControlSettings():
    if request.method=="POST":
        result = request.form
        app.data.config.updateSettings("WebControl Settings", result)
        setValues = app.data.config.getJSONSettingSection("WebControl Settings")
        message = {'status': 200}
        resp = jsonify(message)
        resp.status_code = 200
        return resp
'''
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
'''
@app.route('/gcode', methods=['POST'])
def gcode():
    if request.method == 'POST':
        f = request.files['file']
        app.data.gcodeFile.filename="gcode\\"+secure_filename(f.filename)
        f.save(app.data.gcodeFile.filename)
        app.data.gcodeFile.loadUpdateFile()
        #return render_template('frontpage.html')
        message = {'status': 200}
        resp = jsonify(message)
        resp.status_code = 200
        return resp

@app.route('/actions')
def actions():
    return render_template('actions.html')

@socketio.on('my event', namespace='/MaslowCNC')
def my_event(msg):
    print msg['data']

@socketio.on('requestPage', namespace="/MaslowCNC")
def requestPage(msg):
    if msg['data']=="maslowSettings":
        setValues = app.data.config.getJSONSettingSection("Maslow Settings")
        page =render_template('settings.html', title="Maslow Settings", settings=setValues)
        socketio.emit('activateModal', {'title':"Maslow Settings", 'message':page}, namespace='/MaslowCNC')
    if msg['data']=="advancedSettings":
        setValues = app.data.config.getJSONSettingSection("Advanced Settings")
        page =render_template('settings.html', title="Advanced Settings", settings=setValues)
        socketio.emit('activateModal', {'title':"Advanced Settings", 'message':page}, namespace='/MaslowCNC')
    if msg['data']=="webControlSettings":
        setValues = app.data.config.getJSONSettingSection("WebControl Settings")
        page =render_template('settings.html', title="WebControl Settings", settings=setValues)
        socketio.emit('activateModal', {'title':"WebControl Settings", 'message':page}, namespace='/MaslowCNC')
    if msg['data']=="gcode":
        page =render_template('gcode.html')
        socketio.emit('activateModal', {'title':"GCode", 'message':page}, namespace='/MaslowCNC')

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
    print "here"
    if (msg['data']=='resetChainLengths'):
        app.data.gcode_queue.put("B08 ")
    elif (msg['data']=='reportSettings'):
        app.data.gcode_queue.put('$$')
    elif (msg['data']=='home'):
        app.data.gcode_queue.put("G90  ")
        #todo:self.gcodeVel = "[MAN]"
        safeHeightMM = float(app.data.config.getValue('Maslow Settings', 'zAxisSafeHeight'))
        safeHeightInches = safeHeightMM / 25.5
        if app.data.units == "INCHES":
            app.data.gcode_queue.put("G00 Z" + '%.3f'%(safeHeightInches))
        else:
            app.data.gcode_queue.put("G00 Z" + str(safeHeightMM))
        app.data.gcode_queue.put("G00 X" + str(app.data.gcodeShift[0]) + " Y" + str(app.data.gcodeShift[1]) + " ")
        app.data.gcode_queue.put("G00 Z0 ")
    elif (msg['data']=='defineHome'):

        if app.data.units == 'MM':
            scaleFactor = 25.4
        else:
            scaleFactor = 1.0
        #print "xval:"+str(app.data.xval)+", yval:"+str(app.data.yval)
        app.data.gcodeShift = [app.data.xval/scaleFactor,app.data.yval/scaleFactor]
        app.data.config.setValue("Advanced Settings", 'homeX', str(app.data.xval))
        app.data.config.setValue("Advanced Settings", 'homeY', str(app.data.yval))
        app.data.gcodeFile.loadUpdateFile()
        print "preparing gcode update"
        sendStr = json.dumps([ob.__dict__ for ob in app.data.gcodeFile.line])
        app.data.gcodeFile.isChanged=False
        units = app.data.config.getValue('Computed Settings', 'units')
        socketio.emit('requestedSetting', {'setting':'units','value':units}, namespace='/MaslowCNC')
        socketio.emit('gcodeUpdate', {'data':sendStr}, namespace='/MaslowCNC')
        print "#Gcode Sent"
    elif (msg['data']=='startRun'):
        try:
            app.data.uploadFlag = 1
            app.data.gcode_queue.put(app.data.gcode[app.data.gcodeIndex])
            app.data.gcodeIndex = app.data.gcodeIndex + 1
        except:
            print "gcode run complete"
            app.gcodecanvas.uploadFlag = 0
            app.data.gcodeIndex = 0
    elif (msg['data']=='stopRun'):
        app.data.uploadFlag = 0
        app.data.gcodeIndex = 0
        app.data.quick_queue.put("!")
        with app.data.gcode_queue.mutex:
            app.data.gcode_queue.queue.clear()
        #TODO: app.onUploadFlagChange(self.stopRun, 0)
        print("Gcode Stopped")

@socketio.on('move', namespace='/MaslowCNC')
def move(msg):
    distToMove = float(msg['data']['distToMove'])
    if (msg['data']['direction']=='upLeft'):
        app.data.gcode_queue.put("G91 G00 X" + str(-1.0*distToMove) + " Y" + str(distToMove) + " G90 ")
    elif (msg['data']['direction']=='up'):
        app.data.gcode_queue.put("G91 G00 Y" + str(distToMove) + " G90 ")
    elif (msg['data']['direction']=='upRight'):
        app.data.gcode_queue.put("G91 G00 X" + str(distToMove) + " Y" + str(distToMove) + " G90 ")
    elif (msg['data']['direction']=='left'):
        app.data.gcode_queue.put("G91 G00 X" + str(-1.0*distToMove) + " G90 ")
    elif (msg['data']['direction']=='right'):
        app.data.gcode_queue.put("G91 G00 X" + str(distToMove) + " G90 ")
    elif (msg['data']['direction']=='downLeft'):
        app.data.gcode_queue.put("G91 G00 X" + str(-1.0*distToMove) + " Y" + str(-1.0*distToMove) + " G90 ")
    elif (msg['data']['direction']=='down'):
        app.data.gcode_queue.put("G91 G00 Y" + str(-1.0*distToMove) + " G90 ")
    elif (msg['data']['direction']=='downRight'):
        app.data.gcode_queue.put("G91 G00 X" + str(distToMove) + " Y" + str(-1.0*distToMove) + " G90 ")

@socketio.on('settingRequest', namespace="/MaslowCNC")
def settingRequest(msg):
    if (msg['data']=="units"):
        units = app.data.config.getValue('Computed Settings', 'units')
        socketio.emit('requestedSetting', {'setting':msg['data'], 'value':units}, namespace='/MaslowCNC')
    if (msg['data']=="distToMove"):
        distToMove = app.data.config.getValue('Computed Settings', 'distToMove')
        socketio.emit('requestedSetting', {'setting':msg['data'], 'value':distToMove}, namespace='/MaslowCNC')

@socketio.on('updateSetting', namespace="/MaslowCNC")
def updateSetting(msg):
    if (msg['data']['setting']=='toInches'):
        app.data.units = "INCHES"
        app.data.config.setValue("Computed Settings", 'units',app.data.units)
        scaleFactor = 1.0
        app.data.gcodeShift = [app.data.xval/scaleFactor,app.data.yval/scaleFactor]
        app.data.tolerance = 0.020
        app.data.gcode_queue.put('G20 ')
        app.data.config.setValue("Computed Settings", 'distToMove',msg['data']['value'])
    if (msg['data']['setting']=='toMM'):
        app.data.units = "MM"
        app.data.config.setValue("Computed Settings", 'units',app.data.units)
        scaleFactor = 25.4
        app.data.gcodeShift = [app.data.xval/scaleFactor,app.data.yval/scaleFactor]
        app.data.tolerance = 0.5
        app.data.gcode_queue.put('G21')
        app.data.config.setValue("Computed Settings", 'distToMove',msg['data']['value'])

@socketio.on('checkForGCodeUpdate', namespace="/MaslowCNC")
def checkForGCodeUpdate(msg):
    print "got request for gcode update"
    #print app.data.gcodeFile.isChanged
    if app.data.gcodeFile.isChanged:
        print "preparing gcode update"
        sendStr = json.dumps([ob.__dict__ for ob in app.data.gcodeFile.line])
        app.data.gcodeFile.isChanged=False
        units = app.data.config.getValue('Computed Settings', 'units')
        print units
        socketio.emit('requestedSetting', {'setting':'units', 'value':units}, namespace='/MaslowCNC')
        socketio.emit('gcodeUpdate', {'data':sendStr}, namespace='/MaslowCNC')
        print "#Gcode Sent"


@socketio.on_error_default
def default_error_handler(e):
    print(request.event["message"]) # "my error event"
    print(request.event["args"])    # (data,)1



if __name__ == '__main__':
    app.debug = False
    app.config['SECRET_KEY'] = 'secret!'
    socketio.run(app, use_reloader=False)
