from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
import re
import requests
from github import Github

class HelpManager(MakesmithInitFuncs):

    def __init__(self):
        pass

    releases = None
    latestRelease = None

    def getReleases(self):
        return self.releases

    def getLatestRelease(self):
        return self.latestRelease

    def checkForUpdatedHelp(self):
        self.getWikiUrls()
        return True

    def getWikiUrls(self):

        url = 'https://api.github.com/graphql'
        json = {'query': '{ viewer { repositories(first: 30) { totalCount pageInfo { hasNextPage endCursor } edges { node { name } } } } }'}
        api_token = "your api token here..."
        headers = {'Authorization': 'token %s' % api_token}

        r = requests.post(url=url, json=json)
        print(r.text)

        '''
        g = Github()
        self.wiki = g.get_repo("madgrizzle/WebControl.wiki.repo")
        print(self.wiki)
        
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
        '''
