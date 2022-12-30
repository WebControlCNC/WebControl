from app import socketio

from flask import request


def init_socket_maslowcnclogs(app):
    route_type = "socket"
    namespace = "/MaslowCNCLogs"
    app.data.console_queue.put(f"{__name__}: Initializing {route_type} handling for {namespace}")

    @socketio.on("connect", namespace=namespace)
    def log_connect():
        app.data.console_queue.put(f"{__name__}: Client connected to socket for namespace {namespace}")
        app.data.console_queue.put(f"{__name__}: {request.sid}")
        socketio.emit(
            "after connect", {"data": "Connected", "count": 0}, namespace=namespace
        )

    @socketio.on("disconnect", namespace=namespace)
    def log_disconnect():
        app.data.console_queue.put(f"{__name__}: Client disconnected")
