import torch
# from phonemizer.backend import EspeakBackend
# from phonemizer.separator import Separator
from app.lifemodels.controller.espeakIPA import to_ipa

from app.controller import life_logging
import pandas as pd
import os

import stanza
from stanza import DownloadMethod

torch.set_num_threads(8)

logger = life_logging.get_logger()

basedir = os.path.abspath(os.path.dirname(__file__))
basedir_parent = '/'.join(basedir.split('/')[:-1])

logger = life_logging.get_logger()
# logger.debug('Basedir parent', basedir_parent)
translit_res_path = os.path.join(
    basedir_parent, 'static/translit_resources')
print('Translit res path', translit_res_path)

stanza_pipelines = {
    'hi': stanza.Pipeline(
        'hi', download_method=DownloadMethod.REUSE_RESOURCES)
}


def get_boundaries(model_name, model_params):
    # effective_func = getattr()
    timestamps, cleaned_audio = globals(
    )['get_boundaries_'+model_name](model_params)
    # timestamps, cleaned_audio = effective_func()
    return timestamps, cleaned_audio


def get_transcription(model_name, **kwargs):
    transcription = globals()['get_transcription_'+model_name](**kwargs)
    return transcription


def get_transliteration(data, source_script, target_script, lang_code, **kwargs):
    if target_script == 'IPA':
        transcription_words = to_ipa(data.split(' '), lang_code=lang_code)
        transcription_words = [transcription_word.strip(
            '#') for transcription_word in transcription_words]
        logger.info('Data %s, IPA Transcription %s', data, transcription_words)
        transcription = ' '.join(transcription_words)
    else:
        all_functs = globals()
        current_funct_name = 'get_transliteration_'+source_script + '_to_'+target_script
        if current_funct_name in all_functs:
            transcription = globals()[current_funct_name](
                data, lang_code, **kwargs)
        else:
            transcription = ''
    return transcription

# This gets the timestamps of the parts of the audio with voice activity; also
# returns an audio after removing the pauses, if asked to


def get_boundaries_vadsilero(model_params):
    audio_file = model_params["audio_file"]
    SAMPLING_RATE = model_params["SAMPLING_RATE"]
    remove_pauses = model_params["remove_pauses"]
    USE_ONNX = model_params["USE_ONNX"]
    model_path = model_params['model_path']
    min_speech_duration = model_params['minimum_speech_duration']
    min_silence_duration = model_params['minimum_silence_duration']

    model, utils = torch.hub.load(repo_or_dir=model_path,
                                  model='silero_vad',
                                  force_reload=False,
                                  onnx=USE_ONNX)

    (get_speech_timestamps,
     save_audio,
     read_audio,
     VADIterator,
     collect_chunks) = utils

    wav = read_audio(audio_file, sampling_rate=SAMPLING_RATE)

    # get speech timestamps from full audio file
    speech_timestamps = get_speech_timestamps(
        wav, model, return_seconds=True, sampling_rate=SAMPLING_RATE, min_speech_duration_ms=min_speech_duration, min_silence_duration_ms=min_silence_duration)

    # TODO: implement this to save audio without pauses in MongoDB
    if remove_pauses:
        # wav = save_audio('only_speech.wav',
        #  collect_chunks(speech_timestamps, wav), sampling_rate=SAMPLING_RATE)
        wav = collect_chunks(speech_timestamps, wav)

    return speech_timestamps, wav


# Must return a list of transcriptions depending on the number of boundaries
def get_transcription_wav2vec2(model_params):
    transcriptions = {}
    audio_file = model_params["audio_file"]
    boundaries = model_params["boundaries"]
    model_path = model_params['model_path']
    # boundaries are a list of dictionaries with "start" and "end" as keys and their
    # values are the start and end position of boundary. The audio may be cropped using
    # this and individual boundaries may be autotranscribed
    return transcriptions


