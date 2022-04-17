"""

This file provides a single dict which contains all of the details about the
various settings.  It also has a number of helper functions for interacting
and using the data in this dict.

"""
import json

"""

This is the settings dict.  Its structure is:

{
    // The top level keys are the section names, their values is a list of dicts
    // representing the settings contained in that section.
    Section : [
        {
            "type": "string",
            "title": "Some Setting",
            "desc": "A description of the setting",
            "key": "keyName", //this has to be a valid keyname
            "default": "default value",
            "firmwareKey": 12   // if this is a setting in the firmware, this
                                // is the integer value of that setting
        },
        {...}
    ]
}

"""


settings = {
    "Maslow Settings": [
        {
            "type": "string",
            "title": "Serial Connection",
            "desc": "Select the COM port to connect to machine",
            "key": "COMport",
            "default": "",
        },
        {
            "type": "string",
            "title": "Distance Between Motors",
            "desc": "The horizontal distance between the center of the motor shafts in MM.",
            "key": "motorSpacingX",
            "default": 2978.4,
            "firmwareKey": 2,
        },
        {
            "type": "string",
            "title": "Work Area Width in MM",
            "desc": "The width of the machine working area (normally 8 feet).",
            "key": "bedWidth",
            "default": 2438.4,
            "firmwareKey": 0,
        },
        {
            "type": "string",
            "title": "Work Area Height in MM",
            "desc": "The Height of the machine working area (normally 4 feet).",
            "key": "bedHeight",
            "default": 1219.2,
            "firmwareKey": 1,
        },
        {
            "type": "string",
            "title": "Motor Offset Height in MM",
            "desc": "The vertical distance from the edge of the work area to the level of the motors.",
            "key": "motorOffsetY",
            "default": 463,
            "firmwareKey": 3,
        },
        {
            "type": "string",
            "title": "Distance Between Sled Mounting Points",
            "desc": "The horizontal distance between the points where the chains mount to the sled.",
            "key": "sledWidth",
            "default": 310,
            "firmwareKey": 4,
        },
        {
            "type": "string",
            "title": "Vertical Distance Sled Mounts to Cutter",
            "desc": "The vertical distance between where the chains mount on the sled to the cutting tool.",
            "key": "sledHeight",
            "default": 139,
            "firmwareKey": 5,
        },
        {
            "type": "string",
            "title": "Center Of Gravity",
            "desc": "How far below the cutting bit is the center of gravity. This can be found by resting the sled on a round object and observing where it balances.",
            "key": "sledCG",
            "default": 79,
            "firmwareKey": 6,
        },
        {
            "type": "bool",
            "title": "Z-axis installed",
            "desc": "Does the machine have an automatic z-axis?",
            "key": "zAxis",
            "default": 0,
            "firmwareKey": 16,
        },
        {
            "type": "string",
            "title": "Z-Axis Pitch",
            "desc": "The number of mm moved per rotation of the z-axis",
            "key": "zDistPerRot",
            "default": 3.17,
            "firmwareKey": 19,
        },
        {
            "type": "bool",
            "title": "Wii Pendant Installed",
            "desc": "Wii controller connected via Bluetooth",
            "key": "wiiPendantPresent",
            "default": 0,
        },
        {
            "type": "bool",
            "title": "Raspberry Pi Button Service Active",
            "desc": "GPIO buttons run in separate process / system service",
            "key": "MaslowButtonService",
            "default": 0,
        },
        {
            "type": "bool",
            "title": "RPI Text display",
            "desc": "Attached command line text display on Maslow",
            "key": "clidisplay",
            "default": 0,
        },
        {
            "type": "options",
            "title": "Color Scheme",
            "desc": "Switch between the light and dark color schemes. Restarting GC is needed for this change to take effect",
            "options": ["Light", "Dark", "DarkGreyBlue"],
            "key": "colorScheme",
            "default": "Light",
        },
        {
            "type": "string",
            "title": "Open File",
            "desc": "The path to the open file\\ndefault setting: your home directory",
            "key": "openFile",
            "default": "",
        },
        {
            "type": "string",
            "title": "Macro 1",
            "desc": "User defined gcode bound to the Macro 1 button",
            "key": "macro1",
            "default": "",
        },
        {
            "type": "string",
            "title": "Macro 1 Title",
            "desc": "User defined title for the Macro 1 button",
            "key": "macro1_title",
            "default": "Macro1",
        },
        {
            "type": "string",
            "title": "Macro 2",
            "desc": "User defined gcode bound to the Macro 2 button",
            "key": "macro2",
            "default": "",
        },
        {
            "type": "string",
            "title": "Macro 2 Title",
            "desc": "User defined title for the Macro 2 button",
            "key": "macro2_title",
            "default": "Macro2",
        },
        {
            "type": "string",
            "title": "Macro 2",
            "desc": "User defined gcode bound to the Macro 2 button",
            "key": "macro2",
            "default": "",
        },
        {
            "type": "string",
            "title": "Macro 3 Title",
            "desc": "User defined title for the Macro 3 button",
            "key": "macro3_title",
            "default": "Macro3",
        },
        {
            "type": "string",
            "title": "Macro 4",
            "desc": "User defined gcode bound to the Macro 4 button",
            "key": "macro4",
            "default": "",
        },
        {
            "type": "string",
            "title": "Macro 4 Title",
            "desc": "User defined title for the Macro 4 button",
            "key": "macro4_title",
            "default": "Macro4",
        },
        {
            "type": "string",
            "title": "Macro 5",
            "desc": "User defined gcode bound to the Macro 5 button",
            "key": "macro5",
            "default": "",
        },
        {
            "type": "string",
            "title": "Macro 5 Title",
            "desc": "User defined title for the Macro 5 button",
            "key": "macro5_title",
            "default": "Macro5",
        },
        {
            "type": "string",
            "title": "Z-Axis Safe Travel Height in MM",
            "desc": "The vertical distance above the work area to raise the z-axis for safe travel. Used by 'Home', 'Return to Center' and 'z-Axis' settings.",
            "key": "zAxisSafeHeight",
            "default": 5,
        },
        {
            "type": "bool",
            "title": "Buffer Gcode",
            "desc": "Buffer gcode on arduino to increase execution speed. Requres restart to take effect. Experimental.",
            "key": "bufferOn",
            "default": 0,
        },
    ],
    "Advanced Settings": [
        {
            "type": "string",
            "title": "Max touch Z-axis plunge",
            "desc": "Max depth the z axis should plunge in order to find the touch probe",
            "key": "maxTouchProbePlungeDistance",
            "default": 0.0,
        },
        {
            "type": "string",
            "title": "Encoder Steps per Revolution",
            "desc": "The number of encoder steps per revolution of the left or right motor",
            "key": "encoderSteps",
            "default": 8113.73,
            "firmwareKey": 12,
        },
        {
            "type": "string",
            "title": "Gear Teeth",
            "desc": "The number of teeth on the gear of the left or right motor",
            "key": "gearTeeth",
            "default": 10,
        },
        {
            "type": "string",
            "title": "Chain Pitch",
            "desc": "The distance between chain roller centers",
            "key": "chainPitch",
            "default": 6.35,
        },
        {
            "type": "string",
            "title": "Chain Tolerance, Left Chain",
            "desc": "The tolerance adjustment for the left chain length, in percent",
            "key": "leftChainTolerance",
            "default": 0,
        },
        {
            "type": "string",
            "title": "Chain Tolerance, Right Chain",
            "desc": "The tolerance adjustment for the right chain length, in percent",
            "key": "rightChainTolerance",
            "default": 0,
        },
        {
            "type": "options",
            "title": "Top/Bottom Chain Feed",
            "desc": "On which side of the motor sprockets do the chains leave from to connect to the sled",
            "options": ["Top", "Bottom"],
            "default": "Top",
            "key": "chainOverSprocket",
        },
        {
            "type": "string",
            "title": "Extend Chain Distance",
            "desc": "The length in mm that will be extended during chain calibration",
            "key": "chainExtendLength",
            "default": 1650,
            "firmwareKey": 11,
        },
        {
            "type": "string",
            "title": "Chain Length",
            "desc": "The length in mm of your chains, used to define the kinematics search space",
            "key": "chainLength",
            "default": 3360,
            "firmwareKey": 10,
        },
        {
            "type": "string",
            "title": "Z-Axis Encoder Steps per Revolution",
            "desc": "The number of encoder steps per revolution of the z-axis",
            "key": "zEncoderSteps",
            "default": 7560.0,
            "firmwareKey": 20,
        },
        {
            "type": "options",
            "title": "Spindle Automation",
            "desc": "How should the spindle start and stop automatically based on gcode? Leave off for none, or set external servo control, or external relay control, active high or low.",
            "key": "spindleAutomate",
            "options": ["None", "Servo", "Relay_High", "Relay_Low"],
            "default": "None",
            "firmwareKey": 17,
        },
        {
            "type": "string",
            "title": "Max Feedrate",
            "desc": "The maximum feedrate in mm/min that machine is capable of sustaining.  Setting this value too high will cause movements to start before the prior movement finishes.",
            "key": "maxFeedrate",
            "default": 800,
            "firmwareKey": 15,
        },
        {
            "type": "string",
            "title": "Home Position X Coordinate",
            "desc": "The X coordinate of the home position",
            "key": "homeX",
            "default": 0.0,
        },
        {
            "type": "string",
            "title": "Home Position Y Coordinate",
            "desc": "The X coordinate of the home position",
            "key": "homeY",
            "default": 0.0,
        },
        {
            "type": "bool",
            "title": "Truncate Floating Point Numbers",
            "desc": "Truncate floating point numbers at the specified number of decimal places",
            "key": "truncate",
            "default": 0,
        },
        {
            "type": "string",
            "title": "Floating Point Precision",
            "desc": "If truncate floating point numbers is enabled, the number of digits after the decimal place to preserve",
            "key": "digits",
            "default": 4,
        },
        {
            "type": "options",
            "title": "Kinematics Type",
            "desc": "Switch between trapezoidal and triangular kinematics",
            "options": ["Quadrilateral", "Triangular"],
            "key": "kinematicsType",
            "default": "Quadrilateral",
        },
        {
            "type": "string",
            "title": "Rotation Radius for Triangular Kinematics",
            "desc": "The distance between where the chains attach and the center of the router bit in mm",
            "key": "rotationRadius",
            "default": 100,
            "firmwareKey": 8,
        },
        {
            "type": "string",
            "title": "Chain Sag Correction Value for Triangular Kinematics",
            "desc": "The scaled value computed by the calibration process to calculate chain sag based on sled weight, chain weight, and workspace angle",
            "key": "chainSagCorrection",
            "default": 0,
            "firmwareKey": 37,
        },
        {
            "type": "bool",
            "title": "Use Calibration Error Matrix (Experimental)",
            "desc": "Enable modifying x,y coordinates during calculations to account for errors determined by optical calibration",
            "key": "enableOpticalCalibration",
            "default": 0,
            "firmwareKey": 44,
        },
        {
            "type": "bool",
            "title": "Use Interpolation (True) or Curve Fit (False) (Experimental)",
            "desc": "Selects use interpolation of calibration error matrix or curve fit",
            "key": "useInterpolationOrCurve",
            "default": 0,
            "firmwareKey": 46,
        },
        {
            "type": "string",
            "title": "Top Beam Tilt (Experimental)",
            "desc": "Experimental adjustment for top beam tilt in degrees",
            "key": "topBeamTilt",
            "default": 0,
            "firmwareKey": 43,
        },
        {
            "type": "bool",
            "title": "Enable Custom Positional PID Values",
            "desc": "Enable using custom values for the positional PID controller. Turning this off will return to the default values",
            "key": "enablePosPIDValues",
            "default": 0,
        },
        {
            "type": "string",
            "title": "Kp Position",
            "desc": "The proportional constant for the position PID controller",
            "key": "KpPos",
            "default": 1300,
        },
        {
            "type": "string",
            "title": "Ki Position",
            "desc": "The integral constant for the position PID controller",
            "key": "KiPos",
            "default": 0,
        },
        {
            "type": "string",
            "title": "Kd Position",
            "desc": "The derivative constant for the position PID controller",
            "key": "KdPos",
            "default": 34,
        },
        {
            "type": "string",
            "title": "Kp Position Z-Axis",
            "desc": "The proportional constant for the position Z-Axis PID controller",
            "key": "KpPosZ",
            "default": 1300,
        },
        {
            "type": "string",
            "title": "Ki Position Z-Axis",
            "desc": "The integral constant for the position Z-Axis PID controller",
            "key": "KiPosZ",
            "default": 0,
        },
        {
            "type": "string",
            "title": "Kd Position Z-Axis",
            "desc": "The derivative constant for the position Z-Axis PID controller",
            "key": "KdPosZ",
            "default": 34,
        },
        {
            "type": "string",
            "title": "Proportional Weighting",
            "desc": "The ratio of Proportional on Error (1) to Proportional on Measure (0)",
            "key": "propWeight",
            "default": 1,
        },
        {
            "type": "bool",
            "title": "Enable Custom Velocity PID Values",
            "desc": "Enable using custom values for the Velocity PID controller. Turning this off will return to the default values",
            "key": "enableVPIDValues",
            "default": 0,
        },
        {
            "type": "string",
            "title": "Kp Velocity",
            "desc": "The proportional constant for the velocity PID controller",
            "key": "KpV",
            "default": 5,
        },
        {
            "type": "string",
            "title": "Ki Velocity",
            "desc": "The integral constant for the velocity PID controller",
            "key": "KiV",
            "default": 0,
        },
        {
            "type": "string",
            "title": "Kd Velocity",
            "desc": "The derivative constant for the velocity PID controller",
            "key": "KdV",
            "default": 0.28,
        },
        {
            "type": "string",
            "title": "Kp Velocity Z-Axis",
            "desc": "The proportional constant for the Z-axis velocity PID controller",
            "key": "KpVZ",
            "default": 5,
        },
        {
            "type": "string",
            "title": "Ki Velocity Z-Axis",
            "desc": "The integral constant for the Z-axis velocity PID controller",
            "key": "KiVZ",
            "default": 0,
        },
        {
            "type": "string",
            "title": "Kd Velocity Z-Axis",
            "desc": "The derivative constant for the Z-axis velocity PID controller",
            "key": "KdVZ",
            "default": 0.28,
        },
        {
            "type": "string",
            "title": "Proportional Weighting for Z-Axis",
            "desc": "The ratio of Proportional on Error (1) to Proportional on Measure (0)",
            "key": "propWeightZ",
            "default": 1,
        },
        {
            "type": "options",
            "title": "PWM frequency for motor control",
            "desc": "The PWM frequence used for motor speed control",
            "options": ["490Hz", "4,100Hz", "31,000Hz"],
            "default": "490Hz",
            "key": "fPWM",
        },
        {
            "type": "string",
            "title": "Position Error Limit",
            "desc": "If the position of the sled varies from the expected position by more than this amount, cutting wil be stopped. Program must be restarted to take effect.",
            "key": "positionErrorLimit",
            "default": 2.0,
            "firmwareKey": 42,
        },
    ],
    "Ground Control Settings": [
        {
            "type": "bool",
            "title": "Center Canvas on Window Resize",
            "desc": "When resizing the window, automatically reset the Gcode canvas to be centered and zoomed out. Program must be restarted to take effect.",
            "key": "centerCanvasOnResize",
            "default": 0,
        },
        {
            "type": "string",
            "title": "Zoom In",
            "desc": "Pressing this key will zoom in. Note combinations of keys like 'shift' + '=' may not work as expected. Program must be restarted to take effect.",
            "key": "zoomIn",
            "default": "pageup",
        },
        {
            "type": "string",
            "title": "Zoom Out",
            "desc": "Pressing this key will zoom in. Note combinations of keys like 'shift' + '=' may not work as expected. Program must be restarted to take effect.",
            "key": "zoomOut",
            "default": "pagedown",
        },
        {
            "type": "string",
            "title": "Valid File Extensions",
            "desc": "Valid file extensions for Ground Control to open. Comma separated list.",
            "key": "validExtensions",
            "default": ".nc, .ngc, .text, .gcode",
        },
        {
            "type": "string",
            "title": "Reset View Scale",
            "desc": "Zoom scale for 'Reset View' command.",
            "key": "viewScale",
            "default": ".45",
        },
    ],
    "Computed Settings": [  # These are setting calculated from the user inputs on other settings, they are not directly seen by the user
        {"type": "string", "key": "kinematicsTypeComputed", "firmwareKey": 7},
        {"type": "string", "key": "distPerRot", "firmwareKey": 13},
        {"type": "string", "key": "KpPosMain", "firmwareKey": 21},
        {"type": "string", "key": "KiPosMain", "firmwareKey": 22},
        {"type": "string", "key": "KdPosMain", "firmwareKey": 23},
        {"type": "string", "key": "propWeightMain", "firmwareKey": 24},
        {"type": "string", "key": "KpPosZ", "firmwareKey": 29},
        {"type": "string", "key": "KiPosZ", "firmwareKey": 30},
        {"type": "string", "key": "KdPosZ", "firmwareKey": 31},
        {"type": "string", "key": "propWeightZ", "firmwareKey": 32},
        {"type": "string", "key": "KpVMain", "firmwareKey": 25},
        {"type": "string", "key": "KiVMain", "firmwareKey": 26},
        {"type": "string", "key": "KdVMain", "firmwareKey": 27},
        {"type": "string", "key": "KpVZ", "firmwareKey": 33},
        {"type": "string", "key": "KiVZ", "firmwareKey": 34},
        {"type": "string", "key": "KdVZ", "firmwareKey": 35},
        {"type": "string", "key": "chainOverSprocketComputed", "firmwareKey": 38},
        {"type": "string", "key": "fPWMComputed", "firmwareKey": 39},
        {"type": "string", "key": "distPerRotLeftChainTolerance", "firmwareKey": 40},
        {"type": "string", "key": "distPerRotRightChainTolerance", "firmwareKey": 41},
    ],
    "Optical Calibration Settings": [
        {
            "type": "string",
            "key": "xyErrorArray",
            "default": "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0",
            "firmwareKey": 45,
        },
        {"type": "string", "key": "calX0", "firmwareKey": 47, "default": "0"},
        {"type": "string", "key": "calX1", "firmwareKey": 48, "default": "0"},
        {"type": "string", "key": "calX2", "firmwareKey": 49, "default": "0"},
        {"type": "string", "key": "calX3", "firmwareKey": 50, "default": "0"},
        {"type": "string", "key": "calX4", "firmwareKey": 51, "default": "0"},
        {"type": "string", "key": "calX5", "firmwareKey": 52, "default": "0"},
        {"type": "string", "key": "calY0", "firmwareKey": 53, "default": "0"},
        {"type": "string", "key": "calY1", "firmwareKey": 54, "default": "0"},
        {"type": "string", "key": "calY2", "firmwareKey": 55, "default": "0"},
        {"type": "string", "key": "calY3", "firmwareKey": 56, "default": "0"},
        {"type": "string", "key": "calY4", "firmwareKey": 57, "default": "0"},
        {"type": "string", "key": "calY5", "firmwareKey": 58, "default": "0"},
        {"type": "string", "key": "opticalCenterX", "default": "0"},
        {"type": "string", "key": "opticalCenterY", "default": "0"},
        {"type": "string", "key": "scaleX", "default": "1.0"},
        {"type": "string", "key": "scaleY", "default": "1.0"},
        {"type": "int", "key": "gaussianBlurValue", "default": 5},
        {"type": "float", "key": "cannyLowValue", "default": 50.0},
        {"type": "float", "key": "cannyHighValue", "default": 100.0},
        {"type": "int", "key": "autoScanDirection", "default": 0},
        {"type": "float", "key": "markerX", "default": 12.7},
        {"type": "float", "key": "markerY", "default": 12.7},
    ],
}


