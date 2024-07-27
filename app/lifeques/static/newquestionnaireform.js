var fieldType = [{
    "name": "text",
    "value": "text"
    },
    {
    "name": "textarea",
    "value": "textarea"
    },
    {
    "name": "file",
    "value": "file"
    }
  ];
  
var languages = [
  {"id": "", "text": ""},
  {"id": "Assamese", "text": "Assamese"},
  {"id": "Angika", "text": "Angika"},
  {"id": "Awadhi", "text": "Awadhi"},
  {"id": "Bajjika", "text": "Bajjika"},
  {"id": "Bangla", "text": "Bangla"},
  {"id": "Bhojpuri", "text": "Bhojpuri"},
  {"id": "Bodo", "text": "Bodo"},
  {"id": "Braj", "text": "Braj"},
  {"id": "Bundeli", "text": "Bundeli"},
  {"id": "Chhattisgarhi", "text": "Chhattisgarhi"},
  {"id": "Chokri", "text": "Chokri"},
  {"id": "Dogri", "text": "Dogri"},
  {"id": "English", "text": "English"},
  {"id": "Gujarati", "text": "Gujarati"},
  {"id": "Haryanvi", "text": "Haryanvi"},
  {"id": "Hindi", "text": "Hindi"},
  {"id": "Kashmiri", "text": "Kashmiri"},
  {"id": "Kannada", "text": "Kannada"},
  {"id": "Khortha", "text": "Khortha"},
  {"id": "Konkani", "text": "Konkani"},
  {"id": "KokBorok", "text": "Kok Borok"},
  {"id": "Magahi", "text": "Magahi"},
  {"id": "Maithili", "text": "Maithili"},
  {"id": "Malayalam", "text": "Malayalam"},
  {"id": "Marathi", "text": "Marathi"},
  {"id": "Meitei", "text": "Meitei"},
  {"id": "Nagamese", "text": "Nagamese"},
  {"id": "Nepali", "text": "Nepali"},
  {"id": "Nyishi", "text": "Nyishi"},
  {"id": "Odia", "text": "Odia"},
  {"id": "Punjabi", "text": "Punjabi"},
  {"id": "Sadri", "text": "Sadri"},
  {"id": "Sanskrit", "text": "Sanskrit"},
  {"id": "Santali", "text": "Santali"},
  {"id": "Sambalpuri", "text": "Sambalpuri"},
  {"id": "Tamil", "text": "Tamil"},
  {"id": "Telugu", "text": "Telugu"},
  {"id": "Toto", "text": "Toto"},
  {"id": "Urdu", "text": "Urdu"},
  {"id": "Azamgarhi", "text": "Azamgarhi"},
  {"id": "Kannauji", "text": "Kannauji"},
  {"id": "Marwari", "text": "Marwari"},
  {"id": "TaiAiton", "text": "Tai Aiton"},
  {"id": "Spiti", "text": "Spiti"},
  {"id": "Karbi", "text": "Karbi"},
  {"id": "Paite", "text": "Paite"},
  {"id": "Chiru", "text": "Chiru"},
  {"id": "Chothe", "text": "Chothe"},
  {"id": "Purum", "text": "Purum"},
  {"id": "Markodi", "text": "Markodi"},
  {"id": "Byari", "text": "Byari"},
  {"id": "Tanghkul", "text": "Tanghkul"},
  {"id": "Chiru", "text": "Chiru"},
  {"id": "Bangru", "text": "Bangru"},
  {"id": "Ahirwati", "text": "Ahirwati"},
  {"id": "Sumi", "text": "Sumi"},
  {"id": "Sylheti", "text": "Sylheti"}
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
      },
      {
        "id": "Toto", 
        "text": "Toto"
      },
      {
        "id": "LikTai", 
        "text": "Lik-Tai"
      }
]

var QuestionnaireDomain = [
  // {"id": "", "text": ""},
  {"id": "General", "text": "General"},
  {"id": "Agriculture", "text": "Agriculture"},
  {"id": "Education", "text": "Education"},
  {"id": "Science-Technology", "text": "Science-Technology"},
  {"id": "Culture", "text": "Culture"},
  {"id": "Lifecycle", "text": "Lifecycle"},
  {"id": "Healthcare", "text": "Healthcare"},
  {"id": "Sports", "text": "Sports"},
  {"id": "General-Oral-History", "text": "General-Oral-History"}
];


var ElicitationMethod = [
  // {"id": "", "text": ""},
  {"id": "Conversation", "text": "Conversation"},
  {"id": "Interview", "text": "Interview"},
  {"id": "Narration", "text": "Narration"},
  {"id": "Picture Book Narration", "text": "Picture Book Narration"},
  {"id": "Role-Play", "text": "Role-Play"},
  {"id": "Translation", "text": "Translation"},
  {"id": "Video Narration", "text": "Video Narration"}  
];


