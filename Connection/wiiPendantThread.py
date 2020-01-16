from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from DataStructures.data import Data
#from collections import queue
import cwiid
import time


class WiiPendantThread(MakesmithInitFuncs):
 '''
    This class will communicate with the wiimote, decode the button  messages and enque the desired actions.
    Inherits wm from wiiPendant ... or at least it should.
 '''

 def __init__(self):
    """
       set up the flags for interpreting the controls
    """
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

 def rumble(self,mode=0):
  '''
     rumble shakes the wiimote when it connects, when a movement is made, or a setting is confirmed
     Inputs:  mode 0 - heartbeat, 1, shutdown or timeout, 2 sled home reset confirmed, 3 z-axis zero confirmed
  '''
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

  if mode == 2: # sled home reset
    self.wm.rumble=True
    time.sleep(.6)
    self.wm.rumble = False
    time.sleep(0.2)
    self.wm.rumble=True
    time.sleep(.2)
    self.wm.rumble = False

  if mode >= 30: # Z-axis zero
    self.wm.rumble=True
    time.sleep(.8)
    self.wm.rumble = False

#end rumble

 def read_buttons(self):
  
  while True:
    time.sleep(0.01)
    if self.data.wiiPendantPresent == False:
          self.data.wiiPendantConnected = False
          break
    if self.wm == None: 
        #i=2
      while not self.wm:
        try:
          self.wm=cwiid.Wiimote()
          wm.rpt_mode = cwiiid.RPT_BTN
          #          self.wm.led.battery = 1  # this should show the battery power with the LED's when it connects...
          #  return(True)
        except RuntimeError:
          '''
            this is a silent fail if the wiimote is not there... should set something to know that it  isn't there$
          '''
          self.data.wiiPendantConnected = False
          self.wm = None
          break
          #  if (i>10):
          #    return(false)
          #  print ("Error opening wiimote connection" )
          #  print ("attempt " + str(i))
          #  i += 1
    else:
      #  not using classic, this is if the remote is standing up though you hold it sideways
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
            self.data.ui_queue1.put("defineHome")
        elif self.ZTRIGGER == 1:
          self.ZTRIGGER = 0
          if self.CONFIRM > 0:
            print("Z PLUNGE RESET CONFIRMED")
            self.rumble(2)
            self.data.ui_queue1.put("defineZ0")
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
            self.data.ui_queue1.put("move", "left", self.DISTANCE[self.LED_ON])
          if (self.wm.state['buttons'] & cwiid.BTN_DOWN):
            print("MOVE RIGHT")
            self.rumble(1)
            self.TRIGGER = 1
            self.RIGHT = 0
            self.move_sled("X",self.DISTANCE[self.LED_ON])
            self.data.ui_queue1.put("move", "right", self.DISTANCE[self.LED_ON])
          if (self.wm.state['buttons'] & cwiid.BTN_RIGHT):
            print("MOVE UP")
            self.rumble(1)
            self.TRIGGER = 1
            self.UP = 0
            self.move_sled("Y",self.DISTANCE[self.LED_ON])
            self.data.ui_queue1.put("move", "up", self.DISTANCE[self.LED_ON])
          if (self.wm.state['buttons'] & cwiid.BTN_LEFT):
            print("MOVE DOWN")
            self.rumble(1)
            self.TRIGGER = 1
            self.DOWN = 0
            self.move_sled("-Y",self.DISTANCE[self.LED_ON])
            self.data.ui_queue1.put("move", "down", self.DISTANCE[self.LED_ON])
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
            self.data.ui_queue1.put("moveZ", "left", self.DISTANCE[self.LED_ON])
          if (self.wm.state['buttons'] & cwiid.BTN_LEFT):
            print("MOVE Z DOWN")
            self.rumble(2)
            self.ZTRIGGER = 1
            self.move_z("-Z",self.Z[self.LED_ON])
            self.data.ui_queue1.put("move", "left", self.DISTANCE[self.LED_ON])
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
  thread.exit()
  #end button scan
#END class