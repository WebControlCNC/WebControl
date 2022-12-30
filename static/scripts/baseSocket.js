import { io } from "../node_modules/socket.io-client/dist/socket.io.esm.min.js";

import {
  closeAlertModals,
  closeContentModals,
  closeModals,
  processActivateModal,
  processControllerStatus,
  processHealthMessage,
  pyInstallUpdateBadge,
  setupStatusButtons,
} from "./base.js";
import {
  boardDataUpdate,
  clearAlarm,
  processAlarm,
  processControllerMessage,
  processErrorValueMessage,
  processGCodePositionMessage,
  processHomePositionMessage,
  processPositionMessage,
  processRequestedSetting,
  processStatusMessage,
} from "./frontpageControlsCommon.js";
import {
  processPositionMessageOptical,
  updateCalibrationImage,
  updateOpticalCalibrationCurve,
  updateOpticalCalibrationError,
  updateOpticalCalibrationFindCenter,
} from "./opticalCalibration.js";
import { updatePIDData } from "./pidTuning.js";
import { processCalibrationMessage } from "./setSprockets.js";
import { updatePorts } from "./settings.js";
import { action, settingRequest, checkForGCodeUpdate, checkForBoardUpdate } from "./socketEmits.js";
import { updateDirectories } from "./uploadGCode.js";

// Note: because this is a module, these variables are NOT global
let socketClientID;
let hostAddress = "..."

$(document).ready(function () {
  const namespace = '/MaslowCNC'; // change to an empty string to use the global namespace
  // the socket.io documentation recommends sending an explicit package upon connection
  // this is specially important when using the global namespace
  const serverURL = `//${location.hostname}:${location.port}${namespace}`;
  console.log(serverURL);

  // Set up our globals
  window.socket = io(serverURL);
  window.enable3D = true;
  window.controllerMessages = [];

  setListeners();
  setupStatusButtons();

  // Originally from frontpageControls.js
  action("statusRequest", "cameraStatus");

  // Originally From zAxis.js
  settingRequest("Computed Settings", "unitsZ");
  settingRequest("Computed Settings", "distToMoveZ");
});

function processHostAddress(data) {
  hostAddress = data["hostAddress"]
  $("#clientStatus").text("Connected to " + hostAddress);
}

