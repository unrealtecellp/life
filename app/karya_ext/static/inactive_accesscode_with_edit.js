function showDTable(event) {
    var code = event.target.dataset.code;

    // Perform AJAX request to fetch data
    $.ajax({
      type: 'POST',
      url: "{{ url_for('karya_bp.deactive_accesscodes') }}",
      data: {
        code: code
      },
      success: function(response) {
        console.log(response);
        console.log('james');
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
          $('#hiddenDTableDName').text(name);
          $('#hiddenDTableDAge').text(age);
          $('#hiddenDTableDGender').text(gender);
          $('#hiddenDTableDAccessCode').text(accessCode);
          $('#hiddenDTableDSpeakerID').text(speakerID);
          $('#hiddenDTableDStatus').text(status);
          $('#hiddenDTableDFetchData').text(fetchData);
          $('#hiddenDTableDEducationalevel').text(educationalevel);
          $('#hiddenDTableDEducationmediumupto12').text(educationmediumupto12);
          $('#hiddenDTableDEducationmediumafter12').text(educationmediumafter12);
          $('#hiddenDTableDPlace').text(place);
          $('#hiddenDTableDTypeofplace').text(typeofplace)
;
          // Show the hidden table
          $('#hiddenDTable').show();
        }
      },
      error: function(error) {
        console.log(error);
      }
    });
  }

  function edithiddenDTableRow() {
// Enable edit mode
$('#hiddenDTable td:not(:first-child)').each(function() {
  var text = $(this).text();
  $(this).html(`<input type="text" value="${text}">`);
});

// Show the Save button
$('#hiddenDTable button:nth-child(2)').show();
}

function savehiddenDTableRow() {
var data = {
  name: $('#hiddenDTableDName input').val(),
  age: $('#hiddenDTableDAge input').val(),
  gender: $('#hiddenDTableDGender input').val(),
  accessCode: $('#hiddenDTableDAccessCode input').val(),
  speakerID: $('#hiddenDTableDSpeakerID input').val(),
  status: $('#hiddenDTableDStatus input').val(),
  fetchData: $('#hiddenDTableDFetchData input').val(),
  educationalevel: $('#hiddenDTableDEducationalevel input').val(),
  educationmediumupto12: $('#hiddenDTableDEducationmediumupto12 input').val(),
  educationmediumafter12: $('#hiddenDTableDEducationmediumafter12 input').val(),
  place: $('#hiddenDTableDPlace input').val(),
  typeofplace: $('#hiddenDTableDTypeofplace input').val()
};

console.log('Data to be updated:', data);

// Send the updated data to Flask using AJAX
$.ajax({
  type: 'POST',
  url: "{{ url_for('karya_bp.deactive_update_table_data') }}",
  data: data,
  success: function(response) {
    // Handle success response
    alert('Data updated successfully!');
    console.log("response :", response);

    // Disable edit mode and hide the Save button
    $('#hiddenDTable td:not(:first-child)').each(function() {
      var text = $(this).find('input').val();
      $(this).html(text);
    });
    $('#hiddenDTable button:nth-child(2)').hide();
  },
  error: function(error) {
    console.log(error);
  }
});
}

function closehiddenDTable() {
// Hide the hidden table
$('#hiddenDTable').hide();
}