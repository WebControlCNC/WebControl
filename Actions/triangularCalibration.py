from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
import math


class TriangularCalibration(MakesmithInitFuncs):

    motorYoffsetEst = 0
    chainSagCorrectionEst = 0
    rotationRadiusEst = 0
    
    def cutTriangularCalibrationPattern(self):
        '''
        Sends command to controller to cut the calibration pattern.
        :return:
        '''

        workspaceHeight = float(
            self.data.config.getValue("Maslow Settings", "bedHeight")
        )
        workspaceWidth = float(self.data.config.getValue("Maslow Settings", "bedWidth"))

        # keep track of the units the machine is currently using to revert back if needed.
        oldUnits = self.data.units

        self.data.gcode_queue.put("G21 ")
        self.data.gcode_queue.put("G90 ")  # Switch to absolute mode
        self.data.gcode_queue.put("G40 ")

        self.data.gcode_queue.put("G0 Z5 ")
        self.data.gcode_queue.put("G0 X0 Y0 ")
        self.data.gcode_queue.put("G0 Z0 ")
        self.data.gcode_queue.put("G17 ")

        self.data.gcode_queue.put("G91 ")  # Switch to relative mode
        self.data.gcode_queue.put("G0 Z5 ")
        self.data.gcode_queue.put("M3 ")  # Turn on the spindle

        self.data.gcode_queue.put(
            "G0 X-"
            + str((workspaceWidth / 2) - 254)
            + " Y+"
            + str((workspaceHeight / 2) - 241.3)
            + " "
        )  # Move to first cut point
        self.data.gcode_queue.put("G1 Z-10 F500 ")
        self.data.gcode_queue.put("G1 Y-25.4 ")  # Cut 25.4mm vertical mark
        self.data.gcode_queue.put("G1 Z10")
        self.data.gcode_queue.put(
            "G0 Y-" + str(workspaceHeight - 533.4) + " "
        )  # Move down on the workspace to third cut point
        self.data.gcode_queue.put("G1 Z-10 ")
        self.data.gcode_queue.put("G1 Y-25.4 ")  # Cut 25.4mm vertical mark
        self.data.gcode_queue.put("G1 Z10 ")
        self.data.gcode_queue.put(
            "G0 X"
            + str(workspaceWidth - 533.4)
            + " Y"
            + str(workspaceHeight - 482.6)
            + " "
        )  # Move up and right on the workspace to fifth and second cut points
        self.data.gcode_queue.put("G1 Z-10 ")
        self.data.gcode_queue.put("G1 X25.4 ")  # Cut 25.4mm horizontal mark
        self.data.gcode_queue.put("G1 Y-25.4 ")  # Cut 25.4mm vertical mark
        self.data.gcode_queue.put("G1 Z10 ")
        self.data.gcode_queue.put(
            "G0 Y-" + str(workspaceHeight - 533.4) + " "
        )  # Move down on the workspace to fourth cut point
        self.data.gcode_queue.put("G1 Z-10 ")
        self.data.gcode_queue.put("G1 Y-25.4 ")  # Cut 25.4mm vertical mark
        self.data.gcode_queue.put("G1 Z10 ")

        self.data.gcode_queue.put("M5 ")  # Turn off the spindle

        self.data.gcode_queue.put("G90 ")  # Switch back to absolute mode
        self.data.gcode_queue.put("G0 X0 Y0 ")  # Move to home location

        if oldUnits == "INCHES":
            # switch back to inches
            self.data.gcode_queue.put("G20 ")  # Switch back to inches

        return True


    def calculate(self, result):
        """
        Takes the measured distance and uses it to iteratively calculate the rotationDiskRadius and yMotorOffset
        """

        # Validate user inputs

        workspaceHeight = float(
            self.data.config.getValue("Maslow Settings", "bedHeight")
        )
        workspaceWidth = float(self.data.config.getValue("Maslow Settings", "bedWidth"))

        try:
            distBetweenCuts12 = float(result["cut12"])
            self.data.console_queue.put(distBetweenCuts12)
        except:
            self.data.message_queue.put(
                "Message: Please enter a number for the distance between cut 1 and cut 2."
            )
            return False

        try:
            distBetweenCuts34 = float(result["cut34"])
            self.data.console_queue.put(distBetweenCuts34)
        except:
            self.data.message_queue.put(
                "Message: Please enter a number for the distance between cut 3 and cut 4."
            )
            return False

        try:
            distWorkareaTopToCut5 = float(result["cut5"])
            self.data.console_queue.put(distWorkareaTopToCut5)
        except:
            self.data.message_queue.put(
                "Message: Please enter a number for the distance between the top of the work area and cut 5."
            )
            return False

        try:
            bitDiameter = float(result["bitDiameter"])
            self.data.console_queue.put(bitDiameter)
        except:
            self.data.message_queue.put(
                "Message: Please enter a number for the bit diameter."
            )
            return False

        if True:
            if (distBetweenCuts12 > workspaceWidth) or (
                distBetweenCuts12 < (workspaceWidth / 2)
            ):
                self.data.message_queue.put(
                    "Message: The measurement between cut 1 and cut 2 of "
                    + str(distBetweenCuts12)
                    + " mm seems wrong.\n\nPlease check the number and enter it again."
                )
                return False
            if (distBetweenCuts34 > workspaceWidth) or (
                distBetweenCuts34 < (workspaceWidth / 2)
            ):
                self.data.message_queue.put(
                    "Message: The measurement between cut 3 and cut 4 of "
                    + str(distBetweenCuts34)
                    + " mm seems wrong.\n\nPlease check the number and enter it again."
                )
                return False
            if (distWorkareaTopToCut5 > (workspaceHeight / 2)) or (
                distWorkareaTopToCut5 < 0
            ):
                self.data.message_queue.put(
                    "Message: The measurement between the top edge of the work area and cut 5 of "
                    + str(distWorkareaTopToCut5)
                    + " mm seems wrong.\n\nPlease check the number and enter it again."
                )
                return False
            if (bitDiameter > 25.4) or (bitDiameter < 0):
                self.data.message_queue.put(
                    "Message: The bit diameter value of "
                    + str(bitDiameter)
                    + " mm seems wrong.\n\nPlease check the number and enter it again."
                )
                return False

        # Configure iteration parameters

        acceptableTolerance = 0.0001
        numberOfIterations = 5000
        motorYcoordCorrectionScale = 0.5
        rotationRadiusCorrectionScale = 0.5
        chainSagCorrectionCorrectionScale = 1
        cutYoffsetCorrectionScale = 0.5

        # Gather current machine parameters

        motorSpacing = float(
            self.data.config.getValue("Maslow Settings", "motorSpacingX")
        )
        motorXcoord = motorSpacing / 2
        motorYoffsetEst = float(
            self.data.config.getValue("Maslow Settings", "motorOffsetY")
        )
        motorYcoordEst = (workspaceHeight / 2) + motorYoffsetEst
        rotationRadiusEst = float(
            self.data.config.getValue("Advanced Settings", "rotationRadius")
        )
        chainSagCorrectionEst = float(
            self.data.config.getValue("Advanced Settings", "chainSagCorrection")
        )
        if (
            str(self.data.config.getValue("Advanced Settings", "chainOverSprocket"))
            == "Top"
        ):
            chainOverSprocket = 1
        else:
            chainOverSprocket = 2
        gearTeeth = float(self.data.config.getValue("Advanced Settings", "gearTeeth"))
        chainPitch = float(self.data.config.getValue("Advanced Settings", "chainPitch"))
        motorSprocketRadius = (gearTeeth * chainPitch) / (2 * 3.14159)

        # Calculate the actual chain lengths for each cut location

        MotorDistanceCut1 = math.sqrt(
            math.pow(motorXcoord - ((workspaceWidth / 2) - 254), 2)
            + math.pow(motorYcoordEst - ((workspaceHeight / 2) - 254), 2)
        )
        MotorDistanceCut2 = math.sqrt(
            math.pow(motorXcoord + ((workspaceWidth / 2) - 254), 2)
            + math.pow(motorYcoordEst - ((workspaceHeight / 2) - 254), 2)
        )
        MotorDistanceCut3 = math.sqrt(
            math.pow(motorXcoord - ((workspaceWidth / 2) - 254), 2)
            + math.pow(motorYcoordEst + ((workspaceHeight / 2) - 254), 2)
        )
        MotorDistanceCut4 = math.sqrt(
            math.pow(motorXcoord + ((workspaceWidth / 2) - 254), 2)
            + math.pow(motorYcoordEst + ((workspaceHeight / 2) - 254), 2)
        )

        # Calculate the chain angles from horizontal, based on if the chain connects to the sled from the top or bottom of the sprocket
        if chainOverSprocket == 1:
            ChainAngleCut1 = math.asin(
                (motorYcoordEst - ((workspaceHeight / 2) - 254)) / MotorDistanceCut1
            ) + math.asin(motorSprocketRadius / MotorDistanceCut1)
            ChainAngleCut2 = math.asin(
                (motorYcoordEst - ((workspaceHeight / 2) - 254)) / MotorDistanceCut2
            ) + math.asin(motorSprocketRadius / MotorDistanceCut2)
            ChainAngleCut3 = math.asin(
                (motorYcoordEst + ((workspaceHeight / 2) - 254)) / MotorDistanceCut3
            ) + math.asin(motorSprocketRadius / MotorDistanceCut3)
            ChainAngleCut4 = math.asin(
                (motorYcoordEst + ((workspaceHeight / 2) - 254)) / MotorDistanceCut4
            ) + math.asin(motorSprocketRadius / MotorDistanceCut4)

            ChainAroundSprocketCut1 = motorSprocketRadius * ChainAngleCut1
            ChainAroundSprocketCut2 = motorSprocketRadius * ChainAngleCut2
            ChainAroundSprocketCut3 = motorSprocketRadius * ChainAngleCut3
            ChainAroundSprocketCut4 = motorSprocketRadius * ChainAngleCut4
        else:
            ChainAngleCut1 = math.asin(
                (motorYcoordEst - ((workspaceHeight / 2) - 254)) / MotorDistanceCut1
            ) - math.asin(motorSprocketRadius / MotorDistanceCut1)
            ChainAngleCut2 = math.asin(
                (motorYcoordEst - ((workspaceHeight / 2) - 254)) / MotorDistanceCut2
            ) - math.asin(motorSprocketRadius / MotorDistanceCut2)
            ChainAngleCut3 = math.asin(
                (motorYcoordEst + ((workspaceHeight / 2) - 254)) / MotorDistanceCut3
            ) - math.asin(motorSprocketRadius / MotorDistanceCut3)
            ChainAngleCut4 = math.asin(
                (motorYcoordEst + ((workspaceHeight / 2) - 254)) / MotorDistanceCut4
            ) - math.asin(motorSprocketRadius / MotorDistanceCut4)

            ChainAroundSprocketCut1 = motorSprocketRadius * (3.14159 - ChainAngleCut1)
            ChainAroundSprocketCut2 = motorSprocketRadius * (3.14159 - ChainAngleCut2)
            ChainAroundSprocketCut3 = motorSprocketRadius * (3.14159 - ChainAngleCut3)
            ChainAroundSprocketCut4 = motorSprocketRadius * (3.14159 - ChainAngleCut4)

        # Calculate the straight chain length from the sprocket to the bit
        ChainStraightCut1 = math.sqrt(
            math.pow(MotorDistanceCut1, 2) - math.pow(motorSprocketRadius, 2)
        )
        ChainStraightCut2 = math.sqrt(
            math.pow(MotorDistanceCut2, 2) - math.pow(motorSprocketRadius, 2)
        )
        ChainStraightCut3 = math.sqrt(
            math.pow(MotorDistanceCut3, 2) - math.pow(motorSprocketRadius, 2)
        )
        ChainStraightCut4 = math.sqrt(
            math.pow(MotorDistanceCut4, 2) - math.pow(motorSprocketRadius, 2)
        )

        # Correct the straight chain lengths to account for chain sag
        ChainStraightCut1 *= 1 + (
            (chainSagCorrectionEst / 1000000000000)
            * math.pow(math.cos(ChainAngleCut1), 2)
            * math.pow(ChainStraightCut1, 2)
            * math.pow(
                (math.tan(ChainAngleCut2) * math.cos(ChainAngleCut1))
                + math.sin(ChainAngleCut1),
                2,
            )
        )
        ChainStraightCut2 *= 1 + (
            (chainSagCorrectionEst / 1000000000000)
            * math.pow(math.cos(ChainAngleCut2), 2)
            * math.pow(ChainStraightCut2, 2)
            * math.pow(
                (math.tan(ChainAngleCut1) * math.cos(ChainAngleCut2))
                + math.sin(ChainAngleCut2),
                2,
            )
        )
        ChainStraightCut3 *= 1 + (
            (chainSagCorrectionEst / 1000000000000)
            * math.pow(math.cos(ChainAngleCut3), 2)
            * math.pow(ChainStraightCut3, 2)
            * math.pow(
                (math.tan(ChainAngleCut4) * math.cos(ChainAngleCut3))
                + math.sin(ChainAngleCut3),
                2,
            )
        )
        ChainStraightCut4 *= 1 + (
            (chainSagCorrectionEst / 1000000000000)
            * math.pow(math.cos(ChainAngleCut4), 2)
            * math.pow(ChainStraightCut4, 2)
            * math.pow(
                (math.tan(ChainAngleCut3) * math.cos(ChainAngleCut4))
                + math.sin(ChainAngleCut4),
                2,
            )
        )

        # Calculate total chain lengths accounting for sprocket geometry and chain sag
        ChainLengthCut1 = ChainAroundSprocketCut1 + ChainStraightCut1
        ChainLengthCut2 = ChainAroundSprocketCut2 + ChainStraightCut2
        ChainLengthCut3 = ChainAroundSprocketCut3 + ChainStraightCut3
        ChainLengthCut4 = ChainAroundSprocketCut4 + ChainStraightCut4

        # Subtract of the virtual length which is added to the chain by the rotation mechanism
        ChainLengthCut1 -= rotationRadiusEst
        ChainLengthCut2 -= rotationRadiusEst
        ChainLengthCut3 -= rotationRadiusEst
        ChainLengthCut4 -= rotationRadiusEst

        # Set up the iterative algorithm

        self.data.console_queue.put("Previous machine parameters:")
        self.data.console_queue.put(
            "Motor Spacing: "
            + str(motorSpacing)
            + ", Motor Y Offset: "
            + str(motorYoffsetEst)
            + ", Rotation Disk Radius: "
            + str(rotationRadiusEst)
            + ", Chain Sag Correction Value: "
            + str(chainSagCorrectionEst)
        )

        motorYcoordEst = distWorkareaTopToCut5 + (bitDiameter / 2) + 12.7
        # rotationRadiusEst = 0
        # chainSagCorrectionEst= 0
        cut34YoffsetEst = 0
        ChainErrorCut1 = acceptableTolerance
        ChainErrorCut2 = acceptableTolerance
        ChainErrorCut3 = acceptableTolerance
        ChainErrorCut4 = acceptableTolerance
        n = 0

        self.data.console_queue.put("Iterating for new machine parameters")

        # Iterate until error tolerance is achieved or maximum number of iterations occurs

        while (
            (abs(ChainErrorCut1) >= acceptableTolerance)
            or (abs(ChainErrorCut2) >= acceptableTolerance)
            or (abs(ChainErrorCut3) >= acceptableTolerance)
            or (abs(ChainErrorCut4) >= acceptableTolerance)
        ) and (n < numberOfIterations):
            n += 1

            # Calculate chain lengths for current estimated parameters

            MotorDistanceCut1Est = math.sqrt(
                math.pow(motorXcoord - (distBetweenCuts12 / 2), 2)
                + math.pow(motorYcoordEst, 2)
            )
            MotorDistanceCut2Est = math.sqrt(
                math.pow(motorXcoord + (distBetweenCuts12 / 2), 2)
                + math.pow(motorYcoordEst, 2)
            )
            MotorDistanceCut3Est = math.sqrt(
                math.pow(motorXcoord - (distBetweenCuts34 / 2), 2)
                + math.pow(
                    motorYcoordEst + (workspaceHeight - 508) - cut34YoffsetEst, 2
                )
            )
            MotorDistanceCut4Est = math.sqrt(
                math.pow(motorXcoord + (distBetweenCuts34 / 2), 2)
                + math.pow(
                    motorYcoordEst + (workspaceHeight - 508) - cut34YoffsetEst, 2
                )
            )

            # Calculate the chain angles from horizontal, based on if the chain connects to the sled from the top or bottom of the sprocket
            if chainOverSprocket == 1:
                ChainAngleCut1Est = math.asin(
                    motorYcoordEst / MotorDistanceCut1Est
                ) + math.asin(motorSprocketRadius / MotorDistanceCut1Est)
                ChainAngleCut2Est = math.asin(
                    motorYcoordEst / MotorDistanceCut2Est
                ) + math.asin(motorSprocketRadius / MotorDistanceCut2Est)
                ChainAngleCut3Est = math.asin(
                    (motorYcoordEst + (workspaceHeight - 508) - cut34YoffsetEst)
                    / MotorDistanceCut3Est
                ) + math.asin(motorSprocketRadius / MotorDistanceCut3Est)
                ChainAngleCut4Est = math.asin(
                    (motorYcoordEst + (workspaceHeight - 508) - cut34YoffsetEst)
                    / MotorDistanceCut4Est
                ) + math.asin(motorSprocketRadius / MotorDistanceCut4Est)

                ChainAroundSprocketCut1Est = motorSprocketRadius * ChainAngleCut1Est
                ChainAroundSprocketCut2Est = motorSprocketRadius * ChainAngleCut2Est
                ChainAroundSprocketCut3Est = motorSprocketRadius * ChainAngleCut3Est
                ChainAroundSprocketCut4Est = motorSprocketRadius * ChainAngleCut4Est
            else:
                ChainAngleCut1Est = math.asin(
                    motorYcoordEst / MotorDistanceCut1Est
                ) - math.asin(motorSprocketRadius / MotorDistanceCut1Est)
                ChainAngleCut2Est = math.asin(
                    motorYcoordEst / MotorDistanceCut2Est
                ) - math.asin(motorSprocketRadius / MotorDistanceCut2Est)
                ChainAngleCut3Est = math.asin(
                    (motorYcoordEst + (workspaceHeight - 508) - cut34YoffsetEst)
                    / MotorDistanceCut3Est
                ) - math.asin(motorSprocketRadius / MotorDistanceCut3Est)
                ChainAngleCut4Est = math.asin(
                    (motorYcoordEst + (workspaceHeight - 508) - cut34YoffsetEst)
                    / MotorDistanceCut4Est
                ) - math.asin(motorSprocketRadius / MotorDistanceCut4Est)

                ChainAroundSprocketCut1Est = motorSprocketRadius * (
                    3.14159 - ChainAngleCut1Est
                )
                ChainAroundSprocketCut2Est = motorSprocketRadius * (
                    3.14159 - ChainAngleCut2Est
                )
                ChainAroundSprocketCut3Est = motorSprocketRadius * (
                    3.14159 - ChainAngleCut3Est
                )
                ChainAroundSprocketCut4Est = motorSprocketRadius * (
                    3.14159 - ChainAngleCut4Est
                )

            # Calculate the straight chain length from the sprocket to the bit
            ChainStraightCut1Est = math.sqrt(
                math.pow(MotorDistanceCut1Est, 2) - math.pow(motorSprocketRadius, 2)
            )
            ChainStraightCut2Est = math.sqrt(
                math.pow(MotorDistanceCut2Est, 2) - math.pow(motorSprocketRadius, 2)
            )
            ChainStraightCut3Est = math.sqrt(
                math.pow(MotorDistanceCut3Est, 2) - math.pow(motorSprocketRadius, 2)
            )
            ChainStraightCut4Est = math.sqrt(
                math.pow(MotorDistanceCut4Est, 2) - math.pow(motorSprocketRadius, 2)
            )

            # Correct the straight chain lengths to account for chain sag
            ChainStraightCut1Est *= 1 + (
                (chainSagCorrectionEst / 1000000000000)
                * math.pow(math.cos(ChainAngleCut1Est), 2)
                * math.pow(ChainStraightCut1Est, 2)
                * math.pow(
                    (math.tan(ChainAngleCut2Est) * math.cos(ChainAngleCut1Est))
                    + math.sin(ChainAngleCut1Est),
                    2,
                )
            )
            ChainStraightCut2Est *= 1 + (
                (chainSagCorrectionEst / 1000000000000)
                * math.pow(math.cos(ChainAngleCut2Est), 2)
                * math.pow(ChainStraightCut2Est, 2)
                * math.pow(
                    (math.tan(ChainAngleCut1Est) * math.cos(ChainAngleCut2Est))
                    + math.sin(ChainAngleCut2Est),
                    2,
                )
            )
            ChainStraightCut3Est *= 1 + (
                (chainSagCorrectionEst / 1000000000000)
                * math.pow(math.cos(ChainAngleCut3Est), 2)
                * math.pow(ChainStraightCut3Est, 2)
                * math.pow(
                    (math.tan(ChainAngleCut4Est) * math.cos(ChainAngleCut3Est))
                    + math.sin(ChainAngleCut3Est),
                    2,
                )
            )
            ChainStraightCut4Est *= 1 + (
                (chainSagCorrectionEst / 1000000000000)
                * math.pow(math.cos(ChainAngleCut4Est), 2)
                * math.pow(ChainStraightCut4Est, 2)
                * math.pow(
                    (math.tan(ChainAngleCut3Est) * math.cos(ChainAngleCut4Est))
                    + math.sin(ChainAngleCut4Est),
                    2,
                )
            )

            # Calculate total chain lengths accounting for sprocket geometry and chain sag
            ChainLengthCut1Est = ChainAroundSprocketCut1Est + ChainStraightCut1Est
            ChainLengthCut2Est = ChainAroundSprocketCut2Est + ChainStraightCut2Est
            ChainLengthCut3Est = ChainAroundSprocketCut3Est + ChainStraightCut3Est
            ChainLengthCut4Est = ChainAroundSprocketCut4Est + ChainStraightCut4Est

            # Subtract of the virtual length which is added to the chain by the rotation mechanism
            ChainLengthCut1Est -= rotationRadiusEst
            ChainLengthCut2Est -= rotationRadiusEst
            ChainLengthCut3Est -= rotationRadiusEst
            ChainLengthCut4Est -= rotationRadiusEst

            # Determine chain length errors for current estimated machine parameters versus the measured parameters

            ChainErrorCut1 = ChainLengthCut1Est - ChainLengthCut1
            ChainErrorCut2 = ChainLengthCut2Est - ChainLengthCut2
            ChainErrorCut3 = ChainLengthCut3Est - ChainLengthCut3
            ChainErrorCut4 = ChainLengthCut4Est - ChainLengthCut4

            # Develop a printable motor Y offset value to update the user

            motorYoffsetEstPrint = (
                motorYcoordEst - distWorkareaTopToCut5 - (bitDiameter / 2) - 12.7
            )

            self.data.console_queue.put(
                "N: "
                + str(n)
                + ", Motor Spacing: "
                + str(round(motorSpacing, 3))
                + ", Motor Y Offset: "
                + str(round(motorYoffsetEstPrint, 3))
                + ", Rotation Disk Radius: "
                + str(round(rotationRadiusEst, 3))
                + ", Chain Sag Correction Value: "
                + str(round(chainSagCorrectionEst, 6))
            )
            self.data.console_queue.put(
                "  Chain Error Cut 1: "
                + str(round(ChainErrorCut1, 4))
                + ", Chain Error Cut 2: "
                + str(round(ChainErrorCut2, 4))
                + ", Chain Error Cut 3: "
                + str(round(ChainErrorCut3, 4))
                + ", Chain Error Cut 4: "
                + str(round(ChainErrorCut4, 4))
                + ", Sled Drift Compensation: "
                + str(round(cut34YoffsetEst, 4))
            )

            # Update the motorYcoord and rotationRadius parameters based on the current chain length errors

            motorYcoordEst -= ChainErrorCut1 * motorYcoordCorrectionScale
            rotationRadiusEst += ChainErrorCut2 * rotationRadiusCorrectionScale
            if rotationRadiusEst < 0:
                rotationRadiusEst = 0

            # When we get close to correct values for motorYcoord and rotationRadius begin calibrating for chain sag

            if abs(ChainErrorCut1) < 1 and abs(ChainErrorCut2) < 1:
                chainSagCorrectionEst -= (
                    ChainErrorCut4 * chainSagCorrectionCorrectionScale
                )
                cut34YoffsetEst += (
                    (ChainErrorCut3 + ChainErrorCut4) / 2
                ) * cutYoffsetCorrectionScale
                if chainSagCorrectionEst < 0:
                    chainSagCorrectionEst = 0

            # If we get unrealistic values, reset and try again with smaller steps

            if (
                motorYcoordEst < -(workspaceHeight / 4)
                or motorYcoordEst > (2 * workspaceHeight)
                or rotationRadiusEst > workspaceHeight
            ):
                motorYcoordEst = distWorkareaTopToCut5 + (bitDiameter / 2) + 12.7
                rotationRadiusEst = 0
                chainSagCorrectionEst = 0
                cut34YoffsetEst = 0
                motorYcoordCorrectionScale = float(motorYcoordCorrectionScale / 2)
                rotationRadiusCorrectionScale = float(rotationRadiusCorrectionScale / 2)
                chainSagCorrectionCorrectionScale = float(
                    chainSagCorrectionCorrectionScale / 2
                )
                cutYoffsetCorrectionScale = float(cutYoffsetCorrectionScale / 2)
                self.data.console_queue.put("Estimated values out of range, trying again with smaller steps")

        if n == numberOfIterations:
            self.data.ui_queue1.put("Alert", "Alert",
                "Message: The machine was not able to be calibrated. Please ensure the work area dimensions are correct and try again."
            )
            self.data.console_queue.put("Machine parameters could not be determined")

            return False

        self.data.console_queue.put("Machine parameters found:")

        motorYoffsetEst = (
            motorYcoordEst - distWorkareaTopToCut5 - (bitDiameter / 2) - 12.7
        )

        motorYoffsetEst = round(motorYoffsetEst, 1)
        rotationRadiusEst = round(rotationRadiusEst, 1)
        chainSagCorrectionEst = round(chainSagCorrectionEst, 6)

        self.data.console_queue.put(
            "Motor Spacing: "
            + str(motorSpacing)
            + ", Motor Y Offset: "
            + str(motorYoffsetEst)
            + ", Rotation Disk Radius: "
            + str(rotationRadiusEst)
            + ", Chain Sag Correction Value: "
            + str(chainSagCorrectionEst)
        )

        self.motorYoffsetEst = motorYoffsetEst
        self.rotationRadiusEst = rotationRadiusEst
        self.chainSagCorrectionEst = chainSagCorrectionEst

        return (
            motorYoffsetEst,
            rotationRadiusEst,
            chainSagCorrectionEst,
            cut34YoffsetEst,
        )

    def acceptTriangularCalibrationResults(self):
        '''
        Saves the values that were calculated.
        :return:
        '''
        self.data.config.setValue('Maslow Settings', 'motorOffsetY', str(self.motorYoffsetEst))
        self.data.config.setValue('Advanced Settings', 'rotationRadius', str(self.rotationRadiusEst))
        self.data.config.setValue('Advanced Settings', 'chainSagCorrection', str(self.chainSagCorrectionEst))
        
        self.data.gcode_queue.put("G21 ")
        self.data.gcode_queue.put("G90 ")
        self.data.gcode_queue.put("G40 ")
        self.data.gcode_queue.put("G0 X0 Y0 ")
        return True

