var ele = '';

ele += '<div class="modal fade" id="browseShareModal" tabindex="-1" role="dialog" aria-labelledby="browseShareModalLabel">'+
        '<div class="modal-dialog" role="document">'+
        '<div class="modal-content">'+
        '<div class="modal-header">'+
        '<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>'+
        '<h4 class="modal-title" id="browseShareModalLabel">Share Files</h4>'+
        '</div>'+
        '<div class="modal-body">'+
        // '<br><br>'+
        '<div class="row">'+
        '<div class="col-xs-12">'+
        '<div class="form-group">'+
        '<select name="" id="browseShareSelectMode" style="width: 100%;">'+
        '</select>'+
        '<br>'+
        '<br>'+
        '<select name="" id="browseShareSelect" multiple="multiple" style="width: 100%; display: block;">'+
        '</select>'+
        '<select name="" id="browseRemoveShareSelect" multiple="multiple" style="width: 100%; display: none;">'+
        '</select>'+
        '</div>'+
        '</div>'+
        '</div>'+
        '</div>'+
        '<div class="modal-footer">'+
        // '<button type="button" class="btn btn-sm btn-success pull-left" id="givefileaccess"  style="display: none;">'+
        // // '<span class="glyphicon glyphicon-share" aria-hidden="true"></span>'+
        // 'Give Access'+
        // '</button>'+
        '<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>'+
        '<button type="button" class="btn btn-sm btn-danger browsesharewith" id="removesharedfileaccess"  style="display: none;">'+
        // '<span class="glyphicon glyphicon-remove" aria-hidden="true"></span>'+
        'Remove Access'+
        '</button>'+
        '<button type="button" id="browsesharebtn" class="btn btn-primary browsesharewith" data-dismiss="modal">Share</button>'+
        '</div>'+
        '</div>'+
        '</div>'+
        '</div>';
$('#plugBrowseShareModal').html(ele);

var browseShareSelMode = ["share", "remove"]
$('#browseShareSelectMode').select2({
        // placeholder: 'Share with',
        data: browseShareSelMode,
        // allowClear: true
});
