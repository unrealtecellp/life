var currentSpeakerCount = 0;
var speakerCount = 0;

$(document).ready(function() {
      $.getJSON('/assignkaryaaccesscode', {
      }, function(data) {
         
    });
    $('#assignKaryaAccessCodeModal').on('show.bs.modal', function() {
      console.log('on show');
      if (currentSpeakerCount > 0) {
        speakerDetailForm();
      }
      else {
        alert('Speakers Details Saved:)');
        window.location.reload();
      }

    });
    $(document).on("hidden.bs.modal", "#assignKaryaAccessCodeModal", function () {
      document.getElementById('speakerdetail').innerHTML='';
    });
  });

$(".assignkaryaaccesscodebtn").click(function() {
  console.log('assignkaryaaccesscodebtn click');
  speakerCount = document.getElementById('assignkaryaaccesscodenum').value
  currentSpeakerCount = speakerCount;
});

$(".savespeakerdata").click(function() {
  console.log('save speaker data click');
  currentSpeakerCount -= 1;
  document.getElementById('speakerdetail').innerHTML='';
  $("#assignKaryaAccessCodeModal").modal();
});

function speakerDetailForm() {
  var speakerMetadata = ['Name', 'Age', 'Gender', 'Occupation']
  var speakerinpt = '<h4>Details for Speaker '+((speakerCount-currentSpeakerCount)+1)+'</h4>';
  for (let i=0; i<speakerMetadata.length; i++) {
    speakerinpt += '<div class="form-group">'+
            '<label for="'+ speakerMetadata[i] +'">'+ speakerMetadata[i] +'</label>'+
            '<input type="text" class="form-control" id="'+ speakerMetadata[i] +'"'+ 
            'placeholder="'+ speakerMetadata[i] +'" name="'+ speakerMetadata[i] +'">'+
            '</div>';
  }
  $(".speakerdetail").append(speakerinpt);
}

var inpt = '<select class="form-control" name="assignkaryaaccesscodenum" id="assignkaryaaccesscodenum">'
for (let i=1; i<=10; i++) {
  inpt += '<option value="'+i+'">'+i+'</option>'
}
inpt += '</select>'
$(".assignkaryaaccesscodecount").append(inpt);
