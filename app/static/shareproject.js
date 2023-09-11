var shareModeObject = {
  // 'removeallaccess': -1,
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
  subEle += '<select name="" id="shareProjectSelect" style="width: 100%"></select><br>';
  subEle += '<div id="shareLatest"></div><br>';
  subEle += '<select name="" id="shareSpeakerSelect" multiple="multiple" style="width: 100%; display: none;"></select><br>';
  subEle += '<div class="sharemode"></div>';
  ele += subEle;
  ele += '</div></div></div>';

  $('#sharemodalbodystructure').append(ele);
}

function clearShareProjectModalHTML() {
  document.getElementById("sharemodalbodystructure").innerHTML = "";
}

function createrShareProjectAction(shareAction) {
  $('#shareProjectAction').select2({
    placeholder: 'Share Action',
    data: shareProjectActionOptions,
    // allowClear: true
  });
  $('#shareProjectAction').val(shareAction);
  $('#shareProjectAction').trigger('change');
  $("#shareProjectAction").change(function() {
    let shareAction = $('#shareProjectAction').select2('data')[0].id;
    clearShareProjectModalHTML();
    buildShareInterface(shareAction);
  });
}

function createShareUsersList(usersList, multiple=true, selectedUser='', allowClear=true) {
  // console.log(usersList);
  let usersToShare = '';
  let shareuserlist = [];
  // for (let [key, value] of Object.entries(usersList)){
  for (let i=0; i<usersList.length; i++) {
    let value = usersList[i];
    usersToShare += '<option value="'+value+'">'+value+'</option>';
    shareuserlist.push(value)
  };
  localStorage.setItem("shareuserlist", JSON.stringify(shareuserlist));
  $('#shareProjectSelect').append(usersToShare);
  $('#shareProjectSelect').select2({
    placeholder: 'Share with users',
    // data: usersList,
    allowClear: allowClear,
    multiple: multiple,
  });
  if (selectedUser === '') {
    $("#shareProjectSelect").val(null).trigger('change');
  }
  else {
    $("#shareProjectSelect").val(selectedUser).trigger('change');
  }
  $("#shareProjectSelect").change(function() {
    let shareAction = $('#shareProjectAction').select2('data')[0].id;
    // clearShareProjectModalHTML();
    if (shareAction === 'update' ||
        shareAction === 'remove') {
          // updateRemoveShareInterface(shareAction);
          let selectedUser = $('#shareProjectSelect').select2('data')[0].id;
          clearShareProjectModalHTML();
          buildShareInterface(shareAction, selectedUser);
        }
  });
}

function createShareLatestChecked() {
  let shareLatest = '';
  shareLatest += '<br><input type="checkbox" id="sharelatestchecked" name="sharelatestchecked" value="">'+
                    '<label for="sharelatestchecked">&nbsp; Share Annotations by Other Users</label><br>';
  $('#shareLatest').append(shareLatest);
}

