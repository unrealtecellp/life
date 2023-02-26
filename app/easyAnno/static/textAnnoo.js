let inpt = ''
let select2Keys = new Array();

function myFunction(projData) {
    lastActiveId = projData["lastActiveId"]
    accessedOnTime = projData["accessedOnTime"]
    currentUser = projData['currentUser']
    inpt += '<span class="textFormAlert"></span><div class="row">' +
        '<form name="savetextanno" class="form-horizontal" action="/easyAnno/savetextAnno" method="POST" onsubmit="return validateForm()">' +
        '<div class="col-sm-6">';
    inpt += '<input type="hidden" id="accessedOnTime" name="accessedOnTime" value="' + accessedOnTime + '">' +
        '<input type="hidden" id="lastActiveId" name="lastActiveId" value="' + lastActiveId + '">' +
        '<input type="hidden" id="' + projData["textData"]["ID"] + '" name="id" value="' + projData["textData"]["ID"] + '">';
    inpt += '<div class="form-group">' +
        '<div class="col">' +
        '<button type="button" id="previous" class="btn btn-info btn-lg" onclick="previousText()">Previous</button>' +
        '<button type="button" id="next" class="btn btn-lg btn-info pull-right" onclick="nextText()">Next</button>' +
        '</div></div>';
    inpt += '<p class="form-group" id="' + projData["textData"]["ID"] + '"><strong>Text ID: ' + projData["textData"]["ID"] + '</strong></p>' +
        '<div class="form-group">' +
        '<label class="col" for="text">Text:</label><br>' +
        '<input type="hidden" class="form-control" id="text"' + ' name="text" value="' + projData["textData"]["Text"] + '">' +
        '<div class="col" style=background-color:#DCDCDC;>' + projData["textData"]["Text"] + '</div>' +
        '</div>';
    inpt += '<div class="form-group">' +
        '<div class="col">' +
        '<button type="button" id="previous" class="btn btn-info btn-lg" onclick="previousText()">Previous</button>' +
        '<button type="button" id="next" class="btn btn-lg btn-info pull-right" onclick="nextText()">Next</button>' +
        '</div>' +
        '</div></div>';
    // already annotated data. Open form in edit mode
    if ('currentUser' in projData) {
        // console.log(projData['currentUser'])
        inpt += '<div class="col-sm-6">';
        if (projData[currentUser]["annotatedFLAG"] === 0) {
            inpt += '<div class="col"><strong>Already Annotated: <span style="color:Tomato;">NO</span></strong></div>';
        }
        else {
            inpt += '<div class="col"><strong>Already Annotated: <span style="color:MediumSeaGreen;">YES</span></strong></div>';
        }

        let dependendTagLabel = new Object();
        for (let [key, value] of Object.entries(projData["tagSet"])) {
            if (value[0] === 'SELECT2') {
                // console.log(value[0], projData[currentUser][key], typeof projData[currentUser][key]);
                inpt += '<br><label for="' + key + '">' + key + ': </label><br>' +
                    '<select class="' + key + 'class" id="' + key + '" name="' + key + '" multiple="multiple" style="width: 100%">';
                if (projData[currentUser][key].length !== 0) {
                    for (s = 0; s < projData[currentUser][key].length; s++) {
                        eval = projData[currentUser][key][s]
                        inpt += '<option value="' + eval + '" selected>' + eval + '</option>';
                    }
                }
                inpt += '</select><br>';

                select2Keys.push(key);
                continue;
            }
            // else if (value[0] === 'TEXTAREA') {
            //     // console.log(value[0]);
            //     inpt += '<br><label for="'+key+'">'+key+': </label>'+
            //             '<textarea class="form-control" id="'+key+'" name="'+key+'" rows="5">'+projData[currentUser][key]+'</textarea>';
            //     continue;
            // }
            dependendTagLabel[key] = 0;
            inpt += '<br><div class="col btn-group-toggle ' + key + '" data-toggle="buttons" id="'+key+'"><strong>' + key + ': </strong><br/>';
            console.log(key, value);
            for (let i = 0; i < value.length; i++) {
                // Show hide categories
                if ("tagSetMetaData" in projData) {
                    // console.log(key, value[i])
                    categoryClass = undefined;
                    notInDepencyColFLAG = 1;
                    notInDepencyCol = undefined;
                    if (key in projData["tagSetMetaData"]["categoryDependency"]) {
                        // console.log(key, value[i], projData[currentUser][key])
                        if (projData[currentUser][key] !== '') {
                            delStr = '<br><div class="col btn-group-toggle ' + key + '" data-toggle="buttons" id="'+key+'"><strong>' + key + ': </strong><br/>';
                            // changes here for radio btn to look like button
                            // inpt = inpt.replace(delStr, '<div class="col ' + key + '">');
                            inpt = inpt.replace(delStr, '<div class="col btn-group-toggle" ' + key + '" data-toggle="buttons" id="'+key+'"">');

                            categoryClass = projData["tagSetMetaData"]["categoryDependency"][key];
                            // console.log(categoryClass);
                            categoryClassCategory = categoryClass.split('=')[0];
                            independentTag = 'independentTag_' + categoryClassCategory;
                            if (dependendTagLabel[key] === 0) {
                                inpt += '<strong class="dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + categoryClass + key + '">' + key + ': </strong>';
                                dependendTagLabel[key] = 1;
                            }
                            if (projData[currentUser][key] === value[i]) {
                                // console.log(key, value[i])
                                if (value[i] === 'TEXTAREA') {
                                    inpt += '<textarea class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" name="' + key + '" id="' + key + '_' + value[i] + '" cols="60">' + projData[currentUser][key] + '</textarea>';

                                }
                                // changes here for radio btn to look like button
                                // else {
                                //     inpt += '<input class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked>' +
                                //         '<label class="form-check-label dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + value[i] + 'Label" for="' + value[i] + '">' + value[i] + '</label>';
                                // }
                                else {
                                    inpt += '<label class="btn btn-danger  btn-block active dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + value[i] + 'Label" for="' + value[i] + '">' + value[i] +
                                        '<input class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked>' +
                                        '</label>' +
                                        '<span class="button-margin"></span>';
                                        
                                }
                            }
                            else {
                                // console.log(key, value[i]);
                                if (value[i] === 'TEXTAREA') {
                                    inpt += '<textarea class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" name="' + key + '" id="' + key + '_' + value[i] + '" cols="60">' + projData[currentUser][key] + '</textarea>';

                                }
                                // changes here for radio btn to look like button
                                // else {
                                //     inpt += '<input class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '">' +
                                //         '<label class="form-check-label dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + value[i] + 'Label" for="' + value[i] + '">' + value[i] + '</label>';
                                // }
                                else {
                                    inpt += '<label class="btn btn-danger  btn-block dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + value[i] + 'Label" for="' + value[i] + '">' + value[i] +
                                        '<input class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '">' +
                                        '</label>'+
                                        '<span class="button-margin"></span>';
                                }
                            }
                        }
                        else {
                            delStr = '<br><div class="col btn-group-toggle ' + key + '" data-toggle="buttons" id="'+key+'"><strong>' + key + ': </strong><br/>';
                            // changes here for radio btn to look like button
                            // inpt = inpt.replace(delStr, '<div class="col ' + key + '">');
                            inpt = inpt.replace(delStr, '<div class="col btn-group-toggle ' + key + '" data-toggle="buttons" id="'+key+'" style="display: none;">');

                            categoryClass = projData["tagSetMetaData"]["categoryDependency"][key];
                            categoryClassCategory = categoryClass.split('=')[0];
                            independentTag = 'independentTag_' + categoryClassCategory;
                            // false disabled and hidden for the categories depending on their dependent
                            // cTag contain the name of the category tag on which the dependent category depend
                            // console.log(categoryClass.split('='));
                            cTagFLAG = 0;
                            getCatgAndTag = categoryClass.split('=')
                            catg = getCatgAndTag[0];
                            // console.log(catg);
                            if (getCatgAndTag[1].includes('|')) {
                                catgTag = getCatgAndTag[1].split('|')
                                // console.log(catgTag, projData[currentUser][catg]);
                                for (ct = 0; ct < catgTag.length; ct++) {

                                    if (projData[currentUser][catg] == catgTag[ct]) {
                                        cTagFLAG = 1;
                                    }
                                }
                            }
                            else {
                                catgTag = getCatgAndTag[1];
                                if (projData[currentUser][catg] == catgTag) {
                                    cTagFLAG = 1;
                                }
                            }
                            if (cTagFLAG === 1) {
                                if (dependendTagLabel[key] === 0) {
                                    inpt += '<strong class="dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + categoryClass + key + '">' + key + ': </strong><br/>';
                                    dependendTagLabel[key] = 1;
                                }
                                if (projData["tagSetMetaData"]["defaultCategoryTags"][key] == value[i]) {
                                    if (value[i] === 'TEXTAREA') {
                                        inpt += '<textarea class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" name="' + key + '" id="' + key + '_' + value[i] + '" cols="60"></textarea>';

                                    }
                                    // changes here for radio btn to look like button
                                    // else {
                                    //     inpt += '<input class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked>' +
                                    //         '<label class="form-check-label dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + value[i] + 'Label" for="' + value[i] + '">' + value[i] + '</label>';
                                    // }
                                    else {
                                        inpt += '<label class="btn btn-danger  btn-block active dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + value[i] + 'Label" for="' + value[i] + '">' + value[i] +
                                            '<input class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked>' +
                                            '</label>' +
                                            '<span class="button-margin"></span>';
                                    }
                                }
                                else {
                                    if (value[i] === 'TEXTAREA') {
                                        inpt += '<textarea class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" name="' + key + '" id="' + key + '_' + value[i] + '" cols="60"></textarea>';

                                    }
                                    // changes here for radio btn to look like button
                                    // else {
                                    //     inpt += '<input class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '">' +
                                    //         '<label class="form-check-label dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + value[i] + 'Label" for="' + value[i] + '">' + value[i] + '</label>';
                                    // }
                                    else {
                                        inpt += '<label class="btn btn-danger  btn-block dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + value[i] + 'Label" for="' + value[i] + '">' + value[i] +
                                            '<input class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '">' +
                                            '</label>'+
                                            '<span class="button-margin"></span>';
                                    }

                                }
                            }
                            else {
                                if (dependendTagLabel[key] === 0) {
                                    inpt += '<strong class="dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + categoryClass + key + '" hidden>' + key + ': </strong></br>';
                                    dependendTagLabel[key] = 1;
                                }
                                if (projData["tagSetMetaData"]["defaultCategoryTags"][key] == value[i]) {
                                    // console.log(key, value[i])
                                    if (value[i] === 'TEXTAREA') {
                                        inpt += '<textarea class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" name="' + key + '" id="' + key + '_' + value[i] + '" cols="60" disabled hidden></textarea>';

                                    }
                                    // changes here for radio btn to look like button
                                    // else {
                                    //     inpt += '<input class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked disabled hidden>' +
                                    //         '<label class="form-check-label dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + value[i] + 'Label" for="' + value[i] + '" hidden>' + value[i] + '</label>';
                                    // }
                                    else {
                                        inpt += '<label class="btn btn-danger  btn-block active dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + value[i] + 'Label" for="' + value[i] + '" hidden>' + value[i] +
                                            '<input class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked disabled hidden>' +
                                            '</label>' +
                                            '<span class="button-margin"></span>';
                                    }
                                }
                                else {
                                    if (value[i] === 'TEXTAREA') {
                                        inpt += '<textarea class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" name="' + key + '" id="' + key + '_' + value[i] + '" cols="60" disabled hidden></textarea>';

                                    }
                                    // changes here for radio btn to look like button
                                    // else {
                                    //     inpt += '<input class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" disabled hidden>' +
                                    //         '<label class="form-check-label dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + value[i] + 'Label" for="' + value[i] + '" hidden>' + value[i] + '</label>';
                                    // }
                                    else {
                                        inpt += '<label class="btn btn-danger  btn-block dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + value[i] + 'Label" for="' + value[i] + '" hidden>' + value[i] +
                                            '<input class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" disabled hidden>' +
                                            '</label>'+
                                            '<span class="button-margin"></span>';
                                    }
                                }
                            }
                        }
                    }
                    else if (!(key in projData["tagSetMetaData"]["categoryDependency"])) {

                        for (let [k, v] of Object.entries(projData["tagSetMetaData"]["categoryDependency"])) {
                            if (v.includes("=")) {
                                tempV = v.split('=');
                                // console.log(tempV);
                                if (tempV[0] === key) {
                                    // if (tempV[1].includes('|')) {
                                    //     tempV = tempV[1].split('|');
                                    //     // console.log(tempV);
                                    //     for (t = 0; t < tempV.length; t++) {
                                    //         if (tempV[t] === value[i]) {
                                    //             categoryClass = v;
                                    //         }
                                    //     }
                                    // }
                                    if (v.includes('|')) {
                                        tempVPipe = v.split('|');
                                        // console.log(tempV);
                                        for (t = 0; t < tempVPipe.length; t++) {
                                            if (tempVPipe[t].includes(value[i])) {
                                                categoryClass = v;
                                            }
                                        }
                                    }
                                    else if (tempV[1] === value[i]) {
                                        categoryClass = v;
                                    }
                                    else {
                                        for (let [kk, vv] of Object.entries(projData["tagSetMetaData"]["categoryDependency"])) {
                                            if (vv.includes(value[i])) {
                                                notInDepencyColFLAG = 0;
                                            }
                                        }
                                        if (notInDepencyColFLAG === 1) {
                                            notInDepencyCol = v;
                                        }
                                    }
                                }
                                else {
                                    // console.log(key, 'not in dependency column', value[i], categoryClass, v, notInDepencyColFLAG)
                                }
                            }
                            else {
                                alert('"=" not in dependency column of the tagset file!')
                            }
                        }
                        // console.log(key, value[i])
                        // Language
                        if (categoryClass === undefined && notInDepencyCol === undefined) {
                            console.log(key, value[i])
                            // changes here for radio btn to look like button
                            // if (projData[currentUser][key] == value[i]) {
                            //     inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked>' +
                            //         '<label class="form-check-label" for="' + value[i] + '">' + value[i] + '</label>';
                            // }
                            // else {
                            //     inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '">' +
                            //         '<label class="form-check-label" for="' + value[i] + '">' + value[i] + '</label>';
                            // }
                            if (projData[currentUser][key] == value[i]) {
                                console.log(key, value[i])
                                inpt += '<label class="btn btn-danger  btn-block active" for="' + value[i] + '">' + value[i] +
                                    '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked>' +
                                    '</label>' +
                                    '<span class="button-margin"></span>';
                                    
                            }
                            else {
                                inpt += '<label class="btn btn-danger  btn-block" for="' + value[i] + '">' + value[i] +
                                    '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '">' +
                                    '</label>'+
                                    '<span class="button-margin"></span>';
                                    
                            }
                        }
                        // NHUM
                        else if (categoryClass === undefined && notInDepencyCol !== undefined) {
                            // console.log(key, value[i])
                            independentTagHide = 'independentTag_' + key;
                            console.log(independentTagHide);
                            // changes here for radio btn to look like button
                            // if (projData[currentUser][key] == value[i]) {
                            //     inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked onclick="hideHideCategory(\'' + independentTagHide + '\')">' +
                            //         '<label class="form-check-label" for="' + value[i] + '">' + value[i] + '</label>';
                            // }
                            // else {
                            //     inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" onclick="hideHideCategory(\'' + independentTagHide + '\')">' +
                            //         '<label class="form-check-label" for="' + value[i] + '">' + value[i] + '</label>';
                            // }
                            if (projData[currentUser][key] == value[i]) {
                                inpt += '<label class="btn btn-danger  btn-block active" for="' + value[i] + '" onclick="hideHideCategory(\'' + independentTagHide + '\')">' + value[i] +
                                    '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked onclick="hideHideCategory(\'' + independentTagHide + '\')">' +
                                    '</label>' +
                                    '<span class="button-margin"></span>';
                            }
                            else {
                                inpt += '<label class="btn btn-danger  btn-block" for="' + value[i] + '" onclick="hideHideCategory(\'' + independentTagHide + '\')">' + value[i] +
                                    '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" onclick="hideHideCategory(\'' + independentTagHide + '\')">' +
                                    '</label>'+
                                    '<span class="button-margin"></span>';
                                    
                            }
                        }
                        // HUM/PDOW
                        else if (categoryClass !== undefined) {
                            // console.log(key, value[i])
                            if (projData[currentUser][key] == value[i]) {
                                // if (key === '01_who2') {
                                //     inpt += '<input class="form-check-input" type="checkbox" name="'+value[i]+'" id="'+value[i]+'" value="'+value[i]+'" checked onclick="showHideCategory(\''+categoryClass+'\')">'+
                                //         '<label class="form-check-label" for="'+value[i]+'">'+value[i]+'</label>';
                                // }
                                // else {
                                // changes here for radio btn to look like button
                                // inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked onclick="showHideCategory(\'' + categoryClass + '\')">' +
                                //     '<label class="form-check-label" for="' + value[i] + '">' + value[i] + '</label>';
                                inpt += '<label class="btn btn-danger  btn-block active" for="' + value[i] + '" onclick="showHideCategory(\'' + categoryClass + '\')">' + value[i] +
                                    '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked onclick="showHideCategory(\'' + categoryClass + '\')">' +
                                    '</label>' +
                                    '<span class="button-margin"></span>';
                                    
                                // }
                            }
                            else {
                                // if (key === '01_who2') {
                                //     inpt += '<input class="form-check-input" type="checkbox" name="'+value[i]+'" id="'+value[i]+'" value="'+value[i]+'" onclick="showHideCategory(\''+categoryClass+'\')">'+
                                //         '<label class="form-check-label" for="'+value[i]+'">'+value[i]+'</label>';
                                // }
                                // else {
                                // changes here for radio btn to look like button
                                // inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" onclick="showHideCategory(\'' + categoryClass + '\')">' +
                                //     '<label class="form-check-label" for="' + value[i] + '">' + value[i] + '</label>';
                                inpt += '<label class="btn btn-danger  btn-block" for="' + value[i] + '" onclick="showHideCategory(\'' + categoryClass + '\')">' + value[i] +
                                    '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" onclick="showHideCategory(\'' + categoryClass + '\')">' +
                                    '</label>'+
                                    '<span class="button-margin"></span>';
                                    
                                // }
                            }
                        }
                    }
                }
                else if (projData[currentUser][key] === value[i]) {
                    // console.log(key, value[i]);
                    // changes here for radio btn to look like button
                    // inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked>' +
                    //     '<label class="form-check-label" for="' + value[i] + '">' + value[i] + '</label>';
                    inpt += '<label class="btn btn-danger  btn-block active" for="' + value[i] + '">' + value[i] +
                        '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked>' +
                        '</label>' +
                        '<span class="button-margin"></span>';
                }
                else if (projData[currentUser][key] === '') {
                    if (value[i].includes('NA') || value[i].includes('NC') || value[i].includes('NE') || value[i].includes('NG') || value[i].includes('None') || value[i].includes('Neutral')) {
                        // changes here for radio btn to look like button
                        // inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked>' +
                        //     '<label class="form-check-label" for="' + value[i] + '">' + value[i] + '</label>';
                        inpt += '<label class="btn btn-danger  btn-block active" for="' + value[i] + '">' + value[i] +
                            '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked>' +
                            '</label>' +
                            '<span class="button-margin"></span>';
                    }
                    else {
                        // changes here for radio btn to look like button
                        // inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '">' +
                        //     '<label class="form-check-label" for="' + value[i] + '">' + value[i] + '</label>';
                        inpt += '<label class="btn btn-danger  btn-block" for="' + value[i] + '">' + value[i] +
                            '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '">' +
                            '</label>' +
                            '<span class="button-margin"></span>';
                    }
                }
                else {
                    // changes here for radio btn to look like button
                    // inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '">' +
                    //     '<label class="form-check-label" for="' + value[i] + '">' + value[i] + '</label>';
                    inpt += '<label class="btn btn-danger  btn-block" for="' + value[i] + '">' + value[i] +
                        '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '">' +
                        '</label>' +
                        '<span class="button-margin"></span>';
                        
                }
            }
            inpt += '</div>';

        }
        key = 'Duplicate Text'
        inpt += '<br><div class="col btn-group-toggle" data-toggle="buttons" id="'+key+'"><strong>' + key + ': </strong></br>';

        // if (projData[currentUser]["Duplicate"] === 'Yes') {
        //     inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="Yes" value="Yes" checked>' +
        //         '<label class="form-check-label" for="Yes">Yes</label>' +
        //         '<input class="form-check-input" type="radio" name="' + key + '" id="No" value="No">' +
        //         '<label class="form-check-label" for="No">No</label>';
        // }
        // else {
        //     inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="Yes" value="Yes">' +
        //         '<label class="form-check-label" for="Yes">Yes</label>' +
        //         '<input class="form-check-input" type="radio" name="' + key + '" id="No" value="No" checked>' +
        //         '<label class="form-check-label" for="No">No</label>';
        // }
        if (projData[currentUser]["Duplicate"] === 'Yes') {
            inpt += '<label class="btn btn-danger  btn-block active">' +
                    '<input class="form-check-input" type="radio" name="' + key + '" id="Yes" value="Yes" checked>' + 'Yes' +
                    '</label>' +
                    '<span class="button-margin"></span>' +
                    '<label class="btn btn-danger  btn-block">' +
                    '<input class="form-check-input" type="radio" name="' + key + '" id="No" value="No">' + 'No' +
                    '</label>';
        }
        else {
            inpt += '<label class="btn btn-danger  btn-block">' +
                    '<input class="form-check-input" type="radio" name="' + key + '" id="Yes" value="Yes">' + 'Yes' +
                    '</label>' +
                    '<span class="button-margin"></span>' +
                    '<label class="btn btn-danger  btn-block active">' +
                    '<input class="form-check-input" type="radio" name="' + key + '" id="No" value="No" checked>' + 'No' +
                    '</label>';
        }
        inpt += '</div>';

        inpt += '<br><div class="col">' +
            '<label class="col" for="text">Annotator Comment:</label>' +
            '<div class="col">' +
            '<input type="text" class="form-control" id="annotatorComment"' +
            ' name="annotatorComment" value="' + projData[currentUser]["annotatorComment"] + '">' +
            '</div>' +
            '</div>';
    }
    // data is not annotated yet
    else {
        inpt += '<div class="col-sm-6">';
        inpt += '<div class="col"><strong>Already Annotated: <span style="color:Tomato;">NO</span></strong></div>';

        let dependendTagLabel = new Object()

        for (let [key, value] of Object.entries(projData["tagSet"])) {

            dependendTagLabel[key] = 0;
            // console.log(key, value);
            // console.log(dependendTagLabel);
            if (value[0] === 'SELECT2') {
                // console.log(value[0]);
                inpt += '<br><label for="' + key + '">' + key + ': </label><br>' +
                    '<select class="' + key + 'class" id="' + key + '" name="' + key + '" multiple="multiple" style="width: 100%"></select><br>'

                select2Keys.push(key);
                continue;
            }
            // else if (value[0] === 'TEXTAREA') {
            //     // console.log(value[0]);
            //     inpt += '<br><label for="'+key+'">'+key+': </label>'+
            //             '<textarea class="form-control" id="'+key+'" name="'+key+'" rows="5"></textarea>';
            //     continue;
            // }
            inpt += '<br><div class="col btn-group-toggle ' + key + '" data-toggle="buttons" id="'+key+'"><strong>' + key + ': </strong></br>';
            for (let i = 0; i < value.length; i++) {
                // Show hide categories
                if ("tagSetMetaData" in projData) {
                    // console.log(key, value);
                    categoryClass = undefined;
                    notInDepencyColFLAG = 1;
                    notInDepencyCol = undefined;
                    if (key in projData["tagSetMetaData"]["categoryDependency"]) {
                        // console.log(key, value);
                        delStr = '<br><div class="col btn-group-toggle ' + key + '" data-toggle="buttons" id="'+key+'"><strong>' + key + ': </strong></br>';
                        // changes here for radio btn to look like button
                        // inpt = inpt.replace(delStr, '<div class="col ' + key + '">');
                        inpt = inpt.replace(delStr, '<div class="col btn-group-toggle ' + key + '" data-toggle="buttons"  id="'+key+'" style="display: none;">');

                        categoryClass = projData["tagSetMetaData"]["categoryDependency"][key];
                        categoryClassCategory = categoryClass.split('=')[0];
                        independentTag = 'independentTag_' + categoryClassCategory;

                        if (dependendTagLabel[key] === 0) {
                            inpt += '<strong class="dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + categoryClass + key + '" hidden>' + key + ': </strong></br>';
                            dependendTagLabel[key] = 1;
                        }

                        if (projData["tagSetMetaData"]["defaultCategoryTags"][key] == value[i]) {
                            if (value[i] === 'TEXTAREA') {
                                inpt += '<textarea class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" name="' + key + '" id="' + key + '_' + value[i] + '" cols="60" disabled hidden></textarea>';

                            }
                            // changes here for radio btn to look like button
                            // else {
                            //     inpt += '<input class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked disabled hidden>' +
                            //         '<label class="form-check-label dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + value[i] + 'Label" for="' + value[i] + '" hidden>' + value[i] + '</label>';
                            // }
                            else {
                                inpt += '<label class="btn btn-danger  btn-block active dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + value[i] + 'Label" for="' + value[i] + '" hidden>' + value[i] +
                                    '<input class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked disabled hidden>' +
                                    '</label>'+
                                    '<span class="button-margin"></span>';
                            }
                        }
                        else {
                            if (value[i] === 'TEXTAREA') {
                                inpt += '<textarea class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" name="' + key + '" id="' + key + '_' + value[i] + '" cols="60" disabled hidden></textarea>';

                            }
                            // changes here for radio btn to look like button
                            // else {
                            //     inpt += '<input class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" disabled hidden>' +
                            //         '<label class="form-check-label dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + value[i] + 'Label" for="' + value[i] + '" hidden>' + value[i] + '</label>';
                            // }
                            else {
                                inpt += '<label class="btn btn-danger  btn-block dependentTag ' + categoryClass + ' ' + independentTag + '" id="' + value[i] + 'Label" for="' + value[i] + '" hidden>' + value[i] +
                                    '<input class="form-check-input dependentTag ' + categoryClass + ' ' + independentTag + '" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" disabled hidden>' +
                                    '</label>'+
                                    '<span class="button-margin"></span>';
                            }
                        }
                    }
                    else if (!(key in projData["tagSetMetaData"]["categoryDependency"])) {
                        // console.log(key, value);
                        for (let [k, v] of Object.entries(projData["tagSetMetaData"]["categoryDependency"])) {
                            // if (key === '09-b_how1_mood') {
                            //     console.log(k, v);
                            // }
                            if (v.includes("=")) {
                                tempV = v.split('=');
                                // if (key === '09-b_how1_mood') {
                                //     console.log(tempV);
                                // }
                                if (tempV[0] === key) {
                                    if (key === '09-b_how1_mood') {
                                        console.log(k, v);
                                        console.log(tempV, value[i]);
                                    }
                                    // if (tempV[1].includes('|')) {
                                    //     tempV = tempV[1].split('|');
                                    //     // console.log(tempV);
                                    //     for (t = 0; t < tempV.length; t++) {
                                    //         if (tempV[t] === value[i]) {
                                    //             categoryClass = v;
                                    //         }
                                    //     }
                                    // }
                                    if (v.includes('|')) {
                                        tempVPipe = v.split('|');
                                        // console.log(tempV);
                                        for (t = 0; t < tempVPipe.length; t++) {
                                            if (tempVPipe[t].includes(value[i])) {
                                                categoryClass = v;
                                            }
                                        }
                                    }
                                    else if (tempV[1] === value[i]) {
                                        categoryClass = v;
                                    }
                                    else {
                                        for (let [kk, vv] of Object.entries(projData["tagSetMetaData"]["categoryDependency"])) {
                                            if (vv.includes(value[i])) {
                                                if (key === '09-b_how1_mood') {
                                                    console.log(vv)
                                                }
                                                notInDepencyColFLAG = 0;
                                            }
                                        }
                                        if (notInDepencyColFLAG === 1) {
                                            notInDepencyCol = v;
                                        }
                                    }
                                }
                                else {
                                    // console.log(key, 'not in dependency column', value[i], categoryClass, v, notInDepencyColFLAG)
                                }
                            }
                            else {
                                alert('"=" not in dependency column of the tagset file!')
                            }
                        }
                        // Language
                        if (categoryClass === undefined && notInDepencyCol === undefined) {
                            if (key === '09-b_how1_mood') {
                                console.log(key, value, value[i]);
                                console.log(key, categoryClass);
                            }
                            // console.log(key, value, value[i]);
                            // console.log(key, categoryClass, value[i]);
                            // console.log(projData["tagSetMetaData"]["defaultCategoryTags"][key] == value[i])
                            if (projData["tagSetMetaData"]["defaultCategoryTags"][key] == value[i]) {
                                // console.log(value[i]);
                                // changes here for radio btn to look like button
                                // inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked>' +
                                //     '<label class="form-check-label" for="' + value[i] + '">' + value[i] + '</label>';
                                inpt += '<label class="btn btn-danger  btn-block active" for="' + value[i] + '">' + value[i] +
                                    '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked>' +
                                    '</label>'+
                                    '<span class="button-margin"></span>';
                            }
                            // changes here for radio btn to look like button
                            // else {
                            //     inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '">' +
                            //         '<label class="form-check-label" for="' + value[i] + '">' + value[i] + '</label>';
                            // }
                            else {
                                inpt += '<label class="btn btn-danger  btn-block" for="' + value[i] + '">' + value[i] +
                                    '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '">' +
                                    '</label>'+
                                    '<span class="button-margin"></span>';
                            }

                        }
                        // NHUM
                        else if (categoryClass === undefined && notInDepencyCol !== undefined) {
                            // console.log(key, value);
                            // console.log(key, categoryClass, value[i]);
                            independentTagHide = 'independentTag_' + key;
                            // console.log(independentTagHide);
                            // changes here for radio btn to look like button
                            // if (projData["tagSetMetaData"]["defaultCategoryTags"][key] == value[i]) {
                            //     inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked onclick="hideHideCategory(\'' + independentTagHide + '\')">' +
                            //         '<label class="form-check-label" for="' + value[i] + '">' + value[i] + '</label>';
                            // }
                            // else {
                            //     inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" onclick="hideHideCategory(\'' + independentTagHide + '\')">' +
                            //         '<label class="form-check-label" for="' + value[i] + '">' + value[i] + '</label>';
                            // }
                            if (projData["tagSetMetaData"]["defaultCategoryTags"][key] == value[i]) {
                                inpt += '<label class="btn btn-danger  btn-block active" for="' + value[i] + '"  onclick="hideHideCategory(\'' + independentTagHide + '\')">' + value[i] +
                                    '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked onclick="hideHideCategory(\'' + independentTagHide + '\')">' +
                                    '</label>'+
                                    '<span class="button-margin"></span>';
                            }
                            else {
                                inpt += '<label class="btn btn-danger  btn-block" for="' + value[i] + '"  onclick="hideHideCategory(\'' + independentTagHide + '\')">' + value[i] +
                                    '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" onclick="hideHideCategory(\'' + independentTagHide + '\')">' +
                                    '</label>'+
                                    '<span class="button-margin"></span>';
                            }

                        }
                        // HUM/PDOW
                        else if (categoryClass !== undefined) {
                            if (key === '09-b_how1_mood') {
                                console.log(key, value, value[i]);
                                console.log(key, categoryClass);
                            }
                            // changes here for radio btn to look like button
                            // if (projData["tagSetMetaData"]["defaultCategoryTags"][key] == value[i]) {
                            //     inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked onclick="showHideCategory(\'' + categoryClass + '\')">' +
                            //         '<label class="form-check-label" for="' + value[i] + '">' + value[i] + '</label>';
                            // }
                            // else {
                            //     inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" onclick="showHideCategory(\'' + categoryClass + '\')">' +
                            //         '<label class="form-check-label" for="' + value[i] + '">' + value[i] + '</label>';
                            // }\
                            if (projData["tagSetMetaData"]["defaultCategoryTags"][key] == value[i]) {
                                inpt += '<label class="btn btn-danger  btn-block active" for="' + value[i] + '"  onclick="showHideCategory(\'' + categoryClass + '\')">' + value[i] +
                                    '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked onclick="showHideCategory(\'' + categoryClass + '\')">' +
                                    '</label>'+
                                    '<span class="button-margin"></span>';
                            }
                            else {
                                inpt += '<label class="btn btn-danger  btn-block" for="' + value[i] + '"  onclick="showHideCategory(\'' + categoryClass + '\')">' + value[i] +
                                    '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" onclick="showHideCategory(\'' + categoryClass + '\')">' +
                                    '</label>'+
                                    '<span class="button-margin"></span>';
                            }
                        }
                    }
                }
                // changes here for radio btn to look like button
                // else if (value[i].includes('NA') || value[i].includes('NC') || value[i].includes('NE') || value[i].includes('NG') || value[i].includes('None') || value[i].includes('Neutral')) {
                //     inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked>' +
                //         '<label class="form-check-label" for="' + value[i] + '">' + value[i] + '</label>';
                // }
                else if (value[i].includes('NA') || value[i].includes('NC') || value[i].includes('NE') || value[i].includes('NG') || value[i].includes('None') || value[i].includes('Neutral')) {
                    inpt += '<label class="btn btn-danger  btn-block active" for="' + value[i] + '">' + value[i] +
                        '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" checked>' +
                        '</label>'+
                        '<span class="button-margin"></span>';
                }
                // changes here for radio btn to look like button
                // else {
                //     inpt += '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '">' +
                //         '<label class="form-check-label" for="' + value[i] + '">' + value[i] + '</label>';
                // }
                else {
                    inpt += '<label class="btn btn-danger  btn-block" for="' + value[i] + '">' + value[i] +
                        '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '">' +
                        '</label>'+
                        '<span class="button-margin"></span>';
                }
            }
            inpt += '</div>';

        }
        key = 'Duplicate Text'
        // inpt += '<br><div class="col"><strong>' + key + ': </strong>' +
        //     '<input class="form-check-input" type="radio" name="' + key + '" id="Yes" value="Yes">' +
        //     '<label class="form-check-label" for="Yes">Yes</label>' +
        //     '<input class="form-check-input" type="radio" name="' + key + '" id="No" value="No" checked>' +
        //     '<label class="form-check-label" for="No">No</label>' +
        //     '</div>';

        inpt += '<br><div class="col btn-group-toggle" data-toggle="buttons" id="'+key+'"><strong>' + key + ': </strong><br/>' +
            '<label class="btn btn-danger  btn-block">' +
            '<input class="form-check-input" type="radio" name="' + key + '" id="Yes" value="Yes">' + 'Yes' +
            '</label>' +
            '<span class="button-margin"></span>' +
            '<label class="btn btn-danger  btn-block active">' +
            '<input class="form-check-input" type="radio" name="' + key + '" id="No" value="No" checked>' + 'No' +
            '</label>' +
            '</div>';

        inpt += '<br><div class="col">' +
            '<label class="col" for="text">Annotator Comment:</label>' +
            '<div class="col">' +
            '<input type="text" class="form-control" id="annotatorComment"' +
            ' name="annotatorComment">' +
            '</div>' +
            '</div>';
    }
    inpt += '<br><button type="submit" class="btn btn-lg btn-primary pull-right btn-block">Save</button>';
    inpt += '</div>';
    inpt += '</form></div>';

    $('.textdata').append(inpt);
    // console.log(select2Keys);
    for (s = 0; s < select2Keys.length; s++) {
        select2Key = select2Keys[s];
        $('.' + select2Key + 'class').select2({
            placeholder: select2Key,
            // data: languageslist,
            tags: true,
            allowClear: true
        });
    }
}

