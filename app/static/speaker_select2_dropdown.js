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
  { "id": "", "text": "" },
  { "id": "Assamese", "text": "Assamese" },
  { "id": "Angika", "text": "Angika" },
  { "id": "Awadhi", "text": "Awadhi" },
  { "id": "Bajjika", "text": "Bajjika" },
  { "id": "Bangla", "text": "Bangla" },
  { "id": "Bhojpuri", "text": "Bhojpuri" },
  { "id": "Bodo", "text": "Bodo" },
  { "id": "Braj", "text": "Braj" },
  { "id": "Bundeli", "text": "Bundeli" },
  { "id": "Chhattisgarhi", "text": "Chhattisgarhi" },
  { "id": "Chokri", "text": "Chokri" },
  { "id": "Dogri", "text": "Dogri" },
  { "id": "English", "text": "English" },
  { "id": "Gujarati", "text": "Gujarati" },
  { "id": "Haryanvi", "text": "Haryanvi" },
  { "id": "Hindi", "text": "Hindi" },
  { "id": "Kashmiri", "text": "Kashmiri" },
  { "id": "Kannada", "text": "Kannada" },
  { "id": "Khortha", "text": "Khortha" },
  { "id": "Konkani", "text": "Konkani" },
  { "id": "KokBorok", "text": "Kok Borok" },
  { "id": "Magahi", "text": "Magahi" },
  { "id": "Maithili", "text": "Maithili" },
  { "id": "Malayalam", "text": "Malayalam" },
  { "id": "Marathi", "text": "Marathi" },
  { "id": "Meitei", "text": "Meitei" },
  { "id": "Nagamese", "text": "Nagamese" },
  { "id": "Nepali", "text": "Nepali" },
  { "id": "Nyishi", "text": "Nyishi" },
  { "id": "Odia", "text": "Odia" },
  { "id": "Punjabi", "text": "Punjabi" },
  { "id": "Sadri", "text": "Sadri" },
  { "id": "Sanskrit", "text": "Sanskrit" },
  { "id": "Santali", "text": "Santali" },
  { "id": "Sambalpuri", "text": "Sambalpuri" },
  { "id": "Tamil", "text": "Tamil" },
  { "id": "Telugu", "text": "Telugu" },
  { "id": "Toto", "text": "Toto" },
  { "id": "Urdu", "text": "Urdu" }
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
      "id": "Meitei_Mayek",
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
    },
    {
      "id": "Toto",
      "text": "Toto"
    }
  ];

var OtherLanguagesSpeakerCouldSpeak =
  [
    { "id": "", "text": "" },
    { "id": "Assamese", "text": "Assamese" },
    { "id": "Angika", "text": "Angika" },
    { "id": "Awadhi", "text": "Awadhi" },
    { "id": "Bajjika", "text": "Bajjika" },
    { "id": "Bangla", "text": "Bangla" },
    { "id": "Bhojpuri", "text": "Bhojpuri" },
    { "id": "Bodo", "text": "Bodo" },
    { "id": "Braj", "text": "Braj" },
    { "id": "Bundeli", "text": "Bundeli" },
    { "id": "Chhattisgarhi", "text": "Chhattisgarhi" },
    { "id": "Chokri", "text": "Chokri" },
    { "id": "Dogri", "text": "Dogri" },
    { "id": "English", "text": "English" },
    { "id": "Gujarati", "text": "Gujarati" },
    { "id": "Haryanvi", "text": "Haryanvi" },
    { "id": "Hindi", "text": "Hindi" },
    { "id": "Kashmiri", "text": "Kashmiri" },
    { "id": "Kannada", "text": "Kannada" },
    { "id": "Khortha", "text": "Khortha" },
    { "id": "Konkani", "text": "Konkani" },
    { "id": "KokBorok", "text": "Kok Borok" },
    { "id": "Magahi", "text": "Magahi" },
    { "id": "Maithili", "text": "Maithili" },
    { "id": "Malayalam", "text": "Malayalam" },
    { "id": "Marathi", "text": "Marathi" },
    { "id": "Meitei", "text": "Meitei" },
    { "id": "Nagamese", "text": "Nagamese" },
    { "id": "Nepali", "text": "Nepali" },
    { "id": "Nyishi", "text": "Nyishi" },
    { "id": "Odia", "text": "Odia" },
    { "id": "Punjabi", "text": "Punjabi" },
    { "id": "Sadri", "text": "Sadri" },
    { "id": "Sanskrit", "text": "Sanskrit" },
    { "id": "Santali", "text": "Santali" },
    { "id": "Sambalpuri", "text": "Sambalpuri" },
    { "id": "Tamil", "text": "Tamil" },
    { "id": "Telugu", "text": "Telugu" },
    { "id": "Toto", "text": "Toto" },
    { "id": "Urdu", "text": "Urdu" }
  ]

