// view button on dictionary view table
$(document).ready(function() {  
    $(".lexemeview").click(function() {
      var headword = []
      var $row = $(this).closest("tr");    // Find the row
      var $text = $row.find("#lexemeId").text(); // Find the text
      headword.push($text)
      var $text = $row.find("#headword").text(); // Find the text
      headword.push($text)
      $.getJSON('/lexemeview', {
            a:String(headword)
      }, function(data) {
          $("#myViewModal").modal();
            // console.log(data.newData)
            var senseCount = 0;
            var variantCount = 0;
            var allomorphCount = 0;
            var glossLang;
            var count = '';
            var i = 1;

            // var newData = JSON.parse(localStorage.getItem("newData"));
            // var lexeme = JSON.parse(localStorage.getItem("lexeme"));
            // var filen = JSON.parse(localStorage.getItem("filen"));
            // console.log(newData, lexeme, filen)
            // localStorage.clear();

            if(data.newData != null) {
              viewFunction(data.newData, data.result1, data.result2)
            }
            // for (let [key, value] of Object.entries(data.result1)){
            //   // console.log(key, value);
            //   if (key === 'filesname'){
            //     $("<br>");
            //   }
            //   else {
            //   $("<p>"+key+" : "+value+"</p>").attr({"id":key}).appendTo( "#view" );
            //   }
            // }
            // let i = 0;
            // for (let d in data.result2){
            //   // console.log(data.result2[i].split('.').pop());
            //   if (data.result2[i].split('.').pop() === 'png') {
            //   $("<img />").attr({"src":data.result2[i], width:"320", height:"240", class:"img-thumbnail"}).appendTo( "#view" );
            //   }
            //   else if (data.result2[i].split('.').pop() === 'wav'){
            //     $(' <div><audio controls><source src="'+data.result2[i]+'" type="audio/wav"></audio></div>').appendTo( "#view" );
            //   }
            //   else if (data.result2[i].split('.').pop() === 'mp4'){
            //     $('<video width="320" height="240" controls><source src="'+data.result2[i]+'" type="video/mp4"></video>').appendTo( "#view" );
            //   }
            //   i++;
            // };
            // nextBtn = '<button type="button" class="btn btn-default btn-lg previous" onclick="myFunction()">'+
            //           '<span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span>'+
            //           '</button>';
            // nextBtn += '<button type="button" class="btn btn-default btn-lg pull-right next">'+
            //           '<span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span>'+
            //           '</button>';
            // nextBtn += '<button type="button" class="btn btn-dark btn-lg" onclick="myFunction()">&#10095;</button>'
            // $('#view').append(nextBtn);
    });
      return false; 
    });
    // $("#myViewModal").click(function() {
    //   location.reload(true);
    // });
    $(document).on("hidden.bs.modal", "#myViewModal", function () {
      // $(this).find("#view").html(""); // Just clear the contents.
      $(this).find("#lexemeviewprojectname").html("");
      $(this).find(".lexemeviewprojectname").html("");
      $(this).find(".lexemeviewlexemeform").html("");
      $(this).find(".lexemeviewenternewlexeme1").html("");
      $(this).find(".lexemeviewsense").html("");
      $(this).find(".lexemeviewvariant").html("");
      $(this).find(".lexemeviewallomorph").html("");
      $(this).find(".lexemeviewenternewlexeme2").html("");
      $(this).find(".lexemeviewcustomfields").html("");
      // $(this).find(".modal-body").remove(); // Remove from DOM.
    });

  });

