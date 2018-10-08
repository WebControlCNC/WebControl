'''

This file provides a single dict which contains all of the details about the
various settings.  It also has a number of helper functions for interacting
and using the data in this dict.

'''
import json
from __main__ import app

with open('webcontrol.json', 'r') as infile:
    settings = json.load(infile)

def getJSONSettings():
    return settings

def updateSettings(section, result):

    for x in range(len(app.data.config.settings[section])):
        found = False
        for setting in result:
            if app.data.config.settings[section][x]["key"]==setting:
                if (app.data.config.settings[section][x]["type"]=="float"):
                    try:
                        app.data.config.settings[section][x]["value"]=float(result[setting])
                    except:
                        pass
                elif (app.data.config.settings[section][x]["type"]=="int"):
                    try:
                        app.data.config.settings[section][x]["value"]=int(result[setting])
                    except:
                        pass
                elif (app.data.config.settings[section][x]["type"]=="bool"):
                    try:
                        if (result[setting]=="on"):
                            app.data.config.settings[section][x]["value"]=1
                        else:
                            app.data.config.settings[section][x]["value"]=0
                    except:
                        pass
                else:
                    app.data.config.settings[section][x]["value"]=result[setting]
                #print setting+":"+str(result[setting])+"->"+str(settings[section][x]["value"])
                found = True
                break
        if found==False:
            #must be a turned off checkbox.. what a pain to figure out
            if (app.data.config.settings[section][x]["type"]=="bool"):
                app.data.config.settings[section][x]["value"]=0
        with open('webcontrol.json', 'w') as outfile:
            json.dump(app.data.config.settings,outfile, sort_keys=True, indent=4, ensure_ascii=False)

def getJSONSettingSection(section):
    '''
    This generates a JSON string which is used to construct the settings page
    '''
    options = []
    if section in app.data.config.settings:
        options = app.data.config.settings[section]
    for option in options:
        option['section'] = section
        if 'desc' in option and 'default' in option:
            if not "default setting:" in option['desc']:                            #check to see if the default text has already been added
                option['desc'] += "\ndefault setting: " + str(option['default'])
    return options

def getDefaultValueSection(section):
    '''
    Returns a dict with the settings keys as the key and the default value
    of that setting as the value for the section specified
    '''
    ret = {}
    if section in app.data.config.settings:
        for option in app.data.config.settings[section]:
            if 'default' in option:
                ret[option['key']] = option['default']
                break
    return ret

def getDefaultValue(section, key):
    '''
    Returns the default value of a setting
    '''
    ret = None
    if section in app.data.config.settings:
        for option in app.data.config.settings[section]:
            if option['key'] == key and 'default' in option:
                ret = option['default']
                break
    return ret

def getFirmwareKey(section, key):

    ret = None
    if section in app.data.config.settings:
        for option in app.data.config.settings[section]:
            if option['key'] == key and 'firmwareKey' in option:
                ret = option['firmwareKey']
                break
    return ret

def getSettingValue(section, key):
    '''
    Returns the actual value of a setting
    '''
    ret = None
    if section in app.data.config.settings:
        for option in app.data.config.settings[section]:
            if option['key'] == key :
                ret = option['value']
                break
    return ret


'''
# TODO:
def syncFirmwareKey(firmwareKey, value, data):
    for section in settings:
        for option in settings[section]:
            if 'firmwareKey' in option and option['firmwareKey'] == firmwareKey:
                storedValue = app.data.config.get(section, option['key'])
                if (option['key'] == "spindleAutomate"):
                    if (storedValue == "Servo"):
                        storedValue = 1
                    elif (storedValue == "Relay_High"):
                        storedValue = 2
                    elif (storedValue == "Relay_Low"):
                        storedValue = 3
                    else:
                        storedValue = 0
                if ( (firmwareKey == 45) ):
                    print "firmwareKey = 45"
                    if (storedValue != ""):
                        sendErrorArray(firmwareKey, storedValue, data)
                elif not isClose(float(storedValue), value):
                    print "firmwareKey(send) = "+str(firmwareKey)
                    app.data.gcode_queue.put("$" + str(firmwareKey) + "=" + str(storedValue))
                else:
                    break
    return
'''
def isClose(a, b, rel_tol=1e-06):
    '''
    Takes two values and returns true if values are close enough in value
    such that the difference between them is less than the significant
    figure specified by rel_tol.  Useful for comparing float values on
    arduino adapted from https://stackoverflow.com/a/33024979
    '''
    return abs(a-b) <= rel_tol * max(abs(a), abs(b))

def parseErrorArray(value, asFloat):

    #not the best programming, but I think it'll work
    xErrors = [[0 for x in range(15)] for y in range(31)]
    yErrors = [[0 for x in range(15)] for y in range(32)]

    index = 0
    xCounter = 0
    yCounter = 0
    val = ""
    while (index < len(value) ):
        while ( (index < len(value) ) and ( value[index] != ',') ):
            val += value[index]
            index += 1
        index += 1
        xErrors[xCounter][yCounter] = int(val)
        #print str(xCounter)+", "+str(yCounter)+", "+str(xErrors[xCounter][yCounter])
        val=""
        xCounter += 1
        if (xCounter == 31):
            xCounter = 0
            yCounter += 1
        if (yCounter == 15):
            xCounter = 0
            yCounter = 0
            while (index < len(value) ):
                while ( (index < len(value) ) and ( value[index] != ',') ):
                    val += value[index]
                    index += 1
                index += 1
                #print str(xCounter)+", "+str(yCounter)+": "+val+"->"+str(len(val))
                yErrors[xCounter][yCounter] = int(val)
                val=""
                xCounter += 1
                if (xCounter == 31):
                    xCounter = 0
                    yCounter += 1
                if (yCounter == 15):
                    break;

    if (asFloat==False):
        return xErrors, yErrors
    else:
        xFloatErrors = [[0.0 for x in range(15)] for y in range(31)]
        yFloatErrors = [[0.0 for x in range(15)] for y in range(32)]
        for x in range(31):
            for y in range(15):
                xFloatErrors[x][y] = float(xErrors[x][y])/1000.0
                yFloatErrors[x][y] = float(yErrors[x][y])/1000.0
        return xFloatErrors, yFloatErrors
'''
#TODO
def sendErrorArray(firmwareKey, value, data):
    # parse out the array from string and then send them using the $O command
    xErrors, yErrors = parseErrorArray(value,False)
    # now send the array:
    for x in range(0, 31):#31
        for y in range (0, 15):#15
            app.data.gcode_queue.put("$O=" + str(x)+","+str(y)+","+str(xErrors[x][y])+","+str(yErrors[x][y])+" ")
    # if you send a 31,15 , it will trigger a save to EEPROM
    app.data.gcode_queue.put("$O=" + str(31)+","+str(15)+","+str(42)+","+str(42)+" ")
'''
