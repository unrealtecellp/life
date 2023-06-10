function createSelect2(eleId, optionsList) {
    $('#'+eleId).select2({
        data: optionsList
        });
}

function createBrowseActions(projectOwner, currentUsername) {
    let ele = '';
    let browseActionOptionsList = ['Delete']
    ele += '<label for="browseactiondropdown">Action:&nbsp;</label>'+
            '<select class="custom-select custom-select-sm" id="browseactiondropdown" style="width: 50%;"></select>&nbsp;&nbsp;&nbsp;&nbsp;';
    ele += '<button type="button" class="btn btn-danger" id="multipleaudiodelete"  style="display: inline;">Delete Multiple Audio</button>';
    ele += '<button type="button" class="btn btn-success" id="multipleaudiorevoke" style="display: none;">Revoke Multiple Audio</button>';
    $('#browseaudiodropdowns').append(ele);
    if (currentUsername === projectOwner) {
        browseActionOptionsList.push('Revoke');
    }
    createSelect2('browseactiondropdown', browseActionOptionsList);
}

function createAudioBrowseTable(audioDataFields, audioData) {
    console.log(audioData);
    let count = audioData.length
    let ele = '';
    ele += '<p id="totalrecords">Total Records:&nbsp;'+count+'</p>'+
            '<table class="table table-striped " id="myTable">'+
            '<thead>'+
            '<tr>'+
            '<th><input type="checkbox" id="headcheckbox" onchange="checkAllLexeme(this)" name="chk[]" checked/>&nbsp;</th>';
    for (let i=0; i<audioDataFields.length; i++) {
        ele += '<th onclick="sortTable('+(i+1)+')">'+audioDataFields[i]+'</th>';
    }
    ele += '<th>Delete</th>'+
            '</tr>'+
            '</thead>';
    ele += '<tbody id="myTableBody">';
            // {% for data in sdata %}
    for (let i=0; i<audioData.length; i++) {
        aData = audioData[i];
        ele += '<tr>'+
                '<td><input type="checkbox" id="lexemecheckbox" onchange="checkLexeme(this)" name="name1" checked /></td>';
        for (let j=0; j<audioDataFields.length; j++) {
            let field = audioDataFields[j];
            if (field in aData) {
                ele += '<td id='+field+'>'+aData[field]+'</td>';
            }
            else {
                ele += '<td> - </td>';
            }
        }

    }
    ele += '<td><button type="button" id="deleteaudio" class="btn btn-danger">'+
            '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>'+
            ' Delete Audio'+
            '</button></td>'+
            '</tr>'+
            '</tbody>'+
            '</table>';
    $('#audiobrowsetable').append(ele);
}

function createAudioBrowse(newData) {
    console.log(newData);
    let speakerIds = newData['speakerIds'];
    let currentUsername = newData['currentUsername']
    let projectOwner = newData['projectOwner']
    let shareInfo = newData['shareInfo']
    let shareMode = shareInfo['sharemode']
    let activeSpeakerId = shareInfo['activeSpeakerId']
    let audioDataFields = newData['audioDataFields']
    let audioData = newData['audioData']
    createSelect2('speakeridsdropdown', speakerIds);
    $('#speakeridsdropdown').val(activeSpeakerId);
    createSelect2('audiofilescountdropdown', [10, 20, 50])
    if (shareMode >= 4) {
        createBrowseActions(projectOwner, currentUsername);
    }
    createAudioBrowseTable(audioDataFields, audioData)
    eventsMapping();
}

function eventsMapping() {
    // change in browse action select
    $("#browseactiondropdown").change(function() {
        let browseActionSelectedOption = document.getElementById('browseactiondropdown').value;
        // console.log(browseActionSelectedOption);
        if (browseActionSelectedOption === 'Delete') {
            document.getElementById('multipleaudiorevoke').style.display = "none";
            document.getElementById('multipleaudiodelete').style.display = "inline";
        }
        else if (browseActionSelectedOption === 'Revoke') {
            document.getElementById('multipleaudiodelete').style.display = "none";
            document.getElementById('multipleaudiorevoke').style.display = "inline";
        }
    })
}