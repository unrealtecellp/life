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
        '<label for="idyoutubeapikey">Project Name</label>'+
        '<input type="text" class="form-control" id="idyoutubeapikey" placeholder="Youtube API Key" name="youtubeAPIKey" style="width: 55%" required>'+
        '</div>'+

        '<div class="form-group">'+
        '<label for= "id">About the Project</label><br>'+
        '<textarea id="idabout" name="aboutproject" style="width:55%" required></textarea>'+
        '</div>';
    sourceinpt += '<div class="form-group">' +
        '<label for="iddatasource">Data Source </label> <br>' +
        '<select class="datasourceclass" id="iddatasource" name="datasource" style="width:55%" >'+
        '<option value="internet">Internet</option>'+
        '</select><br>' +
        '</div>';
    subsourceinpt += '<div id="idsubsourcediv" style="display: block;">' +
        '<div class="form-group">' +
        '<label for="iddatasubsource">Data Sub Source </label> <br>' +
        '<select class="datasubsourceclass" id="iddatasubsource" name="datasubsource" style="width:55%" >' +
        '</select><br>' +
        '</div>';
    // subsourceinpt += '<div id="idytsubsourcediv" style="display: block;">' +
    //     '<div class="form-group">' +
    //     '<label class="col-form-label">Youtube Channel Name</label><br>' +
    //     '<input type="text" class="form-control" id="idytchannelname" name="ytchannelname" placeholder="--Youtube Channel Name--" style="width:55%;">' +
    //     '</div>' +
    //     '<div class="form-group">' +
    //     '<label class="col-form-label">Youtube Channel URL</label><br>' +
    //     '<input type="url" class="form-control" id="idytchannelurl" name="ytchannelurl" placeholder="--Youtube Channel URL--" style="width:55%;">' +
    //     '</div>' +
    //     '</div>';
    subsourceinpt += '</div>';
    sourceinpt += subsourceinpt;
    ele += sourceinpt;
    ele += '<br>'+
        '<input class="btn btn-lg btn-primary create" id="crawldataformsubmit" type="submit" value="Create Form">'+
        '</form><br>';
    $('#crawldataform').append(ele);

    $('.classyoutubedatafor').select2({});

}

function crawlerInterface(dataSubSource) {
    console.log(dataSubSource);
    if (dataSubSource === 'youtube') {
        youtubeCrawlerInterface()
    }

}