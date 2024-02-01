function modelsList(models) {
    // console.log(models);
    // models = ['123'];
    $('#myModelPlaygroundListSelect2').select2({
        // tags: true,
        placeholder: 'Select Model Name',
        data: models,
        // allowClear: true
    });
    $('#myModelPlaygroundListSelect2').val(models[models.length-1]); // Select the option with a value of '1'
    $('#myModelPlaygroundListSelect2').trigger('change'); // Notify any JS components that the value changed
}

function modelPlaygroundTextAreaForm () {
    
    let ele = '';
    ele += '<label for="myModelPlaygroundTextArea">Text: </label><br />'+
            '<textarea class="form-control" id="myModelPlaygroundTextArea" rows="3" name="myModelPlaygroundTextArea" placeholder="Use newline for new text" onfocus="updateForm(this, \'textarea\')" required></textarea>';

    ele += '<input type="checkbox" id="myModelPlaygroundFileCheckbox" name="myModelPlaygroundFileCheckbox" onchange="updateForm(this, \'file\')"/> '+
    '<label for="myModelPlaygroundFileCheckbox">Upload File (in CSV format) :</label><br>';
            
    ele += '<input type="checkbox" id="myModelPlaygroundCrawlerCheckbox" name="myModelPlaygroundCrawlerCheckbox" onchange="updateForm(this, \'crawler\')"/> '+
    '<label for="myModelPlaygroundCrawlerCheckbox">Crawl Data</label><br>';
    $('#modelPlaygroundDataForm').html(ele);
}

function modelPlaygroundFileForm () {
    
    let ele = '';
    // ele += '<label for="myModelPlaygroundTextArea">Text: </label><br />'+
    //         '<textarea class="form-control" id="myModelPlaygroundTextArea" rows="3" name="myModelPlaygroundTextArea" placeholder="Use newline for new text" onfocus="updateForm(this, \'textarea\')" required></textarea>';

    ele += '<input type="checkbox" id="myModelPlaygroundFileCheckbox" name="myModelPlaygroundFileCheckbox" onchange="updateForm(this, \'file\')"/ checked> '+
    '<label for="myModelPlaygroundFileCheckbox">Upload File (in CSV format) :</label><br>';

    ele += '<input type="file" id="myModelPlaygroundFile" name="myModelPlaygroundFile" accept=".csv">'
            
    ele += '<input type="checkbox" id="myModelPlaygroundCrawlerCheckbox" name="myModelPlaygroundCrawlerCheckbox" onchange="updateForm(this, \'crawler\')"/> '+
    '<label for="myModelPlaygroundCrawlerCheckbox">Crawl Data</label><br>';
    $('#modelPlaygroundDataForm').html(ele);
}

function modelPlaygroundCrawlerForm () {
    
    let ele = '';
    // ele += '<label for="myModelPlaygroundTextArea">Text: </label><br />'+
    //         '<textarea class="form-control" id="myModelPlaygroundTextArea" rows="3" name="myModelPlaygroundTextArea" placeholder="Use newline for new text" onfocus="updateForm(this, \'textarea\')" required></textarea>';

    ele += '<input type="checkbox" id="myModelPlaygroundFileCheckbox" name="myModelPlaygroundFileCheckbox" onchange="updateForm(this, \'file\')"/> '+
    '<label for="myModelPlaygroundFileCheckbox">Upload File (in CSV format) :</label><br>';
            
    ele += '<input type="checkbox" id="myModelPlaygroundCrawlerCheckbox" name="myModelPlaygroundCrawlerCheckbox" onchange="updateForm(this, \'crawler\')"/ checked> '+
    '<label for="myModelPlaygroundCrawlerCheckbox">Crawl Data</label><br>';

    ele += '<div id="modelPlaygroundCrawler"></div>'

    $('#modelPlaygroundDataForm').html(ele);

    youtubeCrawlerInterface();
}

function updateForm(checkboxEle, ele) {
    console.log(ele);
    if (ele == 'file') {
        if (checkboxEle.checked) {
            modelPlaygroundFileForm();
            // document.getElementById('modelPlaygroundFile').style.display = 'block';
            // document.getElementById('myModelPlaygroundFile').required = true;
            // document.getElementById('myModelPlaygroundFile').disabled = false;

            // document.getElementById('modelPlaygroundTextArea').style.display = 'none';
            // document.getElementById('myModelPlaygroundTextArea').required = false;
            // document.getElementById('myModelPlaygroundTextArea').disabled = true;

            // document.getElementById('modelPlaygroundCrawler').style.display = 'none';
            // document.getElementById('myModelPlaygroundCrawler').required = false;
            // document.getElementById('myModelPlaygroundCrawler').disabled = true;
        }
        else {
            modelPlaygroundTextAreaForm();
        }
    }
    // else if (ele == 'textarea') {
    //     // location.reload(true);
    //     modelPlaygroundTextAreaForm();
    // }
    else if (ele == 'crawler') {
        if (checkboxEle.checked) {
            modelPlaygroundCrawlerForm();
            // document.getElementById('modelPlaygroundTextArea').style.display = 'none';
            // document.getElementById('myModelPlaygroundTextArea').required = false;
            // document.getElementById('myModelPlaygroundTextArea').disabled = true;

            // document.getElementById('modelPlaygroundFile').style.display = 'none';
            // document.getElementById('myModelPlaygroundFile').required = false;
            // document.getElementById('myModelPlaygroundFile').disabled = true;

            // document.getElementById('modelPlaygroundCrawler').style.display = 'block';
            // document.getElementById('myModelPlaygroundCrawler').required = true;
            // document.getElementById('myModelPlaygroundCrawler').disabled = false;
        }
        else {
            modelPlaygroundTextAreaForm();
        }
    }

}

