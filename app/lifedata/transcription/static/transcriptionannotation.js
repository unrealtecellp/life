let select2Keys = new Array();
let modalSelect2Keys = new Array();

function createSelect2(select2Keys, tagSet) {
    // console.log(select2Keys);
    let data = [];
    for (s = 0; s < select2Keys.length; s++) {
        let select2Key = select2Keys[s];
        let select2KeyValue = tagSet[select2Key][0];
        if (select2KeyValue === '#ID#') {
            continue;
            // console.log('getIds')
            // // data = getIds()
            // $.ajax({
            //     url: '/easyAnno/getIdList',
            //     type: 'GET',
            //     data: { 'data': JSON.stringify('') },
            //     contentType: "application/json; charset=utf-8",
            //     success: function (response) {
            //         data = response.allIds;
            //         // console.log(data);
            //         $('#' + select2Key+'_select').select2({
            //             placeholder: select2Key,
            //             data: data,
            //             // tags: true,
            //             allowClear: true
            //         });
            //     }
            // });
            // return false;
        }
        else {
            // console.log(select2Key, tagSet[select2Key]);
            $('#' + select2Key+'_select').select2({
                placeholder: select2Key,
                data: tagSet[select2Key],
                tags: true,
                allowClear: true
            });
        }
    }
}

function showHideCategory(category) {
    // console.log(category);
    if (category === 'undefined') {
        return false;
    }
    parentNodeIds = []
    for (let [key, value] of Object.entries(document.getElementsByClassName(category))) {
        // console.log(key, value, value.parentNode);
        // document.getElementById(value.id).hidden = false;
        document.getElementById(value.id).disabled = false;
        parentNode = value.parentNode;
        // parentNodeIds.push(parentNode.id);
        document.getElementById(parentNode.id).style.display = "block";
        // document.getElementById(value.id).nextSibling.hidden = false;
    }
}

// hide all dependent categories
function hideHideCategory(category) {
    // console.log(category);
    if (category === 'undefined') {
        return false;
    }
    for (let [key, value] of Object.entries(document.getElementsByClassName(category))) {
        // document.getElementById(value.id).hidden = true;
        document.getElementById(value.id).disabled = true;
        parentNode = value.parentNode ;
        document.getElementById(parentNode.id).style.display = "none";
        // document.getElementById(value.id).nextSibling.hidden = true;
    }
}

function categoryDependencyInfo(categoryClass, categoryClassValue, categoryDependency) {
    let categoryDependencyInfoList = [];
    let valueList = []
    // console.log(categoryClass, categoryClassValue);
    for (let [key, value] of Object.entries(categoryDependency)) {
        // console.log(categoryClass, categoryClassValue);
        let insertValue = []
        if (value.includes(categoryClass)) {
            if (value.includes('|')) {
                valueList = value.split('|');
            }
            else {
                valueList = value.split();
            }
            for (let i = 0; i < valueList.length; i++) {
                valueListValue  = valueList[i];
                if (valueListValue.includes(categoryClass)) {
                    if (valueListValue.includes('!=')) {
                        for (let j = 0; j < categoryClassValue.length; j++) {
                            // console.log(categoryClassValue[j]);
                            insertValue = valueListValue.split('!=')[1]
                            if (!(categoryDependencyInfoList.includes(categoryClassValue[j])) &&
                                categoryClassValue[j] !== insertValue) {
                                categoryDependencyInfoList.push(categoryClassValue[j])
                            }
                        }
                    }
                    else if (valueListValue.includes('=')) {
                            insertValue = valueListValue.split('=')[1]
                            if (!(categoryDependencyInfoList.includes(insertValue))) {
                                categoryDependencyInfoList.push(insertValue)
                            }
                    }
                }
            }
        }
        // break;
    }
    // console.log('categoryDependencyInfoList', categoryDependencyInfoList);
    return categoryDependencyInfoList;
}

