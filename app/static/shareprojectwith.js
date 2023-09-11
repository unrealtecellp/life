$(document).ready(function() {  
    $(".shareprojectwith").click(function() {
      let data = Object();
      let sharewithusers= [];
      let sharespeakers = [];
      let shareaction = $('#shareProjectAction').select2('data')[0].id;
      let shareuserlist = $('#shareProjectSelect').select2('data');
      let sharespeakerlist = $('#shareSpeakerSelect').select2('data');
      // console.log(shareuserlist, sharespeakerlist);
      //   var $ele = Object.values(document.getElementsByClassName('select2-selection__choice'));
      //   // var $ele = document.getElementById('shareProjectSelect')
      //   // console.log($ele);
      //   var $users = []
      //   // var $speakers = []
      // for (i = 0; i < $ele.length; i++) {
      // //   console.log($ele[i].getAttribute('title'))
      //   var userName = $ele[i].getAttribute('title')
      //     $users.push(userName)
      // }
      // // console.log(Object.assign({}, $users))
      // // console.log($users);
      // let shareuserlist = JSON.parse(localStorage.shareuserlist)
      // let sharespeakerlist = JSON.parse(localStorage.sharespeakerlist)
      // // console.log(sharespeakerlist, shareuserlist)
      // for (i=0; i<$users.length; i++) {
      //   // console.log($users[i]);
      //   d = $users[i]
      //   if (shareuserlist.includes(d)) {
      //     sharewithusers.push(d)
      //   }
      //   else if (sharespeakerlist.includes(d)) {
      //     sharespeakers.push(d)
      //   }
      // }
      for (i=0; i<shareuserlist.length; i++) {
        sharewithusers.push(shareuserlist[i].id)
      }
      for (i=0; i<sharespeakerlist.length; i++) {
        sharespeakers.push(sharespeakerlist[i].id)
      }
      // console.log(sharewithusers, sharespeakers, displayRadioValue())
      data['shareaction'] = shareaction;
      data['sharewithusers'] = sharewithusers;
      data['sharespeakers'] = sharespeakers;
      if (shareaction == 'remove') {
        data['sharemode'] = -1
      }
      else {
        data['sharemode'] = displayRadioValue();
      }
      console.log(data['sharemode']);
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