// var script = [{
//     "id": "IPA",
//     "text": "IPA"
//     },
//     {
//     "id": "Roman",
//     "text": "Roman"
//     },
//     {
//     "id": "Devanagari",
//     "text": "Devanagari"
//     },
//     {
//     "id": "Bengali",
//     "text": "Bengali"
//     },
//   ];

// $(document).ready(function() {
//     $('.js-example-basic-single').select2({
//         tags: true,
//         placeholder: 'Script',
//         data: script,
//         allowClear: true

//     });
//     $('.script').select2({
//         tags: true,
//         placeholder: 'Script',
//         data: script,
//         allowClear: true
//     });
//     // $(".script").select2({
//     //     ajax: {
//     //       url: "/jsonfiles",
//     //       dataType: 'json',
//     //       delay: 100,
//     //       data: function (params) {
//     //         return {
//     //           q: params.term, // search term
//     //         };
//     //       },
//     //       cache: true
//     //     },
//     //     placeholder: 'Search for a repository',
//     //     minimumInputLength: 1,
//     //     templateResult: formatRepo,
//     //     templateSelection: formatRepoSelection
//     //   });
      
//     //   function formatRepo (repo) {
//     //     if (repo.loading) {
//     //       return repo.text;
//     //     }
      
//     //     var $container = $(
//     //       "<div class='select2-result-repository clearfix'>" +
//     //           "<div class='select2-result-repository__title'></div>" +
//     //       "</div>"
//     //     );
      
//     //     $container.find(".select2-result-repository__title").text(repo.full_name);
      
//     //     return $container;
//     //   }
      
//     //   function formatRepoSelection (repo) {
//     //     return repo.full_name || repo.text;
//     //   }

// });

$(document).ready(function() {

    $('#myModal').on('show.bs.modal', function() {
      $('#select2-sample').select2();
    })
    
    $('#myModal').on('hidden.bs.modal', function() {
      $('#select2-sample').select2('destroy');
    })
  });