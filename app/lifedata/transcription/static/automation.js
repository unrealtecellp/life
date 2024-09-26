
// {
//   "name": "BHASHINI",
//   "value": "bhashini"
//   }]


function autoTranscription() {
  console.log("Opened!")
  populateBoundaryId('Transcription');
  model_list = document.getElementById('myASRModelListSelect2')
  console.log('All options', model_list, model_list.length)
  // let actibeBoundaryId = JSON.parse(localStorage.getItem('activeprojectform'));
  if (model_list.length == 0) {

    $.ajax({
      url: '/lifemodels/getModelList',
      type: 'POST',
      // data: formData,
      contentType: false,
      cache: false,
      processData: false,
      success: function (data) {
        console.log('Success!');
        console.log(data)
        activeSpeaker = document.getElementById("speakeridsdropdown").value;
        // console.log(document.getElementById("speakeridsdropdown"));
        filename = document.getElementById("audioFilename").textContent;
        audioDuration = document.getElementById("currentaudioduration").textContent;
        document.getElementById("asrspeakeriduploaddropdown").value = activeSpeaker;
        document.getElementById("asraudiofileid").value = filename
        document.getElementById("asraudiodurationid").value = audioDuration

        // console.log('Models list', asrmodels)
        $('#transcribeUsingSelect2Id').select2({
          // tags: true,
          placeholder: 'Select Transcription Source',
          dropdownParent: $("#myAutomationModal"),
          data: asrmodels
          // allowClear: true
        });

        $('#overwriteMyBoundariesid').select2({
          // tags: true,
          placeholder: 'Select Boundary Level',
          dropdownParent: $("#myAutomationModal"),
          data: boundaryLevels,
          allowClear: true
        });

        $('#myASRModelListSelect2').empty().trigger('change');
        $('#myASRModelListSelect2').select2({
          // tags: true,
          placeholder: 'Select Model Name',
          dropdownParent: $("#myAutomationModal")
          // data: posCategories
          // allowClear: true
        });
        // var newOption = new Option('Hindi-Bhashini_ai4bharat/conformer-hi-gpu--t4', 'bhashini_ai4bharat/conformer-hi-gpu--t4', false, false);
        // $('#myASRModelListSelect2').append(newOption);
        for (entry of data.models) {

          // console.log ('Entry', entry)
          var newOption = new Option(entry.text, entry.id, false, false);
          $('#myASRModelListSelect2').append(newOption);

          // window.location.reload();
        }

        $('#myASRLanguageListSelect2').empty().trigger('change');
        $('#myASRLanguageListSelect2').select2({
          // tags: true,
          placeholder: 'Select preset value or enter a custom value',
          dropdownParent: $("#myAutomationModal")
          // data: posCategories
          // allowClear: true
        });

        for (entry of data.languages) {
          var newOption = new Option(entry, entry, false, false);
            $('#myASRLanguageListSelect2').append(newOption);
        }

        $('#myASRScriptListSelect2').empty().trigger('change');
        $('#myASRScriptListSelect2').select2({
          // tags: true,
          placeholder: 'Select preset value or enter a custom value',
          dropdownParent: $("#myAutomationModal"),
          // data: posCategories
          allowClear: true
        });       
        
        for (entry of data.scripts) {
          // var newOption = new Option(entry, "Transcription_" + entry, false, false);
          if ((entry != 'IPA') && (entry != 'Latin')) {
            var newOption = new Option(entry, entry, false, false);
            $('#myASRScriptListSelect2').append(newOption);
          }
          else {
            if (entry == 'IPA') {
              $('#ipaspanid').show();
            }
            if (entry == 'Latin') {
              $('#romanspanid').show();
              $('#romanspanid').prop("checked", true);
            }
          }
        }
        $('#myASRModelListSelect2').trigger('change');
        $('#myASRScriptListSelect2').trigger('change');
        // $('#myASRModal').show.bs.modal;
      },
    });
  }
}

