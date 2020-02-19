#!/usr/bin/python3
from gpiozero import Button
from gpiozero import LED
from signal import pause
import requests
#from wiiPendant import WiiPendant
import time
from subprocess import check_call

#wp = WiiPendant()
print("setting up buttons")
btnStart = Button(16) #21 # 21,20,16,12
btnPause = Button(20) #20
btnStop = Button(21) #16
btnExit = Button(12) #12
#btnWiimote = Button(26) #26
LEDRun = LED(13)
LEDPause = LED(5)
LEDIR = LED(6) #5.6.13.19
LEDPpower = LED(19)
pause = 0
Buttons = []
LEDs = []
actionList = ["", "WebMCP Running", "Shutdown", "Stop", "Pause", "Play", "Home", "Return to Center", "PlayLED", "PauseLED", "StopLED"]
def getpause():
    return pause
def setpause(newpause):
    pause = newpause
    
def getActionList(self):
    return actionList
def Start():
    print ("start press")
    Send("gcode:playRun")
    print

def Stop():
    print ("Stop press")
    Send("gcode:stopRun")

def Pause():
    print ("Pause press")
    if (getpause() == 0):
        Send("gcode:pauseRun")
        setpause(1)
    else:
        Send("gcode:resumeRun")
        setpause(0)

#def Wii():
#    wp.wiiFlag = not(wp.wiiFlag)

def Exit():
    print ("EXIT")
    Send("system:exit")

def Get(command):
    URL = "http://localhost:5000/GPIO"
    r = requests.get(URL,params = command)
    print (r.text)
    return r.text

def Send(command):
    URL = "http://localhost:5000/GPIO"
    r=requests.put(URL,command)
    print (r)

def Shutdown():
    print ("shutting down system from button press")
    check_call(['sudo', 'poweroff'])

def setup():
    setValues = Put("GPIO")
    print(setValues)
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
    if action == "Stop":
        return "button", Stop
    elif action == "Pause":
        return "button", Pause
    elif action == "Play":
        return "button", Start
    else:
        return "led", None
    
def causeAction(action, onoff):
    for led in LEDs:
        if led[0] == action:
            print(led[1])
            if onoff == "on":
                led[1].on()
            else:
                led[1].off()
            print(led[1])
    if action == "PlayLED" and onoff == "on":
        causeAction("PauseLED", "off")
        causeAction("StopLED", "off")
    if action == "PauseLED" and onoff == "on":
        causeAction("PlayLED", "off")
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

while True:
    time.sleep (2)
    try:
      items = Get("stuff")
      itemss = items.replace('"', '')
      #for i in bad_chars : 
      items = items.replace('\n', '')
      items = items.replace('[', '')
      items = items.replace(']', '')                        
      #print (items)
      details = items.split(",")
      #print (details[0])
      items = details[0].split(":")
      
      #print (items[1])
      gcodeIndex = str(int(items[1].replace('"', '')))
      #print (led1)
      items = details[1].split(":")
      #print (items)
      Flag = str(int(items[1].replace('"', '')))
      if Flag == '0': # run or stopped
        if gcodeIndex == '0': # if 0, then stopped
            print("stopped")
            #LEDStop.on()
            LEDPause.off()
            LEDRun.off()
        else:
            print ("Paused")
            LEDPause.on()
            #LEDStop.off()
            LEDRun.off()
      else:
        print ("Running")
        LEDRun.on()
        #LEDStop.off()
        LEDPause.off()
    except requests.exceptions.RequestException as e:
        print ("error")
        #      fail in silence

 #   if wp.wiiFlag:
 #       wp.wiiFlag = False
 #       if (wp.wiiPendantConnected == True):
 #           print("stopping wiimote")
 #           wp.closeConnection()
 #       else:
 #           print("starting wiimote")
 #           wp.openConnection()
