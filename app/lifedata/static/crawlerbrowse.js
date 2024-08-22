var activePageNumber = 1;

function crawlerCreateSelect2(eleId, optionsList, selectedOption, moreInfo={}, optionKey='') {
    let ele = '';
    for (let i=0; i<optionsList.length; i++) {
        optionValue = optionsList[i];
        option = optionsList[i];
        if (optionValue in moreInfo) {
            option = moreInfo[optionValue][optionKey]
        }
        if (optionValue === selectedOption) {
            ele += '<option value="'+optionValue+'" selected>'+option+'</option>'
        }
        else {
            ele += '<option value="'+optionValue+'">'+option+'</option>'
        }
    }
    $('#'+eleId).append(ele);
    $('#'+eleId).select2({
        // data: optionsList
        });
}

function createBrowseActions(projectOwner, currentUsername) {
    let ele = '';
    let browseActionOptionsList = ['Delete'];
    // ele += '<label for="browsedataactiondropdowns">Action:&nbsp;</label>';
    ele += '<select class="custom-select custom-select-sm" id="browsedataactiondropdowns" style="width: 70%;"></select>';
    ele += '<button type="button" class="btn btn-danger" id="multipledatadelete"  style="display: inline;">'+
            '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>'+
            ' +1</button>';
    ele += '<button type="button" class="btn btn-success" id="multipledatarevoke" style="display: none;">'+
            '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'+
            ' +1</button>';
    $('#browsedatadropdowns').append(ele);
    if (currentUsername === projectOwner) {
        browseActionOptionsList.push('Revoke');
    }
    crawlerCreateSelect2('browsedataactiondropdowns', browseActionOptionsList, 'Delete');
}