function autoTranslation() {
  console.log("Opened!")
  populateBoundaryId('Translation');
  model_list = document.getElementById('mytranslationModelListSelect2')
  console.log('All options', model_list, model_list.length)
  if (model_list.length == 0) {
    $.ajax({
      url: '/lifemodels/getTranslationModelList',
      type: 'POST',
      // data: formData,
      contentType: false,
      cache: false,
      processData: false,
      success: function (data) {
        console.log('Success!');
        console.log(data)

        // Building top-level metadata
        activeSpeaker = document.getElementById("speakeridsdropdown").value;
        filename = document.getElementById("audioFilename").textContent;
        audioDuration = document.getElementById("currentaudioduration").textContent;
        document.getElementById("translationspeakeriduploaddropdown").value = activeSpeaker;
        document.getElementById("translationaudiofileid").value = filename


        // Translation Source
        $('#translateUsingSelect2Id').select2({
          // tags: true,
          placeholder: 'Select Translation Source',
          dropdownParent: $("#myAutomationModal"),
          data: asrmodels
          // allowClear: true
        });

        // Translation Model List
        $('#mytranslationModelListSelect2').empty().trigger('change');
        $('#mytranslationModelListSelect2').select2({
          // tags: true,
          placeholder: 'Select Model Name',
          dropdownParent: $("#myAutomationModal")
          // data: posCategories
          // allowClear: true
        });

        for (entry of data.models) {
          var newOption = new Option(entry.text, entry.id, false, false);
          $('#mytranslationModelListSelect2').append(newOption);
        }

        // Source Script for Translation
        $('#mytranslationSourceScriptListSelect2').empty().trigger('change');
        $('#mytranslationSourceScriptListSelect2').select2({
          // tags: true,
          placeholder: 'Select preset value',
          dropdownParent: $("#myAutomationModal")
          // data: posCategories
          // allowClear: true
        });
        for (entry of data.scripts) {
          // var newOption = new Option(entry, "Transcription_" + entry, false, false);
          if (entry !== 'IPA') {
            var newOption = new Option(entry, entry, false, false);
            $('#mytranslationSourceScriptListSelect2').append(newOption);
          }
        }

        // Target Languages for Translation
        $('#mytranslationTargetLanguageListSelect2').empty().trigger('change');
        $('#mytranslationTargetLanguageListSelect2').select2({
          // tags: true,
          placeholder: 'Select preset value',
          dropdownParent: $("#myAutomationModal")
          // data: posCategories
          // allowClear: true
        });
        for (entry of Object.keys(data.targetLanguages)) {
          var newOption = new Option(entry, entry, false, false);
          $('#mytranslationTargetLanguageListSelect2').append(newOption);
        }

        $('#mytranslationModelListSelect2').trigger('change');
        $('#mytranslationSourceScriptListSelect2').trigger('change');
        $('#mytranslationTargetLanguageListSelect2').trigger('change');
        // $('#myASRModal').show.bs.modal;
      },
    });
  }
}

