from __main__ import socketio

import time
import math
import json


class UIProcessor:

    app = None

    def start(self, _app):

        self.app = _app
        with self.app.app_context():
            while True:
                time.sleep(0.001)
                if self.app.data.opticalCalibrationImageUpdated is True:
                    self.sendCalibrationMessage(
                        "OpticalCalibrationImageUpdated",
                        self.app.data.opticalCalibrationImage,
                    )
                    self.app.data.opticalCalibrationImageUpdated = False
                while (
                    not self.app.data.ui_queue.empty()
                ):  # if there is new data to be read
                    message = self.app.data.ui_queue.get()
                    # send message to web for display in appropriate column
                    if message != "":
                        if message[0] == "<":
                            # print message
                            self.setPosOnScreen(message)
                        elif message[0] == "[":
                            if message[1:4] == "PE:":
                                # todo:
                                oo = 1
                                # app.setErrorOnScreen(message)
                        elif message[0:8] == "Message:":
                            if message.find("adjust Z-Axis") != -1:
                                print("found adjust Z-Axis in message")
                                socketio.emit(
                                    "requestedSetting",
                                    {"setting": "pauseButtonSetting", "value": "Resume"},
                                    namespace="/MaslowCNC",
                                )
                            self.activateModal("Notification:", message[9:])
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
                        elif message[0:6] == "ALARM:":
                            self.activateModal("Notification:", message[7:])
                        elif message == "ok\r\n":
                            pass  # displaying all the 'ok' messages clutters up the display
                        else:
                            print("UIProcessor:"+message)
                            self.sendControllerMessage(message)

    def setPosOnScreen(self, message):
        try:
            with self.app.app_context():
                startpt = message.find("MPos:") + 5
                endpt = message.find("WPos:")
                numz = message[startpt:endpt]
                units = "mm"  # message[endpt+1:endpt+3]
                valz = numz.split(",")

                self.app.data.xval = float(valz[0])
                self.app.data.yval = float(valz[1])
                self.app.data.zval = float(valz[2])

                # print "x:"+str(app.data.xval)+", y:"+str(app.data.yval)+", z:"+str(app.data.zval)

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

    def activateModal(self, title, message):
        socketio.emit(
            "activateModal",
            {"title": title, "message": message},
            namespace="/MaslowCNC",
        )

    def sendControllerMessage(self, message):
        socketio.emit("controllerMessage", {"data": message}, namespace="/MaslowCNC")

    def sendPositionMessage(self, position):
        socketio.emit(
            "positionMessage", {"data": json.dumps(position)}, namespace="/MaslowCNC"
        )

    def sendCalibrationMessage(self, message, data):
        socketio.emit(
            "calibrationMessage", {"msg": message, "data": data}, namespace="/MaslowCNC"
        )
