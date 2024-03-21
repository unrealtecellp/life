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
                        '<a href="javascript:void(0)" class="closebtn" onclick="closeNav()">&times;</a>';
                        // '<a><button type="button" id="progressreport" class="btn btn-primary" data-toggle="modal"'+
                        // 'data-target="#myProgressReportModal">'+
                        // 'Progress Report'+
                        // '</button></a>';
    if ('downloadchecked' in shareinfo &&
        shareinfo['downloadchecked'] == 'true') {
        sidePanelElement += '<a><button type="button" id="downloadques" class="btn btn-primary" data-toggle="modal"'+
                            'data-target="#downloadQuesModal">'+
                            'Download'+
                            '</button></a>';
        }
    if (shareinfo['sharemode'] >= 3) {
        sidePanelElement += '<a><button type="button" id="uploadques" class="btn btn-primary uploadaudio" data-toggle="modal"'+
                            'data-target="#uploadQuesModal">'+
                            'Upload'+
                            '</button></a>';

    }
    sidePanelElement += '</div>';

    $("#sidepanel").html(sidePanelElement);
}
