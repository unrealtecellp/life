function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
    // document.getElementById("main").style.marginRight = "250px";
    document.body.style.backgroundColor = "rgba(0,0,0,0.4)";
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
    // document.getElementById("main").style.marginRight= "0";
    document.body.style.backgroundColor = "white";
}

function createSidePanel(shareinfo) {
    var sidePanelElement = '';

    sidePanelElement += '<div id="mySidenav" class="sidenav">'+
                        '<a href="javascript:void(0)" class="closebtn" onclick="closeNav()">&times;</a>';                        // '<a href="#">About</a>'+
                        // '<a href="#">Services</a>'+
                        // '<a href="#">Clients</a>'+
                        // '<a href="#">Contact</a>'+
                        // '<div class="col-sm-7 pull-right">'+
                        // '<a><button type="button" id="progressreport" class="btn btn-primary" data-toggle="modal"'+
                        // 'data-target="#myProgressReportModal">'+
                        // 'Progress Report'+
                        // '</button></a>';
    if (shareinfo['sharemode'] >= 10) {
        sidePanelElement += '<a><button type="button" id="transcriptionreportid" class="btn btn-primary transcriptionreport"'+
                            'onclick="getTranscriptionReport(this)">'+
                            'Transcription Report'+
                            '</button></a>';

    }
    if ('downloadchecked' in shareinfo &&
        shareinfo['downloadchecked'] == 'true') {
        sidePanelElement += '<a><button type="button" id="downloadtranscription" class="btn btn-primary" data-toggle="modal"'+
                            'data-target="#myDownloadTranscriptionModal">'+
                            'Download'+
                            '</button></a>';
        }
                        
    if (shareinfo['sharemode'] >= 3) {
        sidePanelElement += '<a><button type="button" id="addnewspeakertranscriptionid" class="btn btn-primary addnewspeaker"'+
                            'data-toggle="modal" data-target="#addNewSpeakerModal" onclick="getMetadataForm(this)">'+
                            'Add New Source'+
                            '</button></a>'+
                            '<a><button type="button" id="uploadaudioid" class="btn btn-primary uploadaudio" data-toggle="modal"'+
                            'data-target="#myUploadAudioModal">'+
                            'Upload Audio'+
                            '</button></a>';

    }
    // sidePanelElement += '</div>'+
    sidePanelElement += '</div>';

    // sidePanelElement += '<div id="main">'+
    //                     // '<h2>Sidenav Push Example</h2>'+
    //                     // '<p>Click on the element below to open the side navigation menu, and push this content to the right. Notice that we add a black see-through background-color to body when the sidenav is opened.</p>'+
    //                     // '<span style="font-size:30px; position:absolute; right:0px;cursor:pointer" onclick="openNav()">&#9776; open</span>'+
    //                     '<span style="font-size:30px; position:absolute; right:0px;cursor:pointer" onclick="openNav()"><i class="glyphicon glyphicon-triangle-left"></i></span>'+
    //                     // '<button class="btn pull-right" type="button" onclick="openNav()">'+
    //                     // '<span class="previousaudio glyphicon glyphicon-triangle-left" aria-hidden="true"></span>'+
    //                     // '</button>'+
    //                     '</div>';

    $("#sidepanel").html(sidePanelElement);
}

function getTranscriptionReport(ele) {
    $.post( "/lifedata/transcription/transcriptionreport", {
        // a: JSON.stringify(data_info )
      })
      .done(function( data ) {
        console.log(data);
        let totalAudioDurationProject = new Date(data.totalAudioDurationProject * 1000).toISOString().substring(11, 19);
        let docCountProject = data.docCountProject;
        let totalAudioDurationTranscribed = new Date(data.totalAudioDurationTranscribed * 1000).toISOString().substring(11, 19);
        let docCountTranscribed = data.docCountTranscribed;
        let totalAudioDurationTranscribedBoundary = new Date(data.totalAudioDurationTranscribedBoundary * 1000).toISOString().substring(11, 19);

        alert('Audio Duration Project: '+totalAudioDurationProject+', Doc Count Project: '+docCountProject+
            '\n\nAudio Duration Transcribed: '+totalAudioDurationTranscribed+', Doc Count Transcribed: '+docCountTranscribed+
            '\n\nAudio Duration Transcribed(Boundary): '+totalAudioDurationTranscribedBoundary)

        // window.location.href = window.location.href.replace("models_playground", "file_download/"+data.fileName);
      });
}