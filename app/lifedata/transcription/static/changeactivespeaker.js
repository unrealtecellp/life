let speakerid = document.getElementById('speakeridsdropdown');

if (speakerid !== null){
    speakerid.onchange = function() {
      sid = speakerid.value;
        $.ajax({
          data : {
            a : sid
          },
          type : 'GET',
          url : '/changespeakerid'
        }).done(function(){
            loc = window.location.href;
            window.location.assign(loc);
        });
    };
}
