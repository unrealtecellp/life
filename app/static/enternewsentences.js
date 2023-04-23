var activeTranslationField = '<input type="checkbox" id="activeTranslationField" name="activeTranslationField" value="false">'+
                            '<label for="activeTranslationField">&nbsp; Add Translation</label><br></br>'+
                            '<div id="translationlangs" style="display: none;"></div>';

var activeTagsField = '<input type="checkbox" id="activeTagsField" name="activeTagsField" value="false">'+
                      '<label for="activeTagsField">&nbsp; Add Tags</label><br></br>'+
                      '<div id="tags" style="display: none;">'+
                      '<div class="form-group">'+
                      '<label for="Tags">Tags</label>'+
                      '<input type="text" class="form-control" id="Tags" name="Tags">'+
                      '</div></div></div>'; 
$(".tagsfield").append(activeTagsField);

// add new custom element
var sentenceField = 1;

$("#activeSentenceMorphemicBreak").click(function() {
  activetranscriptionscript = displayRadioValue();
  activetranscriptionscriptvalue = document.getElementById(activetranscriptionscript).value;
  if (activetranscriptionscriptvalue === '') {
    document.getElementById("activeSentenceMorphemicBreak").checked=false;
    alert('No input given in the selected transcription script!');  
  }
  else {
    activeMorphSentenceField(activetranscriptionscriptvalue, activetranscriptionscript);
  }
});

function activeMorphSentenceField (value, name) {
  var drow = '<div class="container containerremovesentencefield">';
  var dItems = '<div id="morphemicDetail">'+
                '<p><strong>Give Morphemic Break</strong></p>'+
                '<p><strong>**(use "#" for word boundary(if there are affixes in the word) and "-" for morphemic break)</strong></p>'+
                '<div class="col-md-12"><div class="form-group"><div class="input-group">'+
                '<input type="text" class="form-control" name="morphsentenceMorphemicBreak' + name +'"'+
                'placeholder="e.g. I have re-#write#-en the paper#-s"'+
                'id="sentenceMorphemicBreak' + name +'" value="'+value+'">'+
                '<div class="input-group-btn">'+
                '<button class="btn btn-success" type="button" id="checkSentenceField"'+
                'onclick="getSentence(\''+value+'\', \''+name+'\');">'+
                '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'+ 
                '</button></div>'+
                '</div></div></div></div>';

  drow += dItems;
  if (document.getElementById("activeSentenceMorphemicBreak").checked) {
    document.getElementById("activeSentenceMorphemicBreak").value = true;
    $(".sentencefield").append(drow);
  }
  else {
    document.getElementById("activeSentenceMorphemicBreak").value = false;
    $(".containerremovesentencefield").remove();
  }
}

function activeTranslationLangs() {
  var x = document.getElementById("translationlangs");
  if (x.style.display === "none") {
    document.getElementById("activeTranslationField").value = true;
    x.style.display = "block";
  } else {
    document.getElementById("activeTranslationField").value = false;
    x.style.display = "none";
  }
}

function activeTags() {
    var x = document.getElementById("tags");
    if (x.style.display === "none") {
      document.getElementById("activeTagsField").value = true;
      x.style.display = "block";
    } else {
      document.getElementById("activeTagsField").value = false;
      x.style.display = "none";
    }
}

// remove a sentence element
function removeSentenceFields(rid) {
$(".containerremovesentencefield"+rid).remove();
$("#sentenceForm"+rid).remove();
document.getElementById("addSentenceField").disabled = false;

}  

function getWordPos(morphemicSplitSentence, name) {
  $.getJSON('/predictPOSNaiveBayes', {

  a:String(morphemicSplitSentence)
  }, function(data) {
  morphemeFields(morphemicSplitSentence, name, data.predictedPOS);
  
  });
  return false;
}

