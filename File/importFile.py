from DataStructures.makesmithInitFuncs import MakesmithInitFuncs

import re
import json

class ImportFile(MakesmithInitFuncs):
    def importGCini(self, filename):
        self.data.console_queue.put(filename)
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
                        self.data.config.setValue(
                            section, setting[0], setting[1], True, isImporting=True,
                        )
            self.data.console_queue.put("computing settings")
            self.data.config.computeSettings(None, None, None, True)
            self.data.gcode_queue.put("$$")
        except:
            self.data.console_queue.put("Import File Error")
            self.data.message_queue.put("Message: Cannot open import file.")
            return False
        return True

    def importWebControlJSON(self, filename):
        self.data.console_queue.put(filename)
        if filename is "":  # Blank file?
            return False
        try:
            with open(filename, "r") as infile:
                imported = json.load(infile)
                updated = False
                for section in imported:
                    sectionFound = False
                    for x in range(len(imported[section])):
                        found = False
                        for _section in self.data.config.settings:
                            if _section == section:
                                sectionFound = True
                                for y in range(len(self.data.config.settings[_section])):
                                    if imported[section][x]["key"] == self.data.config.settings[_section][y]["key"]:
                                        found = True
                                        if "value" in imported[section][x]:
                                            if self.data.config.settings[_section][y]["value"] != imported[section][x]["value"]:
                                                self.data.config.settings[_section][y]["value"] = imported[section][x]["value"]
                                                self.data.console_queue.put("Updated "+self.data.config.settings[_section][y]["key"])
                                                updated = True
                                        break
                        if not found:
                            if sectionFound:
                                print("section found")
                            else:
                                print("section not found")
                                self.data.config.settings[section] = []
                            print(section + "->" + imported[section][x]["key"] + " was not found..")
                            t = {}
                            if "default" in imported[section][x]:
                                t["default"] = imported[section][x]["default"]
                            if "desc" in imported[section][x]:
                                t["desc"] = imported[section][x]["desc"]
                            if "firmwareKey" in imported[section][x]:
                                t["firmwareKey"] = imported[section][x]["firmwareKey"]
                            if "key" in imported[section][x]:
                                t["key"] = imported[section][x]["key"]
                            if "section" in imported[section][x]:
                                t["section"] = imported[section][x]["section"]
                            if "title" in imported[section][x]:
                                t["title"] = imported[section][x]["title"]
                            if "type" in imported[section][x]:
                                t["type"] = imported[section][x]["type"]
                            if "value" in imported[section][x]:
                                t["value"] = imported[section][x]["value"]
                            if "options" in imported[section][x]:
                                t["options"] = imported[section][x]["options"]
                            self.data.config.settings[section].append(t)
                            print("added " + section + "->" + self.data.config.settings[section][len(self.data.config.settings[section]) - 1]["key"])
                            updated = True
                if updated:
                    with open(self.data.config.home+"/.WebControl/webcontrol.json", "w") as outfile:
                        json.dump(self.data.config.settings, outfile, sort_keys=True, indent=4, ensure_ascii=False)
                        self.data.gcode_queue.put("$$")
        except:
            self.data.console_queue.put("Import File Error")
            self.data.message_queue.put("Message: Cannot open import file.")
            return False
        return True
