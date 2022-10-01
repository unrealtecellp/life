var usersToShare = ''
var speakersToShare = ''
var shareuserlist = []
var sharespeakerlist = []
var shareModeList = ['view', 'download', 'edit', 'add', 'delete']
var shareMode = ''

// share project button on dictionary view page
$(document).ready(function() { 
      
      $.getJSON('/userslist', {
      }, function(data) {
        sharemodecount = data.sharemode
        // console.log('qwaaszxzx') 
        // console.log(data.usersList)
        for (let [key, value] of Object.entries(data.usersList)){
          usersToShare += '<option value="'+value+'">'+value+'</option>';
          shareuserlist.push(value)

        };
        for (let [key, value] of Object.entries(data.speakersList)){
          speakersToShare += '<option value="'+value+'">'+value+'</option>';
          sharespeakerlist.push(value)

        };
        localStorage.setItem("shareuserlist", JSON.stringify(shareuserlist));
        localStorage.setItem("sharespeakerlist", JSON.stringify(sharespeakerlist));
        $('#shareProjectSelect').append(usersToShare)
        $('#shareSpeakerSelect').append(speakersToShare)
        for (i=0; i<=sharemodecount;i++) {
          shareMode += '<input type="radio" id="'+shareModeList[i]+'" name="sharemode" value="'+i+'">'+
                        '<label for="'+shareModeList[i]+'">&nbsp; '+shareModeList[i]+'</label><br>';
        }
        shareMode += '<input type="checkbox" id="sharechecked" name="sharechecked" value="">'+
                      '<label for="sharechecked">&nbsp; Share</label><br>';

        // var shareMode = '<input type="radio" id="view" name="sharemode" value="0">'+
        //                 '<label for="view">&nbsp; View</label><br>'+
        //                 '<input type="radio" id="download" name="sharemode" value="1">'+
        //                 '<label for="download">&nbsp; Download</label><br>'+
        //                 '<input type="radio" id="edit" name="sharemode" value="2">'+
        //                 '<label for="edit">&nbsp; Edit</label><br>'+
        //                 '<input type="radio" id="add" name="sharemode" value="3">'+
        //                 '<label for="add">&nbsp; Add</label><br>'+
        //                 '<input type="radio" id="delete" name="sharemode" value="4">'+
        //                 '<label for="delete">&nbsp; Delete</label><br>'+
        //                 '<br>'+
        //                 '<input type="checkbox" id="sharechecked" name="sharechecked" value="">'+
        //                 '<label for="sharechecked">&nbsp; Share</label><br>';

        $('.sharemode').append(shareMode);
      });
      $('#myShareProjectModal').on('show.bs.modal', function() {
        $('#shareProjectSelect').select2({
        placeholder: 'Share with users',
        // data: usersList,
        allowClear: true
      });
      $('#shareSpeakerSelect').select2({
        placeholder: 'speakers',
        // data: usersList,
        allowClear: true
      });
      })
      
      $('#myShareProjectModal').on('hidden.bs.modal', function() {
        $('#shareProjectSelect').select2('destroy');
        $('#shareSpeakerSelect').select2('destroy');
      })
  });

$(".shareprojectwith").click(function() {
  alert('Project sharing successful :)');
  });