function createElement(tagSet,
    key,
    value,
    defaultCategoryTag='',
    categoryDependency,
    modalEle,
    element='radio',
    elementProperties='required=False') {
        // console.log(key, element, elementProperties);
        let ele = '';
        if (Object.keys(categoryDependency).length !== 0 && key in categoryDependency && !modalEle) {
            ele += '<div class="border col btn-group-toggle ' + key + '" data-toggle="buttons" id="'+key+'"  style="display: none;" disabled>';
        }
        else {
            ele += '<div class="border col btn-group-toggle ' + key + '" data-toggle="buttons" id="'+key+'">';
        }
        // ele+='</legend>';
        // ele += '<h4><strong>' + key + ': </strong></h4>';

        ele+='<legend>'+key.replaceAll('_', ' ')+'</legend>'
        let categoryDependencyInfoList = categoryDependencyInfo(key, value, categoryDependency);
        let dependentOnClass = dependentOn(tagSet, key, categoryDependency).join(' ');
        for (let i = 0; i < value.length; i++) {
        // console.log(key, value, value[i], defaultCategoryTag, element, elementProperties);
        let elementClass = "";
        let elementPropertiesAddon = elementProperties;
        let labelElementProperties = '';
        if (categoryDependencyInfoList.includes(value[i])) {
            elementPropertiesAddon += ' onclick=" showHideCategory(\'' + key+'='+value[i] + '\')"';
            labelElementProperties += ' onclick=" showHideCategory(\'' + key+'='+value[i] + '\')"';
        }
        else {
            elementPropertiesAddon += ' onclick=" hideHideCategory(\'' + key+'_hideDependency' + '\')"';
            labelElementProperties += ' onclick=" hideHideCategory(\'' + key+'_hideDependency' + '\')"';
        }
        if (Object.keys(categoryDependency).length !== 0 && key in categoryDependency) {
            // console.log(key, dependentOnClass);
            elementClass += ' '+dependentOnClass;
        }
        if (element === 'radio') {
            elementClass += " btn btn-default btn-block";
            if (defaultCategoryTag === value[i]) {
                elementClass += ' active';
                elementPropertiesAddon += ' checked'
            }
            ele += '<label id="' + value[i] + '_label"class="'+elementClass+'" for="' + value[i] + '" '+labelElementProperties+'>' + value[i] +
            '<input class="form-check-input" type="radio" name="' + key + '" id="' + value[i] + '" value="' + value[i] + '" '+elementPropertiesAddon+'>' +
            '</label>';
            // console.log(ele);
        }
        else if (element === 'textarea'){
            // console.log(key, element, elementProperties);
            ele += '<textarea class="form-check-input ' + elementClass + ' " name="' + key + '" id="' + key + '_' + value[i] + '" cols="30">' + defaultCategoryTag + '</textarea>';
        }
        // else if (element === 'modal+textarea'){
        //     // console.log(key, element, elementProperties);
        //     // ele += '<textarea class="form-check-input ' + elementClass + ' " name="' + key + '" id="' + key + '_' + value[i] + '" cols="60">' + defaultCategoryTag + '</textarea>';
        //     ele += '<button type="button" id="'+key+'" class="btn btn-info btn ' + elementClass + ' " onclick="openCategoryModal(this.id)"  data-toggle="modal" data-target="#'+key+'Modal">'+key+'</button>';
        //     // ele += '<button type="button" id="'+key+'" class="btn btn-info btn-sm ' + elementClass + ' " onclick=" showHideCategory(\'' + key+'='+value[i] + '\')">'+key+'</button>';
        //     // ele += '<button type="button" id="'+key+'" class="btn btn-info btn-sm ' + elementClass + ' " onclick=" hideHideCategory(\'' + key+'_hideDependency' + '\')">'+key+'</button>';
        //     // ele += addModalElement(key)
        // }
        else if (element === 'select') {
            // console.log(defaultCategoryTag, value[i]);
            // if ((value[i] === "#ID#")) {
            //     // console.log(key, element, elementProperties, value[i], defaultCategoryTag);
            //     ele += '<select class="' + elementClass + '" id="' + key+'_select' + '" name="' + key + '" '+elementProperties.replace('#', ' ')+' style="width: 100%">';
            //         // console.log(defaultCategoryTag);
            //     if (defaultCategoryTag!== 'NONE' &&
            //         defaultCategoryTag.length !== 0) {
            //         for (s = 0; s < defaultCategoryTag.length; s++) {
            //             eval = defaultCategoryTag[s];
            //             ele += '<option value="' + eval + '" selected>' + eval + '</option>';
            //         }
            //     }
            //     ele += '</select>';

            //     if (modalEle && !modalSelect2Keys.includes(key)) {
            //         modalSelect2Keys.push(key);
            //     }
            //     else {
            //         if (!select2Keys.includes(key))
            //             select2Keys.push(key);
            //     }
            //     // console.log(select2Keys);
            //     // continue;
            // }
            // else if ((defaultCategoryTag.includes(value[i]) &&
            if ((defaultCategoryTag.includes(value[i]) &&
                !select2Keys.concat(modalSelect2Keys).includes(key))) {
                // console.log(key, element, elementProperties, value[i], defaultCategoryTag);
                ele += '<select class="' + elementClass + '" id="' + key+'_select' + '" name="' + key + '" '+elementProperties.replace('#', ' ')+' style="width: 100%">';
                // console.log(defaultCategoryTag);
                if (defaultCategoryTag!== 'NONE' &&
                defaultCategoryTag.length !== 0) {
                    for (s = 0; s < defaultCategoryTag.length; s++) {
                        eval = defaultCategoryTag[s];
                        if (value.includes(eval)) {
                            ele += '<option value="' + eval + '" selected>' + eval + '</option>';
                        }
                    }
                }
                ele += '</select>';

                if (modalEle && !modalSelect2Keys.includes(key)) {
                    modalSelect2Keys.push(key);
                }
                else {
                    if (!select2Keys.includes(key))
                        select2Keys.push(key);
                }
                // console.log(select2Keys);
            }
            else if ((defaultCategoryTag === '' &&
                !select2Keys.concat(modalSelect2Keys).includes(key))) {
                // console.log(key, element, elementProperties, value[i], defaultCategoryTag);
                ele += '<select class="' + elementClass + '" id="' + key+'_select' + '" name="' + key + '" '+elementProperties.replace('#', ' ')+' style="width: 100%">';
                // console.log(defaultCategoryTag);
                // if (defaultCategoryTag!== 'NONE' &&
                //     defaultCategoryTag.length !== 0) {
                //     for (s = 0; s < defaultCategoryTag.length; s++) {
                //         eval = defaultCategoryTag[s];
                //         ele += '<option value="' + eval + '" selected>' + eval + '</option>';
                //     }
                // }
                ele += '</select>';

                if (modalEle && !modalSelect2Keys.includes(key)) {
                    modalSelect2Keys.push(key);
                }
                else {
                    if (!select2Keys.includes(key))
                        select2Keys.push(key);
                }
                // console.log(select2Keys);
            }
            else if ((!defaultCategoryTag.includes(value[i]) &&
                defaultCategoryTag!== 'NONE' &&
                defaultCategoryTag.length !== 0 &&
                !select2Keys.concat(modalSelect2Keys).includes(key))) {
                let defaulter = false;
                let notDefaulter = false;
                for (s = 0; s < defaultCategoryTag.length; s++) {
                    eval = defaultCategoryTag[s];
                    if (!value.includes(eval)) {
                        defaulter = true;
                    }
                    else if (value.includes(eval)) {
                        notDefaulter = true;
                    }
                }
                if (notDefaulter) {
                    continue
                }
                else if (defaulter) {
                    // console.log(key, element, elementProperties, value[i], defaultCategoryTag);
                    ele += '<select class="' + elementClass + '" id="' + key+'_select' + '" name="' + key + '" '+elementProperties.replace('#', ' ')+' style="width: 100%">';
                    ele += '</select>';

                    if (modalEle && !modalSelect2Keys.includes(key)) {
                        modalSelect2Keys.push(key);
                    }
                    else {
                        if (!select2Keys.includes(key))
                            select2Keys.push(key);
                    }
                    // console.log(select2Keys);
                }
            // continue
            }
            // else if (defaultCategoryTag.includes(value[i])) {
            //     if (defaultCategoryTag!== 'NONE' &&
            //         defaultCategoryTag.length !== 0) {
            //         for (s = 0; s < defaultCategoryTag.length; s++) {
            //             eval = defaultCategoryTag[s];
            //             ele += '<option value="' + eval + '" selected>' + eval + '</option>';
            //         }
            //     }
            // }
        }
    }
    ele += '</div>';

    // console.log(ele);

    return ele
}

