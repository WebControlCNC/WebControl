import { settingRequest } from "./socketEmits.js";

export function processZAxisRequestedSetting(msg) {
  if (msg.setting == "unitsZ") {
    console.log("requestedSetting:" + msg.value);
    $("#unitsZ").text(msg.value)
  }
  if (msg.setting == "distToMoveZ") {
    console.log("requestedSetting for distToMoveZ:" + msg.value);
    $("#distToMoveZ").val(msg.value)
  }
}
