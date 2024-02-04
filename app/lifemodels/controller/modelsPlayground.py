from simpletransformers.classification import ClassificationModel
import torch
import json
import os
import urllib.request
import html2text
import re
from datetime import datetime
import io
import pandas as pd

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
def get_video_title(key, vlink):
    urlv = "https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id="+vlink+"&key="+key
    with urllib.request.urlopen(urlv) as url:
        datav = json.loads(url.read())
    # logger.debug(datav)
    # logger.debug(datav['items'])
    # logger.debug(len(datav['items']))

    video_title = datav['items'][0]['snippet']['title']

    return video_title

def get_crawled_data(key, vlink):
    csv_data = []
    # Comments on the video
    urlc = "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet,replies&videoId="+vlink+"&key="+key
    with urllib.request.urlopen(urlc) as url:
        datac = json.loads(url.read())

    # logger.debug("datac: %s", datac)
    for data in datac['items']:
        # ccount += 1
        # logger.debug('Video:\t %s, \tComment:\t %s', video_count, ccount)
        topc = data['snippet']['topLevelComment']['snippet']
        final_text = topc['textDisplay']
        csv_data.append(html2text.html2text(final_text).strip())
    # logger.debug('csv_data: %s', csv_data)

    return csv_data

def get_crawled_data_by_link(key, video_ids):
    uploaded_data_ids = []
    input_data_dict = {}
    for video_count, vlink in enumerate(video_ids):
        # get comments from first page
        # logger.debug('Video:\t:%s \tPage:\t1', video_count)
        video_title = get_video_title(key, vlink)
        csv_data = get_crawled_data(key, vlink)
        uploaded_data_ids.append(video_title)
        input_data_dict[video_title] = csv_data

    return (uploaded_data_ids, input_data_dict)


# Get link to top n videos for the given search query
def get_topn_videos(api_key,
                    search_query,
                    video_count,
                    video_license):
    video_ids = []

    urld = "https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=" + \
        video_count+"&q="+search_query + \
        "&type=video&videoLicense="+video_license+"&key="+api_key

    with urllib.request.urlopen(urld) as url:
        datad = json.loads(url.read())

    all_itens = datad['items']
    for item in all_itens:
        vid = item['id']['videoId']
        video_ids.append(vid)

    return video_ids

def get_crawled_data_by_keywords(key, search_keywords):
    input_data_dict = {}
    for keyword in search_keywords:
        # logger.debug(keyword)
        csv_data = []
        video_ids = get_topn_videos(key,
                                    keyword,
                                    '2',
                                    'any')
        logger.debug(video_ids)
        for video_count, vlink in enumerate(video_ids):
            # get comments from first page
            # logger.debug('Video:\t:%s \tPage:\t1', video_count)
            csv_data.extend(get_crawled_data(key, vlink))
            input_data_dict[keyword] = csv_data
    #     logger.debug(input_data_dict)
    # logger.debug(input_data_dict)
    
    return input_data_dict

def get_prediction(model_path,
                   model_type_mapping,
                   selected_model,
                   input_data):
    prediction_df = pd.DataFrame(columns=[selected_model])
    # prediction_df['Text'] = input_data
    selected_model_path = os.path.join(model_path, selected_model)
    model_type = model_type_mapping[selected_model.split('_')[-1]]
    prediction_df[selected_model] = model_prediction(model_type,
                                                selected_model_path,
                                                input_data)
    # logger.debug(prediction_df)

    return prediction_df

def download_file(prediction_df, file_name):
    timestamp = '_' + re.sub(r'[-: \.]', '', str(datetime.now())) + '_prediction.csv'
    download_prediction_filename = file_name.replace('.csv', timestamp)
    download_prediction_filename_zip = download_prediction_filename.replace('.csv', '.zip')
    logger.debug('%s, %s', download_prediction_filename, download_prediction_filename_zip)
    
    compression_opts = dict(method='zip', archive_name=download_prediction_filename)

    csv_buffer = io.BytesIO()
    prediction_df.to_csv(csv_buffer, 
                            index=False,
                            compression=compression_opts)
    csv_buffer.seek(0)

    return (csv_buffer, download_prediction_filename_zip)

