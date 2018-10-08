'''

This module provides a logger which can be used to record and later report the machine's
behavior.

'''

from DataStructures.makesmithInitFuncs       import MakesmithInitFuncs
import threading
from app import app,socketio
from flask_sse import sse



class Logger(MakesmithInitFuncs):

    errorValues = []
    recordingPositionalErrors = False
    clients = []

    messageBuffer = ""

    #clear the old log file
    with open("log.txt", "a") as logFile:
            logFile.truncate()

    def addClient(self,sid):
        print "sid="+str(sid)
        print "self="+str(self)
        self.clients.append(sid)

    def removeClient(self,sid):
        self.clients.remove(sid)

    def writeToLog(self, message):

        '''

        Writes a message into the log

        Actual writing is done in a separate thread to no lock up the UI because file IO is
        way slow

        '''
        #if hasattr(self,"clients"):
        #print self.clients
        #else:
        #    print self
        #for client in self.clients:
            #app.data.sendMessage("message",message, client)
            #print "logger socket="+str(socketio)+" client:"+client
            #print app.app_context()
            #with app.app_context():
            #    print socketio
            #    socketio.emit('message', {'data': message}, room=client)
        #with app.app_context():
        #    sse.publish({"message":"hello there"}, type='message')
        app.data.message = app.data.message+message

        if (message[0]!="<" and message[0]!="["):
        #if (True):
            try:
                self.messageBuffer = self.messageBuffer + message
            except:
                pass

        if len(self.messageBuffer) > 100:

            t = threading.Thread(target=self.writeToFile, args=(self.messageBuffer, "write"))
            t.daemon = True
            t.start()
            self.messageBuffer = ""

    def writeToFile(self, toWrite, *args):
        '''

        Write to the log file

        '''

        with open("log.txt", "a") as logFile:
            logFile.write(toWrite)

        return

    def writeErrorValueToLog(self, error):
        '''

        Writes an error value into the log.

        '''
        if self.recordingPositionalErrors:
            self.errorValues.append(abs(error))

        #if we've gotten to the end of the file
        if self.data.gcodeIndex == len(self.data.gcode) and self.recordingPositionalErrors:
            self.endRecordingAvgError()
            self.reportAvgError()

    def beginRecordingAvgError(self):
        '''

        Begins recording error values.

        '''
        self.recordingPositionalErrors = True
        self.errorValues = []

    def endRecordingAvgError(self):
        '''

        Stops recording error values.

        '''
        print "stopping to record"
        self.recordingPositionalErrors = False

    def reportAvgError(self):
        '''

        Reports the average positional error since the recording began.

        '''

        avg = sum(self.errorValues)/len(self.errorValues)
        self.data.message_queue.put("Message: The average feedback system error was: " + "%.2f" % avg + "mm")


        #should popup message here
