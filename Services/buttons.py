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

def Start():
    print ("start press")
    Send("gcode:playRun")
    print

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

btnStart.when_pressed = Start
btnPause.when_pressed = Pause
btnStop.when_pressed = Stop
btnExit.when_pressed = Shutdown
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
