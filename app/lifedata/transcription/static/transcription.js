// 7fcbad4950b4adad46de5a9ca28efedb3f8cfbb9

function createSelect2(eleId, optionsList, selectedOption, moreInfo={}, optionKey='') {
  let ele = '';
  for (let i=0; i<optionsList.length; i++) {
      optionValue = optionsList[i];
      option = optionsList[i];
      if (optionValue in moreInfo &&
      optionKey in moreInfo[optionValue]) {
          option = moreInfo[optionValue][optionKey]
      }
      if (optionValue === selectedOption) {
          ele += '<option value="'+optionValue+'" selected>'+option+'</option>'
      }
      else {
          ele += '<option value="'+optionValue+'">'+option+'</option>'
      }
  }
  $('#'+eleId).html(ele);
  $('#'+eleId).select2({
      // data: optionsList
      });
}

function createTextareaElement(key, elevalue, type, defaultdatavalue) {
    var qform = '';
    for (let i=0; i<elevalue.length; i++) {
      eval = key + ' ' + elevalue[i]
      var keyid = eval.replace(new RegExp(' ', 'g'), '_');
      qform += '<div class="form-group">'+
                '<label for="'+ keyid +'">'+ eval +'</label><br>'+
                '<textarea id="'+ keyid +'" name="'+ eval +'" rows="4" cols="50">'+
                '</textarea>'+
                '</div>';
    }

    return qform;
}

function createTranscriptionForm(key, elevalue, eletype, defaultdatavalue) {
    let transcriptionForm = '';
    transcriptionForm += createTextareaElement(key, elevalue, eletype, defaultdatavalue)

    return transcriptionForm
}

function createTranslationForm() {
    let translationForm = '';
    translationForm += createTextareaElement(key, elevalue, eletype, defaultdatavalue)

    return translationForm
}

function createInterlinearglossForm() {
    let interlinearglossForm = '';

    return interlinearglossForm
}

function createTagsetsForm() {
    let tagsetsForm = '';

    return tagsetsForm
}

function uploadTranscriptionPromptFile(btn) {
  // console.log(btn, btn.id);
  promptFileUploadBtnId = btn.id
  promptFileId = promptFileUploadBtnId.replace(new RegExp('ques|submit', 'g'), '');
  // console.log(promptFileId);
  const file = document.getElementById(promptFileId).files[0];
  var formData = new FormData();
  formData.append(promptFileId, file);
  // console.log(formData);
  $.ajax({
    url: '/lifedata/transcription/transcriptionpromptfile',
    type: 'POST',
    data: formData,
    contentType: false,
    cache: false,
    processData: false,
    success: function(data) {
        // console.log('Success!');
        window.location.reload();
    },
  });
  return false;
}

function saveTranscriptionPromptText(btn) {
  // console.log(btn, btn.id);
  promptTextSaveBtnId = btn.id
  promptTextId = promptTextSaveBtnId.replace(new RegExp('ques|submit', 'g'), '');
  // console.log(promptTextId);
  const data = document.getElementById(promptTextId).value;
  var formData = new FormData();
  formData.append(promptTextId, data);
  // console.log(formData);
  $.ajax({
    url: '/lifedata/transcription/transcriptionprompttext',
    type: 'POST',
    data: formData,
    contentType: false,
    cache: false,
    processData: false,
    success: function(data) {
        // console.log('Success!');
        window.location.reload();
    },
  });
  return false;
}

function collapseTranscriptionPrompt() {
  // console.log("collapseTranscriptionPrompt");
  $(".prompt").ready(function(){
    // console.log("collapseTranscriptionPrompt");
      $(".prompt").on('shown.bs.collapse', function(){
        // console.log("collapseTranscriptionPrompt");
        $(".promp").addClass('glyphicon-chevron-up').removeClass('glyphicon-chevron-down');
      });  
      $('.prompt').on('hidden.bs.collapse', function() {
        // console.log("collapseTranscriptionPrompt");
        $(".promp").addClass('glyphicon-chevron-down').removeClass('glyphicon-chevron-up');
      });   
  });
}

function showTranslationSubtitle() {
  // console.log('translationtab');
  let firstTranscriptionFieldValue = document.getElementsByClassName('transcription-box')[0].value;
  let translationsubtitle = document.getElementById('translationsubtitle');
  // console.log(firstTranscriptionFieldValue, translationsubtitle);
  if (translationsubtitle) {
    if (firstTranscriptionFieldValue !== '') {
      translationsubtitle.innerHTML = firstTranscriptionFieldValue;
      translationsubtitle.style.display = 'block';
    }
    else {
      translationsubtitle.style.display = 'none';
    }
  }
  // console.log(translationsubtitle.innerHTML, firstTranscriptionFieldValue);
}

