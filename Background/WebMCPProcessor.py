from __main__ import socketio

import time

from DataStructures.makesmithInitFuncs import MakesmithInitFuncs


class WebMCPProcessor(MakesmithInitFuncs):
    """
    This class is deprecated as shifting away from WebMCP.
    """

    app = None

    def start(self, _app):
        print("Starting WebMCP Queue Processor")
        self.app = _app
        self.data.webMCPActive = True
        while True:
            time.sleep(0.001)
            while not self.data.mcp_queue.empty():  # if there is new data to be read
                message = self.data.mcp_queue.get()
                # print("MCP Queue:"+message)
                if self.app is not None:
                    with self.app.app_context():
                        # print("Emitting:"+message)
                        socketio.emit(
                            "webcontrolMessage", {"data": message}, namespace="/WebMCP"
                        )

    def connect(self, _app):
        self.app = _app


class ConsoleProcessor(MakesmithInitFuncs):
    def start(self):
        print(f"{__name__}: Starting Console Queue Processor")
        while True:
            time.sleep(0.001)
            while (
                not self.data.console_queue.empty()
            ):  # if there is new data to be read
                message = self.data.console_queue.get()
                print(message)
                if self.data.webMCPActive:
                    # print("putting message in mcp_queue")
                    self.data.mcp_queue.put(message)
