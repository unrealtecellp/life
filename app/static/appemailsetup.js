$('#editbutton').click(function () {

    $('#formdisplay').find('input').attr('readonly', false);
    $('#editbutton').attr('disabled', true);
    $('#submitbutton').attr('disabled', false);
    // $('#accodeformheader').find('input, select').attr('disabled', true);
});