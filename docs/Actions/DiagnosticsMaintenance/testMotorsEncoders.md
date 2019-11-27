---
layout: default
title: Test Motors/Encoders
nav_order: 1
parent: Diagnostics/Maintenance
grand_parent: Actions
---
# Test Motors/Encoders

### Description
This function sends a test command to the controller to exercise the motors and read values from the encoders.

### Process
Each axis is tested individually.  For a stock machine (two motors and z-axis) the test sequence is:

* Left Motor
* Right Motor
* Z-Axis

For each motor, the following actions are taken (based upon current stock firmware as of 11/27/19):

##### Forward Motion Test:
* Encoder position is read and stored.
* Motor is run "forward" at full power for one second
* Encoder position is read and stored.
* If the difference between the ending encoder position value and beginning encoder position value is **greater than** 500 steps, then indicate a PASS, otherwise indicate a FAIL.

##### Reverse Motion Test:
* Encoder position is read and stored.
* Motor is run "reverse" at full power for one second
* Encoder position is read and stored.
* If the difference between the ending encoder position value and beginning encoder position value is **less than** than 500 steps, then indicate a PASS, otherwise indicate a FAIL.
 
### Interpretation

|Result   	|Possible Cause/Solution   	|
|---	|---	|
|All Motors Fail All Tests   	|Power cord is inserted into the Arduino controller instead of the motor controller shield.  Check installation.   	|
|One or More Motors Fails Both Directions   	|Motor cable not inserted properly into either the motor controller shield or the motor.  Unplug and replug the cable ends.   	|
|One or More Motors Fail One Direction   	|Possible hardware issue with motor or encoder   	|


Release: >0.906
{: .label .label-blue }
