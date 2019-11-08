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
from shutil import copyfile


class ReleaseManager(MakesmithInitFuncs):

    def __init__(self):
        pass

    releases = None
    latestRelease = None

    def getReleases(self):
        return self.releases

    def getLatestRelease(self):
        return self.latestRelease

    def checkForLatestPyRelease(self):
        if True:  # self.data.platform=="PYINSTALLER":
            print("check for pyrelease")
            g = Github()
            repo = g.get_repo("madgrizzle/WebControl")
            self.releases = repo.get_releases()
            latest = 0
            latestRelease = None
            type = self.data.pyInstallType
            platform = self.data.pyInstallPlatform
            for release in self.releases:
                try:
                    tag_name = re.sub(r'[v]', r'', release.tag_name)
                    # print(tag_name)
                    if float(tag_name) > latest:
                        latest = float(tag_name)
                        self.latestRelease = release

                except:
                    print("error parsing tagname")
            print(latest)
            if latest > self.data.pyInstallCurrentVersion:
                if self.latestRelease is not None:
                    print(self.latestRelease.tag_name)
                    assets = self.latestRelease.get_assets()
                    for asset in assets:
                        if asset.name.find(type) != -1 and asset.name.find(platform) != -1:
                            print(asset.name)
                            print(asset.url)
                            self.data.ui_queue1.put("Action", "pyinstallUpdate", "on")
                            self.data.pyInstallUpdateAvailable = True
                            self.data.pyInstallUpdateBrowserUrl = asset.browser_download_url
                            self.data.pyInstallUpdateVersion = latest

    def processAbsolutePath(self, path):
        index = path.find("main.py")
        self.data.pyInstallInstalledPath = path[0:index - 1]
        print(self.data.pyInstallInstalledPath)

    def updatePyInstaller(self, bypassCheck = False):
        home = self.data.config.getHome()
        if self.data.pyInstallUpdateAvailable == True or bypassCheck:
            if not os.path.exists(home + "/.WebControl/downloads"):
                print("creating downloads directory")
                os.mkdir(home + "/.WebControl/downloads")
            fileList = glob.glob(home + "/.WebControl/downloads/*.gz")
            for filePath in fileList:
                try:
                    os.remove(filePath)
                except:
                    print("error cleaning download directory: ", filePath)
                    print("---")
            if self.data.pyInstallPlatform == "win32" or self.data.pyInstallPlatform == "win64":
                filename = wget.download(self.data.pyInstallUpdateBrowserUrl, out=home + "\\.WebControl\\downloads")
            else:
                filename = wget.download(self.data.pyInstallUpdateBrowserUrl, out=home + "/.WebControl/downloads")
            print(filename)

            if self.data.platform == "PYINSTALLER":
                lhome = os.path.join(self.data.platformHome)
            else:
                lhome = "."
            if self.data.pyInstallPlatform == "win32" or self.data.pyInstallPlatform == "win64":
                path = lhome + "/tools/upgrade_webcontrol_win.bat"
                copyfile(path, home + "/.WebControl/downloads/upgrade_webcontrol_win.bat")
                path = lhome + "/tools/7za.exe"
                copyfile(path, home + "/.WebControl/downloads/7za.exe")
                self.data.pyInstallInstalledPath = self.data.pyInstallInstalledPath.replace('/', '\\')
                program_name = home + "\\.WebControl\\downloads\\upgrade_webcontrol_win.bat"

            else:
                path = lhome + "/tools/upgrade_webcontrol.sh"
                copyfile(path, home + "/.WebControl/downloads/upgrade_webcontrol.sh")
                program_name = home + "/.WebControl/downloads/upgrade_webcontrol.sh"
                self.make_executable(home + "/.WebControl/downloads/upgrade_webcontrol.sh")
            tool_path = home + "\\.WebControl\\downloads\\7za.exe"
            arguments = [filename, self.data.pyInstallInstalledPath, tool_path]
            command = [program_name]
            command.extend(arguments)
            print("popening")
            print(command)
            subprocess.Popen(command)
            return True
        return False

    def make_executable(self, path):
        print("1")
        mode = os.stat(path).st_mode
        print("2")
        mode |= (mode & 0o444) >> 2  # copy R bits to X
        print("3")
        os.chmod(path, mode)
        print("4")


    def update(self, version):
        if version == self.latestRelease.tag_name:
            return self.updatePyInstaller()
        else:
            print("downgrade to ")
            print(version)
            type = self.data.pyInstallType
            platform = self.data.pyInstallPlatform
            for release in self.releases:
                if release.tag_name == version:
                    assets = release.get_assets()
                    for asset in assets:
                        if asset.name.find(type) != -1 and asset.name.find(platform) != -1:
                            print(asset.name)
                            print(asset.url)
                            self.data.pyInstallUpdateBrowserUrl = asset.browser_download_url
                            print(self.data.pyInstallUpdateBrowserUrl)
                            return self.updatePyInstaller(True)


