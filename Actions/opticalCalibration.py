from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from scipy.spatial import distance as dist
from imutils import perspective, contours

# from imutils.video                      import VideoStream
# from Background.webcamVideoStream       import WebcamVideoStream
# from imutils.video			import WebcamVideoStream
import numpy as np
import imutils
import cv2
import time
import re
import sys
import math
import base64
import json


class OpticalCalibration(MakesmithInitFuncs):

    camera = None
    time.sleep(2.0)
    gaussianBlurValue = 5
    cannyLowValue = 50
    cannyHighValue = 100
    opticalCenter = (None, None)
    HomingPosX = 0
    HomingPosY = 0
    HomingX = 0
    HomingY = 0
    matrixSize = (31, 15)
    calErrorsX = np.zeros(matrixSize)
    calErrorsY = np.zeros(matrixSize)
    xCurve = np.zeros(shape=(6))  # coefficients for quadratic curve
    yCurve = np.zeros(shape=(6))  # coefficients for quadratic curve
    inAutoMode = False
    inMeasureOnlyMode = False
    autoScanDirection = 0

    def __init__(self):
        # can't do much because data hasn't been initialized yet
        pass

    def reloadCalibration(self):
        try:
            xyErrors = self.data.config.getValue('Optical Calibration Settings', 'xyErrorArray')
            self.calErrorsX, self.calErrorsY = self.data.config.parseErrorArray(xyErrors, True)
            self.xCurve[0] = float(self.data.config.getValue('Optical Calibration Settings', 'calX0'))
            self.xCurve[1] = float(self.data.config.getValue('Optical Calibration Settings', 'calX1'))
            self.xCurve[2] = float(self.data.config.getValue('Optical Calibration Settings', 'calX2'))
            self.xCurve[3] = float(self.data.config.getValue('Optical Calibration Settings', 'calX3'))
            self.xCurve[4] = float(self.data.config.getValue('Optical Calibration Settings', 'calX4'))
            self.xCurve[5] = float(self.data.config.getValue('Optical Calibration Settings', 'calX5'))
            self.yCurve[0] = float(self.data.config.getValue('Optical Calibration Settings', 'calY0'))
            self.yCurve[1] = float(self.data.config.getValue('Optical Calibration Settings', 'calY1'))
            self.yCurve[2] = float(self.data.config.getValue('Optical Calibration Settings', 'calY2'))
            self.yCurve[3] = float(self.data.config.getValue('Optical Calibration Settings', 'calY3'))
            self.yCurve[4] = float(self.data.config.getValue('Optical Calibration Settings', 'calY4'))
            self.yCurve[5] = float(self.data.config.getValue('Optical Calibration Settings', 'calY5'))
            print("reloaded calibration data")
            return self.calErrorsX, self.calErrorsY, self.xCurve, self.yCurve
        except Exception as e:
            print(e)
            return None, None, None, None


    def clearCalibration(self):
        try:
            self.calErrorsX = np.zeros(self.matrixSize)
            self.calErrorsY = np.zeros(self.matrixSize)
            self.xCurve = np.zeros(shape=(6))  # coefficients for quadratic curve
            self.yCurve = np.zeros(shape=(6))  # coefficients for quadratic curve
            return True
        except Exception as e:
            print(e)
            return False


    def stopCut(self):
        self.data.quick_queue.put("!")
        with self.data.gcode_queue.mutex:
            self.data.gcode_queue.queue.clear()
        self.inAutoMode = False
        self.inMeasureOnlyMode = False

    def midpoint(self, ptA, ptB):
        return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

    def distance(self, ptA, ptB):
        a = ptA[0]-ptB[0]
        b = ptA[1]-ptB[1]
        return (math.sqrt((a*a+b*b)))

    def removeOutliersAndAverage(self, data):
        mean = np.mean(data)
        sd = np.std(data)
        tArray = [
            x for x in data if ((x >= mean - 2.0 * sd) and (x <= mean + 2.0 * sd))
        ]
        return np.average(tArray), np.std(tArray)

    def simplifyContour(self, c, sides=4):
        tolerance = 0.01
        while True:
            _c = cv2.approxPolyDP(c, tolerance * cv2.arcLength(c, True), True)
            if len(_c) <= sides or tolerance > 0.5:
                break
            tolerance += 0.01
        if (
            len(_c) < sides
        ):  # went too small.. now lower the tolerance until four points or more are reached
            while True:
                tolerance -= 0.01
                _c = cv2.approxPolyDP(c, tolerance * cv2.arcLength(c, True), True)
                if len(_c) >= sides or tolerance <= 0.1:
                    break
        return _c

    def setCalibrationSettings(self, args):
        self.markerX = float(args["markerX"])
        self.markerY = float(args["markerY"])
        self.opticalCenter = (float(args["opticalCenterX"]), float(args["opticalCenterY"]))
        self.scaleX = float(args["scaleX"])
        self.scaleY = float(args["scaleY"])
        self.tlX = int(args["tlX"])
        self.tlY = int(args["tlY"])
        self.brX = int(args["brX"])
        self.brY = int(args["brY"])
        self.autoScanDirection = int(args["autoScanDirection"])
        self.gaussianBlurValue = int(args["gaussianBlurValue"])
        self.cannyLowValue = float(args["cannyLowValue"])
        self.cannyHighValue = float(args["cannyHighValue"])

    def saveOpticalCalibrationConfiguration(self, args):
        print("Saving Configuration")
        try:
            print(args)
            self.data.config.setValue("Optical Calibration Settings", "opticalCenterX", float(args["opticalCenterX"]))
            self.data.config.setValue("Optical Calibration Settings", "opticalCenterY", float(args["opticalCenterY"]))
            self.data.config.setValue("Optical Calibration Settings", "scaleX", float(args["scaleX"]))
            self.data.config.setValue("Optical Calibration Settings", "scaleY", float(args["scaleY"]))
            self.data.config.setValue("Optical Calibration Settings", "gaussianBlurValue",
                                      int(args["gaussianBlurValue"]))
            self.data.config.setValue("Optical Calibration Settings", "cannyLowValue", float(args["cannyLowValue"]))
            self.data.config.setValue("Optical Calibration Settings", "cannyHighValue", float(args["cannyHighValue"]))
            self.data.config.setValue("Optical Calibration Settings", "autoScanDirection",
                                      int(args["autoScanDirection"]))
            self.data.config.setValue("Optical Calibration Settings", "markerX", float(args["markerX"]))
            self.data.config.setValue("Optical Calibration Settings", "markerY", float(args["markerY"]))
            self.data.config.setValue("Optical Calibration Settings", "tlX", int(args["tlX"]))
            self.data.config.setValue("Optical Calibration Settings", "tlY", int(args["tlY"]))
            self.data.config.setValue("Optical Calibration Settings", "brX", int(args["brX"]))
            self.data.config.setValue("Optical Calibration Settings", "brY", int(args["brY"]))
            self.data.config.setValue("Optical Calibration Settings", "calibrationExtents", args["calibrationExtents"])
        except Exception as e:
            print(e)
            return False
        return True

    def translatePoint(self, xB, yB, xA, yA, angle):
        cosa = math.cos((angle) * 3.141592 / 180.0)
        sina = math.sin((angle) * 3.141592 / 180.0)
        xB -= xA
        yB -= yA
        _xB = xB * cosa - yB * sina
        _yB = xB * sina + yB * cosa
        xB = _xB + xA
        yB = _yB + yA
        return xB, yB

    def HomeIn(self):
        _posX = round(self.HomingPosX * 3.0 + self.HomingX / 25.4, 4)
        _posY = round(self.HomingPosY * 3.0 + self.HomingY / 25.4, 4)
        # self.updateTargetIndicator(_posX,_posY,"INCHES")
        print(
            "Moving to ({},{}) by trying [{}, {}]".format(
                self.HomingPosX * 3.0, self.HomingPosY * 3.0, _posX, _posY
            )
        )
        #self.on_AutoHome()
        
        self.data.units = "INCHES"
        self.data.gcode_queue.put("G20 ")
        self.data.gcode_queue.put("G90  ")
        self.data.gcode_queue.put("G0 X" + str(_posX) + " Y" + str(_posY) + "  ")
        self.data.gcode_queue.put("G91  ")
        self.data.measureRequest = self.on_CenterOnSquare
        # request a measurement
        self.data.gcode_queue.put("B10 L")
        

    def processImage(self, findCenter=False):

        dxList = np.zeros(shape=(10))
        dyList = np.zeros(shape=(10))
        diList = np.zeros(shape=(10))
        xBList = np.zeros(shape=(10))
        yBList = np.zeros(shape=(10))
        x = 0
        falseCounter = 0

        while True:
            (grabbed, image) = self.camera.read()
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(
                gray, (self.gaussianBlurValue, self.gaussianBlurValue), 0
            )
            edged = cv2.Canny(gray, self.cannyLowValue, self.cannyHighValue)
            edged = cv2.dilate(edged, None, iterations=1)
            edged = cv2.erode(edged, None, iterations=1)
            cnts = cv2.findContours(
                edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            cnts = cnts[0] if imutils.is_cv2() else cnts[1]
            (cnts, _) = contours.sort_contours(cnts)
            colors = (
                (0, 0, 255),
                (240, 0, 159),
                (0, 165, 255),
                (255, 255, 0),
                (255, 0, 255),
            )
            refObj = None
            height, width, channels = image.shape
            if self.opticalCenter[0] is None or self.opticalCenter[1] is None:
                xA = int(width / 2)
                yA = int(height / 2)
            else:
                xA, yA = self.opticalCenter

            maxArea = 0
            for cTest in cnts:
                if cv2.contourArea(cTest) > maxArea:
                    maxArea = cv2.contourArea(cTest)
                    c = cTest
            if cv2.contourArea(c) > 1000:
                orig = image.copy()
                # approximate to a square (i.e., four contour segments)
                cv2.drawContours(orig, [c.astype("int")], -1, (255, 255, 0), 2)
                # simplify the contour to get it as square as possible (i.e., remove the noise from the edges)
                if findCenter:
                    sides = 20
                else:
                    sides = 4
                c = self.simplifyContour(c, sides)
                cv2.drawContours(orig, [c.astype("int")], -1, (255, 0, 0), 2)
                box = cv2.minAreaRect(c)
                angle = box[-1]
                if abs(angle + 90) < 30:
                    _angle = angle + 90
                else:
                    _angle = angle
                box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
                box = np.array(box, dtype="int")
                box = perspective.order_points(box)
                cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)
                # cv2.imwrite('testing/image-out'+str(x)+".png",orig)
                if findCenter == False:
                    M = cv2.getRotationMatrix2D((xA, yA), _angle, 1)
                    #orig = cv2.warpAffine(orig, M, (width, height))  # don't need to do this for every image
                xB = np.average(box[:, 0])
                yB = np.average(box[:, 1])
                (tl, tr, br, bl) = box
                (tlblX, tlblY) = self.midpoint(tl, bl)
                (trbrX, trbrY) = self.midpoint(tr, br)
                (tltrX, tltrY) = self.midpoint(tl, tr)
                (blbrX, blbrY) = self.midpoint(bl, br)
                xD = self.distance((tlblX, tlblY), (trbrX, trbrY)) / (self.markerX*25.4)
                yD = self.distance((tltrX, tltrY), (blbrX, blbrY)) / (self.markerY*25.4)
                if xD == 0:  # doing this to catch bad calibrations and stop crashing
                    xD = 1.0
                if yD == 0:
                    yD = 1.0
                cos = math.cos(angle * 3.141592 / 180.0)
                sin = math.sin(angle * 3.141592 / 180.0)
                if _angle < 30:
                    _angle = _angle * -1.0
                if findCenter == False:
                    xB, yB = self.translatePoint(xB, yB, xA, yA, _angle)
                Dx = dist.euclidean((xA, 0), (xB, 0)) / xD
                if xA > xB:
                    Dx *= -1
                Dy = dist.euclidean((0, yA), (0, yB)) / yD
                if yA < yB:
                    Dy *= -1
                Dist = math.sqrt(Dx ** 2.0 + Dy ** 2.0)
                dxList[x] = Dx
                dyList[x] = Dy
                diList[x] = Dist
                xBList[x] = xB
                yBList[x] = yB
                x += 1
                #print("Processed Image " + str(x))
                if x == 10:
                    break
            else:
                falseCounter += 1
                if falseCounter == 10:
                    break
        print("Got 10 images processed, " + str(falseCounter) + " images were bad")
        if dxList.ndim != 0:
            avgDx, stdDx = self.removeOutliersAndAverage(dxList)
            avgDy, stdDy = self.removeOutliersAndAverage(dyList)
            avgDi, stdDi = self.removeOutliersAndAverage(diList)
            avgxB, stdxB = self.removeOutliersAndAverage(xBList)
            avgyB, stdyB = self.removeOutliersAndAverage(yBList)

            if findCenter == False:
                orig = cv2.warpAffine(orig, M, (width, height))
            return avgDx, avgDy, avgDi, avgxB, avgyB, orig
        else:
            return None, None, None, None, None, edged

    def on_CenterOnSquare(self, _dist, findCenter=False):

        avgDx, avgDy, avgDi, avgxB, avgyB, image = self.processImage(findCenter)

        if avgDx is not None:
            cv2.putText(image, "(" + str(self.HomingPosX) + ", " + str(self.HomingPosY) + ")", (15, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,0,255), 2)
            cv2.putText(image, "Dx:{:.3f}, Dy:{:.3f}->Di:{:.3f}mm".format(avgDx, avgDy, avgDi), (15, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,0,255), 2)
            cv2.putText(image, "({:.3f}, {:.3f})".format(avgxB, avgyB), (15, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,0,255), 2)
            imgencode = cv2.imencode(".png", image)[1]
            stringData = base64.b64encode(imgencode).decode()
            self.data.opticalCalibrationImage = stringData
            self.data.opticalCalibrationImageUpdated = True
            self.HomingX += avgDx
            self.HomingY += avgDy
            if ((abs(avgDx) >= 0.125) or (abs(avgDy) >= 0.125)) and ( not findCenter ):
                print("Adjusting Location")
                self.HomeIn()
            else:
                xS = self.HomingX + self.HomingPosX * 3 * 25.4 * (1.0 - self.scaleX)
                yS = self.HomingY + self.HomingPosY * 3 * 25.4 * (1.0 - self.scaleY)
                if self.inMeasureOnlyMode:
                    self.measuredErrorsX[self.HomingPosX + 15][7 - self.HomingPosY] = xS
                    self.measuredErrorsY[self.HomingPosX + 15][7 - self.HomingPosY] = yS
                elif not findCenter:
                    self.calErrorsX[self.HomingPosX + 15][7 - self.HomingPosY] = xS
                    self.calErrorsY[self.HomingPosX + 15][7 - self.HomingPosY] = yS
                else:
                    self.opticalCenter = (avgxB, avgyB)
                    print(str(avgxB)+", "+str(avgyB))
                if self.inAutoMode:
                    self.on_AutoHome()
                else:
                    print("avgDx,Dy:" + str(avgDx) + ", " + str(avgDy))
                    print("Releasing Camera")
                    self.camera.release()
                    print("Done")
        else:
            return False

    def on_AutoHome(self, measureMode=False):
        try:
            minX = self.tlX
            maxX = self.brX
            minY = self.tlY
            maxY = self.brY
            if measureMode == True:
                print("Measure Only")
                self.inMeasureOnlyMode = True
            if self.inAutoMode == False:
                self.HomingX = 0.0
                self.HomingY = 0.0
                self.HomingPosX = minX
                self.HomingPosY = minY
                self.HomingScanDirection = 1
                self.inAutoMode = True
                self.HomeIn()
            else:
                # note, the self.HomingX and self.HomingY are not reinitialzed here
                # The rationale is that the offset for the previous registration point is
                # probably a good starting point for this registration point..
                if self.autoScanDirection == 0:  # horizontal
                    if self.inMeasureOnlyMode:
                        self.HomingX = 0.0
                        self.HomingY = 0.0
                    self.HomingPosX += self.HomingScanDirection
                    if (self.HomingPosX == maxX + 1) or (self.HomingPosX == minX - 1):
                        if self.HomingPosX == maxX + 1:
                            self.HomingPosX = maxX
                        else:
                            self.HomingPosX = minX
                        self.HomingScanDirection *= -1
                        self.HomingPosY -= 1
                    if self.HomingPosY >= maxY:
                        self.HomingY -= 7.0  # drop down 7 mm for next square's guess (only)
                        self.HomeIn()
                    else:
                        self.inAutoMode = False
                        print("Releasing Camera")
                        self.camera.release()
                        self.camera=None
                        print("Calibration Completed")
                        #send ui updated data
                        data = {"errorX": self.calErrorsX.tolist(), "errorY": self.calErrorsY.tolist()}
                        self.data.ui_queue.put(
                             "Action: updateOpticalCalibrationError:_" + json.dumps(data)
                        )
                        print("sent")
                        # self.printCalibrationErrorValue()
                else:  # vertical
                    print("Vertical Scan")
                    if self.inMeasureOnlyMode:
                        self.HomingX = 0.0
                        self.HomingY = 0.0
                    self.HomingPosY -= self.HomingScanDirection
                    if (self.HomingPosY == maxY - 1) or (self.HomingPosY == minY + 1):
                        if self.HomingPosY == minY + 1:
                            self.HomingPosY = minY
                        else:
                            self.HomingPosY = maxY
                        self.HomingScanDirection *= -1
                        self.HomingPosX += 1
                    if self.HomingPosX <= maxX:
                        self.HomingY -= 7.0  # drop down 7 mm for next square's guess (only)
                        self.HomeIn()
                    else:
                        self.inAutoMode = False
                        print("Releasing Camera")
                        self.camera.release()
                        self.camera=None
                        print("Calibration Completed")
        except Exception as e:
            print(e)

    def on_Calibrate(self, args):
        print("Initializing")
        self.setCalibrationSettings(args)
        self.saveOpticalCalibrationConfiguration(args)
        print(
            "Extents:"
            + str(self.tlX)
            + ", "
            + str(self.tlY)
            + " to "
            + str(self.brX)
            + ", "
            + str(self.brY)
        )
        if self.camera is None:
            print("Starting Camera")
            self.camera = cv2.VideoCapture(0)
        print("Analyzing Images")
        self.on_AutoHome(False)
        return True

    def testImage(self, args):
        print("at Test Image")
        self.setCalibrationSettings(args)
        if self.camera is None:
            print("Starting Camera")
            self.camera = cv2.VideoCapture(0)
        avgDx, avgDy, avgDi, avgxB, avgyB, image = self.processImage(False)
        print("Releasing Camera")
        self.camera.release()
        self.camera = None
        if avgDx is not None:
            imgencode = cv2.imencode(".png", image)[1]
            stringData = base64.b64encode(imgencode).decode()
            self.data.opticalCalibrationTestImage = stringData
            self.data.opticalCalibrationTestImageUpdated = True
            print(str(avgxB)+", "+str(avgyB))
            return True
        else:
            imgencode = cv2.imencode(".png", image)[1]
            stringData = base64.b64encode(imgencode).decode()
            self.data.opticalCalibrationTestImage = stringData
            self.data.opticalCalibrationTestImageUpdated = True
            return True

    def on_SaveCSV(self):
        outFile = open("calibrationValues.csv","w")
        line = ""
        for y in range(7, -8, -1):
            line = ""
            for x in range(-15, 16, +1):
                line += "{:.2f},".format(self.calErrorsX[x+15][7-y])
            line +="\n"
            outFile.write(line)
        outFile.write("\n")
        for y in range(7, -8, -1):
            line = ""
            for x in range(-15, 16, +1):
                line += "{:.2f},".format(self.calErrorsY[x+15][7-y])
            line +="\n"
            outFile.write(line)
        outFile.close()


    def saveAndSend(self):
        try:
            _str = ""
            _strcomma = ""
            for z in range(2):
                for y in range(15):
                    for x in range(31):
                        if ((x == 30) and (y == 14) and (z == 1)):
                            _strcomma = ""
                        else:
                            _strcomma = ","
                        if (z == 0):
                            _str += str(int(self.calErrorsX[x][y] * 1000)) + _strcomma
                        else:
                            _str += str(int(self.calErrorsY[x][y] * 1000)) + _strcomma
            # print _str

            self.data.config.setValue('Optical Calibration Settings', 'calX0', str(self.xCurve[0]))
            self.data.config.setValue('Optical Calibration Settings', 'calX1', str(self.xCurve[1]))
            self.data.config.setValue('Optical Calibration Settings', 'calX2', str(self.xCurve[2]))
            self.data.config.setValue('Optical Calibration Settings', 'calX3', str(self.xCurve[3]))
            self.data.config.setValue('Optical Calibration Settings', 'calX4', str(self.xCurve[4]))
            self.data.config.setValue('Optical Calibration Settings', 'calX5', str(self.xCurve[5]))
            self.data.config.setValue('Optical Calibration Settings', 'calY0', str(self.yCurve[0]))
            self.data.config.setValue('Optical Calibration Settings', 'calY1', str(self.yCurve[1]))
            self.data.config.setValue('Optical Calibration Settings', 'calY2', str(self.yCurve[2]))
            self.data.config.setValue('Optical Calibration Settings', 'calY3', str(self.yCurve[3]))
            self.data.config.setValue('Optical Calibration Settings', 'calY4', str(self.yCurve[4]))
            self.data.config.setValue('Optical Calibration Settings', 'calY5', str(self.yCurve[5]))

            self.data.config.setValue('Optical Calibration Settings', 'xyErrorArray', _str)
            return True
        except Exception as e:
            print(e)
            return False

    def surfaceFit(self):
        # set data into proper format
        try:
            dataX = np.zeros(((15 * 31), 3))
            dataY = np.zeros(((15 * 31), 3))
            for y in range(7, -8, -1):
                for x in range(-15, 16, +1):
                    dataX[(7 - y) * 31 + (x + 15)][0] = float(x * 3.0 * 25.4)
                    dataY[(7 - y) * 31 + (x + 15)][0] = float(x * 3.0 * 25.4)
                    dataX[(7 - y) * 31 + (x + 15)][1] = float(y * 3.0 * 25.4)
                    dataY[(7 - y) * 31 + (x + 15)][1] = float(y * 3.0 * 25.4)
                    dataX[(7 - y) * 31 + (x + 15)][2] = self.calErrorsX[x + 15][7 - y]
                    dataY[(7 - y) * 31 + (x + 15)][2] = self.calErrorsY[x + 15][7 - y]
            # surface fit X Errors
            xA = np.c_[np.ones(dataX.shape[0]), dataX[:, :2], np.prod(dataX[:, :2], axis=1), dataX[:, :2] ** 2]
            self.xCurve, _, _, _ = np.linalg.lstsq(xA, dataX[:, 2], rcond=None)
            xB = dataX[:, 2]
            xSStot = ((xB - xB.mean()) ** 2).sum()
            xSSres = ((xB - np.dot(xA, self.xCurve)) ** 2).sum()
            if (xSStot != 0):
                xR2 = 1.0 - xSSres / xSStot
            else:
                xR2 = 0.0
            # surface fit Y Errors

            yA = np.c_[np.ones(dataY.shape[0]), dataY[:, :2], np.prod(dataY[:, :2], axis=1), dataY[:, :2] ** 2]
            self.yCurve, _, _, _ = np.linalg.lstsq(yA, dataY[:, 2], rcond=None)
            yB = dataY[:, 2]
            ySStot = ((yB - yB.mean()) ** 2).sum()
            ySSres = ((yB - np.dot(yA, self.yCurve)) ** 2).sum()
            if (ySStot != 0):
                yR2 = 1.0 - ySSres / ySStot
            else:
                yR2 = 0.0

            print(self.xCurve)
            print(xR2)
            print(self.yCurve)
            print(yR2)
            return self.xCurve.tolist(), self.yCurve.tolist()
        except Exception as e:
            print(e)
            return None, None

