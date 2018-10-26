from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from Connection.serialPortThread import SerialPortThread

import sys
import serial
import serial.tools.list_ports
import threading
import schedule
import time
import json

class SerialPort(MakesmithInitFuncs):
    """

    The SerialPort is an object which manages communication with the device over the serial port.

    The actual connection is run in a separate thread by an instance of a SerialPortThread object.

    """

    # COMports = ListProperty(("Available Ports:", "None"))

    def __init__(self):
        """
        Runs on creation, schedules the software to attempt to connect to the machine

        """
        schedule.every(5).seconds.do(self.openConnection)

    def setPort(self, port):
        """

        Defines which port the machine is attached to

        """
        print("update ports")
        print(port)
        self.data.comport = port

    def connect(self, *args):
        """

        Forces the software to begin trying to connect on the new port.

        This function may not be necessary, but it should stay in because it simplifies the user experience.

        """
        self.data.config.setValue(
            "Makesmith Settings", "COMport", str(self.data.comport)
        )

    """

    Serial Connection Functions

    """

    def openConnection(self, *args):
        # This function opens the thread which handles the input from the serial port
        # It only needs to be run once, it is run by connecting to the machine

        # print("Attempting to open connection to controller")
        if not self.data.connectionStatus:
            # self.data.message_queue is the queue which handles passing CAN messages between threads
            # print "serialport.self.app.logger="+str(self.app.logger)
            self.data.ui_queue.put(
                "Message: connectionStatus:_" + json.dumps({'status': 'disconnected', 'port': 'none'})
            )  # the "_" facilitates the parse
            x = SerialPortThread()
            x.data = self.data
            self.th = threading.Thread(target=x.getmessage)
            self.th.daemon = True
            self.th.start()
        else:
            self.data.ui_queue.put(
                "Action: connectionStatus:_" + json.dumps({'status': 'connected', 'port': self.data.comport})
            )  # the "_" facilitates the parse


