import sys
import distro
import os
import platform
from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from Connection.serialPort import SerialPort
from File.gcodeFile import GCodeFile
from File.importFile import ImportFile
from Actions.actions import Actions
from Actions.triangularCalibration import TriangularCalibration
from Actions.holeyCalibration import HoleyCalibration
from Actions.HoleySimulationKinematics import Kinematics as HoleyKinematics
from Actions.gpioActions import GPIOActions
from Background.messageProcessor import MessageProcessor
from Background.WebMCPProcessor import WebMCPProcessor
from Background.WebMCPProcessor import ConsoleProcessor
# from Background.webcamVideoStream import WebcamVideoStream
from Boards.boardManager import BoardManager
from ReleaseManager.releaseManager import ReleaseManager
from HelpManager.helpManager import HelpManager
#from GCodeOptimizer.gcodeOptimizer import GCodeOptimizer

class NonVisibleWidgets(MakesmithInitFuncs):
    """

    NonVisibleWidgets is a home for widgets which do not have a visible representation like
    the serial connection, but which still need to be tied in to the rest of the program.

    """

    serialPort = SerialPort()
    gcodeFile = GCodeFile()
    importFile = ImportFile()
    actions = Actions()
    triangularCalibration = TriangularCalibration()
    holeyCalibration = HoleyCalibration()
    holeyKinematics = HoleyKinematics()
    messageProcessor = MessageProcessor()
    mcpProcessor = WebMCPProcessor()
    consoleProcessor = ConsoleProcessor()
    #camera = WebcamVideoStream()
    gpioActions = GPIOActions()
    boardManager = BoardManager()
    releaseManager = ReleaseManager()
    helpManager = HelpManager()
    #gcodeOptimizer = GCodeOptimizer()

    def setUpData(self, data):
        """

        The setUpData function is called when a widget is first created to give that widget access
        to the global data object. This should be replaced with a supper classed version of the __init__
        function.

        """

        self.data = data
        # print "Initialized: " + str(self)

        data.serialPort = (
            self.serialPort
        )  # add the serial port widget to the data object
        data.gcodeFile = self.gcodeFile
        data.importFile = self.importFile
        data.actions = self.actions
        data.triangularCalibration = self.triangularCalibration
        data.holeyCalibration = self.holeyCalibration
        data.holeyKinematics = self.holeyKinematics
        data.messageProcessor = self.messageProcessor
        data.mcpProcessor = self.mcpProcessor
        data.consoleProcessor = self.consoleProcessor
        #data.camera = self.camera
        data.gpioActions = self.gpioActions
        data.boardManager = self.boardManager
        data.releaseManager = self.releaseManager
        data.helpManager = self.helpManager
        #data.gcodeOptimizer = self.gcodeOptimizer

        if hasattr(sys, '_MEIPASS'):
            data.platform = "PYINSTALLER"
            data.platformHome = sys._MEIPASS

        data.pyInstallPlatform = platform.system().lower()
        
        if data.pyInstallPlatform == "windows":
            if platform.machine().endswith('64'):
                data.pyInstallPlatform = "win64"
            if platform.machine().endswith('32'):
                data.pyInstallPlatform = "win32"

        if data.pyInstallPlatform == "linux":
            _platform = distro.linux_distribution()[0].lower()
            print("##")
            print(data.pyInstallPlatform)
            print(_platform)
            if  os.path.exists('/etc/rpi-issue'):
                data.pyInstallPlatform = 'RPI'
                print("--RPI--")
            else:
                print("not raspberrypi")
            print("##")
        print("----")
        print(data.pyInstallPlatform)


        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                if sys._MEIPASS.find("_MEI") == -1:
                    data.pyInstallType = "singledirectory"
                else:
                    data.pyInstallType = "singlefile"
        else:
            data.pyInstallType = "singledirectory"

        print(data.pyInstallType)
        print("----")

        self.serialPort.setUpData(data)
        self.gcodeFile.setUpData(data)
        self.importFile.setUpData(data)
        self.actions.setUpData(data)
        self.triangularCalibration.setUpData(data)
        self.holeyCalibration.setUpData(data)
        self.holeyKinematics.setUpData(data)
        self.messageProcessor.setUpData(data)
        self.mcpProcessor.setUpData(data)
        self.consoleProcessor.setUpData(data)
        #self.camera.setUpData(data)
        #self.camera.getSettings()
        self.gpioActions.setUpData(data)
        self.gpioActions.setup()
        self.boardManager.setUpData(data)
        self.boardManager.initializeNewBoard()
        self.releaseManager.setUpData(data)
        self.helpManager.setUpData(data)
        #self.gcodeOptimizer.setUpData(data)

        #set up kinematics with current settings
        self.holeyKinematics.initializeSettings()
        #self.camera.start()
        
        
