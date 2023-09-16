from huggingface_hub import HfApi, list_models, ModelFilter
from pprint import pprint

hf_api = HfApi(
    endpoint="https://huggingface.co",  # Can be a Private Hub endpoint.
    # Token is not persisted on the machine.
    token="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",
)
model_filter = ModelFilter(language='hi',
                           task='automatic-speech-recognition'
                           )

models = hf_api.list_models(filter=model_filter, cardData=True, search='hi')

# print(len(models))

i = 0
all_performance_vals = {}
no_metric_models = []
for model in models:
    i += 1
    print('Model', i, model)
    model_id = model.modelId
    model_author = model.author
    card_data = dict(model.cardData)

    if 'model-index' in card_data:
        model_index = card_data.get('model-index', [])[0]
        # print('Model index', model_index)
        if 'results' in model_index:
            model_results = model_index.get('results', [])
            # print('Model results', model_results)
            for result in model_results:
                # print('Results', result)
                if 'metrics' in result:
                    model_result_vals = result['metrics']
                    for model_result_val in model_result_vals:
                        metric_type = model_result_val['type'].lower()
                        metric_value = model_result_val['value']
                        try:
                            metric_value = float(metric_value)
                        except Exception as e:
                            print('Exception', e, metric_value)
                            metric_value = 0.0
                        if metric_type not in all_performance_vals:
                            all_performance_vals[metric_type] = {
                                model_id: metric_value}
                        else:
                            all_performance_vals[metric_type].update(
                                {model_id: metric_value})
                        print('Model performance:\t',
                              metric_type, metric_value)
                else:
                    no_metric_models.append((model_id, card_data))
                    print('No metric value defined')
        else:
            no_metric_models.append((model_id, card_data))
            print('No metric value defined')
    else:
        no_metric_models.append((model_id, card_data))
        print('No metric value defined')

# print('All performance values', all_performance_vals)

for metric_type, models_score in all_performance_vals.items():
    # print('Models score', models_score)
    print('Metric Type: ', metric_type)
    print('Total values reported', len(models_score))
    print('==============================')
    sorted_models_score = sorted(
        models_score.items(), key=lambda x: x[1])
    sorted_models_dict = dict(sorted_models_score)

    for scored_model, model_score in sorted_models_dict.items():
        print('Metric Type: %s \tModel name: %s \tModel Score:\t %s'
              % (metric_type, scored_model, model_score))
    print('==============================')
print(no_metric_models)
# for key, val in card_data.items():
#     print('Key:%s\tValue:%s', key, val)

# print(car)

# print(models[0])
