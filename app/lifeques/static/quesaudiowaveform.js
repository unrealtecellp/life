/**
 * Create a WaveSurfer instance.
 */
 var wavesurfer; // eslint-disable-line no-var

 /**
  * Init & load.
  */
 document.addEventListener('DOMContentLoaded', function() {
     // Init wavesurfer
     wavesurfer = WaveSurfer.create({
         container: '#waveform',
         height: 100,
         pixelRatio: 1,
         scrollParent: true,
         normalize: true,
         minimap: true,
         backend: 'MediaElement',
         plugins: [
             WaveSurfer.regions.create(),
             WaveSurfer.minimap.create({
                 height: 30,
                 waveColor: '#ddd',
                 progressColor: '#999',
                 cursorColor: '#999'
             }),
             WaveSurfer.timeline.create({
                 container: '#wave-timeline'
             })
         ]
     });
     document.querySelector('#slider').oninput = function () {
         wavesurfer.zoom(Number(this.value));
     };
 
     /* Regions */
     filePath = JSON.parse(localStorage.getItem('QuesAudioFilePath'));
     wavesurfer.load(filePath)
     wavesurfer.on('ready', function() {
         
         wavesurfer.enableDragSelection({
             color: randomColor(0.1)
         });
 
         if (localStorage.regions) {
             // console.log(localStorage.regions)
             loadRegions(JSON.parse(localStorage.regions));
         }
     });
     wavesurfer.on('region-click', function(region, e) {
         e.stopPropagation();
         // Play on click, loop on shift click
         e.shiftKey ? region.playLoop() : region.play();
     });
     wavesurfer.on('region-click', editAnnotation);
     // wavesurfer.on('region-created', saveRegions);
     wavesurfer.on('region-updated', saveRegions);
     // wavesurfer.on('region-removed', saveRegions);
    //  wavesurfer.on('region-in', showNote);
 
     wavesurfer.on('region-play', function(region) {
         region.once('out', function() {
             wavesurfer.play(region.start);
             wavesurfer.pause();
         });
     });
     wavesurfer.on('finish', function () {
         $(".audioplaypause").addClass('glyphicon-play').removeClass('glyphicon-pause');
     });
 
     document.querySelector(
         '[data-action="delete-region"]'
     ).addEventListener('click', function() {
        //  let form = document.forms.edit;
        let form = document.forms[document.forms.length-1];
        let regionId = form.dataset.region;

        // form.elements[2].setAttribute("value", '0');
        // form.elements[3].setAttribute("value", '0');
        // form.elements[4].setAttribute("value", '');
        // document.getElementById("end").setAttribute("value", '0');
        document.getElementById("deleteboundary").disabled = true;

        console.log(form, typeof form, form.elements[2].value, regionId)
        for (let [key, value] of Object.entries(form)) {
            console.log(key, value, typeof value, value.id);
            if (value.id === 'start' || value.id === 'end') {
                form.elements[key].setAttribute("value", '0');
            }
            else if (value.id.includes('Prompt_Audio_Transcription')) {
                form.elements[key].setAttribute("value", '-');
            }
        }
        if (regionId) {
            let region = wavesurfer.regions.list[regionId];
            wavesurfer.regions.list[regionId].remove();

            form.reset();
            rid = region.start.toString().slice(0, 4).replace('.', '').concat(region.end.toString().slice(0, 4).replace('.', ''));
            localStorageRegions = JSON.parse(localStorage.regions)
            for (let [key, value] of Object.entries(localStorageRegions)) {
                // console.log(key, value)
                if (localStorageRegions[key]['boundaryID'] === rid) {
                    localStorageRegions.splice(key, 1)
                    // console.log(localStorageRegions)
                    localStorage.setItem("regions", JSON.stringify(localStorageRegions));
                }
            }
        }
    });
});
 
 /**
  * Save annotations to localStorage.
  */
 function saveRegions() {
     // console.log('WHERE')
     localStorage.regions = JSON.stringify(
         Object.keys(wavesurfer.regions.list).map(function(id) {
             let region = wavesurfer.regions.list[id];
             // console.log(region)
             rid = region.start.toString().slice(0, 4).replace('.', '').concat(region.end.toString().slice(0, 4).replace('.', ''));
              
             return {
                 boundaryID: rid,
                 start: region.start,
                 end: region.end,
                 attributes: region.attributes,
                 data: region.data,
                 // sentence: updateSentenceDetails(rid, sentence, region)
             };
         })
     );
 }
 
 /**
  * Load regions from localStorage.
  */
 function loadRegions(regions) {
     // console.log(regions)
     regions.forEach(function(region) {
         region.color = randomColor(0.1);
         // console.log(region)
         wavesurfer.addRegion(region);
     });
 }
 
 /**
  * Extract regions separated by silence.
  */
 function extractRegions(peaks, duration) {
     // Silence params
     const minValue = 0.0015;
     const minSeconds = 0.25;
 
     let length = peaks.length;
     let coef = duration / length;
     let minLen = minSeconds / coef;
 
     // Gather silence indeces
     let silences = [];
     Array.prototype.forEach.call(peaks, function(val, index) {
         if (Math.abs(val) <= minValue) {
             silences.push(index);
         }
     });
 
     // Cluster silence values
     let clusters = [];
     silences.forEach(function(val, index) {
         if (clusters.length && val == silences[index - 1] + 1) {
             clusters[clusters.length - 1].push(val);
         } else {
             clusters.push([val]);
         }
     });
 
     // Filter silence clusters by minimum length
     let fClusters = clusters.filter(function(cluster) {
         return cluster.length >= minLen;
     });
 
     // Create regions on the edges of silences
     let regions = fClusters.map(function(cluster, index) {
         let next = fClusters[index + 1];
         return {
             start: cluster[cluster.length - 1],
             end: next ? next[0] : length - 1
         };
     });
 
     // Add an initial region if the audio doesn't start with silence
     let firstCluster = fClusters[0];
     if (firstCluster && firstCluster[0] != 0) {
         regions.unshift({
             start: 0,
             end: firstCluster[firstCluster.length - 1]
         });
     }
 
     // Filter regions by minimum length
     let fRegions = regions.filter(function(reg) {
         return reg.end - reg.start >= minLen;
     });
 
     // Return time-based regions
     return fRegions.map(function(reg) {
         return {
             start: Math.round(reg.start * coef * 10) / 10,
             end: Math.round(reg.end * coef * 10) / 10
         };
     });
 }
 
 /**
  * Random RGBA color.
  */
 function randomColor(alpha) {
     return (
         'rgba(' +
         [
             ~~(Math.random() * 255),
             ~~(Math.random() * 255),
             ~~(Math.random() * 255),
             alpha || 1
         ] +
         ')'
     );
 }
 
 /**
  * Edit annotation for a region.
  */
 function editAnnotation(region) {
     // console.log('editAnnotation(region)')
     // console.log(region)
     document.getElementById("deleteboundary").disabled = false;
     let form = document.forms[document.forms.length-1]
     console.log(form);
     (form.elements.start.value = region.start),
     (form.elements.end.value = region.end);
    //  formOnSubmit(form, region)
     form.onreset = function() {
         // form.style.opacity = 0;
        //  transcriptionFormDisplay(form);
         form.dataset.region = null;
     };
     form.dataset.region = region.id;
 }
 
 // save partial transcription details
 function formOnSubmit(form, region) {
     // console.log('formOnSubmit(form, region) region', region)
     form.onsubmit = function(e) {
         e.preventDefault();
         // morphData = morphemeDetails();
         // let sentenceData = new Object();
         // if (region.data.sentence) {
         //     sentenceData = region.data.sentence
         //     sentData = sentenceDetails(sentenceData);
         // }
         // else {
         //     sentData = sentenceDetails(sentenceData);
         // }
         // console.log(morphData);
         // $(".containerremovesentencefield1").remove();
         // document.getElementById("activeSentenceMorphemicBreak").checked = false;
         // rid = region.start.toFixed(2);
         // console.log('formOnSubmit(form, region) form', form)
         let regions = JSON.parse(localStorage.regions)
         for (i=0; i<regions.length; i++) {
             if (regions[i]['start'] === region.start &&
                 regions[i]['end'] === region.end) {
                     rid = region.start.toString().slice(0, 4).replace('.', '').concat(region.end.toString().slice(0, 4).replace('.', ''));
                     sentence = regions[i]['data']['sentence']
                     sentece = updateSentenceDetailsOnSaveBoundary(rid, sentence, region, form)
                 }
             }
         // console.log('formOnSubmit(form, region) sentence', sentence)  
         // localStorage.setItem("regions", JSON.stringify(regions));
         // console.log('regions', regions)
 
         region.update({
             start: form.elements.start.value,
             end: form.elements.end.value,
             data: {
                 // note: form.elements.note.value,
                 sentence: sentence
             }
         });
         // something = window.open("data:text/json," + encodeURIComponent(sentData),
         //                "_blank");
         // something.focus();
         // form.style.opacity = 0;
         transcriptionFormDisplay(form);
     };
 }
 
 /**
  * Display annotation.
  */