function autoGloss() {
  console.log("Opened!")
  populateBoundaryId('Gloss');
  model_list = document.getElementById('myfreetranslationModelListSelect2')
  console.log('All options', model_list, model_list.length)
  if (model_list.length == 0) {
    $.ajax({
      url: '/lifemodels/getTranslationModelList',
      type: 'POST',
      // data: formData,
      contentType: false,
      cache: false,
      processData: false,
      success: function (data) {
        console.log('Success!');
        console.log(data)

        // Building top-level metadata
        activeSpeaker = document.getElementById("speakeridsdropdown").value;
        filename = document.getElementById("audioFilename").textContent;
        audioDuration = document.getElementById("currentaudioduration").textContent;
        document.getElementById("glossingspeakeriduploaddropdown").value = activeSpeaker;
        document.getElementById("glossingaudiofileid").value = filename

        //Glossing Model
        $('#myglossingModelListSelect2').select2({
          // tags: true,
          placeholder: 'Select Glossing Model',
          dropdownParent: $("#myAutomationModal"),
          data: glossingModels
          // allowClear: true
        });

        //Glossing Language
        $('#myglossModelLangListSelect2').empty().trigger('change');
        $('#myglossModelLangListSelect2').select2({
          // tags: true,
          placeholder: 'Select Glossing Language',
          dropdownParent: $("#myAutomationModal"),
          // data: glossingLangs
          // allowClear: true
        });

        let projectForm = JSON.parse(localStorage.getItem('activeprojectform'));
        let languages = projectForm['Audio Language'][1];
        for (lang of languages) {
          var newOption = new Option(lang, lang, false, false);
          $('#myglossModelLangListSelect2').append(newOption);
        }
        $('#myglossModelLangListSelect2').trigger('change');

        // Translation Source
        $('#freetranslateUsingSelect2Id').select2({
          // tags: true,
          placeholder: 'Select Translation Source',
          dropdownParent: $("#myAutomationModal"),
          data: asrmodels
          // allowClear: true
        });

        // Translation Model List
        $('#myfreetranslationModelListSelect2').empty().trigger('change');
        $('#myfreetranslationModelListSelect2').select2({
          // tags: true,
          placeholder: 'Select Model Name',
          dropdownParent: $("#myAutomationModal")
          // data: posCategories
          // allowClear: true
        });

        for (entry of data.models) {
          var newOption = new Option(entry.text, entry.id, false, false);
          $('#myfreetranslationModelListSelect2').append(newOption);
        }

        // Source Script for Translation
        $('#myfreetranslationSourceScriptListSelect2').empty().trigger('change');
        $('#myfreetranslationSourceScriptListSelect2').select2({
          // tags: true,
          placeholder: 'Select preset value',
          dropdownParent: $("#myAutomationModal")
          // data: posCategories
          // allowClear: true
        });
        for (entry of data.scripts) {
          // var newOption = new Option(entry, "Transcription_" + entry, false, false);
          if (entry !== 'IPA') {
            var newOption = new Option(entry, entry, false, false);
            $('#myfreetranslationSourceScriptListSelect2').append(newOption);
          }
        }

        // Target Languages for Translation
        $('#myfreetranslationTargetLanguageListSelect2').select2({
          // tags: true,
          placeholder: 'Select preset value',
          dropdownParent: $("#myAutomationModal"),
          data: freeTranslationLanguages
          // allowClear: true
        });
        // for (entry of Object.keys(data.targetLanguages)) {
        //   var newOption = new Option(entry, entry, false, false);
        //   $('#mytranslationTargetLanguageListSelect2').append(newOption);
        // }

        $('#myglossingModelListSelect2').trigger('change');
        $('#myfreetranslationModelListSelect2').trigger('change');
        $('#myfreetranslationSourceScriptListSelect2').trigger('change');
        $('#myfreetranslationTargetLanguageListSelect2').trigger('change');
        // $('#myASRModal').show.bs.modal;
      },
    });
  }
}

$('#myglossModelLangListSelect2').change(function () {
  let audioLang = $(this).val();
  console.log('Audio Lang Gloss', audioLang);
  if (audioLang === 'English') {
    $('#glosstranslationsettingsid').css("display", "none");
    $('#get-translationid').prop("disabled", true);
    // $('#glosstranslationsettingsid :input').css("display", "none");
  }
  else {
    $('#glosstranslationsettingsid').css("display", "block");
    $('#get-translationid').prop("disabled", false);
  }

})

$('#taskTypeSelect2Id').change(function () {
  let selectedTask = $(this).val();
  console.log('Selected Task', selectedTask);
  let otherTasks = automationTaskTypes.filter(function (item) {
    return item.id !== selectedTask;
  });
  console.log('other Tasks', otherTasks);
  for (let otherTask of otherTasks) {
    let otherTaskId = otherTask["id"];
    if (otherTaskId !== "") {
      $("#auto" + otherTaskId + "-divid").css("display", "none");
      $("#auto" + otherTaskId + "-divid :input").prop("disabled", true);
    }
  }
  console.log('Selected Task', selectedTask);
  let selectedDiv = "#auto" + selectedTask + "-divid";
  $(selectedDiv).css("display", "block");
  $(selectedDiv + " :input").prop("disabled", false);
  window["auto" + selectedTask]();
})

