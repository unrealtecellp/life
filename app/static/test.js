var questionaireprojectform = {
  "username": "alice",
  "projectname": "alice_project_1",
  "Elicitation Method": ["select", ["Translation", "Agriculture", "Sports"]],
  "Domain": ["multiselect", ["General", "Agriculture", "Sports"]],
  "Language": ["text", ["English", "Hindi"]],
  "Script": ["", ["latin", "devanagari"]],
  "Prompt Audio": ["file", ["audio"]],
  "Target": ["multiselect", ["case", "classifier", "adposition"]]
}

function createInputElement(key, elevalue, type) {
  var qform = '';
  for (let i=0; i<elevalue.length; i++) {
    eval = key + ' ' + elevalue[i]
    var keyid = eval.replace(new RegExp(' ', 'g'), '_');
    qform += '<div class="form-group">'+
              '<label for="'+ keyid +'">'+ eval +'</label>'+
              '<input type="'+type+'" class="form-control" id="'+ keyid +'"'+ 
              'placeholder="'+ eval +'" name="'+ eval +'" required>'+
              '</div>';
  }

  return qform;
}

function createSelectElement(key, elevalue, type) {
  var qform = '';
  var keyid = key.replace(new RegExp(' ', 'g'), '_');
  qform += '<div class="form-group">'+
            '<label for="'+keyid+'">'+key+'</label>';
  if (type === 'multiple') {
    qform += '<select class="quesselect" id="'+keyid+'" name="'+key+'" multiple="'+type+'" style="width: 100%" required>';
  }
  else {
    qform += '<select class="quesselect" id="'+keyid+'" name="'+key+'" style="width: 100%" required>';
  }
  
  for (let i=0; i<elevalue.length; i++) {
    eval = elevalue[i]
    qform += '<option value="'+eval+'">'+eval+'</option>';
  }
  qform += '</select></div>';

  return qform;
}

var quesform = '';
quesform += '<div class="col-md-6">';
quesform += '<form action="{{ url_for(\'newproject\') }}" method="POST" enctype="multipart/form-data">';
for (let [key, value] of Object.entries(questionaireprojectform)) {
  // console.log(key, value, value[0], typeof value);
  eletype = value[0];
  elevalue = value[1];
  if (eletype === 'text') {
    quesform += createInputElement(key, elevalue, eletype)
  }
  else if (eletype === 'file') {
    quesform += createInputElement(key, elevalue, eletype)
  }
  else if (eletype === 'select') {
    quesform += createSelectElement(key, elevalue, '')
  }
  else if (eletype === 'multiselect') {
    quesform += createSelectElement(key, elevalue, 'multiple')
  }
}
quesform += '<input class="btn btn-lg btn-primary" type="submit" value="Submit">';
quesform += '</form>'
quesform += '</div>';
$('#questionnaire').html(quesform);
$('.quesselect').select2({
  placeholder: 'select',
  // data: usersList,
  allowClear: true
});
