from __main__ import socketio

import time
import math
import json
import psutil
from flask import render_template

class UIProcessor:

    app = None
    lastCameraTime = 0
    lastHealthCheck = 0
    
    def start(self, _app):
        
        self.app = _app
        self.app.data.console_queue.put("starting UI")

        with self.app.app_context():
            while True:
                currentTime = time.time()
                if currentTime-self.lastHealthCheck > 5:
                    self.lastHealthCheck = currentTime
                    load = max(psutil.cpu_percent(interval=None, percpu=True))
                    healthData = {
                        "cpuUsage": load
                    }
                    self.sendHealthMessage(healthData)
                time.sleep(0.001)

                if self.app.data.config.firstRun:
                    self.app.data.console_queue.put("here at firstRun")
                    self.app.data.config.firstRun = False
                    time.sleep(2)
                    self.activateModal("Notification:",
                                       "New installation detected.  If you have an existing groundcontrol.ini file you would like to import, please do so now by pressing Actions->Import groundcontrol.ini file before doing anything else.","notification")
                if self.app.data.opticalCalibrationImageUpdated is True:
                    self.sendCalibrationImage(
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
                    self.sendCalibrationImage(
                        "OpticalCalibrationTestImageUpdated",
                        self.app.data.opticalCalibrationTestImage,
                    )
                    self.app.data.opticalCalibrationTestImageUpdated = False
                while ( not self.app.data.ui_controller_queue.empty() or not self.app.data.ui_queue1.empty()):  # if there is new data to be read
                    if not self.app.data.ui_controller_queue.empty():
                        message = self.app.data.ui_controller_queue.get()
                        if message != "":
                            if message[0] == "<":
                                self.setPosOnScreen(message)
                            elif message[0] == "[":
                                if message[1:4] == "PE:":
                                    self.setErrorOnScreen(message)
                            elif message[0:13] == "Maslow Paused":
                                self.app.data.console_queue.put("caught maslow paused")
                                self.app.data.uploadFlag = 0
                                self.app.data.quick_queue.put("~")
                                data = json.dumps({"setting": "pauseButtonSetting", "value": "Resume"})
                                socketio.emit("message", {"command": "requestedSetting", "data": data, "dataFormat": "json"},
                                              namespace="/MaslowCNC", )
                            elif message[0:12] == "Tool Change:":
                                self.app.data.manualZAxisAdjust = True
                                self.app.data.previousUploadStatus = self.app.data.uploadFlag
                                self.app.data.pausedzval = self.app.data.zval
                                self.app.data.console_queue.put("found tool change in message")
                                self.activateModal("Notification:", message[13:], "notification", resume="resume")
                            elif message[0:8] == "Message:":
                                if message.find("adjust Z-Axis") != -1:
                                    self.app.data.console_queue.put("found adjust Z-Axis in message")
                                    self.activateModal("Notification:", message[9:], "notification", resume="resume")
                                elif message.find("Unable to find valid") != -1:
                                    self.sendAlarm(message);
                                else:
                                    self.activateModal("Notification:", message[9:], "notification")
                            elif message[0:6] == "ALARM:":
                                if message.find("The sled is not keeping up") != -1:
                                    self.sendAlarm("Alarm: Sled Not Keeping Up")
                                elif message.find("Position Lost") != -1:
                                    self.sendAlarm("Alarm: Position Lost.  Reset Chains.")
                                else:
                                    self.sendAlarm(message);
                            elif message[0:6] == "Unable to":
                                if message.find("The sled is not keeping up") != -1:
                                    pass
                                self.sendAlarm("Alarm: Sled Not Keeping Up")

                                #self.activateModal("Alarm:", message[7:], "alarm", resume="clear")
                            elif message == "ok\r\n":
                                pass  # displaying all the 'ok' messages clutters up the display
                            else:
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

        xdiff = abs(self.app.data.xval - self.app.data.xval_prev)
        ydiff = abs(self.app.data.yval - self.app.data.yval_prev)
        zdiff = abs(self.app.data.zval - self.app.data.zval_prev)

        percentComplete = '%.1f' % math.fabs(100 * (self.app.data.gcodeIndex / (len(self.app.data.gcode) - 1))) + "%"

        if (xdiff + ydiff + zdiff) > 0.01:
            position = {
                "xval": self.app.data.xval,
                "yval": self.app.data.yval,
                "zval": self.app.data.zval,
                "pcom": percentComplete,
                "state": state
            }
            self.sendPositionMessage(position)
            self.app.data.xval_prev = self.app.data.xval
            self.app.data.yval_prev = self.app.data.yval
            self.app.data.zval_prev = self.app.data.zval
            #self.app.data.console_queue.put("Update position")


    def setErrorOnScreen(self, message):
        limit = float(self.app.data.config.getValue("Advanced Settings", "positionErrorLimit"))
        computedEnabled = int(self.app.data.config.getValue("WebControl Settings", "computedPosition"))
        if limit != 0:
            try:
                with self.app.app_context():
                    startpt = message.find(':') + 1
                    endpt = message.find(',', startpt)
                    leftErrorValueAsString = message[startpt:endpt]
                    self.app.data.leftError = float(leftErrorValueAsString)/limit

                    startpt = endpt + 1
                    endpt = message.find(',', startpt)
                    rightErrorValueAsString = message[startpt:endpt]
                    self.app.data.rightError = float(rightErrorValueAsString)/limit

                    if self.app.data.controllerFirmwareVersion > 50 and self.app.data.controllerFirmwareVersion < 100 and computedEnabled > 0:

                        startpt = endpt + 1
                        endpt = message.find(',', startpt)
                        bufferSizeValueAsString = message[startpt:endpt]
                        self.app.data.bufferSize = int(bufferSizeValueAsString)

                        startpt = endpt + 1
                        endpt = message.find(',', startpt)
                        leftChainLengthAsString = message[startpt:endpt]
                        self.app.data.leftChain = float(leftChainLengthAsString)

                        startpt = endpt + 1
                        endpt = message.find(']', startpt)
                        rightChainLengthAsString = message[startpt:endpt]
                        self.app.data.rightChain = float(rightChainLengthAsString)

                        self.app.data.computedX, self.app.data.computedY = self.app.data.holeyKinematics.forward(self.app.data.leftChain, self.app.data.rightChain, self.app.data.xval, self.app.data.yval )
                        #print("leftChain=" + str(self.app.data.leftChain) + ", rightChain=" + str(self.app.data.rightChain)+", x= "+str(self.app.data.computedX)+", y= "+str(self.app.data.computedY))
                        computedEnabled = 1
                    else:
                        self.app.data.computedX = -999999
                        self.app.data.computedY = -999999
                        computedEnabled = 0

                    if math.isnan(self.app.data.leftError):
                        self.app.data.leftErrorValue = 0
                    if math.isnan(self.app.data.rightError):
                        self.app.data.rightErrorValue = 0
            except:
                self.app.data.console_queue.put("One Error Report Command Misread")
                return

            leftDiff = abs(self.app.data.leftError - self.app.data.leftError_prev)
            rightDiff = abs(self.app.data.rightError - self.app.data.rightError_prev)

            if (leftDiff + rightDiff ) >= 0.001:
                errorValues = {
                    "leftError": abs(self.app.data.leftError),
                    "rightError": abs(self.app.data.rightError),
                    "computedX": self.app.data.computedX,
                    "computedY": self.app.data.computedY,
                    "computedEnabled": computedEnabled
                }
                self.sendErrorValueMessage(errorValues)
                self.app.data.leftError_prev = self.app.data.leftError
                self.app.data.rightError_prev = self.app.data.rightError
                #self.app.data.console_queue.put("Update error values")



    def activateModal(self, title, message, modalType, resume="false", progress="false"):
        data = json.dumps({"title": title, "message": message, "resume": resume, "progress": progress, "modalSize": "small", "modalType": modalType})
        socketio.emit("message", {"command": "activateModal", "data": data, "dataFormat": "json"},
            namespace="/MaslowCNC",
        )

    def sendAlarm(self, message):
        data = json.dumps({"message":message})
        socketio.emit("message", {"command": "alarm", "data": data, "dataFormat": "json"},
            namespace="/MaslowCNC",
        )

    def sendControllerMessage(self, message):
        socketio.emit("message", {"command": "controllerMessage", "data": json.dumps(message), "dataFormat": "json"},
                      namespace="/MaslowCNC")
        #socketio.emit(
        #    "controllerMessage", {"data": message}, namespace="/MaslowCNC"
        #)

    def sendWebMCPMessage(self, message):
        #print(message)
        #socketio.emit("message", {"command": json.dumps(message), "dataFormat": "json"},namespace="/WebMCP")
        socketio.emit("shutdown",namespace="/WebMCP")

    def sendPositionMessage(self, position):
        socketio.emit("message", {"command": "positionMessage", "data": json.dumps(position), "dataFormat": "json"},
                      namespace="/MaslowCNC")

    def sendErrorValueMessage(self, position):
        socketio.emit("message", {"command": "errorValueMessage", "data": json.dumps(position), "dataFormat": "json"},
                      namespace="/MaslowCNC")

    def sendHealthMessage(self, healthData):
        socketio.emit("message", {"command": "healthMessage", "data": json.dumps(healthData), "dataFormat": "json"},
                      namespace="/MaslowCNC")

    def sendCameraMessage(self, message, _data=""):

        data = json.dumps({"command": message, "data": _data})

        socketio.emit(
            "message", {"command":"cameraMessage", "data": data, "dataFormat": "json"}, namespace="/MaslowCNC"
        )

    def updatePIDData(self, message, _data=""):

        data = json.dumps({"command": message, "data": _data})
        print(data)
        socketio.emit(
            "message", {"command":"updatePIDData", "data": data, "dataFormat": "json"}, namespace="/MaslowCNC"
        )


    def sendGcodeUpdate(self):
        if self.app.data.compressedGCode3D is not None:
            self.app.data.console_queue.put("Sending Gcode compressed")
            socketio.emit("message", {"command": "showFPSpinner",
                                      "data": len(self.app.data.compressedGCode3D), "dataFormat": "int"},
                          namespace="/MaslowCNC", )
            time.sleep(0.25)
            socketio.emit("message", {"command": "gcodeUpdateCompressed",
                                      "data": self.app.data.compressedGCode3D, "dataFormat": "base64"},
                          namespace="/MaslowCNC", )
            self.app.data.console_queue.put("Sent Gcode compressed")

    def sendBoardUpdate(self):
        boardData = self.app.data.boardManager.getCurrentBoard().getBoardInfoJSON()
        if boardData is not None:
            self.app.data.console_queue.put("Sending Board Data compressed")
            socketio.emit("message", {"command": "showFPSpinner",
                                      "data": 1, "dataFormat": "int"},
                          namespace="/MaslowCNC", )
            time.sleep(0.25)
            socketio.emit("message", {"command": "boardDataUpdate",
                                      "data": boardData, "dataFormat": "json"},
                          namespace="/MaslowCNC", )
            self.app.data.console_queue.put("Sent Board Data compressed")

        cutData = self.app.data.boardManager.getCurrentBoard().getCompressedCutData()
        if cutData is not None:
            self.app.data.console_queue.put("Sending Board Cut Data compressed")
            socketio.emit("message", {"command": "showFPSpinner",
                                      "data": 1, "dataFormat": "int"},
                          namespace="/MaslowCNC", )
            time.sleep(0.25)
            socketio.emit("message", {"command": "boardCutDataUpdateCompressed",
                                      "data": cutData, "dataFormat": "base64"},
                          namespace="/MaslowCNC", )
            self.app.data.console_queue.put("Sent Board Cut Data compressed")

    def unitsUpdate(self):
        units = self.app.data.config.getValue(
            "Computed Settings", "units"
        )
        data = json.dumps({"setting": "units", "value": units})
        socketio.emit("message", {"command": "requestedSetting", "data": data, "dataFormat": "json"},
                      namespace="/MaslowCNC", )
    def distToMoveUpdate(self):
        distToMove = self.app.data.config.getValue(
            "Computed Settings", "distToMove"
        )
        data = json.dumps({"setting": "distToMove", "value": distToMove})
        socketio.emit("message", {"command": "requestedSetting", "data": data, "dataFormat": "json"},
                      namespace="/MaslowCNC", )

    def processMessage(self, _message):
        msg = json.loads(_message)
        if msg["command"] == "WebMCP":
            self.sendWebMCPMessage(msg["message"])
        if msg["command"] == "Action":
            if msg["message"] == "gcodeUpdate":
                self.sendGcodeUpdate()
            if msg["message"] == "boardUpdate":
                self.sendBoardUpdate()
            elif msg["message"] == "unitsUpdate":
                self.unitsUpdate()
            elif msg["message"] == "distToMoveUpdate":
                self.distToMoveUpdate()
            elif msg["message"] == "updateTimer":
                #Todo: clean this up
                self.sendCalibrationMessage("updateTimer", json.loads(msg["data"]))
            elif msg["message"] == "updateCamera":
                self.sendCameraMessage("updateCamera", json.loads(msg["data"]))
            elif msg["message"] == "updatePIDData":
                self.updatePIDData("updatePIDData", json.loads(msg["data"]))
            elif msg["message"] == "clearAlarm":
                msg["data"] = json.dumps({"data":""})
                socketio.emit("message", {"command": msg["message"], "data": msg["data"], "dataFormat": "json"},
                              namespace="/MaslowCNC")
            else:
                if msg["message"] == "setAsPause":
                    msg["message"] = "requestedSetting"
                    msg["data"] = json.dumps({"setting": "pauseButtonSetting", "value": "Pause"})
                elif msg["message"] == "setAsResume":
                    msg["message"] = "requestedSetting"
                    msg["data"] = json.dumps({"setting": "pauseButtonSetting", "value": "Resume"})
                elif msg["message"] == "updatePorts":
                    msg["data"] = json.dumps(self.app.data.comPorts)
                elif msg["message"] == "closeModals":
                    msg["data"] = json.dumps({"title": msg["data"]})
                socketio.emit("message", {"command": msg["message"], "data": msg["data"], "dataFormat": "json"}, namespace="/MaslowCNC")
        elif msg["command"] == "TextMessage":
            socketio.emit("message", {"command": "controllerMessage", "data": msg["data"], "dataFormat": "json"},
                          namespace="/MaslowCNC")
        elif msg["command"] == "Alert":
            #if message.find("adjust Z-Axis") != -1:
            #    self.app.data.console_queue.put("found adjust Z-Axis in message")
            #    self.activateModal("Notification:", message[9:], "notification", resume="resume")
            #else:
            self.activateModal(msg["message"], msg["data"], "alert")
        elif msg["command"] == "SpinnerMessage":
            self.activateModal("Notification:", msg["data"], "notification", progress="spinner")

    def sendCalibrationImage(self, message, _data):

        data = json.dumps({"command": message, "data": _data})

        socketio.emit(
            "message", {"command": "updateCalibrationImage", "data": data, "dataFormat": "json"}, namespace="/MaslowCNC"
        )
