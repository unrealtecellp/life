function getMetadataForm(ele, options) {
    let defaults = { submitRoute: "/addnewspeakerdetails", 'text': 'text', includeFieldMetadata: true, includeInternetMetadata: true };
    options = Object.assign({}, defaults, options); //first it assigns defaults to the options and then overwrites those with the values present in 'options' object
    let { submitRoute, includeFieldMetadata, includeInternetMetadata } = options;

    cur_id = $(ele).attr('id')
    console.log('Current ID', cur_id);
    console.log('Options', options);
    speakerDetailForm(cur_id, submitRoute, includeFieldMetadata, includeInternetMetadata);
}
// $('.addnewspeaker').on('click', function () {
//     // console.log('on click');
//     cur_id = $(this).attr('id')
//     console.log('Current ID', cur_id)
//     if (cur_id === '')
//     speakerDetailForm(cur_id);
// });
// $('#addNewSpeakerModal').on('show.bs.modal', function () {
//     console.log('on show');
//     speakerDetailForm();
// });

$(document).on("hidden.bs.modal", "#addNewSpeakerModal", function () {
    document.getElementById('addnewspeakerform').innerHTML = '';
});

$('.metadataview').click(function () {
    var lifespeakerid = $(this).attr("id");
    console.log('Speaker ID', lifespeakerid)
    
    $.getJSON("/getonespeakermetadata", {
        lifespeakerid: String(lifespeakerid)
    }, function (data) {
        console.log("Received data", data)
        console.log("End Received data")

        metadata = data.onespeakerdetails.current.sourceMetadata
        lifespeakerid = data.onespeakerdetails.lifesourceid
        datasource = data.onespeakerdetails.metadataSchema

        // accesscode = data.speakerdetails.accesscode
        console.log("Metadata", metadata)
        console.log("Data source", datasource)
        $('#lifespeakerid').attr('value', lifespeakerid)

        form_html = window[datasource + "MetadataForm"](metadata);
        console.log("Form", form_html)
        $('#idmetadataformdisplaydiv').html(form_html);
        $('#idmetadataformdisplaydiv').show();
        $('#idmetadataformdisplaydiv').attr('required', '');
        $('#idmetadataformdisplaydiv').attr('data-error', 'This field is required.')

        $('#idmetadataformdisplaydiv').find('input, select').attr('disabled', true);
        
        addNewSpeakerFormEvents();
        addNewSpeakerSelect2();
    });
});


$('.speakerview').click(function () {
    // $('#fieldspeakerdetailsmodal').show.bs.modal
    // document.getElementById("fieldspeakerdetails").style.display = "block";
    var lifespeakerid = $(this).attr("id");
    console.log('Speaker ID', lifespeakerid)
    addNewSpeakerSelect2();
    // $.getJSON("{{url_for('getoneuserdetails')}}", {
    $.getJSON("/getonespeakermetadata", {
        lifespeakerid: String(lifespeakerid)
    }, function (data) {
        console.log("Received data", data)
        console.log("End Received data")

        $('#formdisplay').find('input, select').attr('disabled', true);
        // $('#formsubmit').find('input, select').attr('disabled', true);

        metadata = data.onespeakerdetails.current.sourceMetadata
        lifespeakerid = data.onespeakerdetails.lifesourceid

        // accesscode = data.speakerdetails.accesscode
        $('#lifespeakerid').attr('value', lifespeakerid)

        name = metadata.name
        $('#idviewname').attr('value', name)
        console.log("Name", name)

        agroup = metadata.agegroup
        ageOption = '<option value="' + agroup + '" selected="selected">' + agroup + '</option>'
        // document.getElementById('idage').innerHTML=""
        // $('#idage').html(ageOption)                        
        $('#idviewage').val(agroup).trigger('change');
        // $('#idgender').select2("val", "25-60");
        console.log("Age group", agroup)


        // $('#idspeakerdetailsdiv').show();
        // $('#idspeakerdetailsdiv').attr('required', '');
        // $('#idspeakerdetailsdiv').attr('data-error', 'This field is required.')

        gender = metadata.gender
        // genderOption = '<option value="'+gender+'" selected="selected">'+gender+'</option>'
        // $('#idgender').html(genderOption)
        $('#idviewgender').val(gender).trigger('change');
        console.log(gender);

        elevel = metadata.educationlevel
        elevelOption = '<option value="' + elevel + '" selected="selected">' + elevel + '</option>'
        // $('#idelevel').html(elevelOption)
        $('#idviewelevel').val(elevel).trigger('change');
        console.log(elevel);

        // mediumpre = metadata.medium-of-education-after-12th
        // mediumpost = metadata.medium-of-education-upto-12th

        // console.log("All education medium", EducationMedium)
        // let all_medium = [];
        // for (i = 0; i < EducationMedium.length; i++) {
        //     medium = EducationMedium[i]["text"];
        //     if (medium !== "") {
        //         all_medium.push(medium)
        //     }
        // }
        // console.log("Medium", all_medium);

        mediumupto12 = metadata.educationmediumupto12
        // mediumupto12option = ''
        // for (i = 0; i < mediumupto12.length; i++) {
        //     console.log("Medium upto 12", mediumupto12[i])
        //     mediumupto12option += '<option value="' + mediumupto12[i] + '" selected="selected">' + mediumupto12[i] + '</option>'
        // }
        // $('#idmediumpre').html(mediumupto12option)
        for (i = 0; i < mediumupto12.length; i++) {
            current_medium = mediumupto12[i]
            // if (!all_medium.includes(current_medium)) {
            if (!$('#idviewmediumpre').find("option[value='" + current_medium + "']").length) {
                // $('#idviewmediumpre').val(current_medium).trigger('change');
                let new_option = new Option(current_medium, current_medium, false, true);
                $('#idviewmediumpre').append(new_option);
            }            
        }
        $('#idviewmediumpre').val(mediumupto12);
        $('#idviewmediumpre').trigger('change');
        console.log(mediumupto12);


        mediumafter12 = metadata.educationmediumafter12
        // mediumafter12option = ''
        // for (i = 0; i < mediumafter12.length; i++) {
        //     mediumafter12option += '<option value="' + mediumafter12[i] + '" selected="selected">' + mediumafter12[i] + '</option>'
        // }
        // $('#idmediumpost').html(mediumafter12option)
        for (i = 0; i < mediumafter12.length; i++) {
            current_medium = mediumafter12[i]
            // if (!all_medium.includes(current_medium)) {
            if (!$('#idviewmediumpost').find("option[value='" + current_medium + "']").length) {
                // $('#idviewmediumpre').val(current_medium).trigger('change');
                let new_option = new Option(current_medium, current_medium, false, true);
                $('#idviewmediumpost').append(new_option);
            }            
        }
        $('#idviewmediumpost').val(mediumafter12);
        $('#idviewmediumpost').trigger('change');
        // $('#idviewmediumpost').val(mediumafter12).trigger('change');

        speakerotherlangs = metadata.speakerspeaklanguage
        // speakerotherlangsOption = ''
        // for (i = 0; i < speakerotherlangs.length; i++) {
        //     speakerotherlangsOption += '<option value="' + speakerotherlangs[i] + '" selected="selected">' + speakerotherlangs[i] + '</option>'
        // }
        // $('#idotherlangs').html(speakerotherlangsOption)
        for (i = 0; i < speakerotherlangs.length; i++) {
            current_language = speakerotherlangs[i]
            // if (!all_medium.includes(current_medium)) {
            if (!   $('#idviewotherlangs').find("option[value='" + current_language + "']").length) {
                // $('#idviewmediumpre').val(current_medium).trigger('change');
                let new_option = new Option(current_language, current_language, false, true);
                $('#idviewotherlangs').append(new_option);
            }            
        }
        $('#idviewotherlangs').val(speakerotherlangs);
        $('#idviewotherlangs').trigger('change');
        // $('#idviewotherlangs').val(speakerotherlangs).trigger('change');

        // name = metadata.name
        // $('#idname').attr('value', name)
        place = metadata.recordingplace
        // $('#idplace').attr('value', place)
        $('#idviewplace').val(place).trigger('change');

        ptype = metadata.typeofrecordingplace
        ptypeOption = '<option value="' + ptype + '" selected="selected">' + ptype + '</option>'
        // $('#idptype').html(ptypeOption)
        $('#idviewptype').val(ptype).trigger('change');

        // addNewSpeakerSelect2();
        // addNewSpeakerFormEvents();
    });
});