$(document).ready(function () {
    document.getElementById("NAG").onchange = function () {
        let aggIntensity = document.forms["savetextanno"]["Aggression Intensity"].value;
        let discRole = document.forms["savetextanno"]["Discursive Role"].value;
        if (aggIntensity !== "") {
            document.getElementById(aggIntensity).checked = false;
        }
        if (discRole !== "") {
            document.getElementById(discRole).checked = false;
        }
    };
});


function changeAggIntensity(tag) {
    // console.log(tag)
    if (tag == "NAG") {
        let aggIntensity = document.forms["savetextanno"]["Aggression Intensity"].value;
        document.getElementById(aggIntensity).checked = false;

    }
}

function validateForm() {
    $('.textFormAlertDiv').remove();
    textformalert = '';
    let language = document.forms["savetextanno"]["Language"].value;
    if (language == "") {
        //   alert("Language must be selected");
        textformalert += '<div class="alert alert-danger textFormAlertDiv" role="alert">Language must be selected</div>';
        $('.textFormAlert').append(textformalert);
        return false;
    }
    let aggression = document.forms["savetextanno"]["Aggression"].value;
    if (aggression == "") {
        // alert("Aggression must be selected");
        textformalert += '<div class="alert alert-danger textFormAlertDiv" role="alert">Aggression must be selected</div>';
        $('.textFormAlert').append(textformalert);
        return false;
    }
    if (aggression == "NAG") {
        let aggIntensity = document.forms["savetextanno"]["Aggression Intensity"].value;
        if (aggIntensity !== "") {
            document.getElementById(aggIntensity).checked = false;
            // return false;
        }
    }
    if (aggression == "CAG" || aggression == "OAG") {
        let aggIntensity = document.forms["savetextanno"]["Aggression Intensity"].value;
        if (aggIntensity === "") {
            // alert("Aggression Intensity must be selected");
            textformalert += '<div class="alert alert-danger textFormAlertDiv" role="alert">Aggression Intensity must be selected</div>';
            $('.textFormAlert').append(textformalert);
            return false;
        }
    }
    let cast = document.forms["savetextanno"]["Caste/Class Bias"].value;
    if (cast == "") {
        // alert("Caste/Class Bias must be selected");
        textformalert += '<div class="alert alert-danger textFormAlertDiv" role="alert">Caste/Class Bias must be selected</div>';
        $('.textFormAlert').append(textformalert);
        return false;
    }
    let communal = document.forms["savetextanno"]["Communal Bias"].value;
    if (communal == "") {
        // alert("Communal Bias must be selected");
        textformalert += '<div class="alert alert-danger textFormAlertDiv" role="alert">Communal Bias must be selected</div>';
        $('.textFormAlert').append(textformalert);
        return false;
    }
    let racial = document.forms["savetextanno"]["Ethnicity/Racial Bias"].value;
    if (racial == "") {
        // alert("Ethnicity/Racial Bias must be selected");
        textformalert += '<div class="alert alert-danger textFormAlertDiv" role="alert">Ethnicity/Racial Bias must be selected</div>';
        $('.textFormAlert').append(textformalert);
        return false;
    }
    let gender = document.forms["savetextanno"]["Gender Bias"].value;
    if (gender == "") {
        // alert("Gender Bias must be selected");
        textformalert += '<div class="alert alert-danger textFormAlertDiv" role="alert">Gender Bias must be selected</div>';
        $('.textFormAlert').append(textformalert);
        return false;
    }
}

