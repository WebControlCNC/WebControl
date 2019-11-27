---
layout: default
title: Sync Settings
nav_order: 4
parent: Controller
grand_parent: Actions
---
# Sync Settings
  
Release: >0.906
{: .label .label-blue }  

  
### Description
This function sends a command to the controller to return each of its settings.  Upon receiving the setting, WebControl compares the setting's value and if different than what WebControl has in its settings, WebControl sends a setting update to the controller.

### Process

The process for syncing settings  (based upon current stock firmware as of 11/27/19) is as follows:

* A special gcode command ($$) is sent to the controller
* Controller reports each firmware setting's key and value in the $x=y format, where 'x' is the firmware setting's key and 'y' is the value.
* WebControl compares the received setting value with the one in its memory.
* If the two settings are not equal or not really, really close to each other, WebControl sends the setting value to the controller in the $x=y format.
 
### Notes

"Really, really close" is roughly defined as a difference so small that it would have no impact on the performance of the controller if the old setting was used.  For example, if distance between motors in the firmware is 3000.0000 mm and in WebControl its 3000.0001 mm, the setting will not be updated because its "really, really close"

The routine to determine if the values are really, really close needs some work when dealing with really, really small numbers.  It's possible (or likely) that you might see a setting update for something like "Chain Elasticity" everytime the controller and WebControl syncs.  Don't Panic.  It's fine.


