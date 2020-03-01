#!/usr/bin/python3

#get.py

import requests

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
items = Get('LED','stuff')
if (items != None):
    if (flag == "0"):
        if(items["data"]["flag"] == "1"):
            pass#start_time = time.time()
    else:
        if(items["data"]["flag"] == "0"):
           pass# stop_time = time.time()
    flag = items["data"]["flag"]
    index = items["data"]["index"]
    moving = items["data"]["moving"]
    zMove = items["data"]["zMove"]
    wiiPendantPresent = bool(items["data"]["wiiPendantPresent"])
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
