from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from Connection.wiiPendantThread import WiiPendantThread
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

 def setup(self):
    """
       try every 5 seconds to connect if the wiimote is an option
    """
    
    if self.data.wiiPendantPresent:
      print("scheduling connection attempt every 10 seconds")
      schedule.every(10).seconds.do(self.openConnection)
    else:
      #nothing to do
      print("wii pendant not selected in maslow settings")
      self.wiiPendantRequest = "Not Present"

 def connect(self, *args):
    """
        copied from serial port connect routing to being connecting  - may not be needed
    """
    print("test connect ... need to open connection")
    self.data.config.setValue("Makesmith Settings","wiiPendantPresent",str(self.data.wiiPendant))

 def openConnection(self):
    '''
       if the wiiPendantFlag in the config is True, then check if the wiiPendant is already connected
       if not connected, then set t
    '''
    print("is wii pendant selected?")
    if self.data.wiiPendantPresent:
      print("yes, it is selected")
      print("is the pendant actually connected?")
      if not self.data.wiiPendantConnected:
            print("no it is not connected")
            print("is the wiimote object instantiated")
            if self.wm == None:
              print("no, it is not instantiated")
              while not self.wm:
               print("trying to connect")
               try:
                 self.wm=cwiid.Wiimote()
                 self.wm.rumble=True
                 time.sleep(.3)
                 self.wm.rumble = False
                 time.sleep(0.2)
                 self.wm.rumble=True
                 time.sleep(.3)
                 self.wm.rumble = False
                 x = wiiPendantThread()
                 x.data = self.data
                 self.th = threading.Thread(target=x.readbuttons)
                 self.th.daemon = True
                 self.th.start()

   #          self.wm.led.battery = 1  # this should show the battery power with the LED's when it connects...
        #  return(True)
               except RuntimeError:
                 '''
                 this is a silent fail if the wiimote is not there... should set something to know that it  isn't there$
                 '''
        #  if (i>10):
        #    return(false)
        #  print ("Error opening wiimote connection" )
        #  print ("attempt " + str(i))
        #  i += 1

            #self.data.ui_queue1.put("Action", "wiiPendantConnected",{'status': 'False'})
      else:
            self.data.ui_queue1.put("Action", "connectionStatus",{'status': 'True'})

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
