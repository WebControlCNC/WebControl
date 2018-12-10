from __main__ import socketio

import time
import math
import json
from flask import render_template

class UIProcessor:

    app = None
    lastCameraTime = 0
    
    def start(self, _app):
        
        self.app = _app
        self.app.data.console_queue.put("starting UI")
        with self.app.app_context():
            while True:
                time.sleep(0.001)
                if self.app.data.config.firstRun:
                    self.app.data.console_queue.put("here at firstRun")
                    self.app.data.config.firstRun = False
                    time.sleep(2)
                    self.activateModal("Notification:",
                                       "New installation detected.  If you have an existing groundcontrol.ini file you would like to import, please do so now by pressing Actions->Import groundcontrol.ini file before doing anything else.","notification")
                if self.app.data.opticalCalibrationImageUpdated is True:
                    self.sendCalibrationMessage(
                        "OpticalCalibrationImageUpdated",
                        self.app.data.opticalCalibrationImage,
                    )
                    self.app.data.opticalCalibrationImageUpdated = False
                if self.app.data.cameraImageUpdated is True:
                    if time.time()-self.lastCameraTime > .25:
                        self.sendCameraMessage(
                            "cameraImageUpdated",
                            self.app.data.cameraImage,
                        )
                        self.app.data.cameraImageUpdated = False
                        self.lastCameraTime = time.time()
                if self.app.data.opticalCalibrationTestImageUpdated is True:
                    self.sendCalibrationMessage(
                        "OpticalCalibrationTestImageUpdated",
                        self.app.data.opticalCalibrationTestImage,
                    )
                    self.app.data.opticalCalibrationTestImageUpdated = False
                while ( not self.app.data.ui_queue.empty() or not self.app.data.ui_queue1.empty()):  # if there is new data to be read
                    if not self.app.data.ui_queue.empty():
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
                                self.app.data.console_queue.put("caught maslow paused")
                                #socketio.emit(
                                #    "requestedSetting",
                                #    {"setting": "pauseButtonSetting", "value": "Resume"},
                                #    namespace="/MaslowCNC",
                                #)
                                data = json.dumps({"setting": "pauseButtonSetting", "value": "Resume"})
                                socketio.emit("message", {"command": "requestedSetting", "data": data},
                                              namespace="/MaslowCNC", )

                            elif message[0:12] == "Tool Change:":
                                self.app.data.console_queue.put("found tool change in message")
                                self.activateModal("Notification:", message[13:],"notification", resume="resume")
                            elif message[0:13] == "showFPSpinner":
                                socketio.emit("message", {"command": "showFPSpinner", "data": ""},
                                              namespace="/MaslowCNC", )
                                #socketio.emit("showFPSpinner", {"data": ""}, namespace="/MaslowCNC")
                            elif message[0:12] == "closeModals:":
                                msg = message.split("_")
                                #socketio.emit(
                                #    "closeModals",
                                #    {"data": {"title": msg[1]}},
                                #    namespace="/MaslowCNC",
                                #)
                                data = json.dumps({"title":msg[1]})
                                socketio.emit("message", {"command": "closeModals", "data": data},
                                              namespace="/MaslowCNC", )

                            elif message[0:8] == "Message:":
                                if message.find("adjust Z-Axis") != -1:
                                    self.app.data.console_queue.put("found adjust Z-Axis in message")
                                    #socketio.emit(
                                    #    "requestedSetting",
                                    #    {"setting": "pauseButtonSetting", "value": "Resume"},
                                    #    namespace="/MaslowCNC",
                                    #)
                                    self.activateModal("Notification:", message[9:], "notification", resume="resume")
                                else:
                                    self.activateModal("Notification:", message[9:], "notification")
                            elif message[0:16] == "ProgressMessage:":
                                    self.activateModal("Notification:", message[17:], "notification", progress="enable")
                            elif message[0:15] == "SpinnerMessage:":
                                    self.activateModal("Notification:", message[15:], "notification", progress="spinner")
                            elif message[0:7] == "Action:":
                                if message.find("updateDirectories") != -1:
                                    msg = message.split(
                                        "_"
                                    )  # everything to the right of the "_" should be the position data already json.dumps'ed
                                    #socketio.emit(
                                    #    "updateDirectories",
                                    #    {"data": msg[1]},
                                    #    namespace="/MaslowCNC",
                                    #)
                                    print(msg[1])
                                    socketio.emit("message", {"command": "updateDirectories", "data": msg[1]},
                                                  namespace="/MaslowCNC", )
                                if message.find("unitsUpdate") != -1:
                                    units = self.app.data.config.getValue(
                                        "Computed Settings", "units"
                                    )
                                    #socketio.emit(
                                    #    "requestedSetting",
                                    #    {"setting": "units", "value": units},
                                    #    namespace="/MaslowCNC",
                                    #)
                                    data = json.dumps({"setting": "units", "value": units})
                                    socketio.emit("message", {"command": "requestedSetting", "data": data},
                                                  namespace="/MaslowCNC", )
                                if message.find("distToMoveUpdate") != -1:
                                    units = self.app.data.config.getValue(
                                        "Computed Settings", "distToMove"
                                    )
                                    #socketio.emit(
                                    #    "requestedSetting",
                                    #    {"setting": "distToMove", "value": units},
                                    #    namespace="/MaslowCNC",
                                    #)
                                    data = json.dumps({"setting": "distToMove", "value": units})
                                    socketio.emit("message", {"command": "requestedSetting", "data": data},
                                                  namespace="/MaslowCNC", )
                                if message.find("gcodeUpdate") != -1:
                                    if self.app.data.compressedGCode is not None:
                                        enable3D = self.app.data.config.getValue("WebControl Settings", "enable3D")
                                        if enable3D:
                                            #self.app.data.console_queue.put("sending compressed")
                                            #socketio.emit("gcodeUpdateCompressed", {"data":self.app.data.compressedGCode3D}, namespace="/MaslowCNC")
                                            self.app.data.console_queue.put("Sending Gcode compressed")
                                            socketio.emit("message", {"command": "showFPSpinner",
                                                                      "data": len(self.app.data.compressedGCode3D)},
                                                          namespace="/MaslowCNC", )
                                            time.sleep(0.25)
                                            socketio.emit("message", {"command": "gcodeUpdateCompressed",
                                                                      "data": self.app.data.compressedGCode3D},
                                                          namespace="/MaslowCNC", )
                                            self.app.data.console_queue.put("Sent Gcode compressed")
                                        else:
                                            #self.app.data.console_queue.put("sending compressed3D")
                                            #socketio.emit("gcodeUpdateCompressed", {"data": self.app.data.compressedGCode}, namespace="/MaslowCNC")
                                            self.app.data.console_queue.put("Sending Gcode compressed")
                                            socketio.emit("message", {"command": "showFPSpinner",
                                                                      "data": len(self.app.data.compressedGCode)},
                                                          namespace="/MaslowCNC", )
                                            time.sleep(0.25)
                                            socketio.emit("message", {"command": "gcodeUpdateCompressed",
                                                                      "data": self.app.data.compressedGCode},
                                                          namespace="/MaslowCNC", )
                                            self.app.data.console_queue.put("Sent Gcode compressed")


                                if message.find("setAsPause") != -1:
                                    #socketio.emit(
                                    #    "requestedSetting",
                                    #    {"setting": "pauseButtonSetting", "value": "Pause"},
                                    #    namespace="/MaslowCNC",
                                    #)
                                    data = json.dumps({"setting": "pauseButtonSetting", "value": "Pause"})
                                    socketio.emit("message", {"command": "requestedSetting", "data": data},
                                                  namespace="/MaslowCNC", )
                                if message.find("setAsResume") != -1:
                                    #socketio.emit(
                                    #    "requestedSetting",
                                    #    {"setting": "pauseButtonSetting", "value": "Resume"},
                                    #    namespace="/MaslowCNC",
                                    #)
                                    data = json.dumps({"setting": "pauseButtonSetting", "value": "Resume"})
                                    socketio.emit("message", {"command": "requestedSetting", "data": data},
                                                  namespace="/MaslowCNC", )
                                if message.find("positionUpdate") != -1:
                                    msg = message.split(
                                        "_"
                                    )  # everything to the right of the "_" should be the position data already json.dumps'ed
                                    socketio.emit("message", {"command": "positionMessage", "data": msg[1]},
                                                  namespace="/MaslowCNC")
                                    #socketio.emit(
                                    #    "positionMessage",
                                    #    {"data": msg[1]},
                                    #    namespace="/MaslowCNC",
                                    #)
                                if message.find("homePositionMessage") != -1:
                                    msg = message.split(
                                        "_"
                                    )  # everything to the right of the "_" should be the position data already json.dumps'ed
                                    self.app.data.console_queue.put("sending home position update")
                                    socketio.emit(
                                        "message",
                                        {"command":"homePositionMessage","data": msg[1]},
                                        namespace="/MaslowCNC",
                                    )

                                if message.find("gcodePositionUpdate") != -1:
                                    msg = message.split(
                                        "_"
                                    )  # everything to the right of the "_" should be the position data already json.dumps'ed
                                    socketio.emit(
                                        "message",
                                        {"command":"gcodePositionMessage","data": msg[1]},
                                        namespace="/MaslowCNC",
                                    )

                                    #socketio.emit(
                                    #    "gcodePositionMessage",
                                    #    {"data": msg[1]},
                                    #    namespace="/MaslowCNC",
                                    #)
                                if message.find("updatePorts") != -1:
                                    data = json.dumps(self.app.data.comPorts)
                                    #socketio.emit(
                                    #    "updatePorts", {"data": ports}, namespace="/MaslowCNC"
                                    #)
                                    socketio.emit(
                                        "message",
                                        {"command":"updatePorts","data": data},
                                        namespace="/MaslowCNC",
                                    )

                                #if message.find("connectionStatus") != -1:
                                #    msg = message.split("_")
                                #    socketio.emit("message",{"command":"controllerStatus", "data":msg[1]}, namespace="/MaslowCNC")

                                if message.find("updateOpticalCalibrationCurve") != -1:
                                    msg = message.split("_")
                                    self.sendCalibrationMessage("updateOpticalCalibrationCurve", msg[1])
                                #if message.find("updateOpticalCalibrationError") != -1:
                                #    msg = message.split("_")
                                #    self.sendCalibrationMessage("updateOpticalCalibrationError", msg[1])
                                if message.find("updateOpticalCalibrationFindCenter") != -1:
                                    msg = message.split("_")
                                    self.sendCalibrationMessage("updateOpticalCalibrationFindCenter", msg[1])
                                if message.find("updateTimer") != -1:
                                    msg = message.split("_")
                                    self.sendCalibrationMessage("updateTimer", msg[1])
                                if message.find("updateCamera") != -1:
                                    msg = message.split("_")
                                    self.sendCameraMessage("updateCamera", msg[1])

                            elif message[0:6] == "ALARM:":
                                if message.find("The sled is not keeping up") != -1:
                                    #change color of stop button
                                    pass
                                self.activateModal("Alarm:", message[7:], "alarm", resume="clear")
                            elif message == "ok\r\n":
                                pass  # displaying all the 'ok' messages clutters up the display
                            else:
                                #print("UIProcessor:"+message)
                                self.sendControllerMessage(message)
                    if not self.app.data.ui_queue1.empty():
                        message = self.app.data.ui_queue1.get()
                        self.processMessage(message)

    def setPosOnScreen(self, message):
        try:
            with self.app.app_context():
                startpt = message.find("MPos:") + 5
                endpt = message.find("WPos:")
                numz = message[startpt:endpt]
                valz = numz.split(",")
                state = ""
                if message.find("Stop")!=-1:
                    state = "Stopped"
                elif message.find("Pause")!=-1:
                    state = "Paused"
                elif message.find("Idle")!=-1:
                    state = "Idle"

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
            self.app.data.console_queue.put("One Machine Position Report Command Misread")
            return

        percentComplete = '%.1f' % math.fabs(100 * (self.app.data.gcodeIndex / (len(self.app.data.gcode) - 1))) + "%"

        position = {
            "xval": self.app.data.xval,
            "yval": self.app.data.yval,
            "zval": self.app.data.zval,
            "pcom": percentComplete,
            "state": state
        }
        
        #print("upload="+str(self.app.data.uploadFlag)+", gInd="+str(self.app.data.gcodeIndex)+", gco_qu"+str(self.app.data.gcode_queue.qsize()))
        
        self.sendPositionMessage(position)

    def activateModal(self, title, message, modalType, resume="false", progress="false"):
        data = json.dumps({"title": title, "message": message, "resume": resume, "progress": progress, "modalSize": "small", "modalType": modalType})
        socketio.emit("message",{"command":"activateModal","data":data},
            namespace="/MaslowCNC",
        )

    def sendControllerMessage(self, message):
        socketio.emit("message", {"command": "controllerMessage", "data": message},
                      namespace="/MaslowCNC")
        #socketio.emit(
        #    "controllerMessage", {"data": message}, namespace="/MaslowCNC"
        #)

    def sendPositionMessage(self, position):
        socketio.emit("message", {"command": "positionMessage", "data": json.dumps(position)},
                      namespace="/MaslowCNC")

    def sendCalibrationMessage(self, message, _data):

        data = json.dumps({"command": message, "data": _data})

        socketio.emit(
            "message", {"command": "calibrationMessage", "data": data}, namespace="/MaslowCNC"
        )
    
    def sendCameraMessage(self, message, _data=""):

        data = json.dumps({"command": message, "data": _data})

        socketio.emit(
            "message", {"command":"cameraMessage", "data": data}, namespace="/MaslowCNC"
        )
    
    def processMessage(self, _message):


        msg = json.loads(_message)
        if msg["command"] == "Action":
            socketio.emit("message", {"command": msg["message"], "data": msg["data"]}, namespace="/MaslowCNC")
        elif msg["command"] == "TextMessage":
            socketio.emit("message", {"command": "controllerMessage", "data": msg["data"]},
                          namespace="/MaslowCNC")
        elif msg["command"] == "Alert":
            #if message.find("adjust Z-Axis") != -1:
            #    self.app.data.console_queue.put("found adjust Z-Axis in message")
            #    self.activateModal("Notification:", message[9:], "notification", resume="resume")
            #else:
            self.activateModal(msg["message"], msg["data"], "notification")


