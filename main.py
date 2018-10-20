# main.py
from app import app, socketio

from gevent import monkey

monkey.patch_all()

import schedule
import time
import threading
import json
import re
import queue
from threading import Thread
from flask import Flask, jsonify, render_template, current_app, request, flash
from flask_mobility import Mobility
from flask_mobility.decorators import mobile_template
from flask_socketio import SocketIO
from werkzeug import secure_filename

from background.backgroundTasks import (
    background_stuff,
)  # do this after socketio is declared

# from background.scheduler           import    ScheduleThread
from DataStructures.data import Data
from Connection.serialPort import SerialPort
from config.config import Config
from DataStructures.logger import Logger
from DataStructures.loggingQueue import LoggingQueue
from Connection.nonVisibleWidgets import NonVisibleWidgets
from Actions.actions import Actions


app.data = Data()
app.nonVisibleWidgets = NonVisibleWidgets()
app.nonVisibleWidgets.setUpData(app.data)
app.data.config.computeSettings(None, None, None, True)
app.data.units = app.data.config.getValue("Computed Settings", "units")
app.data.comport = app.data.config.getValue("Maslow Settings", "COMport")
if app.data.units == "INCHES":
    scale = 1.0
else:
    scale = 25.4
app.data.gcodeShift = [
    float(app.data.config.getValue("Advanced Settings", "homeX")) / scale,
    float(app.data.config.getValue("Advanced Settings", "homeY")) / scale,
]
app.previousPosX = 0.0
app.previousPosY = 0.0

## this runs the scheduler
def run_schedule():
    while 1:
        schedule.run_pending()
        time.sleep(1)


app.th = threading.Thread(target=run_schedule)
app.th.daemon = True
app.th.start()

# write settings file to disk:
# from settings import settings
# settings = settings.getJSONSettings()
# with open('webcontrol.json', 'w') as outfile:
#    json.dump(settings,outfile, sort_keys=True, indent=4, ensure_ascii=False)

# read settings file from disk:


@app.route("/")
@mobile_template("{mobile/}")
def index(template):
    # print template
    current_app._get_current_object()
    thread = socketio.start_background_task(
        background_stuff, current_app._get_current_object()
    )
    thread.start()
    # if not app.data.connectionStatus:
    #    app.data.serialPort.openConnection()
    if template == "mobile/":
        return render_template("frontpage_mobile.html")
    else:
        return render_template("frontpage.html")


@app.route("/maslowSettings", methods=["POST"])
def maslowSettings():
    if request.method == "POST":
        result = request.form
        app.data.config.updateSettings("Maslow Settings", result)
        # setValues = app.data.config.getJSONSettingSection("Maslow Settings")
        message = {"status": 200}
        resp = jsonify(message)
        resp.status_code = 200
        return resp


@app.route("/advancedSettings", methods=["POST"])
def advancedSettings():
    if request.method == "POST":
        result = request.form
        app.data.config.updateSettings("Advanced Settings", result)
        # setValues = app.data.config.getJSONSettingSection("Advanced Settings")
        message = {"status": 200}
        resp = jsonify(message)
        resp.status_code = 200
        return resp


@app.route("/webControlSettings", methods=["POST"])
def webControlSettings():
    if request.method == "POST":
        result = request.form
        app.data.config.updateSettings("WebControl Settings", result)
        # setValues = app.data.config.getJSONSettingSection("WebControl Settings")
        message = {"status": 200}
        resp = jsonify(message)
        resp.status_code = 200
        return resp


@app.route("/gcode", methods=["POST"])
def gcode():
    if request.method == "POST":
        f = request.files["file"]
        app.data.gcodeFile.filename = "gcode\\" + secure_filename(f.filename)
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
        message = {
            "status":200,
        }
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


@socketio.on("my event", namespace="/MaslowCNC")
def my_event(msg):
    print(msg["data"])


