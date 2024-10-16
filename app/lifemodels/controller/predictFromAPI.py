import torch
import torchaudio
import requests
import json
import numpy as np
from huggingface_hub import InferenceClient
from transformers import pipeline

from app.controller import life_logging
from app.lifedata.transcription.controller.transcription_audiodetails import generate_boundary_id
from app.lifemodels.controller.predictFromLocalModels import get_transliteration
from app.lifemodels.controller.bhashiniUtils import (
    transcribe_data,
    translate_data,
    get_translation_model,
    get_transcription_model,
    get_translation_model_from_id
)


from sentencex import segment

from pyannote.audio import Pipeline

import base64

# from pycountry import scripts

from isocodes import script_names as sn

logger = life_logging.get_logger()


def predictFromAPI(model_name, model_params):
    pass


def predictFromHFModel(model_inputs, model_url, hf_token, model_params={}, task='automatic-speech-recognition', script_names=['IPA']):
    # hf_token = input_data['hf_token']
    # task = model_params['task']
    # prediction = globals(
    # )['predict_'+task](model_params)
    model_lang_code = model_params['model_language_code']
    lang_code = model_params['language_code']
    all_outputs = {}
    inference_source = model_params['model_api']
    script_name = script_names[0]
    if len(script_names) > 1:
        other_scripts = script_names[1:]
    else:
        other_scripts = []

    if inference_source == 'hfinference':
        client = InferenceClient(token=hf_token)
        logger.debug('HF Token %s', hf_token)
        # logger.debug('Model Input %s', model_inputs)
        logger.debug('Model %s', model_url)
        for input_id, model_input in model_inputs.items():
            if task == 'automatic-speech-recognition':
                output = client.automatic_speech_recognition(
                    audio=model_input, model=model_url)
                logger.info('Output from inference client %s',
                            output)
            else:
                if isinstance(model_input, dict):
                    response = client.post(
                        data=model_input, model=model_url, task=task)
                else:
                    response = client.post(
                        json={"inputs": model_input, "parameters": model_params}, model=model_url, task=task)
                logger.info('Response from inference client %s',
                            response)
                output = json.loads(response.decode())
                logger.info('Output from inference client %s',
                            output)
            all_outputs[input_id] = {script_name: output}

            for other_script in other_scripts:
                source_script = script_name
                # if other_script == 'IPA':
                #     source_script = lang_code
                # else:
                #     source_script = script_name
                script_transcript = get_transliteration(
                    output, source_script, other_script, lang_code, model_lang_code)
                all_outputs[input_id][other_script] = script_transcript

    else:
        timestamp_level = model_params['boundary_level']
        # sentence_delim = model_params['sentence_delimiter']
        lang_code = model_params['language_code']
        if 'whisper' in model_url:
            # if timestamp_level == 'wordseg':
            #     timestamp_level = True
            if timestamp_level == 'character':
                timestamp_level = 'word'
        else:
            if timestamp_level == 'wordseg':
                timestamp_level = 'word'
            if timestamp_level == 'character':
                timestamp_level = 'char'

        # Needed because only word or char level is allowed in CTC model
        if timestamp_level == 'sentence':
            timestamp_level = 'word'

        # if timestamp_level == '':
        #     timestamp_level = 'sentence'

        if timestamp_level == '':
            transcriber = pipeline(task="automatic-speech-recognition",
                                   model=model_url)
        else:
            transcriber = pipeline(task="automatic-speech-recognition",
                                   model=model_url, return_timestamps=timestamp_level)

        outputs = transcriber(list(model_inputs.values()))
        for i, input_id in enumerate(list(model_inputs.keys())):
            output = outputs[i]
            if 'chunks' in output:
                # logger.debug('Output: %s', output)
                chunks = output['chunks']
                if timestamp_level == 'sentence':
                    full_text = output['text']
                    # all_sentences = full_text.split(sentence_delim)
                    all_sentences = list(segment(lang_code, full_text))
                    chunks = get_sentence_chunks(
                        all_sentences, chunks, lang_code)
                for chunk in chunks:
                    text = chunk['text']
                    boundary = {'start': chunk['timestamp']
                                [0], 'end': chunk['timestamp'][1]}
                    boundary_id = generate_boundary_id(boundary)
                    all_outputs[boundary_id] = {script_name: text}
                    all_outputs[boundary_id]['boundary'] = boundary
                    for other_script in other_scripts:
                        source_script = script_name
                        # if other_script == 'IPA':
                        #     source_script = lang_code
                        # else:
                        #     source_script = script_name
                        script_transcript = get_transliteration(
                            output, source_script, other_script, lang_code, model_lang_code)
                        all_outputs[boundary_id][other_script] = script_transcript
            else:
                all_outputs[input_id] = {script_name: output['text']}
                for other_script in other_scripts:
                    source_script = script_name
                    # if other_script == 'IPA':
                    #     source_script = lang_code
                    # else:
                    #     source_script = script_name
                    script_transcript = get_transliteration(
                        output, source_script, other_script, lang_code, model_lang_code)
                    all_outputs[input_id][other_script] = script_transcript

    logger.info('ASR Output for file %s \tusing model %s',
                all_outputs, model_url)

    return all_outputs


