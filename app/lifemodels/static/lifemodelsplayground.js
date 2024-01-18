function modelsList(models) {
    // console.log(models);
    // models = ['123'];
    $('#myModelPlaygroundListSelect2').select2({
        // tags: true,
        placeholder: 'Select Model Name',
        data: models,
        // allowClear: true
    });
    $('#myModelPlaygroundListSelect2').val(models[models.length-1]); // Select the option with a value of '1'
    $('#myModelPlaygroundListSelect2').trigger('change'); // Notify any JS components that the value changed
}

function uploadFile(checkboxEle) {
    if (checkboxEle.checked) {
        document.getElementById('modelPlaygroundFile').style.display = 'block';
        document.getElementById('myModelPlaygroundFile').required = true;
        document.getElementById('myModelPlaygroundFile').disabled = false;

        document.getElementById('modelPlaygroundTextArea').style.display = 'none';
        document.getElementById('myModelPlaygroundTextArea').required = false;
        document.getElementById('myModelPlaygroundTextArea').disabled = true;
    }
    else {
        document.getElementById('modelPlaygroundTextArea').style.display = 'block';
        document.getElementById('myModelPlaygroundTextArea').required = true;
        document.getElementById('myModelPlaygroundTextArea').disabled = false;

        document.getElementById('modelPlaygroundFile').style.display = 'none';
        document.getElementById('myModelPlaygroundFile').required = false;
        document.getElementById('myModelPlaygroundFile').disabled = true;
    }

}
