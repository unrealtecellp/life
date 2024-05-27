/**
 * Create a WaveSurfer instance.
 */
var wavesurfer; // eslint-disable-line no-var
var activeprojectform = JSON.parse(localStorage.getItem('activeprojectform'));
var audiowaveformData;
var boundaryCount;
var lstUpdatedBy;
var currentCursorTime = 0;

try {
    audiowaveformData = activeprojectform.audioMetadata.audiowaveform.data;
    boundaryCount = activeprojectform.boundaryCount;
    lstUpdatedBy = activeprojectform.lastUpdatedBy;
}
catch (err) {
    // console.log(typeof err.message);
    audiowaveformData = '';
    boundaryCount = '';
    lstUpdatedBy = '';
}

filePath = JSON.parse(localStorage.getItem('AudioFilePath'));
getAudiDuration(filePath);
showBoundaryCount(boundaryCount);
lastUpdatedBy(lstUpdatedBy)

// console.log(audiowaveformData);
/**
 * Init & load.
 */
document.addEventListener('DOMContentLoaded', function () {
    // Init wavesurfer
    wavesurfer = WaveSurfer.create({
        container: '#waveform',
        height: 120,
        pixelRatio: 1,
        scrollParent: true,
        normalize: true,
        // minimap: true,
        minPxPerSec: 10,
        backend: 'MediaElement',
        mediaControls: true,
        barWidth: 1,
        barGap: 3,
        // partialRender: true,
        plugins: [
            WaveSurfer.regions.create(),
            // WaveSurfer.minimap.create({
            //     height: 30,
            //     waveColor: '#ddd',
            //     progressColor: '#999',
            //     cursorColor: '#999'
            // }),
            // WaveSurfer.timeline.create({
            //     container: '#wave-timeline'
            // }),
            WaveSurfer.cursor.create({
                showTime: true,
                opacity: 1,
                customShowTimeStyle: {
                    'background-color': '#000',
                    color: '#fff',
                    padding: '2px',
                    // 'font-size': '10px'
                }
            }),
            // WaveSurfer.spectrogram.create({
            //     wavesurfer: wavesurfer,
            //     container: "#wave-spectrogram",
            //     labels: true,
            //     height: 256,
            // })
        ]
    });
    document.querySelector('#slider').oninput = function () {
        wavesurfer.zoom(Number(this.value));
    };

    // wavesurfer.load(filePath);
    if (audiowaveformData === '') {
        wavesurfer.load(filePath);

    }
    else {
        wavesurfer.load(filePath, audiowaveformData);
    }

    wavesurfer.on('ready', function (region) {

        wavesurfer.enableDragSelection({
            // color: randomColor(0.1)
            color: boundaryColor(255, 0, 0, 0.1),
        });

        if (localStorage.regions) {
            // console.log(localStorage.regions)
            loadRegions(JSON.parse(localStorage.regions));
        }
    });
    wavesurfer.on('region-dblclick', function (region, e) {
        updateCurrentCursorTime()
        // console.log(wavesurfer);
        // console.log(region);
        e.stopPropagation();
        // Play on click, loop on shift click
        e.shiftKey ? region.playLoop() : region.play();
    });
    wavesurfer.on('region-mouseenter', showRegionInfo);
    wavesurfer.on('region-mouseleave', hideRegionInfo);
    wavesurfer.on('region-click', editAnnotation);
    // wavesurfer.on('region-created', saveRegions);
    // wavesurfer.on('region-removed', saveRegions);
    // wavesurfer.on('region-updated', saveRegions);
    wavesurfer.on('region-update-end', saveRegions);
    wavesurfer.on('region-update-end', function (region) {
        preventOverlapBoundaries(region);
    });
    wavesurfer.on('region-update-end', editAnnotation);
    // wavesurfer.on('region-click', showNote);
    wavesurfer.on('region-click', showTranslationSubtitle);

    wavesurfer.on('region-play', function (region) {
        togglePlayPause(1);
        region.once('out', function () {
            wavesurfer.play(region.start);
            wavesurfer.pause();
        });
    });
    wavesurfer.on('finish', function () {
        // $(".audioplaypause").addClass('glyphicon-play').removeClass('glyphicon-pause');
        togglePlayPause(0);
        togglePlayPauseBoundary(0);
        togglePlayPauseBoundaryStart(0);
    });

    document.querySelector(
        '[data-action="delete-region"]'
    ).addEventListener('click', function () {
        // deleteBoundary();
        let form = document.forms.edit;
        // console.log(form.dataset, Object.keys(form.dataset), form);
        let regionId = form.dataset.region;
        // console.log(regionId);
        if (regionId) {
            let region = wavesurfer.regions.list[regionId];
            wavesurfer.regions.list[regionId].remove();

            form.reset();
            transcriptionFormDisplay(form);
            wavesurfer.pause();
            // console.log("Region", region)

            startId = get_boundary_id_from_number(parseFloat(region.start).toFixed(2), 5, "0"); //5 is the length of the returned string and 0 is the prefix
            endId = get_boundary_id_from_number(parseFloat(region.end).toFixed(2), 5, "0");

            // console.log('New', startId, endId)
            rid = startId.concat(endId);

            //Code retained for backward compatibility
            oldStartId = region.start.toString().slice(0, 4).replace('.', '');
            if (oldStartId === '0') {
                oldStartId = '000';
            }
            oldEndId = region.end.toString().slice(0, 4).replace('.', '');
            if (oldEndId === '0') {
                oldEndId = '000';
            }
            oldRid = oldStartId.concat(oldEndId);
            // console.log('Old', oldStartId, oldEndId)

            localStorageRegions = JSON.parse(localStorage.regions);
            // console.log("Local storage region id", rid, oldRid, localStorageRegions);

            for (let [key, value] of Object.entries(localStorageRegions)) {
                // console.log("Key, value", key, value)
                if ((key in localStorageRegions) &&
                    (localStorageRegions[key]['boundaryID'] === rid || localStorageRegions[key]['boundaryID'] === oldRid)) {
                    localStorageRegions.splice(key, 1)
                    // console.log(rid, oldRid, localStorageRegions)
                    localStorage.setItem("regions", JSON.stringify(localStorageRegions));
                }
            }
        }
    });

    document.querySelector(
        '[data-action="delete-region-all"]'
    ).addEventListener('click', function () {
        confirm_msg = confirm("Delete all boundaries?");
        // alert(confirm_msg);
        if (confirm_msg) {
            wavesurfer.clearRegions();
            // alert(wavesurfer.regions.list);
            localStorage.setItem("regions", "[]");
        }
    });
});

function get_boundary_id_from_number(number, length, prefix_string) {
    return number.toString().replace('.', '').padStart(length, prefix_string);
}

function deleteBoundary(regionId) {
    // console.log('deleteBoundary');
    let form = document.forms.edit;
    // let regionId = form.dataset.region;
    // console.log(form.dataset, Object.keys(form.dataset), form);
    if (regionId) {
        let region = wavesurfer.regions.list[regionId];
        wavesurfer.regions.list[regionId].remove();

        form.reset();
        // transcriptionFormDisplay(form);
        wavesurfer.pause();
        startId = get_boundary_id_from_number(parseFloat(region.start).toFixed(2), 5, "0"); //5 is the length of the returned string and 0 is the prefix
        endId = get_boundary_id_from_number(parseFloat(region.end).toFixed(2), 5, "0");

        // startId = region.start.toString().slice(0, 4).replace('.', '');
        // if (startId === '0') {
        //     startId = '000';
        // }
        // endId = region.end.toString().slice(0, 4).replace('.', '');
        // if (endId === '0') {
        //     endId = '000';
        // }
        // console.log(startId, endId)
        rid = startId.concat(endId);
        localStorageRegions = JSON.parse(localStorage.regions);
        for (let [key, value] of Object.entries(localStorageRegions)) {
            // console.log(key, value)
            if (key in localStorageRegions &&
                localStorageRegions[key]['boundaryID'] === rid) {
                localStorageRegions.splice(key, 1)
                // console.log(localStorageRegions)
                localStorage.setItem("regions", JSON.stringify(localStorageRegions));
            }
        }
    }
}

function updateCurrentCursorTime(from = '') {
    if (from == 'edit') {
        wavesurfer.on('seek', function (position) {
            currentCursorTime = position * wavesurfer.getDuration();
            // console.log(currentCursorTime)
        });
    }
    else {
        currentCursorTime = wavesurfer.getCurrentTime();
    }
}

/**
 * Save annotations to localStorage.
 */
