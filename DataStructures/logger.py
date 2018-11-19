"""

This module provides a logger which can be used to record and later report the machine's
behavior.

"""

from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
import threading
import os
import time
import datetime
from pathlib import Path
from app import app, socketio



class Logger(MakesmithInitFuncs):

    errorValues = []
    recordingPositionalErrors = False
    clients = []
    logStartTime = 0

    messageBuffer = ""
    amessageBuffer = ""
    idler = 0
    suspendLogging = False
    lastALogWrite = 0
    lastLogWrite = 0
    loggingTimeout = -1

    def __init__(self):
        print("Initializing Logger")
        self.home = str(Path.home())
        # clear the old log file
        if not os.path.isdir(self.home + "/.WebControl"):
            print("creating " + self.home + "/.WebControl directory")
            os.mkdir(self.home + "/.WebControl")
        print(self.home+"/.WebControl/"+"log.txt")
        with open(self.home+"/.WebControl/"+"log.txt", "a") as logFile:
            logFile.truncate()

        with open(self.home+"/.WebControl/"+"alog.txt", "a") as logFile:
            logFile.truncate()
        
        self.logStartTime = time.time()
        dateTime = datetime.datetime.fromtimestamp(self.logStartTime).strftime('%Y-%m-%d %H:%M:%S')
        self.amessageBuffer = "+++++\n"+dateTime+"\n+++++\n".format(self.logStartTime)
        self.messageBuffer = "+++++\n"+dateTime+"\n+++++\n".format(self.logStartTime)
        self.idler = time.time()
        self.lastALogWrite = self.idler
        self.lastLogWrite = self.idler

    def resetIdler(self):
        self.idler = time.time()

    def setLoggingTimeout(self, timeOut):
        self.loggingTimeout = timeOut

    def writeToLog(self, message):

        """

        Writes a message into the log

        Actual writing is done in a separate thread to no lock up the UI because file IO is
        way slow

        """
        if self.loggingTimeout == -1: #get setting for suspend time
            self.loggingTimeout = self.data.config.get("WebControl Settings","loggingTimeout")
        currentTime = time.time()
        logTime = "{:0.2f}".format(currentTime-self.logStartTime)
        dateTime = datetime.datetime.fromtimestamp(currentTime).strftime('%Y-%m-%d %H:%M:%S')
        if self.loggingTimeout > 0 and self.data.uploadFlag == 0 and currentTime-self.idler > self.loggingTimeout:
            if not self.suspendLogging:
                self.messageBuffer += logTime + ": " + "Logging suspended due to user idle time > "+str(self.loggingTimeout)+" seconds\n"
                self.suspendLogging = True
        else:
            if self.suspendLogging:
                self.messageBuffer += logTime + ": " + "Logging resumed due to user activity\n"
                self.suspendLogging = False

        if message[0] != "<" and message[0] != "[":
            try:
                tmessage = message.rstrip('\r\n')
                self.amessageBuffer += logTime+": " + tmessage+"\n"
                if not self.suspendLogging:
                    self.messageBuffer += logTime+": " + tmessage+"\n"
            except:
                pass
        else:
            try:
                if not self.suspendLogging:
                    tmessage = message.rstrip('\r\n')
                    self.messageBuffer += logTime+": "+ tmessage+"\n"
            except:
                pass

        if len(self.messageBuffer) > 500 or currentTime-self.lastLogWrite > 15:
            if self.messageBuffer != "":  #doing it this way will flush out the buffer when in idle state.
                t = threading.Thread(
                    target=self.writeToFile, args=(self.messageBuffer, True, "write")
                )
                t.daemon = True
                t.start()
                self.messageBuffer = ""
                self.lastLogWrite = currentTime

        if len(self.amessageBuffer) > 500 or currentTime-self.lastALogWrite > 15:
            if self.amessageBuffer != "":
                t = threading.Thread(
                    target=self.writeToFile, args=(self.amessageBuffer, False, "write")
                )
                t.daemon = True
                t.start()
                self.amessageBuffer = ""
                self.lastALogWrite = currentTime

    def writeToFile(self, toWrite, log, *args):
        """
        Write to the log file
        """
        if log is True:
            with open(self.home+"/.WebControl/"+"log.txt", "a") as logFile:
                logFile.write(toWrite)
        else:
            with open(self.home+"/.WebControl/"+"alog.txt", "a") as logFile:
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
        self.data.console_queue.put("stopping to record")
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
