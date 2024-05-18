function camelCase(str) {
    // Using replace method with regEx
    return str.replace(/(?:^\w|[A-Z]|\b\w)/g, function (word, index) {
        return index == 0 ? word.toLowerCase() : word.toUpperCase();
    }).replace(/\s+/g, '');
}


function generateMetadataTable(speakerData, tableHeaders, count) {
    let ele = '';
    console.log(speakerData);
    console.log(tableHeaders);
    for (let [dataSource, metadata] of Object.entries(speakerData)) {
        let metadataFields = [];
        // ele += '<div class="row">';
        // ele += '<div class="col">';
        ele += '<b><h4>' + dataSource + ' RECORDS</h4></b>';
        ele += '<p id="totalrecords"><strong>Total Records:</strong>&nbsp;' + metadata.length + '</p>';
        ele += '<input id="myInput" type="text" placeholder="Search">' +
            '<table class="table table-striped " id="myTable" data-toolbar="#toolbar" data-search="true"' +
            'data-show-refresh="true" data-show-toggle="true" data-show-fullscreen="true" data-show-columns="true"' +
            'data-show-columns-toggle-all="true" data-detail-view="true" data-show-export="true"' +
            'data-click-to-select="true" data-detail-formatter="detailFormatter" data-minimum-count-columns="2"' +
            'data-show-pagination-switch="true" data-pagination="true" data-id-field="id"' +
            'data-page-list="[10, 25, 50, 100, all]" data-show-footer="true" data-side-pagination="server">';
        ele += '<thead><tr>';
        ele += '<th><input type="checkbox" id="headcheckbox" onchange="checkAllLexeme(this)" name="chk[]"' +
            'checked />&nbsp;</th>';
        for (const header of tableHeaders[dataSource]) {
            ele += '<th onclick="sortTable(2)">' + header + '</th>';
            if (header == "Speaker ID") {
                metadataFields.push("lifesourceid");
            }
            else {
                metadataFields.push(camelCase(header));
            }
        }
        ele += '<th>View</th>';
        ele += '</tr ></thead >';

        ele += '<tbody id="myTableBody">';
        console.log("Data source", dataSource);
        console.log("Metadata", metadata);
        console.log('Metadata Fields', metadataFields);
        for (const metadataEntry of metadata) {
            // console.log('Metadata entry', metadataEntry);
            let metadataEntryValues = metadataEntry["current"]["sourceMetadata"];
            ele += '<tr>' +
                '<td>' +
                '<input type="checkbox" id="lexemecheckbox" onchange="checkLexeme(this)" name="name1"checked />' +
                '</td>';
            for (let metadataField of metadataFields) {
                let metadataValue = '';
                if (metadataField == "lifesourceid" || metadataField == "createdBy") {
                    metadataValue = metadataEntry[metadataField];
                }
                else if (metadataField == "updatedBy") {
                    metadataValue = metadataEntry["current"][metadataField];
                }
                else {
                    if (metadataField in metadataEntryValues) {
                        metadataValue = metadataEntryValues[metadataField];
                    }
                }
                // console.log("Metadata Field", metadataField, "Metadata Value", metadataValue);
                ele += '<td>' + metadataValue + '</td>';

            }
            ele += '<td>' +
                '<button type="button" class="btn btn-primary metadataview" id="' + metadataEntry['lifesourceid'] + '"' +
                'data-toggle="modal" data-target="#metadatadetailsmodal">' +
                'View' +
                '</button>' +
                '</td>';
        }
        ele += '</tbody></table>';
    }

    $('#idMetaTable').html(ele);
    $.getScript("static/addnewspeaker.js", function () {
        console.log("Script loaded");
    })
}