var socket
var alogMessages = [];
var logMessages = [];
var alogEnabled = true;
var logEnabled = true;

$(document).ready(function(){
  namespace = '/MaslowCNCLogs'; // change to an empty string to use the global namespace
  // the socket.io documentation recommends sending an explicit package upon connection
  // this is specially important when using the global namespace
  socket = io.connect('http://' + document.domain + ':' + location.port + namespace, {'forceNew':true});
  setListeners();

  $("#enablealog").change(function(){
    if ($(this).prop('checked'))
        alogEnabled=true;
    else
        alogEnabled=false;
  });

  $("#enablelog").change(function(){
    if ($(this).prop('checked'))
        logEnabled=true;
    else
        logEnabled=false;
  });


});

function setListeners(){
  console.log("setting Listeners");
  socket.on('connect', function(msg) {
      socket.emit('my event', {data: 'I\'m connected!'});
  });

  socket.on('disconnect', function(msg) {
  });

  socket.on('message', function(msg){
      switch(msg.log) {
        case 'alog':
            if (alogEnabled)
                processalog(msg.data);
            break;
        case 'log':
            if (logEnabled)
                processlog(msg.data);
            break;
        default:
            console.log("!!!!!!");
            console.log("uncaught action:"+msg.command);
            console.log("!!!!!!");
      }
  });
}

function processalog(data){
    if (alogMessages.length >100){
        alogMessages.shift();
        $('#alogMessages').get(0).firstChild.remove();
        $('#alogMessages').get(0).firstChild.remove();
    }
    alogMessages.push(data);

    $('#alogMessages').append(document.createTextNode(data));
    $('#alogMessages').append("<br>");
    $('#alogMessages').scrollBottom();
}

function processlog(data){

    if (logMessages.length >100){
        logMessages.shift();
        $('#logMessages').get(0).firstChild.remove();
        $('#logMessages').get(0).firstChild.remove();
    }
    logMessages.push(data);

    $('#logMessages').append(document.createTextNode(data));
    $('#logMessages').append("<br>");
    $('#logMessages').scrollBottom();
}

$.fn.scrollBottom = function() {
    return $(this).scrollTop($(this)[0].scrollHeight);
};
