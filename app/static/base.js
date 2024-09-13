function getJsonfileData(fileName) {
    let jsonFileNames = {
        select2DataKey: "select2_"+fileName+".json"
    }
    // console.log(fileName)
    let select2Data = JSON.parse(localStorage.getItem(fileName));
    // console.log(select2Data);
    if (!select2Data) {
        $.ajax({
            url: '/get_jsonfile_data',
            type: 'GET',
            async: false,
            data: { 'data': JSON.stringify(jsonFileNames) },
            contentType: "application/json; charset=utf-8",
            success: function (response) {
                select2Data = response.jsonData.select2DataKey;
                // console.log(select2Data);
                localStorage.setItem(fileName, JSON.stringify(select2Data));
            }
        });
    }
    return select2Data;
}