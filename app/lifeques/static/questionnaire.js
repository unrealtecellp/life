// var questionaireprojectform = {
//   "username": "alice",
//   "projectname": "alice_project_1",
//   "Language": ["text", ["English", "Hindi"]],
//   "Script": ["", ["latin", "devanagari"]],
//   "Prompt Audio": ["file", ["audio"]],
//   "Domain": ["multiselect", ["General", "Agriculture", "Sports"]],
//   "Elicitation Method": ["select", ["Translation", "Agriculture", "Sports"]],
//   "Target": ["multiselect", ["case", "classifier", "adposition"]]
// }
var questionaireprojectform = {
  "_id":{"$oid":"6370f76bbf61c0a50d2a6ef9"},
  "username":"alice",
  "projectname":"Q_Derived_test_108",
  "Prompt Type":[
      "prompt",
      {
          "English":{
              "Audio":["waveform",""],
              "Multimedia":["file",""],
              "Image":["file",""],
              "Text":["text",""]
          },
          "Hindi":{
            "Audio":["waveform",""],
            "Multimedia":["file",""],
            "Image":["file",""],
            "Text":["text",""]
          }
      }
  ],
  "Language_Script":[
      "",
      {
        "English":"Latin",
        "Hindi": "Devanagari"
      }
  ],
  "Target":["multiselect",["on"]],
  "Elicitation Method":["select",["Translation","Narration","Role-Play"]],
  "Domain":["multiselect",["General","Education","Agriculture","Science-Technology"]]
}

var testquesdata = {
  "username": "",
  "projectname": "",
  "quesID": "",
  "Q_Id": "",
  "lastUpdatedBy": "",
  "prompt": {
      "domain": [],
      "elicitation method": "",
      "target": [],
      "content": {
          "English": {
              "text": {
                  "txtboundaryspan": {
                      "startindex": "",
                      "endindex": "",
                      "textspan": {
                          "Latin": "This is english sentence."
                      }
                  }
              },
              "audio": {
                  "fileId": "",
                  "filename": "",
                  "instructions": "",
                  "textgrid": {
                      "sentence": {
                          "audioboundarydur": {
                              "startindex": "",
                              "endindex": "",
                              "transcription": {
                                  "script": ""
                              }
                          }
                      }
                  }
              },
              "image": {
                  "fileId": "",
                  "filename": "",
                  "instructions": "",
                  "imagetext": {
                      "txtboundaryspan": {
                          "startindex": "",
                          "endindex": "",
                          "textspan": {
                              "script": ""
                          }   
                      }
                  }
              },
              "multimedia": {
                  "fileId": "",
                  "filename": "",
                  "instructions": "",
                  "textgrid": {
                      "sentence": {
                          "audioboundarydur": {
                              "startindex": "",
                              "endindex": "",
                              "transcription": {
                                  "script": ""
                              }
                          }
                      }
                  }
              }
          },
          "Hindi": {
            "text": {
                "txtboundaryspan": {
                    "startindex": "",
                    "endindex": "",
                    "textspan": {
                        "Devanagari": "ye hindi sentence hai."
                    }
                }
            },
            "audio": {
                "fileId": "",
                "filename": "",
                "instructions": "",
                "textgrid": {
                    "sentence": {
                        "audioboundarydur": {
                            "startindex": "",
                            "endindex": "",
                            "transcription": {
                                "script": ""
                            }
                        }
                    }
                }
            },
            "image": {
                "fileId": "",
                "filename": "",
                "instructions": "",
                "imagetext": {
                    "txtboundaryspan": {
                        "startindex": "",
                        "endindex": "",
                        "textspan": {
                            "script": ""
                        }   
                    }
                }
            },
            "multimedia": {
                "fileId": "",
                "filename": "",
                "instructions": "",
                "textgrid": {
                    "sentence": {
                        "audioboundarydur": {
                            "startindex": "",
                            "endindex": "",
                            "transcription": {
                                "script": ""
                            }
                        }
                    }
                }
            }
        }

      }
  },
  "current_username": {
      "prompt": {
          "bhojpuri": "",
          "awadhi": ""
      }   
  }
}