// get the sentence enter by the user when green check button is clicked and 
// create the boxes for words and morphemes
function getSentence(value, name) {
  var morphemicSplitSentence = [];
  if (value === '') {
    value = document.getElementById("Transcription_" + name).value.trim();
  }
  sentence = value.trim().split(' ');
  sentence_morphemic_break_full = document.getElementById("sentenceMorphemicBreak_" + name).value.trim(); // Find the text
  sentence_morphemic_break = document.getElementById("sentenceMorphemicBreak_" + name).value.trim().split(' '); // Find the text

  replaceObj = new RegExp('[#-]', 'g')
  if (value !== sentence_morphemic_break_full.replace(replaceObj, '')) {
    alert('Sentence do not match to: '+value)
    return false;
  }
  if (sentence.length === 1 && sentence[0] === "") {
  alert('No input given!');
  document.getElementById("checkSentenceField").disabled = false;
  return false;
  }
  if (sentence_morphemic_break.length === 1 && sentence_morphemic_break[0] === "") {
  alert('No input given!');
  document.getElementById("checkSentenceField").disabled = false;
  return false;
  }

  if (sentence_morphemic_break_full.includes('-')) {
    morph_len = (sentence_morphemic_break_full.match(/-/g)||[]).length;
    boundary_len = (sentence_morphemic_break_full.match(/#/g)||[]).length;
    if (boundary_len > morph_len) {
      alert("Number of # ("+boundary_len+") should be less than or equal to number of - ("+morph_len+") in the morphemic break")
      document.getElementById("checkSentenceField").disabled = false;
      return false;
    }
  }

  for (i = 0; i < sentence_morphemic_break.length; i++) {
    if (sentence_morphemic_break[i].includes('#') || sentence_morphemic_break[i].includes('-')) {
      if (sentence_morphemic_break[i].includes('#') && sentence_morphemic_break[i].includes('-')) {
        morphSplit = sentence_morphemic_break[i].split('#')

        if (morphSplit.length <= 3) {
          for (j = 0; j < morphSplit.length; j++) {
            var currentMorph = morphSplit[j]
            if (currentMorph.includes("-")) {
              var dashIndex = currentMorph.indexOf("-")
              var morphemes = currentMorph.split("-")

              for (k = 0; k < morphemes.length; k++){
                if (morphemes[k].trim() !== "") {
                  if (dashIndex == 0) {
                    morphemicSplitSentence.push("-"+morphemes[k]);
                  }
                  else{
                    morphemicSplitSentence.push(morphemes[k]+"-");
                  }
                }
              }
            }
            else if (currentMorph.trim() !== "") {
              morphemicSplitSentence.push(currentMorph);
            }
          }
        }
        else {
          alert("Number of # should be less than or equal to 2 in <<"+ sentence_morphemic_break[i] + ">>");
          document.getElementById("checkSentenceField").disabled = false;
          return false;
        } 
      }
      else {
        if (sentence_morphemic_break[i].includes('#')) {
          alert("- is missing in the morphemic break in <<"+ sentence_morphemic_break[i] + ">>");
        }
        else {
          alert("# is missing in the morphemic break in <<"+ sentence_morphemic_break[i] + ">>");
        }
        document.getElementById("checkSentenceField").disabled = false;
        return false;
      }
    }
    else {
      morphemicSplitSentence.push(sentence_morphemic_break[i]);
    }
  }
  console.log('morphemicSplitSentence', morphemicSplitSentence)

  document.getElementById("sentenceMorphemicBreak_"+name).readOnly = true;
  var checkBtn = '<button class="btn btn-warning" type="button" id="editSentenceField"'+
              'onclick="editMorphemicBreakSentence(\''+value+'\', \''+name+'\');">'+
              '<span class="glyphicon glyphicon-edit" aria-hidden="true"></span></button><br>';
  $("#editsentmorpbreak").html(checkBtn);
  getWordPos(morphemicSplitSentence, name)
}  

function morphemeFields(morphemicSplitSentence, name, morphemePOS) {
  var morphemeinput = '<div class="morphemefield_' + name + '">';
  morphemeinput += '<div class="row">'+
  '<div class="col-sm-3"><strong>Morphemes</strong></div>'+
  '<div class="col-sm-3"><strong>Gloss</strong></div>'+
  '<div class="col-sm-3"><strong>Morph Type</strong></div>'+
  '<div class="col-sm-3"><strong>POS</strong></div>'+
  '</div>';
  morphemeCount = morphemicSplitSentence.length
  for(let i = 0; i < morphemeCount; i++) {
    if (morphemicSplitSentence[i].includes('-')) {
    morphemeinput += '<div class="input-group">'+
                      '<input type="text" class="form-control" name="morph_morpheme_' + name + '_' +  (i+1) +'"'+
                      'placeholder="'+ morphemicSplitSentence[i] +'" value="'+morphemicSplitSentence[i]+'"'+
                      'id="morphemeField' + name + (i+1) +'" readonly/>'+
                      '<span class="input-group-btn" style="width:50px;"></span>'+
                      '<select class="morphemicgloss' + name + (i+1) +'" name="morph_gloss_' + name + '_' +  (i+1) +'"'+
                      ' multiple="multiple" style="width: 210px"></select>'+
                      '<span class="input-group-btn" style="width:50px;"></span>'+
                      '<select class="lextype' + name + (i+1) +'" name="morph_lextype_' + name + '_' +  (i+1) +'" style="width: 210px">'+
                      '<option value="affix" selected>affix</option></select>'+
                      '<span class="input-group-btn" style="width:50px;"></span></div><br>';
    }
    else {
    morphemeinput += '<div class="input-group">'+
                      '<input type="text" class="form-control" name="morph_morpheme_' + name + '_' +  (i+1) +'"'+
                      'placeholder="'+ morphemicSplitSentence[i] +'" value="'+ morphemicSplitSentence[i] +'"'+
                      'id="morphemeField' + name + (i+1) +'" readonly/>'+
                      '<span class="input-group-btn" style="width:50px;"></span>'+
                      '<input type="text" class="form-control" name="morph_gloss_' + name + '_' +  (i+1) +'"'+
                      ' id="morphemicgloss' + name + (i+1) +'"/>'+
                      '<span class="input-group-btn" style="width:50px;"></span>'+
                      '<select class="lextype' + name + (i+1) +'" name="morph_lextype_' + name + '_' +  (i+1) +'" style="width: 210px"></select>'+
                      '<span class="input-group-btn" style="width:50px;"></span>'+
                      '<select class="pos' + name + (i+1) +'" name="morph_pos_' + name + '_' +  (i+1) +'" style="width: 210px">'+
                      '<option value="'+ morphemePOS[i][1] +'" selected>'+ morphemePOS[i][1] +'</option>'+
                      '</select></div><br>';

    }
  }
  morphemeinput += ' <input type="text" id="morphcount" name="morphcount'+ name +'" value="'+ morphemeCount +'" hidden>';
  $(".morphemefield_"+name).remove();
  $("#morphemicDetail_"+name).append(morphemeinput);
  for(let i = 0; i < morphemicSplitSentence.length; i++) {
  $('.morphemicgloss'+ name +(i+1)).select2({
  tags: true,
  placeholder: 'Gloss',
  data: morphemicGloss,
  allowClear: true
  });

  $('.lextype'+ name +(i+1)).select2({
  tags: true,
  placeholder: 'Morph Type',
  data: morphType
  // allowClear: true
  });

  $('.pos'+ name +(i+1)).select2({
  tags: true,
  placeholder: 'POS',
  data: posCategories
  // allowClear: true
  });

  }
}


function editMorphemicBreakSentence(transcriptionvalue, transcriptionkey) {
  document.getElementById("sentenceMorphemicBreak_"+transcriptionkey).readOnly = false;
  var checkBtn = '<button class="btn btn-success" type="button" id="checkSentenceField"'+
              'onclick="getSentence(\''+transcriptionvalue+'\', \''+transcriptionkey+'\');">'+
              '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span></button>';

  $("#editsentmorpbreak").html(checkBtn);
}

$("#save").click(function() {
  var transcriptionData = Object();
  var transcriptionRegions = localStorage.regions;
  var lastActiveId = document.getElementById("lastActiveId").value;
  transcriptionData['lastActiveId'] = lastActiveId;
  transcriptionData['transcriptionRegions'] = transcriptionRegions;
  $.post( "/savetranscription", {
    a: JSON.stringify(transcriptionData )
  })
  .done(function( data ) {
    window.location.reload();
  });
});

function myFunction(newData) {
  localStorage.setItem("activeprojectform", JSON.stringify(newData));
  localStorage.setItem("regions", JSON.stringify(newData['transcriptionRegions']));
  var activeAudioFilename = newData["AudioFilePath"].split('/')[2];
  if (activeAudioFilename === undefined) {
    activeAudioFilename = '';
  }
  var inpt = '<strong>Audio Filename: </strong><strong id="audioFilename">'+ activeAudioFilename +'</strong>'
  $(".defaultfield").append(inpt);
  lastActiveId = newData["lastActiveId"]
  inpt = '<input type="hidden" id="lastActiveId" name="lastActiveId" value="'+lastActiveId+'">';
  $('.defaultfield').append(inpt);
  inpt = ''
  localStorage.setItem("transcriptionDetails", JSON.stringify([newData['transcriptionDetails']]));
  localStorage.setItem("AudioFilePath", JSON.stringify(newData['AudioFilePath']));
  for (let [key, value] of Object.entries(newData)){
    if (key === 'Sentence Language') {
      inpt += '<div class="col"><div class="form-group">'+
                  '<label for="'+key+'">'+key+'</label>'+
                  '<input type="text" class="form-control" id="'+key+'" name="'+key+'" value="'+newData[key]+'" readonly>'+
                  '</div></div>'; 
          $('.lexemelang').append(inpt);
          inpt = '';
        }
  }
}

function mapArrays(array_1, array_2) {
  if(array_1.length != array_2.length || 
    array_1.length == 0 || 
    array_2.length == 0) {
    return null;
  }
  let mappedData = new Object();
  // Using the foreach method
  array_1.forEach((k, i) => {mappedData[k] = array_2[i]})

  return mappedData;
}

function displayRadioValue() {
  var ele = document.getElementsByName('activeTranscriptionScript');
  activetranscriptionscript = ''
  for(i = 0; i < ele.length; i++) {
      if(ele[i].checked)
        activetranscriptionscript =  ele[i].value
  }
  return activetranscriptionscript
}


function previousAudio() {
  var lastActiveId = document.getElementById("lastActiveId").value;
    $.ajax({
        url: '/loadpreviousaudio',
        type: 'GET',
        data: {'data': JSON.stringify(lastActiveId)},
        contentType: "application/json; charset=utf-8", 
        success: function(response){
          window.location.reload(); 
        }
    });
    return false;
}

function nextAudio() {
  var lastActiveId = document.getElementById("lastActiveId").value;
    $.ajax({
        url: '/loadnextaudio',
        type: 'GET',
        data: {'data': JSON.stringify(lastActiveId)},
        contentType: "application/json; charset=utf-8", 
        success: function(response){
          window.location.reload();
        }
    });
    return false;
}

function unAnnotated() {
  unanno = '';
  $('#uNAnnotated').remove();
  $.ajax({
      url: '/allunannotated',
      type: 'GET',
      data: {'data': JSON.stringify(unanno)},
      contentType: "application/json; charset=utf-8", 
      success: function(response){
          allunanno = response.allunanno;
          allanno = response.allanno;
          // console.log(allanno)
          var inpt = '';
          inpt += '<select class="col-sm-3 allanno" id="allanno" onchange="loadAnnoText()" style="width: 45%">'+
                  '<option selected disabled>Completed</option>';
                  for (i=0; i<allanno.length; i++) {
                      inpt += '<option value="'+allanno[i]+'">'+allanno[i]+'</option>';
                  }
          inpt += '</select>&nbsp; ';
          inpt += '<select class="pr-4 col-sm-3" id="allunanno" onchange="loadUnAnnoText()"style="width: 45%">'+
                  '<option selected disabled>Not Completed</option>';
                  for (i=0; i<allunanno.length; i++) {
                      inpt += '<option value="'+allunanno[i]+'">'+allunanno[i]+'</option>';
                  }
          inpt += '</select>';
          $('.commentIDs').append(inpt);
          // console.log(inpt);

          $('#allanno').select2({
            // placeholder: 'select user'
            });
          $('#allunanno').select2({
            // placeholder: 'select user'
            });
      }
  });
  return false; 
}

function loadUnAnnoText() {
  newAudioFilename = document.getElementById('allunanno').value;
  $.ajax({
      url: '/loadunannotext',
      type: 'GET',
      data: {'data': JSON.stringify(newAudioFilename)},
      contentType: "application/json; charset=utf-8", 
      success: function(response){
          window.location.reload();
      }
  });
  return false;
}

function loadAnnoText() {
  newAudioFilename = document.getElementById('allanno').value;
  console.log(newAudioFilename)
  // loadRandomAudio(newAudioFilename)
  $.ajax({
      url: '/loadunannotext',
      type: 'GET',
      data: {'data': JSON.stringify(newAudioFilename)},
      contentType: "application/json; charset=utf-8", 
      success: function(response){
          window.location.reload();
      }
  });
  return false;
}

function loadRandomAudio(newAudioFilename) {
  filePath = JSON.parse(localStorage.getItem('AudioFilePath'));
  currentAudioFilename = filePath.split('/')[2];
  newfilePath = filePath.replace(currentAudioFilename, newAudioFilename)
  localStorage.setItem("AudioFilePath", JSON.stringify(newfilePath));
  window.location.reload();
}

$('#usernamesdropdown').select2({
  // tags: true,
  placeholder: 'select user',
  // data: posCategories
  // allowClear: true
  });

$('#speakeridsdropdown').select2({
  // tags: true,
  placeholder: 'select speaker',
  // data: posCategories
  // allowClear: true
  });

$('#speakeriduploaddropdown').select2({
  // tags: true,
  placeholder: 'select speaker',
  // data: posCategories
  // allowClear: true
  });

$("#audiofile").change(function() {
    let zipFileElement = document.getElementById('audiofile');
    zipFileName = zipFileElement.files[0];
    console.log(zipFileName);
    zipFileSize = zipFileName.size
    console.log(typeof zipFileSize, Math.round((zipFileSize/1024)));
    if (! (zipFileSize <= 200000000)) {
      
      const size = (zipFileSize / 1000 / 1000).toFixed(2);
      console.log(zipFileSize, size);
      alert('Please upload file upto 200 MB. This file size is: ' + size + " MB");
      window.location.reload(true);
    }
    
})

function replaceZoomSlider() {
  let slider = '<input id="slider" data-action="zoom" type="range" min="20" max="100" value="0" style="width: 50%">';
  $("#sliderdivid").html(slider);
}

replaceZoomSlider();
