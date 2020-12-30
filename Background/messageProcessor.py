from DataStructures.makesmithInitFuncs import MakesmithInitFuncs

import time
import math
import json


class MessageProcessor(MakesmithInitFuncs):
    """
    This class processes messages from the controller and sends them to the UI message queue if something needs to get relayed to the user
    """

    def start(self):

        while True:
            # give other threads opportunity to run
            time.sleep(0.001)
            # check for available update file every hour.
            if time.time()-self.data.lastChecked > 60*60:
                self.data.lastChecked = time.time()
                self.data.releaseManager.checkLatestRelease(True)
                self.data.helpManager.checkForUpdatedHelp()
            # process messages while queue is not empty.  Everything else is on hold until queue is cleared.
            while (  not self.data.message_queue.empty() ):  # if there is new data to be read
                message = self.data.message_queue.get()
                if message != "":
                    if message[0] == "<":
                        # message to be processed by UIProcessor
                        self.data.ui_controller_queue.put(message)
                    elif message[0] == "$":
                        # setting received from controller
                        self.data.config.receivedSetting(message)
                    elif message[0] == "[":
                        # positional error or measurement message
                        if message[1:4] == "PE:":
                            # send to UIProcessor for processing
                            self.data.ui_controller_queue.put(message)
                        elif message[1:8] == "Measure":
                            # get distance and call the callback.
                            measuredDist = float(message[9 : len(message) - 3])
                            try:
                                self.data.measureRequest(measuredDist)
                            except Exception as e:
                                self.data.console_queue.put(str(e))
                                self.data.console_queue.put("No function has requested a measurement")
                    elif message[0:14] == "FAKE_SERVO off":
                        self.data.fakeServoStatus = False
                        self.data.console_queue.put(message)
                    elif message[0:13] == "FAKE_SERVO on":
                        self.data.fakeServoStatus = True
                        self.data.console_queue.put(message)
                    elif message[0:13] == "Maslow Paused":
                        # received controller-initiated pause message.  Free controller to accept moves and send
                        # message to UIProcessor to process.
                        self.data.uploadFlag = 0
                        self.data.ui_controller_queue.put(message)
                    elif message[0:8] == "Message:":
                        # suppress the annoying messages about invalid chain lengths during the calibration process
                        if (self.data.calibrationInProcess and message[0:15] == "Message: Unable"):
                            break
                        # track the previous uploadFlag and stop uploading.  Likely am going to receive a message
                        # that requires a pause.
                        self.data.previousUploadStatus = self.data.uploadFlag
                        self.data.uploadFlag = 0
                        if message.find("adjust Z-Axis") != -1:
                            # z-axis must not be enabled.  Send message to UIProcessor for processing.
                            # set manualZAxisAdjust, but not sure its needed if manual adjustment is being used.
                            # Todo: cleanup if needed.
                            self.data.manualZAxisAdjust = True
                            self.data.ui_controller_queue.put(message)
                        if message[0:15] == "Message: Unable":
                            # received an error message from forward.kinematics that chain lengths don't resolve.
                            # send to UIProcessor for processing.
                            self.data.ui_controller_queue.put(message)
                    elif message[0:6] == "ALARM:":
                        # something bad happened, likley sled not keeping up.
                        # keep track of upload status, pause run, and send to UIProcessor for processing.
                        self.data.previousUploadStatus = self.data.uploadFlag
                        self.data.uploadFlag = 0
                        self.data.ui_controller_queue.put(message)
                    elif message[0:8] == "Firmware":
                        '''
                        send this alarm clear if Firmware is received.  The thought is that if there is an alarm and
                        this message appears, then the connection to the arduino has been reset.
                        '''
                        self.data.ui_queue1.put("Action", "clearAlarm", "")

                        self.data.logger.writeToLog("Ground Control Version " + str(self.data.version) + "\n")
                        self.data.console_queue.put("WebControl " + str(self.data.version) + "\r\n" + message + "\r\n")
                        # Check that version numbers match
                        self.data.controllerFirmwareVersion = float(message[16-len(message):])
                        tmpVersion = self.data.controllerFirmwareVersion
                        # <50 implies a stock firmware
                        if tmpVersion <50:
                            if self.data.stockFirmwareVersion is not None:
                                if tmpVersion < float(self.data.stockFirmwareVersion):
                                    self.data.ui_queue1.put("Alert", "Alert",
                                                            "<p>Warning, you are running a stock firmware that is not up to date.  This version may not work correctly with this version of WebControl.</p>"
                                                            + "</p><p>Please, click Actions->Upgrade Stock Firmware to update the controller to the latest WebControl-compatible code.</p>"
                                                            +"<p>WebControl:"+str(float(self.data.stockFirmwareVersion))+", Controller:"+str(tmpVersion)+"</p>"
                                                            )
                                elif tmpVersion > float(self.data.stockFirmwareVersion):
                                    self.data.ui_queue1.put("Alert", "Alert",
                                                            "<p>Warning, you are running a stock firmware that is newer than what is included in WebControl.  This version may not work correctly with this version of WebControl.</p>"
                                                            +"<p>WebControl:"+str(float(self.data.stockFirmwareVersion))+", Controller:"+str(tmpVersion)+"</p>"
                                                            )
                        # 50 <= x < 100 implies holey calibration firmware
                        if tmpVersion >= 50 and tmpVersion < 100:
                            if self.data.holeyFirmwareVersion is not None:
                                if tmpVersion < float(self.data.holeyFirmwareVersion):
                                    self.data.ui_queue1.put("Alert", "Alert",
                                                                "<p>Warning, you are running a Holey Calibration firmware that is not up to date.  This version may not work correctly with this version of WebControl.</p>"
                                                                + "</p><p>Please, click Actions->Upgrade Holey Firmware to update the controller to the latest WebControl-compatible code.</p>"
                                                                +"<p>WebControl:"+str(float(self.data.holeyFirmwareVersion))+", Controller:"+str(tmpVersion)+"</p>"
                                                                )
                                elif tmpVersion > float(self.data.holeyFirmwareVersion):
                                    self.data.ui_queue1.put("Alert", "Alert",
                                                            "<p>Warning, you are running a Holey Calibration firmware that is newer than what is included in WebControl.  This version may not work correctly with this version of WebControl.</p>"
                                                            "<p>WebControl:"+str(float(self.data.holeyFirmwareVersion))+", Controller:"+str(tmpVersion)+"</p>"
                                                            )
                        # x >= 100 implies optical calibration firmware
                        if tmpVersion >= 100:
                            if self.data.customFirmwareVersion is not None:
                                if tmpVersion < float(self.data.customFirmwareVersion):
                                    self.data.ui_queue1.put("Alert", "Alert",
                                                            "<p>Warning, you are running a custom firmware that is not"
                                                            + " up to date.  This version may not work correctly with"
                                                            + " this version of WebControl.</p>"
                                                            + "</p><p>Please, click Actions->Upgrade Custom Firmware to"
                                                            + " update the controller to the latest"
                                                            + " WebControl-compatible code.</p>"
                                                            + "<p>WebControl:"
                                                            + str(float(self.data.customFirmwareVersion))
                                                            + ", Controller:"+str(tmpVersion)+"</p>"
                                                            )
                                elif tmpVersion > float(self.data.customFirmwareVersion):
                                    self.data.ui_queue1.put("Alert", "Alert",
                                                            "<p>Warning, you are running a custom firmware that is "
                                                            + "newer than what is included in WebControl.  This version"
                                                            + " may not work correctly with this version of WebControl."
                                                            + "</p><p>WebControl:"
                                                            + str(float(self.data.customFirmwareVersion))
                                                            + ", Controller:" + str(tmpVersion)+"</p>"
                                                            )

                    elif message == "ok\r\n":
                        pass  # displaying all the 'ok' messages clutters up the display

                    ###
                    ### Velocity PID Testing Processing
                    ### Watch for messages and log data
                    ###
                    elif message[0:26] == "--PID Velocity Test Stop--":
                        self.data.actions.velocityPIDTestRun("stop", "")
                    elif self.data.inPIDVelocityTest:
                        self.data.actions.velocityPIDTestRun("running", message)
                    elif message[0:27] == "--PID Velocity Test Start--":
                        self.data.actions.velocityPIDTestRun("start", "")
                    ###
                    ### Positional PID Testing Processing
                    ### Watch for messages and log data
                    ###
                    elif message[0:26] == "--PID Position Test Stop--":
                        self.data.actions.positionPIDTestRun("stop", "")
                    elif self.data.inPIDPositionTest:
                        self.data.actions.positionPIDTestRun("running", message)
                    elif message[0:27] == "--PID Position Test Start--":
                        self.data.actions.positionPIDTestRun("start", "")

                    else:
                        # Just send it to the UIProcessor for processing.
                        self.data.ui_controller_queue.put(message)

