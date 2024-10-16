$(document).ready(function() {
  // console.log(document.getElementById("newdataform"))
  document.getElementById("newdataform").reset();
  // console.log(document.getElementById("newdataform"))
});

var dataProjectType = [
  {"id": "", "text": ""},
  {"id": "annotation", "text": "Annotation"},
  {"id": "recordings", "text": "Recordings"},
  {"id": "validation", "text": "Validation"},
  {"id": "transcriptions", "text": "Speech Transcription and Labeling"},
  // {"id": "crawling", "text": "Crawling"},
];
var languages = getJsonfileData('languages');
var scripts = getJsonfileData('scripts');
var conllu = getJsonfileData('conllu_2');
var additionalOptions = ['Languages'];
conllu.push(...additionalOptions)
eventSelect2();

// var jsonFileNames = {
//   languages: "select2_languages.json",
//   scripts: "select2_scripts.json",
//   conllu: "select2_conllu_2.json",
// }
// $.ajax({
//   url: '/get_jsonfile_data',
//   type: 'GET',
//   data: {'data': JSON.stringify(jsonFileNames)},
//   contentType: "application/json; charset=utf-8",
//   success: function(response){
//     languages = response.jsonData.languages;
//     scripts = response.jsonData.scripts;
//     conllu = response.jsonData.conllu;
//     conllu.push(...additionalOptions)
//     eventSelect2();
//   }
// });

function languageScriptFieldsSelect2(langIdName,
                                      scriptIdName,
                                      id,
                                      langTags=false,
                                      scriptTags=false,
                                      langData=true,
                                      allowClear=false) {
  let tempLanguages = [];
  if (langData) {
    tempLanguages = languages;
  }
  let tempScripts = scripts;
  $('#'+langIdName+id).select2({
    tags: langTags,
    placeholder: 'Tier Name',
    data: tempLanguages,
    allowClear: allowClear
  });

  $('#'+scriptIdName+id).select2({
    tags: scriptTags,
    placeholder: 'Script',
    data: tempScripts,
    allowClear: allowClear
  });
}

function eventSelect2 () {
  $('.dataprojecttype').select2({
    // tags: true,
    placeholder: 'select the type of data project',
    data: dataProjectType
  });

  $('.datasentencelanguageclass').select2({
    tags: true,
    placeholder: 'Audio Language',
    data: languages,
    // allowClear: true
  });
  
  $('.recordingssentencelanguageclass').select2({
    tags: true,
    placeholder: 'Audio Language',
    data: languages,
    // allowClear: true
  });
  
  $('.datatranscriptionscriptclass').select2({
    // tags: true,
    placeholder: 'Transcription Scripts',
    data: scripts,
    allowClear: true,
    // sorter: false
  });
  select2Multiselect();
}

function select2Multiselect() {
  // partial solution to the select2 multiselect
  $("select").on("select2:select", function (evt) {
    var element = evt.params.data.element;
    // console.log(element);
    var $element = $(element);
    $element.detach();
    $(this).append($element);
    $(this).trigger("change");
  });
}

var additionalTranscriptionField = 0;

$("#addAdditionalTranscriptionField").click(function() {
    additionalTranscriptionField++;

    var drow = '<div class="row removeadditionaltranscriptionfield' + additionalTranscriptionField + '">';

    var fItems = '<div class="col-md-3"><div class="form-group">'+
                '<select id="additionaltranscriptionname' + additionalTranscriptionField + '" class="form-control" name="Additional Transcription Name" required>';
    // fItems += '<option value="">Additional Transcription Name</option>';

    // for (var i = 0; i < languages.length; i++) {
    //     fItems += '<option value="' + languages[i].text + '">' + languages[i].id + '</option>';
    // }
    fItems += '</select></div></div>';

    fItems += '<div class="col-md-3"><div class="form-group">'+
                '<div class="input-group">'+
                '<select id="additionaltranscriptionscript' + additionalTranscriptionField + '" class="form-control" name="Additional Transcription Script" required>';
    // fItems += '<option value="">Transcription Script</option>';

    // for (var i = 0; i < scripts.length; i++) {
    //     fItems += '<option value="' + scripts[i].text + '">' + scripts[i].id + '</option>';
    // }
    fItems += '</select>';

    fItems += '<div class="input-group-btn">'+
                '<button class="btn btn-sm btn-danger" type="button" onclick="removeAdditionalTranscriptionFields('+ additionalTranscriptionField +');">'+
                '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></div></div></div></div>';

    drow += fItems;
    drow += '</div>'
    $(".additionaltranscription").append(drow);
    languageScriptFieldsSelect2("additionaltranscriptionname",
                                  "additionaltranscriptionscript",
                                  additionalTranscriptionField,
                                  true,
                                  false,
                                  false,
                                  true);
});

