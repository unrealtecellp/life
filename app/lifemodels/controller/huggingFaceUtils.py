from huggingface_hub import HfApi, list_models, ModelFilter
from pprint import pprint
from app.controller import (
    life_logging
)

logger = life_logging.get_logger()

featured_authors = ['ai4bharat', 'Harveenchadha', 'facebook', 'meta-llama', 
'google', 'microsoft', 'allenai', 'Intel', 'openai', 'openchat', 'writer', 'amazon',
'assemblyai', 'EleutherAI', 'tiiuae', 'bigscience', 'Salesforce', 'lmsys', 'mosaicml', 'databricks',
'stabilityai', 'Open-Orca', 'mistralai', 'HuggingFaceH4', 'distil-whisper']

def get_hf_models (hf_token, task='automatic-speech-recognition'):
    hf_api = HfApi(
        endpoint="https://huggingface.co",  # Can be a Private Hub endpoint.
        # Token is not persisted on the machine.
        # token="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",
        token=hf_token
    )
    # model_filter = ModelFilter(language='hi',
    #                         task='automatic-speech-recognition'
    #                         )
    model_filter = ModelFilter(task='automatic-speech-recognition')

    models = hf_api.list_models(filter=model_filter, full=True, cardData=True, fetch_config=True)

    logger.debug('Models type %s', type(models))
    # try:
    #     models = list(models)
    #     logger.debug('Models length %s', len(models))        
    # except:
    #     logger.exception('')

    # print(len(models))
    author_model_map = {}
    all_models = []
    # i = 0
    # all_performance_vals = {}
    # no_metric_models = []
    try:
        for i, model in enumerate(models):
            # i += 1
            # print('Model', i)
            # model_dict = dict(model)

            # current_model_entry['modelMetadata']
            current_model = {}
            # try:
            #     mod_dict = model.__dict__
            #     logger.debug('Model dict info %s', mod_dict)
            # except:
            #     logger.exception('')
            
            current_model_info = {}
            # current_model_info['card_data'] = model.card_data.to_dict
            cardData = model.cardData
            if not cardData is None:
                cardData = cardData.to_dict()
            current_model_info['cardData'] = cardData
            current_model_info['model_index'] = model.model_index
            current_model_info['config'] = model.config
            current_model_info['disabled'] = model.disabled
            current_model_info['card_data'] = model.gated
            current_model_info['downloads'] = model.downloads
            current_model_info['library_name'] = model.library_name
            current_model_info['gated'] = model.gated
            current_model_info['likes'] = model.likes
            current_model_info['mask_token'] = model.mask_token
            current_model_info['private'] = model.private
            current_model_info['model_index'] = model.model_index
            current_model_info['pipeline_tag'] = model.pipeline_tag
            current_model_info['safetensors'] = model.safetensors
            current_model_info['sha'] = model.sha
            current_model_info['siblings'] = [sibling.__dict__ for sibling in model.siblings]
            current_model_info['spaces'] = model.spaces
            current_model_info['tags'] = model.tags
            current_model_info['transformers_info'] = model.transformers_info
            current_model_info['widget_data'] = model.widget_data
            current_model_info['last_modified'] = model.last_modified
            current_model['hfModelInfo'] = current_model_info
            current_model['hfTask'] = task        

            model_id = model.modelId
            model_author = model.author
            current_model['hfModelID'] = model_id
            current_model['hfModelAuthor'] = model_author
            
            existing_models = author_model_map.get(model_author, [])
            existing_models.append(model_id)
            author_model_map[model_author] = existing_models
            logger.info ('Model number: %s\tModel ID %s\tModel Author %s', i, model_id, model_author)
            
            # model_performance = {'modelPerformance': []}
            # model_languages = {'modelLanguages': []}
            current_model['hfModelLanguages'] = []
            current_model['hfModelPerformance'] = []

            try:            
                card_data = model.cardData.to_dict()
                # print ('Languages', card_data.get('language', []))
            except Exception as e:
                logger.exception ('Exception for model', i, model_id, e)
                card_data = {}
            current_model_info['card_data'] = card_data
            # current_model['hfModelPerformance'] = model_results
            
            if 'language' in card_data:
                model_langs = card_data.get('language', [])
                # model_languages['modelLanguages'] = model_langs
                current_model['hfModelLanguages'] = model_langs

            if 'model-index' in card_data:
                model_index = card_data.get('model-index', [])[0]
                # print('Model index', model_index)
                if 'results' in model_index:                
                    model_results = model_index.get('results', [])
                    # model_performance['modelPerformance'] = model_results
                    current_model['hfModelPerformance'] = model_results
            # current_model_entry['modelMetadata'] = current_model
            all_models.append(current_model)

                    # # print('Model results', model_results)
                    # for result in model_results:
                    #     # print('Results', result)
                    #     if 'metrics' in result:
                    #         model_result_vals = result['metrics']
                    #         for model_result_val in model_result_vals:
                    #             metric_type = model_result_val['type'].lower()
                    #             metric_value = model_result_val['value']
                    #             try:
                    #                 metric_value = float(metric_value)
                    #             except Exception as e:
                    #                 print('Exception', e, metric_value)
                    #                 metric_value = 0.0
                                
                    #             # if metric_type not in all_performance_vals:
                    #             #     all_performance_vals[metric_type] = {
                    #             #         model_id: metric_value}
                    #             # else:
                    #             #     all_performance_vals[metric_type].update(
                    #             #         {model_id: metric_value})
                    #             # print('Model performance:\t',
                    #             #     metric_type, metric_value)
                    #     else:
                    #         no_metric_models.append((model_id, card_data))
                    #         print('No metric value defined')
            #     else:
            #         no_metric_models.append((model_id, card_data))
            #         print('No metric value defined')
            # else:
            #     no_metric_models.append((model_id, card_data))
            #     print('No metric value defined')

        # print('All performance values', all_performance_vals)

        # for metric_type, models_score in all_performance_vals.items():
        #     # print('Models score', models_score)
        #     print('Metric Type: ', metric_type)
        #     print('Total values reported', len(models_score))
        #     print('==============================')
        #     sorted_models_score = sorted(
        #         models_score.items(), key=lambda x: x[1])
        #     sorted_models_dict = dict(sorted_models_score)

        #     for scored_model, model_score in sorted_models_dict.items():
        #         print('Metric Type: %s \tModel name: %s \tModel Score:\t %s'
        #             % (metric_type, scored_model, model_score))
        #     print('==============================')
        # # print(no_metric_models)
        # print ('Total models', i)
        # print (author_model_map)
        # print ('Total authors', len(author_model_map))
        # print ('All authors', author_model_map.keys(), sep='\n')
        # # for key, val in card_data.items():
        #     print('Key:%s\tValue:%s', key, val)

        # print(car)

        # print(models[0])
    except:
        logger.exception('')
    return all_models


if __name__ == '__main__':
    token="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"
    model_list = get_hf_models(token)
    print (model_list[0])
    print ('Total Models', len(model_list))