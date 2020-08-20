from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from gpiozero.pins.mock import MockFactory
from gpiozero import Device, Button, LED
from signal import pause

class GPIOActions(MakesmithInitFuncs):

    def __init__(self):
        pass

    '''
    get gpio settings
    '''
    Buttons = []
    LEDs = []
    actionList = ["","Spindle On", "Spindle Off", "Shutdown", "Stop", "Pause", "Play", "Set Home", "Go Home", "Return to Center", "PlayLED", "PauseLED", "StopLED", "Tri_LED_RED","Tri_LED_GREEN","Tri_LED_BLUE" ]
    
    LEDStatusList = ["Idle",
                     "At Home",
                     "Homing",
                     "Run",
                     "Sled Moving",
                     "Calibrating",
                     "Paused",
                     "Cutting",
                     "Off",
                     "Z Moving",
                     "Error"]
    
    LEDColorList = ["",
                    "Off",
                    "Red On",
                    "Red Blink",
                    "Red BlinkFast",
                    "Red BlinkSlow",
                    "Yellow On",
                    "Yellow Blink",
                    "Yellow BlinkFast",
                    "Yellow BlinkSlow",
                    "Green On",
                    "Green Blink",
                    "Green BlinkFast",
                    "Green BlinkSlow",
                    "Cyan On",
                    "Cyan Blink",
                    "Cyan BlinkFast",
                    "Cyan BlinkSlow",
                    "Blue On",
                    "Blue Blink",
                    "Blue BlinkFast",
                    "Blue BlinkSlow",
                    "Magenta On",
                    "Magenta Blink",
                    "Magenta BlinkFast",
                    "Magenta BlinkSlow",
                    "White On",
                    "White Blink",
                    "White BlinkFast",
                    "White BlinkSlow"
                    ]
    
    def getActionList(self):
        return self.actionList
    
    def getLEDStatusList(self):
        return self.LEDStatusList
    
    def getLEDColorList(self):
        return self.LEDColorList
    
    def getLEDColors(self):
        return self.LEDColors
    
    def getLEDBehaviorList(self):
        return self.LEDBehaviorList
    
    def setup(self):
        #self.setGPIOAction(2,"Stop")
        setValues = self.data.config.getJSONSettingSection("GPIO Settings")
        self.data.RGB_LED = self.data.config.getValue("Maslow Settings","TriColorLED")
        self.data.GPIOButtonService = self.data.config.getValue("Maslow Settings","MaslowButtonService")
        if (self.data.GPIOButtonService):
            self.data.wiiPendantPresent = self.data.config.getValue("Maslow Settings","wiiPendantPresent")
            self.clidisplay = self.data.config.getValue("Maslow Settings", "clidisplay")
        #print(setValues)
        for setting in setValues:
            if setting["value"] != "":
                pinNumber = int(setting["key"][4:])
                if (self.data.GPIOButtonService == False): # if MaslowButton.py is not running then set up gpio in this process
                    self.setGPIOAction(pinNumber, setting["value"])

    def setGPIOAction(self,pin, action):
        # first remove pin assignments if already made
        foundButton = None
        for button in self.Buttons:
            if button.pin.number == pin:
                button.pin.close()
                foundButton = button
                break
        if foundButton is not None:
            self.Buttons.remove(foundButton)

        foundLED = None
        for led in self.LEDs:
            if led[1].pin.number == pin:
                led[1].pin.close()
                foundLED = led
                break
        if foundLED is not None:
            self.LEDs.remove(foundLED)

        type, pinAction = self.getAction(action)
        if type == "button":
            button = Button(pin)
            button.when_pressed = pinAction
            self.Buttons.append(button)
            print("set Button with action: "+action)
        if ((type == "led") and not (self.data.GPIOButtonService)):
            _led = LED(pin)
            led = (action,_led)
            self.LEDs.append(led)
            print("set LED with action: " + action)
            #if (self.data.tricolor):
                # TODO implement color as a function of LEDStatus
               # pass
    def getAction(self, action):
        '''
        buttons cause actions
        '''
        if action == "Stop":
            return "button", self.data.actions.stopRun
        elif action == "Pause":
            return "button", self.data.actions.pauseRun
        elif action == "Play":
            return "button", self.data.actions.startRun
        else:
            return "led", None
        
    def runrun(self):
        print("gpio button press detected")
        self.data.actions.startRun()
        
    def causeAction(self, action, onoff):
        for led in self.LEDs:
            if led[0] == action:
                print(led[1])
                if onoff == "on":
                    led[1].on()
                else:
                    led[1].off()
                print(led[1])
        if action == "PlayLED" and onoff == "on":
            self.causeAction("PauseLED", "off")
            self.causeAction("StopLED", "off")
        if action == "PauseLED" and onoff == "on":
            self.causeAction("PlayLED", "off")
            self.causeAction("StopLED", "off")
        if action == "StopLED" and onoff == "on":
            self.causeAction("PauseLED", "off")
            self.causeAction("PlayLED", "off")