//  function showNote(region) {
//      if (!showNote.el) {
//          showNote.el = document.querySelector('#subtitle');
//      }
//      showNote.el.textContent = region.data.note || '–';
//  }
 
 function updateSentenceDetailsOnSaveBoundary(boundaryID, sentence, region, form) {
 
     for (let [key, value] of Object.entries(sentence[boundaryID])) {
         // console.log(key, value)
         if (key === 'transcription') {
             for (let [k, v] of Object.entries(sentence[boundaryID][key])) {
                 // console.log(k, v)
                 eleName = 'transcription_'+k
                 sentence[boundaryID][key][k] = form[eleName].value
             }
         }
         else if (key === 'translation') {
             for (let [k, v] of Object.entries(sentence[boundaryID][key])) {
                 // console.log(k, v)
                 tk = k.split('-')[1]
                 eleName = 'translation_'+tk
                 sentence[boundaryID][key][k] = form[eleName].value
             }
         }
         else if (key === 'sentencemorphemicbreak') {
             for (let [k, v] of Object.entries(sentence[boundaryID][key])) {
                 // console.log(k, v)
                 eleName = 'morphsentenceMorphemicBreak_'+k
                 sentence[boundaryID][key][k] = form[eleName].value
             }
         }
         else if (key === 'morphemes') {
             // console.log('morphemes!!!!!!!!!!!!!!')
             for (let [k, v] of Object.entries(sentence[boundaryID][key])) {
                 // console.log(k, v)
                 if (form['morphcount'] !== undefined && k === 'IPA') {
                     morphCount = form['morphcount'].value
                     morphemeFor = k
                     actualTranscription = form['Transcription_'+morphemeFor].value.split(" ")
                     // console.log(actualTranscription)
                     morphemicBreakTranscription = form['morphsentenceMorphemicBreak_'+morphemeFor].value
                     // console.log(morphCount, morphemeFor, actualTranscription, morphemicBreakTranscription)
                     sentence[boundaryID][key][k] = morphemeDetails(actualTranscription, morphemicBreakTranscription)
                     
                     sentenceId = sentence[boundaryID]['sentenceId']
                     console.log("sentence[boundaryID]['sentenceId']", sentenceId)
                     morphemeIdMap = morphemeidMap(actualTranscription, morphemicBreakTranscription)
                     // console.log(morphemeIdMap);
                     glossAndpos = glossDetails(morphCount,
                                                 morphemeFor,
                                                 form,
                                                 morphemeIdMap,
                                                 sentenceId,
                                                 actualTranscription)
                     // console.log(glossAndpos)
                     sentence[boundaryID]['gloss'][k] = glossAndpos[0]
                     var tempgloss = Object()
                     tempgloss[boundaryID] = flattenObject(sentence[boundaryID]['gloss'])
                     console.log(tempgloss)
                     var temppos = Object()
                     sentence[boundaryID]['pos'] = glossAndpos[1]
                     temppos[boundaryID] = flattenObject(sentence[boundaryID]['pos'])
                     console.log(temppos)
 
                     activeprojectform = JSON.parse(localStorage.activeprojectform)
                     if ('glossDetails' in activeprojectform) {
                         var glossdetails = activeprojectform['glossDetails']
                         Object.assign(glossdetails, tempgloss)
                     }
                     else {
                         activeprojectform['glossDetails'] = tempgloss
                     }
                     // localStorage.setItem(activeprojectform.glossDetails, JSON.stringify(glossdetails));
                     if ('posDetails' in activeprojectform) {
                         var posdetails = activeprojectform['posDetails']
                         Object.assign(posdetails, temppos)
                     }
                     else {
                         activeprojectform['posDetails'] = temppos
                     }
                     // localStorage.setItem(activeprojectform.posDetails, JSON.stringify(posdetails))
                     localStorage.setItem("activeprojectform", JSON.stringify(activeprojectform));
                     // console.log(sentence)
                 }
                 // tk = k.split('-')[1]
                 // eleName = 'translation_'+tk
                 // sentence[boundaryID][key][k] = form[eleName].value
             }
         }
         // else if (key === 'gloss') {
         //     console.log('gloss!!!!!!!!!!!!!!')
         //     for (let [k, v] of Object.entries(sentence[boundaryID][key])) {
         //         console.log(k, v)
                 
         //         // if (form['morphcount'] !== undefined && k === 'IPA') {
         //         //     morphCount = form['morphcount'].value
         //         //     morphemeFor = k
         //         //     actualTranscription = form['Transcription_'+morphemeFor].value.split(" ")
         //         //     morphemicBreakTranscription = form['morphsentenceMorphemicBreakTranscription_'+morphemeFor].value
         //         //     console.log(morphCount, morphemeFor, actualTranscription, morphemicBreakTranscription)
         //         //     sentence[boundaryID][key][k] = morphemeDetails(actualTranscription, morphemicBreakTranscription)
         //         //     console.log(sentence)
         //         // }
         //         // tk = k.split('-')[1]
         //         // eleName = 'translation_'+tk
         //         // sentence[boundaryID][key][k] = form[eleName].value
         //     }
         // }
     }
     // console.log(sentence);
 
     let regions = JSON.parse(localStorage.regions)
     for (i=0; i<regions.length; i++) {
         if (regions[i]['start'] === region.start &&
             regions[i]['end'] === region.end) {
                 regions[i]['data']['sentence'] = sentence
             }
         }
     localStorage.setItem("regions", JSON.stringify(regions));
     // console.log('regions', regions)
     // console.log('updateSentenceDetails(boundaryID, sentence, region, form)', sentence)
 
     return sentence
 }
 
 function updateSentenceDetails(boundaryID, sentence, region) {
     // console.log(sentence)
     // if (sentence !== undefined ) {
     //     console.log(sentence)
     //     sentence[boundaryID] = {
     //         'start': region.start,
     //         'end': region.end
     //     }
     // }
     // else {
     if (sentence === undefined ) {    
         sentence = new Object()
         transcription = {}
         translation = {}
         sentencemorphemicbreak = {}
         morphemes = {}
         gloss = {}
         activeprojectform= JSON.parse(localStorage.getItem('activeprojectform'));
         // console.log('activeprojectform', activeprojectform)
         scriptCode = activeprojectform['scriptCode']
         
         // console.log(activeprojectform)
         // console.log(scriptCode)
         scripts = activeprojectform["Transcription Script"]
         translationscripts = activeprojectform["Translation Script"]
         translationlang = activeprojectform["Translation Language"]
         console.log(translationlang);
         for (i=0; i<scripts.length; i++) {
             script = scripts[i]
             script_code = scriptCode[scripts[i]]
             // console.log(lang_code)
             // console.log(scripts[i], script_code)
             // transcription[script_code] = ''
             // sentencemorphemicbreak[script_code] = ''
             // morphemes[script_code] = {}
             // gloss[script_code] = {}
             transcription[script] = ''
             sentencemorphemicbreak[script] = ''
             morphemes[script] = {}
             gloss[script] = {}
         }
         for (i=0; i<translationscripts.length; i++) {
             tscript_code = scriptCode[translationscripts[i]]
             lang_code = translationlang[i].slice(0, 3).toLowerCase()+'-'+tscript_code
             translation[lang_code] = ''
         }
         pos = {}
         tags = {}
         sentence[boundaryID] = {
             'start': region.start,
             'end': region.end,
             'transcription': transcription,
             'translation': translation,
             'sentencemorphemicbreak': sentencemorphemicbreak,
             'morphemes': morphemes,
             'gloss': gloss,
             'pos': pos,
             'tags': tags,
             'sentenceId': document.getElementById('lastActiveId').value
         }
         // }
         // let regions = JSON.parse(localStorage.regions)
         // for (i=0; i<regions.length; i++) {
         //     if (regions[i]['start'] === region.start &&
         //         regions[i]['end'] === region.end) {
         //             regions[i]['data']['sentence'] = sentence
         //         }
         //     }
         // localStorage.setItem("regions", JSON.stringify(regions));
         // console.log('regions', regions)
         // console.log('updateSentenceDetails(boundaryID, sentence, region)', sentence)
     }
     else {
         // console.log(boundaryID)
         // console.log(sentence)
         tempSentence = sentence
         sentence = new Object()
         sentence[boundaryID] = tempSentence
         sentence[boundaryID]['start'] = region.start,
         sentence[boundaryID]['end'] = region.end
     }
     let regions = JSON.parse(localStorage.regions)
         for (i=0; i<regions.length; i++) {
             if (regions[i]['start'] === region.start &&
                 regions[i]['end'] === region.end) {
                     regions[i]['data']['sentence'] = sentence
                 }
             }
         localStorage.setItem("regions", JSON.stringify(regions));
     //     console.log('regions', regions)
     //     console.log('updateSentenceDetails(boundaryID, sentence, region)', sentence)
     // console.log('return sentence', sentence)
     return sentence
 
 }
 
 function flattenObject(ob) {
 // const flattenObj = (ob) => {
  
     // The object which contains the
     // final result
     let result = {};
  
     // loop through the object "ob"
     for (const i in ob) {
  
         // We check the type of the i using
         // typeof() function and recursively
         // call the function again
         if ((typeof ob[i]) === 'object' && !Array.isArray(ob[i])) {
             const temp = flattenObject(ob[i]);
             for (const j in temp) {
  
                 // Store temp in result
                 result[i + '.' + j] = temp[j];
             }
         }
  
         // Else store ob[i] in result directly
         else {
             result[i] = ob[i];
         }
     }
     return result;
 };
 
 function sentenceDetails(sentenceData) {
    //  formData = document.forms.edit.elements;
    formData = document.forms[document.forms.length-1].elements;
     // console.log(typeof formData)
     // let sentenceData = new Object();
     let transcriptionData = new Object();
     if (Object.keys(sentenceData).includes('transcription')) {
         transcriptionData = sentenceData['transcription']
     }
     let translationData = new Object();
     let tagsData = new Object();
     let morphData = new Object();
     if (Object.keys(sentenceData).includes('morphemes')) {
         morphData = sentenceData['morphemes']    
     }
     let glossData = new Object();
     if (Object.keys(sentenceData).includes('gloss')) {
         glossData = sentenceData['gloss']
     }
     activetranscriptionscript = displayRadioValue();
     var transcriptionScriptLocalStorage = JSON.parse(localStorage.getItem("Transcription Script"));
     // console.log('transcriptionScriptLocalStorage', transcriptionScriptLocalStorage)
     for (i = 0; i<transcriptionScriptLocalStorage.length; i++) {
         for (let [key, value] of Object.entries(formData)) {
             eleName = value.name;
             ename = value.name.replace(activetranscriptionscript, '');
             // console.log(eleName, ename)
             if (eleName !== '') {
                 // console.log(key, value.name, formData[eleName].value);
 
                 if (ename.includes('Transcription') && !ename.includes('active')) {
                     // console.log('!!!!!!!!!!!!!!!', key, value.name, formData[eleName].value);
                     transcriptionData[value.name] = formData[eleName].value;
                 }
                 else if (ename.includes('Translation') && !ename.includes('active')) {
                     translationData[value.name] = formData[eleName].value;
                 }
                 else if (ename.includes('Tags') && !ename.includes('active')) {
                     tagsData[value.name] = formData[eleName].value;
                 }
                 else if (ename.includes('activeSentenceMorphemicBreak')) {
                     sentenceData[value.name+'_'+activetranscriptionscript] = formData[eleName].value;
                 }
                 else if (eleName.includes('morphcount') && eleName.includes(transcriptionScriptLocalStorage[i])) {
                     // console.log('morphcountTranscription_'+transcriptionScriptLocalStorage[i]);
                     morphCount = formData[eleName].value
                     morphemeFor = transcriptionScriptLocalStorage[i]
                     actualTranscription = formData['Transcription_'+morphemeFor].value.split(" ")
                     morphemicBreakTranscription = formData['morphsentenceMorphemicBreakTranscription_'+morphemeFor].value
                     morphData[morphemeFor] = morphemeDetails(actualTranscription, morphemicBreakTranscription)
                     morphemeIdMap = morphemeidMap(actualTranscription, morphemicBreakTranscription)
                     glossData[morphemeFor] = glossDetails(morphCount,
                                                             morphemeFor,
                                                             formData,
                                                             morphemeIdMap)
                     // console.log('morphData', morphData)
                 }
                 // else if (eleName.includes('morph') && eleName.includes(activetranscriptionscript)) {
                 //     morphData[value.name] = formData[eleName].value;
                 // }
                 else {
                     // console.log(key, value.name, formData[eleName].value);
                     sentenceData[value.name] = formData[eleName].value;
                 }
 
             }
         }
     }
     sentenceData['transciption'] = transcriptionData
     sentenceData['translation'] = translationData
     sentenceData['tags'] = tagsData
     sentenceData['morphemes'] = morphData
     sentenceData['gloss'] = glossData
     bid = sentenceData['start'].toString().slice(0, 4).replace('.', '').concat(sentenceData['end'].toString().slice(0, 4).replace('.', ''));
     sentenceData['boundaryID'] = bid
     // console.log(sentenceData);
     
     return sentenceData;
 }
 
 function morphemeDetails(actualTranscription, morphemicBreakTranscription) {
     // console.log('morphemeDetails!!!!!!!!!')
     replaceObj = new RegExp('[#]', 'g')
     // morphemicBreakTranscription = morphemicBreakTranscription.replace('#', '').split(" ")
     morphemicBreakTranscription = morphemicBreakTranscription.replace(replaceObj, '').split(" ")
     morphemeData = mapArrays(actualTranscription, morphemicBreakTranscription)
 
     console.log(morphemeData);
 
     return morphemeData
 }
 
 // function glossDetails(morphCount, morphemeFor, formData, actualTranscription, morphemicBreakTranscription) {
 function glossDetails(morphCount,
                         morphemeFor,
                         formData,
                         morphemeIdMap,
                         sentenceId,
                         actualTranscription) {
     
     console.log(sentenceId)
     // console.log(actualTranscription, morphemicBreakTranscription)
     // console.log(formData)
     let glossData = new Object();
     // for (i=1; i<=actualTranscription.length; i++) {
     //     wordId = 'W00'+String(i)
     //     glossData[wordId] = {}
     // }
     console.log(glossData);
     let pos = new Object();
     for (i=1; i<=morphCount; i++) {
         let glossSubData = new Object();
         glossSubData[i] = {}
         let morpheme = ''
         let lexgloss = ''
         let lextype = ''
         for (let [key, value] of Object.entries(formData)) {
             // console.log(key, value)
             if (value !== undefined) {
                 eleName = value.name;
             }
             else {
                 eleName = ''
             }
             // console.log(eleName)
             if (eleName.includes(i) &&
                 eleName.includes(morphemeFor)) {
                 // console.log(eleName);
                 if (eleName.includes('morpheme')) {
                     morpheme = formData[eleName].value
                     // console.log(morpheme)
                 }
                 else if (eleName.includes('gloss')) {
                     lexgloss = {
                         "eng-Latn": formData[eleName].value
                     }
                 }
                 else if (eleName.includes('lextype')) {
                     lextype = formData[eleName].value
                 }
                 else if (eleName.includes('pos')) {
                     morphemeIdWord = morphemeIdMap[i][2]
                     wordId = morphemeIdMap[i][0]
                     // pos[morphemeIdMap[i]] = formData[eleName].value
                     pos[wordId] = {}
                     pos[wordId][i] = {}
                     pos[wordId][i][morphemeIdWord] = formData[eleName].value
                 }
                 // else if (eleName.includes('gloss')) {
                     
                 // }
             }
         }
         // datetime = new Date()
         // console.log(datetime.toJSON());
         glossSubData[i][morpheme] = {
             'lexemeId': sentenceId+'L'+String(i),
             'lexgloss': lexgloss,
             'lextype': lextype
         }
         // console.log(glossSubData);
         // console.log(morphemeIdMap[i]);
         // if (morphemeIdMap[i] in glossData) {
         //     Object.assign(glossData[morphemeIdMap[i]], glossSubData)
         // }
         // else {
         //     glossData[morphemeIdMap[i]] = glossSubData
         // }
         morphemeIdWord = morphemeIdMap[i][2]
         wordId = morphemeIdMap[i][0]
         // console.log(i, morphemeIdMap[i], morphemeIdWord, wordId)
         if (wordId in glossData) {
             if (morphemeIdWord in glossData[wordId]) {
                 Object.assign(glossData[wordId][morphemeIdWord], glossSubData)
             }
             else {
                 glossData[wordId][morphemeIdWord] = glossSubData
             }
         }
         else {
             glossData[wordId] = {}
         }
         if (morphemeIdWord in glossData[wordId]) {
             Object.assign(glossData[wordId][morphemeIdWord], glossSubData)
         }
         else {
             glossData[wordId][morphemeIdWord] = glossSubData
         }
         // console.log(glossData);
     }
     console.log(glossData);
     // console.log(pos)
 
     return [glossData, pos]
 }
 
 function morphemeidMap(actualTranscription, morphemicBreakTranscription) {
     morphemicBreakTranscription = morphemicBreakTranscription.split(" ")
     // replaceObj = new RegExp('[#]', 'g')
     // morphemicBreakTranscription = morphemicBreakTranscription.replace(replaceObj, '').split(" ")
     glossDataMapping = mapArrays(actualTranscription, morphemicBreakTranscription)
     console.log(glossDataMapping);
     // let glossData = new Object();
     let morphemeIdMap = new Object();
     mCount = 0;
     // wCount = 1
     for (let [wordkey, wordvalue] of Object.entries(glossDataMapping)) {
         console.log(wordkey, wordvalue)
         for (let [key, value] of Object.entries(wordvalue)) {
             console.log(key, value);
             // let glossSubData = new Object();
             // wordId = 'W00'+String(wCount)
             if (value.includes('#')) {
                 v = value.replace('#', '').replace('-', '')
                 value = value.split('#')
                 for (i=0; i<value.length; i++) {
                     // glossSubData[value[i]] = {}
                     // glossData[key] = glossSubData
                     mCount += 1
                     morphemeIdMap[mCount] = [wordkey, value[i], v]
                 }
             }
             else {
                 // glossSubData[value] = {}
                 // glossData[key] = glossSubData
                 mCount += 1
                 morphemeIdMap[mCount] = [wordkey, value, value]
             }
             // wCount += 1
         }
     }   
     // console.log(glossData);
     console.log(morphemeIdMap)
     return morphemeIdMap;
 }
 
 function mapArrays(array_1, array_2) {
     if(array_1.length != array_2.length || 
         array_1.length == 0 || 
         array_2.length == 0) {
         return null;
        }
     let mappedData = new Object();
     
     function mapping(item, index, arr) {
         // console.log(item, index, arr);
         wordmap = new Object();
         wordmap[item] = array_2[index]
         mappedData['W00'+String(index+1)] = wordmap
     }
 
      // Using the foreach method
     // array_1.forEach((k, i) => {mappedData[k] = array_2[i]})
     // array_1.forEach((k, i) => { mappedData['W00'+String(i+1)] = {k: array_2[i]} })
     array_1.forEach(mapping);
 
     return mappedData;
 }
 
 function scriptCodeToLang(transcriptionkey, scriptCode, langScript) {
     let script = '';
     let lang = '';
     for (let [key, value] of Object.entries(scriptCode)) {
         if (value === transcriptionkey) {
             script = key
         }
     }
 }
 
 function createSentenceForm(formElement, boundaryID) {
     // var activeSentenceMorphemicBreak = '<input type="checkbox" id="activeSentenceMorphemicBreak" name="activeSentenceMorphemicBreak" value="false" onclick="">'+
     //                                     '<label for="activeSentenceMorphemicBreak">&nbsp; Add Interlinear Gloss</label><br></br>'
     // // document.getElementById("sentencefield2").innerHTML = "";                                        
     // $(".sentencefield").html(activeSentenceMorphemicBreak);
     console.log('createSentenceForm(formElement)', formElement)
     inpt = '';
     activeprojectform = JSON.parse(localStorage.activeprojectform)
     for (let [key, value] of Object.entries(formElement)) {
         // console.log(key, value)
         if (key === 'transcription') {
             var transcriptionScript = formElement[key];
             console.log('Object.keys(transcriptionScript)[0]', Object.keys(transcriptionScript)[0]);
             firstTranscriptionScript = Object.keys(transcriptionScript)[0]
             for (let [transcriptionkey, transcriptionvalue] of Object.entries(transcriptionScript)) {
                 // activeprojectform = JSON.parse(localStorage.getItem('activeprojectform'));
                 // // console.log('activeprojectform', activeprojectform)
                 // scriptCode = activeprojectform['scriptCode']
                 // langScript = activeprojectform['langScript']
                 // lang = scriptCodeToLang(transcriptionkey, scriptCode, langScript)
                 sentencemorphemicbreakvalue = formElement['sentencemorphemicbreak'][transcriptionkey]
                 // console.log("formElement['sentencemorphemicbreak']", sentencemorphemicbreakvalue)
                 inpt += '<div class="form-group">';
                 inpt += '<label for="Transcription_'+ transcriptionkey +'">Transcription in '+ transcriptionkey +'</label>'+
                         '<input type="text" class="form-control" id="Transcription_'+ transcriptionkey +'"'+ 
                         'placeholder="Transcription '+ transcriptionkey +'" name="transcription_'+ transcriptionkey +'"'+
                         'value="'+ transcriptionvalue +'" required><br>';
                         // '</div></div>';
                 if (transcriptionkey === firstTranscriptionScript) {
                     // activeprojectform = JSON.parse(localStorage.activeprojectform)
                     if ('glossDetails' in activeprojectform &&
                         boundaryID in activeprojectform['glossDetails']) {
                         glossdetails = activeprojectform['glossDetails'][boundaryID]
                         posdetails = activeprojectform['posDetails'][boundaryID]
                         // console.log(glossdetails)
                         // console.log(posdetails)
                         inpt += '<div id="morphemicDetail_'+transcriptionkey+'" style="display: none;">'+
                                 '<p><strong>Give Morphemic Break</strong></p>'+
                                 '<p><strong>**(use "#" for word boundary(if there are affixes in the word) and "-" for morphemic break)</strong></p>'+
                                 '<div class="form-group"><div class="input-group">'+
                                 '<input type="text" class="form-control" name="morphsentenceMorphemicBreak_' + transcriptionkey +'"'+
                                 'placeholder="e.g. I have re-#write#-en the paper#-s"'+
                                 'id="sentenceMorphemicBreak_' + transcriptionkey +'" value="'+sentencemorphemicbreakvalue+'" readonly>';
 
                         inpt += '<div class="input-group-btn" id="editsentmorpbreak">'+
                                 '<button class="btn btn-warning" type="button" id="editSentenceField"'+
                                 'onclick="editMorphemicBreakSentence(\''+transcriptionvalue+'\', \''+transcriptionkey+'\');">'+
                                 '<span class="glyphicon glyphicon-edit" aria-hidden="true"></span>'+ 
                                 '</button></div>';
                         createEditableGlossForm(transcriptionvalue,
                                                 transcriptionkey,
                                                 sentencemorphemicbreakvalue,
                                                 glossdetails,
                                                 posdetails,
                                                 boundaryID)
                     }
                     else {
                         inpt += '<div id="morphemicDetail_'+transcriptionkey+'" style="display: none;">'+
                             '<p><strong>Give Morphemic Break</strong></p>'+
                             '<p><strong>**(use "#" for word boundary(if there are affixes in the word) and "-" for morphemic break)</strong></p>'+
                             '<div class="form-group"><div class="input-group">'+
                             '<input type="text" class="form-control" name="morphsentenceMorphemicBreak_' + transcriptionkey +'"'+
                             'placeholder="e.g. I have re-#write#-en the paper#-s"'+
                             'id="sentenceMorphemicBreak_' + transcriptionkey +'" value="'+sentencemorphemicbreakvalue+'">';
 
                         inpt += '<div class="input-group-btn"  id="editsentmorpbreak">'+
                                 '<button class="btn btn-success" type="button" id="checkSentenceField"'+
                                 'onclick="getSentence(\''+transcriptionvalue+'\', \''+transcriptionkey+'\');">'+
                                 '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>'+ 
                                 '</button></div>';
                     }
                 }
                 else {
                     inpt += '<div id="morphemicDetail_'+transcriptionkey+'" style="display: none;">'+
                             '<p><strong>Give Morphemic Break</strong></p>'+
                             '<p><strong>**(use "#" for word boundary(if there are affixes in the word) and "-" for morphemic break)</strong></p>'+
                             '<div class="form-group"><div class="input-group">'+
                             '<input type="text" class="form-control" name="morphsentenceMorphemicBreak_' + transcriptionkey +'"'+
                             'placeholder="e.g. I have re-#write#-en the paper#-s"'+
                             'id="sentenceMorphemicBreak_' + transcriptionkey +'" value="'+sentencemorphemicbreakvalue+'">';
                     inpt += '<div class="input-group-btn">'+
                             '<button class="btn btn-success" type="button" id="checkSentenceField"'+
                             'onclick="getSentence(\''+transcriptionvalue+'\', \''+transcriptionkey+'\');" disabled>'+
                             '<span class="glyphicon glyphicon-unchecked" aria-hidden="true"></span>'+ 
                             '</button></div>';
                 }
                 inpt += '</div></div></div></div>';
             }
             document.getElementById("transcription2").innerHTML = "";
             $('.transcription1').append(inpt);
             inpt = '';
         }
         else if (key === 'translation') {
         var activeTranslationField = '<input type="checkbox" id="activeTranslationField" name="activeTranslationField" value="false" onclick="activeTranslationLangs()" checked disabled>'+
                                         '<label for="activeTranslationField">&nbsp; Add Translation</label><br></br>'+
                                         '<div id="translationlangs" style="display: block;"></div>';
         document.getElementById("translationfield2").innerHTML = "";                                
         $(".translationfield1").append(activeTranslationField);
         translationLang = formElement[key];
         // console.log(translationLang)
         translang = activeprojectform["Translation Language"]
         // console.log(translang)
         translangcount = -1
         for (let [translationkey, translationvalue] of Object.entries(translationLang)) {
             translangcount += 1
             console.log(translationkey, translationvalue);
             translationkey = translationkey.split('-')[1]
             inpt += '<div class="form-group">'+
                     '<label for="Translation_'+ translationkey +'">Translation in '+ translang[translangcount] +'</label>'+
                     '<input type="text" class="form-control" id="Translation_'+ translationkey +'"'+ 
                     'placeholder="Translation '+ translationkey +'" name="translation_'+ translationkey + '"'+
                     'value="'+ translationvalue +'" required>'+
                     '</div></div>';          
         }
         document.getElementById("translationlangs").innerHTML = "";
         $('#translationlangs').append(inpt);
         inpt = '';
         }
         else if (key === 'pos') {
 
         }
         else if (key === 'tags') {
         var tagsData = formElement[key]
         let value = ''
         for (let [tagskey, tagsvalue] of Object.entries(tagsData)) {
             value = value+';'+tagskey+':'+tagsvalue
         }
         var activeTagsField = '<input type="checkbox" id="activeTagsField" name="activeTagsField" value="false" onclick="activeTags()">'+
                             '<label for="activeTagsField">&nbsp; Add Tags</label><br></br>'+
                             '<div id="tags" style="display: none;">'+
                             '<div class="form-group">'+
                             '<label for="Tags">Tags</label>'+
                             '<input type="text" class="form-control" id="Tags" name="Tags" value="'+value+'">'+
                             '</div></div></div>';
         // document.getElementById("tagsfield2").innerHTML = "";          
         // $(".tagsfield1").append(activeTagsField);
         inpt = '';
         }
         // else if (key === 'gloss') {
         //     activeprojectform = JSON.parse(localStorage.activeprojectform)
         //     glossDetail = activeprojectform['glossDetails']
         //     console.log("glossDetails['glossDetails']", glossDetails)
         //     console.log("glossDetails['glossDetails']", glossDetails['glossDetails'])
         //     inpt = '';
         //     inpt = createEditableGlossForm(glossDetails)
 
         //             }
         // else if (key == 'morphemes' ||
         //             key == 'gloss' ||
         //             key == 'pos') {
         //                 inpt = '';
         //             }
         // else if (key == 'start' ||
         //             key == 'end') {
         //                 inpt = '';
         //             }
     }
 
     $("#activeSentenceMorphemicBreak").click(function() {
         // activetranscriptionscript = displayRadioValue();
         eleid = 'Transcription_'+Object.keys(transcriptionScript)[0]
         activetranscriptionscriptvalue = document.getElementById(eleid).value;
         if (activetranscriptionscriptvalue === '') {
           document.getElementById("activeSentenceMorphemicBreak").checked=false;
           alert('No input given in the selected transcription script!');  
         }
         else {
           activeMorphSentenceField(activetranscriptionscriptvalue, eleid);
         }
       });
 }
 
 function createEditableGlossForm(value,
                                     name,
                                     sentencemorphemicbreakvalue,
                                     glossdetails,
                                     posdetails,
                                     boundaryID) {
     console.log(value, name);
     var morphemicSplitSentence = [];
 
     sentence = value.trim().split(' ');
     sentence_morphemic_break_full = sentencemorphemicbreakvalue.trim(); // Find the text
     sentence_morphemic_break = sentencemorphemicbreakvalue.trim().split(' '); // Find the text
 
 
     // console.log(sentence, sentence_morphemic_break)
 
     if (sentence.length === 1 && sentence[0] === "") {
         alert('No input given!');
         document.getElementById("checkSentenceField" + sid).disabled = false;
         return false;
     }
     if (sentence_morphemic_break.length === 1 && sentence_morphemic_break[0] === "") {
         alert('No input given!');
         document.getElementById("checkSentenceField").disabled = false;
         return false;
     }
 
     if (sentence_morphemic_break_full.includes('-')) {
         morph_len = (sentence_morphemic_break_full.match(/-/g)||[]).length;
         boundary_len = (sentence_morphemic_break_full.match(/#/g)||[]).length;
         // console.log(morph_len)
         // console.log(boundary_len)
         if (morph_len != boundary_len) {
             alert("Number of # ("+boundary_len+") not equal to numer of - ("+morph_len+") in the morphemic break")
             document.getElementById("checkSentenceField" + sid).disabled = false;
             return false;
         }
     }
 
     for (i = 0; i < sentence_morphemic_break.length; i++) {
         if (sentence_morphemic_break[i].includes('#')) {
             morphSplit = sentence_morphemic_break[i].split('#')
             for (j = 0; j < morphSplit.length; j++) {
                 morphemicSplitSentence.push(morphSplit[j]);
             }  
         }
         else {
             morphemicSplitSentence.push(sentence_morphemic_break[i]);
         }
     }
     // console.log('morphemicSplitSentence', morphemicSplitSentence);
     // getEditableWordPos(morphemicSplitSentence, name);
     morphemepos = getEditableWordPos(morphemicSplitSentence, name, boundaryID, glossdetails, posdetails);
     // console.log(morphemepos);
     // morphemeEditableFields(morphemicSplitSentence, name, morphemepos, glossdetails);
 }  
 
 function getEditableWordPos(morphemicSplitSentence, name, boundaryID, glossdetails, posdetails) {
     $.getJSON('/predictPOSNaiveBayes', {
 
         a:String(morphemicSplitSentence)
         }, function(data) {
             console.log(data.predictedPOS);
             
 
             // var morphemePOS = data.predictedPOS;
             var morphemePOS = [];
             // activeprojectform= JSON.parse(localStorage.getItem('activeprojectform'));
             // editablePOS = activeprojectform['transcriptionDetails']['data']['sentence'][boundaryID]['pos']
             // console.log(editablePOS);
             // for (let [wordId, wordpos] of Object.entries(editablePOS)) {
             //     for (let [morph, morphpos] of Object.entries(wordpos)) {
             //         morphemePOS.push([morph, morphpos])
             //     }
             // }
             // console.log(morphemePOS);
             morphemeEditableFields(morphemicSplitSentence, name, morphemePOS, glossdetails, posdetails);
         });   
         return false; 
 }
 
 function morphemeEditableFields(morphemicSplitSentence, name, morphemePOS, glossdetails, posdetails) {
 
   // console.log(morphemePOS);
   var morphemeinput = '</br><div class="morphemefield_' + name + '">';
   morphemeinput += '<div class="row">'+
   '<div class="col-sm-3"><strong>Morphemes</strong></div>'+
   '<div class="col-sm-3"><strong>Gloss</strong></div>'+
   '<div class="col-sm-3"><strong>Morph Type</strong></div>'+
   '<div class="col-sm-3"><strong>POS</strong></div>'+
   '</div>';
   // var morphemeinput = '';
   morphemeCount = morphemicSplitSentence.length
   for(let i = 0; i < morphemeCount; i++) {
     morphemicgloss = ''
     morphemiclextype = ''
     pos = ''
     // console.log(morphemePOS[i]);
     // console.log(sentence[i]);
     // console.log('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!morph_gloss_' + name + '_' +  (i+1))
     for (let [morphkey, morphvalue] of Object.entries(glossdetails)) {
         // console.log(i+1, morphkey, morphvalue, morphemicSplitSentence[i])
         morphkey = morphkey.split('.')
         // console.log(i+1, morphkey, morphvalue, morphemicSplitSentence[i])
         // console.log(morphkey[2], morphkey[3], morphkey[4])
         if (morphkey[3] === String(i+1) && morphkey[4] === morphemicSplitSentence[i]) {
             // console.log(morphkey[2], morphkey[3], morphkey[4])
             if (morphkey[5].includes('gloss')) {
                 // console.log(morphkey[2], morphkey[3], morphkey[4])
                 // console.log(i+1, morphkey, morphvalue, morphemicSplitSentence[i])
                 morphemicgloss = morphvalue
                 
             }
             else if (morphkey[5].includes('lextype')) {
                 // console.log(morphkey[2], morphkey[3], morphkey[4])
                 // console.log(i+1, morphkey, morphvalue, morphemicSplitSentence[i])
                 morphemiclextype = morphvalue
             }
             // console.log(i, morphkey, morphvalue)
         }
         // console.log(morphemicSplitSentence[i], morphemicgloss)
     }
     for (let [poskey, posvalue] of Object.entries(posdetails)) {
         // console.log(poskey, posvalue)
         poskey = poskey.split('.')
         if (poskey[1] === String(i+1)) {
             pos = posvalue
         }
         
     }
     // console.log(pos)
     // console.log('morphemicgloss', morphemicgloss)
     if (morphemicSplitSentence[i].includes('-')) {
         // console.log(morphemicSplitSentence[i], morphemicgloss)
         morphemeinput += '<div class="input-group">'+
             '<input type="text" class="form-control" name="morph_morpheme_' + name + '_' +  (i+1) +'"'+
             'placeholder="'+ morphemicSplitSentence[i] +'" value="'+morphemicSplitSentence[i]+'"'+
             'id="morphemeField' + name + (i+1) +'" readonly/>'+
             '<span class="input-group-btn" style="width:50px;"></span>'+
             '<select class="morphemicgloss' + name + (i+1) +'" name="morph_gloss_' + name + '_' +  (i+1) +'"'+
             ' multiple="multiple" style="width: 210px">';
         if (morphemicgloss != '') {
             morphemeinput += '<option value="'+morphemicgloss+'" selected>'+morphemicgloss+'</option>';
         }
         morphemeinput += '</select>'+
             '<span class="input-group-btn" style="width:50px;"></span>'+
             '<select class="lextype' + name + (i+1) +'" name="morph_lextype_' + name + '_' +  (i+1) +'"'+
             ' style="width: 210px">';
         morphemeinput += '<option value="'+morphemiclextype+'" selected>'+morphemiclextype+'</option>';
         morphemeinput += '</select>'+
             '<span class="input-group-btn" style="width:50px;"></span></div><br>';
         // console.log(morphemeinput);                  
     }
     else {
         morphemeinput += '<div class="input-group">'+
             '<input type="text" class="form-control" name="morph_morpheme_' + name + '_' +  (i+1) +'"'+
             'placeholder="'+ morphemicSplitSentence[i] +'" value="'+ morphemicSplitSentence[i] +'"'+
             'id="morphemeField' + name + (i+1) +'" readonly/>'+
             '<span class="input-group-btn" style="width:50px;"></span>'+
             '<input type="text" class="form-control" name="morph_gloss_' + name + '_' +  (i+1) +'"'+
             ' id="morphemicgloss' + name + (i+1) +'" value="'+morphemicgloss+'"/>'+
             '<span class="input-group-btn" style="width:50px;"></span>'+
             '<select class="lextype' + name + (i+1) +'" name="morph_lextype_' + name + '_' +  (i+1) +'"'+
             ' style="width: 210px"';
             // console.log(morphemicSplitSentence[i], morphemePOS[i][1])
         morphemeinput += '<option value="'+morphemiclextype+'" selected>'+morphemiclextype+'</option>';
         morphemeinput += '</select>'+
             '<span class="input-group-btn" style="width:50px;"></span>'+
             '<select class="pos' + name + (i+1) +'" name="morph_pos_' + name + '_' +  (i+1) +'" style="width: 210px">'+
             // '<option value="'+ morphemePOS[i][1] +'" selected>'+ morphemePOS[i][1] +'</option>'+
             '<option value="'+ pos +'" selected>'+ pos +'</option>'+
             '</select></div><br>';
 
     }
   }
   morphemeinput += ' <input type="text" id="morphcount" name="morphcount'+ name +'" value="'+ morphemeCount +'" hidden>'
 //   console.log(morphemeinput)
 //   console.log(".morphemicDetail_"+name)
   $("#morphemicDetail_"+name).append(morphemeinput);
 
   for(let i = 0; i < morphemicSplitSentence.length; i++) {
     $('.morphemicgloss'+ name +(i+1)).select2({
     tags: true,
     placeholder: 'Gloss',
     data: morphemicGloss,
     allowClear: true
     // sorter: false
     });
   
     $('.lextype'+ name +(i+1)).select2({
     tags: true,
     placeholder: 'Morph Type',
     data: morphType
     // allowClear: true,
     // sorter: false
     });
   
     $('.pos'+ name +(i+1)).select2({
     tags: true,
     placeholder: 'POS',
     data: posCategories
     // allowClear: true,
     // sorter: false
     // width: 'element'
     });
   
     }
 }
 
 function createMorphemeForm(form, region) {
     if (region.data.morphemicData.activeSentenceMorphemicBreak == "true") {
         // console.log(region.data.note);
         document.getElementById("activeSentenceMorphemicBreak").checked = true;
         $(".containerremovesentencefield1").remove();
         activeMorphSentenceField();
         if (region.data.morphemicData.sentenceMorphemicBreak1) {
             form.elements.sentenceMorphemicBreak1.value = region.data.morphemicData.sentenceMorphemicBreak1
             getSentence(1);
             setTimeout(function() {
                 for (let [key, value] of Object.entries(region.data.morphemicData)) {
                     // console.log(key, value, form.elements[key].tagName);
                     if (form.elements[key] !== undefined && form.elements[key].tagName == "SELECT") {
                         // console.log(key, value, form.elements[key]);
                         form.elements[key].value = value
                     }
                     else if (form.elements[key] !== undefined) {
                         form.elements[key].value = value
                     }
                 }
             }, 100);
             
         }
     }
 
 }
 
//  $("#stopAudio").click(function() {
//      wavesurfer.stop();
//      playPauseState = $(".audioplaypause").attr('class');
//      if (playPauseState.includes('glyphicon-pause')) {
//          $(".audioplaypause").addClass('glyphicon-play').removeClass('glyphicon-pause');
//      }
//  });

 document.querySelector(
    '[data-action="stop-audio"]'
).addEventListener('click', function() {
    console.log('STOP-AUDIO');
    wavesurfer.stop();
     playPauseState = $(".audioplaypause").attr('class');
     if (playPauseState.includes('glyphicon-pause')) {
         $(".audioplaypause").addClass('glyphicon-play').removeClass('glyphicon-pause');
     }
});
 
 $("#playPauseAudio").click(function() {
     wavesurfer.playPause();
     playPauseState = $(".audioplaypause").attr('class');
     // console.log(playPauseState)
     if (playPauseState.includes('glyphicon-play')) {
         $(".audioplaypause").addClass('glyphicon-pause').removeClass('glyphicon-play');
     }
     else if (playPauseState.includes('glyphicon-pause')) {
         $(".audioplaypause").addClass('glyphicon-play').removeClass('glyphicon-pause');
     }
 });
 
 function transcriptionFormDisplay(form, mode) {
     if (form.style.display === "none") {
         form.style.display = "block";
     } 
     else if (form.style.display === "block" && mode==='edit') {
         form.style.display = "block";
     }
     else {
         form.style.display = "none";
     }
 }
 
 function getActiveTranscription() {
     // console.log('Hi')
     activetranscriptionscript = displayRadioValue()
     // console.log(activetranscriptionscript);
    //  let form = document.forms.edit;
    let form = document.forms[document.forms.length-1];
     let id = form.dataset.region;
     let wavesurferregion = wavesurfer.regions.list[id];
     // console.log(wavesurferregion)
     transcriptionDetailsOnChange(form, wavesurferregion)
     // console.log(form)
     // console.log(regionId)
     // console.log(document.getElementById('start').value)
     start = document.getElementById('start').value
     end = document.getElementById('end').value
     rid = start.toString().slice(0, 4).replace('.', '').concat(end.toString().slice(0, 4).replace('.', ''));
     // console.log(rid);
     regions = JSON.parse(localStorage.regions)
     for (i=0; i<regions.length;i++) {
       region = regions[i];
     //   console.log(region)
       if (region['boundaryID'] === rid && 'sentence' in region.data) {
         if (!(activetranscriptionscript in region.data.sentence)) {
         //   console.log(region)
           document.getElementById("activeSentenceMorphemicBreak").checked = false;
           $(".containerremovesentencefield").remove();
         }
       }
     }
   }
 
 //  change in trancription radio button
 function transcriptionDetailsOnChange(form, region) {
     let sentenceData = new Object();
     if (region.data.sentence) {
         sentenceData = region.data.sentence
         sentData = sentenceDetails(sentenceData);
     }
     else {
         sentData = sentenceDetails(sentenceData);
     }
     region.update({
         start: form.elements.start.value,
         end: form.elements.end.value,
         data: {
             sentence: sentData
         }
     });
 }
 
 function getActiveRegionSentence(region) {
     var sentence = ''
     let regions = JSON.parse(localStorage.regions)
     for (i=0; i<regions.length; i++) {
         if (regions[i]['start'] === region.start &&
             regions[i]['end'] === region.end) {
                 // console.log('getActiveRegionSentence(region)', regions[i])
                 // if ('sentence' in regions[i]) {
                 //     console.log("'sentence' in Object.values(regions[i])")
                 //     sentence = Object.values(regions[i]['sentence'])[0]
                 //     console.log('sentence getActiveRegionSentence(region)', sentence)    
                 // }
                 if ('sentence' in regions[i]['data']) {
                     // console.log("'sentence' in Object.values(regions[i])")
                     sentence = Object.values(regions[i]['data']['sentence'])[0]
                     // console.log('sentence YES getActiveRegionSentence(region)', sentence)    
                 }
                 else {
                     // console.log('sentence NOT getActiveRegionSentence(region)', sentence)
                     sentence = undefined
                 }
                 return sentence
         }
     }
 } 
 
 