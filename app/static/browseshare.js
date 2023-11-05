var usersToShare = ''
// share project button on dictionary view page
$(document).ready(function() {
      $.getJSON('/browseshareuserslist', {
      }, function(data) {
        // console.log(data.usersList);
        // usersToShare = data.usersList;
        for (let [key, value] of Object.entries(data.usersList)){
          usersToShare += '<option value="'+value+'">'+value+'</option>';

        };
        $('#browseShareSelect').append(usersToShare)
      });
      $('#browseShareSelect').select2({
        placeholder: 'Share with',
        // data: usersToShare,
        allowClear: true
      });
      $('#browseShareModal').on('show.bs.modal', function() {
        // console.log('show.bs.modal');
        document.getElementById("browseShareSelect").style.display = "block";
        document.getElementById("browsesharebtn").style.display = "inline";
        $('#browseShareSelect').select2({
          placeholder: 'Share with',
          // data: usersList,
          allowClear: true
        });
        // if (document.getElementById("browseShareSelectMode").value === "share") {

        //   $('#browseShareSelect').select2({
        //     placeholder: 'Share with',
        //     // data: usersList,
        //     allowClear: true
        //   });

        // }
        if (document.getElementById("browseShareSelectMode").value === "remove") {
          // $('#browseRemoveShareSelect').select2({
          //   placeholder: 'Remove Access For',
          //   // data: data.sharedWithUsers,
          //   allowClear: true
          // });
          document.getElementById("browseRemoveShareSelect").style.display = "none";
          document.getElementById("removesharedfileaccess").style.display = "none";
          $("#browseShareSelectMode").val(null).trigger('change');
          $('#browseShareSelectMode').select2({
            // placeholder: 'Share with',
            data: browseShareSelMode,
            // allowClear: true
          });
        }
      });
      
      $('#browseShareModal').on('hidden.bs.modal', function() {
        // console.log('hidden.bs.modal');
        if (document.getElementById("browseShareSelectMode").value === "share") {
          $('#browseShareSelect').select2('destroy');
        }
        else if (document.getElementById("browseShareSelectMode").value === "remove") {
          $('#browseRemoveShareSelect').select2('destroy');
        }
      });

      $(".browsesharewith").click(function() {
        // console.log('toggle');
        $('#browseShareModal').modal('toggle');
      });
  });
  