var EducationMedium =
  [
    { "id": "", "text": "" },
    { "id": "Assamese", "text": "Assamese" },
    { "id": "Angika", "text": "Angika" },
    { "id": "Awadhi", "text": "Awadhi" },
    { "id": "Bajjika", "text": "Bajjika" },
    { "id": "Bangla", "text": "Bangla" },
    { "id": "Bhojpuri", "text": "Bhojpuri" },
    { "id": "Bodo", "text": "Bodo" },
    { "id": "Braj", "text": "Braj" },
    { "id": "Bundeli", "text": "Bundeli" },
    { "id": "Chhattisgarhi", "text": "Chhattisgarhi" },
    { "id": "Chokri", "text": "Chokri" },
    { "id": "Dogri", "text": "Dogri" },
    { "id": "English", "text": "English" },
    { "id": "Gujarati", "text": "Gujarati" },
    { "id": "Haryanvi", "text": "Haryanvi" },
    { "id": "Hindi", "text": "Hindi" },
    { "id": "Kashmiri", "text": "Kashmiri" },
    { "id": "Kannada", "text": "Kannada" },
    { "id": "Khortha", "text": "Khortha" },
    { "id": "Konkani", "text": "Konkani" },
    { "id": "KokBorok", "text": "Kok Borok" },
    { "id": "Magahi", "text": "Magahi" },
    { "id": "Maithili", "text": "Maithili" },
    { "id": "Malayalam", "text": "Malayalam" },
    { "id": "Marathi", "text": "Marathi" },
    { "id": "Meitei", "text": "Meitei" },
    { "id": "Nagamese", "text": "Nagamese" },
    { "id": "Nepali", "text": "Nepali" },
    { "id": "Nyishi", "text": "Nyishi" },
    { "id": "Odia", "text": "Odia" },
    { "id": "Punjabi", "text": "Punjabi" },
    { "id": "Sadri", "text": "Sadri" },
    { "id": "Sanskrit", "text": "Sanskrit" },
    { "id": "Santali", "text": "Santali" },
    { "id": "Sambalpuri", "text": "Sambalpuri" },
    { "id": "Tamil", "text": "Tamil" },
    { "id": "Telugu", "text": "Telugu" },
    { "id": "Toto", "text": "Toto" },
    { "id": "Urdu", "text": "Urdu" }
  ]

var LdcilEducationLevel =
  [
    { "id": "", "text": "" },
    { "id": "School", "text": "School" },
    { "id": "Bachelor", "text": "Bachelor" },
    { "id": "Master", "text": "Master" }
  ];

var EducationLevel =
  [
    { "id": "", "text": "" },
    { "id": "No Schooling", "text": "No Schooling" },
    { "id": "Upto 12th", "text": "Upto 12ᵗʰ" },
    { "id": "Graduate", "text": "Graduate" },
    { "id": "Post-Graduate", "text": "Post-Graduate" },
    { "id": "Above PG", "text": "Above PG" },
  ];

var gender =
  [
    { "id": "", "text": "" },
    { "id": "Female", "text": "Female" },
    { "id": "Male", "text": "Male" },
    { "id": "Non-Binary", "text": "Non-Binary" }
  ];

var AgeGroup = [
  { "id": "", "text": "" },
  { "id": "18-30", "text": "18-30" },
  { "id": "30-45", "text": "30-45" },
  { "id": "45-60", "text": "45-60" },
  { "id": "60+", "text": "60+" }
];

