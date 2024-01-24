$('#myASRModalButton').on('click', function (e) {
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
        filename = document.getElementById("audioFilename").textContent;
        audioDuration = document.getElementById("currentaudioduration").textContent;
        document.getElementById("asrspeakeriduploaddropdown").value = activeSpeaker;
        document.getElementById("asraudiofileid").value = filename
        document.getElementById("asraudiodurationid").value = audioDuration

        for (entry of data.models) {
          $('#myASRModelListSelect2').select2({
            // tags: true,
            placeholder: 'Select Model Name',
            dropdownParent: $("#myASRModal")
            // data: posCategories
            // allowClear: true
          });
          // console.log ('Entry', entry)
          var newOption = new Option(entry.text, entry.id, false, false);
          $('#myASRModelListSelect2').append(newOption);

          // window.location.reload();
        }

        for (entry of data.scripts) {
          $('#myASRScriptListSelect2').select2({
            // tags: true,
            placeholder: 'Select preset value or enter a custom value',
            dropdownParent: $("#myASRModal")
            // data: posCategories
            // allowClear: true
          });
          // var newOption = new Option(entry, "Transcription_" + entry, false, false);
          var newOption = new Option(entry, entry, false, false);
          $('#myASRScriptListSelect2').append(newOption);
        }
        $('#myASRModelListSelect2').trigger('change');
        $('#myASRScriptListSelect2').trigger('change');
        $('#myASRModal').show.bs.modal;
      },
    });
  }
  // activeSpeaker = document.getElementById("speakeridsdropdown").value;
  // filename = document.getElementById("audioFilename").textContent;
  // audioDuration = document.getElementById("currentaudioduration").textContent;
  // // alert(audioDuration) 
  // document.getElementById("makeboundaryspeakeriduploaddropdown").value = activeSpeaker;
  // document.getElementById("makeboundaryaudiofileid").value = filename
  // document.getElementById("makeboundaryaudiodurationid").value = audioDuration
  // // document.getElementById("speakeriduploaddropdown-divid").innerHTML = activeSpeaker;
  // $('#myMakeBoundaryModal').show.bs.modal;

});

$('#transcribebtnid').on('click', function (e) {
  // alert("Clicked!");
  let fname = document.getElementById("asraudiofileid").value
  let duration = document.getElementById("asraudiodurationid").value
  let model_name = document.getElementById("myASRModelListSelect2").value
  let elem_name = document.getElementById("myASRScriptListSelect2").value
  document.getElementById(elem_name).innerHTML = 'Transcription of audio';
  console.log(fname, duration, model_name, elem_name);
  $('#myASRModal').hide .bs.modal;
});