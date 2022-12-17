function createSelectElement(elevalue, activeprojectname) {
    console.log(activeprojectname)
    var qform = '';
    //   qform += '<select class="allprojectslistselect" id="'+keyid+'" name="'+key+'" style="width: 100%" required>';
    qform += '<select class="allprojectslistselect" id="allprojectslistselectid" style="width: 60%">';
    qform += '<option selected disabled>Change Active Project</option>';

    for (let i=0; i<elevalue.length; i++) {
        eval = elevalue[i]
        if (activeprojectname.includes(eval)) {
            qform += '<option value="'+eval+'" selected disabled>'+eval+'</option>';  
        }
        else {
            qform += '<option value="'+eval+'">'+eval+'</option>';
        }
    }
    qform += '</select></div>';

    return qform;
  }

function allProjects(allProjectsList) {
    var projectslist = '';
    // console.log(allProjectsList);
    projectslist += createSelectElement(allProjectsList, []);

    $('#allprojectslist').html(projectslist);

    $('.allprojectslistselect').select2({
        placeholder: 'select',
        // data: usersList,
        allowClear: true
    });

    // event fire from thew home page all projects list select element
    $("#allprojectslistselectid").change(function() {
        let projectname = document.getElementById('allprojectslistselectid');
        pname = projectname.value;

        $.ajax({
        data : {
            a : pname
        },
        type : 'GET',
        url : '/activeprojectname'
        }).done(function(){
            // window.location.reload();
            loc = window.location.href
            window.location.assign(loc)
    
        });
    });
}
