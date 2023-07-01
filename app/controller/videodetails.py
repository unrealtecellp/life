"""Module to save the uploaded audio file(s) from 'enternewsenteces' route."""


import json
import os
import shutil
from datetime import datetime
import re
import gridfs
from flask import flash
import pandas as pd
from zipfile import ZipFile
from werkzeug.datastructures import FileStorage
import io
from app.controller import (
    getcommentstats,
    readJSONFile,
    getdbcollections,
    getcurrentusername,
    userdetails,
    getcurrentuserprojects,
    getactiveprojectname,
    life_logging,
    audiodetails,
    getprojecttype
)
from app.lifemodels.controller import (
    predictFromAPI,
    predictFromLocalModels
)
import subprocess
import shutil
from pprint import pprint, pformat
from pymongo import ReturnDocument

basedir = os.path.abspath(os.path.dirname(__file__))
basedir_parent = '/'.join(basedir.split('/')[:-1])

logger = life_logging.get_logger()
# logger.debug('Basedir parent', basedir_parent)
modelConfigPath = os.path.join(
    basedir_parent, 'jsonfiles/model_config.json')

# logger.debug('Modle config', modelConfigPath)

all_model_names = readJSONFile.readJSONFile(modelConfigPath)


allowed_file_formats = ['mp3', 'wav']

# TODO: This should be saved in a separate document in MongoDB that will bind
# specific keys in database to specific models


# appConfigPath = os.path.join(basedir, 'jsonfiles/app_config.json')

# allowed_file_formats = get_allowed_file_formats()

def get_video_id_filename(videofile, video_filename="no_filename"):
    if videofile['videofile'].filename != '':
        video_filename = videofile['videofile'].filename
    video_id = 'V'+re.sub(r'[-: \.]', '', str(datetime.now()))
    # audio_filename = audio_id+

    return video_id, video_filename