var targets = [
  {"id": "Simple and Complex", "text": "Simple and Complex"},
  {"id": "Case", "text": "Case"},
  {"id": "Classifiers", "text": "Classifiers"},
  {"id": "Reflexives and Reciprocals", "text": "Reflexives and Reciprocals"},
  {"id": "Interrogatives", "text": "Interrogatives"},
  {"id": "Tag Questions", "text": "Tag Questions"},
  {"id": "Tense Aspect Mood", "text": "Tense Aspect Mood"},
  {"id": "Intransitive", "text": "Intransitive"},
  {"id": "Transitive", "text": "Transitive"},
  {"id": "Ditransitive", "text": "Ditransitive"},
  {"id": "Additional", "text": "Additional"},
  {"id": "ECV, Converbs, Serial Verbs", "text": "ECV, Converbs, Serial Verbs"},
  {"id": "Negatives and Prohibitives", "text": "Negatives and Prohibitives"},
  {"id": "Causatives and Passives", "text": "Causatives and Passives"},
  {"id": "Reduplication, echo forms and binomials", "text": "Reduplication, echo forms and binomials"},
  {"id": "Comparatives and Superlatives", "text": "Comparatives and Superlatives"},
  {"id": "Sentences with Adverbs", "text": "Sentences with Adverbs"},
  {"id": "Quantifiers and Intensifiers", "text": "Quantifiers and Intensifiers"},
  {"id": "Miscellaneous", "text": "Miscellaneous"}
]

var audioWaveform = 0

function createInputElement(key, elevalue, type, quesdatavalue) {
  // console.log(key, elevalue, type, quesdatavalue);
  var qform = '';
  for (let i=0; i<elevalue.length; i++) {
    // console.log(elevalue[i], quesdatavalue);
    if (elevalue[i] === '') {
      eval = key
    }
    else {
      eval = key + ' ' + elevalue[i]
    }
    var keyid = eval.replace(new RegExp(' ', 'g'), '_');
    var val = '';
    if (key === 'Language') {
      val = quesdatavalue[elevalue[i]];
      eval = 'Prompt ' + eval
    }
    else if (key.includes("Transcription")) {
      val = quesdatavalue;
    }
    else {
      val = quesdatavalue;
    }
    // console.log(val);
    qform += '<div class="form-group">'+
              '<label for="'+ keyid +'">'+ eval +'</label>'+
              '<input type="'+type+'" class="form-control" id="'+ keyid +'"'+ 
              'placeholder="'+ eval +'" name="'+ eval +'" value="'+ val +'" required>'+
              // 'placeholder="'+ eval +'" name="'+ eval +'" value="'+ val +'">'+
              '</div>';
  }

  return qform;
}

function createTextareaElement(key, elevalue, type, quesdatavalue) {
  var qform = '';
  for (let i=0; i<elevalue.length; i++) {
    eval = key + ' ' + elevalue[i]
    var keyid = eval.replace(new RegExp(' ', 'g'), '_');
    qform += '<div class="form-group">'+
              '<label for="'+ keyid +'">'+ eval +'</label><br>'+
              '<textarea id="'+ keyid +'" name="'+ eval +'" rows="4" cols="50">'+
              '</textarea>'+
              '</div>';
  }

  return qform;
}

function createSelectElement(key, elevalue, type, quesdatavalue) {
  // console.log(quesdatavalue)
  var qform = '';
  var keyid = key.replace(new RegExp(' ', 'g'), '_');
  qform += '<div class="form-group">'+
            '<label for="'+keyid+'">'+key+'</label>';
  if (type === 'multiple') {
    qform += '<select class="quesselect" id="'+keyid+'" name="'+key+'" multiple="'+type+'" style="width: 100%" required>';
    // qform += '<select class="quesselect" id="'+keyid+'" name="'+key+'" multiple="'+type+'" style="width: 100%">';
  }
  else {
    qform += '<select class="quesselect" id="'+keyid+'" name="'+key+'" style="width: 100%" required>';
    // qform += '<select class="quesselect" id="'+keyid+'" name="'+key+'" style="width: 100%">';
  }
  
  for (let i=0; i<elevalue.length; i++) {
    eval = elevalue[i]
    // console.log(eval, quesdatavalue, quesdatavalue.includes(eval))
    if (type === 'multiple') {
      if (quesdatavalue.includes(eval)) {
        qform += '<option value="'+eval+'" selected>'+eval+'</option>';  
      }
      else {
        qform += '<option value="'+eval+'">'+eval+'</option>';
      }
    }
    else {
      if (quesdatavalue.includes(eval)) {
        // console.log(eval, quesdatavalue)
        qform += '<option value="'+eval+'" selected>'+eval+'</option>';  
      }
      else {
        qform += '<option value="'+eval+'">'+eval+'</option>';
      }
    }
  }
  qform += '</select></div>';

  return qform;
}

