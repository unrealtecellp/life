shareModeList = ['view', 'download', 'edit', 'add', 'delete']
$("#delete").click(function() {
  index = shareModeList.indexOf('delete');
  tempShareModeList = shareModeList
  tempShareModeList.splice(index, 1)
  for (i=0; i<tempShareModeList.length; i++) {
    document.getElementById('add').checked = true;
  }
  });