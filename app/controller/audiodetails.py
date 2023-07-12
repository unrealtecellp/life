"""Module to save the uploaded audio file(s) from 'enternewsenteces' route."""

import librosa
import pydub
from pydub import AudioSegment
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
    getprojecttype,
    life_logging
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


def get_file_format(current_file):
    cur_filename = current_file.filename
    # logger.debug("Filename", cur_filename)
    file_format = cur_filename.rsplit('.', 1)[-1].lower()
    # TODO: Infer file format based on its header

    return file_format


def saveaudiofiles(mongo,
                   projects,
                   userprojects,
                   transcriptions,
                   projectowner,
                   activeprojectname,
                   current_username,
                   speakerId,
                   new_audio_file,
                   run_vad=True,
                   run_asr=False,
                   split_into_smaller_chunks=True,
                   get_audio_json=True,
                   vad_model=[],
                   asr_model=[],
                   transcription_type='sentence',
                   boundary_threshold=0.3,
                   slice_threshold=0.9,
                   slice_size=120,
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
    """

    type = 'audiofile'
    # logger.debug ('New ques file', new_ques_file)
    file_states = []
    transcription_doc_ids = []
    fs_file_ids = []

    if new_audio_file[type].filename != '':
        current_file = new_audio_file[type]
        # logger.debug("Filepath", current_file)
        file_format = get_file_format(current_file)

        if (file_format in allowed_file_formats):
            file_state, transcription_doc_id, fs_file_id = saveoneaudiofile(mongo,
                                                                            projects,
                                                                            userprojects,
                                                                            transcriptions,
                                                                            projectowner,
                                                                            activeprojectname,
                                                                            current_username,
                                                                            speakerId,
                                                                            new_audio_file,
                                                                            run_vad,
                                                                            run_asr,
                                                                            split_into_smaller_chunks,
                                                                            vad_model,
                                                                            asr_model,
                                                                            transcription_type,
                                                                            boundary_threshold,
                                                                            slice_threshold,
                                                                            slice_size)
            file_states.append(file_state)
            transcription_doc_ids.append(transcription_doc_id)
            fs_file_ids.append(fs_file_id)

        elif (file_format == 'zip'):
            logger.debug('ZIP file format')
            file_states, transcription_doc_ids, fs_file_ids = savemultipleaudiofiles(mongo,
                                                                                     projects,
                                                                                     userprojects,
                                                                                     transcriptions,
                                                                                     projectowner,
                                                                                     activeprojectname,
                                                                                     current_username,
                                                                                     speakerId,
                                                                                     new_audio_file,
                                                                                     run_vad,
                                                                                     run_asr,
                                                                                     split_into_smaller_chunks,
                                                                                     get_audio_json,
                                                                                     vad_model,
                                                                                     asr_model,
                                                                                     transcription_type,
                                                                                     boundary_threshold,
                                                                                     slice_threshold,
                                                                                     slice_size)
        else:
            return ([False], ['Unsupported file format'], ['File not stored'])

    return (file_states, transcription_doc_ids, fs_file_ids)


def savemultipleaudiofiles(mongo,
                           projects,
                           userprojects,
                           transcriptions,
                           projectowner,
                           activeprojectname,
                           current_username,
                           speakerId,
                           all_audio_files,
                           run_vad=True,
                           run_asr=False,
                           split_into_smaller_chunks=True,
                           get_audio_json=True,
                           vad_model=[],
                           asr_model=[],
                           transcription_type='sentence',
                           boundary_threshold=0.3,
                           slice_threshold=0.9,
                           slice_size=120,
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
        all_audio_files: uploaded audio file details.
        type: the type of data - one of 'sentence', 'word', 'discourse' or 'phone'
        boundary_threshold: the threshold value of 'pause' where boundary is to be drawn
        slice_threshold: the threshold value of 'pause' where the file will be split into another files (0=no slice)
    """
    all_file_states = []
    transcription_doc_ids = []
    fs_file_ids = []
    new_audio_file = {}

    if all_audio_files['audiofile'].filename != '':
        zip_audio_files = all_audio_files['audiofile']

    try:
        with ZipFile(zip_audio_files) as myzip:
            # logger.debug('File list', myzip.namelist())
            for file_name in myzip.namelist():
                # if (file_name.endswith('.wav')):
                # logger.debug('Current File name', file_name)
                with myzip.open(file_name) as myfile:
                    # file_format = get_file_format(myfile)
                    file_format = file_name.rsplit('.', 1)[-1].lower()
                    # logger.debug('File format during upload', file_format)
                    if file_format in allowed_file_formats:
                        # upload_file_full = {}
                        file_content = io.BytesIO(myfile.read())
                        # logger.debug ('ZIP file', mainfile)
                        # logger.debug ("File content", file_content)
                        # logger.debug ("Upload type", fileType)
                        new_audio_file['audiofile'] = FileStorage(
                            file_content, filename=file_name)
                        file_state, transcription_doc_id, fs_file_id = saveoneaudiofile(mongo,
                                                                                        projects,
                                                                                        userprojects,
                                                                                        transcriptions,
                                                                                        projectowner,
                                                                                        activeprojectname,
                                                                                        current_username,
                                                                                        speakerId,
                                                                                        new_audio_file,
                                                                                        run_vad,
                                                                                        run_asr,
                                                                                        split_into_smaller_chunks,
                                                                                        get_audio_json,
                                                                                        vad_model,
                                                                                        asr_model,
                                                                                        transcription_type,
                                                                                        boundary_threshold,
                                                                                        slice_threshold,
                                                                                        slice_size)

                        all_file_states.append(file_state)
                        transcription_doc_ids.append(transcription_doc_id)
                        fs_file_ids.append(fs_file_id)
    except Exception as e:
        logger.debug(e)
        flash(f"ERROR")
        all_file_states.append(False)
        transcription_doc_ids.append('')
        fs_file_ids.append('')
        # return (False)

    return (all_file_states, transcription_doc_ids, fs_file_ids)


def saveoneaudiofile(mongo,
                     projects,
                     userprojects,
                     transcriptions,
                     projectowner,
                     activeprojectname,
                     current_username,
                     speakerId,
                     new_audio_file,
                     sourceId='',
                     run_vad=True,
                     run_asr=False,
                     split_into_smaller_chunks=True,
                     get_audio_json=True,
                     vad_model=[],
                     asr_model=[],
                     transcription_type='sentence',
                     boundary_threshold=0.3,
                     slice_threshold=0.9,
                     max_slice_size=120,
                     data_type="audio",
                     new_audio_details={},
                     prompt="",
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

    all_transcription_doc_ids = []
    all_audio_fs_file_ids = []

    project_type = getprojecttype.getprojecttype(projects, activeprojectname)

    audiowaveform_file = new_audio_file['audiofile']

    full_audio_file = AudioSegment.from_file(audiowaveform_file)
    audio_duration = full_audio_file.duration_seconds

    json_basedir = os.path.abspath(os.path.dirname(__file__))
    audiowaveform_json_dir_path = '/'.join(json_basedir.split('/')[:-1])
    audio_json_parent_dir = 'audiowaveform'

    if get_audio_json or run_vad or run_asr or split_into_smaller_chunks:
        store_in_local = True
    else:
        store_in_local = False

    if split_into_smaller_chunks:
        store_in_mongo = False
    else:
        store_in_mongo = True

    # audio_json_path = os.path.join(
    #     audiowaveform_json_dir_path, audio_json_parent_dir)

    # save audio file details in transcriptions collection
    if sourceId == '':
        sourceId = speakerId
        # lifesourceid = speakerId

    if len(new_audio_details) == 0:
        new_audio_details = {
            "username": projectowner,
            "projectname": activeprojectname,
            "updatedBy": current_username,
            "audiodeleteFLAG": 0,
            "audioverifiedFLAG": 0,
            "prompt": prompt,
            "dataType": data_type,
            "lifesourceid": sourceId,
            "speakerId": speakerId,
            "additionalInfo": {},
            "audioMetadata": {
                "verificationReport": {},
                "audiowaveform": {},
                "audioWaveformNorm": {}
            }
        }
    for kwargs_key, kwargs_value in kwargs.items():
        new_audio_details[kwargs_key] = kwargs_value

    all_audio_ids = []
    all_audio_filenames = []

    audio_id, audio_filename = get_audio_id_filename(new_audio_file)
    updated_audio_filename = (audio_id +
                              '_' +
                              audio_filename)

    # Save audio file in mongoDb and also get it in Local File System

    # if split_into_smaller_chunks:
    audio_fs_file_id, audio_file_path = save_audio_in_mongo_and_localFs(mongo,
                                                                        updated_audio_filename,
                                                                        audiowaveform_file,
                                                                        audio_id,
                                                                        projectowner,
                                                                        activeprojectname,
                                                                        current_username,
                                                                        audiowaveform_json_dir_path,
                                                                        audio_json_parent_dir,
                                                                        store_in_local=store_in_local,
                                                                        store_in_mongo=store_in_mongo)

    # mongo, audio_path, type, max_pause = 0.5
    audio_chunks, text_grids, transcriptionFLAG = get_slices_and_text_grids(mongo,
                                                                            run_vad,
                                                                            run_asr,
                                                                            vad_model,
                                                                            asr_model,
                                                                            audio_file_path,
                                                                            transcription_type,
                                                                            boundary_threshold,
                                                                            slice_threshold,
                                                                            max_slice_size,
                                                                            audio_duration)

    # logger.debug('Final generated text grid', text_grid)
    logger.debug('Final transcription flag %s', transcriptionFLAG)

    new_audio_details["transcriptionFLAG"] = transcriptionFLAG

    if not split_into_smaller_chunks:
        all_audio_ids.append(audio_id)
        all_audio_filenames.append(audio_filename)
        all_audio_fs_file_ids.append(audio_fs_file_id)

        add_audio_details(new_audio_details,
                          get_audio_json,
                          current_username,
                          audio_id,
                          updated_audio_filename,
                          text_grids[0],
                          audiowaveform_json_dir_path,
                          audio_json_parent_dir
                          )

        transcription_doc_id = transcriptions.insert_one(new_audio_details)
        all_transcription_doc_ids.append(transcription_doc_id)

    else:

        for i in range(len(text_grids)):
            # for current_text_gird in text_grids:
            current_audio_id = audio_id + '-slice'+str(i)
            current_audio_filename = (current_audio_id +
                                      '_' +
                                      audio_filename)
            all_audio_ids.append(current_audio_id)
            all_audio_filenames.append(current_audio_filename)

            current_audio_chunk = audio_chunks[i]
            current_audio_chunk_begn = current_audio_chunk['start']*1000
            if current_audio_chunk_begn > 0:
                current_audio_chunk_begn = current_audio_chunk_begn-100

            current_audio_chunk_end = current_audio_chunk['end']*1000
            if current_audio_chunk_end < audio_duration:
                current_audio_chunk_end = current_audio_chunk_end+100
            current_audio_file = full_audio_file[current_audio_chunk_begn:current_audio_chunk_end]

            current_text_grid = text_grids[i]
            current_audio_details = json.loads(json.dumps(new_audio_details))
            current_audio_fs_file_id, current_audio_file_path = save_audio_in_mongo_and_localFs(mongo,
                                                                                                current_audio_filename,
                                                                                                current_audio_file,
                                                                                                current_audio_id,
                                                                                                projectowner,
                                                                                                activeprojectname,
                                                                                                current_username,
                                                                                                audiowaveform_json_dir_path,
                                                                                                audio_json_parent_dir,
                                                                                                store_in_local=False,
                                                                                                store_in_mongo=True)
            all_audio_fs_file_ids.append(current_audio_fs_file_id)

            add_audio_details(current_audio_details,
                              get_audio_json,
                              current_username,
                              current_audio_id,
                              current_audio_filename,
                              current_text_grid,
                              audiowaveform_json_dir_path,
                              audio_json_parent_dir
                              )
            transcription_doc_id = transcriptions.insert_one(
                current_audio_details)
            all_transcription_doc_ids.append(transcription_doc_id)

    # plogger.debug(new_audio_details)

        # logger.debug(speakerIds)

    speaker_id_key_name, speakerIds = get_speaker_ids(projects,
                                                      activeprojectname,
                                                      current_username,
                                                      speakerId,
                                                      project_type)

    speaker_audioid_key_name, speaker_audio_ids = get_speaker_audio_ids(projects,
                                                                        activeprojectname,
                                                                        all_audio_ids,
                                                                        speakerId,
                                                                        project_type)
    # plogger.debug(speaker_audio_ids)
    # try:
    # Update projects collection with speakerIds and Audio Ids of each speakerIds
    last_active_id = all_audio_ids[0]
    update_speakerid_audioid(projects,
                             activeprojectname,
                             current_username,
                             speakerId,
                             last_active_id,
                             speaker_id_key_name,
                             speakerIds,
                             speaker_audioid_key_name,
                             speaker_audio_ids)

    # Update active speaker ID in user projects
    update_active_speaker_Id(userprojects,
                             activeprojectname,
                             current_username,
                             speakerId
                             )
    # logger.debug('new_audio_file', type(new_audio_file), new_audio_file)
    # transcription_doc_id = transcriptions.insert(new_audio_details)
    # save audio file details in fs collection

    # logger.debug('audiowaveform_audio_path', audiowaveform_audio_path)
    # audiowaveform_audio_path = os.path.join(audiowaveform_audio_path, updated_audio_filename)

    return (True, all_transcription_doc_ids, all_audio_fs_file_ids)

    # except Exception as e:
    #     logger.debug(e)
    #     flash(f"ERROR")
    #     return (False, '', '')


def add_audio_details(audio_details_dict,
                      get_audio_json,
                      current_username,
                      audio_id,
                      updated_audio_filename,
                      text_grid,
                      audiowaveform_json_dir_path,
                      audio_json_parent_dir
                      ):
    audio_details_dict['audioId'] = audio_id
    audio_details_dict['audioFilename'] = updated_audio_filename
    audio_details_dict["textGrid"] = text_grid
    audio_details_dict['additionalIndo'] = {
        'totalSlices': 1, 'currentSliceNumber': 0}
    audio_details_dict[current_username] = {}
    audio_details_dict[current_username]["textGrid"] = text_grid
    if get_audio_json:
        audiowaveform_json = get_audio_waveform_json(
            audiowaveform_json_dir_path, audio_json_parent_dir, updated_audio_filename)
        audio_details_dict['audioMetadata']['audiowaveform'] = audiowaveform_json


def update_active_speaker_Id(userprojects,
                             activeprojectname,
                             current_username,
                             speakerId
                             ):
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


def update_speakerid_audioid(projects,
                             activeprojectname,
                             current_username,
                             speakerId,
                             last_active_id,
                             speaker_id_key_name,
                             speakerIds,
                             speaker_audioid_key_name,
                             speaker_audio_ids
                             ):
    projects.update_one({'projectname': activeprojectname},
                        {'$set': {
                            'lastActiveId.'+current_username+'.'+speakerId+'.audioId':  last_active_id,
                            speaker_id_key_name: speakerIds,
                            speaker_audioid_key_name: speaker_audio_ids
                        }})


def get_speaker_ids(projects,
                    activeprojectname,
                    current_username,
                    speakerId,
                    project_type):
    # save audio file details and speaker ID in projects collection
    speaker_id_key_name = get_speaker_id_key_name(project_type)

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

    return speaker_id_key_name, speakerIds


def get_speaker_audio_ids(projects,
                          activeprojectname,
                          all_audio_ids,
                          speakerId,
                          project_type):
    speaker_audioid_key_name = get_audiospeaker_id_key_name(project_type)
    speaker_audio_ids = projects.find_one({'projectname': activeprojectname},
                                          {'_id': 0, speaker_audioid_key_name: 1})
    # logger.debug(len(speaker_audio_ids))
    # logger.debug(speaker_audio_ids)
    if len(speaker_audio_ids) != 0:
        speaker_audio_ids = speaker_audio_ids[speaker_audioid_key_name]
        # logger.debug('speaker_audio_ids', speaker_audio_ids)
        if speakerId in speaker_audio_ids:
            speaker_audio_idskeylist = speaker_audio_ids[speakerId]
            speaker_audio_idskeylist.extend(all_audio_ids)
            speaker_audio_ids[speakerId] = speaker_audio_idskeylist
        else:
            # logger.debug('speakerId', speakerId)
            speaker_audio_ids[speakerId] = all_audio_ids
        # plogger.debug(speaker_audio_ids)
    else:
        speaker_audio_ids = {
            speakerId: all_audio_ids
        }

    return speaker_audioid_key_name, speaker_audio_ids


def get_speaker_id_key_name(project_type):
    speaker_id_key_name = ''
    if project_type == 'crawling' or project_type == 'annotation':
        speaker_id_key_name = 'sourceIds'
    else:
        speaker_id_key_name = 'speakerIds'

    return speaker_id_key_name


def get_audiospeaker_id_key_name(project_type):
    speaker_id_key_name = ''
    if project_type == 'crawling' or project_type == 'annotation':
        speaker_id_key_name = 'sourceAudioIds'
    else:
        speaker_id_key_name = 'speakersAudioIds'

    return speaker_id_key_name


def createaudiowaveform(audiowaveform_audio_path, audiowaveform_json_path, audio_filename):
    # if os.path.exists(audiowaveform_json_path):
    #     shutil.rmtree(audiowaveform_json_path)
    #     os.mkdir(audiowaveform_json_path)
    # else:
    #     os.mkdir(audiowaveform_json_path)
    # audio_file = io.BytesIO(audiowaveform_file['audiofile'])
    # audio_file = audiowaveform_file['audiofile']
    # audio_filename = os.path.join(audiowaveform_json_path, str(audio_file.filename))
    # audio_file.save(audio_filename)
    audio_filename = audio_filename[0:audio_filename.rfind('.')]
    json_filename = os.path.join(
        audiowaveform_json_path, audio_filename+'.json')
    logger.debug('audio filename', audiowaveform_audio_path)
    logger.debug('json_filename', json_filename)
    subprocess.run(
        ['audiowaveform', '-i', audiowaveform_audio_path, '-o',  json_filename])
    with open(json_filename, 'r') as jsonfile:
        read_json = json.load(jsonfile)
    # logger.debug(read_json)

    # shutil.rmtree(audiowaveform_json_path)

    return read_json


def updateaudiofiles(mongo,
                     projects,
                     userprojects,
                     project_type_collection,
                     projectowner,
                     activeprojectname,
                     current_username,
                     speakerId,
                     new_audio_file,
                     audio_id,
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
    """

    # save audio file details in transcriptions collection
    new_audio_details = {
        "speakerId": speakerId
    }
    for kwargs_key, kwargs_value in kwargs.items():
        new_audio_details[kwargs_key] = kwargs_value

    if new_audio_file['audiofile'].filename != '':
        audio_filename = new_audio_file['audiofile'].filename
        updated_audio_filename = (audio_id +
                                  '_' +
                                  audio_filename)
        new_audio_details['audioFilename'] = updated_audio_filename

    # save audio file details and speaker ID in projects collection
    speakerIds = projects.find_one({'projectname': activeprojectname},
                                   {'_id': 0, 'speakerIds': 1})
    # logger.debug(f"SPEAKER IDS: {speakerIds}")
    if len(speakerIds) != 0:
        speakerIds = speakerIds['speakerIds']
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

    speaker_audio_ids = projects.find_one({'projectname': activeprojectname},
                                          {'_id': 0, 'speakersAudioIds': 1})
    # logger.debug(len(speaker_audio_ids))
    # logger.debug(speaker_audio_ids)
    if len(speaker_audio_ids) != 0:
        speaker_audio_ids = speaker_audio_ids['speakersAudioIds']
        # logger.debug('speaker_audio_ids', speaker_audio_ids)
        if speakerId in speaker_audio_ids:
            speaker_audio_idskeylist = speaker_audio_ids[speakerId]
            speaker_audio_idskeylist.append(audio_id)
            speaker_audio_ids[speakerId] = speaker_audio_idskeylist
        else:
            # logger.debug('speakerId', speakerId)
            speaker_audio_ids[speakerId] = [audio_id]
        # plogger.debug(speaker_audio_ids)
    else:
        speaker_audio_ids = {
            speakerId: [audio_id]
        }
    # plogger.debug(speaker_audio_ids)
    try:
        projects.update_one({'projectname': activeprojectname},
                            {'$set': {
                                'lastActiveId.'+current_username+'.'+speakerId+'.audioId':  audio_id,
                                'speakerIds': speakerIds,
                                'speakersAudioIds': speaker_audio_ids
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
        logger.debug("audio_id: %s", audio_id)
        logger.debug("new_audio_details: %s", pformat(new_audio_details))
        logger.debug("project_type_collection: %s", project_type_collection)
        # pprint(new_audio_details)
        project_type_collection_doc_id = project_type_collection.update_one({"audioId": audio_id},
                                                                            {"$set": new_audio_details})
        # save audio file details in fs collection
        fs_file_id = mongo.save_file(updated_audio_filename,
                                     new_audio_file['audiofile'],
                                     audioId=audio_id,
                                     username=projectowner,
                                     projectname=activeprojectname,
                                     updatedBy=current_username)

        return (True, project_type_collection_doc_id, fs_file_id)

    except:
        logger.exception("")
        flash(f"ERROR")
        return (False, "", "")


def getactiveaudioid(projects,
                     activeprojectname,
                     activespeakerId,
                     current_username):
    """get last active audio id for current user from projects collections

    Args:
        projects (_type_): _description_
        activeprojectname (_type_): _description_
        current_username (_type_): _description_

    Returns:
        _type_: _description_
    """

    try:
        last_active_audio_id = projects.find_one({'projectname': activeprojectname},
                                                 {
            '_id': 0,
            'lastActiveId.'+current_username+'.'+activespeakerId+'.audioId': 1
        }
        )
        # logger.debug(last_active_audio_id)
        if len(last_active_audio_id) != 0:
            last_active_audio_id = last_active_audio_id['lastActiveId'][
                current_username][activespeakerId]['audioId']
    except:
        last_active_audio_id = ''

    return last_active_audio_id


def getaudiofiletranscription(data_collection, audio_id):
    """get the transcription details of the audio file

    Args:
        data_collection (_type_): _description_
        file_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    transcription_details = {}
    transcription_data = data_collection.find_one({'audioId': audio_id})
    if transcription_data is not None:
        transcription_details['data'] = transcription_data['textGrid']

    return transcription_details


def getaudiowaveformfilefromfs(mongo,
                               basedir,
                               folder_name,
                               file_id,
                               file_type):
    """get file from fs collection save it to local storage 'static' folder

    Args:
        mongo (_type_): _description_
        basedir (_type_): _description_
        file_id (_type_): _description_
        file_type (_type_): _description_

    Returns:
        _type_: _description_
    """
    # logger.debug(file_type, file_id)
    # creating GridFS instance to get required files
    # logger.debug('fs file:', basedir, folder_name,
    #                    file_id,
    #                    file_type)
    fs = gridfs.GridFS(mongo.db)
    file = fs.find_one({file_type: file_id})
    audioFolder = os.path.join(basedir, folder_name)
    logger.debug('Audio folder path', audioFolder)
    if (os.path.exists(audioFolder)):
        logger.debug('Audio folder path exists', audioFolder, 'deleting')
        shutil.rmtree(audioFolder)
    os.mkdir(audioFolder)
    file_path = ''
    if (file is not None and
            'audio' in file.contentType):
        file_name = file.filename
        logger.debug('File name', file_name)
        audiofile = fs.get_last_version(filename=file_name)
        audiofileBytes = audiofile.read()
        # if len(audiofileBytes) != 0:
        file_path = os.path.join(folder_name, file_name)
        save_file_path = os.path.join(basedir, file_path)
        logger.debug('Save file path', save_file_path)
        open(save_file_path, 'wb').write(audiofileBytes)
    else:
        save_file_path = ''
    # logger.debug('file_path', file_path)
    return save_file_path


def getaudiofilefromfs(mongo,
                       basedir,
                       file_id,
                       file_type):
    """get file from fs collection save it to local storage 'static' folder

    Args:
        mongo (_type_): _description_
        basedir (_type_): _description_
        file_id (_type_): _description_
        file_type (_type_): _description_

    Returns:
        _type_: _description_
    """
    # logger.debug(file_type, file_id)
    # creating GridFS instance to get required files
    # logger.debug('fs file:', basedir,
    #                    file_id,
    #                    file_type)
    fs = gridfs.GridFS(mongo.db)
    file = fs.find_one({file_type: file_id})
    audioFolder = os.path.join(basedir, 'static/audio')
    if (os.path.exists(audioFolder)):
        shutil.rmtree(audioFolder)
    os.mkdir(audioFolder)
    file_path = ''
    if (file is not None and
            'audio' in file.contentType):
        file_name = file.filename
        audiofile = fs.get_last_version(filename=file_name)
        audiofileBytes = audiofile.read()
        # if len(audiofileBytes) != 0:
        file_path = os.path.join('static', 'audio', file_name)
        save_file_path = os.path.join(basedir, file_path)
        open(save_file_path, 'wb').write(audiofileBytes)
    else:
        file_path = ''

    return file_path


def getnewaudioid(projects,
                  activeprojectname,
                  last_active_id,
                  activespeakerId,
                  which_one):
    """_summary_

    Args:
        projects (_type_): _description_
        activeprojectname (_type_): _description_
        last_active_id (_type_): _description_
        which_one (_type_): _description_
    """
    audio_ids_list = projects.find_one({'projectname': activeprojectname},
                                       {'_id': 0, 'speakersAudioIds': 1})
    # logger.debug('audio_ids_list', audio_ids_list)
    if len(audio_ids_list) != 0:
        audio_ids_list = audio_ids_list['speakersAudioIds'][activespeakerId]
        logger.debug('audio_ids_list: %s', audio_ids_list)
    if (len(audio_ids_list) != 0):
        if (last_active_id in audio_ids_list):
            audio_id_index = audio_ids_list.index(last_active_id)
        else:
            audio_id_index = 0
        # logger.debug('latestAudioId Index!!!!!!!', audio_id_index)
        if which_one == 'previous':
            audio_id_index = audio_id_index - 1
        elif which_one == 'next':
            if len(audio_ids_list) == (audio_id_index+1):
                audio_id_index = 0
            else:
                audio_id_index = audio_id_index + 1
        latest_audio_id = audio_ids_list[audio_id_index]
    else:
        latest_audio_id = ''
    logger.debug('latest_audio_id AUDIODETAILS: %s', latest_audio_id)

    return latest_audio_id


def updatelatestaudioid(projects,
                        activeprojectname,
                        latest_audio_id,
                        current_username,
                        activespeakerId):
    """_summary_

    Args:
        projects (_type_): _description_
        activeprojectname (_type_): _description_
        latest_audio_id (_type_): _description_
        current_username (_type_): _description_
    """
    projects.update_one({'projectname': activeprojectname},
                        {'$set': {'lastActiveId.'+current_username+'.'+activespeakerId+'.audioId':  latest_audio_id}})


def getaudiotranscriptiondetails(transcriptions, audio_id):
    """_summary_

    Args:
        transcriptions (_type_): _description_
        audio_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    transcription_data = {}
    transcription_regions = []
    gloss = {}
    pos = {}
    boundary_count = 0
    try:
        t_data = transcriptions.find_one({'audioId': audio_id},
                                         {'_id': 0, 'textGrid.sentence': 1})
        # logger.debug('t_data!!!!!', t_data)
        if t_data is not None:
            transcription_data = t_data['textGrid']
        # plogger.debug(transcription_data)
        sentence = transcription_data['sentence']
        for type, value in sentence.items():
            # logger.debug(type, value)
            transcription_region = {}
            # gloss = {}
            # transcription_region['sentence'] = {}
            transcription_region['data'] = {}
            transcription_region['boundaryID'] = type
            transcription_region['start'] = sentence[type]['start']
            transcription_region['end'] = sentence[type]['end']
            # transcription_region['sentence'] = {type: value}
            transcription_region['data'] = {'sentence': {type: value}}
            # plogger.debug(transcription_region)
            boundary_count += 1
            try:
                # logger.debug('!@!#!@!#!@!#!@!#!@!##!@!#!#!@!#!@!#!@!#!@!#!@!##!@!#!#', gloss)
                tempgloss = sentence[type]['gloss']
                # logger.debug('!@!#!@!#!@!#!@!#!@!##!@!#!#!@!#!@!#!@!#!@!#!@!##!@!#!#', tempgloss)
                gloss[type] = pd.json_normalize(
                    tempgloss, sep='.').to_dict(orient='records')[0]
                # logger.debug('!@!#!@!#!@!#!@!#!@!##!@!#!#!@!#!@!#!@!#!@!#!@!##!@!#!#', gloss)
                temppos = sentence[type]['pos']
                pos[type] = pd.json_normalize(
                    temppos, sep='.').to_dict(orient='records')[0]

                # logger.debug('288', gloss)
            except:
                # logger.debug('=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=', gloss)
                gloss = {}
                pos = {}

        # plogger.debug(transcription_region)
    #     if (type == 'speakerId' or
    #         type == 'sentenceId'):
    #         continue
    #     sentence['boundaryID'] = type
    #     for k, v in value.items():
    #         transcription_region[k] = v
    #         sentence[k] = v
    #     transcription_region['data']['sentence'] = sentence
            transcription_regions.append(transcription_region)
        # plogger.debug(transcription_regions)
    # logger.debug('303', gloss, pos)
    except:
        pass

    return (transcription_regions, gloss, pos, boundary_count)


def savetranscription(transcriptions,
                      activeprojectform,
                      scriptCode,
                      current_username,
                      transcription_regions,
                      audio_id,
                      activespeakerId):
    """Module to work on the sentence details (transcription and all) through ajax.

    Args:
        transcription_details (_type_): _description_
    """

    # plogger.debug(activeprojectform)
    # plogger.debug(scriptCode)
    # transcription_details = {
    #     'updatedBy' : current_username,
    #     "textdeleteFLAG": 0
    # }
    # text_grid = {}
    sentence = {}
    if transcription_regions is not None:
        transcription_regions = json.loads(transcription_regions)
        # plogger.debug(transcription_regions)
        for transcription_boundary in transcription_regions:
            transcription_boundary = transcription_boundary['data']
            if 'sentence' in transcription_boundary:
                for type, value in transcription_boundary['sentence'].items():
                    # logger.debug(f"KEY: {type}\nVALUE: {value}")
                    value["speakerId"] = activespeakerId
                    value["sentenceId"] = audio_id
                    sentence[type] = value
            # plogger.debug(sentence)
            #     logger.debug('transcription_boundary.keys()', transcription_boundary.keys())
            #     sentence[transcription_boundary['boundaryID']] = {
            #         "speakerId": activespeakerId,
            #         "sentenceId": audio_id,
            #         'start': transcription_boundary['start'],
            #         'end': transcription_boundary['end'],

            #         "transcription": {},
            #         "translation": {},
            #         "morphemes": {},
            #         "gloss": {},
            #         "pos": {},
            #         "tags": {}
            #     }
            # for transcription_data in transcription_regions:
            #     for type in list(transcription_data['data'].keys()):
            #         if type == 'sentence':
            #             logger.debug(type)

            # text_grid['sentence'] = sentence
            # logger.debug(text_grid)
            # transcription_details['textGrid'] = text_grid
            # transcriptions.insert(transcription_details)
            # logger.debug("'sentence' in transcription_boundary")
            # logger.debug('371', sentence)
            # plogger.debug(sentence)
    transcriptions.update_one({'audioId': audio_id},
                              {'$set':
                               {
                                   'textGrid.sentence': sentence,
                                   'updatedBy': current_username,
                                   'transcriptionFLAG': 1,
                                   current_username+'.textGrid.sentence': sentence
                               }
                               })


def getaudioprogressreport(projects,
                           transcriptions,
                           speakerdetails,
                           activeprojectname,
                           isharedwith):
    datatoshow = []
    users_speaker_ids = projects.find_one({'projectname': activeprojectname},
                                          {'_id': 0, 'speakerIds': 1})['speakerIds']
    # logger.debug('speaker_ids_1', users_speaker_ids)
    if len(users_speaker_ids) != 0:
        # logger.debug('speaker_ids_2', users_speaker_ids)
        for username in isharedwith:
            user_datatoshow = {"01_speakerId": '',
                               "02_createdBy": '',
                               "03_assignedTo": '',
                               "04_totalFiles": '',
                               "05_completedFiles": '',
                               "06_remainingFiles": ''}
            if username in users_speaker_ids:
                user_datatoshow['03_assignedTo'] = username
                for speakerid in users_speaker_ids[username]:
                    user_datatoshow['01_speakerId'] = speakerid
                    user_datatoshow['02_createdBy'] = speakerdetails.find_one(
                        {"projectname": activeprojectname,
                            "lifesourceid": speakerid, },
                        {"_id": 0, "createdBy": 1})['createdBy']
                    total_comments, annotated_comments, remaining_comments = getcommentstats.getcommentstats(projects,
                                                                                                             transcriptions,
                                                                                                             activeprojectname,
                                                                                                             speakerid,
                                                                                                             'audio')
                    # commentstats = [total_comments,annotated_comments, remaining_comments]
                    # datatoshow[username][speakerid] = commentstats
                    user_datatoshow['04_totalFiles'] = total_comments
                    user_datatoshow['05_completedFiles'] = annotated_comments
                    user_datatoshow['06_remainingFiles'] = remaining_comments

                    datatoshow.append(user_datatoshow)

    # logger.debug('datatoshow', datatoshow)

    return datatoshow


def getaudioidforderivedtranscriptionproject(transcriptions,
                                             activeprojectname,
                                             derive_from_project_type,
                                             search_id):
    if (derive_from_project_type == 'questionnaires'):
        search_id_key = 'quesId'
    elif (derive_from_project_type == 'transcriptions'):
        search_id_key = 'audioId'
    all_transcription_data = transcriptions.find({"projectname": activeprojectname},
                                                 {"_id": 0,
                                                     "audioId": 1,
                                                     "derivedfromprojectdetails": 1}
                                                 )
    for transcription_data in all_transcription_data:
        if (transcription_data["derivedfromprojectdetails"][search_id_key] == search_id):
            audio_id = transcription_data['audioId']
            return audio_id

    return 'False'


def getaudioidlistofsavedaudios(data_collection,
                                activeprojectname,
                                language,
                                exclude,
                                for_worker_id):
    """_summary_
    """
    logger.debug('checking recordings')
    all_audio = data_collection.find({"projectname": activeprojectname},
                                     {
        "_id": 0,
        "audioId": 1,
        "audioFilename": 1,
        "speakerId": 1
    })

    for audio in all_audio:
        audio_filename = audio['audioFilename']
        speaker_id = audio['speakerId']
        if (audio_filename != '' and
                for_worker_id in speaker_id):
            audioId = audio['audioId']
            exclude.append(audioId)

    return exclude


def getaudiofromprompttext(projectsform,
                           data_collection,
                           derivedFromProjectName,
                           activeprojectname,
                           text,
                           exclude):
    """_summary_
    """

    projectform = projectsform.find_one(
        {"projectname": derivedFromProjectName}, {"_id": 0})
    lang_script = projectform['LangScript'][1]
    # logger.debug(lang_script)
    all_audio = data_collection.find({"projectname": activeprojectname},
                                     {
        "_id": 0
        # "prompt.content": 1,
        # "audioId": 1
    })
    foundText = 'text not found in the '+str(data_collection)
    logger.debug('foundText: %s', foundText)
    for audio in all_audio:
        logger.debug("audio: %s", audio)
        speaker_id = audio['speakerId']
        logger.debug("speaker_id: %s", speaker_id)
        for lang, lang_info in audio["prompt"]["content"].items():
            logger.debug("lang: %s\nlang_info: %s", lang, lang_info)
            script = lang_script[lang]
            logger.debug("script: %s", script)
            for prompt_type, prompt_info in lang_info.items():
                if (prompt_type == 'text'):
                    for boundaryId in lang_info['text'].keys():
                        logger.debug("boundaryId: %s", boundaryId)
                        prompt_text = lang_info['text'][boundaryId]['textspan'][script].strip(
                        )

                        if (text == prompt_text and speaker_id == ''):
                            foundText = "text found but audio already available"
                            logger.debug('foundText: %s', foundText)
                            # audioId = audio['audioId'
                            audioId = copyofaudiodata(data_collection, audio)
                            if audioId not in exclude:
                                logger.debug("audio: %s", audio)
                                logger.debug(
                                    "prompt_text: %s\naudioId: %s", prompt_text, audioId)
                                return (audioId, '')
                elif (prompt_type == 'audio'):
                    for boundaryId in lang_info['audio']['textGrid']['sentence'].keys():
                        logger.debug("boundaryId: %s", boundaryId)
                        prompt_text = lang_info['audio']['textGrid']['sentence'][boundaryId]['transcription'][script].strip(
                        )
                        if (text == prompt_text):
                            logger.debug(
                                'prompt_text: %s\nspeaker_id: %s\naudio["speakerId"]: %s', prompt_text, speaker_id, audio['speakerId'])
                        if (text == prompt_text and speaker_id == ''):
                            foundText = "text found but audio already available"
                            logger.debug('foundText: %s', foundText)
                            # audioId = audio['audioId']
                            audioId = copyofaudiodata(data_collection, audio)
                            if audioId not in exclude:
                                logger.debug("audio: %s", audio)
                                logger.debug(
                                    "prompt_text: %s\naudioId: %s", prompt_text, audioId)
                                return (audioId, '')
                elif (prompt_type == 'image'):
                    pass
                elif (prompt_type == 'multimedia'):
                    pass
    logger.debug('foundText: %s', foundText)

    return ('False', foundText)


def copyofaudiodata(data_collection,
                    audio_data):
    audio_id = 'A'+re.sub(r'[-: \.]', '', str(datetime.now()))
    audio_data['audioId'] = audio_id

    data_collection_doc_id = data_collection.insert_one(audio_data)

    return audio_id


def addedspeakerids(speakerdetails,
                    activeprojectname):
    # logger.debug('addedspeakerids')
    all_speaker_ids = speakerdetails.find({"projectname": activeprojectname, "isActive": 1},
                                          {"_id": 0, "lifesourceid": 1})
    added_speaker_ids = []
    for speaker_id in all_speaker_ids:
        s_id = speaker_id["lifesourceid"]
        added_speaker_ids.append(s_id)
    # logger.debug ("Added Speaker IDS", added_speaker_ids)
    return added_speaker_ids


def getaudiometadata(data_collection, audio_id):
    """get the audi metadata details of the audio file

    Args:
        data_collection (_type_): _description_
        file_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    audio_metadata_details = dict({'audioMetadata': ''})
    audio_metadata = data_collection.find_one(
        {'audioId': audio_id}, {'_id': 1, 'audioMetadata': 1})
    # logger.debug(audio_metadata)
    if audio_metadata is not None and 'audioMetadata' in audio_metadata:
        audio_metadata_details['audioMetadata'] = audio_metadata['audioMetadata']

    return audio_metadata_details


def lastupdatedby(transcriptions, audio_id):
    """get the transcription last updated by

    Args:
        transcriptions (_type_): _description_
        file_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    last_updated_by_details = dict({'updatedBy': ''})
    last_updated_by = transcriptions.find_one(
        {'audioId': audio_id}, {'_id': 1, 'updatedBy': 1})
    # logger.debug(last_updated_by)
    if last_updated_by is not None and 'updatedBy' in last_updated_by:
        last_updated_by_details['updatedBy'] = last_updated_by['updatedBy']

    return last_updated_by_details


def merge_boundary_with_next(current_end, next_start, span_start, span_end, max_pause, max_boundary_size):
    return ((next_start-current_end) <= max_pause) and ((span_end-span_start) <= max_boundary_size)


def get_new_boundaries(boundaries, max_pause, max_boundary_size=-1, include_transcription=False, transcriptions=None):
    new_boundaries = []
    new_transcriptions = []

    if max_boundary_size == -1:
        max_boundary_size = boundaries[-1]['end']

    span_start = 0
    span_end = 0
    logger.debug('Initial total boundaries', len(boundaries))
    logger.debug('Initial boundary', boundaries[0])
    # logger.debug('Second boundary', boundaries[1])
    # logger.debug('Initial end boundary', boundaries[-1])
    # logger.debug('Initial second end boundary', boundaries[-2:-5])

    if len(boundaries) > 1:
        for i in range(len(boundaries)-1):
            if include_transcription:
                current_transcription = transcriptions[i]

            current_boundary = boundaries[i]
            next_boundary = boundaries[i+1]
            current_start = current_boundary['start']
            # logger.debug(i, 'out of', len(boundaries), current_boundary)
            # logger.debug(i+1, 'out of', len(boundaries), next_boundary)

            if i == 0 or reset_start:
                span_start = current_start
                reset_start = False

                if include_transcription:
                    span_transcription = current_transcription

            current_end = current_boundary['end']
            next_start = next_boundary['start']

            if i == len(boundaries)-2:
                span_end = next_boundary['end']
            else:
                span_end = current_end

            if merge_boundary_with_next(current_end, next_start, span_start, span_end, max_pause, max_boundary_size):
                if i == len(boundaries) - 2:
                    new_boundaries.append({
                        'start': span_start,
                        'end': span_end
                    })
                    reset_start = True

                    if include_transcription:
                        span_transcription = span_transcription + ' ' + \
                            current_transcription + ' ' + transcriptions[i+1]
                        new_transcriptions.append(span_transcription)
                        span_transcription = ''
                else:
                    if include_transcription:
                        span_transcription = span_transcription + ' ' + current_transcription
                continue
            else:
                new_boundaries.append({
                    'start': span_start,
                    'end': span_end
                })
                reset_start = True

                if include_transcription:
                    new_transcriptions.append(span_transcription)
                    span_transcription = ''
    else:
        current_boundary = boundaries[0]

        new_boundaries.append({
            'start': current_boundary['start'],
            'end': current_boundary['end']
        })
        reset_start = True

        if include_transcription:
            new_transcriptions.append(transcriptions[0])
            span_transcription = ''

    logger.debug('Final total boundaries', len(new_boundaries))
    logger.debug('Final start', new_boundaries[0])
    logger.debug('Final end', new_boundaries[-1])

    if include_transcription:
        return new_boundaries, new_transcriptions
    else:
        return new_boundaries


def update_text_grid(mongo, text_grid, new_boundaries, transcription_type, include_transcription=False, transcriptions={}):
    logger.debug('Data type', transcription_type)

    # if include_transcription:
    #     transcription_scripts = list(transcriptions.keys())

    transcription_scripts = get_current_transcription_langscripts(mongo)
    logger.debug('All transcription lang scripts', transcription_scripts)

    translation_langscripts = get_current_translation_langscripts(mongo)
    logger.debug('All translation lang scripts', translation_langscripts)

    # logger.debug('Boundaries to update text grid', new_boundaries)
    logger.debug('Total expected boundaries', len(new_boundaries))
    logger.debug('Input Text Grid', text_grid)

    for i in range(len(new_boundaries)):
        current_boundary = new_boundaries[i]
        start_boundary = current_boundary['start']
        end_boundary = current_boundary['end']
        boundary_id_start = str(start_boundary).replace('.', '')[:4]
        boundary_id_end = str(end_boundary).replace('.', '')[:4]
        boundary_id = boundary_id_start+boundary_id_end

        text_grid[transcription_type][boundary_id] = {}
        text_grid[transcription_type][boundary_id]['start'] = float(
            start_boundary)
        text_grid[transcription_type][boundary_id]['end'] = float(
            end_boundary)
        text_grid[transcription_type][boundary_id]['speakerId'] = ""
        text_grid[transcription_type][boundary_id]['sentenceId'] = ""

        if transcription_type == 'sentence':
            text_grid[transcription_type][boundary_id]['tags'] = ""

        for langscript_code, script_name in transcription_scripts.items():
            if include_transcription and script_name in transcriptions:
                text_grid[transcription_type][boundary_id]['transcription'] = {
                    script_name: transcriptions[script_name][i]}
            else:
                text_grid[transcription_type][boundary_id]['transcription'] = {
                    script_name: ""}

            text_grid[transcription_type][boundary_id]['sentencemorphemicbreak'] = {
                script_name: ""}
            text_grid[transcription_type][boundary_id]['morphemes'] = {
                script_name: ""}
            text_grid[transcription_type][boundary_id]['gloss'] = {
                script_name: ""}
        if (len(translation_langscripts) != 0):
            for langscript_code, script_name in translation_langscripts.items():
                text_grid[transcription_type][boundary_id]['translation'] = {
                    langscript_code: ""}
        else:
            text_grid[transcription_type][boundary_id]['translation'] = {}

            # text_grid[boundary_id_key+'.transcription'] = ""

            # logger.debug(f"========Current Text Grid(%i)================", i)
            # logger.debug(text_grid)

    return text_grid


def generate_text_grid_without_transcriptions(
        mongo, text_grid, boundaries, transcription_type, max_pause):

    new_boundaries = get_new_boundaries(
        boundaries, max_pause)

    text_grid = update_text_grid(
        mongo, text_grid, new_boundaries, transcription_type)

    return text_grid


def generate_text_grid_with_transcriptions(
        mongo, text_grid, boundaries, transcriptions, transcription_type, max_pause):

    new_boundaries, new_transcriptions = get_new_boundaries(
        boundaries, max_pause, transcription=True, transcriptions=transcriptions)

    text_grid = update_text_grid(
        mongo, text_grid, new_boundaries, transcription_type, include_transcription=True, transcriptions=new_transcriptions)

    return text_grid


# def generate_sentence_text_grid(
#         text_grid, boundaries, transcriptions, max_pause):

#     if len(transcriptions) == 0:
#         text_grid = generate_sentence_text_grid_without_transcriptions(
#             text_grid, boundaries, max_pause)
#     else:
#         text_grid = generate_sentence_text_grid_with_transcriptions(
#             text_grid, boundaries, transcriptions, max_pause)

#     return text_grid


def generate_text_grid(mongo, text_grid, boundaries, transcriptions, transcription_type, max_pause):
    logger.debug('Type of the data', transcription_type)
    if len(transcriptions) == 0:
        text_grid = generate_text_grid_without_transcriptions(
            mongo, text_grid, boundaries, transcription_type, max_pause)
    else:
        text_grid = generate_text_grid_with_transcriptions(
            mongo, text_grid, boundaries, transcriptions, transcription_type, max_pause)
    # if transcription_type == "sentence":
    #     text_grid = generate_sentence_text_grid(
    #         text_grid, boundaries, transcriptions, max_pause)
    return text_grid


def get_smaller_chunks_of_audio(
    boundaries, max_pause, max_new_file_duration, audio_duration
):
    new_audio_chunks = get_new_boundaries(
        boundaries, max_pause, max_boundary_size=max_new_file_duration)
    new_audio_chunks[0]['start'] = 0
    new_audio_chunks[-1]['end'] = audio_duration

    return new_audio_chunks


def get_boundary_lists_of_smaller_chunks(
        audio_chunk_boundaries, boundaries):
    all_chunk_boundaries = []
    for audio_chunk_boundary in audio_chunk_boundaries:
        current_chunk_boundary_start = audio_chunk_boundary['start']
        current_chunk_boundary_end = audio_chunk_boundary['end']
        boundary_start_index = boundaries.index(current_chunk_boundary_start)
        boundary_end_index = boundaries.index(current_chunk_boundary_end)+1
        all_chunk_boundaries.append(
            boundaries[boundary_start_index: boundary_end_index])
    return all_chunk_boundaries


def get_current_translation_langscripts(mongo):
    userprojects, projectsform = getdbcollections.getdbcollections(
        mongo, 'userprojects', 'projectsform')
    current_username = getcurrentusername.getcurrentusername()
    logger.debug('USERNAME: ', current_username)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)

    current_project_scripts = projectsform.find_one({'projectname': activeprojectname}, {
        'Translation Script': 1, 'Translation Language': 1, '_id': 0})

    try:
        translations_langs = current_project_scripts['Translation Language']
        translation_scripts = current_project_scripts['Translation Script']

        scriptCodeJSONFilePath = os.path.join(
            basedir_parent, 'static/json/scriptCode.json')
        langScriptJSONFilePath = os.path.join(
            basedir_parent, 'static/json/langScript.json')

        scriptCode = readJSONFile.readJSONFile(scriptCodeJSONFilePath)
        langScript = readJSONFile.readJSONFile(langScriptJSONFilePath)

        all_lang_scripts = {}
        for current_lang, current_script in zip(translations_langs, translation_scripts):
            current_script_code = scriptCode[current_script]
            current_language_code = current_lang[0][:3].lower()
            langscript_code = current_language_code + '-' + current_script_code
            all_lang_scripts[langscript_code] = langscript_code
        return all_lang_scripts
    except Exception as error:
        logger.debug(error)
        return dict()


def get_current_transcription_langscripts(mongo):
    userprojects, projectsform = getdbcollections.getdbcollections(
        mongo, 'userprojects', 'projectsform')
    current_username = getcurrentusername.getcurrentusername()
    logger.debug('USERNAME: ', current_username)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)

    current_project_scripts = projectsform.find_one({'projectname': activeprojectname}, {
        'Transcription Script': 1, 'Sentence Language': 1, '_id': 0})

    project_language = current_project_scripts['Sentence Language']
    project_language_code = project_language[0][:3].lower()

    project_scripts = current_project_scripts['Transcription Script']

    scriptCodeJSONFilePath = os.path.join(
        basedir_parent, 'static/json/scriptCode.json')
    langScriptJSONFilePath = os.path.join(
        basedir_parent, 'static/json/langScript.json')

    scriptCode = readJSONFile.readJSONFile(scriptCodeJSONFilePath)
    langScript = readJSONFile.readJSONFile(langScriptJSONFilePath)

    all_lang_scripts = {}
    for current_script in project_scripts:
        current_script_code = scriptCode[current_script]
        langscript_code = project_language_code + '-' + current_script_code
        all_lang_scripts[langscript_code] = current_script
        return all_lang_scripts


def get_audio_transcriptions(mongo, model_params):
    transcriptions = {}
    transcribed = 0
    # transcription_scripts = []
    current_lang_scripts = get_current_transcription_langscripts(mongo)
    logger.debug('All current lang scripts', current_lang_scripts)

    for transcription_model in all_model_names['transcription']:
        target = transcription_model['target']
        # target_val = current_lang_scripts[target]
        if target in current_lang_scripts:
            target_val = current_lang_scripts[target]
            if target_val not in transcriptions:
                model_names = transcription_model['model']['local']
                model_path = transcription_model['model']['localpath']
                model_params['model_path'] = model_path

                if len(model_names) > 0:
                    transcriptions[target_val] = predictFromLocalModels.getTranscription(
                        model_names[0], model_params)
                    transcribed = 1

    return transcriptions, transcribed


def get_audio_boundaries(model_params):
    for textgrid_boundary_model in all_model_names['textGrid_boundary']:
        model_names = textgrid_boundary_model['model']['local']
        model_path = textgrid_boundary_model['model']['localpath']
        model_params['model_path'] = model_path

        if len(model_names) > 0:
            boundaries, cleaned_file = predictFromLocalModels.get_boundaries(
                model_names[0], model_params)
            break
    return boundaries, cleaned_file


def get_slices_and_text_grids(mongo,
                              run_vad,
                              run_asr,
                              split_into_smaller_chunks,
                              vad_model,
                              asr_model,
                              audio_path,
                              transcription_type,
                              max_pause_boundary,
                              max_pause_slice,
                              max_new_file_duration,
                              audio_duration):
    all_text_grids = [{
        "discourse": {},
        "sentence": {},
        "word": {},
        "phoneme": {}
    }]

    boundaries = None
    transcriptions = None
    transcribed = 0

    # TODO: This needs to be improved and based on user-inputs regarding the choice
    # of a model. We could store project-specific prefeerences here.
    # Currently it gives preference to local models and select the first
    # model in the list.
    if run_vad or run_asr or split_into_smaller_chunks:
        if 'textGrid_boundary' in all_model_names:
            model_params = {
                "audio_file": audio_path,
                "SAMPLING_RATE": 16000,
                "remove_pauses": False,
                "USE_ONNX": False
            }
            boundaries, cleaned_file = get_audio_boundaries(
                model_params)

        if run_asr and 'transcription' in all_model_names:
            model_params = {
                "audio_file": audio_path,
                "boundaries": boundaries
            }

            transcriptions, transcribed = get_audio_transcriptions(
                mongo, model_params)

        # logger.debug('Boundaries received', boundaries)
        if split_into_smaller_chunks:
            audio_chunk_boundaries = get_smaller_chunks_of_audio(
                boundaries, max_pause_slice, max_new_file_duration, audio_duration)

            audio_chunk_boundary_lists = get_boundary_lists_of_smaller_chunks(
                audio_chunk_boundaries, boundaries)

        else:
            audio_chunk_boundaries = [
                {'start': boundaries[0], 'end': boundaries[-1]}]
            audio_chunk_boundary_lists = boundaries

        for audio_chunk_boundary_list in audio_chunk_boundary_lists:
            all_text_grids.append(generate_text_grid(
                mongo, audio_chunk_boundary_list, audio_chunk_boundary_list, transcriptions, transcription_type, max_pause_boundary))

    return audio_chunk_boundaries, all_text_grids, transcribed


def save_audio_in_mongo_and_localFs(mongo,
                                    updated_audio_filename,
                                    new_audio_file,
                                    audio_id,
                                    projectowner,
                                    activeprojectname,
                                    current_username,
                                    audio_store_path='',
                                    audio_store_dir='',
                                    store_in_local=False,
                                    store_in_mongo=True):

    if store_in_mongo:
        fs_file_id = mongo.save_file(updated_audio_filename,
                                     new_audio_file,
                                     audioId=audio_id,
                                     username=projectowner,
                                     projectname=activeprojectname,
                                     updatedBy=current_username,
                                     filedeleteFLAG=0)
    else:
        fs_file_id = ''

    # logger.debug('audioLength', new_audio_file['audiofile'].content_length)

    # logger.debug('json_basedir', json_basedir)

    # # audiowaveform_json_path = os.path.join(audiowaveform_json, 'audiowaveform_json')

    # logger.debug('audiowaveform_json', audiowaveform_json)
    # logger.debug('audiowaveform_json_path', audiowaveform_json_path)

    # logger.debug('new_audio_file', type(new_audio_file), new_audio_file)
    # audiowaveform_file = new_audio_file.stream.seek(0)
    # audiowaveform_file.stream.seek(0)
    # getaudiofilefromfs(mongo,
    #                 audiowaveform_json,
    #                 audio_id,
    #                 'audio')

    if store_in_local:
        saved_path = getaudiowaveformfilefromfs(mongo,
                                                audio_store_path,
                                                audio_store_dir,
                                                audio_id,
                                                'audioId')
        logger.debug('Audio saved path', saved_path)
    else:
        saved_path = ''

    return fs_file_id, saved_path


def get_audio_id_filename(audiofile, audio_filename="no_filename"):
    if audiofile['audiofile'].filename != '':
        audio_filename = audiofile['audiofile'].filename
    audio_id = 'A'+re.sub(r'[-: \.]', '', str(datetime.now()))
    # audio_filename = audio_id+

    return audio_id, audio_filename


def get_audio_waveform_json(audiowaveform_json, json_dir, audio_filename):
    audiowaveform_audio_path = os.path.join(
        audiowaveform_json, json_dir)
    audiowaveform_json_path = os.path.join(audiowaveform_json, json_dir)
    audiowaveform_audio_path = os.path.join(
        audiowaveform_audio_path, audio_filename)
    # logger.debug('audiowaveform_audio_path', audiowaveform_audio_path)
    # logger.debug('audiowaveform_json_path', audiowaveform_json_path)
    audiowaveform_json = createaudiowaveform(
        audiowaveform_audio_path, audiowaveform_json_path, audio_filename)

    return audiowaveform_json


def delete_one_audio_file(projects_collection,
                          transcriptions_collection,
                          project_name,
                          current_username,
                          active_speaker_id,
                          audio_id,
                          update_latest_audio_id=1):
    try:
        logger.debug("project_name: %s, audio_id: %s", project_name, audio_id)
        transcription_doc_id = transcriptions_collection.find_one_and_update({
            "projectname": project_name,
            "audioId": audio_id
        },
            {"$set": {"audiodeleteFLAG": 1}},
            projection={'_id': True},
            return_document=ReturnDocument.AFTER)['_id']
        logger.debug('DELETED transcription_doc_id: %s, %s',
                     transcription_doc_id, type(transcription_doc_id))

        if (update_latest_audio_id):
            latest_audio_id = getnewaudioid(projects_collection,
                                            project_name,
                                            audio_id,
                                            active_speaker_id,
                                            'next')
            updatelatestaudioid(projects_collection,
                                project_name,
                                latest_audio_id,
                                current_username,
                                active_speaker_id)

        projects_collection.update_one({"projectname": project_name},
                                       {"$pull": {"speakersAudioIds."+active_speaker_id: audio_id},
                                        "$addToSet": {"speakersAudioIdsDeleted."+active_speaker_id: audio_id}
                                        })
    except:
        logger.exception("")
        transcription_doc_id = False

    return transcription_doc_id


def get_audio_delete_flag(transcriptions_collection,
                          project_name,
                          audio_id):
    logger.debug("%s, %s, %s", transcriptions_collection,
                 project_name,
                 audio_id)
    audio_delete_flag = transcriptions_collection.find_one({"projectname": project_name,
                                                            "audioId": audio_id},
                                                           {"_id": 0,
                                                            "audiodeleteFLAG": 1})["audiodeleteFLAG"]

    return audio_delete_flag


def revoke_deleted_audio(projects_collection,
                         transcriptions_collection,
                         project_name,
                         active_speaker_id,
                         audio_id):
    try:
        logger.debug("project_name: %s, audio_id: %s", project_name, audio_id)
        transcription_doc_id = transcriptions_collection.find_one_and_update({
            "projectname": project_name,
            "audioId": audio_id
        },
            {"$set": {"audiodeleteFLAG": 0}},
            projection={'_id': True},
            return_document=ReturnDocument.AFTER)['_id']
        logger.debug('REVOKED transcription_doc_id: %s, %s',
                     transcription_doc_id, type(transcription_doc_id))

        projects_collection.update_one({"projectname": project_name},
                                       {"$pull": {"speakersAudioIdsDeleted."+active_speaker_id: audio_id},
                                        "$addToSet": {"speakersAudioIds."+active_speaker_id: audio_id}
                                        })
    except:
        logger.exception("")
        transcription_doc_id = False

    return transcription_doc_id


def get_n_audios(data_collection,
                 activeprojectname,
                 active_speaker_id,
                 start_from=0,
                 number_of_audios=10,
                 audio_delete_flag=0):
    aggregate_output = data_collection.aggregate([
        {
            "$match": {
                "projectname": activeprojectname,
                "speakerId": active_speaker_id,
                "audiodeleteFLAG": audio_delete_flag
            }
        },
        {
            "$sort": {
                "audioId": 1
            }
        },
        {
            "$project": {
                "_id": 0,
                "audioId": 1,
                "audioFilename": 1
            }
        }
    ])
    # logger.debug("aggregate_output: %s", aggregate_output)
    aggregate_output_list = []
    for doc in aggregate_output:
        # logger.debug("aggregate_output: %s", pformat(doc))
        aggregate_output_list.append(doc)
    # logger.debug('aggregate_output_list: %s', pformat(aggregate_output_list))
    total_records = len(aggregate_output_list)
    # logger.debug('total_records AUDIO: %s', total_records)

    return (total_records,
            aggregate_output_list[start_from:number_of_audios])
