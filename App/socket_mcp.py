from app import socketio

from flask import current_app, request


def init_socket_mcp(app):
    route_type = "socket"
    namespace = "/WebMCP"
    print(f"Initializing {route_type} handling for {namespace}")
    
    @socketio.on("checkInRequested", namespace=namespace)
    def checkInRequested():
        socketio.emit("checkIn", namespace=namespace)


    @socketio.on("connect", namespace=namespace)
    def watchdog_connect():
        app.data.console_queue.put("watchdog connected")
        app.data.console_queue.put(request.sid)
        socketio.emit("connect", namespace=namespace)

        # TODO: This requires handling in a completely different way - this breaks socketio.on connect handling
        # if app.mcpthread == None:
        #     app.data.console_queue.put("going to start mcp thread")
        #     app.mcpthread = socketio.start_background_task(
        #         app.data.mcpProcessor.start, current_app._get_current_object()
        #     )
        #     app.data.console_queue.put("created mcp thread")
        #     app.mcpthread.start()
        #     app.data.console_queue.put("started mcp thread")
