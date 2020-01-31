from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from Connection.serialPortThread import SerialPortThread

import serial
import threading


class SerialPort(MakesmithInitFuncs):
    """
    The SerialPort is an object which manages communication with the device over the serial port.
    The actual connection is run in a separate thread by an instance of a SerialPortThread object.
    """

    serialPortRequest = ""
    _worker = None
    _serialInstance = None
    _thread = None

    # COMports = ListProperty(("Available Ports:", "None"))

    def __init__(self):
        """
        Runs on creation, schedules the software to attempt to connect to the machine
        """
        self._serialInstance = serial.Serial(baudrate=57600, timeout=0.25)
        self._stop_event = threading.Event()

        # schedule.every(5).seconds.do(self.openConnection)

    def setUpData(self, data):
        self.data = data
        self._worker = SerialPortThread(self._serialInstance)
        self._worker.data = data
        self._thread = threading.Thread(
            target=self._worker.getmessage, daemon=True, args=(self._stop_event,)
        )

    def openConnection(self, *args):
        # This function opens the thread which handles the input from the serial port

        # check for serial version being > 3
        if float(serial.VERSION[0]) < 3:
            self.data.ui_queue1.put(
                "Alert",
                "Incompability Detected",
                "Pyserial version 3.x is needed, but version "
                + serial.VERSION
                + " is installed",
            )
        self.data.comport = self.data.config.getValue("Maslow Settings", "COMport")

        # set com port every time as it could have changed.
        self._serialInstance.port = self.data.comport

        if not self._serialInstance.is_open:
            try:
                connectMessage = (
                    "Trying to connect to controller on " + self.data.comport
                )
                self.data.console_queue.put(connectMessage)
                self._serialInstance.open()
            except Exception as e:
                self.data.console_queue.put("Error opening serial port: " + str(e))

        if self._serialInstance.is_open:
            self.data.connectionStatus = 1
            self.serialPortRequest = "Open"
            self.data.currentTool = 0  # This is necessary since the controller will have reset tool to zero.
            self.data.console_queue.put(
                "\r\nConnected on port " + self.data.comport + "\r\n"
            )
            self.data.ui_queue1.put(
                "TextMessage", "", "Connected on port " + self.data.comport
            )
            self.data.ui_queue1.put(
                "Action",
                "connectionStatus",
                {
                    "status": "connected",
                    "port": self.data.comport,
                    "fakeServoStatus": self.data.fakeServoStatus,
                },
            )

            if not self._thread.isAlive():
                self._thread.start()

            self._getFirmwareVersion()
            self._setupMachineUnits()
            self._requestSettingsUpdate()
        else:
            self.data.connectionStatus = 0
            self.serialPortRequest = "Closed"
            self.data.ui_queue1.put(
                "Action",
                "connectionStatus",
                {
                    "status": "disconnected",
                    "port": "none",
                    "fakeServoStatus": self.data.fakeServoStatus,
                },
            )

    def closeConnection(self):
        if self._serialInstance is not None and self._serialInstance.is_open:
            # Stop the worker thread
            self._stop_event.set()
            # Close the connection
            self._serialInstance.close()
            print("Serial connection closed at serialPortThread")
        else:
            print("Serial Instance is none??")

        if self.data.uploadFlag > 0:
            self.data.ui_queue1.put(
                "Alert",
                "Connection Lost",
                "Message: USB connection lost. This has likely caused the machine to loose it's calibration, which can cause erratic behavior. It is recommended to stop the program, remove the sled, and perform the chain calibration process. Press Continue to override and proceed with the cut.",
            )
        else:
            self.data.ui_queue1.put(
                "SendAlarm", "Alarm: Connection Failed or Invalid Firmware", ""
            )

        self.serialPortRequest = "Closed"
        self.data.connectionStatus = 0
        return

    def getConnectionStatus(self):
        return self.serialPortRequest

    def _getFirmwareVersion(self):
        """
        Send command to have controller report details
        :return:
        """
        self.data.gcode_queue.put("B05 ")

    def _setupMachineUnits(self):
        """
        Send command to put controller in correct units state.
        :return:
        """
        if self.data.units == "INCHES":
            self.data.gcode_queue.put("G20 ")
        else:
            self.data.gcode_queue.put("G21 ")

    def _requestSettingsUpdate(self):
        """
        Send command to have controller report settings
        :return:
        """
        self.data.gcode_queue.put("$$")

    def clearAlarm(self):
        if not self._serialInstance.is_open:
            self.openConnection()