@socketio.on("requestPage", namespace="/MaslowCNC")
def requestPage(msg):
    if msg["data"]["page"] == "maslowSettings":
        setValues = app.data.config.getJSONSettingSection("Maslow Settings")
        # because this page allows you to select the comport from a list that is not stored in webcontrol.json, we need to package and send the list of comports
        # Todo:? change it to store the list?
        ports = app.data.comPorts
        if msg["data"]["isMobile"]:
            page = render_template(
                "settings_mobile.html",
                title="Maslow Settings",
                settings=setValues,
                ports=ports,
                pageID="maslowSettings",
            )
        else:
            page = render_template(
                "settings.html",
                title="Maslow Settings",
                settings=setValues,
                ports=ports,
                pageID="maslowSettings",
            )
            print("here3")
        socketio.emit(
            "activateModal",
            {"title": "Maslow Settings", "message": page},
            namespace="/MaslowCNC",
        )
    elif msg["data"]["page"] == "advancedSettings":
        setValues = app.data.config.getJSONSettingSection("Advanced Settings")
        if msg["data"]["isMobile"]:
            page = render_template(
                "settings_mobile.html",
                title="Advanced Settings",
                settings=setValues,
                pageID="advancedSettings",
            )
        else:
            page = render_template(
                "settings.html",
                title="Advanced Settings",
                settings=setValues,
                pageID="advancedSettings",
            )
        socketio.emit(
            "activateModal",
            {"title": "Advanced Settings", "message": page},
            namespace="/MaslowCNC",
        )
    elif msg["data"]["page"] == "webControlSettings":
        setValues = app.data.config.getJSONSettingSection("WebControl Settings")
        if msg["data"]["isMobile"]:
            page = render_template(
                "settings_mobile.html",
                title="WebControl Settings",
                settings=setValues,
                pageID="webControlSettings",
            )
        else:
            page = render_template(
                "settings.html",
                title="WebControl Settings",
                settings=setValues,
                pageID="webControlSettings",
            )
        socketio.emit(
            "activateModal",
            {"title": "WebControl Settings", "message": page},
            namespace="/MaslowCNC",
        )
    elif msg["data"]["page"] == "openGCode":
        page = render_template("openGCode.html")
        socketio.emit(
            "activateModal", {"title": "GCode", "message": page}, namespace="/MaslowCNC"
        )
    elif msg["data"]["page"] == "importGCini":
        page = render_template("importFile.html")
        socketio.emit(
            "activateModal",
            {"title": "Import File", "message": page},
            namespace="/MaslowCNC",
        )
    elif msg["data"]["page"] == "actions":
        page = render_template("actions.html")
        socketio.emit(
            "activateModal",
            {"title": "Actions", "message": page},
            namespace="/MaslowCNC",
        )
    elif msg["data"]["page"] == "zAxis":
        page = render_template("zaxis.html")
        socketio.emit(
            "activateModal",
            {"title": "Z-Axis", "message": page},
            namespace="/MaslowCNC",
        )
    elif msg["data"]["page"] == "setSprockets":
        page = render_template("setSprockets.html")
        socketio.emit(
            "activateModal",
            {"title": "Z-Axis", "message": page},
            namespace="/MaslowCNC",
        )
    elif msg["data"]["page"] == "triangularCalibration":
        motorYoffset = app.data.config.getValue("Maslow Settings", "motorOffsetY")
        rotationRadius = app.data.config.getValue("Advanced Settings", "rotationRadius")
        chainSagCorrection = app.data.config.getValue(
            "Advanced Settings", "chainSagCorrection"
        )
        page = render_template(
            "triangularCalibration.html",
            pageID="triangularCalibration",
            motorYoffset=motorYoffset,
            rotationRadius=rotationRadius,
            chainSagCorrection=chainSagCorrection,
        )
        socketio.emit(
            "activateModal",
            {"title": "Triangular Calibration", "message": page},
            namespace="/MaslowCNC",
        )
    elif msg["data"]["page"] == "opticalCalibration":
        page = render_template(
            "triangularCalibration.html",
            pageID="opticalCalibration",
        )
        socketio.emit(
            "activateModal",
            {"title": "Optical Calibration", "message": page},
            namespace="/MaslowCNC",
        )
    elif msg["data"]["page"] == "quickConfigure":
        motorOffsetY = app.data.config.getValue("Maslow Settings", "motorOffsetY")
        rotationRadius = app.data.config.getValue("Advanced Settings", "rotationRadius")
        kinematicsType = app.data.config.getValue("Advanced Settings", "kinematicsType")
        if kinematicsType != "Quadrilateral":
            if abs(float(rotationRadius) - 138.4) < 0.01:
                kinematicsType = "Ring"
            else:
                kinematicsType = "Custom"
        motorSpacingX = app.data.config.getValue("Maslow Settings", "motorSpacingX")
        chainOverSprocket = app.data.config.getValue(
            "Advanced Settings", "chainOverSprocket"
        )
        print("MotorOffsetY=" + str(motorOffsetY))
        page = render_template(
            "quickConfigure.html",
            pageID="quickConfigure",
            motorOffsetY=motorOffsetY,
            rotationRadius=rotationRadius,
            kinematicsType=kinematicsType,
            motorSpacingX=motorSpacingX,
            chainOverSprocket=chainOverSprocket,
        )
        socketio.emit(
            "activateModal",
            {"title": "Quick Configure", "message": page},
            namespace="/MaslowCNC",
        )


