function modelsList(models) {
    // console.log(models);
    // models = ['123'];
    $('#myModelPlaygroundListSelect2').select2({
        // tags: true,
        placeholder: 'Select Model Name',
        data: models,
        allowClear: true
    });
    $('#myModelPlaygroundListSelect2').val(models[models.length-1]); // Select the option with a value of '1'
    $('#myModelPlaygroundListSelect2').trigger('change'); // Notify any JS components that the value changed
}

function modelPlaygroundTextAreaForm () {
    
    let ele = '';
    ele += '<label for="myModelPlaygroundTextArea">Text: </label><br />'+
            '<textarea class="form-control" id="myModelPlaygroundTextArea" rows="3" name="myModelPlaygroundTextArea" placeholder="Use newline for new text" onfocus="updateForm(this, \'textarea\')" required></textarea>';

    ele += '<input type="checkbox" id="myModelPlaygroundFileCheckbox" name="myModelPlaygroundFileCheckbox" onchange="updateForm(this, \'file\')"/> '+
    '<label for="myModelPlaygroundFileCheckbox">Upload CSV File :</label><br>';
            
    ele += '<input type="checkbox" id="myModelPlaygroundCrawlerCheckbox" name="myModelPlaygroundCrawlerCheckbox" onchange="updateForm(this, \'crawler\')"/> '+
    '<label for="myModelPlaygroundCrawlerCheckbox">Analyse Youtube</label><br>';
    $('#modelPlaygroundDataForm').html(ele);
}

function modelPlaygroundFileForm () {
    
    let ele = '';
    // ele += '<label for="myModelPlaygroundTextArea">Text: </label><br />'+
    //         '<textarea class="form-control" id="myModelPlaygroundTextArea" rows="3" name="myModelPlaygroundTextArea" placeholder="Use newline for new text" onfocus="updateForm(this, \'textarea\')" required></textarea>';

    ele += '<input type="checkbox" id="myModelPlaygroundFileCheckbox" name="myModelPlaygroundFileCheckbox" onchange="updateForm(this, \'file\')"/ checked> '+
    '<label for="myModelPlaygroundFileCheckbox">Upload CSV File :</label><br>';

    ele += '<input type="file" id="myModelPlaygroundFile" name="myModelPlaygroundFile" accept=".csv" multiple="multiple">'
            
    ele += '<input type="checkbox" id="myModelPlaygroundCrawlerCheckbox" name="myModelPlaygroundCrawlerCheckbox" onchange="updateForm(this, \'crawler\')"/> '+
    '<label for="myModelPlaygroundCrawlerCheckbox">Analyse Youtube</label><br>';
    $('#modelPlaygroundDataForm').html(ele);
}

function modelPlaygroundCrawlerForm () {
    
    let ele = '';
    // ele += '<label for="myModelPlaygroundTextArea">Text: </label><br />'+
    //         '<textarea class="form-control" id="myModelPlaygroundTextArea" rows="3" name="myModelPlaygroundTextArea" placeholder="Use newline for new text" onfocus="updateForm(this, \'textarea\')" required></textarea>';

    ele += '<input type="checkbox" id="myModelPlaygroundFileCheckbox" name="myModelPlaygroundFileCheckbox" onchange="updateForm(this, \'file\')"/> '+
    '<label for="myModelPlaygroundFileCheckbox">Upload CSV File :</label><br>';
            
    ele += '<input type="checkbox" id="myModelPlaygroundCrawlerCheckbox" name="myModelPlaygroundCrawlerCheckbox" onchange="updateForm(this, \'crawler\')"/ checked> '+
    '<label for="myModelPlaygroundCrawlerCheckbox">Analyse Youtube</label><br>';

    ele += '<div id="modelPlaygroundCrawler"></div>'

    $('#modelPlaygroundDataForm').html(ele);

    youtubeCrawlerInterface();
}

function updateForm(checkboxEle, ele) {
    // console.log(ele);
    if (ele == 'file') {
        if (checkboxEle.checked) {
            modelPlaygroundFileForm();
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
    
    ele += '<div class="form-group">' +
        '<label for="idyoutubeapikey">Youtube API Key</label>' +
        '<input type="password" class="form-control" id="idyoutubeapikey" placeholder="Youtube API Key" name="youtubeAPIKey" style="width: 100%" required>' +
        '</div>';
    
    ele += '<br><div class="input-group videoschannelsid">'+
            '<label for="idvideoschannelsid">Add Search Keywords/Video Ids for Data</label>'+
            '<select class="form-control" id="idvideoschannelId" name="videoschannelId" multiple="multiple" style="width: 100%;" required>'+
            '</select>';

    ele += '</div>';

    $('#modelPlaygroundCrawler').append(ele);

    $('#idvideoschannelId').select2({
        placeholder: 'Add Search Keywords/Video Ids for Data',
        // data: languages,
        tags: true,
        allowClear: true,
        maximumSelectionLength: 10
    });
}

function getPrediction() {
    let form_ele = document.getElementById("modelplaygroundformid");
    // const formData = new FormData(submit_span_form_ele, ele);
    const formData = new FormData(form_ele);
    // console.log(formData);
    var object = {};
    formData.forEach(function(value, key){
        // console.log('key: ', key, 'value: ', value, tagSetMetaData);
        if (key in object) {
            object[key].push(value);
        }
        else {
            object[key] = [value];
        }
    });
    // console.log(object);
    $.ajax({
        url: '/lifemodels/models_playground_prediction',
        type: 'POST',
        data: formData,
        contentType: false,
        cache: false,
        processData: false,
        success: function(data) {
            // console.log('Success!');
            let data_info = data.data_info;
            let data_info_size = Object.keys(data_info).length;
            console.log(Object.keys(data_info).length);
            if (data_info_size > 0){
                createChart(data_info);
            }
            else{
                alert('No data to analyse!');
            }
            // window.location.reload();
        },
    });
}

modelPlaygroundTextAreaForm();
