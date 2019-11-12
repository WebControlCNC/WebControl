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

        with self.app.app_context():
            while True:
                # this sleep function is needed to keep it non-blocking.
                time.sleep(0.001)
                while (
                        not self.app.data.alog_streamer_queue.empty() or not self.app.data.log_streamer_queue.empty()):  # if there is new data to be read
                    if not self.app.data.alog_streamer_queue.empty():
                        message = self.app.data.alog_streamer_queue.get()
                        if message != "":
                            socketio.emit("message", {"log": "alog", "data": message, "dataFormat": "text"},
                                          namespace="/MaslowCNCLogs", )
                    if not self.app.data.log_streamer_queue.empty():
                        message = self.app.data.log_streamer_queue.get()
                        if message != "":
                            socketio.emit("message", {"log": "log", "data": message, "dataFormat": "text"},
                                          namespace="/MaslowCNCLogs", )


