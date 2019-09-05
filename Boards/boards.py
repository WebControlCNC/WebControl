import json
import gzip
import io


class Board():
    def __init__(self):
        # can't do much because data hasn't been initialized yet
        pass

    width = 95
    height = 47
    thickness = 0.75
    centerX = 0
    centerY = 0

    boardID = "Undefined"
    material = "Undefined"

    boardPoints = []
    cutPoints = []
    cutPoints2 = []
    pointsPerInch = 1

    compressedCutData = None

    def updateBoardInfo(self, boardID, material, height, width, thickness, centerX, centerY):
        try:
            self.width = float(width)
            self.height = float(height)
            self.thickness = float(thickness)
            self.centerX = float(centerX)
            self.centerY = float(centerY)
            self.boardID = boardID
            self.material = material
            self.updateBoardPoints()
            return True
        except Exception as e:
            return False

    def updateBoardPoints(self):
        '''
        self.boardPoints = []

        outline = []
        outline.append([self.centerX - self.width/2.0, self.centerY + self.height/2.0, 0])
        outline.append([self.centerX + self.width / 2.0, self.centerY + self.height / 2.0, 0])
        outline.append([self.centerX + self.width / 2.0, self.centerY - self.height / 2.0, 0])
        outline.append([self.centerX - self.width / 2.0, self.centerY - self.height / 2.0, 0])
        outline.append([self.centerX - self.width / 2.0, self.centerY + self.height / 2.0, 0])
        self.boardPoints.append(outline)

        coutline = []
        coutline.append([self.centerX - self.width/2.0, self.centerY + self.height/2.0, 0])
        coutline.append([self.centerX - self.width / 2.0, self.centerY - self.height / 2.0, 0])
        self.boardPoints.append(coutline)

        self.compressCuytutData()
        '''
        return

    def updateCutPoints(self, data):
        self.cutPoints = data
        self.compressCutData()

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
        tstr = json.dumps({"width": self.width, "height": self.height, "thickness": self.thickness, "centerX": self.centerX, "centerY": self.centerY, "boardID":self.boardID, "material":self.material})
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
        self.updateBoardPoints()
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
        self.compressedCutData = data