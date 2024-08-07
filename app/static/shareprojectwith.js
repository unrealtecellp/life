$(document).ready(function() {  
    $(".shareprojectwith").click(function() {
      let data = Object();
      let sharewithusers= [];
      let sharespeakers = [];
      let shareaction = $('#shareProjectAction').select2('data')[0].id;
      let shareuserlist = $('#shareProjectSelect').select2('data');
      let sharespeakerlist = $('#shareSpeakerSelect').select2('data');
      for (i=0; i<shareuserlist.length; i++) {
        sharewithusers.push(shareuserlist[i].id)
      }
      for (i=0; i<sharespeakerlist.length; i++) {
        sharespeakers.push(sharespeakerlist[i].id)
      }
      if (sharespeakers.includes('*')) {
        console.log(sharewithusers, sharespeakers, displayRadioValue());
        sharespeakers = JSON.parse(localStorage.getItem('sharespeakerlist'))
        // console.log(sharewithusers, sharespeakers, displayRadioValue());
        const index = sharespeakers.indexOf('*');
        console.log(index);
        if (index > -1) { // only splice sharespeakers when item is found
          sharespeakers.splice(index, 1); // 2nd parameter means remove one item only
        }
      }
      // console.log(sharewithusers, sharespeakers, displayRadioValue());
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