function viewFunction(newData, lexeme, filen) {
  // console.log(newData, lexeme, filen)
    
    var inpt = '';
    inpt += 'Project Name : '+newData["projectname"];
    $('#lexemeviewprojectname').prepend(inpt);
    inpt = ''
    inpt += '<input type="hidden" class="form-control" placeholder="Project Name : '+newData["projectname"]+
          '" name="projectname" value="'+newData["projectname"]+'" readonly></br>';
    $('.lexemeviewprojectname').prepend(inpt);
    // console.log(inpt)
    inpt = '';	 
    for (let [key, value] of Object.entries(newData)){
      // console.log(key, value)
      if (key === 'Lexeme Form Script') {
      var lexemeScript = newData[key];
          inpt += '<fieldset class="form-group border">'+
                  '<legend class="col-form-label">Lexeme Form'+
                  '<button class="btn btn-default pull-right" type="button" data-toggle="collapse"'+
                  'data-target=".script" aria-expanded="false" aria-controls="lexemeform">'+
                  '<span class="glyphicon glyphicon-chevron-down lf" aria-hidden="true"></span>'+
                  '</button></legend>';
          // lexemeScript[0] is Head Word       
          inpt += '<div class="collapse script"><div class="form-group">'+
                  '<label for="'+ lexemeScript[0] +'">'+ lexemeScript[0] +' (Head Word)</label>'+
                  '<input type="text" class="form-control" id="'+ lexemeScript[0] +'"'+ 
          'placeholder="'+ lexemeScript[0] +'" name="Lexeme Form Script '+ lexemeScript[0] +'" '+
          'value="'+ lexeme[key][0][lexemeScript[0]] +'">'+
                  '</div></div>';
          for (var i = 1; i < lexemeScript.length; i++) {
            inpt += '<div class="collapse script"><div class="form-group">'+
                  '<label for="'+ lexemeScript[i] +'">'+ lexemeScript[i] +'</label>'+
                  '<input type="text" class="form-control" id="'+ lexemeScript[i] +'"'+ 
          'placeholder="'+ lexemeScript[i] +'" name="Lexeme Form Script '+ lexemeScript[i] +'" '+
          'value="'+ lexeme[key][i][lexemeScript[i]] +'">'+
                  '</div></div>';
          }      
      inpt += '</fieldset>';
      // console.log(inpt)
          $('.lexemeviewlexemeform').append(inpt);
          inpt = '';
      }
      else if (key === 'Gloss Language') {
        glossLang = newData[key];
      //   console.log(glossLang);
      //   if (senseCount === 0) {
      // senseCount += 1;
      for (let [skey, svalue] of Object.entries(lexeme['Sense'])) {
        // console.log(skey, svalue);
        senseCount = skey.match(/[0-9]/);
        // console.log(senseCount);
          inpt += '<fieldset class="form-group border">'+
                  '<legend class="col-form-label">'+skey+
                  '<button class="btn btn-default pull-right" type="button" data-toggle="collapse"'+
                  'data-target=".sense' +senseCount[0]+'" aria-expanded="false" aria-controls="sense' +senseCount[0]+'" '+
                  'onclick="collapseSense('+senseCount[0]+')">'+
                  '<span class="glyphicon glyphicon-chevron-down s'+senseCount[0]+'" aria-hidden="true"></span>'+
                  '</button></legend>';
  
          for (var i = 0; i < svalue.length; i++) {
        // console.log(Object.entries(svalue[i]));
        senseData = Object.entries(svalue[i]);
        // console.log(senseData[0][0], senseData[0][1]);
        if (senseData[0][0] == 'Semantic Domain'
          || senseData[0][0] === 'Lexical Relation' 
          || senseData[0][0] === 'Grammatical Category'
        ) {
          inpt += '<div class="col-md-4 collapse sense'+senseCount+'"><div class="form-group">'+
                      '<label for="'+ senseData[0][0] +'">'+ senseData[0][0] +'</label>'+
            '<select class="'+ senseData[0][0] +'" name="'+senseData[0][0]+ ' Sense '+ senseCount+'" multiple="multiple" style="width: 100%">'
          if (senseData[0][0] !== 'Grammatical Category') {	
            for (j = 0; j < senseData[0][1].length; j++) {
              inpt += '<option value="'+senseData[0][1][j]+'" selected>'+senseData[0][1][j]+'</option>'
            }	
          }
          else {
            inpt += '<option value="'+senseData[0][1]+'" selected>'+senseData[0][1]+'</option>'
          }
                  inpt += '</select></div></div>';
        }
        // for (var i = 0; i < svalue.length; i++) {
        else if (senseData[0][0].includes('Gloss')
            || senseData[0][0].includes('Definition')
            ) {
            inpt += '<div class="col-md-6 collapse sense' + senseCount[0] +'"><div class="form-group">'+
                '<label for="'+ senseData[0][0] +'">'+ senseData[0][0] +'</label>'+
                '<input type="text" class="form-control" id="'+ senseData[0][0] +'"'+ 
                'name="'+ senseData[0][0] + ' Sense '+ senseCount[0]+'"'+
                'value="'+senseData[0][1]+'">'+
                '</div></div>';
        
        }
        else {
          inpt += '<div class="col-md-4 collapse sense' + senseCount[0] +'"><div class="form-group">'+
            '<label for="'+ senseData[0][0] +'">'+ senseData[0][0] +'</label>'+
            '<input type="text" class="form-control" id="'+ senseData[0][0] +'"'+ 
            'name="'+ senseData[0][0] + ' Sense '+ senseCount[0]+'"'+
            'value="'+senseData[0][1]+'">'+
            '</div></div>';
        }
          }
                  
          // for (var i = 0; i < Sense.length; i++) {
          //   if (Sense[i].name === 'Upload Picture') {
          //     inpt += '<div class="col-md-4 collapse sense' + senseCount +'"><div class="form-group">'+
          //           '<label for="'+ Sense[i].name +'">'+ Sense[i].name +'</label>'+
          //           '<input type="file" class="form-control" id="'+ Sense[i].name +'" name="'+ Sense[i].name + ' Sense '+ senseCount+'">'+
          //           '</div></div>';  
          //   }
          //   else if (Sense[i].name === 'Semantic Domain'|| Sense[i].name === 'Lexical Relation' || Sense[i].name === 'Grammatical Category') {
          //     inpt += '<div class="col-md-4 collapse sense' + senseCount +'"><div class="form-group">'+
          //             '<label for="'+ Sense[i].name +'">'+ Sense[i].name +'</label>'+
          //             '<select class="'+ Sense[i].name +'" name="'+ Sense[i].name + ' Sense '+ senseCount+'" multiple="multiple" style="width: 100%"></select>'+
          //             '</div></div>';
          //   }
          //   else {
          //     inpt += '<div class="col-md-4 collapse sense' + senseCount +'"><div class="form-group">'+
          //             '<label for="'+ Sense[i].name +'">'+ Sense[i].name +'</label>'+
          //             '<input type="text" class="form-control" id="'+ Sense[i].name +'" name="'+ Sense[i].name + ' Sense '+ senseCount+'">'+
          //             '</div></div>';
          //   }          
          // }         
          inpt += '</fieldset>';
          $('.lexemeviewsense').append(inpt);
      inpt = '';
      }
      count = '<input type="hidden" id="senseCount" name="senseCount" value="'+ senseCount +'">';
          $('.lexemeviewcount').append(count);
      }
      else if (key === 'Variant') {
      //   if (variantCount === 0) {
      for (let [vkey, vvalue] of Object.entries(lexeme[key])) {
        // console.log(vkey, vvalue);
        // console.log(vvalue[0]['Variant Form']);
          variantCount = vkey.match(/[0-9]/);
          inpt += '<fieldset class="form-group border">'+
                  '<legend class="col-form-label">'+
                  ' '+ vkey +'</legend>';
              
          // for (var i = 0; i < Variant.length; i++) {
          //   if (Variant[i].name === 'Variant Type') {
        inpt += '<div class="col-md-4"><div class="form-group">'+
            '<label for="Variant Form">Variant Form</label>'+
              '<input type="text" class="form-control" id="Variant Form" name="Variant Form '+vkey+'"'+
              'value="'+vvalue[0]["Variant Form"]+'">'+
                      '</div></div>';
            if (vvalue[1] !== undefined) {          
              inpt += '<div class="col-md-4"><div class="form-group">'+
                      '<label for="Variant Type">Variant Type</label>'+
            '<select class="Variant Type" name="Variant Type '+vkey+'" multiple="multiple" style="width: 100%">'+
            '<option value="'+vvalue[1]["Variant Type"]+'" selected>'+vvalue[1]["Variant Type"]+'</option></select>'+
            '</div></div>';
            }
          //   else {
              // inpt += '<div class="col-md-4"><div class="form-group">'+
        // 		'<label for="Variant Type">Variant Form</label>'+
              //       	'<input type="text" class="form-control" id="Variant Form" name="Variant form '+vkey+'">'+
              //       	'</div></div>';
          //   }         
          // }                  
          inpt += '</fieldset>';
          $('.lexemeviewvariant').append(inpt);
          inpt = '';
      }
      count = '<input type="hidden" id="variantCount" name="variantCount" value="'+ variantCount +'">';
        $('.lexemeviewcount').append(count);
      }
      else if (key === 'Allomorph') {
      //   if (allomorphCount === 0) {
      // allomorphCount += 1;
      for (let [akey, avalue] of Object.entries(lexeme[key])) {
        // console.log(akey, avalue);
        // console.log(Object.keys(avalue[0])[0])
        // console.log(avalue[0][0])
        allomorphCount = akey.match(/[0-9]/);
          inpt += '<fieldset class="form-group border">'+
                  '<legend class="col-form-label">'+
                  ' '+akey+'</legend>';
              
          for (var i = 0; i < avalue.length; i++) {
        // console.log(Object.keys(avalue[i])
            if ('Morph Type' === Object.keys(avalue[i])[0]) {
        //   console.log(i);
              inpt += '<div class="col-md-4"><div class="form-group">'+
                      '<label for="Morph Type">Morph Type</label>'+
            '<select class="Morph Type" name="Morph Type '+akey+'" multiple="multiple" style="width: 100%">'+
            '<option value="'+avalue[i]["Morph Type"]+'" selected>'+avalue[i]["Morph Type"]+'</option></select>'+
                      '</div></div>';
            }
            else {
              inpt += '<div class="col-md-4"><div class="form-group">'+
                      '<label for="'+Object.keys(avalue[i])[0]+'">'+Object.keys(avalue[i])[0]+'</label>'+
            '<input type="text" class="form-control" id="'+Object.keys(avalue[i])[0]+'"'+
            'name="'+Object.keys(avalue[i])[0]+ ' ' +akey+'" value="'+avalue[i][Object.keys(avalue[i])[0]]+'">'+
                      '</div></div>';
            }
      }
      inpt += '</fieldset>';
          $('.lexemeviewallomorph').append(inpt);
        inpt = '';                  
      }
      count = '<input type="hidden" id="allomorphCount" name="allomorphCount" value="'+ allomorphCount +'">';
          $('.lexemeviewcount').append(count);
      }
      else if (value === 'multimedia') {
        inpt += '<div class="col"><div class="form-group">'+
                  '<label for="'+key+'">'+key+'</label>'+
                  '<input type="file" class="form-control" id="'+key+'" name="'+key+'">'+
                  '</div></div>';
        if (key === 'Pronunciation' || key === 'Upload Sound File' || key === 'Upload Movie File') {               
          $('.lexemeviewenternewlexeme1').append(inpt);
          inpt = '';         
        }
        else {
          $('.lexemeviewenternewlexeme2').append(inpt);
          inpt = '';         
        }
      }            
      else if (key === 'Pronunciation'){
        inpt += '<div class="col"><div class="form-group">'+
                  '<label for="'+key+'">'+key+'</label>'+
          '<input type="text" class="form-control" id="'+key+'" name="'+key+'"'+
          'value="'+lexeme[key]+'">'+
                  '</div></div>';
          $('.enternewlexeme1').append(inpt);
          inpt = '';         
      }
      else if (
        key === 'Additional Metadata Information' 
        || key === 'Any Additional Information' 
        || key === 'Encyclopedic Information'
        || key === 'Source'
      ) {
        inpt += '<div class="col"><div class="form-group">'+
                  '<label for="'+key+'">'+key+'</label>'+
                  '<textarea class="form-control" id="'+key+'" name="'+key+'">'+lexeme[key]+'</textarea>'+
                  '</div></div>'; 
          $('.lexemeviewenternewlexeme2').append(inpt);
          inpt = '';         
      }
      else if (key === 'Custom Fields') {
        inpt += '<fieldset class="form-group border">'+
                  '<legend class="col-form-label">Custom Fields'+
                  '<button class="btn btn-default pull-right" type="button" data-toggle="collapse"'+
                  'data-target=".customfield" aria-expanded="false" aria-controls="customfields">'+
                  '<span class="glyphicon glyphicon-chevron-down cf" aria-hidden="true"></span>'+
                  '</button></legend>';
        var customFields = newData[key];
        for (var j  = 0; j < customFields.length; j++) {
          for (let [ckey, cvalue] of Object.entries(customFields[j])) {
            if (cvalue === 'multimedia') {
              inpt += '<div class="col collapse customfield"><div class="form-group">'+
            '<label for="'+ckey+'">'+ckey+'</label>'+
            '<input type="file" class="form-control" id="'+ckey+'" name="Custom Field '+ckey+'">'+
            '</div></div>';         
              }
            else if (cvalue === 'text'){
                inpt += '<div class="col collapse customfield"><div class="form-group">'+
              '<label for="'+ckey+'">'+ckey+'</label>'+
              '<input type="text" class="form-control" id="'+ckey+'" name="Custom Field '+ckey+'"'+
              'value="'+lexeme[key][j][ckey]+'">'+
              '</div></div>';
              }
              else if (cvalue === 'textarea'){
                inpt += '<div class="col collapse customfield"><div class="form-group">'+
              '<label for="'+ckey+'">'+ckey+'</label>'+
              '<textarea class="form-control" id="'+ckey+'" name="Custom Field '+ckey+'">'+lexeme[key][j][ckey]+'</textarea>'+
              '</div></div>'; 
              }
          }
        }     
        inpt += '</fieldset>';
        $('.lexemeviewcustomfields').append(inpt);
        inpt = '';  
      }
    }
  }
  
  
  
