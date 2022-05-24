// edit button on dictionary view table

// $(document).ready(function() {  
//     $(".lexemeedit").click(function() {
//       var $row = $(this).closest("tr");    // Find the row
//       var $text = $row.find("#headword").text(); // Find the text
//       $.getJSON('/lexemeedit', {
//             a:$text
//       }, function(data) {
//           $("#myEditModal").modal();

//           var inpt = '<label for="projectname">'+'Project Name'+'</label>'+ 
//                     '<input type="text" class="form-control" id="projectname" placeholder="Project Name :'+ 
//                     data.newData['projectname']+ '"name="projectname" value="'+data.newData['projectname']+'" readonly>'+
//                     '<br><label for="headword">'+'Head Word'+'</label>'+
//                     '<input type="text" class="form-control" id="headword" placeholder="Head Word" name="headword"'+ 
//                     'value="'+data.result1['headword']+'" readonly><br>';

//             for (let [key, value] of Object.entries(data.newData)){
                
//             // if (value === 'multimedia'){
//             //     inpt += '<div class="col"><div class="form-group">'+
//             //             '<label for="'+key+'">'+key+'</label>'+
//             //             '<input type="file" class="form-control" id="'+key+'" name="'+key+'"'+
//             //             'value="'+data.result1[key]+'">'+
//             //             '</div></div>';
//             // }          
//             if (value === 'text'){
//                 inpt += '<div class="col"><div class="form-group">'+
//                         '<label for="'+key+'">'+key+'</label>'+
//                         '<input type="text" class="form-control" id="'+key+'" name="'+key+'"'+
//                         'value="'+data.result1[key]+'">'+
//                         '</div></div>';         
//             }
//             else if (value === 'textarea'){
//                 inpt += '<div class="col"><div class="form-group">'+
//                         '<label for="'+key+'">'+key+'</label>'+
//                         '<textarea class="form-control" id="'+key+'" name="'+key+'">'+data.result1[key]+'</textarea>'+
//                         '</div></div>';       
//             }

//             }
//             inpt += '<input class="btn btn-primary pull-right" id="submit" type="submit" value="Update">';
//             $('#edit').append(inpt);
//       });
//       return false; 
//     });
//     $(document).on("hidden.bs.modal", "#myEditModal", function () {
//         $(this).find("#edit").html(""); // Just clear the contents.
//         // $(this).find(".modal-body").remove(); // Remove from DOM.
//       });

//   });



//   function(data) {
//     $("#myEditModal").modal();
//       for (let [key, value] of Object.entries(data.result1)){
//         console.log(key, value);
//         if (key === 'filesname'){
//           $("<br>");
//         }
//         else {
//         $("<p>"+key+" : "+value+"</p>").appendTo( "#edit" );
//         }
//       }
//       let i = 0;
//       for (let d in data.result2){
//         // console.log(data.result2);
//         $("<img />").attr({"src":data.result2[i], width:"300", height:"300", class:"img-thumbnail"}).appendTo( "#edit" );
//         i++;
//       };
// }



//   "<h3>"+Project Name+":"{{ data.newData['projectname'] }}+"</h3>"
// '<form action="{{ url_for('+dictionaryview+') }}" method="POST" enctype="multipart/form-data">'
// '<div class="form-group">'
//     '<input type="text" class="form-control" placeholder="Project Name : {{ newData['+projectname+'] }}" name="projectname" value="{{ newData['+projectname+'] }}" readonly><br>'
//     '<input type="text" class="form-control" placeholder="Head Word" name="headword">'
// '</div></form>'



// edit button on dictionary view table

// $(document).ready(function() {  
//   $(".lexemeedit").click(function() {
//     var $row = $(this).closest("tr");    // Find the row
//     var $text = $row.find("#headword").text(); // Find the text
//     $.getJSON('/lexemeedit', {
//           a:$text
//     }, function(data) {
//         $("#myEditModal").modal();

//         var inpt = '<label for="projectname">'+'Project Name'+'</label>'+ 
//                   '<input type="text" class="form-control" id="projectname" placeholder="Project Name :'+ 
//                   data.newData[1]['projectname']+ '"name="projectname" value="'+data.newData[1]['projectname']+'" readonly>'+
//                   '<br><label for="headword">'+'Head Word'+'</label>'+
//                   '<input type="text" class="form-control" id="headword" placeholder="Head Word" name="headword"'+ 
//                   'value="'+data.result1[1]['Head Word']+'" readonly><br>';

//         for (let ele = 0; ele < data.newData.length; ele++) {
//           for (let e = 0; e < data.result1.length; e++) {
//             if (Object.keys(data.newData[ele])[0] == Object.keys(data.result1[e])[0]){
//               var key = String(Object.keys(data.newData[ele]));
//               var value = String(Object.values(data.newData[ele]));

//               if (value === 'text'){
//                 console.log(data.result1[e][key]);
//                   inpt += '<div class="col"><div class="form-group">'+
//                           '<label for="'+key+'">'+key+'</label>'+
//                           '<input type="text" class="form-control" id="'+key+'" name="'+key+'"'+
//                           'value="'+data.result1[e][key]+'">'+
//                           '</div></div>';         
//               }
//               else if (value === 'textarea'){
//                   inpt += '<div class="col"><div class="form-group">'+
//                           '<label for="'+key+'">'+key+'</label>'+
//                           '<textarea class="form-control" id="'+key+'" name="'+key+'">'+data.result1[e][key]+'</textarea>'+
//                           '</div></div>';       
//               }
//             }
//           }
//         }
//         inpt += '<input class="btn btn-primary pull-right" id="submit" type="submit" value="Submit">';
//         $('#edit').append(inpt);
//       });
//     return false; 
//   });
//   $(document).on("hidden.bs.modal", "#myEditModal", function () {
//       $(this).find("#edit").html(""); // Just clear the contents.
//       // $(this).find(".modal-body").remove(); // Remove from DOM.
//     });

// });


// edit button on dictionary view table

$(document).ready(function() {  
  
  $(".lexemeedit").click(function() {
    var headword = []
    var $row = $(this).closest("tr");    // Find the row
    var $text = $row.find("#lexemeId").text(); // Find the text
    headword.push($text)
    var $text = $row.find("#headword").text(); // Find the text
    headword.push($text)
    $.getJSON('/lexemeedit', {
          a:String(headword)
    }, function(data) {
      // console.log(data.newData, data.result1, data.result2)
      // window.location.href = "http://127.0.0.1:5000/editlexeme";
      localStorage.clear();
      localStorage.setItem("newDataeditlexeme", JSON.stringify(data.newData));
      localStorage.setItem("lexemeeditlexeme", JSON.stringify(data.result1));
      localStorage.setItem("fileneditlexeme", JSON.stringify(data.result2));
      // window.open("http://127.0.0.1:5000/editlexeme", "_blank");
      // window.open("http://127.0.0.1:5000/editlexeme");
      window.location.href = window.location.href.replace("dictionaryview", "editlexeme");
      // editFunction(data.newData, data.result1, data.result2)
        
    });
    return false; 
  });
});