function removeAdditionalTranscriptionFields(rid) {
    $(".removeadditionaltranscriptionfield"+rid).remove();
}

var translationField = 0;

$("#addTranslationLanguageField").click(function(){
    translationField++;

    var drow = '<div class="row removetranslationfield' + translationField + '">';

    var fItems = '<div class="col-md-3"><div class="form-group">'+
                '<select id="translationlanguage' + translationField + '" class="form-control" name="Translation Language" required>';
    // fItems += '<option value="">Translation Language</option>';

    // for (var i = 0; i < languages.length; i++) {
    //     fItems += '<option value="' + languages[i].text + '">' + languages[i].id + '</option>';
    // }
    fItems += '</select></div></div>';

    fItems += '<div class="col-md-3"><div class="form-group">'+
                '<div class="input-group">'+
                '<select id="translationscript' + translationField + '" class="form-control" name="Translation Script" required>';
    // fItems += '<option value="">Translation Script</option>';

    // for (var i = 0; i < scripts.length; i++) {
    //     fItems += '<option value="' + scripts[i].text + '">' + scripts[i].id + '</option>';
    // }
    fItems += '</select>';

    fItems += '<div class="input-group-btn">'+
                '<button class="btn btn-sm btn-danger" type="button" onclick="removeTranslationFields('+ translationField +');">'+
                '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></div></div></div></div>';

    drow += fItems;
    drow += '</div>'
    $(".translationlanguage").append(drow);
    languageScriptFieldsSelect2("translationlanguage",
                                  "translationscript",
                                  translationField);
});


// remove a translation element
function removeTranslationFields(rid) {
    $(".removetranslationfield"+rid).remove();
}

var interlinearGlossField = 0;

$("#addInterlinearGlossField").click(function(){
    interlinearGlossField++;

    var drow = '<div class="row removeinterlinearglossfield' + interlinearGlossField + '">';

    var fItems = '<div class="col-md-3"><div class="form-group">'+
                '<select class="form-control" name="Interlinear Gloss Language" required>';
    fItems += '<option value="">Interlinear Gloss Language</option>';

    for (var i = 0; i < languages.length; i++) {
        fItems += '<option value="' + languages[i].text + '">' + languages[i].id + '</option>';
    }
    fItems += '</select></div></div>';

    fItems += '<div class="col-md-3"><div class="form-group">'+
                '<div class="input-group">'+
                '<select class="form-control" name="Interlinear Gloss Script" required>';
    fItems += '<option value="">Interlinear Gloss Script</option>';

    for (var i = 0; i < scripts.length; i++) {
        fItems += '<option value="' + scripts[i].text + '">' + scripts[i].id + '</option>';
    }
    fItems += '</select>';

    fItems += '<div class="input-group-btn">'+
                '<button class="btn btn-danger" type="button" onclick="removeInterlinearGlossFields('+ interlinearGlossField +');">'+
                '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></div></div></div></div>';

    drow += fItems;
    drow += '</div>'
    $(".interlinearglossfield").append(drow);
});


// remove a interlineargloss element
function removeInterlinearGlossFields(rid) {
    $(".removeinterlinearglossfield"+rid).remove();
}

