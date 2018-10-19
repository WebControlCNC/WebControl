from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from Connection.serialPort import SerialPort
from File.gcodeFile import GCodeFile
from File.importFile import ImportFile
from Actions.actions import Actions
from Actions.triangularCalibration import TriangularCalibration


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
        self.serialPort.setUpData(data)
        self.gcodeFile.setUpData(data)
        self.importFile.setUpData(data)
        self.actions.setUpData(data)
        self.triangularCalibration.setUpData(data)
