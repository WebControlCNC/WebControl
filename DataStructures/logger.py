"""

This module provides a logger which can be used to record and later report the machine's
behavior.

"""

from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
import threading
from app import app, socketio


class Logger(MakesmithInitFuncs):

    errorValues = []
    recordingPositionalErrors = False
    clients = []

    messageBuffer = ""
    amessageBuffer = ""

    # clear the old log file
    with open("log.txt", "a") as logFile:
        logFile.truncate()

    with open("alog.txt", "a") as logFile:
        logFile.truncate()

    def writeToLog(self, message):

        """

        Writes a message into the log

        Actual writing is done in a separate thread to no lock up the UI because file IO is
        way slow

        """
        if message[0] != "<" and message[0] != "[":
            try:
                self.amessageBuffer = self.amessageBuffer + message
                self.messageBuffer = self.messageBuffer + message
            except:
                pass
        else:
            try:
                self.messageBuffer = self.messageBuffer + message
            except:
                pass

        if len(self.messageBuffer) > 500:
            t = threading.Thread(
                target=self.writeToFile, args=(self.messageBuffer, True, "write")
            )
            t.daemon = True
            t.start()
            self.messageBuffer = ""

        if len(self.amessageBuffer) > 500:
            t = threading.Thread(
                target=self.writeToFile, args=(self.amessageBuffer, False, "write")
            )
            t.daemon = True
            t.start()
            self.amessageBuffer = ""

    def writeToFile(self, toWrite, log, *args):
        """
        Write to the log file
        """
        if log is True:
            with open("log.txt", "a") as logFile:
                logFile.write(toWrite)
        else:
            with open("alog.txt", "a") as logFile:
                logFile.write(toWrite)

        return

    def writeErrorValueToLog(self, error):
        """

        Writes an error value into the log.

        """
        if self.recordingPositionalErrors:
            self.errorValues.append(abs(error))

        # if we've gotten to the end of the file
        if (
            self.data.gcodeIndex == len(self.data.gcode)
            and self.recordingPositionalErrors
        ):
            self.endRecordingAvgError()
            self.reportAvgError()

    def beginRecordingAvgError(self):
        """

        Begins recording error values.

        """
        self.recordingPositionalErrors = True
        self.errorValues = []

    def endRecordingAvgError(self):
        """

        Stops recording error values.

        """
        print("stopping to record")
        self.recordingPositionalErrors = False

    def reportAvgError(self):
        """

        Reports the average positional error since the recording began.

        """

        avg = sum(self.errorValues) / len(self.errorValues)
        self.data.ui_queue.put(
            "Message: The average feedback system error was: " + "%.2f" % avg + "mm"
        )

        # should popup message here
