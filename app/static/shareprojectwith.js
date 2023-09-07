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
      else if (sharespeakerlist.includes(d)) {
        sharespeakers.push(d)
      }
    }
    // console.log(sharewithusers, sharespeakers, displayRadioValue())
    data['sharewithusers'] = sharewithusers
    data['sharespeakers'] = sharespeakers
    data['sharemode'] = displayRadioValue()
    // console.log(data['sharemode']);
    try {
      sharechecked = document.getElementById('sharechecked').checked;
    }
    catch(err) {
      // console.log(typeof err.message);
      sharechecked = '';
    }
    data['sharechecked'] = String(sharechecked)

    try {
      downloadchecked = document.getElementById('downloadchecked').checked;
    }
    catch(err) {
      // console.log(typeof err.message);
      downloadchecked = '';
    }
    
    data['downloadchecked'] = String(downloadchecked)

    try {
      sharelatestchecked = document.getElementById('sharelatestchecked').checked;
    }
    catch(err) {
      // console.log(typeof err.message);
      sharelatestchecked = '';
    }
    data['sharelatestchecked'] = String(sharelatestchecked)

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
    // console.log(ele);
    sharemode = ''
    for(i = 0; i < ele.length; i++) {
        if(ele[i].checked) {
          // console.log(ele[i].id);
          // sharemode =  ele[i].value - 1
          sharemode =  ele[i].id;
        }
    }
    // console.log(sharemode);
    sharemode = shareModeObject[sharemode];
    // console.log(sharemode);
    if (sharemode === undefined) {
      sharemode = 0;
    }
    return sharemode
  }