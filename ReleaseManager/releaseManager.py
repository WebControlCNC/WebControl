from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
import time
import json
import datetime
import os
import glob
import zipfile
import re
from github import Github
import wget
import subprocess
import shutil
import datetime
import sys
from app import socketio

class ReleaseManager(MakesmithInitFuncs):

    def __init__(self):
        pass

    releases = None
    latestRelease = None

    def fetchReleases(self):
        try:
            print("Fetching GitHub releases.")
            g = Github()
            repo = g.get_repo("WebControlCNC/WebControl")
            self.releases = repo.get_releases()
            for release in self.releases:
                release.tag_version = 0
                release.tag_date = datetime.datetime(1, 1, 1, 0, 0)

                versionPattern = re.compile(r"^v?([0-9.]+)_?([0-9]{4}-[0-9]{2}-[0-9]{2})?$")
                versionInfo = versionPattern.match(release.tag_name)
                if (versionInfo):
                    release.tag_version = float(versionInfo.group(1))
                    if (versionInfo.group(2)):
                        release.tag_date = datetime.datetime.strptime("%Y-%m-%d", versionInfo.group(2))
                    else:
                        release.tag_date = release.published_at
                else:
                    # This release tage name is not valid.
                    print("Release tag invlaid: " + release.tag_name)
                    # For testing of temp release.
                    if (release.tag_name == "2020-05-26-2021"):
                        release.tag_version = 0.94
                        release.tag_date = datetime.datetime(2020, 5, 26)

        except Exception as e:
            print("Error fetching github releases: " + str(e))

    def getValidReleases(self, refresh = False):
        if (self.releases is None or refresh):
            self.fetchReleases()

        try:
            print("Getting valid releases.")
            enablePreRelease = self.data.config.getValue("WebControl Settings", "experimentalReleases")
            tempReleases = []
            for release in self.releases:
                if release.prerelease:
                    if enablePreRelease:
                        # Add experimental releases is setting enabled.
                        tempReleases.append(release)
                else:
                    # Add stable releases.
                    tempReleases.append(release)
            return tempReleases

        except Exception as e:
            print("Error getting valid releases: " + str(e))

    def getLatestValidRelease(self, refresh = False):
        if (self.latestRelease == None or refresh):
            self.checkLatestRelease()

        return self.latestRelease

    def checkLatestRelease(self, refresh = False):
        if True:  # self.data.platform=="PYINSTALLER":
            try:
                print("Checking latest valid release.")
                validReleases = self.getValidReleases(refresh)
                self.latestRelease = None
                latestVersionNumber = 0
                latestVersionDate = datetime.datetime(1, 1, 1, 0, 0)

                for release in validReleases:
                    if (release.tag_version > latestVersionNumber):
                        latestVersionNumber = release.tag_version
                        latestVersionDate = release.tag_date
                        self.latestRelease = release
                    elif (release.tag_version == latestVersionNumber and release.tag_date > latestVersionDate):
                        latestVersionDate = release.tag_date
                        self.latestRelease = release

                print("Latest release: " + str(self.latestRelease.tag_name))

                if self.latestRelease is not None and latestVersionNumber >= self.data.pyInstallCurrentVersionNumber and latestVersionDate > self.data.pyInstallCurrentVersionDate:
                    print("Fetching Assets for release: " + self.latestRelease.tag_name)
                    assets = self.latestRelease.get_assets()
                    for asset in assets:
                        if asset.name.find(self.data.pyInstallType) != -1 and asset.name.find(self.data.pyInstallPlatform) != -1:
                            print(asset.name)
                            print(asset.url)
                            self.data.ui_queue1.put("Action", "pyinstallUpdate", "on")
                            self.data.pyInstallUpdateAvailable = True
                            self.data.pyInstallUpdateBrowserUrl = asset.browser_download_url
                            self.data.pyInstallUpdateVersion = self.latestRelease

            except Exception as e:
                print("Error checking latest valid release: " + str(e))

    def processAbsolutePath(self, path):
        index = path.find("main.py")
        self.data.pyInstallInstalledPath = path[0:index - 1]
        print(self.data.pyInstallInstalledPath)

    def wgetBarCustom(self, current, total, width=80):
        percentDone = int(current / total * 100)
        data = {
            "percent": percentDone,
            "current" : current,
            "total" : total,
            }
        socketio.emit("message", {"command": "upgradeDownload", "data": json.dumps(data), "dataFormat": "json"}, namespace="/MaslowCNC", room="modal")
        print("Downloading: %d%% [%d / %d] bytes" % (percentDone, current, total))

    def updatePyInstaller(self, bypassCheck = False):
        try:
            home = self.data.config.getHome()

            if self.data.pyInstallUpdateAvailable == True or bypassCheck:
                if not os.path.exists(home + "/.WebControl/downloads"):
                    self.emitStatusUpdate("Creating downloads directory.")
                    os.mkdir(home + "/.WebControl/downloads", exists_ok=True)

                fileList = glob.glob(home + "/.WebControl/downloads/*.gz")

                for filePath in fileList:
                    os.remove(filePath)

                self.emitStatusUpdate("Downloading new release.")
                if self.data.pyInstallPlatform == "win32" or self.data.pyInstallPlatform == "win64":
                    filename = wget.download(self.data.pyInstallUpdateBrowserUrl, out=home + "\\.WebControl\\downloads", bar = self.wgetBarCustom)
                else:
                    filename = wget.download(self.data.pyInstallUpdateBrowserUrl, out=home + "/.WebControl/downloads", bar = self.wgetBarCustom)
                self.emitStatusUpdate("Successfully downloaded new release to:" + filename)

                if self.data.platform == "PYINSTALLER":
                    lhome = os.path.join(self.data.platformHome)
                else:
                    lhome = "."

                self.emitStatusUpdate("Creating target version directory.")
                target_dir = self.data.pyInstallInstalledPath + '_next'
                if os.path.exists(target_dir):
                    self.emitStatusUpdate("New release directory already exists, removing it.")
                    shutil.rmtree(target_dir)
                os.mkdir(target_dir)

                self.emitStatusUpdate("Extracting new release.")
                if self.data.pyInstallPlatform == "win32" or self.data.pyInstallPlatform == "win64":
                    command = [
                        lhome + "/tools/7za.exe",
                        "x",
                        "-y",
                        filename,
                        "-o",
                        target_dir
                    ]
                    print(command)
                    subprocess.run(command)
                else:
                    command = [
                        "tar",
                        "-zxf",
                        filename,
                        "-C",
                        target_dir
                    ]
                    print(command)
                    subprocess.run(command)

                self.emitStatusUpdate("Checking for upgrade script.")
                if self.data.pyInstallPlatform == "win32" or self.data.pyInstallPlatform == "win64":
                    upgrade_script_path = target_dir + "\\tools\\upgrade_" + self.data.pyInstallPlatform + ".bat"
                else:
                    upgrade_script_path = target_dir + "/tools/upgrade_" + self.data.pyInstallPlatform + ".sh"
                if os.path.exists(upgrade_script_path):
                    self.emitStatusUpdate("Running upgrade script.")
                    self.make_executable(upgrade_script_path)
                    subprocess.run([upgrade_script_path])
                else:
                    self.emitStatusUpdate("Upgrade script not required.")

                self.emitStatusUpdate("Backing up the current install.")
                backup_path = self.data.pyInstallInstalledPath + '_old'
                print("Backup location: " + backup_path)
                if os.path.exists(backup_path):
                    self.emitStatusUpdate("Old backup found, removing it.")
                    shutil.rmtree(backup_path)
                os.rename(self.data.pyInstallInstalledPath, self.data.pyInstallInstalledPath + '_old')
                print("Backing up the current install DONE")

                self.emitStatusUpdate("Moving the target version in place.")
                os.rename(target_dir, self.data.pyInstallInstalledPath)
                print("Moving the target version in place DONE")

                self.emitStatusUpdate("WebControl upgrade complete.")
                socketio.emit("message", {"command": "upgradeSuccess", "data": "success", "dataFormat": "text"}, namespace="/MaslowCNC", room="modal")
                # Restart application terminating current.
                return True

        except Exception as e:
            self.emitStatusUpdate("Error updating release: " + str(e))
            return False

    def make_executable(self, path):
        print("1")
        mode = os.stat(path).st_mode
        print("2")
        mode |= (mode & 0o444) >> 2  # copy R bits to X
        print("3")
        os.chmod(path, mode)
        print("4")

    def update(self, releaseTagName):
        '''
        :param releaseTagName:
        :return:
        '''
        try:
            validReleases = self.getValidReleases()
            releaseAssetsFound = False
            for release in validReleases:
                if release.tag_name == releaseTagName:
                    assets = release.get_assets()
                    for asset in assets:
                        if asset.name.find(self.data.pyInstallType) != -1 and asset.name.find(self.data.pyInstallPlatform) != -1:
                            print(asset.name)
                            print(asset.url)
                            self.data.pyInstallUpdateBrowserUrl = asset.browser_download_url
                            print(self.data.pyInstallUpdateBrowserUrl)
                            releaseAssetsFound = True
                            break
            if releaseAssetsFound:
                return self.updatePyInstaller(True)
            else:
                raise Exception("Assets not found for release: " + str(releaseTagName))

        except Exception as e:
            print("Update error: " + str(e))
            return False

    def emitStatusUpdate(self, text):
        print(text)
        socketio.emit("message", {"command": "upgradeStatus", "data": text, "dataFormat": "text"}, namespace="/MaslowCNC", room="modal")