$('.youtubeview').click(function () {
    // $('#fieldspeakerdetailsmodal').show.bs.modal
    // document.getElementById("fieldspeakerdetails").style.display = "block";
    var lifespeakerid = $(this).attr("id");
    console.log('Speaker ID', lifespeakerid)
    addNewSpeakerSelect2();
    // $.getJSON("{{url_for('getoneuserdetails')}}", {
    $.getJSON("/getonespeakermetadata", {
        lifespeakerid: String(lifespeakerid)
    }, function (data) {
        console.log("Received data", data)
        console.log("End Received data")

        $('#formdisplayyoutube').find('input, select').attr('disabled', true);

        metadata = data.onespeakerdetails.current.sourceMetadata
        lifespeakerid = data.onespeakerdetails.lifesourceid
        // accesscode = data.speakerdetails.accesscode
        console.log('lifespeakerid', lifespeakerid)
        $('.lifespeakeridyt').attr('value', lifespeakerid)

        name = metadata.channelName
        $('#idytchannelname').attr('value', name)
        console.log("Name", name)

        url = metadata.channelUrl
        $('#idytchannelurl').attr('value', url)
        console.log("URL", url)

    });
});


function activeform(buttonType) {
    var x = document.getElementById("formdisplay");
    // buttonType = $(this).attr("id");
    // console.log(buttonType)

    if (x.style.display === "none") {
        x.style.display = "block";
    } else if (buttonType == 'closebutton') {
        x.style.display = "none";
    }
}


$('#editbutton').click(function () {

    $('#idmetadataformdisplaydiv').find('input, select').attr('disabled', false);
    $('#metadatasubmitid').attr('disabled', false);
    $('#editbutton').attr('hidden', true);
    // $('#idname').hidden();
    // $('#idage').attr('hidden', false);
    // document.getElementById('idviewname').readonly = true;
    // document.getElementById('idviewage').readonly = true;
    
    // $('#idviewname').attr('readonly', true);
    // $('#idviewage').attr('readonly', true);

    // $('#accodeformheader').find('input, select').attr('disabled', true);
});

$('#editbuttonyt').click(function () {

    $('#formdisplayyoutube').find('input, select').attr('disabled', false);
    $('#editbuttonyt').attr('hidden', true);
});

$('.assignaccesscode').click(function () {
    document.getElementById("accodeformheader").style.display = "block";
    buttonType = $(this).attr("id")
    activeform(buttonType)
    // activeform()
    $('#editbutton').attr('hidden', true)
    // document.getElementById('idname').style.display = "block";
    $('#formdisplay').find('input, select').attr('disabled', false);

    // $("#formdisplay").trigger('clear');
    // $('#formdisplay').reset();
    // document.getElementById('idname').style.display = "block";
    // $('#idname').attr('hidden', true)
    $('#idname').attr('value', '');
    $('#idplace').attr('value', '');
    // $('#formdisplay').find('input').attr('value', '')

    // $('#formdisplay').find('select').attr('selected', false)
    // $('#formdisplay').find('select2').val(null).trigger('change');

    $('#idage').val(" ").trigger("change");
    $('#idgender').val(" ").trigger("change");
    $('#idelevel').val(" ").trigger("change");
    $('#idmediumpre').val(" ").trigger("change");
    $('#idmediumpost').val(" ").trigger("change");
    $('#idotherlangs').val(" ").trigger("change");
    $('#idplace').val(" ").trigger("change");
    $('#idptype').val(" ").trigger("change");

    // $('#formdisplay').find('select').html("")
    // $('#formdisplay option:selected').removeAttr('selected')                  

    $('#accesscode').attr('value', '')
})
// $('#closebutton').click(function () {
//     buttonType = $(this).attr("id")
//     // activeform(buttonType)
//     // activeform()
//     // $('#formdisplay').find('input, select').attr('disabled', false);
//     // $('#editbutton').attr('hidden', true)
// })
// // });

