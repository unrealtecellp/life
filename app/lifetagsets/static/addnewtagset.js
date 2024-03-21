function getTagsetForm(ele, options) {
    let defaults = { submitRoute: "/ltset/addnestagset" };
    options = Object.assign({}, defaults, options); //first it assigns defaults to the options and then overwrites those with the values present in 'options' object
    let { submitRoute, includeFieldMetadata, includeInternetMetadata } = options;

    cur_id = $(ele).attr('id')
    console.log('Current ID', cur_id);
    console.log('Options', options);
    tagsetDetailForm(cur_id, submitRoute);
}

$('.addnewtagset').on('click', function () {
    console.log('on click');
    cur_id = $(this).attr('id')
    console.log('Current ID', cur_id)

    tagsetDetailForm(cur_id);
});

$('#editbutton').click(function () {

    $('#formdisplay').find('input, select').attr('disabled', false);
    $('#editbutton').attr('hidden', true);
    // $('#idname').hidden();
    // $('#idage').attr('hidden', false);
    // document.getElementById('idviewname').readonly = true;
    // document.getElementById('idviewage').readonly = true;
    
    // $('#idviewname').attr('readonly', true);
    // $('#idviewage').attr('readonly', true);

    // $('#accodeformheader').find('input, select').attr('disabled', true);
});

function removelangScriptPromptFields(rid) {
    $(".removelangScriptPromptfield"+rid).remove();
}

function removesupportedtaksfield(rid) {
    $(".removesupportedtasksfield"+rid).remove();
  }


function tagsetDetailForm(cur_id, submitRoute) {
    let sourceinpt = ''
    
    sourceinpt += '<form id="newtagsetform" action="' + submitRoute + '" method="POST" enctype="multipart/form-data">';
    
    sourceinpt += '<input type="hidden" value="' +
        cur_id +
        '"name = "sourcecallpage" id="sourcecallpageid">';
    
    sourceinpt += '<div id="formdisplayinitial" style="display: block;">';

    sourceinpt += '<div id="idtagsetmetadatadiv" style="display: none;"></div>';

    sourceinpt += '<div id="idtagsetupload" style="display: none;"></div>';
    
    sourceinpt += '<input class="btn btn-lg btn-primary upload" id="uploadtagsetsubmit" type="submit" value="Upload Tagset">';

    $("#addnewtagsetform").html("");
    $("#addnewtagsetform").append(sourceinpt);
        
    addNewTagsetFormEvents();
    addNewTagsetSelect2();
}

function createUploadFields() {
    sourceinpt = '';
    
    sourceinpt += '<div class="col upload">' +
        '<label class="btn btn-danger">' +
        'Select ZIP File <input type="file" id="annotationtagsetZipFile" name="annotationtagsetZipFile" accept="application/zip" hidden>' +
        '</label>' +
        '<p id="displayAnnotationZipFileName"></p>' +
        '</div>';
    
    return sourceinpt
}

function uploadMetadataTagsetForm(form_vals = {}) {
    sourceinpt = '';

    sourceinpt += '<div class="form-group">' +
        '<label for="idtagsetname">Tagset Name</label>' +
        '<input type="text" class="form-control" id="idtagsetname" placeholder="Tagset Name" name="tagsetname" style="width: 55%" required>' +
        '</div>';

    sourceinpt += '<div class="form-group">' +
        '<label for= "idabout">About the Tagset</label><br>' +
        '<textarea id="idabout" name="abouttagset" style="width:55%" required></textarea>' +
        '</div>';
    
    sourceinpt += '<div class="row ">' +
        '<div class="col-md-3">' +
        '<label>Supported Languages and Scripts</label>' +
        '<p>' +
        '<em>' +
        '*Leave blank if its language independent' +
        '</em>' +
        '</p>' +
        '</div>' +
        '</div>' +
        '<div class="row"> ' +
        '<div class="col-md-3">' +
        '<div class="form-group">' +
        '<button class="btn btn-success" type="button" id="addtagsetlangscripts" onclick=addLanguageScriptDiv()> ' +
        '<span class="glyphicon glyphicon-plus" aria-hidden="true"></span> ' +
        '</button>' +
        '</div>' +
        '</div>' +
        '</div>' +
        '<div class="col-md-12 tagsetlangscripts"></div>';
    
    sourceinpt += '<div class="row ">' +
        '<div class="col-md-3">' +
        '<label>Supported Tasks</label>' +
        '</div>' +
        '</div>' +
        '<div class="row"> ' +
        '<div class="col-md-3">' +
        '<div class="form-group">' +
        '<button class="btn btn-success" type="button" id="addsupportedtasks" onclick=addSupportedTaskDiv()> ' +
        '<span class="glyphicon glyphicon-plus" aria-hidden="true"></span> ' +
        '</button>' +
        '</div>' +
        '</div>' +
        '</div>' +
        '<div class="col-md-12 supportedtaks"></div>';
    
    sourceinpt += '<div class="form-group">' +
        '<input type="checkbox" id="idisprivate" name="isprivate" checked>' +
        '<label for="idisprivate">Private Tagset</label><br>' +
        '</div>';
    
    return sourceinpt
}