function previousText() {
    lastActiveId = document.forms["savetextanno"]["lastActiveId"].value
    $.ajax({
        url: '/easyAnno/loadprevioustext',
        type: 'GET',
        data: { 'data': JSON.stringify(lastActiveId) },
        contentType: "application/json; charset=utf-8",
        success: function (response) {
            window.location.reload();
        }
    });
    return false;
}

function nextText() {
    lastActiveId = document.forms["savetextanno"]["lastActiveId"].value
    $.ajax({
        url: '/easyAnno/loadnexttext',
        type: 'GET',
        data: { 'data': JSON.stringify(lastActiveId) },
        contentType: "application/json; charset=utf-8",
        success: function (response) {
            window.location.reload();
        }
    });
    return false;
}

function unAnnotated() {
    unanno = '';
    $('#uNAnnotated').remove();
    $.ajax({
        url: '/easyAnno/allunannotated',
        type: 'GET',
        data: { 'data': JSON.stringify(unanno) },
        contentType: "application/json; charset=utf-8",
        success: function (response) {
            allunanno = response.allunanno;
            allanno = response.allanno;
            var inpt = '';
            inpt += '<select class="col-sm-3 allanno" id="allanno" onchange="loadAnnoText()">' +
                '<option selected disabled>All Annotated</option>';
            for (i = 0; i < allanno.length; i++) {
                inpt += '<option value="' + allanno[i]["textId"] + '">' + allanno[i]["ID"] + '</option>';
            }
            inpt += '</select>';
            inpt += '<select class="pr-4 col-sm-3" id="allunanno" onchange="loadUnAnnoText()">' +
                '<option selected disabled>All Un-Annotated</option>';
            for (i = 0; i < allunanno.length; i++) {
                inpt += '<option value="' + allunanno[i]["textId"] + '">' + allunanno[i]["ID"] + '</option>';
            }
            inpt += '</select>';
            $('.commentIDs').append(inpt);
            // console.log(inpt);
        }
    });
    return false;
}

