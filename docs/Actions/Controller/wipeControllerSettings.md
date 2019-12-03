---
layout: default
title: Wipe Controller Settings
nav_order: 5
parent: Controller
grand_parent: Actions
---
# Wipe Controller Settings
  
Release: >0.918
{: .label .label-blue }  

  
### Description
This function sends a command to the controller to reinitialize the firmware settings. 

### Process

The process for wiping the controller settings (based upon current stock firmware as of 11/27/19) is as follows:

* A special gcode command ($RST=$) is sent to the controller
* Controller writes a 0 value to EEPROM bytes associated with the settings storage area.
* Controller will reset after completed.

New to 0.918 

* WebControl will wait for two seconds and then send a settings sync command ($$) to resend WebControl's settings to the controller.
 