var crawlerVideosChannelsId = 0;

function youtubeCrawlerInterface() {
    let ele = '';
    ele += '<div id="formdisplay" style="display: block;">' ;
    // ele += '<form role="form" method="post" action="/lifedata/youtubecrawler">';
    
    ele += '<div class="form-group">' +
        '<label for="idyoutubeapikey">Youtube API Key</label>' +
        '<input type="password" class="form-control" id="idyoutubeapikey" placeholder="Youtube API Key" name="youtubeAPIKey" style="width: 100%" required>' +
        '</div>';
    
    // ele += '<div class="form-group">' +
    //     '<label for="idyoutubedatatypes">Data Type</label><br>' +
    //     '<select class="classyoutubedatatypes" id="idyoutubedatatypes" name="youtubeDataType" placeholder="Select the data type that is to be stored" style="width:55%" required multiple="multiple">' +
    //     '<option value="comments">Comments</option>' +
    //     '<option value="audio">Audio</option>' +
    //     '<option value="video">Video</option>' +
    //     '</select><br>' +
    //     '</div>';
    
    // ele += '<div class="form-group">'+
    //     '<label for="idyoutubedatafor">Crawl Mode</label><br>'+
    //     '<select class="classyoutubedatafor" id="idyoutubedatafor" name="youtubeDataFor" style="width:55%" required>' +
    //     '<option value="" disabled selected>Select the crawl mode</option>'+
    //     '<option value="videos">Specific Videos</option>'+
    //     '<option value="channels">Specific Channels</option>'+
    //     '<option value="topn">Top Videos</option>' +
    //     '</select><br>'+
    //     '</div>';
    
    // ele += '<div class="form-group">' +
    //     '<label for="idyoutubecrawlmode">Crawl Mode</label><br>' +
    //     '<select class="classyoutubecrawlmode" id="idyoutubecrawlmode" name="youtubeCrawlMode" style="width:55%" required>' +
    //     '<option value="topn">Top Videos</option>' +
    //     '<option value="specificlinks">Specific Videos/Channels</option>' +
    //     '</select><br>' +
    //     '</div>';

    
    ele += '<div class="classspecificlinksdiv" id="idspecificlinksdiv" style="display: none;">'
    
    ele += createVideosChannelIdInput();

    ele += '</div>';

    // ele += '<div class="classtopndiv" id="idtopndiv" style="display: none;">' +
    // '<div class="form-group">' +
    // '<label for="idyoutubetopnsearchquery">Search Query</label>' +
    // '<input type="text" class="form-control" id="idyoutubetopnsearchquery" placeholder="Enter your search query" name="youtubeTopNSearchQuery" style="width: 55%" required>' +
    // '</div>' +
    // '<div class="form-group">' +
    // '<label for="idyoutubetopnsearchtags">Additional Tags, if any</label><br/>' +
    // '<select class="classyoutubetopnsearchtags" id="idyoutubetopnsearchtags" name="youtubeTopNSearchTags" style="width:55%" multiple="multiple">' +
    // '</select>' +
    // '</div>' +
    // '<div class="form-group">' +
    // '<label for="idyoutubetopnvideocount">Total Videos to crawl from (Max - 50): </label>' +
    // '<input type="number" min="1" max="50" class="form-control" id="idyoutubetopnvideocount" placeholder="Total number of videos to crawl" name="youtubeTopNVideoCount" style="width: 55%" required>' +
    // '</div>' +
    // '<div class="form-group">' +
    // '<label for="idyoutubevideolicense">Youtube Video License</label><br>' +
    // '<select class="classyoutubevideolicense" id="idyoutubevideolicense" name="youtubeVideoLicense" style="width:55%" required>' +
    // '<option value="creativeCommon">Creative Commons</option>' +
    // '<option value="youtube">Standard YouTube License</option>' +
    // '<option value="any">Any License</option>' +
    // '</select><br>' +
    // '</div>' +
    // '</div>';

        // '<div class="form-group">'+
        // '<label for= "iddatalinks">Videos/Channels Id</label><br>'+
        // '<textarea id="iddatalinks" name="dataLinks" style="width:55%" required rows=5></textarea>'+
        // '</div>';
    // ele += '<br>'+
    //     '<input class="btn btn-lg btn-primary create" id="crawlersubmit" type="submit" value="Crawl">'+
    //     '</form><br>';
    $('#modelPlaygroundCrawler').append(ele);

    $('.classyoutubedatafor').select2({});

    $('.classyoutubedatatypes').select2({
        placeholder: 'Select all data types to crawl',
        allowClear: true
    });

    // $('classyoutubecrawlmode').select2({});

    $('.classyoutubevideolicense').select2({});

    $('.classyoutubetopnsearchtags').select2({
        placeholder: 'Additional Tags for Metadata',
        tags: true,
        allowClear: true
    });


    crawlerInterfaceEvents();
    $('.classspecificlinksdiv').css("display", "block");
    $(".classspecificlinksdiv :input").prop("disabled", false);

}

