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

// $(document).ready(function() {
// $('#idtask').change(function() {
//   var taskVal = $(this).val();
//   console.log("Current task value", taskVal);
//   if (taskVal === "SPEECH_DATA_COLLECTION") {
//     $('#idspeakerdetailsdiv').show();
//       $('#idspeakerdetailsdiv').attr('required', '');
//       $('#idspeakerdetailsdiv').attr('data-error', 'This field is required.')

//   }
//   else {
//     $('#idspeakerdetailsdiv').hide();
//       $('#idspeakerdetailsdiv').removeAttr('required');
//       $('#idspeakerdetailsdiv').removeAttr('data-error');
//   }
// });


// $('.lexemeview').click(function() {
//   $('#accodeformheader').find('input, select').attr('disabled', true);
//   $('#accodeformheader').find('input, select').attr('required', false);

//   document.getElementById("accodeformheader").style.display = "none";

//   buttonType = $(this).attr("id")
//   activeform(buttonType)
//   $('#formdisplay').find('input, select').attr('disabled', true);
//   $('#editbutton').attr('hidden', false);
//   // $('#idname').attr('hidden', true);
//   // $('#idage').attr('hidden', true);

//   // sending accesscode using AJAX
//   // getting speaker details assigned to that accesscode

//   var accode = $(this).attr("id");
//   // console.log(accode)
//   $.getJSON("{{url_for('karya_bp.getonespeakerdetails')}}", {
//     asycaccesscode:String(accode)
//     }, function(data) {
//         // console.log(data)
//         metadata = data.speakerdetails.current.workerMetadata
//         task = data.speakerdetails.task
//         console.log (metadata, task)
//         // accesscode = data.speakerdetails.accesscode
//         $('#accesscode').attr('value', accode)

//         name = metadata.name
//         $('#idname').attr('value', name)
//         // 

//         agroup = metadata.agegroup
//         ageOption = '<option value="'+agroup+'" selected="selected">'+agroup+'</option>'
//         // document.getElementById('idage').innerHTML=""
//         // $('#idage').html(ageOption)                        
//         $('#idage').val(agroup).trigger('change');
//         // $('#idgender').select2("val", "25-60");
//         // console.log (agroup)

//         console.log("Current task value", task);
//         if (task === "SPEECH_DATA_COLLECTION") {
//           $('#idspeakerdetailsdiv').show();
//           $('#idspeakerdetailsdiv').attr('required', '');
//           $('#idspeakerdetailsdiv').attr('data-error', 'This field is required.')

//           gender = metadata.gender
//           // genderOption = '<option value="'+gender+'" selected="selected">'+gender+'</option>'
//           // $('#idgender').html(genderOption)
//           $('#idgender').val(gender).trigger('change');
//           console.log (gender)

//           elevel = metadata.educationlevel
//           elevelOption = '<option value="'+elevel+'" selected="selected">'+elevel+'</option>'
//           // $('#idelevel').html(elevelOption)
//           $('#idelevel').val(elevel).trigger('change');

//           // mediumpre = metadata.medium-of-education-after-12th
//           // mediumpost = metadata.medium-of-education-upto-12th

//           mediumupto12 = metadata.educationmediumupto12
//           mediumupto12option = ''
//           for (i=0; i<mediumupto12.length; i++) {
//             mediumupto12option += '<option value="'+mediumupto12[i]+'" selected="selected">'+mediumupto12[i]+'</option>'
//           }                        
//           // $('#idmediumpre').html(mediumupto12option)
//           $('#idmediumpre').val(mediumupto12).trigger('change');


//           mediumafter12 = metadata.educationmediumafter12
//           mediumafter12option = ''
//           for (i=0; i<mediumafter12.length; i++) {
//             mediumafter12option += '<option value="'+mediumafter12[i]+'" selected="selected">'+mediumafter12[i]+'</option>'
//           }                        
//           // $('#idmediumpost').html(mediumafter12option)
//           $('#idmediumpost').val(mediumafter12).trigger('change');

