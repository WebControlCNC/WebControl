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
        for led in self.LEDs:
            if led.pin.number == pin:
                led.pin.close()
                foundLED = led
                break
        if foundLED is not None:
            self.LEDs.remove(foundLED)

        type, pinAction = self.getAction(action)
        if type == "button":
            button = Button(pin)
            button.when_pressed = pinAction
            self.Buttons.append(button)


    def getAction(self,action):
        if action == "Stop":
            return "button", self.data.actions.stopRun
        if action == "Pause":
            return "button", self.data.actions.pauseRun
        if action == "Play":
            return "button", self.data.actions.startRun
