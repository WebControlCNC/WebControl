---
layout: default
title: Upgrade Custom Firmware
nav_order: 3
parent: Controller
grand_parent: Actions
---
# Upgrade Custom Firmware
  
Release: >0.906
{: .label .label-blue }  

  
### Description
This function upgrades the controller firmware with the 'custom' firmware included in the WebControl release.  This is highly experimental and not recommended for anyone to attempt to use... except for madgrizzle.. it's what he uses to experiment.  When running custom firmware, 'Optical Calibration' is enabled.

### Process

The process for upgrading the custom firmware (based upon current stock firmware as of 11/27/19) is as follows:

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