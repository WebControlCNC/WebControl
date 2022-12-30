import { action } from "./socketEmits.js";

function onFooterSubmit(){
    var url = $("#pageID").val()
    $.ajax({
        url : '/'+url,
        type: "POST",
        data: $("#settingsForm").serialize(),
        success: function (data) {
          console.log("success");
            $('#contentModal').modal('toggle')
        },
        error: function (jXHR, textStatus, errorThrown) {
            alert(errorThrown);
        }
    });
}

$(document).ready(function () {
    $('#settingsForm').on('submit', function(e) {
        e.preventDefault();
        var url = $("#pageID").val()
        $.ajax({
            url : '/'+url,
            type: "POST",
            data: $(this).serialize(),
            success: function (data) {
              console.log("success");
                $('#contentModal').modal('toggle')
            },
            error: function (jXHR, textStatus, errorThrown) {
                alert(errorThrown);
            }
        });
    });

    $('#updateListofPorts').on('click',function(){ //bind click handler
        event.preventDefault();
        action('updatePorts');
     });

});

function updatePorts(data){
  var selectedPort = $("#comPorts").find(":selected").text();
  if ($("#comPorts").length){
    $("#comPorts").empty()
    data.forEach(function(port){
       var option = "";
       if (port==selectedPort){
          option = "<option value='"+port+"' 'selected'>"+port+"</option>";
       }
       else {
          option = "<option value='"+port+"' >"+port+"</option>";
       }
       $("#comPorts").append(option);
    });
  }
}

export { updatePorts };