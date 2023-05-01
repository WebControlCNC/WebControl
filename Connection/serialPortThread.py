from collections import deque
import time
import re

import serial

from DataStructures.makesmithInitFuncs import MakesmithInitFuncs


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
    weAreBufferingLines = 0
    # Minimum time between lines sent to allow Arduino to cope
    # could be smaller (0.02) however larger number doesn't seem to impact performance
    MINTimePerLine = 0.05

    serialInstance = None

    def _write(self, message, isQuickCommand=False):
        '''
        Sends messages to controller.  No change from what I can tell from ground control
        :param message:
        :param isQuickCommand:
        :return:
        '''
        taken = time.time() - self.lastWriteTime
        if taken < self.MINTimePerLine:  # wait between sends
            time.sleep(self.MINTimePerLine)  # could use (taken - MINTimePerLine)

        message = message + "\n"

        if len(message) > 1:
            self.data.console_queue.put(f"{__name__}: Sending: " + str(message).rstrip('\n'))
        
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

            '''
            Monitor gcode for positioning mode change requests
            '''
            positioningMode = None
            findG90 = message.rfind("G90")
            findG91 = message.rfind("G91")

            if findG90 != -1 and findG91 != -1:
                if findG90 > findG91:
                    positioningMode = 0
                else:
                    positioningMode = 1
            else:
                if findG90 != -1:
                    positioningMode = 0
                if findG91 != -1:
                    positioningMode = 1

            message = message.encode()

            '''
            try sending message
            '''
            try:
                self.serialInstance.write(message)
                # Update positioning mode after message has been sent.
                # In 'try' block to maintain state integrity if message send fails.
                if (positioningMode is not None):
                    self.data.positioningMode = positioningMode
                    #print("Set positioning mode: " + str(positioningMode))
                self.data.logger.writeToLog("Sent: " + str(message.decode()))
            except:
                self.data.console_queue.put(f"{__name__}: write issue")
                self.data.logger.writeToLog("Send FAILED: " + str(message.decode()))

            self.lastWriteTime = time.time()
        else:
            self.data.console_queue.put(f"{__name__}: Skipping: " + str(message).rstrip('\n'))

    def _getFirmwareVersion(self):
        '''
        Send command to have controller report details
        :return:
        '''
        self.data.gcode_queue.put("B05 ")

    def _setupMachineUnits(self):
        '''
        Send command to put controller in correct units state.
        :return:
        '''
        if self.data.units == "INCHES":
            self.data.gcode_queue.put("G20 ")
        else:
            self.data.gcode_queue.put("G21 ")

    def _requestSettingsUpdate(self):
        '''
        Send command to have controller report settings
        :return:
        '''
        self.data.gcode_queue.put("$$")

    def sendNextLine(self):
        """
            Sends the next line of gcode to the machine
        """
        if self.data.gcodeIndex < len(self.data.gcode):
            line = self.data.gcode[self.data.gcodeIndex]
            # filter comments from line
            filtersparsed = re.sub(r'\(([^)]*)\)', '', line)  # replace mach3 style gcode comments with newline
            line = re.sub(r';([^\n]*)?', '',filtersparsed)  # replace standard ; initiated gcode comments with newline
            # check if command is going to be issued that pauses the controller.
            self.managePause(line)
            self.manageToolChange(line)
            if not line.isspace(): # if all spaces, don't send.  likely a comment.
                # put gcode home shift here.. only if in absolute mode (G90)    
                if self.data.positioningMode == 0:
                    line = self.data.gcodeFile.moveLine(line)
                self._write(line)
                # if there is a units change, then update the UI client so position messages are processed correctly.
                if line.find("G20") != -1:
                    if self.data.units != "INCHES":
                        self.data.actions.updateSetting("toInches", 0, True)  # value = doesn't matter
                if line.find("G21") != -1:
                    if self.data.units != "MM":
                        self.data.actions.updateSetting("toMM", 0, True)  # value = doesn't matter
                # send a gcode update to UI client.
                self.data.actions.sendGCodePositionUpdate(self.data.gcodeIndex)
                # track current target Z-Axis position
                z = re.search("Z(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", line)
                if z:
                    self.data.currentZTarget = float(z.groups()[0])
                    #self.data.currentZTargetUnits = self.data.units

            # increment gcode index
            if self.data.gcodeIndex + 1 < len(self.data.gcode):
                self.data.gcodeIndex = self.data.gcodeIndex + 1
            else:
                self.data.uploadFlag = 0
                self.data.gcodeIndex = 0
                self.data.console_queue.put(f"{__name__}: Gcode Ended")

    def managePause(self, line):
        if line.find("M0 ") != -1 or line.find("M00") != -1 or line.find("M1 ") != -1 or line.find("M01") != -1:
            print("found M command for pause")
            self.data.uploadFlag = -1
            self.data.pausedUnits = self.data.units
            self.data.ui_queue1.put("Action", "setAsResume", "")
            # clear machine out of pause mode
            self.data.quick_queue.put("~")

    def manageToolChange(self, line):
        if line.find("M6 ") != -1 or line.find("M06") != -1:
            # if this is a different tool, the controller will respond with a 'Tool Change:' and pause.
            # if this is a the same tool as the controller is currently tracking, it will continue on.
            # first, determine the tool being called for...
            toolNumber = int(self.extractGcodeValue(line, 'T', 0))
            self.data.console_queue.put(f"{__name__}: {toolNumber}")
            self.data.console_queue.put(f"{__name__}: {self.data.currentTool}")
            # so, in the first case...
            if toolNumber != self.data.currentTool:
                # set uploadFlag to -1 to turn off sending more lines (after this one)
                # -1 means it was set by an M command
                print("found M command")
                self.data.uploadFlag = -1
                self.data.currentTool = toolNumber
                self.data.pausedUnits = self.data.units
                ## new stuff
                #self.data.quick_queue.put("~")
                #self.data.ui_queue1.put("Action", "setAsResume", "")
                ## end new stuff

                # now, the issue is that if the controller gets reset, then the tool number will revert to 0.. so
                # on serial port connect/reconnect, reinitialize tool number to 0

            # but in the second case, just continue on..

            ## new stuff
            #self.data.quick_queue.put("~")
            #self.data.ui_queue1.put("Action", "setAsResume", "")
            ## end new stuff

    def closeConnection(self):
        '''
        Closes the serial connection and updates the status.  Needed for firmware upgrades.
        :return:
        '''
        if self.serialInstance is not None:
            self.serialInstance.close()
            self.data.serialPort.serialPortRequest = "Closed"
            self.data.console_queue.put(f"{__name__}: connection closed at serialPortThread")
        else:
            self.data.console_queue.put(f"{__name__}: serial Instance is none??")
        return


    def getmessage(self):
        '''
        Opens a serial connection called self.serialInstance
        Processes all the messages from controller.
        :return:
        '''

        # check for serial version being > 3
        if float(serial.VERSION[0]) < 3:
            self.data.ui_queue1.put("Alert", "Incompability Detected",
                f"Pyserial version 3.x is needed, but version {serial.VERSION} is installed"
            )

        self.weAreBufferingLines = bool(int(self.data.config.getValue("Maslow Settings", "bufferOn")) )

        try:
            self.data.comport = self.data.config.getValue("Maslow Settings", "COMport")
            connectMessage = f"{__name__}:  Trying to connect to controller on COM port {self.data.comport}"
            self.data.console_queue.put(connectMessage)
            self.serialInstance = serial.Serial(
                self.data.comport, 57600, timeout=0.25
            )  # self.data.comport is the com port which is opened
        except:
            #self.data.console_queue.put(self.data.comport + " is unavailable or in use")
            pass
        else:
            self.data.console_queue.put(f"\r\n{__name__}:  Connected on port {self.data.comport}\r\n")
            self.data.ui_queue1.put("Action", "connectionStatus", {'status': 'connected', 'port': self.data.comport, 'fakeServoStatus': self.data.fakeServoStatus})
            self.data.ui_queue1.put("TextMessage", "", "Connected on port " + self.data.comport)

            self.serialInstance.parity = (
                serial.PARITY_ODD
            )  # This is something you have to do to get the connection to open properly. I have no idea why.
            self.serialInstance.close()
            self.serialInstance.open()
            self.serialInstance.close()
            self.serialInstance.parity = serial.PARITY_NONE
            self.serialInstance.open()

            self.lastMessageTime = time.time()
            self.data.connectionStatus = 1
            self._getFirmwareVersion()
            self._setupMachineUnits()
            self._requestSettingsUpdate()
            self.data.currentTool = 0  # This is necessary since the controller will have reset tool to zero.

            while True:

                # Read serial line from machine if available
                # -------------------------------------------------------------------------------------
                lineFromMachine = ""

                # check to see if the serail port needs to be closed (for firmware upgrade)
                if self.data.serialPort.serialPortRequest == "requestToClose":
                    self.data.console_queue.put(f"{__name__}: processing request to close")
                    self.closeConnection()
                    # do not change status just yet...
                    return

                try:
                    if self.serialInstance.in_waiting > 0:
                        # the need for the .decode() at the end MIGHT be a python3 thing.  ground control doesn't have
                        # it.
                        lineFromMachine = self.serialInstance.readline().decode()
                        self.lastMessageTime = time.time()
                        self.data.message_queue.put(lineFromMachine)
                except:
                    pass

                # Check if a line has been completed
                if lineFromMachine == "ok\r\n" or (len(lineFromMachine) >= 6 and lineFromMachine[0:6] == "error:"):
                    self.machineIsReadyForData = True
                    if bool(self.lengthOfLastLineStack) is True:  # if we've sent lines to the machine
                        # free up that space in the buffer
                        self.bufferSpace = (self.bufferSpace + self.lengthOfLastLineStack.pop())


                # Write to the machine if ready
                # -------------------------------------------------------------------------------------

                # send any emergency instructions to the machine if there are any
                if self.data.quick_queue.empty() != True:
                    command = self.data.quick_queue.get_nowait()
                    self._write(command, True)

                # send regular instructions to the machine if there are any
                #print("bSpace="+str(self.bufferSpace)+", bSize="+str(self.bufferSize)+", ready="+str(self.machineIsReadyForData))
                if self.bufferSpace == self.bufferSize:
                    if self.data.gcode_queue.empty() != True:
                        if self.machineIsReadyForData:
                            command = self.data.gcode_queue.get_nowait()# + " "
                            # filter out comments
                            # replace mach3 style gcode comments with newline
                            filtersparsed = re.sub(r'\(([^)]*)\)', '', command)
                            # replace standard ; initiated gcode comments with ''
                            command = re.sub(r';([^\n]*)?', '', filtersparsed)
                            # if there's something left..
                            if len(command) != 0:
                                command = command + " "
                                self.manageToolChange(command)
                                self._write(command)
                                # if units have changed, update settings and notify UI clients to stay in sync
                                if command.find("G20") != -1:
                                    if self.data.units != "INCHES":
                                        self.data.actions.updateSetting("toInches", 0, True)  # value = doesn't matter
                                if command.find("G21") != -1:
                                    if self.data.units != "MM":
                                        self.data.actions.updateSetting("toMM", 0, True)  # value = doesn't matter
                                # send updated gcode position to UI clients
                                self.data.actions.sendGCodePositionUpdate(self.data.gcodeIndex, recalculate=True)
                # Send the next line of gcode to the machine if we're running a program and uploadFlag is enabled. Will
                # send lines to buffer if there is space and the feature is turned on
                # Also, don't send if there's still data in gcode_queue.
                if self.data.uploadFlag == 1 and len(self.data.gcode) > 0 and self.data.gcode_queue.empty():
                    if self.weAreBufferingLines:
                        try:
                            # todo: clean this up because the line gets filtered twice.. once to make sure its not too
                            # long, and the second in the sendNextLine command.. bit redundant.
                            line = self.data.gcode[self.data.gcodeIndex]
                            # replace mach3 style gcode comments with newline
                            filtersparsed = re.sub(r'\(([^)]*)\)', '', line)
                            # replace standard ; initiated gcode comments with newline
                            line = re.sub(r';([^\n]*)?', '', filtersparsed)
                            # if there is space in the buffer send line
                            if self.bufferSpace > len(line):
                                self.sendNextLine()
                        except IndexError:
                            self.data.console_queue.put(f"{__name__}: index error when reading gcode")
                            # we don't want the whole serial thread to close if the gcode can't be sent because of an
                            # index error (file deleted...etc)
                    else:
                        if (self.bufferSpace == self.bufferSize and self.machineIsReadyForData ):
                            # if the receive buffer is empty and the machine has acked the last line complete...
                            self.sendNextLine()

                # Check for serial connection loss
                # -------------------------------------------------------------------------------------
                if time.time() - self.lastMessageTime > 5:
                    self.data.console_queue.put(f"{__name__}: Connection Timed Out")
                    if self.data.uploadFlag > 0:
                        self.data.ui_queue1.put("Alert", "Connection Lost",
                                                "Message: USB connection lost. This has likely caused the machine to loose it's calibration, which can cause erratic behavior. It is recommended to stop the program, remove the sled, and perform the chain calibration process. Press Continue to override and proceed with the cut.")
                    else:
                        self.data.ui_queue1.put("SendAlarm", "Alarm: Connection Failed or Invalid Firmware", "")
                    self.data.connectionStatus = 0
                    self.serialInstance.close()
                    return

                if self.data.requestSerialClose:
                    # close down the serial port.
                    self.data.requestSerialClose = False
                    self.data.connectionStatus = 0
                    self.serialInstance.close()

                time.sleep(0.01)

    def extractGcodeValue(self, readString, target, defaultReturn):
        # Reads a string and returns the value of number following the target character.
        # if no number is found, defaultReturn is returned

        begin = readString.find(target)
        end = self.findEndOfNumber(readString, begin + 1)
        numberAsString = readString[begin + 1: end]
        try:
            numberAsFloat = float(numberAsString)
        except:
            return defaultReturn

        if begin == -1:
            return defaultReturn
        else:
            return numberAsFloat

    def findEndOfNumber(self, textString, index):
        # Return the index of the last digit of the number beginning at the index passed in

        i = index
        while i < len(textString):
            if textString[i].isdigit() or textString[i] == '.':
                i = i + 1
            else:
                return i
        return i

