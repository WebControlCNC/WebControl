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
            time.sleep(0.001)
            # check for available update file
            if time.time()-self.data.lastChecked > 60*60:
                self.data.lastChecked = time.time()
                self.data.actions.checkForLatestPyRelease()
            while (
                not self.data.message_queue.empty()
            ):  # if there is new data to be read
                message = self.data.message_queue.get()
                # send message to web for display in appropriate column
                if message != "":
                    if message[0] == "<":
                        self.data.ui_controller_queue.put(message)
                    elif message[0] == "$":
                        self.data.config.receivedSetting(message)
                    elif message[0] == "[":
                        if message[1:4] == "PE:":
                            self.data.ui_controller_queue.put(message)
                        elif message[1:8] == "Measure":
                            measuredDist = float(message[9 : len(message) - 3])
                            try:
                                self.data.measureRequest(measuredDist)
                            except Exception as e:
                                self.data.console_queue.put(str(e))
                                self.data.console_queue.put("No function has requested a measurement")
                    elif message[0:13] == "Maslow Paused":
                        self.data.uploadFlag = 0
                        self.data.ui_controller_queue.put(message)
                    elif message[0:8] == "Message:":
                        if (
                            self.data.calibrationInProcess
                            and message[0:15] == "Message: Unable"
                        ):  # this suppresses the annoying messages about invalid chain lengths during the calibration process
                            break
                        self.data.previousUploadStatus = self.data.uploadFlag
                        self.data.uploadFlag = 0
                        if message.find("adjust Z-Axis") != -1:
                            self.data.manualZAxisAdjust = True
                            self.data.ui_controller_queue.put(message)
                        if message[0:15] == "Message: Unable":
                            self.data.ui_controller_queue.put(message)
                    elif message[0:6] == "ALARM:":
                        self.data.previousUploadStatus = self.data.uploadFlag
                        self.data.uploadFlag = 0
                        self.data.ui_controller_queue.put(message)
                    elif message[0:8] == "Firmware":
                        self.data.logger.writeToLog(
                            "Ground Control Version " + str(self.data.version) + "\n"
                        )
                        self.data.console_queue.put(
                            "WebControl "
                            + str(self.data.version)
                            + "\r\n"
                            + message
                            + "\r\n"
                        )
                        # Check that version numbers match
                        self.data.controllerFirmwareVersion = float(message[16-len(message):])
                        #print(self.data.controllerFirmwareVersion)
                        '''
                        if self.data.controllerFirmwareVersion < 100:
                            self.data.ui_queue1.put("Alert", "Alert",
                                "<p>Warning, you are using stock firmware with WebControl.  Custom features will be disabled.</p>"
                                + "<p>Ground Control Version "
                                + str(self.data.version)
                                + "</p><p>"
                                + message
                                + "</p>"
                            )
                        else:
                        '''
                        tmpVersion = self.data.controllerFirmwareVersion
                        if tmpVersion <50:
                            if self.data.stockFirmwareVersion is not None:
                                if tmpVersion < float(self.data.stockFirmwareVersion):
                                    self.data.ui_queue1.put("Alert", "Alert",
                                                            "<p>Warning, you are running a stock firmware that is not up to date.  This version may not work correctly with this version of WebControl.</p>"
                                                            + "</p><p>Please, click Actions->Upgrade Stock Firmware to update the controller to the latest WebControl-compatible code.</p>"
                                                            )
                                elif tmpVersion > float(self.data.stockFirmwareVersion):
                                    self.data.ui_queue1.put("Alert", "Alert",
                                                            "<p>Warning, you are running a stock firmware that is newer than what is included in WebControl.  This version may not work correctly with this version of WebControl.</p>"
                                                            )

                        if tmpVersion >= 50 and tmpVersion < 100:
                            if self.data.holeyFirmwareVersion is not None:
                                if tmpVersion < float(self.data.holeyFirmwareVersion):
                                    self.data.ui_queue1.put("Alert", "Alert",
                                                                "<p>Warning, you are running a Holey Calibration firmware that is not up to date.  This version may not work correctly with this version of WebControl.</p>"
                                                                + "</p><p>Please, click Actions->Upgrade Holey Firmware to update the controller to the latest WebControl-compatible code.</p>"
                                                                )
                                elif tmpVersion > float(self.data.holeyFirmwareVersion):
                                    self.data.ui_queue1.put("Alert", "Alert",
                                                            "<p>Warning, you are running a Holey Calibration firmware that is newer than what is included in WebControl.  This version may not work correctly with this version of WebControl.</p>"
                                                            )
                        if tmpVersion >= 100:
                            if self.data.customFirmwareVersion is not None:
                                if tmpVersion < float(self.data.customFirmwareVersion):
                                    self.data.ui_queue1.put("Alert", "Alert",
                                                            "<p>Warning, you are running a custom firmware that is not up to date.  This version may not work correctly with this version of WebControl.</p>"
                                                            + "</p><p>Please, click Actions->Upgrade Custom Firmware to update the controller to the latest WebControl-compatible code.</p>"
                                                           )
                                elif tmpVersion > float(self.data.customFirmwareVersion):
                                    self.data.ui_queue1.put("Alert", "Alert",
                                                        "<p>Warning, you are running a custom firmware that is newer than what is included in WebControl.  This version may not work correctly with this version of WebControl.</p>"
                                                        )

                        '''
                        if tmpVersion < float(self.data.version):
                            self.data.ui_queue1.put("Alert", "Alert",
                                "<p>Warning, your firmware is out of date and may not work correctly with this version of WebControl.</p>"
                                + "<p>WebControl Version "
                                + str(self.data.version)
                                + "</p><p>"
                                + message
                                + "</p><p>Please, click Actions->Update Firmware to update the controller to the latest WebControl-compatible code.</p>"
                            )
                        if tmpVersion > float(self.data.version):
                            self.data.ui_queue1.put("Alert", "Alert",
                                "<p>Warning, your version of WebControl is out of date and may not work with this firmware version</p>"
                                + "<p>WebControl Version "
                                + str(self.data.version)
                                + "</p><p>"
                                + message
                                + "</p><p>Please, update WebControl via WebMCP.</p>"
                            )
                        '''
                    elif message == "ok\r\n":
                        pass  # displaying all the 'ok' messages clutters up the display

                    ### Velocity PID Testing Processing###
                    elif message[0:26] == "--PID Velocity Test Stop--":
                        self.data.actions.velocityPIDTestRun("stop", "")
                    elif self.data.inPIDVelocityTest:
                        self.data.actions.velocityPIDTestRun("running", message)
                    elif message[0:27] == "--PID Velocity Test Start--":
                        self.data.actions.velocityPIDTestRun("start", "")
                    ### END ###

                    ### Position PID Testing Processing###
                    elif message[0:26] == "--PID Position Test Stop--":
                        self.data.actions.positionPIDTestRun("stop", "")
                    elif self.data.inPIDPositionTest:
                        self.data.actions.positionPIDTestRun("running", message)
                    elif message[0:27] == "--PID Position Test Start--":
                        self.data.actions.positionPIDTestRun("start", "")
                    ### END ###

                    else:
                        self.data.ui_controller_queue.put(message)

