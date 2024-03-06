var crawlerVideosChannelsId = 0;

function youtubeCrawlerInterface() {
    let ele = '';
    ele += '<div id="formdisplay" style="display: block;">' +
        '<form role="form" method="post" action="/lifedata/youtubecrawler" onsubmit="return runLoader()">';
    
    ele += '<div class="form-group">' +
        '<label for="idyoutubeapikey">Youtube API Key</label>' +
        '<input type="password" class="form-control" id="idyoutubeapikey" placeholder="Youtube API Key" name="youtubeAPIKey" style="width: 55%"  value="AIzaSyDkzGzNgMOPQKEC4A5Y4fM7aRd3AmlvNTc" required>' +
        '</div>';
    
    ele += '<div class="form-group">' +
        '<label for="idyoutubedatatypes">Data Type</label><br>' +
        '<select class="classyoutubedatatypes" id="idyoutubedatatypes" name="youtubeDataType" placeholder="Select the data type that is to be stored" style="width:55%" required multiple="multiple">' +
        '<option value="comments">Comments</option>' +
        '<option value="audio" selected>Audio</option>' +
        '<option value="video">Video</option>' +
        '</select><br>' +
        '</div>';
    
    ele += '<div class="form-group">'+
        '<label for="idyoutubedatafor">Crawl Mode</label><br>'+
        '<select class="classyoutubedatafor" id="idyoutubedatafor" name="youtubeDataFor" style="width:55%" required>' +
        '<option value="" disabled selected>Select the crawl mode</option>'+
        '<option value="videos">Specific Videos</option>'+
        '<option value="channels">Specific Channels</option>'+
        '<option value="topn">Top Videos</option>' +
        '</select><br>'+
        '</div>';
    
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

    ele += '<div class="classtopndiv" id="idtopndiv" style="display: none;">' +
    '<div class="form-group">' +
    '<label for="idyoutubetopnsearchquery">Search Query</label>' +
    '<input type="text" class="form-control" id="idyoutubetopnsearchquery" placeholder="Enter your search query" name="youtubeTopNSearchQuery" style="width: 55%" required>' +
    '</div>' +
    '<div class="form-group">' +
    '<label for="idyoutubetopnsearchtags">Additional Tags, if any</label><br/>' +
    '<select class="classyoutubetopnsearchtags" id="idyoutubetopnsearchtags" name="youtubeTopNSearchTags" style="width:55%" multiple="multiple">' +
    '</select>' +
    '</div>' +
    '<div class="form-group">' +
    '<label for="idyoutubetopnvideocount">Total Videos to crawl from (Max - 50): </label>' +
    '<input type="number" min="1" max="50" class="form-control" id="idyoutubetopnvideocount" placeholder="Total number of videos to crawl" name="youtubeTopNVideoCount" style="width: 55%" required>' +
    '</div>' +
    '<div class="form-group">' +
    '<label for="idyoutubevideolicense">Youtube Video License</label><br>' +
    '<select class="classyoutubevideolicense" id="idyoutubevideolicense" name="youtubeVideoLicense" style="width:55%" required>' +
    '<option value="creativeCommon">Creative Commons</option>' +
    '<option value="youtube">Standard YouTube License</option>' +
    '<option value="any">Any License</option>' +
    '</select><br>' +
    '</div>' +
    '</div>';

        // '<div class="form-group">'+
        // '<label for= "iddatalinks">Videos/Channels Id</label><br>'+
        // '<textarea id="iddatalinks" name="dataLinks" style="width:55%" required rows=5></textarea>'+
        // '</div>';
    ele += '<br>'+
        '<input class="btn btn-lg btn-primary create" id="crawlersubmit" type="submit" value="Crawl">'+
        '</form><br>';
    $('#crawlerinterface').append(ele);

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

}

function crawlerInterface(dataSubSource) {
    console.log(dataSubSource);
    if (dataSubSource === 'youtube') {
        youtubeCrawlerInterface()
    }
}

function createVideosChannelIdInput() {
    let ele = '';
    ele += '<div class="videoschannelsid">'+
            '<div class="form-group">'+
            '<label for="idvideoschannelsid">Add Videos/Channels Id for Data</label>'+
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
    
        fItems += '<div class="col-md-2"><div class="form-group">'+
                    // '<div class="input-group">'+
                    '<select class="form-control" id="idsearchkeywords' + crawlerVideosChannelsId + '" name="searchkeywords_' + crawlerVideosChannelsId + '" multiple="multiple">';
        
        fItems += '</select></div></div>';

        fItems += '<div class="col-md-5"><div class="form-group">'+
                    '<div class="input-group">'+
                    '<select class="form-control" id="idvideoschannelId' + crawlerVideosChannelsId + '" name="videoschannelId_' + crawlerVideosChannelsId + '" multiple="multiple">';
        
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
            allowClear: true
        });
        $('#idvideoschannelId' + crawlerVideosChannelsId).select2({
            placeholder: 'Videos/Channels Ids',
            // data: languages,
            tags: true,
            allowClear: true
        });
    });

    $('#idyoutubedatafor').on('change.select2', function() {
        selectedVal = $('#idyoutubedatafor').val();
        // console.log("Selected Val", selectedVal);
        if (selectedVal === "topn") {
            // $('.classspecificlinksdiv').toggle("slide");
            // $('.classtopndiv').toggle("slide");
            $('.classspecificlinksdiv').css("display", "none");
            $(".classspecificlinksdiv :input").prop("disabled", true);

            $('.classtopndiv').css("display", "block");
            $('.classtopndiv :input').prop("disabled", false);
            // var $drillDown = $("#drilldown");
            
            
            // $('.classtopndiv').display = "block";
            // $('.classspecificlinksdiv').display = "none";
        }
        else if (selectedVal === "videos" || selectedVal === "channels") {
            // $('.classspecificlinksdiv').toggle("slide");
            // $('.classtopndiv').toggle("slide");
            // $('.classspecificlinksdiv').style = "display: block";
            // $('.classtopndiv').style = "display: none";
            // console.log("Selected Val2", selectedVal);
            $('.classtopndiv').css("display", "none");            
            $('.classtopndiv :input').prop("disabled", true);

            $('.classspecificlinksdiv').css("display", "block");
            $(".classspecificlinksdiv :input").prop("disabled", false);
            // var $drillDown = $("#drilldown");
        }
        // document.getElementById('crawlersubmit').disabled = false;
    });

    // $("#crawlersubmit").click(function() {
    //     console.log('123213');
    //     console.log(document.getElementById("loader"));
    //     document.getElementById("loader").style.display = "block";
    // });

}

// remove a translation element
function removeVideosChannelsIdsFields(rid) {
    $(".removecrawlervideoschannelsId"+rid).remove();
}

function runLoader() {
    console.log('123213');
    console.log(document.getElementById("loader"));
    document.getElementById("loader").style.display = "block";
}