$(document).ready(function () {
    $("#praattexgrid").click(function () {
        downloadFormat = "textgrid";
        send_details = { "format": downloadFormat, "latest": true, "includeAudio": false };
        // alert(downloadFormat)
        $.ajax({
            url: 'download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/textgrid; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#csv").click(function () {
        downloadFormat = "csv";
        send_details = { "format": downloadFormat, "latest": true, "includeAudio": false };
        // alert(downloadFormat)
        $.ajax({
            url: 'download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/csv; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#tsv").click(function () {
        downloadFormat = "tsv";
        send_details = { "format": downloadFormat, "latest": true, "includeAudio": false };
        // alert(downloadFormat)
        $.ajax({
            url: 'download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/tsv; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#xlsx").click(function () {
        downloadFormat = "xlsx";
        send_details = { "format": downloadFormat, "latest": true, "includeAudio": false };
        // alert(downloadFormat)
        $.ajax({
            url: 'download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/xlsx; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#json").click(function () {
        downloadFormat = "json";
        send_details = { "format": downloadFormat, "latest": true, "includeAudio": false };
        // alert(downloadFormat)
        $.ajax({
            url: 'download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/json; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});


$(document).ready(function () {
    $("#latex").click(function () {
        downloadFormat = "latex";
        send_details = { "format": downloadFormat, "latest": true, "includeAudio": false };
        // alert(downloadFormat)
        $.ajax({
            url: 'download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/tex; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#html").click(function () {
        downloadFormat = "html";
        send_details = { "format": downloadFormat, "latest": true, "includeAudio": false };
        // alert(downloadFormat)
        $.ajax({
            url: 'download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/html; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#markdown").click(function () {
        downloadFormat = "markdown";
        send_details = { "format": downloadFormat, "latest": true, "includeAudio": false };
        // alert(downloadFormat)
        $.ajax({
            url: 'download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/markdown; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#lifejson").click(function () {
        downloadFormat = "lifejson";
        send_details = { "format": downloadFormat, "latest": true, "includeAudio": false };
        // alert(downloadFormat)
        $.ajax({
            url: 'download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/json; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#mypraattexgrid").click(function () {
        downloadFormat = "textgrid";
        // alert(downloadFormat)
        send_details = { "format": downloadFormat, "latest": false, "includeAudio": false };
        $.ajax({
            url: 'download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/textgrid; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#mycsv").click(function () {
        downloadFormat = "csv";
        // alert(downloadFormat)
        send_details = { "format": downloadFormat, "latest": false, "includeAudio": false };
        $.ajax({
            url: 'download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/csv; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#mytsv").click(function () {
        downloadFormat = "tsv";
        // alert(downloadFormat)
        send_details = { "format": downloadFormat, "latest": false, "includeAudio": false };
        $.ajax({
            url: 'download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/tsv; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});


$(document).ready(function () {
    $("#myjson").click(function () {
        downloadFormat = "json";
        // alert(downloadFormat)
        send_details = { "format": downloadFormat, "latest": false, "includeAudio": false };
        $.ajax({
            url: 'download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/json; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});


$(document).ready(function () {
    $("#myxlsx").click(function () {
        downloadFormat = "xlsx";
        // alert(downloadFormat)
        send_details = { "format": downloadFormat, "latest": false, "includeAudio": false };
        $.ajax({
            url: 'download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/xlsx; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#mylatex").click(function () {
        downloadFormat = "latex";
        // alert(downloadFormat)
        send_details = { "format": downloadFormat, "latest": false, "includeAudio": false };
        $.ajax({
            url: 'download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/tex; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#myhtml").click(function () {
        downloadFormat = "html";
        // alert(downloadFormat)
        send_details = { "format": downloadFormat, "latest": false, "includeAudio": false };
        $.ajax({
            url: 'download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/html; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});

$(document).ready(function () {
    $("#mymarkdown").click(function () {
        downloadFormat = "markdown";
        // alert(downloadFormat)
        send_details = { "format": downloadFormat, "latest": false, "includeAudio": false };
        $.ajax({
            url: 'download/downloadtranscriptions',
            type: 'GET',
            data: { 'data': JSON.stringify(send_details) },
            contentType: "application/xlsx; charset=utf-8",
            success: function (response) {
                // window.location.href = "http://127.0.0.1:5000/downloadjson";
                window.location.href = window.location.href.replace("enternewsentences", "download/tgdownloader");
                // window.location.reload();
                // console.info(response);
            }
        });
        return false;
    });
});