// var target = [
//   {"id": "", "text": ""},
//   {"id": "Anaphors", "text": "Anaphors"},
//   {"id": "Case", "text": "Case"},
//   {"id": "Oral", "text": "Oral"}

// ];

  
var promptType = [
  // {"id": "", "text": ""},
  {"id": "Audio", "text": "Audio"},
  {"id": "Image", "text": "Image"},
  {"id": "Multimedia", "text": "Multimedia"}
];

// $('.promptlanguage').select2({
//   tags: true,
//   placeholder: 'Prompt Language',
//   data: languages,
//   allowClear: true
// });

// $('.promptlangscript').select2({
//   tags: true,
//   placeholder: 'Prompt Language Script',
//   data: scripts,
//   allowClear: true
// });
$('.translang').select2({
  placeholder: 'Transcription Language',
  data: languages,
  allowClear: true,
  // console.log( "ready!" )
});

$('.transscript').select2({
  placeholder: 'Transcription Script',
  data: scripts,
  allowClear: true,
  // console.log( "ready!" )
});

$('.prompttype').select2({
  placeholder: '--Prompt Type--',
  data: promptType,
  allowClear: true,
  // console.log( "ready!" )
});

$('.questionnairedomain').select2({
  tags: true,
  placeholder: '-- Questionnire Domain --',
  data: QuestionnaireDomain  ,
  allowClear: true
});

$('.elicitationmethod').select2({
  tags: true,
  placeholder: '--Elicitation Method--',
  data: ElicitationMethod ,
  allowClear: true,
  // console.log( "ready!" )
});

// $('.target').select2({
//   tags: true,
//   placeholder: '-- Target --',
//   data: target,
//   allowClear: true,
//   // console.log( "ready!" )
// });

// For checking and unchecking the instructions and transcription checkbox based on
// audio, mm or image is checked or not in new questionnaire form
$(document).ready(function(){
  $(document).on('change', 'input[type="checkbox"]', function(){
// $('input[type="checkbox"]').click(function(){
    var checkId = $(this).attr('id');
    var both = true;
    if (checkId.indexOf("idprompt") > -1) {
      var checkIdNumber = checkId.substring(checkId.indexOf("_"));
      if (checkId.indexOf("idpromptaudio") > -1) {
        var transboxId = "idincludeaudiotranscription"+checkIdNumber;
        console.log('transboxId', transboxId);
        var transCheckbox = document.getElementById(transboxId);
        console.log('transboxCheckbox', transCheckbox);

        var instboxId = "idincludeaudioinstruction"+checkIdNumber;
        var instCheckbox = document.getElementById(instboxId);
        
      }
      else if (checkId.indexOf("idpromptmm") > -1) {
        var transboxId = "idincludemmtranscription"+checkIdNumber;
        var transCheckbox = document.getElementById(transboxId);

        var instboxId = "idincludemminstruction"+checkIdNumber;
        var instCheckbox = document.getElementById(instboxId);
      }
      else {
        var instboxId = "idincludeimageinstruction"+checkIdNumber;
        var instCheckbox = document.getElementById(instboxId);
        both = false;
      }
      
      if (this.checked) {
        if (both) {
          transCheckbox.disabled=false;
        }
        instCheckbox.disabled=false;
      }
      else {
        if (both) {
          transCheckbox.disabled=true;
        }
        instCheckbox.disabled=true;
      }
    }
  })
});

