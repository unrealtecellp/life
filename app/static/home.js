// 1c10c4e2fe71e0f346311f143ac085b119561e67
function createSelectElement(elevalue, activeprojectname) {
    // console.log(activeprojectname)
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
        placeholder: 'select'
        // data: usersList,
        // allowClear: true
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

// event fire from thew home page to get the route for View/Edit Project button
$("#idhomevieweditbtn").click(function() {

        $.ajax({
        data : {},
        type : 'GET',
        url : '/projecttype',
        success: function(response){
            projectType = response.projectType;
            shareMode = response.shareMode;
            activeprojectform = response.activeprojectform;
            windowHref = window.location.href
            pathname = window.location.pathname
            lastIndexOfPathname = windowHref.lastIndexOf(pathname)
            // console.log(projectType,);
            console.log(shareMode);
            if (projectType === 'transcriptions') {
                console.log(activeprojectform);
                if ('Sentence Language' in activeprojectform) {
                    if (shareMode === 0) {
                        window.location.href = windowHref.slice(0, lastIndexOfPathname) +  
                        windowHref.slice(lastIndexOfPathname).replace(pathname, "/audiobrowse");
                    }
                    else if (shareMode >= 2) {
                        window.location.href = windowHref.slice(0, lastIndexOfPathname) +  
                        windowHref.slice(lastIndexOfPathname).replace(pathname, "/enternewsentences");
                    }
                }
                else {
                    if (shareMode === 0) {
                        window.location.href = windowHref.slice(0, lastIndexOfPathname) +  
                        windowHref.slice(lastIndexOfPathname).replace(pathname, "/lifedata/transcription/audiobrowse");
                    }
                    else if (shareMode >= 2) {
                        window.location.href = windowHref.slice(0, lastIndexOfPathname) +  
                        windowHref.slice(lastIndexOfPathname).replace(pathname, "/lifedata/transcription/home");
                    }
                }
                // if (shareMode === 0) {
                //     window.location.href = windowHref.slice(0, lastIndexOfPathname) +  
                //     windowHref.slice(lastIndexOfPathname).replace(pathname, "/lifedata/transcription/audiobrowse");
                // }
                // else if (shareMode >= 2) {
                //     window.location.href = windowHref.slice(0, lastIndexOfPathname) +  
                //     windowHref.slice(lastIndexOfPathname).replace(pathname, "/lifedata/transcription/home");
                // }
            }
            else if (projectType === 'questionnaires') {
                window.location.href = windowHref.slice(0, lastIndexOfPathname) +  
                                        windowHref.slice(lastIndexOfPathname).replace(pathname, '/lifeques/questionnaire');
                // window.location.href = window.location.href.replace(pathname, '/lifeques/questionnaire');
            }
            else if (projectType === 'text') {
                window.location.href = windowHref.slice(0, lastIndexOfPathname) +  
                                        windowHref.slice(lastIndexOfPathname).replace(pathname, '/easyAnno/textAnno');
                // window.location.href = window.location.href.replace(pathname, '/lifeques/questionnaire');
            }
            else if (projectType === 'validation') {
                window.location.href = windowHref.slice(0, lastIndexOfPathname) +  
                                        windowHref.slice(lastIndexOfPathname).replace(pathname, '/lifedata/validation');
                // window.location.href = window.location.href.replace(pathname, '/lifeques/questionnaire');
            }
            else if (projectType === 'crawling') {
                window.location.href = windowHref.slice(0, lastIndexOfPathname) +  
                                        windowHref.slice(lastIndexOfPathname).replace(pathname, "/lifedata/crawler");
            }
            else if (projectType === 'annotation') {
                window.location.href = windowHref.slice(0, lastIndexOfPathname) +  
                                        windowHref.slice(lastIndexOfPathname).replace(pathname, "/lifedata/annotation");
            }
            else {
                window.location.href = windowHref.slice(0, lastIndexOfPathname) +  
                                        windowHref.slice(lastIndexOfPathname).replace(pathname, "/enternewlexeme");
            }
        }
    })
});