//           speakerotherlangs = metadata.speakerspeaklanguage
//           speakerotherlangsOption = ''
//           for (i=0; i<speakerotherlangs.length; i++) {
//             speakerotherlangsOption += '<option value="'+speakerotherlangs[i]+'" selected="selected">'+speakerotherlangs[i]+'</option>'
//           }                        
//           // $('#idotherlangs').html(speakerotherlangsOption)
//           $('#idotherlangs').val(speakerotherlangs).trigger('change');


//           // name = metadata.name
//           // $('#idname').attr('value', name)
//           place = metadata.recordingplace
//           // $('#idplace').attr('value', place)
//           $('#idplace').val(place).trigger('change');

//           ptype = metadata.typeofrecordingplace
//           ptypeOption = '<option value="'+ptype+'" selected="selected">'+ptype+'</option>'
//           // $('#idptype').html(ptypeOption)
//           $('#idptype').val(ptype).trigger('change');
//         }


//     });
//     return false;            
// });

$('#editbutton').click(function () {

    $('#formdisplay').find('input, select').attr('disabled', false);
    $('#editbutton').attr('hidden', true);
    // $('#idname').hidden();
    // $('#idage').attr('hidden', false);
    document.getElementById('idname').disabled = true;
    document.getElementById('idage').disabled = true;
    $('#accodeformheader').find('input, select').attr('disabled', true);
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
$('#closebutton').click(function () {
    buttonType = $(this).attr("id")
    activeform(buttonType)
    // activeform()
    // $('#formdisplay').find('input, select').attr('disabled', false);
    // $('#editbutton').attr('hidden', true)
})
// });


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
    sourceinpt += '<div id="formdisplay" style="display: block;">' +
        '<form role="form" method="post" action="/addnewspeakerdetails">';
    sourceinpt += '<div class="form-group">' +
        '<label for="idaudiosource">Audio Source </label> <br>' +
        '<select class="audiosourceclass" id="idaudiosource" name="audiosource" style="width:55%" >' +
        '</select><br>' +
        '</div>';
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
    speakerinpt += sourceinpt;

    speakerinpt += '<div id="idspeakerdetailsdiv" style="display: none;">' +
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
        '</div>' +

        '<input type="hidden" value="' +
        cur_id +
        '"name = "sourcecallpage" id="sourcecallpageid">' +

        '<button type="button" id="closebutton" class="btn btn-secondary" data-dismiss="modal">Close</button>' +
        '<input type="submit" value="Submit"> <br><br>' +

        '</form>' +
        '</div>';
    $("#addnewspeakerform").append(speakerinpt);
    addNewSpeakerSelect2();
    addNewSpeakerFormEvents();
}

function addNewSpeakerSelect2() {

    $('#idaudiosource').select2({
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
        placeholder: '--Type Of City:--',
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
        if (sourceVal === "field") {
            $('#idsubsourcediv').hide();
            $('#idsubsourcediv').removeAttr('required');
            $('#idsubsourcediv').removeAttr('data-error');
            $('#idspeakerdetailsdiv').show();
            $('#idspeakerdetailsdiv').attr('required', '');
            $('#idspeakerdetailsdiv').attr('data-error', 'This field is required.')

        }
        else if (sourceVal === "internet") {
            $('#idspeakerdetailsdiv').hide();
            $('#idspeakerdetailsdiv').removeAttr('required');
            $('#idspeakerdetailsdiv').removeAttr('data-error');
            $('#idsubsourcediv').show();
            $('#idsubsourcediv').attr('required', '');
            $('#idsubsourcediv').attr('data-error', 'This field is required.')

        }
        else {
            $('#idspeakerdetailsdiv').hide();
            $('#idspeakerdetailsdiv').removeAttr('required');
            $('#idspeakerdetailsdiv').removeAttr('data-error');
            $('#idsubsourcediv').hide();
            $('#idsubsourcediv').removeAttr('required');
            $('#idsubsourcediv').removeAttr('data-error');
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
}