def get_sentence_chunks(all_sentences, chunks):
    new_chunks = []
    start_chunk = 0
    for i, current_sentence in enumerate(all_sentences):
        all_words = current_sentence.split(' ')
        current_sentence_chunks = chunks[start_chunk: len(all_words)]
        chunk_dict = {'text': current_sentence}
        chunk_dict['timestamp'] = tuple(
            current_sentence_chunks[0]['timestamp'][0], current_sentence_chunks[-1]['timestamp'][1])
        new_chunks.append(chunk_dict)
        return new_chunks


def transcribe_using_bhashini(model_inputs, model_url, model_params={}, script_names=['IPA'], max_retries=3):
    status = 0
    lang_code = model_params['language_code']
    model_lang_code = model_params['model_language_code']

    model, api_key, end_url, target_script = get_transcription_model(
        model_lang_code, model_url)

    all_outputs = {}

    # script_name = script_names[0]
    # script_code = sn.get(
    #     name=script_name).get("alpha_4", script_name)
    script_name = ''

    other_scripts = []

    logger.info('All script names %s', script_names)

    for current_script_name in script_names:
        if current_script_name == 'Latin':
            current_script_code = 'Latn'
        else:
            current_script_code = sn.get(
                name=current_script_name).get("alpha_4", current_script_name)
        logger.info('Current script name %s\tCurrent script code %s\tTarget Script %s',
                    current_script_name, current_script_code, target_script)
        if current_script_code == target_script:
            script_code = current_script_code
            script_name = current_script_name
        else:
            other_scripts.append(current_script_name)

    completed_count = 0
    retry_count = 0
    all_count = len(model_inputs)
    completed_ids = []

    logger.info('Model URL %s, %s', model, model_url)
    logger.info('Current Script: %s %s\tTarget Script %s \tOther Scripts %s \tLanguage %s \tModel Lang Code%s',
                script_name, script_code, target_script, other_scripts, lang_code, model_lang_code)

    if model != '' and target_script == script_code:
        while completed_count < all_count and retry_count < max_retries:
            retry_count += 1
            for input_id, model_input in model_inputs.items():
                if not input_id in completed_ids:
                    model_input_str = base64.b64encode(
                        model_input).decode('utf-8')
                    logger.info('%s Input for %s', retry_count, input_id)
                    print('%s Input for %s', retry_count, input_id)
                    logger.info('Retry: %s\t Input ID: %s',
                                retry_count, input_id)
                    try:
                        transcript = transcribe_data(
                            model_input_str, model, api_key, end_url, lang_code)
                        logger.info('Bhashini response %s', transcript)
                        output = transcript["pipelineResponse"][0]["output"][0]["source"]
                        completed_count += 1
                        completed_ids.append(input_id)
                    except:
                        logger.exception('')
                        output = ""

                    all_outputs[input_id] = {script_name: output}
                    if output != '':
                        for other_script in other_scripts:
                            source_script = script_name
                            # if other_script == 'IPA':
                            #     source_script = lang_code
                            # else:
                            #     source_script = script_name
                            script_transcript = get_transliteration(
                                output, source_script, other_script, lang_code, model_lang_code)
                            all_outputs[input_id][other_script] = script_transcript

            logger.info('Retry count: %s\tTotal completed: %s\tTotal to be completed: %s',
                        retry_count, completed_count, all_count)

        if completed_count == all_count:
            status = 1
        logger.info('ASR Output for file %s \tusing Bhashini (retries count: %s)',
                    all_outputs, retry_count)
    else:
        logger.info('Language: %s\t or Script: %s (supported: %s)\tnot supported in Bhashini',
                    lang_code, script_code, target_script)

    return all_outputs, status