var LdcilAgeGroup = [
  { "id": "", "text": "" },
  { "id": "16To20", "text": "16To20" },
  { "id": "21To50", "text": "21To50" },
  { "id": "Above50", "text": "Above50" }
];

var TypeOfCity = [
  { "id": "", "text": "" },
  { "id": "Town", "text": "Town" },
  { "id": "Village", "text": "Village" },
  { "id": "City", "text": "City" }
];

var audioSource = [
  { "id": "", "text": "" },
  { "id": "field", "text": "Field" },
  { "id": "internet", "text": "Internet" }
];

var metadataSchema = [
  { "id": "", "text": "" },
  { "id": "speed", "text": "SpeeD-IL" },
  { "id": "ldcil", "text": "LDC-IL " }
];

var audioInterntSources = [
  { "id": "", "text": "" },
  { "id": "youtube", "text": "Youtube" },
  // {"id": "facebook", "text": "Facebook"}
];

var downloadFormats = [
  { "id": "textgrid", "text": "Praat TextGrid" },
  { "id": "csv", "text": "CSV" },
  { "id": "tsv", "text": "TSV" },
  { "id": "json", "text": "JSON" },
  { "id": "xlsx", "text": "XLSX" },
  { "id": "latex", "text": "LaTeX" },
  { "id": "html", "text": "HTML" },
  { "id": "markdown", "text": "Markdown" }
]

var transcriptionBy = [
  { "id": "", "text": "" },
  { "id": "latest", "text": "Latest" },
  { "id": "mytranscription", "text": "My Transcriptions" }
]

var automationTaskTypes = [
  { "id": "", "text": "" },
  { "id": "Transcription", "text": "Transcription" },
  { "id": "Translation", "text": "Translation" },
  { "id": "Gloss", "text": "Gloss" }
]

var glossingModels = [
  { "id": "stanza", "text": "Stanza Model" }
]

var freeTranslationLanguages = [
  { "id": "English-Latin", "text": "English-Latin" }
]

var asrmodels = [{
  "text": "Bhashini (ULCA)",
  "id": "bhashini"
}, {
  "text": "HF Local",
  "id": "hfpipeline"
},
{
  "text": "HF Inference API",
  "id": "hfinference"
},
{
  "text": "Others",
  "id": "other"
},
];

var boundaryLevels = [{
  "text": "",
  "id": ""
},
{
  "text": "Sentence",
  "id": "sentence"
},
{
  "text": "Word",
  "id": "word"
},
{
  "text": "Word Segment (only for Whisper)",
  "id": "wordseg"
},
{
  "text": "Character (not for whisper)",
  "id": "character"
}
];

// var QuestionnaireDomain = [
//   {"id": "", "text": ""},
//   {"id": "General", "text": "General"},
//   {"id": "Agriculture", "text": "Agriculture"},
//   {"id": "Science-Technology", "text": "Science-Technology"},
//   {"id": "Education", "text": "Education"}
// ];


// var ElicitationMethod = [
//   {"id": "", "text": ""},
//   {"id": "Narration", "text": "Narration"},
//   {"id": "Translation", "text": "Translation"},
//   {"id": "Role-Play", "text": "Role-Play"},
//   {"id": "Interview", "text": "Interview"},
//   {"id": "Picture Book Narration", "text": "Picture Book Narration"},
//   {"id": "Video Narration", "text": "Video Narration"},
//   {"id": "Conversation", "text": "Conversation"}
// ];


// var target = [
//   {"id": "", "text": ""},
//   {"id": "Anaphors", "text": "Anaphors"},
//   {"id": "Case", "text": "Case"},
//   {"id": "Oral", "text": "Oral"}

// ];

// var task = [
//   {"id": "", "text": ""},
//   {"id": "SPEECH_DATA_COLLECTION", "text": "Recording"},
//   {"id": "SPEECH_VERIFICATION", "text": "Verification of Recordings"},
//   {"id": "SPEECH_TRANSCRIPTION", "text": "Transcription of Recordings"}
// ];

// var accesscodefor = [
//   {"id": "", "text": ""},
//   {"id": "0", "text": "Data Collection Using Karya"}
//   //{"id": "1", "text": "Syncing Karya Recording with LiFE"}
// ];