def getJSONSettingSection(section):
    """
    This generates a JSON string which is used to construct the settings page
    """
    options = []
    if section in settings:
        options = settings[section]
    for option in options:
        option["section"] = section
        if "desc" in option and "default" in option:
            if (
                not "default setting:" in option["desc"]
            ):  # check to see if the default text has already been added
                option["desc"] += "\ndefault setting: " + str(option["default"])
    return json.dumps(options)


def getDefaultValueSection(section):
    """
    Returns a dict with the settings keys as the key and the default value
    of that setting as the value for the section specified
    """
    ret = {}
    if section in settings:
        for option in settings[section]:
            if "default" in option:
                ret[option["key"]] = option["default"]
    return ret


def getDefaultValue(section, key):
    """
    Returns the default value of a setting
    """
    ret = None
    if section in settings:
        for option in settings[section]:
            if option["key"] == key and "default" in option:
                ret = option["default"]
    return ret


def getFirmwareKey(section, key):
    ret = None
    if section in settings:
        for option in settings[section]:
            if option["key"] == key and "firmwareKey" in option:
                ret = option["firmwareKey"]
    return ret


"""
# TODO:
def syncFirmwareKey(firmwareKey, value, data):
    for section in settings:
        for option in settings[section]:
            if 'firmwareKey' in option and option['firmwareKey'] == firmwareKey:
                storedValue = data.config.get(section, option['key'])
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
                    data.gcode_queue.put("$" + str(firmwareKey) + "=" + str(storedValue))
                else:
                    break
    return
"""


