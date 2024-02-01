from simpletransformers.classification import ClassificationModel
import torch
import json
import os
import urllib.request
import html2text

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
    
def get_crawled_data(key, video_ids):
    csv_data = []
    for video_count, vlink in enumerate(video_ids):
        ccount = 0
        # Comments on the video
        urlc = "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet,replies&videoId="+vlink+"&key="+key
        with urllib.request.urlopen(urlc) as url:
            datac = json.loads(url.read())

        # get comments from first page
        logger.debug('Video:\t:%s \tPage:\t1', video_count)
        logger.debug("datac: %s", datac)
        for data in datac['items']:
            ccount += 1
            logger.debug('Video:\t %s, \tComment:\t %s', video_count, ccount)
            topc = data['snippet']['topLevelComment']['snippet']
            final_text = topc['textDisplay']
            csv_data.append(html2text.html2text(final_text).strip())
    logger.debug('csv_data: %s', csv_data)

    return csv_data
