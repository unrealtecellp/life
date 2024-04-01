function generateDownloadForm(shareinfo, transcriptionsBy, activeTranscriptionBy, projectName, audioIds={}) {
    // console.log('GenDown Share info', shareinfo)
    // console.log('GenDown Transc by', transcriptionsBy)
    // console.log('GenDown Active Transc by', activeTranscriptionBy)
    // console.log('Audio IDs empty', $.isEmptyObject(audioIds), audioIds)
    var downloadModal = ''

    downloadModal += '<div class="modal fade" id="myDownloadTranscriptionModal" tabindex="-1" role="dialog" aria-labelledby="myDownloadTranscriptionModalLabel">' +
        '<div class="modal-dialog modal-lg" role="document">' +
        '<div class="modal-content">' +
        '<div class="modal-header">' +
        '<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>';
    downloadModal += '<h4 class="modal-title" id="myDownloadTranscriptionModalLabel">Project Name:' + projectName + '</h4>';
    downloadModal += '</div>';

    downloadModal += '<div class="modal-body" id="idtranscriptiondownloadform">';
    downloadModal += '<form name="downloadtranscriptions" id="iddownloadtranscriptionsform" action="/download/downloadtranscriptions" method="POST" enctype="multipart/form-data">';
    downloadModal += '<div class="form-group classaudioidsdiv" id = "idaudioidsdiv" style="display: block">' +
        '<h4>File Names:</h4>';
    downloadModal += '<select class="custom-select custom-select-sm classaudioids" id="idaudioids" name="audioIds" multiple="multiple" style="width:90%" readonly>';
    // if ($.isEmptyObject(audioIds)) {
    //     // <input type="text" id="idaudioids" name="audioIds" value="all" readonly />
    //     downloadModal += '<option value = "" selected> * (All Files) </option>';
    // }
    // else {
        // '<label for="idaudioids">Download Files: </label>' +        
        for (const audioId in audioIds) {
            downloadModal += '<option value = "' + audioId + '" selected>' + audioIds[audioId] + '</option>';
        }
    // }
    downloadModal += '</select>';
    downloadModal += '</div>'+
        '<hr/>';
        
    
    
        downloadModal += '<div id="idjsondownloads" class="classjsondownloads bg-secondary">' +
            '<h4>LiFE Data Downloads:</h4>';
    if ("sharelatestchecked" in shareinfo || ('sharelatestchecked' in shareinfo && shareinfo['sharelatestchecked'] == "true")) {
        downloadModal += '<div class="btn-group" role="group">' +
            '<button type="button" id="lifejson" class="btn btn-info">' +
            'LiFE JSON <span class="glyphicon glyphicon-download-alt" aria-hidden="true"></span>' +
            '</button>' +
            '</div>' +
            '<div class="btn-group" role="group">' +
            '<button type="button" id="lifejsonaudio" class="btn btn-warning">' +
            'LiFE JSON+Audio <span class="glyphicon glyphicon-download-alt" aria-hidden="true"></span>' +
            '</button>' +
            '</div>';
    }
    downloadModal += '<div class="btn-group" role="group">' +
            '<button type="button" id="onlyaudio" class="btn btn-success">' +
            'Sliced Audio <span class="glyphicon glyphicon-download-alt" aria-hidden="true"></span>' +
            '</button>' +
            '</div>';
    downloadModal += '</div>' +
            '<br />' +
            '<hr/>';
    

    // downloadModal += '<div class="btn-group" role="group">' +
    //     '<button type="button" id="myjson" class="btn btn-success">' +
    //     'My JSON<span class="glyphicon glyphicon-download-alt" aria-hidden="true"></span>' +
    //     '</button>' +
    //     '</div>';
    
    
    downloadModal += '<div id="idcustomdownloads" class="classcustomownloads">' +
        '<h4>Custom Downloads: </h4>' +
        '<div class="input-group col-md-12 upload" id="downloadformat-divid">' +
        'Download: ' +
        '<input type="checkbox" id="downloadparameters-singletranscriptionsid" name="singleTranscriptions" checked> ' +
        '<label for="downloadparameters-singletranscriptionsid">Sliced Transcriptions</label>  ' +
        '<input type="checkbox" id="downloadparameters-includeaudioid" name="includeAudio"> ' +
        '<label for="downloadparameters-includeaudioid">Sliced Audios</label>  ' +
        '<input type="checkbox" id="downloadparameters-mergetranscriptionsid" name="mergeTranscriptions">  ' +
        '<label for="downloadparameters-mergetranscriptionsid">Merged Transcriptions</label><br/>' +
        '<label for="idtranscriptionbydropdown">By: </label> ' +
        '<select class="custom-select custom-select-sm classtranscriptionbydropdown" id="idtranscriptionbydropdown" name="transcriptionBy" style="width:30%" required>';
    
    downloadModal += '<option value = "' +activeTranscriptionBy +'" selected>' + activeTranscriptionBy + '</option>';

    if ("sharelatestchecked" in shareinfo || ('sharelatestchecked' in shareinfo && shareinfo['sharelatestchecked'] == "true")) {
        for (const d of transcriptionsBy) {
            if (d != activeTranscriptionBy) {
                downloadModal += '<option value = "' +d +'">' + d + '</option>';
            }
        }
    }

    downloadModal += '</select><br /><br />';

    downloadModal += '<label for="iddownloadformatdropdown">As: </label> ' +
        '<select class="custom-select custom-select-sm classdownloadformatdropdown" id="iddownloadformatdropdown" name="downloadFormat" style="width:30%" required>' +
        '</select>' +
        '<br/><br/>';
    
    downloadModal += 'Download Options:' +
              '<input type="checkbox" id="downloadparameters-mergeintervalsid" name="mergeIntervals"> ' + 
        '<label for="downloadparameters-mergeintervalsid">Merge Same Intervals</label>  ';
    
    downloadModal += '<input type="checkbox" id="downloadparameters-retainfilenameid" name="retainFilename"> ' +
        '<label for="downloadparameters-retainfilenameid">Retain Original Filename</label><br></br>';
    
    downloadModal += '<label for="downloadparameters-silencetagid">Tag for Silence: </label> ' +
        '<input type="text" name="silenceTag" id="downloadparameters-silencetagid" value="0"><br/><br/>';
    
    downloadModal += '</div>';

    downloadModal += '<div class="btn-group" role="group">' +
        '<button type="submit" id="iddownloadtranscriptionsbutton" class="btn btn-primary">' +
        'Transcriptions <span class="glyphicon glyphicon-download-alt" aria-hidden="true"></span>' +
        '</button>' +
        '</div>';
    
    downloadModal += '</div>';
    downloadModal += '</br>';
    downloadModal += '</form>';
    downloadModal += '</div>';

    downloadModal += '<div class="modal-footer">' +
        '<button type="button" class="btn btn-danger" data-dismiss="modal">Close</button>' +
        '</div>';
    
    downloadModal += '</div>';
    downloadModal += '</div>';
    downloadModal += '</div>';
    

    $('#idTranscriptionDownloadModal').html(downloadModal);

    downloadModalSelect2();
}

