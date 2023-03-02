import "jquery";

$(document).ready(function () {
  var controllerMessage = document.getElementById('controllerMessage');
  controllerMessage.scrollTop = controllerMessage.scrollHeight;
  
  window.isFrontpage3d_mobilecontrols = false;

  $("#stickyButtons").css("top", $(".navbar").outerHeight());
});
