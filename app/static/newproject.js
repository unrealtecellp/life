var dictionaryFields = [{
    "name": "Pronunciation",
    "value": "Pronunciation"
  },
  {
    "name": "Upload Sound File",
    "value": "Upload Sound File"
  },
  {
    "name": "Upload Movie File",
    "value": "Upload Movie File"
  },
  {
    "name": "Variant",
    "value": "Variant"
  },
  {
    "name": "Allomorph",
    "value": "Allomorph"
  },
  {
    "name": "Source",
    "value": "Source"
  },
  {
    "name": "Additional Metadata Information",
    "value": "Additional Meta Data Information"
  },
  {
    "name": "Upload Field Notebook Scan",
    "value": "Upload Field Notebook Scan"
  },
  {
    "name": "Encyclopedic Information",
    "value": "Encyclopedic Information"
  },
  {
    "name": "Any Additional Information",
    "value": "Any Additional Information"
  }
];

var fieldType = [{
  "name": "text",
  "value": "text"
  },
  {
  "name": "textarea",
  "value": "textarea"
  },
  {
  "name": "multimedia",
  "value": "multimedia"
  }
];

var languages = [
  {"id": "", "text": ""},
  {"id": "Assamese", "text": "Assamese"},
  {"id": "Awadhi", "text": "Awadhi"},
  {"id": "Bangla", "text": "Bangla"},
  {"id": "Bhojpuri", "text": "Bhojpuri"},
  {"id": "Bodo", "text": "Bodo"},
  {"id": "Braj", "text": "Braj"},
  {"id": "Bundeli", "text": "Bundeli"},
  {"id": "Gujarati", "text": "Gujarati"},
  {"id": "Haryanvi", "text": "Haryanvi"},
  {"id": "Hindi", "text": "Hindi"},
  {"id": "Kannada", "text": "Kannada"},
  {"id": "Konkani", "text": "Konkani"},
  {"id": "Magahi", "text": "Magahi"},
  {"id": "Maithili", "text": "Maithili"},
  {"id": "Malayalam", "text": "Malayalam"},
  {"id": "Marathi", "text": "Marathi"},
  {"id": "Meitei", "text": "Meitei"},
  {"id": "Nepali", "text": "Nepali"},
  {"id": "Odia", "text": "Odia"},
  {"id": "Punjabi", "text": "Punjabi"},
  {"id": "Santali", "text": "Santali"},
  {"id": "Tamil", "text": "Tamil"},
  {"id": "Telugu", "text": "Telugu"}
]