function createquesform(quesprojectform) {
  // console.log(quesprojectform);
  // quesprojectform = questionaireprojectform;
  localStorage.setItem("quesactiveprojectform", JSON.stringify(quesprojectform));
  if (!('quesdata' in quesprojectform) ||
      !(quesprojectform['quesdata'])) {
    // creatNewQues(quesprojectform)
    console.log('creatNewQues(quesprojectform)');
  }
  else {
    let quesdata = quesprojectform['quesdata']
    transcriptionRegions = quesprojectform['transcriptionRegions']
    localStorage.setItem("regions", JSON.stringify(transcriptionRegions));
    // console.log(transcriptionRegions);
    // var activeAudioFilename = JSON.parse(localStorage.getItem('AudioFilePath')).split('/')[2];
    var activeAudioFilename = quesprojectform["QuesAudioFilePath"].split('/')[2];
    if (activeAudioFilename === undefined) {
      activeAudioFilename = '';
    }
    // console.log(activeAudioFilename)
    // var inpt = '<strong>Audio Filename: </strong><strong id="audioFilename">'+ activeAudioFilename +'</strong>'
    // $(".defaultfield").append(inpt);
    // lastActiveId = newData["lastActiveId"]
    // // console.log(lastActiveId)
    // inpt = '<input type="hidden" id="lastActiveId" name="lastActiveId" value="'+lastActiveId+'">';
    // $('.defaultfield').append(inpt);
    // inpt = ''
    // localStorage.removeItem('regions');
    localStorage.setItem("transcriptionDetails", JSON.stringify([quesprojectform['transcriptionDetails']]));
    localStorage.setItem("QuesAudioFilePath", JSON.stringify(quesprojectform['QuesAudioFilePath']));
    // console.log(quesdata);
    // var quesformControlAbove = '<div id="quesformControlAbove">'+
    //                             '<button class="btn btn-info btn-lg" type="button" id="previous" onclick="previousQues()">'+
    //                             '<span class="previousaudio glyphicon glyphicon-chevron-left" aria-hidden="true"></span>'+
    //                             'Previous'+
    //                             '</button>'+
    //                             '<button class="btn btn-info btn-lg pull-right" type="button" id="next" onclick="nextQues()">'+
    //                             'Next'+
    //                             '<span class="nextaudio glyphicon glyphicon-chevron-right" aria-hidden="true"></span>'+
    //                             '</button>'+
    //                           '</div>';
    let quesform = '';
    quesform += createInputElement('Q_Id', [''], 'text', quesdata['Q_Id'])
    let transcriptionBoundaryForm = '';
    // let instructionmode = '';
    // quesform += '<div class="col-md-6">';
    let qform = '<form id="idsavequesform" action="/lifeques/savequestionnaire" method="POST" enctype="multipart/form-data">';

    for (let [key, value] of Object.entries(quesprojectform)) {
      // console.log(key, value, value[0], typeof value, quesdata['prompt'][key]);
      
      if (key === 'Instruction') {
        continue;
      }

      let eletype = value[0];
      let elevalue = value[1];
      // console.log(eletype, elevalue);
      quesdatavalue = quesdata['prompt'][key]
      if (eletype === 'text') {
        if (key === 'Language') {
          quesdatavalue = quesdata['prompt']['text']['content']
          quesform += createInputElement(key, elevalue, eletype, quesdatavalue)
        }
        else {
          quesform += createInputElement(key, elevalue, eletype, quesdatavalue)
        }
        
      }
      else if (eletype === 'textarea') {
        quesform += createTextareaElement(key, elevalue, eletype, quesdatavalue)
      }
      else if (eletype === 'file') {
        quesform += createInputElement(key, elevalue, eletype, quesdatavalue)
      }
      else if (eletype === 'select') {
        quesform += createSelectElement(key, elevalue, '', quesdatavalue)
      }
      else if (eletype === 'multiselect') {
        if (key === 'Target') {
          quesform += createSelectElement(key, quesdatavalue, 'multiple', quesdatavalue)
        }
        else {
          quesform += createSelectElement(key, elevalue, 'multiple', quesdatavalue)
        }
        
      }
      else if (eletype === 'prompt') {
        
        // test field start

        var testquesform = ''
        // testtype = questionaireprojectform[key][0];
        // testvalue = questionaireprojectform[key][1];
        testquesdata = quesdata;
        testtype = eletype
        testvalue = elevalue
        // console.log(questionaireprojectform[key], testtype, testvalue);
        // console.log(quesprojectform[key], testtype, testvalue);
        for (let [testpromptTypeKey, testpromptTypeValue] of Object.entries(testvalue)) {
          transcriptionBoundaryForm = '';
          var promptquesdatavalue = Object();
          testquesform += '<div class="form-group ' + testpromptTypeKey +'">';
          testquesform += '<fieldset class="form-group border">'+
                      '<legend class="col-form-label">'+
                      'Prompt'+' '+ testpromptTypeKey +
                      '<button class="btn btn-default pull-right" type="button" data-toggle="collapse"'+
                      'data-target=".prompt' + testpromptTypeKey +'" aria-expanded="false" aria-controls="' + testpromptTypeKey +'" '+
                      'onclick="collapsePrompt(\''+testpromptTypeKey+'\')">'+
                      '<span class="glyphicon glyphicon-chevron-up promp'+testpromptTypeKey+'" aria-hidden="true"></span>'+
                      '</button></legend>';
          // console.log(testpromptTypeKey, testpromptTypeValue);
          // console.log(key, elevalue, eletype, quesdatavalue);
          langData = testquesdata['prompt']['content'][testpromptTypeKey]
          langText = testquesdata['prompt']['content'][testpromptTypeKey]['text']
          langTextBoundary = Object.keys(langText)[0]
          langScript = quesprojectform['LangScript'][1][testpromptTypeKey]
          // console.log(langText, langTextBoundary, langScript);
          promptquesdatavalue[testpromptTypeKey] = langText[langTextBoundary]['textspan'][langScript]
          // console.log(key, elevalue, eletype, quesdatavalue, promptquesdatavalue);
          testquesform += '<div class="form-group prompt'+testpromptTypeKey+' collapse in">';
          testquesform += createInputElement('Language', [testpromptTypeKey], 'text', promptquesdatavalue)
          for (let [testpromptTypeValueKey, testpromptTypeValueInfo] of Object.entries(testpromptTypeValue)) {
            // console.log(testpromptTypeValueKey, testpromptTypeValueInfo);
            transcriptionBoundaryForm = '';
            temp_testpromptTypeValueKey = testpromptTypeValueKey;
            update_key = key.replace('Type', '')+testpromptTypeValueKey;
            if (testpromptTypeValueKey === 'Text') continue;
            testpromptTypeValueKey = testpromptTypeValueKey.toLowerCase();
            quesdatavalue = langData[testpromptTypeValueKey]
            // console.log(langData[testpromptTypeValueKey])
            let filePathKey = [testpromptTypeKey, testpromptTypeValueKey.toLocaleLowerCase(), 'FilePath'].join('_')
            // console.log(filePathKey);
            let filePath = quesprojectform[filePathKey]
            // console.log(filePath);
            if (testpromptTypeValueInfo[0] === 'waveform' &&
                testpromptTypeValueKey === 'audio' &&
                !audioWaveform) {
              substr = createInputElement('Language', [testpromptTypeKey], 'text', promptquesdatavalue)
              // console.log(substr);
              testquesform = testquesform.replace(substr, '');
              transcriptionBoundaryForm = testwaveFormFunction(update_key, testpromptTypeKey, testpromptTypeValue, quesdatavalue, filePath, langScript)
              if (transcriptionBoundaryForm === undefined) {
                transcriptionBoundaryForm = '';
              }
              else {
                audioWaveform = 1
              }
            }
            else if (testpromptTypeValueInfo[0] === 'file' ||
                      testpromptTypeValueKey === 'multimedia' ||
                      audioWaveform) {
              transcriptionBoundaryForm = testpromptFileFunction(update_key, testpromptTypeKey, testpromptTypeValue, quesdatavalue, filePath)
              if (transcriptionBoundaryForm === undefined) {
                transcriptionBoundaryForm = '';
              }
            }
            testquesform += transcriptionBoundaryForm;
            if (testpromptTypeValueInfo[1] === 'text') {
              let instructionVal = testquesdata['prompt']['content'][testpromptTypeKey][testpromptTypeValueKey][testpromptTypeValueKey+'Instruction']
              // console.log('Instruction', [testpromptTypeKey], 'text', instructionVal);
              if (instructionVal === undefined) {
                instructionVal = ''
              }
              // console.log(instructionVal);
              let instructionForm = createInputElement(temp_testpromptTypeValueKey+' Instruction', [testpromptTypeKey], 'text', instructionVal)
              testquesform += instructionForm
            }
          }
          testquesform += '</div>';
          testquesform += '</fieldset>';
          testquesform += '</div>';
          // console.log(testquesform);
        }
        // $('.testfield').html(testquesform);
        quesform += testquesform

        // test field end
    }
  }
    // quesform += '<input class="btn btn-lg btn-primary" type="submit" value="Submit">';
    // quesform += '<div id="quesformControlBelow">'+
    //                 '<button class="btn btn-info btn-lg" type="button" id="previous" onclick="previousQues()">'+
    //                 '<span class="previousaudio glyphicon glyphicon-chevron-left" aria-hidden="true"></span>'+
    //                 'Previous'+
    //                 '</button>'+
    //                 '<button class="btn btn-info btn-lg pull-right" type="button" id="next" onclick="nextQues()">'+
    //                 'Next'+
    //                 '<span class="nextaudio glyphicon glyphicon-chevron-right" aria-hidden="true"></span>'+
    //                 '</button>'+
    //                 '<br>'+
    //                 '<br>'+
    //                 '<button type="submit" class="btn btn-warning btn-lg btn-block pull-right" id="saveques">'+
    //                   'Save'+
    //                   '<span class="glyphicon glyphicon-floppy-save" aria-hidden="true"></span>'+
    //                 '</button>'+
    //             '</div>';
    
    // qform += quesformControlAbove + '<br>' + transcriptionBoundaryForm + '<hr>' + quesform;
    qform += transcriptionBoundaryForm + '<hr>' + quesform;
    qform += '</form>'
    // quesform += '</div>';
    
    $('#quesform').html(qform);

    $('.quesselect').select2({
      placeholder: 'select',
      // data: usersList,
      allowClear: true
    });
    $('#Target').select2({
      placeholder: 'select',
      data: targets,
      allowClear: true
    });

    quesIdDetails(quesdata['Q_Id'], quesdata['quesId'])
  }
}

