from app import socketio


def init_socket_catchall(app):
    route_type = "socket"
    print(f"Initializing {route_type} handling for catch all")

    @socketio.on("*")
    def catch_all(event, sid, data):
        print("Hit the socket catch_all")
        print(f"Event: {event}")
        print(f"SID: {sid}")
        print(f"Data: {data}")
