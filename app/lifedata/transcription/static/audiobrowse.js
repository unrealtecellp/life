var activePageNumber = 1;
var audioIds = [];
var totalData = 0;

var audioSortingCategories = [
    { "id": "lifespeakerid", "text": "Source" },
    { "id": "sourcemetainfo", "text": "Source Meta Info" }
    // {"id": "agegroup", "text": "Age Group"},
    // {"id": "gender", "text": "Gender"},
    // {"id": "educationlevel", "text": "Education Level"},
    // {"id": "educationmediumupto12", "text": "Education Medium Upto 12"},
    // {"id": "educationmediumafter12", "text": "Education Medium After 12"},
    // {"id": "speakerspeaklanguage", "text": "Source Language"}
]

function createSelect2(eleId, optionsList, selectedOption, moreInfo = {}, optionKey = '') {
    let ele = '';
    for (let i = 0; i < optionsList.length; i++) {
        optionValue = optionsList[i];
        option = optionsList[i];
        if (optionValue in moreInfo &&
            optionKey in moreInfo[optionValue]) {
            option = moreInfo[optionValue][optionKey]
        }
        if (optionValue === selectedOption) {
            ele += '<option value="' + optionValue + '" selected>' + option + '</option>'
        }
        else {
            ele += '<option value="' + optionValue + '">' + option + '</option>'
        }
    }
    $('#' + eleId).html(ele);
    $('#' + eleId).select2({
        // data: optionsList
    });
}

function createSelect2FromObject(eleId, optionsObject, selectedOption) {
    let ele = '';
    for (let i = 0; i < optionsObject.length; i++) {
        optionValue = optionsObject[i]['id'];
        option = optionsObject[i]['text'];
        if (option === selectedOption) {
            ele += '<option value="' + optionValue + '" selected>' + option + '</option>'
        }
        else {
            ele += '<option value="' + optionValue + '">' + option + '</option>'
        }
    }
    $('#' + eleId).html(ele);
    $('#' + eleId).select2({
        // data: optionsList
    });
}

function createSelect2optgroup(eleId, optionsObject, selectedOption) {
    // console.log(eleId, optionsObject, selectedOption);
    let ele = '';
    for (let [key, value] of Object.entries(optionsObject)) {
        // console.log(value.length);
        if (!(value.length === 0)) {
            let optGroup = key;
            // let optGroupId = key.toLowerCase().replaceAll(' ', '');
            let optGroupId = key;
            ele += '<optgroup id="' + optGroupId + '" label="' + optGroup + '">';
            for (let i = 0; i < value.length; i++) {
                option = value[i];
                if (option === selectedOption) {
                    ele += '<option value="' + option + '" selected>' + option + '</option>'
                }
                else {
                    ele += '<option value="' + option + '">' + option + '</option>'
                }
            }
            ele += '</optgroup>';
        }
    }
    $('#' + eleId).html(ele);
    $('#' + eleId).select2({
        // data: value
        placeholder: 'Filter Audio On',
        allowClear: true
    });
}

function createBrowseActions(projectOwner, currentUsername, shareMode, shareChecked, downloadChecked) {
    let ele = '';
    let browseActionOptionsList = ['Delete']
    ele += '<div class="pull-right">';
    if (downloadChecked === 'true') {
        // multiple audio download
        ele += '<button type="button" class="btn btn-sm btn-success classmultipletranscriptiondownload" id="idmultipletranscriptiondownload" style="display: inline;" data-toggle="modal" data-target="#myDownloadTranscriptionModal">' +
            '<span class="glyphicon glyphicon-download-alt" aria-hidden="true"></span>' +
            ' +1</button>';
    }

    if (shareChecked === 'true') {
        // multiple audio share
        ele += '<button type="button" class="btn btn-sm btn-warning" id="multipleaudioshare" style="display: inline;" data-toggle="modal" data-target="#browseShareModal">' +
            '<span class="glyphicon glyphicon-share-alt" aria-hidden="true"></span>' +
            ' +1</button>';
    }

    if (shareMode >= 4) {

        // let tabSpace = '&nbsp;&nbsp;&nbsp;&nbsp;';
        // ele += '<label for="browseactiondropdown">Action:&nbsp;</label>'+
        ele += '<select class="custom-select custom-select-sm" id="browseactiondropdown"></select>';
        // ele += tabSpace;
        // multiple audio delete
        ele += '<button type="button" class="btn btn-sm btn-danger" id="multipleaudiodelete" style="display: inline;">' +
            '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>' +
            ' +1</button>';
        // ele += tabSpace;
        // multiple audio revove
        ele += '<button type="button" class="btn btn-sm btn-success" id="multipleaudiorevoke" style="display: none;">' +
            '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>' +
            ' +1</button>';

        // ele += tabSpace;
    }
    ele += '</div>';

    $('#browseaudiodropdowns').append(ele);
    if (shareMode >= 4) {
        if (currentUsername === projectOwner) {
            browseActionOptionsList.push('Revoke');
        }
        createSelect2('browseactiondropdown', browseActionOptionsList, 'Delete');
    }
}

