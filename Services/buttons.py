#!/usr/bin/python3
from gpiozero import Button
from gpiozero import LED
from signal import pause
import requests
#from wiiPendant import WiiPendant
import time
from subprocess import check_call
import json

#wp = WiiPendant()
print("setting up buttons")
#btnStart = Button(16) #21 # 21,20,16,12
#btnPause = Button(20) #20
#btnStop = Button(21) #16
#btnExit = Button(12) #12
#btnWiimote = Button(26) #26
#LEDRun = LED(13)
#LEDPause = LED(5)
#LEDIR = LED(6) #5.6.13.19
#LEDPpower = LED(19)
runpause = 0
pendantService = False

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

def Exit():
    print ("EXIT")
    Send("system:exit")

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
    #if (pendantService == False):
        
        print("kickstart pendant process (TOTALLY SEPARATE)")
        #mp.set_start_method('spawn')
        #q = mp.Queue()
        #print (q)
        #p = mp.Process(target='/home/pi/buttons/pwiid.sh')
        #print (p)
        #p.start()
        #print(q.get())
        subprocess.run(['/home/pi/buttons/MaslowPendantservice.sh'])
        print ('subprocess started a service')
    
   # else:
        #print('stopping service')
        #subprocess.run('/home/pi/buttons/pwiidshutdown.sh')
       # pendantService = False

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
            elif onoff == "blink":
                led[1].blink()
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
print (LEDs)
while True:
      time.sleep (2)
    #try:
      items = Get('LED','stuff')
      #if (items != None):
      stuff = items # eval(items)
      #print(items)
      print (type(stuff))
      print (stuff)
      for i in range (0, len(stuff)):
          ss = stuff[i].split(":")
          print (ss)
          if (ss[0] == 'flag'): # run or stopped
              flag = ss[1]
          if (ss[0] == 'index'):
              index = ss[1]
          if (ss[0] == 'moving'):
              moving = ss[1]
          if (ss[0] == 'RGC'):
              RGC = ss[1]
          if (ss[0] == 'pausedGcode'):
              pausedGcode = ss[1]
      if (index == '0'):  
        if (flag == '0'): # if 0, then stopped
            print("stopped")
            #LEDStop.on()
            #LEDPause.off()
            LEDs['PlayLED'].off()
        else:
            if (pausedGcode == 'True'):
              print ("Paused")
              #LEDPause.on()
              #LEDStop.off()
              LEDs[0].on()
        if (moving == 'True'):
              print ("Moving")
              LED[1].blink()
      else:
            if (moving == 'True'):
              print ("Running")
              LEDs[0].blink()
              #LEDStop.off()
              #LEDPause.off()
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