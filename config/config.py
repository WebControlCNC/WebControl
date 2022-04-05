"""

This file provides a single dict which contains all of the details about the
various settings.  It also has a number of helper functions for interacting
and using the data in this dict.

"""
import json
import re
import os, sys, os.path
import math
from shutil import copyfile
from pathlib import Path
import time
import glob
import subprocess

from __main__ import app
from DataStructures.makesmithInitFuncs import MakesmithInitFuncs


class Config(MakesmithInitFuncs):
    settings = {}
    defaults = {}
    home = "."
    home1 = "."
    firstRun = False

    def __init__(self):
        '''
        This function determines if a pyinstaller version is being run and if so,
        sets the home directory of the pyinstaller files.  This facilitates updates
        to the pyinstaller releases.
        '''
        self.home = str(Path.home())
        if hasattr(sys, '_MEIPASS'):
            self.home1 = os.path.join(sys._MEIPASS)
            print(self.home1)

        '''
        This portion creates directories that are missing and creates a new webcontrol.json
        file if this is the first run (copies defaultwebcontrol.json)
        '''
        print("Initializing Configuration")
        if not os.path.isdir(self.home+"/.WebControl"):
            print("creating "+self.home+"/.WebControl directory")
            os.mkdir(self.home+"/.WebControl")
        if not os.path.exists(self.home+"/.WebControl/webcontrol.json"):
            print("copying defaultwebcontrol.json to "+self.home+"/.WebControl/")
            copyfile(self.home1+"/defaultwebcontrol.json",self.home+"/.WebControl/webcontrol.json")
            self.firstRun = True
        if not os.path.isdir(self.home+"/.WebControl/systemd"):
            print("creating "+self.home+"/.WebControl/systemd directory")
            os.mkdir(self.home+"/.WebControl/systemd")
            copyfile(self.home1+"/Services/MaslowButton.py",self.home+"/.WebControl/systemd/MaslowButton.py")
            copyfile(self.home1+"/Services/MaslowButton.service",self.home+"/.config/systemd/user/MaslowButton.service")
            
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
        '''
        This portion scans the webcontrol.json file and sees if anything is missing in comparison to
        the defaultwebcontrol.json file.  Changes to the defaultwebcontrol.json file are automatically
        ADDED to the webcontrol.json file.  This function does not DELETE entries in the webcontrol.json
        file if they do not appear in the defaultwebcontrol.json file.
        '''
        # TODO: add DELETE function to this to clean up unneeded entries
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

        '''
        If there was a change to webcontrol.json file due to differences with
        defaultwebcontrol.json, then the config is reloaded.
        '''
        if updated:
            with open(self.home+"/.WebControl/webcontrol.json", "w") as outfile:
                # print ("writing file")
                json.dump(
                    self.settings, outfile, sort_keys=True, indent=4, ensure_ascii=False
                )

        '''
        Delete any copies of webcontrol in the downloads directory to cleanup the file system
        '''
        home = self.home
        dirName = home + "/.WebControl/downloads"
        if os.path.exists(dirName):
            dir = os.listdir(dirName)
            for item in dir:
                if item.startswith("webcontrol"):
                    if item.endswith("gz") or item.endswith("zip") or item.endswith("dmg"):
                        print("Removing file:"+item)
                        os.remove(os.path.join(dirName, item))

    def checkForTouchedPort(self):
        '''
        this function looks for a file that has a port number embedded
        in the filename.  If found, it parses the port number and uses it
        to start the flask engine.
        '''
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
    def getWebPortNumber(self):
        '''
        This function looks for the flask / socket IO port number where the webcontrol page is to be hosted.  default is 5000, but often is not found there
        '''
        webPort = self.data.config.getValue("WebControl Settings", "webPort")
        webPortInt = 5000
        try:
            webPortInt = int(webPort)
            if webPortInt < 0 or webPortInt > 65535:
                webPortInt = 5000
            return (str(webPortInt))
        except Exception as e:
            self.data.console_queue.put(e)
            self.data.console_queue.put("Invalid port assignment found in webcontrol.json")
            return('5000') 
            
    def buttonSubProcess(self, command):
        '''
        this function starts and stops a separate process called MaslowButton that handles the GPIO completely separate from the threads in webcontrol
        MaslowButton communicates over a socket text communication using the IO web port set up in webcontrol and is toggled by the gpio settings menu
        this process is only available if running on raspberry pi
        '''
        #sys.setrecursionlimit(15000)
        if ((self.data.GPIOButtonService) and (self.data.platform == "RPI")):
            #try:
                cwd = os.getcwd()
                startcommand = 'python3 ' + str(cwd) + '/Services/maslowButton.py'
                print("current working directory: ", str(cwd))
                path =  cwd + '/Services/maslowButton.py'                
                if (os.path.isfile(path)):
                    print("path 1 is ", path)
                    #startcommand = "python " + path
                    openpath = cwd + "/Services/buttonconfig.json"
                else:
                    path = "./Services/maslowButton.py"
                    if(os.path.isfile(path)):
                        print("path 2 is ", path)
                        #startcommand = "python " + path
                        openpath = './buttonconfig.json'
                    else:
                        path = "../Services/maslowButton.py"
                        if(os.path.isfile(path)):
                            print("path 3 is ", path)
                            #startcommand = "python " + path
                            openpath = '../buttonconfig.json'
                f = open(openpath, 'w')
                f.write(str(self.getWebPortNumber()))
                f.close
                print("subprocess start command: ", startcommand)
                if command == 'stop':
                    print("Maslow Button subprocess stopping")
                    subprocess.Popen('killall -9 maslowButton.py')
                    return True
                elif command == 'start':
                    print("Maslow Button subprocess starting")
                    subprocess.call([cwd + '/Services/MBstart.sh'])
                    #subprocess.Popen(startcommand,, stdout=dev_null, stderr=dev_null)
                    return True
                elif command == 'restart':
                    print("Maslow Button subprocess restarting")
                    subprocess.call('killall -9 maslowButton.py')
                    subprocess.Popen([cwd + '/Services/MBstart.sh'])
                    return True
                else:
                    self.data.console_queue.put("no process found or cannot start service - invalid request")
                    return False          
            #except Exception as e:
            #    self.data.console_queue.put(e)
            #    self.data.console_queue.put("Error with staring MaslowButton.py subprocess")
                return False
        else:
            self.data.console_queue.put("button service option not selected.  No Buttons activated") 
            return True  
              
    def getHome(self):
        return self.home

    def getJSONSettings(self):
        return self.settings

    def updateQuickConfigure(self, result):
        '''
        Updates settings based upon the form results.
        :param result: submitted form
        :return: always returns true.
        '''
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
        '''
        This function is intended to update a setting and call the necessary recomputes and syncs with the controller.
        :param section: The section of the setting.. Advanced Settings, etc.
        :param key:  The key of the setting.. motorSpacingX, etc.
        :param value: The value to set the setting to.
        :param recursionBreaker: Prevents loops due to computed settings.. not sure is needed in reality.
        :param isImporting: intended to delay sending settings and recomputing settings until import is done.
        :return:

        Re: recursionBreaker.  IIRC, I was having a heck of time getting settings to work, particularly when compute
        settings was being called.  computeSettings calls this function after computing a new value, but this function
        calls computeSetting if a value is updated.  To avoid testing on whether a setting is a computed setting or not,
        computeSetting just sets recursionBreaker to true and this function doesn't call computeSetting.
        '''
        updated = False
        found = False
        changedValue = None
        changedKey = None
        # Probably an easier way to do this than to iterate through all keys in a section to find the one you want to
        # update.  TODO: Find a pythonic way to find the key.
        for x in range(len(self.settings[section])):
            if self.settings[section][x]["key"].lower() == key.lower():
                found = True
                # each type (float, string, bool, etc.) is handled separately.  This is approach is legacy, and could
                # be cleaned up.  TODO: cleanup this so it's handled with less redundancy.
                if self.settings[section][x]["type"] == "float":
                    try:
                        storedValue = self.settings[section][x]["value"]
                        self.settings[section][x]["value"] = float(value)
                        updated = True
                        # This test updates certain settings in webcontrol.  Might be a bit hackis.
                        if storedValue != float(value):
                            self.processChange(self.settings[section][x]["key"],float(value))
                        # If setting is a controller setting, then sync with controller if needed.
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
                        updated = True
                        # This test updates certain settings in webcontrol.  Might be a bit hackis.
                        if storedValue != int(value):
                            self.processChange(self.settings[section][x]["key"], int(value))
                        # If setting is a controller setting, then sync with controller if needed.
                        if "firmwareKey" in self.settings[section][x]:
                            #not sure why this test is here, probably legacy as the setting type for 85 is string.
                            if self.settings[section][x]["firmwareKey"] != 85:
                                self.syncFirmwareKey(
                                    self.settings[section][x]["firmwareKey"],
                                    storedValue,
                                    isImporting,
                                )
                        #added this because it appears to be missing.
                        break
                    except:
                        break
                elif self.settings[section][x]["type"] == "bool":
                    try:
                        # change true/false to on/off if that's how it comes in to this function.  I think this was
                        # done because forms come in as checkbox results (on/off) and webcontrol somewhere might want
                        # to set the value as true/false.
                        if isinstance(value, bool):
                            if value:
                                value = "on"
                            else:
                                value = "off"
                        if value == "on" or value == "1" or value == 1:
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
                    # If not float, int, bool, then must be string.
                    storedValue = self.settings[section][x]["value"]
                    self.settings[section][x]["value"] = value
                    # This test updates certain settings in webcontrol.  Might be a bit hackis.
                    if storedValue != value:
                        self.processChange(self.settings[section][x]["key"], value)
                    updated = True
                    if "firmwareKey" in self.settings[section][x]:
                        self.syncFirmwareKey(
                            self.settings[section][x]["firmwareKey"], storedValue, isImporting,
                        )
                    break
        if not found:
            # I think SHOULDN'T be called any more.  It was here previously because of how checkboxes were returned
            # from forms (they aren't part of the form result if they aren't enabled).
            if self.settings[section][x]["type"] == "bool":
                self.data.console_queue.put(self.settings[section][x]["key"])
                storedValue = self.settings[section][x]["value"]
                self.settings[section][x]["value"] = 0
                if "firmwareKey" in self.settings[section][x]:
                    self.syncFirmwareKey(
                        self.settings[section][x]["firmwareKey"], storedValue
                    )
                updated = True
        if updated:
            # if not being updated from the computSettings, then call computeSettings to update if needed.
            if not recursionBreaker:
                self.computeSettings(None, None, None, True)
            # and now save the settings to storage
            with open(self.home+"/.WebControl/webcontrol.json", "w") as outfile:
                # print ("writing file")
                json.dump(
                    self.settings, outfile, sort_keys=True, indent=4, ensure_ascii=False
                )

    def updateSettings(self, section, result):
        '''
        Take the form result, iterate through it and update the settings
        :param section: The form's section (i.e., Advanced Settings)
        :param result: the form's returned results.  NOTE: disabled checkboxes are NOT returned in the results.
        :return:
        '''
        # Iterate through all the settings that SHOULD be in the form.
        for x in range(len(self.settings[section])):
            setting = self.settings[section][x]["key"]
            # I think I put this here so that a disabled checkbox gets called as well.
            # If the setting is not found in the results, then it must be a disabled checkbox and its value gets set
            # to a zero.  This probably should be cleaned up and resultValue set to "off" to make it jive with the
            # tests in updateSetting.
            if setting in result:
                resultValue = result[setting]
            else:
                resultValue = 0
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
        '''
        :param firmwareKey: the firmwareKey value
        :param value: the PREVIOUS value prior to updating.
        :param isImporting: indicates to bypass syncing until all the importing of values is done.
        :param useStored: indicates to use the value that's currently stored to update controller (holeyKinematics)
        :param data: used by optical calibration to send function the error array to send to controller. (optical)
        :return:
        '''
        for section in self.settings:
            for option in self.settings[section]:
                if "firmwareKey" in option and option["firmwareKey"] == firmwareKey:
                    # if this is custom firmware OR if the setting is not custom, then do this.
                    if self.data.controllerFirmwareVersion > 100 or ("custom" not in option or option["custom"] != 1):
                        storedValue = option["value"]
                        # update storedValue based upon saved values.. TODO: fix this for comparison to value if broken.
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
                        # if error array, send by special function (optical)
                        if firmwareKey == 85:
                            if self.data.controllerFirmwareVersion >= 100:
                                self.data.console_queue.put("Sending error array")
                                if storedValue != "":
                                    self.sendErrorArray(firmwareKey, storedValue, data)
                                # Can't recall why this is a pass and not a break.. might be legacy or related to
                                # the !="" check above.
                                pass
                        elif useStored is True:
                            # This probably could be moved to the last elif statement.  Think this was here for
                            # troubleshooting purposes initially.  TODO: verify and add 'or useStored' to last elif
                            strValue = self.firmwareKeyString(firmwareKey, storedValue)
                            app.data.gcode_queue.put(strValue)
                            # updates holeKinematics simulator model with new value.
                            self.data.holeyKinematics.updateSetting(firmwareKey, storedValue)
                        elif firmwareKey >= 87 and firmwareKey <= 98:
                            # Special test for sending curve fit coefficients (optical)
                            if self.data.controllerFirmwareVersion >= 100:
                                # Attempt at testing whether or not really small values are close by comparing % diff.
                                if not self.isPercentClose(float(storedValue), float(value)):
                                    if not isImporting:
                                        strValue = self.firmwareKeyString(firmwareKey, storedValue)
                                        app.data.gcode_queue.put(strValue)
                                        #not really needed since this is optical calibration section, but no harm.
                                        self.data.holeyKinematics.updateSetting(firmwareKey, storedValue)
                                else:
                                    break
                        elif not self.isClose(float(storedValue), float(value)) and not isImporting:
                            # Update the controller value if its different enough from previous value and
                            # we are not importing the groundcontrol.ini file.
                            strValue = self.firmwareKeyString(firmwareKey, storedValue)
                            app.data.gcode_queue.put(strValue)
                            # updates holeKinematics simulator model with new value.
                            self.data.holeyKinematics.updateSetting(firmwareKey, storedValue)
                        else:
                            break
        return

    def isPercentClose(self, a, b, rel_tol = 0.0001):
        '''
        Compares two numbers (really small or really large) and returns true if they are either really close
        percent-wise (based on rel_tol) or, in the event b is zero, if is close by really small absolute difference.
        If b=0, then there's a divide by zero error otherwise.
        :param a:
        :param b:
        :param rel_tol:
        :return:
        '''
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
        '''
        Parses the error array that is stored in webcontrol.json and returns an array of either floats or integers.
        Values are stored as integers that are equal to their original float value x 1000.
        :param value: the error array
        :param asFloat: iirc, used in optical calibration to get the numbers in float format rather than integers.
        :return:
        '''
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
        '''
        :param firmwareKey: firmware key of controller's error array.
        :param value: the value from settings
        :param data: doesn't appear to be used, probably legacy.
        :return:
        '''
        # Get values in integer format
        xErrors, yErrors = self.parseErrorArray(value, False)
        # now send the array:
        # The '$O' triggers the firmware that this is an array coming in and to parse the values appropriately
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
        # if you send a 31,15 , it will trigger a save to EEPROM.
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
        '''
        Function was initially intended to recompute settings when needed, but currently all calls to this function
        have doAll set to true, which causes all settings to be recomputed.
        :param section:
        :param key:
        :param value:
        :param doAll: Forces all settings to be recomputed.
        :return:
        '''
        # Update Computed settings
        if key == "loggingTimeout" or doAll is True:
            loggingTimeout = self.getValue("WebControl Settings", "loggingTimeout")

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
        '''
        Parses the files located in the installation's firmware directory for certain arduino firmwares (.hex files)
        /madgrizzle is the optical calibration firmware
        /holey is the holey calibration firmware
        /maslowcnc is the stock firmware.
        This function determines the version number.
        :return:
        '''
        home = "."
        if hasattr(sys, '_MEIPASS'):
            home = os.path.join(sys._MEIPASS)
            print(self.home)
        path = home+"/firmware/test/*.hex"
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
         pass
    #     ### TODO: This does not currently fire on bools ##
    #     # Not really sure why I don't have it firing on bools.. must of had a reason
        #  if key == "fps" or key == "videoSize" or key == "cameraSleep":
        #      self.data.camera.changeSetting(key, value)



    def firmwareKeyString(self, firmwareKey, value):
        '''
        Processes firmwareKey and value into a gcode string to be sent to controller
        :param firmwareKey:
        :param value:
        :return:
        '''
        strValue = self.firmwareKeyValue(value)
        gc = "$" + str(firmwareKey) + "=" + strValue
        return gc

    def firmwareKeyValue(self, value):
        '''
        Pulled in from holey calibration fork.  Haven't really worked with it.
        :param value:
        :return:
        '''
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
        '''
        Reloads the webcontrol.json file.  This would be called after a restoral of the file.
        :return:
        '''
        try:
            with open(self.home+"/.WebControl/webcontrol.json", "r") as infile:
                self.settings = json.load(infile)
            return True
        except:
            print("error reloading WebControlJSON")
            return False