var langScriptPromptField = 0;
$("#addpromptlangscripts").click(function(){
  langScriptPromptField++;
  
  var drow = '<div class="row removelangScriptPromptfield' + langScriptPromptField + '">'+
  '<div class="row">';

  var fItems = '<div class="col-md-3"><div class="form-group">'+
              '<select class="form-control" name="Language_' + langScriptPromptField + '"  required>';
  fItems += '<option value="" selected disabled>Language</option>';

  for (var i = 0; i < languages.length; i++) {
    if (languages[i].id !== '' && languages[i].text !== '') {
      fItems += '<option value="' + languages[i].text + '">' + languages[i].id + '</option>';
    }
  }
  fItems += '</select></div></div>';

  fItems += '<div class="col-md-3"><div class="form-group">'+
              '<div class="input-group">'+
              '<select class="form-control" name="Script_' + langScriptPromptField + '"  required>';
  fItems += '<option value="" selected disabled>Script</option>';

  for (var i = 0; i < scripts.length; i++) {
    if (scripts[i].id !== '' && scripts[i].text) {
      fItems += '<option value="' + scripts[i].text + '">' + scripts[i].id + '</option>';
    }
  }
  fItems += '</select>';

  fItems += '<div class="input-group-btn">'+
            '<button class="btn btn-danger" type="button" onclick="removelangScriptPromptFields('+ langScriptPromptField +');">'+
            '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></div></div></div></div></div>';


  fItems += '<div class="row"><div class="col-md-3"><div class="form-group">'+
  '<input class="mmcheck" type="checkbox" id="idpromptaudio_' + langScriptPromptField + '" name="Audio_' + langScriptPromptField + '">'+
  '<label for="idpromptaudio_' + langScriptPromptField + '">Audio</label>'+
  '<input type="checkbox" id="idincludeaudiotranscription_' + langScriptPromptField + '" name="TranscriptionAudio_' + langScriptPromptField + '" disabled>'+
  '<label for="idincludeaudiotranscription_' + langScriptPromptField + '">Include Transcription</label>'+
  '<input type="checkbox" id="idincludeaudioinstruction_' + langScriptPromptField + '" name="InstructionAudio_' + langScriptPromptField + '" disabled>'+
  '<label for="idincludeaudioinstruction_' + langScriptPromptField + '">Include Instruction</label><br>'+
  '</div></div>';

  fItems += '<div class="col-md-3"><div class="form-group">'+
  '<input class="mmcheck" type="checkbox" id="idpromptmm_' + langScriptPromptField + '"name="Multimedia_' + langScriptPromptField + '">'+
  '<label for="idpromptmm_' + langScriptPromptField + '">Multimedia</label>'+
  '<input type="checkbox" id="idincludemmtranscription_' + langScriptPromptField + '" name="TranscriptionMM_' + langScriptPromptField + '" disabled>'+
  '<label for="idincludemmtranscription_' + langScriptPromptField + '">Include Transcription</label>'+
  '<input type="checkbox" id="idincludemminstruction_' + langScriptPromptField + '" name="InstructionMM_' + langScriptPromptField + '" disabled>'+
  '<label for="idincludemminstruction_' + langScriptPromptField + '">Include Instruction</label>'+
  '</div></div>';

  fItems += '<div class="col-md-3"><div class="form-group">'+
  '<input class="mmcheck" type="checkbox" id="idpromptimage_' + langScriptPromptField + '" name="Image_' + langScriptPromptField + '">'+
  '<label for="idpromptimage_' + langScriptPromptField + '">Image</label>'+
  '<input type="checkbox" id="idincludeimageinstruction_' + langScriptPromptField + '" name="InstructionImage_' + langScriptPromptField + '" disabled>'+
  '<label for="idincludeimageinstruction_' + langScriptPromptField + '">Include Instruction</label>'+
  '</div></div>';

  
  drow += fItems;
  drow += '</div>'
  $(".promptlangscripts").append(drow);
});

var transcriptioncheckbox = document.getElementById("idincludetranscription")
var instructioncheckbox = document.getElementById("idincludeinstruction")

$('#idprompttype').on('select2:select', function (e) {
  var data = e.params.data;
  // console.log(data);
  // console.log(data['text']);
  prompttype = data['text']
  if (prompttype === 'Audio' || prompttype === 'Multimedia') {
    transcriptioncheckbox.disabled = false;
  }
  instructioncheckbox.disabled = false;
});

$('#idprompttype').on('select2:unselect', function (e) {
  var data = e.params.data;
  // console.log(data);
  // console.log(data['text']);
  prompttype = data['text']
  if (prompttype === 'Audio' || prompttype === 'Multimedia') {
    transcriptioncheckbox.disabled = true;
  }
  instructioncheckbox.disabled = true;
});


transcriptioncheckbox.addEventListener('change', function() {
  translangscriptid =  document.getElementById("idtranscriptionlangscript")
  if (this.checked) {
    translangscriptid.style.display = "block";
  } else {
    translangscriptid.style.display = "none";
  }
});

var quescustomField = 0;
$("#quesaddCustomField").click(function(){
  quescustomField++;
  
  var drow = '<div class="row removequescustomfield' + quescustomField + '">';

  var dItems = '<div class="col-md-3"><div class="form-group">'+
              '<input type="text" class="form-control"'+
              ' name="quescustomField' + quescustomField + '" placeholder="Custom Field" required></div></div>';

  var fItems = '<div class="col-md-3"><div class="form-group">'+
              '<div class="input-group">'+
              '<select class="form-control" name="fieldType' + quescustomField + '" required>';
  fItems += '<option value="">Field Type</option>';

  for (var i = 0; i < fieldType.length; i++) {
    fItems += '<option value="' + fieldType[i].value + '">' + fieldType[i].name + '</option>';
  }

  fItems += '</select>';

  fItems += '<div class="input-group-btn">'+
            '<button class="btn btn-danger" type="button" onclick="removequesCustomFields('+ quescustomField +');">'+
            '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></div></div></div></div>';

  //ddrow += '</div>';

  drow += dItems + fItems;
  drow += '</div>'
  $(".quescustomfield").append(drow);
  // console.log(drow)
});

function removelangScriptPromptFields(rid) {
    $(".removelangScriptPromptfield"+rid).remove();
  }

// remove a custom element
function removequesCustomFields(rid) {
  $(".removequescustomfield"+rid).remove();
}