function testwaveFormFunction(key, promptTypeKey, promptTypeValue, quesdatavalue, filePath, langScript) {
  // console.log(key, promptTypeKey, promptTypeValue, quesdatavalue, filePath, langScript);
  // console.log(quesdatavalue['fileId']);
  
  let transcriptionBoundaryForm = '';
  let quesTranscription = ''
  if (quesdatavalue['fileId'] === '' ||
    quesdatavalue['fileId'] === undefined) {
    // console.log('waveformmmm', promptTypeKey, promptTypeValue, quesdatavalue)
    var uploadFormId = 'ques'+key+' '+promptTypeKey
    uploadFormId = uploadFormId.replace(new RegExp(' ', 'g'), '_');
    // quesTranscription += '<form action="{{ url_for(\'lifeques.quespromptfile\') }}" method="POST" enctype="multipart/form-data">';
    quesTranscription +=  '<div id="'+uploadFormId+'">';
    quesTranscription += createInputElement(key, [promptTypeKey], 'file', quesdatavalue);
    
    // quesTranscription += '<input class="btn btn-primary pull-right" id="'+uploadFormId+'submit" type="submit" formaction="{{ url_for(\'lifeques.quespromptfile\') }}" value="Upload">';
    quesTranscription += '<input class="btn btn-primary pull-right" id="'+uploadFormId+'submit" type="button" value="Upload" onclick="uploadPromptFile(this);">';
    quesTranscription += '</div>';
    // quesTranscription += '</form>';
    quesTranscription += '<br>';

    return quesTranscription;
  }
  else {
    start = transcriptionRegions[0]['start']
    end = transcriptionRegions[0]['end']
    boundaryId = transcriptionRegions[0]['boundaryID']
    // lang = quesdatavalue['fileLanguage']
    let lang = promptTypeKey
    val = transcriptionRegions[0]['data']['sentence'][boundaryId]['transcription'][langScript]
    if (val === undefined) {
      val = '';
    }
    // console.log(val);
    // var x = document.getElementById("questranscriptionsubmit");
    // x.style.display = "none";
    // var x = document.getElementById("questranscriptionwaveform");
    // x.style.display = "block";
    quesTranscription += createInputElement(key+' Transcription', [lang], 'text', val);

    let waveform = '<div id="wave-timeline"></div>'+
                    '<div id="waveform"></div>'+
                    '<div id="wave-spectrogram" style="display: none;"></div>'+
                    '<br>';

    let waveformController = '<hr>'+
                              '<div class="col-sm-3">'+
                                '<input id="slider" data-action="zoom" type="range" min="0" max="5000" value="0" style="width: 50%">'+
                              '</div>'+
                              // '<i class="glyphicon glyphicon-zoom-in"></i>'+
                              
                              '<div class="pull-right">'+
                                // '<button type="button" id="deleteboundary" class="btn btn-danger btn-block" data-action="delete-region" disabled>Delete Boundary</button>'+
                                '<button type="button" id="deleteboundary" class="btn btn-warning btn-block" data-toggle="tooltip" title="Delete Boundary" data-action="delete-region" disabled>'+
                                  '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span>'+
                                '</button>'+
                                // '<br>'+
                                // '<button class="btn btn-danger" type="button" id="stopAudio" data-action="stop-audio">STOP'+
                                //   '<span class="audiostop glyphicon glyphicon-stop" aria-hidden="true"></span>'+
                                // '</button>'+
                                // '<button class="btn btn-primary" type="button" id="playPauseAudio">PLAY/PAUSE'+
                                //   '<span class="audioplaypause glyphicon glyphicon-play" aria-hidden="true"></span>'+
                                // '</button>'+
                              '</div><br><br><hr>';

    transcriptionBoundaryForm += waveform + waveformController;
    
    transcriptionBoundaryForm += '<div class="form-group">'+
                                  // '<label for="start">Boundary Start Time</label>'+
                                  '<input type="hidden" class="form-control" id="start" name="start" value="'+start+'" required/>'+
                                  '</div>'+
                                  '<div class="form-group">'+
                                  // '<label for="end">Boundary End Time</label>'+
                                  '<input type="hidden" class="form-control" id="end" name="end" value="'+end+'" required/>'+
                                  '</div>';
    transcriptionBoundaryForm += quesTranscription;
    
    return transcriptionBoundaryForm;
  }
}

