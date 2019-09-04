from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from Boards.boards import Board
import numpy as np
from scipy.spatial import ConvexHull, convex_hull_plot_2d

class BoardManager(MakesmithInitFuncs):
    currentBoard = None

    def __init__(self):
        # can't do much because data hasn't been initialized yet
        pass

    def initializeNewBoard(self):
        self.currentBoard = Board()

    def getCurrentBoard(self):
        return self.currentBoard

    def editBoard(self, result):
        #try:
            if self.currentBoard.updateBoardInfo(result["boardID"], result["material"], result["height"], result["width"], result["thickness"], result["centerX"], result["centerY"]):
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
            boardData = self.currentBoard.getBoardInfoJSON()
            file.write(boardData+'\n')
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