function createAudioBrowseTable(
    audioDataFields,
    audioData,
    shareMode = 0,
    totalRecords = 0,
    shareChecked = "false",
    downloadChecked = "false",
    shareInfo = undefined,
) {
    // console.log(audioDataFields);
    // console.log(audioData);
    // console.log(audioData);
    // console.log(shareChecked);
    // console.log(downloadChecked);
    totalData = totalRecords;
    let count = audioData.length;
    let eleInfo = '';
    let ele = '';
    let browseActionSelectedOption = '';
    let audioIdAdded = [];
    // ele += '<p id="actualtotalrecords">Total Records:&nbsp;'+totalRecords+'</p>';
    eleInfo += '<div class="col">';
    eleInfo += '<strong><p id="totalrecords" style="display:inline">Records:&nbsp;' + count + ' of ' + totalRecords + '</p></strong>';
    eleInfo += '<div class="pull-right">';
    eleInfo += '<input class="form-control" id="myInput" type="search" placeholder="Search">';
    eleInfo += '</div>';
    eleInfo += '</div>';
    eleInfo += '<hr>';
    $('#audiobrowsetableinfo').html(eleInfo);
    ele += '<div id="myTablediv">';
    ele += '<table class="table table-striped table-hover" id="myTable">';
    ele += '<thead>';
    ele += '<tr>' +
        '<th><input type="checkbox" id="headcheckbox" onchange="checkAllAudio(this)" name="chk[]" checked/>&nbsp;</th>';
    for (let i = 0; i < audioDataFields.length; i++) {
        // console.log(audioDataFields[i]);
        if (audioDataFields[i] == "audioFilename") {
            ele += '<th onclick="sortTable(' + (i + 1) + ')" hidden>' + audioDataFields[i] + '</th>';
            continue;
        }
        if (audioDataFields[i] == "Shared With") {
            if (shareChecked === 'true'){
                ele += '<th onclick="sortTable(' + (i + 1) + ')">' + audioDataFields[i] + '</th>';
            }
            continue;
        }
        // console.log(audioDataFields[i]);
        ele += '<th onclick="sortTable(' + (i + 1) + ')">' + audioDataFields[i] + '</th>';
    }
    ele += '<th>View</th>';
    if (downloadChecked === 'true') {
        ele += '<th>Download</th>';
        // ele += '<th>Share Info</th>';
    }
    if (shareChecked === 'true') {
        ele += '<th>Share</th>';
        // ele += '<th>Share Info</th>';
    }
    if (shareMode >= 4) {
        browseActionSelectedOption = document.getElementById('browseactiondropdown').value;
        ele += '<th>' + browseActionSelectedOption + '</th>';
    }
    ele += '</tr>';
    ele += '</thead>';
    ele += '<tbody id="myTableBody">';
    // {% for data in sdata %}
    for (let i = 0; i < audioData.length; i++) {
        aData = audioData[i];
        let audioCount = i + 1;
        ele += '<tr>' +
            '<td><input type="checkbox" id="lexemecheckbox" onchange="checkAudio(this)" name="name1" checked /></td>';
        for (let j = 0; j < audioDataFields.length; j++) {
            let field = audioDataFields[j];
            if (field in aData) {
                // console.log(field);
                if (field == "audioFilename") {
                    ele += '<td id=' + field + ' hidden>' + aData[field] + '</td>';
                    continue;
                }
                else if (field == "Shared With") {
                    if (shareChecked === 'true'){
                        ele += '<td id=' + field + '>' + aData[field] + '</td>';
                    }
                    continue;
                }
                else if (field == 'Audio File') {
                    ele += '<td>' +
                        '<button type="button" id="playaudio_' + audioCount + '" class="btn btn-sm btn-primary playaudioclass">' +
                        '<span class="glyphicon glyphicon-play" aria-hidden="true"></span>' +
                        // ' Play Audio'+
                        '</button>' +
                        '</td>';
                    // ele += '<td id='+field+'>'+
                    // '<audio controls oncontextmenu="return false" controlslist="nofullscreen nodownload noremoteplayback noplaybackrate">'+
                    // '<source src="'+aData[field]+'" type="audio/wav"></audio>'+
                    // '</td>';
                }
                else if (field == "audioId") {
                    if (audioIdAdded.includes(aData[field])) {
                        continue
                    }
                    else {
                        ele += '<td id=' + field + '>' + aData[field] + '</td>';
                        audioIdAdded.push(aData[field]);
                    }
                    // console.log(audioIdAdded);
                }
                else {
                    ele += '<td id=' + field + '>' + aData[field] + '</td>';
                }

            }
            else {
                // console.log(field);
                ele += '<td> - </td>';
            }
        }
        ele += '<td><button type="button" id="viewaudio" class="btn btn-sm btn-primary viewaudioclass">' +
            '<span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span>' +
            // ' View Audio'+
            '</button></td>';
        if (downloadChecked === 'true') {
            // multiple audio download
            ele += '<td><button type="button" class="btn btn-sm btn-success classsingletranscriptiondownload" id="idsingletranscriptiondownload" data-toggle="modal" data-target="#myDownloadTranscriptionModal">' +
                '<span class="glyphicon glyphicon-download-alt" aria-hidden="true"></span>' +
                '</button></td>';
        }
        if (shareChecked === 'true') {
            ele += '<td><button type="button" id="shareaudio" class="btn btn-sm btn-warning shareaudioclass"  data-toggle="modal" data-target="#browseShareModal">' +
                '<span class="glyphicon glyphicon-share-alt" aria-hidden="true"></span>' +
                // ' Share Audio'+
                '</button></td>';
            // if (shareInfo) {
            //     ele += '<td>'+shareInfo+'</td>';
            // }
            // else {
            //     // console.log(field);
            //     ele += '<td> - </td>';
            // }
        }
        if (browseActionSelectedOption === 'Delete') {
            ele += '<td><button type="button" id="deleteaudio" class="btn btn-sm btn-danger deleteaudioclass">' +
                '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>' +
                // ' Delete Audio'+
                '</button></td>';

        }
        else if (browseActionSelectedOption === 'Revoke') {
            ele += '<td><button type="button" id="revokeaudio" class="btn btn-sm btn-success revokeaudioclass">' +
                '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>' +
                // ' Revoke Audio'+
                '</button></td>';
        }
        ele += '</tr>';
    }
    ele += '</tbody>';
    ele += '</table>';
    ele += '</div>';
    $('#audiobrowsetable').html(ele);
}

