---
layout: default
title: Backup WebControl
nav_order: 4
parent: Diagnostics / Maintenance
grand_parent: Actions
WCVersion: 0.917
---
# Backup WebControl

Release: >0.917
{: .label .label-blue }

### Description

This function allows you to download a backup copy of your .WebControl directory.

### Process

Pressing the 'Backup WebControl' will instruct WebControl to create a zip file of the .WebControl directory containing all information specific to your installation of WebControl.  This includes the following:

* Uploaded GCode files
* Board Management Files
* webcontrol.json
* log.txt
* alog.txt
* Imported files (like groundcontrol.ini)
* Downloaded upgrade files (see note below)

The file will be named 'wc_backup_XXXXX-YYYYY.zip' where XXXXXX is the data in YYMMDD format and YYYYYY is the time in HHMMSS format.

After creating the zip file, WebControl will send the file to the browser for the user to download.

**Note:** The backup file will also contain a copy of all the release versions to which you have upgraded.  The release files are rather large (~70 MB) so the backup file will grow to be pretty large.  A near-future release will delete the old files after an upgrade is complete so this won't become an issue. 

### Troubleshooting

|Result   	|Possible Cause/Solution   	|
|---	|---	|
|xxxx   	|xxxx.   	|
|xxxx   	|xxxx.   	|


