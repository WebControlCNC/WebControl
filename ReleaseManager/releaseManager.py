from DataStructures.makesmithInitFuncs import MakesmithInitFuncs

import os
import glob
import re
from shutil import copyfile
import subprocess

from github import Github
import requests


class ReleaseManager(MakesmithInitFuncs):
    def __init__(self):
        pass

    releases = None
    latestRelease = None

    def getReleases(self):
        tempReleases = []
        enableExperimental = self.data.config.getValue(
            "WebControl Settings", "experimentalReleases"
        )
        for release in self.releases:
            if not enableExperimental:
                if not self.isExperimental(re.sub(r"[v]", r"", release.tag_name)):
                    tempReleases.append(release)
            else:
                tempReleases.append(release)
        return tempReleases

    def getLatestRelease(self):
        return self.latestRelease

    def checkForLatestPyRelease(self):
        if True:  # self.data.platform=="PYINSTALLER":
            print(f"{__name__}: Checking latest pyrelease.")
            try:
                enableExperimental = self.data.config.getValue(
                    "WebControl Settings", "experimentalReleases"
                )
                g = Github()
                repo = g.get_repo("WebControlCNC/WebControl")
                self.releases = repo.get_releases()
                latestVersionGithub = 0
                self.latestRelease = None
                # Map tags that didn't use the `vX.Y` numbering to a floatable value
                release_tag_map = {"2020-05-26-2021": "0.939"}
                for release in self.releases:
                    tag_name = re.sub(r"[v]", r"", release.tag_name)
                    if tag_name in release_tag_map:
                        tag_name = release_tag_map[tag_name]
                    tag_float = float(tag_name)
                    eligible = False
                    if not enableExperimental:
                        if not self.isExperimental(tag_name):
                            eligible = True
                    else:
                        eligible = True
                    # print("tag:"+tag_name+", eligible:"+str(eligible))
                    if eligible and tag_float > latestVersionGithub:
                        latestVersionGithub = tag_float
                        self.latestRelease = release

                print(f"{__name__}: Latest pyrelease: {latestVersionGithub}")
                if (
                    self.latestRelease is not None
                    and latestVersionGithub > self.data.pyInstallCurrentVersion
                ):
                    print(f"{__name__}: Latest release tag: {self.latestRelease.tag_name}")
                    assets = self.latestRelease.get_assets()
                    for asset in assets:
                        if (
                            asset.name.find(self.data.pyInstallType) != -1
                            and asset.name.find(self.data.pyInstallPlatform) != -1
                        ):
                            print(f"{__name__}: {asset.name}")
                            print(f"{__name__}: {asset.url}")
                            self.data.ui_queue1.put("Action", "pyinstallUpdate", "on")
                            self.data.pyInstallUpdateAvailable = True
                            self.data.pyInstallUpdateBrowserUrl = (
                                asset.browser_download_url
                            )
                            self.data.pyInstallUpdateVersion = self.latestRelease
            except Exception as e:
                print(f"{__name__}: Error checking pyrelease: {e}")

    def isExperimental(self, tag):
        """
        Deternmines if release is experimental.  All even releases are stable, odd releases are experimental
        :param tag:
        :return:
        """
        if float(tag) <= 0.931:  # all releases before now are 'stable'
            return False
        lastDigit = tag[-1]
        if (int(lastDigit) % 2) == 0:  # only even releases are 'stable'
            return False
        else:
            return True

    def processAbsolutePath(self, path):
        index = path.find("main.py")
        self.data.pyInstallInstalledPath = path[0 : index - 1]
        print(f"{__name__}: {self.data.pyInstallInstalledPath}")

    def updatePyInstaller(self, bypassCheck=False):
        home = self.data.config.getHome()
        if self.data.pyInstallUpdateAvailable == True or bypassCheck:
            if not os.path.exists(home + "/.WebControl/downloads"):
                print(f"{__name__}: creating downloads directory")
                os.mkdir(home + "/.WebControl/downloads")
            fileList = glob.glob(home + "/.WebControl/downloads/*.gz")
            for filePath in fileList:
                try:
                    os.remove(filePath)
                except:
                    print(f"{__name__}: error cleaning download directory: {filePath}")
                    print(f"{__name__}: ---")
            req = requests.get(self.data.pyInstallUpdateBrowserUrl)
            if (
                self.data.pyInstallPlatform == "win32"
                or self.data.pyInstallPlatform == "win64"
            ):
                filename = home + "\\.WebControl\\downloads"
            else:
                filename = home + "/.WebControl/downloads"
            open(filename, "wb").write(req.content)
            print(f"{__name__}: {filename}")

            if self.data.platform == "PYINSTALLER":
                lhome = os.path.join(self.data.platformHome)
            else:
                lhome = "."
            if (
                self.data.pyInstallPlatform == "win32"
                or self.data.pyInstallPlatform == "win64"
            ):
                path = lhome + "/tools/upgrade_webcontrol_win.bat"
                copyfile(
                    path, home + "/.WebControl/downloads/upgrade_webcontrol_win.bat"
                )
                path = lhome + "/tools/7za.exe"
                copyfile(path, home + "/.WebControl/downloads/7za.exe")
                self.data.pyInstallInstalledPath = (
                    self.data.pyInstallInstalledPath.replace("/", "\\")
                )
                program_name = (
                    home + "\\.WebControl\\downloads\\upgrade_webcontrol_win.bat"
                )

            else:
                path = lhome + "/tools/upgrade_webcontrol.sh"
                copyfile(path, home + "/.WebControl/downloads/upgrade_webcontrol.sh")
                program_name = home + "/.WebControl/downloads/upgrade_webcontrol.sh"
                self.make_executable(
                    home + "/.WebControl/downloads/upgrade_webcontrol.sh"
                )
            tool_path = home + "\\.WebControl\\downloads\\7za.exe"
            arguments = [filename, self.data.pyInstallInstalledPath, tool_path]
            command = [program_name]
            command.extend(arguments)
            print(f"{__name__}: popening")
            print(f"{__name__}: {command}")
            subprocess.Popen(command)
            return True
        return False

    def make_executable(self, path):
        print(f"{__name__}: 1")
        mode = os.stat(path).st_mode
        print(f"{__name__}: 2")
        mode |= (mode & 0o444) >> 2  # copy R bits to X
        print(f"{__name__}: 3")
        os.chmod(path, mode)
        print(f"{__name__}: 4")

    def update(self, version):
        """
        Need to clean this up.
        :param version:
        :return:
        """
        for release in self.releases:
            if release.tag_name == version:
                assets = release.get_assets()
                for asset in assets:
                    if (
                        asset.name.find(self.data.pyInstallType) != -1
                        and asset.name.find(self.data.pyInstallPlatform) != -1
                    ):
                        print(f"{__name__}: {asset.name}")
                        print(f"{__name__}: {asset.url}")
                        self.data.pyInstallUpdateBrowserUrl = asset.browser_download_url
                        print(f"{__name__}: {self.data.pyInstallUpdateBrowserUrl}")
                        return self.updatePyInstaller(True)
        print(f"{__name__}: hmmm.. issue")
        return False