function createAudioBrowse(newData) {
    // console.log(newData);
    let speakerIds = newData['speakerIds'];
    let sourceMetadata = newData['sourceMetadata'];
    let currentUsername = newData['currentUsername'];
    let projectOwner = newData['projectOwner'];
    let projectName = newData['activeProjectName'];
    let totalRecords = newData['totalRecords'];
    totalData = totalRecords;
    let shareInfo = newData['shareInfo'];
    // console.log("Share info", shareInfo);
    let shareMode = shareInfo['sharemode'];
    let shareChecked = shareInfo['sharechecked'];
    let downloadChecked = shareInfo['downloadchecked'];
    let activeSpeakerId = shareInfo['activespeakerId'];
    // console.log(activeSpeakerId)
    let audioDataFields = newData['audioDataFields'];
    let audioData = newData['audioData'];
    let transcriptionsBy = newData['transcriptionsBy'];
    // console.log(transcriptionsBy);
    createSelect2FromObject('audiosortingcategoriesdropdown', audioSortingCategories, 'Source');
    // createSelect2('audiosortingsubcategoriesdropdown', speakerIds, activeSpeakerId);
    createSelect2('speakeridsdropdown', speakerIds, activeSpeakerId, sourceMetadata, 'video_title');
    createSelect2('audiofilescountdropdown', [10, 20, 50], 10)
    // if (shareMode >= 4) {
    createBrowseActions(projectOwner, currentUsername, shareMode, shareChecked, downloadChecked);
    // }
    createAudioBrowseTable(audioDataFields,
        audioData,
        shareMode,
        totalRecords,
        shareChecked,
        downloadChecked);

    generateDownloadForm(shareInfo,
        transcriptionsBy,
        currentUsername,
        projectName);

    // downloadModalSelect2();
    eventsMappingOnce();
    eventsMapping();
    createPagination(totalRecords);
}

