
function unitSwitch(){
  if ( $("#units").text()=="MM") {
    distToMove = (parseFloat($("#distToMove").val())/25.4).toFixed(3)
    updateSetting('toInches',distToMove);
  } else {
    distToMove = (parseFloat($("#distToMove").val())*25.4).toFixed(3)
    updateSetting('toMM',distToMove);
  }
}

$(document).ready(function(){
    //settingRequest("Computed Settings","units");
    //settingRequest("Computed Settings","distToMove");
    //settingRequest("Computed Settings","homePosition");
    var controllerMessage = document.getElementById('controllerMessage');
    controllerMessage.scrollTop = controllerMessage.scrollHeight;
});

function pauseRun(){
  if ($("#pauseButton").text()=="Pause"){
    action('pauseRun');
  }
  else {
    action('resumeRun');
  }
}

function processRequestedSetting(data){
  if (data.setting=="pauseButtonSetting"){
    if(data.value=="Resume")
        $('#pauseButton').removeClass('btn-warning').addClass('btn-info');
    else
        $('#pauseButton').removeClass('btn-info').addClass('btn-warning');
    $("#pauseButton").text(data.value);
  }
  if (data.setting=="units"){
    console.log("requestedSetting:"+data.value);
    $("#units").text(data.value)
  }
  if (data.setting=="distToMove"){
    console.log("requestedSetting for distToMove:"+data.value);
    $("#distToMove").val(data.value)
  }
  if ((data.setting=="unitsZ") || (data.setting=="distToMoveZ")){
    if (typeof processZAxisRequestedSetting === "function") {
       processZAxisRequestedSetting(data)
    }
  }
}

function processPositionMessage(data){
  $('#positionMessage').html('X:'+parseFloat(data.xval).toFixed(2)+' Y:'+parseFloat(data.yval).toFixed(2)+' Z:'+parseFloat(data.zval).toFixed(2));
  $('#percentComplete').html(data.pcom)
  $('#machineState').html(data.state)
}

function processErrorValueMessage(data){
 $('#leftError').css('width', data.leftError*100+'%').attr('aria-valuenow', data.leftError*100);
 $('#rightError').css('width', data.rightError*100+'%').attr('aria-valuenow', data.rightError*100);
}

function processHomePositionMessage(data){
  $('#homePositionMessage').html('X:'+parseFloat(data.xval).toFixed(2)+' Y:'+parseFloat(data.yval).toFixed(2));
}

function processGCodePositionMessage(data){
  $('#gcodePositionMessage').html('X:'+parseFloat(data.xval).toFixed(2)+' Y:'+parseFloat(data.yval).toFixed(2));
  $('#gcodeLine').html(data.gcodeLine);
  $('#gcodeLineIndex').val(data.gcodeLineIndex+1)
}

function gcodeUpdate(msg){
  console.log("Unsupported");
}

function gcodeUpdateCompressed(data){
  console.log("Unsupported");
  $("#fpCircle").hide();
}

function showFPSpinner(msg){
    $("#fpCircle").show();
}

function toggle3DView()
{
    console.log("Unsupported");
}

function resetView(){
    console.log("Unsupported");
}

function cursorPosition(){
    console.log("Unsupported");
}

function processCameraMessage(data){
    console.log("Unsupported");
}

function processControllerMessage(data){
    if (controllerMessages.length >100)
        controllerMessages.shift();
    controllerMessages.push(data);
    $('#controllerMessage').html('');
    controllerMessages.forEach(function(message){
        $('#controllerMessage').append(message+"<br>");
    });
    $('#controllerMessage').scrollBottom();
}

function processAlarm(data){
    console.log("alarm received");
    $("#alarms").html("<marquee behavior='scroll' direction='left'>"+data.message+"</marquee>");
    $("#alarms").removeClass('alert-success').addClass('alert-danger');
    $("#stopButton").addClass('stopbutton');
}

function clearAlarm(data){
    console.log("clearing alarm");
    $("#alarms").text("Alarm cleared.");
    $("#alarms").removeClass('alert-danger').addClass('alert-success');
}

function processStatusMessage(data){
    if (data.uploadFlag == 1){
        if (!isDisabled){
            $('.disabler').prop('disabled', true);
            isDisabled = true;
        }
    } else {
        if (isDisabled){
            $('.disabler').prop('disabled', false);
            isDisabled = false;
        }
    }
    $("#currentTool").text(data.currentTool.toString());
    if (data.positioningMode == 0)
        $("#currentPositioningMode").text("Absolute (G90)");
    else
        $("#currentPositioningMode").text("Incremental (G91)");
}
