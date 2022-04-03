# main.py
from app import app, socketio
from gevent import monkey
import webbrowser
import socket
import math
import os
import subprocess
import sys
import schedule
import time
import threading
import json
import platform
monkey.patch_all()

from flask import Flask, jsonify, render_template, current_app, request, flash, Response, send_file, send_from_directory
from flask_mobility.decorators import mobile_template
from werkzeug.utils import secure_filename
from Background.UIProcessor import UIProcessor  # do this after socketio is declared
from Background.LogStreamer import LogStreamer  # do this after socketio is declared
from Background.WebMCPProcessor import WebMCPProcessor
from Background.WebMCPProcessor import ConsoleProcessor
from DataStructures.data import Data
from Connection.nonVisibleWidgets import NonVisibleWidgets
from WebPageProcessor.webPageProcessor import WebPageProcessor
from os import listdir
from os.path import isfile, join

app.data = Data()
app.nonVisibleWidgets = NonVisibleWidgets()
app.nonVisibleWidgets.setUpData(app.data)
app.data.config.computeSettings(None, None, None, True)
app.data.config.parseFirmwareVersions()
app.data.units = app.data.config.getValue("Computed Settings", "units")
app.data.tolerance = app.data.config.getValue("Computed Settings", "tolerance")
app.data.distToMove = app.data.config.getValue("Computed Settings", "distToMove")
app.data.distToMoveZ = app.data.config.getValue("Computed Settings", "distToMoveZ")
app.data.unitsZ = app.data.config.getValue("Computed Settings", "unitsZ")
app.data.comport = app.data.config.getValue("Maslow Settings", "COMport")
app.data.gcodeShift = [
    float(app.data.config.getValue("Advanced Settings", "homeX")),
    float(app.data.config.getValue("Advanced Settings", "homeY")),
]
version = sys.version_info

if version[:2] > (3, 5):
    app.data.pythonVersion35 = False
    print("Using routines for Python > 3.5")
else:
    app.data.pythonVersion35 = True
    print("Using routines for Python == 3.5")

app.data.firstRun = False
# app.previousPosX = 0.0
# app.previousPosY = 0.0

app.UIProcessor = UIProcessor()
app.webPageProcessor = WebPageProcessor(app.data)
app.LogStreamer = LogStreamer()

## this defines the schedule for running the serial port open connection
def run_schedule():
    while 1:
        schedule.run_pending()
        time.sleep(1)

## this runs the scheduler to check for connections
app.th = threading.Thread(target=run_schedule)
app.th.daemon = True
app.th.start()

## this runs the thread that processes messages from the controller
app.th1 = threading.Thread(target=app.data.messageProcessor.start)
app.th1.daemon = True
app.th1.start()

## this runs the thread that sends debugging messages to the terminal and webmcp (if active)
app.th2 = threading.Thread(target=app.data.consoleProcessor.start)
app.th2.daemon = True
app.th2.start()

## uithread set to None.. will be activated upon first websocket connection from browser
app.uithread = None

## uithread set to None.. will be activated upon first websocket connection from webmcp
app.mcpthread = None

## logstreamerthread set to None.. will be activated upon first websocket connection from log streamer browser
app.logstreamerthread = None

def web_input_command(cmd, source):
    """
    processes input commands from separate service such as raspberry pi GPIO or remote pendant to activate local commands such as start, pause, stop, move, set home, etc.
    """
    if (len(cmd) > 2):  # pull off the distance if it is there
        distance = cmd[2]  # distance is the third list element
    else:
        distance = 0  # if it isn't then put a 0 value in so no error is thrown
    message = 'none'
    if ('gcode' in cmd):  # gcode commands found in gpioactions like start the gcode file cut, pause current cut, resume from pause, stop the cut, move sled home
        print ('gcode selected')
        if ('startRun' in cmd):
            print ('start gcode ',source, ' requested')
            app.data.actions.processAction({"data":{"command":"startRun","arg":"","arg1":""}})
            message = {"data":{source:"started"}}
        elif ('pauseRun' in cmd):
            if (app.data.uploadFlag == 1):
                print ('pause gcode ',source, ' requested')
                app.data.actions.processAction({"data":{"command":"pauseRun","arg":"","arg1":""}})
                message = {"data":{source:"paused"}}
            elif (app.data.uploadFlag == 2):
                print ('continue gcode ', source, ' requested')
                app.data.actions.processAction({"data":{"command":"resumeRun","arg":"","arg1":""}})
                message = {"data":{source:"resumed"}}
            else:
                print("not running - no pause")
                message = {"data":{source:"No Pause - not running"}}
        elif (cmd[1] == 'resumeRun'):
            print ('continue gcode ',source, ' requested')
            app.data.actions.processAction({"data":{"command":"resumeRun","arg":"","arg1":""}})
            message = {"data":{source:"resumed"}}
        elif (cmd[1] == 'stopRun'):
            print ('stop gcode', source, ' requested')
            app.data.actions.processAction({"data":{"command":"stopRun","arg":"","arg1":""}})
            message = {"data":{source:"stopped"}}
        elif('home' in cmd):
            print (source, ' says go home')
            app.data.actions.processAction({"data":{"command":"home","arg":"","arg1":""}})
            message = {"data":{source:"movetoHome"}}
        else:
            print(cmd, " Invalid command")
            message = {"data":{"gcode":"NONE selected"}}
    if ('zAxis' in cmd):  # this command set works with the z axis
        print ('zaxis selected ', source)
        if('raise' in cmd):
            print (source, ' zaxis', distance, 'raise')
            app.data.actions.processAction({"data":{"command":"moveZ","arg":"raise","arg1":distance}})
            message = {"data":{source:"raise"}}
        elif('lower' in cmd):
            print (source, ' zaxis', distance, 'lower')
            app.data.actions.processAction({"data":{"command":"moveZ","arg":"lower","arg1":distance}})
            message = {"data":{source:"Lower"}}
        elif('stopZ' in cmd ):
            print (source, ' zaxis stop ', source)
            app.data.actions.processAction({"data":{"command":"stopZ","arg":"","arg1":""}})
            message = {"data":{source:"stopZ"}}
        elif('defineZ0' in cmd):
            # TODO fix set z axis zero position
            print ('new Z axis zero point via ', source)
            app.data.actions.processAction({"data":{"command":"defineZ0","arg":"","arg1":""}})
            message = {"data":{source:"defineZ"}}  # this command set will move or change the sled
        else:
            print(cmd, " Invalid command")
            message = {"data":{source:" NONE selected"}}
    if ('sled' in cmd or 'move' in cmd):    
        if('up' in cmd):
            print (source, ' move', distance, 'up')
            app.data.actions.processAction({"data":{"command":"move","arg":"up","arg1":distance}})
            message = {"data":{source:"up"}}
        elif('down' in cmd):
            print (source, ' move', distance, 'down')
            app.data.actions.processAction({"data":{"command":"move","arg":"down","arg1":distance}})
            message = {"data":{source:"down"}}
        elif('left' in cmd):
            print (source, ' move', distance, 'left')
            app.data.actions.processAction({"data":{"command":"move","arg":"left","arg1":distance}})
            message = {"data":{source:"left"}}
        elif('right' in cmd):
            print (source, ' move', distance, 'right')
            app.data.actions.processAction({"data":{"command":"move","arg":"right","arg1":distance}})
            message = {"data":{source:"right"}}
        elif('home' in cmd):
            print ('go home via ', source)
            app.data.actions.processAction({"data":{"command":"home","arg":"","arg1":""}})
            message = {"data":{source:"movetoHome"}}
        elif('defineHome' in cmd):
            # TODO fix set home position
            # this does not work
            print ('new home set via ', source, ' to ', app.data.xval ,', ', app.data.yval) 
            app.data.actions.processAction({"data":{"command":"defineHome","arg":str(app.data.xval),"arg1":str(app.data.yval)}})
            message = {"data":{source:"NewHome"}}
        else:
            print(cmd, " Invalid command")
            message = {"data":{"sled":"NONE selected"}}
    if ('system' in cmd): # this command set will adjust the system including pendant connection status and system power
        print ('system selected via ', source)
        if ('exit' in cmd):
            print("system shutdown requested")
            if (app.data.uploadFlag == 0):
                os._exit(0)
            else:
                app.data.actions.processAction({"data":{"command":"stopRun","arg":"","arg1":""}})
                print("denied: running code.  Code stopped near try again")
                message = {"data":{"system":"shutdownAttempt"}}
        else:
            print(cmd, " Invalid command")
            message = {"data":{"system":"NONE selected"}}
    return(message)

