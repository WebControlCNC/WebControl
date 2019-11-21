from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
import re
import requests
from github import Github
import base64

class HelpManager(MakesmithInitFuncs):

    def __init__(self):
        pass

    repo = None

    def getReleases(self):
        return self.releases

    def getLatestRelease(self):
        return self.latestRelease

    def checkForUpdatedHelp(self):
        pages = self.getHelpPages()
        print(pages)
        return True

    def getHelpPages(self):
        g = Github()
        self.repo = g.get_repo("madgrizzle/WebControl")
        contents = self.repo.get_contents("docs")
        pages = []
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(self.repo.get_contents(file_content.path))
            else:
                pages.append({"name": file_content.name, "download_url": file_content.download_url})
        return pages