def load_ipa_to_char_mapping(target_char='rom'):
    fname = 'ipa-to-'+target_char+'.csv'
    fpath = os.path.join(translit_res_path, fname)
    df = pd.read_csv(fpath)
    df = df.fillna('')
    df['ipa'] = df['ipa'].str.replace("'", "")
    df[target_char] = df[target_char].str.split('/')
    ipa_character_map = dict(zip(df['ipa'], df[target_char]))
    return ipa_character_map


# def transliterate_Devanagari_to_Latin(text, ipa_transcript, ipa_character_map):
#     translit_n = 0
#     exception_chars = ['p:', 't:', 'k:']

#     def handle_exception_cons(trans_lemma, next_char):
#         if next_char == 'j':
#             return trans_lemma[:-1]
#         return trans_lemma

#     def handle_exception_vow(trans_lemma):
#         last_two_chars = trans_lemma[-2:]
#         if last_two_chars == 'aa':
#             return trans_lemma[:-1]
#         return trans_lemma

#     wordform = text.strip()
#     trans_lemma = ''

#     ipa_trans = ipa_transcript.strip().split(' ')

#     for i, cchar in enumerate(ipa_trans):
#         cchar = cchar.strip()

#         if i == len(ipa_trans)-1 and cchar == 'j' and wordform[-2:] == 'एँ':
#             cchar = 'ẽː'

#         ipa_chars = ipa_character_map.get(cchar, [''])
#         # print('IPA tranlit', ipa_chars)
#         ipa_char = ipa_chars[translit_n]
#         trans_lemma += ipa_char

#         if cchar in exception_chars:
#             trans_lemma = handle_exception_cons(trans_lemma, ipa_char[i+1])

#         if cchar == 'ɛ':
#             trans_lemma = handle_exception_vow(trans_lemma)

#     trans_lemma = trans_lemma.replace('nn', 'n')
#     trans_lemma = trans_lemma.lower()
#     if len(trans_lemma) > 1:
#         if trans_lemma[-1] == trans_lemma[-2]:
#             trans_lemma = trans_lemma[:-1]

#     return trans_lemma


def transliterate_IPA_to_Latin(text, ipa_transcript, ipa_character_map, lang_code):
    translit_n = 0
    exception_chars = ['p:', 't:', 'k:']
    skip_chars = ['ː', 'ʰ']
    skip_two_chars = ['̃']
    possible_dups = ['ɖ', 'ɖʰ', 'ʈʰ', 'ʈ']

    def handle_exception_cons_hin(trans_lemma, next_char):
        if next_char == 'j':
            return trans_lemma[:-1]
        return trans_lemma

    def handle_exception_vow_hin(trans_lemma):
        last_two_chars = trans_lemma[-2:]
        if last_two_chars == 'aa':
            return trans_lemma[:-1]
        return trans_lemma

    def handle_exception_ipa_hin(cchar, wordform):
        if cchar == 'j' and wordform[-2:] == 'एँ':
            cchar = 'ẽː'
        return cchar

    wordform = text.strip()
    trans_lemma = ''

    ipa_trans = ipa_transcript.strip()
    len_index = len(ipa_trans)-1

    cindex = 0
    for i in range(len(ipa_trans)):
        next_char_thresh = 1
        if cindex < len(ipa_trans):
            cchar = ipa_trans[cindex].strip()
            if cindex < len_index:
                next_char = ipa_trans[cindex+next_char_thresh]
                if next_char in skip_two_chars:
                    if (len_index-cindex) >= 2:
                        second_char = ipa_trans[cindex+2]
                        if second_char in skip_chars:
                            next_char += second_char
                            cindex += 1

                    cchar += next_char
                    cindex += 1
                if next_char in skip_chars:
                    cchar += next_char
                    cindex += 1
                    next_char_thresh = 2
                if (len_index-cindex) >= next_char_thresh:
                    if cchar in possible_dups:
                        next_char = ipa_trans[cindex:cindex+next_char_thresh+1]
                        if next_char == cchar:
                            cchar += next_char
                            cindex += next_char_thresh

            if cindex == len_index:
                if lang_code == 'hi' or lang_code == 'hin':
                    cchar = handle_exception_ipa_hin(cchar, wordform)

            ipa_chars = ipa_character_map.get(cchar, [cchar])
            # print('IPA tranlit', ipa_chars)
            ipa_char = ipa_chars[translit_n]
            trans_lemma += ipa_char

            if lang_code == 'hi' or lang_code == 'hin':
                if cchar in exception_chars:
                    trans_lemma = handle_exception_cons_hin(
                        trans_lemma, ipa_char[cindex+1])

                if cchar == 'ɛ':
                    trans_lemma = handle_exception_vow_hin(trans_lemma)

            cindex += 1

    if lang_code == 'hi' or lang_code == 'hin':
        trans_lemma = trans_lemma.replace('nn', 'n')
        if len(trans_lemma) > 1:
            if trans_lemma[-1] == trans_lemma[-2]:
                trans_lemma = trans_lemma[:-1]

    trans_lemma = trans_lemma.lower()

    return trans_lemma


