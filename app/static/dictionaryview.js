function GetSelected() {
    
    //Reference the Table.
    var grid = document.getElementById("myTable");
    
    //Reference the CheckBoxes in Table.
    var checkBoxes = grid.getElementsByTagName("INPUT");
    
    // var checkedlexemes = [];
    var checkedlexemes = {};
    //Loop through the CheckBoxes.
    for (var i = 1; i < checkBoxes.length; i++) {
        
        if (checkBoxes[i].type == 'checkbox' && checkBoxes[i].checked == true) {
            var row = checkBoxes[i].parentNode.parentNode;
            // checkedlexemes.push(row.cells[1].innerHTML);
            key = row.cells[1].innerHTML
            value = row.cells[2].innerHTML
            checkedlexemes[key] = value
            // message += "   " + row.cells[2].innerHTML;
            // message += "   " + row.cells[3].innerHTML;
            // message += "\n";
            
        }
    }

    //Display selected Row data in Alert Box.
    // console.log(checkedlexemes);
    // checkedlexemesajax(checkedlexemes);
    return checkedlexemes;
}

function checkAllLexeme(ele) {
    // checked true or false when checkbox in table header is clicked
    var checkboxes = document.getElementsByTagName('input');
    if (ele.checked) {
        for (var i = 0; i < checkboxes.length; i++) {
            if (checkboxes[i].type == 'checkbox') {
                checkboxes[i].checked = true;
            }
        }
    } else {
        for (var i = 0; i < checkboxes.length; i++) {
            console.log(i)
            if (checkboxes[i].type == 'checkbox') {
                checkboxes[i].checked = false;
            }
        }
    }
}

function checkLexeme(ele) {
    // checkbox in table header true or false when any checkbox of table body is true or false
    var checkboxcount = 0;
    var headcheckbox = document.getElementById('headcheckbox');
    var checkboxes = document.getElementsByTagName('input');
    var totalrecords = document.getElementById('totalrecords').innerHTML;
    totalrecordscount = totalrecords.match(/\d/);
    // alert(totalrecordscount);
    if (ele.checked == false) {
        headcheckbox.checked = false;
    }
    else {
        for (var i = 1; i < checkboxes.length; i++) {
            if (checkboxes[i].type == 'checkbox' && checkboxes[i].checked == true) {
                checkboxcount += 1
            }
        }
        if (checkboxcount == totalrecordscount) {
            headcheckbox.checked = true;
        }
    }
}

$(document).ready(function() {  
    $(".multipledelete").click(function() {
      lexemes = GetSelected()
      $.ajax({
            url: '/deletemultiplelexemes',
            type: 'GET',
            data: {'data': JSON.stringify(lexemes)},
            contentType: "application/json; charset=utf-8", 
            success: function(response){
                window.location.reload();
            }
        });
      return false; 
    });
});

$(document).ready(function() {  
    $(".json").click(function() {
      lexemes = GetSelected()
      lexemes['downloadFormat'] = "json";
      console.log(lexemes)
      $.ajax({
            url: '/downloadselectedlexeme',
            type: 'GET',
            data: {'data': JSON.stringify(lexemes)},
            contentType: "application/json; charset=utf-8", 
            success: function(response){
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("dictionaryview", "downloadjson");
                // window.location.reload();
                // console.info(response);
            }
        });
      return false; 
    });
});

$(document).ready(function() {  
    $(".csv").click(function() {
      lexemes = GetSelected()
      lexemes['downloadFormat'] = "csv";
      $.ajax({
            url: '/downloadselectedlexeme',
            type: 'GET',
            data: {'data': JSON.stringify(lexemes)},
            contentType: "application/json; charset=utf-8", 
            success: function(response){
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("dictionaryview", "downloadjson");
                // window.location.reload();
                // console.info(response);
            }
        });
      return false; 
    });
});

$(document).ready(function() {  
    $(".xlsx").click(function() {
      lexemes = GetSelected()
      lexemes['downloadFormat'] = "xlsx";
      $.ajax({
            url: '/downloadselectedlexeme',
            type: 'GET',
            data: {'data': JSON.stringify(lexemes)},
            contentType: "application/json; charset=utf-8", 
            success: function(response){
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("dictionaryview", "downloadjson");
                // window.location.reload();
                // console.info(response);
            }
        });
      return false; 
    });
});

$(document).ready(function() {  
    $(".pdf").click(function() {
      lexemes = GetSelected()
      lexemes['downloadFormat'] = "pdf";
      $.ajax({
            url: '/downloadselectedlexeme',
            type: 'GET',
            data: {'data': JSON.stringify(lexemes)},
            contentType: "application/json; charset=utf-8", 
            success: function(response){
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("dictionaryview", "downloadjson");
                // window.location.reload();
                // console.info(response);
            }
        });
      return false; 
    });
});

