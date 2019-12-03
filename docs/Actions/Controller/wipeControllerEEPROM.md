---
layout: default
title: Wipe Controller EEPROM
nav_order: 7
parent: Controller
grand_parent: Actions
---
# Wipe Controller EEPROM
  
Release: >0.918
{: .label .label-blue }  

  
### Description
This function sends a command to the controller to fully wipe the EEPROM, including the positional data and the firmware settings.  This function is intended to restore the EEPROM back to original clean condition. 

### Process

The process for wiping the EEPROM based upon current stock firmware as of 11/27/19) is as follows:

* A special gcode command ($RST=*) is sent to the controller
* Controller writes a 0 value to the entire EEPROM memory space.  This will delete all positional data and settings as well as FAKE_SERVO settings.
* Controller will reset after completed.

New to 0.918 

* WebControl will wait for two seconds and then send a settings sync command ($$) to resend WebControl's settings to the controller.
* WebControl will send a command to the controller (B04) to set the chain lengths equal to the 'Extend Chain Distance' in Advanced Settings
 
 