// $('#closebuttonyoutube').click(function () {
//     var x = document.getElementById("formdisplayyoutube");
//     // x.style.display = "none";
//     if (x.style.display === "none") {
//         x.style.display = "block";
//     } else if (buttonType == 'closebuttonyoutube') {
//         x.style.display = "none";
//     }
// })




function speakerDetailForm(curId, submitRoute="/addnewspeakerdetails", includeFieldMetadata=false, includeInternetMetadata=true) {
    console.log('Current ID', curId)

    var speakerMetadata = ['Name', 'Age', 'Gender', 'Occupation']
    var speakerinpt = ''
    // var speakerinpt = '<h4>Details for Speaker</h4>';
    // for (let i=0; i<speakerMetadata.length; i++) {
    //   speakerinpt += '<div class="form-group">'+
    //           '<label for="'+ speakerMetadata[i] +'">'+ speakerMetadata[i] +'</label>'+
    //           '<input type="text" class="form-control" id="'+ speakerMetadata[i] +'"'+ 
    //           'placeholder="'+ speakerMetadata[i] +'" name="'+ speakerMetadata[i] +'">'+
    //           '</div>';
    // }
    let sourceinpt = ''
    let subsourceinpt = ''
    sourceinpt += '<form action="'+submitRoute+'" method="POST" enctype="multipart/form-data">';
    sourceinpt += '<input type="hidden" value="' +
        curId +
        '"name = "sourcecallpage" id="sourcecallpageid">';
    
    sourceinpt += '<div id="formdisplayinitial" style="display: block;">';
    
    sourceinpt += '<div class="form-group">' +
        '<input type="radio" name="metadataentrytype" value="single" id="entrytypesingleid" class="metadatauploadtypeclass">' +
        '<label for="entrytypesingleid" name="metadatauploadtypesingle" class="btn btn-lg btn-inline-block btn-info metadatauploadtypesingle" style="width:35%">Single Entry</label> &nbsp;&nbsp;&nbsp;&nbsp;' +
        '<input type="radio" name="metadataentrytype" value="bulk" id="entrytypebulkid" class="metadatauploadtypeclass">' +
        '<label for="entrytypebulkid" name="metadatauploadtypebulk" class="btn btn-lg btn-inline-block btn-info metadatauploadtypebulk pull-right" style="width:35%">Bulk Entry</label>' +
        '</div>';  
    
    
    sourceinpt += '<div id="formdisplaybulk" style="display: none;" class="col-xs-12">';
    sourceinpt += '<h4> Bulk Metadata Entry</h4>';
    
    sourceinpt += '<div  class="col-xs-12">' +
        '<a target="_blank" href="https://drive.google.com/drive/folders/1TxyW6D5mlqQVaFrJaLGXiYgtBCODjALs">' +
        '<button type="button" class="btn btn-warning pull-right">' +
        'Metadata Form <span class="glyphicon glyphicon-download-alt" aria-hidden="true"></span>' +
        '</button > ' +
        '</a><br /><br/>' +
        '</div>';          
    
    sourceinpt += '<div class="col-xs-12" >';
    // sourceinpt += '<input type="hidden" name="uploadtype" value="bulk">'
    sourceinpt += '<div class="form-group">' +
        '<label for="idaudiosourcebulk">Audio Source </label> <br>' +
        '<select class="audiosourceclassbulk" id="idaudiosourcebulk" name="audiosource" style="width:55%" >' +
        '</select><br>' +
        '</div>';
    
    subsourceinpt += '<div id="idfieldmetadataschemabulkdiv" style="display: none;">';
    if (includeFieldMetadata) {
        subsourceinpt += '<div class="form-group">' +
            '<label for="idfieldmetadataschemabulk">Metadata Schema </label> <br>' +
            '<select class="fieldmetadataschemaclassbulk" id="idfieldmetadataschemabulk" name="fieldMetadataSchema" style="width:55%" required>' +
            '</select><br>';
        subsourceinpt += '</div>';
    }
    else {
        subsourceinpt += '<div class="alert alert-danger" role="alert">' +
            'No schema available for field source!' +
            '</div>';
    }
    subsourceinpt += '</div>';
    
    subsourceinpt += '<div id="idaudiointernetsourcebulkdiv" style="display: none;">';
    if (includeInternetMetadata) {
        subsourceinpt += '<div class="form-group">' +
            '<label for="idaudiosubsourcebulk">Audio Internet Source </label> <br>' +
            '<select class="classaudiointernetsourcebulk" id="idaudiointernetsourcebulk" name="audioInternetSource" style="width:55%" required>' +
            '</select><br>';
        subsourceinpt += '</div>';
    }
    else {
        subsourceinpt += '<div class="alert alert-danger" role="alert">' +
            'No schema available for internet source!' +
            '</div>';
    }
    subsourceinpt += '</div>';
    
         
    sourceinpt += subsourceinpt;
    sourceinpt += '<div class="form-group">' +
        '<label for="metadata-upload-button">Select Metadata Form:</label> <br/>' +
        '<input type="file" class="form-control col-xs-6 " style="width:55%" id="metadata-upload-button" name="metadatafile" required><br /><br />' +
        '<input class="btn btn-success classmetadatauploadbutton" id="idmetadatauploadbutton" type="submit" value="Upload Metadata" disabled>' +
        // '</form>' +
        '</div>'
    sourceinpt += '</div>';
    sourceinpt += '</div>';


    sourceinpt += '<div id="formdisplaysingle" style="display: none;">'
        // '<form role="form" method="post" action="/addnewspeakerdetails">';
    // sourceinpt += '<input type="hidden" name="uploadtype" value="single">'
    sourceinpt += '<h4> Single Metadata Entry</h4>';
    sourceinpt += '<div class="form-group">' +
        '<label for="idaudiosource">Audio Source </label> <br>' +
        '<select class="audiosourceclass" id="idaudiosource" name="audiosource" style="width:55%" >' +
        '</select><br>' +
        '</div>';
    
    subsourceinpt = '<div id="idfieldmetadataschemadiv" style="display: none;">';    
    if (includeFieldMetadata) {
        subsourceinpt += '<div class="form-group">' +
            '<label for="idfieldmetadataschema">Metadata Schema </label> <br>' +
            '<select class="fieldmetadataschemaclass" id="idfieldmetadataschema" name="fieldMetadataSchema" style="width:55%">' +
            '</select><br>' +
            '</div>';
    }
    else {
        subsourceinpt += '<div class="alert alert-danger" role="alert">' +
            'No schema available for field source!' +
            '</div>';
    }
    subsourceinpt += '</div>';
    
    
        subsourceinpt += '<div id="idspeakerdetailsdiv" style="display: none;"></div>';
        // subsourceinpt += '</div>';
    
    
        // '<form role="form" method="post" action="/addnewspeakerdetails">'+

        // '<button class="pull-right btn-danger" type="button" id ="editbutton">Edit</button><br/>'+

        // '<input type ="hidden" id = "accesscode" name = "accode" value = {{accode}}>'+


        // '<div id="accodeformheader" style="display: block;">'+
        // '<h4>Access Code Metadata</h4>'+
        // '<div class="form-group">'+
        // '<label for="idaccesscodefor">Access Code For:</label><br>'+
        // '<select class="accesscodefor" id="idaccesscodefor" name="accesscodefor" style="width:55%" required></select><br>'+
        // '</div>'+

        // '<div class="form-group">'+
        // '<label for="idtask">Task :</label><br>'+
        // '<select class="task" id="idtask" name="task"  style="width:55%" required></select><br>'+
        // '</div>'+

        // '<div id="uploadaccode" style="display: block;"></div> '+
        // '<hr>'+
        // '</div>'+
    
    // subsourceinpt += ; // div of idfieldmetadataschemadiv
    
        subsourceinpt += '<div id="idinternetsourcediv" style="display: none;">';
        if (includeInternetMetadata) {
            subsourceinpt += '<div class="form-group">' +
                '<label for="idaudiointernetsource">Audio Internet Source </label> <br>' +
                '<select class="classaudiointernetsource" id="idaudiointernetsource" name="audioInternetSource" style="width:55%;">' +
                '</select><br>' +
                '</div>';
            // subsourceinpt += </div>';
            subsourceinpt += '<div id="idinternetsourcedetailsdiv" style="display: none;"></div>';
        }
        else {
            subsourceinpt += '<div class="alert alert-danger alert-dismissible" role="alert">' +
                'No schema available for internet source!' +
                '<button type="button" class="close" data-dismiss="alert" aria-label="Close">'+
                '<span aria-hidden="true">&times;</span>' +
                '</div>';
        }
    subsourceinpt += '</div>';
    
    subsourceinpt +=   '<button type="button" id="closebutton" class="btn btn-warning" data-dismiss="modal">Cancel</button>' +
        '<input type="submit" class="btn btn-primary clasmetadatasubmitbutton" id="idmetadatasubmitbutton" value="Save Metadata" disabled> <br><br>';
    
    subsourceinpt += '</div>';

    sourceinpt += subsourceinpt;
    
    sourceinpt += '</div>';
    sourceinpt += '</div>';
    sourceinpt += '</form>';
    // speakerinpt += sourceinpt;

    
    $("#addnewspeakerform").append(sourceinpt);
        
    addNewSpeakerFormEvents();
    addNewSpeakerSelect2();
}

