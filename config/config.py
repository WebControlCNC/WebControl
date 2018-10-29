"""

This file provides a single dict which contains all of the details about the
various settings.  It also has a number of helper functions for interacting
and using the data in this dict.

"""
import json
import re
import os
from shutil import copyfile
from pathlib import Path

from __main__ import app
from DataStructures.makesmithInitFuncs import MakesmithInitFuncs


class Config(MakesmithInitFuncs):
    settings = {}
    home = ""

    def __init__(self):
        self.home = str(Path.home())
        print("Initializing Configuration")
        if not os.path.isdir(self.home+"/.WebControl"):
            print("creating "+self.home+"/.WebControl directory")
            os.mkdir(self.home+"/.WebControl")
        if not os.path.exists(self.home+"/.WebControl/webcontrol.json"):
            print("copying webcontrol.json to "+self.home+"/.WebControl/")
            copyfile("webcontrol.json",self.home+"/.WebControl/webcontrol.json")
        with open(self.home+"/.WebControl/webcontrol.json", "r") as infile:
            self.settings = json.load(infile)
            # self.computeSettings(None, None, None, True);

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
        for x in range(len(self.settings[section])):
            if self.settings[section][x]["key"].lower() == key.lower():
                found = True
                if self.settings[section][x]["type"] == "float":
                    try:
                        storedValue = self.settings[section][x]["value"]
                        self.settings[section][x]["value"] = float(value)
                        updated = True
                        if "firmwareKey" in self.settings[section][x]:
                            self.syncFirmwareKey(
                                self.settings[section][x]["firmwareKey"], storedValue, isImporting,
                            )
                    except:
                        pass
                elif self.settings[section][x]["type"] == "int":
                    try:
                        storedValue = self.settings[section][x]["value"]
                        self.settings[section][x]["value"] = int(value)
                        updated = True
                        if "firmwareKey" in self.settings[section][x]:
                            if self.settings[section][x]["firmwareKey"] != 45:
                                self.syncFirmwareKey(
                                    self.settings[section][x]["firmwareKey"],
                                    storedValue,
                                    isImporting,
                                )
                    except:
                        pass
                elif self.settings[section][x]["type"] == "bool":
                    try:
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

                    except:
                        pass
                else:
                    storedValue = self.settings[section][x]["value"]
                    self.settings[section][x]["value"] = value
                    updated = True
                    if "firmwareKey" in self.settings[section][x]:
                        self.syncFirmwareKey(
                            self.settings[section][x]["firmwareKey"], storedValue, isImporting,
                        )
        if not found:
            print("Did not find " + str(section) + ", " + str(key) + ", " + str(value))
        if updated:
            if not recursionBreaker:
                self.computeSettings(None, None, None, True)
            with open(self.home+"/.WebControl/webcontrol.json", "w") as outfile:
                # print ("writing file")
                json.dump(
                    self.settings, outfile, sort_keys=True, indent=4, ensure_ascii=False
                )

    def updateSettings(self, section, result):
        print("at update Settings")
        updated = False
        for x in range(len(self.settings[section])):
            # print(self.settings[section][x]["key"])
            # print(self.settings[section][x]["type"])
            found = False
            for setting in result:
                if self.settings[section][x]["key"] == setting:

                    if self.settings[section][x]["type"] == "float":
                        try:
                            storedValue = self.settings[section][x]["value"]
                            self.settings[section][x]["value"] = float(result[setting])
                            updated = True
                            if "firmwareKey" in self.settings[section][x]:
                                self.syncFirmwareKey(
                                    self.settings[section][x]["firmwareKey"],
                                    storedValue,
                                )
                        except:
                            pass
                    elif self.settings[section][x]["type"] == "int":
                        try:
                            storedValue = self.settings[section][x]["value"]
                            self.settings[section][x]["value"] = int(result[setting])
                            updated = True
                            if "firmwareKey" in self.settings[section][x]:
                                self.syncFirmwareKey(
                                    self.settings[section][x]["firmwareKey"],
                                    storedValue,
                                )
                        except:
                            pass
                    elif self.settings[section][x]["type"] == "bool":
                        # print result[setting]
                        try:
                            if result[setting] == "on":
                                storedValue = self.settings[section][x]["value"]
                                self.settings[section][x]["value"] = 1
                                updated = True
                                if "firmwareKey" in self.settings[section][x]:
                                    # print "syncing1 true bool at:"+str(self.settings[section][x]['firmwareKey'])
                                    self.syncFirmwareKey(
                                        self.settings[section][x]["firmwareKey"],
                                        storedValue,
                                    )
                            else:
                                storedValue = self.settings[section][x]["value"]
                                self.settings[section][x]["value"] = 0
                                updated = True
                                if "firmwareKey" in self.settings[section][x]:
                                    # print "syncing2 true bool at:"+str(self.settings[section][x]['firmwareKey'])
                                    self.syncFirmwareKey(
                                        self.settings[section][x]["firmwareKey"],
                                        storedValue,
                                    )
                        except:
                            pass

                    elif self.settings[section][x]["type"] == "options":
                        try:
                            # print(str(result[setting]))
                            storedValue = self.settings[section][x]["value"]
                            self.settings[section][x]["value"] = str(result[setting])
                            # print(self.settings[section][x]["value"])
                            updated = True
                            if "firmwareKey" in self.settings[section][x]:
                                self.syncFirmwareKey(
                                    self.settings[section][x]["firmwareKey"],
                                    storedValue,
                                )
                        except:
                            pass

                    else:
                        storedValue = self.settings[section][x]["value"]
                        self.settings[section][x]["value"] = result[setting]
                        updated = True
                        # print str(storedValue)+", "+str(result[settig])
                        if "firmwareKey" in self.settings[section][x]:
                            # print "firmwareKey:"+str(self.settings[section][x]["firmwareKey"])
                            self.syncFirmwareKey(
                                self.settings[section][x]["firmwareKey"], storedValue
                            )

                    # print setting+":"+str(result[setting])+"->"+str(settings[section][x]["value"])
                    found = True
                    break
            if not found:
                # must be a turned off checkbox.. what a pain to figure out
                if self.settings[section][x]["type"] == "bool":
                    storedValue = self.settings[section][x]["value"]
                    self.settings[section][x]["value"] = 0
                    if "firmwareKey" in self.settings[section][x]:
                        # print "syncing3 false bool at:"+str(self.settings[section][x]['firmwareKey'])
                        self.syncFirmwareKey(
                            self.settings[section][x]["firmwareKey"], storedValue
                        )
                    updated = True
        if updated:
            self.computeSettings(None, None, None, True)
            with open(self.home+"/.WebControl/webcontrol.json", "w") as outfile:
                json.dump(
                    self.settings, outfile, sort_keys=True, indent=4, ensure_ascii=False
                )

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
                    # storedValue = self.get(section, option['key'])
                    storedValue = option["value"]
                    # print("firmwareKey:"+str(firmwareKey)+ " section:"+section+" storedValue:"+str(storedValue)+" value:"+str(value))
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

                    # print str(firmwareKey)+": "+str(storedValue)+"?"+str(value)
                    if firmwareKey == 45:
                        # print "firmwareKey = 45"
                        # if storedValue != "":
                        #    self.sendErrorArray(firmwareKey, storedValue, data)
                        pass
                    elif useStored is True:
                        app.data.gcode_queue.put(
                            "$" + str(firmwareKey) + "=" + str(storedValue)
                        )
                    elif not self.isClose(float(storedValue), float(value)):
                        # print("firmwareKey(send) = "+ str(firmwareKey)+ ":"+ str(storedValue))
                        if not isImporting:
                            app.data.gcode_queue.put(
                                "$" + str(firmwareKey) + "=" + str(storedValue)
                            )
                    else:
                        break
        return

    def isClose(self, a, b, rel_tol=1e-06):
        """
        Takes two values and returns true if values are close enough in value
        such that the difference between them is less than the significant
        figure specified by rel_tol.  Useful for comparing float values on
        arduino adapted from https://stackoverflow.com/a/33024979
        """
        return abs(a - b) <= rel_tol * max(abs(a), abs(b))

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
        xErrors, yErrors = parseErrorArray(value, False)
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
        if key == "kinematicsType" or doAll is True:
            if doAll is True:
                value = self.getValue("Advanced Settings", "kinematicsType")
            if value == "Quadrilateral":
                self.setValue("Computed Settings", "kinematicsTypeComputed", "1", True)
            else:
                self.setValue("Computed Settings", "kinematicsTypeComputed", "2", True)

        if key == "gearTeeth" or key == "chainPitch" or doAll is True:
            gearTeeth = float(self.getValue("Advanced Settings", "gearTeeth"))
            chainPitch = float(self.getValue("Advanced Settings", "chainPitch"))
            distPerRot = gearTeeth * chainPitch
            self.setValue("Computed Settings", "distPerRot", str(distPerRot), True)
            leftChainTolerance = float(
                self.getValue("Advanced Settings", "leftChainTolerance")
            )
            distPerRotLeftChainTolerance = (1 + leftChainTolerance / 100.0) * distPerRot
            self.setValue(
                "Computed Settings",
                "distPerRotLeftChainTolerance",
                str("{0:.5f}".format(distPerRotLeftChainTolerance)),
                True,
            )
            rightChainTolerance = float(
                self.getValue("Advanced Settings", "rightChainTolerance")
            )
            distPerRotRightChainTolerance = (
                1 + rightChainTolerance / 100.0
            ) * distPerRot
            self.setValue(
                "Computed Settings",
                "distPerRotRightChainTolerance",
                str("{0:.5f}".format(distPerRotRightChainTolerance)),
                True,
            )

        if key == "leftChainTolerance" or doAll:
            distPerRot = float(self.getValue("Computed Settings", "distPerRot"))
            leftChainTolerance = float(
                self.getValue("Advanced Settings", "leftChainTolerance")
            )
            distPerRotLeftChainTolerance = (1 + leftChainTolerance / 100.0) * distPerRot
            self.setValue(
                "Computed Settings",
                "distPerRotLeftChainTolerance",
                str("{0:.5f}".format(distPerRotLeftChainTolerance)),
                True,
            )

        if key == "rightChainTolerance" or doAll is True:
            distPerRot = float(self.getValue("Computed Settings", "distPerRot"))
            rightChainTolerance = float(
                self.getValue("Advanced Settings", "rightChainTolerance")
            )
            distPerRotRightChainTolerance = (
                1 + rightChainTolerance / 100.0
            ) * distPerRot
            self.setValue(
                "Computed Settings",
                "distPerRotRightChainTolerance",
                str("{0:.5f}".format(distPerRotRightChainTolerance)),
                True,
            )

        if key == "enablePosPIDValues" or doAll is True:
            for key in ("KpPos", "KiPos", "KdPos", "propWeight"):
                if int(self.getValue("Advanced Settings", "enablePosPIDValues")) == 1:
                    value = float(self.getValue("Advanced Settings", key))
                else:
                    value = self.getDefaultValue("Advanced Settings", key)
                self.setValue("Computed Settings", key + "Main", value, True)
            # updated computed values for z-axis
            for key in ("KpPosZ", "KiPosZ", "KdPosZ", "propWeightZ"):
                if int(self.getValue("Advanced Settings", "enablePosPIDValues")) == 1:
                    value = float(self.getValue("Advanced Settings", key))
                else:
                    value = self.getDefaultValue("Advanced Settings", key)
                self.setValue("Computed Settings", key, value, True)

        if key == "enableVPIDValues" or doAll is True:
            for key in ("KpV", "KiV", "KdV"):
                if int(self.getValue("Advanced Settings", "enablePosPIDValues")) == 1:
                    value = float(self.getValue("Advanced Settings", key))
                else:
                    value = self.getDefaultValue("Advanced Settings", key)
                self.setValue("Computed Settings", key + "Main", value, True)
            # updated computed values for z-axis
            for key in ("KpVZ", "KiVZ", "KdVZ"):
                if int(self.getValue("Advanced Settings", "enablePosPIDValues")) == 1:
                    value = float(self.getValue("Advanced Settings", key))
                else:
                    value = self.getDefaultValue("Advanced Settings", key)
                self.setValue("Computed Settings", key, value, True)

        if key == "chainOverSprocket" or doAll is True:
            if doAll is True:
                value = self.getValue("Advanced Settings", "chainOverSprocket")
                # print(value)
            if value == "Top":
                self.setValue("Computed Settings", "chainOverSprocketComputed", 1, True)
            elif value == "Bottom":
                self.setValue("Computed Settings", "chainOverSprocketComputed", 2, True)

        if key == "fPWM" or doAll is True:
            if value == "31,000Hz":
                self.setValue("Computed Settings", "fPWMComputed", 1, True)
            elif value == "4,100Hz":
                self.setValue("Computed Settings", "fPWMComputed", 2, True)
            else:
                self.setValue("Computed Settings", "fPWMComputed", 3, True)
