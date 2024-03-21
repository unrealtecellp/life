$('#editbutton').click(function () {

    $('#formdisplay').find('input').attr('readonly', false);
    $('#formdisplay').find('select').attr('readonly', false);
    $('#editbutton').attr('disabled', true);
    $('#submitbutton').attr('disabled', false);
    // $('#accodeformheader').find('input, select').attr('disabled', true);
});

function addHFDataDetails(userData, adminData, userType) {
    $('#idapiTokens').select2({
        tags: true,
        placeholder: '--API Tokens--',
        // data: audioSource,
        allowClear: true
    });

    $('#idtaskType').select2({
        // tags: true,
        placeholder: '--Task Type--'
        // data: audioSource,
        // allowClear: true
    });

    $('#idauthorsList').select2({
        tags: true,
        placeholder: '--Featured Authors--',
        // data: audioSource,
        allowClear: true
    });

}