function eventsMappingOnce() {
    // change audio sorting categories
    $("#audiosortingcategoriesdropdown").change(function () {
        // console.log('browseActionSelectedOption');
        activePageNumber = 1;
        updateAudioSortingSubCategoriesDropdown();
    })
    // change audio file count to show
    $("#audiofilescountdropdown").change(function () {
        // console.log(browseActionSelectedOption);
        activePageNumber = 1;
        let selectedAudioSortingCategories = document.getElementById("audiosortingcategoriesdropdown").value;
        console.log(selectedAudioSortingCategories);
        if (selectedAudioSortingCategories === 'sourcemetainfo') {
            audioFilter();
        }
        else {
            updateAudioBrowseTable();
        }
    })
    audioFilteringEvent();
    // download multiple transcriptions
    $("#idmultipletranscriptiondownload").click(function () {
        let multipleAudiosInfo = GetSelected();
        // audioIds = Object.keys(multipleAudiosInfo);
        // $('#idaudioids').val("").trigger('change');
        $('#idaudioids').empty().trigger('change');
        // for (i = 0; i < audioIds.length; i++) {
        for (var current_id in multipleAudiosInfo) {
            // current_id = audioIds[i]
            // if (!all_medium.includes(current_medium)) {
            // if (!   $('#idviewotherlangs').find("option[value='" + current_language + "']").length) {
            // $('#idviewmediumpre').val(current_medium).trigger('change');
            let new_option = new Option(multipleAudiosInfo[current_id], current_id, false, true);
            $('#idaudioids').append(new_option);
            // }            
        }
        $('#idaudioids').trigger('change');
        // console.log("Multiple audios", multipleAudiosInfo);
    });
    // share multiple audios
    $("#multipleaudioshare").click(function () {
        audios = GetSelected();
        // console.log(audios);
        // console.log(Object.keys(audios));
        audioIds = Object.keys(audios);
        // $("#browseShareSelectMode").val(null).trigger('change');
        document.getElementById("browseShareSelectMode").innerHTML = "";
        $('#browseShareSelectMode').select2({
            // placeholder: 'Share with',
            data: ["share"],
            // allowClear: true
        });
        document.getElementById("browseRemoveShareSelect").style.display = "none";
        document.getElementById("removesharedfileaccess").style.display = "none";
        // browseShareMode(["share"]);
        // audioBrowseActionShare(audios);
    });
    // change in browse action select
    $("#browseactiondropdown").change(function () {
        activePageNumber = 1;
        let browseActionSelectedOption = document.getElementById('browseactiondropdown').value;
        // console.log(browseActionSelectedOption);
        let selectedAudioSortingCategories = document.getElementById("audiosortingcategoriesdropdown").value;
        // console.log(selectedAudioSortingCategories);
        if (selectedAudioSortingCategories === 'sourcemetainfo') {
            audioFilter();
        }
        else {
            updateAudioBrowseTable();
        }
        if (browseActionSelectedOption === 'Delete') {
            document.getElementById('multipleaudiorevoke').style.display = "none";
            document.getElementById('multipleaudiodelete').style.display = "inline";
        }
        else if (browseActionSelectedOption === 'Revoke') {
            document.getElementById('multipleaudiodelete').style.display = "none";
            document.getElementById('multipleaudiorevoke').style.display = "inline";
        }
    })
    // delete multiple audios
    $("#multipleaudiodelete").click(function () {
        audios = GetSelected();
        // console.log("Multiple audios", audios);
        deleteAudioFLAG = confirm("Delete These Audios!!!");
        if (deleteAudioFLAG) {
            audioBrowseAction(audios);
        }
    });
    // revoke multiple audios
    $("#multipleaudiorevoke").click(function () {
        audios = GetSelected();
        // console.log(audios);
        revokeAudioFLAG = confirm("Revoke These Audios!!!");
        if (revokeAudioFLAG) {
            audioBrowseAction(audios);
        }
    });
}

