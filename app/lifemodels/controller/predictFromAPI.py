import requests
import json
import numpy as np
from huggingface_hub import InferenceClient
from transformers import pipeline

from app.controller import life_logging
from app.lifedata.transcription.controller.transcription_audiodetails import generate_boundary_id

from sentencex import segment

logger = life_logging.get_logger()


def predictFromAPI(model_name, model_params):
    pass


def predictFromHFModel(model_inputs, model_url, hf_token, model_params={}, task='automatic-speech-recognition', script_name=''):
    # hf_token = input_data['hf_token']
    # task = model_params['task']
    # prediction = globals(
    # )['predict_'+task](model_params)
    all_outputs = {}
    inference_source = model_params['model_api']

    if inference_source == 'hfinference':
        client = InferenceClient(token=hf_token)
        logger.debug('HF Token %s', hf_token)
        # logger.debug('Model Input %s', model_inputs)
        logger.debug('Model %s', model_url)
        for input_id, model_input in model_inputs.items():
            if task == 'automatic-speech-recognition':
                output = client.automatic_speech_recognition(
                    audio=model_input, model=model_url,)
            else:
                if isinstance(model_input, dict):
                    response = client.post(
                        data=model_input, model=model_url, task=task)
                else:
                    response = client.post(
                        json={"inputs": model_input, "parameters": model_params}, model=model_url, task=task)
                output = json.loads(response.decode())
                all_outputs[input_id] = {script_name: output}
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
            else:
                all_outputs[input_id] = {script_name: output['text']}

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
