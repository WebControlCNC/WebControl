import "jquery";

import { checkForGCodeUpdate } from "./socketEmits.js";

$('#gcCircle').hide();
var unselected = [];
var selectedDirectory = "{{lastSelectedDirectory}}"

$(() => {
    // document.ready
    refreshList();
    $("#directorySelect").change(refreshList);
});

function refreshList(){
  unselected.forEach(element => {
      $("#fileSelect").append(element)
  });
  unselected = [];
  selectedDirectory = $("#directorySelect").val();
  if (selectedDirectory[selectedDirectory.length-1]=="/")
      selectedDirectory = selectedDirectory.slice(0,-1)
  $("#fileSelect > option").each(function() {
      var splits = $(this).val().split("/");
      if (splits[0]!=selectedDirectory){
        unselected.push($(this))
        $(this).remove();
      }
  });
}

function onFooterSubmit(){
    //var formdata = $("#gcodeForm").serialize();
    $('#gcCircle').show();
    var formdata = new FormData($('#gcodeForm')[0]);

    $.ajax({
        url : '/saveGCode',
        type: "POST",
        data: formdata,
        mimeTypes:"multipart/form-data",
        contentType: false,
        cache: false,
        processData: false,
        success: function (data) {
          console.log("success");
            $('#contentModal').modal('toggle')
            checkForGCodeUpdate();
            $('#gcCircle').hide();
        },
        error: function (jXHR, textStatus, errorThrown) {
            alert(errorThrown);
            $('#gcCircle').hide();
        }
    });
}

export { onFooterSubmit };