function createCrawlerBrowseTable(crawlerDataFields,
    crawlerData,
    shareMode=0,
    totalRecords=0,
    dataType="text",
    shareChecked = "false",
    downloadChecked = "false",) {
    // console.log(crawlerData);
    let count = crawlerData.length;
    let ele = '';
    let browseActionSelectedOption = '';
    // ele += '<p id="actualtotalrecords">Total Records:&nbsp;'+totalRecords+'</p>';
    // ele += '<p id="totalrecords">Showing Records:&nbsp;'+count+'</p>'+
    //         '<table class="table table-striped " id="myTable">'+
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
            '<th><input type="checkbox" id="headcheckbox" onchange="checkAllData(this)" name="chk[]" checked/>&nbsp;</th>';
    for (let i=0; i<crawlerDataFields.length; i++) {
        if (crawlerDataFields[i] == "audioFilename"){
            ele += '<th onclick="sortTable('+(i+1)+')" hidden>'+crawlerDataFields[i]+'</th>';
            continue;
        }
        ele += '<th onclick="sortTable('+(i+1)+')">'+crawlerDataFields[i]+'</th>';
    }
    ele += '<th>View</th>';
    if (shareMode >= 4) {
        browseActionSelectedOption = document.getElementById('browsedataactiondropdowns').value;
        ele += '<th>'+browseActionSelectedOption+'</th>';
    }
    
    ele += '</tr>'+
            '</thead>';
    ele += '<tbody id="myTableBody">';
            // {% for data in sdata %}
    for (let i=0; i<crawlerData.length; i++) {
        aData = crawlerData[i];
        let audioCount = i+1;
        ele += '<tr>'+
                '<td><input type="checkbox" id="lexemecheckbox" onchange="checkData(this)" name="name1" checked /></td>';
        for (let j=0; j<crawlerDataFields.length; j++) {
            let field = crawlerDataFields[j];
            // console.log(field);
            if (field in aData) {
                if (field == "audioFilename") {
                    ele += '<td id='+field+' hidden>'+aData[field]+'</td>';
                    continue;
                }
                if (field == 'Crawler Audio') {
                    ele += '<td id='+field+'>'+
                            '<audio controls><source src="'+aData[field]+'" type="audio/wav"></audio>'+
                            '</td>';
                }
                else if (field == 'Audio File') {
                    ele += '<td>'+
                            '<button type="button" id="playaudio_'+audioCount+'" class="btn btn-primary playaudioclass">'+
                            '<span class="glyphicon glyphicon-play" aria-hidden="true"></span>'+
                            // ' Play Audio'+
                            '</button>'+
                            '</td>';
                    // ele += '<td id='+field+'>'+
                            // '<audio controls oncontextmenu="return false" controlslist="nofullscreen nodownload noremoteplayback noplaybackrate">'+
                            // '<source src="'+aData[field]+'" type="audio/wav"></audio>'+
                            // '</td>';
                }
                else if (field == 'Crawler Video') {
                    ele += '<td id='+field+'>'+ 
                            '<video width="320" height="240" controls>' +
                                '<source src="'+aData[field]+'" type="video/mp4">' +
                                'Your browser does not support the video tag.' +
                            '</video>' +
                            '</td>';
                }
                 else   if (field == 'Crawler Image') {
                    ele += '<td id='+field+'>'+
                            '<img src="'+aData[field]+'" height="240">'+
                            '</td>';
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
        ele += '<td><button type="button" id="viewcrawler" class="btn btn-primary viewdataclass">'+
                    '<span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span>'+
                    // ' View Data'+
                    '</button></td>';
        if (browseActionSelectedOption === 'Delete') {
            ele += '<td><button type="button" id="deletecrawler" class="btn btn-danger deletedataclass">'+
                    '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>'+
                    // ' Delete Data'+
                    '</button></td>';

        }
        else if (browseActionSelectedOption === 'Revoke') {
            ele += '<td><button type="button" id="revokecrawler" class="btn btn-success revokedataclass">'+
                    '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'+
                    // ' Revoke Data'+
                    '</button></td>';

        }
        ele += '</tr>';
    }
    ele += '</tbody>'+
            '</table>';
    $('#crawlerbrowsetable').html(ele);
}

function createCrawlerBrowse(newData) {
    // console.log(newData);
    let sourceIds = newData['sourceIds'];
    let sourceMetadata = newData['sourceMetadata'];
    let currentUsername = newData['currentUsername'];
    let projectOwner = newData['projectOwner'];
    let totalRecords = newData['totalRecords'];
    let shareInfo = newData['shareInfo'];
    let shareMode = shareInfo['sharemode'];
    let activeSourceId = shareInfo['activesourceId'];
    // console.log(activeSourceId)
    let crawlerDataFields = newData['crawlerDataFields'];
    let crawlerData = newData['crawlerData'];
    let dataTypes = newData['dataTypes'];
    let defaultDataType = newData['defaultDataType'];
    crawlerCreateSelect2('sourceidsdropdown', sourceIds, activeSourceId, sourceMetadata, 'video_title');
    crawlerCreateSelect2('datatypedropdown', dataTypes, defaultDataType)
    crawlerCreateSelect2('sourcedatacountdropdown', [10, 20, 50], 10)
    if (shareMode >= 4) {
        createBrowseActions(projectOwner, currentUsername);
    }
    createCrawlerBrowseTable(crawlerDataFields,
        crawlerData,
        shareMode,
        totalRecords,
        defaultDataType)
    eventsMapping();
    createPagination(totalRecords);
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

function getAudioBrowseInfo() {
    let activeSpeakerId = document.getElementById('sourceidsdropdown').value;
    let audioFilesCount = Number(document.getElementById('sourcedatacountdropdown').value);
    let browseActionSelectedOption = '';
    try {
        browseActionSelectedOption = document.getElementById('browsedataactiondropdowns').value;
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

function audioEnded(ele) {
    let eleId = ele.id;
    let audioBtnId = eleId.replaceAll("_audioEle", "");
    // console.log(eleId, audioBtnId);
    let audioBtnEle = document.getElementById(audioBtnId);
    togglePlayPause(audioBtnEle, 'playaudioclass', 'play');
}

function togglePlayPause(ele, state, icon, audioSource=undefined) {
    let togglePlayPause = '<button type="button" id="'+ele.id+'" class="btn btn-primary '+state+'">'+
                                    '<span class="glyphicon glyphicon-'+icon+'" aria-hidden="true"></span>'+
                                    // ' Play Audio'+
                                    '</button>';
    if (audioSource) {
        let embededAudio = '<audio id="'+ele.id+'_audioEle" onended="audioEnded(this)" controls autoplay hidden oncontextmenu="return false" controlslist="nofullscreen nodownload noremoteplayback noplaybackrate">'+
                        '<source src="'+audioSource+'" type="audio/wav"></audio>';
        togglePlayPause += embededAudio;
    }
    ele.parentNode.innerHTML = togglePlayPause;
    // eventsMapping();
    playpauseEvent();
}

function audioBrowseActionPlay(audioInfo, audioCountInfo) {
    console.log(audioCountInfo);
    console.log(audioCountInfo.id);
    let audioBrowseInfo = getAudioBrowseInfo();
    console.log(activePageNumber);
    audioBrowseInfo['pageId'] = activePageNumber;
    let data_1 = {
        audioInfo: audioInfo,
        audioBrowseInfo: audioBrowseInfo
    }
    $.post( "/lifedata/crawleraudiobrowseactionplay", {
        a: JSON.stringify(data_1)
    //   }),
      })
      .done(function(data){
        console.log(data);
        // console.log(audioCountInfo.id);
        createCrawlerBrowseTable(data.audioDataFields,
            data.audioData,
            data.shareMode,
            data.totalRecords,
            data.shareChecked,
            data.downloadChecked);
        // eventsMapping();
        console.log(activePageNumber);
        createPagination(data.totalRecords, activePageNumber);
        audioCountInfo = document.getElementById(audioCountInfo.id);
        // console.log(audioCountInfo.id);
        let audioSource = data.audioSource;
        togglePlayPause(audioCountInfo, 'pauseaudioclass', 'pause', audioSource)
      });
}

function eventsMapping() {
    // change in browse action select
    $("#browsedataactiondropdowns").change(function() {
        let browseActionSelectedOption = document.getElementById('browsedataactiondropdowns').value;
        // console.log(browseActionSelectedOption);
        updateCrawlerBrowseTable();
        if (browseActionSelectedOption === 'Delete') {
            document.getElementById('multipledatarevoke').style.display = "none";
            document.getElementById('multipledatadelete').style.display = "inline";
        }
        else if (browseActionSelectedOption === 'Revoke') {
            document.getElementById('multipledatadelete').style.display = "none";
            document.getElementById('multipledatarevoke').style.display = "inline";
        }
    })
    // change crawler file count to show
    $("#sourcedatacountdropdown").change(function() {
        // console.log(browseActionSelectedOption);
        updateCrawlerBrowseTable();
    })

    // change data type to show
    $("#datatypedropdown").change(function() {
        // console.log(browseActionSelectedOption);
        updateCrawlerBrowseTable();
    })

    // delete single crawler
    $(".deletedataclass").click(function() {
        let dataInfo = getSingleCrawlerBrowseAction(this);
        deleteCrawlerFLAG = confirm("Delete This Data!!!");
        if(deleteCrawlerFLAG) {
            crawlerBrowseAction(dataInfo);
        }
    });
    // delete multiple crawlers
    $("#multipledatadelete").click(function() {
        crawlers = GetSelected();
        // console.log(crawlers);
        deleteCrawlerFLAG = confirm("Delete These Data!!!");
        if(deleteCrawlerFLAG) {
            crawlerBrowseAction(crawlers);
        }
    });
    // revoke single crawler
    $(".revokedataclass").click(function() {
        let dataInfo = getSingleCrawlerBrowseAction(this);
        revokeCrawlerFLAG = confirm("Revoke This Data!!!");
        if(revokeCrawlerFLAG) {
            crawlerBrowseAction(dataInfo);
        }
    });
    // revoke multiple crawlers
    $("#multipledatarevoke").click(function() {
        crawlers = GetSelected();
        // console.log(crawlers);
        revokeCrawlerFLAG = confirm("Revoke These Data!!!");
        if(revokeCrawlerFLAG) {
            crawlerBrowseAction(crawlers);
        }
    });
    $(".viewdataclass").click(function() {
        let dataInfo = getSingleCrawlerBrowseAction(this);
        crawlerBrowseActionViewData(dataInfo);
    });
    $("#loadnextbutton").click(function() {
        loadNextNData();
    });
    playpauseEvent();
    // play single audio
    // $(".playaudioclass").click(function() {
    //     let audioInfo = getSingleAudioBrowseAction(this);
    //     audioBrowseActionPlay(audioInfo, this);
    // });
    // $(".pauseaudioclass").click(function() {
    //     let playingAudioId = this.id;
    //     // console.log(playingAudioId);
    //     let playingAudioEleId = playingAudioId + "_audioEle";
    //     let playingAudioEle = document.getElementById(playingAudioEleId);
    //     // console.log(playingAudioEleId, playingAudioEle);
    //     playingAudioEle.pause();
    //     togglePlayPause(this, 'playaudioclass', 'play');
        
    // });
}

function playpauseEvent() {
    $(".playaudioclass").click(function() {
        let audioInfo = getSingleAudioBrowseAction(this);
        audioBrowseActionPlay(audioInfo, this);
    });
    $(".pauseaudioclass").click(function() {
        let playingAudioId = this.id;
        // console.log(playingAudioId);
        let playingAudioEleId = playingAudioId + "_audioEle";
        let playingAudioEle = document.getElementById(playingAudioEleId);
        // console.log(playingAudioEleId, playingAudioEle);
        playingAudioEle.pause();
        togglePlayPause(this, 'playaudioclass', 'play');
        
    });
}

function updateCrawlerBrowseTable() {
    let crawlerBrowseInfo = getCrawlerBrowseInfo();
    $.ajax({
        data : {
          a : JSON.stringify(crawlerBrowseInfo)
        },
        type : 'GET',
        url : '/lifedata/updatecrawlerbrowsetable'
      }).done(function(data){
        // console.log(data);
        // console.log(data.crawledDataFields, data.crawledData, data.shareMode);
        createCrawlerBrowseTable(data.crawledDataFields,
            data.crawledData,
            data.shareMode,
            data.totalRecords,
            data.dataType);
        // eventsMapping();
        createPagination(data.totalRecords);
      });
}

function crawlerBrowseAction(dataInfo) {
    let crawlerBrowseInfo = getCrawlerBrowseInfo();
    $.ajax({
        data : {
          a : JSON.stringify({
            "dataInfo": dataInfo,
            "crawlerBrowseInfo": crawlerBrowseInfo
        })
        },
        type : 'GET',
        url : '/lifedata/crawlerbrowseaction'
      }).done(function(data){
            window.location.reload();
      });
}

function crawlerBrowseActionViewData(dataInfo) {
    let crawlerBrowseInfo = getCrawlerBrowseInfo();
    $.ajax({
        data : {
          a : JSON.stringify({
            "dataInfo": dataInfo,
            "crawlerBrowseInfo": crawlerBrowseInfo
        })
        },
        type : 'GET',
        url : '/lifedata/crawlerbrowseactionviewdata'
      }).done(function(data){
        commentInfo = data.commentInfo;
        // console.log(commentInfo);
        let modalEle = ''
        modalEle += '<div class="modal fade" id="myViewModal" role="dialog">'+
                    '<div class="modal-dialog modal-lg">'+
                    '<div class="modal-content">'+
                    '<div class="modal-header" style="padding:10px 50px;">'+
                    '<button type="button" class="close" data-dismiss="modal">&times;</button>'+
                    '</div>'+
                    '<div class="modal-body" style="padding:50px 60px; word-wrap: break-word;">';
        for (let [key, value] of Object.entries(commentInfo)){
            modalEle += '<p><strong>'+key+':</strong> '+value+'</p>'
        }
        modalEle += '</div>'+
                    '<div class="modal-footer">'+
                    '<button id="refreshmodal" type="submit" class="btn btn-danger btn-default pull-left" data-dismiss="modal">Close</button>'+
                    '</div>'+
                    '</div>'+
                    '</div>'+
                    '</div>';
        $("#crawlerbrowsedataview").html(modalEle);
        $("#myViewModal").modal();
      });
}

function getCrawlerBrowseInfo() {
    let activeSourceId = document.getElementById('sourceidsdropdown').value;
    let crawledDataCount = Number(document.getElementById('sourcedatacountdropdown').value);
    let dataType = document.getElementById('datatypedropdown').value;
    let browseActionSelectedOption = '';
    try {
        browseActionSelectedOption = document.getElementById('browsedataactiondropdowns').value;
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
    let crawlerBrowseInfo = {
        "activeSourceId": activeSourceId,
        "crawledDataCount": crawledDataCount,
        "browseActionSelectedOption": browseActionSelectedOption,
        "dataType": dataType
    }
    // console.log(crawlerBrowseInfo);

    return crawlerBrowseInfo
}

function GetSelected() {
    
    //Reference the Table.
    var grid = document.getElementById("myTable");
    
    //Reference the CheckBoxes in Table.
    var checkBoxes = grid.getElementsByTagName("INPUT");
    
    // var checkeddatapoints = [];
    var checkeddatapoints = {};
    //Loop through the CheckBoxes.
    for (var i = 1; i < checkBoxes.length; i++) {
        
        if (checkBoxes[i].type == 'checkbox' && checkBoxes[i].checked == true) {
            var row = checkBoxes[i].parentNode.parentNode;
            // checkeddatapoints.push(row.cells[1].innerHTML);
            key = row.cells[1].innerHTML;
            value = row.cells[2].innerHTML;
            checkeddatapoints[key] = value;
        }
    }
    return checkeddatapoints;
}

function checkAllData(ele) {
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

function checkData(ele) {
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

function getSingleCrawlerBrowseAction(element) {

    // console.log(element);

    var dataInfo = {}
    let dataType = document.getElementById('datatypedropdown').value;
    var $row = $(element).closest("tr");    // Find the row
    if (dataType == 'text') {
        var dataId = $row.find("#dataId").text(); // Find the text
        var data = $row.find("#Data").text(); // Find the text
    }
    else if (dataType == 'audio') {
        var dataId = $row.find("#audioId").text(); // Find the text
        var data = $row.find("#audioFilename").text(); // Find the text
    }
    dataInfo[dataId] = data
    // console.log(dataInfo);

    return dataInfo
}

function createPagination(totalRecords, active=1) {
    let crawledDataCount = Number(document.getElementById('sourcedatacountdropdown').value);
    let paginationEle = '';
    totalPages = Math.ceil(totalRecords/crawledDataCount);
    // console.log(totalPages);
    paginationEle +=  '<div class="btn-group">';
    for (let i=1; i<=totalPages; i++) {
        if (i == active) {
            paginationEle += '<button type="button" class="btn btn-primary" id="'+i+'" onclick="changeCrawlerBrowsePage(this.id)">'+i+'</button>';
        }
        else {
            paginationEle += '<button type="button" class="btn" id="'+i+'" onclick="changeCrawlerBrowsePage(this.id)">'+i+'</button>';
        }
    }
    paginationEle += '</div><br><br>';
    $("#crawlerbrowsepagination").html(paginationEle);
}

function changeCrawlerBrowsePage(pageId) {
    // console.log(pageId);
    let crawlerBrowseInfo = getCrawlerBrowseInfo();
    activePageNumber = Number(pageId);
    crawlerBrowseInfo['pageId'] = Number(pageId);
    $.ajax({
        data : {
          a : JSON.stringify(crawlerBrowseInfo)
        },
        type : 'GET',
        url : '/lifedata/crawlerbrowsechangepage'
      }).done(function(data){
        console.log(data);
        // console.log(data.crawledDataFields, data.crawledData, data.shareMode);
        createCrawlerBrowseTable(data.crawledDataFields,
            data.crawledData,
            data.shareMode,
            data.totalRecords,
            data.dataType);
        // eventsMapping();
        playpauseEvent();
        createPagination(data.totalRecords, data.activePage);
    });
}
