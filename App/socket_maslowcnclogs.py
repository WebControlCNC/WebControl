from app import socketio

from flask import current_app, request


def init_socket_maslowcnclogs(app):
    route_type = "socket"
    namespace = "/MaslowCNCLogs"
    print(f"Initializing {route_type} handling for {namespace}")

    @socketio.on("connect", namespace=namespace)
    def log_connect():
        app.data.console_queue.put(f"client connected to socket for namespace {namespace}")
        app.data.console_queue.put(request.sid)
        socketio.emit(
            "after connect", {"data": "Connected", "count": 0}, namespace=namespace
        )

        # TODO: This requires handling in a completely different way - this breaks socketio.on connect handling
        # if app.logstreamerthread == None:
        #     app.logstreamerthread = socketio.start_background_task(
        #         app.LogStreamer.start, current_app._get_current_object()
        #     )
        #     app.logstreamerthread.start()

    @socketio.on("disconnect", namespace=namespace)
    def log_disconnect():
        app.data.console_queue.put("Client disconnected")
