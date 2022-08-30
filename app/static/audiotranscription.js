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

    // wavesurfer.util
    //     .fetchFile({
    //         responseType: 'json',
    //         url: 'rashomon.json'
    //     })
    //     .on('success', function(data) {
    //         wavesurfer.load(
    //             'http://www.archive.org/download/mshortworks_001_1202_librivox/msw001_03_rashomon_akutagawa_mt_64kb.mp3',
    //             data
    //         );
    //     });

    /* Regions */
    // localStorage.removeItem('regions');
    // localStorage.setItem("regions", JSON.stringify([]));
    filePath = JSON.parse(localStorage.getItem('AudioFilePath'));
    wavesurfer.load(filePath)
    wavesurfer.on('ready', function() {
        
        wavesurfer.enableDragSelection({
            color: randomColor(0.1)
        });

        if (localStorage.regions) {
            // console.log(localStorage.regions)
            loadRegions(JSON.parse(localStorage.regions));
        } else {
            // loadRegions(
            //     extractRegions(
            //         wavesurfer.backend.getPeaks(512),
            //         wavesurfer.getDuration()
            //     )
            // );
            fetch('annotations.json')
                .then(r => r.json())
                .then(data => {
                    loadRegions(data);
                    saveRegions();
                });
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
    wavesurfer.on('region-removed', saveRegions);
    wavesurfer.on('region-in', showNote);

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
        let form = document.forms.edit;
        let regionId = form.dataset.region;
        if (regionId) {
            wavesurfer.regions.list[regionId].remove();
            form.reset();
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
            // console.log(rid)
            return {
                boundaryID: rid,
                start: region.start,
                end: region.end,
                attributes: region.attributes,
                data: region.data
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
    console.log('editAnnotation(region)')
    // console.log(region)
    let form = document.forms.edit;
    transcriptionFormDisplay(form, 'edit');
    // form.style.opacity = 1;
    // (form.elements.start.value = Math.round(region.start * 10) / 10),
    // (form.elements.end.value = Math.round(region.end * 10) / 10);
    (form.elements.start.value = region.start),
    (form.elements.end.value = region.end);
    // form.elements.note.value = region.data.note || '';
    document.getElementById("activeSentenceMorphemicBreak").checked = false;
    $(".containerremovesentencefield1").remove();
    if (region.data.sentence) {
        createSentenceForm(form, region);
        // console.log('true true');
    }
    formOnSubmit(form, region)
    form.onreset = function() {
        // form.style.opacity = 0;
        transcriptionFormDisplay(form);
        form.dataset.region = null;
    };
    form.dataset.region = region.id;
}

// save partial transcription details
function formOnSubmit(form, region) {
    // console.log('formOnSubmit(form, region)', region)
    form.onsubmit = function(e) {
        e.preventDefault();
        // morphData = morphemeDetails();
        let sentenceData = new Object();
        if (region.data.sentence) {
            sentenceData = region.data.sentence
            sentData = sentenceDetails(sentenceData);
        }
        else {
            sentData = sentenceDetails(sentenceData);
        }
        // console.log(morphData);
        // $(".containerremovesentencefield1").remove();
        // document.getElementById("activeSentenceMorphemicBreak").checked = false;
        // rid = region.start.toFixed(2);
        region.update({
            start: form.elements.start.value,
            end: form.elements.end.value,
            data: {
                // note: form.elements.note.value,
                sentence: sentData
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
function showNote(region) {
    if (!showNote.el) {
        showNote.el = document.querySelector('#subtitle');
    }
    showNote.el.textContent = region.data.note || '–';
}

function sentenceDetails(sentenceData) {
    // console.log(sentenceData);
    // console.log(document.forms.edit.elements)
    formData = document.forms.edit.elements
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
                console.log(key, value.name, formData[eleName].value);

                if (ename.includes('Transcription') && !ename.includes('active')) {
                    console.log('!!!!!!!!!!!!!!!', key, value.name, formData[eleName].value);
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
                    console.log(key, value.name, formData[eleName].value);
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
    console.log('morphemeDetails!!!!!!!!!')
    morphemicBreakTranscription = morphemicBreakTranscription.replace('#', '').split(" ")
    morphemeData = mapArrays(actualTranscription, morphemicBreakTranscription)

    return morphemeData
    // console.log(morphemeData);
}

function glossDetails(morphCount, morphemeFor, formData, actualTranscription, morphemicBreakTranscription) {
    // console.log(actualTranscription, morphemicBreakTranscription)
    let glossData = new Object();
    for (i=1; i<=morphCount; i++) {
        let morpheme = ''
        let glossSubData = new Object();
        let lexgloss = ''
        let lextype = ''
        for (let [key, value] of Object.entries(formData)) {
            eleName = value.name;
            if (eleName.includes(i) &&
                eleName.includes(morphemeFor)) {
                // console.log(eleName);
                if (eleName.includes('morpheme')) {
                    morpheme = formData[eleName].value
                }
                else if (eleName.includes('gloss')) {
                    lexgloss = {
                        "eng-Latn": formData[eleName].value
                    }
                }
                else if (eleName.includes('lextype')) {
                    lextype = formData[eleName].value
                }
                // else if (eleName.includes('gloss')) {
                    
                // }
            }
        }
        // datetime = new Date()
        // console.log(datetime.toJSON());
        glossSubData[morpheme] = {
            'lexgloss': lexgloss,
            'lextype': lextype
        }
        console.log(glossSubData);
        if (morphemeIdMap[i] in glossData) {
            Object.assign(glossData[morphemeIdMap[i]], glossSubData)
        }
        else {
            glossData[morphemeIdMap[i]] = glossSubData
        }
    }
    console.log(glossData);

    return glossData
}

function morphemeidMap() {
    morphemicBreakTranscription = morphemicBreakTranscription.split(" ")
    glossDataMapping = mapArrays(actualTranscription, morphemicBreakTranscription)
    // console.log(glossDataMapping);
    // let glossData = new Object();
    let morphemeIdMap = new Object();
    mCount = 0;
    for (let [key, value] of Object.entries(glossDataMapping)) {
        // console.log(key, value);
        // let glossSubData = new Object();
        if (value.includes('#')) {
            v = value.replace('#', '').replace('-', '')
            value = value.split('#')
            for (i=0; i<value.length; i++) {
                // glossSubData[value[i]] = {}
                // glossData[key] = glossSubData
                mCount += 1
                morphemeIdMap[mCount] = v
            }
        }
        else {
            // glossSubData[value] = {}
            // glossData[key] = glossSubData
            mCount += 1
            morphemeIdMap[mCount] = value
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
         
     // Using the foreach method
     array_1.forEach((k, i) => {mappedData[k] = array_2[i]})
       return mappedData;
}

function createSentenceForm(form, region) {

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

$("#stopAudio").click(function() {
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