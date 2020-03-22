from DataStructures.makesmithInitFuncs import MakesmithInitFuncs

import sys
import threading
import json
import re
import math
import gzip
import io


class Line:
    def __init__(self):
        self.points = []
        self.color = None
        self.dashed = False
        self.type = None
        self.radius = None
        self.command = None


class GCodeFile(MakesmithInitFuncs):
    isChanged = False
    canvasScaleFactor = 1  # scale from mm to pixels
    INCHES = 1.0
    MILLIMETERS = 1.0/25.4

    xPosition = 0
    yPosition = 0
    zPosition = 0
    truncate = -1 #do this to truncate after shift of home position

    lineNumber = 0  # the line number currently being processed

    absoluteFlag = 0

    prependString = "G01 "

    maxNumberOfLinesToRead = 300000

    filename = ""
    line3D = []
    '''
    prependString is defined here so it can be persistent across each 'moveOneLine'.  That way, if a gcode line
    does not contain a valid gcode, it uses the previous line's gcode.  Thanks to @amantalion for discovering the
    glitch.  https://github.com/madgrizzle/WebControl/issues/78
    '''
    prependString = ""


    def serializeGCode3D(self):
        sendStr = json.dumps([ob.__dict__ for ob in self.data.gcodeFile.line3D])
        return sendStr

    def saveFile(self, fileName, directory):
        if fileName is "":  # Blank the g-code if we're loading "nothing"
            return False
        if directory is "":
            return False
        try:
            homeX = float(self.data.config.getValue("Advanced Settings", "homeX"))
            homeY = float(self.data.config.getValue("Advanced Settings", "homeY"))
            fileToWrite = directory + "/" + fileName
            gfile = open(fileToWrite, "w+")
            print(fileToWrite)
            for line in self.data.gcode:
                gfile.write(line+'\n')
            #gfile = open(directory+fileName, "w+")
            #gfile.writelines(map(lambda s: s+ '\n', self.data.gcode))
            print("Closing File")
            gfile.close()
        except Exception as e:
            self.data.console_queue.put(str(e))
            self.data.console_queue.put("Gcode File Error")
            self.data.ui_queue1.put("Alert", "Alert", "Cannot save gcode file.")
            self.data.gcodeFile.filename = ""
            return False
        return True



    def loadUpdateFile(self, gcode=""):
        print("At loadUpdateFile")
        gcodeLoad = False
        if gcode=="":
            gcodeLoad = True
        if self.data.units == "MM":
            self.canvasScaleFactor = self.MILLIMETERS
        else:
            self.canvasScaleFactor = self.INCHES

        if gcode == "":
            filename = self.data.gcodeFile.filename
            self.data.gcodeShift[0] = round(float(self.data.config.getValue("Advanced Settings", "homeX")),4)
            self.data.gcodeShift[1] = round(float(self.data.config.getValue("Advanced Settings", "homeY")),4)

            del self.line3D[:]
            if filename is "":  # Blank the g-code if we're loading "nothing"
                self.data.gcode = ""
                return False

            try:
                filterfile = open(filename, "r")
            except Exception as e:
                self.data.console_queue.put(str(e))
                self.data.console_queue.put("Gcode File Error")
                self.data.ui_queue1.put("Alert", "Alert", "Cannot open gcode file.")
                self.data.gcodeFile.filename = ""
                return False
            rawfilters = filterfile.read()
            filterfile.close()  # closes the filter save file
        else:
            del self.line3D[:]
            rawfilters = gcode

        try:
            filtersparsed = rawfilters #get rid of this if above is uncommented)
            '''
            filtersparsed = re.sub(
                r";([^\n]*)\n", "\n", filtersparsed
            )  # replace standard ; initiated gcode comments with newline
            '''
            #print(filtersparsed)
            filtersparsed = re.sub(r"\n\n", "\n", filtersparsed)  # removes blank lines
            filtersparsed = re.sub(
                r"([0-9])([GXYZIJFTM]) *", "\\1 \\2", filtersparsed
            )  # put spaces between gcodes
            filtersparsed = re.sub(r"  +", " ", filtersparsed)  # condense space runs
            value = self.data.config.getValue("Advanced Settings", "truncate")

            if value == 1:
                digits = self.data.config.getValue("Advanced Settings", "digits")
                filtersparsed = re.sub(
                    r"([+-]?\d*\.\d{1," + digits + "})(\d*)", r"\g<1>", filtersparsed
                )  # truncates all long floats to 4 decimal places, leaves shorter floats
                self.truncate = int(digits)
            else:
                self.truncate = -1
            filtersparsed = re.split(
                "\n", filtersparsed
            )  # splits the gcode into elements to be added to the list
            filtersparsed = [x.lstrip() for x in filtersparsed] # remove leading spaces
            filtersparsed = [
                x + " " for x in filtersparsed
            ]  # adds a space to the end of each line
            filtersparsed = [x.replace("X ", "X") for x in filtersparsed]
            filtersparsed = [x.replace("Y ", "Y") for x in filtersparsed]
            filtersparsed = [x.replace("Z ", "Z") for x in filtersparsed]
            filtersparsed = [x.replace("I ", "I") for x in filtersparsed]
            filtersparsed = [x.replace("J ", "J") for x in filtersparsed]
            filtersparsed = [x.replace("F ", "F") for x in filtersparsed]
            self.data.gcode = "[]"
            self.data.gcode = filtersparsed



            # Find gcode indicies of z moves
            self.data.zMoves = [0]
            zList = []
            for index, line in enumerate(self.data.gcode):
                filtersparsed = re.sub(r'\(([^)]*)\)', '', line)  # replace mach3 style gcode comments with newline
                line = re.sub(r';([^\n]*)?', '\n',filtersparsed)  # replace standard ; initiated gcode comments with newline
                if not line.isspace(): # if all spaces, don't send.  likely a comment. #if line.find("(") == -1:
                    if line.find("G20") != -1:
                        self.data.tolerance = 0.020
                        self.data.config.setValue("Computed Settings", "tolerance", self.data.tolerance)
                    if line.find("G21") != -1:
                        self.data.tolerance = 0.50
                        self.data.config.setValue("Computed Settings", "tolerance", self.data.tolerance)
                    z = re.search("Z(?=.)([+-]?([0-9]*)(\.([0-9]+))?)", line)
                    if z:
                        zList.append(z)
                        if len(zList) > 1:
                            if not self.isClose(
                                float(zList[-1].groups()[0]), float(zList[-2].groups()[0])
                            ):
                                self.data.zMoves.append(index)  # - 1)
                        else:
                            self.data.zMoves.append(index)
        except Exception as e:
            self.data.console_queue.put(str(e))
            self.data.console_queue.put("Gcode File Error")
            self.data.ui_queue1.put("Alert", "Alert", "Cannot open gcode file.")
            self.data.gcodeFile.filename = ""
            return False
        self.updateGcode()
        self.data.gcodeFile.isChanged = True
        self.data.actions.sendGCodePositionUpdate(self.data.gcodeIndex, recalculate=True)
        return True

    def isClose(self, a, b):
        return abs(a - b) <= self.data.tolerance

    '''def addPoint(self, x, y):
        """
        Add a point to the line currently being plotted
        """
        self.line[-1].points.append(
            #(x * self.canvasScaleFactor, y * self.canvasScaleFactor * -1.0)
            (x , y * -1.0)
        )
    '''

    def addPoint3D(self, x, y, z):
        """
        Add a point to the line currently being plotted
        """
        self.line3D[-1].points.append(
            (x, y, z)
        )


    def isNotReallyClose(self, x0, x1):
        if abs(x0 - x1) > 0.0001:
            return True
        else:
            return False

    def drawLine(self, gCodeLine, command):
        """

        drawLine draws a line using the previous command as the start point and the xy coordinates
        from the current command as the end point. The line is styled based on the command to allow
        visually differentiating between normal and rapid moves. If the z-axis depth is changed a
        circle is placed at the location of the depth change to alert the user.

        """

        if True:
            xTarget = self.xPosition
            yTarget = self.yPosition
            zTarget = self.zPosition

            x = re.search("X(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if x:
                xTarget = float(x.groups()[0]) * self.canvasScaleFactor
                if self.absoluteFlag == 1:
                    xTarget = self.xPosition + xTarget

            y = re.search("Y(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if y:
                yTarget = float(y.groups()[0]) * self.canvasScaleFactor
                if self.absoluteFlag == 1:
                    yTarget = self.yPosition + yTarget
            z = re.search("Z(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if z:
                zTarget = float(z.groups()[0]) * self.canvasScaleFactor

            if self.isNotReallyClose(self.xPosition, xTarget) or self.isNotReallyClose(
                self.yPosition, yTarget
            ):

                if command == "G00":
                    # draw a dashed line

                    self.line3D.append(Line())  # points = (), width = 1, group = 'gcode')
                    self.line3D[-1].type = "line"
                    self.line3D[-1].command = None
                    self.line3D[-1].dashed = True
                    self.addPoint3D(self.xPosition, self.yPosition, self.zPosition)
                    self.addPoint3D(xTarget, yTarget, zTarget)

                else:
                    if (len(self.line3D) == 0 or self.line3D[-1].dashed or self.line3D[-1].type != "line"):  #test123
                        self.line3D.append( Line() )
                        self.line3D[-1].type = "line"
                        self.line3D[-1].command = None
                        self.addPoint3D(self.xPosition, self.yPosition, self.zPosition)
                        self.line3D[-1].dashed = False


                    self.addPoint3D(xTarget, yTarget, zTarget)

            # If the zposition has changed, add indicators
            tol = 0.05  # Acceptable error in mm
            if abs(zTarget - self.zPosition) >= tol:
                if True:
                    if zTarget - self.zPosition > 0:
                        # Color(0, 1, 0)
                        radius = 2
                    else:
                        # Color(1, 0, 0)
                        radius = 1

                    self.line3D.append(Line())  # points = (), width = 1, group = 'gcode')
                    self.line3D[-1].type = "circle"
                    self.line3D[-1].command = None
                    self.addPoint3D(self.xPosition, self.yPosition, self.zPosition)
                    self.addPoint3D(radius, 0, zTarget)  #targetOut
                    self.line3D[-1].dashed = False

            self.xPosition = xTarget
            self.yPosition = yTarget
            self.zPosition = zTarget

    def drawMCommand(self, mString):
        """

        drawToolChange draws a circle indicating a tool change.

        """
        #print(mString)
        code = self.getMCommand(mString)
        #print(code)
        #code = mString[1:2] #just the number?
        circleSize = 0
        arg = 0
        command = None
        if code == 3:
            arg = self.getSpindleSpeed(mString)
            if arg == 0:
                circleSize = 5
                command = "SpindleOff"
            else:
                circleSize = 3
                command = "SpindleOnCW"
        if code == 4:
            arg = self.getSpindleSpeed(mString)
            if arg == 0:
                circleSize = 5
                command = "SpindleOff"
            else:
                circleSize = 4
                command = "SpindleOnCCW"
        if code == 5: # Spindle Stop
            circleSize = 5
            command = "SpindleOff"
        if code == 6:  # Tool Change
            circleSize = 6
            command = "ToolChange"
            arg = self.currentDrawTool

        self.line3D.append(Line())  # points = (), width = 1, group = 'gcode')
        self.line3D[-1].type = "circle"
        self.line3D[-1].command = command
        self.addPoint3D(self.xPosition, self.yPosition, self.zPosition)
        self.addPoint3D(circleSize, arg, self.zPosition)
        self.line3D[-1].dashed = False

    def getSpindleSpeed(self, mString):
        code = mString[mString.find("S")+1:]
        if code!="":
            return float(code)
        else:
            return 0

    def getToolNumber(self, mString):
        code0 = mString.find("T")
        code1 = mString.find("M")
        code = mString[code0+1:code1-code0]
        #print(mString)
        #print(code)
        if code!="":
            return int(code)
        else:
            return 0

    def getMCommand(self, mString):
        code0 = mString.find("M")
        code1 = mString.find(" ", code0)
        if code1 == -1:
            code1 = mString.find("T", code0)
            if code1 == -1:
                code = mString[code0+1:]
        else:
            code = mString[code0+1: code1-code0]
        if code!="":
            return int(code)
        else:
            return 0


    def drawArc(self, gCodeLine, command):
        """

        drawArc draws an arc using the previous command as the start point, the xy coordinates from
        the current command as the end point, and the ij coordinates from the current command as the
        circle center. Clockwise or counter-clockwise travel is based on the command.

        """

        if True:
            xTarget = self.xPosition
            yTarget = self.yPosition
            zTarget = self.zPosition
            iTarget = 0
            jTarget = 0

            x = re.search("X(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if x:
                xTarget = float(x.groups()[0]) * self.canvasScaleFactor
            y = re.search("Y(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if y:
                yTarget = float(y.groups()[0]) * self.canvasScaleFactor
            i = re.search("I(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if i:
                iTarget = float(i.groups()[0]) * self.canvasScaleFactor
            j = re.search("J(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if j:
                jTarget = float(j.groups()[0]) * self.canvasScaleFactor
            z = re.search("Z(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
            if z:
                zTarget = float(z.groups()[0]) * self.canvasScaleFactor

            radius = math.sqrt(iTarget ** 2 + jTarget ** 2)
            centerX = self.xPosition + iTarget
            centerY = self.yPosition + jTarget

            angle1 = math.atan2(self.yPosition - centerY, self.xPosition - centerX)
            angle2 = math.atan2(yTarget - centerY, xTarget - centerX)

            # atan2 returns results from -pi to +pi and we want results from 0 - 2pi
            if angle1 < 0:
                angle1 = angle1 + 2 * math.pi
            if angle2 < 0:
                angle2 = angle2 + 2 * math.pi

            # take into account command G1 or G2
            if int(command[1:]) == 2:
                if angle1 < angle2:
                    angle1 = angle1 + 2 * math.pi
                direction = -1
            else:
                if angle2 < angle1:
                    angle2 = angle2 + 2 * math.pi
                direction = 1

            arcLen = abs(angle1 - angle2)
            if abs(angle1 - angle2) == 0:
                arcLen = 6.28313530718

            if (
                len(self.line3D) == 0
                or self.line3D[-1].dashed
                or self.line3D[-1].type != "line"
            ):
                self.line3D.append(Line())  # points = (), width = 1, group = 'gcode')
                self.addPoint3D(self.xPosition, self.yPosition, self.zPosition)
                self.line3D[-1].type = "line"
                self.line3D[-1].dashed = False
            zStep = (zTarget - self.zPosition)/math.fabs(arcLen/(.1*direction))
            i = 0
            counter = 0
            while abs(i) < arcLen:
                xPosOnLine = centerX + radius * math.cos(angle1 + i)
                yPosOnLine = centerY + radius * math.sin(angle1 + i)
                zPosOnLine = self.zPosition + zStep*counter
                self.addPoint3D(xPosOnLine, yPosOnLine, zPosOnLine)
                i = i + 0.1 * direction  # this is going to need to be a direction
                counter+=1

            self.addPoint3D(xTarget, yTarget, zTarget)

            self.xPosition = xTarget
            self.yPosition = yTarget
            self.zPosition = zTarget

    def clearGcode(self):
        """

        clearGcode deletes the lines and arcs corresponding to gcode commands from the canvas.

        """

        del self.line3D[:]

    def clearGcodeFile(self):
        """

        clearGcodeFile deletes the lines and arcs and the file

        """

        del self.line3D[:]

        self.data.gcode = []
        self.updateGcode()
        self.data.gcodeFile.isChanged = True




    def moveLine(self, gCodeLine):

        originalLine = gCodeLine
        shiftX = self.data.gcodeShift[0]
        shiftY = self.data.gcodeShift[1]
        if len(gCodeLine) > 0:
            if gCodeLine[0] == '(' or gCodeLine[0] == ';':
                return originalLine
        #next check for comment after line and if exist, split on first occurrence and retain the comment portion
        findexA = gCodeLine.find('(')
        findexB = gCodeLine.find(';')
        #check to see which came first.. who knows, maybe someone used a ; within a (
        if findexA != -1 and findexA < findexB:
            findex = findexA
        else:
            findex = findexB
        comment = ""
        if findex != -1:
            #found comment at findex
            comment = gCodeLine[findex:]
            #print("comment:"+comment)
            gCodeLine = gCodeLine[:findex]

        #This test should always pass so taking it out
        #if gCodeLine.find("(") == -1 and gCodeLine.find(";") == -1:
        if True:
            try:
                gCodeLine = gCodeLine.upper() + " "
                x = re.search("X(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
                if x:
                    q = abs(float(x.groups()[0])+shiftX)
                    if self.truncate >= 0:
                        q = str(round(q, self.truncate))
                    else:
                        q = str(q)

                    eNtnX = re.sub("\-?\d\.|\d*e-","",q,)  # strip off everything but the decimal part or e-notation exponent

                    e = re.search(".*e-", q)

                    if e:
                        fmtX = "%0.{0}f".format(eNtnX)
                    else:
                        fmtX = "%0.{0}f".format(len(eNtnX))
                    gCodeLine = (
                        gCodeLine[0 : x.start() + 1]
                        + (fmtX % (float(x.groups()[0]) + shiftX))
                        + gCodeLine[x.end() :]
                    )

                y = re.search("Y(?=.)(([ ]*)?[+-]?([0-9]*)(\.([0-9]+))?)", gCodeLine)
                if y:
                    q = abs(float(y.groups()[0])+shiftY)
                    if self.truncate >= 0:
                        q = str(round(q, self.truncate))
                    else:
                        q = str(q)

                    eNtnY = re.sub("\-?\d\.|\d*e-", "", q, )

                    e = re.search(".*e-", q )

                    if e:
                        fmtY = "%0.{0}f".format(eNtnY)
                    else:
                        fmtY = "%0.{0}f".format(len(eNtnY))
                    gCodeLine = (
                        gCodeLine[0 : y.start() + 1]
                        + (fmtY % (float(y.groups()[0]) + shiftY))
                        + gCodeLine[y.end() :]
                    )
                #now, put any comment back.
                gCodeLine = gCodeLine+comment
                return gCodeLine
            except ValueError:
                self.data.console_queue.put("line could not be moved:")
                self.data.console_queue.put(originalLine)
                return originalLine
        return originalLine

    def loadNextLine(self):
        """

        Load the next line of gcode

        """

        try:
            fullString = self.data.gcode[self.lineNumber]
        except:
            return  # we have reached the end of the file

        filtersparsed = re.sub(r'\(([^)]*)\)', '\n', fullString)  # replace mach3 style gcode comments with newline
        #fullString = re.sub(r';([^\n]*)\n', '\n', filtersparsed)  # replace standard ; initiated gcode comments with newline
        fullString = re.sub(r';([^\n]*)?', '\n', filtersparsed)  # replace standard ; initiated gcode comments with newline
        #print("fullString:"+fullString)
        # if the line contains multiple gcode commands split them and execute them individually
        listOfLines = fullString.split("G")
        if len(listOfLines) > 1:  # if the line contains at least one 'G'
            for line in listOfLines:
                if len(line) > 0:  # If the line is not blank
                    self.updateOneLine("G" + line)  # Draw it
        else:
            self.updateOneLine(fullString)

        self.lineNumber = self.lineNumber + 1

    def updateOneLine(self, fullString):
        """

        Draw the next line on the gcode canvas

        """

        validPrefixList = [
            "G00",
            "G0 ",
            "G1 ",
            "G01",
            "G2 ",
            "G02",
            "G3 ",
            "G03",
            "G17",
        ]

        fullString = (
            fullString + " "
        )  # ensures that there is a space at the end of the line
        # find 'G' anywhere in string

        gString = fullString[fullString.find("G") : fullString.find("G") + 3]

        if gString in validPrefixList:
            self.prependString = gString

        if (
            fullString.find("G") == -1
        ):  # this adds the gcode operator if it is omitted by the program
            fullString = self.prependString + " " + fullString
            gString = self.prependString

        # print gString
        if gString == "G00" or gString == "G0 ":
            self.drawLine(fullString, "G00")

        if gString == "G01" or gString == "G1 ":
            self.drawLine(fullString, "G01")

        if gString == "G02" or gString == "G2 ":
            self.drawArc(fullString, "G02")

        if gString == "G03" or gString == "G3 ":
            self.drawArc(fullString, "G03")

        if gString == "G17":
            # Take no action, XY coordinate plane is the default
            pass

        if gString == "G18":
            self.data.console_queue.put("G18 not supported")

        if gString == "G20":
            #print(fullString)
            if self.data.units != "INCHES":
                self.data.actions.updateSetting("toInches", 0, True) # value = doesn't matter
            self.canvasScaleFactor = self.INCHES
            self.data.gcodeFileUnits = "INCHES"

        if gString == "G21":
           # print(fullString)
            if self.data.units != "MM":
                self.data.actions.updateSetting("toMM", 0, True) #value = doesn't matter
            self.data.gcodeFileUnits = "MM"
            self.canvasScaleFactor = self.MILLIMETERS

        if gString == "G90":
            self.absoluteFlag = 0

        if gString == "G91":
            self.absoluteFlag = 1

        #tString = fullString[fullString.find("T") : fullString.find("T") + 2]
        tString = fullString[fullString.find("T") :]
        if tString.find("T") != -1:
            self.currentDrawTool = self.getToolNumber(tString)

        mString = fullString[fullString.find("M") : ]
        if mString.find("M") != -1:
            self.drawMCommand(mString)


    def callBackMechanism(self):
        """
        Call the loadNextLine function in background.
        """

        for _ in range(min(len(self.data.gcode), self.maxNumberOfLinesToRead)):
            self.loadNextLine()

        tstr = json.dumps([ob.__dict__ for ob in self.data.gcodeFile.line3D])
        out = io.BytesIO()
        with gzip.GzipFile(fileobj=out, mode="w") as f:
            f.write(tstr.encode())
        self.data.compressedGCode3D = out.getvalue()

        self.data.console_queue.put("uncompressed:"+str(len(tstr)))
        self.data.console_queue.put("compressed3D:"+str(len(self.data.compressedGCode3D)))


    def updateGcode(self):
        """
        updateGcode parses the gcode commands and calls the appropriate drawing function for the
        specified command.
        """
        # reset variables
        self.data.backgroundRedraw = False
        if (self.data.units=="INCHES"):
            scaleFactor = 1.0;
        else:
            scaleFactor = 1/25.4;
        #before, gcode shift = home X
        #old #self.xPosition = self.data.gcodeShift[0] * scaleFactor
        #old #self.yPosition = self.data.gcodeShift[1] * scaleFactor
        #self.xPosition = float(self.data.config.getValue("Advanced Settings", "homeX")) * scaleFactor #test123
        #self.yPosition = float(self.data.config.getValue("Advanced Settings", "homeY")) * scaleFactor #test123
        self.xPosition = 0
        self.yPosition = 0
        self.zPosition = 0

        self.prependString = "G00 "
        self.lineNumber = 0

        self.clearGcode()

        # Check to see if file is too large to load
        if len(self.data.gcode) > self.maxNumberOfLinesToRead:
            errorText = (
                "The current file contains "
                + str(len(self.data.gcode))
                + " lines of gcode.  Rendering all "
                + str(len(self.data.gcode))
                + " lines simultaneously may crash the program, therefore, only the first "
                + str(self.maxNumberOfLinesToRead)
                + "lines are shown here.  The complete program will cut if you choose to do so unless the home position is moved from (0,0)."
            )
            self.data.console_queue.put(errorText)
            self.data.ui_queue1.put("Alert", "Alert", errorText)


        th = threading.Thread(target=self.callBackMechanism)
        th.start()


    def getLinePoints(self):

        points = []
        for line in self.line3D:
            for point in line.points:
                if point[2]<0:
                    newPoint = [point[0],point[1]]
                    points.append(newPoint)
        return points
