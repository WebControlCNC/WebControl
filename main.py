# main.py
from app import app, socketio
from gevent import monkey

monkey.patch_all()

import schedule
import time
import threading
import json

from flask import Flask, jsonify, render_template, current_app, request, flash
from flask_mobility.decorators import mobile_template
from werkzeug import secure_filename
from Background.UIProcessor import UIProcessor  # do this after socketio is declared
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
app.data.units = app.data.config.getValue("Computed Settings", "units")
app.data.comport = app.data.config.getValue("Maslow Settings", "COMport")
app.data.gcodeShift = [
    float(app.data.config.getValue("Advanced Settings", "homeX")),
    float(app.data.config.getValue("Advanced Settings", "homeY")),
]
app.data.firstRun = False
# app.previousPosX = 0.0
# app.previousPosY = 0.0

app.UIProcessor = UIProcessor()
app.webPageProcessor = WebPageProcessor(app.data)

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

@app.route("/")
@mobile_template("{mobile/}")
def index(template):
    current_app._get_current_object()
    if template == "mobile/":
        return render_template("frontpage_mobile.html", modalStyle="modal-lg")
    else:
        return render_template("frontpage.html", modalStyle="mw-100 w-75")


@app.route("/maslowSettings", methods=["POST"])
def maslowSettings():
    if request.method == "POST":
        result = request.form
        app.data.config.updateSettings("Maslow Settings", result)
        message = {"status": 200}
        resp = jsonify(message)
        resp.status_code = 200
        print("here")
        return resp


@app.route("/advancedSettings", methods=["POST"])
def advancedSettings():
    if request.method == "POST":
        result = request.form
        app.data.config.updateSettings("Advanced Settings", result)
        message = {"status": 200}
        resp = jsonify(message)
        resp.status_code = 200
        return resp


@app.route("/webControlSettings", methods=["POST"])
def webControlSettings():
    if request.method == "POST":
        result = request.form
        app.data.config.updateSettings("WebControl Settings", result)
        message = {"status": 200}
        resp = jsonify(message)
        resp.status_code = 200
        return resp


@app.route("/uploadGCode", methods=["POST"])
def uploadGCode():
    if request.method == "POST":
        f = request.files["file"]
        app.data.gcodeFile.filename = "gcode/" + secure_filename(f.filename)
        f.save(app.data.gcodeFile.filename)
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


@app.route("/openGCode", methods=["POST"])
def openGCode():
    if request.method == "POST":
        f = request.form["selectedGCode"]
        app.data.console_queue.put("selectedGcode="+str(f))
        app.data.gcodeFile.filename = "gcode/" + f
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


@app.route("/importFile", methods=["POST"])
def importFile():
    if request.method == "POST":
        f = request.files["file"]
        secureFilename = "imports\\" + secure_filename(f.filename)
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


@app.route("/triangularCalibration", methods=["POST"])
def triangularCalibration():
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


@app.route("/opticalCalibration", methods=["POST"])
def opticalCalibration():
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
    if request.method == "POST":
        result = request.form
        app.data.config.updateQuickConfigure(result)
        message = {"status": 200}
        resp = jsonify(message)
        resp.status_code = 200
        return resp

#Watchdog socketio.. not working yet.
@socketio.on("checkInRequested", namespace="/WebMCP")
def checkInRequested():
    socketio.emit("checkIn", namespace="/WebMCP")
    #print("sent checkIn")

#Watchdog socketio.. not working yet.
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
    socketio.emit("closeModals", {"data": {"title": msg["data"]}}, namespace="/MaslowCNC")


@socketio.on("contentModalClosed", namespace="/MaslowCNC")
def contentModalClosed(msg):
    socketio.emit("closeContentModals", {"data": {"title": msg["data"]}}, namespace="/MaslowCNC")


@socketio.on("actionModalClosed", namespace="/MaslowCNC")
def actionModalClosed(msg):
    socketio.emit("closeActionModals", {"data": {"title": msg["data"]}}, namespace="/MaslowCNC")


@socketio.on("requestPage", namespace="/MaslowCNC")
def requestPage(msg):
    try:
        page, title, isStatic, modalSize, modalType = app.webPageProcessor.createWebPage(msg["data"]["page"],msg["data"]["isMobile"])
        socketio.emit(
            "activateModal",
            {"title": title, "message": page, "isStatic": isStatic, "modalSize": modalSize, "modalType": modalType},
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
        app.data.serialPort.openConnection()

    socketio.emit("my response", {"data": "Connected", "count": 0})


@socketio.on("disconnect", namespace="/MaslowCNC")
def test_disconnect():
    app.data.console_queue.put("Client disconnected")


@socketio.on("action", namespace="/MaslowCNC")
def command(msg):
    app.data.actions.processAction(msg)


@socketio.on("settingRequest", namespace="/MaslowCNC")
def settingRequest(msg):
    # didn't move to actions.. this request is just to send it computed values.. keeping it here makes it faster than putting it through the UIProcessor
    setting, value = app.data.actions.processSettingRequest(msg["data"]["section"],msg["data"]["setting"])
    if setting is not None:
        socketio.emit(
            "requestedSetting",
            {"setting": setting, "value": value},
            namespace="/MaslowCNC",
        )

@socketio.on("updateSetting", namespace="/MaslowCNC")
def updateSetting(msg):
    if not app.data.actions.updateSetting(msg["data"]["setting"], msg["data"]["value"]):
        app.data.ui_queue.put("Message: Error updating setting")


@socketio.on("checkForGCodeUpdate", namespace="/MaslowCNC")
def checkForGCodeUpdate(msg):
    # this currently doesn't check for updated gcode, it just resends it..
    ## the gcode file might change the active units so we need to inform the UI of the change.
    app.data.console_queue.put("Check for GCode Update Received")
    units = app.data.config.getValue("Computed Settings", "units")
    socketio.emit(
        "requestedSetting", {"setting": "units", "value": units}, namespace="/MaslowCNC"
    )
    ## send updated gcode to UI
    app.data.console_queue.put("Sending Gcode compressed")
    socketio.emit("gcodeUpdateCompressed", {"data":app.data.compressedGCode}, namespace="/MaslowCNC")
    app.data.console_queue.put("Sent Gcode compressed")
    #socketio.emit(
    #    "gcodeUpdate",
    #    {"data": json.dumps([ob.__dict__ for ob in app.data.gcodeFile.line])},
    #    namespace="/MaslowCNC",
    #)


@socketio.on_error_default
def default_error_handler(e):
    app.data.console_queue.put(request.event["message"])  # "my error event"
    app.data.console_queue.put(request.event["args"])  # (data,)1


if __name__ == "__main__":
    app.debug = False
    app.config["SECRET_KEY"] = "secret!"
    socketio.run(app, use_reloader=False, host="0.0.0.0")
    # socketio.run(app, host='0.0.0.0')
