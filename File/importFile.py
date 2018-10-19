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
                        self.data.config.setValue(
                            section, setting[0], setting[1], True
                        )  # True to prevent recomputing settings everytime.
            self.data.config.computeSettings(None, None, None, True)
        except:
            print("Import File Error")
            self.data.message_queue.put("Message: Cannot open import file.")
            return False
        return True