function eventsMapping(playPauseEventActive=true) {
    searchEvent();
    if (playPauseEventActive) {
        playPauseEvent();
    }
    // download single transcription
    $(".classsingletranscriptiondownload").click(function () {
        let audioInfo = getSingleAudioBrowseAction(this);
        audioIds = Object.keys(audioInfo);
        current_id = audioIds[0];
        console.log("Single audio info", audioIds);
        // $('#idaudioids').val("").trigger('change');
        $('#idaudioids').empty().trigger('change');
        let new_option = new Option(audioInfo[current_id], current_id, false, true);
        $('#idaudioids').append(new_option);
        $('#idaudioids').trigger('change');
    });
    $(".shareaudioclass").click(function () {
        let audioInfo = getSingleAudioBrowseAction(this);
        // console.log(audioInfo);
        // console.log(Object.keys(audioInfo));
        audioIds = Object.keys(audioInfo);
        $("#browseShareSelectMode").val(null).trigger('change');
        $('#browseShareSelectMode').select2({
            // placeholder: 'Share with',
            data: browseShareSelMode,
            // allowClear: true
        });
        document.getElementById("browseRemoveShareSelect").style.display = "none";
        document.getElementById("removesharedfileaccess").style.display = "none";
    });
    // delete single audio
    $(".deleteaudioclass").click(function () {
        let audioInfo = getSingleAudioBrowseAction(this);
        // console.log("Single audio info", audioInfo);
        deleteAudioFLAG = confirm("Delete This Audio!!!");
        if (deleteAudioFLAG) {
            audioBrowseAction(audioInfo);
        }
    });
    // revoke single audio
    $(".revokeaudioclass").click(function () {
        let audioInfo = getSingleAudioBrowseAction(this);
        revokeAudioFLAG = confirm("Revoke This Audio!!!");
        if (revokeAudioFLAG) {
            audioBrowseAction(audioInfo);
        }
    });
}

function updateAudioSortingSubCategoriesDropdown() {
    let audioBrowseInfo = getAudioBrowseInfo();
    let selectedAudioSortingCategories = document.getElementById("audiosortingcategoriesdropdown").value;
    $.ajax({
        data: {
            a: JSON.stringify({
                "audioBrowseInfo": audioBrowseInfo,
                "selectedAudioSortingCategories": selectedAudioSortingCategories
            })
        },
        type: 'GET',
        url: '/lifedata/transcription/updateaudiosortingsubcategories'
    }).done(function (data) {
        // console.log(data);
        audioSortingSubCategories = data.audioSortingSubCategories;
        selectedAudioSortingSubCategories = data.selectedAudioSortingSubCategories;
        // console.log(audioSortingSubCategories, selectedAudioSortingSubCategories);
        if (selectedAudioSortingCategories === 'sourcemetainfo') {
            $('#speakeridsdropdown').select2('destroy');
            document.getElementById('speakeridsdropdown').style.display = "none";
            document.getElementById('audiosortingsubcategoriesdropdown').style.display = "block";
            document.getElementById('audiofilter').style.display = "inline";
            createSelect2optgroup('audiosortingsubcategoriesdropdown', audioSortingSubCategories, selectedAudioSortingSubCategories);
        }
        else if (selectedAudioSortingCategories === 'lifespeakerid') {
            let sourceMetadata = data.sourceMetadata;
            $('#audiosortingsubcategoriesdropdown').select2('destroy');
            document.getElementById('audiosortingsubcategoriesdropdown').style.display = "none";
            document.getElementById('audiofilter').style.display = "none";
            document.getElementById('speakeridsdropdown').style.display = "block";
            createSelect2('speakeridsdropdown', audioSortingSubCategories, selectedAudioSortingSubCategories, sourceMetadata, 'video_title');
        }
        createAudioBrowseTable(data.audioDataFields,
            data.audioData,
            data.shareMode,
            data.totalRecords,
            data.shareChecked,
            data.downloadChecked);
        eventsMapping();
        createPagination(data.totalRecords)
    });
}

function updateAudioBrowseTable() {
    let audioBrowseInfo = getAudioBrowseInfo();
    $.ajax({
        data: {
            a: JSON.stringify(audioBrowseInfo)
        },
        type: 'GET',
        url: '/lifedata/transcription/updateaudiobrowsetable'
    }).done(function (data) {
        // console.log(data.audioDataFields, data.audioData, data.shareMode);
        createAudioBrowseTable(data.audioDataFields,
            data.audioData,
            data.shareMode,
            data.totalRecords,
            data.shareChecked,
            data.downloadChecked);
        eventsMapping();
        createPagination(data.totalRecords)
    });
}

function audioBrowseAction(audioInfo) {
    let audioBrowseInfo = getAudioBrowseInfo();
    $.ajax({
        data: {
            a: JSON.stringify({
                "audioInfo": audioInfo,
                "audioBrowseInfo": audioBrowseInfo
            })
        },
        type: 'GET',
        url: '/lifedata/transcription/audiobrowseaction'
    }).done(function (data) {
        window.location.reload();
    });
}

