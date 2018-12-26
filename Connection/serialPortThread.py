from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from DataStructures.data import Data
import serial
import time
from collections import deque
import json


class SerialPortThread(MakesmithInitFuncs):
    """

    SerialPort is the thread which handles direct communication with the CNC machine.
    SerialPort initializes the connection and then receives
    and parses messages. These messages are then passed to the main thread via the message_queue
    queue where they are added to the GUI

    """

    # def __init__(self, app):
    #    self.app = app
    #    print "serialportthread.self.data.logger="+str(self.data.logger)

    machineIsReadyForData = False  # Tracks whether last command was acked
    lastWriteTime = time.time()
    bufferSize = 126  # The total size of the arduino buffer
    bufferSpace = bufferSize  # The amount of space currently available in the buffer
    lengthOfLastLineStack = deque()

    # Minimum time between lines sent to allow Arduino to cope
    # could be smaller (0.02) however larger number doesn't seem to impact performance
    MINTimePerLine = 0.05

    def _write(self, message, isQuickCommand=False):
        # message = message + 'L' + str(len(message) + 1 + 2 + len(str(len(message))) )

        taken = time.time() - self.lastWriteTime
        if taken < self.MINTimePerLine:  # wait between sends
            # self.data.logger.writeToLog("Sleeping: " + str( taken ) + "\n")
            time.sleep(self.MINTimePerLine)  # could use (taken - MINTimePerLine)

        message = message + "\n"
        # message = message.encode()
        #print("Sending: " + str(message).rstrip('\n'))
        if message[0]!='(':
            self.data.console_queue.put("Sending: " + str(message).rstrip('\n'))
        
            self.bufferSpace = self.bufferSpace - len(
                message
            )  # shrink the available buffer space by the length of the line

            self.machineIsReadyForData = False

            # if this is a quick message sent as soon as the button is pressed (like stop) then put it on the right side of the queue
            # because it is the first message sent, otherwise put it at the end (left) because it is the last message sent
            if isQuickCommand:
                if message[0] == "!":
                    # if we've just sent a stop command, the buffer is now empty on the arduino side
                    self.lengthOfLastLineStack.clear()
                    self.bufferSpace = self.bufferSize - len(message)
                    self.lengthOfLastLineStack.append(len(message))
                else:
                    self.lengthOfLastLineStack.append(len(message))
            else:
                self.lengthOfLastLineStack.appendleft(len(message))

            message = message.encode()
            try:
                self.serialInstance.write(message)
                self.data.logger.writeToLog("Sent: " + str(message.decode()))
            except:
                #print("write issue")
                self.data.console_queue.put("write issue")
                self.data.logger.writeToLog("Send FAILED: " + str(message.decode()))

            self.lastWriteTime = time.time()
        else:
            self.data.console_queue.put("Skipping: " + str(message).rstrip('\n'))

    def _getFirmwareVersion(self):
        self.data.gcode_queue.put("B05 ")

    def _setupMachineUnits(self):
        if self.data.units == "INCHES":
            self.data.gcode_queue.put("G20 ")
            self.data.console_queue.put("Sent G20")
        else:
            self.data.gcode_queue.put("G21 ")
            self.data.console_queue.put("Sent G21")

    def _requestSettingsUpdate(self):
        self.data.gcode_queue.put("$$")

    def sendNextLine(self):
        """
            Sends the next line of gcode to the machine
        """
        if self.data.gcodeIndex < len(self.data.gcode):
            if self.data.uploadFlag:
                line = self.data.gcode[self.data.gcodeIndex]
                self._write(self.data.gcode[self.data.gcodeIndex])
                if line.find("G20") != -1:
                    if self.data.units != "INCHES":
                        self.data.actions.updateSetting("toInches", 0, True)  # value = doesn't matter
                if line.find("G21") != -1:
                    if self.data.units != "MM":
                        self.data.actions.updateSetting("toMM", 0, True)  # value = doesn't matter
                self.data.actions.sendGCodePositionUpdate(self.data.gcodeIndex)

                # increment gcode index
                if self.data.gcodeIndex + 1 < len(self.data.gcode):
                    self.data.gcodeIndex = self.data.gcodeIndex + 1
                else:
                    self.data.uploadFlag = 0
                    self.data.gcodeIndex = 0
                    self.data.console_queue.put("Gcode Ended")
                    #print("Gcode Ended")

    def getmessage(self):
        # opens a serial connection called self.serialInstance

        # check for serial version being > 3
        if float(serial.VERSION[0]) < 3:
            self.data.ui_queue1.put("Alert", "Incompability Detected",
                "Pyserial version 3.x is needed, but version "
                + serial.VERSION
                + " is installed"
            )

        weAreBufferingLines = bool(
            int(self.data.config.getValue("Maslow Settings", "bufferOn"))
        )

        try:
            self.data.console_queue.put("connecting")
            #print("connecting")
            self.data.comport = self.data.config.getValue("Maslow Settings", "COMport")
            self.serialInstance = serial.Serial(
                self.data.comport, 57600, timeout=0.25
            )  # self.data.comport is the com port which is opened
        except:
            #print(self.data.comport + " is unavailable or in use")
            self.data.console_queue.put(self.data.comport + " is unavailable or in use")
            # self.data.ui_queue.put("\n" + self.data.comport + " is unavailable or in use")
            pass
        else:
            #print("\r\nConnected on port " + self.data.comport + "\r\n")
            self.data.console_queue.put("\r\nConnected on port " + self.data.comport + "\r\n")
            self.data.ui_queue1.put("Action", "connectionStatus", {'status': 'connected', 'port': self.data.comport})
            #self.data.ui_queue.put(
            #    "Action: connectionStatus:_" + json.dumps({'status': 'connected', 'port': self.data.comport})
            #)  # the "_" facilitates the parse
            #self.data.ui_queue.put(
            #    "\r\nConnected on port " + self.data.comport + "\r\n"
            #)
            self.data.ui_queue1.put("TextMessage", "", "Connected on port " + self.data.comport)
            gcode = ""
            msg = ""
            subReadyFlag = True

            self.serialInstance.parity = (
                serial.PARITY_ODD
            )  # This is something you have to do to get the connection to open properly. I have no idea why.
            self.serialInstance.close()
            self.serialInstance.open()
            self.serialInstance.close()
            self.serialInstance.parity = serial.PARITY_NONE
            self.serialInstance.open()

            # print "port open?:"
            # print self.serialInstance.isOpen()
            self.lastMessageTime = time.time()
            self.data.connectionStatus = 1
            self._getFirmwareVersion()
            self._setupMachineUnits()
            self._requestSettingsUpdate()

            while True:

                # Read serial line from machine if available
                # -------------------------------------------------------------------------------------
                lineFromMachine = ""

                try:
                    if self.serialInstance.in_waiting > 0:
                        lineFromMachine = self.serialInstance.readline().decode()
                        # lineFromMachine = lineFromMachine.encode('utf-8')
                        self.lastMessageTime = time.time()
                        self.data.message_queue.put(lineFromMachine)
                except:
                    pass

                # Check if a line has been completed
                if lineFromMachine == "ok\r\n" or (
                    len(lineFromMachine) >= 6 and lineFromMachine[0:6] == "error:"
                ):
                    self.machineIsReadyForData = True
                    if (
                        bool(self.lengthOfLastLineStack) is True
                    ):  # if we've sent lines to the machine
                        self.bufferSpace = (
                            self.bufferSpace + self.lengthOfLastLineStack.pop()
                        )  # free up that space in the buffer

                        # Write to the machine if ready
                # -------------------------------------------------------------------------------------

                # send any emergency instructions to the machine if there are any
                if self.data.quick_queue.empty() != True:
                    command = self.data.quick_queue.get_nowait()
                    self._write(command, True)

                # send regular instructions to the machine if there are any
                #print("bSpace="+str(self.bufferSpace)+", bSize="+str(self.bufferSize)+", ready="+str(self.machineIsReadyForData))
                if self.bufferSpace == self.bufferSize and self.machineIsReadyForData:
                    if self.data.gcode_queue.empty() != True:
                        command = self.data.gcode_queue.get_nowait() + " "
                        self._write(command)

                # Send the next line of gcode to the machine if we're running a program. Will send lines to buffer if there is space
                # and the feature is turned on
                if weAreBufferingLines:
                    try:
                        if self.bufferSpace > len(
                            self.data.gcode[self.data.gcodeIndex]
                        ):  # if there is space in the buffer keep sending lines
                            self.sendNextLine()
                    except IndexError:
                        self.data.console_queue.put("index error when reading gcode")
                        #print("index error when reading gcode")
                        # we don't want the whole serial thread to close if the gcode can't be sent because of an index error (file deleted...etc)
                else:
                    if (
                        self.bufferSpace == self.bufferSize
                        and self.machineIsReadyForData
                    ):  # if the receive buffer is empty and the machine has acked the last line complete
                        self.sendNextLine()

                        # Check for serial connection loss
                # -------------------------------------------------------------------------------------
                if time.time() - self.lastMessageTime > 5:
                    self.data.console_queue.put("Connection Timed Out")
                    #print("Connection Timed Out")
                    #self.data.ui_queue.put("Connection Timed Out\n")
                    self.data.ui_queue1.put("TextMessage", "", "Connection Timed Out")
                    if self.data.uploadFlag:
                        self.data.ui_queue1.put("Alert", "Connection Lost",
                                                "Message: USB connection lost. This has likely caused the machine to loose it's calibration, which can cause erratic behavior. It is recommended to stop the program, remove the sled, and perform the chain calibration process. Press Continue to override and proceed with the cut.")
                        #self.data.ui_queue.put(
                        #    "Message: USB connection lost. This has likely caused the machine to loose it's calibration, which can cause erratic behavior. It is recommended to stop the program, remove the sled, and perform the chain calibration process. Press Continue to override and proceed with the cut."
                        #)
                    else:
                        self.data.ui_queue1.put("Alert", "Connection Lost", "It is possible that the serial port selected is not the one used by the Maslow's Arduino, or that the firmware is not loaded on the Arduino.")
                        #self.data.ui_queue.put(
                        #    "It is possible that the serial port selected is not the one used by the Maslow's Arduino,\nor that the firmware is not loaded on the Arduino."
                        #)
                    self.data.connectionStatus = 0
                    self.serialInstance.close()
                    return

                if self.data.requestSerialClose:
                    self.data.requestSerialClose = False
                    self.data.connectionStatus = 0
                    self.serialInstance.close()

                # Sleep between passes to save CPU
                time.sleep(0.001)
