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
                            # todo:
                            oo = 1
                            # app.setErrorOnScreen(message)
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
                        print(self.data.controllerFirmwareVersion)
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
                            if self.data.controllerFirmwareVersion < float(self.data.version):
                                self.data.ui_queue1.put("Alert", "Alert",
                                    "<p>Warning, your firmware is out of date and may not work correctly with this version of WebControl.</p>"
                                    + "<p>WebControl Version "
                                    + str(self.data.version)
                                    + "</p><p>"
                                    + message
                                    + "</p><p>Please, click Actions->Update Firmware to update the controller to the latest WebControl-compatible code.</p>"
                                )
                            if self.data.controllerFirmwareVersion > float(self.data.version):
                                self.data.ui_queue1.put("Alert", "Alert",
                                    "<p>Warning, your version of WebControl is out of date and may not work with this firmware version</p>"
                                    + "<p>WebControl Version "
                                    + str(self.data.version)
                                    + "</p><p>"
                                    + message
                                    + "</p><p>Please, update WebControl via WebMCP.</p>"
                                )
                    elif message == "ok\r\n":
                        pass  # displaying all the 'ok' messages clutters up the display

                    ### Velocity PID Testing Processing###
                    elif message[0:26] == "--PID Velocity Test Stop--":
                        self.data.inPIDVelocityTest = False
                        print("PID velocity test stopped")
                        print(self.data.PIDVelocityTestData)
                        data = json.dumps({"result": "velocity", "data": self.data.PIDVelocityTestData})
                        self.data.ui_queue1.put("Action","updatePIDData",data)
                        #send data
                    elif self.data.inPIDVelocityTest:
                        if message.find("Kp=") == -1:
                            self.data.PIDVelocityTestData.append(float(message))
                    elif message[0:27] == "--PID Velocity Test Start--":
                        self.data.inPIDVelocityTest = True
                        self.data.PIDVelocityTestData = []
                        print("PID velocity test started")
                    ### END ###
                    ### Position PID Testing Processing###
                    elif message[0:26] == "--PID Position Test Stop--":
                        self.data.inPIDPositionTest = False
                        print("PID position test stopped")
                        print(self.data.PIDPositionTestData)
                        data = json.dumps({"result": "position", "data": self.data.PIDPositionTestData})
                        self.data.ui_queue1.put("Action", "updatePIDData", data)
                        #send data
                    elif self.data.inPIDPositionTest:
                        if message.find("Kp=") == -1:
                            self.data.PIDPositionTestData.append(float(message))
                    elif message[0:27] == "--PID Position Test Start--":
                        self.data.inPIDPositionTest = True
                        self.data.PIDPositionTestData = []
                        print("PID position test started")
                    ### END ###
                    else:
                        self.data.ui_controller_queue.put(message)

