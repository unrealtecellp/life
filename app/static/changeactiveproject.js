let projectname = document.getElementById('a');

if (projectname !== null){
  projectname.onchange = function() {
  pname = projectname.value;
  
        // alert(pname);
        $.ajax({
          data : {
            a : pname
          },
          type : 'GET',
          url : '/activeprojectname'
        }).done(function(){
            // window.location.reload();
            loc = window.location.href
            window.location.assign(loc)

        });
        
        
    };
}

function changeActiveProject(pName) {
  //  alert(pName);
   $.ajax({
    data : {
      a : pName
    },
    type : 'GET',
    url : '/activeprojectname'
  }).done(function(){
      // window.location.reload();
      loc = window.location.href
      window.location.assign(loc)

  });
}