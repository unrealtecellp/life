import requests
import json
from huggingface_hub import InferenceClient

from app.controller import life_logging

logger = life_logging.get_logger()


def predictFromAPI(model_name, model_params):
    pass


def predictFromHFModel(model_inputs, model_url, hf_token, model_params={}, task='automatic-speech-recognition', script_name=''):
    # hf_token = input_data['hf_token']
    # task = model_params['task']
    # prediction = globals(
    # )['predict_'+task](model_params)
    all_outputs = {}
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
    logger.info('ASR Output for file %s \tusing model %s',
                all_outputs, model_url)

    return all_outputs
