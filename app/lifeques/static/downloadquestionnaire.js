$(document).ready(function() {
    $("#karyajson").click(function() {
      questionnaire['downloadFormat'] = "karyajson";
    //   console.log(questionnaire)
      $.ajax({
            url: '/lifeques/downloadquestionnaire',
            type: 'GET',
            data: {'data': JSON.stringify(questionnaire)},
            contentType: "application/json; charset=utf-8", 
            success: function(response){
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("questionnaire", "lifequesdownloadquestionnaire");
                // window.location.reload();
                // console.info(response);
            }
        });
      return false; 
    });
});

$(document).ready(function() {
  $("#json").click(function() {
    questionnaire['downloadFormat'] = "karyajson";
  //   console.log(questionnaire)
    $.ajax({
          url: '/lifeques/downloadquestionnaire',
          type: 'GET',
          data: {'data': JSON.stringify(questionnaire)},
          contentType: "application/json; charset=utf-8", 
          success: function(response){
              // window.location.href = "http://127.0.0.1:5000/downloadjson";
              window.location.href = window.location.href.replace("questionnaire", "lifequesdownloadquestionnaire");
              // window.location.reload();
              // console.info(response);
          }
      });
    return false; 
  });
});