@app.route("/")
@mobile_template("{mobile/}")
def index(template):
    app.data.logger.resetIdler()
    macro1Title = (app.data.config.getValue("Maslow Settings", "macro1_title"))[:6]
    macro2Title = (app.data.config.getValue("Maslow Settings", "macro2_title"))[:6]
    macro3Title = (app.data.config.getValue("Maslow Settings", "macro3_title"))[:6]
    macro4Title = (app.data.config.getValue("Maslow Settings", "macro4_title"))[:6]
    macro5Title = (app.data.config.getValue("Maslow Settings", "macro5_title"))[:6]
    if template == "mobile/":
        return render_template("frontpage3d_mobile.html", modalStyle="modal-lg", macro1_title=macro1Title,  macro2_title=macro2Title, macro3_title=macro3Title, macro4_title=macro4Title, macro5_title=macro5Title)
    else:
        return render_template("frontpage3d.html", modalStyle="mw-100 w-75", macro1_title=macro1Title,  macro2_title=macro2Title, macro3_title=macro3Title, macro4_title=macro4Title, macro5_title=macro5Title)

@app.route('/GPIO', methods=['PUT', 'GET'])
def call_GPIO():
    '''
    MaslowButton.py starts as a separate python process if the maslow setting menu maslow button flag is true
    The GPIO is for raspberry pi general purpose input/output such as button and LED hardware physically attached to the raspberry pi
    When those buttons are pressed, the seaparate process issues an HTTP/PUT request and this method handles it.  The /LED section below sends information for LEDs
    ''' 
    # TODO  add check for platform and service start information.  
    try:
        if (request.method == "PUT"):
            print ("button function call")
            message = {"data":{"gpio":"selected"}}
            result = request.data
            result = result.decode('utf-8')
            resultlist = result.split(':')
            print ('resultlist', resultlist)
            message = web_input_command(resultlist, "button")                
            print(message)
            resp = jsonify(message)
            resp.status_code = 200 # or whatever the correct number should be
            return (resp)

        if (request.method == "GET"):
            setValues = app.data.config.getJSONSettingSection("GPIO Settings")
            return (jsonify(setValues))
        return('')
    except:
        message = jsonify({"data":{"GPIO Input/Output error":"no data"}})  # on error, respond with something rather than nothing
        resp = jsonify(message)
        resp.status_code = 404 # or whatever the correct number should be
        return (resp)
    
@app.route('/Status', methods=['GET'])
def get_status_info():
        
    '''
    This is data intended for a status LED to be set, though it could be used for a wireless display
    Upload flag signifies system state as running, paused, or stopped,
    Moving flag indicates a stopped cut condition, but the sled is moving
    zmove is the z axis moving    
    ''' 
    try:
        if (request.method == 'GET'):
            message = {"data":{"index": str(app.data.gcodeIndex),
                               "flag": str(app.data.uploadFlag),
                               "sled_location_x": str(app.data.xval),
                               "sled_location_y": str(app.data.yval),
                               "sled_location_z": str(app.data.zval),
                               "home_location_x": str(app.data.config.getValue("Advanced Settings","homeX")),
                               "home_location_y": str(app.data.config.getValue("Advanced Settings","homeY")),
                               "RGB_LED": str(app.data.RGB_LED),
                               "LED_Status": str(app.data.LED_Status),
                               "LED_Color": str(app.data.config.getValue("LED Status List",str(app.data.LED_Status)))
                               }}  #assemble json string
            print("debug message ", message)
            resp = jsonify(message) # java script object notation convrsion of the message
            resp.status_code = 200
            return (resp) # send the message
    except:
        message = jsonify({"data":{"Status message Input/Output error":"no data"}})  # on error, respond with something rather than nothing
        print("message error with message: ", message)
        resp = jsonify(message)
        resp.status_code = 404 # or whatever the correct number should be
        return (resp)

