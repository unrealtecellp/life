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
        '<input type="text" class="form-control" id="idyoutubeapikey" placeholder="Youtube API Key" name="youtubeAPIKey" style="width: 55%" required>'+
        '</div>'+

        '<div class="form-group">'+
        '<label for= "iddatalinks">Videos/Channels Id</label><br>'+
        '<textarea id="iddatalinks" name="dataLinks" style="width:55%" required rows=5></textarea>'+
        '</div>';
    ele += '<br>'+
        '<input class="btn btn-lg btn-primary create" id="crawlersubmit" type="submit" value="Crawl">'+
        '</form><br>';
    $('#crawlerinterface').append(ele);

    $('.classyoutubedatafor').select2({});

}

function crawlerInterface(dataSubSource) {
    console.log(dataSubSource);
    if (dataSubSource === 'youtube') {
        youtubeCrawlerInterface()
    }

}