// $(document).ready(function () {
//   $.getJSON(('/karyaext/getsharelevel'), {
//     // asycaccesscode:String(accode)
//     }, function(data) {

//       // Add Syncing Option for people with add and above privileges
//       console.log(data)
//       var shareLevel = data.shareinfo.sharemode
//       if (shareLevel > 2) {
//         accesscodefor.push({"id": "1", "text": "Syncing Karya Recording with LiFE"})
//       }
//       console.log(accesscodefor)


//       $('.typeofcity').select2({
//         // tags: true,
//         placeholder: '--Type Of City:--',
//         data: TypeOfCity ,
//         allowClear: true,
//         // console.log( "ready!" )
//       });

//       $('#idaccesscodefor').select2({
//         placeholder: '--Access Code For--',
//         data: accesscodefor,
//         // allowClear: true,
//         // console.log( "ready!" )
//       });

//       $('#idtask').select2({
//         placeholder: '--Task--',
//         data: task,
//         allowClear: true,
//         // console.log( "ready!" )
//       });

//       $('.target').select2({
//         tags: true,
//         placeholder: '-- Target --',
//         data: target ,
//         allowClear: true,
//         // console.log( "ready!" )
//       });

//       $('.age').select2({
//         // tags: true,
//         placeholder: '--Age Group--',
//         data:  AgeGroup ,
//         allowClear: true
//       });

//       $('.gender').select2({
//         // tags: true,
//         placeholder: '--Gender--',
//         data:  gender,
//         allowClear: true
//       });

//       $('.educationlvl').select2({
//         // tags: true,
//         placeholder: '-- Educational Level --',
//         data:  EducationLevel ,
//         allowClear: true
//       });

//       $('.educationmediumafter12').select2({
//         tags: true,
//         placeholder: '-- Medium Of Education (After 12ᵗʰ) --',
//         data:  EducationMedium ,
//         allowClear: true
//       });

//       $('.educationmediumupto12').select2({
//         tags: true,
//         placeholder: '-- Medium Of Education (Upto 12ᵗʰ) --',
//         data: EducationMedium ,
//         allowClear: true
//       });

//       $('.speakerspeaklanguage').select2({
//         tags: true,
//         placeholder: '-- Other Languages Speaker Could Speak --',
//         data: OtherLanguagesSpeakerCouldSpeak,
//         allowClear: true
//       });

//       $('.transcriptionscript').select2({
//       tags: true,
//       placeholder: '-- Transcription Scripts --',
//       data: scripts,
//       allowClear: true,
//       // sorter: false 
//     });

//     // $('.lexemelanguage').select2({
//     //   // tags: true,
//     //   placeholder: 'Lexeme Languages',
//     //   data: languages,
//     //   allowClear: true
//     // });

//     // $('.lexemeformscript').select2({
//     //   tags: true,
//     //   placeholder: 'Lexeme Scripts',
//     //   data: scripts,
//     //   allowClear: true,
//     //   // sorter: false
//     // });

//     // // partial solution to the select2 multiselect
//     // $("select").on("select2:select", function (evt) {
//     //   var element = evt.params.data.element;
//     //   console.log(element);
//     //   var $element = $(element);
//     //   $element.detach();
//     //   $(this).append($element);
//     //   $(this).trigger("change");
//     // });

//     // $('.glosslanguage').select2({
//     //   // tags: true,
//     //   placeholder: 'Gloss Languages',
//     //   data: languages,
//     //   allowClear: true
//     // });


//     // $('.transcriptionscript').select2({
//     //   // tags: true,
//     //   placeholder: 'Transcription Scripts',
//     //   data: scripts,
//     //   allowClear: true,
//     //   // sorter: false
//     // });

//     // $('.translationlanguage').select2({
//     //   // tags: true,
//     //   placeholder: 'Translation Languages',
//     //   data: languages,
//     //   allowClear: true,
//     //   // sorter: false
//     // });

//     // $('.translationscript').select2({
//     //   // tags: true,
//     //   placeholder: 'Translation Scripts',
//     //   data: scripts,
//     //   allowClear: true,
//     //   // sorter: false
//     // });
//     // var fListItems = '<option value="">Field Type</option>';

