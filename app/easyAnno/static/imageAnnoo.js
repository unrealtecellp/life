inpt = ''

function imageJS(projData) {
    console.log(projData)
    lastActiveId = projData["lastActiveId"]
    accessedOnTime = projData["accessedOnTime"]
    currentUser = projData['currentUser']
    inpt += '<span class="imageFormAlert"></span><div class="row">'+
            '<form name="saveimageanno" class="form-horizontal" action="/saveimageAnno" method="POST" onsubmit="return imagevalidateForm()">'+
            '<div class="col-sm-6">'+
            '<input type="hidden" id="accessedOnTime" name="accessedOnTime" value="'+accessedOnTime+'">'+
            '<input type="hidden" id="lastActiveId" name="lastActiveId" value="'+lastActiveId+'">'+
            '<input type="hidden" id="'+projData["imageFiles"]["filename"]+'" name="filename" value="'+projData["imageFiles"]["filename"]+'">'+
            '<p class="form-group" id="'+projData["imageFiles"]["filename"]+'"><strong>Image Name: '+projData["imageFiles"]["filename"]+'</strong></p>'+
            '<div class="form-group">'+
            '<label class="col" for="image">Image:</label><br>'+
            '<img class="responsive" id="'+projData["imageFiles"]["filename"]+'" src="data:image/png;base64,'+projData["imageFiles"]["image"]+'" alt="'+projData["imageFiles"]["filename"]+'">'+
            '</div>';
    inpt += '<div class="form-group">'+
            '<label class="col" for="text">Image Text:</label>'+
            '<div class="col imagetext">'+
            '</div>'+
            '</div>';
    inpt += '<div class="form-group">'+
            '<div class="col">'+
            '<button type="button" id="previous" class="btn btn-info btn-lg" onclick="previousImage()">Previous</button>'+
            '<button type="button" id="next" class="btn btn-lg btn-info pull-right" onclick="nextImage()">Next</button>'+
            '</div>'+
            '</div>';        
            // already annotated data. Open form in edit mode
            if ('currentUser' in projData) {
                console.log(projData['currentUser'])
                // text in image input box
                imgText = '<textarea class="form-control" id="imageText" name="imageText" rows="3">'+projData[currentUser]["imageText"]+'</textarea>';
                
                inpt += '</div><div class="col-sm-6">';
                if (projData[currentUser]["annotatedFLAG"] === 0) {
                    inpt += '<div class="col"><strong>Already Annotated: <span style="color:Tomato;">NO</span></strong></div>';
                }
                else {
                    inpt += '<div class="col"><strong>Already Annotated: <span style="color:MediumSeaGreen;">YES</span></strong></div>';
                }
                for (let [key, value] of Object.entries(projData["tagSet"])) {
                    inpt += '<br><div class="col"><strong>'+key+': </strong>';
                    for (let i=0; i<value.length; i++) {
                        if (projData[currentUser][key] === value[i]) {
                            console.log(key, value[i])
                            inpt += '<input class="form-check-input" type="radio" name="'+key+'" id="'+value[i]+'" value="'+value[i]+'" checked>'+
                                '<label class="form-check-label" for="'+value[i]+'">'+value[i]+'</label>';
                        }
                        else {
                            inpt += '<input class="form-check-input" type="radio" name="'+key+'" id="'+value[i]+'" value="'+value[i]+'">'+
                                    '<label class="form-check-label" for="'+value[i]+'">'+value[i]+'</label>';
                        }     
                    }
                    
                    inpt += '</div>';  
                    
                }
                key = 'Duplicate Image'
                inpt += '<br><div class="col"><strong>'+key+': </strong>';

                if (projData[currentUser]["Duplicate"] === 'Yes') {
                    inpt += '<input class="form-check-input" type="radio" name="'+key+'" id="Yes" value="Yes" checked>'+
                            '<label class="form-check-label" for="Yes">Yes</label>'+
                            '<input class="form-check-input" type="radio" name="'+key+'" id="No" value="No">'+
                            '<label class="form-check-label" for="No">No</label>';
                }
                else { 
                    inpt += '<input class="form-check-input" type="radio" name="'+key+'" id="Yes" value="Yes">'+
                            '<label class="form-check-label" for="Yes">Yes</label>'+
                            '<input class="form-check-input" type="radio" name="'+key+'" id="No" value="No" checked>'+
                            '<label class="form-check-label" for="No">No</label>';
                }
                inpt += '</div>';
                
                inpt += '<br><div class="col">'+
                        '<label class="col" for="text">Annotator Comment:</label>'+
                        '<div class="col">'+
                        '<input type="text" class="form-control" id="annotatorComment"'+
                        ' name="annotatorComment" value="'+projData[currentUser]["annotatorComment"]+'">'+
                        '</div>'+
                        '</div>';
            }
            // data is not annotated yet
            else {
                // text in image input box
                if ('imageText' in projData) {
                    imgText = '<textarea class="form-control" id="imageText" name="imageText" rows="3">'+projData["imageText"]+'</textarea>';
                }
                else{
                    imgText = '<textarea class="form-control" id="imageText" name="imageText" rows="3"></textarea>';
                }
                inpt += '</div><div class="col-sm-6">';
                inpt += '<div class="col"><strong>Already Annotated: <span style="color:Tomato;">NO</span></strong></div>';
                for (let [key, value] of Object.entries(projData["tagSet"])) {
                    console.log(key, value)
                    inpt += '<br><div class="col"><strong>'+key+': </strong>';
                    for (let i=0; i<value.length; i++) {
                        if (value[i].includes('NA') || value[i].includes('NC') || value[i].includes('NE') || value[i].includes('NG') || value[i].includes('No')) {
                            inpt += '<input class="form-check-input" type="radio" name="'+key+'" id="'+value[i]+'" value="'+value[i]+'" checked>'+
                                '<label class="form-check-label" for="'+value[i]+'">'+value[i]+'</label>';    
                        }
                        else {
                            if ('imageTextLang' in projData 
                                    && key === 'Language' 
                                    && projData["imageTextLang"] === value[i]) {
                                inpt += '<input class="form-check-input" type="radio" name="'+key+'" id="'+value[i]+'" value="'+value[i]+'" checked>'+
                                    '<label class="form-check-label" for="'+value[i]+'">'+value[i]+'</label>';
                            }
                            else {
                                inpt += '<input class="form-check-input" type="radio" name="'+key+'" id="'+value[i]+'" value="'+value[i]+'">'+
                                        '<label class="form-check-label" for="'+value[i]+'">'+value[i]+'</label>';
                            }
                        }     
                    }
                    
                    inpt += '</div>';  
                    
                }
                key = 'Duplicate Image'
                inpt += '<br><div class="col"><strong>'+key+': </strong>'+
                        '<input class="form-check-input" type="radio" name="'+key+'" id="Yes" value="Yes">'+
                        '<label class="form-check-label" for="Yes">Yes</label>'+
                        '<input class="form-check-input" type="radio" name="'+key+'" id="No" value="No" checked>'+
                        '<label class="form-check-label" for="No">No</label>'+
                        '</div>';
                
                inpt += '<br><div class="col">'+
                        '<label class="col" for="text">Annotator Comment:</label>'+
                        '<div class="col">'+
                        '<input type="text" class="form-control" id="annotatorComment"'+
                        ' name="annotatorComment">'+
                        '</div>'+
                        '</div>';
            }
            
            inpt += '<br><br><button type="submit" class="btn btn-lg btn-primary pull-right btn-block">Save</button>';
            inpt += '</div>';
            inpt += '</form></div>';

    $('.imagedata').append(inpt);
    $('.imagetext').append(imgText);    
}

