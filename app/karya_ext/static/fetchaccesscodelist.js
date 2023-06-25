function createSelectElement(key, elevalue, type, quesdatavalue, classname) {
    // console.log(quesdatavalue)
    tempKey = key.replace('_', ' ')
    var qform = '';
    var keyid = key.replace(new RegExp(' ', 'g'), '_');
    // qform += '<div class="form-group">'+
    qform += '<label for="'+keyid+'">'+tempKey+': </label>';

    if (type === 'multiple') {
      qform += '<select class="'+classname+'" id="'+keyid+'" name="'+key+'" multiple="'+type+'" style="width: 37%" required>';
    }
    else {
      qform += '<select class="'+classname+'" id="'+keyid+'" name="'+key+'" style="width: 37%" required>';
    }
    
    for (let i=0; i<elevalue.length; i++) {
      eval = elevalue[i]
      // console.log(eval, quesdatavalue, quesdatavalue.includes(eval))
      if (type === 'multiple') {
        if (quesdatavalue.includes(eval)) {
          qform += '<option value="'+eval+'" selected>'+eval+'</option>';  
        }
        else {
          qform += '<option value="'+eval+'">'+eval+'</option>';
        }
      }
      else {
        if (quesdatavalue.includes(eval)) {
          // console.log(eval, quesdatavalue)
          qform += '<option value="'+eval+'" selected>'+eval+'</option>';  
        }
        else {
          qform += '<option value="'+eval+'">'+eval+'</option>';
        }
      }
    }
    qform += '</select>';
    // qform += '</select></div>';
  
    return qform;
  }

function fetchAccessCodeList(fetchaccesscodelist) {
    // console.log(fetchaccesscodelist);
    var fetchaccodeform = ''
    fetchaccodeform += createSelectElement('access_code', fetchaccesscodelist, '', [], 'fetchaccodeselect')

    $('#piaccesscode').html(fetchaccodeform);
    $('.fetchaccodeselect').select2({
        placeholder: 'select',
        // data: usersList,
        allowClear: true
    });
}

function karyaSpeakerIdsList(karya_speaker_ids) {
  // console.log(karya_speaker_ids);
  var karyaspeakeridform = ''
  karyaspeakeridform += createSelectElement('speaker_id', [], '', [], 'karyaspeakeridselect')

  $('#idforworker').html(karyaspeakeridform);
  $('.karyaspeakeridselect').select2({
      placeholder: 'select',
      data: karya_speaker_ids,
      allowClear: true
  });
}



function fetchTransAccessCodeList(fetchtransaccesscodelist) {
  // console.log(fetchaccesscodelist);
  var fetchtransaccodeform = ''
  fetchtransaccodeform += createSelectElement('transcription_access_code', fetchtransaccesscodelist, '', [], 'fetchtransaccodeselect')

  $('#pitransaccesscode').html(fetchtransaccodeform);
  $('.fetchtransaccodeselect').select2({
      placeholder: 'select',
      // data: usersList,
      allowClear: true
  });
}


function fetchVerAccessCodeList(fetchveraccesscodelist) {
  // console.log(fetchaccesscodelist);
  var fetchveraccodeform = ''
  fetchveraccodeform += createSelectElement('verification_access_code', fetchveraccesscodelist, '', [], 'fetchveraccodeselect')

  $('#piveraccesscode').html(fetchveraccodeform);
  $('.fetchveraccodeselect').select2({
      placeholder: 'select',
      // data: usersList,
      allowClear: true
  });
}
