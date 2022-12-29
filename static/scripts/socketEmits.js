// These all assume that there is a global value called 'socket'

function action(command, arg, arg1) {
  arg = arg || "";
  arg1 = arg1 || "";
  console.log(`action=${command}`);
  socket.emit('action', { data: { command: command, arg: arg, arg1: arg1 } });
}

function move(direction) {
  distToMove = $("#distToMove").val();
  console.log(distToMove)
  socket.emit('move', { data: { direction: direction, distToMove: distToMove } });
}

function moveZ(direction) {
  distToMoveZ = $("#distToMoveZ").val();
  console.log(distToMoveZ)
  socket.emit('moveZ', { data: { direction: direction, distToMoveZ: distToMoveZ } });
}

function settingRequest(section, setting) {
  console.log(`requesting setting ${setting} in ${section}`);
  socket.emit('settingRequest', { data: { section: section, setting: setting } });
}

// This is not exported
function statusRequest(status) {
  console.log("requesting status..")
  socket.emit('statusRequest', { data: { status: status } });
}

function requestPage(page, args = "") {
  console.log(`requesting page: ${page}`)
  socket.emit('requestPage', { data: { page: page, isMobile: isMobile, args: args } });
}

function updateSetting(setting, value) {
  console.log(`updating setting ${setting} to ${value}`);
  socket.emit('updateSetting', { data: { setting: setting, value: value } });
}

function checkForGCodeUpdate() {
  socket.emit('checkForGCodeUpdate', { data: "Please" });
}

function checkForBoardUpdate() {
  socket.emit('checkForBoardUpdate', { data: "Please" });
}

// function checkForHostAddress() {
//   socket.emit('checkForHostAddress', { data: "Please" });
// }

export { action, move, moveZ, settingRequest, requestPage, updateSetting, checkForGCodeUpdate, checkForBoardUpdate };