// AJAX request to fetch active access code data
function showTable(event) {
    var code = event.target.dataset.code;
  
    // Perform AJAX request to fetch data
    $.ajax({
      type: 'POST',
      url: "{{ url_for('karya_bp.active_accesscodes') }}",
      data: {
        code: code
      },
      success: function(response) {
        console.log(response);
        if ($.isEmptyObject(response)) {
          alert('No data found for the selected code!');
        } else {
          var name = response.response.current.workerMetadata.name;
          var age = response.response.current.workerMetadata.agegroup;
          var gender = response.response.current.workerMetadata.gender;
          var accessCode = response.response.karyaaccesscode;
          var speakerID = response.response.karyaspeakerid;
          var status = response.response.isActive;
          var fetchData = response.response.fetchData;
          var educationalevel = response.response.current.workerMetadata.educationlevel;
          var educationmediumupto12 = response.response.current.workerMetadata.educationmediumupto12;
          var educationmediumafter12 = response.response.current.workerMetadata.educationmediumafter12 ;
          var speakerlanguage = response.response.current.workerMetadata.speakerlanguage;
          var place = response.response.current.workerMetadata.recordingplace;
          var typeofplace = response.response.current.workerMetadata.typeofrecordingplace;
  
          // Set values in the hidden table
          $('#hiddenTableName').text(name);
          $('#hiddenTableAge').text(age);
          $('#hiddenTableGender').text(gender);
          $('#hiddenTableAccessCode').text(accessCode);
          $('#hiddenTableSpeakerID').text(speakerID);
          $('#hiddenTableStatus').text(status);
          $('#hiddenTableFetchData').text(fetchData);
          $('#hiddenTableEducationalevel').text(educationalevel);
          $('#hiddenTableEducationmediumupto12').text(educationmediumupto12);
          $('#hiddenTableEducationmediumafter12').text(educationmediumafter12);
          $('#hiddenTablePlace').text(place);
          $('#hiddenTableTypeofplace').text(typeofplace);
  
          // Show the hidden table
          $('#hiddenTable').show();
        }
      },
      error: function(error) {
        console.log(error);
      }
    });
  }
  
  function editHiddenTableRow() {
    // Enable edit mode
    $('#hiddenTable td:not(:first-child)').each(function() {
      var text = $(this).text();
      $(this).html(`<input type="text" value="${text}">`);
    });
  
    // Show the Save button
    $('#hiddenTable button:nth-child(2)').show();
  }
  
  function saveHiddenTableRow() {
    var data = {
      name: $('#hiddenTableName input').val(),
      age: $('#hiddenTableAge input').val(),
      gender: $('#hiddenTableGender input').val(),
      accessCode: $('#hiddenTableAccessCode input').val(),
      speakerID: $('#hiddenTableSpeakerID input').val(),
      status: $('#hiddenTableStatus input').val(),
      fetchData: $('#hiddenTableFetchData input').val(),
      educationalevel: $('#hiddenTableEducationalevel input').val(),
      educationmediumupto12: $('#hiddenTableEducationmediumupto12 input').val(),
      educationmediumafter12: $('#hiddenTableEducationmediumafter12 input').val(),
      place: $('#hiddenTablePlace input').val(),
      typeofplace: $('#hiddenTableTypeofplace input').val()
    };
  
    console.log('Data to be updated:', data);
  
    // Send the updated data to Flask using AJAX
    $.ajax({
      type: 'POST',
      url: "{{ url_for('karya_bp.update_table_data') }}",
      data: data,
      success: function(response) {
        // Handle success response
        alert('Data updated successfully!');
        console.log("response :", response);
  
        // Disable edit mode and hide the Save button
        $('#hiddenTable td:not(:first-child)').each(function() {
          var text = $(this).find('input').val();
          $(this).html(text);
        });
        $('#hiddenTable button:nth-child(2)').hide();
      },
      error: function(error) {
        console.log(error);
      }
    });
  }
  
  function closeHiddenTable() {
    // Hide the hidden table
    $('#hiddenTable').hide();
  }
  