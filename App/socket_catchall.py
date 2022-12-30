from app import socketio


def init_socket_catchall(app):
    route_type = "socket"
    app.data.console_queue.put(f"{__name__}: Initializing {route_type} handling for catch all")

    @socketio.on("*")
    def catch_all(event, sid, data):
        app.data.console_queue.put(f"{__name__}: Hit the socket catch_all")
        app.data.console_queue.put(f"{__name__}: Event: {event}")
        app.data.console_queue.put(f"{__name__}: SID: {sid}")
        app.data.console_queue.put(f"{__name__}: Data: {data}")
