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
