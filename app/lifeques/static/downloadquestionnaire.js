$(document).ready(function () {
  $("#karyajson").click(function () {
    runLoader();
    let quesData = {};
    quesData['downloadFormat'] = "karyajson";
    quesData['getAudio'] = $('#getAudioId').prop("checked");
    //   console.log(questionnaire)
    $.ajax({
      url: '/lifeques/downloadquestionnaire',
      type: 'GET',
      data: { 'data': JSON.stringify(quesData) },
      contentType: "application/json; charset=utf-8",
      success: function (response) {
        // window.location.href = "http://127.0.0.1:5000/downloadjson";
        window.location.href = window.location.href.replace("questionnaire", "lifequesdownloadquestionnaire");
        stopLoader();
        // window.location.reload();
        // console.info(response);
      }
    });
    return false;
  });
});

$(document).ready(function () {
  $("#json").click(function () {
    runLoader();
    let quesData = {};
    quesData['downloadFormat'] = "karyajson";
    quesData['getAudio'] = $('#getAudioId').prop("checked");
    //   console.log(questionnaire)
    $.ajax({
      url: '/lifeques/downloadquestionnaire',
      type: 'GET',
      data: { 'data': JSON.stringify(quesData) },
      contentType: "application/json; charset=utf-8",
      success: function (response) {
        // window.location.href = "http://127.0.0.1:5000/downloadjson";
        window.location.href = window.location.href.replace("questionnaire", "lifequesdownloadquestionnaire");
        stopLoader();
        // window.location.reload();
        // console.info(response);
      }
    });
    return false;
  });
});

$(document).ready(function () {
  $("#karyajson2").click(function () {
    runLoader();
    let quesData = {};
    quesData['downloadFormat'] = "karyajson2";
    quesData['getAudio'] = $('#getAudioId').prop("checked");
    //   console.log(questionnaire)
    $.ajax({
      url: '/lifeques/downloadquestionnaire',
      type: 'GET',
      data: { 'data': JSON.stringify(quesData) },
      contentType: "application/json; charset=utf-8",
      success: function (response) {
        // window.location.href = "http://127.0.0.1:5000/downloadjson";
        window.location.href = window.location.href.replace("questionnaire", "lifequesdownloadquestionnaire");
        stopLoader();
        // window.location.reload();
        // console.info(response);
      }
    });
    return false;
  });
});

$(document).ready(function () {
  $("#karyajson2audio").click(function () {
    runLoader();
    let quesData = {};
    quesData['downloadFormat'] = "karyajson2";
    quesData['getAudio'] = $('#getAudioId').prop("checked");

    //   console.log(questionnaire)
    $.ajax({
      url: '/lifeques/downloadquestionnaire',
      type: 'GET',
      data: { 'data': JSON.stringify(quesData) },
      contentType: "application/json; charset=utf-8",
      success: function (response) {
        // window.location.href = "http://127.0.0.1:5000/downloadjson";
        window.location.href = window.location.href.replace("questionnaire", "lifequesdownloadquestionnaire");
        stopLoader();
        // window.location.reload();
        // console.info(response);
      }
    });
    return false;
  });
});

$(document).ready(function () {
  $("#xlsx").click(function () {
    runLoader();
    let quesData = {};
    quesData['downloadFormat'] = "xlsx";
    quesData['getAudio'] = $('#getAudioId').prop("checked");
    //   console.log(questionnaire)
    $.ajax({
      url: '/lifeques/downloadquestionnaire',
      type: 'GET',
      data: { 'data': JSON.stringify(quesData) },
      contentType: "application/json; charset=utf-8",
      success: function (response) {
        // window.location.href = "http://127.0.0.1:5000/downloadjson";
        window.location.href = window.location.href.replace("questionnaire", "lifequesdownloadquestionnaire");
        stopLoader();
        // window.location.reload();
        // console.info(response);
      }
    });
    return false;
  });
});
