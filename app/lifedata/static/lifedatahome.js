function hidedisplaydiv(x, y, z) {
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
    if (y !== '') {
        if (y.style.display === "block") {
            y.style.display = "none";
        }
    }
    if (z !== '') {
        if (z.style.display === "block") {
            z.style.display = "none";
        }
    }
}

function addprojectslist() {
    $.getJSON('getprojectslist',
        {}, 
        function(data) {
            var projectslisttoshow = '';
            var projectslist = data.projectslist
            projectslisttoshow += '<option value="">'+""+'</option>';
            for (let i=0; i<projectslist.length; i++) {
                projectname = projectslist[i]
                projectslisttoshow += '<option value="'+projectname+'">'+projectname+'</option>';
            }
            $('#derivefromdataselect').html(projectslisttoshow)
            $('#derivefromdataselect').select2({
                placeholder: 'Select project to derive from'
                // data: usersList,
                // allowClear: true
            });
        }
    );

}

function addlanguagelist(derivedprojectvalue) {
    $.getJSON('getlanguagelist',
        {
            projectname: String(derivedprojectvalue)
        }, 
        function(data) {
            var languageslist = data.languageslist
            var dataSentenceLanguage = '<label for="iddatasentencelanguage">Sentence Language</label><br>'+
                                        '<select class="datasentencelanguageclass" id="iddatasentencelanguage" name="Sentence Language" style="width: 55%" required></select>'
    
            $('#datasentencelanguage').html(dataSentenceLanguage)
            $('.datasentencelanguageclass').select2({
                placeholder: 'Sentence Language',
                data: languageslist
                // allowClear: true
            });
        }
    );

}

$("#createnewdatabtn").click(function() {
    var x = document.getElementById("createnewdatasubbtn");
    var y = document.getElementById("derivefromdatasubbtn");
    var z = document.getElementById("dataform");
    hidedisplaydiv(x, y, z)
});

$("#derivefromdatabtn").click(function() {
    var x = document.getElementById("derivefromdatasubbtn");
    var y = document.getElementById("createnewdatasubbtn");
    var z = document.getElementById("dataform");
    hidedisplaydiv(x, y, z);
    addprojectslist();
});

$("#datamanualentrybtn").click(function() {
    var x = document.getElementById("dataform");
    var y = '';
    var z = '';
    hidedisplaydiv(x, y, z)
    $('#beforefield').empty();
    var transcriptioncheckbox = document.getElementById("idincludetranscription")
    // console.log(transcriptioncheckbox)
    if (transcriptioncheckbox !== null && transcriptioncheckbox.checked) {
        transcriptioncheckbox.checked = false;
        translangscriptid =  document.getElementById("idtranscriptionlangscript")
        translangscriptid.style.display = "none";
    }
});

$("#derivefromdataselect").change(function(){
    var derivedprojectvalue = document.getElementById("derivefromdataselect").value;
    console.log(derivedprojectvalue)
    var derivedprojectform = '';

    derivedprojectform += '<label for="idderivefromproject">Derive From Project</label>'+
                            '<input type="text" class="form-control" id="idderivefromproject"'+
                            'placeholder="Derive From Project" name="derivefromproject" value="'+derivedprojectvalue+'" style="width: 55%" readonly>'
    $('#beforefield').html(derivedprojectform);
    addlanguagelist(derivedprojectvalue);
    var x = document.getElementById("dataform");
    if (x.style.display === "none") {
        x.style.display = "block";
    }
  }); 
