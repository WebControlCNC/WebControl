from flask import session
from flask_socketio import emit
from __main__ import socketio

import time
import math
import json

def background_stuff(app):
    with app.app_context():
        while True:
            time.sleep(.001)

            while not app.data.message_queue.empty(): #if there is new data to be read
                message = app.data.message_queue.get()
                # send message to web for display in appropriate column
                if (message!=""):
                    if (message[0]!="[" and message[0]!="<"):
                        sendControllerMessage(message)
                        #socketio.emit('controllerMessage', {'data':message }, namespace='/MaslowCNC')
                    #else:
                        #sendPositionMessage(message)
                        #socketio.emit('positionMessage', {'data':message }, namespace='/MaslowCNC')
                #further process (original Maslow)
                if message[0] == "<":
                    setPosOnScreen(app,message)
'''
            elif message[0] == "$":
                    app.receivedSetting(message)
                elif message[0] == "[":
                    if message[1:4] == "PE:":
                        app.setErrorOnScreen(message)
                    elif message[1:8] == "Measure":
                        measuredDist = float(message[9:len(message)-3])
                        try:
                            app.data.measureRequest(measuredDist)
                        except:
                            print "No function has requested a measurement"
                elif message[0:13] == "Maslow Paused":
                    app.data.uploadFlag = 0
                    app.writeToTextConsole(message)
                elif message[0:8] == "Message:":
                    if app.data.calibrationInProcess and message[0:15] == "Message: Unable":   #this suppresses the annoying messages about invalid chain lengths during the calibration process
                        break
                    app.previousUploadStatus = app.data.uploadFlag
                    app.data.uploadFlag = 0
                    try:
                        app._popup.dismiss()                                           #close any open popup
                    except:
                        pass                                                            #there wasn't a popup to close
                    content = NotificationPopup(continueOn = app.dismiss_popup_continue, text = message[9:])
                    if sys.platform.startswith('darwin'):
                        app._popup = Popup(title="Notification: ", content=content,
                                auto_dismiss=False, size=(360,240), size_hint=(.3, .3))
                    else:
                        app._popup = Popup(title="Notification: ", content=content,
                                auto_dismiss=False, size=(360,240), size_hint=(None, None))
                    app._popup.open()
                    if global_variables._keyboard:
                        global_variables._keyboard.bind(on_key_down=app.keydown_popup)
                        app._popup.bind(on_dismiss=app.ondismiss_popup)
                elif message[0:6] == "ALARM:":
                    app.previousUploadStatus = app.data.uploadFlag
                    app.data.uploadFlag = 0
                    try:
                        app._popup.dismiss()                                           #close any open popup
                    except:
                        pass                                                            #there wasn't a popup to close
                    content = NotificationPopup(continueOn = app.dismiss_popup_continue, text = message[7:])
                    if sys.platform.startswith('darwin'):
                        app._popup = Popup(title="Alarm Notification: ", content=content,
                                auto_dismiss=False, size=(360,240), size_hint=(.3, .3))
                    else:
                        app._popup = Popup(title="Alarm Notification: ", content=content,
                                auto_dismiss=False, size=(360,240), size_hint=(None, None))
                    app._popup.open()
                    if global_variables._keyboard:
                        global_variables._keyboard.bind(on_key_down=app.keydown_popup)
                        app._popup.bind(on_dismiss=app.ondismiss_popup)
                elif message[0:8] == "Firmware":
                    app.data.logger.writeToLog("Ground Control Version " + str(app.data.version) + "\n")
                    app.writeToTextConsole("Ground Control " + str(app.data.version) + "\r\n" + message + "\r\n")

                    #Check that version numbers match
                    if float(message[-7:]) < float(app.data.version):
                        app.data.message_queue.put("Message: Warning, your firmware is out of date and may not work correctly with this version of Ground Control\n\n" + "Ground Control Version " + str(app.data.version) + "\r\n" + message)
                    if float(message[-7:]) > float(app.data.version):
                        app.data.message_queue.put("Message: Warning, your version of Ground Control is out of date and may not work with this firmware version\n\n" + "Ground Control Version " + str(app.data.version) + "\r\n" + message)
                elif message == "ok\r\n":
                    pass #displaying all the 'ok' messages clutters up the display
                else:
                    app.writeToTextConsole(message)
'''
def setPosOnScreen(app, message):
    try:
        with app.app_context():
            startpt = message.find('MPos:') + 5
            endpt = message.find('WPos:')
            numz  = message[startpt:endpt]
            units = "mm" #message[endpt+1:endpt+3]
            valz = numz.split(",")

            app.data.xval  = float(valz[0])
            app.data.yval  = float(valz[1])
            app.data.zval  = float(valz[2])

            if math.isnan(app.data.xval):
                sendControllerMessage("Unable to resolve x Kinematics.")
                app.data.xval = 0
            if math.isnan(app.data.yval):
                sendControllerMessage("Unable to resolve y Kinematics.")
                app.data.yval = 0
            if math.isnan(app.data.zval):
                sendControllerMessage("Unable to resolve z Kinematics.")
                app.data.zval = 0
    except:
        print "One Machine Position Report Command Misread"
        return

    position = {'xval':app.data.xval,'yval':app.data.yval,'zval':app.data.zval}
    sendPositionMessage(position)
    #app.frontpage.setPosReadout(app.xval, app.yval, app.zval)
    #app.frontpage.gcodecanvas.positionIndicator.setPos(app.xval,app.yval,app.data.units)
    #for widget in app.root_window.children:
    #    if isinstance(widget,Popup):
    #        if widget.title == "Maslow Optical Calibration":
    #            widget.content.updatePositionIndicator(app.xval,app.yval,app.data.units)


def sendControllerMessage(message):
    socketio.emit('controllerMessage', {'data':message }, namespace='/MaslowCNC')

def sendPositionMessage(position):
    socketio.emit('positionMessage', {'data':json.dumps(position) }, namespace='/MaslowCNC')
