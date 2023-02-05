$(document).ready(function() {  
    $(".POS").click(function() {
        // console.log('POS')
        predictPOS();
        var $users = 'POS'
        $.getJSON('/automatepos', {
                a:String($users)
        }, function(data) {
            // console.log(data.users)
        });
        return false; 
    });
    $(".MORPH").click(function() {
        console.log('MORPH')
     });
  });

function predictPOS() {
    $(".removePreviousPosInput").remove();
    console.log('predictPOS')
    var posinpt = '';

    posinpt += '<div class="removePreviousPosInput"></br><div class="col-sm-5 "><div class="form-group"><div class="input-group">'+
                '<input type="text" class="form-control" name="predictedpos"'+
                'placeholder="Enter word to get its POS" id="predictedpos">'+
                '<div class="input-group-btn">'+
                '<button class="btn btn-success" type="button" id="predictedposbtn" onclick="predictedPOS();">'+
                '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'+ 
                '</button></div>'+
                '</div></div></div><div class="addshowpos"></div><br/></div>';

    $(".predictpos").append(posinpt);
}

function predictedPOS() {
    removeShowPOS()
    console.log('predictedPOSbtn')
    var word = []
    word.push(document.getElementById("predictedpos").value.trim()); // Find the text

    console.log(word);

    $.getJSON('/predictPOSNaiveBayes', {
            a:String(word)
    }, function(data) {
        console.log(data.predictedPOS)
        showPredictedPOS(data.predictedPOS[0][1]);
    });
        return false;
}


// remove show pos element
function removeShowPOS() {
    $(".showpos").remove();

    var inptshowpos = '';
    inptshowpos += '<div class="showpos"></div>';
    
    $(".addshowpos").append(inptshowpos);
  }

function showPredictedPOS(predictedpos) {
    var showpos = ''

    showpos += '<span>'+predictedpos+'</span>';

    $(".showpos").append(showpos);
}