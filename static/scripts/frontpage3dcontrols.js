
function unitSwitch(){
  if ( $("#units").text()=="MM") {
    distToMove = Math.round($("#distToMove").val()/25.4,3)
    updateSetting('toInches',distToMove);
  } else {
    distToMove = Math.round($("#distToMove").val()*25.4,3)
    updateSetting('toMM',distToMove);
  }
}

$(document).ready(function(){
    settingRequest("Computed Settings","units");
    settingRequest("Computed Settings","distToMove");
    settingRequest("Computed Settings","homePosition");
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
  $('#positionMessage').html('XPos:'+parseFloat(data.xval).toFixed(2)+' Ypos:'+parseFloat(data.yval).toFixed(2)+' ZPos:'+parseFloat(data.zval).toFixed(2));
  $('#percentComplete').html(data.pcom)
  $('#machineState').html(data.state)
}

function processHomePositionMessage(data){
  $('#homePositionMessage').html('XPos:'+parseFloat(data.xval).toFixed(2)+' Ypos:'+parseFloat(data.yval).toFixed(2));
}

function processGCodePositionMessage(data){
  $('#gcodePositionMessage').html('XPos:'+parseFloat(data.xval).toFixed(2)+' Ypos:'+parseFloat(data.yval).toFixed(2));
  $('#gcodeLine').html(data.gcodeLine);
  $('#gcodeLineIndex').val(data.gcodeLineIndex)
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