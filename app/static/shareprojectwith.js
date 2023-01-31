// share project button on dictionary view page
$(document).ready(function() {  
    $(".shareprojectwith").click(function() {
      var $ele = Object.values(document.getElementsByClassName('select2-selection__choice'));
      // var $ele = document.getElementById('shareProjectSelect')
      // console.log($ele);
      var $users = []
      // var $speakers = []
    for (i = 0; i < $ele.length; i++) {
    //   console.log($ele[i].getAttribute('title'))
      var userName = $ele[i].getAttribute('title')
        $users.push(userName)
    }
    // console.log(Object.assign({}, $users))
    // console.log($users);
    let shareuserlist = JSON.parse(localStorage.shareuserlist)
    let sharespeakerlist = JSON.parse(localStorage.sharespeakerlist)
    var sharewithusers= []
    var sharespeakers = []
    var data = Object()
    // console.log(sharespeakerlist, shareuserlist)
    for (i=0; i<$users.length; i++) {
      // console.log($users[i]);
      d = $users[i]
      if (shareuserlist.includes(d)) {
        sharewithusers.push(d)
      }
      else if (sharespeakerlist.includes($users[i])) {
        sharespeakers.push(d)
      }
    }
    // console.log(sharewithusers, sharespeakers, displayRadioValue())
    data['sharewithusers'] = sharewithusers
    data['sharespeakers'] = sharespeakers
    data['sharemode'] = displayRadioValue()
    try {
      sharechecked = document.getElementById('sharechecked').checked;
    }
    catch(err) {
      // console.log(typeof err.message);
      sharechecked = '';
    }
    
    data['sharechecked'] = String(sharechecked)
    // console.log(data);
      $.ajax({
        url: '/shareprojectwith',
        type: 'GET',
        data: {'data': JSON.stringify(data)},
        contentType: "application/json; charset=utf-8", 
        success: function(response){
          // console.log(response);
        }
    });
    return false; 
    });
  });

  function displayRadioValue() {
    var ele = document.getElementsByName('sharemode');
    // console.log(ele)
    sharemode = ''
    for(i = 0; i < ele.length; i++) {
        if(ele[i].checked)
          sharemode =  ele[i].value - 1
    }
    // console.log(sharemode)
    
    return sharemode
  }