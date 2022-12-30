import { action } from "./socketEmits.js";
import { dp2, pwr2color } from "./utilities.js";
import { processZAxisRequestedSetting } from "./zAxis.js";

window.board = {
  width: 96,
  height: 48,
  thickness: 0.75,
  centerX: 0,
  centerY: 0,
  ID: "-",
  material: "-",
};

function pauseRun() {
  action($("#pauseButton").text() == "Pause" ? "pauseRun" : "resumeRun");
}

function resumeRun() {
  action('resumeRun')
}

function processRequestedSetting(data) {
  if (data.setting == "pauseButtonSetting") {
    if (data.value == "Resume")
      $('#pauseButton').removeClass('btn-warning').addClass('btn-info');
    else
      $('#pauseButton').removeClass('btn-info').addClass('btn-warning');
    $("#pauseButton").text(data.value);
  }
  if (data.setting == "units") {
    console.log("requestedSetting:" + data.value);
    $("#units").text(data.value)
  }
  if (data.setting == "distToMove") {
    console.log("requestedSetting for distToMove:" + data.value);
    $("#distToMove").val(data.value)
  }
  if ((data.setting == "unitsZ") || (data.setting == "distToMoveZ")) {
    if (typeof processZAxisRequestedSetting === "function") {
      processZAxisRequestedSetting(data)
    }
  }
}

function processPositionMessage(data) {
  $('#percentComplete').html(data.pcom)
  $('#machineState').html(data.state)
  if (window.isFrontpage3d_mobilecontrols) {
    $('#positionMessage').html(`X:${dp2(data.xval)} Y:${dp2(data.yval)} Z:${dp2(data.zval)}`);
    return;
  }

  // All the others
  $('#positionMessage').html(`X:${dp2(data.xval)} Y:${dp2(data.yval)} Z:${dp2(data.zval)} V:${(data.vel)}/${(data.rqvel)}`);
  if (window.enable3D) {
    window.frontpage3d.positionUpdate(data.xval, data.yval, data.zval);
  }

  $('#leftError').css('background-color', pwr2color(data.lpwr)).attr('title', data.lpwr);
  $('#rightError').css('background-color', pwr2color(data.rpwr)).attr('title', data.rpwr);
  $('#zError').css('background-color', pwr2color(data.zpwr)).attr('title', data.zpwr);
}

function processErrorValueMessage(data) {
  $('#leftError').css('width', data.leftError * 100 + '%').attr('aria-valuenow', data.leftError * 100);
  $('#rightError').css('width', data.rightError * 100 + '%').attr('aria-valuenow', data.rightError * 100);
  if (window.isFrontpage3d_mobilecontrols && window.enable3D) {
    window.frontpage3d.processError3d(data);
  }
}

function processHomePositionMessage(data) {
  $('#homePositionMessage').html(`X:${dp2(data.xval)} Y:${dp2(data.yval)}`);
  if (window.isFrontpage3d_mobilecontrols && enable3D) {
    window.frontpage3d.homePositionUpdate(data.xval, data.yval);
  }
}

function processGCodePositionMessage(data) {
  $('#gcodeLine').html(data.gcodeLine);
  $('#gcodeLineIndex').val(data.gcodeLineIndex + 1)
  if (window.isFrontpage3d_mobilecontrols) {
    $('#positionMessage').html(`X:${dp2(data.xval)} Y:${dp2(data.yval)}`);
    return;
  }

  // All the others
  $('#gcodePositionMessage').html(`X:${dp(data.xval)} Y:${dp(data.yval)} Z:${dp(data.zval)}`);
  if (enable3D) {
    window.frontpage3d.gcodePositionUpdate(data.xval, data.yval, data.zval);
  }
}

function processControllerMessage(data) {
  if (window.controllerMessages.length > 100) {
    window.controllerMessages.shift();
  }
  window.controllerMessages.push(data);
  $('#controllerMessage').html('');
  window.controllerMessages.forEach((message) => {
    $('#controllerMessage').append(`${message}<br>`);
  });
  $('#controllerMessage').scrollBottom();
}

function processAlarm(data) {
  console.log("alarm received");
  // Can you say 'DEPRECATED'!!!! - TODO: get rid of the marquee
  $("#alarms").html("<marquee behavior='scroll' direction='left'>" + data.message + "</marquee>");
  $("#alarms").removeClass('alert-success').addClass('alert-danger');
  $("#stopButton").addClass('stopbutton');
}

function clearAlarm(data) {
  console.log("clearing alarm");
  $("#alarms").text("Alarm cleared.");
  $("#alarms").removeClass('alert-danger').addClass('alert-success');
  $("#stopButton").removeClass('stopbutton');
}

function boardDataUpdate(data) {
  console.log("updating board data");
  window.board.width = data.width;
  window.board.height = data.height;
  window.board.thickness = data.thickness;
  window.board.centerX = data.centerX;
  window.board.centerY = data.centerY;
  window.board.ID = data.boardID;
  window.board.material = data.material;
  $("#boardID").text(`Board: ${window.board.ID}, Material: ${window.board.material}`);
  if (window.enable3D) {
    window.frontpage3d.board3DDataUpdate(data);
  }
}

function moveAction(direction) {
  distance = $("#distToMove").val();
  distanceValid = distance.search(/^[0-9]*(\.[0-9]{0,3})?$/);
  if (distanceValid == 0) {
    action('move', direction, distance);
  } else {
    $("#distToMove").focus();
  }
}

function processStatusMessage(data) {
  //console.log(data)
  $("#currentTool").text(data.currentTool.toString());
  $("#currentPositioningMode").text((data.positioningMode == 0) ? "Absolute (G90)" : "Incremental (G91)");

  if (window.isFrontpage3d_mobilecontrols) {
    if (data.uploadFlag == 1) {
      if (!window.isDisabled) {
        $('.disabler').prop('disabled', true);
        window.isDisabled = true;
      }
    } else {
      if (window.isDisabled) {
        $('.disabler').prop('disabled', false);
        window.isDisabled = false;
      }
    }
    return;
  }

  if (data.uploadFlag == 1) {
    if (window.isDisabled != data.uploadFlag) {
      $('.disabler').prop('disabled', true);
      $('.ndisabler').prop('disabled', false);
      $('.gcdisabler').prop('disabled', true);
      window.isDisabled = data.uploadFlag;
    }
  } else if (data.uploadFlag == 2 || data.uploadFlag == -1) {
    if (window.isDisabled != data.uploadFlag) {
      $('.gcdisabler').prop('disabled', true);
      $('.disabler').prop('disabled', false);
      $('.ndisabler').prop('disabled', false);
      window.isDisabled = data.uploadFlag;
    }
  } else if (window.isDisabled != data.uploadFlag) {
    $('.disabler').prop('disabled', false);
    $('.ndisabler').prop('disabled', true);
    $('.gcdisabler').prop('disabled', false);
    window.isDisabled = data.uploadFlag;
  }
}

export {
  boardDataUpdate,
  clearAlarm,
  moveAction,
  pauseRun,
  processAlarm,
  processControllerMessage,
  processErrorValueMessage,
  processGCodePositionMessage,
  processHomePositionMessage,
  processPositionMessage,
  processRequestedSetting,
  processStatusMessage,
  resumeRun,
};
