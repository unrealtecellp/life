var usersToShare = ''

// share project button on dictionary view page
$(document).ready(function() {  
      $.getJSON('/browseshareuserslist', {
      }, function(data) {
        for (let [key, value] of Object.entries(data.usersList)){
          usersToShare += '<option value="'+value+'">'+value+'</option>';

        };
        $('#browseShareSelect').append(usersToShare)
      });
      $('#browseShareModal').on('show.bs.modal', function() {
        $('#browseShareSelect').select2({
          placeholder: 'Share with',
          // data: usersList,
          allowClear: true
        });
      });
      
      $('#browseShareModal').on('hidden.bs.modal', function() {
        $('#browseShareSelect').select2('destroy');
      });

      $(".browsesharewith").click(function() {
        $('#browseShareModal').modal('toggle');
      });
  });
  