@socketio.on("connect", namespace="/MaslowCNC")
def test_connect():
    print("connected")
    print(request.sid)
    socketio.emit("my response", {"data": "Connected", "count": 0})


@socketio.on("disconnect", namespace="/MaslowCNC")
def test_disconnect():
    print("Client disconnected")


@socketio.on("action", namespace="/MaslowCNC")
def command(msg):
    if msg["data"]["command"] == "resetChainLengths":
        if not app.data.actions.resetChainLengths():
            app.data.message_queue.put("Message: Error with resetting chain lengths.")
    elif msg["data"]["command"] == "reportSettings":
        app.data.gcode_queue.put("$$")
    elif msg["data"]["command"] == "home":
        if not app.data.actions.home():
            app.data.message_queue.put("Message: Error with returning to home.")
    elif msg["data"]["command"] == "defineHome":
        if app.data.actions.defineHome():
            ## the gcode file might change the active units so we need to inform the UI of the change.
            units = app.data.config.getValue("Computed Settings", "units")
            socketio.emit(
                "requestedSetting",
                {"setting": "units", "value": units},
                namespace="/MaslowCNC",
            )
            ## send updated gcode to UI
            socketio.emit(
                "gcodeUpdate",
                {"data": json.dumps([ob.__dict__ for ob in app.data.gcodeFile.line])},
                namespace="/MaslowCNC",
            )
        else:
            app.data.message_queue.put("Message: Error with defining home.")

    elif msg["data"]["command"] == "defineZ0":
        if not app.data.actions.defineZ0():
            app.data.message_queue.put("Message: Error with defining Z-Axis zero.")
    elif msg["data"]["command"] == "stopZ":
        if not app.data.actions.stopZ():
            app.data.message_queue.put("Message: Error with stopping Z-Axis movement")
    elif msg["data"]["command"] == "startRun":
        if not app.data.actions.startRun():
            app.data.message_queue.put("Message: Error with starting run")
    elif msg["data"]["command"] == "stopRun":
        if not app.data.actions.stopRun():
            app.data.message_queue.put("Message: Error with stopping run")
    elif msg["data"]["command"] == "moveToDefault":
        if not app.data.actions.moveToDefault():
            app.data.message_queue.put(
                "Message: Error with moving to default chain lengths"
            )
    elif msg["data"]["command"] == "testMotors":
        if not app.data.actions.testMotors():
            app.data.message_queue.put("Message: Error with testing motors")
    elif msg["data"]["command"] == "wipeEEPROM":
        if not app.data.actions.wipeEEPROM():
            app.data.message_queue.put("Message: Error with wiping EEPROM")
    elif msg["data"]["command"] == "pauseRun":
        if not app.data.actions.pauseRun():
            app.data.message_queue.put("Message: Error with pausing run")
    elif msg["data"]["command"] == "resumeRun":
        if not app.data.actions.resumeRun():
            app.data.message_queue.put("Message: Error with resuming run")
    elif msg["data"]["command"] == "returnToCenter":
        if not app.data.actions.returnToCenter():
            app.data.message_queue.put("Message: Error with returning to center")
    elif msg["data"]["command"] == "clearGCode":
        if app.data.actions.clearGCode():
            # send blank gcode to UI
            socketio.emit("gcodeUpdate", {"data": ""}, namespace="/MaslowCNC")
        else:
            app.data.message_queue.put("Message: Error with clearing gcode")
    elif msg["data"]["command"] == "moveGcodeZ":
        if not app.data.actions.moveGcodeZ(int(msg["data"]["arg"])):
            app.data.message_queue.put("Message: Error with moving to Z move")
    elif (
        msg["data"]["command"] == "moveGcodeIndex"
        or msg["data"]["command"] == "moveGcodeZ"
    ):
        if not app.data.actions.moveGcodeIndex(int(msg["data"]["arg"])):
            app.data.message_queue.put("Message: Error with moving to index")
    elif msg["data"]["command"] == "setSprockets":
        if not app.data.actions.setSprockets(msg["data"]["arg"], msg["data"]["arg1"]):
            app.data.message_queue.put("Message: Error with setting sprocket")
    elif msg["data"]["command"] == "setSprocketsAutomatic":
        if not app.data.actions.setSprocketsAutomatic():
            app.data.message_queue.put(
                "Message: Error with setting sprockets automatically"
            )
    elif msg["data"]["command"] == "setSprocketsZero":
        if not app.data.actions.setSprocketsZero():
            app.data.message_queue.put(
                "Message: Error with setting sprockets zero value"
            )
    elif msg["data"]["command"] == "updatePorts":
        if not app.data.actions.updatePorts():
            app.data.message_queue.put("Message: Error with updating list of ports")
    elif msg["data"]["command"] == "macro1":
        if not app.data.actions.macro(1):
            app.data.message_queue.put("Message: Error with performing macro")
    elif msg["data"]["command"] == "macro2":
        if not app.data.actions.macro(2):
            app.data.message_queue.put("Message: Error with performing macro")