$( document ).ready(function() {
    document.getElementById("NAG").onchange = function(){
        console.log(document.getElementById("NAG"))
        let aggIntensity = document.forms["saveimageanno"]["Aggression Intensity"].value;
        if (aggIntensity !== "") {
            document.getElementById(aggIntensity).checked = false
        }
    };
});


function changeAggIntensity(tag) {
    console.log(tag)
    if (tag == "NAG") {
        let aggIntensity = document.forms["saveimageanno"]["Aggression Intensity"].value;
        document.getElementById(aggIntensity).checked = false
    }
}
function imagevalidateForm() {
    $('.imageFormAlertDiv').remove();
    imageformalert = '';
    let language = document.forms["saveimageanno"]["Language"].value;
    if (language == "") {
    imageformalert += '<div class="alert alert-danger imageFormAlertDiv" role="alert">Language must be selected</div>';
      $('.imageFormAlert').append(imageformalert);
    //   alert("Language must be selected");
      return false;
    }
    let aggression = document.forms["saveimageanno"]["Aggression"].value;
    if (aggression == "CAG" || aggression == "OAG") {
        let aggIntensity = document.forms["saveimageanno"]["Aggression Intensity"].value;
        if (aggIntensity === "") {
            // alert("Aggression Intensity must be selected");
            imageformalert += '<div class="alert alert-danger imageFormAlertDiv" role="alert">Aggression Intensity must be selected</div>';
            $('.imageFormAlert').append(imageformalert);
            return false;
        }    
        // return false;
      }
  }
  
