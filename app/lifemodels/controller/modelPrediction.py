from simpletransformers.classification import ClassificationModel
import torch
import json
import os

from app.controller import (
    life_logging
)

logger = life_logging.get_logger()

cuda_available = torch.cuda.is_available()

def model_prediction(model_t, b_model, data):
    try:
        with open(os.path.join(b_model, 'model_args.json'), 'r') as f:
            model_args = json.load(f)
        num_labels = len(model_args['labels_list'])
        model = ClassificationModel(model_t, b_model, num_labels=num_labels, use_cuda=cuda_available)
        predictions, raw_outputs = model.predict(data)

        return predictions
    except:
        logger.exception("")
        return ''