$("#idprojecttype").change(function() {
  let projecttypevalue = document.getElementById("idprojecttype").value;
  // console.log(projecttypevalue, this);
  let projectTypeOptions = this.options;
  for (i=0; i<projectTypeOptions.length; i++) {
    if (projectTypeOptions[i].value === '') continue
    let projecttypeId = projectTypeOptions[i].value+"typeproject";
    var x = document.getElementById(projecttypeId);
    // console.log(projecttypeId, x);
    if (projectTypeOptions[i].value === projecttypevalue) {
      // console.log(projectTypeOptions[i].value)
      // console.log(x);
      if (x.style.display === "none") {
        // console.log(x);
          x.style.display = "block";
          $('#'+projecttypeId).find('input, textarea, button, select').attr('disabled', false);
      }
    }
    else {
      x.style.display = "none";
      $('#'+projecttypeId).find('input, textarea, button, select').attr('disabled','disabled');
    }
  }
  if (projecttypevalue === 'validation') {
    enableDisableDataFormSubmitBtn(true);
    let addModal = addModalElement('validationTagsetMapping');
    $('#addModal').html(addModal);
  }
  else {
    enableDisableDataFormSubmitBtn(false);
  }
  // if (projecttypevalue === 'transcriptions') {
  //   var x = document.getElementById(projecttypevalue+"typeproject");
  //   if (x.style.display === "none") {
  //       x.style.display = "block";
  //   }
  // }
});

// uploadFileTypes = [

//   {
//     'id': 'audio',
//     'text': 'Audio'
//   },
//   {
//       'id': 'text',
//       'text': 'Text'
//   },
//   {
//       'id': 'image',
//       'text': 'Image'
//   }
// ]

// function uploadFileType() {
//   $('#fileType').select2({
//       placeholder: 'select',
//       data: uploadFileTypes,
//       // allowClear: true
//   });
// }
// uploadFileType();

$("#tagsetZipFile").change(function() {
  let zipFileElement = document.getElementById('tagsetZipFile');
  // console.log(zipFileElement);
  zipFileName = zipFileElement.files[0];
  // console.log(zipFileName);
  // displayZipFileName = '<p>'+zipFileName.name+'</p>';
  $("#displayZipFileName").html(zipFileName.name);
  document.getElementById('validationtagsetmappingedit').hidden = true;
  document.getElementById('validationzipfilesubmit').hidden = false;

})

function uploadValidatioZipFile(btn) {
  // console.log(btn, btn.id);
  const file = document.getElementById('tagsetZipFile').files[0];
  // console.log(file);
  if (file !== undefined) {
    var formData = new FormData();
    formData.append('tagsetZipFile', file);
    let deriveFromProjectName = document.getElementById('idderivefromproject').value;
    formData.append('deriveFromProjectName', deriveFromProjectName);
    let projectType = document.getElementById('idprojecttype').value;
    formData.append('projectType', projectType);
    $.ajax({
      url: '/lifedata/datazipfile',
      type: 'POST',
      data: formData,
      contentType: false,
      cache: false,
      processData: false,
      success: function(data) {
        // console.log(data);
        if (data.completed) {
          addValidationTagsetMappingToMainForm('');
          localStorage.setItem("validationTagsetKeys", JSON.stringify(data.validationTagsetKeys));
          let modalData = mappingModalForm(data.mappingTagset);
          $('#validationTagsetMapping_modal_data').html(modalData);
          createSelect2(data.mappingTagset);
          $('#validationTagsetMappingModal').modal('toggle');
        }
        else {
          alert(data.message);
        }
      },
    });
    return false;
  }
}

