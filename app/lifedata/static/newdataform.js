$(document).ready(function() {
  // console.log(document.getElementById("newdataform"))
  document.getElementById("newdataform").reset();
  // console.log(document.getElementById("newdataform"))
});
var languages = [

  {"id": "", "text": ""},
  {"id": "Assamese", "text": "Assamese"},
  {"id": "Awadhi", "text": "Awadhi"},
  {"id": "Bangla", "text": "Bangla"},
  {"id": "Bhojpuri", "text": "Bhojpuri"},
  {"id": "Bodo", "text": "Bodo"},
  {"id": "Braj", "text": "Braj"},
  {"id": "Bundeli", "text": "Bundeli"},
  {"id": "Chhattisgarhi", "text": "Chhattisgarhi"},
  {"id": "Chokri", "text": "Chokri"},
  {"id": "English", "text": "English"},
  {"id": "Gujarati", "text": "Gujarati"},
  {"id": "Haryanvi", "text": "Haryanvi"},
  {"id": "Hindi", "text": "Hindi"},
  {"id": "Kannada", "text": "Kannada"},
  {"id": "Konkani", "text": "Konkani"},
  {"id": "KokBorok", "text": "Kok Borok"},
  {"id": "Magahi", "text": "Magahi"},
  {"id": "Maithili", "text": "Maithili"},
  {"id": "Malayalam", "text": "Malayalam"},
  {"id": "Marathi", "text": "Marathi"},
  {"id": "Meitei", "text": "Meitei"},
  {"id": "Nepali", "text": "Nepali"},
  {"id": "Nyishi", "text": "Nyishi"},
  {"id": "Odia", "text": "Odia"},
  {"id": "Punjabi", "text": "Punjabi"},
  {"id": "Santali", "text": "Santali"},
  {"id": "Tamil", "text": "Tamil"},
  {"id": "Telugu", "text": "Telugu"},
  {"id": "Toto", "text": "Toto"}
]

var scripts = 
[    
      {
        "id": "",
        "text": ""
      },
      {
        "id": "Bengali", 
        "text": "Bengali"
      },
      {
        "id": "Devanagari", 
        "text": "Devanagari"
      },
      {
        "id": "Gujarati", 
        "text": "Gujarati"
      },
      {
        "id": "Gurumukhi", 
        "text": "Gurumukhi"
      },
      {
        "id": "IPA", 
        "text": "IPA"
      },
      {
        "id": "Kannada", 
        "text": "Kannada"
      },
      {
        "id": "Latin", 
        "text": "Latin"
      },
      {
        "id": "Malayalam", 
        "text": "Malayalam"
      },
      {
        "id": "Mayek", 
        "text": "Mayek"
      },
      {
        "id": "Odia", 
        "text": "Odia"
      },
      {
        "id": "OlChiki", 
        "text": "Ol Chiki"
      },
      {
        "id": "Tamil", 
        "text": "Tamil"
      },
      {
        "id": "Telugu", 
        "text": "Telugu"
      }
]

var dataProjectType = [
  {"id": "", "text": ""},
  {"id": "recordings", "text": "Recordings"},
  {"id": "validation", "text": "Validation"},
  {"id": "transcriptions", "text": "Speech Transcription and Labeling"},
  // {"id": "crawling", "text": "Crawling"},
  // {"id": "annotation", "text": "Annotation"}
];

$('.dataprojecttype').select2({
  // tags: true,
  placeholder: 'select the type of data project',
  data: dataProjectType
});

$('.datasentencelanguageclass').select2({
  tags: true,
  placeholder: 'Audio Language',
  data: languages,
  allowClear: true
});

$('.recordingssentencelanguageclass').select2({
  tags: true,
  placeholder: 'Audio Language',
  data: languages,
  allowClear: true
});

$('.datatranscriptionscriptclass').select2({
  // tags: true,
  placeholder: 'Transcription Scripts',
  data: scripts,
  allowClear: true,
  // sorter: false
});
  
// partial solution to the select2 multiselect
$("select").on("select2:select", function (evt) {
  var element = evt.params.data.element;
  // console.log(element);
  var $element = $(element);
  $element.detach();
  $(this).append($element);
  $(this).trigger("change");
});

var translationField = 0;

$("#addTranslationLanguageField").click(function(){
    translationField++;

    var drow = '<div class="row removetranslationfield' + translationField + '">';

    var fItems = '<div class="col-md-3"><div class="form-group">'+
                '<select class="form-control" name="Translation Language" required>';
    fItems += '<option value="">Translation Language</option>';

    for (var i = 0; i < languages.length; i++) {
        fItems += '<option value="' + languages[i].text + '">' + languages[i].id + '</option>';
    }
    fItems += '</select></div></div>';

    fItems += '<div class="col-md-3"><div class="form-group">'+
                '<div class="input-group">'+
                '<select class="form-control" name="Translation Script" required>';
    fItems += '<option value="">Translation Script</option>';

    for (var i = 0; i < scripts.length; i++) {
        fItems += '<option value="' + scripts[i].text + '">' + scripts[i].id + '</option>';
    }
    fItems += '</select>';

    fItems += '<div class="input-group-btn">'+
                '<button class="btn btn-danger" type="button" onclick="removeTranslationFields('+ translationField +');">'+
                '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></div></div></div></div>';

    drow += fItems;
    drow += '</div>'
    $(".translationlanguage").append(drow);
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
  var projecttypevalue = document.getElementById("idprojecttype").value;
  // console.log(projecttypevalue, this);
  projectTypeOptions = this.options;
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
    formData.append('deriveFromProjectName', deriveFromProjectName)
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