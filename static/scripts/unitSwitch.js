import { updateSetting } from "./socketEmits.js";

export function unitSwitch() {
  if ($("#units").text() == "MM") {
    window.distToMove = (parseFloat($("#distToMove").val()) / 25.4).toFixed(3)
    updateSetting('toInches', window.distToMove);
  } else {
    window.distToMove = (parseFloat($("#distToMove").val()) * 25.4).toFixed(3)
    updateSetting('toMM', window.distToMove);
  }
}

export function unitSwitchZ() {
  if ($("#unitsZ").text() == "MM") {
    $("#unitsZ").text("INCHES");
    window.distToMoveZ = (parseFloat($("#distToMoveZ").val()) / 25.4).toFixed(2);
    //$("#distToMoveZ").val(window.distToMoveZ);
    updateSetting('toInchesZ', window.distToMoveZ);
  } else {
    $("#unitsZ").text("MM");
    window.distToMoveZ = (parseFloat($("#distToMoveZ").val()) * 25.4).toFixed(2);
    //$("#distToMoveZ").val(window.distToMoveZ);
    updateSetting('toMMZ', window.distToMoveZ);
  }
}
