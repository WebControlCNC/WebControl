function unitSwitch(){
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

function setSprocketsZero(){
    action('setSprocketsZero');$("input").prop('disabled', false);
    $("#leftChainDefault").prop('disabled',false);
    $("#rightChainDefault").prop('disabled',false);
}

function disableChainToDefault()
{
    $("#leftChainDefault").prop('disabled',true);
    $("#rightChainDefault").prop('disabled',true);
}

function processCalibrationMessage(msg)
{
    data = msg.data.split(":");
    if(data[0]=="left")
    {
        if (data[1]!="0"){
            $("#leftChainDefault").text(data[1]+"...");
        } else {
            $("#leftChainDefault").text("Left Chain To Default");
        }
    }
    if(data[0]=="right")
    {
        if (data[1]!="0"){
            $("#rightChainDefault").text(data[1]+"...");
        } else {
            $("#rightChainDefault").text("Right Chain To Default");
        }
    }

}