@app.route('/GPIOsettings', methods=['PUT', 'GET'])
def GPIOsettings():
    '''
    MaslowButton.py starts as a separate python process if the maslow setting menu maslow button flag is true
    The GPIO is for raspberry pi general purpose input/output such as button and LED hardware physically attached to the raspberry pi
    When those buttons are pressed, the seaparate process issues an HTTP/PUT request and this method handles it.  The /LED section below sends information for LEDs
    ''' 
    if (request.method == "PUT"):
        print ("button function call")
        message = {"data":{"gpio":"selected"}}
        result = request.data
        result = result.decode('utf-8')
        resultlist = result.split(':')
        print ('resultlist', resultlist)
                
        if ('gcode' in resultlist):  # gcode commands found in gpioactions like start the gcode file cut, pause current cut, resume from pause, stop the cut, move sled home
            print ('gcode selected')
            message = {"data":{"gcode":"selected"}}
            if ('startRun' in resultlist):
                print ('start gcode requested')
                app.nonVisibleWidgets.actions.processAction({"data":{"command":"startRun","arg":"","arg1":""}})
                message = {"data":{"buttonrun":"started"}}
            if ('pauseRun' in resultlist):
                if (app.data.uploadFlag == 1):
                    print ('pause gcode requested')
                    app.nonVisibleWidgets.actions.processAction({"data":{"command":"pauseRun","arg":"","arg1":""}})
                    message = {"data":{"buttonrun":"paused"}}
                elif (app.data.uploadFlag == 2):
                    print ('continue gcode requested')
                    app.nonVisibleWidgets.actions.processAction({"data":{"command":"resumeRun","arg":"","arg1":""}})
                    message = {"data":{"buttonrun":"resumed"}}
            if (resultlist[1] == 'resumeRun'):
                print ('continue gcode requested')
                app.nonVisibleWidgets.actions.processAction({"data":{"command":"resumeRun","arg":"","arg1":""}})
                message = {"data":{"buttonrun":"resumed"}}
            if (resultlist[1] == 'stopRun'):
                print ('stop gcode requested')
                app.nonVisibleWidgets.actions.processAction({"data":{"command":"stopRun","arg":"","arg1":""}})
                message = {"data":{"butttonrun":"stopped"}}
            if('home' in resultlist):
                print ('go home')
                app.nonVisibleWidgets.actions.processAction({"data":{"command":"home","arg":"","arg1":""}})
                message = {"data":{"buttonmove":"movetoHome"}}
        
        resp = jsonify(message)
        resp.status_code = 200 # or whatever the correct number should be
        return (resp)
    
    if (request.method == "GET"):
        setValues = app.data.config.getJSONSettingSection("GPIO Settings")
        return (jsonify(setValues))
        
@app.route('/LED', methods=['PUT','GET'])
#This is the LED method responds to requests from the button process (every 5 seconds or so) that gets the system state so the LED can be updated in the button service.
#The data consists of the gcode index, the gcode upload flag (upload to the arduino) which indicates it is running or paused or stopped
#The moving flag is for sled moves without "running" gcode
#The 
def getLEDinfo():
    '''
    The MaslowButton.py has provisions for an on-system display.  
    This is the LED method responds MaslowButton.py requests via HTTP/GET
    and processses the repeated inquiry every 2-5 seconds.
    Upload flag signifies system state as running, paused, or stopped,
    Moving flag indicates a stopped cut condition, but the sled is moving
    zmove is the z axis moving    
    ''' 
    if (request.method == 'GET'):
        try:
            message = {"data":{"index": str(app.data.gcodeIndex), \
                "flag": str(app.data.uploadFlag), \
                "moving": str(app.data.sledMoving), \
                "zMove": str(app.data.zMoving), \
                "wiiPendantPresent": str(app.data.config.getValue("Maslow Settings","wiiPendantPresent")), \
                "wiiconnected" : str(app.data.wiiPendantConnected), \
                "clidisplay" : str(app.data.config.getValue("Maslow Settings","clidisplay")), \
                "sled_location_X": str(app.data.xval), \
                "sled_location_y": str(app.data.yval), \
                #"sled_location_z": str(app.data.zval), \
                #This part works
                "home_location_x": str(app.data.config.getValue("Advanced Settings","homeX")), \
                "home_location_y": str(app.data.config.getValue("Advanced Settings","homeY")), \
                #this part does not work
                "gcode_max_x": str(app.data.gcode_x_max), \
                "gcode_min_x": str(app.data.gcode_x_min), \
                "gcode_max_y": str(app.data.gcode_y_max), \
                "gcode_min_y": str(app.data.gcode_y_min)}}  #assemble json string
            #print(message)
            resp = jsonify(message) # java script object notation convrsion of the message
            resp.status_code = 200
            return (resp) # send the message
        except:
            message = jsonify({"data":{"error":"no data"}})  # on error, respond with something rather than nothing
            resp = jsonify(message)
            resp.status_code = 404 # or whatever the correct number should be
            return (resp)
    
