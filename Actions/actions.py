from DataStructures.makesmithInitFuncs         import  MakesmithInitFuncs

import sys
import threading
import re
import math

class Actions(MakesmithInitFuncs):


    def defineHome(self):
        try:
            if self.data.units == 'MM':
                scaleFactor = 25.4
            else:
                scaleFactor = 1.0
            self.data.gcodeShift = [self.data.xval/scaleFactor,self.data.yval/scaleFactor]
            self.data.config.setValue("Advanced Settings", 'homeX', str(self.data.xval))
            self.data.config.setValue("Advanced Settings", 'homeY', str(self.data.yval))
            self.data.gcodeFile.loadUpdateFile()
            return True
        except:
            return False

    def home(self):
        try:
            self.data.gcode_queue.put("G90  ")
            #todo:self.gcodeVel = "[MAN]"
            safeHeightMM = float(self.data.config.getValue('Maslow Settings', 'zAxisSafeHeight'))
            safeHeightInches = safeHeightMM / 25.5
            if self.data.units == "INCHES":
                self.data.gcode_queue.put("G00 Z" + '%.3f'%(safeHeightInches))
            else:
                self.data.gcode_queue.put("G00 Z" + str(safeHeightMM))
            self.data.gcode_queue.put("G00 X" + str(self.data.gcodeShift[0]) + " Y" + str(self.data.gcodeShift[1]) + " ")
            self.data.gcode_queue.put("G00 Z0 ")
            return True
        except:
            return False

    def resetChainLengths(self):
        try:
            self.data.gcode_queue.put("B08 ")
            return True
        except:
            return False

    def defineZ0(self):
        try:
            self.data.gcode_queue.put("G10 Z0 ")
            return True
        except:
            return False

    def stopZ(self):
        try:
            self.data.quick_queue.put("!")
            with self.data.gcode_queue.mutex:
                self.data.gcode_queue.queue.clear()
            return True
        except:
            return False

    def startRun(self):
        try:
            self.data.uploadFlag = 1
            self.data.gcode_queue.put(self.data.gcode[self.data.gcodeIndex])
            self.data.gcodeIndex += 1
            return True
        except:
            app.gcodecanvas.uploadFlag = 0
            self.data.gcodeIndex = 0
            return False

    def stopRun(self):
        try:
            self.data.uploadFlag = 0
            self.data.gcodeIndex = 0
            self.data.quick_queue.put("!")
            with self.data.gcode_queue.mutex:
                self.data.gcode_queue.queue.clear()
            #TODO: app.onUploadFlagChange(self.stopRun, 0)
            print("Gcode Stopped")
            return True
        except:
            return False

    def moveToDefault(self):
        try:
            chainLength = self.data.config.getValue('Advanced Settings', 'chainExtendLength')
            self.data.gcode_queue.put("G90 ")
            self.data.gcode_queue.put("B09 R"+str(chainLength)+" L"+str(chainLength)+" ")
            self.data.gcode_queue.put("G91 ")
            return True
        except:
            return False

    def testMotors(self):
        try:
            self.data.gcode_queue.put("B04 ")
            return True
        except:
            return False

    def wipeEEPROM(self):
        try:
            self.data.gcode_queue.put("$RST=* ")
            timer = threading.Timer(6.0, self.data.gcode_queue.put('$$'))
            timer.start()
            return True
        except:
            return False

    def pauseRun(self):
        try:
            self.data.uploadFlag = 0
            print("Run Paused")
            return True
        except:
            return False

    def resumeRun(self):
        try:
            self.data.uploadFlag = 1
            self.data.quick_queue.put("~") #send cycle resume command to unpause the machine
            return True
        except:
            return False

    def returnToCenter(self):
        try:
            self.data.gcode_queue.put("G90  ")
            safeHeightMM = float(self.data.config.getValue('Maslow Settings', 'zAxisSafeHeight'))
            safeHeightInches = safeHeightMM / 24.5
            if self.data.units == "INCHES":
                self.data.gcode_queue.put("G00 Z" + '%.3f'%(safeHeightInches))
            else:
                self.data.gcode_queue.put("G00 Z" + str(safeHeightMM))
            self.data.gcode_queue.put("G00 X0.0 Y0.0 ")
            return True
        except:
            return False

    def clearGCode(self):
        try:
            self.data.gcodeFile = ""
            return True
        except:
            return False

    def moveGcodeZ(self, moves):
        try:
            dist = 0
            for index,zMove in enumerate(self.data.zMoves):
                if moves > 0 and zMove > self.data.gcodeIndex:
                    dist = self.data.zMoves[index+moves-1]-self.data.gcodeIndex
                    break
                if moves < 0 and zMove < self.data.gcodeIndex:
                    dist = self.data.zMoves[index+moves+1]-self.data.gcodeIndex
            if moveGcodeIndex(dist):
            #this command will continue on in the moveGcodeIndex "if"
                return True
            else:
                return False
        except:
            return False


    def moveGcodeIndex(self, dist):
        try:
            maxIndex = len(self.data.gcode)-1
            targetIndex = self.data.gcodeIndex + dist

            #print "targetIndex="+str(targetIndex)
            #check to see if we are still within the length of the file
            if maxIndex < 0:              #break if there is no data to read
                return
            elif targetIndex < 0:             #negative index not allowed
                self.data.gcodeIndex = 0
            elif targetIndex > maxIndex:    #reading past the end of the file is not allowed
                self.data.gcodeIndex = maxIndex
            else:
                self.data.gcodeIndex = targetIndex
            gCodeLine = self.data.gcode[self.data.gcodeIndex]
            #print self.data.gcode
            #print "gcodeIndex="+str(self.data.gcodeIndex)+", gCodeLine:"+gCodeLine
            xTarget = 0
            yTarget = 0

            try:
                x = re.search("X(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
                if x:
                    xTarget = float(x.groups()[0])
                    app.previousPosX = xTarget
                else:
                    xTarget = app.previousPosX

                y = re.search("Y(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
                #print y
                if y:
                    yTarget = float(y.groups()[0])
                    app.previousPosY = yTarget
                else:
                    yTarget = app.previousPosY
                #self.gcodecanvas.positionIndicator.setPos(xTarget,yTarget,self.data.units)
                #print "xTarget:"+str(xTarget)+", yTarget:"+str(yTarget)
                position = {'xval':xTarget,'yval':yTarget,'zval':self.data.zval}
                socketio.emit('positionMessage', {'data':json.dumps(position) }, namespace='/MaslowCNC')
            except:
                print("Unable to update position for new gcode line")
                return False
            return True
        except:
            return False


    def move(self,direction,distToMove):
        try:
            if (direction=='upLeft'):
                self.data.gcode_queue.put("G91 G00 X" + str(-1.0*distToMove) + " Y" + str(distToMove) + " G90 ")
            elif (direction=='up'):
                self.data.gcode_queue.put("G91 G00 Y" + str(distToMove) + " G90 ")
            elif (direction=='upRight'):
                self.data.gcode_queue.put("G91 G00 X" + str(distToMove) + " Y" + str(distToMove) + " G90 ")
            elif (direction=='left'):
                self.data.gcode_queue.put("G91 G00 X" + str(-1.0*distToMove) + " G90 ")
            elif (direction=='right'):
                self.data.gcode_queue.put("G91 G00 X" + str(distToMove) + " G90 ")
            elif (direction=='downLeft'):
                self.data.gcode_queue.put("G91 G00 X" + str(-1.0*distToMove) + " Y" + str(-1.0*distToMove) + " G90 ")
            elif (direction=='down'):
                self.data.gcode_queue.put("G91 G00 Y" + str(-1.0*distToMove) + " G90 ")
            elif (direction=='downRight'):
                self.data.gcode_queue.put("G91 G00 X" + str(distToMove) + " Y" + str(-1.0*distToMove) + " G90 ")
            return True
        except:
            return False


    def moveZ(self, distToMoveZ):
        try:
            distToMoveZ = float(msg['data']['distToMoveZ'])
            self.data.config.setValue("Computed Settings", 'distToMoveZ',distToMoveZ)
            unitsZ = self.data.config.getValue('Computed Settings', 'unitsZ')
            if unitsZ == "MM":
                self.data.gcode_queue.put('G21 ')
            else:
                self.data.gcode_queue.put('G20 ')
            if (msg['data']['direction']=='raise'):
                self.data.gcode_queue.put("G91 G00 Z" + str(float(distToMoveZ)) + " G90 ")
            elif (msg['data']['direction']=='lower'):
                self.data.gcode_queue.put("G91 G00 Z" + str(-1.0*float(distToMoveZ)) + " G90 ")
            units = self.data.config.getValue('Computed Settings', 'units')
            if units == "MM":
                self.data.gcode_queue.put('G21 ')
            else:
                self.data.gcode_queue.put('G20 ')
            return True
        except:
            return False

    def updateSetting(self, setting, value):
        try:
            if (setting=='toInches'):
                self.data.units = "INCHES"
                self.data.config.setValue("Computed Settings", 'units',self.data.units)
                scaleFactor = 1.0
                self.data.gcodeShift = [self.data.xval/scaleFactor,self.data.yval/scaleFactor]
                self.data.tolerance = 0.020
                self.data.gcode_queue.put('G20 ')
                self.data.config.setValue("Computed Settings", 'distToMove',value)
            elif (setting=='toMM'):
                self.data.units = "MM"
                self.data.config.setValue("Computed Settings", 'units',self.data.units)
                scaleFactor = 25.4
                self.data.gcodeShift = [self.data.xval/scaleFactor,self.data.yval/scaleFactor]
                self.data.tolerance = 0.5
                self.data.gcode_queue.put('G21')
                self.data.config.setValue("Computed Settings", 'distToMove',value)
            elif (setting=='toInchesZ'):
                self.data.units = "INCHES"
                self.data.config.setValue("Computed Settings", 'unitsZ',self.data.units)
                self.data.config.setValue("Computed Settings", 'distToMoveZ',value)
            elif (setting=='toMMZ'):
                self.data.units = "MM"
                self.data.config.setValue("Computed Settings", 'unitsZ',self.data.units)
                self.data.config.setValue("Computed Settings", 'distToMoveZ',value)
            return True
        except:
            return False


    def setSprockets(self, sprocket, degrees):
        try:
            degValue = round(float(self.data.config.getValue('Advanced Settings',"gearTeeth"))*float(self.data.config.getValue('Advanced Settings',"chainPitch"))/360.0*degrees,4);
            self.data.gcode_queue.put("G91 ")
            if self.data.config.getValue('Advanced Settings', 'chainOverSprocket') == 'Top':
                self.data.gcode_queue.put("B09 L"+str(degValue)+" ")
            else:
                self.data.gcode_queue.put("B09 L-"+str(degValue)+" ")
            self.data.gcode_queue.put("G90 ")
            return True
        except:
            return False


    def setVerticalAutomatic(self):
        #set the call back for the measurement
        try:
            self.data.measureRequest = self.getLeftChainLength
            #request a measurement
            self.data.gcode_queue.put("B10 L")
            return True
        except:
            return False

    def getLeftChainLength(self, dist):
        self.leftChainLength = dist
        #set the call back for the measurement
        self.data.measureRequest = self.getRightChainLength
        #request a measurement
        self.data.gcode_queue.put("B10 R")

    def getRightChainLength(self, dist):
        self.rightChainLength = dist
        self.moveToVertical()

    def moveToVertical(self):
        #print "Current chain lengths:"
        #print self.leftChainLength
        #print self.rightChainLength

        chainPitch = float(self.data.config.get('Advanced Settings', 'chainPitch'))
        gearTeeth  = float(self.data.config.get('Advanced Settings', 'gearTeeth'))

        distPerRotation = chainPitch*gearTeeth

        #print "Rotations remainder:"
        distL = (-1*(self.leftChainLength%distPerRotation))
        distR = (-1*(self.rightChainLength%distPerRotation))

        #print distL
        #print distR

        self.data.gcode_queue.put("G91 ")
        self.data.gcode_queue.put("B09 L"+str(distL)+" ")
        self.data.gcode_queue.put("B09 R"+str(distR)+" ")
        self.data.gcode_queue.put("G90 ")

    def setSprocketsZero(self):
        #mark that the sprockets are straight up
        try:
            self.data.gcode_queue.put("B06 L0 R0 ");
            return True
        except:
            return False
