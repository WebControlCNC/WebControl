import { io } from "../node_modules/socket.io-client/dist/socket.io.esm.min.js";

window.logSocket;
window.alogMessages = [];
window.logMessages = [];
window.alogEnabled = true;
window.logEnabled = true;
window.loggingState = false;

$(document).ready(function () {
  const namespace = "/MaslowCNCLogs"; // change to an empty string to use the global namespace
  // the socket.io documentation recommends sending an explicit package upon connection
  // this is specially important when using the global namespace
  const serverURL = `//${location.hostname}:${location.port}${namespace}`;
  window.logSocket = io.connect(serverURL);
  setListeners();

  $("#enablealog").change(() => {
    window.alogEnabled = $(this).prop('checked');
  });

  $("#enablelog").change(() => {
    window.logEnabled = $(this).prop('checked');
  });
});

function setListeners() {
  console.log("setting Listeners");
  window.logSocket.on('connect', () => {
    window.logSocket.emit('my event', { data: 'I\'m connected!' });
  });

  window.logSocket.on('disconnect', (msg) => {
  });

  window.logSocket.on('message', (msg) => {
    switch (msg.log) {
      case 'alog':
        if (window.alogEnabled) {
          processalog(msg.data);
        }
        processLoggingState(msg.state);
        break;
      case 'log':
        if (window.logEnabled) {
          processlog(msg.data);
        }
        processLoggingState(msg.state);
        break;
      case 'state':
        if (window.loggingState != msg.state) {
          processLoggingState(msg.state);
          break;
        }

      default:
        console.log("!!!!!!");
        console.log("uncaught action:" + msg.command);
        console.log("!!!!!!");
    }
  });
}

function processalog(data) {
  if (window.alogMessages.length > 1000) {
    window.alogMessages.shift();
    $('#alogMessages').get(0).firstChild.remove();
    $('#alogMessages').get(0).firstChild.remove();
  }
  window.alogMessages.push(data);

  $('#alogMessages').append(document.createTextNode(data));
  $('#alogMessages').append("<br>");
  $('#alogMessages').scrollBottom();
}

function processlog(data) {
  if (window.logMessages.length > 1000) {
    window.logMessages.shift();
    $('#logMessages').get(0).firstChild.remove();
    $('#logMessages').get(0).firstChild.remove();
  }
  window.logMessages.push(data);

  $('#logMessages').append(document.createTextNode(data));
  $('#logMessages').append("<br>");
  $('#logMessages').scrollBottom();
}

function processLoggingState(data) {
  if (data) {
    $("#loggingState").text("Logging Suspended");
    $("#loggingState").removeClass('alert-success').addClass('alert-secondary');
  }
  else {
    $("#loggingState").text("Logging Active");
    $("#loggingState").removeClass('alert-secondary').addClass('alert-success');
  }
}

$.fn.scrollBottom = function () {
  return $(this).scrollTop($(this)[0].scrollHeight);
};
