
var isMobile = false; //initiate as false

if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent)
  || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(navigator.userAgent.substr(0,4))) {
  isMobile = true;
}


function processControllerStatus(data){
    if (data.status=="disconnected"){
      $("#controllerStatus").text("Not Connected");
      $("#controllerStatus").removeClass('alert-success').removeClass('alert-secondary').addClass('alert-danger');
      $("#mobileControllerStatus").removeClass('alert-success').removeClass('alert-secondary').addClass('alert-danger');
    }
    else
    {
      $("#controllerStatus").text(data.port);
      $("#controllerStatus").removeClass('alert-danger').addClass('alert-success');
      $("#mobileControllerStatus").removeClass('alert-danger').addClass('alert-success');
    }
}

function processActivateModal(data){
    var $modal, $modalTitle, $modalText
    if (data.modalType == "content"){
      $modal = $('#contentModal');
      $modalDialog = $('#contentDialog');
      $modalTitle = $('#contentModalTitle');
      $modalText = $('#contentModalText');
      if (data.resume=='footerSubmit'){
        $('#footerSubmit').show();
      } else {
        $('#footerSubmit').hide();
      }
    }
    else if (data.modalType == "alarm") {
      $modal = $('#alarmModal');
      $modalDialog = $('#alarmDialog');
      $modalTitle = $('#alarmModalTitle');
      $modalText = $('#alarmModalText');
      if (data.resume=="clear"){
          $('#clearButton').show();
      } else {
          $('#clearButton').hide();
      }
    }
    else{
      $modal = $('#notificationModal');
      $modalDialog = $('#notificationDialog');
      $modalTitle = $('#notificationModalTitle');
      $modalText = $('#notificationModalText');
      if (data.resume=="resume"){
        $('#resumeButton').show();
      } else {
        $('#resumeButton').hide();
      }
      if (data.progress=="true"){
        $('#progressBarDiv').show();
      } else {
        $('#progressBarDiv').hide();
      }
      if (data.progress=="spinner"){
        $('#notificationCircle').show();
      } else {
        $('#notificationCircle').hide();
      }
    }
    $modalDialog.removeClass('modal-lg');
    $modalDialog.removeClass('modal-sm');
    $modalDialog.removeClass('mw-100 w-75');
    if (data.modalSize=="large"){
      if (isMobile)
        $modalDialog.addClass('modal-lg');
      else
        $modalDialog.addClass('mw-100 w-75');
    }
    if (data.modalSize=="medium")
      $modalDialog.addClass('modal-lg');
    if (data.modalSize=="small")
      $modalDialog.addClass('modal-sm');
    $modal.data('bs.modal',null);
    $modal.data('name',data.title);

    $modalTitle.html("<h3>"+data.title+"</h3");
    $modalText.html(JSON.parse(data.message));

    if (data.isStatic==true){
        console.log("Static Modal")
        $modal.modal({backdrop: 'static', keyboard: false})
    } else {
        $modal.modal();
    }
    $modalText.scrollTop(0);
}

function closeModals(data){
    if ($('#notificationModal').data('name') == data.title)
    {
      $('#notificationModal').modal('hide');
    }
}

function closeActionModals(data){
    if ($('#actionModal').data('name') == data.title)
    {
      $('#actionModal').modal('hide');
    }
}

function closeContentModals(data){
    if ($('#contentModal').data('name') == data.title)
    {
      $('#contentModal').modal('hide');
    }
};


function action(command, arg, arg1){
    if (arg==null)
      arg = "";
    if (arg1==null)
      arg1 = "";
    console.log("action="+command);
    socket.emit('action',{data:{command:command,arg:arg, arg1:arg1}});
}

function move(direction){
  distToMove = $("#distToMove").val();
  console.log(distToMove)
  socket.emit('move',{data:{direction:direction,distToMove:distToMove}});
}
function moveZ(direction){
  distToMoveZ = $("#distToMoveZ").val();
  console.log(distToMoveZ)
  socket.emit('moveZ',{data:{direction:direction,distToMoveZ:distToMoveZ}});
}

function settingRequest(section,setting){
  console.log("requesting..")
  socket.emit('settingRequest',{data:{section:section,setting:setting}});
}

function statusRequest(status){
  console.log("requesting status..")
  socket.emit('statusRequest',{data:{status:status}});
}

function requestPage(page, args=""){
  console.log("requesting page..")
  socket.emit('requestPage',{data:{page:page, isMobile:isMobile, args:args}});
}

function updateSetting(setting, value){
    socket.emit('updateSetting',{data:{setting:setting,value:value}});
}

function checkForGCodeUpdate(){
    socket.emit('checkForGCodeUpdate',{data:"Please"});
}

$.fn.scrollBottom = function() {
    return $(this).scrollTop($(this)[0].scrollHeight);
};


function setupStatusButtons(){
  if (isMobile){
      $('#mobileClientStatus').show();
      $('#mobileControllerStatus').show();
  } else {
    $('#mobileClientStatus').hide();
    $('#mobileControllerStatus').hide();
  }
}