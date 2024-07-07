Dropzone.autoDiscover = false;

$("div#audiofileid").dropzone({
    url: "/lifedata/transcription/uploadaudiofiles",
    maxFilesize: 512,
    // autoProcessQueue: false,
    uploadMultiple: false,
    parallelUploads: 1,
    maxFiles: 1,
    paramName: "audiofile",
    init: function () {
        var myDropzone = this;
        myDropzone.on("sending", function (file, xhr, formData) {
            $(":input[name]", $("#newaudiouploadId")).each(function () {
                let eleName = this.name;
                let eleVal = $(':input[name=' + eleName + ']', $("#newaudiouploadId")).val();
                formData.append(eleName, eleVal);
            });
        });
    }

});

// Dropzone.options.audiofileid = { // The camelized version of the ID of the form element

//     // The configuration we've talked about above
//     autoProcessQueue: false,
//     uploadMultiple: true,
//     parallelUploads: 100,
//     maxFiles: 100,
//     maxFilesize: 512,

//     // The setting up of the dropzone
//     init: function () {
//         var myDropzone = this;

//         // First change the button to actually tell Dropzone to process the queue.
//         this.element.querySelector("button[type=submit]").addEventListener("click", function (e) {
//             // Make sure that the form isn't actually being sent.
//             e.preventDefault();
//             e.stopPropagation();
//             myDropzone.processQueue();
//         });

//         // Listen to the sendingmultiple event. In this case, it's the sendingmultiple event instead
//         // of the sending event because uploadMultiple is set to true.
//         this.on("sendingmultiple", function () {
//             // Gets triggered when the form is actually being sent.
//             // Hide the success button or the complete form.
//         });
//         this.on("successmultiple", function (files, response) {
//             // Gets triggered when the files have successfully been sent.
//             // Redirect user or notify of success.
//         });
//         this.on("errormultiple", function (files, response) {
//             // Gets triggered when there was an error sending the files.
//             // Maybe show form again, and notify user of error
//         });
//     }

// }