function audioFilter(pageId=1) {
    // console.log('filtering...');
    selectedFilterOptions = {};
    let filterOptions = $('#audiosortingsubcategoriesdropdown').select2('data');
    // console.log(filterOptions); 
    for (let i=0; i<filterOptions.length; i++) {
        let option = filterOptions[i].text;
        let optGroup = filterOptions[i].element.parentNode.id;
        // console.log(option, optGroup);
        if (optGroup in selectedFilterOptions) {
            selectedFilterOptions[optGroup].push(option);
        }
        else {
            selectedFilterOptions[optGroup] = [option];
        }
    }
    // console.log(selectedFilterOptions);
    let audioBrowseInfo = getAudioBrowseInfo();
    audioBrowseInfo['pageId'] = pageId;
    // console.log(audioBrowseInfo);
    $.ajax({
        data : {
            a : JSON.stringify({
            "selectedFilterOptions": selectedFilterOptions,
            "audioBrowseInfo": audioBrowseInfo
        })
        },
        type : 'GET',
        url : '/filteraudiobrowsetable'
        }).done(function(data){
        console.log(data.audioDataFields, data.audioData, data.shareMode);
        createAudioBrowseTable(data.audioDataFields, data.audioData, data.shareMode, data.totalRecords, data.shareChecked, data.downloadChecked);
        // eventsMapping();
        createPagination(data.totalRecords, data.activePage);
        });
}
// filter audios
function audioFilteringEvent() {
    $("#audiofilter").click(function() {
        audioFilter();
    });
}
