from app import socketio

from flask import current_app, request


def init_socket_maslowcnclogs(app):
    route_type = "socket"
    namespace = "/MaslowCNCLogs"
    print(f"Initializing {route_type} handling for {namespace}")

    @socketio.on("connect", namespace=namespace)
    def log_connect():
        app.data.console_queue.put("connected to log")
        app.data.console_queue.put(request.sid)
        if app.logstreamerthread == None:
            app.logstreamerthread = socketio.start_background_task(
                app.LogStreamer.start, current_app._get_current_object()
            )
            app.logstreamerthread.start()

        socketio.emit(
            "my response", {"data": "Connected", "count": 0}, namespace=namespace
        )


    @socketio.on("disconnect", namespace=namespace)
    def log_disconnect():
        app.data.console_queue.put("Client disconnected")
