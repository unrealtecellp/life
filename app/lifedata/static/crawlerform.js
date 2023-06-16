$("#datacrawlbtn").click(function() {
    console.log('crawler')
    var x = document.getElementById("crawldataform");
    var y = document.getElementById("dataform");;
    var z = '';
    hidedisplaydiv(x, y, z)
});

function crawlDataForm() {
    let project_info = '';
    let sourceinpt = '';
    let subsourceinpt = '';
    project_info += '<div id="formdisplay" style="display: block;">' +
        '<form role="form" method="post" action="/lifedata/crawler">';
    project_info += '<div class="form-group">'+
        '<label for="idcrawlprojecttype">Project Type</label><br>'+
        '<select class="crawldataprojecttype" id="idcrawlprojecttype" name="projectType" style="width:55%" required>'+
        '<option value="crawling">Crawling</option>'+
        '</select><br>'+
        '</div>'+

        '<div class="form-group">'+
        '<label for="idprojectname">Project Name</label>'+
        '<input type="text" class="form-control" id="idprojectname" placeholder="Project Name" name="projectname" style="width: 55%" required>'+
        '</div>'+

        '<div class="form-group">'+
        '<label for= "idabout">About the Project</label><br>'+
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
    project_info += sourceinpt;
    project_info += '<br>'+
        '<input class="btn btn-lg btn-primary create" id="crawldataformsubmit" type="submit" value="Create Form">'+
        '</form><br>';
    $('#crawldataform').append(project_info);

    $('.crawldataprojecttype').select2({});
    $('.datasourceclass').select2({});
    $.getJSON('/lifedata/datasubsource', {
    }, function(data) {
        dataSubSource = data.dataSubSource;
        console.log(dataSubSource)
        $('.datasubsourceclass').select2({
            data: dataSubSource
        });
    });
}

crawlDataForm();
