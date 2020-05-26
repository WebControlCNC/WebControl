var socket;
var socketClientID;
var controllerMessages = [];
var hostAddress = "..."
var enable3D = true;
$(document).ready(function(){
  namespace = '/MaslowCNC'; // change to an empty string to use the global namespace
  // the socket.io documentation recommends sending an explicit package upon connection
  // this is specially important when using the global namespace
  socket = io.connect('//' + document.domain + ':' + location.port + namespace, {'forceNew':true});

  setListeners();
  setupStatusButtons();
});

function processHostAddress(data){
  hostAddress = data["hostAddress"]
  $("#clientStatus").text("Connected to "+hostAddress);
}

function setListeners(){
  console.log("setting Listeners");
  socket.on('connect', function(msg) {
      socketClientID = socket.io.engine.id;
      console.log("id="+socketClientID);
      socket.emit('my event', {data: 'I\'m connected!'});
      $("#clientStatus").text("Connected: "+hostAddress);
      $("#clientStatus").removeClass('alert-danger').addClass('alert-success');
      $("#mobileClientStatus").removeClass('alert-danger').addClass('alert-success');
      $("#mobileClientStatus svg.feather.feather-alert-circle").replaceWith(feather.icons["check-circle"].toSvg());
      settingRequest("Computed Settings","units");
      settingRequest("Computed Settings","distToMove");
      settingRequest("Computed Settings","homePosition");
      settingRequest("Computed Settings","unitsZ");
      settingRequest("Computed Settings","distToMoveZ");
      settingRequest("None","pauseButtonSetting");
      checkForGCodeUpdate();
      checkForBoardUpdate();
  });

  socket.on('disconnect', function(msg) {
      $("#clientStatus").text("Not Connected");
      hostAddress = "Not Connected"
      $("#clientStatus").removeClass('alert-success').addClass('alert-outline-danger');
      $("#mobileClientStatus").removeClass('alert-success').addClass('alert-danger');
      $("#mobileClientStatus svg.feather.feather-check-circle").replaceWith(feather.icons["alert-circle"].toSvg());
      $("#controllerStatus").removeClass('alert-success').removeClass('alert-danger').addClass('alert-secondary');
      $("#mobileControllerStatus").removeClass('alert-success').removeClass('alert-danger').addClass('alert-secondary');

  });

  $("#notificationModal").on('hidden.bs.modal', function(e){
      var name = $('#notificationModal').data('name');
      console.log("closing modal:"+name);
      socket.emit('modalClosed', {data:name});
  });

  /*
  todo: cleanup
  Not used

  $("#actionModal").on('hidden.bs.modal', function(e){
      var name = $('#actionModal').data('name');
      console.log("closing modal:"+name);
      socket.emit('actionModalClosed', {data:name});
  });
*/
  $("#alertModal").on('hidden.bs.modal', function(e){
      var name = $('#alertModal').data('name');
      console.log("closing modal:"+name);
      socket.emit('alertModalClosed', {data:name});
  });

  $("#contentModal").on('hidden.bs.modal', function(e){
      var name = $('#contentModal').data('name');
      console.log("closing modal:"+name);
      //socket.emit('contentModalClosed', {data:name});
  });

  socket.on('message', function(msg){
      //console.log(msg);
      //blink activity indicator
      $("#cpuUsage").removeClass('alert-success').addClass('alertalert-warning');
      $("#mobileCPUUsage").removeClass('alert-success').addClass('alert-warning');
      setTimeout(function(){
        $("#cpuUsage").removeClass('alert-warning').addClass('alert-success');
        $("#mobileCPUUsage").removeClass('alert-warning').addClass('alert-success');
      },125);
      //console.log(msg.command);
      if (msg.dataFormat=='json')
        data = JSON.parse(msg.data);
      else
        data = msg.data;
      passValue = true
      if ((data !=null) && (data.hasOwnProperty('client')))
      {
            //console.log(data.client);
            if ((data.client != socketClientID) && (data.client!="all"))
                passValue = false;
      }

      if (passValue)
      {
          switch(msg.command) {
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
                processCalibrationMessage(data);
                break;
            case 'cameraMessage':
                //completed
                if (enable3D)
                    processCameraMessage(data);
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
                if (enable3D)
                    gcodeUpdate(msg.message);
                else
                    $("#fpCircle").hide();
                break;
            case 'showFPSpinner':
                //completed
                showFPSpinner(msg.message);
                break;
            case 'gcodeUpdateCompressed':
                if (enable3D)
                    gcodeUpdateCompressed(data);
                else
                    $("#fpCircle").hide();
                break;
            case 'boardDataUpdate':
                boardDataUpdate(data);
                break;
            case 'boardCutDataUpdateCompressed':
                if (enable3D)
                    boardCutDataUpdateCompressed(data);
                else
                    $("#fpCircle").hide();
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
                console.log("uncaught action:"+msg.command);
                console.log("!!!!!!");
        }
      }
  });

}

function action() {
  var msg = {"command": arguments[0]};
  if (arguments.length > 1 ) {
    var args = new Array()
    for (var i=1; i < arguments.length; i++) {
      args[i-1] = arguments[i];
    }
    msg["args"] = args;
  }
  console.log("action=" + arguments[0]);
  socket.emit('action', msg);
}


function settingRequest(section,setting){
  console.log("requesting..")
  socket.emit('settingRequest',{data:{section:section,setting:setting}});
}

function statusRequest(status){
  console.log("requesting status..")
  socket.emit('statusRequest',{data:{status:status}});
}

function requestPage(page, args=""){
  console.log("requesting page..")
  socket.emit('requestPage',{data:{page:page, isMobile:isMobile, args:args}});
}

function updateSetting(setting, value){
    socket.emit('updateSetting',{data:{setting:setting,value:value}});
}

function checkForGCodeUpdate(){
    socket.emit('checkForGCodeUpdate',{data:"Please"});
}

function checkForBoardUpdate(){
    socket.emit('checkForBoardUpdate',{data:"Please"});
}

function checkForHostAddress(){
    socket.emit('checkForHostAddress',{data:"Please"});
}
