
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

function pwr2color(pwr) {
	var r, g, b = 0;

	if(pwr < 127) {
		g = 255;
		r = pwr*2;
	}
	else {
		r = 255;
		g = 255-(pwr-127)*2;
		if(pwr>240) {
		    g=0
		    b=(pwr-240)*16
		}
	}
	var h = r * 0x10000 + g * 0x100 + b * 0x1;
	return '#' + ('000000' + h.toString(16)).slice(-6);
}

function processPositionMessage(data){
  $('#positionMessage').html('X:'+parseFloat(data.xval).toFixed(2)+' Y:'+parseFloat(data.yval).toFixed(2)+' Z:'+parseFloat(data.zval).toFixed(2)+' V:'+parseFloat(data.vel).toFixed(2)+'/'+parseFloat(data.rqvel).toFixed(2));
  $('#percentComplete').html(data.pcom)
  $('#machineState').html(data.state)
  if (enable3D)
    positionUpdate(data.xval,data.yval,data.zval);

  $('#leftError').css('background-color', pwr2color(data.lpwr)).attr('title', data.lpwr);
  $('#rightError').css('background-color', pwr2color(data.rpwr)).attr('title', data.rpwr);
  $('#zError').css('background-color', pwr2color(data.zpwr)).attr('title', data.zpwr);
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
	distance = $("#distToMove").val();
	distanceValid = distance.search(/^[0-9]*(\.[0-9]{0,3})?$/);
	if (distanceValid == 0) {
		action('move', direction, distance);
	} else {
		$("#distToMove").focus();
	}
}

function processStatusMessage(data){
    //console.log(data)
    if (data.uploadFlag==1){
        if (isDisabled!=data.uploadFlag){
            $('.disabler').prop('disabled', true);
            $('.ndisabler').prop('disabled', false);
            $('.gcdisabler').prop('disabled', true);
            isDisabled =data.uploadFlag;
        }
    } else if (data.uploadFlag==2 || data.uploadFlag==-1 ){
        if (isDisabled!=data.uploadFlag){
            $('.gcdisabler').prop('disabled', true);
            $('.disabler').prop('disabled', false);
            $('.ndisabler').prop('disabled', false);
            isDisabled = data.uploadFlag;
            }
        }
    else {
        if (isDisabled!=data.uploadFlag){
            $('.disabler').prop('disabled', false);
            $('.ndisabler').prop('disabled', true);
            $('.gcdisabler').prop('disabled', false);
            isDisabled = data.uploadFlag;
        }
    }
    $("#currentTool").text(data.currentTool.toString());
    if (data.positioningMode == 0)
        $("#currentPositioningMode").text("Absolute (G90)");
    else
        $("#currentPositioningMode").text("Incremental (G91)");
}