function downloadModalSelect2() {
    $('.classdownloadformatdropdown').select2({
            // tags: true,
            placeholder: 'Transcription Download Format',
            data: downloadFormats,
            // allowClear: true
            // sorter: false
    });
    $('.classtranscriptionbydropdown').select2({
            // tags: true,
            placeholder: 'Transcription By',
            // data: transcriptionBy,
            // allowClear: true
            // sorter: false
    });
    $('.classaudioids').select2({
        placeholder: '* (All files will be downloaded)',
    });
}

// $(document).ready(function () {
//     $("#iddownloadtranscriptionsbutton").click(function () {
//         console.log('Download button');
//         var $form = $(this);
//         var url = $form.attr("action");
//         console.log('Form', '$form', url);
//         // $("#iddownloadtranscriptionsform").submit();
//     })
// })

$(document).ready(function () {
    $("#iddownloadtranscriptionsform").on("submit", function (event) {
        event.preventDefault();
        console.log('Download button');
        var $form = $(this);
        var url = $form.attr("action");
        var formData = new FormData(document.querySelector("#iddownloadtranscriptionsform"));
        console.log("Form data", formData, formData.get("downloadFormat"));
        // console.log("Audio IDS", audioIds);
        $.ajax({
            url: '/download/downloadtranscriptions',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                let cur_location = window.location.href;
                console.log("Location", cur_location);
                if (response != "0") {
                    if (cur_location.includes("lifedata/transcription/home")) {
                        window.location.href = window.location.href.replace("lifedata/transcription/home", "download/tgdownloader");
                    }
                    else if (cur_location.includes("lifedata/transcription/audiobrowse")) {
                        window.location.href = window.location.href.replace("lifedata/transcription/audiobrowse", "download/tgdownloader");
                    }
                    else if (cur_location.includes("enternewsentences")) {
                        window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                    }
                    else if (cur_location.includes("audiobrowse")) {
                        window.location.href = window.location.href.replace("audiobrowse", "download/tgdownloader");
                    }
                }
                else {
                    window.location.reload();
                }
                // console.info(response);
            }
        });
        // $.post(url,
        //     {
        //     data: formData
        //     }
        // )
            // .done(function( data ) {
            // window.location.reload();
            // });

        // console.log('Form', $form, url);
        
    })
})

// $("#myDownloadTranscriptionModal").click(function () {
    
// })

