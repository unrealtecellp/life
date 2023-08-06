$('.addnewspeaker').on('click', function () {
    console.log('on click');
    cur_id = $(this).attr('id')
    console.log('Current ID', cur_id)

    speakerDetailForm(cur_id);
});
// $('#addNewSpeakerModal').on('show.bs.modal', function () {
//     console.log('on show');
//     speakerDetailForm();
// });

$(document).on("hidden.bs.modal", "#addNewSpeakerModal", function () {
    document.getElementById('addnewspeakerform').innerHTML = '';
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

    $('#formdisplay').find('input, select').attr('disabled', false);
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




function speakerDetailForm(cur_id) {
    console.log('Current ID', cur_id)

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
    sourceinpt += '<form action="/addnewspeakerdetails" method="POST" enctype="multipart/form-data">';
    sourceinpt += '<input type="hidden" value="' +
        cur_id +
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
        '<a href="https://docs.google.com/spreadsheets/d/1-_ryNLIw4ZC1L78oiDBAoWAMVsXaBC_H0EzHL76PEmY/export?format=xlsx">' +
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
    subsourceinpt += '<div id="idfieldmetadataschemabulkdiv" style="display: none;">' +
        '<div class="form-group">' +
        '<label for="idfieldmetadataschemabulk">Metadata Schema </label> <br>' +
        '<select class="fieldmetadataschemaclassbulk" id="idfieldmetadataschemabulk" name="fieldmetadataschema" style="width:55%" >' +
        '</select><br>' +
        '</div></div>';
    subsourceinpt += '<div id="idsubsourcebulkdiv" style="display: none;">' +
        '<div class="form-group">' +
        '<label for="idaudiosubsourcebulk">Audio Sub Source </label> <br>' +
        '<select class="audiosubsourceclassbulk" id="idaudiosubsourcebulk" name="audiosubsourcebulk" style="width:55%" >' +
        '</select><br>' +
        '</div></div>';
    sourceinpt += subsourceinpt;
    sourceinpt += '<div class="form-group">' +
        '<label for="metadata-upload-button">Select Metadata Form:</label> <br/>' +
        '<input type="file" class="form-control col-xs-6 " style="width:55%" id="metadata-upload-button" name="metadatafile" required><br /><br />' +
        '<input class="btn btn-success" id="submit" type="submit" value="Upload Metadata">' +
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
    subsourceinpt = '<div id="idfieldmetadataschemadiv" style="display: none;">' +
        '<div class="form-group">' +
        '<label for="idfieldmetadataschema">Metadata Schema </label> <br>' +
        '<select class="fieldmetadataschemaclass" id="idfieldmetadataschema" name="fieldmetadataschema" style="width:55%" >' +
        '</select><br>' +
        '</div>';
    subsourceinpt += '<div id="idspeakerdetailsdiv" style="display: none;">' +
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

        '<div class="form-group">' +
        '<h4>Speaker Metadata</h4>' +

        '<label class="col-form-label">Name:</label>' +
        '<input type="text" class="form-control" id="idname" name="sname" placeholder="--Speaker Name--" style="width:55%" value="">' +
        '</div>' +

        '<div class="form-group">' +
        '<label for="sagegroup">Age Group: </label><br>' +
        '<select class="age" id="idage" name="sagegroup" style="width:55%">' +
        '</select><br>' +
        '</div>' +

        // '<div id="idspeakerdetailsdiv" style="display: block;">'+
        '<div class="form-group">' +
        '<label for="sgender">Gender: </label><br>' +
        '<select class="gender" id="idgender" name="sgender" style="width:55%" >' +
        '</select><br>' +
        '</div>' +

        '<div class="form-group">' +
        '<label for="educationalevel">Educational Level: </label> <br>' +
        '<select class="educationlvl" id="idelevel" name="educationalevel" style="width:55%" >' +
        '</select><br>' +
        '</div>' +


        '<div class="form-group">' +
        '<label for="moe12">Medium Of Education (upto 12ᵗʰ): </label><br>' +
        '<select class="educationmediumupto12" id="idmediumpre" name="moe12" multiple="multiple" style="width:55%" >' +
        '</select><br>' +
        '</div>' +


        '<div class="form-group">' +
        '<label for="moea12">Medium Of Education (After 12ᵗʰ): </label><br>' +
        '<select class="educationmediumafter12" id="idmediumpost" name="moea12" multiple="multiple" style="width:55%" >' +
        '</select><br>' +
        '</div>' +

        '<div class="form-group">' +
        '<label for="sols">Other Languages Speaker Could Speak: </label><br>' +
        '<select class="speakerspeaklanguage" id="idotherlangs" name="sols" multiple="multiple" style="width:55%" >' +
        '</select><br>' +
        '</div>' +

        '<div class="form-group">' +
        '<label class="col-form-label">Place Of Recording:</label><br>' +
        '<input type="text" class="form-control" id="idplace" name="por" placeholder="--Place Of Recording--" style="width:55%;">' +
        '</div>' +

        '<div class="form-group">' +
        '<label for="toc">Type Of Place: </label> <br>' +
        '<select class="typeofcity" id="idptype" name="toc"  style="width:55%" >' +
        '</select><br>' +
        '</div>' +
        '</div>';

        // '</form>'; 
        // '</div>';
    
    subsourceinpt += '</div>'; // div of idfieldmetadataschemadiv
    
    subsourceinpt += '<div id="idsubsourcediv" style="display: none;">' +
        '<div class="form-group">' +
        '<label for="idaudiosubsource">Audio Sub Source </label> <br>' +
        '<select class="audiosubsourceclass" id="idaudiosubsource" name="audiosubsource" style="width:55%" >' +
        '</select><br>' +
        '</div>';
    subsourceinpt += '<div id="idytsubsourcediv" style="display: none;">' +
        '<div class="form-group">' +
        '<label class="col-form-label">Youtube Channel Name</label><br>' +
        '<input type="text" class="form-control" id="idytchannelname" name="ytchannelname" placeholder="--Youtube Channel Name--" style="width:55%;">' +
        '</div>' +
        '<div class="form-group">' +
        '<label class="col-form-label">Youtube Channel URL</label><br>' +
        '<input type="url" class="form-control" id="idytchannelurl" name="ytchannelurl" placeholder="--Youtube Channel URL--" style="width:55%;">' +
        '</div>' +
        '</div>';
    subsourceinpt += '</div>';
    sourceinpt += subsourceinpt;


    sourceinpt +=   '<button type="button" id="closebutton" class="btn btn-secondary" data-dismiss="modal">Close</button>' +
        '<input type="submit" value="Submit"> <br><br>';

    sourceinpt += '</div>';
    sourceinpt += '</form>';
    // speakerinpt += sourceinpt;

    
    $("#addnewspeakerform").append(sourceinpt);
        
    addNewSpeakerFormEvents();
    addNewSpeakerSelect2();
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

    $('#idaudiosubsource').select2({
        // tags: true,
        placeholder: '--Audio Sub Source--',
        data: audioSubSource,
        // allowClear: true
    });

    $('#idaudiosubsourcebulk').select2({
        // tags: true,
        placeholder: '--Audio Sub Source--',
        data: audioSubSource,
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

    $('.age').select2({
        // tags: true,
        placeholder: '--Age Group--',
        data: AgeGroup,
        // allowClear: true
    });

    $('.gender').select2({
        // tags: true,
        placeholder: '--Gender--',
        data: gender,
        // allowClear: true
    });

    $('.educationlvl').select2({
        // tags: true,
        placeholder: '-- Educational Level --',
        data: EducationLevel,
        // allowClear: true
    });

    $('.educationmediumafter12').select2({
        tags: true,
        placeholder: '-- Medium Of Education (After 12ᵗʰ) --',
        data: EducationMedium,
        // allowClear: true
    });

    $('.educationmediumupto12').select2({
        tags: true,
        placeholder: '-- Medium Of Education (Upto 12ᵗʰ) --',
        data: EducationMedium,
        // allowClear: true
    });

    $('.speakerspeaklanguage').select2({
        tags: true,
        placeholder: '-- Other Languages Speaker Could Speak --',
        data: OtherLanguagesSpeakerCouldSpeak,
        // allowClear: true
    });

    $('.typeofcity').select2({
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
        if (sourceVal === "field" || sourceVal === "field-ldcil") {
            $('#idsubsourcediv').hide();
            $('#idsubsourcediv').removeAttr('required');
            $('#idsubsourcediv').removeAttr('data-error');
            // $('#idspeakerdetailsdiv').show();
            $('#idfieldmetadataschemadiv').show();
            $('#idfieldmetadataschemadiv').attr('required', '');
            $('#idfieldmetadataschemadiv').attr('data-error', 'This field is required.')

        }
        else if (sourceVal === "internet") {
            $('#idfieldmetadataschemadiv').hide();
            $('#idfieldmetadataschemadiv').removeAttr('required', '');
            $('#idfieldmetadataschemadiv').removeAttr('data-error', 'This field is required.')
            // $('#idspeakerdetailsdiv').hide();
            // $('#idspeakerdetailsdiv').removeAttr('required');
            // $('#idspeakerdetailsdiv').removeAttr('data-error');
            $('#idsubsourcediv').show();
            $('#idsubsourcediv').attr('required', '');
            $('#idsubsourcediv').attr('data-error', 'This field is required.')

        }
        else {
            // $('#idspeakerdetailsdiv').hide();
            // $('#idspeakerdetailsdiv').removeAttr('required');
            // $('#idspeakerdetailsdiv').removeAttr('data-error');
            $('#idfieldmetadataschemadiv').hide();
            $('#idfieldmetadataschemadiv').removeAttr('required', '');
            $('#idfieldmetadataschemadiv').removeAttr('data-error', 'This field is required.')
            $('#idsubsourcediv').hide();
            $('#idsubsourcediv').removeAttr('required');
            $('#idsubsourcediv').removeAttr('data-error');
        }
    });

    $('#idaudiosourcebulk').change(function () {
        console.log('idaudiosourcebulk');
        var sourceVal = $(this).val();
        console.log("Current task value", sourceVal);
        if (sourceVal === "field") {
            $('#idsubsourcebulkdiv').hide();
            $('#idsubsourcebulkdiv').removeAttr('required');
            $('#idsubsourcebulkdiv').removeAttr('data-error');
            // $('#idspeakerdetailsdiv').show();
            $('#idfieldmetadataschemabulkdiv').show();
            $('#idfieldmetadataschemabulkdiv').attr('required', '');
            $('#idfieldmetadataschemabulkdiv').attr('data-error', 'This field is required.')

        }
        else if (sourceVal === "internet") {
            $('#idfieldmetadataschemabulkdiv').hide();
            $('#idfieldmetadataschemabulkdiv').removeAttr('required', '');
            $('#idfieldmetadataschemabulkdiv').removeAttr('data-error', 'This field is required.')
            // $('#idspeakerdetailsdiv').hide();
            // $('#idspeakerdetailsdiv').removeAttr('required');
            // $('#idspeakerdetailsdiv').removeAttr('data-error');
            $('#idsubsourcebulkdiv').show();
            $('#idsubsourcebulkdiv').attr('required', '');
            $('#idsubsourcebulkdiv').attr('data-error', 'This field is required.')

        }
        else {
            // $('#idspeakerdetailsdiv').hide();
            // $('#idspeakerdetailsdiv').removeAttr('required');
            // $('#idspeakerdetailsdiv').removeAttr('data-error');
            $('#idfieldmetadataschemabulkdiv').hide();
            $('#idfieldmetadataschemabulkdiv').removeAttr('required', '');
            $('#idfieldmetadataschemabulkdiv').removeAttr('data-error', 'This field is required.')
            $('#idsubsourcebulkdiv').hide();
            $('#idsubsourcebulkdiv').removeAttr('required');
            $('#idsubsourcebulkdiv').removeAttr('data-error');
        }
    });

    $('#idaudiosubsource').change(function () {
        console.log('idsubsourcediv');
        var subSourceVal = $(this).val();
        console.log("Current task value", subSourceVal);
        if (subSourceVal === "youtube") {
            $('#idytsubsourcediv').show();
            $('#idytsubsourcediv').attr('required', '');
            $('#idytsubsourcediv').attr('data-error', 'This field is required.')

        }
        // else if (sourceVal === "internet") {
        //     $('#idspeakerdetailsdiv').hide();
        //         $('#idspeakerdetailsdiv').removeAttr('required');
        //         $('#idspeakerdetailsdiv').removeAttr('data-error');
        //     $('#idsubsourcediv').show();
        //         $('#idsubsourcediv').attr('required', '');
        //         $('#idsubsourcediv').attr('data-error', 'This field is required.')

        //     }
        else {
            $('#idytsubsourcediv').hide();
            $('#idytsubsourcediv').removeAttr('required');
            $('#idytsubsourcediv').removeAttr('data-error');
        }
    });

    $('#idfieldmetadataschema').change(function () {
        console.log('idfieldmetadataschema');
        var schemaVal = $(this).val();
        console.log("Current schema value", schemaVal);
        if (schemaVal === "speed") {
            // $('#idsubsourcediv').hide();
            // $('#idsubsourcediv').removeAttr('required');
            // $('#idsubsourcediv').removeAttr('data-error');
            $('#idspeakerdetailsdiv').show();
            $('#idspeakerdetailsdiv').attr('required', '');
            $('#idspeakerdetailsdiv').attr('data-error', 'This field is required.')
        }
        // else if (sourceVal === "internet") {
        //     $('#idspeakerdetailsdiv').hide();
        //         $('#idspeakerdetailsdiv').removeAttr('required');
        //         $('#idspeakerdetailsdiv').removeAttr('data-error');
        //     $('#idsubsourcediv').show();
        //         $('#idsubsourcediv').attr('required', '');
        //         $('#idsubsourcediv').attr('data-error', 'This field is required.')

        //     }
        else if (schemaVal == "ldcil") {
            // $('#idsubsourcediv').hide();
            // $('#idsubsourcediv').removeAttr('required');
            // $('#idsubsourcediv').removeAttr('data-error');
            $('#idspeakerdetailsdiv').show();
            $('#idspeakerdetailsdiv').attr('required', '');
            $('#idspeakerdetailsdiv').attr('data-error', 'This field is required.')
        }
        else {
            // $('#idsubsourcediv').hide();
            // $('#idsubsourcediv').removeAttr('required');
            // $('#idsubsourcediv').removeAttr('data-error');
            // $('#idspeakerdetailsdiv').show();
            // $('#idspeakerdetailsdiv').attr('required', '');
            // $('#idspeakerdetailsdiv').attr('data-error', 'This field is required.')
            $('#idspeakerdetailsdiv').hide();
            $('#idspeakerdetailsdiv').removeAttr('required');
            $('#idspeakerdetailsdiv').removeAttr('data-error');
        }
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
            $('#formdisplaysingle').hide();
            $("#formdisplaysingle :input").prop("disabled", true);
        }

        // $("label").removeClass("btn-info");
            

        // // add the background only to the parent-label of the clicked button.
        // $(this).parent().addClass("btn-success");
    });
}