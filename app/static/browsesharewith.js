var usersToShare = ''
var sharealert = ''
// share project button on dictionary view page
$(document).ready(function() {
// function audioBrowseActionShare(audioInfo) {
  $(".browsesharewith").click(function() {
    // console.log(audioInfo)
    // let audioBrowseInfo = getAudioBrowseInfo();
    // var $ele = Object.values(document.getElementsByClassName('select2-selection__choice'));
    var browseShareSelectedMode = $('#browseShareSelectMode').select2('data');
    browseShareSelectedMode = browseShareSelectedMode[0].id
    // console.log(browseShareSelectedMode);
    if (browseShareSelectedMode === 'share') {
      var $ele = $('#browseShareSelect').select2('data');
    }
    else if (browseShareSelectedMode === 'remove') {
      var $ele = $('#browseRemoveShareSelect').select2('data');
    }
    // console.log($ele);
    var $users = []
    for (i = 0; i < $ele.length; i++) {
    // var userName = $ele[i].getAttribute('title')
        let userName = $ele[i].text
        $users.push(userName)
    }
    // console.log(Object.assign({}, $users));
    if ($users.length === 0) {
      alert('No User selected!!');
      return false;
    }
    $.getJSON('/browsesharewith', {
          a : JSON.stringify({
            "browseShareSelectedMode": browseShareSelectedMode,
            "users": $users,
            "audioInfo": audioIds,
            // "audioBrowseInfo": audioBrowseInfo
          })
    }, function(data) {
        // console.log(data);
        if (data.sharingSuccess[0]) {
          alert('File(s) '+data.sharingSuccess[1]+' successful :)');
        }
        else {
          alert('File(s) '+data.sharingSuccess[1]+' failed :(');
        }
        // return false;
        // window.location.reload();
    });
    return false;
  });
});
