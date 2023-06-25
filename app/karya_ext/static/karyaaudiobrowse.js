function createSelect2(eleId, optionsList, selectedOption) {
    let ele = '';
    for (let i=0; i<optionsList.length; i++) {
        option = optionsList[i];
        if (option === selectedOption) {
            ele += '<option value="'+option+'" selected>'+option+'</option>'
        }
        else {
            ele += '<option value="'+option+'">'+option+'</option>'
        }
    }
    $('#'+eleId).append(ele);
    $('#'+eleId).select2({
        // data: optionsList
        });
}

function createBrowseActions(projectOwner, currentUsername) {
    let ele = '';
    let browseActionOptionsList = ['Delete']
    ele += '<label for="browseactiondropdown">Action:&nbsp;</label>'+
            '<select class="custom-select custom-select-sm" id="browseactiondropdown" style="width: 50%;"></select>&nbsp;&nbsp;&nbsp;&nbsp;';
    ele += '<button type="button" class="btn btn-danger" id="multipleaudiodelete"  style="display: inline;">'+
            '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>'+
            ' Delete Multiple Audio</button>';
    ele += '<button type="button" class="btn btn-success" id="multipleaudiorevoke" style="display: none;">'+
            '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'+
            ' Revoke Multiple Audio</button>';
    $('#browseaudiodropdowns').append(ele);
    if (currentUsername === projectOwner) {
        browseActionOptionsList.push('Revoke');
    }
    createSelect2('browseactiondropdown', browseActionOptionsList, 'Delete');
}

function createAudioBrowseTable(audioDataFields, audioData) {
    console.log(audioData);
    let count = audioData.length
    let browseActionSelectedOption = document.getElementById('browseactiondropdown').value;
    let ele = '';
    ele += '<p id="totalrecords">Total Records:&nbsp;'+count+'</p>'+
            '<table class="table table-striped " id="myTable">'+
            '<thead>'+
            '<tr>'+
            '<th><input type="checkbox" id="headcheckbox" onchange="checkAllAudio(this)" name="chk[]" checked/>&nbsp;</th>';
    for (let i=0; i<audioDataFields.length; i++) {
        ele += '<th onclick="sortTable('+(i+1)+')">'+audioDataFields[i]+'</th>';
    }
    ele += '<th>View</th>';
    ele += '<th>'+browseActionSelectedOption+'</th>'+
            '</tr>'+
            '</thead>';
    ele += '<tbody id="myTableBody">';
            // {% for data in sdata %}
    for (let i=0; i<audioData.length; i++) {
        aData = audioData[i];
        ele += '<tr>'+
                '<td><input type="checkbox" id="lexemecheckbox" onchange="checkAudio(this)" name="name1" checked /></td>';
        for (let j=0; j<audioDataFields.length; j++) {
            let field = audioDataFields[j];
            if (field in aData) {
                if (field == 'Audio File') {
                    ele += '<td id='+field+'>'+
                            '<audio controls><source src="'+aData[field]+'" type="audio/wav"></audio>'+
                            '</td>';
                }
                else {
                    ele += '<td id='+field+'>'+aData[field]+'</td>';
                }
                
            }
            else {
                console.log(field);
                ele += '<td> - </td>';
            }
        }
        ele += '<td><button type="button" id="viewaudio" class="btn btn-primary viewaudioclass">'+
                    '<span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span>'+
                    ' View Audio'+
                    '</button></td>';
        if (browseActionSelectedOption === 'Delete') {
            ele += '<td><button type="button" id="deleteaudio" class="btn btn-danger deleteaudioclass">'+
                    '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>'+
                    ' Delete Audio'+
                    '</button></td>';

        }
        else if (browseActionSelectedOption === 'Revoke') {
            ele += '<td><button type="button" id="revokeaudio" class="btn btn-success revokeaudioclass">'+
                    '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'+
                    ' Revoke Audio'+
                    '</button></td>';

        }
        ele += '</tr>';
    }
    ele += '</tbody>'+
            '</table>';
    $('#audiobrowsetable').html(ele);
}