@socketio.on("move", namespace="/MaslowCNC")
def move(msg):
    if not app.data.actions.move(
        msg["data"]["direction"], float(msg["data"]["distToMove"])
    ):
        app.data.message_queue.put("Message: Error with move")


@socketio.on("moveZ", namespace="/MaslowCNC")
def moveZ(msg):
    if not app.data.actions.moveZ(
        msg["data"]["direction"], float(msg["data"]["distToMoveZ"])
    ):
        app.data.message_queue.put("Message: Error with Z-Axis move")


@socketio.on("settingRequest", namespace="/MaslowCNC")
def settingRequest(msg):
    # didn't move to actions.. this request is just to send it computed values
    if msg["data"] == "units":
        units = app.data.config.getValue("Computed Settings", "units")
        socketio.emit(
            "requestedSetting",
            {"setting": msg["data"], "value": units},
            namespace="/MaslowCNC",
        )
    if msg["data"] == "distToMove":
        distToMove = app.data.config.getValue("Computed Settings", "distToMove")
        socketio.emit(
            "requestedSetting",
            {"setting": msg["data"], "value": distToMove},
            namespace="/MaslowCNC",
        )
    if msg["data"] == "unitsZ":
        unitsZ = app.data.config.getValue("Computed Settings", "unitsZ")
        socketio.emit(
            "requestedSetting",
            {"setting": msg["data"], "value": unitsZ},
            namespace="/MaslowCNC",
        )
    if msg["data"] == "distToMoveZ":
        distToMoveZ = app.data.config.getValue("Computed Settings", "distToMoveZ")
        socketio.emit(
            "requestedSetting",
            {"setting": msg["data"], "value": distToMoveZ},
            namespace="/MaslowCNC",
        )


@socketio.on("updateSetting", namespace="/MaslowCNC")
def updateSetting(msg):
    if not app.data.actions.updateSetting(msg["data"]["setting"], msg["data"]["value"]):
        app.data.message_queue.put("Message: Error updating setting")


@socketio.on("checkForGCodeUpdate", namespace="/MaslowCNC")
def checkForGCodeUpdate(msg):
    # this currently doesn't check for updated gcode, it just resends it..
    ## the gcode file might change the active units so we need to inform the UI of the change.
    units = app.data.config.getValue("Computed Settings", "units")
    socketio.emit(
        "requestedSetting", {"setting": "units", "value": units}, namespace="/MaslowCNC"
    )
    ## send updated gcode to UI
    socketio.emit(
        "gcodeUpdate",
        {"data": json.dumps([ob.__dict__ for ob in app.data.gcodeFile.line])},
        namespace="/MaslowCNC",
    )


@socketio.on_error_default
def default_error_handler(e):
    print(request.event["message"])  # "my error event"
    print(request.event["args"])  # (data,)1


if __name__ == "__main__":
    app.debug = False
    app.config["SECRET_KEY"] = "secret!"
    socketio.run(app, use_reloader=False, host="0.0.0.0")
    # socketio.run(app, host='0.0.0.0')