function translationSubtitle() {
  document.getElementById("translationtab").onclick = function() {showTranslationSubtitle()};
}

function getActiveTag() {
  let innerHtml = document.getElementsByClassName('tab-pane');
  // console.log(innerHtml);
  for (let tabEle of Object.values(innerHtml)) {
    if (Object.values(tabEle.classList).includes('active')) {
      // console.log(tabEle.id);
      return tabEle.id;
    }
  }
}

function createNavTabs(activeprojectform, activeTag='transcription2') {
  // console.log(activeTag);
  let tabs = '';
  let tabsOptions = ['Transcription', 'Translation', 'Interlinear Gloss', 'Annotation']
  tabs += '<ul class="nav nav-tabs">';
  for (let i=0; i< tabsOptions.length; i++) {
    let tabsOption = tabsOptions[i];
    if (tabsOption in activeprojectform ||
      (tabsOption == 'Annotation' && 'Tagsets' in activeprojectform)) {
      let tabsOptionAnchor = tabsOption.toLowerCase().replace(' ', '')+'2';
      if (tabsOptionAnchor == activeTag) {
        tabs += '<li id="'+tabsOptionAnchor.replace("2", "tab")+'" role="presentation" class="active">'+
                '<a data-toggle="tab" href="#'+tabsOptionAnchor+'">'+tabsOption+'</a>'+
                '</li>';
      }
      else {
        tabs += '<li id="'+tabsOptionAnchor.replace("2", "tab")+'" role="presentation">'+
                '<a data-toggle="tab" href="#'+tabsOptionAnchor+'">'+tabsOption+'</a>'+
                '</li>';
      }
    }
  }
  tabs += '</ul>';

  $('#tabsfield2').html(tabs);
}

function createTranscriptionPrompt(audio_lang_script) {
  let activeprojectform = JSON.parse(localStorage.activeprojectform);
  let prompt = activeprojectform['prompt']
  // console.log(prompt);
  let promptInpt = '';
  promptInpt += '<fieldset class="form-group border">'+
              '<legend class="col-form-label">'+
              'Prompt'+
              '<button class="btn btn-default pull-right" type="button" data-toggle="collapse"'+
              'data-target=".prompt" aria-expanded="false" aria-controls="transcriptionpromptfield1"'+
              'onclick="collapseTranscriptionPrompt()">'+
              '<span class="glyphicon glyphicon-chevron-down promp" aria-hidden="true"></span>'+
              '</button></legend>';
  if (Object.keys(prompt).length === 0) {
    promptInpt += '<div class="form-group prompt collapse">';
    promptInpt += '<label for="prompt_text_'+audio_lang_script+'">Prompt Text</label>';
                    
    promptInpt += '<textarea class="form-control translation-box" id="prompt_text_'+audio_lang_script+'"' +
                  'placeholder="Prompt Text " name="prompt_text_'+audio_lang_script+'' +
                  'value=""></textarea>';
    promptInpt += '<input class="btn btn-primary pull-right" id="prompt_text_'+audio_lang_script+'submit"'+
                  'type="button" value="Save" onclick="saveTranscriptionPromptText(this);">';
    promptInpt += '</div>';

    promptInpt += '<br>';

    promptInpt += '<div class="form-group prompt collapse">'+
                  '<label for="prompt_image_'+audio_lang_script+'">Prompt File</label>'+
                  '<input type="file" class="form-control" id="prompt_image_'+audio_lang_script+'"'+ 
                  'name="prompt_image_'+audio_lang_script+'" accept="image/png, image/jpeg" />';
    promptInpt += '<input class="btn btn-primary pull-right" id="prompt_image_'+audio_lang_script+'submit"'+
                  'type="button" value="Upload" onclick="uploadTranscriptionPromptFile(this);">';
    promptInpt += '</div>';
    // promptInpt += '</div>';
    promptInpt += '<br>';
  }
  else {
    // console.log(prompt['content'][audio_lang_script]);
    let prompt_text_val = '';
    let filePath = ''
    try {
      let prompt_text_object = prompt['content'][audio_lang_script]['text']
      let prompt_text_boundary = Object.keys(prompt_text_object)[0]
      let lang_script_array = audio_lang_script.split('-');
      let lang_script = lang_script_array[lang_script_array.length-1]
      // console.log(lang_script);
      prompt_text_val = prompt_text_object[prompt_text_boundary]['textspan'][lang_script]
      // console.log(prompt_text_val);
    }
    catch {
      prompt_text_val = '';
    }
    promptInpt += '<div class="form-group prompt collapse">';
    promptInpt += '<label for="prompt_text_'+audio_lang_script+'">Prompt Text</label>';
                    
    promptInpt += '<textarea class="form-control translation-box" id="prompt_text_'+audio_lang_script+'"' +
                  'placeholder="Prompt Text " name="prompt_text_'+audio_lang_script+'' +
                  'value="'+prompt_text_val+'">'+prompt_text_val+'</textarea>';
    promptInpt += '<input class="btn btn-primary pull-right" id="prompt_text_'+audio_lang_script+'submit"'+
                  'type="button" value="Save" onclick="saveTranscriptionPromptText(this);">';
    promptInpt += '</div>';

    promptInpt += '<br>';
    // console.log(filePath);

    try {
      filePath = '/retrieve/'+prompt['content'][audio_lang_script]['image']['filename'];
    }
    catch {
      filePath = '';
    }
    if (filePath !== '') {
      promptInpt += '<div class="form-group prompt collapse">'+
                  '<label for="prompt_image">Prompt Image</label><br>'+
                  '<img src="'+filePath+'" alt="prompt image" width="400" height="341" />'+
                  '</div>';
    }

    promptInpt += '<div class="form-group prompt collapse">'+
                  '<label for="prompt_image_'+audio_lang_script+'">Prompt File</label>'+
                  '<input type="file" class="form-control" id="prompt_image_'+audio_lang_script+'"'+ 
                  'name="prompt_image_'+audio_lang_script+'" accept="image/png, image/jpeg" />';
    promptInpt += '<input class="btn btn-primary pull-right" id="prompt_image_'+audio_lang_script+'submit"'+
                  'type="button" value="Upload" onclick="uploadTranscriptionPromptFile(this);">';
    promptInpt += '</div>';
    // promptInpt += '</div>';
    promptInpt += '<br>';
  }
  promptInpt += '</fieldset>';
  document.getElementById("transcriptionpromptfield2").innerHTML = "";
  $('#transcriptionpromptfield2').append(promptInpt);
  promptInpt = '';
}

