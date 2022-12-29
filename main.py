# main.py
from gevent import monkey

monkey.patch_all()

from app import app, socketio

import os
import socket
import threading
import time
import webbrowser

import schedule

from App.data import init_data
from App.route import init_route
from App.socket_maslowcnc import init_socket_maslowcnc
from App.socket_maslowcnclogs import init_socket_maslowcnclogs
from App.socket_mcp import init_socket_mcp

from Background.UIProcessor import UIProcessor  # do this after socketio is declared
from Background.LogStreamer import LogStreamer  # do this after socketio is declared
from Connection.nonVisibleWidgets import NonVisibleWidgets
from WebPageProcessor.webPageProcessor import WebPageProcessor

app = init_data(app)

app.nonVisibleWidgets = NonVisibleWidgets()
app.nonVisibleWidgets.setUpData(app.data)

app.UIProcessor = UIProcessor()
app.webPageProcessor = WebPageProcessor(app.data)
app.LogStreamer = LogStreamer()

## this defines the schedule for running the serial port open connection
def run_schedule():
    while 1:
        schedule.run_pending()
        time.sleep(1)


## this runs the scheduler to check for connections
app.th = threading.Thread(target=run_schedule)
app.th.daemon = True
app.th.start()

## this runs the thread that processes messages from the controller
app.th1 = threading.Thread(target=app.data.messageProcessor.start)
app.th1.daemon = True
app.th1.start()

## this runs the thread that sends debugging messages to the terminal and webmcp (if active)
app.th2 = threading.Thread(target=app.data.consoleProcessor.start)
app.th2.daemon = True
app.th2.start()

## uithread set to None.. will be activated upon first websocket connection from browser
app.uithread = None

## uithread set to None.. will be activated upon first websocket connection from webmcp
app.mcpthread = None

## logstreamerthread set to None.. will be activated upon first websocket connection from log streamer browser
app.logstreamerthread = None

init_route(app)
init_socket_mcp(app)
init_socket_maslowcnc(app)
init_socket_maslowcnclogs(app)


@app.template_filter("isnumber")
def isnumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# def shutdown():
#    print("Shutdown")


if __name__ == "__main__":
    app.debug = False
    app.config["SECRET_KEY"] = "secret!"
    # look for touched file
    app.data.config.checkForTouchedPort()
    webPort = app.data.config.getValue("WebControl Settings", "webPort")
    webPortInt = 5000
    try:
        webPortInt = int(webPort)
        if webPortInt < 0 or webPortInt > 65535:
            webPortInt = 5000
    except Exception as e:
        app.data.console_queue.put(e)
        app.data.console_queue.put("Invalid port assignment found in webcontrol.json")

    print("-$$$$$-")
    print(os.path.abspath(__file__))
    app.data.releaseManager.processAbsolutePath(os.path.abspath(__file__))
    print("-$$$$$-")

    webHost = "http://localhost"
    print(f"opening browser on {webHost}:{webPortInt}")
    webbrowser.open_new_tab(f"{webHost}:{webPortInt}")
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    print(f"setting app data host address to {host_ip}:{webPortInt}")
    app.data.hostAddress = f"{host_ip}:{webPortInt}"

    # app.data.shutdown = shutdown
    socketio.run(app, use_reloader=False, host="0.0.0.0", port=webPortInt)
    # socketio.run(app, host='0.0.0.0')
