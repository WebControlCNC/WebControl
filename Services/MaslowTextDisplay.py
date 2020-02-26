#!/usr/bin/python3

import requests
import json

while True:
    data = Get('LED','stuff')
        if (items != None):
            flag = items["data"]["flag"]
            index = items["data"]["index"]
            moving = items["data"]["moving"]
            zMove = items["data"]["zMove"]
            wiiPendantPresent = items["data"]["wiiPendantPresent"]
            #print (flag)
            #print (index)
            #print (moving)
        print(items)