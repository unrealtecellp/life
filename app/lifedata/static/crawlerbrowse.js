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
    ele += '<label for="browsedatadropdowns">Action:&nbsp;</label>'+
            '<select class="custom-select custom-select-sm" id="browsedatadropdowns" style="width: 50%;"></select>&nbsp;&nbsp;&nbsp;&nbsp;';
    ele += '<button type="button" class="btn btn-danger" id="multiplecrawlerdelete"  style="display: inline;">'+
            '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>'+
            ' Delete Multiple Crawler</button>';
    ele += '<button type="button" class="btn btn-success" id="multiplecrawlerrevoke" style="display: none;">'+
            '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'+
            ' Revoke Multiple Crawler</button>';
    $('#browsedatadropdowns').append(ele);
    if (currentUsername === projectOwner) {
        browseActionOptionsList.push('Revoke');
    }
    createSelect2('browsedatadropdowns', browseActionOptionsList, 'Delete');
}

function createCrawlerBrowseTable(crawlerDataFields, crawlerData, shareMode=0) {
    console.log(crawlerData);
    let count = crawlerData.length
    let ele = '';
    let browseActionSelectedOption = '';
    ele += '<p id="totalrecords">Total Records:&nbsp;'+count+'</p>'+
            '<table class="table table-striped " id="myTable">'+
            '<thead>'+
            '<tr>'+
            '<th><input type="checkbox" id="headcheckbox" onchange="checkAllCrawler(this)" name="chk[]" checked/>&nbsp;</th>';
    for (let i=0; i<crawlerDataFields.length; i++) {
        ele += '<th onclick="sortTable('+(i+1)+')">'+crawlerDataFields[i]+'</th>';
    }
    ele += '<th>View</th>';
    if (shareMode >= 4) {
        browseActionSelectedOption = document.getElementById('browsedatadropdowns').value;
        ele += '<th>'+browseActionSelectedOption+'</th>';
    }
    
    ele += '</tr>'+
            '</thead>';
    ele += '<tbody id="myTableBody">';
            // {% for data in sdata %}
    for (let i=0; i<crawlerData.length; i++) {
        aData = crawlerData[i];
        ele += '<tr>'+
                '<td><input type="checkbox" id="lexemecheckbox" onchange="checkCrawler(this)" name="name1" checked /></td>';
        for (let j=0; j<crawlerDataFields.length; j++) {
            let field = crawlerDataFields[j];
            if (field in aData) {
                if (field == 'Crawler File') {
                    ele += '<td id='+field+'>'+
                            '<crawler controls><source src="'+aData[field]+'" type="crawler/wav"></crawler>'+
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
        ele += '<td><button type="button" id="viewcrawler" class="btn btn-primary viewcrawlerclass">'+
                    '<span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span>'+
                    ' View Crawler'+
                    '</button></td>';
        if (browseActionSelectedOption === 'Delete') {
            ele += '<td><button type="button" id="deletecrawler" class="btn btn-danger deletecrawlerclass">'+
                    '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>'+
                    ' Delete Crawler'+
                    '</button></td>';

        }
        else if (browseActionSelectedOption === 'Revoke') {
            ele += '<td><button type="button" id="revokecrawler" class="btn btn-success revokecrawlerclass">'+
                    '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'+
                    ' Revoke Crawler'+
                    '</button></td>';

        }
        ele += '</tr>';
    }
    ele += '</tbody>'+
            '</table>';
    $('#crawlerbrowsetable').html(ele);
}

function createCrawlerBrowse(newData) {
    console.log(newData);
    let sourceIds = newData['sourceIds'];
    let currentUsername = newData['currentUsername']
    let projectOwner = newData['projectOwner']
    let shareInfo = newData['shareInfo']
    let shareMode = shareInfo['sharemode']
    let activeSourceId = shareInfo['activesourceId']
    console.log(activeSourceId)
    let crawlerDataFields = newData['crawlerDataFields']
    let crawlerData = newData['crawlerData']
    createSelect2('sourceidsdropdown', sourceIds, activeSourceId);
    createSelect2('sourcedatacountdropdown', [10, 20, 50], 10)
    if (shareMode >= 4) {
        createBrowseActions(projectOwner, currentUsername);
    }
    createCrawlerBrowseTable(crawlerDataFields, crawlerData, shareMode)
    eventsMapping();
}

function eventsMapping() {
    // change in browse action select
    $("#browsedatadropdowns").change(function() {
        let browseActionSelectedOption = document.getElementById('browsedatadropdowns').value;
        // console.log(browseActionSelectedOption);
        updateCrawlerBrowseTable();
        if (browseActionSelectedOption === 'Delete') {
            document.getElementById('multiplecrawlerrevoke').style.display = "none";
            document.getElementById('multiplecrawlerdelete').style.display = "inline";
        }
        else if (browseActionSelectedOption === 'Revoke') {
            document.getElementById('multiplecrawlerdelete').style.display = "none";
            document.getElementById('multiplecrawlerrevoke').style.display = "inline";
        }
    })
    // change crawler file count to show
    $("#sourcedatacountdropdown").change(function() {
        // console.log(browseActionSelectedOption);
        updateCrawlerBrowseTable();
    })
    // delete single crawler
    $(".deletecrawlerclass").click(function() {
        let crawlerInfo = getSingleCrawlerBrowseAction(this);
        deleteCrawlerFLAG = confirm("Delete This Crawler!!!");
        if(deleteCrawlerFLAG) {
            crawlerBrowseAction(crawlerInfo);
        }
    });
    // delete multiple crawlers
    $("#multiplecrawlerdelete").click(function() {
        crawlers = GetSelected();
        console.log(crawlers);
        deleteCrawlerFLAG = confirm("Delete These Crawlers!!!");
        if(deleteCrawlerFLAG) {
            crawlerBrowseAction(crawlers);
        }
    });
    // revoke single crawler
    $(".revokecrawlerclass").click(function() {
        let crawlerInfo = getSingleCrawlerBrowseAction(this);
        revokeCrawlerFLAG = confirm("Revoke This Crawler!!!");
        if(revokeCrawlerFLAG) {
            crawlerBrowseAction(crawlerInfo);
        }
    });
    // revoke multiple crawlers
    $("#multiplecrawlerrevoke").click(function() {
        crawlers = GetSelected();
        console.log(crawlers);
        revokeCrawlerFLAG = confirm("Revoke These Crawlers!!!");
        if(revokeCrawlerFLAG) {
            crawlerBrowseAction(crawlers);
        }
    });
}

function updateCrawlerBrowseTable() {
    let crawlerBrowseInfo = getCrawlerBrowseInfo();
    $.ajax({
        data : {
          a : JSON.stringify(crawlerBrowseInfo)
        },
        type : 'GET',
        url : '/updatecrawlerbrowsetable'
      }).done(function(data){
        console.log(data.crawlerDataFields, data.crawlerData);
        createCrawlerBrowseTable(data.crawlerDataFields, data.crawlerData);
        eventsMapping();
      });
}

function crawlerBrowseAction(crawlerInfo) {
    let crawlerBrowseInfo = getCrawlerBrowseInfo();
    $.ajax({
        data : {
          a : JSON.stringify({
            "crawlerInfo": crawlerInfo,
            "crawlerBrowseInfo": crawlerBrowseInfo
        })
        },
        type : 'GET',
        url : '/crawlerbrowseaction'
      }).done(function(data){
            window.location.reload();
      });
}

function getCrawlerBrowseInfo() {
    let activeSourceId = document.getElementById('sourceidsdropdown').value;
    let crawlerFilesCount = Number(document.getElementById('sourcedatacountdropdown').value);
    let browseActionSelectedOption = '';
    try {
        browseActionSelectedOption = document.getElementById('browsedatadropdowns').value;
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
        "crawlerFilesCount": crawlerFilesCount,
        "browseActionSelectedOption": browseActionSelectedOption
    }

    return crawlerBrowseInfo
}

function GetSelected() {
    
    //Reference the Table.
    var grid = document.getElementById("myTable");
    
    //Reference the CheckBoxes in Table.
    var checkBoxes = grid.getElementsByTagName("INPUT");
    
    // var checkedcrawlers = [];
    var checkedcrawlers = {};
    //Loop through the CheckBoxes.
    for (var i = 1; i < checkBoxes.length; i++) {
        
        if (checkBoxes[i].type == 'checkbox' && checkBoxes[i].checked == true) {
            var row = checkBoxes[i].parentNode.parentNode;
            // checkedcrawlers.push(row.cells[1].innerHTML);
            key = row.cells[1].innerHTML;
            value = row.cells[2].innerHTML;
            checkedcrawlers[key] = value;
        }
    }
    return checkedcrawlers;
}

function checkAllCrawler(ele) {
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

function checkCrawler(ele) {
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

    var crawlerInfo = {}
    var $row = $(element).closest("tr");    // Find the row
    var crawlerId = $row.find("#crawlerId").text(); // Find the text
    var crawlerFilename = $row.find("#crawlerFilename").text(); // Find the text
    crawlerInfo[crawlerId] = crawlerFilename
    console.log(crawlerInfo);

    return crawlerInfo
}