//     // for (var i = 0; i < fieldType.length; i++) {
//     //     fListItems += "<option value='" + fieldType[i].value + "'>" + fieldType[i].name + "</option>";
//     // } 

//     // $("#fieldType1").html(fListItems);
//   });
// });

var glossField = 0;

$("#addGlossField").click(function () {
  glossField++;

  var drow = '<div class="row removeglossfield' + glossField + '">';

  var fItems = '<div class="col-md-3"><div class="form-group">' +
    // '<select class="form-control" name="Gloss Language' + glossField + '" required>';
    '<select class="form-control" name="Gloss Language" required>';
  fItems += '<option value="">Translation/Gloss Language</option>';

  for (var i = 0; i < languages.length; i++) {
    fItems += '<option value="' + languages[i].text + '">' + languages[i].id + '</option>';
  }
  fItems += '</select></div></div>';

  fItems += '<div class="col-md-3"><div class="form-group">' +
    '<div class="input-group">' +
    // '<select class="form-control" name="glossScriptField' + glossField + '" required>';
    '<select class="form-control" name="Gloss Script" required>';
  fItems += '<option value="">Translation/Gloss Script</option>';

  for (var i = 0; i < scripts.length; i++) {
    fItems += '<option value="' + scripts[i].text + '">' + scripts[i].id + '</option>';
  }
  fItems += '</select>';

  fItems += '<div class="input-group-btn">' +
    '<button class="btn btn-danger" type="button" onclick="removeGlossFields(' + glossField + ');">' +
    '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></div></div></div></div>';

  drow += fItems;
  drow += '</div>'
  $(".Sensefield").append(drow);
});


// remove a interlineargloss element
function removeGlossFields(rid) {
  $(".removeglossfield" + rid).remove();
}

var interlinearGlossField = 0;

$("#addInterlinearGlossField").click(function () {
  interlinearGlossField++;

  var drow = '<div class="row removeinterlinearglossfield' + interlinearGlossField + '">';

  var fItems = '<div class="col-md-3"><div class="form-group">' +
    // '<select class="form-control" name="interlinearGlossLangField' + interlinearGlossField + '" required>';
    '<select class="form-control" name="Interlinear Gloss Language" required>';
  fItems += '<option value="">Interlinear Gloss Language</option>';

  for (var i = 0; i < languages.length; i++) {
    fItems += '<option value="' + languages[i].text + '">' + languages[i].id + '</option>';
  }
  fItems += '</select></div></div>';

  fItems += '<div class="col-md-3"><div class="form-group">' +
    '<div class="input-group">' +
    // '<select class="form-control" name="interlinearGlossScriptField' + interlinearGlossField + '" required>';
    '<select class="form-control" name="Interlinear Gloss Script" required>';
  fItems += '<option value="">Interlinear Gloss Script</option>';

  for (var i = 0; i < scripts.length; i++) {
    fItems += '<option value="' + scripts[i].text + '">' + scripts[i].id + '</option>';
  }
  fItems += '</select>';

  fItems += '<div class="input-group-btn">' +
    '<button class="btn btn-danger" type="button" onclick="removeInterlinearGlossFields(' + interlinearGlossField + ');">' +
    '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></div></div></div></div>';

  drow += fItems;
  drow += '</div>'
  $(".interlinearglossfield").append(drow);
});


// remove a interlineargloss element
function removeInterlinearGlossFields(rid) {
  $(".removeinterlinearglossfield" + rid).remove();
}

// add new custom element
// var customField = 1;
var customField = 0;

$("#addCustomField").click(function () {
  customField++;

  var drow = '<div class="row removecustomfield' + customField + '">';

  var dItems = '<div class="col-md-3"><div class="form-group">' +
    '<input type="text" class="form-control"' +
    ' name="customField' + customField + '" placeholder="Custom Field" required></div></div>';

  var fItems = '<div class="col-md-3"><div class="form-group">' +
    '<div class="input-group">' +
    '<select class="form-control" name="fieldType' + customField + '" required>';
  fItems += '<option value="">Field Type</option>';

  for (var i = 0; i < fieldType.length; i++) {
    fItems += '<option value="' + fieldType[i].value + '">' + fieldType[i].name + '</option>';
  }

  fItems += '</select><div class="input-group-btn">' +
    '<button class="btn btn-danger" type="button" onclick="removeCustomFields(' + customField + ');">' +
    '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></div></div></div></div>';

  //ddrow += '</div>';

  drow += dItems + fItems;
  drow += '</div>'
  $(".customfield").append(drow);
});

