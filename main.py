#main.py
from app    import app, socketio

from gevent import monkey
monkey.patch_all()

import time
import json
import re
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
app.previousPosX = 0.0
app.previousPosY = 0.0


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

@socketio.on('my event', namespace='/MaslowCNC')
def my_event(msg):
    print msg['data']

@socketio.on('requestPage', namespace="/MaslowCNC")
def requestPage(msg):
    if msg['data']=="maslowSettings":
        setValues = app.data.config.getJSONSettingSection("Maslow Settings")
        page =render_template('settings.html', title="Maslow Settings", settings=setValues, pageID="maslowSettings")
        socketio.emit('activateModal', {'title':"Maslow Settings", 'message':page}, namespace='/MaslowCNC')
    if msg['data']=="advancedSettings":
        setValues = app.data.config.getJSONSettingSection("Advanced Settings")
        page =render_template('settings.html', title="Advanced Settings", settings=setValues, pageID="advancedSettings")
        socketio.emit('activateModal', {'title':"Advanced Settings", 'message':page}, namespace='/MaslowCNC')
    if msg['data']=="webControlSettings":
        setValues = app.data.config.getJSONSettingSection("WebControl Settings")
        page =render_template('settings.html', title="WebControl Settings", settings=setValues, pageID="webControlSettings")
        socketio.emit('activateModal', {'title':"WebControl Settings", 'message':page}, namespace='/MaslowCNC')
    if msg['data']=="openGCode":
        page =render_template('openGCode.html')
        socketio.emit('activateModal', {'title':"GCode", 'message':page}, namespace='/MaslowCNC')
    if msg['data']=='actions':
        page = render_template('actions.html')
        socketio.emit('activateModal', {'title':"Actions", 'message':page}, namespace='/MaslowCNC')
    if msg['data']=='zAxis':
        page = render_template('zaxis.html')
        socketio.emit('activateModal', {'title':"Z-Axis", 'message':page}, namespace='/MaslowCNC')

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
    dist = 0
    if (msg['data']['command']=='resetChainLengths'):
        app.data.gcode_queue.put("B08 ")
    elif (msg['data']['command']=='reportSettings'):
        app.data.gcode_queue.put('$$')
    elif (msg['data']['command']=='home'):
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
    elif (msg['data']['command']=='defineHome'):
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
        #app.data.gcodeFile.isChanged=False
        units = app.data.config.getValue('Computed Settings', 'units')
        socketio.emit('requestedSetting', {'setting':'units','value':units}, namespace='/MaslowCNC')
        socketio.emit('gcodeUpdate', {'data':sendStr}, namespace='/MaslowCNC')
        print "#Gcode Sent"
    elif (msg['data']['command']=='defineZ0'):
        app.data.gcode_queue.put("G10 Z0 ")
    elif (msg['data']['command']=='stopZ'):
        app.data.quick_queue.put("!")
        with app.data.gcode_queue.mutex:
            app.data.gcode_queue.queue.clear()
    elif (msg['data']['command']=='startRun'):
        try:
            app.data.uploadFlag = 1
            app.data.gcode_queue.put(app.data.gcode[app.data.gcodeIndex])
            app.data.gcodeIndex = app.data.gcodeIndex + 1
        except:
            print "gcode run complete"
            app.gcodecanvas.uploadFlag = 0
            app.data.gcodeIndex = 0
    elif (msg['data']['command']=='stopRun'):
        app.data.uploadFlag = 0
        app.data.gcodeIndex = 0
        app.data.quick_queue.put("!")
        with app.data.gcode_queue.mutex:
            app.data.gcode_queue.queue.clear()
        #TODO: app.onUploadFlagChange(self.stopRun, 0)
        print("Gcode Stopped")
    elif (msg['data']['command']=='moveToDefault'):
        chainLength = app.data.config.getValue('Advanced Settings', 'chainExtendLength')
        app.data.gcode_queue.put("G90 ")
        app.data.gcode_queue.put("B09 R"+str(chainLength)+" L"+str(chainLength)+" ")
        app.data.gcode_queue.put("G91 ")
    elif (msg['data']['command']=='testMotors'):
        app.data.gcode_queue.put("B04 ")
    elif (msg['data']['command']=='wipeEEPROM'):
        app.data.gcode_queue.put("$RST=* ")
        timer = threading.Timer(6.0, app.data.gcode_queue.put('$$'))
        timer.start()
    elif (msg['data']['command']=='pauseRun'):
        app.data.uploadFlag = 0
        print("Run Paused")
    elif (msg['data']['command']=='resumeRun'):
        app.data.uploadFlag = 1
        app.data.quick_queue.put("~") #send cycle resume command to unpause the machine
    elif (msg['data']['command']=='returnToCenter'):
        app.data.gcode_queue.put("G90  ")
        safeHeightMM = float(app.data.config.getValue('Maslow Settings', 'zAxisSafeHeight'))
        safeHeightInches = safeHeightMM / 24.5
        if app.data.units == "INCHES":
            app.data.gcode_queue.put("G00 Z" + '%.3f'%(safeHeightInches))
        else:
            app.data.gcode_queue.put("G00 Z" + str(safeHeightMM))
        app.data.gcode_queue.put("G00 X0.0 Y0.0 ")
    elif (msg['data']['command']=='clearGCode'):
        app.data.gcodeFile = ""
        socketio.emit('gcodeUpdate', {'data':''}, namespace='/MaslowCNC')
    elif (msg['data']['command']=='moveGcodeZ'):
        dist = 0
        moves = int(msg['data']['arg'])
        for index,zMove in enumerate(app.data.zMoves):
            if moves > 0 and zMove > app.data.gcodeIndex:
                dist = app.data.zMoves[index+moves-1]-app.data.gcodeIndex
                break
            if moves < 0 and zMove < app.data.gcodeIndex:
                dist = app.data.zMoves[index+moves+1]-app.data.gcodeIndex
        #this command will continue on in the moveGcodeIndex "if"

    if (msg['data']['command']=='moveGcodeIndex' or msg['data']['command']=='moveGcodeZ'):
        maxIndex = len(app.data.gcode)-1
        if  msg['data']['command']=='moveGcodeZ':
            targetIndex = app.data.gcodeIndex + dist
        else:
            targetIndex = app.data.gcodeIndex + int(msg['data']['arg'])

        print "targetIndex="+str(targetIndex)
        #check to see if we are still within the length of the file
        if maxIndex < 0:              #break if there is no data to read
            return
        elif targetIndex < 0:             #negative index not allowed
            app.data.gcodeIndex = 0
        elif targetIndex > maxIndex:    #reading past the end of the file is not allowed
            app.data.gcodeIndex = maxIndex
        else:
            app.data.gcodeIndex = targetIndex
        gCodeLine = app.data.gcode[app.data.gcodeIndex]
        print app.data.gcode
        print "gcodeIndex="+str(app.data.gcodeIndex)+", gCodeLine:"+gCodeLine
        xTarget = 0
        yTarget = 0

        try:
            x = re.search("X(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if x:
                xTarget = float(x.groups()[0])
                app.previousPosX = xTarget
            else:
                xTarget = app.previousPosX

            y = re.search("Y(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            print y
            if y:
                yTarget = float(y.groups()[0])
                app.previousPosY = yTarget
            else:
                yTarget = app.previousPosY
            #self.gcodecanvas.positionIndicator.setPos(xTarget,yTarget,self.data.units)
            print "xTarget:"+str(xTarget)+", yTarget:"+str(yTarget)
            position = {'xval':xTarget,'yval':yTarget,'zval':app.data.zval}
            socketio.emit('positionMessage', {'data':json.dumps(position) }, namespace='/MaslowCNC')
        except:
            print "Unable to update position for new gcode line"

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

@socketio.on('moveZ', namespace='/MaslowCNC')
def moveZ(msg):
    distToMoveZ = float(msg['data']['distToMoveZ'])
    app.data.config.setValue("Computed Settings", 'distToMoveZ',distToMoveZ)
    unitsZ = app.data.config.getValue('Computed Settings', 'unitsZ')
    if unitsZ == "MM":
        app.data.gcode_queue.put('G21 ')
    else:
        app.data.gcode_queue.put('G20 ')
    if (msg['data']['direction']=='raise'):
        app.data.gcode_queue.put("G91 G00 Z" + str(float(distToMoveZ)) + " G90 ")
    elif (msg['data']['direction']=='lower'):
        app.data.gcode_queue.put("G91 G00 Z" + str(-1.0*float(distToMoveZ)) + " G90 ")
    units = app.data.config.getValue('Computed Settings', 'units')
    if units == "MM":
        app.data.gcode_queue.put('G21 ')
    else:
        app.data.gcode_queue.put('G20 ')

@socketio.on('settingRequest', namespace="/MaslowCNC")
def settingRequest(msg):
    if (msg['data']=="units"):
        units = app.data.config.getValue('Computed Settings', 'units')
        socketio.emit('requestedSetting', {'setting':msg['data'], 'value':units}, namespace='/MaslowCNC')
    if (msg['data']=="distToMove"):
        distToMove = app.data.config.getValue('Computed Settings', 'distToMove')
        socketio.emit('requestedSetting', {'setting':msg['data'], 'value':distToMove}, namespace='/MaslowCNC')
    if (msg['data']=="unitsZ"):
        unitsZ = app.data.config.getValue('Computed Settings', 'unitsZ')
        socketio.emit('requestedSetting', {'setting':msg['data'], 'value':unitsZ}, namespace='/MaslowCNC')
    if (msg['data']=="distToMoveZ"):
        distToMoveZ = app.data.config.getValue('Computed Settings', 'distToMoveZ')
        socketio.emit('requestedSetting', {'setting':msg['data'], 'value':distToMoveZ}, namespace='/MaslowCNC')

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
    if (msg['data']['setting']=='toInchesZ'):
        app.data.units = "INCHES"
        app.data.config.setValue("Computed Settings", 'unitsZ',app.data.units)
        app.data.config.setValue("Computed Settings", 'distToMoveZ',msg['data']['value'])
    if (msg['data']['setting']=='toMMZ'):
        app.data.units = "MM"
        app.data.config.setValue("Computed Settings", 'unitsZ',app.data.units)
        app.data.config.setValue("Computed Settings", 'distToMoveZ',msg['data']['value'])

@socketio.on('checkForGCodeUpdate', namespace="/MaslowCNC")
def checkForGCodeUpdate(msg):
    print "got request for gcode update"
    #print app.data.gcodeFile.isChanged
    if True:#app.data.gcodeFile.isChanged:
        print "preparing gcode update"
        sendStr = json.dumps([ob.__dict__ for ob in app.data.gcodeFile.line])
        #app.data.gcodeFile.isChanged=False
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
