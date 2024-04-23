let speakerid = document.getElementById('speakeridsdropdown');



if (speakerid !== null){
    speakerid.onchange = function() {
      sid = speakerid.value;
      // sid = $('#speakeridsdropdown').val();
      // console.log('All Speaker IDS', sid)
  
        // alert(sid);
        $.ajax({
          data : {
            // a: JSON.stringify(sid)
            a : sid
          },
          type : 'GET',
          url : '/changespeakerid'
        }).done(function(){
            loc = window.location.href
            window.location.assign(loc)

        });
        
        
    };
}