$('#syncTranscriptsAllModalButton').on('click', function (e) {
  // console.log("Opened!")
  script_list = document.getElementById('syncTranscriptScriptsSource')
  // console.log('All options', script_list, script_list.length)
  if (script_list.length == 0) {

    $.ajax({
      url: '/lifedata/transcription/getScriptsList',
      type: 'POST',
      // data: formData,
      contentType: false,
      cache: false,
      processData: false,
      success: function (data) {
        // console.log('Success!');
        // console.log(data)
        $('#syncTranscriptScriptsSource').select2({
          // tags: true,
          placeholder: 'Select preset value or enter a custom value',
          dropdownParent: $("#syncTranscriptsAllModal")
          // data: posCategories
          // allowClear: true
        });
        $('#syncTranscriptScriptsTargets').select2({
          // tags: true,
          placeholder: 'Select preset value or enter a custom value',
          dropdownParent: $("#syncTranscriptsAllModal")
          // data: posCategories
          // allowClear: true
        });
        for (entry of data.scripts) {

          if ((entry == 'IPA') || (entry == 'Latin')) {
            var newOption = new Option(entry, entry, false, false);
            var newOption2 = new Option(entry, entry, true, true);
          }
          else {
            var newOption = new Option(entry, entry, true, true);
            var newOption2 = new Option(entry, entry, false, false);
          }
          $('#syncTranscriptScriptsSource').append(newOption);

          // var newOption2 = new Option(entry, entry, false, false);
          $('#syncTranscriptScriptsTargets').append(newOption2);
        }

        $('#syncTranscriptScriptsSource').trigger('change');
        $('#syncTranscriptScriptsTargets').trigger('change');
        // $('#syncTranscriptsAllModal').show.bs.modal;

      }
    })
  }
});

$('#myAutomationButton').on('click', function (e) {
  let task = $('#taskTypeSelect2Id').val();
  console.log('Task', task);
  if (task !== "") {
    populateBoundaryId(task);
  }
})

$('#transcribebtnid').on('click', function (e) {
  // alert("Clicked!");
  // let fname = document.getElementById("asraudiofileid").value
  // let duration = document.getElementById("asraudiodurationid").value
  // let model_name = document.getElementById("myASRModelListSelect2").value
  // let elem_name = document.getElementById("myASRScriptListSelect2").value
  // document.getElementById(elem_name).innerHTML = 'Transcription of audio';
  // console.log(fname, duration, model_name, elem_name);
  // $('#myASRModal').hide.bs.modal;
  let transcForm = document.forms.maketranscriptionformid;
  let formData = new FormData(transcForm);
  // print(formData);
  let boundaryIds = $('#processBoundariesTranscriptionSelect2Id').val();
  $.ajax({
    url: "/lifedata/transcription/maketranscription",
    method: "POST",
    data: formData,
    processData: false,
    contentType: false,
    success: function (data) {
      console.log(data);
      try {
        let activeBoundaryId = JSON.parse(localStorage.getItem('activeboundaryid'));
          // console.log('All boundaries', boundaryIds);
          // console.log('Active boundary ID', activeBoundaryId);
          if ((boundaryIds.length == 1) && (boundaryIds[0] === activeBoundaryId)) {
            // console.log('Setting Data');
            let syncedData = data.data;
            if (Object.keys(syncedData).length === 0) {
              stopLoader();
              alert('Boundary mismatch. Please save the created boundaries. OR There is model and script mismatch');
              return false
            }
            // console.log('Synced Data', syncedData);
            // for (const currentBoundaryData of syncedData) {
            for (const currentBoundaryId in syncedData) {
              // console.log('Current Boundary', currentBoundaryId);
              if (currentBoundaryId === activeBoundaryId) {
                let currentTransData = syncedData[currentBoundaryId];
                // console.log('Current transc data', currentTransData);
                let response500 = true;
                for (const currentScript in currentTransData) {
                  let value = currentTransData[currentScript];
                  console.log('Current script value', value);
                  if (value !== '') {
                    response500 = false;
                  }
                  $('#Transcription_' + currentScript).val(value).change();
                  var e = jQuery.Event("input", { keyCode: 64 });
                  // console.log($('#Transcription_' + currentScript)[0]);
                  // console.log(document.getElementById('#Transcription_' + currentScript)[0]);
                  autoSavetranscription(e, $('#Transcription_' + currentScript)[0]);
                  // stopLoader();
                  if (response500) {
                    alert('Unable to predict! Maybe boundary is more than 20s or boundary is without any speech!')
                  }
                }
              }
            }
            // }
          }
          else {
            window.location.reload();
            // alert('Going for reload', activeBoundaryId, boundaryIds);
          }
          stopLoader();
      }
      catch {
        alert("Some error occured!!");
        stopLoader();
      }
    }
  });
});

