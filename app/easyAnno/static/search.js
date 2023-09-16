$(document).ready(function(){
    $("#searchFile").on("keyup", function() {
      var value = $(this).val().toLowerCase();
      $("#allFilesTableBody tr").filter(function() {
        $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
      });
    });
  });
  