$(document).ready(function () {
  $('.Grammatical').select2({
    // tags: true,
    placeholder: 'Grammatical Category',
    data: grammaticalCategories,
    allowClear: true
  });
  $('.Semantic').select2({
    // tags: true,
    placeholder: 'Semantic Domain',
    data: semanticDomains,
    allowClear: true
  });
  $('.Lexical').select2({
    // tags: true,
    placeholder: 'Lexical Relation',
    data: lexicalRelations,
    allowClear: true
  });
  $('.Variant').select2({
    // tags: true,
    // placeholder: 'Variant Type',
    data: variantTypes,
    allowClear: true
  });
  $('.Morph').select2({
    // tags: true,
    placeholder: 'Morph Type',
    data: morphTypes,
    allowClear: true
  });
});  

$(".script").ready(function(){
  $(".script").on('shown.bs.collapse', function(){
    $(".lf").addClass('glyphicon-chevron-up').removeClass('glyphicon-chevron-down');
  });  
  $('.script').on('hidden.bs.collapse', function() {
    $(".lf").addClass('glyphicon-chevron-down').removeClass('glyphicon-chevron-up');
  });   
});

function collapseSense(eleClass) {
//   console.log(eleClass);
  $(".sense"+eleClass).ready(function(){
    $(".sense"+eleClass).on('shown.bs.collapse', function(){
      $(".s"+eleClass).addClass('glyphicon-chevron-up').removeClass('glyphicon-chevron-down');
    });  
    $(".sense"+eleClass).on('hidden.bs.collapse', function() {
      $(".s"+eleClass).addClass('glyphicon-chevron-down').removeClass('glyphicon-chevron-up');
    });   
  });
}

