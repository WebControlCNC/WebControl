from __main__ import socketio

import time
import math
import json
import psutil
import webbrowser
from flask import render_template

'''
This class sends messages the browser via sockets.  It monitors the ui_controller_queue (where controller messages that
need to be sent to the UI are put) and the ui_queue1 (where webcontrol-initiated messages that need to be sent to the UI
are put).  There is a legacy ui_queue (not the missing 1) that I reworked into ui_queue1 but I never refactored.

This class is not MakesmithInitFuncs inherited, so it doesn't have direct access to the data.  Therefore, it gets
passed the app.  
'''

class UIProcessor:
    app = None
    lastCameraTime = 0
    lastHealthCheck = 0
    previousUploadFlag = None
    previousCurrentTool = None
    previousPositioningMode = None

    def start(self, _app):

        self.app = _app
        self.app.data.console_queue.put("starting UI")
        with self.app.app_context():
            while True:
                time.sleep(0.001)
                # send health message
                self.performHealthCheck()
                # send status message
                self.performStatusCheck()
                # send message to UI client if this is the first time webcontrol is being run.
                if self.app.data.config.firstRun:
                    self.app.data.config.firstRun = False
                    # I *think* this was added to give time for the browser to open up.
                    time.sleep(2)
                    self.activateModal("Notification:",
                                       "New installation detected.  If you have an existing groundcontrol.ini file you would like to import, please do so now by pressing Actions->Import groundcontrol.ini file before doing anything else.",
                                       "notification")
                # This sends an updated camera image from optical calibration if available (optical)
                if self.app.data.opticalCalibrationImageUpdated is True:
                    self.sendCalibrationImage(
                        "OpticalCalibrationImageUpdated",
                        self.app.data.opticalCalibrationImage,
                    )
                    self.app.data.opticalCalibrationImageUpdated = False
                # This sends an updated camera image if available (camera)
                if self.app.data.cameraImageUpdated is True:
                    if time.time() - self.lastCameraTime > .25:
                        self.sendCameraMessage(
                            "cameraImageUpdated",
                            self.app.data.cameraImage,
                        )
                        self.app.data.cameraImageUpdated = False
                        self.lastCameraTime = time.time()
                # This sends an updated camera 'test' image from optical calibration (optical).. test image is the
                # image used to calibrate the camera.
                if self.app.data.opticalCalibrationTestImageUpdated is True:
                    self.sendCalibrationImage(
                        "OpticalCalibrationTestImageUpdated",
                        self.app.data.opticalCalibrationTestImage,
                    )
                    self.app.data.opticalCalibrationTestImageUpdated = False
                # function is run while queues are not empty
                while (
                        not self.app.data.ui_controller_queue.empty() or not self.app.data.ui_queue1.empty()):  # if there is new data to be read
                    # ui_controller_queue are messages from the controller.
                    if not self.app.data.ui_controller_queue.empty():
                        message = self.app.data.ui_controller_queue.get()
                        if message != "":
                            if message[0] == "<":
                                #call function to parse position message and update UI clients
                                self.setPosOnScreen(message)
                            elif message[0] == "[":
                                # call function to parse position error message and update UI clients
                                if message[1:4] == "PE:":
                                    self.setErrorOnScreen(message)
                            elif message[0:13] == "Maslow Paused":
                                # Maslow has been paused.  set uploadFlag to 0 and update the pause button on the
                                # UI clients.  In reality, uploadFlag should already be set to 0 by serialPortThread
                                # that is, the controller shouldn't be pausing without webcontrol already know it's
                                # going to pause.
                                self.app.data.uploadFlag = 0
                                # Send '~' upon receiveing the "Maslow Paused" notification.  This
                                # operation is to issue this 'un-pause' command which then lets two ok's to come back
                                # (one for the tool change and one for the ~)  Without this, serialThread won't see
                                # that the bufferSize = bufferSpace and therefore won't issue any commands.
                                ## new stuff
                                # self.app.data.quick_queue.put("~")
                                ## end new stuff
                                self.app.data.pausedUnits = self.app.data.units
                                data = json.dumps({"setting": "pauseButtonSetting", "value": "Resume"})
                                socketio.emit("message",
                                              {"command": "requestedSetting", "data": data, "dataFormat": "json"},
                                              namespace="/MaslowCNC", )
                            elif message[0:12] == "Tool Change:":
                                # Tool change message detected.
                                # not sure what manualzaxisadjust is.. ###
                                self.app.data.manualZAxisAdjust = True
                                # keep track of whether upload flag was set... can't remember why.
                                self.app.data.previousUploadStatus = self.app.data.uploadFlag
                                # remember the current z value so it can be returned to.
                                self.app.data.pausedzval = self.app.data.zval
                                # remember the current units because user might switch them to zero the zaxis.
                                self.app.data.pausedUnits = self.app.data.units
                                # Remember current positioning mode.
                                self.app.data.pausedPositioningMode = self.app.data.positioningMode
                                self.app.data.console_queue.put("found tool change in message")
                                # send unpause
                                self.app.data.quick_queue.put("~")
                                # notify user
                                self.activateModal("Notification:", message[13:], "notification", resume="resume")
                            elif message[0:8] == "Message:":
                                # message received from controller
                                if message.find("adjust Z-Axis") != -1:
                                    # manual z-axis adjustment requested.
                                    self.app.data.console_queue.put("found adjust Z-Axis in message")
                                    self.app.data.pausedUnits = self.app.data.units
                                    self.activateModal("Notification:", message[9:], "notification", resume="resume")
                                elif message.find("Unable to find valid") != -1:
                                    # position alarm detected.. chain lengths do not allow for forward kinematic.
                                    # This could occur during the set sprockets to zero process.. so ignore alarm
                                    # if either sprocket distance is zero.
                                    if not self.isChainLengthZero(message):
                                        self.sendAlarm(message);
                                else:
                                    # something other than above..
                                    self.activateModal("Notification:", message[9:], "notification")
                            elif message[0:6] == "ALARM:":
                                # alarm received from controller
                                if message.find("The sled is not keeping up") != -1:
                                    self.sendAlarm("Alarm: Sled Not Keeping Up")
                                elif message.find("Position Lost") != -1:
                                    self.sendAlarm("Alarm: Position Lost.  Reset Chains.")
                                else:
                                    self.sendAlarm(message);
                            elif message[0:6] == "Unable to":
                                # not sure what this is for.. probably legacy or something.. TODO: cleanup
                                if message.find("The sled is not keeping up") != -1:
                                    pass
                                self.sendAlarm("Alarm: Sled Not Keeping Up")
                            elif message == "ok\r\n":
                                pass  # displaying all the 'ok' messages clutters up the display
                            else:
                                #if something else, send it to the UI to figure out.
                                self.sendControllerMessage(message)
                    if not self.app.data.ui_queue1.empty():
                        # webcontrol generated messages to be sent to UI client
                        message = self.app.data.ui_queue1.get()
                        self.processMessage(message)

    def setPosOnScreen(self, message):
        '''
        Parses the controller message and determines x,y,z coordinates of sled.
        Based on ground control's implementation.  Added a few hooks for the state.
        :param message:
        :return:
        '''
        try:
            with self.app.app_context():
                startpt = message.find("MPos:") + 5
                endpt = message.find("WPos:")
                numz = message[startpt:endpt]
                valz = numz.split(",")
                state = ""
                if message.find("Stop") != -1:
                    state = "Stopped"
                elif message.find("Pause") != -1:
                    state = "Paused"
                elif message.find("Idle") != -1:
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

        # compute just how much the sled has moved.
        xdiff = abs(self.app.data.xval - self.app.data.xval_prev)
        ydiff = abs(self.app.data.yval - self.app.data.yval_prev)
        zdiff = abs(self.app.data.zval - self.app.data.zval_prev)

        # compute percentage of gcode that's been completed.
        percentComplete = '%.1f' % math.fabs(100 * (self.app.data.gcodeIndex / (len(self.app.data.gcode) - 1))) + "%"

        # if the sled has moved more than a very, very small amount, then go ahead and send.  Cuts down on network
        # traffic.
        if (xdiff + ydiff + zdiff) > 0.01:
            # package as json
            position = {
                "xval": self.app.data.xval,
                "yval": self.app.data.yval,
                "zval": self.app.data.zval,
                "pcom": percentComplete,
                "state": state
            }
            # call command to send the position data
            self.sendPositionMessage(position)
            # keep track of position
            self.app.data.xval_prev = self.app.data.xval
            self.app.data.yval_prev = self.app.data.yval
            self.app.data.zval_prev = self.app.data.zval

    def setErrorOnScreen(self, message):
        '''
        Parses the error message and sends to UI clients.  Allows for option to perform forward kinematics to see
        where the router actually is based upon chain length errors.  Not sure if particularly useful, but its an option
        :param message:
        :return:
        '''
        limit = float(self.app.data.config.getValue("Advanced Settings", "positionErrorLimit"))
        computedEnabled = int(self.app.data.config.getValue("WebControl Settings", "computedPosition"))
        if limit != 0:
            try:
                with self.app.app_context():
                    startpt = message.find(':') + 1
                    endpt = message.find(',', startpt)
                    leftErrorValueAsString = message[startpt:endpt]
                    self.app.data.leftError = float(leftErrorValueAsString) / limit

                    startpt = endpt + 1
                    endpt = message.find(',', startpt)
                    rightErrorValueAsString = message[startpt:endpt]
                    self.app.data.rightError = float(rightErrorValueAsString) / limit

                    # the two custom firmwares were modified to send the chain lengths as well as the error.  This
                    # allows for forward kinematics to be performed to get sled location.
                    if self.app.data.controllerFirmwareVersion > 50 and self.app.data.controllerFirmwareVersion < 150:

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

                    else:
                        # if not custom firmware, then just buffer size remains.
                        startpt = endpt + 1
                        endpt = message.find(']', startpt)
                        bufferSizeValueAsString = message[startpt:endpt]
                        self.app.data.bufferSize = int(bufferSizeValueAsString)
                        # regardless of setting, if not custom firmware there cannot be a forward kinematic compute
                        computedEnabled = 0

                    if computedEnabled > 0:
                        self.app.data.computedX, self.app.data.computedY = self.app.data.holeyKinematics.forward(
                            self.app.data.leftChain, self.app.data.rightChain, self.app.data.xval, self.app.data.yval)
                    else:
                        # the -999999 value tells the UI client to ignore the data.
                        self.app.data.computedX = -999999
                        self.app.data.computedY = -999999

                    # sets bad error values to zero.  Not sure if needed anymore.
                    if math.isnan(self.app.data.leftError):
                        self.app.data.leftErrorValue = 0
                    if math.isnan(self.app.data.rightError):
                        self.app.data.rightErrorValue = 0

            except:
                self.app.data.console_queue.put("One Error Report Command Misread")
                return

            # only send the error information if it has changed at least slightly.
            leftDiff = abs(self.app.data.leftError - self.app.data.leftError_prev)
            rightDiff = abs(self.app.data.rightError - self.app.data.rightError_prev)

            if (leftDiff + rightDiff) >= 0.001:
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

    def activateModal(self, title, message, modalType, resume="false", progress="false"):
        '''
        Sends socket message to UI client to activate a modal
        :param title: Title to be used for the modal
        :param message: The message that should appear in the modal body
        :param modalType: The type of modal (content, notification, alarm).. I don't think content modals come via this
        fucntion because modalSize is hardcoded to small.
        :param resume: Whether to have a resume button on the modal.. used while gcode is running
        :param progress: Whether to show the progress bar/spinner
        :return:
        '''
        data = json.dumps(
            {"title": title, "message": message, "resume": resume, "progress": progress, "modalSize": "small",
             "modalType": modalType})
        socketio.emit("message", {"command": "activateModal", "data": data, "dataFormat": "json"},
                      namespace="/MaslowCNC",
                      )

    def sendAlarm(self, message):
        '''
        Sends an alarm to the UI client via socket.  Alarms display as a scrolling marque on right side of screen.
        :param message:
        :return:
        '''
        data = json.dumps({"message": message})
        socketio.emit("message", {"command": "alarm", "data": data, "dataFormat": "json"},
                      namespace="/MaslowCNC",
                      )

    def sendControllerMessage(self, message):
        '''
        Sends a message from the controller to the UI client.  This occurs for messages that aren't processed by
        webcontrol in the main UI Processor loop.
        :param message:
        :return:
        '''
        socketio.emit("message", {"command": "controllerMessage", "data": json.dumps(message), "dataFormat": "json"},
                      namespace="/MaslowCNC")

    def sendWebMCPMessage(self, message):
        '''
        Seems to just send a shutdown message to webmcp.. everything else appears to be commented out.
        :param message:
        :return:
        '''
        # print(message)
        # socketio.emit("message", {"command": json.dumps(message), "dataFormat": "json"},namespace="/WebMCP")
        socketio.emit("shutdown", namespace="/WebMCP")

    def sendPositionMessage(self, position):
        '''
        Sends the position message to UI client.  Not sure why I separated this from the only function that calls it.
        :param position:
        :return:
        '''
        socketio.emit("message", {"command": "positionMessage", "data": json.dumps(position), "dataFormat": "json"},
                      namespace="/MaslowCNC")

    def sendErrorValueMessage(self, position):
        '''
        Sends the error value message to UI client.  Not sure why I separated this from the only function that calls it.
        :param position:
        :return:
        '''
        socketio.emit("message", {"command": "errorValueMessage", "data": json.dumps(position), "dataFormat": "json"},
                      namespace="/MaslowCNC")

    def sendCameraMessage(self, message, _data=""):
        '''
        Sends message to the UI client regarding camera.. message could be to turn camera display on or off, or to
        update the camera display.
        :param message:
        :param _data:
        :return:
        '''
        data = json.dumps({"command": message, "data": _data})
        socketio.emit(
            "message", {"command": "cameraMessage", "data": data, "dataFormat": "json"}, namespace="/MaslowCNC"
        )

    def updatePIDData(self, message, _data=""):
        '''
        Sends PID test data to UI client.
        :param message:
        :param _data:
        :return:
        '''
        data = json.dumps({"command": message, "data": _data})
        socketio.emit(
            "message", {"command": "updatePIDData", "data": data, "dataFormat": "json"}, namespace="/MaslowCNC"
        )

    def sendGcodeUpdate(self):
        '''
        Sends the gcode display data to the UI client.  Originally this was sent uncompressed but later I added
        compression to speed up the transmisison process.
        :return:
        '''
        if self.app.data.compressedGCode3D is not None:
            self.app.data.console_queue.put("Sending Gcode compressed")
            # turn on spinner on UI clients
            socketio.emit("message", {"command": "showFPSpinner",
                                      "data": len(self.app.data.compressedGCode3D), "dataFormat": "int"},
                          namespace="/MaslowCNC", )
            # pause to let the spinner get turned on.
            time.sleep(0.25)
            # send the data.  Once processed by the UI client, the client will turn off the spinner.
            socketio.emit("message", {"command": "gcodeUpdateCompressed",
                                      "data": self.app.data.compressedGCode3D, "dataFormat": "base64"},
                          namespace="/MaslowCNC", )
            self.app.data.console_queue.put("Sent Gcode compressed")
        else:
            #send "" if there is no compressed data (i.e., because there's no gcode to compress)
            socketio.emit("message", {"command": "gcodeUpdateCompressed",
                                      "data": "", "dataFormat": "base64"},
                          namespace="/MaslowCNC", )

    def sendBoardUpdate(self):
        '''
        Sends board information including cutdata.  boardData is dimensions, material, ID.  cutData is an array that
        defines the area that has been cut.
        :return:
        '''
        boardData = self.app.data.boardManager.getCurrentBoard().getBoardInfoJSON()
        if boardData is not None:
            self.app.data.console_queue.put("Sending Board Data")
            socketio.emit("message", {"command": "boardDataUpdate",
                                      "data": boardData, "dataFormat": "json"},
                          namespace="/MaslowCNC", )
            self.app.data.console_queue.put("Sent Board Data")

        cutData = self.app.data.boardManager.getCurrentBoard().getCompressedCutData()
        if True:  # cutData is not None:
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
        '''
        Sends the units in use to the UI Client.
        :return:
        '''
        units = self.app.data.config.getValue(
            "Computed Settings", "units"
        )
        data = json.dumps({"setting": "units", "value": units})
        socketio.emit("message", {"command": "requestedSetting", "data": data, "dataFormat": "json"},
                      namespace="/MaslowCNC", )

    def distToMoveUpdate(self):
        '''
        Sends the value to populate the distance to move on the frontpage.
        :return:
        '''
        distToMove = self.app.data.config.getValue(
            "Computed Settings", "distToMove"
        )
        data = json.dumps({"setting": "distToMove", "value": distToMove})
        socketio.emit("message", {"command": "requestedSetting", "data": data, "dataFormat": "json"},
                      namespace="/MaslowCNC", )

    def unitsUpdateZ(self):
        '''
        Sends the z-units in use to the UI client
        :return:
        '''
        unitsZ = self.app.data.config.getValue(
            "Computed Settings", "unitsZ"
        )
        data = json.dumps({"setting": "unitsZ", "value": unitsZ})
        socketio.emit("message", {"command": "requestedSetting", "data": data, "dataFormat": "json"},
                      namespace="/MaslowCNC", )

    def distToMoveUpdateZ(self):
        '''
        Sends the value to populate the distance to move on the z-axis popup.
        :return:
        '''
        distToMoveZ = self.app.data.config.getValue(
            "Computed Settings", "distToMoveZ"
        )
        data = json.dumps({"setting": "distToMoveZ", "value": distToMoveZ})
        socketio.emit("message", {"command": "requestedSetting", "data": data, "dataFormat": "json"},
                      namespace="/MaslowCNC", )

    def processMessage(self, _message):
        '''
        This function process all the webcontrol initiated ui_queue1 messages.  I separated this because the main queue
        function was getting annoyingly big.  it basically just calls the function that has been requested.
        :param _message: a json containing the message
        :return:
        '''
        # parse the message to get to its components
        msg = json.loads(_message)
        if msg["command"] == "WebMCP":
            self.sendWebMCPMessage(msg["message"])
        if msg["command"] == "SendAlarm":
            self.sendAlarm(msg["message"])
        if msg["command"] == "Action":
            if msg["message"] == "gcodeUpdate":
                self.sendGcodeUpdate()
            elif msg["message"] == "boardUpdate":
                self.sendBoardUpdate()
            elif msg["message"] == "unitsUpdate":
                self.unitsUpdate()
            elif msg["message"] == "distToMoveUpdate":
                self.distToMoveUpdate()
            elif msg["message"] == "unitsUpdateZ":
                self.unitsUpdateZ()
            elif msg["message"] == "distToMoveUpdateZ":
                self.distToMoveUpdateZ()
            elif msg["message"] == "updateTimer":
                # TODO: clean this up .. edit: sendCalibrationMessage got deleted somewhere.
                # self.sendCalibrationMessage("updateTimer", json.loads(msg["data"]))
                pass
            elif msg["message"] == "updateCamera":
                self.sendCameraMessage("updateCamera", json.loads(msg["data"]))
            elif msg["message"] == "updatePIDData":
                self.updatePIDData("updatePIDData", json.loads(msg["data"]))
            elif msg["message"] == "clearAlarm":
                msg["data"] = json.dumps({"data": ""})
                socketio.emit("message", {"command": msg["message"], "data": msg["data"], "dataFormat": "json"},
                              namespace="/MaslowCNC")
            # I'm pretty sure this can be cleaned up into just a continuation of elif's
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
                    title = json.loads(msg["data"])
                    msg["data"] = json.dumps({"title": title})  # msg["data"]})
                socketio.emit("message", {"command": msg["message"], "data": msg["data"], "dataFormat": "json"},
                              namespace="/MaslowCNC")
        # I think I was working on clearing on an issue with the formatting of messages so I added this.  I think the
        # only function that calls it is the serialPortThread when webcontrol connects to the arduino.
        elif msg["command"] == "TextMessage":
            socketio.emit("message", {"command": "controllerMessage", "data": msg["data"], "dataFormat": "json"},
                          namespace="/MaslowCNC")
        # Alerts activate the modal.  If alerts are sent on top of each other, it can mess up the UI client display.
        elif msg["command"] == "Alert":
            self.activateModal(msg["message"], msg["data"], "alert")
        elif msg["command"] == "SpinnerMessage":
            self.activateModal("Notification:", msg["data"], "notification", progress="spinner")

    def sendCalibrationImage(self, message, _data):
        '''
        Sends the calibration image (either an image or the test image)
        :param message:
        :param _data:
        :return:
        '''

        data = json.dumps({"command": message, "data": _data})

        socketio.emit(
            "message", {"command": "updateCalibrationImage", "data": data, "dataFormat": "json"}, namespace="/MaslowCNC"
        )

    def performHealthCheck(self):
        '''
        This function sends a message to the UI clients every 5 seconds.  It contains cpuUsage, current bufferSize as
        reported by the controller, and indication if the uploadFlag is enabled or disabled.  The client prevents the
        user from performing certain functions when the gcode is being sent (i.e., uploadFlag enabled).
        :return:
        '''
        currentTime = time.time()
        if currentTime - self.lastHealthCheck > 5:
            self.lastHealthCheck = currentTime
            load = max(psutil.cpu_percent(interval=None, percpu=True))
            weAreBufferingLines = bool(int(self.app.data.config.getValue("Maslow Settings", "bufferOn")))
            if weAreBufferingLines:
                bufferSize = self.app.data.bufferSize
            else:
                bufferSize = -1
            healthData = {
                "cpuUsage": load,
                "bufferSize": bufferSize,
            }
            socketio.emit("message", {"command": "healthMessage", "data": json.dumps(healthData), "dataFormat": "json"},
                          namespace="/MaslowCNC")
            self.performStatusCheck(True)

    def performStatusCheck(self, healthCheckCalled=False):
        '''
        This function sends a message to the client if it detects a change in the following parameters:
        uploadFlag, positioningMode, currentTool
        Also sends on every health check to get new connected clients in sync.
        :return:
        '''
        update = healthCheckCalled
        if self.previousUploadFlag != self.app.data.uploadFlag:
            update = True
            self.previousUploadFlag = self.app.data.uploadFlag
        if self.previousPositioningMode != self.app.data.positioningMode:
            update = True
            self.previousPositioningMode = self.app.data.positioningMode
        if self.previousCurrentTool != self.app.data.currentTool:
            update = True
            self.previousCurrentTool = self.app.data.currentTool

        #print("positioning mode = "+str(self.app.data.positioningMode))

        if update:
            statusData = {
                "uploadFlag": self.app.data.uploadFlag,
                "positioningMode": self.app.data.positioningMode,
                "currentTool": self.app.data.currentTool,
            }
            socketio.emit("message",
                          {"command": "statusMessage", "data": json.dumps(statusData), "dataFormat": "json"},
                          namespace="/MaslowCNC")

    def isChainLengthZero(self, msg):
        #Message: Unable to find valid machine position for chain lengths 0.00, 0.00 Left Chain Length
        # If one chain length is zero, it will report as above.
        if msg.find("lengths 0.00") != -1:
            return True
        if msg.find(", 0.00") != -1:
            return True
        return False

