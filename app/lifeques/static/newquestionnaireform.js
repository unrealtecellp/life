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
  
var promptType = [
  // {"id": "", "text": ""},
  {"id": "Audio", "text": "Audio"},
  {"id": "Image", "text": "Image"},
  {"id": "Multimedia", "text": "Multimedia"}
];

$('.translang').select2({
  placeholder: 'Transcription Language',
  data: getJsonfileData('languages'),
  allowClear: true,
  // console.log( "ready!" )
});

$('.transscript').select2({
  placeholder: 'Transcription Script',
  data: getJsonfileData('scripts'),
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
  placeholder: 'Questionnaire Domain',
  data: getJsonfileData('questionnaire_domain'),
  allowClear: true
});

$('.elicitationmethod').select2({
  tags: true,
  placeholder: 'Elicitation Method',
  data: getJsonfileData('elicitation_method'),
  allowClear: true,
  // console.log( "ready!" )
});

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
        // console.log('transboxId', transboxId);
        var transCheckbox = document.getElementById(transboxId);
        // console.log('transboxCheckbox', transCheckbox);

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
  
  var drow = '';
  // drow += '<div class="form-group">';
  drow += '<div class="removelangScriptPromptfield' + langScriptPromptField + '">'+
  '<div class="row">';

  var fItems = '<div class="col-md-3"><div class="form-group">'+
              '<select class="form-control" id="language_id_' + langScriptPromptField + '" name="Language_' + langScriptPromptField + '" required>';
  fItems += '<option value="" selected disabled>Language</option>';

  // for (var i = 0; i < languages.length; i++) {
  //   if (languages[i].id !== '' && languages[i].text !== '') {
  //     fItems += '<option value="' + languages[i].text + '">' + languages[i].id + '</option>';
  //   }
  // }
  fItems += '</select></div></div>';

  fItems += '<div class="col-md-3"><div class="form-group">'+
              '<div class="input-group">'+
              '<select class="form-control" id="script_id_' + langScriptPromptField + '" name="Script_' + langScriptPromptField + '" required>';
  fItems += '<option value="" selected disabled>Script</option>';

  // for (var i = 0; i < scripts.length; i++) {
  //   if (scripts[i].id !== '' && scripts[i].text) {
  //     fItems += '<option value="' + scripts[i].text + '">' + scripts[i].id + '</option>';
  //   }
  // }
  fItems += '</select>';

  fItems += '<div class="input-group-btn">'+
            '<button class="btn btn-sm btn-danger" type="button" onclick="removelangScriptPromptFields('+ langScriptPromptField +');">'+
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
  drow += '</div>';
  // drow += '</div>';
  $(".promptlangscripts").append(drow);
  $('#language_id_' + langScriptPromptField).select2({
    placeholder: 'Language',
    data: getJsonfileData('languages'),
    // tags: true,
    // allowClear: true
  });
  $('#script_id_' + langScriptPromptField).select2({
    placeholder: 'Script',
    data: getJsonfileData('scripts'),
    // tags: true,
    // allowClear: true
  });
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
