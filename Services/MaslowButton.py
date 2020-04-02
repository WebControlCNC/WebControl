#!/usr/bin/python3
from gpiozero import Button
from gpiozero import LED
from signal import pause
import requests
import time
import subprocess
from subprocess import check_call
import json
import os
from os import system, name   # import only system from os 

print("setting up buttons")
runpause = 0
wiiPendantPresent = False
clidisplay = False
flag = '0'
Buttons = []
LEDs = []
index = 0
moving = False
homeX = 0.00
homeY = 0.00
sledX = 0.00
sledY = 0.00
minX = 0.00
minY = 0.00
maxX = 0.00
maxY = 0.00
actionList = ["", "WebMCP Running", "Shutdown", "Stop", "Pause", "Play", "Home", "Return to Center", "PlayLED", "PauseLED", "StopLED"]
start_time = time.time()
end_time = time.time()

def getpause():
    return runpause

def setpause(newpause):
    runpause = newpause
    
def getActionList(self):
    return actionList

def Start():
    print ("start press")
    Send("gcode:startRun")
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
# define our clear function 
def clear(): 
    # for windows 
    if name == 'nt': 
        _ = system('cls')   
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear') 

def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60.
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)
# End hms_string

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
    try:
        items = Get('LED','stuff')
        if (items != None):
            if (flag == "0"):
                if(items["data"]["flag"] == "1"):
                    start_time = time.time()
            else:
                if(items["data"]["flag"] == "0"):
                    stop_time = time.time()
            flag = items["data"]["flag"]
            index = items["data"]["index"]
            moving = items["data"]["moving"]
            zMove = items["data"]["zMove"]
            wiiPendantPresent = bool(items["data"]["wiiPendantPresent"])
            wiiconnected = bool(items["data"]["wiiconnected"])
            clidisplay = bool(items["data"]["clidisplay"])
            sledX = float(items["data"]["sled_location_X"])
            sledY = float(items["data"]["sled_location_y"])
                #"sled_location_z": str(app.data.zval), \
            homeX = float(items["data"]["home_location_x"])
            homeY = float(items["data"]["home_location_y"])
            xmin = items["data"]["gcode_min_x"]
            xmax = float(items["data"]["gcode_max_x"])
            ymin = items["data"]["gcode_min_y"]
            ymax = float(items["data"]["gcode_max_y"])
            #print (index)
            #print (moving)
            #print(items)
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
        if (clidisplay == True):
            clear()
            print("")
            if (flag == '1'):
                print("STATUS - run time: {}".format(hms_string(end_time - start_time)))
                print("")
            else:
                print("STATUS - not running")
                print("")
            if (wiiPendantPresent == True):
                if (wiiconnected == True):
                    print("wiimote: attached")
                else:
                    print("wiimote: disconnected")                
            print("Sled: {:.2f},{:.2f}".format(sledX,sledY))
            print("")
            print("Home: {:.2f},{:.2f}".format(homeX,homeY))
            print("")
            print("Bound box from sled (inches)")
            upper = (ymax - sledY)/25.4
            right = (xmax - sledX)/25.4
            print("Top: {:.2f}".format(upper))
            print("Right: {:.2f}".format(right))
            print("")
            print ("Absolute bounds")
            print("Upper Right: {:.2f}, {:.2f}".format(xmax, ymax))
            print("Lower Left: {:.2f}, {:.2f}".format(xmin,ymin))
            #moving or other temp step, then mention?        
    except:
       # pass
        print ("error with display")
        #       fail in silence