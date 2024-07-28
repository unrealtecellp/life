// edit button on dictionary view table
$(document).ready(function() {  
  
  $(".lexemeedit").click(function() {
    var headword = []
    var $row = $(this).closest("tr");    // Find the row
    var $text = $row.find("#lexemeId").text(); // Find the text
    headword.push($text)
    var $text = $row.find("#headword").text(); // Find the text
    headword.push($text)
    $.getJSON('/lifelexemes/lexemeedit', {
          a:String(headword)
    }, function(data) {
      localStorage.clear();
      localStorage.setItem("newDataeditlexeme", JSON.stringify(data.newData));
      localStorage.setItem("lexemeeditlexeme", JSON.stringify(data.result1));
      localStorage.setItem("fileneditlexeme", JSON.stringify(data.result2));
      window.location.href = window.location.href.replace("dictionaryview", "editlexeme");
        
    });
    return false;
  });
});