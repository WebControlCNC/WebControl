#!/usr/bin/python

import cwiid
import time

class WiiPendant():
 '''
    This class will connect to the wiimode with the Bluetooth address specified in the input file
    This class relies on the setpoints in the /etc/cwiid/wminput/ folder of files that has the names of the input fields sent by the wiimote
    'BTN_1', 'BTN_2', 'BTN_A', 'BTN_B', 'BTN_DOWN', 'BTN_HOME', 'BTN_LEFT', 'BTN_MINUS', 'BTN_PLUS', 'BTN_RIGHT', 'BTN_UP', etc.
    It also requires that the connection script with the specific bluetooth ID of the wiimote be in /home/pi/bin/
    to get the ID:
      push 1&2 buttons on wiimote
    start pi blutooth scan:
      hcitool scan
    record wiimote address and put it in the script file:
      mkdir bin
      nano ./binconnectwii.sh
      #!/bin/bash
      sleep 1 # Wait until Bluetooth services are fully initialized
      hcitool dev | grep hci >/dev/null
      if test $? -eq 0 ; then
          wminput -d -c  /home/pi/mywminput 00:19:1D:48:D8:FD &
          wminput -d -c  /home/pi/mywminput 00:22:D7:C2:A6:B9 &
      else
          echo "Blue-tooth adapter not present!"
          exit 1
      fi
    Here are instructions on using it:
      sudo modprobe uinput
      sudo nano /etc/profile.d/10-retropie.sh
      rebootWithoutWiimotes=0
      sudo /home/pi/bin/connectwii.sh
 '''

 def __init__(self):
    self.L = [1,2,4,8]
    self.DISTANCE = [0.1,1,10,100]
    self.Z = [0.1, 0.5, 1, 5]
    self.LED_ON = 2 # default is 10 mm.  range is  = 0.1, 1, 10, 100  Z_LED = 1 # default is 1 m.  range is 0.1, 0.5, 1, 5
    self.MINUS = 0
    self.PLUS = 0
    self.TRIGGER = 0
    self.ZTRIGGER = 0
    self.CONFIRM = -10
    self.StartTiime = time.time()
    self.HOME = 0
    self.A = 0
    self.wm = None
    if self.connect():
      self.wm.led = self.L[self.LED_ON]
      self.wm.rpt_mode = cwiid.RPT_BTN
    else:
      print("no controllers found")

 def connect(self):
      i=2
      while not self.wm:
        try:
          self.wm=cwiid.Wiimote()
#          self.wm.led.battery = 1  # this should show the battery power with the LED's when it connects...
          return(True)
        except RuntimeError:
          if (i>10):
            return(false)
          print ("Error opening wiimote connection" )
          print ("attempt " + str(i))
          i += 1
#end init

 def rumble(self,mode=0):

  if mode == 0: # start up heartbeat = 2 quick rumbles / prompt for confirmation
    self.wm.rumble=True
    time.sleep(.3)
    self.wm.rumble = False
    time.sleep(0.2)
    self.wm.rumble=True
    time.sleep(.3)
    self.wm.rumble = False

  if mode == 1: # shutdown or timeout
    self.wm.rumble=True
    time.sleep(.2)
    self.wm.rumble = False
    time.sleep(0.2)
    self.wm.rumble=True
    time.sleep(.6)
    self.wm.rumble = False

  if mode == 2: # shutdown or timeout
    self.wm.rumble=True
    time.sleep(.6)
    self.wm.rumble = False
    time.sleep(0.2)
    self.wm.rumble=True
    time.sleep(.2)
    self.wm.rumble = False

  if mode >= 30: # shutdown or timeout
    self.wm.rumble=True
    time.sleep(.8)
    self.wm.rumble = False

