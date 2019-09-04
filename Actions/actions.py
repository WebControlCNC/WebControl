
from DataStructures.makesmithInitFuncs import MakesmithInitFuncs

import os
import sys
import threading
import re
import math
import serial.tools.list_ports
import glob
import json
import time
from zipfile import ZipFile
import datetime
from gpiozero.pins.mock import MockFactory
from gpiozero import Device

class Actions(MakesmithInitFuncs):

    Device.pin_factory = MockFactory()

    def processAction(self, msg):
        try:
            if msg["data"]["command"] == "cutTriangularCalibrationPattern":
                if not self.data.triangularCalibration.cutTriangularCalibrationPattern():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with cutting triangular calibration pattern.")
            elif msg["data"]["command"] == "acceptTriangularCalibrationResults":
                if not self.data.triangularCalibration.acceptTriangularCalibrationResults():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with accepting triangular calibration results.")
            if msg["data"]["command"] == "cutHoleyCalibrationPattern":
                if not self.data.holeyCalibration.CutTestPattern():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with cutting holey calibration pattern.")
            elif msg["data"]["command"] == "acceptHoleyCalibrationResults":
                if not self.data.holeyCalibration.acceptCalibrationResults():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with accepting holey calibration results.")
            elif msg["data"]["command"] == "resetChainLengths":
                if not self.resetChainLengths():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with resetting chain lengths.")
            elif msg["data"]["command"] == "createDirectory":
                if not self.createDirectory(msg["data"]["arg"]):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with creating directory.")
            elif msg["data"]["command"] == "move":
                if not self.move(msg["data"]["arg"], float(msg["data"]["arg1"])):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with initiating move.")
            elif msg["data"]["command"] == "moveTo":
                if not self.moveTo(msg["data"]["arg"], float(msg["data"]["arg1"])):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with initiating move.")
            elif msg["data"]["command"] == "moveZ":
                if not self.moveZ(msg["data"]["arg"], float(msg["data"]["arg1"])):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with initiating Z-Axis move.")
            elif msg["data"]["command"] == "reportSettings":
                self.data.gcode_queue.put("$$")
            elif msg["data"]["command"] == "home":
                if not self.home():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with returning to home.")
            elif msg["data"]["command"] == "defineHome":
                posX= msg["data"]["arg"]
                posY= msg["data"]["arg1"]
                if self.defineHome(posX, posY):
                    ## the gcode file might change the active units so we need to inform the UI of the change.
                    self.data.ui_queue1.put("Action", "unitsUpdate", "")
                    self.data.ui_queue1.put("Action", "gcodeUpdate", "")
                else:
                    self.data.ui_queue1.put("Alert", "Alert", "Error with defining home.")
            elif msg["data"]["command"] == "defineZ0":
                if not self.data.actions.defineZ0():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with defining Z-Axis zero.")
            elif msg["data"]["command"] == "stopZ":
                if not self.stopZ():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with stopping Z-Axis movement")
            elif msg["data"]["command"] == "startRun":
                if not self.startRun():
                    if len(self.data.gcode) > 0:
                        self.data.ui_queue1.put("Alert", "Alert", "Error with starting run.")
                    else:
                        self.data.ui_queue1.put("Alert", "Alert", "No GCode file loaded.")
            elif msg["data"]["command"] == "stopRun":
                if not self.stopRun():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with stopping run")
            elif msg["data"]["command"] == "moveToDefault":
                if not self.moveToDefault():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with moving to default chain lengths")
            elif msg["data"]["command"] == "testMotors":
                if not self.testMotors():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with testing motors")
            elif msg["data"]["command"] == "wipeEEPROM":
                if not self.wipeEEPROM(msg["data"]["arg"]):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with wiping EEPROM")
            elif msg["data"]["command"] == "pauseRun":
                if not self.pauseRun():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with pausing run")
            elif msg["data"]["command"] == "resumeRun":
                if not self.resumeRun():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with resuming run")
            elif msg["data"]["command"] == "returnToCenter":
                if not self.returnToCenter():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with returning to center")
            elif msg["data"]["command"] == "clearGCode":
                if self.clearGCode():
                    # send blank gcode to UI
                    self.data.ui_queue1.put("Action", "gcodeUpdate", "")
                else:
                    self.data.ui_queue1.put("Alert", "Alert", "Error with clearing gcode")
            elif msg["data"]["command"] == "moveGcodeZ":
                if not self.moveGcodeZ(int(msg["data"]["arg"])):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with moving to Z move")
            elif msg["data"]["command"] == "moveGcodeGoto":
                if not self.moveGcodeIndex(int(msg["data"]["arg"]), True):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with moving to Z move")
            elif msg["data"]["command"] == "moveGcodeIndex":
                if not self.moveGcodeIndex(int(msg["data"]["arg"])):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with moving to index")
            elif msg["data"]["command"] == "setSprockets":
                if not self.setSprockets(msg["data"]["arg"], msg["data"]["arg1"]):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with setting sprocket")
            elif msg["data"]["command"] == "rotateSprocket":
                if not self.rotateSprocket(msg["data"]["arg"], msg["data"]["arg1"]):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with setting sprocket")                    
            elif msg["data"]["command"] == "setSprocketsAutomatic":
                if not self.setSprocketsAutomatic():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with setting sprockets automatically")
            elif msg["data"]["command"] == "setSprocketsZero":
                if not self.setSprocketsZero():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with setting sprockets zero value")
            elif msg["data"]["command"] == "setSprocketsDefault":
                if not self.setSprocketsDefault():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with setting sprockets as default")
            elif msg["data"]["command"] == "updatePorts":
                if not self.updatePorts():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with updating list of ports")
            elif msg["data"]["command"] == "macro1":
                if not self.macro(1):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with performing macro")
            elif msg["data"]["command"] == "macro2":
                if not self.macro(2):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with performing macro")
            elif msg["data"]["command"] == "optical_onStart":
                if not self.data.opticalCalibration.on_Start():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with starting optical calibration")
            elif msg["data"]["command"] == "optical_Calibrate":
                if not self.data.opticalCalibration.on_Calibrate(msg["data"]["arg"]):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with starting optical calibration")
            elif msg["data"]["command"] == "saveOpticalCalibrationConfiguration":
                if not self.data.opticalCalibration.saveOpticalCalibrationConfiguration(msg["data"]["arg"]):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with saving optical calibration configuration")
            elif msg["data"]["command"] == "stopOpticalCalibration":
                if not self.data.opticalCalibration.stopOpticalCalibration():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with stopping optical calibration.")
            elif msg["data"]["command"] == "testOpticalCalibration":
                if not self.data.opticalCalibration.testImage(msg["data"]["arg"]):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with test image.")
            elif msg["data"]["command"] == "findCenterOpticalCalibration":
                if not self.data.opticalCalibration.findCenter(msg["data"]["arg"]):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with find Center.")
            elif msg["data"]["command"] == "saveAndSendOpticalCalibration":
                if not self.data.opticalCalibration.saveAndSend():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with saving and sending calibration matrix.")
            elif msg["data"]["command"] == "reloadCalibration":
                errorX, errorY, curveX, curveY = self.data.opticalCalibration.reloadCalibration()
                if errorX is None or errorY is None or curveX is None or curveY is None:
                    self.data.ui_queue1.put("Alert", "Alert", "Error with (re)loading calibration.")
                else:
                    data = {"errorX": errorX, "errorY": errorY}
                    self.data.ui_queue1.put("Action", "updateOpticalCalibrationError", data)
            elif msg["data"]["command"] == "saveCalibrationToCSV":
                if not self.data.opticalCalibration.saveCalibrationToCSV():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with saving calibration to CSV.")
            elif msg["data"]["command"] == "clearCalibration":
                if not self.data.opticalCalibration.clearCalibration():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with clearing calibration.")
            elif msg["data"]["command"] == "curveFitOpticalCalibration":
                curveX, curveY = self.data.opticalCalibration.surfaceFit()
                #curveX, curveY = self.data.opticalCalibration.polySurfaceFit()
                if curveX is None or curveY is None:
                    self.data.ui_queue1.put("Alert", "Alert", "Error with curve fitting calibration data.")
                else:
                    data = {"curveX": curveX, "curveY": curveY}
                    self.data.ui_queue1.put("Action", "updateOpticalCalibrationCurve", data)
            elif msg["data"]["command"] == "adjustCenter":
                if not self.adjustCenter(msg["data"]["arg"]):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with adjusting center.")
            elif msg["data"]["command"] == "upgradeCustomFirmware":
                if not self.upgradeFirmware(0):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with upgrading custom firmware.")
                else:
                    self.data.ui_queue1.put("Alert", "Alert", "Custom firmware update complete.")
            elif msg["data"]["command"] == "upgradeStockFirmware":
                if not self.upgradeFirmware(1):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with upgrading stock firmware.")
                else:
                    self.data.ui_queue1.put("Alert", "Alert", "Stock firmware update complete.")
            elif msg["data"]["command"] == "upgradeHoleyFirmware":
                if not self.upgradeFirmware(2):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with upgrading holey firmware.")
                else:
                    self.data.ui_queue1.put("Alert", "Alert", "Custom firmware update complete.")
            elif msg["data"]["command"] == "adjustChain":
                if not self.adjustChain(msg["data"]["arg"]):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with adjusting chain.")
            elif msg["data"]["command"] == "toggleCamera":
                if not self.toggleCamera():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with toggling camera.")
            elif msg["data"]["command"] == "statusRequest":
                if msg["data"]["arg"] == "cameraStatus":
                    if not self.cameraStatus():
                        self.data.ui_queue1.put("Alert", "Alert", "Error with toggling camera.")
            elif msg["data"]["command"] == "queryCamera":
                if not self.queryCamera():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with toggling camera.")
            elif msg["data"]["command"] == "shutdown":
                if not self.shutdown():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with shutting down.")
            elif msg["data"]["command"] == "executeVelocityPIDTest":
                if not self.velocityPIDTest(msg["data"]["arg"]):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with executing velocity PID test.")
            elif msg["data"]["command"] == "executePositionPIDTest":
                if not self.positionPIDTest(msg["data"]["arg"]):
                    self.data.ui_queue1.put("Alert", "Alert", "Error with executing velocity PID test.")
            elif msg["data"]["command"] == "clearLogs":
                if not self.clearLogs():
                    self.data.ui_queue1.put("Alert", "Alert", "Error clearing log files.")
            elif msg["data"]["command"] == "boardProcessGCode":
                if not self.data.boardManager.processGCode():
                    self.data.ui_queue1.put("Alert", "Alert", "Error with processing gcode")
            else:
                self.data.ui_queue1.put("Alert", "Alert", "Function not currently implemented.. Sorry.")
        except Exception as e:
            print(str(e))
            

    def shutdown(self):
        try:
            self.data.ui_queue1.put("WebMCP","shutdown","")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def defineHome(self, posX, posY):
        print("posx = "+str(posX)+", posy="+str(posY)+", units="+ str(self.data.units))
        print("xval = "+str(self.data.xval) + ", yval=" + str(self.data.yval))
        try:
            #oldHomeX = self.data.xval
            #oldHomeY = self.data.yval
            oldHomeX = float(self.data.config.getValue("Advanced Settings", "homeX"))
            oldHomeY = float(self.data.config.getValue("Advanced Settings", "homeY"))

            if self.data.units == "MM":
                scaleFactor = 25.4
            else:
                scaleFactor = 1.0
            if posX!="" and posY!="":
                homeX=posX*scaleFactor
                homeY=posY*scaleFactor
            else:
                homeX=round(self.data.xval,4)
                homeY=round(self.data.yval,4)
            #self.data.gcodeShift = [
            #    homeX,
            #    homeY
            #]
            print("homeX= "+str(homeX) + ", homeY= " + str(homeY))
            print("oldHomeX= "+str(oldHomeX) + ", oldHomeY= " + str(oldHomeY))
            self.data.gcodeShift = [ homeX-oldHomeX, homeY-oldHomeY ]

            self.data.config.setValue("Advanced Settings", "homeX", str(homeX))
            self.data.config.setValue("Advanced Settings", "homeY", str(homeY))
            position = {"xval": homeX, "yval": homeY}
            self.data.ui_queue1.put("Action", "homePositionMessage", position)
            self.data.console_queue.put("gcodeShift="+str(self.data.gcodeShift[0])+", "+str(self.data.gcodeShift[1]))
            self.data.console_queue.put(self.data.gcode)
            text=""
            for line in self.data.gcode:
                text = text + line + "\n"
            self.data.gcodeFile.loadUpdateFile(text)
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
                if self.data.gcodeIndex >0:
                    self.processGCode()
                    self.sendGCodePositionUpdate(recalculate=True)
                    #self.data.console_queue.put("Run Paused")
                    #self.data.ui_queue1.put("Action", "setAsResume", "")
                    #self.data.pausedzval = self.data.zval
                else:
                    #self.data.gcode_queue.put(self.data.gcode[self.data.gcodeIndex])
                    self.data.uploadFlag = 1
                    #self.data.gcodeIndex += 1

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
            self.data.inPIDPositionTest = False
            self.data.inPIDVelocityTest = False
            self.data.uploadFlag = 0
            self.data.gcodeIndex = 0
            self.data.quick_queue.put("!")
            with self.data.gcode_queue.mutex:
                self.data.gcode_queue.queue.clear()
            # TODO: app.onUploadFlagChange(self.stopRun, 0)
            self.data.console_queue.put("Gcode stopped")
            self.data.ui_queue1.put("Action", "clearAlarm", "")
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
            if self.data.uploadFlag == 1:
                self.data.uploadFlag = 0
                self.data.console_queue.put("Run Paused")
                self.data.ui_queue1.put("Action", "setAsResume", "")
                self.data.pausedzval = self.data.zval
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def resumeRun(self):
        try:
            if self.data.manualZAxisAdjust:
                self.data.uploadFlag = self.data.previousUploadStatus
                self.data.gcode_queue.put("G0 Z" + str(self.data.pausedzval) + " ")
            else:
                self.sendGCodePositionUpdate(self.data.gcodeIndex, recalculate=True)
                self.data.uploadFlag = 1
            # send cycle resume command to unpause the machine
            #self.data.quick_queue.put("~")
            self.data.ui_queue1.put("Action", "setAsPause", "")
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
            self.data.gcodeFile.clearGcodeFile()
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

    def moveGcodeIndex(self, dist, index=False):
        try:
            maxIndex = len(self.data.gcode) - 1
            if index is True:
                targetIndex = dist
            else:
                targetIndex = self.data.gcodeIndex + dist

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

            try:
                retval = self.sendGCodePositionUpdate(recalculate=True)
                return retval
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
            else:
                return False
            self.data.config.setValue("Computed Settings","distToMove",distToMove)
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


    def touchZ(self):
        try:
            plungeDepth = self.data.config.getValue("Advanced Settings", "maxTouchProbePlungeDistance")
            revertToInches = False
            if self.data.units == "INCHES":
                revertToInches = True
                self.data.gcode_queue.put("G21")
            self.data.gcode_queue.put("G90 G38.2 Z-" + plungeDepth + " F1 M02")
            if revertToInches:
                self.data.gcode_queue.put("G20")
            self.data.measureRequest = self.defineZ0()
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def updateSetting(self, setting, value, fromGcode = False):
        try:
            self.data.console_queue.put("at update setting from gcode("+str(fromGcode)+"): "+setting+" with value: "+str(value))
            if setting == "toInches" or setting == "toMM":
                scaleFactor = 0
                if fromGcode:
                    value = float(self.data.config.getValue("Computed Settings", "distToMove"))
                    if self.data.units == "INCHES":
                        if setting == "toMM":
                            value = value * 25.4
                            scaleFactor = 25.4
                        else:
                            scaleFactor = 1.0
                    if self.data.units == "MM":
                        if setting == "toInches":
                            value = value / 25.4
                            scaleFactor = 1.0 / 25.4
                        else:
                            scaleFactor = 1.0

                if setting == "toInches":
                    self.data.units = "INCHES"
                    self.data.config.setValue("Computed Settings", "units", self.data.units)
                    if scaleFactor == 0:
                        scaleFactor = 1.0/25.4
                    self.data.tolerance = 0.020
                    self.data.config.setValue("Computed Settings", "tolerance", self.data.tolerance)
                    if not fromGcode:
                        self.data.gcode_queue.put("G20 ")
                else:
                    self.data.units = "MM"
                    self.data.config.setValue("Computed Settings", "units", self.data.units)
                    if scaleFactor == 0:
                        scaleFactor = 25.4
                    self.data.tolerance = 0.5
                    self.data.config.setValue("Computed Settings", "tolerance", self.data.tolerance)
                    if not fromGcode:
                        self.data.gcode_queue.put("G21 ")
                self.data.gcodeShift = [
                  self.data.gcodeShift[0] * scaleFactor,
                  self.data.gcodeShift[1] * scaleFactor,
                ]
                self.data.config.setValue("Computed Settings", "distToMove", value)
                oldHomeX = float(self.data.config.getValue("Advanced Settings", "homeX"))
                oldHomeY = float(self.data.config.getValue("Advanced Settings", "homeY"))
                self.data.config.setValue("Advanced Settings", "homeX", oldHomeX * scaleFactor)
                self.data.config.setValue("Advanced Settings", "homeY", oldHomeY * scaleFactor)
                #self.data.config.setValue("Advanced Settings", "homeX", self.data.gcodeShift[0])
                #self.data.config.setValue("Advanced Settings", "homeY", self.data.gcodeShift[1])
                self.data.ui_queue1.put("Action", "unitsUpdate", "")
                self.data.ui_queue1.put("Action", "distToMoveUpdate", "")
                #position = {"xval": self.data.gcodeShift[0], "yval": self.data.gcodeShift[1]}
                position = {"xval": oldHomeX * scaleFactor, "yval": oldHomeY * scaleFactor}
                self.data.ui_queue1.put("Action", "homePositionMessage", position)
                self.sendGCodePositionUpdate(recalculate=True)
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

    def rotateSprocket(self, sprocket, time):
        try:
            if  time > 0:
                self.data.gcode_queue.put("B11 "+sprocket+" S100 T"+str(time))
            else:
                self.data.gcode_queue.put("B11 "+sprocket+" S-100 T"+str(abs(time)))
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
            if self.data.config.getValue("Advanced Settings", "chainOverSprocket")=="Bottom":
                if self.data.config.getValue("Computed Settings", "chainOverSprocketComputed") != 2:
                   self.data.ui_queue1.put("Alert", "Alert", "mismatch between setting and computed setting. set for bottom feed, but computed !=2. report as issue on github please")
            if self.data.config.getValue("Advanced Settings", "chainOverSprocket")=="Top":
                if self.data.config.getValue("Computed Settings", "chainOverSprocketComputed") != 1:
                   self.data.ui_queue1.put("Alert", "Alert", "mismatch between setting and computed setting. set for top feed, but computed != 1. report as issue on github please")
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
            self.data.ui_queue1.put("Action", "updatePorts", "")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def acceptTriangularKinematicsResults(self):
        try:
            self.data.triangularCalibration.acceptTriangularKinematicsResults()
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

            
    def calibrate(self, result):
        try:
            motorYoffsetEst, rotationRadiusEst, chainSagCorrectionEst, cut34YoffsetEst = self.data.triangularCalibration.calculate(
                result
            )
            if not motorYoffsetEst:
                return False
            return (
                motorYoffsetEst,
                rotationRadiusEst,
                chainSagCorrectionEst,
                cut34YoffsetEst,
            )
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def holeyCalibrate(self, result):
        try:
            motorYoffsetEst, distanceBetweenMotors, leftChainTolerance, rightChainTolerance, calibrationError = self.data.holeyCalibration.Calibrate(
                result
            )
            if not motorYoffsetEst:
                return False
            return (
                motorYoffsetEst,
                distanceBetweenMotors,
                leftChainTolerance,
                rightChainTolerance,
                calibrationError,
            )
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False


    def sendGCode(self, gcode):
        try:
            self.data.sentCustomGCode = gcode
            gcodeLines = gcode.splitlines()
            for line in gcodeLines:
                self.data.gcode_queue.put(line)
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False
    
    def macro(self, number):
        '''
        try:
            if number == 1:
                print("here")
                btn_pin = Device.pin_factory.pin(2)
                btn_pin.drive_low()
                return True
            if number == 2:
                print("here2")
                self.data.gpioActions.setGPIOAction(3, "Stop")
                return True

        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

        '''
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
                self.data.ui_queue1.put("Action", "homePositionMessage", position)
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
                    self.data.ui_queue1.put("Action", "updateOpticalCalibrationCurve", data)
                except Exception as e:
                    self.data.console_queue.put(str(e))
            elif setting == "calibrationError":
                try:
                    xyErrorArray = self.data.config.getValue("Optical Calibration Settings","xyErrorArray")
                    errorX, errorY = self.data.config.parseErrorArray(xyErrorArray, True)
                    data = {"errorX": errorX, "errorY": errorY}
                    self.data.ui_queue1.put("Action", "updateOpticalCalibrationError", data)
                except Exception as e:
                    self.data.console_queue.put(str(e))
            else:
                if setting == "units":
                    self.data.xval_prev = -99999.0 #force a new position send
                retval = self.data.config.getValue(section, setting)
                return setting, retval
        except Exception as e:
            pass
        return None, None

    def upgradeFirmware(self, version):
        try:
            if version == 0:
                self.data.ui_queue1.put("SpinnerMessage", "", "Custom Firmware Update in Progress, Please Wait.")
                path = "/firmware/madgrizzle/*.hex"
            if version == 1:
                self.data.ui_queue1.put("SpinnerMessage", "", "Stock Firmware Update in Progress, Please Wait.")
                path = "/firmware/maslowcnc/*.hex"
            if version == 2:
                self.data.ui_queue1.put("SpinnerMessage", "", "Holey Firmware Update in Progress, Please Wait.")
                path = "/firmware/holey/*.hex"
            time.sleep(.5)
            for filename in glob.glob(path):
                port = self.data.comport
                cmd = "avr/avrdude -Cavr/avrdude.conf -v -patmega2560 -cwiring -P"+port+" -b115200 -D -Uflash:w:"+filename+":i"
                os.system(cmd)
                self.data.ui_queue1.put("Action", "closeModals", "Notification")
                return True
        except Exception as e:
            self.data.console_log.put(str(e))
            return False

    def createDirectory(self, _directory):
        try:

            home = self.data.config.getHome()
            directory = home + "/.WebControl/gcode/" + _directory
            if not os.path.isdir(directory):
                os.mkdir(directory)
            data = {"directory": _directory}
            self.data.ui_queue1.put("Action", "updateDirectories", data)
        except Exception as e:
            print(e)
        return True

    def sendGCodePositionUpdate(self, gCodeLineIndex=None, recalculate=False):
        if self.data.gcode:
            if gCodeLineIndex is None:
                gCodeLineIndex = self.data.gcodeIndex
            gCodeLine = self.data.gcode[gCodeLineIndex]
            #print("Gcode index"+str(gCodeLineIndex)+" : "+ gCodeLine )
            if not recalculate:
                #print("not recalculating.. uploadFlag ="+str(self.data.uploadFlag))

                x = re.search("X(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
                if x:
                    xTarget = float(x.groups()[0])
                    self.data.previousPosX = xTarget
                else:
                    #xTarget = None
                    xTarget = self.data.previousPosX

                y = re.search("Y(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)

                if y:
                    yTarget = float(y.groups()[0])
                    self.data.previousPosY = yTarget
                else:
                    #yTarget = None
                    yTarget = self.data.previousPosY

                z = re.search("Z(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)

                if z:
                    zTarget = float(z.groups()[0])
                    self.data.previousPosZ = zTarget
                else:
                    #zTarget = None
                    zTarget = self.data.previousPosZ
            else:
                #if xTarget is None or yTarget is None:
                xTarget, yTarget, zTarget = self.findPositionAt(self.data.gcodeIndex)

            scaleFactor = 1.0
            if self.data.gcodeFileUnits == "MM" and self.data.units=="INCHES":
                scaleFactor = 1/25.4
            if self.data.gcodeFileUnits == "INCHES" and self.data.units=="MM":
                scaleFactor = 25.4

            #position = {"xval": xTarget*scaleFactor, "yval": yTarget*scaleFactor, "zval": self.data.zval*scaleFactor, "gcodeLine":gCodeLine, "gcodeLineIndex":gCodeLineIndex}
            position = {"xval": xTarget * scaleFactor, "yval": yTarget * scaleFactor,"zval": zTarget * scaleFactor, "gcodeLine": gCodeLine, "gcodeLineIndex": gCodeLineIndex}

            self.data.ui_queue1.put("Action", "gcodePositionMessage", position)
            return True

    def moveTo(self, posX, posY):
        bedHeight = float(self.data.config.getValue("Maslow Settings","bedHeight"))/25.4
        bedWidth = float(self.data.config.getValue("Maslow Settings", "bedWidth"))/25.4
        try:
            if posX<=bedWidth/2 and posX>=bedWidth/-2 and posY<=bedHeight/2 and posY>=bedHeight/-2:
                if self.data.units == "INCHES":
                    posX=round(posX,4)
                    posY=round(posY,4)
                else:
                    posX=round(posX*25.4,4)
                    posY=round(posY*25.4,4)
                self.data.gcode_queue.put(
                    "G90 G00 X"
                    + str(posX)
                    + " Y"
                    + str(posY)
                    + " "
                )
                return True
            return False
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def processGCode(self):
        '''
        This function processes the gcode up to the current gcode index to develop a set of
        gcodes to send to the controller upon the user starting a run.  This function is intended
        to ensure that the sled is in the correct location and the controller is in the correct
        state prior to starting the current gcode move.  Currently processed are relative/absolute
        positioning (G90/G91), imperial/metric units (G20/G21) and x, y and z positions
        '''
        zAxisSafeHeight = float(self.data.config.getValue("Maslow Settings","zAxisSafeHeight"))
        positioning = "G90 "
        units = "G20 "

        xpos = 0
        ypos = 0
        zpos = 0
        tool = None
        spindle = None
        laser = None
        dwell = None
        for x in range(self.data.gcodeIndex):
            if self.data.gcode[x][0] != "(":
                lines = self.data.gcode[x].split(" ")
                if lines:
                    finalLines = []
                    for line in lines:
                        if len(line)>0:
                            if line[0] == "M" or line[0] == "G" or line[0] == "T":
                                finalLines.append(line)
                            else:
                                finalLines[-1] = finalLines[-1] + " " + line
                    for line in finalLines:
                        if line[0]=='G':
                            if line.find("G90")!=-1:
                                positioning = "G90 "
                            if line.find("G91")!=-1:
                                positioning = "G91 "
                            if line.find("G20")!=-1:
                                units = "G20 "
                            if line.find("G21")!=-1:
                                units = "G21 "
                            if line.find("X")!=-1:
                                _xpos = re.search("X(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", line)
                                if positioning == "G91 ":
                                    xpos = xpos+float(_xpos.groups()[0])
                                else:
                                    xpos = float(_xpos.groups()[0])
                            if line.find("Y")!=-1:
                                _ypos = re.search("Y(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", line)
                                if positioning == "G91 ":
                                    ypos = ypos+float(_ypos.groups()[0])
                                else:
                                    ypos = float(_ypos.groups()[0])
                            if line.find("Z")!=-1:
                                _zpos = re.search("Z(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", line)
                                if positioning == "G91 ":
                                    zpos = zpos+float(_zpos.groups()[0])
                                else:
                                    zpos = float(_zpos.groups()[0])
                            if line.find("G4")!=-1:
                                dwell = line[3:]
                            if line.find("G04") != -1:
                                dwell = line[4:]


                        if line[0]=='M':
                            if line.find("M3") != -1 or line.find("M03") != -1:
                                spindle = "M3 "
                            if line.find("M4") != -1 or line.find("M05") != -1:
                                spindle = "M4 "
                            if line.find("M5") != -1 or line.find("M05") != -1:
                                spindle = "M5 "
                            if line.find("M106") != -1:
                                laser = "M106 "
                            if line.find("M107") != -1:
                                laser = "M107 "
                            if line.find("M16") != -1:
                                laser = "M107 "
                        if line[0]=='T':
                            tool = line[1:] #slice off the T

        self.data.gcode_queue.put(positioning)
        if units == "G20 ":
            self.data.actions.updateSetting("toInches", 0, True)  # value = doesn't matter
            zAxisSafeHeight = zAxisSafeHeight/25.4
        else:
            self.data.actions.updateSetting("toMM", 0, True)  # value = doesn't matter
        self.data.gcode_queue.put("G0 Z"+str(round(zAxisSafeHeight,4))+" ")
        self.data.gcode_queue.put("G0 X"+str(round(xpos,4))+" Y"+str(round(ypos,4))+" ")
        if tool is not None:
            self.data.gcode_queue.put("T"+tool+" M6 ")
        if spindle is not None:
            self.data.gcode_queue.put(spindle)
        if laser is not None:
            self.data.gcode_queue.put(laser)
        if dwell is not None:
            self.data.gcode_queue.put("G4 "+dwell)
        self.data.gcode_queue.put("G0 Z" + str(round(zpos, 4)) + " ")


    def findPositionAt(self, index):
        #This function is necessary to update the gcode position indicators on z-index moves
        xpos = 0
        ypos = 0
        zpos = 0
        for x in range(index):
            if self.data.gcode[x][0] != "(":
                listOfLines = filter(None, re.split("(G)", self.data.gcode[x]))  # self.data.gcode[x].split("G")
                # it is necessary to split the lines along G and M commands so that commands concatenated on one line
                # are processed correctly
                for line in listOfLines:
                    line = 'G'+line
                    #print(line)
                    if line[0] == 'G':
                        if line.find("G90") != -1:
                            positioning = "G90 "
                        if line.find("G91") != -1:
                            positioning = "G91 "
                        if line.find("X") != -1:
                            _xpos = re.search("X(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", line)
                            if positioning == "G91 ":
                                xpos = xpos + float(_xpos.groups()[0])
                            else:
                                xpos = float(_xpos.groups()[0])
                        if line.find("Y") != -1:
                            _ypos = re.search("Y(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", line)
                            if positioning == "G91 ":
                                ypos = ypos + float(_ypos.groups()[0])
                            else:
                                ypos = float(_ypos.groups()[0])
                        if line.find("Z") != -1:
                            _zpos = re.search("Z(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", line)
                            if positioning == "G91 ":
                                zpos = zpos + float(_zpos.groups()[0])
                            else:
                                zpos = float(_zpos.groups()[0])
        print("xpos="+str(xpos)+", ypos="+str(ypos)+", zpoz="+str(zpos)+" for index="+str(index))
        return xpos, ypos, zpos

    def adjustChain(self, chain):
        try:
            for x in range(6):
                self.data.ui_queue1.put("Action", "updateTimer", chain+":"+str(5-x))
                self.data.console_queue.put("Action:updateTimer_" + chain + ":" + str(5 - x))
                time.sleep(1)
            if chain == "left":
                self.data.gcode_queue.put("B02 L1 R0 ")
            if chain == "right":
                self.data.gcode_queue.put("B02 L0 R1 ")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def toggleCamera(self):
        try:
            status = self.data.camera.status()
            if status == "stopped":
                self.data.camera.start()
            if status == "suspended":
                self.data.camera.read()
            if status == "running":
                self.data.camera.stop()
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def cameraStatus(self):
        try:
            status = self.data.camera.status()
            if status == "stopped":
                self.data.ui_queue1.put("Action", "updateCamera", "off")
            if status == "suspended":
                self.data.ui_queue1.put("Action", "updateCamera", "off")
            if status == "running":
                self.data.ui_queue1.put("Action", "updateCamera", "on")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def queryCamera(self):
        try:
            self.data.camera.getSettings()
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def velocityPIDTest(self, parameters):
        try:
            print(parameters)
            print(parameters["KpV"])
            self.data.config.setValue("Advanced Settings", "KpV", parameters["KpV"])
            self.data.config.setValue("Advanced Settings", "KiV", parameters["KiV"])
            self.data.config.setValue("Advanced Settings", "KdV", parameters["KdV"])
            gcodeString = "B13 "+parameters["vMotor"]+"1 S"+parameters["vStart"]+" F"+parameters["vStop"]+" I"+parameters["vSteps"]+" V"+parameters["vVersion"]
            print(gcodeString)
            self.data.PIDVelocityTestVersion = parameters["vVersion"]
            self.data.gcode_queue.put(gcodeString)
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def positionPIDTest(self, parameters):
        try:
            print(parameters)
            print(parameters["KpP"])
            self.data.config.setValue("Advanced Settings", "KpPos", parameters["KpP"])
            self.data.config.setValue("Advanced Settings", "KiPos", parameters["KiP"])
            self.data.config.setValue("Advanced Settings", "KdPos", parameters["KdP"])

            gcodeString = "B14 "+parameters["pMotor"]+"1 S"+parameters["pStart"]+" F"+parameters["pStop"]+" I"+parameters["pSteps"]+" T"+parameters["pTime"]+" V"+parameters["pVersion"]
            print(gcodeString)
            self.data.PIDPositionTestVersion = parameters["pVersion"]
            self.data.gcode_queue.put(gcodeString)
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def velocityPIDTestRun(self, command, msg):
        try:
            if command == 'stop':
                self.data.inPIDVelocityTest = False
                print("PID velocity test stopped")
                print(self.data.PIDVelocityTestData)
                data = json.dumps({"result": "velocity", "version": self.data.PIDVelocityTestVersion, "data": self.data.PIDVelocityTestData})
                self.data.ui_queue1.put("Action", "updatePIDData", data)
                self.stopRun()
            if command == 'running':
                if msg.find("Kp=") == -1:
                    if self.data.PIDVelocityTestVersion == "2":
                        if msg.find("setpoint") == -1:
                            self.data.PIDVelocityTestData.append(msg)
                    else:
                        self.data.PIDVelocityTestData.append(float(msg))
            if command == 'start':
                self.data.inPIDVelocityTest = True
                self.data.PIDVelocityTestData = []
                print("PID velocity test started")
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def positionPIDTestRun(self, command, msg):
        try:
            if command == 'stop':
                self.data.inPIDPositionTest = False
                print("PID position test stopped")
                print(self.data.PIDPositionTestData)
                data = json.dumps({"result": "position", "version": self.data.PIDPositionTestVersion, "data": self.data.PIDPositionTestData})
                self.data.ui_queue1.put("Action", "updatePIDData", data)
                self.stopRun()
            if command == 'running':
                if msg.find("Kp=") == -1:
                    if self.data.PIDPositionTestVersion == "2":
                        if msg.find("setpoint") == -1:
                            self.data.PIDPositionTestData.append(msg)
                    else:
                        self.data.PIDPositionTestData.append(float(msg))
            if command == 'start':
                self.data.inPIDPositionTest = True
                self.data.PIDPositionTestData = []
                print("PID position test started")
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def updateGCode(self, gcode):
        try:
            #print(gcode)
            homeX = float(self.data.config.getValue("Advanced Settings", "homeX"))
            homeY = float(self.data.config.getValue("Advanced Settings", "homeY"))

            if self.data.units == "MM":
                scaleFactor = 25.4
            else:
                scaleFactor = 1.0
            self.data.gcodeShift = [
                homeX,
                homeY
            ]

            self.data.gcodeFile.loadUpdateFile(gcode)
            self.data.ui_queue1.put("Action", "gcodeUpdate", "")
            return True
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def downloadDiagnostics(self):
        try:
            timestr = time.strftime("%Y%m%d-%H%M%S")
            filename = self.data.config.home+"/.WebControl"+"wc_diagnostics_"+timestr+".zip"
            zipObj = ZipFile(filename, 'w')
            path1 = self.data.config.home+"/.WebControl/webcontrol.json"
            zipObj.write(path1, os.path.basename(path1))
            path1 = self.data.config.home + "/.WebControl/alog.txt"
            zipObj.write(path1, os.path.basename(path1))
            path1 = self.data.config.home + "/.WebControl/log.txt"
            zipObj.write(path1, os.path.basename(path1))
            zipObj.close()
            return filename
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def clearLogs(self):
        try:
            retval = self.data.logger.deleteLogFiles()
            return retval
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False