function createAudioBrowse(newData) {
    console.log(newData);
    let speakerIds = newData['speakerIds'];
    let currentUsername = newData['currentUsername']
    let projectOwner = newData['projectOwner']
    let shareInfo = newData['shareInfo']
    let shareMode = shareInfo['sharemode']
    let activeSpeakerId = shareInfo['activespeakerId']
    let audioDataFields = newData['audioDataFields']
    let audioData = newData['audioData']
    createSelect2('speakeridsdropdown', speakerIds, activeSpeakerId);
    createSelect2('audiofilescountdropdown', [10, 20, 50], 10)
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
        updateAudioBrowseTable();
        if (browseActionSelectedOption === 'Delete') {
            document.getElementById('multipleaudiorevoke').style.display = "none";
            document.getElementById('multipleaudiodelete').style.display = "inline";
        }
        else if (browseActionSelectedOption === 'Revoke') {
            document.getElementById('multipleaudiodelete').style.display = "none";
            document.getElementById('multipleaudiorevoke').style.display = "inline";
        }
    })
    // change audio file count to show
    $("#audiofilescountdropdown").change(function() {
        // console.log(browseActionSelectedOption);
        updateAudioBrowseTable();
    })
    // delete single audio
    $(".deleteaudioclass").click(function() {
        let audioInfo = getSingleAudioBrowseAction(this);
        deleteAudioFLAG = confirm("Delete This Audio!!!");
        if(deleteAudioFLAG) {
            audioBrowseAction(audioInfo);
        }
    });
    // delete multiple audios
    $("#multipleaudiodelete").click(function() {
        audios = GetSelected();
        console.log(audios);
        deleteAudioFLAG = confirm("Delete These Audios!!!");
        if(deleteAudioFLAG) {
            audioBrowseAction(audios);
        }
    });
    // revoke single audio
    $(".revokeaudioclass").click(function() {
        let audioInfo = getSingleAudioBrowseAction(this);
        revokeAudioFLAG = confirm("Revoke This Audio!!!");
        if(revokeAudioFLAG) {
            audioBrowseAction(audioInfo);
        }
    });
    // revoke multiple audios
    $("#multipleaudiorevoke").click(function() {
        audios = GetSelected();
        console.log(audios);
        revokeAudioFLAG = confirm("Revoke These Audios!!!");
        if(revokeAudioFLAG) {
            audioBrowseAction(audios);
        }
    });
}

function updateAudioBrowseTable() {
    let audioBrowseInfo = getAudioBrowseInfo();
    $.ajax({
        data : {
          a : JSON.stringify(audioBrowseInfo)
        },
        type : 'GET',
        url : '/karya_bp.karyaupdateaudiobrowsetable'
      }).done(function(data){
        console.log(data.audioDataFields, data.audioData);
        createAudioBrowseTable(data.audioDataFields, data.audioData);
        eventsMapping();
      });
}

function audioBrowseAction(audioInfo) {
    let audioBrowseInfo = getAudioBrowseInfo();
    $.ajax({
        data : {
          a : JSON.stringify({
            "audioInfo": audioInfo,
            "audioBrowseInfo": audioBrowseInfo
        })
        },
        type : 'GET',
        url : '/karya_bp.karyaaudiobrowseaction'
      }).done(function(data){
            window.location.reload();
        // console.log(data.audioDataFields, data.audioData);
        // createAudioBrowseTable(data.audioDataFields, data.audioData);
        // eventsMapping();
      });
}

function getAudioBrowseInfo() {
    let activeSpeakerId = document.getElementById('speakeridsdropdown').value;
    let audioFilesCount = Number(document.getElementById('audiofilescountdropdown').value);
    let browseActionSelectedOption = document.getElementById('browseactiondropdown').value;
    if (browseActionSelectedOption === 'Delete') {
        browseActionSelectedOption = 0
    }
    else if (browseActionSelectedOption === 'Revoke') {
        browseActionSelectedOption = 1
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
    // checkbox in table header true or false when any checkbox of table body is true or false
    var checkboxcount = 0;
    var headcheckbox = document.getElementById('headcheckbox');
    var checkboxes = document.getElementsByTagName('input');
    var totalrecords = document.getElementById('totalrecords').innerHTML;
    let totalrecordscount = totalrecords.match(/\d/);
    // alert(totalrecordscount);
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
    console.log(audioInfo);

    return audioInfo
}