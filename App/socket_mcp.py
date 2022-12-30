from app import socketio

from flask import request


def init_socket_mcp(app):
    route_type = "socket"
    namespace = "/WebMCP"
    app.data.console_queue.put(f"{__name__}: Initializing {route_type} handling for {namespace}")
    
    @socketio.on("checkInRequested", namespace=namespace)
    def checkInRequested():
        socketio.emit("checkIn", namespace=namespace)

    @socketio.on("connect", namespace=namespace)
    def watchdog_connect():
        app.data.console_queue.put("watchdog connected")
        app.data.console_queue.put(request.sid)
        socketio.emit("connect", namespace=namespace)