$(document).ready(function() {  
    $(".markdown").click(function() {
      lexemes = GetSelected()
      lexemes['downloadFormat'] = "markdown";
      $.ajax({
            url: '/downloadselectedlexeme',
            type: 'GET',
            data: {'data': JSON.stringify(lexemes)},
            contentType: "application/json; charset=utf-8", 
            success: function(response){
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("dictionaryview", "downloadjson");
                // window.location.reload();
                // console.info(response);
            }
        });
      return false; 
    });
});

$(document).ready(function() {  
    $(".latex").click(function() {
      lexemes = GetSelected()
    //   lexemes['downloadFormat'] = "latex";
      lexemes['downloadFormat'] = "latex_dict";
      $.ajax({
            url: '/downloadselectedlexeme',
            type: 'GET',
            data: {'data': JSON.stringify(lexemes)},
            contentType: "application/json; charset=utf-8", 
            success: function(response){
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("dictionaryview", "downloadjson");
                // window.location.reload();
                // console.info(response);
            }
        });
      return false; 
    });
});

$(document).ready(function() {  
    $(".html").click(function() {
      lexemes = GetSelected()
      lexemes['downloadFormat'] = "html";
      $.ajax({
            url: '/downloadselectedlexeme',
            type: 'GET',
            data: {'data': JSON.stringify(lexemes)},
            contentType: "application/json; charset=utf-8", 
            success: function(response){
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("dictionaryview", "downloadjson");
                // window.location.reload();
                // console.info(response);
            }
        });
      return false; 
    });
});

$(document).ready(function() {  
    $(".ods").click(function() {
      lexemes = GetSelected()
      lexemes['downloadFormat'] = "ods";
      $.ajax({
            url: '/downloadselectedlexeme',
            type: 'GET',
            data: {'data': JSON.stringify(lexemes)},
            contentType: "application/json; charset=utf-8", 
            success: function(response){
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("dictionaryview", "downloadjson");
                // window.location.reload();
                // console.info(response);
            }
        });
      return false; 
    });
});

$(document).ready(function() {  
    $(".rdfturtle").click(function() {
      lexemes = GetSelected()
      lexemes['downloadFormat'] = "rdfturtle";
    // lexemes['downloadFormat'] = "turtle";
      $.ajax({
            url: '/downloadselectedlexeme',
            type: 'GET',
            data: {'data': JSON.stringify(lexemes)},
            contentType: "application/json; charset=utf-8", 
            success: function(response){
                console.info(typeof response);
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("dictionaryview", "downloadjson");
                // window.location.reload();
                // console.info(response);
            }
        });
      return false; 
    });
});

$(document).ready(function() {  
    $(".rdfxml").click(function() {
      lexemes = GetSelected()
      lexemes['downloadFormat'] = "rdfxml";
    //   lexemes['downloadFormat'] = "xml";
      $.ajax({
            url: '/downloadselectedlexeme',
            type: 'GET',
            data: {'data': JSON.stringify(lexemes)},
            contentType: "application/json; charset=utf-8", 
            success: function(response){
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("dictionaryview", "downloadjson");
                // window.location.reload();
                // console.info(response);
            }
        });
      return false; 
    });
});

$(document).ready(function() {  
    $(".rdfntriples").click(function() {
      lexemes = GetSelected()
    //   lexemes['downloadFormat'] = "rdfntriples";
    lexemes['downloadFormat'] = "rdfnt";
      $.ajax({
            url: '/downloadselectedlexeme',
            type: 'GET',
            data: {'data': JSON.stringify(lexemes)},
            contentType: "application/json; charset=utf-8", 
            success: function(response){
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("dictionaryview", "downloadjson");
                // window.location.reload();
                // console.info(response);
            }
        });
      return false; 
    });
});

$(document).ready(function() {  
    $(".rdfn3").click(function() {
      lexemes = GetSelected()
      lexemes['downloadFormat'] = "rdfn3";
    // lexemes['downloadFormat'] = "n3";
      $.ajax({
            url: '/downloadselectedlexeme',
            type: 'GET',
            data: {'data': JSON.stringify(lexemes)},
            contentType: "application/json; charset=utf-8", 
            success: function(response){
                // console.log(window.location.href.replace("dictionaryview", "downloadjson"))
                window.location.href = window.location.href.replace("dictionaryview", "downloadjson");
                // window.location.reload();
                // console.info(response);
                // .replace("dictionaryview", "downloadjson")
            }
        });
      return false; 
    });
});