function addModalElement(key) {
  let modalEle = ''
  modalEle += '<div class="modal fade" id="'+key+'Modal" tabindex="-1" role="dialog" aria-labelledby="'+key+'ModalLabel">'+
              '<div class="modal-dialog">'+
              '<div class="modal-content">'+
                  '<div class="modal-header">'+
                  '<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>'+
                  
                  '<h4 class="modal-title" id="'+key+'ModalLabel">Validation Tagset Mapping</h4>'+
                  '</div>'+
                  '<div class="modal-body">'+
                      '<div class="row" id="'+key+'_modal_data"><form></form>'+
                      '</div>'+
                  '</div>'+
                  '<div class="modal-footer">'+
                  '<button type="button" class="btn btn-default pull-left" data-dismiss="modal">Close</button>'+
                  '<button type="button" class="btn btn-primary" data-dismiss="modal" id="'+key+'save" onclick="saveValidationTagsetMapping(this.id)">Save Mapping</button>'+
                  '</div>'+
              '</div>'+
              '</div>'+
          '</div>';

  return modalEle;
}

function mappingModalForm(mappingTagset, mapped='') {
  let mapModalData = '';
  mapModalData += '<form name="savevalidatiotagsetnmap" id="idsavevalidationtagsetmapform" class="form-horizontal" action="/easyAnno/savevalidationtagsetmap" method="POST"  enctype="multipart/form-data">';
  // for (let i=0; i<deriveFromProjectTagset.length; i++) {
  for (let [key, value] of Object.entries(mappingTagset)) {
    // console.log(key, value);
    mapModalData += '<div class="col-md-12"><div class="form-group">'+
            'Validation of: <label for="'+key+'_select">'+key+'</label>'+
            ' on: <select class="form-control '+key+'" id="' + key+'_select" name="'+key+mapped+'" multiple="multiple" style="width: 100%" required>';
    for (var j=0; j<value.length; j++) {
      mapModalData += '<option value="'+value[j]+'" selected>'+value[j]+'</option>';
    }
    mapModalData += '</select></div></div>';
  }
  mapModalData += '</form>';

  return mapModalData;
}

function createSelect2(mappingTagset) {
  let validationTagstKeys = JSON.parse(localStorage.getItem('validationTagsetKeys'));
  // for (s=0; s<select2Keys.length; s++) {
    for (let [key, value] of Object.entries(mappingTagset)) {
      // console.log(key, value);
      select2Key = key;
      $('#' + select2Key+'_select').select2({
          placeholder: select2Key,
          data: validationTagstKeys,
          allowClear: true
      });
  }
}

function saveValidationTagsetMapping(savebtnid) {
  submit_map_form_ele = document.getElementById("idsavevalidationtagsetmapform");
  // console.log(submit_map_form_ele)
  const formData = new FormData(submit_map_form_ele);
  // console.log(formData);
  var object = {};
  formData.forEach(function(value, key){
      // console.log('key: ', key, 'value: ', value, tagSetMetaData);
    if (key in object) {
      object[key].push(value);
    }
    else {
        object[key] = [value];
    }
  });
  let modalData = mappingModalForm(object, '_mapped');
  addValidationTagsetMappingToMainForm(modalData);
  createSelect2(object);
  localStorage.setItem("validationTagsetMapping", JSON.stringify(object));
  document.getElementById('validationzipfilesubmit').hidden = true;
  document.getElementById('validationtagsetmappingedit').hidden = false;
  enableDisableDataFormSubmitBtn(false);
}

function editValidatioTagsetMapping(btnId) {
  addValidationTagsetMappingToMainForm('');
  let validationTagsetMapping = JSON.parse(localStorage.getItem('validationTagsetMapping'));
  let modalData = mappingModalForm(validationTagsetMapping);
  $('#validationTagsetMapping_modal_data').html(modalData);
  createSelect2(validationTagsetMapping);
}

function addValidationTagsetMappingToMainForm(modalData) {
  $('#validationtagsetmapping').html(modalData);
}

function enableDisableDataFormSubmitBtn(bool) {
  // console.log(bool);
  document.getElementById('dataformsubmit').disabled = bool;
}

$("#annotationtagsetZipFile").change(function() {
  let zipFileElement = document.getElementById('annotationtagsetZipFile');
  // console.log(zipFileElement);
  zipFileName = zipFileElement.files[0];
  // console.log(zipFileName);
  // displayZipFileName = '<p>'+zipFileName.name+'</p>';
  $("#displayAnnotationZipFileName").html(zipFileName.name);

})