def isClose(a, b, rel_tol=1e-06):
    """
    Takes two values and returns true if values are close enough in value
    such that the difference between them is less than the significant
    figure specified by rel_tol.  Useful for comparing float values on
    arduino adapted from https://stackoverflow.com/a/33024979
    """
    return abs(a - b) <= rel_tol * max(abs(a), abs(b))


def parseErrorArray(value, asFloat):

    # not the best programming, but I think it'll work
    xErrors = [[0 for x in range(15)] for y in range(31)]
    yErrors = [[0 for x in range(15)] for y in range(32)]

    index = 0
    xCounter = 0
    yCounter = 0
    val = ""
    while index < len(value):
        while (index < len(value)) and (value[index] != ","):
            val += value[index]
            index += 1
        index += 1
        xErrors[xCounter][yCounter] = int(val)
        # print str(xCounter)+", "+str(yCounter)+", "+str(xErrors[xCounter][yCounter])
        val = ""
        xCounter += 1
        if xCounter == 31:
            xCounter = 0
            yCounter += 1
        if yCounter == 15:
            xCounter = 0
            yCounter = 0
            while index < len(value):
                while (index < len(value)) and (value[index] != ","):
                    val += value[index]
                    index += 1
                index += 1
                # print str(xCounter)+", "+str(yCounter)+": "+val+"->"+str(len(val))
                yErrors[xCounter][yCounter] = int(val)
                val = ""
                xCounter += 1
                if xCounter == 31:
                    xCounter = 0
                    yCounter += 1
                if yCounter == 15:
                    break

    if asFloat == False:
        return xErrors, yErrors
    else:
        xFloatErrors = [[0.0 for x in range(15)] for y in range(31)]
        yFloatErrors = [[0.0 for x in range(15)] for y in range(32)]
        for x in range(31):
            for y in range(15):
                xFloatErrors[x][y] = float(xErrors[x][y]) / 1000.0
                yFloatErrors[x][y] = float(yErrors[x][y]) / 1000.0
        return xFloatErrors, yFloatErrors


"""
#TODO
def sendErrorArray(firmwareKey, value, data):
    # parse out the array from string and then send them using the $O command
    xErrors, yErrors = parseErrorArray(value,False)
    # now send the array:
    for x in range(0, 31):#31
        for y in range (0, 15):#15
            data.gcode_queue.put("$O=" + str(x)+","+str(y)+","+str(xErrors[x][y])+","+str(yErrors[x][y])+" ")
    # if you send a 31,15 , it will trigger a save to EEPROM
    data.gcode_queue.put("$O=" + str(31)+","+str(15)+","+str(42)+","+str(42)+" ")
"""