function testpromptFileFunction(key, promptTypeKey, promptTypeValue, quesdatavalue, filePath) {
  // console.log(key, promptTypeKey, promptTypeValue, quesdatavalue);
  // console.log(quesdatavalue['fileId']);
  let transcriptionBoundaryForm = '';
  let quesTranscription = '';
  // console.log(quesdatavalue['fileId'])
  if (quesdatavalue['fileId'] === '' ||
      quesdatavalue['fileId'] === undefined) {
    // console.log('waveformmmm', promptTypeKey, promptTypeValue, quesdatavalue)
    var uploadFormId = 'ques'+key+' '+promptTypeKey
    uploadFormId = uploadFormId.replace(new RegExp(' ', 'g'), '_');
    
    // quesTranscription += '<form action="{{ url_for(\'lifeques.quespromptfile\') }}" method="POST" enctype="multipart/form-data">';
    quesTranscription += '<div id="'+uploadFormId+'">';
    quesTranscription += createInputElement(key, [promptTypeKey], 'file', quesdatavalue);
    // quesTranscription += '<input class="btn btn-primary pull-right" id="'+uploadFormId+'submit" type="submit" formaction="{{ url_for(\'lifeques.quespromptfile\') }}" value="Upload">';
    quesTranscription += '<input class="btn btn-primary pull-right" id="'+uploadFormId+'submit" type="button" value="Upload" onclick="uploadPromptFile(this);">';
    quesTranscription += '</div>';
    // quesTranscription += '</form>';
    quesTranscription += '<br>';

    return quesTranscription;
  }
  else {
    // var x = document.getElementById("questranscriptionsubmit");
    // x.style.display = "none";
    // filePath = JSON.parse(localStorage.getItem('QuesAudioFilePath'));
    fileCaption = key + ' ' + promptTypeKey
    var fileId = fileCaption.replace(new RegExp(' ', 'g'), '');
    // console.log(fileId);
    if (fileId.includes('Audio')) {
      transcriptionBoundaryForm += '<div class="form-group">'+
                                    '<label for="'+fileId+'">'+fileCaption+'</label><br>'+
                                    '<audio id="'+fileId+'" controls autoplay>'+
                                    '<source src="'+filePath+'" type="audio/wav">'+
                                    'Your browser does not support the audio element.'+
                                    '</audio>'+
                                    '</div>';
    }
    else if (fileId.includes('Image')) {
      transcriptionBoundaryForm += '<div class="form-group">'+
                                    '<label for="'+fileId+'">'+fileCaption+'</label><br>'+
                                    '<img src="'+filePath+'" alt="'+filePath+'" width="400" height="341" />'+
                                    '</div>';
    }
    else if (fileId.includes('Multimedia')) {
      transcriptionBoundaryForm += '<div class="form-group">'+
                                    '<label for="'+fileId+'">'+fileCaption+'</label><br>'+
                                    '<video width="400" height="341" controls>'+
                                    '<source src="'+filePath+'" type="video/mp4">'+
                                    'Your browser does not support the video tag.'+
                                    '</video> '+
                                    '</div>';
    }
    transcriptionBoundaryForm += quesTranscription;

  return transcriptionBoundaryForm;
  }
}

