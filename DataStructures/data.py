from time import time
from DataStructures.logger import Logger
from DataStructures.loggingQueue import LoggingQueue
from DataStructures.uiQueue import UIQueue
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
    gcodeFileUnits = "INCHES"
    sentCustomGCode = ""
    compressedGCode = None
    compressedGCode3D = None

    version = "1.27"
    stockFirmwareVersion = None
    customFirmwareVersion = None
    holeyFirmwareVersion = None
    controllerFirmwareVersion = 0

    '''
    Version Updater
    '''
    lastChecked = -1
    pyInstallCurrentVersion = 0.920
    pyInstallUpdateAvailable = False
    pyInstallUpdateBrowserUrl = ""
    pyInstallUpdateVersion = 0
    pyInstallPlatform = "win"
    pyInstallType = "singlefile"
    pyInstallInstalledPath = ""

 
    # all of the available COM ports
    comPorts = []
    # This defines which COM port is used
    comport = ""
    # stores value to indicate whether or not fake_servo is enabled
    fakeServoStatus = False
    # The index of the next unread line of Gcode
    gcodeIndex = 0
    # Index of changes in z
    zMoves = []
    # Holds the current value of the feed rate
    feedRate = 20
    # holds the address of the g-code file so that the gcode can be refreshed
    gcodeFile = ""
    importFile = ""
    # holds the current gcode x,y,z position
    currentGcodePost = [0.0, 0.0, 0.0]
    # the current position of the cutting head
    currentpos = [0.0, 0.0, 0.0]
    target = [0.0, 0.0, 0.0]
    units = "MM"
    tolerance = 0.5
    gcodeShift = [0.0, 0.0]  # the amount that the gcode has been shifted
    currentTool = 0  # current tool.. upon startup, 0 is the same value as what the controller would have.
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
    inPIDVelocityTest = False
    inPIDPositionTest = False
    PIDVelocityTestVersion = 0
    PIDPositionTestVersion = 0
    wiiPendantPresent = False # has user set wiimote as active?
    wiiPendantConnected = False # is the wiimote BT connected?

    """
    Pointers to Objects
    """
    serialPort = None  # this is a pointer to the program serial port object
    requestSerialClose = False  # this is used to request the serialThread to gracefully close the port
    triangularCalibration = None  # points to the triangular calibration object
    holeyCalibration = None  # points to the triangular calibration object
    opticalCalibration = None  # points to the optical calibration object
    opticalCalibrationImage = None  # stores the current image
    opticalCalibrationImageUpdated = False  # stores whether its been updated or not
    opticalCalibrationTestImage = None  # stores the current image
    opticalCalibrationTestImageUpdated = False  # stores whether its been updated or not
    cameraImage = None
    cameraImageUpdated = False
    continuousCamera = False
    gpioActions = None
    boardManager = None
    #wiiPendant = None  #wiiPendantThread = None
    
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
    ui_controller_queue = queue.Queue()
    ui_queue1 = UIQueue()
    alog_streamer_queue = queue.Queue(1000)  # used for sending log to client screen.. limit to 1000 "items"
    log_streamer_queue = queue.Queue(1000) # used for sending log to client screen.. limit to 1000 "items"
    console_queue = queue.Queue() # used for printing to terminal
    mcp_queue = queue.Queue () # used for sending messages to WebMCP(if enabled)
    webMCPActive = False  # start false until WebMCP connects
    gcode_queue = queue.Queue()
    quick_queue = queue.Queue()

    """
    Position and Error values
    """
    xval = 0.0
    yval = 0.0
    zval = 0.0
    xval_prev = -99990.0
    yval_prev = -99990.0
    zval_prev = -99990.0

    leftError = 0.0
    rightError = 0.0
    leftError_prev = -99999.0
    rightError_prev = -99999.9

    """
    Chain lengths as reported by controller
    """
    leftChain = 1610
    rightChain = 1610

    """
    Sled position computed from controller reported chain lengths
    """
    computedX = 0
    computedY = 0

    """
    Buffer size as reported by controller
    """
    bufferSize = 127

    pausedzval = 0.0

    """
    GCode Position Values
    """
    previousPosX = 0.0
    previousPosY = 0.0
    previousPosZ = 0.0

    """
    Board data
    """
    currentBoard = None


    shutdown = False

    hostAddress = "-"
    platform = "RPI"
    platformHome = ""



    def __init__(self):
        """

        Initializations.

        """
        self.logger.data = self
        self.config.data = self
