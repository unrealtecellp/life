var languages = [

  {"id": "", "text": ""},
  {"id": "Assamese", "text": "Assamese"},
  {"id": "Awadhi", "text": "Awadhi"},
  {"id": "Bangla", "text": "Bangla"},
  {"id": "Bhojpuri", "text": "Bhojpuri"},
  {"id": "Bodo", "text": "Bodo"},
  {"id": "Braj", "text": "Braj"},
  {"id": "Bundeli", "text": "Bundeli"},
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
  // {"id": "", "text": ""},
  {"id": "transcriptions", "text": "Transcription"}
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

$("#idprojecttype").change(function(){
  var projecttypevalue = document.getElementById("idprojecttype").value;
  console.log(projecttypevalue)
  if (projecttypevalue === 'transcriptions') {
    var x = document.getElementById("transcriptiontypeproject");
    if (x.style.display === "none") {
        x.style.display = "block";
    }
  }
});