function createVideosChannelIdInput() {
    let ele = '';
    ele += '<div class="videoschannelsid">'+
            '<div class="form-group">'+
            '<label for="idvideoschannelsid">Add Videos Id for Data</label>'+
            '</div>'+
            '<div class="form-group">'+
            '<button class="btn btn-success" type="button" id="addVideosChannelIdInput">'+
            '<span class="glyphicon glyphicon-plus" aria-hidden="true"></span>'+
            '</button>'+
            '</div></div>';

    return ele
}

function crawlerInterfaceEvents() {
    $("#addVideosChannelIdInput").click(function(){
        crawlerVideosChannelsId++;
    
        var drow = '<div class="row removecrawlervideoschannelsId' + crawlerVideosChannelsId + '">';
        
        var fItems = '';
        
        // fItems += '<div class="col-md-4"><div class="form-group">'+
        //             '<input type="text" class="form-control"'+
        //             ' name="videoschannelId_' + crawlerVideosChannelsId + '" placeholder="Videos/Channels Id" required></div></div>';
    
        // fItems += '<div class="col-md-6"><div class="form-group">'+
        //             // '<div class="input-group">'+
        //             '<select class="form-control" id="idsearchkeywords' + crawlerVideosChannelsId + '" name="searchkeywords_' + crawlerVideosChannelsId + '" multiple="multiple">';
        
        // fItems += '</select></div></div>';

        fItems += '<div class="col-md-12"><div class="form-group">'+
                    '<div class="input-group">'+
                    '<select class="form-control" id="idvideoschannelId' + crawlerVideosChannelsId + '" name="videoschannelId_' + crawlerVideosChannelsId + '" multiple="multiple" style="width: 100%;">';
        
        fItems += '</select>';
    
        fItems += '<div class="input-group-btn">'+
                    '<button class="btn btn-danger" type="button" onclick="removeVideosChannelsIdsFields('+ crawlerVideosChannelsId +');">'+
                    '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></div></div></div></div>';
    
        drow += fItems;
        drow += '</div>'
        $(".videoschannelsid").append(drow);
        $('#idsearchkeywords' + crawlerVideosChannelsId).select2({
            placeholder: 'Search Keywords',
            // data: languages,
            tags: true,
            allowClear: true,
            maximumSelectionLength: 5
        });
        $('#idvideoschannelId' + crawlerVideosChannelsId).select2({
            placeholder: 'Videos/Channels Ids',
            // data: languages,
            tags: true,
            allowClear: true,
            maximumSelectionLength: 5
        });
    });

    // $('#idyoutubedatafor').on('change.select2', function() {
    //     selectedVal = $('#idyoutubedatafor').val();
    //     // console.log("Selected Val", selectedVal);
    //     if (selectedVal === "topn") {
    //         // $('.classspecificlinksdiv').toggle("slide");
    //         // $('.classtopndiv').toggle("slide");
    //         $('.classspecificlinksdiv').css("display", "none");
    //         $(".classspecificlinksdiv :input").prop("disabled", true);

    //         $('.classtopndiv').css("display", "block");
    //         $('.classtopndiv :input').prop("disabled", false);
    //         // var $drillDown = $("#drilldown");
            
            
    //         // $('.classtopndiv').display = "block";
    //         // $('.classspecificlinksdiv').display = "none";
    //     }
    //     else if (selectedVal === "videos" || selectedVal === "channels") {
    //         // $('.classspecificlinksdiv').toggle("slide");
    //         // $('.classtopndiv').toggle("slide");
    //         // $('.classspecificlinksdiv').style = "display: block";
    //         // $('.classtopndiv').style = "display: none";
    //         // console.log("Selected Val2", selectedVal);
    //         $('.classtopndiv').css("display", "none");            
    //         $('.classtopndiv :input').prop("disabled", true);

    //         $('.classspecificlinksdiv').css("display", "block");
    //         $(".classspecificlinksdiv :input").prop("disabled", false);
    //         // var $drillDown = $("#drilldown");
    //     }
    // });


}

// remove a translation element
function removeVideosChannelsIdsFields(rid) {
    $(".removecrawlervideoschannelsId"+rid).remove();
}

modelPlaygroundTextAreaForm();