function quesIdDetails(Q_Id, quesId) {
  inpt = "";
  // var inpt = '<strong>Question ID: </strong><strong id="Q_Id">'+ Q_Id +'</strong>'
  // $(".defaultfield").append(inpt);
  lastActiveId = quesId
  // console.log(lastActiveId)
  inpt = '<input type="hidden" id="lastActiveId" name="lastActiveId" value="'+lastActiveId+'">';
  $('.defaultfield').append(inpt);
}

function previousQues() {
  var lastActiveId = document.getElementById("lastActiveId").value;
    $.ajax({
        url: '/lifeques/loadpreviousques',
        type: 'GET',
        data: {'data': JSON.stringify(lastActiveId)},
        contentType: "application/json; charset=utf-8", 
        success: function(response){
          window.location.reload();
        }
    });
    return false;
}

function nextQues() {
  var lastActiveId = document.getElementById("lastActiveId").value;
  $.ajax({
      url: '/lifeques/loadnextques',
      type: 'GET',
      data: {'data': JSON.stringify(lastActiveId)},
      contentType: "application/json; charset=utf-8", 
      success: function(response){
        window.location.reload();
      }
  });
  return false;
}

function unAnnotated() {
  unanno = '';
  $('#uNAnnotated').remove();
  $.ajax({
      url: '/lifeques/allunannotated',
      type: 'GET',
      data: {'data': JSON.stringify(unanno)},
      contentType: "application/json; charset=utf-8", 
      success: function(response){
          allunanno = response.allunanno;
          allanno = response.allanno;
          // console.log(allanno)
          var inpt = '';
          inpt += '<select class="col-sm-3 allanno" id="allanno" onchange="loadAnnoQues()" style="width: 45%">'+
                  '<option selected disabled>Completed</option>';
                  for (i=0; i<allanno.length; i++) {
                      inpt += '<option value="'+allanno[i]["quesId"]+'">'+allanno[i]["Q_Id"]+'</option>';
                  }
          // inpt += '</select>';
          inpt += '</select>&nbsp; ';
          inpt += '<select class="pr-4 col-sm-3" id="allunanno" onchange="loadUnAnnoQues()" style="width: 45%">'+
                  '<option selected disabled>Not Completed</option>';
                  for (i=0; i<allunanno.length; i++) {
                      inpt += '<option value="'+allunanno[i]["quesId"]+'">'+allunanno[i]["Q_Id"]+'</option>';
                  }
          inpt += '</select>';
          $('.commentIDs').append(inpt);
          $('#allanno').select2({
            // placeholder: 'select user'
            });
          $('#allunanno').select2({
            // placeholder: 'select user'
            });
      }
  });
  return false; 
}

