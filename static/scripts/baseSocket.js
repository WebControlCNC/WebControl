  var socket
  var controllerMessages = [];
  $(document).ready(function(){
      namespace = '/MaslowCNC'; // change to an empty string to use the global namespace
      // the socket.io documentation recommends sending an explicit package upon connection
      // this is specially important when using the global namespace
      socket = io.connect('http://' + document.domain + ':' + location.port + namespace, {'forceNew':true});
      setListeners();
      setupStatusButtons();
  });

  function setListeners(){
      console.log("setting Listeners");
      socket.on('connect', function(msg) {
          socket.emit('my event', {data: 'I\'m connected!'});
          $("#clientStatus").text("Connected");
          $("#clientStatus").removeClass('btn-outline-danger').addClass('btn-success');
          $("#mobileClientStatus").removeClass('btn-outline-danger').addClass('btn-success');
          //checkForGCodeUpdate(); // don't think this is needed here anymore.. called by frontpage.js
      });

      socket.on('disconnect', function(msg) {
          $("#clientStatus").text("Not Connected");
          $("#clientStatus").removeClass('btn-success').addClass('btn-outline-danger');
          $("#mobileClientStatus").removeClass('btn-success').addClass('btn-outline-danger');
          $("#controllerStatus").removeClass('btn-success').removeClass('btn-outine-danger').addClass('btn-secondary');
          $("#mobileControllerStatus").removeClass('btn-success').removeClass('btn-outine-danger').addClass('btn-secondary');

      });

      socket.on('message', function(msg){
          //console.log(msg);
          switch(msg.command) {
            case 'controllerMessage':
                processControllerMessage(msg.message);
                break;
            case 'controllerStatus':
                processControllerStatus(msg.message);
                break;
            case 'calibrationMessage':
                processCalibrationMessage(msg.message);
                break;
            case 'cameraMessage':
                processCameraMessage(msg.message);
                break;
            case 'positionMessage':
                processPositionMessage(msg.message)
                if (typeof processPositionMessageOptical === "function") {
                     processPositionMessageOptical(msg.message)
                }
                break;
            case 'homePositionMessage':
                processHomePositionMessage(msg.message);
                break;
            case 'gcodePositionMessage':
                processGCodePositionMessage(msg.message);
                break;
            case 'activateModal':
                processActivateModal(msg.message);
                break;
            case 'requestedSetting':
                processRequestedSetting(msg.message);
                break;
            case 'updateDirectories':
                updateDirectories(msg.message);
                break;
            case 'gcodeUpdate':
                gcodeUpdate(msg.message);
                break;
            case 'showFPSpinner':
                showFPSpinner(msg.message);
                break;
            case 'gcodeUpdateCompressed':
                gcodeUpdateCompressed(msg.message);
                break;
            case 'updatePorts':
                updatePorts(msg.message);
                break;
            case 'closeModals':
                closeModals(msg.message);
                break;
            case 'closeActionModals':
                closeActionModals(msg.message);
                break;
            case 'closeContentModals':
                closeActionModals(msg.message);
                break;
          }
      });

      socket.on('controllerMessage', function(msg){
          if (controllerMessages.length >100)
            controllerMessages.shift();
          controllerMessages.push(msg.data);
          $('#controllerMessage').html('');
          controllerMessages.forEach(function(message){
            $('#controllerMessage').append(message+"<br>");
          });
          $('#controllerMessage').scrollBottom();
      });


      socket.on('controllerStatus', function(msg){
        msg = JSON.parse(msg);
        console.log(msg.status);
        if (msg.status=="disconnected"){
          $("#controllerStatus").text("Not Connected");
          $("#controllerStatus").removeClass('btn-success').removeClass('btn-secondary').addClass('btn-outline-danger');
          $("#mobileControllerStatus").removeClass('btn-success').removeClass('btn-secondary').addClass('btn-outline-danger');
        }
        else
        {
          $("#controllerStatus").text(msg.port);
          $("#controllerStatus").removeClass('btn-outline-danger').addClass('btn-success');
          $("#mobileControllerStatus").removeClass('btn-outline-danger').addClass('btn-success');
        }
      });

      socket.on('calibrationMessage', function(msg){
          processCalibrationMessage(msg)
      });

      socket.on('cameraMessage', function(msg){
          processCameraMessage(msg)
      });

      socket.on('positionMessage', function(msg){
          processPositionMessage(msg)
          if (typeof processPositionMessageOptical === "function") {
               processPositionMessageOptical(msg)
          }
      });

      socket.on('homePositionMessage', function(msg){
          processHomePositionMessage(msg)
      });

      socket.on('gcodePositionMessage', function(msg){
          //console.log(msg);
          processGCodePositionMessage(msg)
      });


      socket.on('activateModal', function(msg){
        console.log("modal size requested="+msg.modalSize)
        console.log("modal type ="+msg.modalType);
        var $modal, $modalTitle, $modalText
        if (msg.modalType == "content"){
          $modal = $('#contentModal');
          $modalDialog = $('#contentDialog');
          $modalTitle = $('#contentModalTitle');
          $modalText = $('#contentModalText');
        }
        else if (msg.modalType == "alarm") {
          $modal = $('#alarmModal');
          $modalDialog = $('#alarmDialog');
          $modalTitle = $('#alarmModalTitle');
          $modalText = $('#alarmModalText');
          if (msg.resume=="clear"){
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
          if (msg.resume=="resume"){
            $('#resumeButton').show();
          } else {
            $('#resumeButton').hide();
          }
          if (msg.progress=="true"){
            $('#progressBarDiv').show();
          } else {
            $('#progressBarDiv').hide();
          }
          if (msg.progress=="spinner"){
            $('#notificationCircle').show();
          } else {
            $('#notificationCircle').hide();
          }

        }
        $modalDialog.removeClass('modal-lg');
        $modalDialog.removeClass('modal-sm');
        $modalDialog.removeClass('mw-100 w-75');
        if (msg.modalSize=="large"){
          if (isMobile)
            $modalDialog.addClass('modal-lg');
          else
            $modalDialog.addClass('mw-100 w-75');
        }
        if (msg.modalSize=="medium")
          $modalDialog.addClass('modal-lg');
        if (msg.modalSize=="small")
          $modalDialog.addClass('modal-sm');
        $modal.data('bs.modal',null);
        $modal.data('name',msg.title);

        $modalTitle.html("<h3>"+msg.title+"</h3");
        $modalText.html("<p>"+msg.message+"</p>");
        console.log(msg.resume)

        if (msg.isStatic==true){
            console.log("Static Modal")
            $modal.modal({backdrop: 'static', keyboard: false})
        } else {
            $modal.modal();
        }
        $modalText.scrollTop(0);
      });



      socket.on('requestedSetting', function(msg){
        processRequestedSetting(msg);
      });

      socket.on('updateDirectories', function(msg){
        updateDirectories(msg);
      });

      socket.on('gcodeUpdate', function(msg){
        console.log("gcodeUpdate Message Received")
        gcodeUpdate(msg);
      });

      socket.on('showFPSpinner', function(msg){
        console.log("showFPSpinner")
        showFPSpinner(msg);
      });


      socket.on('gcodeUpdateCompressed', function(msg){
        console.log("gcodeUpdate Compressed Message Received")
        gcodeUpdateCompressed(msg);
      });

      socket.on('updatePorts', function(msg){
        if (typeof updatePorts === "function") {
            updatePorts(msg);
        } else {
            console.log("updatePorts not found");
        }
      });

      socket.on('closeModals', function(msg){
        console.log("received notice to close: "+msg.data.title);
        console.log("active modal has name: "+$("#notificationModal").data('name'));
        if ($('#notificationModal').data('name') == msg.data.title)
        {
          console.log("closeModal")
          $('#notificationModal').modal('hide');
         }
      });

      socket.on('closeActionModals', function(msg){
        if ($('#actionModal').data('name') == msg.data.title)
        {
          $('#actionModal').modal('hide');
         }
      });

      socket.on('closeContentModals', function(msg){
        if ($('#contentModal').data('name') == msg.data.title)
        {
          $('#contentModal').modal('hide');
         }
      });


      $("#notificationModal").on('hidden.bs.modal', function(e){
          var name = $('#notificationModal').data('name');
          //console.log("modal "+name+" is closing");
          socket.emit('modalClosed', {data:name});
      });

      $("#actionModal").on('hidden.bs.modal', function(e){
          var name = $('#actionModal').data('name');
          //console.log("action modal "+name+" is closing");
          socket.emit('actionModalClosed', {data:name});
      });

      $("#contentModal").on('hidden.bs.modal', function(e){
          var name = $('#contentModal').data('name');
          console.log("content modal "+name+" is closing");
          socket.emit('contentModalClosed', {data:name});
      });
  }
