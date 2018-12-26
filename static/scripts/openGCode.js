
$('#gcCircle').hide();
var unselected = [];
var selectedDirectory = "{{lastSelectedDirectory}}"

$(document).ready(function () {
    refreshList();
    $("#directorySelect").change(refreshList);

    $('#gcodeForm').on('submit', function(e) {
        e.preventDefault();
        $('#gcCircle').show();
        var formdata = new FormData(this);

        $.ajax({
            url : '/openGCode',
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
    });
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
