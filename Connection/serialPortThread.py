from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
import time
from collections import deque
import re


class SerialPortThread(MakesmithInitFuncs):
    """
    SerialPortThread is the thread which handles direct communication with the CNC machine over the Serial port.
    It sends and received message which are then passsed to the main thread via the message_queue
    where they are processed by the UI.
    """

    machineIsReadyForData = False  # Tracks whether last command was acked
    lastWriteTime = time.time()
    bufferSize = 126  # The total size of the arduino buffer
    bufferSpace = bufferSize  # The amount of space currently available in the buffer
    lengthOfLastLineStack = deque()
    weAreBufferingLines = 0
    # Minimum time between lines sent to allow Arduino to cope
    # could be smaller (0.02) however larger number doesn't seem to impact performance
    MINTimePerLine = 0.05

    def __init__(self, serialInstance):
        self._serialInstance = serialInstance

    def _write(self, message, isQuickCommand=False):
        """
        Sends messages to controller.  No change from what I can tell from ground control.
        :param message:
        :param isQuickCommand:
        :return:
        """
        taken = time.time() - self.lastWriteTime
        if taken < self.MINTimePerLine:  # wait between sends
            time.sleep(self.MINTimePerLine)  # could use (taken - MINTimePerLine)

        message = message + "\n"

        if len(message) > 1:
            self.data.console_queue.put("Sending serial port write: " + str(message).rstrip("\n"))

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

            # Monitor gcode for positioning mode change requests.
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

            # Try sending message to serial port.
            try:
                # Update positioning mode after message has been sent.
                self._serialInstance.write(message)
                # If positioning mode has changed then update.
                if positioningMode is not None:
                    self.data.positioningMode = positioningMode

                self.data.logger.writeToLog("Sent: " + str(message.decode()))
            except:
                self.data.console_queue.put("Serial port write failed.")
                self.data.logger.writeToLog("Serial port write failed: " + str(message.decode()))

            self.lastWriteTime = time.time()
        else:
            self.data.console_queue.put("Skipping: " + str(message).rstrip("\n"))

    def sendNextLine(self):
        """
        Sends the next line of gcode through the serial port.
        """
        if self.data.gcodeIndex < len(self.data.gcode):
            line = self.data.gcode[self.data.gcodeIndex]
            # Filter comments from line.
            filtersparsed = re.sub(
                r"\(([^)]*)\)", "", line
            )
            # Replace mach3 style gcode comments with newline.
            line = re.sub(
                r";([^.]*)?", "", filtersparsed
            )
            # Replace standard ; initiated gcode comments with newline
            # Check if command is going to be issued that pauses the controller.
            self.manageToolChange(line)
            if not line.isspace():  # If all spaces, don't send. Likely a comment.
                # Put gcode home shift here. Only if in absolute mode (G90)
                if self.data.positioningMode == 0:
                    line = self.data.gcodeFile.moveLine(line)
                self._write(line)
                # If there is a units change, then update the UI client so position messages are processed correctly.
                if line.find("G20") != -1:
                    if self.data.units != "INCHES":
                        self.data.actions.updateSetting(
                            "toInches", 0, True
                        ) # value doesn't matter.
                if line.find("G21") != -1:
                    if self.data.units != "MM":
                        self.data.actions.updateSetting(
                            "toMM", 0, True
                        )  # Value doesn't matter.
                # Send a gcode update to UI client.
                self.data.actions.sendGCodePositionUpdate(self.data.gcodeIndex)

            # Increment gcode index.
            if self.data.gcodeIndex + 1 < len(self.data.gcode):
                self.data.gcodeIndex = self.data.gcodeIndex + 1
            else:
                self.data.uploadFlag = 0
                self.data.gcodeIndex = 0
                self.data.console_queue.put("Gcode Ended")

    def manageToolChange(self, line):
        if line.find("M0") != -1 or line.find("M1") != -1 or line.find("M6") != -1:
            # if this is a different tool, the controller will respond with a 'Tool Change:' and pause.
            # if this is a the same tool as the controller is currently tracking, it will continue on.
            # first, determine the tool being called for...
            toolNumber = int(self.extractGcodeValue(line, "T", 0))
            print(toolNumber)
            print(self.data.currentTool)
            # so, in the first case...
            if toolNumber != self.data.currentTool:
                # set uploadFlag to -1 to turn off sending more lines (after this one)
                # -1 means it was set by an M command
                print("found M command")
                self.data.uploadFlag = -1
                self.data.currentTool = toolNumber
                ## new stuff
                # self.data.quick_queue.put("~")
                # self.data.ui_queue1.put("Action", "setAsResume", "")
                ## end new stuff

                # now, the issue is that if the controller gets reset, then the tool number will revert to 0.. so
                # on serial port connect/reconnect, reinitialize tool number to 0

            # but in the second case, just continue on..

            ## new stuff
            # self.data.quick_queue.put("~")
            # self.data.ui_queue1.put("Action", "setAsResume", "")
            ## end new stuff

    def getmessage(self, stop_event):
        """
        Opens a serial connection called self.serialInstance
        Processes all the messages from controller.
        :return:
        """

        self.weAreBufferingLines = bool(
            int(self.data.config.getValue("Maslow Settings", "bufferOn"))
        )
        self.lastMessageTime = time.time()

        while not stop_event.is_set():

            # Read serial line from machine if available
            # -------------------------------------------------------------------------------------
            lineFromMachine = ""

            try:
                if self._serialInstance.in_waiting > 0:
                    # the need for the .decode() at the end MIGHT be a python3 thing.  ground control doesn't have
                    # it.
                    lineFromMachine = self._serialInstance.readline().decode()
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
                    # free up that space in the buffer
                    self.bufferSpace = (
                        self.bufferSpace + self.lengthOfLastLineStack.pop()
                    )

            # Write to the machine if ready
            # -------------------------------------------------------------------------------------

            # send any emergency instructions to the machine if there are any
            if self.data.quick_queue.empty() != True:
                command = self.data.quick_queue.get_nowait()
                self._write(command, True)
                self.data.quick_queue.task_done()

            # send regular instructions to the machine if there are any
            # print("bSpace="+str(self.bufferSpace)+", bSize="+str(self.bufferSize)+", ready="+str(self.machineIsReadyForData))
            if self.bufferSpace == self.bufferSize:
                if self.data.gcode_queue.empty() != True:
                    if self.machineIsReadyForData:
                        command = self.data.gcode_queue.get_nowait()  # + " "
                        # filter out comments
                        # replace mach3 style gcode comments with newline
                        filtersparsed = re.sub(r"\(([^)]*)\)", "", command)
                        # replace standard ; initiated gcode comments with ''
                        command = re.sub(r";([^.]*)?", "", filtersparsed)
                        # if there's something left..
                        if len(command) != 0:
                            command = command + " "
                            self.manageToolChange(command)
                            self._write(command)

                            # if units have changed, update settings and notify UI clients to stay in sync
                            if command.find("G20") != -1:
                                if self.data.units != "INCHES":
                                    self.data.actions.updateSetting(
                                        "toInches", 0, True
                                    )  # value = doesn't matter
                            if command.find("G21") != -1:
                                if self.data.units != "MM":
                                    self.data.actions.updateSetting(
                                        "toMM", 0, True
                                    )  # value = doesn't matter
                            # send updated gcode position to UI clients
                            self.data.actions.sendGCodePositionUpdate(
                                self.data.gcodeIndex, recalculate=True
                            )
                        self.data.gcode_queue.task_done()

            # Send the next line of gcode to the machine if we're running a program and uploadFlag is enabled. Will
            # send lines to buffer if there is space and the feature is turned on
            # Also, don't send if there's still data in gcode_queue.
            if (
                self.data.uploadFlag == 1
                and len(self.data.gcode) > 0
                and self.data.gcode_queue.empty()
            ):
                if self.weAreBufferingLines:
                    try:
                        # todo: clean this up because the line gets filtered twice.. once to make sure its not too
                        # long, and the second in the sendNextLine command.. bit redundant.
                        line = self.data.gcode[self.data.gcodeIndex]
                        # replace mach3 style gcode comments with newline
                        filtersparsed = re.sub(r"\(([^)]*)\)", "", line)
                        # replace standard ; initiated gcode comments with newline
                        line = re.sub(r";([^.]*)?", "", filtersparsed)
                        # if there is space in the buffer send line
                        if self.bufferSpace > len(line):
                            self.sendNextLine()
                    except IndexError:
                        self.data.console_queue.put("index error when reading gcode")
                        # we don't want the whole serial thread to close if the gcode can't be sent because of an
                        # index error (file deleted...etc)
                else:
                    if (
                        self.bufferSpace == self.bufferSize
                        and self.machineIsReadyForData
                    ):
                        # if the receive buffer is empty and the machine has acked the last line complete...
                        self.sendNextLine()
                        self.data.console_queue.put("index error when reading gcode")

            # Check for serial connection loss when not using fake servo
            # -------------------------------------------------------------------------------------
            if self.data.fakeServoStatus == False:
                if time.time() - self.lastMessageTime > 5:
                    self.data.console_queue.put("Connection Timed Out")
                    self.data.serialPort.closeConnection()
                    return

            time.sleep(0.01)

    def extractGcodeValue(self, readString, target, defaultReturn):
        # Reads a string and returns the value of number following the target character.
        # if no number is found, defaultReturn is returned

        begin = readString.find(target)
        end = self.findEndOfNumber(readString, begin + 1)
        numberAsString = readString[begin + 1 : end]

        numberAsFloat = float(numberAsString)

        if begin == -1:
            return defaultReturn
        else:
            return numberAsFloat

    def findEndOfNumber(self, textString, index):
        # Return the index of the last digit of the number beginning at the index passed in.

        i = index
        while i < len(textString):
            if textString[i].isdigit() or textString[i] == ".":
                i = i + 1
            else:
                return i
        return i
