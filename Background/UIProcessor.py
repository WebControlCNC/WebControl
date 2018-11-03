from __main__ import socketio

import time
import math
import json
from flask import render_template

class UIProcessor:

    app = None

    def start(self, _app):

        self.app = _app
        print("starting UI")
        with self.app.app_context():
            while True:
                time.sleep(0.001)
                if self.app.data.config.firstRun:
                    print("here at firstRun")
                    self.app.data.config.firstRun = False
                    time.sleep(2)
                    self.activateModal("Notification:",
                                       "New installation detected.  If you have an existing groundcontrol.ini file you would like to import, please do so now by pressing Actions->Import groundcontrol.ini file before doing anything else.")
                if self.app.data.opticalCalibrationImageUpdated is True:
                    self.sendCalibrationMessage(
                        "OpticalCalibrationImageUpdated",
                        self.app.data.opticalCalibrationImage,
                    )
                    self.app.data.opticalCalibrationImageUpdated = False
                if self.app.data.opticalCalibrationTestImageUpdated is True:
                    self.sendCalibrationMessage(
                        "OpticalCalibrationTestImageUpdated",
                        self.app.data.opticalCalibrationTestImage,
                    )
                    self.app.data.opticalCalibrationTestImageUpdated = False
                while (
                    not self.app.data.ui_queue.empty()
                ):  # if there is new data to be read
                    message = self.app.data.ui_queue.get()
                    # send message to web for display in appropriate column
                    zAxisMessage = False
                    if message != "":
                        if message[0] == "<":
                            # print message
                            self.setPosOnScreen(message)
                        elif message[0] == "[":
                            if message[1:4] == "PE:":
                                # todo:
                                oo = 1
                                # app.setErrorOnScreen(message)
                        elif message[0:13] == "Maslow Paused":
                                print("caught maslow paused")
                                socketio.emit(
                                    "requestedSetting",
                                    {"setting": "pauseButtonSetting", "value": "Resume"},
                                    namespace="/MaslowCNC",
                                )
                        elif message[0:12] == "Tool Change:":
                            print("found tool change in message")
                            self.activateModal("Notification:", message[13:], "resume")
                        elif message[0:8] == "Message:":
                            if message.find("adjust Z-Axis") != -1:
                                print("found adjust Z-Axis in message")
                                #socketio.emit(
                                #    "requestedSetting",
                                #    {"setting": "pauseButtonSetting", "value": "Resume"},
                                #    namespace="/MaslowCNC",
                                #)
                            self.activateModal("Notification:", message[9:], "resume")
                        elif message[0:7] == "Action:":
                            if message.find("unitsUpdate") != -1:
                                units = self.app.data.config.getValue(
                                    "Computed Settings", "units"
                                )
                                socketio.emit(
                                    "requestedSetting",
                                    {"setting": "units", "value": units},
                                    namespace="/MaslowCNC",
                                )
                            if message.find("distToMoveUpdate") != -1:
                                units = self.app.data.config.getValue(
                                    "Computed Settings", "distToMove"
                                )
                                socketio.emit(
                                    "requestedSetting",
                                    {"setting": "distToMove", "value": units},
                                    namespace="/MaslowCNC",
                                )
                            if message.find("gcodeUpdate") != -1:
                                socketio.emit(
                                    "gcodeUpdate",
                                    {
                                        "data": json.dumps(
                                            [
                                                ob.__dict__
                                                for ob in self.app.data.gcodeFile.line
                                            ]
                                        )
                                    },
                                    namespace="/MaslowCNC",
                                )
                            if message.find("setAsPause") != -1:
                                socketio.emit(
                                    "requestedSetting",
                                    {"setting": "pauseButtonSetting", "value": "Pause"},
                                    namespace="/MaslowCNC",
                                )
                            if message.find("setAsResume") != -1:
                                socketio.emit(
                                    "requestedSetting",
                                    {"setting": "pauseButtonSetting", "value": "Resume"},
                                    namespace="/MaslowCNC",
                                )
                            if message.find("positionUpdate") != -1:
                                msg = message.split(
                                    "_"
                                )  # everything to the right of the "_" should be the position data already json.dumps'ed
                                socketio.emit(
                                    "positionMessage",
                                    {"data": msg[1]},
                                    namespace="/MaslowCNC",
                                )
                            if message.find("homePositionMessage") != -1:
                                msg = message.split(
                                    "_"
                                )  # everything to the right of the "_" should be the position data already json.dumps'ed
                                print("sending home position update")
                                socketio.emit(
                                    "homePositionMessage",
                                    {"data": msg[1]},
                                    namespace="/MaslowCNC",
                                )
                            if message.find("updatePorts") != -1:
                                ports = json.dumps(self.app.data.comPorts)
                                socketio.emit(
                                    "updatePorts", {"data": ports}, namespace="/MaslowCNC"
                                )
                            if message.find("connectionStatus") != -1:
                                msg = message.split("_")
                                socketio.emit("controllerStatus", msg[1], namespace="/MaslowCNC")
                            if message.find("updateOpticalCalibrationCurve") != -1:
                                msg = message.split("_")
                                self.sendCalibrationMessage("updateOpticalCalibrationCurve", msg[1])
                            if message.find("updateOpticalCalibrationError") != -1:
                                msg = message.split("_")
                                self.sendCalibrationMessage("updateOpticalCalibrationError", msg[1])

                        elif message[0:6] == "ALARM:":
                            self.activateModal("Notification:", message[7:])
                        elif message == "ok\r\n":
                            pass  # displaying all the 'ok' messages clutters up the display
                        else:
                            #print("UIProcessor:"+message)
                            self.sendControllerMessage(message)

    def setPosOnScreen(self, message):
        try:
            with self.app.app_context():
                startpt = message.find("MPos:") + 5
                endpt = message.find("WPos:")
                numz = message[startpt:endpt]
                valz = numz.split(",")

                self.app.data.xval = float(valz[0])
                self.app.data.yval = float(valz[1])
                self.app.data.zval = float(valz[2])

                if math.isnan(self.app.data.xval):
                    self.sendControllerMessage("Unable to resolve x Kinematics.")
                    self.app.data.xval = 0
                if math.isnan(self.app.data.yval):
                    self.sendControllerMessage("Unable to resolve y Kinematics.")
                    self.app.data.yval = 0
                if math.isnan(self.app.data.zval):
                    self.sendControllerMessage("Unable to resolve z Kinematics.")
                    self.app.data.zval = 0
        except:
            print("One Machine Position Report Command Misread")
            return

        position = {
            "xval": self.app.data.xval,
            "yval": self.app.data.yval,
            "zval": self.app.data.zval,
        }
        self.sendPositionMessage(position)

    def activateModal(self, title, message, resume="false"):
        socketio.emit(
            "activateModal",
            {"title": title, "message": message, "resume": resume},
            namespace="/MaslowCNC",
        )

    def sendControllerMessage(self, message):
        socketio.emit(
            "controllerMessage", {"data": message}, namespace="/MaslowCNC"
        )

    def sendPositionMessage(self, position):
        socketio.emit(
            "positionMessage", {"data": json.dumps(position)}, namespace="/MaslowCNC"
        )

    def sendCalibrationMessage(self, message, data):
        socketio.emit(
            "calibrationMessage", {"msg": message, "data": data}, namespace="/MaslowCNC"
        )