def saveonevideofile(mongo,
                     projects,
                     userprojects,
                     transcriptions,
                     projectowner,
                     activeprojectname,
                     current_username,
                     speakerId,
                     new_video_file,
                     sourceId='',
                     run_vad=False,
                     run_asr=False,
                     get_audio_json=False,
                     vad_model=[],
                     asr_model=[],
                     transcription_type='sentence',
                     boundary_threshold=0.3,
                     slice_threshold=0.9,
                     max_slice_size=120,
                     data_type="video",
                     **kwargs):
    """mapping of this function is with the 'uploadaudiofiles' route.

    Args:
        mongo: instance of PyMongo
        projects: instance of 'projects' collection.
        userprojects: instance of 'userprojects' collection.
        transcriptions: instance of 'transcriptions' collection.
        projectowner: owner of the project.
        activeprojectname: name of the project activated by current active user.
        current_username: name of the current active user.
        speakerId: speaker ID for this audio.
        new_audio_file: uploaded audio file details.
        type: the type of data - one of 'sentence', 'word', 'discourse' or 'phone'
        boundary_threshold: the threshold value of 'pause' where boundary is to be drawn
        slice_threshold: the threshold value of 'pause' where the file will be split into another files (0=no slice)
        max_slice_size: the recommended size of each slice (might have some offset value). Slices should not be larger than this but might be lower than this.
    """

    project_type = getprojecttype.getprojecttype(projects, activeprojectname)
    video_file = new_video_file['videofile']
    # audio_json_path = os.path.join(
    #     audiowaveform_json_dir_path, audio_json_parent_dir)

    # save audio file details in transcriptions collection
    if sourceId == '':
        sourceId = speakerId

    new_video_details = {
        "username": projectowner,
        "projectname": activeprojectname,
        "updatedBy": current_username,
        "videodeleteFLAG": 0,
        "videoverifiedFLAG": 0,
        "prompt": "",
        "dataType": data_type,
        "speakerId": speakerId,
        "sourceId": sourceId,
        "additionalInfo": {},
        "videoMetadata": {
            "verificationReport": {},
            "audiowaveform": {},
            "audioWaveformNorm": {}
        }
    }
    for kwargs_key, kwargs_value in kwargs.items():
        new_video_details[kwargs_key] = kwargs_value

    video_id, video_filename = get_video_id_filename(
        new_video_file)
    new_video_details['videoId'] = video_id
    updated_video_filename = (video_id +
                              '_' +
                              video_filename)
    new_video_details['videoFilename'] = updated_video_filename

    # Save audio file in mongoDb and also get it in Local File System
    fs_file_id, video_file_path = audiodetails.save_audio_in_mongo_and_localFs(mongo,
                                                                               updated_video_filename,
                                                                               video_file,
                                                                               video_id,
                                                                               projectowner,
                                                                               activeprojectname,
                                                                               current_username,
                                                                               store_in_local=False)

    # mongo, audio_path, type, max_pause = 0.5
    text_grid, transcriptionFLAG = audiodetails.get_text_grids(mongo,
                                                               run_vad,
                                                               run_asr,
                                                               vad_model,
                                                               asr_model,
                                                               video_file_path, transcription_type,
                                                               boundary_threshold,
                                                               slice_threshold,
                                                               max_slice_size)

    # logger.debug('Final generated text grid', text_grid)
    logger.debug('Final transcription flag', transcriptionFLAG)

    new_video_details["transcriptionFLAG"] = transcriptionFLAG
    new_video_details["textGrid"] = text_grid
    new_video_details[current_username] = {}
    new_video_details[current_username]["textGrid"] = text_grid
    # plogger.debug(new_audio_details)

    # save audio file details and speaker ID in projects collection
    speaker_id_key_name = audiodetails.get_speaker_id_key_name(project_type)
    speakerIds = projects.find_one({'projectname': activeprojectname},
                                   {'_id': 0, speaker_id_key_name: 1})
    # logger.debug(f"SPEAKER IDS: {speakerIds}")
    if len(speakerIds) != 0:
        speakerIds = speakerIds[speaker_id_key_name]
        if current_username in speakerIds:
            speakerIdskeylist = speakerIds[current_username]
            speakerIdskeylist.append(speakerId)
            speakerIds[current_username] = list(set(speakerIdskeylist))
        else:
            speakerIds[current_username] = [speakerId]
    else:
        speakerIds = {
            current_username: [speakerId]
        }
        # logger.debug(speakerIds)

    speaker_videoid_key_name = get_videospeaker_id_key_name(project_type)
    speaker_video_ids = projects.find_one({'projectname': activeprojectname},
                                          {'_id': 0, speaker_videoid_key_name: 1})
    # logger.debug(len(speaker_audio_ids))
    # logger.debug(speaker_audio_ids)
    if len(speaker_video_ids) != 0:
        speaker_video_ids = speaker_video_ids[speaker_videoid_key_name]
        # logger.debug('speaker_audio_ids', speaker_audio_ids)
        if speakerId in speaker_video_ids:
            speaker_video_idskeylist = speaker_video_ids[speakerId]
            speaker_video_idskeylist.append(video_id)
            speaker_video_ids[speakerId] = speaker_video_idskeylist
        else:
            # logger.debug('speakerId', speakerId)
            speaker_video_ids[speakerId] = [video_id]
        # plogger.debug(speaker_audio_ids)
    else:
        speaker_video_ids = {
            speakerId: [video_id]
        }
    # plogger.debug(speaker_audio_ids)
    # try:
    projects.update_one({'projectname': activeprojectname},
                        {'$set': {
                            'lastActiveId.'+current_username+'.'+speakerId+'.videoId':  video_id,
                            speaker_id_key_name: speakerIds,
                            speaker_videoid_key_name: speaker_video_ids
                        }})
    # update active speaker ID in userprojects collection
    projectinfo = userprojects.find_one({'username': current_username},
                                        {'_id': 0, 'myproject': 1, 'projectsharedwithme': 1})

    # logger.debug(projectinfo)
    userprojectinfo = ''
    for type, value in projectinfo.items():
        if len(value) != 0:
            if activeprojectname in value:
                userprojectinfo = type+'.'+activeprojectname+".activespeakerId"
    userprojects.update_one({"username": current_username},
                            {"$set": {
                                userprojectinfo: speakerId
                            }})

    # logger.debug('new_audio_file', type(new_audio_file), new_audio_file)
    # transcription_doc_id = transcriptions.insert(new_audio_details)
    # save audio file details in fs collection

    # logger.debug('audiowaveform_audio_path', audiowaveform_audio_path)
    # audiowaveform_audio_path = os.path.join(audiowaveform_audio_path, updated_audio_filename)

    # if get_audio_json:
    #     json_basedir = os.path.abspath(os.path.dirname(__file__))
    #     audiowaveform_json_dir_path = '/'.join(json_basedir.split('/')[:-1])
    #     audio_json_parent_dir = 'audiowaveform'
    #     audiowaveform_json = get_audio_waveform_json(
    #         audiowaveform_json_dir_path, audio_json_parent_dir, updated_audio_filename)
    #     new_audio_details['audioMetadata']['audiowaveform'] = audiowaveform_json

    transcription_doc_id = transcriptions.insert_one(new_video_details)

    return (True, transcription_doc_id, fs_file_id)

    # except Exception as e:
    #     logger.debug(e)
    #     flash(f"ERROR")
    #     return (False, '', '')


def get_videospeaker_id_key_name(project_type):
    speaker_id_key_name = ''
    if project_type == 'crawling' or project_type == 'annotation':
        speaker_id_key_name = 'sourceVideoIds'
    else:
        speaker_id_key_name = 'speakersVudioIds'

    return speaker_id_key_name
