from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from Boards.boards import Board
import math
import base64
import numpy as np
from scipy.spatial import ConvexHull, convex_hull_plot_2d

class BoardManager(MakesmithInitFuncs):
    '''
    This class implements the management of various boards (workpieces) that are tracked.
    Each board is stored as a separate file containing both description, dimensions, makeup of board as well
    as an array (1-inch resolution) of what parts of the board have been cut.
    '''
    currentBoard = None

    def __init__(self):
        # can't do much because data hasn't been initialized yet
        pass

    def initializeNewBoard(self):
        '''
        Create a new board and initialize it to the size of the bed.  Default to 0.75 inches thick
        :return:
        '''
        self.currentBoard = Board()
        bedWidth = round(float(self.data.config.getValue("Maslow Settings", "bedWidth"))/25.4, 2)
        bedHeight = round(float(self.data.config.getValue("Maslow Settings", "bedHeight"))/25.4, 2)

        self.currentBoard.updateBoardInfo("-", "-", bedHeight, bedWidth, 0.75, 0, 0, "inches")
        # this creates the necessary compressed data files to avoid None errors.
        self.currentBoard.compressCutData()

    def getCurrentBoard(self):
        '''
        Returns current board
        :return:
        '''
        return self.currentBoard

    def getCurrentBoardFilename(self):
        '''
        Returns current board filename
        :return:
        '''
        return self.currentBoard.boardFilename

    def editBoard(self, result):
        '''
        Updates the board information with data from the form.
        :param result:
        :return:
        '''
        try:
            if self.currentBoard.updateBoardInfo(result["boardID"], result["material"], result["height"],
                                                 result["width"], result["thickness"], result["centerX"],
                                                 result["centerY"], result["units"]):
                # send update to the UI clients
                self.data.ui_queue1.put("Action", "boardUpdate", "")
                return True
            else:
                return False
        except Exception as e:
            self.data.console_queue.put(str(e))
            return False

    def saveBoard(self, fileName, directory):
        '''
        Saves the board data.  File format is one line of board data in json format and one line of cut data in
        compressed and base64 encoded format.
        :param fileName: filename to use
        :param directory: directory to save file
        :return:
        '''
        if fileName is "":  # Blank the g-code if we're loading "nothing"
            return False
        if directory is "":
            return False
        try:
            fileToWrite = directory + "/" + fileName
            file = open(fileToWrite, "w+")
            print(fileToWrite)
            self.currentBoard.setFilename(fileName)
            boardData = self.currentBoard.getBoardInfoJSON()
            file.write(boardData+'\n')
            boardCutData = self.currentBoard.getCompressedCutData()
            boardCutData = base64.b64encode(boardCutData)
            boardCutData = boardCutData.decode('utf-8')
            file.write(boardCutData)
            file.write('\n')
            print("Closing File")
            file.close()
        except Exception as e:
            self.data.console_queue.put(str(e))
            self.data.console_queue.put("Board Save File Error")
            self.data.ui_queue1.put("Alert", "Alert", "Cannot save board.")
            return False
        return True

    def loadBoard(self, fileName):
        '''
        Load the board data.  File format is one line of board data in json format and one line of cut data in
        compressed and base64 encoded format.
        :param fileName: filename to load
        :param directory: directory to load file from
        :return:
        '''
        if fileName is "":  # Blank the g-code if we're loading "nothing"
            return False
        try:
            file = open(fileName, "r")
            print(fileName)
            lines = file.readlines()
            self.currentBoard.updateBoardInfoJSON(lines[0])
            # make sure got at least 2 lines...
            if len(lines) > 1:
                loadedCutData = base64.b64decode(lines[1].encode('utf-8'))
                self.currentBoard.updateCompressedCutData(loadedCutData)
            print("Closing File")
            file.close()
            self.data.ui_queue1.put("Action", "boardUpdate", "")
        except Exception as e:
            self.data.console_queue.put(str(e))
            self.data.console_queue.put("Board Open File Error")
            self.data.ui_queue1.put("Alert", "Alert", "Cannot open board.")
            return False
        return True

    def processGCode(self):
        '''
        Using the gcode in memory, mark the areas in the array that the gcode passes through at a height less than 0.
        :return:
        '''
        boardWidth = self.currentBoard.width
        boardHeight = self.currentBoard.height
        boardLeftX = self.currentBoard.centerX - boardWidth/2
        boardRightX = self.currentBoard.centerX + boardWidth / 2
        boardTopY = self.currentBoard.centerY + boardWidth/2
        boardBottomY = self.currentBoard.centerY - boardWidth / 2

        # calculate the extents of the array and its offset.
        pointsX = math.ceil(boardWidth)
        pointsY = math.ceil(boardHeight)
        offsetX = pointsX / 2 - self.currentBoard.centerX
        offsetY = pointsY / 2 - self.currentBoard.centerY

        homeX = self.data.gcodeShift[0]
        homeY = self.data.gcodeShift[1]

        # initialize an array
        cutPoints = [False for i in range( pointsX * pointsY )]

        # process gcode
        for line in self.data.gcodeFile.line3D:
            if line.type == "circle":
                if line.points[0][0] + homeX >= boardLeftX and line.points[0][0] + homeX <= boardRightX and line.points[0][1] + homeY >= boardBottomY and line.points[0][1] + homeY <= boardTopY and line.points[0][2] < 0:
                    pointx = self.constrain(round(line.points[0][0] + offsetX + homeX), 0, pointsX)
                    pointy = self.constrain(round(line.points[0][1] + offsetY + homeY), 0, pointsY)
                    cutPoints[pointx + pointy * pointsX] = True
                    #cutPoints[int(line.points[0][0] + offsetX) + int(line.points[0][1] + offsetY) * pointsX] = True
            else:
                for x in range(len(line.points)):
                    if x != len(line.points)-1:
                        x0 = line.points[x][0]+homeX
                        y0 = line.points[x][1]+homeY
                        z0 = line.points[x][2]

                        x1 = line.points[x+1][0]+homeX
                        y1 = line.points[x+1][1]+homeY
                        z1 = line.points[x+1][2]

                        lineLength = math.sqrt( (x0-x1) ** 2 + (y0-y1) ** 2 + (z0-z1) ** 2)
                        if lineLength > 0.25:
                            for l in range(int(lineLength*4)+1):
                                xa = x0 + (x1 - x0) / (lineLength * 4) * l
                                ya = y0 + (y1 - y0) / (lineLength * 4) * l
                                za = z0 + (z1 - z0) / (lineLength * 4) * l
                                if za < 0:
                                    if xa >= boardLeftX and xa <= boardRightX and ya >= boardBottomY and ya <= boardTopY:
                                        pointx = self.constrain(round(xa + offsetX), 0, pointsX)
                                        pointy = self.constrain(round(ya + offsetY), 0, pointsY)
                                        cutPoints[pointx + pointy * pointsX] = True
                                        #cutPoints[round(xa + offsetX) + round(ya + offsetY) * pointsX] = True

                        else:
                            if line.points[x][2] < 0:
                                if line.points[x][0] + homeX >= boardLeftX and line.points[x][0] + homeX <= boardRightX and line.points[x][1] + homeY >= boardBottomY and line.points[x][1] + homeX <= boardTopY:
                                    pointx = self.constrain(round(line.points[x][0] + offsetX + homeX), 0, pointsX)
                                    pointy = self.constrain(round(line.points[x][1] + offsetY + homeY), 0, pointsY)
                                    cutPoints[pointx + pointy * pointsX] = True
                            if line.points[x+1][2] < 0:
                                if line.points[x+1][0] + homeX >= boardLeftX and line.points[x+1][0] + homeX <= boardRightX and line.points[x+1][1] + homeY >= boardBottomY and line.points[x+1][1] + homeY <= boardTopY:
                                    pointx = self.constrain(round(line.points[x+1][0] + offsetX + homeX), 0, pointsX)
                                    pointy = self.constrain(round(line.points[x+1][1] + offsetY + homeY), 0, pointsY)
                                    cutPoints[pointx + pointy * pointsX] = True


                    else:
                        if line.points[x][2] < 0:
                            if line.points[x][0] + homeX >= boardLeftX and line.points[x][0] + homeX <= boardRightX and line.points[x][1] + homeY >= boardBottomY and line.points[x][1] + homeY <= boardTopY:
                                pointx = self.constrain(round(line.points[x][0] + offsetX + homeX), 0, pointsX)
                                pointy = self.constrain(round(line.points[x][1] + offsetY + homeY), 0, pointsY)
                                cutPoints[pointx + pointy * pointsX] = True

        # send this array to the current board for updating
        self.currentBoard.updateCutPoints(cutPoints)
        # update the UI clients.
        self.data.ui_queue1.put("Action", "boardUpdate", "")
        return True

    def clearBoard(self):
        '''
        Clear the current board cut data
        :return:
        '''
        self.currentBoard.clearCutPoints()
        # update the UI clients.
        self.data.ui_queue1.put("Action", "boardUpdate", "")
        return True

    def constrain(self, value, lower, upper):
        '''
        Helper routine to constrain values
        :param value: value to be constrained
        :param lower: lower limit
        :param upper: upper limit
        :return:
        '''
        if value < lower:
            return lower
        if value > upper-1:
            return upper-1
        return value

    def trimBoard(self, result):
        '''
        Processes message from form to trim the board cut data.
        :param result:
        :return:
        '''
        trimTop = round(float(result["trimTop"]), 3)
        trimBottom = round(float(result["trimBottom"]), 3)
        trimLeft = round(float(result["trimLeft"]), 3)
        trimRight = round(float(result["trimRight"]), 3)
        units = result["units"]
        retval = self.currentBoard.trimBoard(trimTop, trimBottom, trimLeft, trimRight, units)
        self.data.ui_queue1.put("Action", "boardUpdate", "")
        return retval

    '''
    old stuff not used anymore.. keeping it around for a bit
    # Todo: delete when done with
    def processGCode(self):
        #points = np.random.rand(30,2)
        points = self.data.gcodeFile.getLinePoints()
        #try:
        index = 0
        
        for line in points:
            #print(line)
            point = np.zeros(2)
            #print(point)
            point[0] = line[0]
            point[1] = line[1]
            #print(point)
            if index == 0:
                npoints = [point]
            else:
                npoints = np.append(npoints, [point], axis=0)
            index += 1
        #print(npoints)
        hull = ConvexHull(npoints)
        print("here0")
        cutPoints = []
        for vertex in hull.vertices:
            cutPoints.append([hull.points[vertex][0],hull.points[vertex][1],0])
        print("here1")
        self.currentBoard.updateCutPoints(cutPoints)
        self.data.ui_queue1.put("Action", "boardUpdate", "")
        #except Exception as e:
        #    self.data.console_queue.put(str(e))
        #    self.data.console_queue.put("Gcode Processing Error")
        #    self.data.ui_queue1.put("Alert", "Alert", "Cannot process gcode.")
        #    return False

        return True
    '''


