function createDatasetBrowse(
    projectDataFields
) {
    console.log(projectDataFields);
    let count = projectDataFields.length;
    let ele = '';
    // ele += '<p id="actualtotalrecords">Total Records:&nbsp;'+totalRecords+'</p>';
    ele += '<div class="col">';
    ele += '<strong><p id="totalrecords" style="display:inline">Showing:&nbsp;' + count + ' Datasets</p></strong>';
    ele += '<div class="pull-right">' +
        '<input id="myInput" type="text" placeholder="Search">'
    '</div>';
    ele += '</div>';
    ele += '<hr>';
    ele += '<table class="table table-striped " id="myTable">' +
        '<thead><tr>' +
        '<th> Name </th>' +
        '<th> Language(s) </th>' +
        '<th> Created by </th>' +
        '<th> Contributors </th>' +
        '<th> About </th>' +
        '<th> Transcriptions </th>' +
        '<th> Translations </th>' +
        '<th> Interlinear Gloss </th>' +
        '<th> License </th>' +
        '<th> Contact </th>' +
        '<th> Explore </th>' +
        '</tr></thead>';

    ele += '<tbody>';
    for (const [project, projectDetails] of Object.entries(projectDataFields)) {
        // console.log(audioDataFields[i]);
        ele += '<tr>';
        ele += '<td>' + project + '</td>';

        projectInfo = projectDetails["details"];
        projectType = projectInfo["projectType"];
        aboutProject = projectInfo["aboutproject"];
        projectOwner = projectInfo["projectOwner"];
        projectContributors = projectInfo["sharedwith"];

        if ("projectLicense" in projectInfo) {
            projectLicense = projectInfo["projectLicense"];
        }
        else {
            projectLicense = '<p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><span property="dct:title">' + project + '</span> by <span property="cc:attributionName">' + projectOwner + ' and their collaborators </span> is licensed under <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">CC BY-NC-SA 4.0<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/nc.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/sa.svg?ref=chooser-v1" alt=""></a></p> ';
        }

        projectForm = projectDetails["form"];

        if ("Audio Language" in projectForm) {
            projectAudio = projectForm["Audio Language"][1];
            transcription = projectForm["Transcription"][1];
            translation = projectForm["Translation"][1];
            gloss = projectForm["Interlinear Gloss"][1];
        }
        else if ("Sentence Language" in projectForm) {
            projectAudio = projectForm["Sentence Language"];
            if ("Transcription Script" in projectForm) {
                transcription = projectForm["Transcription Script"];
            }
            else {
                transcription = [];
            }
            if ("Translation Language" in projectForm) {
                translation = projectForm["Translation Language"];
            }
            else {
                translation = [];
            }
            gloss = [];
        }

        ele += '<td>' + projectAudio + '</td>';
        ele += '<td>' + projectOwner + '</td>';
        ele += '<td>' + projectContributors + '</td>';
        ele += '<td>' + aboutProject + '</td>';
        ele += '<td>' + transcription + '</td>';
        ele += '<td>' + translation + '</td>';
        ele += '<td>' + gloss + '</td>';
        ele += '<td>' + projectLicense + '</td>';
        ele += '<td><a href="mailto:unreal.tece@gmail.com">Send email</a>';

        ele += '<td><button type="button" id="viewdataset" class="btn btn-primary viewdatasetclass">' +
            '<span class="glyphicon glyphicon-new-window" aria-hidden="true"></span>' +
            // ' View Audio'+
            '</button></td>';

        ele += '</tr>';
    }

    ele += '</tbody>' +
        '</table>';
    $('#datasetbrowse').html(ele);
}