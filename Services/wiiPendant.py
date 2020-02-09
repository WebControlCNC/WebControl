import schedule
import threading
import cwiid
import time


class WiiPendant():
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
      nano ./conwii.sh
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
      ...
      $ sudo apt-get install bluetooth vorbis-tools python-cwiid wminput
      $ sudo tee /etc/udev/rules.d/wiimote.rules << EOF
      > KERNEL=="uinput", MODE="0666"
      > EOF
      sudo service udev restart
      /etc/init.d/bluetooth status
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
    self.wm = None
    self.wiiPendantRequest = ""
    self.wiiPendantConnected = False
    self.wiiFlag = False
    self.debug = True
    if self.debug:
          print(" ---- wii Pendant activated ---- ")
          
 def Send(self,command):
    URL = "http://localhost:5000/pendant"
    try: 
      r=requests.put(URL,command)
      print (r)
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)
        return
    
 def openConnection(self):
    '''
       if the wiiPendantFlag in the config is True, then check if the wiiPendant is already connected
       if not connected, then set t
    '''
    if self.wm == None:
      if self.debug:
            print("wiimote object is empty")
      while not self.wm:
        if self.debug:
            print("trying to connect")
        try:
          self.wm=cwiid.Wiimote()
          self.wm.rpt_mode = cwiid.RPT_BTN
          self.wiiPendantConnected = True
          self.Send("system:connected")
          self.wm.rumble(0)
          print("wii connection success -> read buttons")
          self.wiiPendantConnected = True
          self.wm.led = self.L[self.LED_ON]
        except RuntimeError:
          '''
          this is a silent fail if the wiimote is not there... should set something to know that it  isn't there$
          '''
          self.Send('system:disconnected')
          print("wiimote connection error")
          self.data.wiiPendantConnected = False
          self.wm = None
          return
        sleep(0.5)
      readbuttons() 
       
 def closeConnection(self):
      '''
        tell wiiPendant to shut down
      '''
      wm = None
      self.wiiPendantRequest = "requestToClose"

 def getConnectionStatus(self):
        '''
          get the system handle
        '''
        return self.wiiPendantConnected

 def rumble(self,mode=0):
  '''
     rumble shakes the wiimote when it connects, when a movement is made, or a setting is confirmed
     Inputs:  mode 0 - heartbeat, 1, shutdown or timeout, 2 sled home reset confirmed, 3 z-axis zero confirmed
  '''
  if mode == 0: # start up heartbeat = 2 quick rumbles / prompt for confirmation
    if self.debug:
          print("rumble mode 0")
    self.wm.rumble=True
    time.sleep(.2)
    self.wm.rumble = False
    time.sleep(0.1)
    self.wm.rumble=True
    time.sleep(.2)
    self.wm.rumble = False

  if mode == 1: # shutdown or timeout
    if self.debug:
          print("rumble mode 1")
    self.wm.rumble=True
    time.sleep(.1)
    self.wm.rumble = False
    time.sleep(0.1)
    self.wm.rumble=True
    time.sleep(.3)
    self.wm.rumble = False

  if mode == 2: # sled home reset
    if self.debug:
          print("rumble mode 2")
    self.wm.rumble=True
    time.sleep(.3)
    self.wm.rumble = False
    time.sleep(0.1)
    self.wm.rumble=True
    time.sleep(.1)
    self.wm.rumble = False

  if mode >= 30: # Z-axis zero
    if self.debug:
          print("rumble mode OUT")
    self.wm.rumble=True
    time.sleep(.4)
    self.wm.rumble = False

 #end rumble
 def move_command(self,direction, distance):
      if (('raise' in direction) or ('lower' in direction)):
        command = "zaxis:" + direction + ":" + str(distance)
      else:
        command = "move:" + direction + ":" + str(distance)
      return command
      
 def read_buttons(self):
  ''' 
  in the  self.wm.rpt_mode = cwiid.RPT_BTN button read mode, we scan the input of the wiibmots
  '''
  try:
   while True:
      time.sleep(0.05)
      #  not using classic, this is if the remote is standing up though you hold it sideways
      if (self.wiiPendantConnected == False):
            self.wm = None
            return
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
            self.Send("sled:defineHome")
        elif self.ZTRIGGER == 1:
          self.ZTRIGGER = 0
          if self.CONFIRM > 0:
            print("Z PLUNGE RESET CONFIRMED")
            self.rumble(2)
            self.Send("zAxis:defineZ0")
        elif (self.wm.state['buttons'] & cwiid.BTN_B):
              print("Wii Remote Disconnect - thread dead")
              self.wiiPendantConnected = False
              self.rumble(0)
              wm = None
              return
        else:
          self.A = 1
      else:
        self.A = 0

      if (self.wm.state['buttons'] & cwiid.BTN_1):
        if self.TRIGGER == 0:
          if (self.wm.state['buttons'] & cwiid.BTN_UP):
            print("Wiimote MOVE SLED LEFT")
            self.rumble(1)
            self.TRIGGER = 1
            self.Send(move_command("left", self.DISTANCE[self.LED_ON]))
          if (self.wm.state['buttons'] & cwiid.BTN_DOWN):
            print("Wiimote MOVE SLED RIGHT")
            self.rumble(1)
            self.TRIGGER = 1
            self.RIGHT = 0
            self.Send(move_command("right", self.DISTANCE[self.LED_ON]))
          if (self.wm.state['buttonscp '] & cwiid.BTN_RIGHT):
            print("Wiimote MOVE SLED UP")
            self.rumble(1)
            self.TRIGGER = 1
            self.UP = 0
            self.Send(move_command("up", self.DISTANCE[self.LED_ON]))
          if (self.wm.state['buttons'] & cwiid.BTN_LEFT):
            print("Wiimote MOVE SLED DOWN")
            self.rumble(1)
            self.TRIGGER = 1
            self.DOWN = 0
            self.Send(move_command("down", self.DISTANCE[self.LED_ON]))
          if (self.wm.state['buttons'] & cwiid.BTN_HOME):
            print("Wiimote SET NEW HOME")
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
            print("Wiimote MOVE Z UP")
            self.rumble(2)
            self.ZTRIGGER = 1
            self.Send(move_command("raise", self.Z[self.LED_ON]))
          if (self.wm.state['buttons'] & cwiid.BTN_LEFT):
            print("Wiimote MOVE Z DOWN")
            self.rumble(2)
            self.ZTRIGGER = 1
            self.Send(move_command("lower", self.Z[self.LED_ON]))
          if (self.wm.state['buttons'] & cwiid.BTN_HOME):
            print("Wiimote Reset Z AXIS to 0")
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
            print ("Wiimote MOVE SLED TO HOME")
            self.rumble(1)
        else:
          self.HOME = 0

      if (self.wm.state['buttons'] & cwiid.BTN_MINUS):
        if self.MINUS == 0:
          self.MINUS = 1
          self.LED_ON = self.LED_ON - 1
          if self.LED_ON < 0:
            self.LED_ON = 3
          print("Sled Move Distance is ", self.DISTANCE[self.LED_ON])
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
  except RuntimeError:
      '''
          this is a silent fail if the wiimote is not there... should set something to know that it  isn'$
      '''
      print (" error, connection dropped, thread dead")
      self.wm = None
      self.wiiPendantConnected = False
      return
 #emd read_buttons
#END class

