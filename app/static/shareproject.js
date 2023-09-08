var shareModeObject = {
  'removeallaccess': -1,
  'view': 0,
  // 'download': 1,
  'edit': 2,
  'add':3,
  'delete': 4
}
var shareModeList = Object.keys(shareModeObject)
// console.log(shareModeList);
var shareMode = '';
var shareLatest = '';
var shareProjectActionOptions = ["share", "update", "remove"]

function shareModalBodyStructure(projectName='') {
  let ele = '';
  let subEle = '';
  ele += '<h4 id="myShareProjectModalLabel">Project Name: '+projectName+'</h4><hr>';
  ele += '<div class="row"><div class="col-xs-12"><div class="form-group">';
  subEle += '<select name="" id="shareProjectAction" style="width: 100%"></select><br><br>';
  subEle += '<select name="" id="shareProjectSelect" multiple="multiple" style="width: 100%"></select><br>';
  subEle += '<div id="shareLatest"></div><br>';
  subEle += '<select name="" id="shareSpeakerSelect" multiple="multiple" style="width: 100%"></select><br>';
  subEle += '<div class="sharemode"></div>';
  ele += subEle;
  ele += '</div></div></div>';

  $('#sharemodalbodystructure').append(ele);
}

function createrShareProjectAction(shareAction) {
  $('#shareProjectAction').select2({
    placeholder: 'Share Action',
    data: shareProjectActionOptions,
    // allowClear: true
  });
  // $('#shareProjectAction').val('remove');
  // $('#shareProjectAction').trigger('change');
}

function createShareUsersList(usersList) {
  let usersToShare = '';
  let shareuserlist = [];
  for (let [key, value] of Object.entries(usersList)){
    usersToShare += '<option value="'+value+'">'+value+'</option>';
    shareuserlist.push(value)
  };
  localStorage.setItem("shareuserlist", JSON.stringify(shareuserlist));
  $('#shareProjectSelect').append(usersToShare);
  $('#shareProjectSelect').select2({
    placeholder: 'Share with users',
    // data: usersList,
    allowClear: true
  });
}

function createShareLatestChecked() {
  let shareLatest = '';
  shareLatest += '<br><input type="checkbox" id="sharelatestchecked" name="sharelatestchecked" value="">'+
                    '<label for="sharelatestchecked">&nbsp; Share Annotations by Other Users</label><br>';
  $('#shareLatest').append(shareLatest);
}

function createShareSourcesList(sourceList) {
  let speakersToShare = '';
  let sharespeakerlist = [];
  for (let [key, value] of Object.entries(sourceList)){
    speakersToShare += '<option value="'+value+'">'+value+'</option>';
    sharespeakerlist.push(value)

  };
  localStorage.setItem("sharespeakerlist", JSON.stringify(sharespeakerlist));
  $('#shareSpeakerSelect').append(speakersToShare);
  $('#shareSpeakerSelect').select2({
    placeholder: 'source',
    // data: usersList,
    allowClear: true
  });
}

function createShareAccessControl(sharemodecount) {
  let shareAccessControlEle = '<hr><h4>Access Control:</h4>';
  if (sharemodecount == 0) {
    sharemodecount = 1;
  }
  for (i=0; i<=sharemodecount;i++) {
    // console.log(shareModeList[i]);
    if (shareModeList[i] !== undefined) {
      shareAccessControlEle += '<input type="radio" id="'+shareModeList[i]+'" name="sharemode" value="'+i+'">'+
                                '<label for="'+shareModeList[i]+'">&nbsp; '+shareModeList[i]+'</label><br>';
    }
  }
  $('.sharemode').append(shareAccessControlEle);
}

function createShareAdvanceAccessControl(shareInfo) {
  let shareAdvanceAccessControlEle = '';
  if (shareInfo["downloadchecked"] == "true" ||
        shareInfo["sharechecked"] == "true") {
      shareAdvanceAccessControlEle += '<hr><h4>Advanced Access Control:</h4>';
      if (shareInfo["downloadchecked"] == "true") {
        shareAdvanceAccessControlEle += '<input type="checkbox" id="downloadchecked" name="downloadchecked" value="">'+
                                        '<label for="downloadchecked">&nbsp; Allow Download</label>';
      }
      shareAdvanceAccessControlEle += '&nbsp;&nbsp;&nbsp;&nbsp;';
      if (shareInfo["sharechecked"] == "true") {
        shareAdvanceAccessControlEle += '<input type="checkbox" id="sharechecked" name="sharechecked" value="">'+
                                        '<label for="sharechecked">&nbsp; Access To Share Button</label><br>';
      }
    }
  $('.sharemode').append(shareAdvanceAccessControlEle);
}
// share project button on LiFE home page
// $(document).ready(function() { 
function buildShareInterface() {
  $.getJSON('/userslist', {
  }, function(data) {
    let shareAction = 'share';
    let projetName = data.projectName;
    let usersList = data.usersList;
    let sourceList = data.sourceList;
    let shareInfo = data.shareInfo;
    let sharemodecount = data.sharemode;
    // console.log('qwaaszxzx') 
    // console.log(data.usersList)
    console.log(shareInfo);
    if (shareInfo["sharechecked"] == "false") {
      $('#myShareProjectModal').modal('hide');
      window.location.reload();
      let alert = '<div class="alert alert-danger">'+
                  'You do not have "Share Project" access.'+
                  '</div>';
      $('#lifehomealert').html(alert);
    }

    shareModalBodyStructure(projetName);
    createrShareProjectAction(shareAction)
    createShareUsersList(usersList);
    if (shareInfo["sharelatestchecked"] == "true") {
      createShareLatestChecked();
    }
    createShareSourcesList(sourceList);
    createShareAccessControl(sharemodecount);
    createShareAdvanceAccessControl(shareInfo);
  });

  return false;
}
// });


$('#myShareProjectModal').on('show.bs.modal', function() {
  buildShareInterface();
});

$('#myShareProjectModal').on('hidden.bs.modal', function() {
  // $('#shareProjectSelect').select2('destroy');
  // $('#shareSpeakerSelect').select2('destroy');
  document.getElementById("sharemodalbodystructure").innerHTML = "";
});

$(".shareprojectwith").click(function() {
  alert('Project sharing successful :)');
  });
