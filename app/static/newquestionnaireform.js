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
          "id": "Meitei-Mayek", 
          "text": "Meitei Mayek"
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
  

var glossField = 0;

$("#addpromptlangscripts").click(function(){
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



// remove a interlineargloss element
function removeGlossFields(rid) {
    $(".removeglossfield"+rid).remove();
  }

// remove a custom element
function removeCustomFields(rid) {
  $(".removecustomfield"+rid).remove();
}