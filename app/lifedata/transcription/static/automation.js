
// {
//   "name": "BHASHINI",
//   "value": "bhashini"
//   }]


function autoTranscription() {
  console.log("Opened!")
  model_list = document.getElementById('myASRModelListSelect2')
  console.log('All options', model_list, model_list.length)
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

        $('#myASRScriptListSelect2').select2({
          // tags: true,
          placeholder: 'Select preset value or enter a custom value',
          dropdownParent: $("#myAutomationModal")
          // data: posCategories
          // allowClear: true
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
        $('#myglossModelLangListSelect2').select2({
          // tags: true,
          placeholder: 'Select Glossing Language',
          dropdownParent: $("#myAutomationModal"),
          data: glossingLangs
          // allowClear: true
        });

        // Translation Source
        $('#freetranslateUsingSelect2Id').select2({
          // tags: true,
          placeholder: 'Select Translation Source',
          dropdownParent: $("#myAutomationModal"),
          data: asrmodels
          // allowClear: true
        });

        // Translation Model List
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

$('#transcribebtnid').on('click', function (e) {
  // alert("Clicked!");
  let fname = document.getElementById("asraudiofileid").value
  let duration = document.getElementById("asraudiodurationid").value
  let model_name = document.getElementById("myASRModelListSelect2").value
  let elem_name = document.getElementById("myASRScriptListSelect2").value
  document.getElementById(elem_name).innerHTML = 'Transcription of audio';
  console.log(fname, duration, model_name, elem_name);
  $('#myASRModal').hide.bs.modal;
});

function updateClickSource(e) {
  let currentId = e.id;
  // document.getElementById('clickSourceId')
  $('#clickSourceId').val (currentId);
  console.log(currentId);
}