function loadUnAnnoQues() {
  newQuesId = document.getElementById('allunanno').value;
  // console.log(newQuesId)
  // loadRandomAudio(newQuesId)
  $.ajax({
      url: '/lifeques/loadunannoques',
      type: 'GET',
      data: {'data': JSON.stringify(newQuesId)},
      contentType: "application/json; charset=utf-8", 
      success: function(response){
          window.location.reload();
      }
  });
  return false;
}

function loadAnnoQues() {
  newQuesId = document.getElementById('allanno').value;
  // console.log(newQuesId)
  // loadRandomAudio(newQuesId)
  $.ajax({
      url: '/lifeques/loadunannoques',
      type: 'GET',
      data: {'data': JSON.stringify(newQuesId)},
      contentType: "application/json; charset=utf-8", 
      success: function(response){
          window.location.reload();
      }
  });
  return false;
}

function collapsePrompt(eleClass) {
  // console.log(eleClass);
  $(".prompt"+eleClass).ready(function(){
    $(".prompt"+eleClass).on('shown.bs.collapse', function(){
      $(".promp"+eleClass).addClass('glyphicon-chevron-up').removeClass('glyphicon-chevron-down');
    });  
    $(".prompt"+eleClass).on('hidden.bs.collapse', function() {
      $(".promp"+eleClass).addClass('glyphicon-chevron-down').removeClass('glyphicon-chevron-up');
    });   
  });
}

