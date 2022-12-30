// These all assume that there is a global value called 'socket'

function action(command, arg, arg1) {
  arg = arg || "";
  arg1 = arg1 || "";
  console.log(`action=${command}`);
  window.socket.emit('action', { data: { command: command, arg: arg, arg1: arg1 } });
}

function move(direction) {
  window.distToMove = $("#distToMove").val();
  console.log(window.distToMove)
  window.socket.emit('move', { data: { direction: direction, distToMove: window.distToMove } });
}

function moveZ(direction) {
  window.distToMoveZ = $("#distToMoveZ").val();
  console.log(window.distToMoveZ)
  window.socket.emit('moveZ', { data: { direction: direction, distToMoveZ: window.distToMoveZ } });
}

function settingRequest(section, setting) {
  console.log(`requesting setting ${setting} in ${section}`);
  window.socket.emit('settingRequest', { data: { section: section, setting: setting } });
}

// This is not exported
function statusRequest(status) {
  console.log("requesting status..")
  window.socket.emit('statusRequest', { data: { status: status } });
}

function requestPage(page, args = "") {
  console.log(`requesting page: ${page}`)
  window.socket.emit('requestPage', { data: { page: page, isMobile: window.isMobile, args: args } });
}

function updateSetting(setting, value) {
  console.log(`updating setting ${setting} to ${value}`);
  window.socket.emit('updateSetting', { data: { setting: setting, value: value } });
}

function checkForGCodeUpdate() {
  window.socket.emit('checkForGCodeUpdate', { data: "Please" });
}

function checkForBoardUpdate() {
  window.socket.emit('checkForBoardUpdate', { data: "Please" });
}

// function checkForHostAddress() {
//   window.socket.emit('checkForHostAddress', { data: "Please" });
// }

export { action, move, moveZ, settingRequest, requestPage, updateSetting, checkForGCodeUpdate, checkForBoardUpdate };