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
          $("#clientStatus").removeClass('alert-danger').addClass('alert-success');
          $("#mobileClientStatus").removeClass('alert-danger').addClass('alert-success');
          settingRequest("Computed Settings","units");
          settingRequest("Computed Settings","distToMove");
          settingRequest("Computed Settings","homePosition");
          checkForGCodeUpdate();
          checkForBoardUpdate();
      });

      socket.on('disconnect', function(msg) {
          $("#clientStatus").text("Not Connected");
          $("#clientStatus").removeClass('alert-success').addClass('alert-outline-danger');
          $("#mobileClientStatus").removeClass('alert-success').addClass('alert-danger');
          $("#controllerStatus").removeClass('alert-success').removeClass('alert-danger').addClass('alert-secondary');
          $("#mobileControllerStatus").removeClass('alert-success').removeClass('alert-danger').addClass('alert-secondary');

      });

      $("#notificationModal").on('hidden.bs.modal', function(e){
          var name = $('#notificationModal').data('name');
          socket.emit('modalClosed', {data:name});
      });

      $("#actionModal").on('hidden.bs.modal', function(e){
          var name = $('#actionModal').data('name');
          socket.emit('actionModalClosed', {data:name});
      });

      $("#contentModal").on('hidden.bs.modal', function(e){
          var name = $('#contentModal').data('name');
          console.log("closing modal:"+name);
          socket.emit('contentModalClosed', {data:name});
      });

      socket.on('message', function(msg){
          //blink activity indicator
          $("#cpuUsage").removeClass('alert-success').addClass('alert-warning');
          $("#mobileCPUUsage").removeClass('alert-success').addClass('alert-warning');
          setTimeout(function(){
            $("#cpuUsage").removeClass('alert-warning').addClass('alert-success');
            $("#mobileCPUUsage").removeClass('alert-warning').addClass('alert-success');
          },125);
          //#console.log(msg.dataFormat);
          if (msg.dataFormat=='json')
            data = JSON.parse(msg.data);
          else
            data = msg.data;
          //console.log(msg.command);
          switch(msg.command) {
            case 'healthMessage':
                //completed
                processHealthMessage(data);
                break;
            case 'controllerMessage':
                //completed
                processControllerMessage(data);
                break;
            case 'connectionStatus':
                //completed
                processControllerStatus(data);
                break;
            case 'calibrationMessage':
                processCalibrationMessage(data);
                break;
            case 'cameraMessage':
                //completed
                processCameraMessage(data);
                break;
            case 'positionMessage':
                //completed
                processPositionMessage(data)
                if (typeof processPositionMessageOptical === "function") {
                     processPositionMessageOptical(data)
                }
                break;
            case 'errorValueMessage':
                processErrorValueMessage(data)
                break;
            case 'homePositionMessage':
                //completed
                processHomePositionMessage(data);
                break;
            case 'gcodePositionMessage':
                //completed
                processGCodePositionMessage(data);
                break;
            case 'activateModal':
                //completed
                console.log(msg)
                processActivateModal(data);
                break;
            case 'requestedSetting':
                //completed
                processRequestedSetting(data);
                break;
            case 'updateDirectories':
                //completed
                updateDirectories(data);
                break;
            case 'gcodeUpdate':
                gcodeUpdate(msg.message);
                break;
            case 'showFPSpinner':
                //completed
                showFPSpinner(msg.message);
                break;
            case 'gcodeUpdateCompressed':
                gcodeUpdateCompressed(data);
                break;
            case 'boardDataUpdate':
                boardDataUpdate(data);
                break;
            case 'boardCutDataUpdateCompressed':
                boardCutDataUpdateCompressed(data);
                break;
            case 'updatePorts':
                //completed
                if (typeof updatePorts === "function") {
                    updatePorts(data);
                }
                break;
            case 'closeModals':
                //completed
                closeModals(data);
                break;
            case 'closeActionModals':
                //completed
                closeActionModals(data);
                break;
            case 'closeContentModals':
                //completed
                closeContentModals(data);
                break;
            case 'updateOpticalCalibrationCurve':
                //completed
                updateOpticalCalibrationCurve(data);
                break;
            case 'updateOpticalCalibrationError':
                //completed
                updateOpticalCalibrationError(data);
                break;
            case 'updateOpticalCalibrationFindCenter':
                //completed
                updateOpticalCalibrationFindCenter(data);
                break;
            case 'updateCalibrationImage':
                //completed
                updateCalibrationImage(data);
                break;
            case 'updatePIDData':
                //completed
                updatePIDData(data);
                break;
            case 'alarm':
                processAlarm(data);
                break;
            case 'clearAlarm':
                clearAlarm(data);
                break;
            default:
                console.log("!!!!!!");
                console.log("uncaught action:"+msg.command);
                console.log("!!!!!!");
          }
      });

        /*
      socket.on('gcodeUpdate', function(msg){
        console.log("gcodeUpdate Message Received")
        gcodeUpdate(msg);
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
        console.log("oldControllerStatus")
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
        */

      /*socket.on('positionMessage', function(msg){
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
        console.log("oldRequestedSetting"+msg.toString());

        processRequestedSetting(msg);
      });


      socket.on('updateDirectories', function(msg){
        console.log("oldUpdateDirectories")
        updateDirectories(msg);
      });
        */
    /*
      socket.on('showFPSpinner', function(msg){
        console.log("oldshowFPSpinner")
        showFPSpinner(msg);
      });


      socket.on('gcodeUpdateCompressed', function(msg){
        console.log("old gcodeUpdate Compressed Message Received")
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
        console.log("oldcloseModals")
        console.log("received notice to close: "+msg.data.title);
        console.log("active modal has name: "+$("#notificationModal").data('name'));
        if ($('#notificationModal').data('name') == msg.data.title)
        {
          console.log("closeModal")
          $('#notificationModal').modal('hide');
         }
      });

      socket.on('closeActionModals', function(msg){
        console.log("oldcloseActionModals")
        if ($('#actionModal').data('name') == msg.data.title)
        {
          $('#actionModal').modal('hide');
         }
      });

      socket.on('closeContentModals', function(msg){
        console.log("oldcloseContentModals")
        if ($('#contentModal').data('name') == msg.data.title)
        {
          $('#contentModal').modal('hide');
         }
      });


      socket.on('cameraMessage', function(msg){
          processCameraMessage(msg)
      });

     socket.on('calibrationMessage', function(msg){
          processCalibrationMessage(msg)
      });



    */

  }
