"""

This file provides a single dict which contains all of the details about the
various settings.  It also has a number of helper functions for interacting
and using the data in this dict.

"""
import json
import re
import os, sys
import math
from shutil import copyfile
from pathlib import Path
import time
import glob

from __main__ import app
from DataStructures.makesmithInitFuncs import MakesmithInitFuncs


class Config(MakesmithInitFuncs):
    settings = {}
    defaults = {}
    home = "."
    home1 = "."
    firstRun = False

    def __init__(self):
        self.home = str(Path.home())
        if hasattr(sys, '_MEIPASS'):
            self.home1 = os.path.join(sys._MEIPASS)
            print(self.home1)
        print("Initializing Configuration")
        if not os.path.isdir(self.home+"/.WebControl"):
            print("creating "+self.home+"/.WebControl directory")
            os.mkdir(self.home+"/.WebControl")
        if not os.path.exists(self.home+"/.WebControl/webcontrol.json"):
            print("copying defaultwebcontrol.json to "+self.home+"/.WebControl/")
            copyfile(self.home1+"/defaultwebcontrol.json",self.home+"/.WebControl/webcontrol.json")
            self.firstRun = True
        if not os.path.isdir(self.home+"/.WebControl/gcode"):
            print("creating "+self.home+"/.WebControl/gcode directory")
            os.mkdir(self.home+"/.WebControl/gcode")
        if not os.path.isdir(self.home+"/.WebControl/imports"):
            print("creating "+self.home+"/.WebControl/imports directory")
            os.mkdir(self.home+"/.WebControl/imports")
        if not os.path.isdir(self.home+"/.WebControl/boards"):
            print("creating "+self.home+"/.WebControl/boards directory")
            os.mkdir(self.home+"/.WebControl/boards")
        with open(self.home+"/.WebControl/webcontrol.json", "r") as infile:
            self.settings = json.load(infile)
        # load default and see if there is anything missing.. if so, add it
        with open(self.home1+"/defaultwebcontrol.json", "r") as infile:
            self.defaults = json.load(infile)
        updated = False
        for section in self.defaults:
            sectionFound = False
            for x in range(len(self.defaults[section])):
                found = False
                for _section in self.settings:
                    if _section == section:
                        sectionFound = True
                        for y in range(len(self.settings[_section])):
                           if self.defaults[section][x]["key"] == self.settings[_section][y]["key"]:
                               found = True
                               break
                if found == False:
                    if sectionFound:
                        print("section found")
                    else:
                        print("section not found")
                        self.settings[section]=[]
                    print(section+"->"+self.defaults[section][x]["key"]+" was not found..")
                    t = {}
                    if "default" in self.defaults[section][x]:
                        t["default"]=self.defaults[section][x]["default"]
                    if "desc" in self.defaults[section][x]:
                        t["desc"]=self.defaults[section][x]["desc"]
                    if "firmwareKey" in self.defaults[section][x]:
                        t["firmwareKey"]=self.defaults[section][x]["firmwareKey"]
                    if "key" in self.defaults[section][x]:
                        t["key"]=self.defaults[section][x]["key"]
                    if "section" in self.defaults[section][x]:
                        t["section"]=self.defaults[section][x]["section"]
                    if "title" in self.defaults[section][x]:
                        t["title"]=self.defaults[section][x]["title"]
                    if "type" in self.defaults[section][x]:
                        t["type"]=self.defaults[section][x]["type"]
                    if "value" in self.defaults[section][x]:
                        t["value"]=self.defaults[section][x]["value"]
                    if "options" in self.defaults[section][x]:
                        t["options"]=self.defaults[section][x]["options"]

                    self.settings[section].append(t)
                    print("added "+section+"->"+self.settings[section][len(self.settings[section])-1]["key"])
                    updated = True

        if updated:
            with open(self.home+"/.WebControl/webcontrol.json", "w") as outfile:
                # print ("writing file")
                json.dump(
                    self.settings, outfile, sort_keys=True, indent=4, ensure_ascii=False
                )

    def checkForTouchedPort(self):
        home = self.home
        path = home+"/.WebControl/webcontrol-*.port"
        print(path)
        try:
            for filename in glob.glob(path):
                print(filename)
                port = filename.split("-")
                port = port[1].split(".port")
                print(port[0])
                self.data.config.setValue("WebControl Settings", "webPort", port[0])
                os.remove(filename)
        except Exception as e:
            print(e)
            return False
        return True

    def getHome(self):
        return self.home

    def getJSONSettings(self):
        return self.settings

    def updateQuickConfigure(self, result):
        if result["kinematicsType"] == "Quadrilateral":
            self.setValue("Advanced Settings", "kinematicsType", "Quadrilateral")
        else:
            self.setValue("Advanced Settings", "kinematicsType", "Triangular")
        self.setValue("Advanced Settings", "rotationRadius", result["rotationRadius"])
        self.setValue(
            "Advanced Settings", "chainOverSprocket", result["chainOverSprocket"]
        )
        self.setValue("Maslow Settings", "motorSpacingX", result["motorSpacingX"])
        self.setValue("Maslow Settings", "motorOffsetY", result["motorOffsetY"])
        return True

    def setValue(self, section, key, value, recursionBreaker=False, isImporting = False):
        updated = False
        found = False
        t0=time.time()
        changedValue = None
        changedKey = None
        for x in range(len(self.settings[section])):
            if self.settings[section][x]["key"].lower() == key.lower():
                found = True
                if self.settings[section][x]["type"] == "float":
                    try:
                        storedValue = self.settings[section][x]["value"]
                        self.settings[section][x]["value"] = float(value)
                        updated = True
                        if storedValue != float(value):
                            self.processChange(self.settings[section][x]["key"],float(value))
                        if "firmwareKey" in self.settings[section][x]:
                            self.syncFirmwareKey(
                                self.settings[section][x]["firmwareKey"], storedValue, isImporting,
                            )
                        break
                    except:
                        break
                elif self.settings[section][x]["type"] == "int":
                    try:
                        storedValue = self.settings[section][x]["value"]
                        self.settings[section][x]["value"] = int(value)
                        if storedValue != int(value):
                            self.processChange(self.settings[section][x]["key"], int(value))
                        updated = True
                        if "firmwareKey" in self.settings[section][x]:
                            if self.settings[section][x]["firmwareKey"] != 85:
                                self.syncFirmwareKey(
                                    self.settings[section][x]["firmwareKey"],
                                    storedValue,
                                    isImporting,
                                )
                    except:
                        break
                elif self.settings[section][x]["type"] == "bool":
                    try:
                        #print(str(self.settings[section][x]["key"])+" found")
                        if isinstance(value, bool):
                            if value:
                                value = "on"
                            else:
                                value = "off"
                        if value == "on":
                            storedValue = self.settings[section][x]["value"]
                            self.settings[section][x]["value"] = 1
                            updated = True
                            if "firmwareKey" in self.settings[section][x]:
                                self.syncFirmwareKey(
                                    self.settings[section][x]["firmwareKey"],
                                    storedValue,
                                    isImporting,
                                )
                        else:
                            storedValue = self.settings[section][x]["value"]
                            self.settings[section][x]["value"] = 0
                            updated = True
                            if "firmwareKey" in self.settings[section][x]:
                                self.syncFirmwareKey(
                                    self.settings[section][x]["firmwareKey"],
                                    storedValue,
                                    isImporting,
                                )
                        break
                    except:
                        break
                else:
                    storedValue = self.settings[section][x]["value"]
                    self.settings[section][x]["value"] = value
                    if storedValue != value:
                        self.processChange(self.settings[section][x]["key"], value)
                    updated = True
                    if "firmwareKey" in self.settings[section][x]:
                        self.syncFirmwareKey(
                            self.settings[section][x]["firmwareKey"], storedValue, isImporting,
                        )
                    break
        if not found:
            # must be a turned off checkbox.. what a pain to figure out
            #print(str(self.settings[section][x]["key"])+" not found")
            if self.settings[section][x]["type"] == "bool":
                self.data.console_queue.put(self.settings[section][x]["key"])
                storedValue = self.settings[section][x]["value"]
                self.settings[section][x]["value"] = 0

                if "firmwareKey" in self.settings[section][x]:
                    # print "syncing3 false bool at:"+str(self.settings[section][x]['firmwareKey'])
                    self.syncFirmwareKey(
                        self.settings[section][x]["firmwareKey"], storedValue
                    )
                updated = True
        if updated:
            if not recursionBreaker:
                self.computeSettings(None, None, None, True)
            with open(self.home+"/.WebControl/webcontrol.json", "w") as outfile:
                # print ("writing file")
                json.dump(
                    self.settings, outfile, sort_keys=True, indent=4, ensure_ascii=False
                )

    def updateSettings(self, section, result):
        for x in range(len(self.settings[section])):
            setting = self.settings[section][x]["key"]
            if setting in result:
                resultValue = result[setting]
            else:
                resultValue = 0
            strValue = setting+" = "+str(resultValue)
            self.data.console_queue.put(strValue)
            #do a special check for comport because if its open, we need to close existing connection
            if setting == "COMport":
                currentSetting = self.data.config.getValue(section, setting)
                if currentSetting != resultValue:
                    if self.data.connectionStatus == 1:
                        self.data.requestSerialClose = True
                        self.data.console_queue.put("closing serial connection")
            self.setValue(section, setting, resultValue, recursionBreaker=False, isImporting = False)
        self.data.console_queue.put("settings updated")

    def getJSONSettingSection(self, section):
        """
        This generates a JSON string which is used to construct the settings page
        """
        options = []
        if section in self.settings:
            options = self.settings[section]
        for option in options:
            option["section"] = section
            if "desc" in option and "default" in option:
                if (
                    not "default setting:" in option["desc"]
                ):  # check to see if the default text has already been added
                    option["desc"] += "\ndefault setting: " + str(option["default"])
        return options

    def getDefaultValueSection(self, section):
        """
        Returns a dict with the settings keys as the key and the default value
        of that setting as the value for the section specified
        """
        ret = {}
        if section in self.settings:
            for option in self.settings[section]:
                if "default" in option:
                    ret[option["key"]] = option["default"]
                    break
        return ret

    def getDefaultValue(self, section, key):
        """
        Returns the default value of a setting
        """
        ret = None
        if section in self.settings:
            for option in self.settings[section]:
                if option["key"] == key and "default" in option:
                    ret = option["default"]
                    break
        return ret

    def getFirmwareKey(self, section, key):

        ret = None
        if section in self.settings:
            for option in self.settings[section]:
                if option["key"] == key and "firmwareKey" in option:
                    ret = option["firmwareKey"]
                    break
        return ret

    def getValue(self, section, key):
        """
        Returns the actual value of a setting
        """
        ret = None
        if section in self.settings:
            for option in self.settings[section]:
                if option["key"] == key:
                    ret = option["value"]
                    break
        return ret

    def syncFirmwareKey(self, firmwareKey, value, isImporting=False, useStored=False, data=None):
        # print "firmwareKey from sync:"+str(firmwareKey)
        # print "value from sync:"+str(value)
        for section in self.settings:
            for option in self.settings[section]:
                if "firmwareKey" in option and option["firmwareKey"] == firmwareKey:
                    if self.data.controllerFirmwareVersion > 100 or ("custom" not in option or option["custom"] != 1):
                        storedValue = option["value"]
                        if option["key"] == "spindleAutomate":
                            if storedValue == "Servo":
                                storedValue = 1
                            elif storedValue == "Relay_High":
                                storedValue = 2
                            elif storedValue == "Relay_Low":
                                storedValue = 3
                            else:
                                storedValue = 0
                            if value == "Servo":
                                value = 1
                            elif value == "Relay_High":
                                value = 2
                            elif value == "Relay_Low":
                                value = 3
                            else:
                                value = 0

                        if firmwareKey == 85:
                            if self.data.controllerFirmwareVersion >= 100:
                                print(self.data.controllerFirmwareVersion)
                                self.data.console_queue.put("firmwareKey = 85")
                                if storedValue != "":
                                    self.sendErrorArray(firmwareKey, storedValue, data)
                                pass
                        elif useStored is True:
                            strValue = self.firmwareKeyString(firmwareKey,storedValue)
                            app.data.gcode_queue.put(strValue)
                            #app.data.gcode_queue.put("$" + str(firmwareKey) + "=" + str(storedValue))
                            self.data.holeyKinematics.updateSetting(firmwareKey, storedValue)
                        elif firmwareKey >= 87 and firmwareKey <= 98:
                            if self.data.controllerFirmwareVersion >= 100:
                                if not self.isPercentClose(float(storedValue), float(value)):
                                    if not isImporting:
                                        strValue = self.firmwareKeyString(firmwareKey, storedValue)
                                        app.data.gcode_queue.put(strValue)
                                        self.data.holeyKinematics.updateSetting(firmwareKey, storedValue)
                                        # app.data.gcode_queue.put("$" + str(firmwareKey) + "=" + str(storedValue))
                                else:
                                    break
                        elif not self.isClose(float(storedValue), float(value)) and not isImporting:
                            strValue = self.firmwareKeyString(firmwareKey, storedValue)
                            app.data.gcode_queue.put(strValue)
                            self.data.holeyKinematics.updateSetting(firmwareKey, storedValue)
                            # app.data.gcode_queue.put("$" + str(firmwareKey) + "=" + str(storedValue))
                        else:
                            break
        return

    def isPercentClose(self, a, b, rel_tol = 0.0001):
        if b != 0:
            c = abs( abs(a/b) - 1.0)
            if c < rel_tol:
                return True
            else:
                return False
        else:
            return self.isClose(a, b)

    def isClose(self, a, b, rel_tol=1e-06):
        """
        Takes two values and returns true if values are close enough in value
        such that the difference between them is less than the significant
        figure specified by rel_tol.  Useful for comparing float values on
        arduino adapted from https://stackoverflow.com/a/33024979
        """
        c = abs(a - b) <= rel_tol * max(abs(a), abs(b))
        return c

    def parseErrorArray(self, value, asFloat):

        # not the best programming, but I think it'll work
        xErrors = [[0 for x in range(15)] for y in range(31)]
        yErrors = [[0 for x in range(15)] for y in range(32)]

        index = 0
        xCounter = 0
        yCounter = 0
        val = ""
        while index < len(value):
            while (index < len(value)) and (value[index] != ","):
                val += value[index]
                index += 1
            index += 1
            xErrors[xCounter][yCounter] = int(val)
            # print str(xCounter)+", "+str(yCounter)+", "+str(xErrors[xCounter][yCounter])
            val = ""
            xCounter += 1
            if xCounter == 31:
                xCounter = 0
                yCounter += 1
            if yCounter == 15:
                xCounter = 0
                yCounter = 0
                while index < len(value):
                    while (index < len(value)) and (value[index] != ","):
                        val += value[index]
                        index += 1
                    index += 1
                    # print str(xCounter)+", "+str(yCounter)+": "+val+"->"+str(len(val))
                    yErrors[xCounter][yCounter] = int(val)
                    val = ""
                    xCounter += 1
                    if xCounter == 31:
                        xCounter = 0
                        yCounter += 1
                    if yCounter == 15:
                        break

        if asFloat == False:
            return xErrors, yErrors
        else:
            xFloatErrors = [[0.0 for x in range(15)] for y in range(31)]
            yFloatErrors = [[0.0 for x in range(15)] for y in range(32)]
            for x in range(31):
                for y in range(15):
                    xFloatErrors[x][y] = float(xErrors[x][y]) / 1000.0
                    yFloatErrors[x][y] = float(yErrors[x][y]) / 1000.0
            return xFloatErrors, yFloatErrors

    def sendErrorArray(self, firmwareKey, value, data):
        # parse out the array from string and then send them using the $O command
        xErrors, yErrors = self.parseErrorArray(value, False)
        # now send the array:
        for x in range(0, 31):  # 31
            for y in range(0, 15):  # 15
                app.data.gcode_queue.put(
                    "$O="
                    + str(x)
                    + ","
                    + str(y)
                    + ","
                    + str(xErrors[x][y])
                    + ","
                    + str(yErrors[x][y])
                    + " "
                )
        # if you send a 31,15 , it will trigger a save to EEPROM
        app.data.gcode_queue.put(
            "$O=" + str(31) + "," + str(15) + "," + str(42) + "," + str(42) + " "
        )

    def receivedSetting(self, message):
        """
        This parses a settings report from the machine, usually received in
        response to a $$ request.  If the value received does not match the
        expected value.
        """
        parameter, position = self.parseFloat(message, 0)
        value, position = self.parseFloat(message, position)
        if parameter is not None and value is not None:
            self.syncFirmwareKey(int(parameter), value)

    def parseFloat(self, text, position=0):
        """
            Takes a string and parses out the float found at position default to 0
            returning a list of the matched float and the ending
            position of the float
            """
        # This regex comes from a python docs recommended
        regex = re.compile("[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?")
        match = regex.search(text[position:])
        if match:
            return (float(match.group(0)), match.end(0))
        else:
            return (None, position)

    def computeSettings(self, section, key, value, doAll=False):
        # Update Computed settings
        if key == "loggingTimeout" or doAll is True:
            loggingTimeout = self.getValue("WebControl Settings", "loggingTimeout")
            #self.data.console_queue.put(str(value))
            #self.data.console_queue.put(str(loggingTimeout))
            self.data.logger.setLoggingTimeout(loggingTimeout)
        if key == "kinematicsType" or doAll is True:
            if doAll is True:
                value = self.getValue("Advanced Settings", "kinematicsType")
            currentValue = self.getValue("Computed Settings", "kinematicsTypeComputed")
            if value == "Quadrilateral":
                if currentValue != "1":
                    self.setValue("Computed Settings", "kinematicsTypeComputed", "1", True)
            else:
                if currentValue != "2":
                    self.setValue("Computed Settings", "kinematicsTypeComputed", "2", True)

        if key == "gearTeeth" or key == "chainPitch" or doAll is True:
            gearTeeth = float(self.getValue("Advanced Settings", "gearTeeth"))
            chainPitch = float(self.getValue("Advanced Settings", "chainPitch"))
            distPerRot = gearTeeth * chainPitch
            currentdistPerRot = self.getValue("Computed Settings", "distPerRot")
            if currentdistPerRot != str(distPerRot):
                self.setValue("Computed Settings", "distPerRot", str(distPerRot), True)

        if key == "enablePosPIDValues" or doAll is True:
            for key in ("KpPos", "KiPos", "KdPos", "propWeight"):
                if int(self.getValue("Advanced Settings", "enablePosPIDValues")) == 1:
                    value = float(self.getValue("Advanced Settings", key))
                else:
                    value = self.getDefaultValue("Advanced Settings", key)
                currentValue = self.getValue("Computed Settings", key + "Main")
                if currentValue != value:
                    self.setValue("Computed Settings", key + "Main", value, True)
            # updated computed values for z-axis
            for key in ("KpPosZ", "KiPosZ", "KdPosZ", "propWeightZ"):
                if int(self.getValue("Advanced Settings", "enablePosPIDValues")) == 1:
                    value = float(self.getValue("Advanced Settings", key))
                else:
                    value = self.getDefaultValue("Advanced Settings", key)
                currentValue = self.getValue("Computed Settings", key)
                if currentValue != value:
                    self.setValue("Computed Settings", key, value, True)

        if key == "enableVPIDValues" or doAll is True:
            for key in ("KpV", "KiV", "KdV"):
                if int(self.getValue("Advanced Settings", "enablePosPIDValues")) == 1:
                    value = float(self.getValue("Advanced Settings", key))
                else:
                    value = self.getDefaultValue("Advanced Settings", key)
                currentValue = self.getValue("Computed Settings", key + "Main")
                if currentValue != value:
                    self.setValue("Computed Settings", key + "Main", value, True)
            # updated computed values for z-axis
            for key in ("KpVZ", "KiVZ", "KdVZ"):
                if int(self.getValue("Advanced Settings", "enablePosPIDValues")) == 1:
                    value = float(self.getValue("Advanced Settings", key))
                else:
                    value = self.getDefaultValue("Advanced Settings", key)
                currentValue = self.getValue("Computed Settings", key)
                if currentValue != value:
                    self.setValue("Computed Settings", key, value, True)

        if key == "chainOverSprocket" or doAll is True:
            if doAll is True:
                value = self.getValue("Advanced Settings", "chainOverSprocket")
            currentValue = self.getValue("Computed Settings","chainOverSprocketComputed")
            if value == "Top":
                if currentValue != 1:
                    self.setValue("Computed Settings", "chainOverSprocketComputed", 1, True)
            elif value == "Bottom":
                if currentValue != 2:
                    self.setValue("Computed Settings", "chainOverSprocketComputed", 2, True)
                    self.setValue("Computed Settings", "chainOverSprocketComputed", 2, True)

        if key == "fPWM" or doAll is True:
            if doAll is True:
                value = self.getValue("Advanced Settings", "fPWM")
            currentValue = self.getValue("Computed Settings", "fPWMComputed")
            if value == "31,000Hz":
                if currentValue != 1:
                    self.setValue("Computed Settings", "fPWMComputed", 1, True)
            elif value == "4,100Hz":
                if currentValue != 2:
                    self.setValue("Computed Settings", "fPWMComputed", 2, True)
            else:
                if currentValue != 3:
                    self.setValue("Computed Settings", "fPWMComputed", 3, True)

    def parseFirmwareVersions(self):
        home = "."
        if hasattr(sys, '_MEIPASS'):
            home = os.path.join(sys._MEIPASS)
            print(self.home)
        path = home+"/firmware/madgrizzle/*.hex"
        for filename in glob.glob(path):
            version = filename.split("-")
            maxIndex = len(version)-1
            if maxIndex >= 0:
                version = version[maxIndex].split(".hex")
                self.data.customFirmwareVersion = version[0]
            else:
                self.data.customFirmwareVersion = "n/a"
        path = home+"/firmware/maslowcnc/*.hex"
        for filename in glob.glob(path):
            version = filename.split("-")
            maxIndex = len(version)-1
            if maxIndex >= 0:
                version = version[maxIndex].split(".hex")
                self.data.stockFirmwareVersion = version[0]
            else:
                self.data.stockFirmwareVersion = "n/a"
        path = home+"/firmware/holey/*.hex"
        for filename in glob.glob(path):
            version = filename.split("-")
            maxIndex = len(version)-1
            if maxIndex >= 0:
                version = version[maxIndex].split(".hex")
                self.data.holeyFirmwareVersion = version[0]
            else:
                self.data.holeyFirmwareVersion = "n/a"

    def processChange(self, key, value):
        ### TODO: This does not currently fire on bools ##
        if key == "fps" or key == "videoSize" or key=="cameraSleep":
            self.data.camera.changeSetting(key, value)


    def firmwareKeyString(self, firmwareKey, value):
        strValue = self.firmwareKeyValue(value)
        gc = "$" + str(firmwareKey) + "=" + strValue
        return gc


    def firmwareKeyValue(self, value):
        try:
            de = math.log(abs(value), 10)
            ru = math.ceil(de)
        except:
            ru = 0
        fmt = '{:' + str(int(max(max(7 - ru, 7), abs(ru)))) + '.' + str(int(6 - ru)) + 'f}'
        try:
            return fmt.format(value)
        except:
            print('firmwareKeyString Exception: value = ' + str(value))
            return str(value)

    def reloadWebControlJSON(self):
        try:
            with open(self.home+"/.WebControl/webcontrol.json", "r") as infile:
                self.settings = json.load(infile)
            return True
        except:
            print("error reloading WebControlJSON")
            return False
