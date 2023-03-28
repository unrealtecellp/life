localStorage.removeItem("textSpanDetails");
localStorage.removeItem("highlightSpanTextDetails");

let inpt = ''
let select2Keys = new Array();

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

    ele+='<legend>'+key+': </legend>'
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
        }
        else if (element === 'textarea'){
            // console.log(key, element, elementProperties);
            ele += '<textarea class="form-check-input ' + elementClass + ' " name="' + key + '" id="' + key + '_' + value[i] + '" cols="30">' + defaultCategoryTag + '</textarea>';
        }
        else if (element === 'modal+textarea'){
            // console.log(key, element, elementProperties);
            // ele += '<textarea class="form-check-input ' + elementClass + ' " name="' + key + '" id="' + key + '_' + value[i] + '" cols="60">' + defaultCategoryTag + '</textarea>';
            ele += '<button type="button" id="'+key+'" class="btn btn-info btn ' + elementClass + ' " onclick="openCategoryModal(this.id)"  data-toggle="modal" data-target="#'+key+'Modal">'+key+'</button>';
            // ele += '<button type="button" id="'+key+'" class="btn btn-info btn-sm ' + elementClass + ' " onclick=" showHideCategory(\'' + key+'='+value[i] + '\')">'+key+'</button>';
            // ele += '<button type="button" id="'+key+'" class="btn btn-info btn-sm ' + elementClass + ' " onclick=" hideHideCategory(\'' + key+'_hideDependency' + '\')">'+key+'</button>';
            // ele += addModalElement(key)
        }
        else if (element === 'select') {
            if (defaultCategoryTag.includes(value[i]) ||
                value[i] === "#ID#") {
                // console.log(key, element, elementProperties, value[i], defaultCategoryTag);
                ele += '<select class="' + elementClass + '" id="' + key+'_select' + '" name="' + key + '" '+elementProperties.replace('#', ' ')+' style="width: 100%">';
                // console.log(defaultCategoryTag);
                if (defaultCategoryTag!== 'NONE' &&
                    defaultCategoryTag.length !== 0) {
                    for (s = 0; s < defaultCategoryTag.length; s++) {
                        eval = defaultCategoryTag[s];
                        ele += '<option value="' + eval + '" selected>' + eval + '</option>';
                    }
                }
                ele += '</select><br>';

                select2Keys.push(key);
                // continue;
            }
        }
    }
    ele += '</div>';

    // console.log(ele);

    return ele
}