function audioBrowseActionPlay(audioInfo, audioCountInfo) {
    // console.log(audioCountInfo);
    let selectedAudioSortingCategories = document.getElementById("audiosortingcategoriesdropdown").value;
    // console.log(selectedAudioSortingCategories);
    let selectedFilterOptions = {};
    if (selectedAudioSortingCategories === 'sourcemetainfo') {
        let filterOptions = $('#audiosortingsubcategoriesdropdown').select2('data');
        // console.log(filterOptions); 
        for (let i=0; i<filterOptions.length; i++) {
            let option = filterOptions[i].text;
            let optGroup = filterOptions[i].element.parentNode.id;
            // console.log(option, optGroup);
            if (optGroup in selectedFilterOptions) {
                selectedFilterOptions[optGroup].push(option);
            }
            else {
                selectedFilterOptions[optGroup] = [option];
            }
        }
    }
    let audioBrowseInfo = getAudioBrowseInfo();
    audioBrowseInfo['pageId'] = activePageNumber;
    let data_1 = {
        audioInfo: audioInfo,
        audioBrowseInfo: audioBrowseInfo,
        selectedAudioSortingCategories: selectedAudioSortingCategories,
        selectedFilterOptions: selectedFilterOptions,
    }
    $.post("/lifedata/transcription/audiobrowseactionplay", {
        a: JSON.stringify(data_1)
        //   }),
    })
        .done(function (data) {
            // window.location.reload();
            // console.log(data)
            // console.log(data.downloadChecked, data.shareChecked)
            createAudioBrowseTable(data.audioDataFields,
                data.audioData,
                data.shareMode,
                data.totalRecords,
                data.shareChecked,
                data.downloadChecked);
            eventsMapping(false);
            // console.log(activePageNumber);
            createPagination(data.totalRecords, activePageNumber);
            // console.log(audioCountInfo);
            audioCountInfo = document.getElementById(audioCountInfo.id);
            // console.log(audioCountInfo);
            let audioSource = data.audioSource;
            togglePlayPause(audioCountInfo, 'pauseaudioclass', 'pause', audioSource)
        });
}

function getAudioBrowseInfo() {
    let activeSpeakerId = document.getElementById('speakeridsdropdown').value;
    let audioFilesCount = Number(document.getElementById('audiofilescountdropdown').value);
    let browseActionSelectedOption = '';
    try {
        browseActionSelectedOption = document.getElementById('browseactiondropdown').value;
        if (browseActionSelectedOption === 'Delete') {
            browseActionSelectedOption = 0
        }
        else if (browseActionSelectedOption === 'Revoke') {
            browseActionSelectedOption = 1
        }
    }
    catch (err) {
        browseActionSelectedOption = 0
    }
    let audioBrowseInfo = {
        "activeSpeakerId": activeSpeakerId,
        "audioFilesCount": audioFilesCount,
        "browseActionSelectedOption": browseActionSelectedOption
    }

    return audioBrowseInfo
}

function GetSelected() {

    //Reference the Table.
    var grid = document.getElementById("myTable");

    //Reference the CheckBoxes in Table.
    var checkBoxes = grid.getElementsByTagName("INPUT");

    // var checkedaudios = [];
    var checkedaudios = {};
    //Loop through the CheckBoxes.
    for (var i = 1; i < checkBoxes.length; i++) {

        if (checkBoxes[i].type == 'checkbox' && checkBoxes[i].checked == true) {
            var row = checkBoxes[i].parentNode.parentNode;
            // checkedaudios.push(row.cells[1].innerHTML);
            key = row.cells[1].innerHTML;
            value = row.cells[2].innerHTML;
            checkedaudios[key] = value;
        }
    }
    return checkedaudios;
}

function checkAllAudio(ele) {
    // checked true or false when checkbox in table header is clicked
    var checkboxes = document.getElementsByTagName('input');
    if (ele.checked) {
        for (var i = 0; i < checkboxes.length; i++) {
            if (checkboxes[i].type == 'checkbox') {
                checkboxes[i].checked = true;
            }
        }
    } else {
        for (var i = 0; i < checkboxes.length; i++) {
            // console.log(i)
            if (checkboxes[i].type == 'checkbox') {
                checkboxes[i].checked = false;
            }
        }
    }
}

function checkAudio(ele) {
    // console.log(ele);
    // checkbox in table header true or false when any checkbox of table body is true or false
    var checkboxcount = 0;
    var headcheckbox = document.getElementById('headcheckbox');
    var checkboxes = document.getElementsByTagName('input');
    var totalrecords = document.getElementById('totalrecords').innerHTML;
    // console.log(totalrecords);
    let totalrecordscount = totalrecords.match(/\d/);
    // console.log(totalrecordscount);
    if (ele.checked == false) {
        headcheckbox.checked = false;
    }
    else {
        for (var i = 1; i < checkboxes.length; i++) {
            if (checkboxes[i].type == 'checkbox' && checkboxes[i].checked == true) {
                checkboxcount += 1
            }
        }
        if (checkboxcount == totalrecordscount) {
            headcheckbox.checked = true;
        }
    }
}