function uploadPromptFile(btn) {
  // console.log(btn, btn.id);
  promptFileUploadBtnId = btn.id
  promptFileId = promptFileUploadBtnId.replace(new RegExp('ques|submit', 'g'), '');
  // console.log(promptFileId);
  const file = document.getElementById(promptFileId).files[0];
  var formData = new FormData();
  formData.append(promptFileId, file);
  $.ajax({
    url: '/lifeques/quespromptfile',
    type: 'POST',
    data: formData,
    contentType: false,
    cache: false,
    processData: false,
    success: function(data) {
        // console.log('Success!');
        window.location.reload();
    },
  });
  return false;
}

function openQuesMetaData() {
  let quesMetadataDisplay = document.getElementById('quesmetadata')
  if(quesMetadataDisplay.style.display == 'none') {
      quesMetadataDisplay.style.display = 'block'
  }
  else if(quesMetadataDisplay.style.display == 'block') {
      quesMetadataDisplay.style.display = 'none'
  }
}

$("#save").click(function() {
  submit_form_ele = document.getElementById("idsavequesform");
  const formData = new FormData(submit_form_ele);
  var object = {};
  formData.forEach(function(value, key){
      // console.log('key: ', key, 'value: ', value);
      if (key in object) {
          object[key].push(value);
      }
      else {
          object[key] = [value];
      }
  });
  // console.log(object);
  $.post( "/lifeques/savequestionnaire", {
    a: JSON.stringify(object)
  })
  .done(function( data ) {
    // console.log(data.savedQuestionnaire);
    if (!data.savedQuestionnaire) {
          alert("Unable to save the questionnaire as question seem to be deleted or revoked access by one of the shared users. Showing you the next question in the list.")
          // window.location.reload();
    }
    else {
      alert("Questionnaire saved successfully.")
    }
    window.location.reload();
  });
  // $.post( "/savetranscription", {
  //   a: JSON.stringify(questionnaireData)
  // })
  // .done(function( data ) {
  //   // console.log(data.savedTranscription);
  //   if (!data.savedQuestionnaire) {
  //     alert("Unable to save the questionnaire as question seem to be deleted or revoked access by one of the shared users. Showing you the next question in the list.")
  //     window.location.reload();
  //   }
  //   else {
  //     alert("Questionnaire saved successfully.")
  //   }
  //   // window.location.reload();
  // });
});

$("#addnewques").click(function() {
  $.get( "/lifeques/createnewques", {
    // a: JSON.stringify(object)
  })
  .done(function( data ) {
    // console.log(data.savedQuestionnaire);
    if (!data.saveState) {
          alert("Unable to add new question.")
          // window.location.reload();
    }
    else {
      alert("New question added successfully.")
    }
    window.location.reload();
  });
});

$("#deleteques").click(function() {
  let deleteQuesFLAG = false;
  let lastActiveId = document.getElementById("lastActiveId").value;
  if (lastActiveId) {
    deleteQuesFLAG = confirm("Delete This Question!!!");
  }
  if(deleteQuesFLAG) {
    // console.log(deleteAudioFLAG, lastActiveId);
    $.post( "/lifeques/deleteques", {
      a: JSON.stringify(lastActiveId)
    })
    .done(function( data ) {
      window.location.reload();
    });
  }
});
