from DataStructures.makesmithInitFuncs import MakesmithInitFuncs

import time
import math
import json


class MessageProcessor(MakesmithInitFuncs):
    '''
    This class processes messages from the controller and sends them to the UI message queue if something needs to get relayed to the user
    '''

    def start(self):
        while True:
            time.sleep(0.001)
            while not self.data.message_queue.empty():  # if there is new data to be read
                message = self.data.message_queue.get()
                # send message to web for display in appropriate column
                if message != "":
                    if message[0] != "[" and message[0] != "<":
                        self.data.ui_queue.put(message)
                if message[0] == "<":
                    self.data.ui_queue.put(message)
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
                            print(e)
                            print("No function has requested a measurement")
                elif message[0:13] == "Maslow Paused":
                    self.data.uploadFlag = 0
                    print(message)
                elif message[0:8] == "Message:":
                    if (
                        self.data.calibrationInProcess
                        and message[0:15] == "Message: Unable"
                    ):  # this suppresses the annoying messages about invalid chain lengths during the calibration process
                        break
                    self.data.previousUploadStatus = self.data.uploadFlag
                    self.data.uploadFlag = 0
                    if message.find('adjust Z-Axis') != -1:
                        self.data.ui_queue.put(message)
                elif message[0:6] == "ALARM:":
                    self.data.previousUploadStatus = self.data.uploadFlag
                    self.data.uploadFlag = 0
                    self.data.ui_queue.put(message)
                elif message[0:8] == "Firmware":
                    self.data.logger.writeToLog(
                        "Ground Control Version " + str(self.data.version) + "\n"
                    )
                    print(
                        "Ground Control "
                        + str(self.data.version)
                        + "\r\n"
                        + message
                        + "\r\n"
                    )
                    # Check that version numbers match
                    if float(message[-7:]) < float(self.data.version):
                        self.data.ui_queue.put(
                            "Message: Warning, your firmware is out of date and may not work correctly with this version of Ground Control\n\n"
                            + "Ground Control Version "
                            + str(self.data.version)
                            + "\r\n"
                            + message
                        )
                    if float(message[-7:]) > float(self.data.version):
                        self.data.ui_queue.put(
                            "Message: Warning, your version of Ground Control is out of date and may not work with this firmware version\n\n"
                            + "Ground Control Version "
                            + str(self.data.version)
                            + "\r\n"
                            + message
                        )
                elif message == "ok\r\n":
                    pass  # displaying all the 'ok' messages clutters up the display
                else:
                    print(message)