function saveRegions(region) {
    // console.log(wavesurfer.regions.list);
    // region.color =  boundaryColor(255, 0, 0, 0.1),
    // console.log('WHERE')
    localStorage.regions = JSON.stringify(
        Object.keys(wavesurfer.regions.list).map(function (id) {
            let region = wavesurfer.regions.list[id];
            // console.log(region)
            region.drag = false;

            startId = get_boundary_id_from_number(parseFloat(region.start).toFixed(2), 5, "0"); //5 is the length of the returned string and 0 is the prefix
            endId = get_boundary_id_from_number(parseFloat(region.end).toFixed(2), 5, "0");

            // startId = region.start.toString().slice(0, 4).replace('.', '');
            // if (startId === '0') {
            //     startId = '000';
            // }
            // endId = region.end.toString().slice(0, 4).replace('.', '');
            // if (endId === '0') {
            //     endId = '000';
            // }
            // console.log(startId, endId)
            rid = startId.concat(endId);
            // rid = region.start.toString().slice(0, 4).replace('.', '').concat(region.end.toString().slice(0, 4).replace('.', ''));

            // console.log(rid)
            // sentence = getActiveRegionSentence(region);
            // console.log(sentence)
            return {
                boundaryID: rid,
                start: region.start,
                end: region.end,
                attributes: region.attributes,
                data: region.data,
                // comment: region.comment
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
    regions.forEach(function (region) {
        region.color = boundaryColor(0, 255, 0, 0.1);
        region.drag = false;
        // console.log(region)
        wavesurfer.addRegion(region);
    });
    // wavesurfer.seekAndCenter(0.5);
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
    Array.prototype.forEach.call(peaks, function (val, index) {
        if (Math.abs(val) <= minValue) {
            silences.push(index);
        }
    });

    // Cluster silence values
    let clusters = [];
    silences.forEach(function (val, index) {
        if (clusters.length && val == silences[index - 1] + 1) {
            clusters[clusters.length - 1].push(val);
        } else {
            clusters.push([val]);
        }
    });

    // Filter silence clusters by minimum length
    let fClusters = clusters.filter(function (cluster) {
        return cluster.length >= minLen;
    });

    // Create regions on the edges of silences
    let regions = fClusters.map(function (cluster, index) {
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
    let fRegions = regions.filter(function (reg) {
        return reg.end - reg.start >= minLen;
    });

    // Return time-based regions
    return fRegions.map(function (reg) {
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
    updateCurrentCursorTime(from = "edit");
    // wavesurfer.playPause();
    region.color = boundaryColor(255, 0, 0, 0.1);
    // console.log('editAnnotation(region)')
    // console.log(region)
    let form = document.forms.edit;
    // console.log(form);
    // let id = form.dataset.region;
    // let wavesurferregion = wavesurfer.regions.list[id];
    // console.log(wavesurferregion)

    var sentence = getActiveRegionSentence(region);

    // console.log("Active region sentence", sentence)
    startId = get_boundary_id_from_number(parseFloat(region.start).toFixed(2), 5, "0"); //5 is the length of the returned string and 0 is the prefix
    endId = get_boundary_id_from_number(parseFloat(region.end).toFixed(2), 5, "0");

    // startId = region.start.toString().slice(0, 4).replace('.', '');
    // if (startId === '0') {
    //     startId = '000';
    // }
    // endId = region.end.toString().slice(0, 4).replace('.', '');
    // if (endId === '0') {
    //     endId = '000';
    // }
    // console.log(startId, endId)
    rid = startId.concat(endId);
    // rid = region.start.toString().slice(0, 4).replace('.', '').concat(region.end.toString().slice(0, 4).replace('.', ''));
    if (sentence === undefined) {
        sentence = updateSentenceDetails(rid, sentence, region)
        // console.log('sentence', sentence)
        createSentenceForm(sentence[rid], rid)

    }
    else {
        // console.log('elseeeee', sentence)
        sentence = updateSentenceDetails(rid, sentence, region)
        // console.log('elseeeee updated', sentence)
        // console.log('elseeeee updated rid', rid)
        createSentenceForm(sentence[rid], rid)
    }
    // sentence = updateSentenceDetails(rid, sentence, region)
    // console.log(sentence)
    // createSentenceForm(sentence[rid])
    allKeymanEle = document.getElementsByClassName("keyman-attached");
    // console.log("All keyman classes", allKeymanEle);
    for (let ele of allKeymanEle) {
        keyman.attachToControl(ele);
    }

    transcriptionFormDisplay(form, 'edit');
    // form.style.opacity = 1;
    // (form.elements.start.value = Math.round(region.start * 10) / 10),
    // (form.elements.end.value = Math.round(region.end * 10) / 10);
    (form.elements.start.value = region.start),
        (form.elements.end.value = region.end);
    // form.elements.note.value = region.data.note || '';
    // document.getElementById("activeSentenceMorphemicBreak").checked = false;
    // $(".containerremovesentencefield1").remove();
    // if (region.data.sentence) {
    //     createSentenceForm(form, region);
    // console.log('true true');
    // }
    saveBoundaryData(region, form)
    updateBoundaryColor(region, form);
    formOnSubmit(form, region)
    // console.log(sentence);

    // form.onreset = function () {
    //     // form.style.opacity = 0;
    // console.log('form reset');
    //     transcriptionFormDisplay(form);
    //     form.dataset.region = null;
    // };
    form.dataset.region = region.id;
    // region.color = boundaryColor(255, 255, 0, 0.1);
}

// save partial transcription details
function formOnSubmit(form, region) {
    // console.log('formOnSubmit(form, region) region', region)
    form.onsubmit = function (e) {
        wavesurfer.pause();
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
        saveBoundaryData(region, form);
        // something = window.open("data:text/json," + encodeURIComponent(sentData),
        //                "_blank");
        // something.focus();
        // form.style.opacity = 0;
        transcriptionFormDisplay(form);
    };
}

function saveBoundaryData(region, form) {
    // console.log(region);
    // console.log(form);
    let regions = JSON.parse(localStorage.regions);
    for (i = 0; i < regions.length; i++) {
        if (regions[i]['start'] === region.start &&
            regions[i]['end'] === region.end) {

            startId = get_boundary_id_from_number(parseFloat(region.start).toFixed(2), 5, "0"); //5 is the length of the returned string and 0 is the prefix
            endId = get_boundary_id_from_number(parseFloat(region.end).toFixed(2), 5, "0");

            // startId = region.start.toString().slice(0, 4).replace('.', '');
            // if (startId === '0') {
            //     startId = '000';
            // }
            // endId = region.end.toString().slice(0, 4).replace('.', '');
            // if (endId === '0') {
            //     endId = '000';
            // }
            rid = startId.concat(endId);
            sentence = regions[i]['data']['sentence']
            sentence = updateSentenceDetailsOnSaveBoundary(rid, sentence, region, form)
        }
    }
    region.update({
        start: form.elements.start.value,
        end: form.elements.end.value,
        // comment: form.elements.comment.textContent,
        data: {
            // note: form.elements.note.value,
            sentence: sentence
        }
    });
}

/**
 * Display annotation.
 */
function showNote(region) {
    let form = document.forms.edit;
    // console.log(form);
    // console.log(form[0].id, form[0].value);
    let firstTranscriptionFieldValue = form[0].value;
    let subtitle = document.getElementById('subtitle');
    // console.log(subtitle, firstTranscriptionFieldValue);
    if (firstTranscriptionFieldValue !== '') {
        subtitle.innerHTML = firstTranscriptionFieldValue
    }
    else {
        subtitle.innerHTML = '–'
    }

}

// // active region
// function activeRegionColor(region) {
//     // region.color = boundaryColor(255, 0, 0, 0.1);
//     // let form = document.forms.edit;
//     // saveBoundaryData(region, form);
// }
function updateInterlinearGlossInfo(scriptName,
    newlyAddedWords,
    deletedWords,
    updatedWords,
    unchangedWords,
    updateInterlinearGloss
) {
    let sentenceMorphemicBreakWord = '';
    let sentenceMorphemicBreakWordList = [];
    let sentenceMorphemicBreakSentence = '';
    let updateWithInterlinearGloss = {};
    let localStorageRegions = JSON.parse(localStorage.regions);
    let sentence_morphemic_break_full_old = '';
    let glossDetails = '';
    let posDetails = '';
    let morphemeDetails = '';
    // console.log(localStorageRegions);
    let activeBoundaryID = document.getElementById('activeBoundaryID').value;
    for (let p = 0; p < localStorageRegions.length; p++) {
        if (localStorageRegions[p]['boundaryID'] === activeBoundaryID) {
            //   console.log(localStorageRegions[p]);
            sentence_morphemic_break_full_old = localStorageRegions[p]['data']['sentence'][activeBoundaryID]['sentencemorphemicbreak'][scriptName];
            glossDetails = localStorageRegions[p]['data']['sentence'][activeBoundaryID]['gloss'][scriptName];
            posDetails = localStorageRegions[p]['data']['sentence'][activeBoundaryID]['pos'];
            morphemeDetails = localStorageRegions[p]['data']['sentence'][activeBoundaryID]['morphemes'][scriptName];
            //   console.log(sentence_morphemic_break_full_old, glossDetails, posDetails, morphemeDetails);
            updateInterlinearGloss['glossDetails'] = glossDetails;
            updateInterlinearGloss['posDetails'] = posDetails;
            updateInterlinearGloss['morphemeDetails'] = morphemeDetails;
            break;
        }
    }
    // console.log(updateInterlinearGloss);
    //   console.log(Object.keys(updateInterlinearGloss['morphemeDetails']).length);
    for (let [key, value] of Object.entries(updateInterlinearGloss)) {
        if (key === 'glossDetails' ||
            key === 'posDetails' ||
            key === 'morphemeDetails') continue;
        sentenceMorphemicBreakWord = value;
        // console.log(sentenceMorphemicBreakWord);
        // console.log(key, value);
        if (unchangedWords.includes(value) ||
            newlyAddedWords.includes(value)) {
            // console.log(key, value);
            let centerWordID = key.slice(-1);
            if (Object.keys(morphemeDetails).includes(key) &&
                Object.keys(morphemeDetails[key])[0] === value) {
                // console.log('MATCH', updateInterlinearGloss[key], centerWordID);
                updateWithInterlinearGloss[key] = [
                    updateInterlinearGloss['glossDetails'][key],
                    updateInterlinearGloss['posDetails'][key],
                    updateInterlinearGloss['morphemeDetails'][key]
                ]
                if (Object.keys(updateInterlinearGloss['morphemeDetails']).length !== 0) {
                    sentenceMorphemicBreakWord = updateInterlinearGloss['morphemeDetails'][key][sentenceMorphemicBreakWord];
                }
                // console.log(sentenceMorphemicBreakWord);
            }
            else {
                // console.log(Object.keys(morphemeDetails).length);
                if (Object.keys(morphemeDetails).length > 1) {
                    // console.log('NOT MATCH');
                    // morphemeDetails[key],
                    // Object.keys(morphemeDetails[key])[0],
                    // centerWordID,
                    // Math.ceil(Object.keys(morphemeDetails).length/2));
                    for (let i = 0; i < Math.ceil(Object.keys(morphemeDetails).length / 2); i++) {
                        let nextWordCount = Number(centerWordID) + (i + 1);
                        let nextWordID = 'W00' + String(nextWordCount);
                        let previousWordCount = Number(centerWordID) - (i + 1);
                        let previousWordID = 'W00' + String(previousWordCount);
                        // console.log(previousWordID, centerWordID, nextWordID);
                        // console.log(Object.keys(morphemeDetails).includes(previousWordID),
                        // Object.keys(morphemeDetails[previousWordID])[0],
                        // value,
                        // Object.keys(morphemeDetails[previousWordID])[0] === value
                        // );
                        if (Object.keys(morphemeDetails).includes(previousWordID) &&
                            Object.keys(morphemeDetails[previousWordID])[0] === value) {
                            // console.log('MATCH TO LEFT AFTER NOT MATCH');
                            updateWithInterlinearGloss[key] = [
                                updateInterlinearGloss['glossDetails'][previousWordID],
                                updateInterlinearGloss['posDetails'][previousWordID],
                                updateInterlinearGloss['morphemeDetails'][previousWordID]
                            ]
                            if (Object.keys(updateInterlinearGloss['morphemeDetails']).length !== 0) {
                                // console.log(sentenceMorphemicBreakWord);
                                sentenceMorphemicBreakWord = updateInterlinearGloss['morphemeDetails'][previousWordID][sentenceMorphemicBreakWord];
                            }
                            // console.log(sentenceMorphemicBreakWord);
                            // console.log('MATCH TO LEFT AFTER NOT MATCH', updateInterlinearGloss[key], Object.keys(morphemeDetails[key])[0], centerWordID, previousWordID);
                        }
                        else if (Object.keys(morphemeDetails).includes(nextWordID) &&
                            Object.keys(morphemeDetails[nextWordID])[0] === value) {
                            // console.log('MATCH TO RIGHT AFTER NOT MATCH');
                            updateWithInterlinearGloss[key] = [
                                updateInterlinearGloss['glossDetails'][nextWordID],
                                updateInterlinearGloss['posDetails'][nextWordID],
                                updateInterlinearGloss['morphemeDetails'][nextWordID]
                            ]
                            if (Object.keys(updateInterlinearGloss['morphemeDetails']).length !== 0) {
                                sentenceMorphemicBreakWord = updateInterlinearGloss['morphemeDetails'][nextWordID][sentenceMorphemicBreakWord];
                            }
                            // console.log(sentenceMorphemicBreakWord);
                            // console.log('MATCH TO RIGHT AFTER NOT MATCH', updateInterlinearGloss[key], Object.keys(morphemeDetails[key])[0], centerWordID, nextWordID);
                        }
                        else {
                            // console.log('NO MATCH FOUND!');
                            continue
                        }
                        break;
                    }
                }
            }
            sentenceMorphemicBreakWordList.push(sentenceMorphemicBreakWord);
            // console.log(sentenceMorphemicBreakWordList);
        }
    }
    sentenceMorphemicBreakSentence = sentenceMorphemicBreakWordList.join(' ');
    // console.log(updateWithInterlinearGloss, sentenceMorphemicBreakSentence);

    return {
        'updateWithInterlinearGloss': updateWithInterlinearGloss,
        'sentenceMorphemicBreakSentence': sentenceMorphemicBreakSentence
    }
}

function infoForUpdateInterlinearGloss(sentence_diff, scriptName) {
    let lines = sentence_diff['lines'];
    let errorFlag = 0;
    let newWord = '';
    let oldWord = '';
    let wordCount = 0;
    let word = '';
    let aIndexNegativeCount = 0;
    let bIndexNegativeCount = 0;
    let newlyAddedWords = [];
    let deletedWords = [];
    let unchangedWords = [];
    let updatedWords = [];
    let updateInterlinearGloss = {};
    for (let l = 0; l < lines.length; l++) {
        let lineData = lines[l];
        //   console.log(l, lineData, errorFlag);
        //   console.log(lineData['aIndex'], lineData['bIndex']);
        if (lineData['aIndex'] === -1 &&
            lineData['line'] !== ' ') {
            aIndexNegativeCount += 1;
            newWord += lineData['line'];
        }
        else if (lineData['bIndex'] === -1 &&
            lineData['line'] !== ' ') {
            // console.log(l, lines[l], errorFlag);
            bIndexNegativeCount += 1;
            oldWord += lineData['line'];
            // console.log(l, lines[l], errorFlag);
        }
        else if (lineData['aIndex'] !== -1 &&
            lineData['bIndex'] !== -1 &&
            lineData['line'] !== ' ') {
            oldWord += lineData['line'];
            newWord += lineData['line'];
        }
        let wordId = 'W00' + String(wordCount + 1);
        word += lineData['line'];
        let dropLastSpace = word.replace(' ', '');
        if (lineData['line'] === ' ') {
            // console.log(word.length);
            // console.log(dropLastSpace.length);
            // console.log([word, newWord, oldWord, aIndexNegativeCount, bIndexNegativeCount]);
            if (newWord !== '') {
                updateInterlinearGloss[wordId] = newWord;
                wordCount += 1;
            }
            if (newWord !== '' &&
                aIndexNegativeCount !== 0 &&
                aIndexNegativeCount === newWord.length) {
                newlyAddedWords.push(newWord);
            }
            else if (oldWord !== '' &&
                bIndexNegativeCount !== 0 &&
                bIndexNegativeCount === oldWord.length) {
                deletedWords.push(oldWord);
            }
            else if (aIndexNegativeCount === 0 &&
                bIndexNegativeCount == 0) {
                unchangedWords.push(newWord);
            }
            else if (aIndexNegativeCount < newWord.length ||
                bIndexNegativeCount < oldWord.length) {
                newlyAddedWords.push(newWord);
                deletedWords.push(oldWord);
            }
            errorFlag = 0;
            oldWord = '';
            newWord = '';
            word = '';
            // wordCount += 1;
            aIndexNegativeCount = 0;
            bIndexNegativeCount = 0;
            // console.log(newlyAddedWords,
            //     deletedWords,
            //     updatedWords,
            //     unchangedWords,
            //     updateInterlinearGloss
            //     )
        }
    }
    // console.log(newlyAddedWords,
    //     deletedWords,
    //     updatedWords,
    //     unchangedWords,
    //     updateInterlinearGloss
    //     )
    let updateWithInterlinearGloss = updateInterlinearGlossInfo(scriptName,
        newlyAddedWords,
        deletedWords,
        updatedWords,
        unchangedWords,
        updateInterlinearGloss
    )
    // console.log('mappinggg;;;');
    // console.log(updateWithInterlinearGloss);
    return updateWithInterlinearGloss;
}

function mapTranscriptionInterlinearGloss(e, sentencemorphemicbreakEle) {
    // console.log(sentencemorphemicbreakEle);
    // console.log(sentencemorphemicbreakEle.id);
    // map transcription and interlinear gloss
    try {
        let transcriptionEleId = sentencemorphemicbreakEle.id.replace('sentenceMorphemicBreak_', 'Transcription_');
        // console.log(transcriptionEleId);
        let transcriptionEle = document.getElementById(transcriptionEleId);
        // console.log(transcriptionEle)
        if (sentencemorphemicbreakEle) {
            let aLines = sentencemorphemicbreakEle.value.trim().replace(/[#-]/g, '');
            let bLines = transcriptionEle.value.trim();
            // console.log(aLines, bLines);
            let sentDiff = patienceDiff(aLines + ' ', bLines + ' ', false);
            // let sentDiff = patienceDiff( bLines, aLines, false );
            // console.log(sentDiff);
            let scriptNameArray = sentencemorphemicbreakEle.id.split('_');
            let scriptName = scriptNameArray[scriptNameArray.length - 1];
            // console.log(scriptName);
            let { updateWithInterlinearGloss, sentenceMorphemicBreakSentence } = infoForUpdateInterlinearGloss(sentDiff, scriptName);
            // console.log(updateWithInterlinearGloss, sentenceMorphemicBreakSentence);
            // console.log(sentencemorphemicbreakEle, transcriptionEle);
            // console.log(sentencemorphemicbreakEle.value)
            // console.log(sentencemorphemicbreakEle.value.trim().replace(/[#-]/g, ''))
            if (Object.keys(updateWithInterlinearGloss).length === 0) {
                if (sentencemorphemicbreakEle.value.trim().replace(/[#-]/g, '') !== transcriptionEle.value.trim()) {
                    sentencemorphemicbreakEle.value = transcriptionEle.value.trim();
                    // sentence[boundaryID]['sentencemorphemicbreak'][k] = form[eleName].value;
                }
            }
            else {
                sentencemorphemicbreakEle.value = sentenceMorphemicBreakSentence.trim();
            }
        }
    }
    catch {
        // console.log(sentencemorphemicbreakEle.id);
    }
}

function morphemeDetails(actualTranscription, morphemicBreakTranscription) {
    // console.log('morphemeDetails!!!!!!!!!')
    // console.log(actualTranscription, morphemicBreakTranscription);
    replaceObj = new RegExp('[#]', 'g');
    // morphemicBreakTranscription = morphemicBreakTranscription.replace('#', '').split(" ")
    // morphemicBreakTranscription = morphemicBreakTranscription.replace(replaceObj, '').trim().split(" ");
    morphemicBreakTranscription = morphemicBreakTranscription.trim().split(" ");
    morphemeData = mapArrays(actualTranscription, morphemicBreakTranscription)

    // console.log(morphemeData);

    return morphemeData
}

function addDeleteGlossSelect2(field,
                                glossTokenIdInfo,
                                tokenId,
                                concatSymbol) {
    let fieldValue = '';
    let oldFieldValueArray = [];
    let selectedFieldValueInfo = [];
    if (glossTokenIdInfo &&
        tokenId in glossTokenIdInfo &&
        field in glossTokenIdInfo[tokenId]){
        fieldValue = glossTokenIdInfo[tokenId][field];
    }
    // console.log(fieldValue);
    // console.log(field);
    // console.log(glossTokenIdInfo)
    // console.log(tokenId)
    // console.log(concatSymbol)
    if (fieldValue !== '') {
        oldFieldValueArray = fieldValue.split(concatSymbol);
    }
    // console.log(fieldValue, oldFieldValueArray);
    try {
        selectedFieldValueInfo = $('#'+tokenId+'_'+field).select2('data');
    }
    catch {}
    // console.log(selectedFieldValueInfo);
    let tempFieldValue = '';
    let incomingFieldValueArray = []
    for (a=0; a<selectedFieldValueInfo.length; a++) {
        // console.log(fieldValue);
        tempFieldValue = selectedFieldValueInfo[a].id;
        incomingFieldValueArray.push(tempFieldValue);
        if (oldFieldValueArray.includes(tempFieldValue)){
            continue
        }
        else {
            if (fieldValue === '') {
                fieldValue = tempFieldValue;
            }
            else {
                fieldValue += concatSymbol+tempFieldValue;
            }
        }
    }
    for (a=0; a<oldFieldValueArray.length; a++) {
        if (incomingFieldValueArray.includes(oldFieldValueArray[a])) {
            continue
        }
        else {
            fieldValue = fieldValue.replace(concatSymbol+oldFieldValueArray[a], '').replace(oldFieldValueArray[a]+concatSymbol, '').replace(oldFieldValueArray[a], '');
        }
    }

    return fieldValue;
}

function processTokenGloss(glossTokenId,
                            interlinearGlossFormat,
                            customizeGloss,
                            glossTokenIdInfo) {
    // console.log('processTokenGloss');
    // console.log(glossTokenIdInfo);
    try {
        let glossedSentenceWithMorphemicBreakInfo = {};
        let glossedSentenceWithTokenIdInfo = {};
        for (let i=0; i<glossTokenId.length; i++) {
            let tokenId = glossTokenId[i];
            // console.log(tokenId);
            // glossedSentenceWithMorphemicBreakInfo[tokenId] = {};
            glossedSentenceWithTokenIdInfo[tokenId] = {};
            // console.log(document.getElementById(tokenId+'_word_input').value);
            let token = document.getElementById(tokenId+'_word_input').value;
            // console.log(token);
            glossedSentenceWithMorphemicBreakInfo[tokenId] = token;
            if (interlinearGlossFormat.includes('Leipzig')) {
                let tokenTranslation = document.getElementById(tokenId+'_word_translation').value;
                // console.log(tokenTranslation);
                // let gloss = document.getElementById(tokenId+'_gloss').value;
                // let gloss = $('#'+tokenId+'_gloss').val();
                let gloss = addDeleteGlossSelect2('gloss',
                                                    glossTokenIdInfo,
                                                    tokenId,
                                                    '.'
                                                );
                // if (gloss !== '') {
                //     console.log(gloss);
                // }
                if (tokenTranslation !== '') {
                    gloss = tokenTranslation+'.'+gloss;
                }
                else {
                    gloss = '_'+'.'+gloss;
                }
                glossedSentenceWithTokenIdInfo[tokenId]['gloss'] = gloss;
            }
            for (let p=0; p<customizeGloss.length; p++) {
                let field = customizeGloss[p].toLowerCase();
                let fieldValue = '';
                // console.log(field);
                if (field === 'id' ||
                    field === 'form') {
                    continue;
                }
                else if (field === 'feats') {
                    fieldValue = addDeleteGlossSelect2(field,
                                                        glossTokenIdInfo,
                                                        tokenId,
                                                        '|'
                                                    );
                    // if (fieldValue !== '') {
                    //     console.log(fieldValue);
                    // }
                }
                else {
                    fieldValue = document.getElementById(tokenId+'_'+field).value;
                }
                // console.log(field, fieldValue);
                glossedSentenceWithTokenIdInfo[tokenId][field] = fieldValue;
                // console.log(glossedSentenceWithTokenIdInfo);
            }
            // console.log(glossedSentenceWithTokenIdInfo);
        }
        // console.log(glossedSentenceWithTokenIdInfo);
        // console.log(glossedSentenceWithMorphemicBreakInfo);
        // console.log(glossedSentenceWithTokenIdInfo);

        return {
            glossedSentenceWithMorphemicBreakInfo: glossedSentenceWithMorphemicBreakInfo,
            glossedSentenceWithTokenIdInfo: glossedSentenceWithTokenIdInfo
        }
    }
    catch(error) {
        console.error(error);
        // console.log(glossedSentenceWithTokenIdInfo);
        console.log('error');
    }
    // console.log(glossedSentenceWithTokenIdInfo);
}

function updateSentenceDetailsOnSaveBoundary(boundaryID, sentence, region, form) {

    let activeprojectform = JSON.parse(localStorage.getItem('activeprojectform'));

    // console.log(boundaryID);
    // console.log(sentence);
    // console.log(region);
    // console.log("Form in update", form);
    // console.log("Form in update", Object.keys(form));
    // console.log("Sentence Spaker IDs", form["sentSpeakerId"])
    // console.log("Sentence Spaker IDs value", form["sentSpeakerId"].values, $("#sentspeakeriddropdown").val())
    // console.log("Comment", form["comment-box"].textContent)
    // console.log("Comment Val", form["comment-box"].value)
    // console.log(document.forms.edit.elements);

    if ("comment-box" in form) {
        // console.log("Comment box found in form")
        key = "comment";
        if (key in sentence[boundaryID]) {
            eleName = 'comment-box'
            sentence[boundaryID][key] = form[eleName].value
        }
        else {
            eleName = 'comment-box'
            sentence[boundaryID][key] = form[eleName].value
        }
    }


    // if ()


    for (let [key, value] of Object.entries(sentence[boundaryID])) {
        // console.log(key, value);
        // if (key === 'comment') {
        //     eleName = 'comment-box'
        //     sentence[boundaryID][key] = form[eleName].value
        // }
        sentenceSpeakerIds = $("#sentspeakeriddropdown").val();
        if (!sentenceSpeakerIds) {
            sentenceSpeakerIds = "";
        }
        else if (sentenceSpeakerIds.length == 1) {
            sentenceSpeakerIds = sentenceSpeakerIds[0];
        }
        // console.log("Setting sentence speaker ID", boundaryID, sentenceSpeakerIds);
        sentence[boundaryID]["speakerId"] = sentenceSpeakerIds;

        if (key === 'transcription') {
            for (let [k, v] of Object.entries(sentence[boundaryID][key])) {
                // console.log(k, v)
                eleName = 'transcription_' + k
                sentence[boundaryID][key][k] = form[eleName].value;
            }
        }
        else if ('Translation' in activeprojectform &&
            key === 'translation') {
            for (let [k, v] of Object.entries(sentence[boundaryID][key])) {
                // console.log(k, v)
                tk = k.split('-')[1]
                eleName = 'translation_' + tk
                sentence[boundaryID][key][k] = form[eleName].value
            }
        }
        else if (key === 'sentencemorphemicbreak') {
            for (let [k, v] of Object.entries(sentence[boundaryID][key])) {
                // console.log(k, v)
                eleName = 'morphsentenceMorphemicBreak_' + k;
                // console.log(sentence[boundaryID][key][k]);
                try {
                    // sentence[boundaryID][key][k] = form[eleName].value;
                    let scripttoglossdropdownselected = getScriptToGlossDropdownSelected();
                    if ("Interlinear Gloss" in activeprojectform &&
                        k === scripttoglossdropdownselected) {
                        let glossTokenId = JSON.parse(localStorage.getItem('glossTokenId'));
                        // console.log(glossTokenId);
                        // console.log(document.getElementById(glossTokenId[0]+'_word_input'));
                        let interlinearglossforminfo = interlinearGlossFormInfo(activeprojectform);
                        let interlinearGlossFormat = interlinearglossforminfo.interlinearGlossFormat;
                        let customizeGloss = interlinearglossforminfo.customizeGloss;
                        // console.log(interlinearGlossFormat,
                        //     customizeGloss
                        // )
                        if (glossTokenId.length !== 0) {
                            let glossedSentenceWithMorphemicBreakInfo = processTokenGloss(glossTokenId,
                                                                                            interlinearGlossFormat,
                                                                                            customizeGloss,
                                                                                            sentence[boundaryID]['glossTokenIdInfo']);
                            // console.log(glossedSentenceWithMorphemicBreakInfo);
                            sentence[boundaryID]['gloss'][k] = glossedSentenceWithMorphemicBreakInfo.glossedSentenceWithMorphemicBreakInfo;
                            sentence[boundaryID]['glossTokenIdInfo'] = glossedSentenceWithMorphemicBreakInfo.glossedSentenceWithTokenIdInfo;
                        }
                    }
                    // sentence[boundaryID][key][k] = form[eleName].value;
                    // let tokenGlossInfo = $('#tokenannotationtagset').select2('data');
                    // // console.log(tokenGlossInfo);
                    // if (tokenGlossInfo) {
                    //     let glossedSentenceWithMorphemicBreakInfo = processTokenGloss(tokenGlossInfo, form[eleName].value);
                    //     sentence[boundaryID]['gloss'][k][glossedSentenceWithMorphemicBreakInfo.tokenId] = glossedSentenceWithMorphemicBreakInfo.glossedSentenceWithMorphemicBreak
                    //     // let glossedSentenceWithMorphemicBreakOld = form[eleName].value;
                    //     // if ('glossedSentenceWithMorphemicBreak' in sentence[boundaryID] &&
                    //     //     k in sentence[boundaryID]['glossedSentenceWithMorphemicBreak']) {
                    //     //         glossedSentenceWithMorphemicBreakOld = sentence[boundaryID]['glossedSentenceWithMorphemicBreak'][k]
                    //     // }
                    //     // let glossedSentenceWithMorphemicBreak = processTokenGloss(tokenGlossInfo, glossedSentenceWithMorphemicBreakOld);
                    //     // console.log(glossedSentenceWithMorphemicBreak);
                    //     // if ('glossedSentenceWithMorphemicBreak' in sentence[boundaryID]) {
                    //     //     sentence[boundaryID]['glossedSentenceWithMorphemicBreak'][k] = glossedSentenceWithMorphemicBreak;

                    //     // }
                    //     // else {
                    //     //     sentence[boundaryID]['glossedSentenceWithMorphemicBreak'] = {};
                    //     //     sentence[boundaryID]['glossedSentenceWithMorphemicBreak'][k] = glossedSentenceWithMorphemicBreak;
                    //     // }

                    // }
                }
                catch {
                    if (sentence[boundaryID][key][k] !== "") {
                        continue
                    }
                    else {
                        sentence[boundaryID][key][k] = "";
                    }
                }
            }
        }
        else if (key === 'morphemes') {
            // console.log('morphemes!!!!!!!!!!!!!!')
            for (let [k, v] of Object.entries(sentence[boundaryID][key])) {
                // console.log(k, v)
                // console.log(form['morphcount']);
                // console.log(typeof form);
                // console.log(Object.keys(form));
                // console.log(Object.values(form));
                // console.log(form[35]);
                // if (form['morphcount'] !== undefined && k === 'IPA') {
                if (form['morphcount'] !== undefined) {
                    try {
                        // console.log(k, v)
                        morphCount = form['morphcount'].value
                        morphemeFor = k
                        actualTranscriptionStr = form['Transcription_' + morphemeFor].value.trim();
                        morphemicBreakTranscriptionStr = form['morphsentenceMorphemicBreak_' + morphemeFor].value.replace(/[#-]/g, '').trim();
                        // console.log(actualTranscriptionStr, morphemicBreakTranscriptionStr);
                        if (actualTranscriptionStr === morphemicBreakTranscriptionStr) {
                            actualTranscription = form['Transcription_' + morphemeFor].value.trim().split(" ");
                            // console.log(actualTranscription)
                            morphemicBreakTranscription = form['morphsentenceMorphemicBreak_' + morphemeFor].value.trim();
                            // console.log(morphCount, morphemeFor, actualTranscription, morphemicBreakTranscription)
                            try {
                                sentence[boundaryID][key][k] = morphemeDetails(actualTranscription, morphemicBreakTranscription);
                            }
                            catch (err) {
                                // console.log(err);
                            }
                            sentenceId = sentence[boundaryID]['sentenceId']
                            // console.log("sentence[boundaryID]['sentenceId']", sentenceId)
                            morphemeIdMap = morphemeidMap(actualTranscription, morphemicBreakTranscription)
                            console.log(morphemeIdMap);
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
                            // console.log(tempgloss)
                            var temppos = Object()
                            sentence[boundaryID]['pos'] = glossAndpos[1]
                            temppos[boundaryID] = flattenObject(sentence[boundaryID]['pos'])
                            // console.log(temppos)

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
                    }
                    catch {
                        continue
                    }
                }
                // tk = k.split('-')[1]
                // eleName = 'translation_'+tk
                // sentence[boundaryID][key][k] = form[eleName].value
            }
        }
        // else if (key === 'gloss') {
        // console.log('gloss!!!!!!!!!!!!!!')
        //     for (let [k, v] of Object.entries(sentence[boundaryID][key])) {
        // console.log(k, v)

        //         // if (form['morphcount'] !== undefined && k === 'IPA') {
        //         //     morphCount = form['morphcount'].value
        //         //     morphemeFor = k
        //         //     actualTranscription = form['Transcription_'+morphemeFor].value.split(" ")
        //         //     morphemicBreakTranscription = form['morphsentenceMorphemicBreakTranscription_'+morphemeFor].value
        // console.log(morphCount, morphemeFor, actualTranscription, morphemicBreakTranscription)
        //         //     sentence[boundaryID][key][k] = morphemeDetails(actualTranscription, morphemicBreakTranscription)
        // console.log(sentence)
        //         // }
        //         // tk = k.split('-')[1]
        //         // eleName = 'translation_'+tk
        //         // sentence[boundaryID][key][k] = form[eleName].value
        //     }
        // }
    }
    // console.log(sentence);

    let regions = JSON.parse(localStorage.regions);
    for (i = 0; i < regions.length; i++) {
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
    // console.log(sentence)
    //     sentence[boundaryID] = {
    //         'start': region.start,
    //         'end': region.end
    //     }
    // }
    // else {
    if (sentence === undefined) {
        sentence = new Object()
        transcription = {}
        translation = {}
        sentencemorphemicbreak = {}
        morphemes = {}
        gloss = {}
        comment = ""
        activeprojectform = JSON.parse(localStorage.getItem('activeprojectform'));
        // console.log('activeprojectform', activeprojectform)
        scriptCode = activeprojectform['scriptCode']

        // console.log(activeprojectform)
        // console.log(scriptCode)
        scripts = activeprojectform["Transcription"][1];
        // console.log(scripts)
        let translationlangscripts = undefined;
        if ("Translation" in activeprojectform) {
            translationlangscripts = activeprojectform["Translation"][1];
        }
        // translationlang = activeprojectform["Translation Language"]
        // console.log(translationlang);
        for (i = 0; i < scripts.length; i++) {
            script = scripts[i]
            // script_code = scriptCode[scripts[i]]
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
        if (translationlangscripts !== undefined) {
            translationlangscripts = Object.keys(translationlangscripts)
            for (i = 0; i < translationlangscripts.length; i++) {
                tscript = translationlangscripts[i];
                // tscript = translationlangscripts[i].split('-')[1];
                // tlang = translationlangscripts[i].split('-')[0];
                // tscript_code = scriptCode[tscript]
                // lang_code = tlang.slice(0, 3).toLowerCase() + '-' + tscript_code
                // translation[lang_code] = ''
                translation[tscript] = '';
            }
        }
        pos = {}
        tags = {}
        sentence[boundaryID] = {
            'start': region.start,
            'end': region.end,
            "speakerId": "",
            'transcription': transcription,
            'translation': translation,
            'sentencemorphemicbreak': sentencemorphemicbreak,
            'morphemes': morphemes,
            'gloss': gloss,
            'pos': pos,
            'tags': tags,
            'sentenceId': document.getElementById('lastActiveId').value,
            'comment': comment
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
        sentence[boundaryID]['start'] = region.start
        sentence[boundaryID]['end'] = region.end
        // sentence[boundaryID]['comment'] = region.end
    }
    let regions = JSON.parse(localStorage.regions)
    for (i = 0; i < regions.length; i++) {
        if (regions[i]['start'] === region.start &&
            regions[i]['end'] === region.end) {
            regions[i]['data']['sentence'] = sentence
            // regions[i]['data']['comment'] = regions.data.comment
        }
    }
    localStorage.setItem("regions", JSON.stringify(regions));
    // console.log('regions', regions)
    // console.log('updateSentenceDetails(boundaryID, sentence, region)', sentence)
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

// function glossDetails(morphCount, morphemeFor, formData, actualTranscription, morphemicBreakTranscription) {
function glossDetails(morphCount,
    morphemeFor,
    formData,
    morphemeIdMap,
    sentenceId,
    actualTranscription) {

    // console.log(sentenceId)
    // console.log(morphCount);
    // console.log(actualTranscription, morphemicBreakTranscription)
    // console.log(formData)
    let glossData = new Object();
    // for (i=1; i<=actualTranscription.length; i++) {
    //     wordId = 'W00'+String(i)
    //     glossData[wordId] = {}
    // }
    // console.log(glossData);
    let pos = new Object();
    for (i = 1; i <= morphCount; i++) {
        let glossSubData = new Object();
        glossSubData[i] = {};
        let morpheme = '';
        let lexgloss = {};
        let lextype = '';
        let eleName = '';
        // for (let [key, value] of Object.entries(formData)) {
        // console.log(key, value)
        //     if (value !== undefined) {
        //         eleName = value.name;
        //     }
        //     else {
        //         eleName = ''
        //     }
        // console.log(eleName);
        //     if (eleName.includes(i) &&
        //         eleName.includes(morphemeFor)) {
        // console.log(eleName);
        //         if (eleName.includes('morpheme')) {
        //             morpheme = formData[eleName].value
        // console.log(morpheme)
        //         }
        //         else if (eleName.includes('gloss')) {
        //             lexgloss = {
        //                 "eng-Latn": formData[eleName].value
        //             }
        // console.log(lexgloss)
        //         }
        //         else if (eleName.includes('lextype')) {
        //             lextype = formData[eleName].value
        // console.log(lextype)
        //         }
        //         else if (eleName.includes('pos')) {
        // console.log(eleName);
        //             morphemeIdWord = morphemeIdMap[i][2]
        //             wordId = morphemeIdMap[i][0]
        //             // pos[morphemeIdMap[i]] = formData[eleName].value
        //             pos[wordId] = {}
        //             pos[wordId][i] = {}
        //             pos[wordId][i][morphemeIdWord] = formData[eleName].value
        // console.log(pos)
        //         }
        //         // else if (eleName.includes('gloss')) {

        //         // }
        //     }
        // }
        // datetime = new Date()
        // console.log(datetime.toJSON());

        eleName = ['morph', '#', morphemeFor, i].join('_')
        // console.log(eleName);
        // console.log(glossSubData);
        morpheme = formData[eleName.replace('#', 'morpheme')].value;
        let lexGlossClass = 'morphemeField' + morphemeFor + i;
        // console.log(lexGlossClass);
        // console.log($('.'+lexGlossClass).find(':selected'));
        lexgloss[morphemeFor] = formData[eleName.replace('#', 'gloss')].value;
        // console.log(lexgloss);
        // console.log(formData[eleName.replace('#', 'lextype')]);
        // console.log(formData[eleName.replace('#', 'lextype')].value);
        lextype = formData[eleName.replace('#', 'lextype')].value;
        glossSubData[i][morpheme] = {
            'lexemeId': sentenceId + 'L' + String(i),
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

        // morphemeIdWord = morphemeIdMap[i][2]
        // wordId = morphemeIdMap[i][0]
        // pos[morphemeIdMap[i]] = formData[eleName].value
        if (document.getElementsByName(eleName.replace('#', 'pos')).length !== 0) {
            // console.log(document.getElementsByName(eleName.replace('#', 'pos')), document.getElementsByName(eleName.replace('#', 'pos')).length)
            pos[wordId] = {}
            // console.log(pos)
            pos[wordId][i] = {}
            // console.log(pos)
            pos[wordId][i][morphemeIdWord] = formData[eleName.replace('#', 'pos')].value;
            // console.log(pos)
        }
    }
    // console.log(glossData);
    // console.log(pos)

    return [glossData, pos]
}

function morphemeidMap(actualTranscription, morphemicBreakTranscription) {
    console.log(actualTranscription, morphemicBreakTranscription);
    morphemicBreakTranscription = morphemicBreakTranscription.split(" ")
    // replaceObj = new RegExp('[#]', 'g')
    let replaceObj = new RegExp('[#-]', 'g')
    // morphemicBreakTranscription = morphemicBreakTranscription.replace(replaceObj, '').split(" ")
    glossDataMapping = mapArrays(actualTranscription, morphemicBreakTranscription)
    // console.log(glossDataMapping);
    // let glossData = new Object();
    let morphemeIdMap = new Object();
    mCount = 0;
    // wCount = 1
    for (let [wordkey, wordvalue] of Object.entries(glossDataMapping)) {
        // console.log(wordkey, wordvalue)
        for (let [key, value] of Object.entries(wordvalue)) {
            // console.log(key, value);
            // let glossSubData = new Object();
            // wordId = 'W00'+String(wCount)
            if (value.includes('#')) {
                v = value.replace(replaceObj, '');
                // v = value;
                value = value.split('#')
                for (i = 0; i < value.length; i++) {
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
    // console.log(morphemeIdMap)
    return morphemeIdMap;
}

function mapArrays(array_1, array_2) {
    if (array_1.length != array_2.length ||
        array_1.length == 0 ||
        array_2.length == 0) {
        return null;
    }
    let mappedData = new Object();

    function mapping(item, index, arr) {
        // console.log(item, index, arr);
        wordmap = new Object();
        wordmap[item] = array_2[index]
        mappedData['W00' + String(index + 1)] = wordmap
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

function collapseTranscription() {
    // console.log("collapseTranscription");
    $(".transcription").ready(function () {
        $(".transcription").on('shown.bs.collapse', function () {
            $(".transcript").addClass('glyphicon-chevron-up').removeClass('glyphicon-chevron-down');
        });
        $('.transcription').on('hidden.bs.collapse', function () {
            $(".transcript").addClass('glyphicon-chevron-down').removeClass('glyphicon-chevron-up');
        });
    });
}

function collapseTranslation() {
    // console.log("collapseTranslation");
    $(".translation").ready(function () {
        $(".translation").on('shown.bs.collapse', function () {
            $(".translate").addClass('glyphicon-chevron-up').removeClass('glyphicon-chevron-down');
        });
        $('.translation').on('hidden.bs.collapse', function () {
            $(".translate").addClass('glyphicon-chevron-down').removeClass('glyphicon-chevron-up');
        });
    });
}

function collapseInterlineargloss() {
    // console.log("collapseInterlineargloss");
    $(".interlineargloss").ready(function () {
        $(".interlineargloss").on('shown.bs.collapse', function () {
            $(".intlingloss").addClass('glyphicon-chevron-up').removeClass('glyphicon-chevron-down');
        });
        $('.interlineargloss').on('hidden.bs.collapse', function () {
            $(".intlingloss").addClass('glyphicon-chevron-down').removeClass('glyphicon-chevron-up');
        });
    });
}

function getAllSpeakerIdsOfAudio() {
    let sentenceSpeakerIds = $("#speakeridsdropdown").val();
    if (!sentenceSpeakerIds) {
        sentenceSpeakerIds = "";
    }
    else if (sentenceSpeakerIds.length == 1) {
        sentenceSpeakerIds = sentenceSpeakerIds[0];
    }
    return sentenceSpeakerIds
}

function createSentenceForm(formElement, boundaryID) {
    // var activeSentenceMorphemicBreak = '<input type="checkbox" id="activeSentenceMorphemicBreak" name="activeSentenceMorphemicBreak" value="false" onclick="">'+
    //                                     '<label for="activeSentenceMorphemicBreak">&nbsp; Add Interlinear Gloss</label><br></br>'
    // // document.getElementById("sentencefield2").innerHTML = "";                                        
    // $(".sentencefield").html(activeSentenceMorphemicBreak);
    // console.log('createSentenceForm(formElement)', formElement, boundaryID);
    inpt = '';
    // console.log('formElement', formElement);
    let activeprojectform = JSON.parse(localStorage.activeprojectform);
    let activeTag = getActiveTag();
    createNavTabs(activeprojectform, activeTag);
    // console.log("activeprojectform", activeprojectform);
    for (let [key, value] of Object.entries(formElement)) {
        // console.log('first', key, value)
        if (key === 'transcription') {
            let transcriptionScriptList = activeprojectform['Transcription'][1];

            // let currentAudioAllSpeakerids = $("#speakeridsdropdown").val();
            let currentAudioAllSpeakerids = activeprojectform['audioSpeakerIds'];
            let currentBoundarySpeakerids = formElement['speakerId'];
            // let currentBoundarySpeakerids = ;

            // console.log("All speaker IDs", currentAudioAllSpeakerids);
            var transcriptionScript = formElement[key];
            // if (Object.keys(transcriptionScript).length > 0) {
            // add fieldset
            // inpt += '<fieldset class="form-group border">'+
            //         '<legend class="col-form-label">'+
            //         'Transcription'+
            //         '<button class="btn btn-default pull-right" type="button" data-toggle="collapse"'+
            //         'data-target=".transcription" aria-expanded="false" aria-controls="transcription1"'+
            //         'onclick="collapseTranscription()">'+
            //         '<span class="glyphicon glyphicon-chevron-up transcript" aria-hidden="true"></span>'+
            //         '</button></legend>';
            // // inpt += '</fieldset>';
            let glossInpt = '';
            glossInpt += '<select id="scripttoglossdropdown" oninput="transcriptionToGloss()" style="width: 80%; display: block;"></select>';
            glossInpt += '&nbsp;&nbsp;&nbsp; &nbsp;';
            glossInpt += '<select id="tokencolcount" oninput="transcriptionToGloss()" style="width: 15%; display: block;"></select>';
            glossInpt += '<div id="idmodal"></div>';
            // add fieldset
            // glossInpt += '<fieldset class="form-group border">'+
            //             '<legend class="col-form-label">'+
            //             'Interlinear Gloss'+
            //             '<button class="btn btn-default pull-right" type="button" data-toggle="collapse"'+
            //             'data-target=".interlineargloss" aria-expanded="false" aria-controls="interlineargloss1"'+
            //             'onclick="collapseInterlineargloss()">'+
            //             '<span class="glyphicon glyphicon-chevron-up intlingloss" aria-hidden="true"></span>'+
            //             '</button></legend>';
            // console.log(transcriptionScript)
            // console.log('second', 'Object.keys(transcriptionScript)[0]', Object.keys(transcriptionScript)[0]);
            // firstTranscriptionScript = Object.keys(transcriptionScript)[0]
            sentSpeakerIdEle = '<label for="sentspeakeriddropdown">Speaker ID: </label>'
            sentSpeakerIdEle += '<select class="custom-select custom-select-sm keyman-attached" id="sentspeakeriddropdown"'
                + 'name = "sentSpeakerId" multiple = "multiple" style = "width:100%" required onclick="updateKeyboard(this)" onchange="autoSavetranscription(event,this)"> "';


            for (let i = 0; i < currentAudioAllSpeakerids.length; i++) {
                optionValue = currentAudioAllSpeakerids[i];
                if (currentBoundarySpeakerids.includes(optionValue) || currentAudioAllSpeakerids.length == 1) {
                    // console.log("Option value", optionValue);
                    if (optionValue != "") {
                        sentSpeakerIdEle += '<option value="' + optionValue + '" selected>' + optionValue + '</option>';
                    }
                }
                else {
                    if (optionValue != "") {
                        sentSpeakerIdEle += '<option value="' + optionValue + '">' + optionValue + '</option>';
                    }
                }
            }

            sentSpeakerIdEle += '</select><br/><br/>'


            inpt += sentSpeakerIdEle

            let firstTranscriptionScript = transcriptionScriptList[0];
            for (let t = 0; t < transcriptionScriptList.length; t++) {
                // for (let [transcriptionkey, transcriptionvalue] of Object.entries(transcriptionScript)) {
                let transcriptionkey = transcriptionScriptList[t];
                let transcriptionvalue = transcriptionScript[transcriptionkey];
                // console.log(transcriptionkey, transcriptionvalue)
                // activeprojectform = JSON.parse(localStorage.getItem('activeprojectform'));
                // console.log('activeprojectform', activeprojectform)
                // scriptCode = activeprojectform['scriptCode']
                // langScript = activeprojectform['langScript']
                // lang = scriptCodeToLang(transcriptionkey, scriptCode, langScript)
                sentencemorphemicbreakvalue = formElement['sentencemorphemicbreak'][transcriptionkey]
                // console.log("formElement['sentencemorphemicbreak']", sentencemorphemicbreakvalue)
                // add fieldset
                // inpt += '<div class="form-group transcription collapse in">';
                // inpt += '<label for="Transcription_' + transcriptionkey + '">Transcription in ' + transcriptionkey + '</label>'
                inpt += '<label for="Transcription_' + transcriptionkey + '">' + transcriptionkey + '</label>';
                // inpt += '<input type="text" class="form-control transcription-box" id="Transcription_' + transcriptionkey + '"' +
                //     'placeholder="Transcription ' + transcriptionkey + '" name="transcription_' + transcriptionkey + '"' +
                //     'value="' + transcriptionvalue + '" onkeyup="autoSavetranscription(this)" required><br>';
                // inpt += '<textarea class="form-control transcription-box" id="Transcription_' + transcriptionkey + '"' +
                //     'placeholder="Transcription ' + transcriptionkey + '" name="transcription_' + transcriptionkey + '"' +
                //     'value="' + transcriptionvalue + '" onkeyup="autoSavetranscription(event,this)" required>' + transcriptionvalue + '</textarea><br>';
                inpt += '<textarea class="form-control transcription-box keyman-attached" id="Transcription_' + transcriptionkey + '"' +
                    'placeholder="Transcription ' + transcriptionkey + '" name="transcription_' + transcriptionkey + '"' +
                    'value="' + transcriptionvalue +
                    '" onclick="updateKeyboard(this)"' +
                    ' oninput="autoSavetranscription(event,this)" required>' + transcriptionvalue + '</textarea><br>';
                // '</div></div>';
                // add fieldset
                // inpt += '</div>';
                // add fieldset
                // glossInpt += '<div class="form-group interlineargloss collapse in">';

                if (transcriptionkey === firstTranscriptionScript) {
                    // console.log("transcriptionkey === firstTranscriptionScript");
                    // glossInpt += '<div id="morphemicDetail_' + transcriptionkey + '" style="display: block;">';
                    // glossInpt += '<p><strong>Give Morphemic Break</strong></p>' +
                    //                 '<p><strong>**(use "#" for word boundary(if there are affixes in the word) and "-" for morphemic break)</strong></p>';
                    // glossInpt += '<div class="form-group"><div class="input-group">';
                    glossInpt += ' <input type="text" id="activeBoundaryID" name="activeBoundaryID" value="' + boundaryID + '" hidden>';
                    if ('glossDetails' in activeprojectform &&
                        boundaryID in activeprojectform['glossDetails']) {
                        // console.log("'glossDetails' in activeprojectform");
                        glossdetails = activeprojectform['glossDetails'][boundaryID]
                        posdetails = activeprojectform['posDetails'][boundaryID]
                        // commented on 2024_04_22_10_27_15_954079
                        // glossInpt += '<textarea class="form-control transcription-box" id="sentenceMorphemicBreak_' + transcriptionkey + '"' +
                        //         'placeholder="e.g. I have re-#write#-en the paper#-s" name="morphsentenceMorphemicBreak_' + transcriptionkey + '"' +
                        //         'value="' + sentencemorphemicbreakvalue + '" '+
                        //         'onfocus="autoSavetranscription(event,this,true,\'sentenceMorphemicBreak_\')" required readonly>' + sentencemorphemicbreakvalue + '</textarea><br>';
                        // glossInpt += '<div class="input-group-btn" id="editsentmorpbreak">' +
                        //     '<button class="btn btn-warning" type="button" id="editSentenceField"' +
                        //     'onclick="editMorphemicBreakSentence(\'' + transcriptionvalue + '\', \'' + transcriptionkey + '\');">' +
                        //     '<span class="glyphicon glyphicon-edit" aria-hidden="true"></span>' +
                        //     '</button></div>';
                        createEditableGlossForm(transcriptionvalue,
                            transcriptionkey,
                            sentencemorphemicbreakvalue,
                            glossdetails,
                            posdetails,
                            boundaryID)
                    }
                    else {
                        // without onkeyup event
                        // commented on 2024_04_22_10_27_15_954079
                        // glossInpt += '<textarea class="form-control transcription-box" id="sentenceMorphemicBreak_' + transcriptionkey + '"' +
                        //             'placeholder="e.g. I have re-#write#-en the paper#-s" name="morphsentenceMorphemicBreak_' + transcriptionkey + '"' +
                        //             'value="' + sentencemorphemicbreakvalue + '" '+
                        //             'onfocus="autoSavetranscription(event,this,true,\'sentenceMorphemicBreak_\')" required>' + sentencemorphemicbreakvalue + '</textarea><br>';
                        // glossInpt += '<div class="input-group-btn"  id="editsentmorpbreak">' +
                        //     '<button class="btn btn-success" type="button" id="checkSentenceField"' +
                        //     'onclick="getSentence(\'' + transcriptionvalue + '\', \'' + transcriptionkey + '\');">' +
                        //     '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>' +
                        //     '</button></div>';
                        // updating interlinearglossing interface
                        let sentencemorphemicbreakupdatedvalue = sentencemorphemicbreakvalue;
                        if (sentencemorphemicbreakupdatedvalue === '') {
                            sentencemorphemicbreakupdatedvalue = transcriptionvalue;
                        }
                        // glossInpt += '<div class="row">';
                        // glossInpt += '<br><div class="col-md-6 form-group textcontentouter">' +
                        //     // '<label class="col" for="text">Text:</label><br>' +
                        //     '<input type="hidden" class="form-control keyman-attached" id="text"' + ' name="text" value="' + sentencemorphemicbreakupdatedvalue + '">' +
                        //     '<textarea class="col form-control textcontent"' +
                        //     ' id="sentenceMorphemicBreak_' + transcriptionkey + '"' +
                        //     ' name="morphsentenceMorphemicBreak_' + transcriptionkey + '"' +
                        //     ' onclick="updateKeyboard(this)"' +
                        //     ' oninput="autoSavetranscription(event,this,true,\'sentenceMorphemicBreak_\')"' +
                        //     ' ondblclick=tokenAnnotation(event)>' + sentencemorphemicbreakupdatedvalue + '</textarea>' +
                        //     '</div>';
                        // glossInpt += '<div class="col-md-12 form-group glosstable">' +
                        //     '<span>123</span>'+
                        //     '</div>';
                        // let interlinearGlossFormat = "";
                        // let customizeGloss = [];
                        // if ("Interlinear Gloss" in activeprojectform) {
                        //     let interlinearglossforminfo = interlinearGlossFormInfo(activeprojectform);
                        //     interlinearGlossFormat = interlinearglossforminfo.interlinearGlossFormat;
                        //     customizeGloss = interlinearglossforminfo.customizeGloss;
                        // }
                        glossInpt += '<br><div id="interlinearglosscontainer" class="container">';
                        // glossInpt += createGlossingTable(sentencemorphemicbreakupdatedvalue,
                        //                                     interlinearGlossFormat,
                        //                                     customizeGloss);
                        glossInpt += '</div>';
                    }
                    // glossInpt += '</div></div></div>';
                    // glossInpt += '</div>';
                }
            }
            // add fieldset
            // inpt += '</fieldset>';
            // glossInpt += '</fieldset>';
            // console.log(document.getElementById("transcription2").innerHTML)
            document.getElementById("transcription2").innerHTML = "";
            // document.getElementById("transcription2").value = "-";
            // $('.transcription1').append(inpt);
            $('#transcription2').append(inpt);
            $('#sentspeakeriddropdown').select2({
                // data: optionsList
            });
            // console.log(document.getElementById("transcription2").innerHTML)
            // console.log(activeprojectform['Interlinear Gloss'][1]);
            if ('Interlinear Gloss' in activeprojectform &&
                Object.keys(activeprojectform['Interlinear Gloss'][1]).length === 0) {
                glossInpt = '';
            }
            document.getElementById("interlineargloss2").innerHTML = "";
            $('#interlineargloss2').append(glossInpt);
            let additioanlTranscription = [];
            if ('Additional Transcription' in activeprojectform) {
                additioanlTranscription = Object.keys(activeprojectform['Additional Transcription'][1]);
            }
            let transcriptionScriptDifference = transcriptionScriptList.filter(x => !additioanlTranscription.includes(x));
            $('#scripttoglossdropdown').select2({
                placeholder: 'Transcription Script',
                data: transcriptionScriptDifference,
            });
            $('#tokencolcount').select2({
                placeholder: 'Transcription Script',
                data: [1, 2, 3, 4, 5, 6],
            });
            $('#tokencolcount').val(6);
            $('#tokencolcount').trigger('change');
            transcriptionToGloss();
            inpt = '';
            glossInpt = '';
            let scripttoglossdropdownselected = getScriptToGlossDropdownSelected();
            document.getElementById("interlinearglosstab").onclick = function () { transcriptionToGloss() };
        }
        else if ('Translation' in activeprojectform &&
            key === 'translation') {
            translationLang = formElement[key];
            // console.log(translationLang);
            if (Object.keys(translationLang).length > 0) {
                inpt += '<p id="translationsubtitle" class="text-center text-info" style="display: none;">&nbsp;</p>';
                translationSubtitle();
                // add fieldset
                // inpt += '<fieldset class="form-group border">'+
                //         '<legend class="col-form-label">'+
                //         'Translation'+
                //         '<button class="btn btn-default pull-right" type="button" data-toggle="collapse"'+
                //         'data-target=".translation" aria-expanded="false" aria-controls="translationfield1"'+
                //         'onclick="collapseTranslation()">'+
                //         '<span class="glyphicon glyphicon-chevron-up translate" aria-hidden="true"></span>'+
                //         '</button></legend>';
                // console.log(translationLang, Object.keys(translationLang).length);
                // if (Object.keys(translationLang).length > 0) {
                // console.log(translationLang, Object.keys(translationLang).length)
                // var activeTranslationField = '<input type="checkbox" id="activeTranslationField" name="activeTranslationField" value="false" onclick="activeTranslationLangs()" checked disabled>' +
                //     '<label for="activeTranslationField">&nbsp; Add Translation</label><br></br>' +
                //     '<div id="translationlangs" style="display: block;"></div>';
                // document.getElementById("translation2").innerHTML = "";
                // $(".translationfield1").append(activeTranslationField);
                translang = Object.keys(activeprojectform["Translation"][1]);
                // console.log(translang)
                translangcount = -1
                for (let [translationkey, translationvalue] of Object.entries(translationLang)) {
                    translangcount += 1
                    // console.log(translationkey, translationvalue);
                    translationkey = translationkey.split('-')[1]
                    // add fieldset
                    // inpt += '<div class="form-group translation collapse in">';
                    // inpt += '<label for="Translation_' + translationkey + '">Translation in ' + translang[translangcount] + '</label>';
                    inpt += '<label for="Translation_' + translationkey + '">' + translang[translangcount] + '</label>';

                    inpt += '<textarea class="form-control translation-box keyman-attached" id="Translation_' + translationkey + '"' +
                        'placeholder="Translation ' + translang[translangcount] + '" name="translation_' + translationkey + '"' +
                        // 'value="' + translationvalue + '" onkeyup="autoSavetranscription(event,this)" required>' + translationvalue + '</textarea><br>';
                        'value="' + translationvalue +
                        '" onclick="updateKeyboard(this)"' +
                        ' oninput="autoSavetranscription(event,this)" required>' + translationvalue + '</textarea><br>';
                    // inpt += '<input type="text" class="form-control" id="Translation_' + translationkey + '"' +
                    //         'placeholder="Translation ' + translang[translangcount] + '" name="translation_' + translationkey + '"' +
                    //         'value="' + translationvalue + '">' +
                    // 'value="'+ translationvalue +'" required>'+
                    // inpt += '</div>';
                    // add fieldset
                    // inpt += '</div>';
                }
                // document.getElementById("translationlangs").innerHTML = "";
                // $('#translationlangs').append(inpt);
                // add fieldset
                // inpt += '</fieldset>';
                document.getElementById("translation2").innerHTML = "";
                $('#translation2').append(inpt);
                inpt = '';
            }
        }
        // else if (key === 'pos') {

        // }
        else if ('Tagsets' in activeprojectform &&
            'Boundary Annotation' in activeprojectform &&
            key === 'tags') {
            let tagsetWithMetadata = activeprojectform['Boundary Annotation']
            let tagsField = transcriptAnnotationInterface(tagsetWithMetadata)
            // document.getElementById("annotation2").innerHTML = "";
            // $(".annotation1").append(tagsField);
            // inpt = '';
        }
        // else if (key === 'gloss') {
        //     activeprojectform = JSON.parse(localStorage.activeprojectform)
        //     glossDetail = activeprojectform['glossDetails']
        // console.log("glossDetails['glossDetails']", glossDetails)
        // console.log("glossDetails['glossDetails']", glossDetails['glossDetails'])
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

        if ("comment" in formElement) {
            var commentVal = formElement["comment"];
        }
        else {
            try {
                commentVal = document.getElementById("comment-box-id").value;
            }
            catch {
                commentVal = '';
            }
            formElement["comment"] = commentVal;
        }


        // console.log("Comment in create", commentVal)
        // console.log(formElement)
        inpt += '<div class="form-group">';
        inpt += '<label for="comment-box-id">Comments:</label>'
        inpt += '<textarea class="form-control comment-box keyman-attached" id="comment-box-id" ' +
            'placeholder="Comments" name="comment-box"' +
            // 'value="' + commentVal + '" onkeyup="autoSavetranscription(event,this)" required>' + commentVal + '</textarea><br>';
            'value="' + commentVal + '" onclick="updateKeyboard(this)" oninput="autoSavetranscription(event,this)" required>' + commentVal + '</textarea><br>';
        document.getElementById("transcription-comments").innerHTML = "";
        $('#transcription-comments').append(inpt);
        inpt = '';
    }

    $("#activeSentenceMorphemicBreak").click(function () {
        // activetranscriptionscript = displayRadioValue();
        eleid = 'Transcription_' + Object.keys(transcriptionScript)[0]
        activetranscriptionscriptvalue = document.getElementById(eleid).value;
        if (activetranscriptionscriptvalue === '') {
            document.getElementById("activeSentenceMorphemicBreak").checked = false;
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
    // console.log(value, name);
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
        morph_len = (sentence_morphemic_break_full.match(/-/g) || []).length;
        boundary_len = (sentence_morphemic_break_full.match(/#/g) || []).length;
        // console.log(morph_len)
        // console.log(boundary_len)
        if (morph_len != boundary_len) {
            alert("Number of # (" + boundary_len + ") not equal to numer of - (" + morph_len + ") in the morphemic break")
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

        a: String(morphemicSplitSentence)
    }, function (data) {
        // console.log(data.predictedPOS);


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
    // console.log(morphemicSplitSentence, name, morphemePOS, glossdetails, posdetails);
    var morphemeinput = '</br><div class="morphemefield_' + name + '">';
    morphemeinput += '<div class="row">' +
        '<div class="col-sm-3"><strong>Morphemes EDIT</strong></div>' +
        '<div class="col-sm-3"><strong>Gloss</strong></div>' +
        '<div class="col-sm-3"><strong>Morph Type</strong></div>' +
        '<div class="col-sm-3"><strong>POS</strong></div><br><br>' +
        '</div>';
    // var morphemeinput = '';
    morphemeCount = morphemicSplitSentence.length;
    for (let i = 0; i < morphemeCount; i++) {
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
            if (morphkey[3] === String(i + 1) && morphkey[4] === morphemicSplitSentence[i]) {
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
            if (poskey[1] === String(i + 1)) {
                pos = posvalue
            }

        }
        // console.log(pos)
        console.log('morphemicgloss', morphemicgloss);
        if (morphemicSplitSentence[i].includes('-')) {
            // console.log(morphemicSplitSentence[i], morphemicgloss)
            morphemeinput += '<div class="input-group">' +
                '<input type="text" class="form-control" name="morph_morpheme_' + name + '_' + (i + 1) + '"' +
                'placeholder="' + morphemicSplitSentence[i] + '" value="' + morphemicSplitSentence[i] + '"' +
                'id="morphemeField' + name + (i + 1) + '" readonly style="float:none;width: 200px;"/>' +
                '<span class="input-group-btn" style="width:50px;"></span>' +
                '<select class="morphemicgloss' + name + (i + 1) + '" name="morph_gloss_' + name + '_' + (i + 1) + '"' +
                ' multiple="multiple" style="width: 200px"  onchange="autoSavetranscription(event,this)">';
            if (morphemicgloss != '') {
                morphemeinput += '<option value="' + morphemicgloss + '" selected>' + morphemicgloss + '</option>';
            }
            morphemeinput += '</select>' +
                '<span class="input-group-btn" style="width:50px;"></span>' +
                '<select class="lextype' + name + (i + 1) + '" name="morph_lextype_' + name + '_' + (i + 1) + '"' +
                ' style="width: 200px"  onchange="autoSavetranscription(event,this)">';
            morphemeinput += '<option value="' + morphemiclextype + '" selected>' + morphemiclextype + '</option>';
            morphemeinput += '</select>' +
                '<span class="input-group-btn" style="width:50px;"></span></div><br>';
            // console.log(morphemeinput);                  
        }
        else {
            morphemeinput += '<div class="input-group">' +
                '<input type="text" class="form-control" name="morph_morpheme_' + name + '_' + (i + 1) + '"' +
                'placeholder="' + morphemicSplitSentence[i] + '" value="' + morphemicSplitSentence[i] + '"' +
                'id="morphemeField' + name + (i + 1) + '" readonly style="float:none;width: 200px;">' +
                '<span class="input-group-btn" style="width:50px;"></span>' +
                '<input type="text" class="form-control" name="morph_gloss_' + name + '_' + (i + 1) + '"' +
                // ' id="morphemicgloss' + name + (i + 1) + '" value="' + morphemicgloss + '" onkeyup="autoSavetranscription(event,this)" style="float:none;width: 200px;"/>' +
                ' id="morphemicgloss' + name + (i + 1) + '" value="' + morphemicgloss + '" oninput="autoSavetranscription(event,this)" style="float:none;width: 200px;"/>' +
                '<span class="input-group-btn" style="width:50px;"></span>' +
                '<select class="lextype' + name + (i + 1) + '" name="morph_lextype_' + name + '_' + (i + 1) + '"' +
                ' style="width: 200px" onchange="autoSavetranscription(event,this)">';
            // console.log(morphemicSplitSentence[i], morphemePOS[i][1])
            morphemeinput += '<option value="' + morphemiclextype + '" selected>' + morphemiclextype + '</option>';
            morphemeinput += '</select>' +
                '<span class="input-group-btn" style="width:50px;"></span>' +
                '<select class="pos' + name + (i + 1) + '" name="morph_pos_' + name + '_' + (i + 1) + '"  onchange="autoSavetranscription(event,this)" style="width: 200px">' +
                // '<option value="'+ morphemePOS[i][1] +'" selected>'+ morphemePOS[i][1] +'</option>'+
                '<option value="' + pos + '" selected>' + pos + '</option>' +
                '</select></div><br>';

        }
    }
    morphemeinput += ' <input type="text" id="morphcount" name="morphcount' + name + '" value="' + morphemeCount + '" hidden>'
    // console.log(morphemeinput)
    // console.log(".morphemicDetail_"+name)
    $("#morphemicDetail_" + name).append(morphemeinput);
    morphemeFieldsSelect2(morphemicSplitSentence, name);
    // for (let i = 0; i < morphemicSplitSentence.length; i++) {
    //     $('.morphemicgloss' + name + (i + 1)).select2({
    //         tags: true,
    //         placeholder: 'Gloss',
    //         data: morphemicGloss,
    //         allowClear: true
    //         // sorter: false
    //     });

    //     $('.lextype' + name + (i + 1)).select2({
    //         tags: true,
    //         placeholder: 'Morph Type',
    //         data: morphType
    //         // allowClear: true,
    //         // sorter: false
    //     });

    //     $('.pos' + name + (i + 1)).select2({
    //         tags: true,
    //         placeholder: 'POS',
    //         data: posCategories
    //         // allowClear: true,
    //         // sorter: false
    //         // width: 'element'
    //     });

    // }
}

// function createMorphemeForm(form, region) {
//     if (region.data.morphemicData.activeSentenceMorphemicBreak == "true") {
// console.log(region.data.note);
//         document.getElementById("activeSentenceMorphemicBreak").checked = true;
//         $(".containerremovesentencefield1").remove();
//         activeMorphSentenceField();
//         if (region.data.morphemicData.sentenceMorphemicBreak1) {
//             form.elements.sentenceMorphemicBreak1.value = region.data.morphemicData.sentenceMorphemicBreak1
//             getSentence(1);
//             setTimeout(function () {
//                 for (let [key, value] of Object.entries(region.data.morphemicData)) {
// console.log(key, value, form.elements[key].tagName);
//                     if (form.elements[key] !== undefined && form.elements[key].tagName == "SELECT") {
// console.log(key, value, form.elements[key]);
//                         form.elements[key].value = value
//                     }
//                     else if (form.elements[key] !== undefined) {
//                         form.elements[key].value = value
//                     }
//                 }
//             }, 100);

//         }
//     }

// }

$("#stopAudio").click(function () {
    wavesurfer.stop();
    playPauseState = $(".audioplaypause").attr('class');
    if (playPauseState.includes('glyphicon-pause')) {
        $(".audioplaypause").addClass('glyphicon-play').removeClass('glyphicon-pause');
    }
});

$("#playPauseAudio").click(function () {
    wavesurfer.playPause();
    playPauseState = $(".audioplaypause").attr('class');
    // console.log(playPauseState)
    if (playPauseState.includes('glyphicon-play')) {
        // $(".audioplaypause").addClass('glyphicon-pause').removeClass('glyphicon-play');
        togglePlayPause(1);
    }
    else if (playPauseState.includes('glyphicon-pause')) {
        // $(".audioplaypause").addClass('glyphicon-play').removeClass('glyphicon-pause');
        togglePlayPause(0);
    }
});


function playPauseBoundaryStart() {
    let form = document.forms.edit;
    // console.log(form[2].id);
    let regionId = form.dataset.region;
    // console.log(regionId);
    if (regionId) {
        let region = wavesurfer.regions.list[regionId];
        startTime = region.start
        endTime = region.end
        if (wavesurfer.isPlaying()) {
            wavesurfer.pause();
            togglePlayPauseBoundaryStart(0);
            // togglePlayPause(0);
        }
        else {
            wavesurfer.play(startTime, endTime);
            // togglePlayPause(1);
            togglePlayPauseBoundaryStart(1);
        }
    }
}
$("#playPauseBoundaryStart").click(function () {
    playPauseBoundaryStart();
});

function playPauseBoundary() {
    let form = document.forms.edit;
    // console.log(form[2].id);
    let regionId = form.dataset.region;
    if (regionId) {
        let region = wavesurfer.regions.list[regionId];
        startTime = region.start
        endTime = region.end
        // currentCursorTime = wavesurfer.getCurrentTime();
        // console.log(startTime, endTime, currentCursorTime);
    }
    if (currentCursorTime !== startTime) {
        // console.log(startTime, endTime, currentCursorTime);
        if (wavesurfer.isPlaying()) {
            // console.log(startTime, endTime, currentCursorTime);
            wavesurfer.pause();
            // togglePlayPause(0);
            togglePlayPauseBoundary(0);
        }
        // else if (Math.trunc(currentCursorTime) === Math.trunc(endTime)) {
        //     wavesurfer.play(startTime, endTime);
        //     togglePlayPause(1);
        // }
        else {
            // console.log(startTime, endTime, currentCursorTime);
            wavesurfer.play(currentCursorTime, endTime);
            // togglePlayPause(1);
            togglePlayPauseBoundary(1);
        }
    }
    else if (currentCursorTime === startTime) {
        // console.log(startTime, endTime, currentCursorTime);
        wavesurfer.play(startTime, endTime);
        togglePlayPause(1);
        // togglePlayPauseBoundary(1);
    }
    // wavesurfer.playPause();
    // playPauseState = $(".playPauseBoundaryClass").attr('class');
    // console.log(playPauseState)
    // console.log(playPauseState.innerText);
    // if (playPauseState.includes('glyphicon-play')) {
    //     // $(".playPauseBoundaryClass").addClass('glyphicon-pause').removeClass('glyphicon-play');
    //     // playPauseState.innerText = 'Play This Boundary'
    //     togglePlayPause(1);
    // }
    // else if (playPauseState.includes('glyphicon-pause')) {
    //     // $(".playPauseBoundaryClass").addClass('glyphicon-play').removeClass('glyphicon-pause');
    //     // playPauseState.innerText = 'Pause This Boundary'
    //     togglePlayPause(0);
    // }
}

function KeyPress(e) {
    var evtobj = window.event ? event : e
    if (evtobj.keyCode == 32 && evtobj.ctrlKey) {
        playPauseBoundary();
    }
}
document.onkeydown = KeyPress;

$("#playPauseBoundary").click(function () {
    playPauseBoundary();
});

function togglePlayPause(state) {
    if (state === 1) {
        $(".audioplaypause").addClass('glyphicon-pause').removeClass('glyphicon-play');
        $(".playPauseBoundaryClass").addClass('glyphicon-pause').removeClass('glyphicon-play');
    }
    else if (state === 0) {
        $(".playPauseBoundaryClass").addClass('glyphicon-play').removeClass('glyphicon-pause');
        $(".audioplaypause").addClass('glyphicon-play').removeClass('glyphicon-pause');
    }
}

function togglePlayPauseBoundary(state) {
    if (state === 1) {
        $(".audioplaypauseboundary").addClass('glyphicon-pause').removeClass('glyphicon-play');
        // $(".playPauseBoundaryClass").addClass('glyphicon-pause').removeClass('glyphicon-play');
    }
    else if (state === 0) {
        // $(".playPauseBoundaryClass").addClass('glyphicon-play').removeClass('glyphicon-pause');
        $(".audioplaypauseboundary").addClass('glyphicon-play').removeClass('glyphicon-pause');
    }
}

function togglePlayPauseBoundaryStart(state) {
    if (state === 1) {
        $(".audioplaypauseboundarystart").addClass('glyphicon-pause').removeClass('glyphicon-play');
        // $(".playPauseBoundaryClass").addClass('glyphicon-pause').removeClass('glyphicon-play');
    }
    else if (state === 0) {
        // $(".playPauseBoundaryClass").addClass('glyphicon-play').removeClass('glyphicon-pause');
        $(".audioplaypauseboundarystart").addClass('glyphicon-play').removeClass('glyphicon-pause');
    }
}

function drawBoundaries(state) {

}


function transcriptionFormDisplay(form, mode) {
    if (form.style.display === "none") {
        form.style.display = "block";
    }
    else if (form.style.display === "block" && mode === 'edit') {
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
    let form = document.forms.edit;
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
    for (i = 0; i < regions.length; i++) {
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

// //  change in trancription radio button
// function transcriptionDetailsOnChange(form, region) {
//     let sentenceData = new Object();
//     if (region.data.sentence) {
//         sentenceData = region.data.sentence
//         sentData = sentenceDetails(sentenceData);
//     }
//     else {
//         sentData = sentenceDetails(sentenceData);
//     }
//     region.update({
//         start: form.elements.start.value,
//         end: form.elements.end.value,
//         data: {
//             sentence: sentData
//         }
//     });
// }

function getActiveRegionSentence(region) {
    var sentence = ''
    let regions = JSON.parse(localStorage.regions)
    for (i = 0; i < regions.length; i++) {
        if (regions[i]['start'] === region.start &&
            regions[i]['end'] === region.end) {
            // console.log('getActiveRegionSentence(region)', regions[i])
            // if ('sentence' in regions[i]) {
            // console.log("'sentence' in Object.values(regions[i])")
            //     sentence = Object.values(regions[i]['sentence'])[0]
            // console.log('sentence getActiveRegionSentence(region)', sentence)    
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

function ipaFocus(x) {
    // console.log('------------------------')
    meeteiString = ''
    ipaString = document.getElementById('ipa').value
    // console.log(ipaString);
    activeprojectform = JSON.parse(localStorage.activeprojectform)
    ipaToMeetei = activeprojectform['ipaToMeetei']
    // console.log(ipaToMeetei);
    ipaStringList = ipaString.split(' ')
    // console.log(ipaStringList, ipaStringList.length)
    meeteiStringList = []
    for (p = 0; p < ipaStringList.length; p++) {

        meeteiChar = ''
        // console.log(ipaStringList[p], ipaStringList[p].length)
        for (i = 0; i < ipaStringList[p].length; i++) {
            ipaChar = ipaStringList[p]
            // console.log(ipaChar[i])
            if (ipaChar[i] in ipaToMeetei) {
                // console.log(ipaChar[i], ipaToMeetei[ipaChar[i]])
                // meeteiString += ipaToMeetei[ipaChar[i]]
                meeteiChar += ipaToMeetei[ipaChar[i]]
            }
            else {
                meeteiChar += ipaChar[i]
            }
        }
        meeteiStringList.push(meeteiChar)
    }
    // console.log(meeteiStringList.join(' '))
    meeteiString = meeteiStringList.join(' ')
    document.getElementById('meetei').value = meeteiString
}

function getAudiDuration(audiFilePath) {
    function getDuration(src, cb) {
        var audio = new Audio();
        $(audio).on("loadedmetadata", function () {
            cb(audio.duration);
        });
        audio.src = src;
    }
    getDuration(audiFilePath, function (length) {
        // console.log('I got length ' + length, (length/60).toFixed(2));
        audioDur = (length / 60).toFixed(2)
        audioDurMin = audioDur.split('.')[0]
        audioDurSec = audioDur.split('.')[1] * 60
        // console.log(audioDur, audioDurMin, audioDurSec);
        let showDur = '<br><span>Duration: <span id="currentaudioduration">' + audioDur + '</span> minutes</span>';
        // document.getElementById("idaudiometadata").append(showDur);
        $('#idaudiometadata').append(showDur);
    });
}

function showBoundaryCount(boundaryCount) {
    if (boundaryCount !== '') {
        let showBCount = '<span>Boundary Count: ' + boundaryCount + '</span>';
        // document.getElementById("idaudiometadata").append(showDur);
        $('#idaudiometadata').append(showBCount);
    }
}

function lastUpdatedBy(lstUpdatedBy) {
    // console.log(lstUpdatedBy);
    // lstUpdatedBy = '';
    if (lstUpdatedBy !== '') {
        let lastUpdate = '<br><span>Last Updated By: ' + lstUpdatedBy + '</span>';
        // document.getElementById("idaudiometadata").append(showDur);
        // $('#idaudiometadata').append(lastUpdate);
        $('#iddefaultfield').append(lastUpdate);
    }
}

function autoSavetranscriptionSubPart() {
    let form = document.forms.edit;
    // console.log(form);
    // console.log(form[2].id);
    // console.log(form, form.dataset);
    let regionId = form.dataset.region;
    if (regionId) {
        let region = wavesurfer.regions.list[regionId];
        // console.log(region);
        if (region) {
            saveBoundaryData(region, form);
        }
        // else if (region === undefined) {
        //     transcriptionFormDisplay(form);
        // }
    }
}

function autoSavetranscription(e, transcriptionField, update = true, from = '') {
    // console.log(wavesurfer, wavesurfer.regions);
    // console.log(e.keyCode);
    // console.log(transcriptionField, transcriptionField.id, transcriptionField.value);
    // console.log(e, transcriptionField);
    // console.log(e, transcriptionField, update, from);
    let sentenceMorphemicBreakSymbols = ['-']
    let data = e.data;
    // console.log(data);
    if (e.keyCode == 13) {
        current_val = transcriptionField.value;
        keyChar = String.fromCharCode(e.keyCode);
        // console.log("keychar", keyChar);
        // console.log("old val", current_val);
        new_val = current_val.replace(/\s/gm, " ");
        transcriptionField.value = new_val
        // console.log("new val", new_val);
        transcriptionField.textContent = new_val;
        // console.log("Replace enter");
    }

    // console.log(from);

    // showNote();
    if (update) {
        if (transcriptionField.id.includes('sentenceMorphemicBreak_')) {
            // console.log(update);
            // mapTranscriptionInterlinearGloss(e, transcriptionField);
        }
    }
    if (from === 'sentenceMorphemicBreak_') {
        let clickedIndex = e.target.selectionEnd;
        // console.log(clickedIndex);
        if (data === null) {
            // console.log('Deletion!')
            current_value = transcriptionField.value;
            let last_value = transcriptionField.value;
            let activeBoundaryID = document.getElementById('activeBoundaryID').value;
            let localStorageRegions = JSON.parse(localStorage.regions);
            let scriptName = getScriptToGlossDropdownSelected();
            for (let p = 0; p < localStorageRegions.length; p++) {
                console.log(p);
                if (localStorageRegions[p]['boundaryID'] === boundaryID) {
                    last_value = localStorageRegions[p]['data']['sentence'][activeBoundaryID]['sentencemorphemicbreak'][scriptName];
                    break;
                }
            }
            // console.log(last_value);
            // console.log(last_value[clickedIndex]);
            // console.log(current_value);
            if (sentenceMorphemicBreakSymbols.includes(last_value[clickedIndex])) {
                autoSavetranscriptionSubPart();
                return;
            }
        }
        if (!sentenceMorphemicBreakSymbols.includes(data)) {
            let activeBoundaryID = document.getElementById('activeBoundaryID').value;
            let scripttoglossdropdownselected = getScriptToGlossDropdownSelected();
            transcriptionToGloss();
            document.getElementById(transcriptionField.id).focus();
            document.getElementById(transcriptionField.id).selectionEnd = clickedIndex;
            alert("Only '-' is allow!");
            return;
        }
        else if (sentenceMorphemicBreakSymbols.includes(data)) {
            // console.log(transcriptionField.value);
            // console.log(transcriptionField.value.slice(0, clickedIndex-1)+transcriptionField.value.slice(clickedIndex));
            current_value = transcriptionField.value;
            last_value = transcriptionField.value.slice(0, clickedIndex - 1) + transcriptionField.value.slice(clickedIndex);
            // console.log(current_value, last_value);
            if (sentenceMorphemicBreakSymbols.includes(current_value[clickedIndex - 2]) ||
                sentenceMorphemicBreakSymbols.includes(current_value[clickedIndex])) {
                let activeBoundaryID = document.getElementById('activeBoundaryID').value;
                let scripttoglossdropdownselected = getScriptToGlossDropdownSelected();
                transcriptionToGloss();
                document.getElementById(transcriptionField.id).focus();
                document.getElementById(transcriptionField.id).selectionEnd = clickedIndex;
                alert("Only one '-' is allow!");
                return;
            }
        }
    }

    // activeTranscriptionFieldId = transcriptionField.id;
    // transciptionLang = activeTranscriptionFieldId.split('_')[1];
    // activeTranscriptionFieldValue = transcriptionField.value.trim();
    autoSavetranscriptionSubPart();
    // startTime = document.getElementById('start').value
    // endTime = document.getElementById('end').value
    // console.log(startTime, endTime);
    // startTime = startTime.toString().slice(0, 4).replace('.', '');
    // if (startTime === '0') {
    //     startTime = '000';
    // }
    // endTime = endTime.toString().slice(0, 4).replace('.', '');
    // if (endTime === '0') {
    //     endTime = '000';
    // }
    // console.log(startId, endId)
    // rid = startTime.concat(endTime);
    // console.log(rid);
    // localStorageRegions = JSON.parse(localStorage.regions)
    // for (let [key, value] of Object.entries(localStorageRegions)) {
    // console.log(key, value)
    //     if (localStorageRegions[key]['boundaryID'] === rid) {
    //         localStorageRegions[key]['data']['sentence'][rid]['transcription'][transciptionLang] = activeTranscriptionFieldValue
    //         localStorage.setItem("regions", JSON.stringify(localStorageRegions));
    //     }
    // }
}

function boundaryColor(r, g, b, alpha) {
    return (
        'rgba(' +
        [
            ~~(r),
            ~~(g),
            ~~(b),
            alpha || 1
        ] +
        ')'
    );
}

// update color to the inactive boundary that has been worked upon and which are not yet saved to server
function updateBoundaryColor(activeRegion) {
    activeRegionId = activeRegion.id;
    regionsList = wavesurfer.regions.list;
    // console.log(regionsList);
    for (let [regionId, regionData] of Object.entries(regionsList)) {
        // console.log(regionId, regionData);
        if (regionId === activeRegionId) {
            // console.log(regionId, regionData.color);
            continue;
        }
        else if (regionId !== activeRegionId && regionData.color === "rgba(255,0,0,0.1)") {
            // console.log(regionId, regionData);
            // console.log(regionId, regionData.color);
            regionData.update({
                color: boundaryColor(255, 255, 0, 0.1)
            });
        }
    }
}

function showRegionInfo(region) {
    let regionInfo = '';
    let trans = '';
    try {
        id = region.id;
        startTime = region.start;
        endTime = region.end;
        boundaryID = getBoundaryId(startTime, endTime);
        sentence = region.data.sentence;
        if (sentence) {
            // console.log("Sentence", sentence)
            // console.log("Boundary ID", boundaryID)
            transciptions = sentence[boundaryID]['transcription'];
            for (let [scriptName, transcription] of Object.entries(transciptions)) {
                trans += scriptName + ': ' + transcription + '<br>';
            }
        }
        // let regionInfo = '<br>Boundary ID: '+id+'<br>Start Time: '+startTime+'<br>End Time: '+endTime+'<br>'+trans;
        // regionInfo += '<br>Boundary ID: ' + id;
        regionInfo += '<br>Start Time: ' + startTime;
        regionInfo += '<br>End Time: ' + endTime;
        regionInfo += '<br>' + trans;
    }
    catch (err) {
        // console.log(err);
        regionInfo = '<br>You still have to listen to this boundary';
    }
    $('#regioninfo').html(regionInfo);
    document.getElementById('regioninfo').style.display = 'block';
    // document.getElementById('subtitle').style.display = 'none';
    // document.getElementById('subtitleabsence').style.display = 'block';

    // console.log(region);
    // console.log(id, startTime, endTime, transciptions);
}

function hideRegionInfo(region) {
    document.getElementById('regioninfo').style.display = 'none';
    // document.getElementById('subtitle').style.display = 'block';
    // document.getElementById('subtitleabsence').style.display = 'none';
}

function getBoundaryId(startTime, endTime) {
    startId = get_boundary_id_from_number(parseFloat(startTime).toFixed(2), 5, "0"); //5 is the length of the returned string and 0 is the prefix
    endId = get_boundary_id_from_number(parseFloat(endTime).toFixed(2), 5, "0");

    // startId = startTime.toString().slice(0, 4).replace('.', '');
    // if (startId === '0') {
    //     startId = '000';
    // }
    // endId = endTime.toString().slice(0, 4).replace('.', '');
    // if (endId === '0') {
    //     endId = '000';
    // }
    // console.log(startId, endId)
    rid = startId.concat(endId);

    return rid
}

function openAudioMetaData() {
    let audioMetadataDisplay = document.getElementById('audiometadata')
    if (audioMetadataDisplay.style.display == 'none') {
        audioMetadataDisplay.style.display = 'block'
    }
    else if (audioMetadataDisplay.style.display == 'block') {
        audioMetadataDisplay.style.display = 'none'
    }
}

function closestBoundary(region, overlapBoundary, dragDirection = 'left', diff = 0.001) {
    const min = Math.min(...overlapBoundary)
    // console.log(min)
    if (dragDirection == 'left') {
        region.end = min - diff;
    }
    if (dragDirection == 'right') {
        region.start = min + diff;
    }
    saveRegions();
}

function preventOverlapBoundaries(region) {
    // console.log(region);
    // console.log(region.wrapper);
    // console.log(region.scrollSpeed);
    // console.log(region.start, region.end);
    localStorageRegions = JSON.parse(localStorage.regions);
    // console.log(localStorageRegions);
    let overlapBoundaryStarts = [];
    let overlapBoundaryEnds = [];
    for (i = 0; i < localStorageRegions.length; i++) {
        localStorageRegion = localStorageRegions[i];
        if (region.start == localStorageRegion.start ||
            region.end == localStorageRegion.end) {
            continue
        }
        if ((region.start < localStorageRegion.end &&
            region.start > localStorageRegion.start)) {
            // console.log(region.start, localStorageRegion.end);
            // console.log(region.end, localStorageRegion.start);
            // console.log('OVERLAP!!!... RIGHT DRAG');
            // console.log('FALLING IN REGION: ', localStorageRegion);
            overlapBoundaryEnds.push(localStorageRegion.end);
            // deleteBoundary(region.id);
        }
        else if ((region.end < localStorageRegion.end &&
            region.end > localStorageRegion.start)) {
            // console.log(region.start, localStorageRegion.end);
            // console.log(region.end, localStorageRegion.start);
            // console.log('OVERLAP!!!... LEFT DRAG');
            // console.log('FALLING IN REGION: ', localStorageRegion);
            // deleteBoundary();
            overlapBoundaryStarts.push(localStorageRegion.start);
        }
        else if ((localStorageRegion.start > region.start &&
            localStorageRegion.start < region.end) &&
            (localStorageRegion.end > region.start &&
                localStorageRegion.end < region.end)) {
            // console.log(region.start, localStorageRegion.end);
            // console.log(region.end, localStorageRegion.start);
            // console.log('OVERLAP!!!');
            // console.log('FALLING IN REGION COMPLETE OERLAP: ', localStorageRegion);
            alert("This new region is completely covering the other regions. DELETING new region.");
            deleteBoundary(region.id);
            break;
            // let dltBoundary = confirm("OK will delete the overlap boungary")
            // if (dltBoundary) {
            //     deleteBoundary();
            // }
            // else {
            //     window.location.reload();
            // }

        }
    }
    if (overlapBoundaryStarts.length) {
        closestBoundary(region, overlapBoundaryStarts, dragDirection = 'left')
    }
    if (overlapBoundaryEnds.length) {
        closestBoundary(region, overlapBoundaryEnds, dragDirection = 'right')
    }
}

$('#myMakeBoundaryModalButton').on('click', function (e) {
    //   alert("Opened!")
    activeSpeaker = document.getElementById("speakeridsdropdown").value;
    filename = document.getElementById("audioFilename").textContent;
    audioDuration = document.getElementById("currentaudioduration").textContent;
    // alert(audioDuration) 
    document.getElementById("makeboundaryspeakeriduploaddropdown").value = activeSpeaker;
    document.getElementById("makeboundaryaudiofileid").value = filename
    document.getElementById("makeboundaryaudiodurationid").value = audioDuration
    // document.getElementById("speakeriduploaddropdown-divid").innerHTML = activeSpeaker;
    $('#myMakeBoundaryModal').show.bs.modal;

})

$('#editAudioSettingsButton').on('click', function (e) {
    //   alert("Opened!")
    filename = document.getElementById("audioFilename").textContent;

    document.getElementById("settingsaudiofileid").value = filename

    // document.getElementById("speakeriduploaddropdown-divid").innerHTML = activeSpeaker;
    // $('#editAudioSettingsModal').show.bs.modal;

})

function getScriptToGlossDropdownSelected() {
    return $('#scripttoglossdropdown').select2('data')[0].id;
}

function transcriptionToGloss() {
    // console.log($('#scripttoglossdropdown').select2('data'));
    // console.log($('#scripttoglossdropdown').select2('data')[0].id);
    let activeprojectform = JSON.parse(localStorage.activeprojectform);
    let boundaryID = document.getElementById('activeBoundaryID').value;
    let additioanlTranscription = [];
    if ('Additional Transcription' in activeprojectform) {
        additioanlTranscription = Object.keys(activeprojectform['Additional Transcription'][1]);
    }
    // console.log(additioanlTranscription);
    let transcriptionScriptList = activeprojectform['Transcription'][1];
    let transcriptionScriptDifference = transcriptionScriptList.filter(x => !additioanlTranscription.includes(x));
    // console.log(transcriptionScriptDifference);
    let transcriptionWordCountMismatch = {};
    for (let i=0; i<transcriptionScriptDifference.length; i++) {
        for (let j=i+1; j<transcriptionScriptDifference.length; j++) {
            // console.log(transcriptionScriptDifference[i], transcriptionScriptDifference[j])
            // console.log(document.getElementById('Transcription_'+transcriptionScriptDifference[i]).value)
            // console.log(document.getElementById('Transcription_'+transcriptionScriptDifference[j]).value)
            let iTranscriptionScript = transcriptionScriptDifference[i];
            let jTranscriptionScript = transcriptionScriptDifference[j];
            let iTranscription = document.getElementById('Transcription_'+iTranscriptionScript).value.trim().replace(/  +/g, ' ');
            let jTranscription = document.getElementById('Transcription_'+jTranscriptionScript).value.trim().replace(/  +/g, ' ');
            if (iTranscription !== '' && jTranscription !== '') {
                let iTranscriptionArray = iTranscription.split(" ");
                let jTranscriptionArray = jTranscription.split(" ");
                if (iTranscriptionArray.length !== jTranscriptionArray.length) {
                    transcriptionWordCountMismatch[iTranscriptionScript+'-'+jTranscriptionScript] = iTranscriptionArray.length+'-'+jTranscriptionArray.length
                }
            }
        }
    }
    // console.log(transcriptionWordCountMismatch);
    if (Object.keys(transcriptionWordCountMismatch).length) {
        alert('Number of words mismatch: \n'+JSON.stringify(transcriptionWordCountMismatch))
        return;
    }
    let scripttoglossdropdownselected = getScriptToGlossDropdownSelected();
    // console.log(scripttoglossdropdownselected);
    document.getElementById("interlinearglosstab").onclick = function () { transcriptionToGloss() };
    let sentencemorphemicbreakupdatedvalue = '';
    let localStorageRegions = JSON.parse(localStorage.regions);
    // let scriptName = ele.value;
    let scriptName = scripttoglossdropdownselected;
    for (let p = 0; p < localStorageRegions.length; p++) {
        // console.log(p);
        if (localStorageRegions[p]['boundaryID'] === boundaryID) {
            // console.log(p, boundaryID, scriptName);
            let sentence_morphemic_break = localStorageRegions[p]['data']['sentence'][boundaryID]['sentencemorphemicbreak'][scriptName];
            // console.log(sentence_morphemic_break);
            sentencemorphemicbreakupdatedvalue = sentence_morphemic_break;
            if (sentence_morphemic_break == '') {
                let transcription_in_script = localStorageRegions[p]['data']['sentence'][boundaryID]['transcription'][scriptName];
                // console.log(transcription_in_script);
                sentencemorphemicbreakupdatedvalue = transcription_in_script;
                break;
            }
            else {
                break;
            }
        }
    }
    // console.log(sentencemorphemicbreakupdatedvalue);
    let inpt = '';
    // inpt += '<input type="hidden" class="form-control" id="text"' + ' name="text" value="' + sentencemorphemicbreakupdatedvalue + '">' +
    //     '<textarea class="col form-control transcription-box textcontent"' +
    //     ' id="sentenceMorphemicBreak_' + scriptName + '"' +
    //     ' name="morphsentenceMorphemicBreak_' + scriptName + '"' +
    //     ' oninput="autoSavetranscription(event,this,true,\'sentenceMorphemicBreak_\')"' +
    //     ' ondblclick=tokenAnnotation(event)>' + sentencemorphemicbreakupdatedvalue + '</textarea>';
    // console.log("Interlinear Gloss" in activeprojectform);
    // console.log("Interlinear Gloss Format" in activeprojectform["Interlinear Gloss"]);
    // console.log("Customize Gloss" in activeprojectform["Interlinear Gloss"]);
    let interlinearGlossFormat = "";
    let customizeGloss = [];
    if ("Interlinear Gloss" in activeprojectform) {
        let interlinearglossforminfo = interlinearGlossFormInfo(activeprojectform);
        interlinearGlossFormat = interlinearglossforminfo.interlinearGlossFormat;
        customizeGloss = interlinearglossforminfo.customizeGloss;
    }
    // if (sentencemorphemicbreakupdatedvalue !== '') {
    returnInfo = createGlossingTable(sentencemorphemicbreakupdatedvalue,
                                interlinearGlossFormat,
                                customizeGloss);
    // console.log(returnInfo);
    inpt += returnInfo.inpt;
    // }
    // $('.textcontentouter').html(inpt);
    $('#interlinearglosscontainer').html(inpt);
    // if (sentencemorphemicbreakupdatedvalue !== '') {
    // console.log(returnInfo.jsonFileNames);
    getSelect2Data(getSelect2DataLocal(returnInfo.jsonFileNames));
    select2Multiselect();
    // autoSavetranscriptionSubPart();
    // }
}

function interlinearGlossFormInfo(activeprojectform) {
    let interlinearGlossFormat = "";
    let customizeGloss = [];
    if ("Interlinear Gloss Format" in activeprojectform["Interlinear Gloss"][1]) {
        interlinearGlossFormat = activeprojectform["Interlinear Gloss"][1]["Interlinear Gloss Format"][0];
    }
    if ("Customize Gloss" in activeprojectform["Interlinear Gloss"][1]) {
        customizeGloss = activeprojectform["Interlinear Gloss"][1]["Customize Gloss"];
    }

    return {
        interlinearGlossFormat: interlinearGlossFormat,
        customizeGloss: customizeGloss
    }
}


function morphemeFieldsSelect2() {
    let jsonFileNames = {
        morphemicGloss: "select2_morphemic_gloss.json",
        //   morphType: "select2_morpheme_type.json",
        //   posCategories: "select2_pos_categories.json"
    }
    var morphemicGloss = "";
    // var morphType = "";
    // var posCategories = "";
    $.ajax({
        url: '/get_jsonfile_data',
        type: 'GET',
        data: { 'data': JSON.stringify(jsonFileNames) },
        contentType: "application/json; charset=utf-8",
        success: function (response) {
            morphemicGloss = response.jsonData.morphemicGloss;
            // morphType = response.jsonData.morphType;
            // posCategories = response.jsonData.posCategories;
            // console.log(morphemicGloss);
            // console.log('.morphemicgloss'+ name +(i+1))
            // for(let i = 0; i < morphemicSplitSentence.length; i++) {
            $('#tokenannotationtagset').select2({
                tags: true,
                placeholder: 'Gloss',
                data: morphemicGloss,
                allowClear: true
            });

            //   $('.lextype'+ name +(i+1)).select2({
            //     tags: true,
            //     placeholder: 'Morph Type',
            //     data: morphType
            //     // allowClear: true
            //   });

            //   $('.pos'+ name +(i+1)).select2({
            //     tags: true,
            //     placeholder: 'POS',
            //     data: posCategories
            //     // allowClear: true
            //   });
            // }
            // autoSavetranscriptionSubPart();
        }
    });
}

function textSpanId(spanStart, spanEnd) {
    let maxSpanLength = 7;
    // console.log(spanStart, spanEnd);
    spanStart = String(spanStart);
    spanEnd = String(spanEnd);
    let spanStartLength = spanStart.length;
    let spanEndLength = spanEnd.length;
    // console.log(spanStartLength, spanEndLength);
    while (spanStartLength != maxSpanLength) {
        spanStart = '0' + spanStart;
        spanStartLength = spanStart.length;
    }
    while (spanEndLength != maxSpanLength) {
        spanEnd = '0' + spanEnd;
        spanEndLength = spanEnd.length;
    }
    // console.log(spanStartLength, spanEndLength);
    spanId = spanStart + spanEnd;

    // console.log(spanId);

    return spanId;
}

function leftModalForm(selection, spanStart, spanEnd, eleId) {
    // console.log(selection, spanStart, spanEnd, eleId);
    let leftModalData = '';
    // let lastActiveId = document.getElementById("lastActiveId").value;
    let spanId = textSpanId(spanStart, spanEnd);
    // console.log(eleValue, selection, spanStart, spanEnd, eleId);
    // leftModalData += '<input type="hidden" id="lastActiveId" name="lastActiveId" value="' + lastActiveId + '">';
    leftModalData += '<input type="hidden" id="tokenModalHeader"' + ' name="tokenModalHeader" value="' + eleId + '">';
    // leftModalData += '<label for="spanStart">Span Start</label>'+
    leftModalData += '<input type="hidden" class="form-control" id="tokenStart" name="tokenstartindex" value=' + spanStart + ' readonly>';
    // leftModalData += '<br>';
    // leftModalData += '<label for="spanEnd">Span End</label>'+
    leftModalData += '<input type="hidden" class="form-control" id="tokenEnd" name="tokenendindex" value=' + spanEnd + ' readonly>';
    // leftModalData += '<br>';
    // leftModalData += '<p class="form-group" id="' + spanId + '"><strong>Text Span ID: ' + spanId + '</strong></p>';
    // leftModalData += '<label for="spanId">Text Span ID</label>'+
    leftModalData += '<input type="hidden" class="form-control" id="tokenId" name="tokenId" value=' + spanId + ' readonly>';
    // leftModalData += '<br>';
    // '<div class="form-group textcontentouter">' +
    // leftModalData += '<label class="col" for="spantextcontent">Text:</label><br>'+
    //                 // '<svg viewBox="0 0 240 80" xmlns="http://www.w3.org/2000/svg">'+
    //                 // '<textarea class="modaltextcontent" id="spantextcontent" name="textspan" onselect=spanAnnotation(this,"'+eleId+'") readonly>' + selection + '</textarea>';
    //                 '<textarea class="modaltextcontent" id="spantextcontent" name="textspan" readonly>' + selection + '</textarea>';

    leftModalData += '<select id="tokenannotationtagset" multiple="multiple" style="width: 100%; display: block;"></select>';

    // console.log(leftModalData);
    $('#modalleft').html(leftModalData);
    morphemeFieldsSelect2();
}

function tokenAnnotationModal() {
    let tokenAnnotationData = '';
    // tokenAnnotationData += '<form name="savetextannospan" id="idsavetextannospanform" class="form-horizontal" action="/easyAnno/savetextAnnoSpan" method="POST"  enctype="multipart/form-data">';
    tokenAnnotationData += '<div class="col-sm-12"  id="modalleft">';
    tokenAnnotationData += '</div>' // left col div

    // tokenAnnotationData += '<div class="col-md-4"  id="modalmiddle">';
    // tokenAnnotationData += '';
    // tokenAnnotationData += '</div>' // right col div

    // tokenAnnotationData+= '<div class="col-sm-2" id="modalright">';
    // tokenAnnotationData += '<button type="button" class="btn btn-danger" data-dismiss="modal" id="'+key+'deleteSpan" onclick="deleteSpanModal(this.id)">'+
    //                         '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>'+
    //                         '</button>';
    // tokenAnnotationData += '<button type="button"  id="modalrightsavebtn" class="btn btn btn-primary"  data-dismiss="modal" onclick="spanSave(this)">'+
    //                         '<span class="glyphicon glyphicon-floppy-open" aria-hidden="true"></span>'+
    //                         '</button>';
    // tokenAnnotationData += '</div>'; //right div close

    // tokenAnnotationData += '</form>';

    return tokenAnnotationData;
}

function addModalElement(key) {
    let modalEle = ''
    modalEle += '<div class="modal fade" id="' + key + 'Modal" tabindex="-1" role="dialog" aria-labelledby="' + key + 'ModalLabel">' +
        '<div class="modal-dialog">' +
        '<div class="modal-content">' +
        // '<div class="row modal-header">'+
        // '<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>'+

        // // '<h4 class="modal-title" id="'+key+'ModalLabel">'+key+'</h4>'+
        // '</div>'+
        '<div class="modal-body" style="width: 100%;text-align: center">' +
        '<button type="button" class="btn btn-sm btn-danger pull-left" data-dismiss="modal" id="' + key + 'deleteSpan" onclick="deleteSpanModal(this.id)">' +
        '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>' +
        '</button>' +
        '<button type="button"  id="modalrightsavebtn" class="btn btn-sm btn-primary pull-left"  data-dismiss="modal" onclick="autoSavetranscriptionSubPart()">' +
        '<span class="glyphicon glyphicon-floppy-open" aria-hidden="true"></span>' +
        '</button>' +
        '<span style="font-size: 20px;">' + key + '</span>' +
        '<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
        '<div class="row" id="' + key + '_modal_data">' +
        '</div>' +
        '</div>' +
        // '<div class="modal-footer">'+
        // // '<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>'+
        // '<button type="button" class="btn btn-sm btn-danger pull-left" data-dismiss="modal" id="'+key+'deleteSpan" onclick="deleteSpanModal(this.id)">'+
        //         '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>'+
        //         '</button>'+
        // '<button type="button"  id="modalrightsavebtn" class="btn btn-sm btn-primary"  data-dismiss="modal" onclick="spanSave(this)">'+
        //         '<span class="glyphicon glyphicon-floppy-open" aria-hidden="true"></span>'+
        //         '</button>'+
        // '</div>'+
        '</div>' +
        '</div>' +
        '</div>';

    return modalEle;
}

function tokenAnnotation(event) {
    eve = event.target;
    // console.log(event, eve);
    event.bubbles = false;
    const spanStart = eve.selectionStart;
    const spanEnd = eve.selectionEnd;
    const selection = eve.value.substring(
        spanStart,
        spanEnd
    );
    // console.log(selection);
    let createModal = addModalElement(selection);
    $('#idmodal').html(createModal);
    let modalData = tokenAnnotationModal();
    $('#' + selection + '_modal_data').html(modalData);
    leftModalForm(selection, spanStart, spanEnd, selection)
    $('#' + selection + 'Modal').modal('toggle');
    $('#' + selection + 'Modal').on('hidden.bs.modal', function () {
        // $('#tokenannotationtagset').select2('destroy');
        // $('#tokenannotationtagset').val('');
        // $('#tokenannotationtagset').trigger('change');
        $('#idmodal').html('');
    });

    let tokenGlossArray = [];
    let localStorageRegions = JSON.parse(localStorage.regions);
    let scriptName = eve.id.split('_')[1];
    let boundaryID = document.getElementById('activeBoundaryID').value;
    let tokenId = textSpanId(spanStart, spanEnd);
    // console.log(scriptName);
    for (let p = 0; p < localStorageRegions.length; p++) {
        if (localStorageRegions[p]['boundaryID'] === boundaryID) {
            try {
                tokenGloss = localStorageRegions[p]['data']['sentence'][boundaryID]['gloss'][scriptName][tokenId]['tokenGloss'];
                // console.log(tokenGloss);
                if (tokenGloss !== '') {
                    let tokenGlossArray = tokenGloss.split('.');
                    // console.log(tokenGlossArray);
                    // $('#tokenannotationtagset').val(tokenGlossArray);
                    // $('#tokenannotationtagset').trigger('change');
                    // console.log(tokenGlossArray,tokenGlossArray.length);
                    let selectedGlossInfo = ''
                    for (let p=0; p<tokenGlossArray.length; p++) {
                        console.log(selectedGlossInfo);
                        let optionValue = tokenGlossArray[p];
                        selectedGlossInfo += '<option value="' + optionValue + '" selected>' + optionValue + '</option>';
                    }
                    $('#tokenannotationtagset').append(selectedGlossInfo);
                    // console.log(selectedGlossInfo);
                }
                break;
            }
            catch {
                continue
            }
        }
    }
}

function createGlossingTable(sentencemorphemicbreakupdatedvalue,
                                interlinearGlossFormat,
                                customizeGloss) {
    // console.log(sentencemorphemicbreakupdatedvalue,
    //     interlinearGlossFormat,
    //     customizeGloss);
    let colorPallet = ['bg-success', 'bg-warning', 'bg-danger', 'bg-info']
    let tokenIdObject = generateTokenId(sentencemorphemicbreakupdatedvalue);
    // console.log(tokenIdObject);
    let inpt = '';
    let jsonFileNames = {};
    let tempJsonFileNames = {};
    // interlinearGlossFormat = 'ud';

    // inpt += sentencemorphemicbreakupdatedvalue;
    let sentencemorphemicbreakupdatedvalueArray = sentencemorphemicbreakupdatedvalue.trim().split(" ");
    let sentencemorphemicbreakupdatedvalueArrayLength = sentencemorphemicbreakupdatedvalueArray.length;
    inpt += '<p class="text-center text-info" style="display: block;">'+sentencemorphemicbreakupdatedvalue+'</p>';
    let colCount = $('#tokencolcount').select2('data')[0].id;
    if (sentencemorphemicbreakupdatedvalueArrayLength < colCount) {
        colCount = sentencemorphemicbreakupdatedvalueArrayLength;
        $('#tokencolcount').val(colCount);
        $('#tokencolcount').trigger("change");
    }
    let eachColLength = Math.floor(12/colCount);
    let headArray = [];
    for (let m=0; m<=sentencemorphemicbreakupdatedvalueArrayLength; m++) {
        headArray.push(m);
    }
    // console.log(headArray);
    localStorage.setItem('head', JSON.stringify(headArray));
    // console.log(eachColLength);
    // console.log(sentencemorphemicbreakupdatedvalueArrayLength);
    // console.log(Math.ceil(sentencemorphemicbreakupdatedvalueArrayLength/colCount));
    let rowCount = Math.ceil(sentencemorphemicbreakupdatedvalueArrayLength/colCount);
    let i=0;
    let j=1;
    let glossTokenIdInfo = getGlossTokenIdInfo();
    // console.log(glossTokenIdInfo)
    if (sentencemorphemicbreakupdatedvalue !== '') {
        for (i=1; i<=rowCount; i++) {
            inpt += '<hr><div class="row" style="overflow-wrap:break-word;">';
            for (j=j; j<=colCount*i; j++) {
                // console.log(j);
                if (j<=sentencemorphemicbreakupdatedvalueArrayLength) {
                    let tokenId = tokenIdObject[j-1];
                    // let word = sentencemorphemicbreakupdatedvalueArray[j-1];
                    let word = sentencemorphemicbreakupdatedvalueArray[j-1];
                    // console.log(word);
                    // console.log(j);
                    inpt += '<div class="col-sm-'+eachColLength+' '+colorPallet[j%colorPallet.length]+'">';
                    if (!interlinearGlossFormat.includes('Leipzig')) {
                        inpt += '<center>'+j+'</center>';
                        inpt += '<input type="text" id="'+tokenId+'_word_input" class="'+tokenId+'_word_class form-control" value="'+word+'" readonly style="border: none;"><br>';
                    }
                    // inpt += '<div id="'+tokenId+'_word" class="'+tokenId+'_word_class" contenteditable="true" oninput="morphemicBreak(event,this)">'+word+'</div><br>';
                    // inpt += '<input type="hidden" id="'+tokenId+'_word_input" class="'+tokenId+'_word_class" value="'+word+'">';
                    if (interlinearGlossFormat.includes('Leipzig')) {
                        if (customizeGloss.includes('ID') ||
                            customizeGloss.includes('HEAD')) {
                            // inpt += j;
                            inpt += '<center>'+j+'</center>';
                        }
                        tempJsonFileNames['leipzig_glossing'] = 'select2_leipzig_glossing.json';
                        let tokenGlossArray = '';
                        let wordTranslationVal = '_';
                        let inptOption = '';
                        if (tokenId in glossTokenIdInfo &&
                            'gloss' in glossTokenIdInfo[tokenId]) {
                            tokenGlossArray = glossTokenIdInfo[tokenId]['gloss'];
                            // console.log(tokenGlossArray);
                            if (!(tokenGlossArray === '')) {
                                tokenGlossArray = glossTokenIdInfo[tokenId]['gloss'].split('.');
                                wordTranslationVal = tokenGlossArray[0];
                                // console.log(tokenGlossArray[0], tokenGlossArray.slice(1,));
                                inptOption = fillGlossedTokenInfo(tempJsonFileNames, tokenGlossArray.slice(1,));
                            }
                        }
                        tempJsonFileNames = {}
                        inpt += '<input type="text" id="'+tokenId+'_word_input" class="'+tokenId+'_word_class form-control" value="'+word+'" oninput="morphemicBreak(event,this)" style="border: none;"><br>';
                        inpt += '<input type="text" id="'+tokenId+'_word_translation"'+
                                'class="'+tokenId+'_word_translation_class form-control"'+
                                'value="'+wordTranslationVal+'"'+
                                'oninput="autoSavetranscription(event,this)"><br>';
                        inpt += '<select id="'+tokenId+'_gloss" class="leipzig_glossing"'+
                                ' oninput="autoSavetranscription(event,this)"' +
                                ' multiple="multiple" style="width: 100%;">';
                        inpt += inptOption;
                        inpt += '</select>';
                        inpt += '<br><br>';
                        jsonFileNames['leipzig_glossing'] = 'select2_leipzig_glossing.json';
                    }
                    for (let p=0; p<customizeGloss.length; p++) {
                        let field = customizeGloss[p].toLowerCase();
                        // console.log(field);
                        // let fieldBgColor = colorPallet[p%colorPallet.length];
                        // console.log(fieldBgColor);
                        let tokenGlossVal = '';
                        if (tokenId in glossTokenIdInfo &&
                            field in glossTokenIdInfo[tokenId]) {
                            tokenGlossVal = glossTokenIdInfo[tokenId][field];
                        }
                        // console.log(tokenGlossVal);
                        if (field === 'id' ||
                            field === 'form') {
                            continue;
                        }
                        else if (field === 'lemma') {
                            // console.log(tokenGlossVal);
                            inpt += '<input type="text" id="'+tokenId+'_'+field+'"'+
                                    ' class="'+field+' form-control" value="'+tokenGlossVal+'"'+
                                    ' oninput="autoSavetranscription(event,this)"' +
                                    ' placeholder="'+field+'"><br>';
                        }
                        else if (field === 'head') {
                            inpt += '<select id="'+tokenId+'_'+field+'" class="'+field+'"'+
                                    ' oninput="autoSavetranscription(event,this)"' +
                                    ' multiple="multiple" style="width: 100%;">';
                                    tempJsonFileNames[field] = 'select2_'+field+'.json';
                                    if (!(tokenGlossVal === '')) {
                                        // console.log(tokenGlossVal);
                                        inpt += fillGlossedTokenInfo(tempJsonFileNames, [tokenGlossVal]);
                                    }
                                    tempJsonFileNames = {}
                                    inpt += '</select><br><br>';
                                    jsonFileNames[field] = 'select2_'+field+'.json';
                        }
                        else if (field === 'feats') {
                            inpt += '<select id="'+tokenId+'_'+field+'" class="'+field+'"'+
                                    ' oninput="autoSavetranscription(event,this)"' +
                                    ' multiple="multiple" style="width: 100%;">';
                                    tempJsonFileNames[field] = 'select2_'+field+'.json';
                                    // console.log(tokenGlossVal);
                                    if (!(tokenGlossVal === '')) {
                                        tokenGlossVal = tokenGlossVal.split('|');
                                        // console.log(tokenGlossVal);
                                        inpt += fillGlossedTokenInfo(tempJsonFileNames, tokenGlossVal);
                                    }
                                    tempJsonFileNames = {}
                                    inpt += '</select><br><br>';
                                    jsonFileNames[field] = 'select2_'+field+'.json';
                        }
                        else {
                            inpt += '<select id="'+tokenId+'_'+field+'" class="'+field+'"'+
                                    ' oninput="autoSavetranscription(event,this)"' +
                                    ' multiple="multiple" style="width: 100%;">';
                            tempJsonFileNames[field] = 'select2_'+field+'.json';
                            if (!(tokenGlossVal === '')) {
                                inpt += fillGlossedTokenInfo(tempJsonFileNames, [tokenGlossVal]);
                            }
                            tempJsonFileNames = {}
                            inpt += '</select><br><br>';
                            jsonFileNames[field] = 'select2_'+field+'.json';
                        }
                    }
                    inpt += '</div>'; // column div
                }
            }
            // j = j-1;
            // inpt += '<div class="clearfix visible-sm-block"></div>';
            inpt += '</div>'; //row div
        }
        // getSelect2Data(getSelect2DataLocal(jsonFileNames));
    }

    return {
        inpt: inpt,
        jsonFileNames: jsonFileNames
    }
}

function select2Multiselect() {
    // partial solution to the select2 multiselect
    $("select").on("select2:select", function (evt) {
      var element = evt.params.data.element;
      // console.log(element);
      var $element = $(element);
      $element.detach();
      $(this).append($element);
      $(this).trigger("change");
    });
  }

function getSelect2DataLocal(jsonFileNames) {
    // console.log(jsonFileNames);
    let jsonFileNamesKeysList = Object.keys(jsonFileNames);
    // console.log(jsonFileNamesKeysList);
    for (let i=0; i<jsonFileNamesKeysList.length; i++) {
        let tags = false;
        let select2ClassName = jsonFileNamesKeysList[i];
        if (select2ClassName.includes('leipzig')) {
            tags = true;
        }
        if (select2ClassName === 'languages') {
            data = getInfoFromprojectForm('Audio Language')[1];
        }
        // console.log(select2ClassName);
        try {
            let data = JSON.parse(localStorage[select2ClassName]);
            // console.log(select2ClassName, data);
            // console.log(typeof data);
            $('.'+select2ClassName).select2({
                tags: tags,
                placeholder: select2ClassName,
                data: data,
                // allowClear: true
            });
            delete jsonFileNames[select2ClassName];
        }
        catch {
            continue;
        }
    }
    // console.log(jsonFileNames);
    return jsonFileNames;
}

function morphemicBreak(e, ele) {
    // console.log(e, ele);
    eleById = document.getElementById(ele.id);
    // console.log(eleById, eleById.value);
    let morphemicBreakSymbols = ['-'];
    let data = e.data;
    // console.log(data);
    let oldWord = e.target.defaultValue;
    let currentWord = e.target.value;
    let selectionEnd = e.target.selectionEnd;
    let updatedWord = '';
    // console.log(selectionEnd);
    // console.log(oldWord,
    //     currentWord);
    // console.log(currentWord[selectionEnd-2],
    //     currentWord,
    // currentWord[selectionEnd]);
    // console.log(oldWord[selectionEnd]);
    if (data === null) {
        if (morphemicBreakSymbols.includes(oldWord[selectionEnd])) {
            updatedWord = currentWord;
            // autoSavetranscriptionSubPart();
        }
        else {
            updatedWord = oldWord;
        }
    }
    else if (morphemicBreakSymbols.includes(data)) {
        // console.log('Allowed');
        if (morphemicBreakSymbols.includes(currentWord[selectionEnd - 2]) ||
                morphemicBreakSymbols.includes(currentWord[selectionEnd])) {
            updatedWord = oldWord;
                }
        else {
            updatedWord = currentWord;
        }
    }
    else if (!morphemicBreakSymbols.includes(data)) {
        updatedWord = oldWord;
    }
    // console.log(eleById, eleById.value, updatedWord);
    eleById.value = updatedWord;
    eleById.setAttribute("value", updatedWord);
    autoSavetranscriptionSubPart();
}

function generateTokenId(sentencemorphemicbreakupdatedvalue) {
    let tokenIdObject = {};
    let localStorageRegions = JSON.parse(localStorage.regions);
    let activeBoundaryID = document.getElementById('activeBoundaryID').value;
    for (let p = 0; p < localStorageRegions.length; p++) {
        // console.log(p);
        // console.log(localStorageRegions[p]['data']['sentence'][boundaryID])
        if (localStorageRegions[p]['data']['sentence'][boundaryID] &&
            localStorageRegions[p]['boundaryID'] === activeBoundaryID &&
            'glossTokenIdInfo' in localStorageRegions[p]['data']['sentence'][boundaryID]) {
            // console.log(localStorageRegions[p]['data']['sentence'][boundaryID])
            tokenIdObject = localStorageRegions[p]['data']['sentence'][boundaryID]['glossTokenIdInfo']

            if (Object.keys(tokenIdObject).length === 0) {
                // console.log('1')
                break;
            }
            else {
                // console.log('2')
                localStorage.setItem("glossTokenId", JSON.stringify(Object.keys(tokenIdObject)));
                return Object.keys(tokenIdObject);
            }
        }
    }
    // console.log(sentencemorphemicbreakupdatedvalue);
    // console.log(sentencemorphemicbreakupdatedvalue.trim().length);
    let sentencemorphemicbreakupdatedvalueArray = [];
    if (sentencemorphemicbreakupdatedvalue.trim().length !== 0) {
        sentencemorphemicbreakupdatedvalueArray = sentencemorphemicbreakupdatedvalue.trim().split(" ");
    }
    // console.log(sentencemorphemicbreakupdatedvalueArray);
    let tokenStart = 0;
    let tokenEnd = 0;
    let maxTokenLength = 7;
    let tokenId = '';
    let subSentenceLength = 0;
    for (let i=0; i<sentencemorphemicbreakupdatedvalueArray.length; i++) {
        let token = sentencemorphemicbreakupdatedvalueArray[i];
        tokenStart = tokenStart;
        tokenEnd = tokenStart+token.length-1;
        // console.log(token, tokenStart, tokenEnd);
        let tokenStartLength = String(tokenStart).length;
        let tokenEndLength = String(tokenEnd).length;
        while (tokenStartLength != maxTokenLength) {
            tokenStart = '0' + tokenStart;
            tokenStartLength = tokenStart.length;
        }
        while (tokenEndLength != maxTokenLength) {
            tokenEnd = '0' + tokenEnd;
            tokenEndLength = tokenEnd.length;
        }
        tokenId = tokenStart + tokenEnd;
        // console.log(tokenId);
        // tokenIdObject[tokenId] = token;
        tokenIdObject[tokenId] = {};
        subSentenceLength += token.length+1;
        tokenStart = subSentenceLength;
    }
    // console.log(tokenIdObject);
    localStorage.setItem("glossTokenId", JSON.stringify(Object.keys(tokenIdObject)));

    // console.log(Object.keys(tokenIdObject));

    return Object.keys(tokenIdObject);
}

function getSelect2Data(jsonFileNames) {
    // console.log(jsonFileNames);
    let jsonFileNamesKeysList = Object.keys(jsonFileNames);
    if (jsonFileNamesKeysList.length !== 0) {
        $.ajax({
            url: '/get_jsonfile_data',
            type: 'GET',
            data: {'data': JSON.stringify(jsonFileNames)},
            async: false,
            contentType: "application/json; charset=utf-8",
            success: function(response){
                // console.log(response);
                // console.log(jsonFileNamesKeysList);
                for (let i=0; i<jsonFileNamesKeysList.length; i++) {
                    let tags = false;
                    let select2ClassName = jsonFileNamesKeysList[i];
                    if (select2ClassName.includes('leipzig')) {
                        tags = true;
                    }
                    // console.log(select2ClassName);
                    let data = response.jsonData[select2ClassName];
                    if (select2ClassName === 'languages') {
                        data = getInfoFromprojectForm('Audio Language')[1];
                    }
                    // console.log(data);
                    // console.log(tags);
                    $('.'+select2ClassName).select2({
                        tags: tags,
                        placeholder: select2ClassName,
                        data: data,
                        // allowClear: true
                    });
                    // console.log(data);
                    localStorage.setItem(select2ClassName, JSON.stringify(data));
                }
            }
        });
    }
}

function getGlossTokenIdInfo() {
    let glossTokenIdInfo = {};
    let localStorageRegions = JSON.parse(localStorage.regions);
    let activeBoundaryID = document.getElementById('activeBoundaryID').value;
    for (let p = 0; p < localStorageRegions.length; p++) {
        // console.log(p);
        if (localStorageRegions[p]['data']['sentence'][boundaryID] &&
            localStorageRegions[p]['boundaryID'] === activeBoundaryID &&
            'glossTokenIdInfo' in localStorageRegions[p]['data']['sentence'][boundaryID]) {
            // console.log(localStorageRegions[p]['data']['sentence'][boundaryID])
            glossTokenIdInfo = localStorageRegions[p]['data']['sentence'][boundaryID]['glossTokenIdInfo']

            // return glossTokenIdInfo;
            break;
        }
    }
    return glossTokenIdInfo;
}

function mapSelect2IdText(jsonFileNames, id) {
    // console.log(jsonFileNames, id);
    var text = id;
    let jsonFileNamesKeysList = Object.keys(jsonFileNames);
    for (let i=0; i<jsonFileNamesKeysList.length; i++) {
        let select2ClassName = jsonFileNamesKeysList[i];
        // console.log(select2ClassName);
        try {
            let data = JSON.parse(localStorage[select2ClassName]);
            // console.log(select2ClassName, data);
            // console.log(typeof data);
            for (let p=0; p<data.length; p++) {
                let tempId = data[p]['id'];
                let tempText = data[p]['text'];
                // console.log(tempId, tempText);
                if (tempId === id) {
                    text = tempText;
                    // console.log(text);
                    // return text;
                    break;
                }
            }
            delete jsonFileNames[select2ClassName];
        }
        catch {
            continue;
        }
    }
    // console.log(jsonFileNames, id);
    if (Object.keys(jsonFileNames).length !== 0) {
        $.ajax({
            url: '/get_jsonfile_data',
            type: 'GET',
            data: {'data': JSON.stringify(jsonFileNames)},
            contentType: "application/json; charset=utf-8",
            async: false,
            success: function(response){
                // console.log(response);
                // console.log(jsonFileNamesKeysList);
                for (let i=0; i<jsonFileNamesKeysList.length; i++) {
                    let select2ClassName = jsonFileNamesKeysList[i];
                    // console.log(select2ClassName);
                    let data = response.jsonData[select2ClassName];
                    // console.log(data);
                    localStorage.setItem(select2ClassName, JSON.stringify(data));
                    for (let p=0; p<data.length; p++) {
                        let tempId = data[p]['id'];
                        let tempText = data[p]['text'];
                        // console.log(tempId, tempText);
                        if (tempId === id) {
                            text = tempText;
                            // console.log(text);
                            // return text;
                            break;
                        }
                    }
                }
            }
        });
    }
    // console.log(id, text);

    return text;
}

function fillGlossedTokenInfo(tempJsonFileNames, tokenGlossArray) {
    // console.log(tokenGlossArray);
    let selectedGlossInfo = ''
    for (let p=0; p<tokenGlossArray.length; p++) {
        // console.log(tempJsonFileNames);
        // console.log(selectedGlossInfo);
        let optionValue = tokenGlossArray[p];
        // console.log(optionValue, typeof optionValue);
        if (String(optionValue)) {
            let optionText = optionValue;
            if ('languages' in tempJsonFileNames ||
                'head' in tempJsonFileNames
            ) {
                optionText = optionValue
                // console.log(optionValue, typeof optionValue, optionText, typeof optionText);
            }
            else {
                let temp = JSON.parse(JSON.stringify(tempJsonFileNames));
                // console.log(temp === tempJsonFileNames);
                // console.log(temp, optionValue);
                optionText = mapSelect2IdText(temp, optionValue);
            }
            selectedGlossInfo += '<option value="' + optionValue + '" selected>' + optionText + '</option>';
        }
    }

    return selectedGlossInfo;
}

function getInfoFromprojectForm(keyName) {
    let activeprojectform = JSON.parse(localStorage.activeprojectform);
    let keyValue = activeprojectform[keyName];

    return keyValue;
}