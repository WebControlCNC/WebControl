from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from Connection.serialPort import SerialPort
from File.gcodeFile import GCodeFile
from File.importFile import ImportFile
from Actions.actions import Actions
from Actions.triangularCalibration import TriangularCalibration
from Actions.opticalCalibration import OpticalCalibration
from Background.messageProcessor import MessageProcessor
from Background.WebMCPProcessor import WebMCPProcessor
from Background.WebMCPProcessor import ConsoleProcessor
from Background.webcamVideoStream import WebcamVideoStream

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
    opticalCalibration = OpticalCalibration()
    messageProcessor = MessageProcessor()
    mcpProcessor = WebMCPProcessor()
    consoleProcessor = ConsoleProcessor()
    camera = WebcamVideoStream()

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
        data.opticalCalibration = self.opticalCalibration
        data.messageProcessor = self.messageProcessor
        data.mcpProcessor = self.mcpProcessor
        data.consoleProcessor = self.consoleProcessor
        data.camera = self.camera

        self.serialPort.setUpData(data)
        self.gcodeFile.setUpData(data)
        self.importFile.setUpData(data)
        self.actions.setUpData(data)
        self.triangularCalibration.setUpData(data)
        self.opticalCalibration.setUpData(data)
        self.messageProcessor.setUpData(data)
        self.mcpProcessor.setUpData(data)
        self.consoleProcessor.setUpData(data)
        self.camera.setUpData(data)
        self.camera.start()

