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
    // let itransScripts = ['bengali', 'gujarati', 'gurmukhi', 'odia']
    let supportedKeyboards = {
        'bengali': {
            'fname': 'itrans_bengali-1.0.2.js',
            'version': '1.0.2',
            'langid': 'bn',
            'kbdid': 'itrans_bengali'
        },
        'gujarati': {
            'fname': 'itrans_gujarati-1.2.0.js',
            'version': '1.2.0',
            'langid': 'gu',
            'kbdid': 'itrans_gujarati'
        },
        'gurmukhi': {
            'fname': 'itrans_gurmukhi-1.0.0.js',
            'version': '1.0.0',
            'langid': 'gu',
            'kbdid': 'itrans_gurmukhi'
        },
        'odia': {
            'fname': 'itrans_odia-1.0.0.js',
            'version': '1.0.0',
            'langid': 'or',
            'kbdid': 'itrans_odia'
        },
        'Mayek': {
            'fname': 'meitei_legacy-0.1.js',
            'version': '0.1',
            'langid': 'or',
            'kbdid': 'meitei_legacy'
        },
        'toto': {
            'fname': 'txo_toto-1.0.1.js',
            'version': '1.0.1',
            'langid': 'txo',
            'kbdid': 'txo_toto'
        },
        'IPA': {
            'fname': 'sil_ipa-1.8.7.js',
            'version': '1.8.7',
            'langid': 'und-fonipa',
            'kbdid': 'sil_ipa'
        },
        'Devanagari': {
            'fname': 'itrans_devanagari_hindi-1.2.1.js',
            'version': '1.2.1',
            'langid': 'hi',
            'kbdid': 'itrans_devanagari_hindi'
        }
    }
    let audioLanguage = newData['Audio Language'][1][0]

    // console.log("Audio scripts", newData['Transcription'][1], newData['Transcription']);
    let currentScripts = newData['Transcription'][1];
    let currentTranslation = newData['Translation'][1];
    let currentTranslationScripts = Object.values(currentTranslation);
    currentScripts.push(currentTranslationScripts);
    // console.log("Translation scripts", currentTranslationScripts);

    // let addedScripts = [];

    //   console.log("Final scripts", scripts);
    // if (navigator.onLine) {

    (function (kmw) {
        // Keyboards are attached in "editAnnotation" function of "audiotranscriptions.js" after the sentence form is created on click
        kmw.init({ attachType: 'manual' }).then(function () {
            //  kmw.addKeyboards(scripts);
            //  kmw.addKeyboards('@en');basic_kbdinen            

            try {
                for (let i = 0; i < currentScripts.length; i++) {
                    let currentScript = currentScripts[i];
                    // console.log('Adding', currentScript);

                    if (currentScript in supportedKeyboards) {
                        // console.log('Supported keyboard', currentScript);
                        var currentKbdParams = supportedKeyboards[currentScript]
                        var currentKeyboard = {
                            name: currentScript,
                            id: currentKbdParams['kbdid'],
                            filename: 'static/keyboards/' + currentKbdParams['fname'],
                            version: currentKbdParams['version'],
                            language: [{
                                name: audioLanguage,
                                id: currentKbdParams['langid'],
                                region: 'global'
                            }]
                        }

                        kmw.addKeyboards(currentKeyboard);
                        // console.log('All keyboards', keyman.getKeyboards());
                    }

                    // if (currentScript.includes('IPA')) {
                    //     // kmw.addKeyboards('sil_ipa', '@und-fonipa');
                    //     kmw.addKeyboards(ipa_keyboard)
                    //     addedScripts.push(currentScript);
                    // }
                    // else if (currentScript.includes('Devanagari')) {
                    //     kmw.addKeyboards(deva_itrans_keyboard);
                    //     addedScripts.push(currentScript);
                    // }
                    // else if (itransScripts.includes(currentScript)) {
                    //     kmw.addKeyboards('itrans_' + currentScript);
                    //     addedScripts.push(currentScript);
                    // }
                    // else if (currentScript == 'Mayek') {
                    //     kmw.addKeyboards(meitei_keyboard);
                    //     addedScripts.push(currentScript);
                    // }
                }
                // console.log('Adding Latin');
                // kmw.addKeyboards('basic_kbdinen');
                // if (currentScripts.includes('Latin')) {
                //     addedScripts.push('Latin');
                // }

                //  audioLanguage = 'Meitei';
                // console.log('Adding', audioLanguage);
                // if (currentScripts.length != addedScripts.length) {
                //     kmw.addKeyboardsForLanguage(audioLanguage);
                // }
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
    // }
    // else {
    //     alert('offline!');
    // }
}

function updateKeyboard(e) {
    // console.log('Clicked textarea for transcription', e.id);
    let itransScripts = ['bengali', 'gujarati', 'gurmukhi', 'odia']
    // keyman.attachToControl(e);
    elId = e.id;
    currentScriptIndex = elId.lastIndexOf('_') + 1;
    currentScript = elId.substring(currentScriptIndex).trim();

    // console.log('Current script', currentScript);
    // console.log('All keyboard', keyman.getKeyboards());
    // keyman.setActiveKeyboard(currentScript);

    if (currentScript.includes('IPA')) {
        keyman.setActiveKeyboard('Keyboard_sil_ipa');
        // kmw.addKeyboards('@en', 'sil_ipa', '@und-fonipa');
        // addedScripts.push(currentScript);
    }
    else if (currentScript.includes('Devanagari')) {
        keyman.setActiveKeyboard('Keyboard_itrans_devanagari_hindi');
        // addedScripts.push(currentScript);
    }
    else if (itransScripts.includes(currentScript)) {
        keyman.setActiveKeyboard('Keyboard_itrans_' + currentScript);
        // addedScripts.push(currentScript);
    }
    else if (currentScript == 'Mayek') {
        keyman.setActiveKeyboard('Keyboard_meitei_legacy');
        // addedScripts.push(currentScript);
    }
    else if (currentScript == 'toto') {
        keyman.setActiveKeyboard('Keyboard_txo_toto');
        // addedScripts.push(currentScript);
    }
    // else if (currentScript == 'Latin') {
    //     keyman.setActiveKeyboard('basic_kbdinen');
    //     // addedScripts.push(currentScript);
    // }
    // else {
    //     keyman.setActiveKeyboard('basic_kbdinen');
    // }
    // keyman.setActiveKeyboard('sil_ipa');


}

