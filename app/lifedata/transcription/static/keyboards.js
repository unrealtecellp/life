/*
For attaching keyman keyboards to any element -
1. Give "keyman-attached" as class to that element
2. Attach "updateKeyboard(this)" as onclick event
3. If you want to attach specific keyboards for specific elements then send those in newData and
capture in createKeyboards and add specific keyboard. Similarly add that in updateKeyboard to activate
correct keyboard
*/
scriptCode = {
    "Bengali": "Beng",
    "Devanagari": "Deva",
    "Gujarati": "Gujr",
    "Gurumukhi": "Guru",
    "IPA": "IPA",
    "Kannada": "Knda",
    "Latin": "Latn",
    "Malayalam": "Mlym",
    "Mayek": "Mtei",
    "Odia": "Orya",
    "Ol_Chiki": "Olck",
    "Tamil": "Taml",
    "Telugu": "Telu",
    "Toto": "Toto"
}

function createKeyboards(newData) {
    let itransScripts = ['bengali', 'gujarati', 'gurmukhi', 'odia']
    let audioLanguage = newData['Audio Language'][1][0]

    // console.log("Audio scripts", newData['Transcription'][1], newData['Transcription']);
    let currentScripts = newData['Transcription'][1];
    let currentTranslation = newData['Translation'][1];
    let currentTranslationScripts = Object.values(currentTranslation);
    currentScripts.push(currentTranslationScripts);
    // console.log("Translation scripts", currentTranslationScripts);

    let addedScripts = [];

    //   console.log("Final scripts", scripts);
    if (navigator.onLine) {

        (function (kmw) {
            // Keyboards are attached in "editAnnotation" function of "audiotranscriptions.js" after the sentence form is created on click
            kmw.init({ attachType: 'manual' }).then(function () {
                //  kmw.addKeyboards(scripts);
                //  kmw.addKeyboards('@en');basic_kbdinen

                try {
                    for (let i = 0; i < currentScripts.length; i++) {
                        let currentScript = currentScripts[i];
                        console.log('Adding', currentScript);

                        if (currentScript.includes('IPA')) {
                            kmw.addKeyboards('sil_ipa', '@und-fonipa');
                            addedScripts.push(currentScript);
                        }
                        else if (currentScript.includes('Devanagari')) {
                            kmw.addKeyboards('itrans_devanagari_hindi');
                            addedScripts.push(currentScript);
                        }
                        else if (itransScripts.includes(currentScript)) {
                            kmw.addKeyboards('itrans_' + currentScript);
                            addedScripts.push(currentScript);
                        }
                        else if (currentScript == 'Mayek') {
                            kmw.addKeyboards('meitei_legacy');
                            addedScripts.push(currentScript);
                        }
                    }
                    //  audioLanguage = 'Meitei';
                    console.log('Adding', audioLanguage);
                    if (currentScripts.length != addedScripts.length) {
                        kmw.addKeyboardsForLanguage(audioLanguage);
                    }

                    console.log('Adding Latin');
                    kmw.addKeyboards('basic_kbdinen');
                    if (currentScripts.includes('Latin')) {
                        addedScripts.push('Latin');
                    }
                }
                catch (err) {
                    document.getElementById("keymanStatus").innerHTML = err.message;
                }


                //  kmw.setActiveKeyboard('basic_kbddv', 'en');
                //  kmw.addKeyboards('meitei_legacy');

                // kmw.addKeyboards('@en'); // Loads default English keyboard from Keyman Cloud (CDN)
                // kmw.addKeyboards('@th'); // Loads default Thai keyboard from Keyman Cloud (CDN)
            });
        })(keyman);
    }
    else {
        alert('offline!');
    }
}

function updateKeyboard(e) {
    console.log('Clicked textarea for transcription', e.id);
    let itransScripts = ['bengali', 'gujarati', 'gurmukhi', 'odia']
    // keyman.attachToControl(e);
    elId = e.id;
    currentScriptIndex = elId.lastIndexOf('_') + 1;
    currentScript = elId.substring(currentScriptIndex).trim();

    console.log('Current script', currentScript);

    if (currentScript.includes('IPA')) {
        keyman.setActiveKeyboard('sil_ipa');
        // kmw.addKeyboards('@en', 'sil_ipa', '@und-fonipa');
        // addedScripts.push(currentScript);
    }
    else if (currentScript.includes('Devanagari')) {
        keyman.setActiveKeyboard('itrans_devanagari_hindi');
        // addedScripts.push(currentScript);
    }
    else if (itransScripts.includes(currentScript)) {
        keyman.setActiveKeyboard('itrans_' + currentScript);
        // addedScripts.push(currentScript);
    }
    else if (currentScript == 'Mayek') {
        keyman.setActiveKeyboard('meitei_legacy');
        // addedScripts.push(currentScript);
    }
    else if (currentScript == 'Latin') {
        keyman.setActiveKeyboard('basic_kbdinen');
        // addedScripts.push(currentScript);
    }
    else {
        keyman.setActiveKeyboard('basic_kbdinen');
    }
    // keyman.setActiveKeyboard('sil_ipa');


}

