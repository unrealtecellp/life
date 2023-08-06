var usersToShare = ''
var sharealert = ''
// share project button on dictionary view page
// $(document).ready(function() {
function audioBrowseActionShare(audioInfo) {
    $(".browsesharewith").click(function() {
      console.log(audioInfo)
      let audioBrowseInfo = getAudioBrowseInfo();
      // var $ele = Object.values(document.getElementsByClassName('select2-selection__choice'));
      var $ele = $('#browseShareSelect').select2('data');
      console.log($ele);
      var $users = []
    for (i = 0; i < $ele.length; i++) {
    // var userName = $ele[i].getAttribute('title')
        let userName = $ele[i].text
        $users.push(userName)
    }
    // console.log(Object.assign({}, $users))
      $.getJSON('/browsesharewith', {
            a : JSON.stringify({
              "users": $users,
              "audioInfo": audioInfo,
              "audioBrowseInfo": audioBrowseInfo
            })
      }, function(data) {
        // console.log(data);
        // if (data.users[0] !== '') {
        //   alert("File shared with: " + data.users)
          
        // }
        window.location.reload();
      });
      return false;
    });
  }
  // });