// function internetMetadataForm() {
//     metadataForm = '<div class="form-group">' +
//         '<label for="idaudiosubsource">Audio Sub Source </label> <br>' +
//         '<select class="audiosubsourceclass" id="idaudiosubsource" name="audiosubsource" style="width:55%" >' +
//         '</select><br>' +
//         '</div>';
//     return metadataForm
// }

function youtubeMetadataForm(form_vals = {}) {
    metadataForm = '<h4>YouTube Metadata</h4>';
    metadataForm += '<div class="form-group">' +
        '<label class="col-form-label">Youtube Channel Name</label><br>' +
        '<input type="text" class="form-control" id="idytchannelname" name="youtubeChannelName" placeholder="--Youtube Channel Name--" style="width:55%;" value="';
    if (form_vals["youtubeChannelName"]) {
        metadataForm += form_vals["youtubeChannelName"];
    }
    metadataForm += '">' +
        '</div>';
        
    metadataForm += '<div class="form-group">' +
        '<label class="col-form-label">Youtube Channel URL</label><br>' +
        '<input type="url" class="form-control" id="idytchannelurl" name="youtubeChannelUrl" placeholder="--Youtube Channel URL--" style="width:55%;" value="';
    if (form_vals["youtubeChannelUrl"]) {
        metadataForm += form_vals["youtubeChannelUrl"];
    }
    metadataForm += '">' +
        '</div>';
    return metadataForm
}

