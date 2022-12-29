import { updateSetting } from "./socketEmits.js";

export function unitSwitchZ() {
  if ($("#unitsZ").text() == "MM") {
    $("#unitsZ").text("INCHES");
    distToMoveZ = (parseFloat($("#distToMoveZ").val()) / 25.4).toFixed(2);
    //$("#distToMoveZ").val(distToMoveZ);
    updateSetting('toInchesZ', distToMoveZ);
  } else {
    $("#unitsZ").text("MM");
    distToMoveZ = (parseFloat($("#distToMoveZ").val()) * 25.4).toFixed(2);
    //$("#distToMoveZ").val(distToMoveZ);
    updateSetting('toMMZ', distToMoveZ);
  }
}
