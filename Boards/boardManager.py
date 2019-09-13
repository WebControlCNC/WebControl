from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from Boards.boards import Board
import math
import base64
import numpy as np
from scipy.spatial import ConvexHull, convex_hull_plot_2d

class BoardManager(MakesmithInitFuncs):
    currentBoard = None

    def __init__(self):
        # can't do much because data hasn't been initialized yet
        pass

    def initializeNewBoard(self):
        self.currentBoard = Board()
        bedWidth = round(float(self.data.config.getValue("Maslow Settings", "bedWidth"))/25.4,2);
        bedHeight = round(float(self.data.config.getValue("Maslow Settings", "bedHeight"))/25.4,2);

        self.currentBoard.updateBoardInfo("-", "-", bedHeight, bedWidth, 0.75, 0, 0, "inches")
        self.currentBoard.compressCutData()

    def getCurrentBoard(self):
        return self.currentBoard

    def getCurrentBoardFilename(self):
        return self.currentBoard.boardFilename

    def editBoard(self, result):
        #try:
        if self.currentBoard.updateBoardInfo(result["boardID"], result["material"], result["height"], result["width"], result["thickness"], result["centerX"], result["centerY"], result["units"]):
            self.data.ui_queue1.put("Action", "boardUpdate", "")
            return True
        else:
            return False
        #except Exception as e:
        #    self.data.console_queue.put(str(e))
        #    return False

    def saveBoard(self, fileName, directory):
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
        if fileName is "":  # Blank the g-code if we're loading "nothing"
            return False
        try:
            file = open(fileName, "r")
            print(fileName)
            lines = file.readlines()
            self.currentBoard.updateBoardInfoJSON(lines[0])
            if (len(lines)>1):
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

    ''' 
    def processGCode1(self):
        board = self.currentBoard
        points = self.data.gcodeFile.getLinePoints()
        cutPoints = [False for i in range(48*96)]
        for line in points:
            if line[0]>=-48 and line[0]<=48 and line[1]>=-24 and line[1]<=24:

                cutPoints[int(line[0])+48+(int(line[1])+24)*96] = True
        print(cutPoints)
        self.currentBoard.updateCutPoints2(cutPoints)
        self.data.ui_queue1.put("Action", "boardUpdate", "")
        return True
    '''
    def processGCode(self):
        boardWidth = self.currentBoard.width
        boardHeight = self.currentBoard.height
        boardLeftX = self.currentBoard.centerX - boardWidth/2
        boardRightX = self.currentBoard.centerX + boardWidth / 2
        boardTopY = self.currentBoard.centerY + boardWidth/2
        boardBottomY = self.currentBoard.centerY - boardWidth / 2

        pointsX = math.ceil(boardWidth)
        pointsY = math.ceil(boardHeight)
        offsetX = pointsX / 2 - self.currentBoard.centerX
        offsetY = pointsY / 2 - self.currentBoard.centerY

        cutPoints = [False for i in range( pointsX * pointsY )]

        for line in self.data.gcodeFile.line3D:
            if line.type == "circle":
                if line.points[0][0] >= boardLeftX and line.points[0][0] <= boardRightX and line.points[0][1] >= boardBottomY and line.points[0][1] <= boardTopY and line.points[0][2] < 0:
                    pointx = self.constrain(round(line.points[0][0] + offsetX), 0, pointsX)
                    pointy = self.constrain(round(line.points[0][1] + offsetY), 0, pointsY)
                    cutPoints[pointx + pointy * pointsX] = True
                    #cutPoints[int(line.points[0][0] + offsetX) + int(line.points[0][1] + offsetY) * pointsX] = True
            else:
                for x in range(len(line.points)):
                    if x != len(line.points)-1:
                        x0 = line.points[x][0]
                        y0 = line.points[x][1]
                        z0 = line.points[x][2]

                        x1 = line.points[x+1][0]
                        y1 = line.points[x+1][1]
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
                                if line.points[x][0] >= boardLeftX and line.points[x][0] <= boardRightX and line.points[x][1] >= boardBottomY and line.points[x][1] <= boardTopY:
                                    pointx = self.constrain(round(line.points[x][0] + offsetX), 0, pointsX)
                                    pointy = self.constrain(round(line.points[x][1] + offsetY), 0, pointsY)
                                    cutPoints[pointx + pointy * pointsX] = True
                            if line.points[x+1][2] < 0:
                                if line.points[x+1][0] >= boardLeftX and line.points[x+1][0] <= boardRightX and line.points[x+1][1] >= boardBottomY and line.points[x+1][1] <= boardTopY:
                                    pointx = self.constrain(round(line.points[x+1][0] + offsetX), 0, pointsX)
                                    pointy = self.constrain(round(line.points[x+1][1] + offsetY), 0, pointsY)
                                    cutPoints[pointx + pointy * pointsX] = True


                    else:
                        if line.points[x][2] < 0:
                            if line.points[x][0] >= boardLeftX and line.points[x][0] <= boardRightX and line.points[x][1] >= boardBottomY and line.points[x][1] <= boardTopY:
                                pointx = self.constrain(round(line.points[x][0] + offsetX), 0, pointsX)
                                pointy = self.constrain(round(line.points[x][1] + offsetY), 0, pointsY)
                                cutPoints[pointx + pointy * pointsX] = True

        self.currentBoard.updateCutPoints(cutPoints)
        self.data.ui_queue1.put("Action", "boardUpdate", "")
        return True

    def clearBoard(self):
        self.currentBoard.clearCutPoints()
        self.data.ui_queue1.put("Action", "boardUpdate", "")
        return True

    def constrain(self, value, lower, upper):
        if value < lower:
            return lower
        if value > upper-1:
            return upper-1
        return value

    def trimBoard(self, result):
        trimTop = round(float(result["trimTop"]),3)
        trimBottom = round(float(result["trimBottom"]),3)
        trimLeft = round(float(result["trimLeft"]),3)
        trimRight = round(float(result["trimRight"]),3)
        retval = self.currentBoard.trimBoard(trimTop, trimBottom, trimLeft, trimRight)
        self.data.ui_queue1.put("Action", "boardUpdate", "")
        return retval

    '''
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


