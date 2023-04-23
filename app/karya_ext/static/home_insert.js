$("#updatespeakerids").click(function() {
    var updatelostfiles = Object();
    var access_code = document.getElementById("access_code").value;
    var speaker_id = document.getElementById("speaker_id").value;
    var pimobilenumber = document.getElementById("pimobilenumber").value;
    var karyaotp = document.getElementById("karyaotp").value;
    updatelostfiles['access_code'] = access_code;
    updatelostfiles['speaker_id'] = speaker_id;
    updatelostfiles['pimobilenumber'] = pimobilenumber;
    updatelostfiles['karyaotp'] = karyaotp;
    console.log(updatelostfiles)
    $.post( "/karyaext/update_speaker_ids", {
      a: JSON.stringify(updatelostfiles)
    })
    .done(function( data ) {
      window.location.reload();
    });
  });



  