function createShareSourcesList(sourceList) {
  // console.log(sourceList);
  let speakersToShare = '';
  let sharespeakerlist = [];
  // for (let [key, value] of Object.entries(sourceList)){
  //   console.log(key, value);
  for (let i=0; i<sourceList.length; i++) {
    let value = sourceList[i];
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

function createShareAccessControl(sharemodecount, selectedUsersharemodecount, checked=false) {
  let shareAccessControlEle = '<hr><h4>Access Control:</h4>';
  for (let [key, value] of Object.entries(shareModeObject)) {
    // console.log(key, value);
    if (value <= sharemodecount) {
      if (checked &&
          value === selectedUsersharemodecount) {
        shareAccessControlEle += '<input type="radio" id="'+key+'" name="sharemode" value="'+value+'" checked>'+
        '<label for="'+key+'">&nbsp; '+key+'</label><br>';
      }
      else {
        shareAccessControlEle += '<input type="radio" id="'+key+'" name="sharemode" value="'+value+'">'+
        '<label for="'+key+'">&nbsp; '+key+'</label><br>';
      }
    }
  }
  // if (sharemodecount == 0) {
  //   sharemodecount = 1;
  // }
  // for (i=1; i<=sharemodecount;i++) {
  //   console.log(shareModeList[i]);
  //   if (shareModeList[i] !== undefined) {
  //     let j = i-1;
  //     shareAccessControlEle += '<input type="radio" id="'+shareModeList[j]+'" name="sharemode" value="'+j+'">'+
  //                               '<label for="'+shareModeList[j]+'">&nbsp; '+shareModeList[j]+'</label><br>';
  //   }
  // }
  $('.sharemode').append(shareAccessControlEle);
}

function createShareAdvanceAccessControl(shareInfo, selectedUserShareInfo, shareAction='') {
  let shareAdvanceAccessControlEle = '';
  if (shareInfo["downloadchecked"] == "true" ||
        shareInfo["sharechecked"] == "true") {
      shareAdvanceAccessControlEle += '<hr><h4>Advanced Access Control:</h4>';
      if (shareInfo["downloadchecked"] == "true") {
        if (shareAction === 'update') {
          if (selectedUserShareInfo["downloadchecked"] == "true") {
            shareAdvanceAccessControlEle += '<input type="checkbox" id="downloadchecked" name="downloadchecked" value="" checked>'+
                                            '<label for="downloadchecked">&nbsp; Allow Download</label>';
          }
          else {
            shareAdvanceAccessControlEle += '<input type="checkbox" id="downloadchecked" name="downloadchecked" value="">'+
                                            '<label for="downloadchecked">&nbsp; Allow Download</label>';
          }
        }
        else {
          shareAdvanceAccessControlEle += '<input type="checkbox" id="downloadchecked" name="downloadchecked" value="">'+
                                          '<label for="downloadchecked">&nbsp; Allow Download</label>';
        }
      }
      shareAdvanceAccessControlEle += '&nbsp;&nbsp;&nbsp;&nbsp;';
      if (shareInfo["sharechecked"] == "true") {
        if (shareAction === 'update') {
          if (selectedUserShareInfo["sharechecked"] == "true") {
            shareAdvanceAccessControlEle += '<input type="checkbox" id="sharechecked" name="sharechecked" value="" checked>'+
                                            '<label for="sharechecked">&nbsp; Access To Share Button</label><br>';
          }
          else {
            shareAdvanceAccessControlEle += '<input type="checkbox" id="sharechecked" name="sharechecked" value="">'+
                                            '<label for="sharechecked">&nbsp; Access To Share Button</label><br>';
          }
        }
        else {
          shareAdvanceAccessControlEle += '<input type="checkbox" id="sharechecked" name="sharechecked" value="">'+
                                          '<label for="sharechecked">&nbsp; Access To Share Button</label><br>';
        }
      }
    }
  $('.sharemode').append(shareAdvanceAccessControlEle);
}
// share project button on LiFE home page
// $(document).ready(function() { 
function buildShareInterface(shareAction='share', selectedUser='') {
  $.getJSON('/userslist', {
    a: JSON.stringify({
      shareAction: shareAction,
      selectedUser: selectedUser
    })
  }, function(data) {
    // let shareAction = 'share';
    let projetName = data.projectName;
    let usersList = data.usersList;
    let sourceList = data.sourceList;
    let shareInfo = data.shareInfo;
    let sharemodecount = data.sharemode;
    let sharelatestchecked = shareInfo["sharelatestchecked"];
    let isSharedWithUsersList = shareInfo["isharedwith"];
    let selectedUserShareInfo = data.selectedUserShareInfo;
    let selectedUsersharelatestchecked = selectedUserShareInfo["sharelatestchecked"];
    let selectedUsersharemodecount = selectedUserShareInfo["sharemode"];
    // console.log('qwaaszxzx') 
    // console.log(data.usersList)
    console.log(shareInfo);
    console.log(shareAction);
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
    if (shareAction === 'share') {
      document.getElementById("sharesharedaccess").style.display = "inline";
      document.getElementById("updatesharedaccess").style.display = "none";
      document.getElementById("removesharedaccess").style.display = "none";
      createShareUsersList(usersList);
      if (sharelatestchecked == "true") {
        createShareLatestChecked();
      }
      document.getElementById("shareSpeakerSelect").style.display = "block";
      createShareSourcesList(sourceList);
      createShareAccessControl(sharemodecount, sharemodecount);
      createShareAdvanceAccessControl(shareInfo, shareInfo);
    }
    else if (shareAction === 'update') {
      document.getElementById("sharesharedaccess").style.display = "none";
      document.getElementById("updatesharedaccess").style.display = "inline";
      document.getElementById("removesharedaccess").style.display = "none";
      createShareUsersList(isSharedWithUsersList, multiple=false, selectedUser, allowClear=false);
      if (selectedUser !== '') {
        if (sharelatestchecked == "true") {
          createShareLatestChecked();
          if (selectedUsersharelatestchecked == "true") {
            document.getElementById("sharelatestchecked").checked = true;
          }
        }
        document.getElementById("shareSpeakerSelect").style.display = "block";
        createShareSourcesList(sourceList);
        createShareAccessControl(sharemodecount, selectedUsersharemodecount, checked=true);
        createShareAdvanceAccessControl(shareInfo, selectedUserShareInfo, shareAction);
      }
    }
    else if (shareAction === 'remove') {
      document.getElementById("sharesharedaccess").style.display = "none";
      document.getElementById("updatesharedaccess").style.display = "none";
      document.getElementById("removesharedaccess").style.display = "inline";
      createShareUsersList(isSharedWithUsersList,  multiple=false, selectedUser, allowClear=false);
      if (selectedUser !== '') {
        document.getElementById("shareSpeakerSelect").style.display = "block";
        createShareSourcesList(sourceList);
      }
    }
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
  // document.getElementById("sharemodalbodystructure").innerHTML = "";
  clearShareProjectModalHTML();
});

$(".shareprojectwith").click(function() {
  alert('Project sharing successful :)');
  });
