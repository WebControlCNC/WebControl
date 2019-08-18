from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
import Actions.HoleySimulationKinematics as kinematics
import math
from scipy.optimize import least_squares
import numpy

import itertools
import time
import re
import sys
import math
import base64
import time
import os
import datetime


class HoleyCalibration(MakesmithInitFuncs):

    def __init__(self):
        # can't do much because data hasn't been initialized yet
        pass

    SP_D = 3629.025
    SP_motorOffsetY = 503.4
    SP_rotationDiskRadius = 138.1
    SP_leftChainTolerance = 0
    SP_rightChainTolerance = 0
    SP_sledWeight = 109.47  # N
    SP_chainOverSprocket = False

    Opt_D = 3601.2
    Opt_motorOffsetY = 468.4
    Opt_rotationDiskRadius = 139.1
    Opt_leftChainTolerance = 0
    Opt_rightChainTolerance = 0
    Opt_sledWeight = 97.9  # N

    # Chain lengths @ each hole
    ChainLengths = []
    MeasurementMap = [
        (1, 2),
        (2, 3),
        (4, 5),
        (5, 6),
        (1, 4),
        (2, 5),
        (3, 6),
        (2, 4),
        (1, 5),
        (3, 5),
        (2, 6)]
    CutOrder = [1, 0, 3, 4, 5, 2]  # Counter Clockwise, starting at top
    IdealLengthArray = 0
    MeasuredLengthArray = 0
    DesiredLengthDeltaArray = 0

    OptimizationOutput = 0

    kin = kinematics.Kinematics()
    kin.isQuadKinematics = False

    # Define function with input of (ideal lengths and) machine parameters (delta) and output of length error
    def LengthDeltaFromIdeal(self,
                             DeltaArray):  # Del_D,Del_motorOffsetY,Del_rotationDiskRadius,Del_chainSagCorrection):
        self.kin.D = self.SP_D + DeltaArray[0]
        self.kin.motorOffsetY = self.SP_motorOffsetY + DeltaArray[1]
        self.kin.leftChainTolerance = self.SP_leftChainTolerance + DeltaArray[2]
        self.kin.rightChainTolerance = self.SP_rightChainTolerance + DeltaArray[3]
        self.kin.recomputeGeometry()
        CalculatedPositions = []
        for LeftChainLength, RightChainLength in self.ChainLengths:
            CalculatedPositions.append(self.kin.forward(LeftChainLength, RightChainLength))

        return self.MeasuredLengthArray - self.CalculateMeasurements(CalculatedPositions)

    def InitialMeasurementError(self, Meas, idx):  # For validating in GUI
        Ideal = self.IdealLengthArray[idx]
        return Ideal - Meas

    def ValidateMeasurement(self, Meas, idx):
        if idx < 11:
            Ideal = self.IdealLengthArray[idx]
            return 0.1 > abs((Ideal - Meas) / Ideal)
        else:
            return Meas > 0.0

    def CutTestPattern(self):
        oldUnits = self.data.units
        #self.data.units = "MM"
        if oldUnits != "MM":
            self.data.actions.updateSetting("toMM", 0, True)
        self.data.console_queue.put('Cutting Holey Calibration Test Pattern')
        self.InitializeIdealXyCoordinates()
        self.data.gcode_queue.put("G21")
        self.data.gcode_queue.put("G90")  # Switch to absolute mode
        self.data.gcode_queue.put("G40")
        self.data.gcode_queue.put("G17")
        self.data.gcode_queue.put("M3")
        for idx in self.CutOrder:
            x, y = self.IdealCoordinates[idx]
            self.data.console_queue.put('cutting index: ' + str(idx + 1))
            self.data.gcode_queue.put("G0 X" + str(x) + " Y" + str(y))
            self.data.gcode_queue.put("G0 Z-5")
            self.data.gcode_queue.put("G0 Z5")

        self.data.gcode_queue.put("G0 X0 Y0")
        self.data.gcode_queue.put("M5")
        if oldUnits != "MM":
            self.data.actions.updateSetting("toInches", 0, True)
        return True

    def CalculateMeasurements(self, HolePositions):
        #        aH1x,aH1y,aH2x,aH2y,aH3x,aH3y,aH4x,aH4y,aH5x,aH5y,aH6x,aH6y
        Measurements = []
        for StartHoleIdx, EndHoleIdx in self.MeasurementMap:
            x1, y1 = HolePositions[StartHoleIdx - 1]
            x2, y2 = HolePositions[EndHoleIdx - 1]
            Measurements.append(self.GeometricLength(x1, y1, x2, y2))
        ToTopHole = 1
        Measurements.append(
            self.GeometricLength(HolePositions[ToTopHole][0], HolePositions[ToTopHole][1], HolePositions[ToTopHole][0],
                            self.kin.machineHeight / 2))

        return numpy.array(Measurements)

    def InitializeIdealXyCoordinates(self):
        self.SP_D = float(self.data.config.getValue("Maslow Settings", "motorSpacingX"))
        self.SP_motorOffsetY = float(self.data.config.getValue("Maslow Settings", "motorOffsetY"))
        self.SP_rotationDiskRadius = float(self.data.config.getValue("Advanced Settings", "rotationRadius"))
        self.SP_leftChainTolerance = float(self.data.config.getValue("Advanced Settings", "leftChainTolerance"))
        self.SP_rightChainTolerance = float(self.data.config.getValue("Advanced Settings", "rightChainTolerance"))
        self.SP_sledWeight = float(self.data.config.getValue("Maslow Settings", "sledWeight"))
        if self.data.config.getValue("Advanced Settings", "chainOverSprocket") == "Top":
            self.SP_chainOverSprocket = 1
        else:
            self.SP_chainOverSprocket = 2
        self.kin.machineHeight = float(self.data.config.getValue("Maslow Settings","bedHeight"))
        self.kin.machineWidth = float(self.data.config.getValue("Maslow Settings","bedWidth"))
        workspaceHeight = self.kin.machineHeight
        workspaceWidth = self.kin.machineWidth
        aH1x = -(workspaceWidth / 2.0 - 254.0)
        aH1y = (workspaceHeight / 2.0 - 254.0)
        aH2x = 0
        IdealCoordinates = [
            (aH1x, aH1y),
            (aH2x, aH1y),
            (-aH1x, aH1y),
            (aH1x, -aH1y),
            (aH2x, -aH1y),
            (-aH1x, -aH1y)]
        self.IdealCoordinates = IdealCoordinates
        self.kin.D = self.SP_D
        self.kin.motorOffsetY = self.SP_motorOffsetY
        self.kin.rotationDiskRadius = self.SP_rotationDiskRadius
        self.kin.sledWeight = self.SP_sledWeight
        self.kin.leftChainTolerance = self.SP_leftChainTolerance
        self.kin.rightChainTolerance = self.SP_rightChainTolerance
        self.kin.chainOverSprocket = self.SP_chainOverSprocket
        self.kin.recomputeGeometry()
        self.IdealLengthArray = self.CalculateMeasurements(IdealCoordinates)

        self.ChainLengths = []
        for x, y in IdealCoordinates:
            self.ChainLengths.append(self.kin.inverse(x, y))
        return self.IdealLengthArray

    def SetMeasurements(self, Measurements):
        self.MeasuredLengthArray = numpy.array(Measurements)

    def Calibrate(self, result):
        self.InitializeIdealXyCoordinates()
        measurements = self.processMeasurements(result)
        self.SetMeasurements(measurements)
        self.OptimizationOutput = least_squares(self.LengthDeltaFromIdeal, numpy.array([0, 0, 0, 0]), jac='2-point',
                                                diff_step=.1, ftol=1e-11)
        Deltas = self.OptimizationOutput.x
        self.Opt_D = round(Deltas[0] + self.SP_D,5)
        self.Opt_motorOffsetY = round(Deltas[1] + self.SP_motorOffsetY,5)
        self.Opt_leftChainTolerance = round(Deltas[2] + self.SP_leftChainTolerance,5)
        self.Opt_rightChainTolerance = round(Deltas[3] + self.SP_rightChainTolerance,5)
        self.kin.D = self.Opt_D
        self.kin.motorOffsetY = self.Opt_motorOffsetY
        self.kin.leftChainTolerance = self.Opt_leftChainTolerance
        self.kin.rightChainTolerance = self.Opt_rightChainTolerance
        self.kin.recomputeGeometry()
        self.ReportCalibration()
        return self.Opt_motorOffsetY, self.Opt_D, self.Opt_leftChainTolerance, self.Opt_rightChainTolerance, 1


    def ReportCalibration(self):
        self.data.console_queue.put('Optimized Errors')
        for idx, pts, ms, cal, er in zip(
                range(self.MeasuredLengthArray.size),
                self.MeasurementMap,
                self.MeasuredLengthArray,
                self.CalibratedLengths(),
                self.CalibratedLengthError()):
            self.data.console_queue.put(('\tIndex                : {}' +
                   '\n\t\tPoints Span        : {} to {}' +
                   '\n\t\tMeasured Distance  : {}' +
                   '\n\t\tCalibrated Distance: {}' +
                   '\n\t\tDistance Error     : {}').format(
                idx, pts[0], pts[1], ms, cal, er))
        self.data.console_queue.put("")
        self.data.console_queue.put("Distance Between Motors:")
        self.data.console_queue.put(self.Opt_D)
        self.data.console_queue.put("")
        self.data.console_queue.put("Motor Y Offset:")
        self.data.console_queue.put(self.Opt_motorOffsetY)
        self.data.console_queue.put("")
        self.data.console_queue.put("Left Chain Tolerance:")
        self.data.console_queue.put(self.Opt_leftChainTolerance)
        self.data.console_queue.put("")
        self.data.console_queue.put("Right Chain Tolerance:")
        self.data.console_queue.put(self.Opt_rightChainTolerance)

    def CalibratedLengths(self):
        return self.MeasuredLengthArray - self.OptimizationOutput.fun

    def CalibratedLengthError(self):
        return self.OptimizationOutput.fun

    def HolePositionsFromChainLengths(self):
        HolePositions = []
        for LeftChainLength, RightChainLength in self.ChainLengths:
            HolePositions.append(self.kin.forward(LeftChainLength, RightChainLength))
        return HolePositions

    def SimulateMeasurement(self, D, motorOffsetY, leftChainTolerance, rightChainTolerance):
        # Simulate Measurement.  Modify machine parameters, use kin.forward to determine x,y coordinates. Return machine parameters to original
        self.kin.D = D
        self.kin.motorOffsetY = motorOffsetY
        self.kin.leftChainTolerance = leftChainTolerance
        self.kin.rightChainTolerance = rightChainTolerance
        self.kin.recomputeGeometry()

        HolePositions = self.HolePositionsFromChainLengths()

        self.kin.D = self.SP_D
        self.kin.motorOffsetY = self.SP_motorOffsetY
        self.kin.rotationDiskRadius = self.SP_rotationDiskRadius
        self.kin.sledWeight = self.SP_sledWeight
        self.kin.leftChainTolerance = self.SP_leftChainTolerance
        self.kin.rightChainTolerance = self.SP_rightChainTolerance
        self.kin.recomputeGeometry()

        Measurements = self.CalculateMeasurements(HolePositions)

        self.SetMeasurements(Measurements)

    def processMeasurements(self, result):
        measurements = []
        try:
            M1 = float(result["M1"])
            self.data.console_queue.put(M1)
            measurements.append(M1)
        except:
            self.data.message_queue.put("Message: Please enter a number for the distance M1." )
            return False
        try:
            M2 = float(result["M2"])
            self.data.console_queue.put(M2)
            measurements.append(M2)
        except:
            self.data.message_queue.put("Message: Please enter a number for the distance M2." )
            return False
        try:
            M3 = float(result["M3"])
            self.data.console_queue.put(M3)
            measurements.append(M3)
        except:
            self.data.message_queue.put("Message: Please enter a number for the distance M3." )
            return False
        try:
            M4 = float(result["M4"])
            self.data.console_queue.put(M4)
            measurements.append(M4)
        except:
            self.data.message_queue.put("Message: Please enter a number for the distance M4." )
            return False
        try:
            M5 = float(result["M5"])
            self.data.console_queue.put(M5)
            measurements.append(M5)
        except:
            self.data.message_queue.put("Message: Please enter a number for the distance M5." )
            return False
        try:
            M6 = float(result["M6"])
            self.data.console_queue.put(M6)
            measurements.append(M6)
        except:
            self.data.message_queue.put("Message: Please enter a number for the distance M6." )
            return False
        try:
            M7 = float(result["M7"])
            self.data.console_queue.put(M7)
            measurements.append(M7)
        except:
            self.data.message_queue.put("Message: Please enter a number for the distance M7." )
            return False
        try:
            M8 = float(result["M8"])
            self.data.console_queue.put(M8)
            measurements.append(M8)
        except:
            self.data.message_queue.put("Message: Please enter a number for the distance M8.")
            return False
        try:
            M9 = float(result["M9"])
            self.data.console_queue.put(M9)
            measurements.append(M9)
        except:
            self.data.message_queue.put("Message: Please enter a number for the distance M9." )
            return False
        try:
            M10 = float(result["M10"])
            self.data.console_queue.put(M10)
            measurements.append(M10)
        except:
            self.data.message_queue.put("Message: Please enter a number for the distance M10." )
            return False
        try:
            M11 = float(result["M11"])
            self.data.console_queue.put(M11)
            measurements.append(M11)
        except:
            self.data.message_queue.put("Message: Please enter a number for the distance M11." )
            return False
        try:
            M12 = float(result["M12"])
            self.data.console_queue.put(M12)
            measurements.append(M12)
        except:
            self.data.message_queue.put("Message: Please enter a number for the distance M12." )
            return False
        return measurements

    def GeometricLength(self,x1,y1,x2,y2):
        return math.sqrt(math.pow(x1-x2,2) + math.pow(y1-y2,2))

    def acceptCalibrationResults(self):
        self.data.config.setValue('Maslow Settings', 'motorOffsetY', str(self.Opt_motorOffsetY))
        self.data.config.setValue('Maslow Settings', 'motorSpacingX', str(self.Opt_D))
        self.data.config.setValue('Advanced Settings', 'leftChainTolerance', str(self.Opt_leftChainTolerance))
        self.data.config.setValue('Advanced Settings', 'rightChainTolerance', str(self.Opt_rightChainTolerance))

        self.data.gcode_queue.put("G21 ")
        self.data.gcode_queue.put("G90 ")
        self.data.gcode_queue.put("G40 ")
        self.data.gcode_queue.put("G0 X0 Y0 ")
        return True