var scripts = 
[
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
        "id": "Ol_Chiki", 
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




$(document).ready(function () {
  $('.lexemelanguage').select2({
    tags: true,
    placeholder: 'Lexeme Languages',
    data: languages,
    allowClear: true
  });

  $('.lexemeformscript').select2({
    // tags: true,
    placeholder: 'Lexeme Scripts',
    data: scripts,
    allowClear: true,
    // sorter: false
  });
  
// partial solution to the select2 multiselect
  $("select").on("select2:select", function (evt) {
    var element = evt.params.data.element;
    console.log(element);
    var $element = $(element);
    $element.detach();
    $(this).append($element);
    $(this).trigger("change");
  });

  $('.glosslanguage').select2({
    // tags: true,
    placeholder: 'Gloss Languages',
    data: languages,
    allowClear: true
  });


  $('.transcriptionscript').select2({
    // tags: true,
    placeholder: 'Transcription Scripts',
    data: scripts,
    allowClear: true,
    // sorter: false
  });

  $('.translationlanguage').select2({
    // tags: true,
    placeholder: 'Translation Languages',
    data: languages,
    allowClear: true,
    // sorter: false
  });

  $('.translationscript').select2({
    // tags: true,
    placeholder: 'Translation Scripts',
    data: scripts,
    allowClear: true,
    // sorter: false
  });
  // var fListItems = '<option value="">Field Type</option>';

  // for (var i = 0; i < fieldType.length; i++) {
  //     fListItems += "<option value='" + fieldType[i].value + "'>" + fieldType[i].name + "</option>";
  // } 

  // $("#fieldType1").html(fListItems);
   
});

var glossField = 0;

$("#addGlossField").click(function(){
  glossField++;
  
  var drow = '<div class="row removeglossfield' + glossField + '">';

  var fItems = '<div class="col-md-3"><div class="form-group">'+
              // '<select class="form-control" name="Gloss Language' + glossField + '" required>';
              '<select class="form-control" name="Gloss Language" required>';
  fItems += '<option value="">Translation/Gloss Language</option>';

  for (var i = 0; i < languages.length; i++) {
    fItems += '<option value="' + languages[i].text + '">' + languages[i].id + '</option>';
  }
  fItems += '</select></div></div>';

  fItems += '<div class="col-md-3"><div class="form-group">'+
              '<div class="input-group">'+
              // '<select class="form-control" name="glossScriptField' + glossField + '" required>';
              '<select class="form-control" name="Gloss Script" required>';
  fItems += '<option value="">Translation/Gloss Script</option>';

  for (var i = 0; i < scripts.length; i++) {
    fItems += '<option value="' + scripts[i].text + '">' + scripts[i].id + '</option>';
  }
  fItems += '</select>';

  fItems += '<div class="input-group-btn">'+
            '<button class="btn btn-danger" type="button" onclick="removeGlossFields('+ glossField +');">'+
            '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></div></div></div></div>';

  drow += fItems;
  drow += '</div>'
  $(".Sensefield").append(drow);
});


// remove a interlineargloss element
function removeGlossFields(rid) {
  $(".removeglossfield"+rid).remove();
}

var interlinearGlossField = 0;

$("#addInterlinearGlossField").click(function(){
  interlinearGlossField++;
  
  var drow = '<div class="row removeinterlinearglossfield' + interlinearGlossField + '">';

  var fItems = '<div class="col-md-3"><div class="form-group">'+
              // '<select class="form-control" name="interlinearGlossLangField' + interlinearGlossField + '" required>';
              '<select class="form-control" name="Interlinear Gloss Language" required>';
  fItems += '<option value="">Interlinear Gloss Language</option>';

  for (var i = 0; i < languages.length; i++) {
    fItems += '<option value="' + languages[i].text + '">' + languages[i].id + '</option>';
  }
  fItems += '</select></div></div>';

  fItems += '<div class="col-md-3"><div class="form-group">'+
              '<div class="input-group">'+
              // '<select class="form-control" name="interlinearGlossScriptField' + interlinearGlossField + '" required>';
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

// add new custom element
// var customField = 1;
var customField = 0;

$("#addCustomField").click(function(){
  customField++;
  
  var drow = '<div class="row removecustomfield' + customField + '">';

  var dItems = '<div class="col-md-3"><div class="form-group">'+
              '<input type="text" class="form-control"'+
              ' name="customField' + customField + '" placeholder="Custom Field" required></div></div>';

  var fItems = '<div class="col-md-3"><div class="form-group">'+
              '<div class="input-group">'+
              '<select class="form-control" name="fieldType' + customField + '" required>';
  fItems += '<option value="">Field Type</option>';

  for (var i = 0; i < fieldType.length; i++) {
    fItems += '<option value="' + fieldType[i].value + '">' + fieldType[i].name + '</option>';
  }

  fItems += '</select><div class="input-group-btn">'+
            '<button class="btn btn-danger" type="button" onclick="removeCustomFields('+ customField +');">'+
            '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></div></div></div></div>';

  //ddrow += '</div>';

  drow += dItems + fItems;
  drow += '</div>'
  $(".customfield").append(drow);
});

// remove a custom element
function removeCustomFields(rid) {
  $(".removecustomfield"+rid).remove();
}

// default dictionary fields
function projectForm() {
  var checkFieldValue = '';
  var formFields = '<div class="row">';
  for (var i = 0; i < dictionaryFields.length; i++) {
    if (dictionaryFields[i].name === 'Pronunciation') {
      checkFieldValue = 'text';
    }
    else if (dictionaryFields[i].name.includes('Upload')) {
      checkFieldValue = 'multimedia';
    }
    else {
      checkFieldValue = 'textarea';
    }
    if (dictionaryFields[i].name === 'Pronunciation') {
      formFields += '<div class="col-md-3"><div class="form-check">'+
                    '<input class="form-check-input" type="checkbox" id="' + dictionaryFields[i].name + '"'+ 
                    'value="' + checkFieldValue + '" name="' + dictionaryFields[i].name + '" checked required>'+
                    // '<label style="color: gray" class="form-check-label" for="' + dictionaryFields[i].name + ' ">'+dictionaryFields[i].name + 
                    '<label class="form-check-label" for="' + dictionaryFields[i].name + ' ">'+dictionaryFields[i].name + 
                    '</label>'+
                    '</div></div>';
    }
    else {
      formFields += '<div class="col-md-3"><div class="form-check">'+
                    '<input class="form-check-input" type="checkbox" id="' + dictionaryFields[i].name + '"'+ 
                    'value="' + checkFieldValue + '" name="' + dictionaryFields[i].name + '">'+
                    // '<label style="color: gray" class="form-check-label" for="' + dictionaryFields[i].name + ' ">'+dictionaryFields[i].name + 
                    '<label class="form-check-label" for="' + dictionaryFields[i].name + ' ">'+dictionaryFields[i].name + 
                    '</label></div></div>';
    }
  }
  formFields += '</div>'
  $(".defaultfield").append(formFields);
}

projectForm();
