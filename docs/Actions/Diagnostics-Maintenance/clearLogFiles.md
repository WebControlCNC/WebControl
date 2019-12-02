---
layout: default
title: Clear Log Files
nav_order: 3
parent: Diagnostics / Maintenance
grand_parent: Actions
WCVersion: 0.917
---
# Clear Log Files

Release: >0.917
{: .label .label-blue }

### Description

This function will delete the existing log.txt and alog.txt files.  New ones will be created (rather instantaneously).

### Process

WebControl will attempt to delete each log file up to 1,000 times.  The need for multiple attempts is that at any given point, WebControl might be writing to the log and if so, the file can't be deleted.  So by attempting mulitple times, eventually the file will be closed and can get deleted.

### Troubleshooting

|Result   	|Possible Cause/Solution   	|
|---	|---	|
|xxxx   	|xxxx.   	|
|xxxx   	|xxxx.   	|