function addSupportedTasks(fieldid) {
    $('.classsupportedtask_'+fieldid).select2({
        tags: true,
        placeholder: '--Supported Tasks--',
        data: supportedTasks,
        // allowClear: true
    });
}


function addNewTagsetSelect2() {
}

var langScriptPromptField = 0;
var supportedTaskPromptField = 0;  
function addLanguageScriptDiv(fieldNumber = 0) {
        // $("#addtagsetlangscripts").click(function () {
        langScriptPromptField += fieldNumber;
        langScriptPromptField++;
    
        var drow = '<div class="row removelangScriptPromptfield' + langScriptPromptField + '">';

        var fItems = '<div class="row">' +
            '<div class="col-md-3"><div class="form-group">' +
            '<select class="form-control" name="Language_' + langScriptPromptField + '"  required>';
        fItems += '<option value="" selected disabled>Language</option>';
        for (var i = 0; i < languages.length; i++) {
            if (languages[i].id !== '' && languages[i].text !== '') {
                fItems += '<option value="' + languages[i].text + '">' + languages[i].id + '</option>';
            }
        }
        fItems += '</select></div></div>';

        
        fItems += '<div class="col-md-3"><div class="form-group">' +
            '<div class="input-group">' +
            '<select class="form-control" name="Script_' + langScriptPromptField + '"  required>';
        fItems += '<option value="" selected disabled>Script</option>';
        for (var i = 0; i < scripts.length; i++) {
            if (scripts[i].id !== '' && scripts[i].text) {
                fItems += '<option value="' + scripts[i].text + '">' + scripts[i].id + '</option>';
            }
        }
        fItems += '</select></div></div>';

        fItems += '<div class="col-md-3"><div class="input-group-btn">' +
            '<button class="btn btn-danger" type="button" onclick="removelangScriptPromptFields(' + langScriptPromptField + ');">' +
            '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></div></div>';
        
        drow += fItems;
        drow += '</div>';
        // $(".tagsetlangscripts").html("");
        $(".tagsetlangscripts").append(drow);
        // });
}

function addSupportedTaskDiv(fieldNumber = 0) {
    // $("#addsupportedtasks").click(function(){
    supportedTaskPromptField += fieldNumber;
    supportedTaskPromptField++;
    
    var drow = '<div class="row removesupportedtasksfield' + supportedTaskPromptField + '">';

    var fItems = '<div class="row">' +
        '<div class="col-md-3"><div class="form-group">' +
        '<label for="idsupportedtask_' + supportedTaskPromptField + '">Supported Task</label><br>' +
        '<select multiple="multiple" class="classsupportedtask_' + supportedTaskPromptField + '" id="idsupportedtask_' + supportedTaskPromptField + '" name="supportedTask_' + supportedTaskPromptField + '" style="width:55%" required></select><br>';       
    fItems += '</div></div>';

    fItems += '<div class="col-md-3"><div class="form-group">' +
        '<div class="input-group">' +
        '<label for= "idsupportedtaskdescription_' + supportedTaskPromptField + '">About the Task</label><br>' +
        '<textarea id="idsupportedtaskdescription_' + supportedTaskPromptField + '" name="supportedTaskDescription_' + supportedTaskPromptField + '"></textarea>';
    fItems += '</div></div>';  

    fItems += '<div class="input-group-btn">' +
        '<button class="btn btn-danger" type="button" onclick="removesupportedtaksfield(' + supportedTaskPromptField + ');">' +
        '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button>' +
        '</div>';
        
    drow += fItems;
    drow += '</div>';
    $(".supportedtaks").append(drow);
    addSupportedTasks(supportedTaskPromptField);
    // });
}

function addNewTagsetFormEvents() {        

    $("#annotationtagsetZipFile").change(function () {
        let zipFileElement = document.getElementById('annotationtagsetZipFile');
        // console.log(zipFileElement);
        zipFileName = zipFileElement.files[0];
        // console.log(zipFileName);
        // displayZipFileName = '<p>'+zipFileName.name+'</p>';
        $("#displayAnnotationZipFileName").html(zipFileName.name);

    });
        
}