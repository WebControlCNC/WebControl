from __main__ import socketio

import time

'''
This class sends logs to a browser via sockets.  It monitors two log queues (log and alog) and sends the messages
if data is available.

This class is not MakesmithInitFuncs inherited, so it doesn't have direct access to the data.  Therefore, it gets
passed the app.  
'''
class LogStreamer:
    app = None

    def start(self, _app):
        self.app = _app
        self.app.data.console_queue.put("Starting Log Streamer")

        timeSinceLastLoggerState = time.time()
        with self.app.app_context():
            while True:
                # this sleep function is needed to keep it non-blocking.
                time.sleep(0.001)
                # if there is new data to be read
                loggerState = self.app.data.logger.getLoggerState()
                while (not self.app.data.alog_streamer_queue.empty() or not self.app.data.log_streamer_queue.empty()):
                    # process a line from the alog queue
                    if not self.app.data.alog_streamer_queue.empty():
                        message = self.app.data.alog_streamer_queue.get()
                        if message != "":
                            socketio.emit("message", {"log": "alog", "data": message, "state": loggerState,
                                                      "dataFormat": "text"}, namespace="/MaslowCNCLogs", )
                            timeSinceLastLoggerState = time.time()
                    # process a line from the log queue
                    if not self.app.data.log_streamer_queue.empty():
                        message = self.app.data.log_streamer_queue.get()
                        if message != "":
                            socketio.emit("message", {"log": "log", "data": message, "state": loggerState,
                                                      "dataFormat": "text"}, namespace="/MaslowCNCLogs", )
                            timeSinceLastLoggerState = time.time()
                currentTime = time.time()
                if currentTime - timeSinceLastLoggerState > 5:
                    socketio.emit("message", {"log": "state", "state": loggerState, "dataFormat":"text"},
                                  namespace="/MaslowCNCLogs", )
                    timeSinceLastLoggerState = currentTime

