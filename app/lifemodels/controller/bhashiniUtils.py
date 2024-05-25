import requests
from pprint import pprint
from app.lifemodels.controller.bhashiniModelDetails import (
    get_bhashini_translation_result,
    get_bhashini_asr_result,
    get_bhashini_transliteration_result
)

from app.controller import life_logging
logger = life_logging.get_logger()


def get_bhashini_transliteration_models():
    pipeline_id = '64392f96daac500b55c543cd'  # MEITY
    # pipeline_id = '643930aa521a4b1ba0f4c41d'  # AI4Bharat
    user_id = '8317886d36a849e184ab621ce660447a'
    api_key = '237901121d-1add-4f37-b836-557b3af5877a'

    end_url = 'https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline'

    headers = {
        'userID': user_id,
        'ulcaApiKey': api_key
    }

    payload = {
        "pipelineTasks": [
            {
                "taskType": "transliteration"
                # "config": {
                #     "language": {
                #             "sourceLanguage": "hi"
                #     }
                # }
            }
        ],
        "pipelineRequestConfig": {
            "pipelineId": pipeline_id
        }
    }

    pipe_config = requests.post(url=end_url, headers=headers, json=payload)
    return pipe_config.json()


def get_bhashini_translation_models():
    pipeline_id = '64392f96daac500b55c543cd'  # MEITY
    # pipeline_id = '643930aa521a4b1ba0f4c41d'  # AI4Bharat
    user_id = '8317886d36a849e184ab621ce660447a'
    api_key = '237901121d-1add-4f37-b836-557b3af5877a'

    end_url = 'https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline'

    headers = {
        'userID': user_id,
        'ulcaApiKey': api_key
    }

    payload = {
        "pipelineTasks": [
            {
                "taskType": "translation"
                # "config": {
                #     "language": {
                #             "sourceLanguage": "hi"
                #     }
                # }
            }
        ],
        "pipelineRequestConfig": {
            "pipelineId": pipeline_id
        }
    }

    pipe_config = requests.post(url=end_url, headers=headers, json=payload)
    return pipe_config.json()


def get_bhashini_asr_models():
    pipeline_id = '64392f96daac500b55c543cd'  # MEITY
    # pipeline_id = '643930aa521a4b1ba0f4c41d'  # AI4Bharat
    user_id = '8317886d36a849e184ab621ce660447a'
    api_key = '237901121d-1add-4f37-b836-557b3af5877a'

    end_url = 'https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline'

    headers = {
        'userID': user_id,
        'ulcaApiKey': api_key
    }

    payload = {
        "pipelineTasks": [
            {
                "taskType": "asr"
                # "config": {
                #     "language": {
                #             "sourceLanguage": "hi"
                #     }
                # }
            }
        ],
        "pipelineRequestConfig": {
            "pipelineId": pipeline_id
        }
    }

    pipe_config = requests.post(url=end_url, headers=headers, json=payload)
    return pipe_config.json()


def get_translation_model(source_lang='hi', target_lang='en'):
    all_results = get_bhashini_translation_result()
    models = all_results['pipelineResponseConfig'][0]['config']
    # print(models)
    for model in models:
        # print(model)
        language = model['language']
        model_source_lang = language['sourceLanguage']
        if model_source_lang == source_lang:
            model_target_lang = language['targetLanguage']
            if model_target_lang == target_lang:
                model_id = model['serviceId']
                api_key = all_results['pipelineInferenceAPIEndPoint']['inferenceApiKey']['value']
                end_url = all_results['pipelineInferenceAPIEndPoint']['callbackUrl']
                source_script = language['sourceScriptCode']
                target_script = language['targetScriptCode']
                return model_id, api_key, end_url, source_script, target_script
    return '', '', ''


def get_transcription_model(source_lang='hi'):
    all_results = get_bhashini_asr_result()
    models = all_results['pipelineResponseConfig'][0]['config']
    for model in models:
        language = model['language']
        model_source_lang = language['sourceLanguage']
        if model_source_lang == source_lang:
            model_id = model['serviceId']
            api_key = all_results['pipelineInferenceAPIEndPoint']['inferenceApiKey']['value']
            end_url = all_results['pipelineInferenceAPIEndPoint']['callbackUrl']
            target_script = language['sourceScriptCode']
            return model_id, api_key, end_url, target_script
    return '', '', ''


def translate_data(data, model, api_key, end_url, source_lang='hi', target_lang='en'):
    # model, api_key, end_url = get_translation_model(source_lang, target_lang)
    header = {"Authorization": api_key}

    if model != '':
        payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                                "sourceLanguage": source_lang,
                                "targetLanguage": target_lang
                        },
                        "serviceId": model
                    }
                }
            ],
            "inputData": {
                "input": [
                    {
                        "source": data
                    }
                ]
            }
        }

        translation = requests.post(url=end_url, headers=header, json=payload)
        print(translation)
        logger.info('Status: %s', translation)

        return translation.json()


def transcribe_data(audio_data, model, api_key, end_url, lang_name='hi'):
    # model, api_key, end_url = get_transcription_model(lang_name)
    # end_url = "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
    # api_key = "A76bWGt9rowZFVQfsJmmgJDnriqa1CT14ECLdBjiGXHc93tP9rX72KfVmdwIAsDZ"
    # model = bhashini_asr_models.get(lang_name, '')

    header = {"Authorization": api_key}

    if model != '':
        payload = {
            "pipelineTasks": [
                {
                    "taskType": "asr",
                    "config": {
                        "language": {
                                "sourceLanguage": lang_name
                        },
                        "serviceId": model,
                        # "postProcessors": ["itn", "punctuation"]
                        "postProcessors": ["itn"]
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
        logger.info('Status: %s', transcript)
        return transcript.json()
    else:
        return ''


if __name__ == '__main__':
    data = ["लास्ट में एन और सेकंड लास्ट में वॉवेल ठीक है दिस इज़ द वे 2 कन्वर्ट थिन आर हो जाएगा 2 एन हो जाएंगे तो हमारा लास्ट में क्या है एन तो हम 2 एन कर देंगे सिंपल।",
            "अंडरस्टैंड।",
            "ओके",
            "ठीक है यस।",
            "बनाना ग्रेप्स ऑरेंज।",
            "और यहाँ पे आपको क्या लगने लगती है कैसे महसूस कर रहा है बहुत ही अच्छा क्यों अच्छा लगने लगती है?"]
    for current_data in data:
        print('Source', current_data)
        result = translate_data(current_data)
        output = result["pipelineResponse"][0]["output"][0]["target"]
        print('Target', output)
    # get_bhashini_transliteration_models()
    # get_bhashini_translation_models()
    # get_bhashini_asr_models()