@app.route('/pendant', methods=['PUT', 'GET']) # this takes data from a wii control pendant via local onboard bluetooth, though it could be from any web device.
# all calls to this app route from the pendant are routed through localhost:5000 using requests library and either PUT or GET
# sending json dict types did not work, so plain text is parsed by splitting a sent command of  r = requests.put("http://localhost:5000/pendant", "move:up:distance") 
def WiiMoteInput():
    '''
    This is for the raspberry pi
    The MaslowButton.py runs as a separate MaslowPendant.py process
    that interacts with this function via HTTP/PUT
    and this routine interprets those commands from the wii to move Maslow
    '''
    print ("pendant function call")
    result = request.data  #pull off the data parameters
    #print (result)
    result = result.decode('utf-8') # convert the binary data into text
    resultlist = result.split(':')  #take the input and cut it up into list pieces
    print (resultlist)
    message = {"data":{"pendant:selected"}}
    if (len(resultlist) > 2):  # pull off the distance if it is there
        distance = resultlist[2]  # distance is the third list element
    else:
        distance = 0  # if it isn't then put a 0 value in so no error is thrown
    if ('zAxis' in resultlist):  # this command set works with the z axis
        print ('zaxis selected')
        message = {"data":{"z:selected"}}
        if('raise' in resultlist):
            print ('zaxis', distance, 'raise')
            app.nonVisibleWidgets.actions.processAction({"data":{"command":"moveZ","arg":"raise","arg1":distance}})
            message = {"data":{"Z":"raise"}}
        if('lower' in resultlist):
            print ('zaxis', distance, 'lower')
            app.nonVisibleWidgets.actions.processAction({"data":{"command":"moveZ","arg":"lower","arg1":distance}})
            message = {"data":{"Z":"Lower"}}
        if('stopZ' in resultlist):
            print ('zaxis stop')
            app.nonVisibleWidgets.actions.processAction({"data":{"command":"stopZ","arg":"","arg1":""}})
            message = {"data":{"Z":"stopZ"}}
        if('defineZ0' in resultlist):
            print ('new Z axis zero point')
            app.nonVisibleWidgets.actions.processAction({"data":{"command":"defineZ0","arg":"","arg1":""}})
            message = {"data":{"Z":"defineZ"}}  # this command set will move or change the sled
    if ('sled' in resultlist):    
        message = {"data":{"sled":"selected"}}
        if('up' in resultlist):
            print ('move', distance, 'up')
            app.nonVisibleWidgets.actions.processAction({"data":{"command":"move","arg":"up","arg1":distance}})
            message = {"data":{"move":"up"}}
        if('down' in resultlist):
            print ('move', distance, 'down')
            app.nonVisibleWidgets.actions.processAction({"data":{"command":"move","arg":"down","arg1":distance}})
            message = {"data":{"move":"down"}}
        if('left' in resultlist):
            print ('move', distance, 'left')
            app.nonVisibleWidgets.actions.processAction({"data":{"command":"move","arg":"left","arg1":distance}})
            message = {"data":{"move":"left"}}
        if('right' in resultlist):
            print ('move', distance, 'right')
            app.nonVisibleWidgets.actions.processAction({"data":{"command":"move","arg":"right","arg1":distance}})
            message = {"data":{"move":"right"}}
        if('home' in resultlist):
            print ('go home')
            app.nonVisibleWidgets.actions.processAction({"data":{"command":"home","arg":"","arg1":""}})
            message = {"data":{"sled":"movetoHome"}}
        if('defineHome' in resultlist):
            print ('new home set')
            app.nonVisibleWidgets.actions.processAction({"data":{"command":"defineHome","arg":"","arg1":""}})
            message = {"data":{"sled":"NewHome"}}
    if ('gcode' in resultlist): # this command set will start, pause, stop the execution of gcode files
        if (resultlist[1] == 'startRun'):
                print ('start gcode requested')
                app.nonVisibleWidgets.actions.processAction({"data":{"command":"startRun","arg":"","arg1":""}})
                message = {"data":{"pendantrun":"started"}}
        if (resultlist[1] == 'pauseRun'):
            if (app.data.uploadFlag == 1):
                print ('pause gcode requested')
                app.nonVisibleWidgets.actions.processAction({"data":{"command":"pauseRun","arg":"","arg1":""}})
                message = {"data":{"pendantrun":"paused"}}
            elif (app.data.uploadFlag == 2):
                print ('continue gcode requested')
                app.nonVisibleWidgets.actions.processAction({"data":{"command":"resumeRun","arg":"","arg1":""}})
                message = {"data":{"pendantrun":"resumed"}}
        if (resultlist[1] == 'resumeRun'):
            print ('continue gcode requested')
            app.nonVisibleWidgets.actions.processAction({"data":{"command":"resumeRun","arg":"","arg1":""}})
            message = {"data":{"pendantrun":"resumed"}}
        if (resultlist[1] == 'stopRun'):
            print ('stop gcode requested')
            app.nonVisibleWidgets.actions.processAction({"data":{"command":"stopRun","arg":"","arg1":""}})
            message = {"data":{"pendantrun":"stopped"}} 
    if ('system' in resultlist): # this command set will adjust the system including pendant connection status and system power
        print ('system selected')
        message = {"data":{"system":"selected"}}
        if ('exit' in resultlist):
            print("system shutdown requested")
            if (app.data.uploadFlag == 0):
                os._exit(0)
            else:
                app.nonVisiblewidgets.actions.processAction({"data":{"command":"stopRun","arg":"","arg1":""}})
                print("denied: running code.  Code stopped near try again")
                message = {"data":{"system":"shutdownAttempt"}}
        if ('connected' in resultlist):
            print("wiimote connected")
            message = {"data":{"system":"Connect"}}
            app.data.wiiPendantConnected = True
        if ('disconnect' in resultlist):
            print("wiimote disconnect")
            app.data.wiiPendantConnected = False    
            message = {"data":{"system":"Disconnect"}}
    resp = jsonify(message)
    resp.status_code = 200
    return (resp)   

@app.route("/controls")
@mobile_template("/controls/{mobile/}")
def controls(template):
    app.data.logger.resetIdler()
    macro1Title = (app.data.config.getValue("Maslow Settings", "macro1_title"))[:6]
    macro2Title = (app.data.config.getValue("Maslow Settings", "macro2_title"))[:6]
    if template == "/controls/mobile/":
        return render_template("frontpage3d_mobilecontrols.html", modalStyle="modal-lg", isControls=True, macro1_title=macro1Title,  macro2_title=macro2Title)
    else:
        return render_template("frontpage3d.html", modalStyle="mw-100 w-75", macro1_title=macro1Title,  macro2_title=macro2Title)

@app.route("/text")
@mobile_template("/text/{mobile/}")
def text(template):
    app.data.logger.resetIdler()
    macro1Title = (app.data.config.getValue("Maslow Settings", "macro1_title"))[:6]
    macro2Title = (app.data.config.getValue("Maslow Settings", "macro2_title"))[:6]
    if template == "/text/mobile":
        return render_template("frontpageText_mobile.html", modalStyle="modal-lg", isControls=True, macro1_title=macro1Title,  macro2_title=macro2Title)
    else:
        return render_template("frontpageText.html", modalStyle="mw-100 w-75", macro1_title=macro1Title,  macro2_title=macro2Title)

