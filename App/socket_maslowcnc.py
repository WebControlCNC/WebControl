from app import socketio

from flask import current_app, json, request


def init_socket_maslowcnc(app):
    route_type = "socket"
    namespace = "/MaslowCNC"
    print(f"Initializing {route_type} handling for {namespace}")

    @socketio.on("my event", namespace=namespace)
    def my_event(msg):
        app.data.console_queue.put(msg["data"])


    @socketio.on("modalClosed", namespace=namespace)
    def modalClosed(msg):
        app.data.logger.resetIdler()
        data = json.dumps({"title": msg["data"]})
        socketio.emit(
            "message",
            {"command": "closeModals", "data": data, "dataFormat": "json"},
            namespace=namespace,
        )


    @socketio.on("contentModalClosed", namespace=namespace)
    def contentModalClosed(msg):
        # Note, this shouldn't be called anymore
        # todo: cleanup
        app.data.logger.resetIdler()
        data = json.dumps({"title": msg["data"]})
        print(data)
        # socketio.emit("message", {"command": "closeContentModals", "data": data, "dataFormat": "json"},
        #              namespace=namespace, )


    """
    todo: cleanup
    not used
    @socketio.on("actionModalClosed", namespace=namespace)
    def actionModalClosed(msg):
        app.data.logger.resetIdler()
        data = json.dumps({"title": msg["data"]})
        socketio.emit("message", {"command": "closeActionModals", "data": data, "dataFormat": "json"},
                    namespace=namespace, )
    """


    @socketio.on("alertModalClosed", namespace=namespace)
    def alertModalClosed(msg):
        app.data.logger.resetIdler()
        data = json.dumps({"title": msg["data"]})
        socketio.emit(
            "message",
            {"command": "closeAlertModals", "data": data, "dataFormat": "json"},
            namespace=namespace,
        )


    @socketio.on("requestPage", namespace=namespace)
    def requestPage(msg):
        print(f"requestPage: {msg}")
        app.data.logger.resetIdler()
        app.data.console_queue.put(request.sid)
        client = request.sid
        try:
            (
                page,
                title,
                isStatic,
                modalSize,
                modalType,
                resume,
            ) = app.webPageProcessor.createWebPage(
                msg["data"]["page"], msg["data"]["isMobile"], msg["data"]["args"]
            )
            # if msg["data"]["page"] != "help":
            #    client = "all"
            data = json.dumps(
                {
                    "title": title,
                    "message": page,
                    "isStatic": isStatic,
                    "modalSize": modalSize,
                    "modalType": modalType,
                    "resume": resume,
                    "client": client,
                }
            )
            socketio.emit(
                "message",
                {"command": "activateModal", "data": data, "dataFormat": "json"},
                namespace=namespace,
            )
        except Exception as e:
            app.data.console_queue.put(e)


    @socketio.on("connect", namespace=namespace)
    def test_connect():
        app.data.console_queue.put("connected")
        app.data.console_queue.put(request.sid)
        if app.uithread == None:
            app.uithread = socketio.start_background_task(
                app.UIProcessor.start, current_app._get_current_object()
            )
            app.uithread.start()

        if not app.data.connectionStatus:
            app.data.console_queue.put(
                "Attempting to re-establish connection to controller"
            )
            app.data.serialPort.openConnection()

        socketio.emit("my response", {"data": "Connected", "count": 0})
        address = app.data.hostAddress
        data = json.dumps({"hostAddress": address})
        print(data)
        socketio.emit(
            "message",
            {"command": "hostAddress", "data": data, "dataFormat": "json"},
            namespace=namespace,
        )
        if app.data.pyInstallUpdateAvailable:
            app.data.ui_queue1.put("Action", "pyinstallUpdate", "on")


    @socketio.on("disconnect", namespace=namespace)
    def test_disconnect():
        app.data.console_queue.put("Client disconnected")


    @socketio.on("action", namespace=namespace)
    def command(msg):
        app.data.logger.resetIdler()
        retval = app.data.actions.processAction(msg)
        if retval == "Shutdown":
            print("Shutting Down")
            socketio.stop()
            print("Shutdown")
        if retval == "TurnOffRPI":
            print("Turning off RPI")
            os.system("sudo poweroff")


    @socketio.on("settingRequest", namespace=namespace)
    def settingRequest(msg):
        app.data.logger.resetIdler()
        # didn't move to actions.. this request is just to send it computed values.. keeping it here makes it faster than putting it through the UIProcessor
        setting, value = app.data.actions.processSettingRequest(
            msg["data"]["section"], msg["data"]["setting"]
        )
        if setting is not None:
            data = json.dumps({"setting": setting, "value": value})
            socketio.emit(
                "message",
                {"command": "requestedSetting", "data": data, "dataFormat": "json"},
                namespace=namespace,
            )


    @socketio.on("updateSetting", namespace=namespace)
    def updateSetting(msg):
        app.data.logger.resetIdler()
        if not app.data.actions.updateSetting(msg["data"]["setting"], msg["data"]["value"]):
            app.data.ui_queue1.put("Alert", "Alert", "Error updating setting")


    @socketio.on("checkForGCodeUpdate", namespace=namespace)
    def checkForGCodeUpdate(msg):
        app.data.logger.resetIdler()
        # this currently doesn't check for updated gcode, it just resends it..
        ## the gcode file might change the active units so we need to inform the UI of the change.
        app.data.ui_queue1.put("Action", "unitsUpdate", "")
        app.data.ui_queue1.put("Action", "gcodeUpdate", "")


    @socketio.on("checkForBoardUpdate", namespace=namespace)
    def checkForBoardUpdate(msg):
        app.data.logger.resetIdler()
        # this currently doesn't check for updated board, it just resends it..
        app.data.ui_queue1.put("Action", "boardUpdate", "")
