---
layout: default
title: Return to Center
nav_order: 8
parent: Calibration / Setup
grand_parent: Actions
WCVersion: 0.916
---
# Return to Center

Release: >0.906
{: .label .label-blue }

### Description
This function instructs WebControl to send a command to the controller to return the sled to center of the work area.

### Process

WebControl places the controller in absolute position mode by sending:

`G90`

WebControl instructs the controller to raise the Z-axis to the 'safe height' (Maslow Settings -> Z-Axis Safe Travel Height in MM)

`G00 Zxx`

where xx is the value for the safe height.

Maslow instructs the controller to move to the center of the work area (i.e., 0,0)

`G00 X0.0, Y0.0`

### Troubleshooting

|Result   	|Possible Cause/Solution   	|
|---	|---	|
|xxxx   	|xxxx.   	|
|xxxx   	|xxxx.   	|