function previousImage() {
    lastActiveId = document.forms["saveimageanno"]["lastActiveId"].value
        $.ajax({
            url: '/loadpreviousimage',
            type: 'GET',
            data: {'data': JSON.stringify(lastActiveId)},
            contentType: "application/json; charset=utf-8", 
            success: function(response){
                window.location.reload();
            }
        });
        return false; 
}

function nextImage() {
    lastActiveId = document.forms["saveimageanno"]["lastActiveId"].value
        $.ajax({
            url: '/loadnextimage',
            type: 'GET',
            data: {'data': JSON.stringify(lastActiveId)},
            contentType: "application/json; charset=utf-8", 
            success: function(response){
                window.location.reload();
            }
        });
        return false; 
}

function unAnnotated() {
    unanno = '';
    console.log('unAnnotated');
    $('#uNAnnotated').remove();
    $.ajax({
        url: '/allunannotated',
        type: 'GET',
        data: {'data': JSON.stringify(unanno)},
        contentType: "application/json; charset=utf-8", 
        success: function(response){
            allunanno = response.allunanno;
            allanno = response.allanno;
            var inpt = '';
            inpt += '<select class="col-sm-3 allanno" id="allanno" onchange="loadAnnoText()">'+
                    '<option selected disabled>All Annotated</option>';
                    for (i=0; i<allanno.length; i++) {
                        inpt += '<option value="'+allanno[i]["imageId"]+'">'+allanno[i]["filename"]+'</option>';
                    }
            inpt += '</select>';
            inpt += '<select class="pr-4 col-sm-3" id="allunanno" onchange="loadUnAnnoText()">'+
                    '<option selected disabled>All Un-Annotated</option>';
                    for (i=0; i<allunanno.length; i++) {
                        inpt += '<option value="'+allunanno[i]["imageId"]+'">'+allunanno[i]["filename"]+'</option>';
                    }
            inpt += '</select>';
            $('.commentIDs').append(inpt);
        }
    });
    return false; 
}

function loadUnAnnoText() {
    textId = document.getElementById('allunanno').value;
    console.log(textId);
    $.ajax({
        url: '/loadunannotext',
        type: 'GET',
        data: {'data': JSON.stringify(textId)},
        contentType: "application/json; charset=utf-8", 
        success: function(response){
            window.location.reload();
        }
    });
    return false;
}

function loadAnnoText() {
    textId = document.getElementById('allanno').value;
    console.log(textId);
    $.ajax({
        url: '/loadunannotext',
        type: 'GET',
        data: {'data': JSON.stringify(textId)},
        contentType: "application/json; charset=utf-8", 
        success: function(response){
            window.location.reload();
        }
    });
    return false;
}
