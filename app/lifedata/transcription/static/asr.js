$('#myASRModalButton').on('click', function (e) {
  console.log("Opened!")
    $.ajax({
    url: '/lifemodels/getModelList',
    type: 'POST',
    // data: formData,
    contentType: false,
    cache: false,
    processData: false,
    success: function(data) {
      console.log('Success!');
      console.log(data)
      for (entry of data.models) {
        $('#myASRModelListSelect2').select2({
          // tags: true,
          placeholder: 'Select preset value or enter a custom value',
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
        var newOption = new Option(entry, entry, false, false);
        $('#myASRScriptListSelect2').append(newOption);
      }
      $('#myASRModelListSelect2').trigger('change');
      $('#myASRScriptListSelect2').trigger('change');
      $('#myASRModal').show.bs.modal;
    },
  });
    // activeSpeaker = document.getElementById("speakeridsdropdown").value;
    // filename = document.getElementById("audioFilename").textContent;
    // audioDuration = document.getElementById("currentaudioduration").textContent;
    // // alert(audioDuration) 
    // document.getElementById("makeboundaryspeakeriduploaddropdown").value = activeSpeaker;
    // document.getElementById("makeboundaryaudiofileid").value = filename
    // document.getElementById("makeboundaryaudiodurationid").value = audioDuration
    // // document.getElementById("speakeriduploaddropdown-divid").innerHTML = activeSpeaker;
    // $('#myMakeBoundaryModal').show.bs.modal;

})