@app.route("/logs")
@mobile_template("/logs/{mobile/}")
def logs(template):
    print("here")
    app.data.logger.resetIdler()
    if template == "/logs/mobile/":
        return render_template("logs.html")
    else:
        return render_template("logs.html")


@app.route("/maslowSettings", methods=["POST"])
def maslowSettings():
    app.data.logger.resetIdler()
    if request.method == "POST":
        result = request.form
        app.data.config.updateSettings("Maslow Settings", result)
        message = {"status": 200}
        resp = jsonify(message)
        resp.status_code = 200
        return resp


@app.route("/advancedSettings", methods=["POST"])
def advancedSettings():
    app.data.logger.resetIdler()
    if request.method == "POST":
        result = request.form
        app.data.config.updateSettings("Advanced Settings", result)
        message = {"status": 200}
        resp = jsonify(message)
        resp.status_code = 200
        return resp


@app.route("/webControlSettings", methods=["POST"])
def webControlSettings():
    app.data.logger.resetIdler()
    if request.method == "POST":
        result = request.form
        app.data.config.updateSettings("WebControl Settings", result)
        message = {"status": 200}
        resp = jsonify(message)
        resp.status_code = 200
        return resp


@app.route("/cameraSettings", methods=["POST"])
def cameraSettings():
    app.data.logger.resetIdler()
    if request.method == "POST":
        result = request.form
        app.data.config.updateSettings("Camera Settings", result)
        message = {"status": 200}
        resp = jsonify(message)
        resp.status_code = 200
        return resp

@app.route("/gpioSettings", methods=["POST"])
def gpioSettings():
    '''
    This is called when the GPIO settings from the menu are changed.  The button service must be restarted so the buttons are initialized correctly and useable.
    '''
    app.data.logger.resetIdler()
    if request.method == "POST":
        result = request.form
        app.data.config.updateSettings("GPIO Settings", result)
        message = {"status": 200}
        resp = jsonify(message)
        resp.status_code = 200
        # restart button service here
        # this button service resets the button maps for the updated gpio pins
        print("restarting maslow button service") 
        try:
            self.home = str(Path.home())
            subprocess.run([self.home+'/Webcontrol/Services/MaslowButtonRestart.sh'])
            print("restarted maslow button service")
        except:
            print("error restarting button service")
        return resp
        
@app.route("/ledSettings", methods=["POST"])
def ledSettings():
    '''
    This is called when the LED settings from the menu are changed.
    '''
    app.data.logger.resetIdler()
    #if app.data.platform == "RPI": #for raspberry pi ONLY commands
    if request.method == "POST":
        result = request.form
        app.data.config.updateSettings("LED Settings", result)
        message = {"status": 200}
        resp = jsonify(message)
        resp.status_code = 200
        print("Updated LED settings webcontrol.json") 
    return resp
def sc_filename(self, filename):
    if isinstance(filename, text_type):
        from unicodedata import normalize
        filename = normalize('NFKD', filename).encode('utf-8', 'ignore')
        filename = filename.decode('utf-8')
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, ' ')
    filename = str(_filename_gbk_strip_re.sub('', '_'.join(
        filename.split()))).strip('._')

    if os.name == 'nt' and filename and \
       filename.split('.')[0].upper() in _windows_device_files:
        filename = '_' + filename
    return filename 

@app.route("/uploadGCode", methods=["POST"])
def uploadGCode():
    app.data.logger.resetIdler()
    if request.method == "POST":
        print("------ in POST processor in main.py")
        #result = request.form["gcodeForm"]
        result = request.form
        print("----- form pull", result)
        directory = result["selectedDirectory"]
        print("-----results: ",result)
        #print(directory)
        uploaded_files = request.files.getlist("file[]")
        for file in uploaded_files:
            print('file name :',file)
            if file.filename !='':
                home = app.data.config.getHome()
                app.data.gcodeFile.filename = home+"/.WebControl/gcode/" + directory+"/"+secure_filename(file.filename)
                file.save(app.data.gcodeFile.filename)
        returnVal = app.data.gcodeFile.loadUpdateFile()
        if returnVal:
            message = {"status": 200}
            resp = jsonify(message)
            resp.status_code = 200
            return resp
        else:
            message = {"status": 500}
            resp = jsonify(message)
            resp.status_code = 500
            return resp

@app.route("/cleanGcode", methods=["POST"])
def cleanGcode():
    app.data.logger.resetIdler()
    if request.method == "POST":
        f = request.form["gcodeForm"]
        print('Post in from gcode Clean')
        print('----- data in from form = ', f)
        print('data in f :',f.data)
        uploaded_files = request.files.getlist("file[]")
        minimize = request.data.getlist('minimize')
        for file in uploaded_files:
            print('file name :',file)
            if file.filename !='':
                home = app.data.config.getHome()
                app.data.gcodeFile.filename = home+"/.WebControl/gcode/" + directory+"/"+secure_filename(file.filename)
                print('filename: ',app.data.gcodeFile.filename)
                gcodecleanFile = app.data.gcodeFile.filename
                print('gcodefilename: ',gcodecleanFile)
        
        ''''
        app.data.console_queue.put("selectedGcode="+str(f))
        tDir = f.split("/")
        app.data.config.setValue("Computed Settings","lastSelectedDirectory",tDir[0])
        home = app.data.config.getHome()
        app.data.gcodeFile.filename = home+"/.WebControl/gcode/" + f
        app.data.config.setValue("Maslow Settings", "gcodecleanFile", tDir[1])
        print("------ in POST processor in main.py")
        #result = request.form["gcodeForm"]
        result = request.form
        print("----- form pull", result)
        directory = result["selectedDirectory"]
        print("-----results: ",result)
        #print(directory)
        uploaded_files = request.files.getlist("file[]")
        
                file.save(app.data.gcodeFile.filename)
        '''
        returnVal = app.data.gcodeFile.cleangcodeFile(gcodecleanFile)
        if returnVal:
            message = {"status": 200}
            resp = jsonify(message)
            resp.status_code = 200
            return resp
        else:
            message = {"status": 500}
            resp = jsonify(message)
            resp.status_code = 500
            return resp
            
