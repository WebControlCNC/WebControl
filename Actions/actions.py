from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from DataStructures.makesmithInitFuncs import MakesmithInitFuncs

import os
import sys
import threading
import re
import math
import serial.tools.list_ports
import glob
import json


class Actions(MakesmithInitFuncs):
    def processAction(self, msg):
        if msg["data"]["command"] == "resetChainLengths":
            if not self.resetChainLengths():
                self.data.ui_queue.put("Message: Error with resetting chain lengths.")
        elif msg["data"]["command"] == "move":
            if not self.move(msg["data"]["arg"], float(msg["data"]["arg1"])):
                self.data.ui_queue.put("Message: Error with initiating move.")
        elif msg["data"]["command"] == "moveZ":
            if not self.moveZ(msg["data"]["arg"], float(msg["data"]["arg1"])):
                self.data.ui_queue.put("Message: Error with initiating Z-Axis move.")
        elif msg["data"]["command"] == "reportSettings":
            self.data.gcode_queue.put("$$")
        elif msg["data"]["command"] == "home":
            if not self.home():
                self.data.ui_queue.put("Message: Error with returning to home.")
        elif msg["data"]["command"] == "defineHome":
            if self.defineHome():
                ## the gcode file might change the active units so we need to inform the UI of the change.
                self.data.ui_queue.put("Action: unitsUpdate gcodeUpdate")
            else:
                self.data.ui_queue.put("Message: Error with defining home.")
        elif msg["data"]["command"] == "defineZ0":
            if not self.data.actions.defineZ0():
                self.data.ui_queue.put("Message: Error with defining Z-Axis zero.")
        elif msg["data"]["command"] == "stopZ":
            if not self.stopZ():
                self.data.ui_queue.put("Message: Error with stopping Z-Axis movement")
        elif msg["data"]["command"] == "startRun":
            if not self.startRun():
                if len(self.data.gcode) > 0:
                    self.data.ui_queue.put("Message: Error with starting run.")
                else:
                    self.data.ui_queue.put("Message: No GCode file loaded.")
        elif msg["data"]["command"] == "stopRun":
            if not self.stopRun():
                self.data.ui_queue.put("Message: Error with stopping run")
        elif msg["data"]["command"] == "moveToDefault":
            if not self.moveToDefault():
                self.data.ui_queue.put(
                    "Message: Error with moving to default chain lengths"
                )
        elif msg["data"]["command"] == "testMotors":
            if not self.testMotors():
                self.data.ui_queue.put("Message: Error with testing motors")
        elif msg["data"]["command"] == "wipeEEPROM":
            if not self.wipeEEPROM(msg["data"]["arg"]):
                self.data.ui_queue.put("Message: Error with wiping EEPROM")
        elif msg["data"]["command"] == "pauseRun":
            if not self.pauseRun():
                self.data.ui_queue.put("Message: Error with pausing run")
        elif msg["data"]["command"] == "resumeRun":
            if not self.resumeRun():
                self.data.ui_queue.put("Message: Error with resuming run")
        elif msg["data"]["command"] == "returnToCenter":
            if not self.returnToCenter():
                self.data.ui_queue.put("Message: Error with returning to center")
        elif msg["data"]["command"] == "clearGCode":
            if self.clearGCode():
                # send blank gcode to UI
                self.data.ui_queue.put("Action: gcodeUpdate")
                # socketio.emit("gcodeUpdate", {"data": ""}, namespace="/MaslowCNC")
            else:
                self.data.ui_queue.put("Message: Error with clearing gcode")
        elif msg["data"]["command"] == "moveGcodeZ":
            if not self.moveGcodeZ(int(msg["data"]["arg"])):
                self.data.ui_queue.put("Message: Error with moving to Z move")
        elif (
            msg["data"]["command"] == "moveGcodeIndex"
            or msg["data"]["command"] == "moveGcodeZ"
        ):
            if not self.moveGcodeIndex(int(msg["data"]["arg"])):
                self.data.ui_queue.put("Message: Error with moving to index")
        elif msg["data"]["command"] == "setSprockets":
            if not self.setSprockets(msg["data"]["arg"], msg["data"]["arg1"]):
                self.data.ui_queue.put("Message: Error with setting sprocket")
        elif msg["data"]["command"] == "setSprocketsAutomatic":
            if not self.setSprocketsAutomatic():
                self.data.ui_queue.put(
                    "Message: Error with setting sprockets automatically"
                )
        elif msg["data"]["command"] == "setSprocketsZero":
            if not self.setSprocketsZero():
                self.data.ui_queue.put(
                    "Message: Error with setting sprockets zero value"
                )
        elif msg["data"]["command"] == "setSprocketsDefault":
            if not self.setSprocketsDefault():
                self.data.ui_queue.put(
                    "Message: Error with setting sprockets as default"
                )
        elif msg["data"]["command"] == "updatePorts":
            if not self.updatePorts():
                self.data.ui_queue.put("Message: Error with updating list of ports")
        elif msg["data"]["command"] == "macro1":
            if not self.macro(1):
                self.data.ui_queue.put("Message: Error with performing macro")
        elif msg["data"]["command"] == "macro2":
            if not self.macro(2):
                self.data.ui_queue.put("Message: Error with performing macro")
        elif msg["data"]["command"] == "optical_onStart":
            if not self.data.opticalCalibration.on_Start():
                self.data.ui_queue.put(
                    "Message: Error with starting optical calibration"
                )
        elif msg["data"]["command"] == "optical_Calibrate":
            if not self.data.opticalCalibration.on_Calibrate(msg["data"]["arg"]):
                self.data.ui_queue.put(
                    "Message: Error with starting optical calibration"
                )
        elif msg["data"]["command"] == "saveOpticalCalibrationConfiguration":
            if not self.data.opticalCalibration.saveOpticalCalibrationConfiguration(msg["data"]["arg"]):
                self.data.ui_queue.put(
                    "Message: Error with saving optical calibration configuration"
                )
        elif msg["data"]["command"] == "stopOpticalCalibration":
            if not self.data.opticalCalibration.stopOpticalCalibration():
                self.data.ui_queue.put("Message: Error with stopping optical calibration.")
        elif msg["data"]["command"] == "testOpticalCalibration":
            if not self.data.opticalCalibration.testImage(msg["data"]["arg"]):
                self.data.ui_queue.put("Message: Error with test image.")
        elif msg["data"]["command"] == "findCenterOpticalCalibration":
            if not self.data.opticalCalibration.findCenter(msg["data"]["arg"]):
                self.data.ui_queue.put("Message: Error with find Center.")
        elif msg["data"]["command"] == "saveAndSendOpticalCalibration":
            if not self.data.opticalCalibration.saveAndSend():
                self.data.ui_queue.put("Message: Error with saving and sending calibration matrix.")
        elif msg["data"]["command"] == "reloadCalibration":
            errorX, errorY, curveX, curveY = self.data.opticalCalibration.reloadCalibration()
            if errorX is None or errorY is None or curveX is None or curveY is None:
                self.data.ui_queue.put("Message: Error with (re)loading calibration.")
            else:
                data = {"errorX": errorX, "errorY": errorY}
                self.data.ui_queue.put(
                    "Action: updateOpticalCalibrationError:_" + json.dumps(data)
                )
                #data = {"curveX": curveX, "curveY": curveY}
                #self.data.ui_queue.put(
                #    "Action: updateOpticalCalibrationCurve:_" + json.dumps(data)
                #)
        elif msg["data"]["command"] == "clearCalibration":
            if not self.data.opticalCalibration.clearCalibration():
                self.data.ui_queue.put("Message: Error with clearing calibration.")
        elif msg["data"]["command"] == "curveFitOpticalCalibration":
            curveX, curveY = self.data.opticalCalibration.surfaceFit()
            if curveX is None or curveY is None:
                self.data.ui_queue.put("Message: Error with curve fitting calibration data.")
            else:
                data = {"curveX":curveX, "curveY":curveY}
                self.data.ui_queue.put(
                    "Action: updateOpticalCalibrationCurve:_" + json.dumps(data)
                )
        elif msg["data"]["command"] == "adjustCenter":
            if not self.adjustCenter(msg["data"]["arg"]):
                self.data.ui_queue.put("Message: Error with adjusting center.")

    def defineHome(self):
        try:
            if self.data.units == "MM":
                scaleFactor = 25.4
            else:
                scaleFactor = 1.0
            self.data.gcodeShift = [
                round(self.data.xval, 4),
                round(self.data.yval, 4),
            ]
            self.data.config.setValue("Advanced Settings", "homeX", str(round(self.data.xval,4)))
            self.data.config.setValue("Advanced Settings", "homeY", str(round(self.data.yval,4)))
            position = {"xval": self.data.xval, "yval": self.data.yval}
            self.data.ui_queue.put(
                "Action: homePositionMessage:_" + json.dumps(position)
            )  # the "_" facilitates the parse
            self.data.console_queue.put("gcodeShift="+str(self.data.gcodeShift[0])+", "+str(self.data.gcodeShift[1]))
            self.data.gcodeFile.loadUpdateFile()
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def home(self):
        try:
            self.data.gcode_queue.put("G90  ")
            # todo:self.gcodeVel = "[MAN]"
            safeHeightMM = float(
                self.data.config.getValue("Maslow Settings", "zAxisSafeHeight")
            )
            safeHeightInches = safeHeightMM / 25.5
            if self.data.units == "INCHES":
                self.data.gcode_queue.put("G00 Z" + "%.3f" % (safeHeightInches))
            else:
                self.data.gcode_queue.put("G00 Z" + str(safeHeightMM))
            homeX = self.data.config.getValue("Advanced Settings", "homeX")
            homeY = self.data.config.getValue("Advanced Settings", "homeY")
            self.data.gcode_queue.put(
                "G00 X"
                + str(homeX)
                + " Y"
                + str(homeY)
                + " "
            )
            self.data.gcode_queue.put("G00 Z0 ")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def resetChainLengths(self):
        try:
            self.data.gcode_queue.put("B08 ")
            if self.data.units == "INCHES":
                self.data.gcode_queue.put("G20 ")
            else:
                self.data.gcode_queue.put("G21 ")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def defineZ0(self):
        try:
            self.data.gcode_queue.put("G10 Z0 ")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def stopZ(self):
        try:
            self.data.quick_queue.put("!")
            with self.data.gcode_queue.mutex:
                self.data.gcode_queue.queue.clear()
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def startRun(self):
        try:
            if len(self.data.gcode)>0:
                self.data.uploadFlag = 1
                self.data.gcode_queue.put(self.data.gcode[self.data.gcodeIndex])
                self.data.gcodeIndex += 1
                return True
            else:
                return False
        except Exception as e:
            self.data.console_queue.put(str(e))
            self.data.uploadFlag = 0
            self.data.gcodeIndex = 0
            return False

    def stopRun(self):
        try:
            self.data.console_queue.put("stopping run")
            self.data.uploadFlag = 0
            self.data.gcodeIndex = 0
            self.data.quick_queue.put("!")
            with self.data.gcode_queue.mutex:
                self.data.gcode_queue.queue.clear()
            # TODO: app.onUploadFlagChange(self.stopRun, 0)
            self.data.console_queue.put("Gcode stopped")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def moveToDefault(self):
        try:
            chainLength = self.data.config.getValue(
                "Advanced Settings", "chainExtendLength"
            )
            self.data.gcode_queue.put("G90 ")
            self.data.gcode_queue.put(
                "B09 R" + str(chainLength) + " L" + str(chainLength) + " "
            )
            self.data.gcode_queue.put("G91 ")

            # the firmware doesn't update sys.xPosition or sys.yPosition during a singleAxisMove
            # therefore, the machine doesn't know where it is.
            # so let tell the machine where it's at by sending a reset chain length
            self.data.gcode_queue.put("B08 ")

            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def testMotors(self):
        try:
            self.data.gcode_queue.put("B04 ")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def wipeEEPROM(self, extent):
        try:
            if extent == "All":
                self.data.gcode_queue.put("$RST=* ")
            elif extent == "Settings":
                self.data.gcode_queue.put("$RST=$ ")
            elif extent == "Maslow":
                self.data.gcode_queue.put("$RST=# ")
            else:
                return False
            #timer = threading.Timer(6.0, self.data.gcode_queue.put("$$"))
            #timer.start()
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def pauseRun(self):
        try:
            self.data.uploadFlag = 0
            self.data.console_queue.put("Run Paused")
            self.data.ui_queue.put("Action: setAsResume")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def resumeRun(self):
        try:
            if self.data.manualZAxisAdjust:
                self.data.uploadFlag = self.data.previousUploadStatus
            else:
                self.data.uploadFlag = 1
            # send cycle resume command to unpause the machine
            self.data.quick_queue.put("~")
            self.data.ui_queue.put("Action: setAsPause")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def returnToCenter(self):
        try:
            self.data.gcode_queue.put("G90  ")
            safeHeightMM = float(
                self.data.config.getValue("Maslow Settings", "zAxisSafeHeight")
            )
            safeHeightInches = safeHeightMM / 24.5
            if self.data.units == "INCHES":
                self.data.gcode_queue.put("G00 Z" + "%.3f" % (safeHeightInches))
            else:
                self.data.gcode_queue.put("G00 Z" + str(safeHeightMM))
            self.data.gcode_queue.put("G00 X0.0 Y0.0 ")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def clearGCode(self):
        try:
            self.data.gcodeFile.clearGcode()
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def moveGcodeZ(self, moves):
        try:
            dist = 0
            for index, zMove in enumerate(self.data.zMoves):
                if moves > 0 and zMove > self.data.gcodeIndex:
                    dist = self.data.zMoves[index + moves - 1] - self.data.gcodeIndex
                    break
                if moves < 0 and zMove < self.data.gcodeIndex:
                    dist = self.data.zMoves[index + moves + 1] - self.data.gcodeIndex
            if self.moveGcodeIndex(dist):
                # this command will continue on in the moveGcodeIndex "if"
                return True
            else:
                return False
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def moveGcodeIndex(self, dist):
        try:
            maxIndex = len(self.data.gcode) - 1
            targetIndex = self.data.gcodeIndex + dist

            # print "targetIndex="+str(targetIndex)
            # check to see if we are still within the length of the file
            if maxIndex < 0:  # break if there is no data to read
                return
            elif targetIndex < 0:  # negative index not allowed
                self.data.gcodeIndex = 0
            elif (
                targetIndex > maxIndex
            ):  # reading past the end of the file is not allowed
                self.data.gcodeIndex = maxIndex
            else:
                self.data.gcodeIndex = targetIndex
            gCodeLine = self.data.gcode[self.data.gcodeIndex]
            # print self.data.gcode
            # print "gcodeIndex="+str(self.data.gcodeIndex)+", gCodeLine:"+gCodeLine
            xTarget = 0
            yTarget = 0

            try:
                x = re.search("X(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
                if x:
                    xTarget = float(x.groups()[0])
                    self.data.previousPosX = xTarget
                else:
                    xTarget = self.data.previousPosX

                y = re.search("Y(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)

                if y:
                    yTarget = float(y.groups()[0])
                    self.data.previousPosY = yTarget
                else:
                    yTarget = self.data.previousPosY
                # self.gcodecanvas.positionIndicator.setPos(xTarget,yTarget,self.data.units)
                # print "xTarget:"+str(xTarget)+", yTarget:"+str(yTarget)
                position = {"xval": xTarget, "yval": yTarget, "zval": self.data.zval}
                self.data.ui_queue.put(
                    "Action: positionMessage:_" + json.dumps(position)
                )  # the "_" facilitates the parse
            except Exception as e:
                self.data.console_queue.put(str(e))
                self.data.console_queue.put("Unable to update position for new gcode line")
                return False
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def move(self, direction, distToMove):

        if self.data.config.getValue("WebControl Settings","diagonalMove") == 1:
            diagMove = round(math.sqrt(distToMove*distToMove/2.0), 4)
        else:
            diagMove = distToMove
        try:
            if direction == "upLeft":
                self.data.gcode_queue.put(
                    "G91 G00 X"
                    + str(-1.0 * diagMove)
                    + " Y"
                    + str(diagMove)
                    + " G90 "
                )
            elif direction == "up":
                self.data.gcode_queue.put("G91 G00 Y" + str(distToMove) + " G90 ")
            elif direction == "upRight":
                self.data.gcode_queue.put(
                    "G91 G00 X" + str(diagMove) + " Y" + str(diagMove) + " G90 "
                )
            elif direction == "left":
                self.data.gcode_queue.put(
                    "G91 G00 X" + str(-1.0 * distToMove) + " G90 "
                )
            elif direction == "right":
                self.data.gcode_queue.put("G91 G00 X" + str(distToMove) + " G90 ")
            elif direction == "downLeft":
                self.data.gcode_queue.put(
                    "G91 G00 X"
                    + str(-1.0 * diagMove)
                    + " Y"
                    + str(-1.0 * diagMove)
                    + " G90 "
                )
            elif direction == "down":
                self.data.gcode_queue.put(
                    "G91 G00 Y" + str(-1.0 * distToMove) + " G90 "
                )
            elif direction == "downRight":
                self.data.gcode_queue.put(
                    "G91 G00 X"
                    + str(diagMove)
                    + " Y"
                    + str(-1.0 * diagMove)
                    + " G90 "
                )
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def moveZ(self, direction, distToMoveZ):
        try:
            self.data.config.setValue("Computed Settings", "distToMoveZ", distToMoveZ)
            unitsZ = self.data.config.getValue("Computed Settings", "unitsZ")
            if unitsZ == "MM":
                self.data.gcode_queue.put("G21 ")
            else:
                self.data.gcode_queue.put("G20 ")
            if direction == "raise":
                self.data.gcode_queue.put(
                    "G91 G00 Z" + str(float(distToMoveZ)) + " G90 "
                )
            elif direction == "lower":
                self.data.gcode_queue.put(
                    "G91 G00 Z" + str(-1.0 * float(distToMoveZ)) + " G90 "
                )
            units = self.data.config.getValue("Computed Settings", "units")
            if units == "MM":
                self.data.gcode_queue.put("G21 ")
            else:
                self.data.gcode_queue.put("G20 ")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def updateSetting(self, setting, value, fromGcode = False):
        try:
            if setting == "toInches" or setting == "toMM":
                if fromGcode:
                    value = float(self.data.config.getValue("Computed Settings", "distToMove")) * 25.4
                if setting == "toInches":
                    self.data.units = "INCHES"
                    self.data.config.setValue("Computed Settings", "units", self.data.units)
                    scaleFactor = 1.0/25.4
                    self.data.tolerance = 0.020
                    self.data.gcode_queue.put("G20 ")
                else:
                    self.data.units = "MM"
                    self.data.config.setValue("Computed Settings", "units", self.data.units)
                    scaleFactor = 25.4
                    self.data.tolerance = 0.5
                    self.data.gcode_queue.put("G21 ")
                self.data.gcodeShift = [
                  self.data.gcodeShift[0] * scaleFactor,
                  self.data.gcodeShift[1] * scaleFactor,
                ]
                self.data.config.setValue("Computed Settings", "distToMove", value)
                self.data.config.setValue("Advanced Settings", "homeX", self.data.gcodeShift[0])
                self.data.config.setValue("Advanced Settings", "homeY", self.data.gcodeShift[1])
                #print("gcodeShift=" + str(self.data.gcodeShift[0]) + ", " + str(self.data.gcodeShift[1]))
                #sending this out updates all the attached clients.
                self.data.ui_queue.put("Action: unitsUpdate")
                self.data.ui_queue.put("Action: distToMoveUpdate")
                position = {"xval": self.data.gcodeShift[0], "yval": self.data.gcodeShift[1]}
                self.data.ui_queue.put(
                    "Action: homePositionMessage:_" + json.dumps(position)
                )  # the "_" facilitates the parse
            elif setting == "toInchesZ":
                self.data.units = "INCHES"
                self.data.config.setValue(
                    "Computed Settings", "unitsZ", self.data.units
                )
                self.data.config.setValue("Computed Settings", "distToMoveZ", value)
            elif setting == "toMMZ":
                self.data.units = "MM"
                self.data.config.setValue(
                    "Computed Settings", "unitsZ", self.data.units
                )
                self.data.config.setValue("Computed Settings", "distToMoveZ", value)
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def setSprockets(self, sprocket, degrees):
        try:
            degValue = round(
                float(self.data.config.getValue("Advanced Settings", "gearTeeth"))
                * float(self.data.config.getValue("Advanced Settings", "chainPitch"))
                / 360.0
                * degrees,
                4,
            )
            self.data.gcode_queue.put("G91 ")
            if (
                self.data.config.getValue("Advanced Settings", "chainOverSprocket")
                == "Bottom"
            ):
                degValue *= -1.0
            self.data.gcode_queue.put("B09 " + sprocket + str(degValue) + " ")
            self.data.gcode_queue.put("G90 ")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def setVerticalAutomatic(self):
        # set the call back for the measurement
        try:
            self.data.measureRequest = self.getLeftChainLength
            # request a measurement
            self.data.gcode_queue.put("B10 L")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def getLeftChainLength(self, dist):
        self.leftChainLength = dist
        # set the call back for the measurement
        self.data.measureRequest = self.getRightChainLength
        # request a measurement
        self.data.gcode_queue.put("B10 R")

    def getRightChainLength(self, dist):
        self.rightChainLength = dist
        self.moveToVertical()

    def moveToVertical(self):
        chainPitch = float(self.data.config.get("Advanced Settings", "chainPitch"))
        gearTeeth = float(self.data.config.get("Advanced Settings", "gearTeeth"))
        distPerRotation = chainPitch * gearTeeth

        distL = -1 * (self.leftChainLength % distPerRotation)
        distR = -1 * (self.rightChainLength % distPerRotation)

        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 L" + str(distL) + " ")
        self.data.gcode_queue.put("B09 R" + str(distR) + " ")
        self.data.gcode_queue.put("G90 ")

    def setSprocketsZero(self):
        # mark that the sprockets are straight up
        try:
            self.data.gcode_queue.put("B06 L0 R0 ")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def setSprocketsDefault(self):
        try:
            self.data.gcode_queue.put("B08 ")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def updatePorts(self):
        # refresh the list of available comports
        self.data.console_queue.put("at Update Ports")
        portsList = []
        try:
            if sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
                # this excludes your current terminal "/dev/tty"
                sysports = glob.glob("/dev/tty[A-Za-z]*")
                for port in sysports:
                    portsList.append(port)
            elif sys.platform.startswith("darwin"):
                sysports = glob.glob("/dev/tty.*")
                for port in sysports:
                    portsList.append(port)
            elif sys.platform.startswith("win"):
                list = serial.tools.list_ports.comports()
                for element in list:
                    portsList.append(element.device)
            if len(portsList) == 0:
                portsList.append("None")
            self.data.comPorts = portsList
            self.data.ui_queue.put("Action: updatePorts")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def calibrate(self, result):
        try:
            motorYoffsetEst, rotationRadiusEst, chainSagCorrectionEst, cut34YoffsetEst = self.data.triangularCalibration.calculate(
                result
            )
            if motorYoffsetEst == False:
                return False
            return (
                motorYoffsetEst,
                rotationRadiusEst,
                chainSagCorrectionEst,
                cut34YoffsetEst,
            )
            """
            self.data.config.setValue('Maslow Settings', 'motorOffsetY', str(motorYoffsetEst))
            self.data.config.setValue('Advanced Settings', 'rotationRadius', str(rotationRadiusEst))
            self.data.config.setValue('Advanced Settings', 'chainSagCorrection', str(chainSagCorrectionEst))

            # With new calibration parameters return sled to workspace center

            self.data.gcode_queue.put("G21 ")
            self.data.gcode_queue.put("G90 ")
            self.data.gcode_queue.put("G40 ")
            self.data.gcode_queue.put("G0 X0 Y0 ")
            """
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def macro(self, number):
        try:
            if number == 1:
                macro = self.data.config.getValue("Maslow Settings", "macro1")
            else:
                macro = self.data.config.getValue("Maslow Settings", "macro2")
            self.data.gcode_queue.put(macro)
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def testImage(self):
        try:
            self.data.opticalCalibration.testImage()
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def adjustCenter(self, dist):
        try:
            motorOffsetY = float(self.data.config.getValue("Maslow Settings","motorOffsetY"))+dist
            self.data.config.setValue('Maslow Settings', 'motorOffsetY', str(motorOffsetY))
            if not self.returnToCenter():
                return False
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def processSettingRequest(self, section, setting):
        try:
            if setting == "homePosition":
                homeX = self.data.config.getValue("Advanced Settings", "homeX")
                homeY = self.data.config.getValue("Advanced Settings", "homeY")
                position = {"xval": homeX, "yval": homeY}
                self.data.ui_queue.put(
                    "Action: homePositionMessage:_" + json.dumps(position)
                )  # the "_" facilitates the parse
                return None, None
            elif setting == "calibrationCurve":
                try:
                    xCurve = [0,0,0,0,0,0]
                    yCurve = [0,0,0,0,0,0]
                    xCurve[0] = float(self.data.config.getValue('Optical Calibration Settings', 'calX0'))
                    xCurve[1] = float(self.data.config.getValue('Optical Calibration Settings', 'calX1'))
                    xCurve[2] = float(self.data.config.getValue('Optical Calibration Settings', 'calX2'))
                    xCurve[3] = float(self.data.config.getValue('Optical Calibration Settings', 'calX3'))
                    xCurve[4] = float(self.data.config.getValue('Optical Calibration Settings', 'calX4'))
                    xCurve[5] = float(self.data.config.getValue('Optical Calibration Settings', 'calX5'))
                    yCurve[0] = float(self.data.config.getValue('Optical Calibration Settings', 'calY0'))
                    yCurve[1] = float(self.data.config.getValue('Optical Calibration Settings', 'calY1'))
                    yCurve[2] = float(self.data.config.getValue('Optical Calibration Settings', 'calY2'))
                    yCurve[3] = float(self.data.config.getValue('Optical Calibration Settings', 'calY3'))
                    yCurve[4] = float(self.data.config.getValue('Optical Calibration Settings', 'calY4'))
                    yCurve[5] = float(self.data.config.getValue('Optical Calibration Settings', 'calY5'))
                    data = {"curveX": xCurve, "curveY": yCurve}
                    self.data.ui_queue.put(
                        "Action: updateOpticalCalibrationCurve:_" + json.dumps(data)
                    )
                except Exception as e:
                    self.data.console_queue.put(str(e))
            elif setting == "calibrationError":
                try:
                    xyErrorArray = self.data.config.getValue("Optical Calibration Settings","xyErrorArray")
                    errorX, errorY = self.data.config.parseErrorArray(xyErrorArray, True)
                    data = {"errorX": errorX, "errorY": errorY}
                    self.data.ui_queue.put(
                        "Action: updateOpticalCalibrationError:_" + json.dumps(data)
                    )
                except Exception as e:
                    self.data.console_queue.put(str(e))
            else:
                retval = self.data.config.getValue(section, setting)
                return setting, retval
        except Exception as e:
            pass
        return None, None