function elementData (projData, key, value, defaultCategoryTag=undefined, modalEle=false) {
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
        elementProperties = categoryHtmlElementProperties[key]
        // console.log(tagSet);
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

function createHighlightSpanTextDetails(currentUserAnnotation, tagSet) {
    // console.log(currentUserAnnotation, tagSet);
    for (let [key, value] of Object.entries(tagSet)) {
        // console.log(key, value[0])
        val = value[0];
        if (val === '#SPAN_TEXT#' && 
            typeof currentUserAnnotation[key] === 'object' &&
            !Array.isArray(currentUserAnnotation[key]) &&
            currentUserAnnotation[key] !== null) {
            // console.log(currentUserAnnotation[key], typeof currentUserAnnotation[key])
            for (let [k, v] of Object.entries(currentUserAnnotation[key])) {
                // console.log(k, v);
                spanStart = Number(v['startindex']);
                spanEnd = Number(v['endindex']);
                selection = v['textspan'];
                highlightSpanTextDetails(spanStart, spanEnd, selection);
            }
        }
    }
}

function createSelect2(select2Keys, tagSet) {
    // console.log(select2Keys);
    let data = [];
    for (s = 0; s < select2Keys.length; s++) {
        select2Key = select2Keys[s];
        select2KeyValue = tagSet[select2Key][0];
        if (select2KeyValue === '#ID#') {
            // console.log('getIds')
            // data = getIds()
            $.ajax({
                url: '/easyAnno/getIdList',
                type: 'GET',
                data: { 'data': JSON.stringify('') },
                contentType: "application/json; charset=utf-8",
                success: function (response) {
                    data = response.allIds;
                    // console.log(data);
                    $('#' + select2Key+'_select').select2({
                        placeholder: select2Key,
                        data: data,
                        // tags: true,
                        allowClear: true
                    });
                }
            });
            return false;
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

function createTextSpanDetails(tagSet, defaultCategoryTags) {
    // console.log(defaultCategoryTags);
    let textSpanDetails = {};
    for (let [key, value] of Object.entries(tagSet)) {
        if (value.includes("#SPAN_TEXT#") && defaultCategoryTags[key]) {
            // console.log(key, value, defaultCategoryTags[key]);
            textSpanDetails[key] = defaultCategoryTags[key]
        }
    }
    localStorage.setItem("textSpanDetails", JSON.stringify(textSpanDetails));
}
function myFunction(projData) {
    localStorage.setItem("projData", JSON.stringify(projData));
    let lastActiveId = projData["lastActiveId"];
    let accessedOnTime = projData["accessedOnTime"];
    let currentUser = projData['currentUser'];
    let currentUserAnnotation = projData[currentUser];
    let tagSet = projData["tagSet"];
    let defaultCategoryTags = projData["tagSetMetaData"]["defaultCategoryTags"]
    let inpt = '';
    
    inpt += '<span class="textFormAlert"></span><div class="row">' +
            '<form name="savetextanno" id="idsavetextannoform" class="form-horizontal" action="/easyAnno/savetextAnno" method="POST"  enctype="multipart/form-data">';
    inpt += '<div class="col-sm-6"  id="left">';
    inpt += '<input type="hidden" id="accessedOnTime" name="accessedOnTime" value="' + accessedOnTime + '">' +
            '<input type="hidden" id="lastActiveId" name="lastActiveId" value="' + lastActiveId + '">' +
            '<input type="hidden" id="' + projData["textData"]["ID"] + '" name="id" value="' + projData["textData"]["ID"] + '">';
    
    inpt += '<p class="form-group" id="' + projData["textData"]["ID"] + '"><strong>Text ID: ' + projData["textData"]["ID"] + '</strong></p>' +
            '<div class="form-group textcontentouter">' +
            '<label class="col" for="text">Text:</label><br>' +
            '<input type="hidden" class="form-control" id="text"' + ' name="text" value="' + projData["textData"]["Text"] + '">' +
            // '<textarea class="col textcontent" id="maintextcontent" readonly>' + projData["textData"]["Text"] + '</textarea>' +
            '<textarea class="col textcontent" id="maintextcontent"  onselect=spanAnnotation(this) readonly>' + projData["textData"]["Text"] + '</textarea>' +
            '</div>';
    // inpt += '<div class="form-group">' +
    //     '<div class="col">' +
    //     '<button type="button" id="previous" class="btn btn-info btn-lg" onclick="previousText()">Previous</button>' +
    //     '<button type="button" id="next" class="btn btn-lg btn-info pull-right" onclick="nextText()">Next</button>' +
    //     '</div>' +
    //     '</div></div>';
    inpt += '</div>';

    inpt += '<div class="col-sm-4" id="middle">';
    let categoryDependency = {};
    if ("categoryDependency" in projData["tagSetMetaData"]) {
        categoryDependency = projData["tagSetMetaData"]["categoryDependency"]
    }
    for (let [key, value] of Object.entries(tagSet)) {
        // console.log(key, value);
        modalKey = checkModalKey(tagSet, key, categoryDependency);
        if (modalKey) {
            continue
        }
        inpt += elementData(projData, key, value);
    }
    inpt += '</div>';

    inpt+= '<div class="col-sm-2" id="right">';
    
    inpt += 
        '<div class="col">' +
        '<div class="commentIDs">'+
        '<button type="button" id="uNAnnotated" class="btn btn-lg btn-block btn-default" onclick="unAnnotated()">All Text IDs</button>'+
        '</div>'+
        '<button type="button" id="previous" class="btn btn-info btn-lg btn-block" onclick="previousText()">Previous</button><br/>' +
        '<button type="button" id="next" class="btn btn-lg btn-info btn-block" onclick="nextText()">Next</button><br/>' +
        '</div>';
    inpt += '<br><button type="button" id="mainsave" class="btn btn-lg btn-danger btn-block"  onclick="mainSave(this)">Save</button>';
    inpt += '</div>'; //right div close
    // inpt += '<br><button type="submit" id="mainsave" class="btn btn-lg btn-danger btn-block"  onclick="mainSave(this)">Save</button>';
    inpt += '</form></div>';

    inpt += '<div id="idmodal"></div>'

    $('.textdata').append(inpt);
    // highlightSpanTextDetails('', '', '');
    if (currentUserAnnotation !== undefined) {
        createHighlightSpanTextDetails(currentUserAnnotation, tagSet);
    }
    textareaScrollHeight('maintextcontent', 'maintextcontent');
    createSelect2(select2Keys, tagSet);
    createTextSpanDetails(tagSet, defaultCategoryTags)

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
            inpt += '<select class="form-control col-sm-3 allanno" id="allanno" onchange="loadAnnoText()">' +
                '<option selected disabled>All Annotated</option>';
            for (i = 0; i < allanno.length; i++) {
                inpt += '<option value="' + allanno[i]["textId"] + '">' + allanno[i]["ID"] + '</option>';
            }
            inpt += '</select>';
            inpt += '<select class="form-control col-sm-3" id="allunanno" onchange="loadUnAnnoText()">' +
                '<option selected disabled>All Un-Annotated</option>';
            for (i = 0; i < allunanno.length; i++) {
                inpt += '<option value="' + allunanno[i]["textId"] + '">' + allunanno[i]["ID"] + '</option>';
            }
            inpt += '</select><br/><br/>';
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

function addModalElement(key) {
    let modalEle = ''
    modalEle += '<div class="modal fade" id="'+key+'Modal" tabindex="-1" role="dialog" aria-labelledby="'+key+'ModalLabel">'+
                '<div class="modal-dialog">'+
                '<div class="modal-content">'+
                    '<div class="modal-header">'+
                    '<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>'+
                    '<h4 class="modal-title" id="'+key+'ModalLabel">'+key+'</h4>'+
                    '</div>'+
                    '<div class="modal-body">'+
                        '<div class="row" id="'+key+'_modal_data"><form></form>'+
                        '</div>'+
                    '</div>'+
                    '<div class="modal-footer">'+
                    '<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>'+
                    // '<button type="button" class="btn btn-primary modalAnno" data-dismiss="modal">Done</button>'+
                    '</div>'+
                '</div>'+
                '</div>'+
            '</div>';

    return modalEle;
}


function openCategoryModal(eleId, start=0, end=0, selectedText='') {
    let spanStart = start;
    let spanEnd = end;
    let selection = selectedText;
    console.log(eleId, start, end, selection);
    let createModal = addModalElement(eleId);
    $('#idmodal').html(createModal);
    let modalData = '';
    let projData = JSON.parse(localStorage.getItem('projData'))
    let eleValue = projData['tagSet'][eleId][0];
    if (eleValue.includes('SPAN_TEXT')) {
        modalData += spanModalForm(projData, eleId);
    }
    $('#'+eleId+'_modal_data').html(modalData);
    // textareaScrollHeight('maintextcontent', 'spantextcontent');
    console.log(start, end);
    if (!start || !end) {
        console.log(start, end);
        let text = document.getElementById('maintextcontent');
        spanStart = text.selectionStart;
        spanEnd = text.selectionEnd;
        selection = text.textContent.substring(
            spanStart,
            spanEnd
        );
        console.log(selection);
    }
    leftModalForm(selection, spanStart, spanEnd, eleId)
    middleModalForm(selection, spanStart, spanEnd, eleId);

}

function spanModalForm(projData, eleId) {
    let spanModalData = '';
    let text = document.getElementById('maintextcontent').value;
    spanModalData += '<form name="savetextannospan" id="idsavetextannospanform" class="form-horizontal" action="/easyAnno/savetextAnnoSpan" method="POST"  enctype="multipart/form-data">';
    spanModalData += '<div class="col-md-6"  id="modalleft">';
    // spanModalData += '<p class="form-group" id="' + projData["textData"]["ID"] + '"><strong>Text ID: ' + projData["textData"]["ID"] + '</strong></p>' +
    //                 // '<div class="form-group textcontentouter">' +
    //                 '<label class="col" for="spantextcontent">Text:</label><br>'+
    //                 // '<svg viewBox="0 0 240 80" xmlns="http://www.w3.org/2000/svg">'+
    //                 '<textarea class="modaltextcontent" id="spantextcontent" onselect=spanAnnotation(this,"'+eleId+'") readonly>' + text + '</textarea>'
                    // '<text class="modaltextcontent" id="spantextcontent" onselect=spanAnnotation(this) readonly>' + text + '</text>'
                //    '</svg>' ;
    spanModalData += '</div>' // left col div

    spanModalData += '<div class="col-md-4"  id="modalmiddle">';
    spanModalData += '';
    spanModalData += '</div>' // right col div

    spanModalData+= '<div class="col-sm-2" id="modalright">';
    spanModalData += '<br><button type="button"  id="modalrightsavebtn" class="btn btn btn-danger" onclick="spanSave(this)">Save Span</button>';
    spanModalData += '</div>'; //right div close

    spanModalData += '</form>';

    return spanModalData;

}

function splitText(text, terminator) {
    const re = new RegExp('(?<='+terminator+')');
    // console.log(re);
    textList = text.split(re);
    console.log(textList);

    return textList;
}

function highlightSpanText(startEndLists) {
    // console.log(startEndLists);
    $('#maintextcontent').highlightWithinTextarea({
        highlight: [startEndLists]
    });
}

function highlightSpanTextDetails(spanStart, spanEnd, selection) {
    let startEndLists = [];
    data = JSON.parse(localStorage.getItem('highlightSpanTextDetails'));
    spanId = textSpanId(spanStart, spanEnd);
    if (data === null) {
        data = {};
    }
    data[spanId] = [spanStart, spanEnd]
    localStorage.setItem("highlightSpanTextDetails", JSON.stringify(data));

    for (let [key, value] of Object.entries(data)) {
        // console.log(key, value);
        startEndLists.push(value);
    }
    // console.log(startEndLists);
    highlightSpanText(startEndLists);
}

function spanAnnotation(event) {
    console.log('span');
    console.log(event);
    // console.log('eleId', eleId);
    const spanStart = event.selectionStart;
    const spanEnd = event.selectionEnd;
    const selection = event.textContent.substring(
        spanStart,
        spanEnd
      );
    // alert(selection);
    // middleModalForm(selection, spanStart, spanEnd)
    // $('#spantextcontent').highlightWithinTextarea({
    //     highlight: [spanStart, spanEnd] // string, regexp, array, function, or custom object
    // });
    // $('#spantextcontent').highlightWithinTextarea('update');

    highlightSpanTextDetails(spanStart, spanEnd, selection);
    // highlightSpanText(spanStart, spanEnd)
}

function textareaScrollHeight(eleId1, eleId2) {
    textareaElement1 = document.getElementById(eleId1)
    textareaElement2 = document.getElementById(eleId2)
    // console.log('textarea height');
    textareaElement2.style.height = (5+textareaElement1.scrollHeight)+"px";
}

function leftModalForm(selection, spanStart, spanEnd, eleId) {
    let leftModalData = '';
    let projData = JSON.parse(localStorage.getItem('projData'));
    let eleValue = projData['tagSet'][eleId][0];
    let lastActiveId = projData["lastActiveId"];
    let spanId = textSpanId(spanStart, spanEnd);
    // console.log(eleValue, selection, spanStart, spanEnd, eleId);
    leftModalData += '<input type="hidden" id="lastActiveId" name="lastActiveId" value="' + lastActiveId + '">';
    leftModalData += '<input type="hidden" id="modalHeader"' + ' name="modalheader" value="' + eleId + '">';
    leftModalData += '<label for="spanStart">Span Start</label>'+
                        '<input class="form-control" id="spanStart" name="startindex" value='+spanStart+' readonly><br>';
    leftModalData += '<label for="spanEnd">Span End</label>'+
                        '<input class="form-control" id="spanEnd" name="endindex" value='+spanEnd+' readonly><br>';
    // leftModalData += '<p class="form-group" id="' + spanId + '"><strong>Text Span ID: ' + spanId + '</strong></p>';
    leftModalData += '<label for="spanId">Text Span ID</label>'+
                        '<input class="form-control" id="spanId" name="spanId" value='+spanId+' readonly><br>';
                    // '<div class="form-group textcontentouter">' +
    leftModalData += '<label class="col" for="spantextcontent">Text:</label><br>'+
                    // '<svg viewBox="0 0 240 80" xmlns="http://www.w3.org/2000/svg">'+
                    // '<textarea class="modaltextcontent" id="spantextcontent" name="textspan" onselect=spanAnnotation(this,"'+eleId+'") readonly>' + selection + '</textarea>';
                    '<textarea class="modaltextcontent" id="spantextcontent" name="textspan" readonly>' + selection + '</textarea>';
    
    $('#modalleft').html(leftModalData);
}

function middleModalForm(selection, spanStart, spanEnd, eleId) {
    // console.log(eleId);
    let middleModalData = '';
    let projData = JSON.parse(localStorage.getItem('projData'));
    let tagSet = projData['tagSet'];
    // let defaultCategoryTags = projData["tagSetMetaData"]["defaultCategoryTags"]
    // console.log(defaultCategoryTags);
    let defaultCategoryTag = '';
    let eleValue = tagSet[eleId][0];
    // console.log(eleValue, selection, spanStart, spanEnd, eleId);
    // middleModalData += '<label for="spanStart">Span Start</label>'+
    //                     '<input class="form-control" id="spanStart" name="spanStart" value='+spanStart+' readonly>';
    // middleModalData += '<label for="spanEnd">Span End</label>'+
    //                     '<input class="form-control" id="spanEnd" name="spanEnd" value='+spanEnd+' readonly>';
    if ("categoryDependency" in projData["tagSetMetaData"]) {
        let categoryDependency = projData["tagSetMetaData"]["categoryDependency"]
        // console.log(categoryDependency);
        for (let [key, value] of Object.entries(categoryDependency)) {
            if (value.includes(eleId)) {
                console.log(key, value, tagSet[key], categoryDependency[key], defaultCategoryTags[value]);
                defaultCategoryTag = getModalDefaultTag(key, eleId, spanStart, spanEnd);
                middleModalData += elementData(projData, key, tagSet[key], defaultCategoryTag, true);
            }
            else {
                // console.log(key, value, tagSet[key]);
                let dependentOnList = dependentOn(tagSet, key, categoryDependency);
                loop1:
                while (dependentOnList.length !== 0) {
                    // console.log(key, value);
                    // console.log(eleId);
                    // console.log(dependentOnList);
                    loop2:
                    for (i=0; i<dependentOnList.length; i++) {
                        if (dependentOnList[i].includes(eleId)) {
                            console.log(key, value, tagSet[key], categoryDependency[key], defaultCategoryTags[value], dependentOnList[i]);
                            defaultCategoryTag = getModalDefaultTag(key, eleId, spanStart, spanEnd);
                            middleModalData += elementData(projData, key, tagSet[key], defaultCategoryTag, false);
                            break loop1;
                        }
                        else if (dependentOnList[i].includes('|')) {
                            dependentOnList = dependentOn(tagSet, dependentOnList[i].split('!=')[0], categoryDependency);
                            // console.log('|', dependentOnList);
                        }
                        else if (dependentOnList[i].includes('=')) {
                            // console.log(dependentOnList[i], dependentOnList[i].split('=')[0])
                            dependentOnList = dependentOn(tagSet, dependentOnList[i].split('=')[0], categoryDependency);
                            // console.log('=', dependentOnList);
                        }
                    }
                }
            }
        }
        // console.log('!!!!!!!!!!!!', dependentOn(tagSet, '01-b_caste_harm_potential_physical', categoryDependency));
        // console.log(categoryDependency['01-b_caste_harm_potential_physical'])
    }
    $('#modalmiddle').html(middleModalData);
}

function getModalDefaultTag(key, eleId, spanStart, spanEnd) {
    let textSpanDetails = JSON.parse(localStorage.getItem('textSpanDetails'));
    let defaultCategoryTag = '';
    spanId = textSpanId(spanStart, spanEnd);
    if (eleId in textSpanDetails) {
        if (spanId in textSpanDetails[eleId]) {
            if (key in textSpanDetails[eleId][spanId]) {
                defaultCategoryTag = textSpanDetails[eleId][spanId][key]
            }
        }
    }
    // console.log(eleId, spanStart, spanEnd, textSpanDetails[eleId], textSpanDetails[eleId][spanId], textSpanDetails[eleId][spanId][key]);

    return defaultCategoryTag
}

function textSpanId(spanStart, spanEnd) {
    // console.log(spanStart, spanEnd);
    let spanStartLength = spanStart.length;
    let spanEndLength = spanEnd.length
    while(spanStartLength != 5) {
        spanStart = '0'+spanStart;
        spanStartLength = spanStart.length;
    }
    while(spanEndLength != 5) {
        spanEnd = '0'+spanEnd;
        spanEndLength = spanEnd.length;
    }
    spanId = spanStart+spanEnd;

    return spanId;
}

function spanSave(ele) {
    console.log('sending transcription and morphemic details to the server');
    let textSpanDetails = JSON.parse(localStorage.getItem('textSpanDetails'));
    let projData = JSON.parse(localStorage.getItem('projData'));
    let tagSet = projData['tagSet'];
    if (textSpanDetails === null) {
        textSpanDetails = {};
    }
    submit_span_form_ele = document.getElementById("idsavetextannospanform");
    // const formData = new FormData(submit_span_form_ele, ele);
    const formData = new FormData(submit_span_form_ele);
    // console.log(formData);
    var object = {};
    formData.forEach(function(value, key){
        // console.log('key: ', key, 'value: ', value);
        object[key] = value;
    });
    // console.log(object);
    let textSpan = object['textspan'];
    // console.log(textSpan);
    if (!textSpan) {
        alert('Please select some text!')
        return false;
    }
    let header = object['modalheader'];
    let spanId = object['spanId'];
    let lastActiveId = object['lastActiveId'];
    ['modalheader', 'spanId', 'lastActiveId'].forEach(e => delete object[e]);
    // console.log(object);
    let currentTextSpanDetails = {};
    currentTextSpanDetails[header] = {}
    currentTextSpanDetails[header][spanId] = object;
    // console.log(currentTextSpanDetails);
    if (header in textSpanDetails) {
        textSpanDetails[header][spanId] = currentTextSpanDetails[header][spanId];
    }
    else {
        textSpanDetails[header] = {};
        textSpanDetails[header][spanId] = currentTextSpanDetails[header][spanId];
    }
    localStorage.setItem("textSpanDetails", JSON.stringify(textSpanDetails));
    currentTextSpanDetails['lastActiveId'] = lastActiveId;
    $.post( "/easyAnno/savetextAnnoSpan", {
        a: JSON.stringify(currentTextSpanDetails)
      })
      .done(function( data ) {
        // window.location.reload();
        alert('Annotation Saved :)')
      });
}

function mainSave(ele) {
    submit_form_ele = document.getElementById("idsavetextannoform");
    // const formData = new FormData(submit_form_ele, ele);
    const formData = new FormData(submit_form_ele);
    var object = {};
    formData.forEach(function(value, key){
        // console.log('key: ', key, 'value: ', value);
        if (key in object) {
            object[key].push(value);
        }
        else {
            object[key] = [value];
        }
    });
    $.post( "/easyAnno/savetextAnno", {
        a: JSON.stringify(object)
      })
      .done(function( data ) {
        window.location.reload();
      });
}

$(document).ready(function(){
    $('#maintextcontent').click(function() { 
        // console.log(this);
        // alert('clicked');
        let eleId = '';
        let startindex = 0;
        let endindex = 0;
        let minimumDistance = this.textLength;
        // console.log('minimumDistance', minimumDistance);
        let textSpanDetails = JSON.parse(localStorage.getItem('textSpanDetails'));
        console.log(textSpanDetails);
        console.log(this.selectionStart, this.selectionEnd);
        let spanStart = this.selectionStart;
        let spanEnd = this.selectionStart;
        // let spanId = textSpanId(spanStart, spanEnd);
        // console.log(spanId);
        loop1:
        for (let [key, value] of Object.entries(textSpanDetails)) {
            console.log(key, value);
            loop2:
            for (let [k, v] of Object.entries(value)) {
                let startIndex = v['startindex'];
                let endIndex = v['endindex'];
                if (spanStart >= startIndex && spanEnd <= endIndex) {
                    differenceFromStart = Math.abs(startIndex-spanStart);
                    differenceFromEnd = Math.abs(endIndex-spanEnd);
                    distance = differenceFromStart+differenceFromEnd;
                    console.log(k, v);
                    console.log(true, spanStart, spanEnd, 'startindex: ', v['startindex'], 'endindex: ', v['endindex'], distance);
                    eleId = key;
                    startindex = startIndex;
                    endindex = endIndex;
                    selection = v['textspan'];
                    break loop1;
                }
            }
        }
        openCategoryModal(eleId, startindex, endindex, selection);
        $('#'+eleId+'Modal').modal('toggle')
    });
  });
