---
layout: default
title: Wipe Controller Position & Settings
nav_order: 6
parent: Controller
grand_parent: Actions
---
# Wipe Controller Position & Settings
  
Release: >0.918
{: .label .label-blue }  

  
### Description
This function sends a command to the controller to reinitialize the positional data and the firmware settings. 

### Process

The process for wiping the controller positional data (i.e., chain lengths) and settings (based upon current stock firmware as of 11/27/19) is as follows:

* A special gcode command ($RST=#) is sent to the controller
* Controller writes a 0 value to EEPROM bytes associated with the positional data and the settings storage area.
* Controller will reset after completed.

New to 0.918 

* WebControl will wait for two seconds and then send a settings sync command ($$) to resend WebControl's settings to the controller.
* WebControl will send a command to the controller (B04) to set the chain lengths equal to the 'Extend Chain Distance' in Advanced Settings
 
 
