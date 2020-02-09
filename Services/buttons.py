#!/usr/bin/python3
from gpiozero import Button
from gpiozero import LED
from signal import pause
import requests
from wiiPendant import WiiPendant

wp = WiiPendant()
print("setting up buttons")
btnStart = Button(25) #21
btnPause = Button(20) #20
btnStop = Button(16) #16
btnWiimote = Button(21)
LEDRunn = LEDbtnUp = Button(26) #26
btnDn = Button(19)
btnLf = Button(18)
btnRt = Button(17)

def Start():
    print ("start press")
    Send("gcode:playRun")

def Stop():
    print ("Stop press")
    Send("gcode:stopRun")

def Pause():
    print ("Pause press")
    if (pause == 0):
        Send("gcode:pauseRun")
        pause = 1
    else:
        Send("gcode:resumeRun")
        pause = 0
        
def Wii():
    if (wp.wiiPendantConnected == True):
        print("stopping wiimote")
        wp.closeConnection() 
    else:  
        print("starting wiimote")
        wp.openConnection() 
       
def Exit():
    print ("EXIT")
    Send("system:exit")
    
def Send(command):
    URL = "http://localhost:5000/GPIO"
    r=requests.put(URL,command)
    print (r)
    
btnStart.when_pressed = Start
btnPause.when_pressed = Pause
btnStop.when_pressed = Stop
btnWiimote.when_pressed = Wii
print("waiting for button press")
pause()