function speedMetadataForm(form_vals = {}) {

    console.log("Form values", form_vals);
    
    metadataForm = '<h4>Speaker Metadata</h4>';

    //Name
    metadataForm += '<div class="form-group">' +
        '<label class="col-form-label">Name:</label>' +
        '<input type="text" class="form-control classname" id="idname" name="name" placeholder="--Speaker Name--" style="width:55%" value="';    
    if (form_vals["name"]) {
        metadataForm += form_vals["name"];
    }
    metadataForm += '">' +
        '</div>';

    //Age Group
    metadataForm += '<div class="form-group">' +
        '<label for="sagegroup">Age Group: </label><br>' +
        '<select class="classagegroup" id="idagegroup" name="ageGroup" style="width:55%">';    
    if (form_vals["ageGroup"]) {
        metadataForm += '<option value="' + form_vals["ageGroup"] + '" selected="selected">' + form_vals["ageGroup"] + '</option>';
    }
    metadataForm += '</select><br>' +
        '</div>';

    //Gender
    metadataForm += '<div class="form-group">' +
        '<label for="sgender">Gender: </label><br>' +
        '<select class="classgender" id="idgender" name="gender" style="width:55%" >';
    if (form_vals["gender"]) {
        metadataForm += '<option value="' + form_vals["gender"] + '" selected="selected">' + form_vals["gender"] + '</option>';
    }
    metadataForm += '</select><br>' +
        '</div>';

    //Educational Level
    metadataForm += '<div class="form-group">' +
        '<label for="educationlevel">Educational Level: </label> <br>' +
        '<select class="classeducationlevel" id="ideducationlevel" name="educationLevel" style="width:55%" >';
    if (form_vals["educationLevel"]) {
        
        metadataForm += '<option value="' + form_vals["educationLevel"] + '">' + form_vals["educationLevel"] + '</option>';
    }
    metadataForm += '</select><br>' +
        '</div>';

    //Medium of Education (upto 12th)
    metadataForm += '<div class="form-group">' +
        '<label for="moe12">Medium Of Education (upto 12ᵗʰ): </label><br>' +
        '<select class="classeducationmediumupto12" id="idmeducationmediumupto12" name="educationMediumUpto12-list" multiple="multiple" style="width:55%">';
    if (form_vals["educationMediumUpto12-list"]) {
        edMed = form_vals["educationMediumUpto12-list"]
        if (typeof edMed === 'string' || edMed instanceof String) {
            edMed = [edMed]
        }
        for (i = 0; i < edMed.length; i++) {
            current_medium = edMed[i]
            metadataForm += '<option value="' + current_medium + '" selected="selected">' + current_medium + '</option>';
        }
    }
    metadataForm += '</select><br>' +
        '</div>';

    
    //Medium of Education (after 12th)
    metadataForm += '<div class="form-group">' +
        '<label for="moea12">Medium Of Education (After 12ᵗʰ): </label><br>' +
        '<select class="classeducationmediumafter12" id="ideducationmediumafter12" name="educationMediumAfter12-list" multiple="multiple" style="width:55%" >';
    if (form_vals["educationMediumAfter12-list"]) {
        for (i = 0; i < form_vals["educationMediumAfter12-list"].length; i++) {
            current_medium = form_vals["educationMediumAfter12-list"][i]
            metadataForm += '<option value="' + current_medium + '" selected="selected">' + current_medium + '</option>';
        }
    }
    metadataForm += '</select><br>' +
        '</div>';

    //Other Languages Speaker could speak
    metadataForm += '<div class="form-group">' +
        '<label for="sols">Other Languages Speaker Could Speak: </label><br>' +
        '<select class="classotherlanguages" id="idotherlanguages" name="otherLanguages-list" multiple="multiple" style="width:55%" >';
    if (form_vals["otherLanguages-list"]) {
        for (i = 0; i < form_vals["otherLanguages-list"].length; i++) {
            current_language = form_vals["otherLanguages-list"][i]
            metadataForm += '<option value="' + current_language + '" selected="selected"> '+ current_language +'</option>';
        }
    }
    metadataForm += '</select><br>' +
        '</div>';

    //Place of Recording
    metadataForm += '<div class="form-group">' +
        '<label class="col-form-label">Place Of Recording:</label><br>' +
        '<input type="text" class="form-control classplaceofrecording" id="idplaceofrecording" name="placeOfRecording" placeholder="--Place Of Recording--" style="width:55%;" value="';
    if (form_vals["placeOfRecording"]) {
        metadataForm += form_vals["placeOfRecording"];
    }
    metadataForm += '"> ' +
        '</div>';

    //Type of Place
    metadataForm += '<div class="form-group">' +
            '<label for="toc">Type Of Place: </label> <br>' +
            '<select class="classtypeofplace" id="idptypeofplace" name="typeOfPlace"  style="width:55%" >';
    if (form_vals["typeOfPlace"]) {
        metadataForm += '<option value="' + form_vals["typeOfPlace"] + '" selected="selected">' + form_vals["typeOfPlace"] + '</option>';
    }
    metadataForm += '</select><br>' +
        '</div>' +
        '</div>';

    return metadataForm
}

