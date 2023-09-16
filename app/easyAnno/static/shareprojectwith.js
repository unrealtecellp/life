var usersToShare = ''
var sharealert = ''
// share project button on dictionary view page
$(document).ready(function() { 
    $(".shareprojectwith").click(function() {
      var $ele = Object.values(document.getElementsByClassName('select2-selection__choice'));
      var $users = []
    for (i = 0; i < $ele.length; i++) {
    var userName = $ele[i].getAttribute('title')
        $users.push(userName)
    }
    console.log(Object.assign({}, $users))
      $.getJSON('/shareprojectwith', {
            a:String($users)
      }, function(data) {
        if (data.users[0] !== '') {
          alert("File shared with: " + data.users)
          
        }
        window.location.reload();
      });
      return false; 
    });
  });
