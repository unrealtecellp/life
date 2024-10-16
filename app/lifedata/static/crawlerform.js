var crawlerLanguageField = 1;

$("#datacrawlbtn").click(function() {
    // console.log('crawler')
    var x = document.getElementById("crawldataform");
    var y = document.getElementById("dataform");;
    var z = '';
    hidedisplaydiv(x, y, z)
});

function createCrawlerFormLangScript() {
    let ele = '';
    let oneLangScript = '';
    ele += '<div class="crawlerlanguage">'+
            '<div class="form-group">'+
            '<label for="idcrawlerlanguage">Add Languages and Scripts for Data</label>'+
            '</div>'+
            '<div class="form-group">'+
            '<button class="btn btn-success" type="button" id="addCrawlerLanguageField">'+
            '<span class="glyphicon glyphicon-plus" aria-hidden="true"></span>'+
            '</button>'+
            '</div>';
    oneLangScript += '<div class="row">'+
                    '<div class="col-md-3"><div class="form-group">'+
                    '<select class="form-control" id="idcrawlerlanguage' + crawlerLanguageField + '" name="crawlerlanguage" required style="width:100%">'+
                    '</select></div></div>'+
                    '<div class="col-md-3"><div class="form-group">'+
                    '<select class="form-control" id="idcrawlerscript' + crawlerLanguageField + '" name="crawlerscript" required style="width:100%">'+
                    '</select></div></div>';
    ele += oneLangScript;
    ele += '</div></div>';

    return ele
}

function crawlDataForm() {
    let project_info = '';
    let sourceinpt = '';
    let subsourceinpt = '';
    let langScript = '';
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
        '<span id="projectnameexist"  style="display: none; color: red;">The Project Name already exist.</span>'+
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
    
    subsourceinpt += '</div>';
    sourceinpt += subsourceinpt;
    project_info += sourceinpt;
    langScript = createCrawlerFormLangScript();
    // console.log(langScript);
    project_info += langScript;
    project_info += '<br>'+
        '<input class="btn btn-lg btn-primary create" id="crawldataformsubmit" type="submit" value="Create Form">'+
        '</form><br>';
    $('#crawldataform').append(project_info);

    $('.crawldataprojecttype').select2({});
    $('.datasourceclass').select2({});
    $('.datasubsourceclass').select2({
      data: getJsonfileData('crawler_type'),
    });
    $('#idcrawlerlanguage' + crawlerLanguageField).select2({
        placeholder: 'Data Language',
        data: getJsonfileData('languages'),
        // allowClear: true
    });
    $('#idcrawlerscript' + crawlerLanguageField).select2({
        placeholder: 'Data Script',
        data: getJsonfileData('scripts'),
        // allowClear: true
    });

    crawlerFormEvents();
}

function crawlerFormEvents() {
    // language script events
    $("#addCrawlerLanguageField").click(function(){
        crawlerLanguageField++;
    
        var drow = '<div class="row removecrawlerlanguagefield' + crawlerLanguageField + '">';
    
        var fItems = '<div class="col-md-3"><div class="form-group">'+
                    '<select class="form-control" id="idcrawlerlanguage' + crawlerLanguageField + '" name="crawlerlanguage" required>';
        
        fItems += '</select></div></div>';
    
        fItems += '<div class="col-md-3"><div class="form-group">'+
                    '<div class="input-group">'+
                    '<select class="form-control" id="idcrawlerscript' + crawlerLanguageField + '" name="crawlerscript" required>';
        
        fItems += '</select>';
    
        fItems += '<div class="input-group-btn">'+
                    '<button class="btn btn-danger" type="button" onclick="removeCrawlerLanguageFields('+ crawlerLanguageField +');">'+
                    '<span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button></div></div></div></div>';
    
        drow += fItems;
        drow += '</div>'
        $(".crawlerlanguage").append(drow);
        $('#idcrawlerlanguage' + crawlerLanguageField).select2({
            placeholder: 'Data Language',
            data: languages,
            // allowClear: true
        });
        $('#idcrawlerscript' + crawlerLanguageField).select2({
            placeholder: 'Data Script',
            data: scripts,
            // allowClear: true
        });
    });
}

// remove a translation element
function removeCrawlerLanguageFields(rid) {
    $(".removecrawlerlanguagefield"+rid).remove();
}

crawlDataForm();
