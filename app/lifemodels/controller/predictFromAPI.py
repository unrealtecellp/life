import requests
import json
import numpy as np
from huggingface_hub import InferenceClient
from transformers import pipeline

from app.controller import life_logging
from app.lifedata.transcription.controller.transcription_audiodetails import generate_boundary_id
from app.lifemodels.controller.predictFromLocalModels import get_transliteration

from sentencex import segment

import base64

logger = life_logging.get_logger()


def predictFromAPI(model_name, model_params):
    pass


def predictFromHFModel(model_inputs, model_url, hf_token, model_params={}, task='automatic-speech-recognition', script_names=['IPA']):
    # hf_token = input_data['hf_token']
    # task = model_params['task']
    # prediction = globals(
    # )['predict_'+task](model_params)
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
                logger.info('Ouptut from inference client %s',
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
                logger.info('Ouptut from inference client %s',
                            output)
            all_outputs[input_id] = {script_name: output}

            for other_script in other_scripts:
                if other_script == 'IPA':
                    source_script = lang_code
                else:
                    source_script = script_name
                script_transcript = get_transliteration(
                    output, source_script, other_script)
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
                        if other_script == 'IPA':
                            source_script = lang_code
                        else:
                            source_script = script_name
                        script_transcript = get_transliteration(
                            output, source_script, other_script)
                        all_outputs[boundary_id][other_script] = script_transcript
            else:
                all_outputs[input_id] = {script_name: output['text']}
                for other_script in other_scripts:
                    if other_script == 'IPA':
                        source_script = lang_code
                    else:
                        source_script = script_name
                    script_transcript = get_transliteration(
                        output, source_script, other_script)
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


def transcribe_data(audio_data):
    end_url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
    api_key = "A76bWGt9rowZFVQfsJmmgJDnriqa1CT14ECLdBjiGXHc93tP9rX72KfVmdwIAsDZ"
    header = {"Authorization": api_key}

    payload = {
        "pipelineTasks": [
            {
                "taskType": "asr",
                "config": {
                    "language": {
                            "sourceLanguage": "hi"
                    },
                    "serviceId": "ai4bharat/conformer-hi-gpu--t4",
                    "postProcessors": ["itn", "punctuation"]
                    # "audioFormat": "wav",
                    # "samplingRate": 16000
                }
            }
        ],
        "inputData": {
            # "input": [
            #     {
            #         "source": null
            #     }
            # ],
            "audio": [
                {
                    "audioContent": audio_data
                }
            ]
        }
    }
    transcript = requests.post(url=end_url, headers=header, json=payload)
    print(transcript)
    return transcript.json()


def predictFromBhashiniModel(model_inputs, model_url, model_params={}, script_names=['IPA'], max_retries=3):
    status = 0
    lang_code = model_params['language_code']
    all_outputs = {}
    script_name = script_names[0]
    if len(script_names) > 1:
        other_scripts = script_names[1:]
    else:
        other_scripts = []

    completed_count = 0
    retry_count = 0
    all_count = len(model_inputs)
    completed_ids = []

    while completed_count < all_count and retry_count < max_retries:
        retry_count += 1
        for input_id, model_input in model_inputs.items():
            if not input_id in completed_ids:
                model_input_str = base64.b64encode(model_input).decode('utf-8')
                print(retry_count, 'Input for', input_id)
                logger.info('Retry: %s\t Input ID: %s', retry_count, input_id)
                try:
                    transcript = transcribe_data(model_input_str)
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
                        if other_script == 'IPA':
                            source_script = lang_code
                        else:
                            source_script = script_name
                        script_transcript = get_transliteration(
                            output, source_script, other_script)
                        all_outputs[input_id][other_script] = script_transcript

        logger.info('Retry count: %s\tTotal completed: %s\tTotal to be completed: %s',
                    retry_count, completed_count, all_count)

    if completed_count == all_count:
        status = 1
    logger.info('ASR Output for file %s \tusing Bhashini (retries count: %s)',
                all_outputs, retry_count)

    return all_outputs, status