$(".customfield").ready(function(){
    $(".customfield").on('shown.bs.collapse', function(){
      $(".cf").addClass('glyphicon-chevron-up').removeClass('glyphicon-chevron-down');
    });  
    $(".customfield").on('hidden.bs.collapse', function() {
      $(".cf").addClass('glyphicon-chevron-down').removeClass('glyphicon-chevron-up');
    });   
  });

  // document.getElementsByClassName(".next").onclick = function() {myFunction()};

  // function myFunction() {
  //   $(".lexemeview").click(function() {
  //     var $row = $(this).closest("tr");    // Find the row
  //     var $text = $row.find("#headword").text(); // Find the text
  //     $.getJSON('/lexemeview', {
  //           a:$text
  //     }, function(data) {
  //         $("#myViewModal").modal();
  //           for (let [key, value] of Object.entries(data.result1)){
  //             // console.log(key, value);
  //             if (key === 'filesname'){
  //               $("<br>");
  //             }
  //             else {
  //             $("<p>"+key+" : "+value+"</p>").attr({"id":key}).appendTo( "#view" );
  //             }
  //           }
  //           let i = 0;
  //           for (let d in data.result2){
  //             // console.log(data.result2[i].split('.').pop());
  //             if (data.result2[i].split('.').pop() === 'png') {
  //             $("<img />").attr({"src":data.result2[i], width:"320", height:"240", class:"img-thumbnail"}).appendTo( "#view" );
  //             }
  //             else if (data.result2[i].split('.').pop() === 'wav'){
  //               $(' <div><audio controls><source src="'+data.result2[i]+'" type="audio/wav"></audio></div>').appendTo( "#view" );
  //             }
  //             else if (data.result2[i].split('.').pop() === 'mp4'){
  //               $('<video width="320" height="240" controls><source src="'+data.result2[i]+'" type="video/mp4"></video>').appendTo( "#view" );
  //             }
  //             i++;
  //           };
  //           nextBtn = '<button type="button" class="btn btn-default btn-lg previous" onclick="myFunction()">'+
  //                     '<span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span>'+
  //                     '</button>';
  //           nextBtn += '<button type="button" class="btn btn-default btn-lg pull-right next">'+
  //                     '<span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span>'+
  //                     '</button>';
  //           nextBtn += '<button type="button" class="btn btn-dark btn-lg lexemeview">&#10095;</button>'
  //           $('#view').append(nextBtn);
  //   });
  //     return false; 
  //   });
  // }



  // view button on dictionary view table