def translate_using_bhashini(model_inputs, model_params={}, max_retries=3):
    status = 0

    target_lang_script = model_params['output_language']
    source_lang_code = model_params['source_language']
    source_script_code = model_params['source_script_code']
    target_lang_code = model_params['target_language']
    target_script_code = model_params['target_script']
    model_id = model_params['model_path']

    logger.info('Model ID %s', model_id)

    all_outputs = {}
    # model, api_key, end_url, source_script, target_script = get_translation_model(
    #     source_lang_code, target_lang_code)
    # model, api_key, end_url, source_script, target_script = get_translation_model_from_id(
    #     model_id)
    model, api_key, end_url = get_translation_model_from_id(
        model_id)
    logger.info('Retrieved Model ID %s', model)
    # logger.info('Model source script code %s \t Input source script code: %s',
    #             source_script, source_script_code)
    # logger.info('Model target script code %s \t Input target script code: %s',
    #             target_script, target_script_code)

    completed_count = 0
    retry_count = 0
    all_count = len(model_inputs)
    completed_ids = []

    # if model != '' and target_script_code == target_script and source_script_code == source_script:
    if model != '':
        while completed_count < all_count and retry_count < max_retries:
            retry_count += 1
            for input_id, model_input_str in model_inputs.items():
                if not input_id in completed_ids:
                    logger.info('%s Input for %s', retry_count, input_id)
                    print('%s Input for %s', retry_count, input_id)

                    logger.info('Retry: %s\t Input ID: %s',
                                retry_count, input_id)
                    try:
                        result = translate_data(
                            model_input_str, model, api_key, end_url, source_lang_code, target_lang_code)
                        logger.info('Bhashini response %s', result)
                        output = result["pipelineResponse"][0]["output"][0]["target"]
                        completed_count += 1
                        completed_ids.append(input_id)
                    except:
                        logger.exception('')
                        output = ""

                    all_outputs[input_id] = {target_lang_script: output}

            logger.info('Retry count: %s\tTotal completed: %s\tTotal to be completed: %s',
                        retry_count, completed_count, all_count)

        if completed_count == all_count:
            status = 1
        logger.info('ASR Output for file %s \tusing Bhashini (retries count: %s)',
                    all_outputs, retry_count)
    else:
        logger.info('Language: %s->%s\t or Script: %s->%s\tnot supported in Bhashini',
                    source_lang_code, target_lang_code, source_script_code, target_script_code)

    return all_outputs, status


def get_boundaries_pyannote(audio, hf_token, num_speakers=1):
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=hf_token)

    # send pipeline to GPU (when available)
    # pipeline.to(torch.device("cuda"))

    # apply pretrained pipeline
    waveform, sample_rate = torchaudio.load(audio)
    diarization = pipeline(
        {"waveform": waveform, "sample_rate": sample_rate}, num_speakers=num_speakers)

    # diarization = pipeline(audio)

    # print the result
    speech_timestamps = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
        info_dict = {'start': turn.start, 'end': turn.end, 'speaker': speaker}
        speech_timestamps.append(info_dict)

    return speech_timestamps, audio


if __name__ == '__main__':
    hf_token = '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'
    audio_path = '/home/ritesh/Downloads/cambridge_ud/SS_Eng_240424.WAV'
    get_boundaries_pyannote(audio_path, hf_token)