function elementData (projData, key, value, defaultCategoryTag=undefined, modalEle=false) {
    // console.log(key, value, defaultCategoryTag, modalEle)
    let eleData = ''
    // let defaultCategoryTag = '';
    let categoryDependency = {};
    let tagSet = projData['tagSet'];
    if ("defaultCategoryTags" in projData["tagSetMetaData"]) {
        defaultCategoryTags = projData["tagSetMetaData"]["defaultCategoryTags"]
        if (key in defaultCategoryTags && defaultCategoryTag === undefined){
            defaultCategoryTag = defaultCategoryTags[key]
            // if (!defaultCategoryTag && modalEle) {
            //     console.log(key, defaultCategoryTag);
            //     // console.log(defaultCategoryTags);
            //     // getModalElementDefaultValue(key, tagSet[value])
            // }
        }
    }
    if ("categoryDependency" in projData["tagSetMetaData"]) {
        categoryDependency = projData["tagSetMetaData"]["categoryDependency"]
    }
    // console.log('defaultCategoryTag', defaultCategoryTag, 'categoryDependency', categoryDependency)
    if ("categoryHtmlElement" in projData["tagSetMetaData"]) {
        categoryHtmlElement = projData["tagSetMetaData"]["categoryHtmlElement"]
        categoryHtmlElementProperties = projData["tagSetMetaData"]["categoryHtmlElementProperties"]
        element = categoryHtmlElement[key]
        // if (element === 'select' && defaultCategoryTag === '') {
        //     defaultCategoryTag = [value[0]]
        // }
        elementProperties = categoryHtmlElementProperties[key]
        // if (element === 'select') {
        //     // console.log(tagSet,
        //     //     key,
        //     //     value,
        //     //     defaultCategoryTag,
        //     //     categoryDependency,
        //     //     modalEle,
        //     //     element,
        //     //     elementProperties);
        // }
        eleData += createElement(tagSet,
                                key,
                                value,
                                defaultCategoryTag,
                                categoryDependency,
                                modalEle,
                                element,
                                elementProperties);
    }
    else {
        eleData += createElement(tagSet,
                                key,
                                value,
                                defaultCategoryTag,
                                categoryDependency,
                                modalEle);
    }

    return eleData;
}