function createTranscriptionInterfaceForm(newData) {
    // console.log(newData);
    localStorage.setItem("activeprojectform", JSON.stringify(newData));
    localStorage.setItem("regions", JSON.stringify(newData['transcriptionRegions']));
    localStorage.setItem("transcriptionDetails", JSON.stringify([newData['transcriptionDetails']]));
    localStorage.setItem("AudioFilePath", JSON.stringify(newData['AudioFilePath']));
    let accessedOnTime = newData["accessedOnTime"];
    var activeAudioFilename = newData["AudioFilePath"].split('/')[2];
    if (activeAudioFilename === undefined) {
      activeAudioFilename = '';
    }
    var inpt = '<span>Audio Filename: </span><span id="audioFilename">'+ activeAudioFilename +'</span>';
    $(".defaultfield").append(inpt);
    lastActiveId = newData["lastActiveId"]
    inpt = '<input type="hidden" id="lastActiveId" name="lastActiveId" value="'+lastActiveId+'">';
    $('.defaultfield').append(inpt);
    inpt = '<input type="hidden" id="accessedOnTime" name="accessedOnTime" value="' + accessedOnTime + '">';
    $('.defaultfield').append(inpt);
    inpt = ''
    let transcription_form = '';
    let translation_form = '';
    let interlineargloss_form = '';
    let tagsets_form = '';
    let audio_language = newData['Audio Language'][1][0]
    let audio_script = newData['Transcription'][1][0]
    let audio_lang_script = audio_language+'-'+audio_script
    let speakerIds = newData['speakerIds'];
    let activeSpeakerId = newData['activespeakerId']
    console.log(activeSpeakerId);
    let sourceMetadata = newData['sourceMetadata']
    // let audio_lang_script = audio_language
    // console.log(audio_lang_script);
    for (let [key, value] of Object.entries(newData)) {
        // console.log(key, value);
        eletype = value[0];
        elevalue = value[1];
        if (eletype === 'text') {
            if (key === 'Audio Language') {
                inpt += '<strong>Audio Language: </strong><strong id="'+key+'">'+elevalue+'</strong>';
                    $('.lexemelang').append(inpt);
                    inpt = '';
            }
        }
        // else if (eletype === 'textarea') {
        //     if (key === 'Transcription') {
        //         transcription_form += createTranscriptionForm(key, elevalue, eletype, defaultdatavalue);
        //     }
        //     if (key === 'Translation') {
        //         translation_form += createTranslationForm();
        //     }
        // }
        // else if (eletype === 'interlineargloss') {
        //     interlineargloss_form += createInterlinearglossForm();
        // }
        // else if (eletype === 'tagsets') {
        //     tagsets_form += createTagsetsForm();
        // }
    }
    createSelect2('speakeridsdropdown', speakerIds, activeSpeakerId, sourceMetadata, 'video_title');
    if (lastActiveId != ''){
      createTranscriptionPrompt(audio_lang_script);
    }
}

