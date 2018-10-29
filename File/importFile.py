from DataStructures.makesmithInitFuncs import MakesmithInitFuncs

import sys
import threading
import re
import math


class ImportFile(MakesmithInitFuncs):
    def importGCini(self, filename):
        print(filename)
        if filename is "":  # Blank file?
            return False
        try:
            filterfile = open(filename, "r")
            rawFile = filterfile.read()
            parsedFile = re.split("\n", rawFile)  # splits the file into lines
            filterfile.close()  # closes the filter save file
            for line in parsedFile:
                if line == "[Computed Settings]":
                    section = "Computed Settings"
                elif line == "[Maslow Settings]":
                    section = "Maslow Settings"
                elif line == "[Advanced Settings]":
                    section = "Advanced Settings"
                elif line == "[Ground Control Settings]":
                    section = ""
                elif line == "[Background Settings]":
                    section = ""
                elif line == "[Optical Calibration Settings]":
                    section = "Optical Calibration Settings"
                elif line == "":
                    pass
                else:
                    if section != "":
                        setting = [x.strip() for x in line.split("=")]
                        # print(section+"->"+setting[0]+":"+setting[1])
                        if True: #if setting[0] != "comport" and setting[0] != "homex" and setting[0] != "homey":
                            self.data.config.setValue(
                                section, setting[0], setting[1], True, isImporting=True,
                            )
            print("computing settings")
            self.data.config.computeSettings(None, None, None, True)
            #self.data.config.setValue("Advanced Settings","positionErrorLimit", 2000)
            ##go through and manually push the critical settings so position can be calculated.
            #print("syncing specific values")
            #self.data.config.syncFirmwareKey(11, 0, isImporting=False, useStored=True)
            #self.data.config.syncFirmwareKey(2, 0, isImporting=False, useStored=True)
            #self.data.config.syncFirmwareKey(3, 0, isImporting=False, useStored=True)
            #self.data.config.syncFirmwareKey(8, 0, isImporting=False, useStored=True)
            #self.data.config.syncFirmwareKey(37, 0, isImporting=False, useStored=True)
            #print("synced specific values")
            self.data.gcode_queue.put("$$")
        except:
            print("Import File Error")
            self.data.message_queue.put("Message: Cannot open import file.")
            return False
        return True