function setListeners() {
  console.log("setting Listeners");
  window.socket.on('connect', function (msg) {
    socketClientID = window.socket.io.engine.id;
    console.log("id=" + socketClientID);
    window.socket.emit('my event', { data: 'I\'m connected!' });
    $("#clientStatus").text("Connected: " + hostAddress);
    $("#clientStatus").removeClass('alert-danger').addClass('alert-success');
    $("#mobileClientStatus").removeClass('alert-danger').addClass('alert-success');
    $("#mobileClientStatus svg.feather.feather-alert-circle").replaceWith(feather.icons["check-circle"].toSvg());
    settingRequest("Computed Settings", "units");
    settingRequest("Computed Settings", "distToMove");
    settingRequest("Computed Settings", "homePosition");
    settingRequest("Computed Settings", "unitsZ");
    settingRequest("Computed Settings", "distToMoveZ");
    settingRequest("None", "pauseButtonSetting");
    checkForGCodeUpdate();
    checkForBoardUpdate();
  });

  window.socket.on('disconnect', function (msg) {
    $("#clientStatus").text("Not Connected");
    hostAddress = "Not Connected"
    $("#clientStatus").removeClass('alert-success').addClass('alert-outline-danger');
    $("#mobileClientStatus").removeClass('alert-success').addClass('alert-danger');
    $("#mobileClientStatus svg.feather.feather-check-circle").replaceWith(feather.icons["alert-circle"].toSvg());
    $("#controllerStatus").removeClass('alert-success').removeClass('alert-danger').addClass('alert-secondary');
    $("#mobileControllerStatus").removeClass('alert-success').removeClass('alert-danger').addClass('alert-secondary');

  });

  $("#notificationModal").on('hidden.bs.modal', function (e) {
    var name = $('#notificationModal').data('name');
    console.log("closing modal:" + name);
    window.socket.emit('modalClosed', { data: name });
  });

  /*
  todo: cleanup
  Not used

  $("#actionModal").on('hidden.bs.modal', function(e){
      var name = $('#actionModal').data('name');
      console.log("closing modal:"+name);
      window.socket.emit('actionModalClosed', {data:name});
  });
*/
  $("#alertModal").on('hidden.bs.modal', function (e) {
    var name = $('#alertModal').data('name');
    console.log("closing modal:" + name);
    window.socket.emit('alertModalClosed', { data: name });
  });

  $("#contentModal").on('hidden.bs.modal', function (e) {
    var name = $('#contentModal').data('name');
    console.log("closing modal:" + name);
    //window.socket.emit('contentModalClosed', {data:name});
  });

  window.socket.on('message', function (msg) {
    //console.log(msg);
    //blink activity indicator
    $("#cpuUsage").removeClass('alert-success').addClass('alertalert-warning');
    $("#mobileCPUUsage").removeClass('alert-success').addClass('alert-warning');
    setTimeout(function () {
      $("#cpuUsage").removeClass('alert-warning').addClass('alert-success');
      $("#mobileCPUUsage").removeClass('alert-warning').addClass('alert-success');
    }, 125);
    //console.log(msg.command);
    if (msg.dataFormat == 'json')
      data = JSON.parse(msg.data);
    else
      data = msg.data;
    passValue = true
    if ((data != null) && (data.hasOwnProperty('client'))) {
      //console.log(data.client);
      if ((data.client != socketClientID) && (data.client != "all"))
        passValue = false;
    }

    if (passValue) {
      switch (msg.command) {
        case 'statusMessage':
          //completed
          processStatusMessage(data);
          break;
        case 'healthMessage':
          //completed
          processHealthMessage(data);
          break;
        case 'hostAddress':
          //completed
          processHostAddress(data);
          break;
        case 'controllerMessage':
          //completed
          processControllerMessage(data);
          break;
        case 'connectionStatus':
          //completed
          processControllerStatus(data);
          break;
        case 'calibrationMessage':
          // TODO: handle optical calibration not supporting this (and not being included)
          processCalibrationMessage(data);
          break;
        case 'cameraMessage':
          //completed
          if (window.enable3D) {
            window.frontpage3d.processCameraMessage(data);
          }
          break;
        case 'positionMessage':
          //completed
          processPositionMessage(data)
          if (typeof processPositionMessageOptical === "function") {
            processPositionMessageOptical(data)
          }
          break;
        case 'errorValueMessage':
          processErrorValueMessage(data)
          break;
        case 'homePositionMessage':
          //completed
          processHomePositionMessage(data);
          break;
        case 'gcodePositionMessage':
          //completed
          processGCodePositionMessage(data);
          break;
        case 'activateModal':
          //completed
          //console.log(msg)
          processActivateModal(data);
          break;
        case 'requestedSetting':
          //completed
          processRequestedSetting(data);
          break;
        case 'updateDirectories':
          //completed
          updateDirectories(data);
          break;
        case 'gcodeUpdate':
          console.log("---gcodeUpdate received via socket---");
          if (window.enable3D)
            window.frontpage3d.gcodeUpdate(msg.message);
          else
            $("#fpCircle").hide();
          break;
        case 'showFPSpinner':
          //completed
          window.showFPSpinner(msg.message);
          break;
        case 'gcodeUpdateCompressed':
          if (window.enable3D) {
            window.frontpage3d.gcodeUpdateCompressed(data);
          } else {
            $("#fpCircle").hide();
          }
          break;
        case 'boardDataUpdate':
          boardDataUpdate(data);
          break;
        case 'boardCutDataUpdateCompressed':
          if (window.enable3D) {
            window.frontpage3d.boardCutDataUpdateCompressed(data);
          } else {
            $("#fpCircle").hide();
          }
          break;
        case 'updatePorts':
          //completed
          if (typeof updatePorts === "function") {
            updatePorts(data);
          }
          break;
        case 'closeModals':
          //completed
          closeModals(data);
          break;
        /*
        todo: cleanup
        Not used
        case 'closeActionModals':
            //completed
            closeActionModals(data);
            break;
        */
        case 'closeAlertModals':
          //completed
          closeAlertModals(data);
          break;
        case 'closeContentModals':
          //completed
          closeContentModals(data);
          break;
        case 'updateOpticalCalibrationCurve':
          //completed
          updateOpticalCalibrationCurve(data);
          break;
        case 'updateOpticalCalibrationError':
          //completed
          updateOpticalCalibrationError(data);
          break;
        case 'updateOpticalCalibrationFindCenter':
          //completed
          updateOpticalCalibrationFindCenter(data);
          break;
        case 'updateCalibrationImage':
          //completed
          updateCalibrationImage(data);
          break;
        case 'updatePIDData':
          //completed
          updatePIDData(data);
          break;
        case 'alarm':
          processAlarm(data);
          break;
        case 'clearAlarm':
          clearAlarm(data);
          break;
        case 'pyinstallUpdate':
          pyInstallUpdateBadge(data);
          break;
        default:
          console.log("!!!!!!");
          console.log("uncaught action:" + msg.command);
          console.log("!!!!!!");
      }
    }
  });

}