$(document).ready(function () {
    $("#onlyaudio").click(function () {
        downloadFormat = "onlyaudio";
        audioIds = $('#idaudioids').val();
        console.log("Audio IDS", audioIds);
        send_details = { "downloadFormat": downloadFormat, "includeAudio": "on", "audioIds": audioIds};
        console.log("Sending request from onlyaudio");
        // send_details = new FormData(document.querySelector("#iddownloadtranscriptionsform"));
        // alert(downloadFormat)
        //JSON.stringify(send_details)
        $.post("/download/downloadtranscriptions", {
            formDataLifeJSON: JSON.stringify(send_details)
        })
            .success(function (response) {
            // window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
            //     window.location.href = window.location.href.replace("audiobrowse", "download/tgdownloader");
                let cur_location = window.location.href;
                console.log("Location", cur_location);
                if (response != "0") {
                    if (cur_location.includes("lifedata/transcription/home")) {
                        window.location.href = window.location.href.replace("lifedata/transcription/home", "download/tgdownloader");
                    }
                    else if (cur_location.includes("lifedata/transcription/audiobrowse")) {
                        window.location.href = window.location.href.replace("lifedata/transcription/audiobrowse", "download/tgdownloader");
                    }
                    else if (cur_location.includes("enternewsentences")) {
                        window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                    }
                    else if (cur_location.includes("audiobrowse")) {
                        window.location.href = window.location.href.replace("audiobrowse", "download/tgdownloader");
                    }
                }
                else {
                    window.location.reload();
                }
         });
        // $.ajax({
        //     url: 'download/downloadtranscriptions',
        //     type: 'POST',
        //     a: JSON.stringify(send_details),
        //     contentType: false,
        //     success: function (response) {
        //         // window.location.href = "http://127.0.0.1:5000/downloadjson";
        //         window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
        //         // window.location.reload();
        //         // console.info(response);
        //     }
        // });
        return false;
    });
});

$(document).ready(function () {
    $("#lifejson").click(function () {
        downloadFormat = "lifejson";
        audioIds = $('#idaudioids').val();
        // console.log("Audio IDS", audioIds);
        send_details = { "downloadFormat": downloadFormat, "audioIds": audioIds};
        console.log("Sending request from lifejson");
        // send_details = new FormData(document.querySelector("#iddownloadtranscriptionsform"));
        // alert(downloadFormat)
        //JSON.stringify(send_details)
        $.post("/download/downloadtranscriptions", {
            formDataLifeJSON: JSON.stringify(send_details)
        })
            .success(function (response) {
            // window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
            //     window.location.href = window.location.href.replace("audiobrowse", "download/tgdownloader");
                let cur_location = window.location.href;
                console.log("Location", cur_location);
                if (response != "0") {
                    if (cur_location.includes("lifedata/transcription/home")) {
                        window.location.href = window.location.href.replace("lifedata/transcription/home", "download/tgdownloader");
                    }
                    else if (cur_location.includes("lifedata/transcription/audiobrowse")) {
                        window.location.href = window.location.href.replace("lifedata/transcription/audiobrowse", "download/tgdownloader");
                    }
                    else if (cur_location.includes("enternewsentences")) {
                        window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                    }
                    else if (cur_location.includes("audiobrowse")) {
                        window.location.href = window.location.href.replace("audiobrowse", "download/tgdownloader");
                    }
                }
                else {
                    window.location.reload();
                }
         });
        // $.ajax({
        //     url: 'download/downloadtranscriptions',
        //     type: 'POST',
        //     a: JSON.stringify(send_details),
        //     contentType: false,
        //     success: function (response) {
        //         // window.location.href = "http://127.0.0.1:5000/downloadjson";
        //         window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
        //         // window.location.reload();
        //         // console.info(response);
        //     }
        // });
        return false;
    });
});

$(document).ready(function () {
    $("#lifejsonaudio").click(function () {
        downloadFormat = "lifejson";
        
        audioIds = $('#idaudioids').val();
        console.log("Audio IDS", audioIds);
        send_details = { "downloadFormat": downloadFormat, "includeAudio": "on", "audioIds": audioIds};
        // alert(downloadFormat)
        $.post("/download/downloadtranscriptions", {
            formDataLifeJSON: JSON.stringify(send_details)
        }).success(function (response) {
            let cur_location = window.location.href;
                console.log("Location", cur_location);
                if (response != "0") {
                    if (cur_location.includes("lifedata/transcription/home")) {
                        window.location.href = window.location.href.replace("lifedata/transcription/home", "download/tgdownloader");
                    }
                    else if (cur_location.includes("lifedata/transcription/audiobrowse")) {
                        window.location.href = window.location.href.replace("lifedata/transcription/audiobrowse", "download/tgdownloader");
                    }
                    else if (cur_location.includes("enternewsentences")) {
                        window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                    }
                    else if (cur_location.includes("audiobrowse")) {
                        window.location.href = window.location.href.replace("audiobrowse", "download/tgdownloader");
                    }
                }
                else {
                    window.location.reload();
                }
         });

        // $.ajax({
        //     url: 'download/downloadtranscriptions',
        //     type: 'GET',
        //     data: { 'data': JSON.stringify(send_details) },
        //     contentType: "application/json; charset=utf-8",
        //     success: function (response) {
        //         // window.location.href = "http://127.0.0.1:5000/downloadjson";
        //         window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
        //         // window.location.reload();
        //         // console.info(response);
        //     }
        // });
        return false;
    });
});


