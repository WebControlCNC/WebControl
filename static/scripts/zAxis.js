
function unitSwitchZ(){
  if ( $("#unitsZ").text()=="MM") {
    $("#unitsZ").text("INCHES");
    distToMoveZ = Math.round($("#distToMoveZ").val()/25.4,3)
    $("#distToMoveZ").val(distToMoveZ);
    updateSetting('toInchesZ',distToMoveZ);
  } else {
    $("#unitsZ").text("MM");
    distToMoveZ = Math.round($("#distToMoveZ").val()*25.4,3)
    $("#distToMoveZ").val(distToMoveZ);
    updateSetting('toMMZ',distToMoveZ);
  }
}

function processZAxisRequestedSetting(msg){
    if (msg.setting=="unitsZ"){
        console.log("requestedSetting:"+msg.value);
        $("#unitsZ").text(msg.value)
    }
    if (msg.setting=="distToMoveZ"){
        console.log("requestedSetting for distToMoveZ:"+msg.value);
        $("#distToMoveZ").val(msg.value)
    }
}

$(document).ready(function(){
    settingRequest("unitsZ");
    settingRequest("distToMoveZ");
});
