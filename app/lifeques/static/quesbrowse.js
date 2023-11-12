var activePageNumber = 1;
var quesIds = [];

var quesSortingCategories = [
    {"id": "lifespeakerid", "text": "Source"},
    {"id": "sourcemetainfo", "text": "Source Meta Info"}
    // {"id": "agegroup", "text": "Age Group"},
    // {"id": "gender", "text": "Gender"},
    // {"id": "educationlevel", "text": "Education Level"},
    // {"id": "educationmediumupto12", "text": "Education Medium Upto 12"},
    // {"id": "educationmediumafter12", "text": "Education Medium After 12"},
    // {"id": "speakerspeaklanguage", "text": "Source Language"}
]

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
    $('#'+eleId).html(ele);
    $('#'+eleId).select2({
        // data: optionsList
        });
}

function createSelect2FromObject(eleId, optionsObject, selectedOption) {
    let ele = '';
    for (let i=0; i<optionsObject.length; i++) {
        optionValue = optionsObject[i]['id'];
        option = optionsObject[i]['text'];
        if (option === selectedOption) {
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

function createSelect2optgroup(eleId, optionsObject, selectedOption) {
    let ele = '';
    for (let [key, value] of Object.entries(optionsObject)) {
        let optGroup = key;
        let optGroupId = key.toLowerCase().replaceAll(' ', '');
        ele += '<optgroup id="'+optGroupId+'" label="'+optGroup+'">';
        for (let i=0; i<value.length; i++) {
            option = value[i];
            if (option === selectedOption) {
                ele += '<option value="'+option+'" selected>'+option+'</option>'
            }
            else {
                ele += '<option value="'+option+'">'+option+'</option>'
            }
        }
        ele += '</optgroup>';
    }
    $('#'+eleId).html(ele);
    $('#'+eleId).select2({
        // data: value
        placeholder: 'Filter Ques On',
        allowClear: true
        });
}

function createBrowseActions(projectOwner, currentUsername, shareMode, shareChecked, downloadChecked) {
    let ele = '';
    let browseActionOptionsList = ['Delete']
    ele += '<div class="pull-right">';
    // if (downloadChecked === 'true') {
    //     // multiple ques download
    //     ele += '<button type="button" class="btn btn-success classmultipletranscriptiondownload" id="idmultipletranscriptiondownload" style="display: inline;" data-toggle="modal" data-target="#myDownloadTranscriptionModal">'+
    //     '<span class="glyphicon glyphicon-download-alt" aria-hidden="true"></span>'+
    //     ' +1</button>';
    // }

    // if (shareChecked === 'true') {
    //     // multiple ques share
    //     ele += '<button type="button" class="btn btn-warning" id="multiplequeshare" style="display: inline;" data-toggle="modal" data-target="#browseShareModal">'+
    //     '<span class="glyphicon glyphicon-share-alt" aria-hidden="true"></span>'+
    //     ' +1</button>';
    // }
    
    if (shareMode >= 4) {
        
        // let tabSpace = '&nbsp;&nbsp;&nbsp;&nbsp;';
        // ele += '<label for="browseactiondropdown">Action:&nbsp;</label>'+
        ele +='<select class="custom-select custom-select-sm" id="browseactiondropdown"></select>';
        // ele += tabSpace;
        // multiple ques delete
        ele += '<button type="button" class="btn btn-danger" id="multiplequesdelete"  style="display: inline;">'+
                '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>'+
                ' +1</button>';
        // ele += tabSpace;
        // multiple ques revove
        ele += '<button type="button" class="btn btn-success" id="multiplequesrevoke" style="display: none;">'+
                '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'+
            ' +1</button>';
        
        // ele += tabSpace;
    }
    ele += '</div>';

    $('#browsequesdropdowns').append(ele);
    if (shareMode >= 4) {
        if (currentUsername === projectOwner) {
            browseActionOptionsList.push('Revoke');
        }
        createSelect2('browseactiondropdown', browseActionOptionsList, 'Delete');
    }
}

function createQuesBrowseTable(
    quesDataFields,
    quesData,
    shareMode=0,
    totalRecords=0,
    shareChecked = "false",
    downloadChecked = "false",
    shareInfo = undefined,
    ) {
    // console.log(quesData);
    // console.log(shareChecked);
    // console.log(downloadChecked);
    let count = quesData.length
    let ele = '';
    let browseActionSelectedOption = '';
    // ele += '<p id="actualtotalrecords">Total Records:&nbsp;'+totalRecords+'</p>';
    ele += '<div class="col">';
    ele += '<strong><p id="totalrecords" style="display:inline">Showing Records:&nbsp;'+count+' of '+totalRecords+'</p></strong>';
    ele += '<div class="pull-right">'+
            '<input id="myInput" type="text" placeholder="Search">'
            '</div>';
    ele +=  '</div>';
    ele += '<hr>';
    ele += '<table class="table table-striped " id="myTable">'+
            '<thead>'+
            '<tr>'+
            '<th><input type="checkbox" id="headcheckbox" onchange="checkAllQues(this)" name="chk[]" checked/>&nbsp;</th>';
    for (let i=0; i<quesDataFields.length; i++) {
        if (quesDataFields[i] == "quesFilename"){
            ele += '<th onclick="sortTable('+(i+1)+')" hidden>'+quesDataFields[i]+'</th>';
            continue;
        }
        ele += '<th onclick="sortTable('+(i+1)+')">'+quesDataFields[i]+'</th>';
    }
    ele += '<th>View</th>';
    // if (downloadChecked === 'true') {
    //     ele += '<th>Download</th>';
    //     // ele += '<th>Share Info</th>';
    // }
    // if (shareChecked === 'true') {
    //     ele += '<th>Share</th>';
    //     // ele += '<th>Share Info</th>';
    // }
    if (shareMode >= 4) {
        browseActionSelectedOption = document.getElementById('browseactiondropdown').value;
        ele += '<th>'+browseActionSelectedOption+'</th>';
    }
    
    
    
    ele += '</tr>'+
            '</thead>';
    ele += '<tbody id="myTableBody">';
            // {% for data in sdata %}
    for (let i=0; i<quesData.length; i++) {
        aData = quesData[i];
        let quesCount = i+1;
        ele += '<tr>'+
                '<td><input type="checkbox" id="lexemecheckbox" onchange="checkQues(this)" name="name1" checked /></td>';
        for (let j=0; j<quesDataFields.length; j++) {
            let field = quesDataFields[j];
            if (field in aData) {
                if (field == "quesFilename") {
                    ele += '<td id='+field+' hidden>'+aData[field]+'</td>';
                    continue;
                }
                if (field == 'Ques File') {
                    ele += '<td>'+
                            '<button type="button" id="playques_'+quesCount+'" class="btn btn-primary playquesclass">'+
                            '<span class="glyphicon glyphicon-play" aria-hidden="true"></span>'+
                            // ' Play Ques'+
                            '</button>'+
                            '</td>';
                    // ele += '<td id='+field+'>'+
                            // '<ques controls oncontextmenu="return false" controlslist="nofullscreen nodownload noremoteplayback noplaybackrate">'+
                            // '<source src="'+aData[field]+'" type="ques/wav"></ques>'+
                            // '</td>';
                }
                else {
                    ele += '<td id='+field+'>'+aData[field]+'</td>';
                }
                
            }
            else {
                // console.log(field);
                ele += '<td> - </td>';
            }
        }
        ele += '<td><button type="button" id="viewques" class="btn btn-primary viewquesclass">'+
                    '<span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span>'+
                    // ' View Ques'+
            '</button></td>';
        // if (downloadChecked === 'true') {
        //     // multiple ques download
        //     ele += '<td><button type="button" class="btn btn-success classsingletranscriptiondownload" id="idsingletranscriptiondownload" data-toggle="modal" data-target="#myDownloadTranscriptionModal">'+
        //     '<span class="glyphicon glyphicon-download-alt" aria-hidden="true"></span>'+
        //     '</button></td>';
        // }
        // if (shareChecked === 'true') {
        //     ele += '<td><button type="button" id="shareques" class="btn btn-warning sharequesclass"  data-toggle="modal" data-target="#browseShareModal">'+
        //             '<span class="glyphicon glyphicon-share-alt" aria-hidden="true"></span>'+
        //             // ' Share Ques'+
        //             '</button></td>';
        //     // if (shareInfo) {
        //     //     ele += '<td>'+shareInfo+'</td>';
        //     // }
        //     // else {
        //     //     // console.log(field);
        //     //     ele += '<td> - </td>';
        //     // }
        // }
        if (browseActionSelectedOption === 'Delete') {
            ele += '<td><button type="button" id="deleteques" class="btn btn-danger deletequesclass">'+
                    '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>'+
                    // ' Delete Ques'+
                    '</button></td>';

        }
        else if (browseActionSelectedOption === 'Revoke') {
            ele += '<td><button type="button" id="revokeques" class="btn btn-success revokequesclass">'+
                    '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'+
                    // ' Revoke Ques'+
                    '</button></td>';

        }
        
        
        ele += '</tr>';
    }
    ele += '</tbody>'+
            '</table>';
    $('#quesbrowsetable').html(ele);
}

function createQuesBrowse(newData) {
    // console.log(newData);
    // let speakerIds = newData['speakerIds'];
    let currentUsername = newData['currentUsername']
    let projectOwner = newData['projectOwner']
    let projectName = newData['activeProjectName']
    let totalRecords = newData['totalRecords']
    let shareInfo = newData['shareInfo']
    // console.log("Share info", shareInfo);
    let shareMode = shareInfo['sharemode']
    let shareChecked = shareInfo['sharechecked']
    let downloadChecked = shareInfo['downloadchecked']
    // let activeSpeakerId = shareInfo['activespeakerId']
    // console.log(activeSpeakerId)
    let quesDataFields = newData['quesDataFields']
    let quesData = newData['quesData']
    // let transcriptionsBy = newData['transcriptionsBy']
    // createSelect2FromObject('quesortingcategoriesdropdown', quesSortingCategories, 'Source');
    // createSelect2('quesortingsubcategoriesdropdown', speakerIds, activeSpeakerId);
    // createSelect2('speakeridsdropdown', [], '');
    createSelect2('quesfilescountdropdown', [10, 20, 50], 10)
    // if (shareMode >= 4) {
    createBrowseActions(projectOwner, currentUsername, shareMode, shareChecked, downloadChecked);
    // }
    createQuesBrowseTable(quesDataFields, quesData, shareMode, totalRecords, shareChecked, downloadChecked);

    // generateDownloadForm(shareInfo, transcriptionsBy, currentUsername, projectName);

    // downloadModalSelect2();

    eventsMapping();
    createPagination(totalRecords)
}

function eventsMapping() {
    // change in browse action select
    $("#browseactiondropdown").change(function() {
        let browseActionSelectedOption = document.getElementById('browseactiondropdown').value;
        // console.log(browseActionSelectedOption);
        // let selectedQuesSortingCategories = document.getElementById("quesortingcategoriesdropdown").value;
        // console.log(selectedQuesSortingCategories);
        // if (selectedQuesSortingCategories === 'sourcemetainfo') {
        //     quesFilter();
        // }
        // else {
        updateQuesBrowseTable();
        // }
        if (browseActionSelectedOption === 'Delete') {
            document.getElementById('multiplequesrevoke').style.display = "none";
            document.getElementById('multiplequesdelete').style.display = "inline";
        }
        else if (browseActionSelectedOption === 'Revoke') {
            document.getElementById('multiplequesdelete').style.display = "none";
            document.getElementById('multiplequesrevoke').style.display = "inline";
        }
    })
    // change ques sorting categories
    $("#quesortingcategoriesdropdown").change(function() {
        // console.log(browseActionSelectedOption);
        updateQuesSortingSubCategoriesDropdown();
    })
    // change ques file count to show
    $("#quesfilescountdropdown").change(function() {
        // console.log(browseActionSelectedOption);
        // let selectedQuesSortingCategories = document.getElementById("quesortingcategoriesdropdown").value;
        // console.log(selectedQuesSortingCategories);
        // if (selectedQuesSortingCategories === 'sourcemetainfo') {
        //     quesFilter();
        // }
        // else {
        updateQuesBrowseTable();
        // }
    })

    // download single transcription
    $(".classsingletranscriptiondownload").click(function () {
        let quesInfo = getSingleQuesBrowseAction(this);
        quesIds = Object.keys(quesInfo);
        current_id = quesIds[0];
        console.log("Single ques info", quesIds);
        // $('#idquesids').val("").trigger('change');
        $('#idquesids').empty().trigger('change');
        let new_option = new Option(quesInfo[current_id], current_id, false, true);
        $('#idquesids').append(new_option);
        $('#idquesids').trigger('change');

        // $("#idquesids").val(quesIds).trigger("change");
        
    });

    // download multiple transcriptions
    $("#idmultipletranscriptiondownload").click(function() {
        let multipleQuesInfo = GetSelected();
        // quesIds = Object.keys(multipleQuesInfo);
        // $('#idquesids').val("").trigger('change');
        $('#idquesids').empty().trigger('change');
        // for (i = 0; i < quesIds.length; i++) {
        for (var current_id in multipleQuesInfo) {
            // current_id = quesIds[i]
            // if (!all_medium.includes(current_medium)) {
            // if (!   $('#idviewotherlangs').find("option[value='" + current_language + "']").length) {
                // $('#idviewmediumpre').val(current_medium).trigger('change');
            let new_option = new Option(multipleQuesInfo[current_id], current_id, false, true);
            $('#idquesids').append(new_option);
            // }            
        }
        $('#idquesids').trigger('change');
        // console.log("Multiple ques", multipleQuesInfo);

    });

    // delete single ques
    $(".deletequesclass").click(function() {
        let quesInfo = getSingleQuesBrowseAction(this);
        // console.log("Single ques info", quesInfo);
        deleteQuesFLAG = confirm("Delete This Ques!!!");
        if(deleteQuesFLAG) {
            quesBrowseAction(quesInfo);
        }
    });
    // delete multiple ques
    $("#multiplequesdelete").click(function() {
        ques = GetSelected();
        // console.log("Multiple ques", ques);
        deleteQuesFLAG = confirm("Delete These Ques!!!");
        if(deleteQuesFLAG) {
            quesBrowseAction(ques);
        }
    });
    // revoke single ques
    $(".revokequesclass").click(function() {
        let quesInfo = getSingleQuesBrowseAction(this);
        revokeQuesFLAG = confirm("Revoke This Ques!!!");
        if(revokeQuesFLAG) {
            quesBrowseAction(quesInfo);
        }
    });
    // revoke multiple ques
    $("#multiplequesrevoke").click(function() {
        ques = GetSelected();
        // console.log(ques);
        revokeQuesFLAG = confirm("Revoke These Ques!!!");
        if(revokeQuesFLAG) {
            quesBrowseAction(ques);
        }
    });
    // play single ques
    $(".playquesclass").click(function() {
        let quesInfo = getSingleQuesBrowseAction(this);
        quesBrowseActionPlay(quesInfo, this);
    });
    $(".pausequesclass").click(function() {
        let playingQuesId = this.id;
        // console.log(playingQuesId);
        let playingQuesEleId = playingQuesId + "_quesEle";
        let playingQuesEle = document.getElementById(playingQuesEleId);
        // console.log(playingQuesEleId, playingQuesEle);
        playingQuesEle.pause();
        togglePlayPause(this, 'playquesclass', 'play');
        
    });
    $(".sharequesclass").click(function() {
        let quesInfo = getSingleQuesBrowseAction(this);
        // console.log(quesInfo);
        // console.log(Object.keys(quesInfo));
        quesIds = Object.keys(quesInfo);
        $("#browseShareSelectMode").val(null).trigger('change');
        $('#browseShareSelectMode').select2({
        // placeholder: 'Share with',
        data: browseShareSelMode,
        // allowClear: true
        });
        document.getElementById("browseRemoveShareSelect").style.display = "none";
        document.getElementById("removesharedfileaccess").style.display = "none";
        // $('#quesInfo').select2({
        //     // placeholder: 'Share with',
        //     data: quesInfo,
        //     // allowClear: true
        // });
        // shareQuesFLAG = confirm("Share This Ques!!!");
        // if(shareQuesFLAG) {
        // getQuesSharedWithUsersList(quesInfo);
        // quesBrowseActionShare(quesInfo);
        // }
    });
    $("#multiplequeshare").click(function() {
        ques = GetSelected();
        // console.log(ques);
        // console.log(Object.keys(ques));
        quesIds = Object.keys(ques);
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
        // quesBrowseActionShare(ques);
    });
}

function updateQuesSortingSubCategoriesDropdown() {
    let quesBrowseInfo = getQuesBrowseInfo();
    // let selectedQuesSortingCategories = document.getElementById("quesortingcategoriesdropdown").value;
    $.ajax({
        data : {
          a : JSON.stringify({
            "quesBrowseInfo": quesBrowseInfo,
            "selectedQuesSortingCategories": selectedQuesSortingCategories
        })
        },
        type : 'GET',
        url : '/updatequesortingsubcategories'
      }).done(function(data){
        // console.log(data);
        quesSortingSubCategories = data.quesSortingSubCategories;
        selectedQuesSortingSubCategories = data.selectedQuesSortingSubCategories;
        // console.log(quesSortingSubCategories, selectedQuesSortingSubCategories);
        if (selectedQuesSortingCategories === 'sourcemetainfo') {
            $('#speakeridsdropdown').select2('destroy');
            document.getElementById('speakeridsdropdown').style.display = "none";
            document.getElementById('quesortingsubcategoriesdropdown').style.display = "block";
            document.getElementById('quesfilter').style.display = "inline";
            createSelect2optgroup('quesortingsubcategoriesdropdown', quesSortingSubCategories, selectedQuesSortingSubCategories);
            // quesbrowsefilter.js
            quesFilteringEvent();
        }
        else if (selectedQuesSortingCategories === 'lifespeakerid') {
            $('#quesortingsubcategoriesdropdown').select2('destroy');
            document.getElementById('quesortingsubcategoriesdropdown').style.display = "none";
            document.getElementById('quesfilter').style.display = "none";
            document.getElementById('speakeridsdropdown').style.display = "block";
            createSelect2('speakeridsdropdown', quesSortingSubCategories, selectedQuesSortingSubCategories);
        }
        createQuesBrowseTable(data.quesDataFields, data.quesData, data.shareMode, data.totalRecords, data.shareChecked, data.downloadChecked);
        eventsMapping();
        createPagination(data.totalRecords)
      });
}

function updateQuesBrowseTable() {
    let quesBrowseInfo = getQuesBrowseInfo();
    $.ajax({
        data : {
          a : JSON.stringify(quesBrowseInfo)
        },
        type : 'GET',
        url : '/lifeques/updatequesbrowsetable'
      }).done(function(data){
        console.log(data.quesDataFields, data.quesData, data.shareMode);
        createQuesBrowseTable(data.quesDataFields, data.quesData, data.shareMode, data.totalRecords, data.shareChecked, data.downloadChecked);
        eventsMapping();
        createPagination(data.totalRecords)
      });
}

function quesBrowseAction(quesInfo) {
    let quesBrowseInfo = getQuesBrowseInfo();
    $.ajax({
        data : {
          a : JSON.stringify({
            "quesInfo": quesInfo,
            "quesBrowseInfo": quesBrowseInfo
        })
        },
        type : 'GET',
        url : '/lifeques/quesbrowseaction'
      }).done(function(data){
            window.location.reload();
      });
}

function quesBrowseActionPlay(quesInfo, quesCountInfo) {
    // console.log(quesCountInfo);
    let quesBrowseInfo = getQuesBrowseInfo();
    quesBrowseInfo['pageId'] = activePageNumber;
    let data_1 = {
        quesInfo: quesInfo,
        quesBrowseInfo: quesBrowseInfo
    }
    $.post( "/quesbrowseactionplay", {
        a: JSON.stringify(data_1)
    //   }),
      })
      .done(function(data){
            // window.location.reload();
            // console.log(data)
            createQuesBrowseTable(data.quesDataFields, data.quesData, data.shareMode, data.totalRecords, data.shareChecked, data.downloadChecked);
            eventsMapping();
            // console.log(activePageNumber);
            createPagination(data.totalRecords, activePageNumber);
            // console.log(quesCountInfo);
            quesCountInfo = document.getElementById(quesCountInfo.id);
            console.log(quesCountInfo);
            let quesSource = data.quesSource;
            // console.log(quesSource)
            // let embededQues = new Ques(quesSource);
            // embededQues = new Ques(quesSource);
            // console.log(embededQues);
            // embededQues.play();
            togglePlayPause(quesCountInfo, 'pausequesclass', 'pause', quesSource)
            // let togglePlayPause = '<button type="button" id="'+quesCountInfo.id+'" class="btn btn-primary pausequesclass">'+
            //                         '<span class="glyphicon glyphicon-pause" aria-hidden="true"></span>'+
            //                         // ' Play Ques'+
            //                         '</button>';
            // let embededQues = '<ques controls autoplay hidden oncontextmenu="return false" controlslist="nofullscreen nodownload noremoteplayback noplaybackrate">'+
            //                     '<source src="'+quesSource+'" type="ques/wav"></ques>';
            // quesCountInfo.parentNode.innerHTML = togglePlayPause;
            // eventsMapping();
      });
}

// function quesBrowseActionShare(quesInfo) {
//     let quesBrowseInfo = getQuesBrowseInfo();
//     $.ajax({
//         data : {
//           a : JSON.stringify({
//             "quesInfo": quesInfo,
//             "quesBrowseInfo": quesBrowseInfo
//         })
//         },
//         type : 'GET',
//         url : '/quesbrowseactionshare'
//       }).done(function(data){
//             window.location.reload();
//       });
// }

function getQuesBrowseInfo() {
    // let activeSpeakerId = document.getElementById('speakeridsdropdown').value;
    let quesFilesCount = Number(document.getElementById('quesfilescountdropdown').value);
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
    let quesBrowseInfo = {
        // "activeSpeakerId": activeSpeakerId,
        "quesFilesCount": quesFilesCount,
        "browseActionSelectedOption": browseActionSelectedOption
    }

    return quesBrowseInfo
}

function GetSelected() {
    
    //Reference the Table.
    var grid = document.getElementById("myTable");
    
    //Reference the CheckBoxes in Table.
    var checkBoxes = grid.getElementsByTagName("INPUT");
    
    // var checkedques = [];
    var checkedques = {};
    //Loop through the CheckBoxes.
    for (var i = 1; i < checkBoxes.length; i++) {
        
        if (checkBoxes[i].type == 'checkbox' && checkBoxes[i].checked == true) {
            var row = checkBoxes[i].parentNode.parentNode;
            // checkedques.push(row.cells[1].innerHTML);
            key = row.cells[1].innerHTML;
            value = row.cells[2].innerHTML;
            checkedques[key] = value;
        }
    }
    return checkedques;
}

function checkAllQues(ele) {
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

function checkQues(ele) {
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

function getSingleQuesBrowseAction(element) {

    var quesInfo = {}
    var $row = $(element).closest("tr");    // Find the row
    var quesId = $row.find("#quesId").text(); // Find the text
    var quesFilename = $row.find("#quesFilename").text(); // Find the text
    quesInfo[quesId] = quesFilename
    // console.log(quesInfo);

    return quesInfo
}

function createPagination(totalRecords, active=1) {
    let quesFilesCount = Number(document.getElementById('quesfilescountdropdown').value);
    let paginationEle = '';
    totalPages = Math.ceil(totalRecords/quesFilesCount);
    // console.log(totalPages);
    paginationEle +=  '<div class="btn-group">';
    for (let i=1; i<=totalPages; i++) {
        if (i == active) {
            paginationEle += '<button type="button" class="btn btn-primary createpagination" id="'+i+'" onclick="changeQuesBrowsePage(this.id)">'+i+'</button>';
        }
        else {
            paginationEle += '<button type="button" class="btn createpagination" id="'+i+'" onclick="changeQuesBrowsePage(this.id)">'+i+'</button>';
        }
    }
    paginationEle += '</div><br><br>';
    $("#quesbrowsepagination").html(paginationEle);
}


function changeQuesBrowsePage(pageId) {
    // console.log(pageId);
    let quesBrowseInfo = getQuesBrowseInfo();
    activePageNumber = Number(pageId);
    quesBrowseInfo['pageId'] = Number(pageId);
    // let selectedQuesSortingCategories = document.getElementById("quesortingcategoriesdropdown").value;
    // console.log(selectedQuesSortingCategories);
    // if (selectedQuesSortingCategories === 'sourcemetainfo') {
    //     quesFilter(Number(pageId));
    // }
    // else {
    $.ajax({
        data : {
            a : JSON.stringify(quesBrowseInfo)
        },
        type : 'GET',
        url : '/lifeques/quesbrowsechangepage'
        }).done(function(data){
        // console.log(data.quesDataFields, data.quesData, data.shareMode);
        createQuesBrowseTable(data.quesDataFields, data.quesData, data.shareMode, data.totalRecords, data.shareChecked, data.downloadChecked);
        eventsMapping();
        createPagination(data.totalRecords, data.activePage);
    });
    // }
}

function togglePlayPause(ele, state, icon, quesSource=undefined) {
    let togglePlayPause = '<button type="button" id="'+ele.id+'" class="btn btn-primary '+state+'">'+
                                    '<span class="glyphicon glyphicon-'+icon+'" aria-hidden="true"></span>'+
                                    // ' Play Ques'+
                                    '</button>';
    if (quesSource) {
        let embededQues = '<ques id="'+ele.id+'_quesEle" onended="quesEnded(this)" controls autoplay hidden oncontextmenu="return false" controlslist="nofullscreen nodownload noremoteplayback noplaybackrate">'+
                        '<source src="'+quesSource+'" type="ques/wav"></ques>';
        togglePlayPause += embededQues;
    }
    ele.parentNode.innerHTML = togglePlayPause;
    eventsMapping();
}

function quesEnded(ele) {
    let eleId = ele.id;
    let quesBtnId = eleId.replaceAll("_quesEle", "");
    // console.log(eleId, quesBtnId);
    let quesBtnEle = document.getElementById(quesBtnId);
    togglePlayPause(quesBtnEle, 'playquesclass', 'play');
}

// function getQuesSharedWithUsersList(quesInfo) {
$(document).ready(function() {
    $("#browseShareSelectMode").change(function() {
        if (this.value === 'remove') {
            // console.log(quesIds);
            $.getJSON('/browsefilesharedwithuserslist', {
                a : JSON.stringify({
                    "quesInfo": quesIds,
                })
            }, function(data) {
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