//  transcription old
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

function morphemeFieldsSelect2(morphemicSplitSentence, name) {
  let jsonFileNames = {
    morphemicGloss: "select2_morphemic_gloss.json",
    morphType: "select2_morpheme_type.json",
    posCategories: "select2_pos_categories.json"
  }
  var morphemicGloss = "";
  var morphType = "";
  var posCategories = "";
  $.ajax({
    url: '/get_jsonfile_data',
    type: 'GET',
    data: {'data': JSON.stringify(jsonFileNames)},
    contentType: "application/json; charset=utf-8", 
    success: function(response){
      morphemicGloss = response.jsonData.morphemicGloss;
      morphType = response.jsonData.morphType;
      posCategories = response.jsonData.posCategories;
      // console.log(morphemicGloss);
      // console.log('.morphemicgloss'+ name +(i+1))
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
      autoSavetranscriptionSubPart();
    }
  });
}

function morphemeFields(morphemicSplitSentence, name, morphemePOS, updateInterlinearGloss, morphemeIdMap) {
  console.log(morphemicSplitSentence, name, morphemePOS, updateInterlinearGloss);
  let wordID = 0;
  var morphemeinput = '<div class="morphemefield_' + name + '">';
  morphemeinput += '<div class="row">'+
  '<div class="col-sm-3"><strong>Morphemes</strong></div>'+
  '<div class="col-sm-3"><strong>Gloss</strong></div>'+
  '<div class="col-sm-3"><strong>Morph Type</strong></div>'+
  '<div class="col-sm-3"><strong>POS</strong></div><br><br>'+
  '</div>';
  morphemeCount = morphemicSplitSentence.length;
  // for(let i = 0; i < morphemeCount; i++) {
  for (let [key, value] of Object.entries(morphemeIdMap)) {
    console.log(key, value);
    let i = key-1;
    wordID = value[0];
    console.log(wordID, wordID in updateInterlinearGloss);
    if (wordID in updateInterlinearGloss) {
      let glossValData = updateInterlinearGloss[wordID][0][morphemeIdMap[key][2]];
      console.log(glossValData);
      let morphemicgloss = '';
      let morphemiclextype = '';
      let morphemicpos1 = '';
      let morphemicpos = '';
      for (let [k, v] of Object.entries(glossValData)) {
        console.log(k, v);
        for (let [kk, vv] of Object.entries(v)) {
          console.log(kk, vv);
          if (kk === morphemicSplitSentence[i]){
            morphemicgloss = vv['lexgloss'][name];
            morphemiclextype = vv['lextype'];
            morphemicpos1 = Object.keys(updateInterlinearGloss[wordID][1])[0];
            morphemicpos = updateInterlinearGloss[wordID][1][morphemicpos1][morphemeIdMap[key][2]];
            console.log(morphemicgloss, morphemiclextype, morphemicpos);
          }
        }
      }
      // continue
      if (morphemicSplitSentence[i].includes('-')) {
        morphemeinput += '<div class="input-group">'+
                          '<input type="text" class="form-control" name="morph_morpheme_' + name + '_' +  (i+1) +'"'+
                          'placeholder="'+ morphemicSplitSentence[i] +'" value="'+morphemicSplitSentence[i]+'"'+
                          'id="morphemeField' + name + (i+1) +'" readonly  style="float:none;width: 200px;"/>'+
                          '<span class="input-group-btn" style="width:50px;"></span>';
        if (morphemicgloss === '') {
          morphemeinput += '<select class="morphemicgloss' + name + (i+1) +'" name="morph_gloss_' + name + '_' +  (i+1) +'"'+
                          ' multiple="multiple" style="width: 200px"></select>'+
                          '<span class="input-group-btn" style="width:50px;"></span>'

        }
        else {
        morphemeinput += '<select class="morphemicgloss' + name + (i+1) +'" name="morph_gloss_' + name + '_' +  (i+1) +'"'+
                          ' multiple="multiple" style="width: 200px">'+
                          '<option value="' + morphemicgloss + '" selected>' + morphemicgloss + '</option>'+
                          '</select>'+
                          '<span class="input-group-btn" style="width:50px;"></span>';
        }
        if (morphemiclextype === '') {
          morphemeinput += 
                          '<select class="lextype' + name + (i+1) +'" name="morph_lextype_' + name + '_' +  (i+1) +'"  onchange="autoSavetranscription(event,this)" style="width: 200px">'+
                          '<option value="affix" selected>affix</option></select>'+
                          '<span class="input-group-btn" style="width:50px;"></span></div><br>';

        }
        else {
          morphemeinput += '<select class="lextype' + name + (i+1) +'" name="morph_lextype_' + name + '_' +  (i+1) +'"  onchange="autoSavetranscription(event,this)" style="width: 200px">'+
                          '<option value="'+morphemiclextype+'" selected>'+morphemiclextype+'</option></select>'+
                          '<span class="input-group-btn" style="width:50px;"></span></div><br>';
        }
        
        }
        else {
        morphemeinput += '<div class="input-group">'+
                          '<input type="text" class="form-control" name="morph_morpheme_' + name + '_' +  (i+1) +'"'+
                          'placeholder="'+ morphemicSplitSentence[i] +'" value="'+ morphemicSplitSentence[i] +'"'+
                          'id="morphemeField' + name + (i+1) +'" readonly  style="float:none;width: 200px;"/>'+
                          '<span class="input-group-btn" style="width:50px;"></span>'+
                          '<input type="text" class="form-control" name="morph_gloss_' + name + '_' +  (i+1) +'" value="' + morphemicgloss + '"'+
                          ' id="morphemicgloss' + name + (i+1) +'" onkeyup="autoSavetranscription(event,this)" style="float:none;width: 200px;"/>'+
                          '<span class="input-group-btn" style="width:50px;"></span>'+
                          '<select class="lextype' + name + (i+1) +'" name="morph_lextype_' + name + '_' +  (i+1) +'"  onchange="autoSavetranscription(event,this)" style="width: 200px">'+
                          '<option value="'+morphemiclextype+'" selected>'+morphemiclextype+'</option></select>'+
                          '<span class="input-group-btn" style="width:50px;"></span>'+
                          '<select class="pos' + name + (i+1) +'" name="morph_pos_' + name + '_' +  (i+1) +'" style="width: 200px">'+
                          '<option value="'+ morphemicpos +'" selected>'+ morphemicpos +'</option>'+
                          '</select></div><br>';
    
        }
    }
    else {
      if (morphemicSplitSentence[i].includes('-')) {
        morphemeinput += '<div class="input-group">'+
                          '<input type="text" class="form-control" name="morph_morpheme_' + name + '_' +  (i+1) +'"'+
                          'placeholder="'+ morphemicSplitSentence[i] +'" value="'+morphemicSplitSentence[i]+'"'+
                          'id="morphemeField' + name + (i+1) +'" readonly  style="float:none;width: 200px;"/>'+
                          '<span class="input-group-btn" style="width:50px;"></span>'+
                          '<select class="morphemicgloss' + name + (i+1) +'" name="morph_gloss_' + name + '_' +  (i+1) +'"'+
                          ' multiple="multiple" style="width: 200px"></select>'+
                          '<span class="input-group-btn" style="width:50px;"></span>'+
                          '<select class="lextype' + name + (i+1) +'" name="morph_lextype_' + name + '_' +  (i+1) +'"  onchange="autoSavetranscription(event,this)" style="width: 200px">'+
                          '<option value="affix" selected>affix</option></select>'+
                          '<span class="input-group-btn" style="width:50px;"></span></div><br>';
        }
        else {
        morphemeinput += '<div class="input-group">'+
                          '<input type="text" class="form-control" name="morph_morpheme_' + name + '_' +  (i+1) +'"'+
                          'placeholder="'+ morphemicSplitSentence[i] +'" value="'+ morphemicSplitSentence[i] +'"'+
                          'id="morphemeField' + name + (i+1) +'" readonly  style="float:none;width: 200px;"/>'+
                          '<span class="input-group-btn" style="width:50px;"></span>'+
                          '<input type="text" class="form-control" name="morph_gloss_' + name + '_' +  (i+1) +'"'+
                          ' id="morphemicgloss' + name + (i+1) +'" onkeyup="autoSavetranscription(event,this)" style="float:none;width: 200px;"/>'+
                          '<span class="input-group-btn" style="width:50px;"></span>'+
                          '<select class="lextype' + name + (i+1) +'" name="morph_lextype_' + name + '_' +  (i+1) +'" onchange="autoSavetranscription(event,this)" style="width: 200px"></select>'+
                          '<span class="input-group-btn" style="width:50px;"></span>'+
                          '<select class="pos' + name + (i+1) +'" name="morph_pos_' + name + '_' +  (i+1) +'" onchange="autoSavetranscription(event,this)" style="width: 200px">'+
                          '<option value="'+ morphemePOS[i][1] +'" selected>'+ morphemePOS[i][1] +'</option>'+
                          '</select></div><br>';
    
        }
    }
  }
  morphemeinput += ' <input type="text" id="morphcount" name="morphcount'+ name +'" value="'+ morphemeCount +'" hidden>';
  $(".morphemefield_"+name).remove();
  $("#morphemicDetail_"+name).append(morphemeinput);
  morphemeFieldsSelect2(morphemicSplitSentence, name);
}