function ldcilMetadataForm(form_vals={}) {
    // console.log("Form values", form_vals);
    
    metadataForm = '<h4>Speaker Metadata</h4>';

    //Language
    metadataForm += '<div class="form-group">' +
        '<label for="language">Language: </label> <br>' +
        '<select class="classlanguage" id="idlanguage" name="language" style="width:55%">';
    if (form_vals["language"]) {
        
        metadataForm += '<option value="' + form_vals["language"] + '" selected="selected">' + form_vals["language"] + '</option>';
    }
    metadataForm += '</select><br>' +
        '</div>';

    //Name
    metadataForm += '<div class="form-group">' +
        '<label class="col-form-label">Name/Speaker ID:</label>' +
        '<input type="text" class="form-control classname" id="idname" name="name" placeholder="--Speaker Name--" style="width:55%" value="';    
    if (form_vals["name"]) {
        metadataForm += form_vals["name"];
    }
    metadataForm += '">' +
        '</div>';

    //Age Group
    metadataForm += '<div class="form-group">' +
        '<label for="sagegroup">Age Group: </label><br>' +
        '<select class="classldcilagegroup" id="idagegroup" name="ageGroup" style="width:55%">';    
    if (form_vals["ageGroup"]) {
        metadataForm += '<option value="' + form_vals["ageGroup"] + '" selected="selected">' + form_vals["ageGroup"] + '</option>';
    }
    metadataForm += '</select><br>' +
        '</div>';

    //Gender
    metadataForm += '<div class="form-group">' +
        '<label for="sgender">Gender: </label><br>' +
        '<select class="classgender" id="idgender" name="gender" style="width:55%" >';
    if (form_vals["gender"]) {
        metadataForm += '<option value="' + form_vals["gender"] + '" selected="selected">' + form_vals["gender"] + '</option>';
    }
    metadataForm += '</select><br>' +
        '</div>';

    //Educational Level
    metadataForm += '<div class="form-group">' +
        '<label for="educationlevel">Education: </label> <br>' +
        '<select class="classldcileducationlevel" id="ideducationlevel" name="educationLevel" style="width:55%" >';
    if (form_vals["educationLevel"]) {
        
        metadataForm += '<option value="' + form_vals["educationLevel"] + '">' + form_vals["educationLevel"] + '</option>';
    }
    metadataForm += '</select><br>' +
        '</div>';
    
    //Place of Elementary Education
    metadataForm += '<div class="form-group">' +
        '<label for="placeOfElementaryEducation">Place of Elementary Education: </label> <br>' +
        '<input type="text" class="form-control classplaceOfElementaryEducation" id="idplaceOfElementaryEducation" name="placeOfElementaryEducation" style="width:55%" value="';
    if (form_vals["placeOfElementaryEducation"]) {
        
        metadataForm += form_vals["placeOfElementaryEducation"];
    }
    metadataForm += '">' +
        '</div>';
    
    
    //State
    metadataForm += '<div class="form-group">' +
        '<label for="state">State: </label> <br>' +
        '<input type="text" class="form-control classstate" id="idstate" name="state" style="width:55%" value="';
   if (form_vals["state"]) {
        
        metadataForm += form_vals["state"];
    }
    metadataForm += '">' +
        '</div>';

    //District
    metadataForm += '<div class="form-group">' +
        '<label for="district">District: </label> <br>' +
        '<input type="text" class="form-control classdistrict" id="iddistrict" name="district" style="width:55%" value="';
    if (form_vals["district"]) {
        
        metadataForm += form_vals["district"];
    }
    metadataForm += '">' +
        '</div>';

    //Place of Recording
    metadataForm += '<div class="form-group">' +
        '<label class="col-form-label">Place Of Recording:</label><br>' +
        '<input type="text" class="form-control classplaceofrecording" id="idplaceofrecording" name="placeOfRecording" placeholder="--Place Of Recording--" style="width:55%;" value="';
    if (form_vals["placeOfRecording"]) {
        metadataForm += form_vals["placeOfRecording"];
    }
    metadataForm += '"> ' +
        '</div>';

    
    return metadataForm
}


function addNewSpeakerSelect2() {

    $('#idaudiosource').select2({
        // tags: true,
        placeholder: '--Audio Source--',
        data: audioSource,
        // allowClear: true
    });

    $('#idaudiosourcebulk').select2({
        // tags: true,
        placeholder: '--Audio Source--',
        data: audioSource,
        // allowClear: true
    });

    $('#idaudiointernetsource').select2({
        // tags: true,
        placeholder: '--Audio Internet Source--',
        data: audioInterntSources,
        // allowClear: true
    });

    $('#idaudiointernetsourcebulk').select2({
        // tags: true,
        placeholder: '--Audio Internet Source--',
        data: audioInterntSources,
        // allowClear: true
    });

    $('#idfieldmetadataschema').select2({
        // tags: true,
        placeholder: '--Metadata Schema--',
        data: metadataSchema,
        // allowClear: true
    });

    $('#idfieldmetadataschemabulk').select2({
        // tags: true,
        placeholder: '--Metadata Schema--',
        data: metadataSchema,
        // allowClear: true
    });

    $('.classlanguage').select2({
        // tags: true,
        placeholder: '--Language--',
        data: OtherLanguagesSpeakerCouldSpeak,
        // allowClear: true
    });

    $('.classagegroup').select2({
        // tags: true,
        placeholder: '--Age Group--',
        data: AgeGroup,
        // allowClear: true
    });

    $('.classldcilagegroup').select2({
        // tags: true,
        placeholder: '--Age Group--',
        data: LdcilAgeGroup,
        // allowClear: true
    });

    $('.classgender').select2({
        // tags: true,
        placeholder: '--Gender--',
        data: gender,
        // allowClear: true
    });

    $('.classeducationlevel').select2({
        // tags: true,
        placeholder: '-- Educational Level --',
        data: EducationLevel,
        // allowClear: true
    });

    $('.classldcileducationlevel').select2({
        // tags: true,
        placeholder: '-- Educational Level --',
        data: LdcilEducationLevel,
        // allowClear: true
    });

    $('.classeducationmediumafter12').select2({
        tags: true,
        placeholder: '-- Medium Of Education (After 12ᵗʰ) --',
        data: EducationMedium,
        // allowClear: true
    });

    $('.classeducationmediumupto12').select2({
        tags: true,
        placeholder: '-- Medium Of Education (Upto 12ᵗʰ) --',
        data: EducationMedium,
        // allowClear: true
    });

    $('.classotherlanguages').select2({
        tags: true,
        placeholder: '-- Other Languages Speaker Could Speak --',
        data: OtherLanguagesSpeakerCouldSpeak,
        // allowClear: true
    });

    $('.classtypeofplace').select2({
        // tags: true,
        placeholder: '--Type Of Place:--',
        data: TypeOfCity,
        // allowClear: true,
        // console.log( "ready!" )
    });
}