#end rumble

 def read_buttons(self):

    # not using classic, this is if the remote is standing up though you hold it sideways
    if self.CONFIRM > 0:
      elapsed = 1 - (time.time() - self.startTime)
      if elapsed > 5:
        self.rumble(1)  # cancelled due to timeout
        self.CONFIRM = - 10 # go back to normal

    if (self.wm.state['buttons'] & cwiid.BTN_A):
      if self.TRIGGER == 1:
        if self.CONFIRM > 0:
          self.TRIGGER = 0
          print("HOME POSITION CONFIRMED")
          self.rumble(1)
      elif self.ZTRIGGER == 1:
        self.ZTRIGGER = 0
        if self.CONFIRM > 0:
          print("Z PLUNGE RESET CONFIRMED")
          self.rumble(2)

      else:
        self.A = 1
    else:
        self.A = 0

    if (self.wm.state['buttons'] & cwiid.BTN_1):
      if self.TRIGGER == 0:
        if (self.wm.state['buttons'] & cwiid.BTN_UP):
          print("MOVE LEFT")
          self.rumble(1)
          self.TRIGGER = 1
          self.move_sled("-X",self.DISTANCE[self.LED_ON])
        if (self.wm.state['buttons'] & cwiid.BTN_DOWN):
          print("MOVE RIGHT")
          self.rumble(1)
          self.TRIGGER = 1
          self.RIGHT = 0
          self.move_sled("X",self.DISTANCE[self.LED_ON])
        if (self.wm.state['buttons'] & cwiid.BTN_RIGHT):
          print("MOVE UP")
          self.rumble(1)
          self.TRIGGER = 1
          self.UP = 0
          self.move_sled("Y",self.DISTANCE[self.LED_ON])
        if (self.wm.state['buttons'] & cwiid.BTN_LEFT):
          print("MOVE DOWN")
          self.rumble(1)
          self.TRIGGER = 1
          self.DOWN = 0
          self.move_sled("-Y",self.DISTANCE[self.LED_ON])
        if (self.wm.state['buttons'] & cwiid.BTN_HOME):
          print("SET NEW HOME")
          self.rumble(1)
          self.TRIGGER = 1
          self.rumble(0)
          self.CONFIRM = 500
          self.startTime = time.clock()
    else:
     self.TRIGGER = 0

     if (self.wm.state['buttons'] & cwiid.BTN_2):
      if self.ZTRIGGER == 0:
        self.TRIGGER = 0
        if (self.wm.state['buttons'] & cwiid.BTN_RIGHT):
            print("MOVE Z UP")
            self.rumble(2)
            self.ZTRIGGER = 1
            self.move_z("Z",self.Z[self.LED_ON])
        if (self.wm.state['buttons'] & cwiid.BTN_LEFT):
            print("MOVE Z DOWN")
            self.rumble(2)
            self.ZTRIGGER = 1
            self.move_z("-Z",self.Z[self.LED_ON])
        if (self.wm.state['buttons'] & cwiid.BTN_HOME):
            print("SET PLUNGE to 0")
            self.rumble(2)
            self.ZTRIGGER = 1
            self.rumble(0)
            self.CONFIRM = 200
            self.startTime = time.clock()
     else:
        self.ZTRIGGER = 0
        if (self.wm.state['buttons'] & cwiid.BTN_HOME):
         if self.HOME == 0:
          self.HOME = 1
          print ("MOVE TO HOME")
          self.rumble(1)
        else:
          self.HOME = 0

    if (self.wm.state['buttons'] & cwiid.BTN_MINUS):
      if self.MINUS == 0:
        self.MINUS = 1
        self.LED_ON = self.LED_ON - 1
        if self.LED_ON < 0:
          self.LED_ON = 3
        print("Move Distance is ", self.DISTANCE[self.LED_ON])
        print("Z Distance is ", self.Z[self.LED_ON])
        self.wm.led = self.L[self.LED_ON]
    else:
      self.MINUS = 0

    if (self.wm.state['buttons'] & cwiid.BTN_PLUS):
      if self.PLUS == 0:
        self.PLUS = 1
        self.LED_ON = self.LED_ON + 1
        if self.LED_ON > 3:
          self.LED_ON = 0
        print("Move Distance is ", self.DISTANCE[self.LED_ON])
        print("Z Distance is ", self.Z[self.LED_ON])
        self.wm.led = self.L[self.LED_ON]
    else:
      self.PLUS = 0

  #end button scan
#END class


def main():
  wp = WiiPendant()

  while True:
    wp.read_buttons()

if __name__ == "__main__":
    main()
