import { io } from "../node_modules/socket.io-client/dist/socket.io.esm.min.js";

let logSocket;
var alogMessages = [];
var logMessages = [];
var alogEnabled = true;
var logEnabled = true;
var loggingState = false;

$(document).ready(function () {
  const namespace = "/MaslowCNCLogs"; // change to an empty string to use the global namespace
  // the socket.io documentation recommends sending an explicit package upon connection
  // this is specially important when using the global namespace
  const serverURL = `//${location.hostname}:${location.port}${namespace}`;
  logSocket = io.connect(serverURL, { 'forceNew': true });
  setListeners();

  $("#enablealog").change(function () {
    if ($(this).prop('checked'))
      alogEnabled = true;
    else
      alogEnabled = false;
  });

  $("#enablelog").change(function () {
    if ($(this).prop('checked'))
      logEnabled = true;
    else
      logEnabled = false;
  });
});

function setListeners() {
  console.log("setting Listeners");
  logSocket.on('connect', function (msg) {
    logSocket.emit('my event', { data: 'I\'m connected!' });
  });

  logSocket.on('disconnect', function (msg) {
  });

  logSocket.on('message', function (msg) {
    switch (msg.log) {
      case 'alog':
        if (alogEnabled)
          processalog(msg.data);
        processLoggingState(msg.state);
        break;
      case 'log':
        if (logEnabled)
          processlog(msg.data);
        processLoggingState(msg.state);
        break;
      case 'state':
        if (loggingState != msg.state) {
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
  if (alogMessages.length > 1000) {
    alogMessages.shift();
    $('#alogMessages').get(0).firstChild.remove();
    $('#alogMessages').get(0).firstChild.remove();
  }
  alogMessages.push(data);

  $('#alogMessages').append(document.createTextNode(data));
  $('#alogMessages').append("<br>");
  $('#alogMessages').scrollBottom();
}

function processlog(data) {

  if (logMessages.length > 1000) {
    logMessages.shift();
    $('#logMessages').get(0).firstChild.remove();
    $('#logMessages').get(0).firstChild.remove();
  }
  logMessages.push(data);

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
