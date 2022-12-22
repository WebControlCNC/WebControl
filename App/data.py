import sys

from DataStructures.data import Data


def init_data(app):
    """
    Initialize the Flask app's data member
    """
    app.data = Data()
    app.data.config.computeSettings(None, None, None, True)
    app.data.config.parseFirmwareVersions()
    app.data.units = app.data.config.getValue("Computed Settings", "units")
    app.data.tolerance = app.data.config.getValue("Computed Settings", "tolerance")
    app.data.distToMove = app.data.config.getValue("Computed Settings", "distToMove")
    app.data.distToMoveZ = app.data.config.getValue("Computed Settings", "distToMoveZ")
    app.data.unitsZ = app.data.config.getValue("Computed Settings", "unitsZ")
    app.data.comport = app.data.config.getValue("Maslow Settings", "COMport")
    app.data.gcodeShift = [
        float(app.data.config.getValue("Advanced Settings", "homeX")),
        float(app.data.config.getValue("Advanced Settings", "homeY")),
    ]

    version = sys.version_info

    if version[:2] > (3, 5):
        app.data.pythonVersion35 = False
        print("Using routines for Python > 3.5")
    else:
        app.data.pythonVersion35 = True
        print("Using routines for Python == 3.5")

    app.data.firstRun = False
    # app.previousPosX = 0.0
    # app.previousPosY = 0.0

    return app