$('#translatebtnid').on('click', function (e) {
  let transForm = document.forms.maketranslationformid;
  let formData = new FormData(transForm);
  // print(formData);
  let boundaryIds = $('#processBoundariesTranslationSelect2Id').val();
  let projectForm = JSON.parse(localStorage.getItem('activeprojectform'));
  if ('Translation' in projectForm) {
    $.ajax({
      url: "/lifedata/maketranslation",
      method: "POST",
      data: formData,
      processData: false,
      contentType: false,
      success: function (data) {
        try {
          let allLangScripts = projectForm['Translation'][1];
          console.log('All Lang Scripts', allLangScripts);
          let activeBoundaryId = JSON.parse(localStorage.getItem('activeboundaryid'));
          console.log('All boundaries', boundaryIds);
          console.log('Active boundary ID', activeBoundaryId);
          console.log('Data', data);
          // alert('Received!');
          if ((boundaryIds.length == 1) && (boundaryIds[0] === activeBoundaryId)) {
            // console.log('Setting Data');
            let syncedData = data.data;
            // console.log('Synced Data', syncedData);
            for (const currentBoundaryData of syncedData) {            
              for (const currentBoundaryId in currentBoundaryData) {
                // console.log('Current Boundary', currentBoundaryId);
                if (currentBoundaryId === activeBoundaryId) {
                  let currentTransData = currentBoundaryData[currentBoundaryId];
                  // console.log('Current transl data', currentTransData);
                  for (const currentLangScript in currentTransData) {
                    if (currentLangScript in allLangScripts) {
                      let currentScript = allLangScripts[currentLangScript];
                      let value = currentTransData[currentLangScript];
                      // console.log('Current script value', value);
                      $('#Translation_' + currentScript).val(value).change();
                      var e = jQuery.Event("input", { keyCode: 64 });
                      // console.log($('#Translation_' + currentScript)[0]);
                      // console.log(document.getElementById('#Transcription_' + currentScript)[0]);
                      autoSavetranscription(e, $('#Translation_' + currentScript)[0]);
                    }
                  }
                }
              }
            }
          }
          else {
            window.location.reload();
            // alert('Going for reload', activeBoundaryId, boundaryIds);
          }
          stopLoader();
        }
        catch {
          alert("Some error occured!!");
          stopLoader();
        }
      }
    });
  }
  else {
    stopLoader();
    alert('Translation is not available for current project');
  }
});

