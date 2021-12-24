// $(document).ready(function(){
//     $("#projectFormSearch").keypress(function( event ) {
//       if ( event.which == 13 ) {
//         var value = $(this).val();
//         // alert(value);
//         $.ajax({
//           data : {
//             a : value
//           },
//           type : 'GET',
//           url : '/enternewlexeme1'
//         }).done(function() {
//           console.log(value);
//       });
        
//       }  
//     });
//   });

// let projectname = document.getElementById('a');

// projectname.onchange = function() {
//   pname = projectname.value;
  
//   $.ajax({
//     url: '/activeprojectname',
//     data: pname,
//     type: 'POST',
//     success: function(response) {
//         console.log(response);
//     },
//     error: function(error) {
//         console.log(error);
//     }
// });
// }

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