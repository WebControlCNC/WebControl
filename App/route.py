from werkzeug.utils import secure_filename

from flask import (
    jsonify,
    render_template,
    request,
    send_file,
    send_from_directory,
)
from flask_mobility.decorators import mobile_template


def init_route(app):
    route_type = "route"
    app.data.console_queue.put(f"{__name__}: Initializing {route_type} handling for the app")

    @app.route("/")
    @mobile_template("{mobile/}")
    def index(template):
        app.data.logger.resetIdler()
        macro1Title = (app.data.config.getValue("Maslow Settings", "macro1_title"))[:6]
        macro2Title = (app.data.config.getValue("Maslow Settings", "macro2_title"))[:6]
        if template == "mobile/":
            return render_template(
                "frontpage3d_mobile.html",
                modalStyle="modal-lg",
                macro1_title=macro1Title,
                macro2_title=macro2Title,
            )
        else:
            return render_template(
                "frontpage3d.html",
                modalStyle="mw-100 w-75",
                macro1_title=macro1Title,
                macro2_title=macro2Title,
            )


    @app.route("/controls")
    @mobile_template("/controls/{mobile/}")
    def controls(template):
        app.data.logger.resetIdler()
        macro1Title = (app.data.config.getValue("Maslow Settings", "macro1_title"))[:6]
        macro2Title = (app.data.config.getValue("Maslow Settings", "macro2_title"))[:6]
        if template == "/controls/mobile/":
            return render_template(
                "frontpage3d_mobilecontrols.html",
                modalStyle="modal-lg",
                isControls=True,
                macro1_title=macro1Title,
                macro2_title=macro2Title,
            )
        else:
            return render_template(
                "frontpage3d.html",
                modalStyle="mw-100 w-75",
                macro1_title=macro1Title,
                macro2_title=macro2Title,
            )


    @app.route("/text")
    @mobile_template("/text/{mobile/}")
    def text(template):
        app.data.logger.resetIdler()
        macro1Title = (app.data.config.getValue("Maslow Settings", "macro1_title"))[:6]
        macro2Title = (app.data.config.getValue("Maslow Settings", "macro2_title"))[:6]
        if template == "/text/mobile":
            return render_template(
                "frontpageText_mobile.html",
                modalStyle="modal-lg",
                isControls=True,
                macro1_title=macro1Title,
                macro2_title=macro2Title,
            )
        else:
            return render_template(
                "frontpageText.html",
                modalStyle="mw-100 w-75",
                macro1_title=macro1Title,
                macro2_title=macro2Title,
            )


    @app.route("/logs")
    @mobile_template("/logs/{mobile/}")
    def logs(template):
        app.data.console_queue.put(f"{__name__}: here")
        app.data.logger.resetIdler()
        if template == "/logs/mobile/":
            return render_template("logs.html")
        else:
            return render_template("logs.html")


    @app.route("/maslowSettings", methods=["POST"])
    def maslowSettings():
        app.data.logger.resetIdler()
        if request.method == "POST":
            result = request.form
            app.data.config.updateSettings("Maslow Settings", result)
            message = {"status": 200}
            resp = jsonify(message)
            resp.status_code = 200
            return resp


    @app.route("/advancedSettings", methods=["POST"])
    def advancedSettings():
        app.data.logger.resetIdler()
        if request.method == "POST":
            result = request.form
            app.data.config.updateSettings("Advanced Settings", result)
            message = {"status": 200}
            resp = jsonify(message)
            resp.status_code = 200
            return resp


    @app.route("/webControlSettings", methods=["POST"])
    def webControlSettings():
        app.data.logger.resetIdler()
        if request.method == "POST":
            result = request.form
            app.data.config.updateSettings("WebControl Settings", result)
            message = {"status": 200}
            resp = jsonify(message)
            resp.status_code = 200
            return resp


    @app.route("/cameraSettings", methods=["POST"])
    def cameraSettings():
        app.data.logger.resetIdler()
        if request.method == "POST":
            result = request.form
            app.data.config.updateSettings("Camera Settings", result)
            message = {"status": 200}
            resp = jsonify(message)
            resp.status_code = 200
            return resp


    @app.route("/gpioSettings", methods=["POST"])
    def gpioSettings():
        app.data.logger.resetIdler()
        if request.method == "POST":
            result = request.form
            app.data.config.updateSettings("GPIO Settings", result)
            message = {"status": 200}
            resp = jsonify(message)
            resp.status_code = 200
            return resp


    @app.route("/uploadGCode", methods=["POST"])
    def uploadGCode():
        app.data.logger.resetIdler()
        if request.method == "POST":
            result = request.form
            directory = result["selectedDirectory"]
            # app.data.console_queue.put(f"{__name__}: {directory}")
            f = request.files.getlist("file[]")
            app.data.console_queue.put(f"{__name__}: {f}")
            home = app.data.config.getHome()
            app.data.config.setValue(
                "Computed Settings", "lastSelectedDirectory", directory
            )

            if len(f) > 0:
                firstFile = f[0]
                for file in f:
                    app.data.gcodeFile.filename = (
                        home
                        + "/.WebControl/gcode/"
                        + directory
                        + "/"
                        + secure_filename(file.filename)
                    )
                    file.save(app.data.gcodeFile.filename)
                app.data.gcodeFile.filename = (
                    home
                    + "/.WebControl/gcode/"
                    + directory
                    + "/"
                    + secure_filename(firstFile.filename)
                )
                returnVal = app.data.gcodeFile.loadUpdateFile()
                if returnVal:
                    message = {"status": 200}
                    resp = jsonify(message)
                    resp.status_code = 200
                    return resp
                else:
                    message = {"status": 500}
                    resp = jsonify(message)
                    resp.status_code = 500
                    return resp
            else:
                message = {"status": 500}
                resp = jsonify(message)
                resp.status_code = 500
                return resp


    @app.route("/openGCode", methods=["POST"])
    def openGCode():
        app.data.logger.resetIdler()
        if request.method == "POST":
            f = request.form["selectedGCode"]
            app.data.console_queue.put(f"selectedGcode={f}")
            tDir = f.split("/")
            app.data.config.setValue("Computed Settings", "lastSelectedDirectory", tDir[0])
            home = app.data.config.getHome()
            app.data.gcodeFile.filename = home + "/.WebControl/gcode/" + f
            app.data.config.setValue("Maslow Settings", "openFile", tDir[1])
            returnVal = app.data.gcodeFile.loadUpdateFile()
            if returnVal:
                message = {"status": 200}
                resp = jsonify(message)
                resp.status_code = 200
                return resp
            else:
                message = {"status": 500}
                resp = jsonify(message)
                resp.status_code = 500
                return resp


    @app.route("/saveGCode", methods=["POST"])
    def saveGCode():
        app.data.logger.resetIdler()
        if request.method == "POST":
            app.data.console_queue.put(f"{__name__}: {request.form}")
            f = request.form["fileName"]
            d = request.form["selectedDirectory"]
            app.data.console_queue.put(f"selectedGcode={f}")
            app.data.config.setValue("Computed Settings", "lastSelectedDirectory", d)
            home = app.data.config.getHome()
            returnVal = app.data.gcodeFile.saveFile(f, home + "/.WebControl/gcode/" + d)
            """
            tDir = f.split("/")
            app.data.config.setValue("Computed Settings","lastSelectedDirectory",tDir[0])
            home = app.data.config.getHome()
            app.data.gcodeFile.filename = home+"/.WebControl/gcode/" + f
            app.data.config.setValue("Maslow Settings", "openFile", tDir[1])
            returnVal = app.data.gcodeFile.loadUpdateFile()
            """
            if returnVal:
                app.data.config.setValue("Maslow Settings", "openFile", f)
                message = {"status": 200}
                resp = jsonify(message)
                resp.status_code = 200
                return resp
            else:
                message = {"status": 500}
                resp = jsonify(message)
                resp.status_code = 500
                return resp


    @app.route("/openBoard", methods=["POST"])
    def openBoard():
        app.data.logger.resetIdler()
        if request.method == "POST":
            f = request.form["selectedBoard"]
            app.data.console_queue.put(f"selectedBoard={f}")
            tDir = f.split("/")
            app.data.config.setValue(
                "Computed Settings", "lastSelectedBoardDirectory", tDir[0]
            )
            home = app.data.config.getHome()
            app.data.gcodeFile.filename = home + "/.WebControl/boards/" + f
            app.data.config.setValue("Maslow Settings", "openBoardFile", tDir[1])
            returnVal = app.data.boardManager.loadBoard(home + "/.WebControl/boards/" + f)
            if returnVal:
                message = {"status": 200}
                resp = jsonify(message)
                resp.status_code = 200
                return resp
            else:
                message = {"status": 500}
                resp = jsonify(message)
                resp.status_code = 500
                return resp


    @app.route("/saveBoard", methods=["POST"])
    def saveBoard():
        app.data.logger.resetIdler()
        if request.method == "POST":
            app.data.console_queue.put(f"{__name__}: {request.form}")
            f = request.form["fileName"]
            d = request.form["selectedDirectory"]
            app.data.console_queue.put(f"selectedBoard={f}")
            app.data.config.setValue("Computed Settings", "lastSelectedBoardDirectory", d)
            home = app.data.config.getHome()
            returnVal = app.data.boardManager.saveBoard(
                f, home + "/.WebControl/boards/" + d
            )
            app.data.config.setValue("Maslow Settings", "openBoardFile", f)
            if returnVal:
                message = {"status": 200}
                resp = jsonify(message)
                resp.status_code = 200
                return resp
            else:
                message = {"status": 500}
                resp = jsonify(message)
                resp.status_code = 500
                return resp


    @app.route("/importFile", methods=["POST"])
    def importFile():
        app.data.logger.resetIdler()
        if request.method == "POST":
            f = request.files["file"]
            home = app.data.config.getHome()
            secureFilename = home + "/.WebControl/imports/" + secure_filename(f.filename)
            f.save(secureFilename)
            returnVal = app.data.importFile.importGCini(secureFilename)
            if returnVal:
                message = {"status": 200}
                resp = jsonify(message)
                resp.status_code = 200
                return resp
            else:
                message = {"status": 500}
                resp = jsonify(message)
                resp.status_code = 500
                return resp


    @app.route("/importFileWCJSON", methods=["POST"])
    def importFileJSON():
        app.data.logger.resetIdler()
        if request.method == "POST":
            f = request.files["file"]
            home = app.data.config.getHome()
            secureFilename = home + "/.WebControl/imports/" + secure_filename(f.filename)
            f.save(secureFilename)
            returnVal = app.data.importFile.importWebControlJSON(secureFilename)
            if returnVal:
                message = {"status": 200}
                resp = jsonify(message)
                resp.status_code = 200
                return resp
            else:
                message = {"status": 500}
                resp = jsonify(message)
                resp.status_code = 500
                return resp


    @app.route("/importRestoreWebControl", methods=["POST"])
    def importRestoreWebControl():
        app.data.logger.resetIdler()
        if request.method == "POST":
            f = request.files["file"]
            home = app.data.config.getHome()
            secureFilename = home + "/" + secure_filename(f.filename)
            f.save(secureFilename)
            returnVal = app.data.actions.restoreWebControl(secureFilename)
            if returnVal:
                message = {"status": 200}
                resp = jsonify(message)
                resp.status_code = 200
                return resp
            else:
                message = {"status": 500}
                resp = jsonify(message)
                resp.status_code = 500
                return resp


    @app.route("/sendGCode", methods=["POST"])
    def sendGcode():
        app.data.logger.resetIdler()
        # app.data.console_queue.put(f"{__name__}: {request.form)#['gcodeInput']}")
        if request.method == "POST":
            returnVal = app.data.actions.sendGCode(request.form["gcode"].rstrip())
            if returnVal:
                message = {"status": 200}
                resp = jsonify("success")
                resp.status_code = 200
                return resp
            else:
                message = {"status": 500}
                resp = jsonify("failed")
                resp.status_code = 500
                return resp


    @app.route("/triangularCalibration", methods=["POST"])
    def triangularCalibration():
        app.data.logger.resetIdler()
        if request.method == "POST":
            result = request.form
            (
                motorYoffsetEst,
                rotationRadiusEst,
                chainSagCorrectionEst,
                cut34YoffsetEst,
            ) = app.data.actions.calibrate(result)
            # app.data.console_queue.put(f"{__name__}: {returnVal}")
            if motorYoffsetEst:
                message = {
                    "status": 200,
                    "data": {
                        "motorYoffset": motorYoffsetEst,
                        "rotationRadius": rotationRadiusEst,
                        "chainSagCorrection": chainSagCorrectionEst,
                        "calibrationError": cut34YoffsetEst,
                    },
                }
                resp = jsonify(message)
                resp.status_code = 200
                return resp
            else:
                message = {"status": 500}
                resp = jsonify(message)
                resp.status_code = 500
                return resp


    @app.route("/holeyCalibration", methods=["POST"])
    def holeyCalibration():
        app.data.logger.resetIdler()
        if request.method == "POST":
            result = request.form
            (
                motorYoffsetEst,
                distanceBetweenMotors,
                leftChainTolerance,
                rightChainTolerance,
                calibrationError,
            ) = app.data.actions.holeyCalibrate(result)
            # app.data.console_queue.put(f"{__name__}: {returnVal}")
            if motorYoffsetEst:
                message = {
                    "status": 200,
                    "data": {
                        "motorYoffset": motorYoffsetEst,
                        "distanceBetweenMotors": distanceBetweenMotors,
                        "leftChainTolerance": leftChainTolerance,
                        "rightChainTolerance": rightChainTolerance,
                        "calibrationError": calibrationError,
                    },
                }
                resp = jsonify(message)
                resp.status_code = 200
                return resp
            else:
                message = {"status": 500}
                resp = jsonify(message)
                resp.status_code = 500
                return resp


    @app.route("/opticalCalibration", methods=["POST"])
    def opticalCalibration():
        app.data.logger.resetIdler()
        if request.method == "POST":
            result = request.form
            message = {"status": 200}
            resp = jsonify(message)
            resp.status_code = 200
            return resp
        else:
            message = {"status": 500}
            resp = jsonify(message)
            resp.status_code = 500
            return resp


    @app.route("/quickConfigure", methods=["POST"])
    def quickConfigure():
        app.data.logger.resetIdler()
        if request.method == "POST":
            result = request.form
            app.data.config.updateQuickConfigure(result)
            message = {"status": 200}
            resp = jsonify(message)
            resp.status_code = 200
            return resp


    @app.route("/editGCode", methods=["POST"])
    def editGCode():
        app.data.logger.resetIdler()
        # app.data.console_queue.put(f"{__name__}: {request.form['gcode']}")
        if request.method == "POST":
            returnVal = app.data.actions.updateGCode(request.form["gcode"].rstrip())
            if returnVal:
                message = {"status": 200}
                resp = jsonify("success")
                resp.status_code = 200
                return resp
            else:
                message = {"status": 500}
                resp = jsonify("failed")
                resp.status_code = 500
                return resp


    @app.route("/downloadDiagnostics", methods=["GET"])
    def downloadDiagnostics():
        app.data.logger.resetIdler()
        if request.method == "GET":
            returnVal = app.data.actions.downloadDiagnostics()
            if returnVal != False:
                app.data.console_queue.put(f"{__name__}: {returnVal}")
                return send_file(returnVal, as_attachment=True)
            else:
                resp = jsonify("failed")
                resp.status_code = 500
                return resp


    @app.route("/backupWebControl", methods=["GET"])
    def backupWebControl():
        app.data.logger.resetIdler()
        if request.method == "GET":
            returnVal = app.data.actions.backupWebControl()
            if returnVal != False:
                app.data.console_queue.put(f"{__name__}: {returnVal}")
                return send_file(returnVal)
            else:
                resp = jsonify("failed")
                resp.status_code = 500
                return resp


    @app.route("/editBoard", methods=["POST"])
    def editBoard():
        app.data.logger.resetIdler()
        if request.method == "POST":
            returnVal = app.data.boardManager.editBoard(request.form)
            if returnVal:
                resp = jsonify("success")
                resp.status_code = 200
                return resp
            else:
                resp = jsonify("failed")
                resp.status_code = 500
                return resp


    @app.route("/trimBoard", methods=["POST"])
    def trimBoard():
        app.data.logger.resetIdler()
        if request.method == "POST":
            returnVal = app.data.boardManager.trimBoard(request.form)
            if returnVal:
                resp = jsonify("success")
                resp.status_code = 200
                return resp
            else:
                resp = jsonify("failed")
                resp.status_code = 500
                return resp


    @app.route("/assets/<path:path>")
    def sendDocs(path):
        app.data.console_queue.put(f"{__name__}: {path}")
        return send_from_directory("docs/assets/", path)
