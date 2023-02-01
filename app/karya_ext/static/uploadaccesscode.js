function createSelectElement(key, elevalue, type, quesdatavalue) {
    // console.log(quesdatavalue)
    var qform = '';
    var keyid = key.replace(new RegExp(' ', 'g'), '_');
    qform += '<div class="form-group">'+
              '<label for="'+keyid+'">'+key+'</label><br>';
    if (type === 'multiple') {
      qform += '<select class="uploadaccodeselect" id="'+keyid+'" name="'+key+'" multiple="'+type+'" style="width: 55%" required>';
    }
    else {
      qform += '<select class="uploadaccodeselect" id="'+keyid+'" name="'+key+'" style="width: 55%" required>';
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
    qform += '</select></div>';
  
    return qform;
  }
  

function uploadaccesscodeform(uploadacesscodemetadata, projecttype) {
    // console.log(uploadacesscodemetadata);
    var uploadaccodeform = ''
    for (let [key, value] of Object.entries(uploadacesscodemetadata)) {
        // console.log(key, value);
        if (key === 'elicitation') {
            uploadaccodeform += createSelectElement(key, value, '', [])
        }
        else if (key === 'domain') {
          if (projecttype === 'questionnaires') {
            value.splice(0, 0, 'all');
          }
          // console.log(value);
          // value.splice(0, 0, 'all');
          // console.log(value);
          uploadaccodeform += createSelectElement(key, value, '', [])
        }
        else {
            uploadaccodeform += createSelectElement(key, value, '', [])
        }
    }

    $('#uploadaccode').html(uploadaccodeform);
    $('.uploadaccodeselect').select2({
        placeholder: 'select',
        // data: usersList,
        // allowClear: true
    });

}