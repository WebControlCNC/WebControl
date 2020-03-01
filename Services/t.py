#!/usr/bin/python3

import requests

URL = "http://localhost:5000/GPIO"

r=requests.put(URL, "gcode:startRun")
r=requests.put(URL, "gcode:pauseRun")
r=requests.put(URL, "gcode:stopRun")
r=requests.put(URL, "move:up")
r=requests.put(URL, "move:down")
r=requests.put(URL, "move:left")
r=requests.put(URL, "move:right")

URL = "http://localhost:5000/pendant"

r=requests.put(URL, "system:connected")
r=requests.put(URL, "system:disconnect")
r=requests.put(URL, "gcode:startRun")
r=requests.put(URL, "gcode:pauseRun")
r=requests.put(URL, "gcode:resumeRun")
r=requests.put(URL, "gcode:stopRun")
r=requests.put(URL, "sled:up")
r=requests.put(URL, "sled:down")
r=requests.put(URL, "sled:left")
r=requests.put(URL, "sled:right")
r=requests.put(URL, "zAxis:raise")
r=requests.put(URL, "zAxis:lower")
r=requests.put(URL, "zAxis:stopZ")
r=requests.put(URL, "zAxis:defineZ0")
r=requests.put(URL, "sled:home")
r=requests.put(URL, "sled:defineHome")