@app.route("/openGCode", methods=["POST"])
def openGCode():
    app.data.logger.resetIdler()
    if request.method == "POST":
        #get data from the form / web page
        f = request.form["selectedGCode"]
        print("f: ",f)
        app.data.console_queue.put("selectedGcode="+str(f))
        tDir = f.split("/")
        print("tDir: ",tDir)
        app.data.config.setValue("Computed Settings","lastSelectedDirectory",tDir[0])
        home = app.data.config.getHome()
        app.data.gcodeFile.filename = home+"/.WebControl/gcode/" + f
        #set the file name
        app.data.config.setValue("Maslow Settings", "openFile", tDir[1])
        # load the file
        returnVal = app.data.gcodeFile.loadUpdateFile()
        if returnVal:
            message = {"status": 200}
            resp = jsonify(message)
            resp.status_code = 200
            return resp
        else:
            message = {"status": 500}
            resp = jsonify(message)
            resp.status_code = 500
            return resp

@app.route("/saveGCode", methods=["POST"])
def saveGCode():
    app.data.logger.resetIdler()
    if request.method == "POST":
        print(request.form)
        f = request.form["fileName"]
        d = request.form["selectedDirectory"]
        app.data.console_queue.put("selectedGcode="+f)
        app.data.config.setValue("Computed Settings", "lastSelectedDirectory",d)
        home = app.data.config.getHome()
        returnVal = app.data.gcodeFile.saveFile(f, home+"/.WebControl/gcode/"+d)
        '''
        tDir = f.split("/")
        app.data.config.setValue("Computed Settings","lastSelectedDirectory",tDir[0])
        home = app.data.config.getHome()
        app.data.gcodeFile.filename = home+"/.WebControl/gcode/" + f
        app.data.config.setValue("Maslow Settings", "openFile", tDir[1])
        returnVal = app.data.gcodeFile.loadUpdateFile()
        '''
        if returnVal:
            app.data.config.setValue("Maslow Settings", "openFile", f)
            message = {"status": 200}
            resp = jsonify(message)
            resp.status_code = 200
            return resp
        else:
            message = {"status": 500}
            resp = jsonify(message)
            resp.status_code = 500
            return resp

@app.route("/openBoard", methods=["POST"])
def openBoard():
    app.data.logger.resetIdler()
    if request.method == "POST":
        f = request.form["selectedBoard"]
        app.data.console_queue.put("selectedBoard="+str(f))
        tDir = f.split("/")
        app.data.config.setValue("Computed Settings","lastSelectedBoardDirectory",tDir[0])
        home = app.data.config.getHome()
        app.data.gcodeFile.filename = home+"/.WebControl/boards/" + f
        app.data.config.setValue("Maslow Settings", "openBoardFile", tDir[1])
        returnVal = app.data.boardManager.loadBoard(home+"/.WebControl/boards/"+f)
        if returnVal:
            message = {"status": 200}
            resp = jsonify(message)
            resp.status_code = 200
            return resp
        else:
            message = {"status": 500}
            resp = jsonify(message)
            resp.status_code = 500
            return resp

@app.route("/saveBoard", methods=["POST"])
def saveBoard():
    app.data.logger.resetIdler()
    if request.method == "POST":
        print(request.form)
        f = request.form["fileName"]
        d = request.form["selectedDirectory"]
        app.data.console_queue.put("selectedBoard="+f)
        app.data.config.setValue("Computed Settings", "lastSelectedBoardDirectory",d)
        home = app.data.config.getHome()
        returnVal = app.data.boardManager.saveBoard(f, home+"/.WebControl/boards/"+d)
        app.data.config.setValue("Maslow Settings", "openBoardFile", f)
        if returnVal:
            message = {"status": 200}
            resp = jsonify(message)
            resp.status_code = 200
            return resp
        else:
            message = {"status": 500}
            resp = jsonify(message)
            resp.status_code = 500
            return resp


@app.route("/importFile", methods=["POST"])
def importFile():
    app.data.logger.resetIdler()
    if request.method == "POST":
        f = request.files["file"]
        home = app.data.config.getHome()
        secureFilename = home+"/.WebControl/imports/" + secure_filename(f.filename)
        f.save(secureFilename)
        returnVal = app.data.importFile.importGCini(secureFilename)
        if returnVal:
            message = {"status": 200}
            resp = jsonify(message)
            resp.status_code = 200
            return resp
        else:
            message = {"status": 500}
            resp = jsonify(message)
            resp.status_code = 500
            return resp

@app.route("/importFileWCJSON", methods=["POST"])
def importFileJSON():
    app.data.logger.resetIdler()
    if request.method == "POST":
        f = request.files["file"]
        home = app.data.config.getHome()
        secureFilename = home + "/.WebControl/imports/" + secure_filename(f.filename)
        f.save(secureFilename)
        returnVal = app.data.importFile.importWebControlJSON(secureFilename)
        if returnVal:
            message = {"status": 200}
            resp = jsonify(message)
            resp.status_code = 200
            return resp
        else:
            message = {"status": 500}
            resp = jsonify(message)
            resp.status_code = 500
            return resp

@app.route("/importRestoreWebControl", methods=["POST"])
def importRestoreWebControl():
    app.data.logger.resetIdler()
    if request.method == "POST":
        f = request.files["file"]
        home = app.data.config.getHome()
        secureFilename = home + "/" + secure_filename(f.filename)
        f.save(secureFilename)
        returnVal = app.data.actions.restoreWebControl(secureFilename)
        if returnVal:
            message = {"status": 200}
            resp = jsonify(message)
            resp.status_code = 200
            return resp
        else:
            message = {"status": 500}
            resp = jsonify(message)
            resp.status_code = 500
            return resp

@app.route("/sendGCode", methods=["POST"])
def sendGcode():
    app.data.logger.resetIdler()
    #print(request.form)#["gcodeInput"])
    if request.method == "POST":
        returnVal = app.data.actions.sendGCode(request.form["gcode"].rstrip())
        if returnVal:
            message = {"status": 200}
            resp = jsonify("success")
            resp.status_code = 200
            return resp
        else:
            message = {"status": 500}
            resp = jsonify("failed")
            resp.status_code = 500
            return resp


