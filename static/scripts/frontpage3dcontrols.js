// This is used only in frontpage3d_mobilecontrols.html

$(document).ready(function () {
  //settingRequest("Computed Settings","units");
  //settingRequest("Computed Settings","distToMove");
  //settingRequest("Computed Settings","homePosition");
  var controllerMessage = document.getElementById('controllerMessage');
  controllerMessage.scrollTop = controllerMessage.scrollHeight;

  window.isFrontpage3d_mobilecontrols = true;
});

function unsupported() {
  console.log("Unsupported");
}

function cursorPosition() {
  console.log("Unsupported");
}

