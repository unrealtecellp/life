$( document ).ready(function() {
    let filetype = document.forms["createProject"]["fileType"].value;
    addInpt(filetype)
    document.getElementById("fileType").onchange = function(){
        let filetype = document.forms["createProject"]["fileType"].value;
        addInpt(filetype)
    };
});

function addInpt(filetype) {
    inpt = '';
    if (filetype === "image") {
        $('.annotatedTextCheck').remove();
        inpt += '<div class="imageFileInpt">'+
                '<label for="imageFileName">File Name:&nbsp;</label>'+
                '<input type="text" id="imageFileName" name="imageFileName">'+
                '</div>';
        $('.upload').append(inpt);
        inpt = '';
    }
    else if (filetype === "text") {
        $('.imageFileInpt').remove();
        inpt += '<div class="annotatedTextCheck">'+
                '<input type="checkbox" id="annotatedTextZip" name="annotatedTextZip">'+
                '<label for="annotatedTextZip">&nbsp;Annotated File</label>'+
                '</div>';
        $('.upload').append(inpt);
        inpt = '';
    }
}

function validateForm() {
    if (typeof document.forms["createProject"]["imageFileName"] !== 'undefined') {
        let language = document.forms["createProject"]["imageFileName"].value;
        if (language == "") {
        alert("Please give File Name");
        return false;
        }
    }
  }
