from flask import flash, redirect, url_for

from app.controller import (
    life_logging,
    getcurrentusername
)
from app import mongo


from app.lifemodels.controller import huggingFaceUtils as hfu
from datetime import datetime
import re

logger = life_logging.get_logger()

def get_hf_tokens(app_config, current_username):
    # current_username = getcurrentusername()
    hf_config = app_config.find_one ({'configtype': 'huggingfacemodel'}, {'_id': 0, 'configparams.usersData': 1})
    if not hf_config is None:
        param_data = hf_config['configparams']['usersData']
        user_data = param_data.get(current_username, {})
        if len(user_data) > 0:
            api_tokens = user_data.get('apiTokens')
            token = api_tokens[0]
    return token

def get_featured_authors(app_config, current_username):
    hf_config = app_config.find_one ({'configtype': 'huggingfacemodel'}, {'_id': 0, 'configparams.usersData': 1})
    if not hf_config is None:
        param_data = hf_config['configparams']['usersData']
        user_data = param_data.get(current_username, {})
        if len(user_data) > 0:
            authors_list = user_data['globals']['automatic-speech-recognition']['authorsList']
            
    return authors_list

def get_model_id(source='hfapi'):
    model_id = 'MOD'+re.sub(r'[-: \.]', '', str(datetime.now()))+'_'+source
    return model_id

def generate_models_database():
    try:
        mongo.db.validate_collection("models")
        logger.info('Models Database found!')
    except Exception as e:
        logger.info('Creating Models Database %s', e)
        models_collection = mongo.db.models
        generate_dummy_model_entry(models_collection)

def get_model_list (models, languages, lang_name='Hindi'):
    pass

def generate_dummy_model_entry(models):
    current_model_entry={}
    current_model_entry['modelId'] = ''
    current_model_entry['source'] = ''
    current_model_entry['target'] = ''
    current_model_entry['modelSource'] = ''
    current_model_entry['model'] = {}
    current_model_entry['lifeTask'] = ''
    current_model_entry['modelMetadata'] = {}
    # model_params = {}
    current_model_entry['modelParams'] = {}
    current_model_entry['createdBy'] = ''
    current_model_entry['lastSyncedBy'] = ''
    current_model_entry['allSync'] = []
    models.insert(current_model_entry)



def sync_hf_models(models, languages, token, current_user, tasks=['automatic-speech-recognition'], model_params={}, force_resync=False):
    # token = get_hf_token()
    task_mapping = {'automatic-speech-recognition': 'transcription'}
    task_abbreviations = {'automatic-speech-recognition': 'asr'}
    all_models = []
    total_models = 0
    for task in tasks:
        logger.debug('Task %s', task)
        model_details = hfu.get_hf_models(token, task)
        total_models+=len(model_details)

        for current_model in model_details:
            life_task = task_mapping[task]
            # current_user = getcurrentusername()

            # if not force_resync:
            existing_model_entry = models.find_one({
                'modelSource': 'HuggingFace', 
                'lifeTask': life_task, 
                'modelMetadata.hfModelID': current_model['hfModelID']},
                {
                    '_id': 1,
                    'allSync': 1
                })
            if (existing_model_entry is None) or (not '_id' in existing_model_entry):
                current_model_entry = {}
                model_id = get_model_id()
                current_model_entry['modelId'] = model_id
                current_model_entry['source'] = 'audioFilename'
                current_model_entry['target'] = ''
                current_model_entry['modelSource'] = 'HuggingFace Hub'
                current_model_entry['model'] = {'api': ['InferenceClient']}
                current_model_entry['model']['local'] = []
                current_model_entry['model']['localpath'] = []
                current_model_entry['lifeTask'] = life_task
                current_model_entry['modelMetadata'] = current_model
                # model_params = {}
                current_model_entry['modelParams'] = model_params.get(life_task, {})
                current_model_entry['createdBy'] = current_user
                current_model_entry['lastSyncedBy'] = current_user
                current_model_entry['allSync'] = [(current_user, datetime.now())]
                all_models.append(current_model_entry)
            elif force_resync:
                all_syncs = existing_model_entry.get('allSync', [])
                all_syncs.append((current_user, datetime.now()))
                current_model_entry['lastSyncedBy'] = current_user
                current_model_entry['modelMetadata'] = current_model
                current_model_entry['modelParams'] = model_params.get(life_task, {})
                all_models.append(current_model_entry)
            
            model_langs = current_model['hfModelLanguages']

            lang_model_key = 'models.' + task
            for model_lang in model_langs:
                if model_lang != '':
                    lang_entry = languages.update_many({
                        'part1ISO639': model_lang
                    },
                    {'$push': {
                        lang_model_key:{
                            'hfTask': task,
                            'lifeTask': life_task,
                            'modelId': model_id
                        }                
                    }},
                    upsert=True )
        # TODO: implement upsert_many force_resync - currently it only inserts
        # but never updates
        models.insert_many(all_models)
    
    return total_models
