function renderSpeakersList(speakerIds, activeSpeakerId) {
    // console.log(speakerIds, activeSpeakerId);
    let speakersList = '';
    speakersList += '<div>'+
                    '<label for="speakeridsdropdown">Audio Files from Source: </label>'+
                    '<select class="custom-select custom-select-sm" id="speakeridsdropdown" style="width: 30%;">'+
                    '<option selected disabled>'+activeSpeakerId+'</option>';
    for (let i=0; i<speakerIds.length; i++) {
        speakersList += '<option value="'+speakerIds[i]+'">'+speakerIds[i]+'</option>';
    }
    speakersList += '</select>'+
                    '</div>';

    return speakersList
}

function applySelect2() {
    $('#speakeridsdropdown').select2({
        placeholder: 'select speaker',
    });
}

function recordingsValidation(projData) {
    console.log(projData);
    let speakerIds = [];
    let activeSpeakerId = '';
    localStorage.setItem("projData", JSON.stringify(projData));
    if ('speakerIds' in projData) {
        speakerIds = projData['speakerIds']
    }
    if ('activeSpeakerId' in projData) {
        activeSpeakerId = projData['activeSpeakerId']
    }
    let speakersList = renderSpeakersList(speakerIds, activeSpeakerId)
    let lastActiveId = projData["lastActiveId"];
    let accessedOnTime = projData["accessedOnTime"];
    let currentUser = projData['currentUser'];
    let currentUserAnnotation = projData[currentUser];
    let tagSet = projData["tagSet"];
    let defaultCategoryTags = projData["tagSetMetaData"]["defaultCategoryTags"]
    let inpt = '';
    inpt += speakersList;
    inpt += '<span class="textFormAlert"></span><div class="row">' +
            '<form name="savetextanno" id="idsavetextannoform" class="form-horizontal" action="/easyAnno/savetextAnno" method="POST"  enctype="multipart/form-data">';
    inpt += '<div class="col-sm-6"  id="left">';
    inpt += '<input type="hidden" id="accessedOnTime" name="accessedOnTime" value="' + accessedOnTime + '">' +
            '<input type="hidden" id="lastActiveId" name="lastActiveId" value="' + lastActiveId + '">';
    inpt += '<div class="form-group textcontentouter">' +
            '<label class="col" for="text">Audio File:</label><br>' +
            '</div>';
    inpt += '</div>';

    inpt += '<div class="col-sm-4" id="middle">';
    let categoryDependency = {};
    if ("categoryDependency" in projData["tagSetMetaData"]) {
        categoryDependency = projData["tagSetMetaData"]["categoryDependency"]
    }
    for (let [key, value] of Object.entries(tagSet)) {
        // console.log(key, value);
        modalKey = checkModalKey(tagSet, key, categoryDependency);
        if (modalKey) {
            continue
        }
        inpt += elementData(projData, key, value);
    }
    inpt += '</div>';

    inpt+= '<div class="col-sm-2" id="right">';
    
    inpt += 
        '<div class="col">' +
        '<div class="commentIDs">'+
        '<button type="button" id="uNAnnotated" class="btn btn-lg btn-block btn-default" onclick="unAnnotated()">All Text IDs</button>'+
        '</div>'+
        '<button type="button" id="previous" class="btn btn-info btn-lg btn-block" onclick="previousText()">Previous</button><br/>' +
        '<button type="button" id="next" class="btn btn-lg btn-info btn-block" onclick="nextText()">Next</button><br/>' +
        '</div>';
    inpt += '<br><button type="button" id="mainsave" class="btn btn-lg btn-danger btn-block"  onclick="mainSave(this)">Save</button>';
    inpt += '</div>'; //right div close
    inpt += '</form></div>';

    inpt += '<div id="idmodal"></div>';
    inpt += '<div id="idpremodal"></div>'

    $('.textdata').append(inpt);
    applySelect2();
    if (currentUserAnnotation !== undefined) {
        createHighlightSpanTextDetails(currentUserAnnotation, tagSet);
    }
    textareaScrollHeight('maintextcontent', 'maintextcontent');
    createSelect2(select2Keys, tagSet);
    createTextSpanDetails(tagSet, defaultCategoryTags)

}