function dependentOn(tagSet, categoryClass, categoryDependency) {
    let dependentOnList = [];
    let valueList = []
    // console.log(categoryClass);
    for (let [key, value] of Object.entries(categoryDependency)) {
        if (key === categoryClass) {
            // console.log(categoryClass);
            if (value.includes('|')) {
                // console.log(categoryClass);
                valueList = value.split('|');
            }
            else {
                // console.log(categoryClass);
                valueList = value.split();
            }
            // console.log(valueList);
            for (let i = 0; i < valueList.length; i++) {
                valueListValue  = valueList[i];
                if (valueListValue.includes('!=')) {
                    insertValue = valueListValue.split('!=')[1]
                    // console.log(insertValue);
                    parentKey = valueListValue.split('!=')[0]
                    // console.log(parentKey);
                    parentValue = tagSet[parentKey];
                    for (let j = 0; j < parentValue.length; j++) {
                        if (!(dependentOnList.includes(parentKey+'='+parentValue[j])) &&
                            parentValue[j] !== insertValue) {
                            dependentOnList.push(parentKey+'='+parentValue[j])
                            dependentOnList.push(parentKey+'_hideDependency')
                        }
                    }
                }
                else if (valueListValue.includes('=')) {
                        insertValue = valueListValue
                        parentKey = valueListValue.split('=')[0]
                        if (!(dependentOnList.includes(insertValue))) {
                            dependentOnList.push(insertValue)
                            dependentOnList.push(parentKey+'_hideDependency')
                        }
                }
            }
        }
    }
    // console.log('dependentOnList', dependentOnList);

    return dependentOnList;
    // dependentOnClass = dependentOnList.join(' ');
    // console.log(dependentOnClass)
    // return dependentOnClass;
}

