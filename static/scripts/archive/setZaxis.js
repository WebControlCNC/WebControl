import "jquery";

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

function unitSwitchZ(){
    if ( $("#unitsZ").text()=="MM") {
      $("#unitsZ").text("INCHES");
      distToMoveZ = (parseFloat($("#distToMoveZ").val())/25.4).toFixed(2);
      //$("#distToMoveZ").val(distToMoveZ);
      updateSetting('toInchesZ',distToMoveZ);
    } else {
      $("#unitsZ").text("MM");
      distToMoveZ = (parseFloat($("#distToMoveZ").val())*25.4).toFixed(2);
      //$("#distToMoveZ").val(distToMoveZ);
      updateSetting('toMMZ',distToMoveZ);
    }
}

$(() => {
    // document.ready
    settingRequest("Computed Settings","unitsZ");
    settingRequest("Computed Settings","distToMoveZ");
});