$(document).ready(function () {
    $("#praattexgrid").click(function () {
        downloadFormat = "textgrid";
        send_details = { "format": downloadFormat, "latest": true, "includeAudio": false };
        // alert(downloadFormat)
        $.ajax({
            url: '/download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/textgrid; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#csv").click(function () {
        downloadFormat = "csv";
        send_details = { "format": downloadFormat, "latest": true, "includeAudio": false };
        // alert(downloadFormat)
        $.ajax({
            url: '/download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/csv; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#tsv").click(function () {
        downloadFormat = "tsv";
        send_details = { "format": downloadFormat, "latest": true, "includeAudio": false };
        // alert(downloadFormat)
        $.ajax({
            url: '/download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/tsv; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#xlsx").click(function () {
        downloadFormat = "xlsx";
        send_details = { "format": downloadFormat, "latest": true, "includeAudio": false };
        // alert(downloadFormat)
        $.ajax({
            url: '/download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/xlsx; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#json").click(function () {
        downloadFormat = "json";
        send_details = { "format": downloadFormat, "latest": true, "includeAudio": false };
        // alert(downloadFormat)
        $.ajax({
            url: '/download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/json; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});


$(document).ready(function () {
    $("#latex").click(function () {
        downloadFormat = "latex";
        send_details = { "format": downloadFormat, "latest": true, "includeAudio": false };
        // alert(downloadFormat)
        $.ajax({
            url: '/download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/tex; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#html").click(function () {
        downloadFormat = "html";
        send_details = { "format": downloadFormat, "latest": true, "includeAudio": false };
        // alert(downloadFormat)
        $.ajax({
            url: '/download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/html; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#markdown").click(function () {
        downloadFormat = "markdown";
        send_details = { "format": downloadFormat, "latest": true, "includeAudio": false };
        // alert(downloadFormat)
        $.ajax({
            url: '/download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/markdown; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});


$(document).ready(function () {
    $("#mypraattexgrid").click(function () {
        downloadFormat = "textgrid";
        // alert(downloadFormat)
        send_details = { "format": downloadFormat, "latest": false, "includeAudio": false };
        $.ajax({
            url: '/download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/textgrid; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#mycsv").click(function () {
        downloadFormat = "csv";
        // alert(downloadFormat)
        send_details = { "format": downloadFormat, "latest": false, "includeAudio": false };
        $.ajax({
            url: '/download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/csv; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#mytsv").click(function () {
        downloadFormat = "tsv";
        // alert(downloadFormat)
        send_details = { "format": downloadFormat, "latest": false, "includeAudio": false };
        $.ajax({
            url: '/download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/tsv; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});


$(document).ready(function () {
    $("#myjson").click(function () {
        downloadFormat = "json";
        // alert(downloadFormat)
        send_details = { "format": downloadFormat, "latest": false, "includeAudio": false };
        $.ajax({
            url: '/download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/json; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});


$(document).ready(function () {
    $("#myxlsx").click(function () {
        downloadFormat = "xlsx";
        // alert(downloadFormat)
        send_details = { "format": downloadFormat, "latest": false, "includeAudio": false };
        $.ajax({
            url: '/download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/xlsx; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#mylatex").click(function () {
        downloadFormat = "latex";
        // alert(downloadFormat)
        send_details = { "format": downloadFormat, "latest": false, "includeAudio": false };
        $.ajax({
            url: '/download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/tex; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#myhtml").click(function () {
        downloadFormat = "html";
        // alert(downloadFormat)
        send_details = { "format": downloadFormat, "latest": false, "includeAudio": false };
        $.ajax({
            url: '/download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/html; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#mymarkdown").click(function () {
        downloadFormat = "markdown";
        // alert(downloadFormat)
        send_details = { "format": downloadFormat, "latest": false, "includeAudio": false };
        $.ajax({
            url: '/download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/xlsx; charset=utf-8",
            success: function (response) {
                let cur_location = window.location.href;
                console.log("Location", cur_location);
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                if (cur_location.includes("lifedata/transcription/home")) {
                    window.location.href = window.location.href.replace("lifedata/transcription/home", "download/tgdownloader");
                }
                else if (cur_location.includes("enternewsentences")) {
                    window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                }
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});