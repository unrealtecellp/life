var ele = '';

ele += '<div class="modal fade" id="browseShareModal" tabindex="-1" role="dialog" aria-labelledby="browseShareModalLabel">'+
        '<div class="modal-dialog" role="document">'+
        '<div class="modal-content">'+
        '<div class="modal-header">'+
        '<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>'+
        '<h4 class="modal-title" id="browseShareModalLabel">Share</h4>'+
        '</div>'+
        '<div class="modal-body">'+
        '<div class="row">'+
        '<div class="col-xs-12">'+
        '<div class="form-group">'+
        '<select name="" id="browseShareSelect"  multiple="multiple" style="width: 100%">'+
        '</select>'+
        '</div>'+
        '</div>'+
        '</div>'+
        '</div>'+
        '<div class="modal-footer">'+
        '<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>'+
        '<button type="button" class="btn btn-primary browsesharewith" data-dismiss="modal">Share</button>'+
        '</div>'+
        '</div>'+
        '</div>'+
        '</div>';
$('#plugBrowseShareModal').html(ele);