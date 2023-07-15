var usersToShare = ''
var speakersToShare = ''
var shareuserlist = []
var sharespeakerlist = []
var shareModeObject = {
  'removeallaccess': -1,
  'view': 0,
  // 'download': 1,
  'edit': 2,
  'add':3,
  'delete': 4
}
var shareModeList = Object.keys(shareModeObject)
// console.log(shareModeList);
var shareMode = '';
var shareLatest = '';

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
        for (let [key, value] of Object.entries(data.sourceList)){
          speakersToShare += '<option value="'+value+'">'+value+'</option>';
          sharespeakerlist.push(value)

        };
        localStorage.setItem("shareuserlist", JSON.stringify(shareuserlist));
        localStorage.setItem("sharespeakerlist", JSON.stringify(sharespeakerlist));
        $('#shareProjectSelect').append(usersToShare)
        shareLatest += '<input type="checkbox" id="sharelatestchecked" name="sharelatestchecked" value="">'+
                      '<label for="sharelatestchecked">&nbsp; Share Only Data</label><br>';
        $('#shareLatest').append(shareLatest)
        $('#shareSpeakerSelect').append(speakersToShare)

        shareMode += '<hr><h4>Access Control:</h4>';
        for (i=0; i<=sharemodecount+1;i++) {
          // console.log(shareModeList[i]);
          if (shareModeList[i] !== undefined) {
            shareMode += '<input type="radio" id="'+shareModeList[i]+'" name="sharemode" value="'+i+'">'+
                        '<label for="'+shareModeList[i]+'">&nbsp; '+shareModeList[i]+'</label><br>';
          }
        }

        shareMode += '<hr><h4>Advanced Access Control:</h4>';
        shareMode += '<input type="checkbox" id="downloadchecked" name="downloadchecked" value="">'+
                      '<label for="downloadchecked">&nbsp; Allow Download</label>';
        shareMode += '&nbsp;&nbsp;&nbsp;&nbsp;';
        // shareMode += 'Access To Share Button&nbsp;';
        shareMode += '<input type="checkbox" id="sharechecked" name="sharechecked" value="">'+
                      '<label for="sharechecked">&nbsp; Access To Share Button</label><br>';

        $('.sharemode').append(shareMode);
      });
      $('#myShareProjectModal').on('show.bs.modal', function() {
        $('#shareProjectSelect').select2({
        placeholder: 'Share with users',
        // data: usersList,
        allowClear: true
      });
      $('#shareSpeakerSelect').select2({
        placeholder: 'source',
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