// remove a custom element
function removeCustomFields(rid) {
  $(".removecustomfield" + rid).remove();
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
      formFields += '<div class="col-md-3"><div class="form-check">' +
        '<input class="form-check-input" type="checkbox" id="' + dictionaryFields[i].name + '"' +
        'value="' + checkFieldValue + '" name="' + dictionaryFields[i].name + '" checked required>' +
        // '<label style="color: gray" class="form-check-label" for="' + dictionaryFields[i].name + ' ">'+dictionaryFields[i].name + 
        '<label class="form-check-label" for="' + dictionaryFields[i].name + ' ">' + dictionaryFields[i].name +
        '</label>' +
        '</div></div>';
    }
    else {
      formFields += '<div class="col-md-3"><div class="form-check">' +
        '<input class="form-check-input" type="checkbox" id="' + dictionaryFields[i].name + '"' +
        'value="' + checkFieldValue + '" name="' + dictionaryFields[i].name + '">' +
        // '<label style="color: gray" class="form-check-label" for="' + dictionaryFields[i].name + ' ">'+dictionaryFields[i].name + 
        '<label class="form-check-label" for="' + dictionaryFields[i].name + ' ">' + dictionaryFields[i].name +
        '</label></div></div>';
    }
  }
  formFields += '</div>'
  $(".defaultfield").append(formFields);
}

// projectForm();


// var languages = [
//   // {"id": "", "text": ""},
//   {"id": "Assamese", "text": "Assamese"},
//   {"id": "Bengali", "text": "Bengali"},
//   {"id": "Bodo", "text": "Bodo"},
//   {"id": "Dogri", "text": "Dogri"},
//   {"id": "Gujarati", "text": "Gujarati"},
//   {"id": "Hindi", "text": "Hindi"},
//   {"id": "Kannada", "text": "Kannada"},
//   {"id": "Kashmiri", "text": "Kashmiri"},
//   {"id": "Konkani", "text": "Konkani"},
//   {"id": "Maithili", "text": "Maithili"},
//   {"id": "Malayalam", "text": "Malayalam"},
//   {"id": "Meitei (Manipuri)", "text": "Meitei (Manipuri)"},
//   {"id": "Marathi", "text": "Marathi"},
//   {"id": "Nepali", "text": "Nepali"},
//   {"id": "Odia", "text": "Odia"},
//   {"id": "Punjabi", "text": "Punjabi"},
//   {"id": "Sanskrit", "text": "Sanskrit"},
//   {"id": "Santali", "text": "Santali"},
//   {"id": "Sindhi", "text": "Sindhi"},
//   {"id": "Tamil", "text": "Tamil"},
//   {"id": "Telugu", "text": "Telugu"},
//   {"id": "Urdu", "text": "Urdu"}
// ];