// $(document).ready(function() {  
//   $(".lexemeview").click(function() {
//     var $row = $(this).closest("tr");    // Find the row
//     var $text = $row.find("#headword").text(); // Find the text
//     $.getJSON('/lexemeview', {
//           a:$text
//     }, function(data) {
//         $("#myViewModal").modal();
//         for (let e = 0; e < data.result1.length; e++) {
//           var key = String(Object.keys(data.result1[e]));
//           var value = String(Object.values(data.result1[e]));

//           console.log(key + ":" + value);

//           if (key === 'filesname'){
//             $("<br>");
//           }
//           else {
//           $("<p>"+key+" : "+value+"</p>").attr({"id":key}).appendTo( "#view" );
//           }
//         }
//         let i = 0;
//         for (let d in data.result2){
//           // console.log(data.result2);
//           $("<img />").attr({"src":data.result2[i], width:"300", height:"300", class:"img-thumbnail"}).appendTo( "#view" );
//           i++;
//         };
//   });
//     return false; 
//   });
//   // $("#myViewModal").click(function() {
//   //   location.reload(true);
//   // });
//   $(document).on("hidden.bs.modal", "#myViewModal", function () {
//     $(this).find("#view").html(""); // Just clear the contents.
//     // $(this).find(".modal-body").remove(); // Remove from DOM.
//   });

// });