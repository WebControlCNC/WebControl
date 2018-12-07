function updateDirectories(data){
   var directory = data.directory;
   console.log(directory);
   $("#directorySelect").append($("<option></option>").attr("value",directory).text(directory));
   $("#directorySelect option[value="+directory+"]").prop('selected', 'selected');
   $("#newDirectory").val("");
}

$(document).ready(function () {
    $('#newDirectoryButton').on('click',function(){ //bind click handler
        event.preventDefault();
        directory=$("#newDirectory").val();
        if (directory!="")
            action("createDirectory",directory);
     });

    $('#gcodeForm').on('submit', function(e) {
        e.preventDefault();

        var formdata = new FormData(this);

        $.ajax({
            url : '/uploadGCode',
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
            },
            error: function (jXHR, textStatus, errorThrown) {
                alert(errorThrown);
            }
        });
    });
});
