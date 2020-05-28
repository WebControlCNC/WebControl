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


class ReleaseManager(MakesmithInitFuncs):

    def __init__(self):
        pass

    releases = None
    latestRelease = None

    def getReleases(self):
        tempReleases = []
        enableExperimental = self.data.config.getValue("WebControl Settings", "experimentalReleases")
        for release in self.releases:
            if not enableExperimental:
                if not self.isExperimental(re.sub(r'[v]', r'', release.tag_name)):
                    tempReleases.append(release)
            else:
                tempReleases.append(release)
        return tempReleases


    def getLatestRelease(self):
        return self.latestRelease

    def checkForLatestPyRelease(self):
        if True:  # self.data.platform=="PYINSTALLER":
            print("Checking latest pyrelease.")
            try:
                enableExperimental = self.data.config.getValue("WebControl Settings", "experimentalReleases")
                g = Github()
                repo = g.get_repo("WebControlCNC/WebControl")
                self.releases = repo.get_releases()
                latestVersionGithub = 0
                self.latestRelease = None
                for release in self.releases:
                    tag_name = re.sub(r'[v]', r'', release.tag_name)
                    tag_float = float(tag_name)
                    eligible = False
                    if not enableExperimental:
                        if not self.isExperimental(release):
                            eligible = True
                    else:
                        eligible = True
                    #print("tag:"+tag_name+", eligible:"+str(eligible))
                    if eligible and tag_float > latestVersionGithub:
                        latestVersionGithub = tag_float
                        self.latestRelease = release

                print("Latest pyrelease: " + str(latestVersionGithub))
                if self.latestRelease is not None and latestVersionGithub > self.data.pyInstallCurrentVersion:
                    print("Latest release tag: " + self.latestRelease.tag_name)
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
                print("Error checking pyrelease: " + str(e))

    def isExperimental(self, release):
        '''
        Deternmines if release is experimental. Pre-Releases are experimental.
        :param tag:
        :return:
        '''
        if release.prerelease:
            return True
        else:
            return False

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
            print("Downloading new WebControl release...")
            if self.data.pyInstallPlatform == "win32" or self.data.pyInstallPlatform == "win64":
                filename = wget.download(self.data.pyInstallUpdateBrowserUrl, out=home + "\\.WebControl\\downloads")
            else:
                filename = wget.download(self.data.pyInstallUpdateBrowserUrl, out=home + "/.WebControl/downloads")
            print("Successfully downloaded new release to:" + filename)

            if self.data.platform == "PYINSTALLER":
                lhome = os.path.join(self.data.platformHome)
            else:
                lhome = "."

            print("Creating target version directory...")
            target_dir = self.data.pyInstallInstalledPath + '_next'
            if os.path.exists(target_dir):
                print("New release directory already exists, removing it")
                shutil.rmtree(target_dir)
            os.mkdir(target_dir)
            print("Creating target version directory DONE")

            print("Unzipping new release...")
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
            print("Unzipping new release DONE")

            print("Upgrade script...")
            print("Checking if it needs to be run for platform: " + self.data.pyInstallPlatform)
            if self.data.pyInstallPlatform == "win32" or self.data.pyInstallPlatform == "win64":
                upgrade_script_path = target_dir + "\\tools\\upgrade_" + self.data.pyInstallPlatform + ".bat"
            else:
                upgrade_script_path = target_dir + "/tools/upgrade_" + self.data.pyInstallPlatform + ".sh"
            if os.path.exists(upgrade_script_path):
                print("Yes, running it")
                self.make_executable(upgrade_script_path)
                subprocess.run([upgrade_script_path])
            else:
                print("No upgrade script needed.")
            print("Upgrade script DONE")

            print("Backing up the current install...")
            backup_path = self.data.pyInstallInstalledPath + '_old'
            print("Backup location: " + backup_path)
            if os.path.exists(backup_path):
                print("Old backup found, removing it")
                shutil.rmtree(backup_path)
            os.rename(self.data.pyInstallInstalledPath, self.data.pyInstallInstalledPath + '_old')
            print("Backing up the current install DONE")

            print("Moving the target version in place...")
            os.rename(target_dir, self.data.pyInstallInstalledPath)
            print("Moving the target version in place DONE")

            print("WebControl upgrade complete, shutting down to make way to the target version")
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
        '''
        Need to clean this up.
        :param version:
        :return:
        '''
        for release in self.releases:
            if release.tag_name == version:
                assets = release.get_assets()
                for asset in assets:
                    if asset.name.find(self.data.pyInstallType) != -1 and asset.name.find(self.data.pyInstallPlatform) != -1:
                        print(asset.name)
                        print(asset.url)
                        self.data.pyInstallUpdateBrowserUrl = asset.browser_download_url
                        print(self.data.pyInstallUpdateBrowserUrl)
                        return self.updatePyInstaller(True)
        print("Couldn't find a suitable file for the current platform and target version: " + version)
        return False