@app.route("/triangularCalibration", methods=["POST"])
def triangularCalibration():
    app.data.logger.resetIdler()
    if request.method == "POST":
        result = request.form
        motorYoffsetEst, rotationRadiusEst, chainSagCorrectionEst, cut34YoffsetEst = app.data.actions.calibrate(
            result
        )
        # print(returnVal)
        if motorYoffsetEst:
            message = {
                "status": 200,
                "data": {
                    "motorYoffset": motorYoffsetEst,
                    "rotationRadius": rotationRadiusEst,
                    "chainSagCorrection": chainSagCorrectionEst,
                    "calibrationError": cut34YoffsetEst,
                },
            }
            resp = jsonify(message)
            resp.status_code = 200
            return resp
        else:
            message = {"status": 500}
            resp = jsonify(message)
            resp.status_code = 500
            return resp

@app.route("/holeyCalibration", methods=["POST"])
def holeyCalibration():
    app.data.logger.resetIdler()
    if request.method == "POST":
        result = request.form
        motorYoffsetEst, distanceBetweenMotors, leftChainTolerance, rightChainTolerance, calibrationError = app.data.actions.holeyCalibrate(
            result
        )
        # print(returnVal)
        if motorYoffsetEst:
            message = {
                "status": 200,
                "data": {
                    "motorYoffset": motorYoffsetEst,
                    "distanceBetweenMotors": distanceBetweenMotors,
                    "leftChainTolerance": leftChainTolerance,
                    "rightChainTolerance": rightChainTolerance,
                    "calibrationError": calibrationError
                },
            }
            resp = jsonify(message)
            resp.status_code = 200
            return resp
        else:
            message = {"status": 500}
            resp = jsonify(message)
            resp.status_code = 500
            return resp

@app.route("/opticalCalibration", methods=["POST"])
def opticalCalibration():
    app.data.logger.resetIdler()
    if request.method == "POST":
        result = request.form
        message = {"status": 200}
        resp = jsonify(message)
        resp.status_code = 200
        return resp
    else:
        message = {"status": 500}
        resp = jsonify(message)
        resp.status_code = 500
        return resp


@app.route("/quickConfigure", methods=["POST"])
def quickConfigure():
    app.data.logger.resetIdler()
    if request.method == "POST":
        result = request.form
        app.data.config.updateQuickConfigure(result)
        message = {"status": 200}
        resp = jsonify(message)
        resp.status_code = 200
        return resp

@app.route("/editGCode", methods=["POST"])
def editGCode():
    app.data.logger.resetIdler()
    #print(request.form["gcode"])
    if request.method == "POST":
        returnVal = app.data.actions.updateGCode(request.form["gcode"].rstrip())
        if returnVal:
            message = {"status": 200}
            resp = jsonify("success")
            resp.status_code = 200
            return resp
        else:
            message = {"status": 500}
            resp = jsonify("failed")
            resp.status_code = 500
            return resp

@app.route("/downloadDiagnostics", methods=["GET"])
def downloadDiagnostics():
    app.data.logger.resetIdler()
    if request.method == "GET":
        returnVal = app.data.actions.downloadDiagnostics()
        if  returnVal != False:
            print(returnVal)
            return send_file(returnVal, as_attachment=True)
        else:
            resp = jsonify("failed")
            resp.status_code = 500
            return resp

@app.route("/backupWebControl", methods=["GET"])
def backupWebControl():
    app.data.logger.resetIdler()
    if request.method == "GET":
        returnVal = app.data.actions.backupWebControl()
        if returnVal != False:
            print(returnVal)
            return send_file(returnVal)
        else:
            resp = jsonify("failed")
            resp.status_code = 500
            return resp


@app.route("/editBoard", methods=["POST"])
def editBoard():
    app.data.logger.resetIdler()
    if request.method == "POST":
        returnVal = app.data.boardManager.editBoard(request.form)
        if returnVal:
            resp = jsonify("success")
            resp.status_code = 200
            return resp
        else:
            resp = jsonify("failed")
            resp.status_code = 500
            return resp

@app.route("/trimBoard", methods=["POST"])
def trimBoard():
    app.data.logger.resetIdler()
    if request.method == "POST":
        returnVal = app.data.boardManager.trimBoard(request.form)
        if returnVal:
            resp = jsonify("success")
            resp.status_code = 200
            return resp
        else:
            resp = jsonify("failed")
            resp.status_code = 500
            return resp

@app.route("/assets/<path:path>")
def sendDocs(path):
    print(path)
    return send_from_directory('docs/assets/', path)


@socketio.on("checkInRequested", namespace="/WebMCP")
def checkInRequested():
    socketio.emit("checkIn", namespace="/WebMCP")


@socketio.on("connect", namespace="/WebMCP")
def watchdog_connect():
    app.data.console_queue.put("watchdog connected")
    app.data.console_queue.put(request.sid)
    socketio.emit("connect", namespace="/WebMCP")
    if app.mcpthread == None:
        app.data.console_queue.put("going to start mcp thread")
        app.mcpthread = socketio.start_background_task(
            app.data.mcpProcessor.start, current_app._get_current_object()
        )
        app.data.console_queue.put("created mcp thread")
        app.mcpthread.start()
        app.data.console_queue.put("started mcp thread")


@socketio.on("my event", namespace="/MaslowCNC")
def my_event(msg):
    app.data.console_queue.put(msg["data"])


@socketio.on("modalClosed", namespace="/MaslowCNC")
def modalClosed(msg):
    app.data.logger.resetIdler()
    data = json.dumps({"title": msg["data"]})
    socketio.emit("message", {"command": "closeModals", "data": data, "dataFormat": "json"},
                  namespace="/MaslowCNC", )


@socketio.on("contentModalClosed", namespace="/MaslowCNC")
def contentModalClosed(msg):
    #Note, this shouldn't be called anymore
    #todo: cleanup
    app.data.logger.resetIdler()
    data = json.dumps({"title": msg["data"]})
    print(data)
    #socketio.emit("message", {"command": "closeContentModals", "data": data, "dataFormat": "json"},
    #              namespace="/MaslowCNC", )

'''
todo: cleanup
not used
@socketio.on("actionModalClosed", namespace="/MaslowCNC")
def actionModalClosed(msg):
    app.data.logger.resetIdler()
    data = json.dumps({"title": msg["data"]})
    socketio.emit("message", {"command": "closeActionModals", "data": data, "dataFormat": "json"},
                  namespace="/MaslowCNC", )
'''