function checkModalKey(tagSet, key, categoryDependency) {
    let modalKey = false;
    let dependentOnList = dependentOn(tagSet, key, categoryDependency);
    let dependOnListBig = [];
    // if (dependentOnList.length === 0) {
    //     console.log('dependentOnList', dependentOnList);
    // }
    loop1:
    while(dependentOnList.length !== 0) {
        // console.log('dependentOnList', dependentOnList);
        let dependOnSet = new Set();
        for (let i=0; i<dependentOnList.length; i++) {
            if (dependentOnList[i].includes('=')) {
                dependOnSet.add(dependentOnList[i].split('=')[0]);
            }
        }
        // console.log(dependOnSet);
        let dependOnList = Array.from(dependOnSet);
        // console.log(dependOnList, dependOnList.length);
        if (dependOnList.length>1) {
            dependOnListBig = dependOnList;
        }
        loop2:
        for (let i=0; i<dependOnList.length; i++) {
            dependOn = dependOnList[i];
            // console.log(dependOn);
            if (Object.keys(categoryDependency).length !== 0 && dependOn in categoryDependency) {
                loop3:
                for (j=0; j<tagSet[dependOn].length; j++) {
                    // console.log(tagSet[dependOn][j]);
                    if (tagSet[dependOn][j].includes('SPAN_TEXT')) {
                        modalKey = true;
                        break loop1;
                    }
                }
                // console.log('tracing...')
                dependentOnList = dependentOn(tagSet, dependOn, categoryDependency);
                // console.log('dependentOnList_2', dependentOnList);
            }
            else {
                // console.log('break from loop2...')
                if (dependOnListBig.length>1) {
                    dependOnListBig.splice(-1);
                    // console.log('dependOnListBig', dependOnListBig);
                    dependOnList = dependOnListBig;
                    // break loop1;
                    continue loop2;
                }
                // dependentOnList = [];
                break loop1;
            }
        }
    }
    // console.log(modalKey);
    return modalKey;
}

function transcriptAnnotationInterface(tagsetWithMetadata) {
    let inpt = '';
    console.log(tagsetWithMetadata)
    let tagSet = tagsetWithMetadata['tagSet'];
    let tagSetMetaData = tagsetWithMetadata['tagSetMetaData']
    inpt += '<div id="middle">';
    let categoryDependency = {};
    if ("categoryDependency" in tagSetMetaData) {
        categoryDependency = tagSetMetaData["categoryDependency"]
    }
    for (let [key, value] of Object.entries(tagSet)) {
        // console.log(key, value);
        modalKey = checkModalKey(tagSet, key, categoryDependency);
        if (modalKey) {
            continue
        }
        inpt += elementData(tagsetWithMetadata, key, value);
    }
    inpt += '</div>';

    document.getElementById("annotation2").innerHTML = "";
    $(".annotation1").html(inpt);

    createSelect2(select2Keys, tagSet);

    // return inpt;
}
