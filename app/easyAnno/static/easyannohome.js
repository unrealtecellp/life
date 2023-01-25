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

function createSelectElement(elevalue, activeprojectname) {
// console.log(activeprojectname)
var qform = '';
qform += '<select class="easyannoallfileslistselect" id="easyannoallfileslistselectid" style="width: 100%">';
qform += '<option selected disabled>Change Active File</option>';

for (let i=0; i<elevalue.length; i++) {
    eval = elevalue[i]
    if (activeprojectname.includes(eval)) {
        qform += '<option value="'+eval+'" selected disabled>'+eval+'</option>';  
    }
    else {
        qform += '<option value="'+eval+'">'+eval+'</option>';
    }
}
qform += '</select></div>';

return qform;
}

function allFiles(allFilesList) {
    var projectslist = '';
    // console.log(allFilesList);
    projectslist += createSelectElement(allFilesList, []);

    $('#easyannoallfileslist').html(projectslist);

    $('.easyannoallfileslistselect').select2({
        placeholder: 'select'
        // data: usersList,
        // allowClear: true
    });

    // event fire from thew home page all projects list select element
    $("#easyannoallfileslistselectid").change(function() {
        let projectname = document.getElementById('easyannoallfileslistselectid');
        pname = projectname.value;

        $.ajax({
        data : {
            a : pname
        },
        type : 'GET',
        url : '/activeprojectname'
        }).done(function(){
            // window.location.reload();
            loc = window.location.href
            window.location.assign(loc)
    
        });
    });
}
