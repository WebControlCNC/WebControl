---
layout: default
title: Restore WebControl
nav_order: 5
parent: Diagnostics / Maintenance
grand_parent: Actions
WCVersion: 0.917
---
# Backup WebControl

Release: >0.917
{: .label .label-blue }

### Description

This function allows you to upload a webcontrol backup file to restore an installation of WebControl.  The backup webcontrol file must have been made by the 'Backup WebControl' process.

### Process

Pressing the 'Restore WebControl' will request the user to upload a webcontrol backup file.  WebControl will extract the contents of this file to the .WebControl directory.

The extraction process overwrites existing files, but will not delete files that are present in the .WebControl directory but not present in the backup file.  

Files that will be restored include

* Uploaded GCode files
* Board Management Files
* webcontrol.json
* log.txt
* alog.txt
* Imported files (like groundcontrol.ini)
* Downloaded upgrade files (see note below)

After the files have been extracted, WebControl will reload the webcontrol.json file and synchronize those settings with the attached controller.

**Note:** The backup files contain a copy of all the release versions to which you have upgraded.  The release files are rather large (~70 MB) so the backup file will grow to be pretty large.  A near-future release will delete the old files after an upgrade is complete. 

### Troubleshooting

|Result   	|Possible Cause/Solution   	|
|---	|---	|
|xxxx   	|xxxx.   	|
|xxxx   	|xxxx.   	|




