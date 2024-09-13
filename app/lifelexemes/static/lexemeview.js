// view button on dictionary view table
$(document).ready(function() {  
    $(".lexemeview").click(function() {
      // localStorage.clear();
      // location.reload(); 
      var headword = []
      var $row = $(this).closest("tr");    // Find the row
      var $text = $row.find("#lexemeId").text(); // Find the text
      headword.push($text)
      var $text = $row.find("#headword").text(); // Find the text
      headword.push($text);
      // console.log(headword);
      $.getJSON('/lifelexemes/lexemeview', {
            a:String(headword)
      }, function(data) {
          $("#myViewModal").modal();

            if(data.newData != null) {
              viewFunction(data.newData, data.result1, data.result2)
            }
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
      $(this).find(".lexemeviewlexemeId").html("");
      $(this).find(".lexemeviewlexemeform").html("");
      $(this).find(".lexemeviewenternewlexeme1").html("");
      $(this).find(".lexemeviewsense").html("");
      $(this).find(".lexemeviewvariant").html("");
      $(this).find(".lexemeviewallomorph").html("");
      $(this).find(".lexemeviewenternewlexeme2").html("");
      $(this).find(".lexemeviewcustomfields").html("");
      $(this).find(".lexemeviewcount").html("");
      // $(this).find(".modal-body").remove(); // Remove from DOM.
    });

  });

var senseCount = 0;
var variantCount = 0;
var allomorphCount = 0;
var glossLang;
var count = '';

function viewFunction(newData, lexeme, filen) {
  
  // console.log(newData);
  // console.log(newData, lexeme, filen)

  var inpt = '';
  inpt += 'Project Name : '+newData["projectname"];
//   $('h4').prepend(inpt);
    $('#lexemeviewprojectname').prepend(inpt);

  inpt = ''
  inpt += 'Lexeme ID: '+lexeme["lexemeId"];
  $('.lexemeviewlexemeId').append(inpt);

  inpt = ''
  for (let [key, value] of Object.entries(newData)){
    // console.log(key, value);
    if (key === 'Lexeme Language') {
          inpt = '';         
    }
    if (key === 'Lexeme Form Script') {
      var lexemeScript = newData[key];
      // console.log(lexemeScript);
        inpt += '<fieldset class="form-group border">'+
                '<legend class="col-form-label">Lexeme Form'+
                '<button class="btn btn-default pull-right" type="button" data-toggle="collapse"'+
                'data-target=".script" aria-expanded="false" aria-controls="lexemeform">'+
                '<span class="glyphicon glyphicon-chevron-up lf" aria-hidden="true"></span>'+
                '</button></legend>';
        // lexemeScript[0] is Head Word
        // console.log(lexemeScript[0])       
        inpt += '<div class="script collapse in"><div class="form-group">'+
                '<label for="'+ lexemeScript[0] +'">'+ lexemeScript[0] +' (Head Word)</label>'+
                '<input type="text" class="form-control" id="'+ lexemeScript[0] +'"'+ 
                'placeholder="'+ lexemeScript[0] +'" name="Lexeme Form Script '+ lexemeScript[0] +'" '+
                'value="'+ lexeme["Lexeme Form"][scriptCode[lexemeScript[0]]] +'" readonly>'+
                '</div></div>';
        for (var i = 1; i < lexemeScript.length; i++) {
          inpt += '<div class="script collapse in"><div class="form-group">'+
                '<label for="'+ lexemeScript[i] +'">'+ lexemeScript[i] +'</label>'+
                '<input type="text" class="form-control" id="'+ lexemeScript[i] +'"'+ 
                'placeholder="'+ lexemeScript[i] +'" name="Lexeme Form Script '+ lexemeScript[i] +'" '+
                'value="'+ lexeme["Lexeme Form"][scriptCode[lexemeScript[i]]] +'"  readonly>'+
                '</div></div>';
        }      
        inpt += '</fieldset>';
        $('.lexemeviewlexemeform').append(inpt);
        inpt = '';
    }
    else if (key === 'Gloss Language') {
      senseCount = 0;
      glossLang = newData[key];
      // console.log(glossLang);
      if (senseCount === 0) {
        maxSenseCount = Object.keys(lexeme['SenseNew']).length
        // console.log(maxSenseCount);
        for (let [skey, svalue] of Object.entries(lexeme['SenseNew'])) {
          senseCount += 1;
          if (senseCount <= maxSenseCount) {
            
            inpt += '<fieldset class="form-group border">'+
                '<legend class="col-form-label">'+
                ' Sense'+' '+ senseCount +
                '<button class="btn btn-default pull-right" type="button" data-toggle="collapse"'+
                'data-target=".sense' + senseCount +'" aria-expanded="false" aria-controls="sense' + senseCount +'" '+
                'onclick="collapseSense('+senseCount+')">'+
                '<span class="glyphicon glyphicon-chevron-down s'+senseCount+'" aria-hidden="true"></span>'+
                '</button></legend>';

            for (var i = 0; i < glossLang.length; i++) {
            inpt += '<div class="col-md-6 collapse sense' + senseCount +'"><div class="form-group">'+
                '<label for="Gloss '+ glossLang[i] +'">Gloss '+ glossLang[i] +'</label>'+
                '<input type="text" class="form-control" id="Gloss '+ glossLang[i] +'"'+ 
                'name="Gloss '+ glossLang[i] + ' Sense '+ senseCount+'"'+
                'value="'+ lexeme["SenseNew"]["Sense "+senseCount]["Gloss"][glossLang[i].substr(0, 3).toLowerCase()]+'" readonly>'+
                '</div></div>';
              // inpt += '<div class="col-md-6 collapse sense' + senseCount +'"><div class="form-group">'+
              //   '<label for="Definition '+ glossLang[i] +'">Definition '+ glossLang[i] +'</label>'+
              //   '<input type="text" class="form-control" id="Definition '+ glossLang[i] +'"'+ 
              //   'name="Definition '+ glossLang[i] + ' Sense '+ senseCount+'"'+
              //   'value="'+ lexeme["SenseNew"]["Sense "+senseCount]["Definition"][glossLang[i].substr(0, 3).toLowerCase()]+'" readonly>'+
              //   '</div></div>';
            }
                
            for (var i = 0; i < Sense.length; i++) {
            if (Sense[i].name === 'Upload Picture') {
              inpt += '<div class="col-md-4 collapse sense' + senseCount +'"><div class="form-group">'+
                '<label for="'+ Sense[i].name +'">'+ Sense[i].name +'</label>'+
                // '<input type="file" class="form-control" id="'+ Sense[i].name +'" name="'+ Sense[i].name + ' Sense '+ senseCount+'">'+
                '<br><img src="'+filen[Sense[i].name]+'" alt="'+Sense[i].name+'">'+
                '</div></div>';  
            }
            else if (Sense[i].name === 'Semantic Domain'
                  || Sense[i].name === 'Lexical Relation'
                  || Sense[i].name === 'Grammatical Category') {
              inpt += '<div class="col-md-4 collapse sense' + senseCount +'"><div class="form-group">'+
                  '<label for="'+ Sense[i].name +'">'+ Sense[i].name +'</label>'+
                  '<input type="text" class="form-control" id="'+ Sense[i].name +'" name="'+ Sense[i].name + ' Sense '+ senseCount+'" '+
                  'value="'+ lexeme["SenseNew"]["Sense "+senseCount][Sense[i].name]+'" readonly>'+
                  '</div></div>';
            }
            else {
              inpt += '<div class="col-md-4 collapse sense' + senseCount +'"><div class="form-group">'+
                  '<label for="'+ Sense[i].name +'">'+ Sense[i].name +'</label>'+
                  '<input type="text" class="form-control" id="'+ Sense[i].name +'" name="'+ Sense[i].name + ' Sense '+ senseCount+'" '+
                  'value="'+ lexeme["SenseNew"]["Sense "+senseCount][Sense[i].name]+'" readonly>'+
                  '</div></div>';
            }          
            }         
            inpt += '</fieldset>';
            $('.lexemeviewsense').append(inpt);
            inpt = '';
            count = '<input type="hidden" id="senseCount" name="senseCount" value="'+ senseCount +'">';
            $('.lexemeviewcount').append(count);
          }
        }
  }
    }
    else if (key === 'Variant') {
      variantCount = 0;
      if (variantCount === 0) {
      maxVariantCount = Object.keys(lexeme['Variant']).length
      for (let [skey, svalue] of Object.entries(lexeme['Variant'])) {
        variantCount += 1;
        if (variantCount <= maxVariantCount) {
          inpt += '<fieldset class="form-group border">'+
              '<legend class="col-form-label">'+
              ' '+ key + ' ' + variantCount +'</legend>';
            
          for (var i = 0; i < Variant.length; i++) {
              inpt += '<div class="col-md-4"><div class="form-group">'+
                '<label for="'+ Variant[i].name +'">'+ Variant[i].name +'</label>'+
                '<input type="text" class="form-control" id="'+ Variant[i].name +'" name="'+ Variant[i].name + ' Variant '+ variantCount+'" '+
                'value="'+ lexeme["Variant"]["Variant "+variantCount][Variant[i].name]+'" readonly>'+
                '</div></div>';     
          }                  
          inpt += '</fieldset>';
          $('.lexemeviewvariant').append(inpt);
          inpt = '';
          count = '<input type="hidden" id="variantCount" name="variantCount" value="'+ variantCount +'">';
          $('.lexemeviewcount').append(count);
        }
      }
      }
    }
    else if (key === 'Allomorph') {
      allomorphCount = 0;
      // console.log(key)
      // console.log(allomorphCount === 0);
      // console.log(allomorphCount);
      if (allomorphCount === 0) {
          maxAllomorphCount = Object.keys(lexeme['Allomorph']).length
          // console.log(maxAllomorphCount);
          for (let [skey, svalue] of Object.entries(lexeme['Allomorph'])) {
            allomorphCount += 1;
            if (allomorphCount <= maxAllomorphCount) {
              inpt += '<fieldset class="form-group border">'+
                  '<legend class="col-form-label">'+
                  ' '+ key + ' ' + allomorphCount +'</legend>';
                
              for (var i = 0; i < Allomorph.length; i++) {
                  inpt += '<div class="col-md-4"><div class="form-group">'+
                      '<label for="'+ Allomorph[i].name +'">'+ Allomorph[i].name +'</label>'+
                      '<input type="text" class="form-control" id="'+ Allomorph[i].name +'" name="'+ Allomorph[i].name + ' Allomorph ' + allomorphCount+'" '+
                      'value="'+lexeme["Allomorph"]["Allomorph "+allomorphCount][Allomorph[i].name]+'" readonly>'+
                      '</div></div>';
                }
              inpt += '</fieldset>';
              $('.lexemeviewallomorph').append(inpt);
              inpt = '';
              count = '<input type="hidden" id="allomorphCount" name="allomorphCount" value="'+ allomorphCount +'">';
              $('.lexemeviewcount').append(count);
            }
          }
      }
    }
    else if (value === 'multimedia') {
      if (key === 'Upload Sound File') {
        inpt += '<br><img src="'+filen[key]+'" alt="'+key+'">';
        $('.lexemeviewenternewlexeme1').append(inpt);
        inpt = '';         
      }
      else if (key === 'Upload Movie File') {
        inpt += '<br><img src="'+filen[key]+'" alt="'+key+'">';
        $('.lexemeviewenternewlexeme1').append(inpt);
        inpt = '';         
      }
      else if (key == 'Upload Field Notebook Scan') {
        inpt += '<br><img src="'+filen[key]+'" alt="'+key+' File">';
        $('.lexemeviewenternewlexeme2').append(inpt);
        inpt = '';         
      }
    }            
    else if (value === 'text'){
      inpt += '<div class="col"><div class="form-group">'+
                '<label for="'+key+'">'+key+'</label>'+
                '<input type="text" class="form-control" id="'+key+'" name="'+key+'" '+
                'value="'+ lexeme["Pronunciation"]+'" readonly>'+
                '</div></div>';         
      if (key === 'Pronunciation' || key === 'Upload Sound File' || key === 'Upload Movie File') {               
        $('.lexemeviewenternewlexeme1').append(inpt);
        inpt = '';         
      }
    }
    else if (value === 'textarea') {
      if (key === 'Additional Metadata Information') {
        inpt += '<div class="col"><div class="form-group">'+
              '<label for="'+key+'">'+key+'</label>'+
              '<textarea class="form-control" id="'+key+'" name="'+key+'" readonly>'+lexeme["Additional Metadata Information"]+'</textarea>'+
              '</div></div>';                
          $('.lexemeviewenternewlexeme2').append(inpt);
          inpt = '';         
      }
      else if (key === 'Any Additional Information') {
        inpt += '<div class="col"><div class="form-group">'+
              '<label for="'+key+'">'+key+'</label>'+
              '<textarea class="form-control" id="'+key+'" name="'+key+'" readonly>'+lexeme["Any Additional Information"]+'</textarea>'+
              '</div></div>';                
          $('.lexemeviewenternewlexeme2').append(inpt);
          inpt = '';         
      }
      else if (key === 'Encyclopedic Information') {
        inpt += '<div class="col"><div class="form-group">'+
              '<label for="'+key+'">'+key+'</label>'+
              '<textarea class="form-control" id="'+key+'" name="'+key+'" readonly>'+lexeme["Encyclopedic Information"]+'</textarea>'+
              '</div></div>';                
          $('.lexemeviewenternewlexeme2').append(inpt);
          inpt = '';         
      }
      else if (key === 'Source') {
        inpt += '<div class="col"><div class="form-group">'+
              '<label for="'+key+'">'+key+'</label>'+
              '<textarea class="form-control" id="'+key+'" name="'+key+'" readonly>'+lexeme["Source"]+'</textarea>'+
              '</div></div>';                
          $('.lexemeviewenternewlexeme2').append(inpt);
          inpt = '';         
      } 
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
        for (let [key, value] of Object.entries(customFields[j])) {
          // console.log(key, value);
          if (value === 'multimedia') {
            inpt += '<div class="col collapse customfield"><div class="form-group">'+
                      '<label for="'+key+'">'+key+'</label>'+
                      // '<input type="file" class="form-control" id="'+key+'" name="Custom Field '+key+'">'+
                      '<br><img src="'+filen[key]+'" alt="'+key+'"> File'+
                      '</div></div>';         
          }
          else if (value === 'text'){
            inpt += '<div class="col collapse customfield"><div class="form-group">'+
                      '<label for="'+key+'">'+key+'</label>'+
                      '<input type="text" class="form-control" id="'+key+'" name="Custom Field '+key+'" '+
                      'value="'+ lexeme["Custom Fields"][key]+'" readonly>'+
                      '</div></div>';
          }
          else if (value === 'textarea'){
            inpt += '<div class="col collapse customfield"><div class="form-group">'+
                      '<label for="'+key+'">'+key+'</label>'+
                      '<textarea class="form-control" id="'+key+'" name="Custom Field '+key+'" readonly>'+ lexeme["Custom Fields"][key]+'</textarea>'+
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

$(".script").ready(function(){
  $(".script").on('shown.bs.collapse', function(){
    $(".lf").addClass('glyphicon-chevron-up').removeClass('glyphicon-chevron-down');
  });  
  $('.script').on('hidden.bs.collapse', function() {
    $(".lf").addClass('glyphicon-chevron-down').removeClass('glyphicon-chevron-up');
  });   
});

function collapseSense(eleClass) {
  console.log(eleClass);
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
