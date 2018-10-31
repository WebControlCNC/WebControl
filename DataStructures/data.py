from time import time
from DataStructures.logger import Logger
from DataStructures.loggingQueue import LoggingQueue
from config.config import Config
import queue


class Data:
    """

    Data is a set of variables which are essentially global variables which hold information
    about the gcode file opened, the machine which is connected, and the user's settings. These
    variables are NOT thread-safe. The queue system should always be used for passing information
    between threads.

    """

    """
    Data available to all widgets
    """

    # Gcodes contains all of the lines of gcode in the opened file
    clients = []
    gcode = []
    version = "1.23"
    # all of the available COM ports
    comPorts = []
    # This defines which COM port is used
    comport = ""
    # The index of the next unread line of Gcode
    gcodeIndex = 0
    # Index of changes in z
    zMoves = []
    # Holds the current value of the feed rate
    feedRate = 20
    # holds the address of the g-code file so that the gcode can be refreshed
    gcodeFile = ""
    importFile = ""
    # the current position of the cutting head
    currentpos = [0.0, 0.0, 0.0]
    target = [0.0, 0.0, 0.0]
    units = "MM"
    tolerance = 0.5
    gcodeShift = [0.0, 0.0]  # the amount that the gcode has been shifted
    message = ""  # used to update the client
    logger = Logger()  # the module which records the machines behavior to review later
    config = Config()
    # Background image stuff, persist but not saved
    backgroundFile = None
    backgroundTexture = None
    backgroundManualReg = []
    backgroundRedraw = False

    """
    Flags
    """
    # sets a flag if the gcode is being uploaded currently
    uploadFlag = 0
    previousUploadStatus = 0
    manualZAxisAdjust = False
    # this is used to determine the first time the position is received from the machine
    firstTimePosFlag = 0
    # report if the serial connection is open
    connectionStatus = 0
    # is the calibration process currently underway 0 -> false
    calibrationInProcess = False

    """
    Pointers to Objects
    """
    serialPort = None  # this is a pointer to the program serial port object
    triangularCalibration = None  # points to the triangular calibration object
    opticalCalibration = None  # points to the optical calibration object
    opticalCalibrationImage = None  # stores the current image
    opticalCalibrationImageUpdated = False  # stores whether its been updated or not
    opticalCalibrationTestImage = None  # stores the current image
    opticalCalibrationTestImageUpdated = False  # stores whether its been updated or not

    """

    Colors

    """
    fontColor = "[color=7a7a7a]"
    drawingColor = [0.47, 0.47, 0.47]
    posIndicatorColor = [0, 0, 0]
    targetIndicatorColor = [1, 0, 0]

    """
    Misc UI bits that need to be saved between invocations (but not saved)
    """
    zPush = None
    zPushUnits = "MM"
    zReadoutPos = 0.00
    zPopupUnits = None
    zStepSizeVal = 0.1

    """
    Queues
    """
    message_queue = LoggingQueue(logger)
    ui_queue = queue.Queue()
    gcode_queue = queue.Queue()
    quick_queue = queue.Queue()

    """
    Position and Error values
    """
    xval = 0.0
    yval = 0.0
    zval = 0.0

    previousPosX = 0.0
    previousPosY = 0.0
    previousPosZ = 0.0

    def __init__(self):
        """

        Initializations.

        """
        self.logger.data = self
        self.config.data = self