function getWordPos(morphemicSplitSentence, name, updateInterlinearGloss, morphemeIdMap) {
  $.getJSON('/predictPOSNaiveBayes', {

  a:String(morphemicSplitSentence)
  }, function(data) {
  morphemeFields(morphemicSplitSentence, name, data.predictedPOS, updateInterlinearGloss, morphemeIdMap);
  
  });
  return false;
}

// get the sentence enter by the user when green check button is clicked and 
// create the boxes for words and morphemes
function getSentence(value, name) {
  console.log(value, name);
  let localStorageRegions = JSON.parse(localStorage.regions);
  let sentence_morphemic_break_full_old = value;
  var morphemicSplitSentence = [];
  value = document.getElementById("Transcription_" + name).value.trim();
  // if (value === '') {
  //   value = document.getElementById("Transcription_" + name).value.trim();
  // }
  let sentence = value.trim().split(' ');
  let sentence_morphemic_break_full = document.getElementById("sentenceMorphemicBreak_" + name).value.trim(); // Find the text
  let sentence_morphemic_break = document.getElementById("sentenceMorphemicBreak_" + name).value.trim().split(' '); // Find the text

  let replaceObj = new RegExp('[#-]', 'g')
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
    // console.log(sentence_morphemic_break[i]);
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
  // console.log('morphemicSplitSentence', morphemicSplitSentence);
  console.log('sentence_morphemic_break_full', sentence_morphemic_break_full);
  
  // let activeBoundaryID = document.getElementById('activeBoundaryID').value;
  // console.log(activeBoundaryID);
  // console.log(localStorageRegions);
  // let updateInterlinearGloss = {};
  // let updateWithInterlinearGloss = {}
  // console.log(value);
  // let sentence_morphemic_break_full_old = value;
  // let glossDetails = '';
  // let posDetails = '';
  // let morphemeDetails = '';
  // for (let p=0; p<localStorageRegions.length; p++) {
  //   if (localStorageRegions[p]['boundaryID'] === activeBoundaryID) {
      // console.log(localStorageRegions[p]);
      // sentence_morphemic_break_full_old = localStorageRegions[p]['data']['sentence'][activeBoundaryID]['sentencemorphemicbreak'][name];
      // glossDetails = localStorageRegions[p]['data']['sentence'][activeBoundaryID]['gloss'][name];
      // posDetails = localStorageRegions[p]['data']['sentence'][activeBoundaryID]['pos'];
      // morphemeDetails = localStorageRegions[p]['data']['sentence'][activeBoundaryID]['morphemes'][name];
      // console.log(sentence_morphemic_break_full_old, glossDetails, posDetails, morphemeDetails);
  //     break;
  //   }
  // }
  console.log('sentence_morphemic_break_full_old', sentence_morphemic_break_full_old);
  // updateInterlinearGloss['glossDetails'] = glossDetails;
  // updateInterlinearGloss['posDetails'] = posDetails;
  // updateInterlinearGloss['morphemeDetails'] = morphemeDetails;
  // let sentence_morphemic_break_diff = patienceDiff( sentence_morphemic_break_full_old+' ', sentence_morphemic_break_full+' ', false )
  // // console.log(sentence_morphemic_break_diff);
  // let lines = sentence_morphemic_break_diff['lines'];
  // let errorFlag = 0;
  // let newWord = '';
  // let oldWord = '';
  // let wordCount = 0;
  // for (let l=0; l<lines.length; l++) {
  //   // console.log(wordId, oldWord, newWord, 'ERROR', errorFlag);
  //   let lineData = lines[l];
  //   if (lineData['aIndex'] !== -1) {
  //     oldWord += lineData['line'];
  //   }
  //   if (lineData['bIndex'] !== -1) {
  //     newWord += lineData['line'];
  //   }
  //   let wordId = 'W00'+String(wordCount+1);
  //   if (lineData['aIndex'] === -1 || lineData['bIndex'] === -1) {
  //     // console.log(l, errorFlag);
  //     errorFlag = 1;
  //     // console.log(l, errorFlag);
  //   }
  //   if (lineData['line'] == ' ' && errorFlag === 1) {
  //     // console.log(wordId, oldWord, newWord, 'ERROR', errorFlag);
  //   }
  //   if (lineData['line'] === ' ') {
  //     updateInterlinearGloss[wordId] = [oldWord, newWord, errorFlag]
  //     updateWithInterlinearGloss[wordId] = [
  //       updateInterlinearGloss['glossDetails'][wordId],
  //       updateInterlinearGloss['posDetails'][wordId],
  //       updateInterlinearGloss['morphemeDetails'][wordId]
  //   ]
  //     errorFlag = 0;
  //     oldWord = '';
  //     newWord = '';
  //     wordCount += 1;
  //   }
  // }
  // console.log(updateInterlinearGloss);
  // console.log(updateWithInterlinearGloss);
  let aLines = sentence_morphemic_break_full_old.trim().replace(/[#-]/g, '');
  let bLines = sentence_morphemic_break_full.trim().replace(/[#-]/g, '');
  let sentDiff = patienceDiff( aLines+' ', bLines+' ', false );
  let {updateWithInterlinearGloss, sentenceMorphemicBreakSentence} = infoForUpdateInterlinearGloss(sentDiff, name);
  console.log(updateWithInterlinearGloss, sentenceMorphemicBreakSentence);
  let morphemeIdMap = morphemeidMap(bLines.split(" "), sentence_morphemic_break_full);
  console.log(morphemeIdMap);


  document.getElementById("sentenceMorphemicBreak_"+name).readOnly = true;
  var checkBtn = '<button class="btn btn-warning" type="button" id="editSentenceField"'+
              'onclick="editMorphemicBreakSentence(\''+value+'\', \''+name+'\');">'+
              '<span class="glyphicon glyphicon-edit" aria-hidden="true"></span></button><br>';
  $("#editsentmorpbreak").html(checkBtn);
  getWordPos(morphemicSplitSentence, name, updateWithInterlinearGloss, morphemeIdMap);
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
  // console.log(JSON.parse(transcriptionRegions));
  var lastActiveId = document.getElementById("lastActiveId").value;
  transcriptionData['lastActiveId'] = lastActiveId;
  transcriptionData['transcriptionRegions'] = transcriptionRegions;
  let accessedOnTime = document.getElementById("accessedOnTime").value;
  transcriptionData['accessedOnTime'] = accessedOnTime;
  $.post( "/savetranscription", {
    a: JSON.stringify(transcriptionData )
  })
  .done(function( data ) {
    // console.log(data.savedTranscription);
    if (!data.savedTranscription) {
      alert("Unable to save the transcription as audio seem to be deleted or revoked access by one of the shared user. Showing you the next audio in the list.")
      window.location.reload();
    }
    else {
      alert("Transcription saved successfully.")
    }
    // window.location.reload();
  });
});

function myFunction(newData) {
  // console.log(newData);
  localStorage.setItem("activeprojectform", JSON.stringify(newData));
  localStorage.setItem("regions", JSON.stringify(newData['transcriptionRegions']));
  var activeAudioFilename = newData["AudioFilePath"].split('/')[2];
  if (activeAudioFilename === undefined) {
    activeAudioFilename = '';
  }
  var inpt = '<span>Audio Filename: </span><span id="audioFilename">'+ activeAudioFilename +'</span>';
  $(".defaultfield").append(inpt);
  lastActiveId = newData["lastActiveId"]
  inpt = '<input type="hidden" id="lastActiveId" name="lastActiveId" value="'+lastActiveId+'">';
  $('.defaultfield').append(inpt);
  inpt = ''
  localStorage.setItem("transcriptionDetails", JSON.stringify([newData['transcriptionDetails']]));
  localStorage.setItem("AudioFilePath", JSON.stringify(newData['AudioFilePath']));
  for (let [key, value] of Object.entries(newData)){
    if (key === 'Audio Language') {
      inpt += '<strong>Audio Language: </strong><strong id="'+key+'">'+newData[key]+'</strong>';
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
  // console.log(newAudioFilename)
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

function loadUserTranscription() {
  var username = document.getElementById('transcriptionbydropdown').value;
  var lastActiveId = document.getElementById("lastActiveId").value;
  // console.log('Load transcription', username, lastActiveId)
  // loadRandomAudio(newAudioFilename)
  $.ajax({
      url: '/loadtranscriptionbyanyuser',
      type: 'GET',
      data: {'transcriptionUser': username, 'activeId': lastActiveId},
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
  
$('#transcriptionbydropdown').select2({
  // tags: true,
  placeholder: 'Select Transcription by',
  // data: posCategories
  // allowClear: true
  });

$('#speakeriduploaddropdown').select2({
  // tags: true,
  placeholder: 'select speaker',
  // data: posCategories
  // allowClear: true
  });

$('#boundarypausedropdown').select2({
tags: true,
placeholder: 'Select preset value or enter a custom value',
// data: posCategories
// allowClear: true
});


$("#audiofile").change(function() {
    let zipFileElement = document.getElementById('audiofile');
    zipFileName = zipFileElement.files[0];
    // console.log(zipFileName);
    zipFileSize = zipFileName.size
    // console.log(typeof zipFileSize, Math.round((zipFileSize/1024)));
    if (! (zipFileSize <= 200000000)) {
      
      const size = (zipFileSize / 1000 / 1000).toFixed(2);
      // console.log(zipFileSize, size);
      alert('Please upload file upto 200 MB. This file size is: ' + size + " MB");
      window.location.reload(true);
    }
    
})

$('#uploadparameters-vadid').change(function () {
  if (this.checked) {
    $('#uploadparameters-boundarypause-divid').css("display", "block");
    $("#uploadparameters-boundarypause-divid :input").prop("disabled", false);
  }
  else {
    $('#uploadparameters-boundarypause-divid').css("display", "none");
    $("#uploadparameters-boundarypause-divid :input").prop("disabled", true);
  }
})

function replaceZoomSlider() {
  let slider = '<input id="slider" data-action="zoom" type="range" min="20" max="100" value="0" style="width: 50%">';
  $("#sliderdivid").html(slider);
}

$("#deleteaudio").click(function() {
  let deleteAudioFLAG = false;
  let lastActiveId = document.getElementById("lastActiveId").value;
  if (lastActiveId) {
    deleteAudioFLAG = confirm("Delete This Audio!!!");
  }
  if(deleteAudioFLAG) {
    // console.log(deleteAudioFLAG, lastActiveId);
    $.post( "/deleteaudio", {
      a: JSON.stringify(lastActiveId)
    })
    .done(function( data ) {
      window.location.reload();
    });
  }
});

function questionnaireDerived(allQuesIds) {
  if (allQuesIds !== '') {
    // console.log(allQuesIds);
    let quesIds = '';
    quesIds += '<h4>Prompt for Transcription:</h4>'+
                '<div class="input-group col-md-12" id="quesiddropdown-divid">'+
                '<label for="quesiddropdown">Select Question: </label>'+
                '<select class="custom-select custom-select-sm" id="quesiddropdown" name="quesId" style="width:30%" required>';
    // for (i=0; i<allQuesIds.length; i++) {
      for (let [quesId, Q_Id] of Object.entries(allQuesIds)){
      // quesIds += '<option value="'+allQuesIds[i]+'">'+allQuesIds[i]+'</option>';
      quesIds += '<option value="'+quesId+'">'+Q_Id+'</option>';
    }
    quesIds += '</select>';
    quesIds += '</div>';
    quesIds += '<hr>';
    $('#questionnairederived').append(quesIds);

    $('#quesiddropdown').select2({
      // tags: true,
      // placeholder: 'select user',
      // data: posCategories
      // allowClear: true
      });
  }
}

function runLoader() {
  console.log('123213');
  console.log(document.getElementById("loader"));
  document.getElementById("loader").style.display = "block";
}

$("#syncaudio").click(function() {
  runLoader();
  $.post( "/lifedata/transcription/syncaudio", {})
  .done(function( data ) {
    console.log(data);
    window.location.reload();
  });
});

replaceZoomSlider();
