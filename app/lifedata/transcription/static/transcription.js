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

function createTranscriptionForm(newData) {
    console.log(newData);
    localStorage.setItem("activeprojectform", JSON.stringify(newData));
    localStorage.setItem("regions", JSON.stringify(newData['transcriptionRegions']));
    localStorage.setItem("transcriptionDetails", JSON.stringify([newData['transcriptionDetails']]));
    localStorage.setItem("AudioFilePath", JSON.stringify(newData['AudioFilePath']));
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
    let transcription_form = '';
    let translation_form = '';
    let interlineargloss_form = '';
    let tagsets_form = '';
    for (let [key, value] of Object.entries(newData)){
        console.log(key, value);
        eletype = value[0];
        elevalue = value[1];
        if (eletype === 'text') {
            if (key === 'Audio Language') {
                inpt += '<strong>Audio Language: </strong><strong id="'+key+'">'+elevalue+'</strong>';
                    $('.lexemelang').append(inpt);
                    inpt = '';
            }
        }
        else if (eletype === 'textarea') {
            if (key === 'Transcription') {
                transcription_form += createTranscriptionForm(key, elevalue, eletype, defaultdatavalue);
            }
            if (key === 'Translation') {
                translation_form += createTranslationForm();
            }
        }
        else if (eletype === 'interlineargloss') {
            interlineargloss_form += createInterlinearglossForm();
        }
        else if (eletype === 'tagsets') {
            tagsets_form += createTagsetsForm();
        }
    }
}