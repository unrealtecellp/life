
function hidedisplaydiv(x, y) {
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
    if (y.style.display === "block") {
        y.style.display = "none";
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
                placeholder: 'Select project to derive from',
                // data: usersList,
                allowClear: true
            });
        }
    );

}

$("#createnewdatabtn").click(function() {
    var x = document.getElementById("createnewdatasubbtn");
    var y = document.getElementById("derivefromdatasubbtn");
    hidedisplaydiv(x, y)
});

$("#derivefromdatabtn").click(function() {
    var x = document.getElementById("derivefromdatasubbtn");
    var y = document.getElementById("createnewdatasubbtn");
    hidedisplaydiv(x, y);
    addprojectslist();
});

$("#derivefromdataselect").change(function(){
    var derivedprojectform = '';
    var derivemode = ['copy', 'edit', 'update']
    var derivemodename = '';
    derivedprojectform += '<form action="{{ url_for(\'newproject\') }}" method="POST" enctype="multipart/form-data">';
    for (let i=0; i<derivemode.length; i++) {
        derivemodename = derivemode[i]
        derivedprojectform += '<input type="radio" id="'+derivemodename+'" name="derivemode" value="'+derivemodename+'">'+
                                '&nbsp;<label for="'+derivemodename+'">'+derivemodename+'</label>&emsp;';
    }
    derivedprojectform += '<input class="btn btn-lg btn-primary" type="submit" value="Submit">';
    derivedprojectform += '</form>';
    $('#derivefromdataform').html(derivedprojectform);
  }); 
