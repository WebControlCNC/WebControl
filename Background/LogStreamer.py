from __main__ import socketio

import time


class LogStreamer:
    app = None

    def start(self, _app):
        self.app = _app
        self.app.data.console_queue.put("starting log streamer")

        with self.app.app_context():
            while True:
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


