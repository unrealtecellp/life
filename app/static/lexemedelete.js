$(document).ready(function() {  
  
  $(".lexemedelete").click(function() {
    var headword = []
    var $row = $(this).closest("tr");    // Find the row
    var $text = $row.find("#lexemeId").text(); // Find the text
    headword.push($text)
    var $text = $row.find("#headword").text(); // Find the text
    headword.push($text)
    $.getJSON('/lexemedelete', {
          a:String(headword)
    }, function(data) {
        // alert(data.msg);
        window.location.reload();
    });
    return false; 
  });
  });