function addNewSpeakerFormEvents() {

    $('#idaudiosource').change(function () {
        console.log('idaudiosource');
        var sourceVal = $(this).val();
        console.log("Current task value", sourceVal);
        // 

        if (sourceVal === "field" || sourceVal === "field-ldcil") {
            // $('#idinternetsourcediv').html("");
            // field_element = document.getElementById("idfieldmetadataschemadiv");
            // if (field_element) {
                $('#idinternetsourcediv').hide();
                $('#idinternetsourcediv').removeAttr('required');
                $('#idinternetsourcediv').removeAttr('data-error');
                $('#idaudiointernetsource').val("");
                $('#idinternetsourcedetailsdiv').html("");
                // $('#idspeakerdetailsdiv').show();
                $('#idfieldmetadataschemadiv').show();
                $('#idfieldmetadataschemadiv').attr('required', '');
                $('#idfieldmetadataschemadiv').attr('data-error', 'This field is required.')
            // }
            

        }
        else if (sourceVal === "internet") {
            // $('#idfieldmetadataschemadiv').html("");
            $('#idfieldmetadataschemadiv').hide();
            $('#idfieldmetadataschemadiv').removeAttr('required', '');
            $('#idfieldmetadataschemadiv').removeAttr('data-error', 'This field is required.')
            $('#idfieldmetadataschema').val("");
            $('#idspeakerdetailsdiv').html ("");
            // $('#idspeakerdetailsdiv').hide();
            // $('#idspeakerdetailsdiv').removeAttr('required');
            // $('#idspeakerdetailsdiv').removeAttr('data-error');
            // form_html = internetMetadataForm();
            // console.log(form_html); 
            // $('#idinternetsourcediv').html(form_html);
            $('#idinternetsourcediv').show();
            $('#idinternetsourcediv').attr('required', '');
            $('#idinternetsourcediv').attr('data-error', 'This field is required.')

        }
        else {
            // $('#idspeakerdetailsdiv').hide();
            // $('#idspeakerdetailsdiv').removeAttr('required');
            // $('#idspeakerdetailsdiv').removeAttr('data-error');
            // $('#idfieldmetadataschemadiv').html("");
            $('#idfieldmetadataschemadiv').hide();
            $('#idfieldmetadataschemadiv').removeAttr('required', '');
            $('#idfieldmetadataschemadiv').removeAttr('data-error', 'This field is required.')
            $('#idfieldmetadataschema').val("");
            // $('#idinternetsourcediv').html("");
            $('#idinternetsourcediv').hide();
            $('#idinternetsourcediv').removeAttr('required');
            $('#idinternetsourcediv').removeAttr('data-error');
            $('#idaudiointernetsource').val("");
        }
        $('#idmetadatasubmitbutton').prop("disabled", true);
        $('#idmetadatauploadbutton').prop("disabled", true);
        addNewSpeakerFormEvents();
        addNewSpeakerSelect2();
    });

    $('#idaudiosourcebulk').change(function () {
        // console.log('idaudiosourcebulk');
        var sourceVal = $(this).val();
        // console.log("Current task value", sourceVal);
        $('#idmetadatauploadbutton').prop("disabled", true);
        if (sourceVal === "field") {
            $('#idaudiointernetsourcebulkdiv').hide();
            $('#idaudiointernetsourcebulkdiv').removeAttr('required');
            $('#idaudiointernetsourcebulkdiv').removeAttr('data-error');
            $('#idfieldmetadataschemabulk').val("");
            // $('#idspeakerdetailsdiv').show();
            $('#idfieldmetadataschemabulkdiv').show();
            $('#idfieldmetadataschemabulkdiv').attr('required', '');
            $('#idfieldmetadataschemabulkdiv').attr('data-error', 'This field is required.')
            
            field_element = document.getElementById("idfieldmetadataschemabulk");
             

        }
        else if (sourceVal === "internet") {
            $('#idfieldmetadataschemabulkdiv').hide();
            $('#idfieldmetadataschemabulkdiv').removeAttr('required', '');
            $('#idfieldmetadataschemabulkdiv').removeAttr('data-error', 'This field is required.')
            $('#idaudiointernetsourcebulk').val("");
            // $('#idspeakerdetailsdiv').hide();
            // $('#idspeakerdetailsdiv').removeAttr('required');
            // $('#idspeakerdetailsdiv').removeAttr('data-error');
            $('#idaudiointernetsourcebulkdiv').show();
            $('#idaudiointernetsourcebulkdiv').attr('required', '');
            $('#idaudiointernetsourcebulkdiv').attr('data-error', 'This field is required.')
            
            field_element = document.getElementById("idaudiointernetsourcebulk");

        }
        else {
            // $('#idspeakerdetailsdiv').hide();
            // $('#idspeakerdetailsdiv').removeAttr('required');
            // $('#idspeakerdetailsdiv').removeAttr('data-error');
            $('#idfieldmetadataschemabulkdiv').hide();
            $('#idfieldmetadataschemabulkdiv').removeAttr('required', '');
            $('#idfieldmetadataschemabulkdiv').removeAttr('data-error', 'This field is required.')
            $('#idaudiointernetsourcebulkdiv').hide();
            $('#idaudiointernetsourcebulkdiv').removeAttr('required');
            $('#idaudiointernetsourcebulkdiv').removeAttr('data-error');
        }
        $('#idmetadatasubmitbutton').prop("disabled", true);
        if (field_element) {
            $('#idmetadatauploadbutton').prop("disabled", false);
        }
        addNewSpeakerFormEvents();
        addNewSpeakerSelect2();
    });

    $('#idaudiointernetsource').change(function () {
        console.log('audioInternetSource');
        var subSourceVal = $(this).val();
        console.log("Current task value", subSourceVal);
        form_html = window[subSourceVal + "MetadataForm"]();
        $('#idspeakerdetailsdiv').html("");
        $('#idinternetsourcedetailsdiv').html(form_html);
        $('#idinternetsourcedetailsdiv').show();
        $('#idinternetsourcedetailsdiv').attr('required', '');
        $('#idinternetsourcedetailsdiv').attr('data-error', 'This field is required.')
        $('#idmetadatasubmitbutton').prop("disabled", false);

        // if (subSourceVal === "youtube") {
        //     form_html = youtubeMetadataForm();
        //     console.log(form_html);
        //     $('#idinternetsourcedetailsdiv').html(form_html);
        //     $('#idinternetsourcedetailsdiv').show();
        //     $('#idinternetsourcedetailsdiv').attr('required', '');
        //     $('#idinternetsourcedetailsdiv').attr('data-error', 'This field is required.')

        // }
        // // else if (sourceVal === "internet") {
        // //     $('#idspeakerdetailsdiv').hide();
        // //         $('#idspeakerdetailsdiv').removeAttr('required');
        // //         $('#idspeakerdetailsdiv').removeAttr('data-error');
        // //     $('#idsubsourcediv').show();
        // //         $('#idsubsourcediv').attr('required', '');
        // //         $('#idsubsourcediv').attr('data-error', 'This field is required.')

        // //     }
        // else {
        //     $('#idinternetsourcedetailsdiv').html("");
        //     $('#idinternetsourcedetailsdiv').hide();
        //     $('#idinternetsourcedetailsdiv').removeAttr('required');
        //     $('#idinternetsourcedetailsdiv').removeAttr('data-error');
        // }
        addNewSpeakerFormEvents();
        addNewSpeakerSelect2();
    });

    $('#idfieldmetadataschema').change(function () {
        // console.log('idfieldmetadataschema');
        var schemaVal = $(this).val();
        // console.log("Current schema value", schemaVal);
        form_val = {'name': 'Ritesh', 'ageGroup': '18-31', 'educationMediumAfter12-list': ['Hindi', 'English', 'Konkani', 'Toto', 'Mahisu']}
        $('#idspeakerdetailsdiv').show();   
        // $('#idspeakerdetailsdiv').innerHTML = "";  
        $('#idinternetsourcedetailsdiv').html("");
        form_html = window[schemaVal + "MetadataForm"](form_val);
        
        // if (schemaVal === "speed") {
        //     // $('#idsubsourcediv').hide();
        //     // $('#idsubsourcediv').removeAttr('required');
        //     // $('#idsubsourcediv').removeAttr('data-error');
        //     // console.log(speedMetadataForm())
        //     form_html = speedMetadataForm();
        //     // $('#idspeakerdetailsdiv').innerHTML += form_html;
        // }
        // else if (schemaVal == "ldcil") {
        //     form_html = ldcilMetadataForm();
        // }
        // else {
        //     form_html = "";
        // }
        $('#idspeakerdetailsdiv').html (form_html);
        $('#idspeakerdetailsdiv').attr('required', '');
        $('#idspeakerdetailsdiv').attr('data-error', 'This field is required.')
        $('#idmetadatasubmitbutton').prop("disabled", false);
        addNewSpeakerFormEvents();
        addNewSpeakerSelect2();
        // else if (sourceVal === "internet") {
        //     $('#idspeakerdetailsdiv').hide();
        //         $('#idspeakerdetailsdiv').removeAttr('required');
        //         $('#idspeakerdetailsdiv').removeAttr('data-error');
        //     $('#idsubsourcediv').show();
        //         $('#idsubsourcediv').attr('required', '');
        //         $('#idsubsourcediv').attr('data-error', 'This field is required.')

        //     }
        // else if (schemaVal == "ldcil") {
        //     // $('#idsubsourcediv').hide();
        //     // $('#idsubsourcediv').removeAttr('required');
        //     // $('#idsubsourcediv').removeAttr('data-error');
        //     $('#idspeakerdetailsdiv').innerHTML = "";
        //     $('#idspeakerdetailsdiv').innerHTML = speedMetadataForm();
        //     addNewSpeakerFormEvents();
        //     addNewSpeakerSelect2();
        //     $('#idspeakerdetailsdiv').show();
        //     $('#idspeakerdetailsdiv').attr('required', '');
        //     $('#idspeakerdetailsdiv').attr('data-error', 'This field is required.')
        // }
        // else {
        //     // $('#idsubsourcediv').hide();
        //     // $('#idsubsourcediv').removeAttr('required');
        //     // $('#idsubsourcediv').removeAttr('data-error');
        //     // $('#idspeakerdetailsdiv').show();
        //     // $('#idspeakerdetailsdiv').attr('required', '');
        //     // $('#idspeakerdetailsdiv').attr('data-error', 'This field is required.')
        //     $('#idspeakerdetailsdiv').hide();
        //     $('#idspeakerdetailsdiv').removeAttr('required');
        //     $('#idspeakerdetailsdiv').removeAttr('data-error');
        // }
    });

    $(".metadatauploadtypeclass").change(function() {
        // remove the background color from all labels.
        // alert("Changed!")
        
        selected_val = $("input[name='metadataentrytype']:checked").val();
        // alert("Value"+ selected_val);
        if (selected_val === "single") {
            $("label[name='metadatauploadtypesingle']").removeClass("btn-info");
            $("label[name='metadatauploadtypesingle']").addClass("btn-success");
            $("label[name='metadatauploadtypebulk']").addClass("btn-info");
            $("label[name='metadatauploadtypebulk']").removeClass("btn-success");

            // $("#formdisplaysingle").css("display", "block");
            $("#formdisplaysingle").show();
            $("#formdisplaysingle :input").prop("disabled", false);

            // $('#formdisplaybulk').css("display", "none");
            // $('.alert').alert('close');
            $('#formdisplaybulk').hide();
            $("#formdisplaybulk :input").prop("disabled", true);

        }
        else {
            $("label[name='metadatauploadtypebulk']").removeClass("btn-info");
            $("label[name='metadatauploadtypebulk']").addClass("btn-success");
            $("label[name='metadatauploadtypesingle']").addClass("btn-info");
            $("label[name='metadatauploadtypesingle']").removeClass("btn-success");

            // $('#formdisplaybulk').css("display", "block");
            $('#formdisplaybulk').show()
            $("#formdisplaybulk :input").prop("disabled", false);

            // $('#formdisplaysingle').css("display", "none");
            // $('.alert').alert('close');
            $('#formdisplaysingle').hide();
            $("#formdisplaysingle :input").prop("disabled", true);
            
        }

        $('#idmetadatasubmitbutton').prop("disabled", true);
        $('#idmetadatauploadbutton').prop("disabled", true);

        // $("label").removeClass("btn-info");
            

        // // add the background only to the parent-label of the clicked button.
        // $(this).parent().addClass("btn-success");
    });
}