function loadUnAnnoText() {
    textId = document.getElementById('allunanno').value;
    $.ajax({
        url: '/easyAnno/loadunannotext',
        type: 'GET',
        data: { 'data': JSON.stringify(textId) },
        contentType: "application/json; charset=utf-8",
        success: function (response) {
            window.location.reload();
        }
    });
    return false;
}

function loadAnnoText() {
    textId = document.getElementById('allanno').value;
    $.ajax({
        url: '/easyAnno/loadunannotext',
        type: 'GET',
        data: { 'data': JSON.stringify(textId) },
        contentType: "application/json; charset=utf-8",
        success: function (response) {
            window.location.reload();
        }
    });
    return false;
}

function showHideCategory(category) {
    console.log(category);
    if (category === 'undefined') {
        return false;
    }

    // for (let [key, value] of Object.entries(document.getElementsByClassName('dependentTag'))) {
    //         if (value.hidden === false) {
    //             document.getElementById(value.id).hidden = true;
    //         }
    //         if (value.disabled == false) {    
    //             document.getElementById(value.id).disabled = true;
    //         }
    // }
    parentNodeIds = []
    for (let [key, value] of Object.entries(document.getElementsByClassName(category))) {
        // console.log(key, value, value.parentNode);
        document.getElementById(value.id).hidden = false;
        document.getElementById(value.id).disabled = false;
        parentNode = value.parentNode;
        // parentNodeIds.push(parentNode.id);
        document.getElementById(parentNode.id).style.display = "block";
        // document.getElementById(value.id).nextSibling.hidden = false;
        console.log(value.id.nextSibling);
    }
    // console.log(parentNode, parentNode.id)
    // for (i=0; i<parentNodeIds.length; i++) {
    //     parentNodeId = parentNodeIds[i]
    //     document.getElementById(parentNodeId).style.display = "block";
    // }
}

// hide all dependent categories
function hideHideCategory(category) {
    console.log(category);
    if (category === 'undefined') {
        return false;
    }
    // console.log(category);
    // if (category === 'undefined'){
    //     return false;
    // }
    // for (let [key, value] of Object.entries(document.getElementsByClassName('dependentTag'))) {
    //         if (value.hidden === false) {
    //             document.getElementById(value.id).hidden = true;
    //         }
    //         if (value.disabled == false) {    
    //             document.getElementById(value.id).disabled = true;
    //         }
    // }
    for (let [key, value] of Object.entries(document.getElementsByClassName(category))) {
        document.getElementById(value.id).hidden = true;
        document.getElementById(value.id).disabled = true;
        parentNode = value.parentNode ;
        document.getElementById(parentNode.id).style.display = "none";
        // document.getElementById(value.id).nextSibling.hidden = true;
    }
}