// var scripts = 
// [
//       {
//         "id": "Bengali–Assamese script", 
//         "text": "Bengali–Assamese script"
//       },
//       {
//         "id": "Balinese script", 
//         "text": "Balinese script"
//       },
//       {
//         "id": "Baybayin script", 
//         "text": "Baybayin script"
//       },
//       {
//         "id": "Buhid script", 
//         "text": "Buhid script"
//       },
//       {
//         "id": "Chakma", 
//         "text": "Chakma"
//       },
//       {
//         "id": "Devanagari", 
//         "text": "Devanagari"
//       },
//       {
//         "id": "Gujarati script", 
//         "text": "Gujarati script"
//       },
//       {
//         "id": "Gurmukhi script", 
//         "text": "Gurmukhi script"
//       },
//       {
//         "id": "Hanunó'o script", 
//         "text": "Hanunó'o script"
//       },
//       {
//         "id": "Javanese script (Hanacaraka)", 
//         "text": "Javanese script (Hanacaraka)"
//       },
//       {
//         "id": "Kaithi script", 
//         "text": "Kaithi script"
//       },
//       {
//         "id": "Kannada script", 
//         "text": "Kannada script"
//       },
//       {
//         "id": "Khmer script", 
//         "text": "Khmer script"
//       },
//       {
//         "id": "Khojki", 
//         "text": "Khojki"
//       },
//       {
//         "id": "Khudawadi", 
//         "text": "Khudawadi"
//       },
//       {
//         "id": "Kulitan alphabet", 
//         "text": "Kulitan alphabet"
//       },
//       {
//         "id": "Lao script", 
//         "text": "Lao script"
//       },
//       {
//         "id": "Leke script", 
//         "text": "Leke script"
//       },
//       {
//         "id": "Lepcha script", 
//         "text": "Lepcha script"
//       },
//       {
//         "id": "Limbu script", 
//         "text": "Limbu script"
//       },
//       {
//         "id": "Lontara script", 
//         "text": "Lontara script"
//       },
//       {
//         "id": "Malayalam script", 
//         "text": "Malayalam script"
//       },
//       {
//         "id": "Meitei Mayek", 
//         "text": "Meitei Mayek"
//       },
//       {
//         "id": "Tirhuta/Mithilakshar", 
//         "text": "Tirhuta/Mithilakshar"
//       },
//       {
//         "id": "Modi", 
//         "text": "Modi"
//       },
//       {
//         "id": "Myanmar script", 
//         "text": "Myanmar script"
//       },
//       {
//         "id": "Odia script", 
//         "text": "Odia script"
//       },
//       {
//         "id": "'Phags-pa script", 
//         "text": "'Phags-pa script"
//       },
//       {
//         "id": "Ranjana", 
//         "text": "Ranjana"
//       },
//       {
//         "id": "Saurashtra", 
//         "text": "Saurashtra"
//       },
//       {
//         "id": "Sinhala script", 
//         "text": "Sinhala script"
//       },
//       {
//         "id": "Sundanese script", 
//         "text": "Sundanese script"
//       },
//       {
//         "id": "Syloti Nagri script", 
//         "text": "Syloti Nagri script"
//       },
//       {
//         "id": "Tagbanwa script", 
//         "text": "Tagbanwa script"
//       },
//       {
//         "id": "Tamil script", 
//         "text": "Tamil script"
//       },
//       {
//         "id": "Telugu script", 
//         "text": "Telugu script"
//       },
//       {
//         "id": "Thaana script", 
//         "text": "Thaana script"
//       },
//       {
//         "id": "Thai script", 
//         "text": "Thai script"
//       },
//       {
//         "id": "Tibetan script", 
//         "text": "Tibetan script"
//       },
//       {
//         "id": "Bosnian Cyrillic alphabet (bosančica)",
//         "text": "Bosnian Cyrillic alphabet (bosančica)"
//       },
//       {
//         "id": "Epi-Olmec script", 
//         "text": "Epi-Olmec script"
//       },
//       {
//         "id": "Maya script", 
//         "text": "Maya script"
//       },
//       {
//         "id": "Mixtec script", 
//         "text": "Mixtec script"
//       },
//       {
//         "id": "Nahuat hieroglyphs", 
//         "text": "Nahuat hieroglyphs"
//       },
//       {
//         "id": "Olmec script", 
//         "text": "Olmec script"
//       },
//       {
//         "id": "Zapotec script", 
//         "text": "Zapotec script"
//       },
//       {
//         "id": "Takalik Abaj and Kaminaljuyú scripts",
//         "text": "Takalik Abaj and Kaminaljuyú scripts"
//       },
//       {
//         "id": "Old Uyghur alphabet", 
//         "text": "Old Uyghur alphabet"
//       },
//       {
//         "id": "Mongolian script", 
//         "text": "Mongolian script"
//       },
//       {
//         "id": "Manchu script", 
//         "text": "Manchu script"
//       },
//       {
//         "id": "Sorang Sompeng", 
//         "text": "Sorang Sompeng"
//       },
//       {
//         "id": "Ol Cemet'", 
//         "text": "Ol Cemet'"
//       },
//       {
//         "id": "Warang Citi", 
//         "text": "Warang Citi"
//       },
//       {
//         "id": "Old Hungarian alphabet", 
//         "text": "Old Hungarian alphabet"
//       },
//       {
//         "id": "IPA",
//         "text": "IPA"
//       },
//       {
//         "id": "Adlam alphabet", 
//         "text": "Adlam alphabet"
//       },
//       {
//         "id": "Afaka syllabary", 
//         "text": "Afaka syllabary"
//       },
//       {
//         "id": "Anatolian alphabets", 
//         "text": "Anatolian alphabets"
//       },
//       {
//         "id": "Arabic script", 
//         "text": "Arabic script"
//       },
//       {
//         "id": "Aramaic alphabet", 
//         "text": "Aramaic alphabet"
//       },
//       {
//         "id": "Armenian script", 
//         "text": "Armenian script"
//       },
//       {
//         "id": "ASL-phabet", 
//         "text": "ASL-phabet"
//       },
//       {
//         "id": "Borama script", 
//         "text": "Borama script"
//       },
//       {
//         "id": "Canadian Aboriginal script", 
//         "text": "Canadian Aboriginal script"
//       },
//       {
//         "id": "Caucasian Albanian alphabet", 
//         "text": "Caucasian Albanian alphabet"
//       },
//       {
//         "id": "Cherokee script", 
//         "text": "Cherokee script"
//       },
//       {
//         "id": "Coptic alphabet", 
//         "text": "Coptic alphabet"
//       },
//       {
//         "id": "Ge'ez script (Eritrean and Ethiopic)",
//         "text": "Ge'ez script (Eritrean and Ethiopic)"
//       },
//       {
//         "id": "Georgian script", 
//         "text": "Georgian script"
//       },
//       {
//         "id": "Glagolitic alphabet", 
//         "text": "Glagolitic alphabet"
//       },
//       {
//         "id": "Gothic alphabet", 
//         "text": "Gothic alphabet"
//       },
//       {
//         "id": "Greek script", 
//         "text": "Greek script"
//       },
//       {
//         "id": "Chinese characters and derivatives",
//         "text": "Chinese characters and derivatives"
//       },
//       {
//         "id": "Hangul", 
//         "text": "Hangul"
//       },
//       {
//         "id": "Hebrew script", 
//         "text": "Hebrew script"
//       },
//       {
//         "id": "Old Italic script", 
//         "text": "Old Italic script"
//       },
//       {
//         "id": "Kaddare script", 
//         "text": "Kaddare script"
//       },
//       {
//         "id": "Kana", 
//         "text": "Kana"
//       },
//       {
//         "id": "Khitan large script", 
//         "text": "Khitan large script"
//       },
//       {
//         "id": "Khitan small script", 
//         "text": "Khitan small script"
//       },
//       {
//         "id": "Latin script", 
//         "text": "Latin script"
//       },
//       {
//         "id": "Meetei Mayek", 
//         "text": "Meetei Mayek"
//       },
//       {
//         "id": "N'Ko script", 
//         "text": "N'Ko script"
//       },
//       {
//         "id": "Naxi script", 
//         "text": "Naxi script"
//       },
//       {
//         "id": "Nsibidi", 
//         "text": "Nsibidi"
//       },
//       {
//         "id": "Ogham", 
//         "text": "Ogham"
//       },
//       {
//         "id": "Osmanya script", 
//         "text": "Osmanya script"
//       },
//       {
//         "id": "Pahawh Hmong", 
//         "text": "Pahawh Hmong"
//       },
//       {
//         "id": "Old Permic alphabet", 
//         "text": "Old Permic alphabet"
//       },
//       {
//         "id": "Runic script", 
//         "text": "Runic script"
//       },
//       {
//         "id": "si5s", 
//         "text": "si5s"
//       },
//       {
//         "id": "SignWriting", 
//         "text": "SignWriting"
//       },
//       {
//         "id": "Stokoe notation", 
//         "text": "Stokoe notation"
//       },
//       {
//         "id": "Tifinagh", 
//         "text": "Tifinagh"
//       },
//       {
//         "id": "Yi script", 
//         "text": "Yi script"
//       }
// ]