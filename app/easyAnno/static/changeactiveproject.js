let projectname = document.getElementById('a');

if (projectname !== null){
  projectname.onchange = function() {
  pname = projectname.value;
        $.ajax({
          data : {
            a : pname
          },
          type : 'GET',
          url : '/activeprojectname'
        }).done(function(){
            loc = window.location.href
            window.location.assign(loc)

        });
    };
}

function changeActiveProject(pName) {
   $.ajax({
    data : {
      a : pName
    },
    type : 'GET',
    url : '/activeprojectname'
  }).done(function(){
      loc = window.location.href
      window.location.assign(loc)
  });
}