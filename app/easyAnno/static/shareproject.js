var usersToShare = ''

// share project button on dictionary view page
$(document).ready(function() {  
      $.getJSON('/userslist', {
      }, function(data) {
        for (let [key, value] of Object.entries(data.usersList)){
          usersToShare += '<option value="'+value+'">'+value+'</option>';

        };
        $('#shareProjectSelect').append(usersToShare)
      });
      $('#myShareProjectModal').on('show.bs.modal', function() {
        $('#shareProjectSelect').select2({
          placeholder: 'Share with',
          // data: usersList,
          allowClear: true
        });
      });
      
      $('#myShareProjectModal').on('hidden.bs.modal', function() {
        $('#shareProjectSelect').select2('destroy');
      });

      $(".shareprojectwith").click(function() {
        console.log("shareprojectwith")
        $('#myShareProjectModal').modal('toggle');
      });
  });
  