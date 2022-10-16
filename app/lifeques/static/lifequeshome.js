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
            $('#derivefromquesselect').html(projectslisttoshow)
            $('#derivefromquesselect').select2({
                placeholder: 'Select project to derive from',
                // data: usersList,
                allowClear: true
            });
        }
    );

}

$("#createnewquesbtn").click(function() {
    var x = document.getElementById("createnewquessubbtn");
    var y = document.getElementById("derivefromquessubbtn");
    var z = document.getElementById("quesform");
    hidedisplaydiv(x, y, z)
});

$("#derivefromquesbtn").click(function() {
    var x = document.getElementById("derivefromquessubbtn");
    var y = document.getElementById("createnewquessubbtn");
    var z = document.getElementById("quesform");
    hidedisplaydiv(x, y, z);
    addprojectslist();
});

$("#quesmanualentrybtn").click(function() {
    var x = document.getElementById("quesform");
    var y = '';
    var z = '';
    hidedisplaydiv(x, y, z)
});

$("#derivefromquesselect").change(function(){
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
    $('#derivefromquesform').html(derivedprojectform);
  }); 
