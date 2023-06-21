var crawlerVideosChannelsId = 0;

function youtubeCrawlerInterface() {
    let ele = '';
    ele += '<div id="formdisplay" style="display: block;">' +
        '<form role="form" method="post" action="/lifedata/youtubecrawler">';
    ele += '<div class="form-group">'+
        '<label for="idyoutubedatafor">Youtube Data For</label><br>'+
        '<select class="classyoutubedatafor" id="idyoutubedatafor" name="youtubeDataFor" style="width:55%" required>'+
        '<option value="videos">Videos</option>'+
        '<option value="channels">Channels</option>'+
        '</select><br>'+
        '</div>'+

        '<div class="form-group">'+
        '<label for="idyoutubeapikey">Youtube API Key</label>'+
        '<input type="password" class="form-control" id="idyoutubeapikey" placeholder="Youtube API Key" name="youtubeAPIKey" style="width: 55%" required>'+
        '</div>';

    ele += createVideosChannelIdInput();

        // '<div class="form-group">'+
        // '<label for= "iddatalinks">Videos/Channels Id</label><br>'+
        // '<textarea id="iddatalinks" name="dataLinks" style="width:55%" required rows=5></textarea>'+
        // '</div>';
    ele += '<br>'+
        '<input class="btn btn-lg btn-primary create" id="crawlersubmit" type="submit" value="Crawl">'+
        '</form><br>';
    $('#crawlerinterface').append(ele);

    $('.classyoutubedatafor').select2({});

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
        
        var fItems = '<div class="col-md-4"><div class="form-group">'+
                    '<input type="text" class="form-control"'+
                    ' name="videoschannelId_' + crawlerVideosChannelsId + '" placeholder="Videos/Channels Id" required></div></div>';
    
        fItems += '<div class="col-md-3"><div class="form-group">'+
                    '<div class="input-group">'+
                    '<select class="form-control" id="idsearchkeywords' + crawlerVideosChannelsId + '" name="searchkeywords_' + crawlerVideosChannelsId + '" multiple="multiple">';
        
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
    });
}

// remove a translation element
function removeVideosChannelsIdsFields(rid) {
    $(".removecrawlervideoschannelsId"+rid).remove();
}
