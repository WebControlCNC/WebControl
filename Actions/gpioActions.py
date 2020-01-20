from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
from gpiozero.pins.mock import MockFactory
from gpiozero import Device, Button, LED


class GPIOActions(MakesmithInitFuncs):

    def __init__(self):
        pass

    '''
    get gpio settings
    '''
    Buttons = []
    LEDs = []

    def setup(self):
        #self.setGPIOAction(2,"Stop")
        setValues = self.data.config.getJSONSettingSection("GPIO Settings")
        #print(setValues)
        for setting in setValues:
            if setting["value"] != "":
                pinNumber = int(setting["key"][4:])
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
        #for led in self.LEDs:
        #    if led.pin.number == pin:
        #        led.pin.close()
        #        foundLED = led
        #        break
        #if foundLED is not None:
        #    self.LEDs.remove(foundLED)

        type, pinAction = self.getAction(action)
        if type == "button":
            button = Button(pin)
            button.when_pressed = pinAction
            self.Buttons.append(button)
            print("set Button with action: "+action)
        #if type == "led":
        #    _led = LED(pin)
        #    led = (action,_led)
        #    self.LEDs.append(led)
        #    print("set LED with action: " + action)

    def getAction(self, action):
        if action == "Stop":
            return "button", self.data.actions.stopRun
        if action == "Pause":
            return "button", self.data.actions.pauseRun
        if action == "Play":
            return "button", self.data.actions.startRun
        else:
            return "led", None
    
    def causeAction(self, action, onoff):
        for led in self.LEDs:
            if led[0] == action:
                if onoff == "on":
                    led[1].on()
                else:
                    led[1].off()
        if action == "PlayLED" and onoff == "on":
            self.causeAction("PauseLED", "off")
            self.causeAction("StopLED", "off")
        if action == "PauseLED" and onoff == "on":
            self.causeAction("PlayLED", "off")
            self.causeAction("StopLED", "off")
        if action == "StopLED" and onoff == "on":
            self.causeAction("PauseLED", "off")
            self.causeAction("PlayLED", "off")
