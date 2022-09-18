var usersToShare = ''

// share project button on dictionary view page
$(document).ready(function() {  
      $.getJSON('/userslist', {
      }, function(data) {
        // console.log(data.usersList)
        for (let [key, value] of Object.entries(data.usersList)){
          usersToShare += '<option value="'+value+'">'+value+'</option>';

        };
        $('#shareProjectSelect').append(usersToShare)
        var shareMode = '<input type="checkbox" id="view" name="view" value="view">'+
                        '<label for="view">&nbsp; View</label><br>'+
                        '<input type="checkbox" id="download" name="download" value="download">'+
                        '<label for="download">&nbsp; Download</label><br>'+
                        '<input type="checkbox" id="edit" name="edit" value="edit">'+
                        '<label for="edit">&nbsp; Edit</label><br>'+
                        '<input type="checkbox" id="add" name="add" value="add">'+
                        '<label for="add">&nbsp; Add</label><br>'+
                        '<input type="checkbox" id="delete" name="delete" value="delete">'+
                        '<label for="delete">&nbsp; Delete</label><br>';

        $('.sharemode').append(shareMode);
      });
      $('#myShareProjectModal').on('show.bs.modal', function() {
        $('#shareProjectSelect').select2({
        placeholder: 'Share with',
        // data: usersList,
        allowClear: true
      });
      })
      
      $('#myShareProjectModal').on('hidden.bs.modal', function() {
        $('#shareProjectSelect').select2('destroy');
      })
  });

$(".shareprojectwith").click(function() {
  alert('Project sharing successful :)');
  });