function showZipFileName(id, zipFileName='') {
  let pTagId = id.replace("ZipFile", "ZipFileName")
  $("#"+pTagId).html(zipFileName);
}

$("#transcriptionstagsetZipFile").change(function() {
  let zipFileElement = document.getElementById('transcriptionstagsetZipFile');
  // console.log(zipFileElement);
  zipFileName = zipFileElement.files[0];
  // console.log(zipFileName);
  // displayZipFileName = '<p>'+zipFileName.name+'</p>';
  // $("#displayTranscriptionsZipFileName").html(zipFileName.name);
  showZipFileName("transcriptionstagsetZipFile", zipFileName.name);
  $("#idtranscriptionstagsetuploadselect").val(null).trigger('change');
  enableDisableDataFormSubmitBtn(true);
})

$("#transcriptionsboundarytagsetZipFile").change(function() {
  let zipFileElement = document.getElementById('transcriptionsboundarytagsetZipFile');
  // console.log(zipFileElement);
  zipFileName = zipFileElement.files[0];
  // console.log(zipFileName);
  // displayZipFileName = '<p>'+zipFileName.name+'</p>';
  // $("#displayTranscriptionsBoundaryZipFileName").html(zipFileName.name);
  showZipFileName("transcriptionsboundarytagsetZipFile", zipFileName.name);
  $("#idtranscriptionsboundarytagsetuploadselect").val(null).trigger('change');
  enableDisableDataFormSubmitBtn(true);
})

$("#idtranscriptionstagsetuploadselect").change(function() {
  let ele = document.getElementById("idtranscriptionstagsetuploadselect");
  let eleValue = ele.value;
  // console.log(eleValue);
  if (eleValue !== '') {
    resetZipFile("transcriptionstagsetuploadcheckbox");
    enableDisableDataFormSubmitBtn(false);
  }
  else if (eleValue === '') {
    if (document.getElementById("transcriptionstagsetuploadcheckbox").checked == false) {
      enableDisableDataFormSubmitBtn(false);
    }
    else {
      enableDisableDataFormSubmitBtn(true);
    }
  }
})

$("#idtranscriptionsboundarytagsetuploadselect").change(function() {
  let ele = document.getElementById("idtranscriptionsboundarytagsetuploadselect");
  let eleValue = ele.value;
  // console.log(eleValue);
  if (eleValue !== '') {
    resetZipFile("transcriptionsboundarytagsetuploadcheckbox");
    enableDisableDataFormSubmitBtn(false);
  }
  else if (eleValue === '') {
    if (document.getElementById("transcriptionsboundarytagsetuploadcheckbox").checked == false) {
      enableDisableDataFormSubmitBtn(false);
    }
    else {
      enableDisableDataFormSubmitBtn(true);
    }
  }
})

$("#transcriptionstagsetuploadcheckbox").change(function() {
  getTagsetsList("transcriptionstagsetuploadcheckbox");
  if(this.checked) {
    enableDisableDataFormSubmitBtn(true);
    document.getElementById("transcriptionstagsetupload").style.display = "block";
  }
  else {
    enableDisableDataFormSubmitBtn(false);
    document.getElementById("transcriptionstagsetupload").style.display = "none";
    resetZipFile("transcriptionstagsetuploadcheckbox");
    // $('#idtranscriptionstagsetuploadselect').select2('destroy');
  }
});

$("#transcriptionsboundarytagsetuploadcheckbox").change(function() {
  getTagsetsList("transcriptionsboundarytagsetuploadcheckbox");
  if(this.checked) {
    enableDisableDataFormSubmitBtn(true);
    document.getElementById("transcriptionsboundarytagsetupload").style.display = "block";
  }
  else {
    enableDisableDataFormSubmitBtn(false);
    document.getElementById("transcriptionsboundarytagsetupload").style.display = "none";
    resetZipFile("transcriptionsboundarytagsetuploadcheckbox");
  }
});