function getSingleAudioBrowseAction(element) {

    var audioInfo = {}
    var $row = $(element).closest("tr");    // Find the row
    var audioId = $row.find("#audioId").text(); // Find the text
    var audioFilename = $row.find("#audioFilename").text(); // Find the text
    audioInfo[audioId] = audioFilename
    // console.log(audioInfo);

    return audioInfo
}

function createPagination(totalRecords, active=1) {
    let defaultShowpages = 6;
    let showpages = defaultShowpages;
    let startFrom = active;
    let audioFilesCount = Number(document.getElementById('audiofilescountdropdown').value);
    let paginationEle = '';
    let totalPages = Math.ceil(totalRecords / audioFilesCount);
    // console.log(totalPages);
    showpages+= active;
    if (totalPages <= defaultShowpages) {
        showpages = totalPages;
        startFrom = 1;
    }
    else if (totalPages > defaultShowpages &&
        totalPages >= showpages-1) {
        showpages = startFrom+Math.ceil(defaultShowpages/2);
        startFrom -= Math.floor(defaultShowpages/2);
        if (active <= Math.ceil(defaultShowpages/2)) {
            startFrom = 1;
            showpages = defaultShowpages+1;
        }
    }
    else if (totalPages <= showpages) {
        showpages = totalPages;
        startFrom -= defaultShowpages - (showpages-startFrom);
    }
    // console.log(startFrom, showpages);
    paginationEle += '<div class="btn-group">';
    paginationEle += '<button type="button" class="btn btn-sm" id="pagebackward" onclick="changeAudioBrowsePage2(this.id)">'+
                        '<span class="glyphicon glyphicon-backward" aria-hidden="true"></span>'+
                        '</button>';
    paginationEle += '<button type="button" class="btn btn-sm" id="pageleft" onclick="changeAudioBrowsePage2(this.id)">'+
                        '<span class="glyphicon glyphicon-chevron-left" aria-hidden="true"></span>'+
                        '</button>';
    for (let i = startFrom; i <= showpages; i++) {
        if (i == active) {
            paginationEle += '<button type="button" class="btn btn-sm btn-primary createpagination" id="' + i + '" onclick="changeAudioBrowsePage(this.id)">' + i + '</button>';
        }
        else {
            paginationEle += '<button type="button" class="btn btn-sm createpagination" id="' + i + '" onclick="changeAudioBrowsePage(this.id)">' + i + '</button>';
        }
    }
    paginationEle += '<button type="button" class="btn btn-sm" id="pageright" onclick="changeAudioBrowsePage2(this.id)">'+
                        '<span class="glyphicon glyphicon-chevron-right" aria-hidden="true"></span>'+
                        '</button>';
    paginationEle += '<button type="button" class="btn btn-sm" id="pageforward" onclick="changeAudioBrowsePage2(this.id)">'+
                    '<span class="glyphicon glyphicon-forward" aria-hidden="true"></span>'+
                    '</button>';
    paginationEle += '</div><br><br>';
    $("#audiobrowsepagination").html(paginationEle);
    if (active === 1) {
        document.getElementById('pagebackward').disabled = true;
        document.getElementById('pageleft').disabled = true;
    }
    if (active === totalPages) {
        document.getElementById('pageright').disabled = true;
        document.getElementById('pageforward').disabled = true;
    }
}

function changeAudioBrowsePage2(movePageTo) {
    // console.log(movePageTo, activePageNumber, totalData);
    let audioFilesCount = Number(document.getElementById('audiofilescountdropdown').value);
    // console.log(audioFilesCount);
    let lastPage = Math.ceil(totalData / audioFilesCount);
    // console.log(lastPage);
    let pageId = activePageNumber;
    if (movePageTo === 'pagebackward') {
        pageId = 1;
    }
    else if (movePageTo === 'pageleft') {
        pageId -= 1;
    }
    else if (movePageTo === 'pageright') {
        pageId += 1;
    }
    else if (movePageTo === 'pageforward') {
        pageId = lastPage;
    }
    // console.log(pageId);
    if (pageId >= 1 &&
        pageId <= lastPage) {
            changeAudioBrowsePage(pageId);
        }
}

