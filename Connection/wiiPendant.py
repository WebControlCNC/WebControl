from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from Connection.wiiPendantThread import WiiPendantThread
#from DataStructures import data
import schedule
import threading
import cwiid
import time


class WiiPendant(MakesmithInitFuncs):
 '''
    This class will start the communication thread for the wiimote Bluetooth connection
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
 wiiPendantRequest = ""
 wm = None
 debug = True
 th = None
 
 def setup(self):
    """
       try every 5 seconds to connect if the wiimote is an option
    """
    self.data.wiiPendantPresent = self.data.config.getValue("Maslow Settings", "wiiPendantPresent")
    
    #if self.data.wiiPendantPresent:
    if self.debug:
          print("scheduling connection attempt every 10 seconds")
    schedule.every(10).seconds.do(self.openConnection)
    #else:
      #nothing to do
    if self.debug:
            print("wii pendant not selected in maslow settings")
      #self.wiiPendantRequest = "Not Present"

 def connect(self, *args):
    """
        copied from serial port connect routing to being connecting  - may not be needed
    """
    if self.debug:
          print("test connect ... need to open connection")
    self.data.config.setValue("Makesmith Settings","wiiPendantPresent",str(self.data.wiiPendant))

 def openConnection(self):
    '''
       if the wiiPendantFlag in the config is True, then check if the wiiPendant is already connected
       if not connected, then set t
    '''
    if self.debug:
        print("checking wiimote connection")
    if self.data.wiiPendantPresent:
      if self.debug:
            print("User has Activated wiimote in menu")
            #print("is the pendant actually running?")
      if not self.data.wiiPendantConnected:
            if self.debug:
                  print("Wiimote connection flag is false")
                  #print("is the wiimote object instantiated")
            if self.wm == None:
              if self.debug:
                    print("wiimote object is empty")
              while not self.wm:
               if self.debug:
                   print("trying to connect")
               try:
                 self.wm=cwiid.Wiimote()
                 wm.rpt_mode = cwiid.RPT_BTN
                 self.wm.rumble(0)
                 print("wii connection success, spawning thread")
                 x = WiiPendantThread()
                 #x.setUpData(data)
                 x.data = self.data
                 self.th = threading.Thread(target=x.read_buttons)
                 self.th.daemon = True
                 self.th.start()
                 self.data.wiiPendantConnected = True
               except RuntimeError:
                 '''
                 this is a silent fail if the wiimote is not there... should set something to know that it  isn't there$
                 '''
                 print("wiimote connection error")
     else:
            self.data.ui_queue1.put("Action", "connectionStatus",{'status': 'True'})
    else:
        if self.th != None:
                self.th.join()
          
 def closeConnection(self):
        '''
           tell wiiPendant to shut down
        '''
        self.wiiPendantRequest = "requestToClose"

 def getConnectionStatus(self):
        '''
          get the system handle
        '''
        return self.wiiPendantRequest

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
    self.wm = None
    if debug:
          print("initialized thread variables")

 def rumble(self,mode=0):
  '''
     rumble shakes the wiimote when it connects, when a movement is made, or a setting is confirmed
     Inputs:  mode 0 - heartbeat, 1, shutdown or timeout, 2 sled home reset confirmed, 3 z-axis zero confirmed
  '''
  if mode == 0: # start up heartbeat = 2 quick rumbles / prompt for confirmation
    if debug:
          print("rumble mode 0")
    self.wm.rumble=True
    time.sleep(.2)
    self.wm.rumble = False
    time.sleep(0.1)
    self.wm.rumble=True
    time.sleep(.2)
    self.wm.rumble = False

  if mode == 1: # shutdown or timeout
    if debug:
          print("rumble mode 1")
    self.wm.rumble=True
    time.sleep(.1)
    self.wm.rumble = False
    time.sleep(0.1)
    self.wm.rumble=True
    time.sleep(.3)
    self.wm.rumble = False

  if mode == 2: # sled home reset
    if debug:
          print("rumble mode 2")
    self.wm.rumble=True
    time.sleep(.3)
    self.wm.rumble = False
    time.sleep(0.1)
    self.wm.rumble=True
    time.sleep(.1)
    self.wm.rumble = False

  if mode >= 30: # Z-axis zero
    if debug:
          print("rumble mode OUT")
    self.wm.rumble=True
    time.sleep(.4)
    self.wm.rumble = False

#end rumble

 def read_buttons(self):
  
  if self.data.wiiPendantPresent == False:
      if self.wm != None
        self.wm = None
        self.data.wiiPendantConnected = False
      return
  while True:
    time.sleep(0.05)
    #self.data.wiiPendantPresent = self.data.config.getValue("Maslow Settings", "wiiPendantPresent")
    if self.data.wiiPendantPresent == False:
          print("wii thread running, but user has disabled option")
          if self.wm = None
          self.data.wiiPendantConnected = False
          return
    if self.data.wiiPendantConnected == False and self.wm == None:
      print("Establishing wii mote connectiond")
      while not self.wm:
        try:
          self.wm=cwiid.Wiimote()
          self.wm.rpt_mode = cwiid.RPT_BTN
          self.rumble(0)
          self.data.wiiPendantConnected = True
          self.wm.led = self.L[self.LED_ON]
        except RuntimeError:
          '''
            this is a silent fail if the wiimote is not there... should set something to know that it  isn't there$
          '''
          self.data.wiiPendantConnected = False
          self.wm = None
          return # closes the thread?
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
  return
  thread.exit()
#END class

