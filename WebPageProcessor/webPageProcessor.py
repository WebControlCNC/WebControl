from __main__ import socketio

import time
import math
import json
from os import listdir
from os.path import isfile, join
import re
from flask import render_template
import os
import frontmatter
import webbrowser
import socket
from github import Github
import markdown


class WebPageProcessor:

    data = None

    def __init__(self, data):
        self.data = data

    def createWebPage(self, pageID, isMobile, args):
        # returns a page and a bool specifying whether the user has to click close to exit modal
        if pageID == "maslowSettings":
            setValues = self.data.config.getJSONSettingSection("Maslow Settings")
            # because this page allows you to select the comport from a list that is not stored in webcontrol.json, we need to package and send the list of comports
            # Todo:? change it to store the list?
            ports = self.data.comPorts
            if self.data.controllerFirmwareVersion < 100:
                enableCustom = False
            else:
                enableCustom = True
            if isMobile:
                page = render_template(
                    "settings_mobile.html",
                    title="Maslow Settings",
                    settings=setValues,
                    ports=ports,
                    pageID="maslowSettings",
                    enableCustom=enableCustom,
                )
            else:
                page = render_template(
                    "settings.html",
                    title="Maslow Settings",
                    settings=setValues,
                    ports=ports,
                    pageID="maslowSettings",
                    enableCustom=enableCustom,
                )
            return page, "Maslow Settings", False, "medium", "content", "footerSubmit"
        elif pageID == "advancedSettings":
            setValues = self.data.config.getJSONSettingSection("Advanced Settings")
            if self.data.controllerFirmwareVersion < 100:
                enableCustom = False
            else:
                enableCustom = True
            if isMobile:
                page = render_template(
                    "settings_mobile.html",
                    title="Advanced Settings",
                    settings=setValues,
                    pageID="advancedSettings",
                    enableCustom=enableCustom,
                )
            else:
                page = render_template(
                    "settings.html",
                    title="Advanced Settings",
                    settings=setValues,
                    pageID="advancedSettings",
                    enableCustom=enableCustom,
                )
            return page, "Advanced Settings", False, "medium", "content", "footerSubmit"
        elif pageID == "webControlSettings":
            setValues = self.data.config.getJSONSettingSection("WebControl Settings")
            if self.data.controllerFirmwareVersion < 100:
                enableCustom = False
            else:
                enableCustom = True
            if isMobile:
                page = render_template(
                    "settings_mobile.html",
                    title="WebControl Settings",
                    settings=setValues,
                    pageID="webControlSettings",
                    enableCustom=enableCustom,
                )
            else:
                page = render_template(
                    "settings.html",
                    title="WebControl Settings",
                    settings=setValues,
                    pageID="webControlSettings",
                    enableCustom=enableCustom,
                )
            return page, "WebControl Settings", False, "medium", "content", "footerSubmit"
        # elif pageID == "cameraSettings":
        #     setValues = self.data.config.getJSONSettingSection("Camera Settings")
        #     if self.data.controllerFirmwareVersion < 100:
        #         enableCustom = False
        #     else:
        #         enableCustom = True
        #     if isMobile:
        #         page = render_template(
        #             "settings_mobile.html",
        #             title="Camera Settings",
        #             settings=setValues,
        #             pageID="cameraSettings",
        #             enableCustom=enableCustom,
        #         )
        #     else:
        #         page = render_template(
        #             "settings.html",
        #             title="Camera Settings",
        #             settings=setValues,
        #             pageID="cameraSettings",
        #             enableCustom=enableCustom,
        #         )
          #  return page, "Camera Settings", False, "medium", "content", "footerSubmit"

        elif pageID == "gpioSettings":
            if self.data.platform == "RPI":
                setValues = self.data.config.getJSONSettingSection("GPIO Settings")
                if self.data.controllerFirmwareVersion < 100:
                    enableCustom = False
                else:
                    enableCustom = True
                options = self.data.gpioActions.getActionList()
                if isMobile:
                    page = render_template(
                        "gpio_mobile.html",
                        title="GPIO Settings",
                        settings=setValues,
                        options=options,
                        pageID="gpioSettings",
                        enableCustom=enableCustom,
                    )
                else:
                    page = render_template(
                        "gpio.html",
                        title="GPIO Settings",
                        settings=setValues,
                        options=options,
                        pageID="gpioSettings",
                        enableCustom=enableCustom,
                    )
                return page, "GPIO Settings", False, "medium", "content", "footerSubmit"
            else:
                page = render_template(
                        "gpio-led-rpi-error.html",
                        title="wrong platform",
                        pageID="not pi"
                    )
                return page, "wrong platform"
        
        elif pageID == "ledSettings":
            print("platform is: ", self.data.platform)
            if self.data.platform == "RPI":
                setValues = self.data.config.getJSONSettingSection("LED Settings")
                if self.data.controllerFirmwareVersion < 100:
                    enableCustom = False
                else:
                    enableCustom = True
                options = self.data.gpioActions.getLEDColors()
                #print(options)  
                if isMobile:
                    page = render_template(
                        "led_mobile.html",
                        title="LED Settings",
                        settings=setValues,
                        options=options,
                        pageID="ledSettings",
                        enableCustom=enableCustom,
                    )
                else:
                    page = render_template(
                        "led.html",
                        title="Tri-Color LED Settings",
                        settings=setValues,
                        options=options,
                        pageID="ledSettings",
                        enableCustom=enableCustom,
                    )
                return page, "Tri-Color LED Indicator Settings", False, "medium", "content", "footerSubmit"
            else:
                page = render_template(
                        "gpio-led-rpi-error.html",
                        title="wrong platform",
                        pageID="not pi"
                    )
                return page, "wrong platform"

        elif pageID =="gcodeClean":
            lastSelectedFile = self.data.config.getValue("Maslow Settings", "openFile")
            print('--from WPP - lastSelectedFile: ',lastSelectedFile)
            lastSelectedDirectory = self.data.config.getValue("Computed Settings", "lastSelectedDirectory")
            home = self.data.config.getHome()
            homedir = home+"/.WebControl/gcode"
            directories = []
            files = []
            try:
                for _root, _dirs, _files in os.walk(homedir):
                    if _dirs:
                        directories = _dirs
                    for file in _files:
                        if _root != homedir:
                            _dir = _root.split("\\")[-1].split("/")[-1]
                        else:
                            _dir = "."
                        files.append({"directory":_dir, "file":file})
            except Exception as e:
                print(e)
           # files = [f for f in listdir(homedir) if isfile(join(homedir, f))]
            directories.insert(0, "./")
            if lastSelectedDirectory is None:
                lastSelectedDirectory="."
            print("--directories",directories, type(directories))
            print("--files",files, type(files))
            print("--last file",lastSelectedFile, type(lastSelectedDirectory))
            print("--homedir",homedir, type(homedir))
        
            page = render_template(
                "gcodeclean.html", 
                directories=directories, 
                files=files, 
                lastSelectedFile=lastSelectedFile, 
                lastSelectedDirectory=lastSelectedDirectory, 
                isOpen=False
            )
            return page, "gcodeClean", False, "medium", "content", "footerSubmit"

        elif pageID == "openGCode":
            lastSelectedFile = self.data.config.getValue("Maslow Settings", "openFile")
            print(lastSelectedFile)
            lastSelectedDirectory = self.data.config.getValue("Computed Settings", "lastSelectedDirectory")
            home = self.data.config.getHome()
            homedir = home+"/.WebControl/gcode"
            directories = []
            files = []
            try:
                for _root, _dirs, _files in os.walk(homedir):
                    if _dirs:
                        directories = _dirs
                    for file in _files:
                        if _root != homedir:
                            _dir = _root.split("\\")[-1].split("/")[-1]
                        else:
                            _dir = "."
                        files.append({"directory":_dir, "file":file})
            except Exception as e:
                print("exception in open gocode file in webpage processor: ", e)
           # files = [f for f in listdir(homedir) if isfile(join(homedir, f))]
            directories.insert(0, "./")
            if lastSelectedDirectory is None:
                lastSelectedDirectory="."
            page = render_template(
                "openGCode.html", 
                directories=directories, 
                files=files, 
                lastSelectedFile=lastSelectedFile, 
                lastSelectedDirectory=lastSelectedDirectory, 
                isOpen=True
            )
            return page, "Open GCode", False, "medium", "content", "footerSubmit"
        elif pageID == "saveGCode":
            lastSelectedFile = self.data.config.getValue("Maslow Settings", "openFile")
            print(lastSelectedFile)
            lastSelectedDirectory = self.data.config.getValue("Computed Settings", "lastSelectedDirectory")
            home = self.data.config.getHome()
            homedir = home + "/.WebControl/gcode"
            directories = []
            files = []
            try:
                for _root, _dirs, _files in os.walk(homedir):
                    if _dirs:
                        directories = _dirs
                    for file in _files:
                        if _root != homedir:
                            _dir = _root.split("\\")[-1].split("/")[-1]
                        else:
                            _dir = "."
                        files.append({"directory": _dir, "file": file})
            except Exception as e:
                print(e)
            # files = [f for f in listdir(homedir) if isfile(join(homedir, f))]
            directories.insert(0, "./")
            if lastSelectedDirectory is None:
                lastSelectedDirectory = "."
            page = render_template(
                "saveGCode.html", 
                directories=directories, 
                files=files, 
                lastSelectedFile=lastSelectedFile,
                lastSelectedDirectory=lastSelectedDirectory, 
                isOpen=False
            )
            return page, "Save GCode", False, "medium", "content", "footerSubmit"

        elif pageID == "uploadGCode":
            validExtensions = self.data.config.getValue(
                "WebControl Settings", "validExtensions"
            )
            lastSelectedDirectory = self.data.config.getValue("Computed Settings", "lastSelectedDirectory")
            home = self.data.config.getHome()
            homedir = home + "/.WebControl/gcode"
            directories = []
            try:
                for _root, _dirs, _files in os.walk(homedir):
                    if _dirs:
                        directories = _dirs
            except Exception as e:
                print("Exception in upload gcode in webpageprocessor", e)
            directories.insert(0, "./")
            if lastSelectedDirectory is None:
                lastSelectedDirectory = "."
            print("----from webpageprocessor----")
            print("----homedir: ", homedir)
            page = render_template("uploadGCode.html", 
                validExtensions=validExtensions, 
                directories=directories, 
                lastSelectedDirectory=lastSelectedDirectory
            )
            return page, "Upload GCode", False, "medium", "content", "footerSubmit"
        elif pageID == "importGCini":
            url = "importFile"
            page = render_template("importFile.html", url=url)
            return page, "Import groundcontrol.ini", False, "medium", "content", False
        elif pageID == "importWCJSON":
            url = "importFileWCJSON"
            page = render_template("importFile.html", url=url)
            return page, "Import webcontrol.json", False, "medium", "content", False
        elif pageID == "restoreWebControl":
            url = "importRestoreWebControl"
            page = render_template("importFile.html", url=url)
            return page, "Restore WebControl", False, "medium", "content", False
        elif pageID == "actions":
            if self.data.controllerFirmwareVersion < 100:
                enableCustom = False
            else:
                enableCustom = True
            if self.data.controllerFirmwareVersion < 50:
                enableHoley = False
            else:
                enableHoley = True
            if (self.data.platform == "PYINSTALLER"):
                docker = False
            else:
                docker = True
            if self.data.platform == "RPI":
                enableRPIshutdown = True
            else:
                enableRPIshutdown = False
            if self.data.pyInstallUpdateAvailable:
                updateAvailable = True
                updateRelease = self.data.pyInstallUpdateVersion
            else:
                updateAvailable = False
                updateRelease = "N/A"
            if (float(self.data.controllerFirmwareVersion) > 1.26):
                firmwareSupportsZaxisLimit = True
            else:
                firmwareSupportsZaxisLimit = False
            print("action render-> firmware version is :", self.data.controllerFirmwareVersion, " so: ", firmwareSupportsZaxisLimit)
            page = render_template("actions.html", 
                                   updateAvailable=updateAvailable, 
                                   updateRelease=updateRelease, 
                                   docker=docker, 
                                   customFirmwareVersion=self.data.customFirmwareVersion, 
                                   stockFirmwareVersion=self.data.stockFirmwareVersion, 
                                   holeyFirmwareVersion=self.data.holeyFirmwareVersion, 
                                   enableCustom=enableCustom, 
                                   enableHoley=enableHoley, 
                                   enableRPIshutdown = enableRPIshutdown,
                                   firmwareSupportsZaxisLimit = firmwareSupportsZaxisLimit
                                   )
            return page, "Actions", False, "large", "content", False
        elif pageID == "zAxis":
            socketio.emit("closeModals", {"data": {"title": "Actions"}}, namespace="/MaslowCNC")
            distToMoveZ = self.data.config.getValue("Computed Settings", "distToMoveZ")
            unitsZ = self.data.config.getValue("Computed Settings", "unitsZ")
            touchPlate = self.data.config.getValue("Advanced Settings", "touchPlate")
            if isMobile:
                page = render_template("zaxis_mobile.html", 
                distToMoveZ=distToMoveZ, 
                unitsZ=unitsZ, 
                touchPlate=touchPlate)
            else:
                page = render_template("zaxis.html", 
                distToMoveZ=distToMoveZ, 
                unitsZ=unitsZ, 
                touchPlate=touchPlate)
            return page, "Z-Axis", False, "medium", "content", False

        elif pageID == "setZaxis":
            socketio.emit("closeModals", {"data": {"title": "Actions"}}, namespace="/MaslowCNC")
            minZlimit = 0 #self.data.config.getValue("Advanced Settings", "minZlimit")
            maxZlimit = 0 #self.data.config.getValue("Advanced Settings", "maxZlimit")
            distToMoveZ = self.data.config.getValue("Computed Settings", "distToMoveZ")
            unitsZ = self.data.config.getValue("Computed Settings", "unitsZ")
            if isMobile:
                page = render_template("setZaxis_mobile.html", 
                                       minZlimit = minZlimit, 
                                       maxZlimit = maxZlimit, 
                                       distToMoveZ=distToMoveZ, 
                                       unitsZ=unitsZ
                                       )
            else:
                page = render_template("setZaxis.html", 
                                       minZlimit = minZlimit, 
                                       maxZlimit = maxZlimit, 
                                       distToMoveZ=distToMoveZ, 
                                       unitsZ=unitsZ
                                       )
            return page, "Z-Axis Limits", False, "medium", "content", False

        elif pageID == "setSprockets":
            if self.data.controllerFirmwareVersion < 100:
                fourMotor = False
            else:
                fourMotor = True
            chainExtendLength = self.data.config.getValue("Advanced Settings", "chainExtendLength")
            socketio.emit("closeModals", {"data": {"title": "Actions"}}, namespace="/MaslowCNC")
            if isMobile:
                page = render_template("setSprockets_mobile.html", chainExtendLength=chainExtendLength, fourMotor=fourMotor)
            else:
                page = render_template("setSprockets.html", chainExtendLength=chainExtendLength, fourMotor=fourMotor)
            return page, "Set Sprockets", False, "medium", "content", False
        elif pageID == "resetChains":
            if self.data.controllerFirmwareVersion < 100:
                fourMotor = False
            else:
                fourMotor = True
            chainExtendLength = self.data.config.getValue("Advanced Settings", "chainExtendLength")
            socketio.emit("closeModals", {"data": {"title": "Actions"}}, namespace="/MaslowCNC")
            if isMobile:
                page = render_template("resetChains_mobile.html", chainExtendLength=chainExtendLength, fourMotor=fourMotor)
            else:
                page = render_template("resetChains.html", chainExtendLength=chainExtendLength, fourMotor=fourMotor)
            return page, "Reset Chains", False, "medium", "content", False

        elif pageID == "triangularCalibration":
            socketio.emit("closeModals", {"data": {"title": "Actions"}}, namespace="/MaslowCNC")
            motorYoffset = self.data.config.getValue("Maslow Settings", "motorOffsetY")
            rotationRadius = self.data.config.getValue("Advanced Settings", "rotationRadius")
            chainSagCorrection = self.data.config.getValue(
                "Advanced Settings", "chainSagCorrection"
            )
            page = render_template(
                "triangularCalibration.html",
                pageID="triangularCalibration",
                motorYoffset=motorYoffset,
                rotationRadius=rotationRadius,
                chainSagCorrection=chainSagCorrection,
            )
            return page, "Triangular Calibration", True, "medium", "content", False
        elif pageID == "holeyCalibration":
            socketio.emit("closeModals", {"data": {"title": "Actions"}}, namespace="/MaslowCNC")
            motorYoffset = self.data.config.getValue("Maslow Settings", "motorOffsetY")
            distanceBetweenMotors = self.data.config.getValue("Maslow Settings", "motorSpacingX")
            leftChainTolerance = self.data.config.getValue("Advanced Settings", "leftChainTolerance")
            rightChainTolerance = self.data.config.getValue("Advanced Settings", "rightChainTolerance")
            page = render_template(
                "holeyCalibration.html",
                pageID="holeyCalibration",
                motorYoffset=motorYoffset,
                distanceBetweenMotors=distanceBetweenMotors,
                leftChainTolerance=leftChainTolerance,
                rightChainTolerance=rightChainTolerance,
            )
            return page, "Holey Calibration", True, "medium", "content", False
        elif pageID == "quickConfigure":
            socketio.emit("closeModals", {"data": {"title": "Actions"}}, namespace="/MaslowCNC")
            motorOffsetY = self.data.config.getValue("Maslow Settings", "motorOffsetY")
            rotationRadius = self.data.config.getValue("Advanced Settings", "rotationRadius")
            kinematicsType = self.data.config.getValue("Advanced Settings", "kinematicsType")
            if kinematicsType != "Quadrilateral":
                if abs(float(rotationRadius) - 138.4) < 0.01:
                    kinematicsType = "Ring"
                else:
                    kinematicsType = "Custom"
            motorSpacingX = self.data.config.getValue("Maslow Settings", "motorSpacingX")
            chainOverSprocket = self.data.config.getValue(
                "Advanced Settings", "chainOverSprocket"
            )
            print("MotorOffsetY=" + str(motorOffsetY))
            page = render_template(
                "quickConfigure.html",
                pageID="quickConfigure",
                motorOffsetY=motorOffsetY,
                rotationRadius=rotationRadius,
                kinematicsType=kinematicsType,
                motorSpacingX=motorSpacingX,
                chainOverSprocket=chainOverSprocket,
            )
            return page, "Quick Configure", False, "medium", "content", False
        elif pageID == "screenAction":
            print(args["x"])
            page = render_template("screenAction.html", posX=args["x"], posY=args["y"])
            return page, "Screen Action", False, "medium", "content", False
        elif pageID == "viewGcode":
            page = render_template("viewGcode.html", gcode=self.data.gcode)
            return page, "View GCode", False, "medium", "content", False
        elif pageID == "editGCode":
            text = ""
            for line in self.data.gcode:
                text = text + line + "\n"
            #text = self.gcodePreProcessor()
            page = render_template("editGCode.html", gcode=text.rstrip(), pageID="editGCode",)
            return page, "Edit GCode", True, "medium", "content", "footerSubmit"
        elif pageID == "sendGCode":
            text = self.data.sentCustomGCode
            page = render_template("editGCode.html", gcode=text, pageID="sendGCode", )
            return page, "Edit GCode", True, "medium", "content", "footerSubmit"
        elif pageID == "pidTuning":
            if self.data.controllerFirmwareVersion < 100:
                fourMotor = False
            else:
                fourMotor = True
            KpP = self.data.config.getValue("Advanced Settings", "KpPos")
            KiP = self.data.config.getValue("Advanced Settings", "KiPos")
            KdP = self.data.config.getValue("Advanced Settings", "KdPos")
            KpV = self.data.config.getValue("Advanced Settings", "KpV")
            KiV = self.data.config.getValue("Advanced Settings", "KiV")
            KdV = self.data.config.getValue("Advanced Settings", "KdV")
            vVersion = "1"
            pVersion = "1"
            page = render_template("pidTuning.html",
                                   KpP=KpP,
                                   KiP=KiP,
                                   KdP=KdP,
                                   KpV=KpV,
                                   KiV=KiV,
                                   KdV=KdV,
                                   vVersion=vVersion,
                                   pVersion=pVersion,
                                   fourMotor=fourMotor)
            return page, "PID Tuning", False, "large", "content", False
        elif pageID == "zpidTuning":
            fourMotor = False
            KpPZ = self.data.config.getValue("Advanced Settings", "KpPosZ")
            KiPZ = self.data.config.getValue("Advanced Settings", "KiPosZ")
            KdPZ = self.data.config.getValue("Advanced Settings", "KdPosZ")
            KpVZ = self.data.config.getValue("Advanced Settings", "KpVZ")
            KiVZ = self.data.config.getValue("Advanced Settings", "KiVZ")
            KdVZ = self.data.config.getValue("Advanced Settings", "KdVZ")
            zvVersion = "1"
            zpVersion = "1"
            page = render_template("zpidTuning.html",
                                   KpPZ=KpPZ,
                                   KiPZ=KiPZ,
                                   KdPZ=KdPZ,
                                   KpVZ=KpVZ,
                                   KiVZ=KiVZ,
                                   KdVZ=KdVZ,
                                   zvVersion=zvVersion,
                                   zpVersion=zpVersion)
            return page, "zPID Tuning", False, "large", "content", False

        elif pageID == "editBoard":
            board = self.data.boardManager.getCurrentBoard()
            scale = 1
            units = "inches"
            if self.data.units == "MM":
                scale = 25.4
                units = "mm"
            if isMobile:
                pageName = "editBoard_mobile.html"
            else:
                pageName = "editBoard.html"
            page = render_template(pageName,
                                   units=units,
                                   boardID=board.boardID,
                                   material=board.material,
                                   height=round(board.height*scale, 2),
                                   width=round(board.width*scale, 2),
                                   thickness=round(board.thickness*scale, 2),
                                   centerX=round(board.centerX*scale, 2),
                                   centerY=round(board.centerY*scale, 2),
                                   routerHorz=self.data.xval,
                                   routerVert=self.data.yval,
                                   pageID="editBoard")
            return page, "Create/Edit Board", False, "medium", "content", "footerSubmit"
        elif pageID == "trimBoard":
            board = self.data.boardManager.getCurrentBoard()
            scale = 1
            units = "inches"
            if self.data.units == "MM":
                scale = 25.4
                units = "mm"
            if isMobile:
                pageName = "trimBoard.html"
            else:
                pageName = "trimBoard.html"
            page = render_template(pageName,
                                   units=units,
                                   pageID="trimBoard")
            return page, "Trim Board", False, "medium", "content", "footerSubmit"
        elif pageID == "saveBoard":
            #lastSelectedFile = self.data.config.getValue("Maslow Settings", "openBoardFile")
            #print(lastSelectedFile)
            lastSelectedDirectory = self.data.config.getValue("Computed Settings", "lastSelectedBoardDirectory")
            lastSelectedFile = self.data.boardManager.getCurrentBoardFilename()
            home = self.data.config.getHome()
            homedir = home + "/.WebControl/boards"
            directories = []
            files = []
            try:
                for _root, _dirs, _files in os.walk(homedir):
                    if _dirs:
                        directories = _dirs
                    for file in _files:
                        if _root != homedir:
                            _dir = _root.split("\\")[-1].split("/")[-1]
                        else:
                            _dir = "."
                        files.append({"directory": _dir, "file": file})
            except Exception as e:
                print(e)
            # files = [f for f in listdir(homedir) if isfile(join(homedir, f))]
            directories.insert(0, "./")
            if lastSelectedDirectory is None:
                lastSelectedDirectory = "."
            page = render_template(
                "saveBoard.html", directories=directories, files=files, lastSelectedFile=lastSelectedFile,
                lastSelectedDirectory=lastSelectedDirectory, isOpen=False
            )
            return page, "Save Board", False, "medium", "content", "footerSubmit"
        elif pageID == "openBoard":
            lastSelectedFile = self.data.config.getValue("Maslow Settings", "openBoardFile")
            print(lastSelectedFile)
            lastSelectedDirectory = self.data.config.getValue("Computed Settings", "lastSelectedBoardDirectory")
            home = self.data.config.getHome()
            homedir = home+"/.WebControl/boards"
            directories = []
            files = []
            try:
                for _root, _dirs, _files in os.walk(homedir):
                    if _dirs:
                        directories = _dirs
                    for file in _files:
                        if _root != homedir:
                            _dir = _root.split("\\")[-1].split("/")[-1]
                        else:
                            _dir = "."
                        files.append({"directory":_dir, "file":file})
            except Exception as e:
                print(e)
           # files = [f for f in listdir(homedir) if isfile(join(homedir, f))]
            directories.insert(0, "./")
            if lastSelectedDirectory is None:
                lastSelectedDirectory="."
            page = render_template(
                "openBoard.html", directories=directories, files=files, lastSelectedFile=lastSelectedFile, lastSelectedDirectory=lastSelectedDirectory, isOpen=True
            )
            return page, "Open Board", False, "medium", "content", "footerSubmit"
        elif pageID == "about":
            version = self.data.pyInstallCurrentVersion
            if isMobile:
                pageName = "about.html"
            else:
                pageName = "about.html"
            page = render_template(pageName, pageID="about", version=version)
            return page, "About", False, "medium", "content", False
        elif pageID == "gettingStarted":
            if isMobile:
                pageName = "gettingStarted.html"
            else:
                pageName = "gettingStarted.html"
            page = render_template(pageName, pageID="gettingStarted")
            return page, "Getting Started", False, "medium", "content", False
        elif pageID == "releases":
            releases = self.data.releaseManager.getReleases()
            latestRelease = self.data.releaseManager.getLatestRelease()
            currentRelease = "v"+str(self.data.pyInstallCurrentVersion)
            for release in releases:
                tag_name = re.sub(r'[v]', r'', release.tag_name)
            if isMobile:
                page = render_template(
                    "releases_mobile.html",
                    title="Update Manager",
                    releases=releases,
                    latestRelease=latestRelease,
                    currentRelease=currentRelease,
                    pageID="releases",
                )
            else:
                page = render_template(
                    "releases.html",
                    title="Update Manager",
                    releases=releases,
                    latestRelease=latestRelease,
                    currentRelease=currentRelease,
                    pageID="releases",
                )
            return page, "Update Manager", False, "medium", "content", False
        elif pageID == "helpPages":
            helpPages = self.data.helpManager.getHelpPages()
            if isMobile:
                page = render_template(
                    "helpPages_mobile.html",
                    title="Help",
                    helpPages=helpPages,
                    pageID="help",
                )
            else:
                page = render_template(
                    "helpPages.html",
                    title="Help",
                    helpPages=helpPages,
                    pageID="help",
                )
            return page, "Help", False, "medium", "content", False
        elif pageID == "fakeServo":
            if isMobile:
                page = render_template(
                    "fakeServo.html",
                    title="Fake Servo",
                    pageID="fakeServo",
                )
            else:
                page = render_template(
                    "fakeServo.html",
                    title="Fake Servo",
                    pageID="fakeServo",
                )
            return page, "Fake Servo", False, "small", "content", False
        elif pageID == "help":
            helpIndex = self.getPage("/docs/assets/helpPages.md", isMobile)
            helpPage = self.getPage("/docs/index.md", isMobile)
            if isMobile:
                page = render_template(
                    "help_mobile.html",
                    title="Help",
                    helpIndex=helpIndex,
                    helpPage=helpPage,
                    pageID="help",
                )
            else:
                page = render_template(
                    "help.html",
                    title="Help",
                    helpIndex=helpIndex,
                    helpPage=helpPage,
                    pageID="help",
                )
            return page, "Help", False, "large", "content", False
        else:
            pageParts = pageID.split("/")
            if len(pageParts) > 1:
                # help page
                print(pageParts)
                helpIndex = self.getPage("/docs/assets/helpPages.md", isMobile)
                helpPage = self.getPage("/docs/"+pageID, isMobile)
                if isMobile:
                    helpIndex = self.createLinks(pageParts)
                    page = render_template(
                        "help_mobile.html",
                        title="Help",
                        helpIndex=helpIndex,
                        helpPage=helpPage,
                        pageID="help",
                    )
                else:
                    page = render_template(
                        "help.html",
                        title="Help",
                        helpIndex=helpIndex,
                        helpPage=helpPage,
                        pageID="help",
                    )
                #print(page)
                return page, "Help", False, "large", "content", False

            else:
                self.data.ui_queue1.put("Alert", "Alert", "Function not currently implemented.. Sorry.")

    def gcodePreProcessor(self):
        text = ""
        for line in self.data.gcode:
            text=text+line+"\n"
        return text

    def getPage(self, pageName, isMobile):
        if self.data.platform == "PYINSTALLER":
            lhome = os.path.join(self.data.platformHome)
        else:
            lhome = "."
        filename = lhome+pageName
        if filename.find("http") != -1:
            print("external link")
            return None
        with open(filename) as f:
            page = frontmatter.loads(f.read())
        pageContent = page.content
        #filterString = '([^\!]|^)\[(.+)\]\((.+)\)'
        filterString = '(?:[^\!]|^)\[([^\[\]]+)\]\((?!http)([^()]+)\)'
        filteredPage = re.sub(filterString, r"""<a href='#' onclick='requestPage("\2");'>\1</a>""", pageContent)
        filteredPage = filteredPage.replace("{{ site.baseurl }}{% link ","")
        filteredPage = filteredPage.replace(".md %}", ".md")
        filteredPage = markdown.markdown(filteredPage, extensions=["markdown.extensions.tables"])
        filteredPage = filteredPage.replace("Â", "")
        filteredPage = filteredPage.replace("{: .label .label-blue }", "")
        filteredPage = filteredPage.replace("<a href=\"http", "<a target='_blank' href=\"http")
        filteredPage = filteredPage.replace("<table>", "<table class='table'>")

        if isMobile:
            # make all images 100%
            filteredPage = filteredPage.replace("img alt=", "img width='100%' alt=")

        return filteredPage

    def createLinks(self, pageParts):
        link = "<a href='#' onclick='requestPage(\"help\");'>Home</a>"
        #assets/actions/Diagnostics Maintenance/index.md
        if len(pageParts) == 4 and pageParts[3]=='index.md':
            # third level index with form like:
            # ['assets', 'actions', 'Diagnostics Maintenance', 'index.md']
            forward = "assets/" + pageParts[1] + "/"
            pageLink = " / <a href='#' onclick='requestPage(\""+forward+pageParts[3]+"\");'>"+pageParts[1]+"</a>"
            link = link + pageLink
            return link
        if len(pageParts) == 3 and pageParts[2].endswith(".md") and pageParts[2] != "index.md":
            # fourth level index with form like:
            # ['Actions', 'Diagnostics Maintenance', 'testMotorsEncoders.md']
            forward = "assets/"+pageParts[0]+ "/index.md"
            pageLink = " / <a href='#' onclick='requestPage(\""+forward+"\");'>"+pageParts[0]+"</a>"
            link = link + pageLink
            forward = "assets/"+pageParts[0]+"/"+pageParts[1] + "/index.md"
            pageLink = " / <a href='#' onclick='requestPage(\""+forward+"\");'>"+pageParts[1]+"</a>"
            link = link + pageLink
            return link
        if len(pageParts) == 3 and pageParts[2].endswith(".md") and pageParts[2] == "index.md":
            # second level index with form like:
            # ['assets', 'actions', 'index.md']
            return link

        return link


    '''
    elif pageID == "opticalCalibration":
            socketio.emit("closeModals", {"data": {"title": "Actions"}}, namespace="/MaslowCNC")
            opticalCenterX = self.data.config.getValue("Optical Calibration Settings", "opticalCenterX")
            opticalCenterY = self.data.config.getValue("Optical Calibration Settings", "opticalCenterY")
            scaleX = self.data.config.getValue("Optical Calibration Settings", "scaleX")
            scaleY = self.data.config.getValue("Optical Calibration Settings", "scaleY")
            gaussianBlurValue = self.data.config.getValue("Optical Calibration Settings", "gaussianBlurValue")
            cannyLowValue = self.data.config.getValue("Optical Calibration Settings", "cannyLowValue")
            cannyHighValue = self.data.config.getValue("Optical Calibration Settings", "cannyHighValue")
            autoScanDirection = self.data.config.getValue("Optical Calibration Settings", "autoScanDirection")
            markerX = self.data.config.getValue("Optical Calibration Settings", "markerX")
            markerY = self.data.config.getValue("Optical Calibration Settings", "markerY")
            tlX = self.data.config.getValue("Optical Calibration Settings", "tlX")
            tlY = self.data.config.getValue("Optical Calibration Settings", "tlY")
            brX = self.data.config.getValue("Optical Calibration Settings", "brX")
            brY = self.data.config.getValue("Optical Calibration Settings", "brY")
            calibrationExtents = self.data.config.getValue("Optical Calibration Settings", "calibrationExtents")
            positionTolerance = self.data.config.getValue("Optical Calibration Settings", "positionTolerance")
            page = render_template("opticalCalibration.html", pageID="opticalCalibration", opticalCenterX=opticalCenterX, opticalCenterY=opticalCenterY, scaleX=scaleX, scaleY=scaleY, gaussianBlurValue=gaussianBlurValue, cannyLowValue=cannyLowValue, cannyHighValue=cannyHighValue, autoScanDirection=autoScanDirection, markerX=markerX, markerY=markerY, tlX=tlX, tlY=tlY, brX=brX, brY=brY, calibrationExtents=calibrationExtents, isMobile=isMobile, positionTolerance=positionTolerance)
            return page, "Optical Calibration", True, "large", "content", False
    '''
