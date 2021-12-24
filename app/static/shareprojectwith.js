var usersToShare = ''

// share project button on dictionary view page
$(document).ready(function() {  
    $(".shareprojectwith").click(function() {
      var $ele = Object.values(document.getElementsByClassName('select2-selection__choice'));
      var $users = []
    for (i = 0; i < $ele.length; i++) {
    //   console.log($ele[i].getAttribute('title'))
    var userName = $ele[i].getAttribute('title')
        $users.push(userName)
    }
    console.log(Object.assign({}, $users))
      $.getJSON('/shareprojectwith', {
            a:String($users)
      }, function(data) {
        // console.log(data.users)
      });
      return false; 
    });
  });