def get_transliteration_IPA_to_Latin(data, lang_code, **kwargs):
    deva_supported_langs = ['hi', 'hin']
    ipa_words = data.split(' ')
    ipa_character_map = load_ipa_to_char_mapping()

    rom_words = []
    all_words = ['']*len(ipa_words)

    # logger.info('IPA words %s\n Length: %s', ipa_words,  len(ipa_words))

    for kwargs_key, kwargs_value in kwargs.items():
        if kwargs_key == 'other_transcripts':
            if lang_code in deva_supported_langs:
                if ('Devanagari' in kwargs_value):
                    transcript_val = kwargs_value['Devanagari']
                    if transcript_val.strip() != '':
                        all_words = transcript_val.split(' ')
    # logger.info('Devanagari words %s\n Length: %s', all_words,  len(all_words))
    for current_word, current_transcript in zip(all_words, ipa_words):
        rom_words.append(transliterate_IPA_to_Latin(
            current_word.strip(), current_transcript.strip(), ipa_character_map, lang_code))
    transcription = ' '.join(rom_words)

    return transcription


def get_transliteration_Devanagari_to_Latin(data, lang_code, **kwargs):
    all_words = data.split(' ')
    # ipa_words = to_ipa(all_words, phone_separator=' ', word_separator='\t',
    #                    lang_code=lang_code)
    ipa_words = to_ipa(all_words, lang_code=lang_code)
    ipa_words = [ipa_word.strip('#') for ipa_word in ipa_words]
    ipa_character_map = load_ipa_to_char_mapping()

    rom_words = []
    # logger.info('IPA words %s\n Length: %s', ipa_words,  len(ipa_words))
    # logger.info('Devanagari words %s\n Length: %s', all_words,  len(all_words))
    if lang_code == 'hi' or lang_code == 'hin' or lang_code == 'hindi':
        for current_word, current_transcript in zip(all_words, ipa_words):
            rom_words.append(transliterate_IPA_to_Latin(
                current_word.strip(), current_transcript.strip(), ipa_character_map, lang_code))
    transcription = ' '.join(rom_words)
    return transcription


def get_gloss_stanza(data, lang_code, **kwargs):
    nlp = stanza_pipelines.get(lang_code, '')
    all_outputs = {}
    try:
        # in_docs = [stanza.Document([], text=d) for d in data]

        if nlp != '':
            input_ids = data.keys()
            model_input_strs = list(data.values())
            results = nlp.bulk_process(model_input_strs)

            for input_id, result in zip(input_ids, results):
                logger.info('Input for %s', input_id)
                # logger.info('result %s', result)
                # logger.info('result.to_dict() %s', result.to_dict())
                output = result.to_dict()
                # logger.info('output %s', output)
                if (len(output) > 0):
                    output = output[0]
                else:
                    output = {}
                all_outputs[input_id] = output
    except:
        logger.exception("")

    return all_outputs