$('#glossbtnid').on('click', function (e) {
  let transForm = document.forms.makeglossformid;
  let formData = new FormData(transForm);
  // print(formData);
  let boundaryIds = $('#processBoundariesGlossSelect2Id').val();
  let projectForm = JSON.parse(localStorage.getItem('activeprojectform'));
  if ('Interlinear Gloss' in projectForm) {
    $.ajax({
      url: "/lifedata/makegloss",
      method: "POST",
      data: formData,
      processData: false,
      contentType: false,
      success: function (data) {
        try {
          // let allLangScripts = projectForm['Translation'][1];
          // console.log('All Lang Scripts', allLangScripts);
          let activeBoundaryId = JSON.parse(localStorage.getItem('activeboundaryid'));
          let localStorageRegions = JSON.parse(localStorage.getItem('regions'));
          // console.log('All boundaries', boundaryIds);
          // console.log('Active boundary ID', activeBoundaryId);
          // console.log('Data', data);
          // alert('Received!');
          if ((boundaryIds.length == 1) && (boundaryIds[0] === activeBoundaryId)) {
            // console.log('Setting Data');
            let syncedData = data.data;
            // console.log('Synced Data', syncedData);
            // for (const currentBoundaryData of syncedData) {            
              for (const currentBoundaryId in syncedData) {
                // console.log('Current Boundary', currentBoundaryId);
                if (currentBoundaryId === activeBoundaryId) {
                  let currentGlossData = syncedData[currentBoundaryId];
                  // console.log('Current gloss data', currentGlossData);
                  for (let p = 0; p < localStorageRegions.length; p++) {
                    // console.log(p);
                    if (localStorageRegions[p]['data']['sentence'][currentBoundaryId] &&
                        localStorageRegions[p]['boundaryID'] === activeBoundaryId) {
                        // console.log(localStorageRegions[p]['data']['sentence'][boundaryID])
                      localStorageRegions[p]['data']['sentence'][boundaryID]['glossTokenIdInfo'] = currentGlossData;
                        break;
                    }
                  }
                  // for (const token_id in currentGlossData) {
                  //   let tokenGlossData = currentGlossData[token_id];
                  //   for (const glossField in tokenGlossData) {

                  //     let currentScript = allLangScripts[currentLangScript];
                  //     let value = currentTransData[currentLangScript];
                  //     console.log('Current script value', value);
                  //     $('#Translation_' + currentScript).val(value).change();
                  //     var e = jQuery.Event("input", { keyCode: 64 });
                  //     console.log($('#Translation_' + currentScript)[0]);
                  //     // console.log(document.getElementById('#Transcription_' + currentScript)[0]);
                  //     autoSavetranscription(e, $('#Translation_' + currentScript)[0]);
                  //     stopLoader();
                  //   }
                  // }
                }
              // }
            }
            localStorage.setItem("regions", JSON.stringify(localStorageRegions));
            $('#interlinearglosstab').click();
          }
          else {
            window.location.reload();
            // alert('Going for reload', activeBoundaryId, boundaryIds);
          }
          stopLoader();
        }
        catch {
          alert("Some error occured!!");
          stopLoader();
        }
      }
    });
  }
  else {
    stopLoader();
    alert('Interlinear Glossing is not available for current project');
  }
});



$('#syncTranscriptsAllModalButton').on('click', function (e) {
  populateBoundaryId('SyncTranscription', 'syncTranscriptsAllModal');
});

function populateBoundaryId (task, parent='myAutomationModal') {
  $('#processBoundaries'+task+'Select2Id').empty().trigger('change');
  $('#processBoundaries'+task+'Select2Id').select2({
          // tags: true,
          placeholder: 'Select Boundary ID',
          dropdownParent: $("#"+parent)
          // data: posCategories
          // allowClear: true
        });
  let regions = JSON.parse(localStorage.getItem('regions'));
  let activeBoundaryId = JSON.parse(localStorage.getItem('activeboundaryid'));
  // console.log('Active Boundary ID', activeBoundaryId);
  // for (const [regionn, regionData] of regions) {
  var defaultAdded = false;
  for (let regionData of regions) {
    // console.log(regionData);
    let currentBoundaryId = regionData['boundaryID'];
    // console.log('Current ID', currentBoundaryId);
    if (activeBoundaryId === currentBoundaryId) {
      var newOption = new Option(currentBoundaryId + '(Current Boundary)', currentBoundaryId, true, true);
      defaultAdded = true;
    }
    else {
      var newOption = new Option(currentBoundaryId, currentBoundaryId, false, false);
    }
    $('#processBoundaries'+task+'Select2Id').append(newOption); 
  }
  if (defaultAdded) {
    var newOption = new Option('* (All Boundaries)', '*', false, false);
  }
  else {
    var newOption = new Option('* (All Boundaries)', '*', true, true);
  }
  $('#processBoundaries'+task+'Select2Id').append(newOption);
  $('#processBoundaries'+task+'Select2Id').trigger('change');
};

function updateClickSource(e) {
  let currentId = e.id;
  // document.getElementById('clickSourceId')
  $('#clickSourceId').val (currentId);
  console.log(currentId);
}