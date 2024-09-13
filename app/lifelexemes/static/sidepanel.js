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
    // console.log(shareinfo)
    var sidePanelElement = '';

    sidePanelElement += '<div id="mySidenav" class="sidenav">'+
                        '<a href="javascript:void(0)" class="closebtn" onclick="closeNav()">&times;</a>';

    if ('downloadchecked' in shareinfo &&
        shareinfo['downloadchecked'] == 'true') {
        sidePanelElement += '<a href=/downloadlexemeformexcel>'+
                            '<button type="button" class="btn btn-primary downloadlexform">'+
                            '<span class="glyphicon glyphicon-download-alt" aria-hidden="true"></span>'+
                            ' Lexeme Entry/Edit Form</button>'+
                            '</a>';
        }
                        
    if (shareinfo['sharemode'] >= 3) {
        sidePanelElement += '<button type="button" id="uploadexcelliftXMLmodalid"'+
                            ' class="btn btn-primary pull-right uploadexcelliftXMLmodal"'+
                            ' data-toggle="modal"'+
                            ' data-target="#uploadExcelLiftXMLModal">'+
                            // '<span class="glyphicon glyphicon-upload" aria-hidden="true"></span>'+
                            'Upload Excel/LiftXML'+
                            '</button>';

    }
    sidePanelElement += '</div>';

    // console.log(sidePanelElement);

    $("#sidepanel").html(sidePanelElement);
}
