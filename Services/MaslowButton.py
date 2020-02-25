#!/usr/bin/python3
from gpiozero import Button
from gpiozero import LED
from signal import pause
import requests
#from wiiPendant import WiiPendant
import time
import subprocess
from subprocess import check_call
#from subprocess import run
import json
import os

#wp = WiiPendant()
print("setting up buttons")
#btnStart = Button(16) #21 # 21,20,16,12
#btnPause = Button(20) #20
#btnStop = Button(21) #16
#btnExit = Button(12) #12
#btnWiimote = Button(26) #26
#LEDRun = LED(26)
#LEDPause = LED(19)
#LEDIR = LED(6) #5.6.13.19
#LEDPower = LED(13)
runpause = 0
wiiPendantPresent = False
flag = 0
Buttons = []
LEDs = []
index = 0
moving = False

actionList = ["", "WebMCP Running", "Shutdown", "Stop", "Pause", "Play", "Home", "Return to Center", "PlayLED", "PauseLED", "StopLED"]

def getpause():
    return runpause

def setpause(newpause):
    runpause = newpause
    
def getActionList(self):
    return actionList

def Start():
    print ("start press")
    Send("gcode:playRun")
    print

def Stop():
    print ("Stop press")
    Send("gcode:stopRun")
    
def getrunPause():
    return(runpause)

def setrunPause(rp:int):
    runpause = rp
    print("set runpause to ", str(rp))

def runPause():
    rp = getrunPause()
    print ("Pause press ", str(rp))
    if (rp == 0):
        setrunPause(1)
        Send("gcode:pauseRun")
    else:
        setrunPause(0)
        Send("gcode:resumeRun")
        
def returnHome():
    print ("return to center")
    Send("gcode:home")
    
def Exit():
    print ("EXIT")
    #Send("system:exit")
    os._exit(0)

def Get(address,command):
    try:
        URL = "http://localhost:5000/" + str(address)
        #print (URL)
        r = requests.get(URL,params = command)
        #print (r.text)
        return r.json()
    except:
        print ('error getting data, check server')
        return ('error:error')
    
def Send(command):
    try:
        URL = "http://localhost:5000/GPIO"
        r=requests.put(URL,command)
        print (r)
    except:
        print ('error sending command, check server')

def Shutdown():
    print ("shutting down system from button press")
    check_call(['sudo', 'poweroff'])

def startPendant():  
    if (wiiPendantPresent):
        print("kickstart pendant process (TOTALLY SEPARATE)")
        try:
            subprocess.run(['sudo','/usr/local/etc/MaslowPendantStart.sh'])
            print ('subprocess started Pendant service')
        except:
            print ('error starting pendant sub process')
   
def setup():
    #retdata = Get("GPIO", "GPIO")
    URL = "http://localhost:5000/GPIO"
    retdata = requests.get(URL,'GPIO')
    setValues = retdata.json()
    
    #print(setValues)
    for setting in setValues:
        if setting["value"] != "":
            pinNumber = int(setting["key"][4:])
            setGPIOAction(pinNumber, setting["value"])

def setGPIOAction(pin, action):
    # first remove pin assignments if already made
    foundButton = None
    for button in Buttons:
        if button.pin.number == pin:
            button.pin.close()
            foundButton = button
            break
    if foundButton is not None:
        Buttons.remove(foundButton)

    foundLED = None
    for led in LEDs:
        if led[1].pin.number == pin:
            led[1].pin.close()
            foundLED = led
            break
    if foundLED is not None:
        LEDs.remove(foundLED)
    #print (LEDs)
    
    type, pinAction = getAction(action)
    if type == "button":
        button = Button(pin)
        button.when_pressed = pinAction
        Buttons.append(button)
        print("set Button ", pin, " with action: ", action)
    if type == "led":
        _led = LED(pin)
        led = (action,_led)
        LEDs.append(led)
        print("set LED with action: " + action)
    #pause()
def getAction(action):
    #print(action)
    if action == "Stop":
        return "button", Stop
    elif action == "Pause":
        return "button", runPause
    elif action == "Play":
        return "button", Start
    elif action == "Shutdown":
        return "button", Shutdown
    elif action == "Pendant":
        return "button", startPendant
    elif "Return" in action:
        print("set return to center as button")
        return "button", returnHome
    else:
        return "led", None
    
def causeAction(action, onoff):
    for led in LEDs:
        if led[0] == action:
            #print(led[1])
            if onoff == "on":
                led[1].on()
            elif onoff == "blink":
                led[1].blink()
            else:
                led[1].off()
            
            #print(led[1])
    if action == "PlayLED" and onoff == "on":
        causeAction("PauseLED", "off")
        causeAction("StopLED", "off")
    if action == "PauseLED" and onoff == "on":
        causeAction("PlayLED", "on")
        causeAction("StopLED", "off")
    if action == "StopLED" and onoff == "on":
        causeAction("PauseLED", "off")
        causeAction("PlayLED", "off")

#btnStart.when_pressed = Start
#btnPause.when_pressed = Pause
#btnStop.when_pressed = Stop
#btnExit.when_pressed = Shutdown
setup()

bad_chars = "'"
#btnWiimote.when_pressed = Wii
print("waiting for button press")
#print (LEDs)
while True:
        time.sleep (3)
    #try:
        items = Get('LED','stuff')
        if (items != None):
            flag = items["data"]["flag"]
            index = items["data"]["index"]
            moving = items["data"]["moving"]
            zMove = items["data"]["zMove"]
            wiiPendantPresent = items["data"]["wiiPendantPresent"]
            #print (flag)
            #print (index)
            #print (moving)
        print(items)
        if (flag == 1):
            RGC = True
            pausedGcode = False          
        if (flag == 2):
            pausedGcode = True
        #if (index == '0'):  
        if (flag == '0'): # if 0, then stopped
            print("stopped")
            causeAction("StopLED", "on")
            if (moving == 'True'):
                print ("Moving")
                causeAction("PlayLED", "blink")
            if (moving == 'True'):
                print ("zMove")
                causeAction("PlayLED", "blink")
        elif (flag == '1'):
            print ("running")
            causeAction("PlayLED", "on")
        elif (flag == '2'):
            print ("Paused")
            causeAction("PauseLED", "on")
    #except:
     #  print ("error")
        #       fail in silence
 #   if wp.wiiFlag:
 #       wp.wiiFlag = False
 #       if (wp.wiiPendantConnected == True):
 #           print("stopping wiimote")
 #           wp.closeConnection()
 #       else:
 #           print("starting wiimote")
 #           wp.openConnection()