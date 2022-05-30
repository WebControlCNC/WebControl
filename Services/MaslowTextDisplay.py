#!/usr/bin/python3

import requests
import json

def Get(address,command):
    try:
        URL = "http://localhost:5000/" + str(address)
        #print (URL)
        r = requests.get(URL,params = command)
        #print (r.text)
        return r.json()
    except:
        print ('error getting data, check server')
        return ('error:error')
    
flag = '0'    
while True:
    items = Get('LED','stuff')
    if (items != None):
        flag = items["data"]["flag"]
        index = items["data"]["index"]
        moving = items["data"]["moving"]
        zMove = items["data"]["zMove"]
        wiiPendantPresent = items["data"]["wiiPendantPresent"]
        #print (flag)
        #print (index)
        #print (moving)
        wiiconnected = bool(items["data"]["wiiconnected"])
        clidisplay = bool(items["data"]["clidisplay"])
        sledX = float(items["data"]["sled_location_X"])
        sledY = float(items["data"]["sled_location_y"])
        #"sled_location_z": str(app.data.zval), \
        homeX = float(items["data"]["home_location_x"])
        homeY = float(items["data"]["home_location_y"])
        xmin = items["data"]["gcode_min_x"]
        xmax = float(items["data"]["gcode_max_x"])
        ymin = items["data"]["gcode_min_y"]
        ymax = float(items["data"]["gcode_max_y"])
        #print (index)
        #print (moving)
        print(items)