
function myFunction(not_mapped_data) {
  // console.log(not_mapped_data);
  
  var inpt = '';

  for (let [key, value] of Object.entries(not_mapped_data)){
    // var encodedStr = key.replace(/[\u00A0-\u9999<>\&]/g, function(i) {
    //   return '&#'+i.charCodeAt(0)+';';
    // });
    key = key.replaceAll('"', '&#x22;');
    // console.log(key);
    console.log(key, value);
    if (value.constructor === Array) {
      inpt += '<div class="col"><div class="form-group">'+
              '<label for="'+key+'">'+key+'</label>'+
              '<select class="form-control '+key+'" name="'+key+'" style="width: 100%" required>'
      for (var i = 0; i < value.length; i++) {
        inpt += '<option value="'+value[i]+'">'+value[i]+'</option>';
      }
      inpt += '</select></div></div>';
    }
    else {
      inpt += '<div class="col"><div class="form-group">'+
                  '<label for="'+key+'">'+key+'</label>'+
                  '<input type="text" class="form-control" id="'+key+'" name="'+key+'" value="'+value+'">'+
                  '</div></div>'; 
    }
    $('.lexemekeymapping').append(inpt);
    inpt = '';         
    }
  }
  