@socketio.on("alertModalClosed", namespace="/MaslowCNC")
def alertModalClosed(msg):
    app.data.logger.resetIdler()
    data = json.dumps({"title": msg["data"]})
    socketio.emit("message", {"command": "closeAlertModals", "data": data, "dataFormat": "json"},
                  namespace="/MaslowCNC", )


@socketio.on("requestPage", namespace="/MaslowCNC")
def requestPage(msg):
    app.data.logger.resetIdler()
    app.data.console_queue.put(request.sid)
    client = request.sid
    try:
        page, title, isStatic, modalSize, modalType, resume = app.webPageProcessor.createWebPage(msg["data"]["page"],msg["data"]["isMobile"], msg["data"]["args"])
        #if msg["data"]["page"] != "help":
        #    client = "all"
        data = json.dumps({"title": title, "message": page, "isStatic": isStatic, "modalSize": modalSize, "modalType": modalType, "resume":resume, "client":client})
        socketio.emit("message", {"command": "activateModal", "data": data, "dataFormat": "json"},
            namespace="/MaslowCNC",
        )
    except Exception as e:
        app.data.console_queue.put(e)

@socketio.on("connect", namespace="/MaslowCNC")
def test_connect():
    app.data.console_queue.put("connected")
    app.data.console_queue.put(request.sid)
    if app.uithread == None:
        app.uithread = socketio.start_background_task(
            app.UIProcessor.start, current_app._get_current_object()
        )
        app.uithread.start()

    if not app.data.connectionStatus:
        app.data.console_queue.put("Attempting to re-establish connection to controller")
        app.data.serialPort.openConnection()

    socketio.emit("my response", {"data": "Connected", "count": 0})
    address = app.data.hostAddress
    data = json.dumps({"hostAddress": address})
    print(data)
    socketio.emit("message", {"command": "hostAddress", "data": data, "dataFormat":"json"}, namespace="/MaslowCNC",)
    if app.data.pyInstallUpdateAvailable:
        app.data.ui_queue1.put("Action", "pyinstallUpdate", "on")

@socketio.on("disconnect", namespace="/MaslowCNC")
def test_disconnect():
    app.data.console_queue.put("Client disconnected")


@socketio.on("action", namespace="/MaslowCNC")
def command(msg):
    app.data.logger.resetIdler()
    retval = app.data.actions.processAction(msg)
    if retval == "Shutdown":
        print("Shutting Down")
        socketio.stop()
        print("Shutdown")
    if (retval == "TurnOffRPI"):
        print("Turning off RPI")
        os.system('sudo poweroff')

@socketio.on("settingRequest", namespace="/MaslowCNC")
def settingRequest(msg):
    app.data.logger.resetIdler()
    # didn't move to actions.. this request is just to send it computed values.. keeping it here makes it faster than putting it through the UIProcessor
    setting, value = app.data.actions.processSettingRequest(msg["data"]["section"], msg["data"]["setting"])
    if setting is not None:
        data = json.dumps({"setting": setting, "value": value})
        socketio.emit("message", {"command": "requestedSetting", "data": data, "dataFormat": "json"}, namespace="/MaslowCNC",)

@socketio.on("updateSetting", namespace="/MaslowCNC")
def updateSetting(msg):
    app.data.logger.resetIdler()
    if not app.data.actions.updateSetting(msg["data"]["setting"], msg["data"]["value"]):
        app.data.ui_queue1.put("Alert", "Alert", "Error updating setting")


@socketio.on("checkForGCodeUpdate", namespace="/MaslowCNC")
def checkForGCodeUpdate(msg):
    app.data.logger.resetIdler()
    # this currently doesn't check for updated gcode, it just resends it..
    ## the gcode file might change the active units so we need to inform the UI of the change.
    app.data.ui_queue1.put("Action", "unitsUpdate", "")
    app.data.ui_queue1.put("Action", "gcodeUpdate", "")

@socketio.on("checkForBoardUpdate", namespace="/MaslowCNC")
def checkForBoardUpdate(msg):
    app.data.logger.resetIdler()
    # this currently doesn't check for updated board, it just resends it..
    app.data.ui_queue1.put("Action", "boardUpdate", "")

@socketio.on("connect", namespace="/MaslowCNCLogs")
def log_connect():
    app.data.console_queue.put("connected to log")
    app.data.console_queue.put(request.sid)
    if app.logstreamerthread == None:
        app.logstreamerthread = socketio.start_background_task(
            app.LogStreamer.start, current_app._get_current_object()
        )
        app.logstreamerthread.start()

    socketio.emit("my response", {"data": "Connected", "count": 0}, namespace="/MaslowCNCLog")

@socketio.on("disconnect", namespace="/MaslowCNCLogs")
def log_disconnect():
    app.data.console_queue.put("Client disconnected")


@app.template_filter('isnumber')
def isnumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
        
#def shutdown():
#    print("Shutdown")


if __name__ == "__main__":
    app.debug = False
    app.config["SECRET_KEY"] = "secret!"
    #look for touched file
    app.data.config.checkForTouchedPort()
    webPort = app.data.config.getWebPortNumber()
    print("-$$$$$-")
    print(os.path.abspath(__file__))
    app.data.releaseManager.processAbsolutePath(os.path.abspath(__file__))
    print("-$$$$$-")


    print("opening browser")
    portstring = "http://localhost:"+webPort
    webbrowser.open_new_tab(portstring)
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    app.data.hostAddress = host_ip + ":" + webPort
    
    if app.data.platform == "RPI":
        app.data.GPIOButtonService = app.data.config.getValue("Maslow Settings","MaslowButtonService")
        # start button service next to last : this launches a separate button script NOT a Thread
        if (app.data.GPIOButtonService):
            print("starting Maslow GPIO button service")
            app.home = str(os.path.home())
            subprocess.run(app.home+'/Services/MaslowButtonStart.sh')
            #app.data.config.buttonSubProcess('start')

    # app.data.shutdown = shutdown
    socketio.run(app, use_reloader=False, host="0.0.0.0", port=int(webPort))
    # socketio.run(app, host='0.0.0.0')

