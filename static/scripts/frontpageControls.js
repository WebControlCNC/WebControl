
var boardWidth = 96
var boardHeight = 48
var boardThickness = 0.75
var boardCenterX = 0
var boardCenterY = 0
var boardID = "-"
var boardMaterial = "-"

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
    action("statusRequest","cameraStatus");
    var controllerMessage = document.getElementById('controllerMessage');
    controllerMessage.scrollTop = controllerMessage.scrollHeight;
    $("#stickyButtons").css("top", $(".navbar").outerHeight());

    // Set custom validation on all form inputs of type 'number' with attribute 'pattern'.
    // Input type 'number' does not support 'pattern' attribute by default using HTML5.
    // Input type 'number' always returns a value compatible with parseFloat using period as decimal separator.
    // @todo: This event handler may need to be moved to other JS files for more/less global application.
    $(':input[type="number"][pattern]').change(function () {
      var re = new RegExp($(this).attr("pattern"));
      var isValid = re.test($(this).val());
      // JQuery selector returns array of possible matches.
      // Validity checks must be applied to first item [0].
      if (isValid) {
        // Set empty value to clear error.
        $(this)[0].setCustomValidity("");
      }
      else {
        // Set title as error message.
        $(this)[0].setCustomValidity($(this).attr("title"));
      }
    });
});

function pauseRun(){
  if ($("#pauseButton").text()=="Pause"){
    action('pauseRun');
  }
  else {
    action('resumeRun');
  }
}

function resumeRun(){
    action('resumeRun')
}

function processRequestedSetting(data){
  //console.log(data);
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
  if (enable3D)
    positionUpdate(data.xval,data.yval,data.zval);
}

function processErrorValueMessage(data){
 $('#leftError').css('width', data.leftError*100+'%').attr('aria-valuenow', data.leftError*100);
 $('#rightError').css('width', data.rightError*100+'%').attr('aria-valuenow', data.rightError*100);
 if (enable3D){
    processError3d(data)
 }
}


function processHomePositionMessage(data){
  console.log(data.xval)
  $('#homePositionMessage').html('X:'+parseFloat(data.xval).toFixed(2)+' Y:'+parseFloat(data.yval).toFixed(2));
  if (enable3D)
    homePositionUpdate(data.xval,data.yval);
}

function processGCodePositionMessage(data){
  $('#gcodePositionMessage').html('X:'+parseFloat(data.xval).toFixed(2)+' Y:'+parseFloat(data.yval).toFixed(2)+' Z:'+parseFloat(data.zval).toFixed(2));
  $('#gcodeLine').html(data.gcodeLine);
  $('#gcodeLineIndex').val(data.gcodeLineIndex+1)
  if (enable3D)
    gcodePositionUpdate(data.xval,data.yval,data.zval);
}

function showFPSpinner(msg){
    $("#fpCircle").show();
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
    $("#stopButton").removeClass('stopbutton');
}


function boardDataUpdate(data){
  console.log("updating board data");
  boardWidth = data.width;
  boardHeight = data.height;
  boardThickness = data.thickness;
  boardCenterX = data.centerX;
  boardCenterY = data.centerY;
  boardID = data.boardID;
  boardMaterial = data.material;
  $("#boardID").text("Board: "+boardID+", Material: "+boardMaterial);
  if (enable3D)
    board3DDataUpdate(data);
}

function moveAction(direction) {
  // JQuery returns list of matching forms so select first [0] for validitity checking.
  var isValid = $("#distInput")[0].checkValidity();
  if (isValid) {
    distance = $("#distToMove").val();
    action('move', direction, distance);
  }
}

function processStatusMessage(data){
    //console.log(data)
    if (data.uploadFlag){
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
