---
layout: default
title: Upgrade Holey Firmware
nav_order: 2
parent: Controller
grand_parent: Actions
---
# Upgrade Holey Firmware
  
Release: >0.906
{: .label .label-blue }  

  
### Description
This function upgrades the controller firmware with the 'holey calibration' firmware included in the WebControl release.  When running holey firmware, 'Holey Calibration' is enabled.

### Process

The process for upgrading the holey firmware (based upon current stock firmware as of 11/27/19) is as follows:

* WebControl closes the serial connection to the controller and pauses trying to reconnect.
* WebControls calls a system command to update the controller firmware.
* After the system command returns, the connection to the controller is reestablished.

### Technical Details

To update the firmware, WebControl uses the os.system() command to call 'avrdude' to upgrade the firmware.  avrdude is included in the release in the tools directory.  Each release contains a version that is compatible with the release's operating system, however, the linux version is based upon Ubuntu and may not work on other linux distributions.

### Troubleshooting

|Result   	|Possible Cause/Solution   	|
|---	|---	|
|xxxx   	|xxxx.   	|
|xxxx   	|xxxx.   	|