function changeAudioBrowsePage(pageId) {
    // console.log(pageId);
    // console.log(activePageNumber);
    let audioBrowseInfo = getAudioBrowseInfo();
    activePageNumber = Number(pageId);
    audioBrowseInfo['pageId'] = Number(pageId);
    let selectedAudioSortingCategories = document.getElementById("audiosortingcategoriesdropdown").value;
    // console.log(selectedAudioSortingCategories);
    if (selectedAudioSortingCategories === 'sourcemetainfo') {
        audioFilter(Number(pageId));
    }
    else {
        $.ajax({
            data: {
                a: JSON.stringify(audioBrowseInfo)
            },
            type: 'GET',
            url: '/lifedata/transcription/audiobrowsechangepage'
        }).done(function (data) {
            // console.log(data.audioDataFields, data.audioData, data.shareMode);
            // console.log(data.downloadChecked)
            createAudioBrowseTable(data.audioDataFields,
                data.audioData,
                data.shareMode,
                data.totalRecords,
                data.shareChecked,
                data.downloadChecked);
            eventsMapping();
            createPagination(data.totalRecords, data.activePage);
        });
    }
}

function playPauseEvent() {
    $(".playaudioclass").click(function () {
        let audioInfo = getSingleAudioBrowseAction(this);
        audioBrowseActionPlay(audioInfo, this);
    });
    $(".pauseaudioclass").click(function () {
        let playingAudioId = this.id;
        // console.log(playingAudioId);
        let playingAudioEleId = playingAudioId + "_audioEle";
        let playingAudioEle = document.getElementById(playingAudioEleId);
        // console.log(playingAudioEleId, playingAudioEle);
        playingAudioEle.pause();
        togglePlayPause(this, 'playaudioclass', 'play');

    });
}

function togglePlayPause(ele, state, icon, audioSource=undefined) {
    // console.log(ele, state, icon, audioSource);
    let toggle_play_pause = '<button type="button" id="' + ele.id + '" class="btn btn-sm btn-primary ' + state + '">' +
        '<span class="glyphicon glyphicon-' + icon + '" aria-hidden="true"></span>' +
        // ' Play Audio'+
        '</button>';
    if (audioSource) {
        // console.log(audioSource);
        let embededAudio = '<audio id="' + ele.id + '_audioEle" onended="audioEnded(this)" controls autoplay hidden oncontextmenu="return false" controlslist="nofullscreen nodownload noremoteplayback noplaybackrate">' +
            '<source src="' + audioSource + '" type="audio/wav"></audio>';
            toggle_play_pause += embededAudio;
    }
    // console.log(audioSource);
    ele.parentNode.innerHTML = toggle_play_pause;
    // console.log(audioSource);
    playPauseEvent();
    // console.log(audioSource);
}

function audioEnded(ele) {
    let eleId = ele.id;
    let audioBtnId = eleId.replaceAll("_audioEle", "");
    // console.log(eleId, audioBtnId);
    let audioBtnEle = document.getElementById(audioBtnId);
    togglePlayPause(audioBtnEle, 'playaudioclass', 'play');
}

// function getAudioSharedWithUsersList(audioInfo) {
$(document).ready(function () {
    $("#browseShareSelectMode").change(function () {
        if (this.value === 'remove') {
            // console.log(audioIds);
            $.getJSON('/browsefilesharedwithuserslist', {
                a: JSON.stringify({
                    "audioInfo": audioIds,
                })
            }, function (data) {
                // console.log(data, $('#browseRemoveShareSelect').hasClass("select2-hidden-accessible"));
                // if (!$(obj).hasClass("select2-hidden-accessible"))

                // $('#browseRemoveShareSelect').select2('destroy');
                document.getElementById("browseRemoveShareSelect").innerHTML = "";
                $('#browseRemoveShareSelect').select2({
                    placeholder: 'Remove Access For',
                    data: data.sharedWithUsers,
                    allowClear: true
                });
                document.getElementById("browseShareSelect").style.display = "none";
                $('#browseShareSelect').select2('destroy');
                document.getElementById("browsesharebtn").style.display = "none";
                document.getElementById("browseRemoveShareSelect").style.display = "block";
                document.getElementById("removesharedfileaccess").style.display = "inline";
            });
            return false;
        }
        else if (this.value === 'share') {
            $('#browseShareSelect').select2({
                placeholder: 'Share with',
                // data: usersList,
                allowClear: true
            });
            document.getElementById("browseRemoveShareSelect").style.display = "none";
            $('#browseRemoveShareSelect').select2('destroy');
            document.getElementById("removesharedfileaccess").style.display = "none";
            document.getElementById("browseShareSelect").style.display = "block";
            document.getElementById("browsesharebtn").style.display = "inline";
        }
    });
});
