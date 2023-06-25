let sourceid = document.getElementById('sourceidsdropdown');

if (sourceid !== null){
    sourceid.onchange = function() {
        sid = sourceid.value;
        $.ajax({
          data : {
            a : sid
          },
          type : 'GET',
          url : '/changesourceid'
        }).done(function(){
            loc = window.location.href
            window.location.assign(loc)
        });
    };
}
