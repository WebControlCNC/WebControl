import json
import gzip
import io
import math


class Board():
    '''
    Class is the generalization of a board that tracks board information including areas that have been cut.  Resolution
    is 1-inch squares.
    '''
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

    ###
    # old, not sure is used
    # todo: delete boardPoints and cutPoints2 if not used
    boardPoints = []
    cutPoints2 = []
    ###

    cutPoints = []
    pointsPerInch = 1
    compressedCutData = ""

    def updateBoardInfo(self, boardID, material, height, width, thickness, centerX, centerY, units):
        '''
        Updates the cut data
        :param boardID: Name give to board, as entered by user
        :param material: Type of material of board, as entered by user
        :param height: height of board, stored in inches but entered as defined by units
        :param width:  width of board, stored in inches but entered as defined by units
        :param thickness: thickness of board, stored in inches but entered as defined by units
        :param centerX: X-coordinate of center of board, stored in inches but entered as defined by units
        :param centerY: Y-coordinate of center of board, stored in inches but entered as defined by units
        :param units: units the measurements are provided in.
        :return:
        '''

        try:
            scale = 1
            if units == "mm":
                scale = 25.4
            self.width = round(float(width)/scale, 2)
            self.height = round(float(height)/scale, 2)
            self.thickness = round(float(thickness)/scale, 2)
            self.centerX = round(float(centerX)/scale, 2)
            self.centerY = round(float(centerY)/scale, 2)
            self.boardID = boardID
            self.material = material
            return True
        except Exception as e:
            print(e)
            return False

    def updateCutPoints(self, data):
        '''
        Using array received from board manager, updates cut data and recompresses.
        :param data:
        :return:
        '''
        if len(self.cutPoints) == 0:
            #if cutdata isn't an array yet, then use the cut data (i.e., no existing data)
            self.cutPoints = data
        else:
            # existing cut data exists, so add this data
            for x in range(len(self.cutPoints)):
                # if the data in data is cut (True) then make the data in cutPoints true as well.. i.e., performs
                # an OR operation
                if data[x]:
                    self.cutPoints[x] = True
        # call to compress the cut data.
        self.compressCutData()

    def trimBoard(self, trimTop, trimBottom, trimLeft, trimRight, units):
        '''
        Trims portion of the board and updates cutdata
        :param trimTop: Amount to trim off top, units as defined in units
        :param trimBottom: Amount to trim off bottom, units as defined in units
        :param trimLeft: Amount to trim off left, units as defined in units
        :param trimRight: Amount to trim off left, units as defined in units
        :param units: units of trim measurements
        :return:
        '''
        # adjust for correct units (i.e., convert to inches and round to 2 decimal points)
        scale = 1
        if units == "mm":
            scale = 25.4
        trimTop = round(float(trimTop)/scale, 2)
        trimBottom = round(float(trimBottom) / scale, 2)
        trimLeft = round(float(trimLeft) / scale, 2)
        trimRight = round(float(trimRight) / scale, 2)

        # determine the new array extents
        aPointsX = math.ceil(self.width)
        aPointsY = math.ceil(self.height)
        bPointsX = math.ceil(self.width - trimLeft - trimRight)
        bPointsY = math.ceil(self.height - trimTop - trimBottom)

        # create a new cut array
        bCutPoints  = [False for i in range( bPointsX * bPointsY )]

        '''
        print(aPointsX)
        print(aPointsY)
        print(bPointsX)
        print(bPointsY)
        print(trimTop)
        print(trimBottom)
        print(trimLeft)
        print(trimRight)
        '''
        # if cutPoints are found...
        if (len(self.cutPoints)!=0):
            # iterate through new array and translate to old cut array points and assign matrix values.
            for x in range(bPointsX):
                for y in range(bPointsY):
                    ax = x + int(trimLeft)
                    ay = y + int(trimBottom)
                    ib = x+y*bPointsX
                    ia = ax+ay*aPointsX
                    #print(str(ib) +", "+ str(ia))
                    bCutPoints[ib] = self.cutPoints[ia]
        # assign cutPoints to new array
        self.cutPoints = bCutPoints
        # update dimensions
        self.height = self.height - trimTop - trimBottom
        self.width = self.width - trimLeft - trimRight
        # compress data
        self.compressCutData()
        return True

    def setFilename(self, data):
        '''
        Sets the filename of the board
        :param data:
        :return:
        '''
        self.boardFilename = data

    def getPoints(self):
        '''
        Don't think this is used.
        todo: remove if not needed
        :return:
        '''
        return self.boardPoints

    def getCutPoints(self):
        '''
        Returns uncompressed cut point data
        :return:
        '''
        return self.cutPoints

    def getCompressedCutData(self):
        '''
        returns compressed cut point data
        :return:
        '''
        return self.compressedCutData

    def getBoardInfoJSON(self):
        '''
        Returns board information formatted as a json
        :return:
        '''
        tstr = json.dumps({"width": self.width, "height": self.height, "thickness": self.thickness, "centerX": self.centerX, "centerY": self.centerY, "boardID":self.boardID, "material":self.material, "fileName":self.boardFilename})
        return tstr

    def updateBoardInfoJSON(self, data):
        '''
        updates board data from a json
        :param data:
        :return:
        '''
        boardData = json.loads(data)
        self.width = boardData["width"]
        self.height = boardData["height"]
        self.thickness = boardData["thickness"]
        self.centerX = boardData["centerX"]
        self.centerY = boardData["centerY"]
        self.boardID = boardData["boardID"]
        self.material = boardData["material"]
        self.boardFilename = boardData["fileName"]

    def compressCutData(self):
        '''
        Compresses cut data using gzip
        :return:
        '''
        tstr = json.dumps(self.cutPoints)
        out = io.BytesIO()
        with gzip.GzipFile(fileobj=out, mode="w") as f:
            f.write(tstr.encode())
        self.compressedCutData = out.getvalue()

    def getUnCompressedCutDataJSON(self):
        '''
        returns uncompressed cut data in json format.
        Not sure is used anymore
        todo: delete if not needed
        :return:
        '''
        tstr = json.dumps(self.cutPoints)
        return tstr

    def updateCompressedCutData(self, data):
        '''
        Updates the compressed cut data using data, uncompresses it and assigns it to cutPoints.  Used in loading
        a board
        :param data:
        :return:
        '''
        self.compressedCutData = data
        mem = io.BytesIO(data)
        f = gzip.GzipFile(fileobj=mem, mode="rb")
        self.cutPoints = json.loads(f.read().decode())

    def clearCutPoints(self):
        '''
        clears the cut points and compressed cut data
        :return:
        '''
        self.cutPoints = []
        self.compressedCutData = None