function resetZipFile(id) {
  let inputEleId = id.replace("uploadcheckbox", "ZipFile")
  const file = document.getElementById(inputEleId);
  // console.log(file);
  file.value = '';
  showZipFileName(inputEleId);
}

function uploadTranscriptionTagsetZipFile(btn) {
  // console.log(btn, btn.id);
  let uploadBtnId = btn.id;
  let file = '';;
  let activeTagsetCheckbox = '';
  if (uploadBtnId.includes("boundary")) {
    file = document.getElementById('transcriptionsboundarytagsetZipFile').files[0];
    activeTagsetCheckbox = "transcriptionsboundarytagsetuploadcheckbox"
  }
  else{
    file = document.getElementById('transcriptionstagsetZipFile').files[0];
    activeTagsetCheckbox = "transcriptionstagsetuploadcheckbox"
  }
  // console.log(file);
  if (file !== undefined) {
    var formData = new FormData();
    formData.append('transcriptionstagsetZipFile', file);
    try {
      let deriveFromProjectName = document.getElementById('idderivefromproject').value;
    }
    catch(err) {
      // console.log(typeof err.message);
      deriveFromProjectName = '';
    }
    formData.append('deriveFromProjectName', deriveFromProjectName);
    let projectType = document.getElementById('idprojecttype').value;
    formData.append('projectType', projectType);
    // console.log(formData);
    $.ajax({
      url: '/lifedata/datazipfile',
      type: 'POST',
      data: formData,
      contentType: false,
      cache: false,
      processData: false,
      success: function(data) {
        // console.log(data);
        if (data.completed) {
          enableDisableDataFormSubmitBtn(false);
        }
        else {
          alert(data.message);
          resetZipFile(activeTagsetCheckbox);

        }
      },
    });
    return false;
  }
  else {
    alert("Please Select Tagset ZIP File ");
  }
}

// $("#transcriptionstagsetZipFile").change(function() {
//   enableDisableDataFormSubmitBtn(true);
// });

function getTagsetsList(id) {
  let selectId = id.replace("checkbox", "select");
  $.getJSON('gettagsetslist',
    {}, 
    function(data) {
        let tagsetsList = data.tagsetsList;
        $('#id'+selectId).select2({
            placeholder: 'Tagset Name',
            data: tagsetsList,
            allowClear: true,
        });
        $("#id"+selectId).val(null).trigger('change');
    }
  );
}

$(document).on('keyup', '#idprojectname', function (e) {
  let inputProjectName = e.target.value;
  console.log(inputProjectName);
  // $.ajax({
  //   data : {
  //     a : inputProjectName
  //   },
  //   type : 'GET',
  //   url : '/checkprojectnameexist'
  // }).done(function(data){
  //     console.log(data);
  //     let status = data.status;
  //     document.getElementById('crawldataformsubmit').disabled = status;
  //     enableDisableDataFormSubmitBtn(status);
  //     if (status) {
  //       document.getElementById('projectnameexist').style.display = 'block';
  //     }
  //     else {
  //       document.getElementById('projectnameexist').style.display = 'none';
  //     }
  // });
});

$(".interlinearGlossFormat").click(function(event){
  // console.log('123');
  // console.log(event);
  console.log(event.target.id);
  let formatType = event.target.id;
  // $('#interlinearGlossFormatModal').modal('toggle');
  let inpt = '';
  inpt += '<select id="custominterlinearglossfield" name="Customize Gloss" multiple="multiple" style="width: 55%"></select>';
  $("#idcustominterlinearglossfield").html(inpt);
  $('#custominterlinearglossfield').select2({
    // tags: true,
    placeholder: 'Customize Gloss Info',
    data: conllu,
    allowClear: true
  });
  if (formatType === 'ud') {
    $('#custominterlinearglossfield').val(conllu);
    $('#custominterlinearglossfield').trigger('change');
  }
  select2Multiselect();
});

