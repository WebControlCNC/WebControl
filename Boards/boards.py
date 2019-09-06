import json
import gzip
import io
import math


class Board():
    def __init__(self):
        # can't do much because data hasn't been initialized yet
        pass
    width = 0
    height = 0
    thickness = 0
    centerX = 0
    centerY = 0

    boardID = "Undefined"
    material = "Undefined"
    boardFilename = ""

    boardPoints = []
    cutPoints = []
    cutPoints2 = []
    pointsPerInch = 1

    compressedCutData = ""


    def updateBoardInfo(self, boardID, material, height, width, thickness, centerX, centerY, units):

        try:
            scale = 1
            if units == "mm":
                scale = 25.4
            self.width = round(float(width)/scale,2)
            self.height = round(float(height)/scale,2)
            self.thickness = round(float(thickness)/scale,2)
            self.centerX = round(float(centerX)/scale,2)
            self.centerY = round(float(centerY)/scale,2)
            self.boardID = boardID
            self.material = material
            return True
        except Exception as e:
            print(e)
            return False

    def updateCutPoints(self, data):
        pointsX = math.ceil(self.width)
        pointsY = math.ceil(self.height)

        if len(self.cutPoints) == 0:
            print("cutpoints = []")
            self.cutPoints = data
        else:
            for x in range(len(self.cutPoints)):
                if data[x] == True:
                    self.cutPoints[x] = True
        self.compressCutData()

    def setFilename(self, data):
        self.boardFilename = data

    '''
    def updateCutPointsOld(self, data):
        self.cutPoints = []
        line = []
        for points in data:
            line.append([points[0],points[1],0])
        self.cutPoints.append(line)
        self.compressCutData()
    '''

    def getPoints(self):
        return self.boardPoints

    def getCutPoints(self):
        return self.cutPoints

    def getCompressedCutData(self):
        return self.compressedCutData

    def getBoardInfoJSON(self):
        tstr = json.dumps({"width": self.width, "height": self.height, "thickness": self.thickness, "centerX": self.centerX, "centerY": self.centerY, "boardID":self.boardID, "material":self.material, "fileName":self.boardFilename})
        return tstr

    def updateBoardInfoJSON(self, data):
        boardData = json.loads(data)
        self.width = boardData["width"]
        self.height = boardData["height"]
        self.thickness = boardData["thickness"]
        self.centerX = boardData["centerX"]
        self.centerY = boardData["centerY"]
        self.boardID = boardData["boardID"]
        self.material = boardData["material"]
        self.boardFilename = boardData["fileName"]
        print(boardData)

    def compressCutData(self):
        tstr = json.dumps(self.cutPoints)
        out = io.BytesIO()
        with gzip.GzipFile(fileobj=out, mode="w") as f:
            f.write(tstr.encode())
        self.compressedCutData = out.getvalue()

    def getUnCompressedCutDataJSON(self):
        tstr = json.dumps(self.cutPoints)
        return tstr

    def updateCompressedCutData(self, data):
        print("here0")
        self.compressedCutData = data
        mem = io.BytesIO(data)
        f = gzip.GzipFile(fileobj=mem, mode="rb")
        print(f)
        self.cutPoints = json.loads(f.read().decode())
        print(self.cutPoints)

    def clearCutPoints(self):
        self.cutPoints = None
        self.compressedCutData = None