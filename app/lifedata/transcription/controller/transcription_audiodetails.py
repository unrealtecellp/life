# 9d4fd99c7dfb7f00387d1df113ce1c428cb53909
"""Module to save the uploaded audio file(s) from 'enternewsenteces' route."""

from app import mongo
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
from io import BytesIO
from app.controller import (
    getcommentstats,
    readJSONFile,
    getdbcollections,
    getcurrentusername,
    userdetails,
    getcurrentuserprojects,
    getactiveprojectname,
    getactiveprojectform,
    getprojecttype,
    life_logging,
    projectDetails
)
from app.lifemodels.controller import (
    predictFromAPI,
    predictFromLocalModels,
    huggingFaceUtils,
    modelManager
)

from app.languages.controller import (
    languageManager
)

import subprocess
import shutil
from pprint import pprint, pformat
from pymongo import ReturnDocument
import numpy as np

basedir = os.path.abspath(os.path.dirname(__file__))
basedir_parent = '/'.join(basedir.split('/')[:-3])

logger = life_logging.get_logger()
# logger.debug('Basedir parent', basedir_parent)
modelConfigPath = os.path.join(
    basedir_parent, 'jsonfiles/model_config.json')

# logger.debug('Modle config %s', modelConfigPath)

all_model_names = readJSONFile.readJSONFile(modelConfigPath)


allowed_file_formats = ['mp3', 'wav']


selected_audio_sorting_subcategory_self_map = {
    "agegroup": "ageGroup",
    "gender": "Gender",
    "educationlevel": "educationLevel",
    "educationmediumupto12": "educationMediumUpto12-list",
    "educationmediumafter12": "educationMediumAfter12-list",
    "speakerspeaklanguage": "Speaker Speak Language"
}

selected_audio_sorting_subcategory_new = {
    "ageGroup": "Age Group",
    "gender": "Gender",
    "educationLevel": "Education Level",
    "educationMediumUpto12-list": "Education Medium Upto 12",
    "educationMediumAfter12-list": "Education Medium After 12",
    "speakerspeaklanguage": "Speaker Speak Language"
}

# TODO: This should be saved in a separate document in MongoDB that will bind
# specific keys in database to specific models


# appConfigPath = os.path.join(basedir, 'jsonfiles/app_config.json')

# allowed_file_formats = get_allowed_file_formats()


def get_file_format(current_file):
    cur_filename = current_file.filename
    # logger.debug("Filename %s", cur_filename)
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
                   sourceId='',
                   run_vad=True,
                   run_asr=False,
                   split_into_smaller_chunks=True,
                   get_audio_json=True,
                   vad_model={},
                   asr_model={},
                   transcription_type='sentence',
                   boundary_threshold=0.3,
                   slice_threshold=0.9,
                   max_slice_size=120,
                   data_type="audio",
                   new_audio_details={},
                   prompt="",
                   update=False,
                   slice_offset_value=0.1,
                   min_boundary_size=2.0,
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
    try:
        # logger.debug("**kwargs: %s", kwargs)
        # return ('', '', '')
        atype = 'audiofile'
        # logger.debug ('New ques file %s', new_ques_file)
        file_states = []
        transcription_doc_ids = []
        fs_file_ids = []

        if new_audio_file[atype].filename != '':
            current_file = new_audio_file[atype]
            # logger.debug("Filepath %s", current_file)
            file_format = get_file_format(current_file)

            if (file_format in allowed_file_formats):
                file_state, transcription_doc_id, fs_file_id, transcription_data = saveoneaudiofile(mongo,
                                                                                                    projects,
                                                                                                    userprojects,
                                                                                                    transcriptions,
                                                                                                    projectowner,
                                                                                                    activeprojectname,
                                                                                                    current_username,
                                                                                                    speakerId,
                                                                                                    new_audio_file,
                                                                                                    sourceId,
                                                                                                    run_vad,
                                                                                                    run_asr,
                                                                                                    split_into_smaller_chunks,
                                                                                                    get_audio_json,
                                                                                                    vad_model,
                                                                                                    asr_model,
                                                                                                    transcription_type,
                                                                                                    boundary_threshold,
                                                                                                    slice_threshold,
                                                                                                    max_slice_size,
                                                                                                    data_type,
                                                                                                    new_audio_details,
                                                                                                    prompt,
                                                                                                    update,
                                                                                                    slice_offset_value,
                                                                                                    min_boundary_size,
                                                                                                    **kwargs)
                file_states.append(file_state)
                transcription_doc_ids.append(transcription_doc_id)
                fs_file_ids.append(fs_file_id)

            elif (file_format == 'zip'):
                # logger.debug('ZIP file format')
                file_states, transcription_doc_ids, fs_file_ids = savemultipleaudiofiles(mongo,
                                                                                         projects,
                                                                                         userprojects,
                                                                                         transcriptions,
                                                                                         projectowner,
                                                                                         activeprojectname,
                                                                                         current_username,
                                                                                         speakerId,
                                                                                         new_audio_file,
                                                                                         sourceId,
                                                                                         run_vad,
                                                                                         run_asr,
                                                                                         split_into_smaller_chunks,
                                                                                         get_audio_json,
                                                                                         vad_model,
                                                                                         asr_model,
                                                                                         transcription_type,
                                                                                         boundary_threshold,
                                                                                         slice_threshold,
                                                                                         max_slice_size,
                                                                                         data_type,
                                                                                         new_audio_details,
                                                                                         prompt,
                                                                                         update,
                                                                                         slice_offset_value,
                                                                                         min_boundary_size)
            else:
                return ([False], ['Unsupported file format'], ['File not stored'])
    except:
        logger.exception("")

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
                           sourceId='',
                           run_vad=True,
                           run_asr=False,
                           split_into_smaller_chunks=True,
                           get_audio_json=True,
                           vad_model={},
                           asr_model={},
                           transcription_type='sentence',
                           boundary_threshold=0.3,
                           slice_threshold=0.9,
                           max_slice_size=120,
                           data_type="audio",
                           new_audio_details={},
                           prompt="",
                           update=False,
                           slice_offset_value=0.1,
                           min_boundary_size=2.0,
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
    try:
        all_file_states = []
        transcription_doc_ids = []
        fs_file_ids = []
        new_audio_file = {}

        if all_audio_files['audiofile'].filename != '':
            zip_audio_files = all_audio_files['audiofile']

        try:
            with ZipFile(zip_audio_files) as myzip:
                # logger.debug('File list %s', myzip.namelist())
                for file_name in myzip.namelist():
                    # if (file_name.endswith('.wav')):
                    # logger.debug('Current File name %s', file_name)
                    with myzip.open(file_name) as myfile:
                        # file_format = get_file_format(myfile)
                        file_format = file_name.rsplit('.', 1)[-1].lower()
                        # logger.debug('File format during upload %s', file_format)
                        if file_format in allowed_file_formats:
                            # upload_file_full = {}
                            file_content = io.BytesIO(myfile.read())
                            # logger.debug ('ZIP file %s', mainfile)
                            # logger.debug ("File content %s", file_content)
                            # logger.debug ("Upload type 5s", fileType)
                            new_audio_file['audiofile'] = FileStorage(
                                file_content, filename=file_name)
                            file_state, transcription_doc_id, fs_file_id, transcription_data = saveoneaudiofile(mongo,
                                                                                                                projects,
                                                                                                                userprojects,
                                                                                                                transcriptions,
                                                                                                                projectowner,
                                                                                                                activeprojectname,
                                                                                                                current_username,
                                                                                                                speakerId,
                                                                                                                new_audio_file,
                                                                                                                sourceId,
                                                                                                                run_vad,
                                                                                                                run_asr,
                                                                                                                split_into_smaller_chunks,
                                                                                                                get_audio_json,
                                                                                                                vad_model,
                                                                                                                asr_model,
                                                                                                                transcription_type,
                                                                                                                boundary_threshold,
                                                                                                                slice_threshold,
                                                                                                                max_slice_size,
                                                                                                                data_type,
                                                                                                                new_audio_details,
                                                                                                                prompt,
                                                                                                                update,
                                                                                                                slice_offset_value,
                                                                                                                min_boundary_size)

                            all_file_states.append(file_state)
                            transcription_doc_ids.append(transcription_doc_id)
                            fs_file_ids.append(fs_file_id)
        except:
            logger.exception("")
            flash(f"ERROR")
            all_file_states.append(False)
            transcription_doc_ids.append('')
            fs_file_ids.append('')
            # return (False)
    except:
        logger.exception("")

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
                     vad_model={},
                     asr_model={},
                     transcription_type='sentence',
                     boundary_threshold=0.3,
                     slice_threshold=0.9,
                     max_slice_size=120,
                     data_type="audio",
                     new_audio_details={},
                     prompt="",
                     update=False,
                     slice_offset_value=0.1,
                     min_boundary_size=2.0,
                     ** kwargs):
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
        slice_offset_value: this is the amount of audio (in seconds) that is repeated / retained across different slices made by automatically slicing the audio into smaller chunks. This is added to the end and substracted from the beginning.
    """
    try:
        all_transcription_doc_ids = []
        all_audio_fs_file_ids = []

        all_audio_ids = []
        all_audio_filenames = []

        project_type = getprojecttype.getprojecttype(
            projects, activeprojectname)

        audiowaveform_json_dir_path = get_audio_dir_path()
        audio_json_parent_dir = 'audiowaveform'

        audiowaveform_file = new_audio_file['audiofile']
        audio_duration, full_audio_file = get_audio_duration_from_file(
            audiowaveform_file)
        audiowaveform_file.stream.seek(0)
        # full_audio_file_array = np.array(full_audio_file.get_array_of_samples())

        # Convert file to wav - takes care of files of other format as well
        audiowaveform_file = io.BytesIO()
        full_audio_file.export(audiowaveform_file, format='wav')

        if slice_offset_value > audio_duration:
            slice_offset_value = audio_duration

        split_into_smaller_chunks = is_split_into_smaller_chunks(
            audio_duration, max_slice_size)

        store_in_local = is_store_in_local(
            get_audio_json, run_vad, run_asr, split_into_smaller_chunks)

        # store_in_mongo = is_store_in_mongo(split_into_smaller_chunks)
        store_in_mongo = True

        new_audio_details = get_audio_doc_details(projectowner,
                                                  activeprojectname,
                                                  current_username,
                                                  speakerId,
                                                  sourceId,
                                                  data_type,
                                                  prompt,
                                                  new_audio_details,
                                                  update,
                                                  kwargs.items())

        logger.debug("new_audio_details: %s", pformat(new_audio_details))

        audio_id, audio_filename = get_audio_id_filename(new_audio_file)
        updated_audio_filename = (audio_id +
                                  '_' +
                                  audio_filename)

        logger.debug("**kwargs: %s", kwargs)
        for kwargs_key, kwargs_value in kwargs.items():
            # logger.debug("kwargs_key: %s, kwargs_value: %s",
            #              kwargs_key, kwargs_value)
            if (kwargs_key == 'derivedfromprojectdetails'):
                new_audio_details[kwargs_key] = kwargs_value
        # return ('', '', '')

        logger.debug("new_audio_details: %s", pformat(new_audio_details))

        # Save audio file in mongoDb and also get it in Local File System

        # if split_into_smaller_chunks:
        logger.debug('Audio Duration %s', str(audio_duration))
        logger.debug('Store in local %s, Store in Mongo %s, Get audio json %s',
                     store_in_local, store_in_mongo, get_audio_json)
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
        logger.debug("Audio File Path %s", audio_file_path)
        audio_chunks, transcription_data, text_grids, boundary_offset_values, slice_offset_values, transcriptionFLAG, model_details = get_slices_and_text_grids(mongo,
                                                                                                                                                                run_vad,
                                                                                                                                                                run_asr,
                                                                                                                                                                split_into_smaller_chunks,
                                                                                                                                                                vad_model,
                                                                                                                                                                asr_model,
                                                                                                                                                                audio_file_path,
                                                                                                                                                                transcription_type,
                                                                                                                                                                boundary_threshold,
                                                                                                                                                                slice_threshold,
                                                                                                                                                                max_slice_size,
                                                                                                                                                                min_boundary_size,
                                                                                                                                                                audio_duration,
                                                                                                                                                                slice_offset_value)

        # logger.debug('Final generated text grid %s', text_grids)
        logger.debug('Final transcription flag %s', transcriptionFLAG)
        logger.debug('Final text grid length %s', len(text_grids))
        logger.debug('Final boundary offset length %s',
                     len(boundary_offset_values))
        logger.debug('Slice Offset values %s', slice_offset_values)
        logger.debug('Model Details %s', model_details)
        # logger.debug('Final first two text grids %s', text_grids[:3])

        new_audio_details["transcriptionFLAG"] = transcriptionFLAG

        full_model_name = get_full_model_name(run_vad,
                                              run_asr,
                                              model_details.get(
                                                  'vad_model_name', ''),
                                              model_details.get('asr_model_name', ''))
        logger.debug('Model Details %s', model_details)

        if not split_into_smaller_chunks:
            all_audio_ids.append(audio_id)
            all_audio_filenames.append(audio_filename)
            all_audio_fs_file_ids.append(audio_fs_file_id)

            add_audio_doc_details(new_audio_details,
                                  get_audio_json,
                                  current_username,
                                  audio_id,
                                  updated_audio_filename,
                                  text_grids[0],
                                  audiowaveform_json_dir_path,
                                  audio_json_parent_dir,
                                  full_model_name,
                                  model_details,
                                  audio_duration=audio_duration,
                                  current_slice_duration=audio_duration
                                  )
            if update:
                transcription_doc_id = transcriptions.update_one({"audioId": audio_id},
                                                                 {"$set": new_audio_details})
            else:
                transcription_doc_id = transcriptions.insert_one(
                    new_audio_details)
            all_transcription_doc_ids.append(transcription_doc_id)

        else:

            # for i in range(len(text_grids)):
            for i, current_text_grid in enumerate(text_grids):
                # for current_text_gird in text_grids:
                current_audio_id = audio_id + '-slice'+(str(i).zfill(4))
                current_audio_filename = (current_audio_id +
                                          '_' +
                                          audio_filename)
                all_audio_ids.append(current_audio_id)
                all_audio_filenames.append(current_audio_filename)

                current_audio_chunk = audio_chunks[i]
                # current_slice_offset_value_begn = slice_offset_values[i]

                # current_audio_chunk_begn = current_audio_chunk['start']*1000

                if i > 0:
                    current_audio_chunk_begn = boundary_offset_values[i]*1000
                    # current_audio_chunk_begn = current_audio_chunk_begn - \
                    #     current_slice_offset_value_begn
                    # delete_previous = False
                else:
                    current_audio_chunk_begn = 0.0
                    # delete_previous = True

                current_audio_chunk_end = current_audio_chunk['end']*1000

                if (i == len(text_grids)-1):
                    current_slice_offset_value_end = 0.0
                    current_audio_chunk_end = audio_duration*1000
                elif (i < len(text_grids)-1):
                    # next_audio_chunk_start = audio_chunks[i+1]['start']*1000
                    # chunk_distance = next_audio_chunk_start - current_audio_chunk_end
                    # current_audio_chunk_end = current_audio_chunk_end + \
                    #     ((slice_offset_value*1000) + float(chunk_distance/2))
                    current_slice_offset_value_end = slice_offset_values[i+1]*1000
                    current_audio_chunk_end = current_audio_chunk_end + current_slice_offset_value_end
                    # current_audio_chunk_end = boundary_offset_values[i+1]*1000
                    # logger.debug('Slice based end: %s',
                    #              (slice_offset_values[i+1]*1000)+(current_audio_chunk_end))

                    # current_audio_chunk_end = audio_chunks[i+1]['start']*1000

                    logger.debug('Actual end %s', current_audio_chunk_end)
                else:
                    current_audio_chunk_end = current_audio_chunk_end + \
                        (slice_offset_value*1000)

                logger.debug('Current chunk: %s \tTotal chunks:%s, \tCurrent chunk begin:%s, \tCurrent chunk end: %s \tAudio end: %s', i, len(
                    text_grids), current_audio_chunk_begn, current_audio_chunk_end, audio_duration*1000)

                current_audio_file = full_audio_file[current_audio_chunk_begn: current_audio_chunk_end]
                current_slice_duration = current_audio_file.duration_seconds
                # current_audio_file_array = full_audio_file_array[
                #     int(current_audio_chunk_begn): int(current_audio_chunk_end)]

                # audio_exp_length = current_audio_chunk_end - current_audio_chunk_begn
                # audio_actual_length = current_audio_file.duration_seconds
                # logger.debug('Audio expected length: %s \tAudio Clip Actual Length: %s', audio_exp_length, audio_actual_length
                #              )

                # current_audio_segment_array = pydub.AudioSegment(current_audio_file_array.tobytes(
                # ), frame_rate=full_audio_file.frame_rate, sample_width=full_audio_file.sample_width, channels=1)
                # audio_array_length = current_audio_segment_array.duration_seconds
                # logger.debug('Audio expected length: %s \tAudio Clip Array Length: %s', audio_exp_length, audio_array_length
                #              )
                audio_segment_bytes = BytesIO()
                current_audio_file.export(audio_segment_bytes, format="wav")
                current_audio_file_segment = FileStorage(
                    audio_segment_bytes, filename=current_audio_filename)

                # current_text_grid = text_grids[i]
                current_audio_details = json.loads(
                    json.dumps(new_audio_details))
                current_audio_fs_file_id, current_audio_file_path = save_audio_in_mongo_and_localFs(mongo,
                                                                                                    current_audio_filename,
                                                                                                    current_audio_file_segment,
                                                                                                    current_audio_id,
                                                                                                    projectowner,
                                                                                                    activeprojectname,
                                                                                                    current_username,
                                                                                                    audiowaveform_json_dir_path,
                                                                                                    audio_json_parent_dir,
                                                                                                    store_in_local=store_in_local,
                                                                                                    store_in_mongo=True)
                all_audio_fs_file_ids.append(current_audio_fs_file_id)

                add_audio_doc_details(current_audio_details,
                                      get_audio_json,
                                      current_username,
                                      current_audio_id,
                                      current_audio_filename,
                                      current_text_grid,
                                      audiowaveform_json_dir_path,
                                      audio_json_parent_dir,
                                      full_model_name,
                                      model_details,
                                      current_slice_number=i,
                                      total_slices=len(text_grids),
                                      boundary_offset_value=boundary_offset_values[i],
                                      slice_offset_value=current_slice_offset_value_end,
                                      slice_overlap_region=slice_offset_value,
                                      audio_duration=audio_duration,
                                      current_slice_duration=current_slice_duration,
                                      original_audio_id=audio_id
                                      )

                if update:
                    transcription_doc_id = transcriptions.update_one({"audioId": audio_id},
                                                                     {"$set": current_audio_details})
                else:
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
                                 speaker_audio_ids,
                                 existing_speaker_ids=[])

        # Update active speaker ID in user projects
        update_active_speaker_Id(userprojects,
                                 activeprojectname,
                                 current_username,
                                 speakerId
                                 )
        # logger.debug('new_audio_file %s, %s', type(new_audio_file), new_audio_file)
        # transcription_doc_id = transcriptions.insert(new_audio_details)
        # save audio file details in fs collection

        # logger.debug('audiowaveform_audio_path %s', audiowaveform_audio_path)
        # audiowaveform_audio_path = os.path.join(audiowaveform_audio_path, updated_audio_filename)
    except:
        logger.exception("")

    return (True, all_transcription_doc_ids, all_audio_fs_file_ids, transcription_data)

    # except Exception as e:
    #     logger.debug(e)
    #     flash(f"ERROR")
    #     return (False, '', '')


def save_boundaries_of_one_audio_file(mongo,
                                      projects,
                                      userprojects,
                                      transcriptions,
                                      projectowner,
                                      activeprojectname,
                                      current_username,
                                      audio_filename,
                                      audio_duration,
                                      sourceId='',
                                      run_vad=True,
                                      run_asr=False,
                                      split_into_smaller_chunks=True,
                                      get_audio_json=True,
                                      vad_model={},
                                      asr_model={},
                                      transcription_type='sentence',
                                      boundary_threshold=0.3,
                                      slice_threshold=0.9,
                                      max_slice_size=150,
                                      min_boundary_size=2.0,
                                      save_for_user=False,
                                      hf_token='',
                                      audio_details={},
                                      create_boundaries=False,
                                      accessed_time='',
                                      boundary_ids=['*'],
                                      **kwargs):

    audio_details_dict = {}

    audio_id = audio_filename.split('_')[0]
    # if get_audio_json:
    audiowaveform_json_dir_path = get_audio_dir_path()
    audio_json_parent_dir = 'audiowaveform'
    # logger.debug("Existing audio data %s", audio_details)
    # logger.debug("Current username %s", current_username)
    if current_username in audio_details:
        text_grid = [audio_details[current_username]['textGrid']]
    else:
        # text_grid = [get_blank_text_grid()]
        text_grid = []
        save_for_user = True
    logger.info('Current user existing text grids %s', text_grid)

    audio_file_path = getaudiowaveformfilefromfs(mongo,
                                                 audiowaveform_json_dir_path,
                                                 audio_json_parent_dir,
                                                 audio_id,
                                                 'audioId'
                                                 )

    audio_chunks, transcription_data, text_grids, boundary_offset_values, slice_offset_values, transcriptionFLAG, model_details = get_slices_and_text_grids(mongo,
                                                                                                                                                            run_vad,
                                                                                                                                                            run_asr,
                                                                                                                                                            split_into_smaller_chunks,
                                                                                                                                                            vad_model,
                                                                                                                                                            asr_model,
                                                                                                                                                            audio_file_path,
                                                                                                                                                            transcription_type,
                                                                                                                                                            boundary_threshold,
                                                                                                                                                            slice_threshold,
                                                                                                                                                            max_slice_size,
                                                                                                                                                            min_boundary_size,
                                                                                                                                                            audio_duration,
                                                                                                                                                            hf_token=hf_token,
                                                                                                                                                            all_audio_bytes={},
                                                                                                                                                            all_text_grids=text_grid,
                                                                                                                                                            create_new_boundaries=create_boundaries,
                                                                                                                                                            boundary_ids=boundary_ids)

    # logger.debug('Final generated text grid %s', text_grids)
    logger.debug('Final transcription flag %s', transcriptionFLAG)
    logger.debug('Final text grid length %s', len(text_grids))
    logger.debug('Final boundary offset length %s',
                 len(boundary_offset_values))
    logger.debug('Model Details %s', model_details)
    # logger.debug('Final first two text grids %s', text_grids[:3])

    audio_details_dict["transcriptionFLAG"] = transcriptionFLAG
    full_model_name = get_full_model_name(run_vad,
                                          run_asr,
                                          model_details.get(
                                              'vad_model_name', ''),
                                          model_details.get('asr_model_name', ''))

    add_text_grid(audio_details_dict,
                  current_username,
                  text_grids[0],
                  full_model_name,
                  model_details,
                  save_for_user=save_for_user)

    if get_audio_json:
        add_waveform_json(audio_details_dict,
                          audiowaveform_json_dir_path,
                          audio_json_parent_dir,
                          audio_filename)

    transcription_doc_id = save_text_grid_into_transcription(transcriptions,
                                                             activeprojectname,
                                                             current_username,
                                                             audio_id,
                                                             audio_details_dict,
                                                             accessed_time)

    # transcription_doc_id = transcriptions.update_one({"projectname": activeprojectname, "audioId": audio_id},
    #  {"$set": audio_details_dict})

    return transcription_doc_id, transcription_data


def delete_all_boundaries_of_one_audio_file(mongo,
                                            projects,
                                            userprojects,
                                            transcriptions,
                                            projectowner,
                                            activeprojectname,
                                            current_username,
                                            audio_filename,
                                            ** kwargs):

    audio_details_dict = {}
    blank_text_grid = get_blank_text_grid()
    audio_id = audio_filename.split('_')[0]
    # if get_audio_json:
    # logger.debug('Final first two text grids %s', text_grids[:3])

    audio_details_dict["transcriptionFLAG"] = 0

    add_text_grid(audio_details_dict,
                  current_username,
                  blank_text_grid,
                  '',
                  {})

    transcription_doc_id = transcriptions.update_one({"projectname": activeprojectname, "audioId": audio_id},
                                                     {"$set": audio_details_dict})

    return transcription_doc_id


def add_audio_doc_details(audio_details_dict,
                          get_audio_json,
                          current_username,
                          audio_id,
                          updated_audio_filename,
                          text_grid,
                          audiowaveform_json_dir_path,
                          audio_json_parent_dir,
                          model_name,
                          model_metadata,
                          current_slice_number=0,
                          total_slices=1,
                          boundary_offset_value=0.0,
                          slice_offset_value=0.0,
                          slice_overlap_region=0.0,
                          audio_duration=0.0,
                          current_slice_duration=0.0,
                          original_audio_id=""
                          ):
    audio_details_dict['audioId'] = audio_id
    audio_details_dict['audioFilename'] = updated_audio_filename

    if original_audio_id == "":
        original_audio_id = audio_id

    add_additional_info(audio_details_dict,
                        current_slice_number,
                        total_slices,
                        boundary_offset_value,
                        slice_offset_value,
                        slice_overlap_region,
                        original_audio_id
                        )

    add_audio_metadata(audio_details_dict,
                       audio_duration,
                       current_slice_duration)

    add_text_grid(audio_details_dict,
                  current_username,
                  text_grid,
                  model_name,
                  model_metadata)

    if get_audio_json:
        add_waveform_json(audio_details_dict,
                          audiowaveform_json_dir_path,
                          audio_json_parent_dir,
                          updated_audio_filename)

    audio_details_dict['createdby'] = current_username
    audio_details_dict['createdat'] = datetime.now().strftime(
        "%d/%m/%y %H:%M:%S")
    audio_details_dict['allAccess'] = {}
    audio_details_dict['allUpdate'] = {}


def add_audio_metadata(audio_details_dict,
                       audio_duration,
                       current_slice_duration):
    if 'audioMetadata' in audio_details_dict:
        audio_details_dict['audioMetadata'].update([
            ('audioDuration', audio_duration), ('currentSliceDuration', current_slice_duration)])
    else:
        audio_details_dict['audioMetadata'] = {
            'audioDuration': audio_duration, 'currentSliceDuration': current_slice_duration}


def add_additional_info(audio_details_dict,
                        current_slice_number,
                        total_slices,
                        boundary_offset_value,
                        slice_offset_value,
                        slice_overlap_region,
                        original_audio_id):
    if 'additionalInfo' in audio_details_dict:
        audio_details_dict['additionalInfo'].update([
            ('totalSlices', total_slices), ('currentSliceNumber',
                                            current_slice_number), ('boundaryOffsetValue', boundary_offset_value),
            ('sliceOffsetValue', slice_offset_value), ('sliceOverlapRegion', slice_overlap_region), ('isSliceOf', original_audio_id)])
    else:
        audio_details_dict['additionalInfo'] = {
            'totalSlices': total_slices, 'currentSliceNumber': current_slice_number, 'boundaryOffsetValue': boundary_offset_value,
            'sliceOffsetValue': slice_offset_value, 'sliceOverlapRegion': slice_overlap_region, 'isSliceOf': original_audio_id}


def add_text_grid(audio_details_dict,
                  current_username,
                  text_grid,
                  model_name,
                  model_metadata,
                  save_for_user=True):

    audio_details_dict["textGrid"] = text_grid
    logger.debug('Model name %s', model_name)

    if save_for_user:
        audio_details_dict[current_username] = {}
        audio_details_dict[current_username]["textGrid"] = text_grid

    if model_name != '':
        model_key = '@model##'+model_name+'##'+current_username
        audio_details_dict[model_key] = {}
        audio_details_dict[model_key]["textGrid"] = text_grid
        audio_details_dict[model_key]["updatedBy"] = current_username
        audio_details_dict[model_key]["updatedAt"] = datetime.now()
        audio_details_dict[model_key]["modelMetadata"] = model_metadata


def add_waveform_json(audio_details_dict,
                      audiowaveform_json_dir_path,
                      audio_json_parent_dir,
                      updated_audio_filename
                      ):
    audiowaveform_json = get_audio_waveform_json(
        audiowaveform_json_dir_path, audio_json_parent_dir, updated_audio_filename)
    audio_details_dict['audioMetadata']['audiowaveform'] = audiowaveform_json


def get_audio_speaker_ids(transcriptions,
                          activeprojectname,
                          audio_id):
    speaker_ids = []
    current_speaker_ids = transcriptions.find_one(
        {'projectname': activeprojectname, 'audioId': audio_id}, {'_id': 1, 'speakerId': 1})
    if not current_speaker_ids is None and 'speakerId' in current_speaker_ids:
        all_speaker_ids = current_speaker_ids['speakerId']
        if type(all_speaker_ids) == str:
            speaker_ids.append(all_speaker_ids)
        else:
            speaker_ids.extend(all_speaker_ids)

    return speaker_ids


def update_transcriptions_collection(transcriptions,
                                     activeprojectname,
                                     audioId,
                                     key_to_update,
                                     new_value):
    transcriptions.update_one({'projectname': activeprojectname, 'audioId': audioId},
                              {"$set": {
                                  key_to_update: new_value
                              }})


def update_speaker_audio_ids(speaker_audio_ids,
                             existing_speaker_ids,
                             new_speaker_ids,
                             audio_id):
    ids_to_remove = {}
    ids_to_add = {}
    for existing_speaker_id in existing_speaker_ids:
        if not existing_speaker_id in new_speaker_ids:
            if existing_speaker_id in speaker_audio_ids:
                try:
                    ids_to_remove[existing_speaker_id] = audio_id
                    existing_ids_all = speaker_audio_ids[existing_speaker_id]
                    existing_ids_remaining = [
                        i for i in existing_ids_all if i != audio_id]
                    speaker_audio_ids[existing_speaker_id] = existing_ids_remaining

                except:
                    logger.exception('')

    for new_speaker_id in new_speaker_ids:
        if not new_speaker_id in existing_speaker_ids:
            if new_speaker_id in speaker_audio_ids:
                existing_ids_all = speaker_audio_ids[new_speaker_id]
                if not audio_id in existing_ids_all:
                    ids_to_add[new_speaker_id] = audio_id
                    existing_ids_all.append(audio_id)
                    speaker_audio_ids[new_speaker_id] = existing_ids_all
            else:
                ids_to_add[new_speaker_id] = audio_id
                speaker_audio_ids[new_speaker_id] = [audio_id]

    logger.info('IDs removed %s', ids_to_remove)
    logger.info('IDs added %s', ids_to_add)
    # for current_audio_id in speaker_audio_ids:
    # if audio_id in speaker_audio_ids:
    #     speaker_audio_ids[audio_id].extend(ids_to_add)
    #     for id_to_remove in ids_to_remove:
    #         try:
    #             speaker_audio_ids[audio_id].remove(id_to_remove)
    #         except:
    #             logger.exception('')


def update_audio_speaker_ids(projects,
                             userprojects,
                             transcriptions,
                             activeprojectname,
                             current_username,
                             speakerId,
                             all_audio_ids):

    last_active_id = all_audio_ids[0]
    project_type = getprojecttype.getprojecttype(projects, activeprojectname)

    existing_speaker_ids = get_audio_speaker_ids(transcriptions,
                                                 activeprojectname,
                                                 last_active_id)

    # logger.info('Existing speaker IDs for audio %s', existing_speaker_ids)

    if set(existing_speaker_ids) != set(speakerId):
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

        update_speaker_audio_ids(speaker_audio_ids,
                                 existing_speaker_ids,
                                 speakerId,
                                 last_active_id)

        # logger.info('Modified audio IDs of speakers %s', speaker_audio_ids)
        update_speakerid_audioid(projects,
                                 activeprojectname,
                                 current_username,
                                 speakerId,
                                 last_active_id,
                                 speaker_id_key_name,
                                 speakerIds,
                                 speaker_audioid_key_name,
                                 speaker_audio_ids,
                                 existing_speaker_ids)

        update_active_speaker_Id(userprojects,
                                 activeprojectname,
                                 current_username,
                                 speakerId
                                 )

        update_transcriptions_collection(transcriptions,
                                         activeprojectname,
                                         last_active_id,
                                         "speakerId",
                                         speakerId)


def update_active_speaker_Id(userprojects,
                             activeprojectname,
                             current_username,
                             speakerIds
                             ):
    # logger.info('Speaker IDs %s', speakerIds)
    if type(speakerIds) == str:
        speakerIds = [speakerIds]
    # update active speaker ID in userprojects collection
    projectinfo = userprojects.find_one({'username': current_username},
                                        {'_id': 0, 'myproject': 1, 'projectsharedwithme': 1})

    # logger.info(projectinfo)
    # logger.info(activeprojectname)
    userprojectinfo = ''
    for key, value in projectinfo.items():
        if len(value) != 0:
            # logger.info(activeprojectname in value)
            if activeprojectname in value:
                userprojectinfo = key+'.'+activeprojectname+".activespeakerId"
    # logger.info(userprojectinfo)
    userprojects.update_one({"username": current_username},
                            {"$set": {
                                userprojectinfo: speakerIds[0]
                            }})


def update_speakerid_audioid(projects,
                             activeprojectname,
                             current_username,
                             all_speakerId,
                             last_active_id,
                             speaker_id_key_name,
                             speakerIds,
                             speaker_audioid_key_name,
                             speaker_audio_ids,
                             existing_speaker_ids=[]
                             ):
    if type(all_speakerId) == str:
        all_speakerId = [all_speakerId]

    all_updates = {speaker_id_key_name: speakerIds,
                   speaker_audioid_key_name: speaker_audio_ids}

    for current_sid in all_speakerId:
        key = 'lastActiveId.'+current_username+'.'+current_sid+'.audioId'
        all_updates[key] = last_active_id

    # projects.update_one({'projectname': activeprojectname},
    #                     {'$set': {
    #                         'lastActiveId.'+current_username+'.'+speakerId+'.audioId':  last_active_id,
    #                         speaker_id_key_name: speakerIds,
    #                         speaker_audioid_key_name: speaker_audio_ids
    #                     }})

    projects.update_one({'projectname': activeprojectname},
                        {'$set': all_updates})


def is_store_in_mongo(split_into_smaller_chunks):
    return not split_into_smaller_chunks


def is_store_in_local(get_audio_json, run_vad, run_asr, split_into_smaller_chunks):
    return get_audio_json or run_vad or run_asr or split_into_smaller_chunks


def is_split_into_smaller_chunks(audio_duration, max_allowed_duration):
    return audio_duration > max_allowed_duration


def get_full_model_name(run_vad,
                        run_asr,
                        vad_model_name,
                        asr_model_name):
    full_model_name = ''
    if vad_model_name != '':
        full_model_name = vad_model_name
    if asr_model_name != '':
        full_model_name = vad_model_name + '##' + asr_model_name

    return full_model_name


def get_audio_doc_details(projectowner,
                          activeprojectname,
                          current_username,
                          speakerId,
                          sourceId="",
                          data_type="audio",
                          prompt="",
                          new_audio_details={},
                          update=False,
                          additional_data={},
                          **kwargs):
    # save audio file details in transcriptions collection
    if sourceId == '':
        sourceId = speakerId
        # lifesourceid = speakerId

    if update:
        new_audio_details = {
            "speakerId": speakerId
        }
    elif len(new_audio_details) == 0:
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
    for additional_key, additional_value in additional_data:
        new_audio_details[additional_key] = additional_value

    for kwargs_key, kwargs_value in kwargs.items():
        new_audio_details[kwargs_key] = kwargs_value

    return new_audio_details


def get_audio_dir_path():
    json_basedir = os.path.abspath(os.path.dirname(__file__))
    audio_dir_path = '/'.join(json_basedir.split('/')[:-1])
    return audio_dir_path


def get_audio_duration_from_file(audio_file):
    full_audio_file = AudioSegment.from_file(audio_file)
    audio_duration = full_audio_file.duration_seconds
    return audio_duration, full_audio_file


def get_speaker_ids(projects,
                    activeprojectname,
                    current_username,
                    speakerId,
                    project_type):
    # save audio file details and speaker ID in projects collection
    if type(speakerId) == str:
        speakerId = [speakerId]

    speaker_id_key_name = get_speaker_id_key_name(project_type)

    speakerIds = projects.find_one({'projectname': activeprojectname},
                                   {'_id': 0, speaker_id_key_name: 1})
    # logger.debug(f"SPEAKER IDS: {speakerIds}")
    if len(speakerIds) != 0:
        speakerIds = speakerIds[speaker_id_key_name]
        if current_username in speakerIds:
            speakerIdskeylist = speakerIds[current_username]
            speakerIdskeylist.extend(speakerId)
            speakerIds[current_username] = list(set(speakerIdskeylist))
        else:

            speakerIds[current_username] = speakerId
    else:
        speakerIds = {
            current_username: speakerId
        }

    return speaker_id_key_name, speakerIds


def get_speaker_audio_ids(projects,
                          activeprojectname,
                          all_audio_ids,
                          speakerIds,
                          project_type):
    try:
        speaker_audio_ids = []
        if type(speakerIds) == str:
            speakerIds = [speakerIds]

        speaker_audioid_key_name = get_audiospeaker_id_key_name(project_type)
        # logger.debug(speaker_audioid_key_name)
        speaker_audio_ids = projects.find_one({'projectname': activeprojectname},
                                              {'_id': 0, speaker_audioid_key_name: 1})
        # logger.debug(speaker_audio_ids)
        speaker_audio_ids = speaker_audio_ids[speaker_audioid_key_name]
        # logger.info(len(speaker_audio_ids))
        # logger.info(speaker_audio_ids)
        for speakerId in speakerIds:
            if len(speaker_audio_ids) != 0:
                # logger.info(speaker_audio_ids.keys())
                # logger.info(speaker_audioid_key_name in speaker_audio_ids)
                # logger.debug('speaker_audio_ids %s', speaker_audio_ids)
                if speakerId in speaker_audio_ids:
                    speaker_audio_idskeylist = speaker_audio_ids[speakerId]
                    speaker_audio_idskeylist.extend(all_audio_ids)
                    speaker_audio_ids[speakerId] = speaker_audio_idskeylist
                else:
                    # logger.debug('speakerId %s', speakerId)
                    speaker_audio_ids[speakerId] = all_audio_ids
                # plogger.debug(speaker_audio_ids)
            else:
                speaker_audio_ids = {
                    speakerId: all_audio_ids
                }
    except:
        logger.exception("")

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
    logger.debug('audio filename %s', audiowaveform_audio_path)
    logger.debug('json_filename %s', json_filename)
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
    logger.debug("Length of speaker audio IDs %s", len(speaker_audio_ids))
    # logger.debug("Speaker Audio IDs %s", speaker_audio_ids)
    if len(speaker_audio_ids) != 0:
        speaker_audio_ids = speaker_audio_ids['speakersAudioIds']
        # logger.debug('speaker_audio_ids %s', speaker_audio_ids)
        if speakerId in speaker_audio_ids:
            speaker_audio_idskeylist = speaker_audio_ids[speakerId]
            speaker_audio_idskeylist.append(audio_id)
            speaker_audio_ids[speakerId] = speaker_audio_idskeylist
        else:
            # logger.debug('speakerId %s', speakerId)
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
        # logger.debug("audio_id: %s", audio_id)
        # logger.debug("new_audio_details: %s", pformat(new_audio_details))
        # logger.debug("project_type_collection: %s", project_type_collection)
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


def get_blank_text_grid():
    blank_text_grid = {
        "discourse": {},
        "sentence": {},
        "word": {},
        "phoneme": {}
    }
    return blank_text_grid


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


def getaudiofiletranscription(data_collection,
                              activeprojectname,
                              audio_id,
                              transcription_by=""):
    """get the transcription details of the audio file

    Args:
        data_collection (_type_): _description_
        file_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    # logger.debug("audio_id: %s", audio_id)
    # logger.debug("activeprojectname: %s", activeprojectname)
    transcription_details = {}
    blank_text_grid = get_blank_text_grid()

    transcription_data = data_collection.find_one(
        {'projectname': activeprojectname, 'audioId': audio_id})
    # logger.debug("transcription_data: %s", transcription_data)
    if transcription_data is not None:
        if (transcription_by == "") or (transcription_by == "latest"):
            transcription_details['data'] = transcription_data['textGrid']
        elif transcription_by in transcription_data:
            transcription_details['data'] = transcription_data[transcription_by]
        elif (transcription_by not in transcription_data):
            transcription_details['data'] = blank_text_grid

    # logger.debug("Transcription by %s, transcription details %s",
    #              transcription_by, transcription_details)

    return transcription_details


def get_audio_transcriptions_by(projects, data_collection, project_name, audio_id, get_model_names=True):
    transcriptions_by = []
    transcription_data = data_collection.find_one({'audioId': audio_id})

    if transcription_data is not None:
        project_shared_with = projectDetails.get_shared_with_users(
            projects, project_name)

        transcription_data_keys = transcription_data.keys()
        # logger.debug("Project shared with %s, transcription keys %s",
        #              project_shared_with, transcription_data_keys)
        # transcriptions_by = [
        #     uname for uname in transcription_data_keys if uname in project_shared_with or uname.startswith("@model")]
        transcriptions_by = [
            uname for uname in transcription_data_keys if uname.startswith("@model")]
        transcriptions_by.append('latest')
        transcriptions_by.extend(project_shared_with)
        # logger.debug("All transcription by %s",
        #              transcriptions_by)
    return transcriptions_by


def getaudiowaveformfilefromfs(mongo,
                               basedir,
                               folder_name,
                               file_id,
                               file_type,
                               delete_previous_files=True):
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
    # logger.debug('fs file: %s, %s, %s, %s', basedir, folder_name,
    #                    file_id,
    #                    file_type)
    fs = gridfs.GridFS(mongo.db)
    file = fs.find_one({file_type: file_id})
    audioFolder = os.path.join(basedir, folder_name)
    logger.debug('Audio folder path %s', audioFolder)

    if delete_previous_files:
        if (os.path.exists(audioFolder)):
            # logger.debug('Audio folder path exists %s',
            #              audioFolder, 'deleting')
            shutil.rmtree(audioFolder)
        os.mkdir(audioFolder)
    else:
        if (not os.path.exists(audioFolder)):
            os.mkdir(audioFolder)

    file_path = ''
    if (file is not None and
            'audio' in file.contentType):
        file_name = file.filename
        logger.debug('File name %s', file_name)
        audiofile = fs.get_last_version(filename=file_name)
        audiofileBytes = audiofile.read()
        # if len(audiofileBytes) != 0:
        file_path = os.path.join(folder_name, file_name)
        save_file_path = os.path.join(basedir, file_path)
        logger.debug('Save file path %s', save_file_path)
        open(save_file_path, 'wb').write(audiofileBytes)
    else:
        save_file_path = ''
    # logger.debug('file_path %s', file_path)
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
    # logger.debug('fs file: %s, %s, %s', basedir,
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
                  speaker_audio_ids,
                  which_one):
    """_summary_

    Args:
        projects (_type_): _description_
        activeprojectname (_type_): _description_
        last_active_id (_type_): _description_
        which_one (_type_): _description_
    """
    # audio_ids_list = projects.find_one({'projectname': activeprojectname},
    #                                    {'_id': 0, 'speakersAudioIds': 1})
    audio_ids_list = speaker_audio_ids
    # logger.debug('audio_ids_list %s', audio_ids_list)
    if len(audio_ids_list) != 0:
        # audio_ids_list = audio_ids_list['speakersAudioIds'][activespeakerId]
        audio_ids_list = speaker_audio_ids
        # logger.debug('audio_ids_list: %s', audio_ids_list)
    if (len(audio_ids_list) != 0):
        if (last_active_id in audio_ids_list):
            audio_id_index = audio_ids_list.index(last_active_id)
        else:
            audio_id_index = 0
        # logger.debug('latestAudioId Index!!!!!!! %s', audio_id_index)
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
    # logger.debug('latest_audio_id AUDIODETAILS: %s', latest_audio_id)

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
    # logger.debug('updatelatestaudioid')
    projects.update_one({'projectname': activeprojectname},
                        {'$set': {'lastActiveId.'+current_username+'.'+activespeakerId+'.audioId':  latest_audio_id}})


def getaudiotranscriptiondetails(transcriptions,
                                 activeprojectname,
                                 audio_id,
                                 transcription_by="",
                                 transcription_data={}):
    """_summary_

    Args:
        transcriptions (_type_): _description_
        audio_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    # logger.debug('Transcription data %s', transcription_data)
    # transcription_data = {}
    transcription_regions = []
    gloss = {}
    pos = {}
    boundary_count = 0
    # logger.debug('Transcription data %s', transcription_data)
    try:
        if 'data' in transcription_data:
            t_data = transcription_data['data']
        else:
            t_data = getaudiofiletranscription(
                transcriptions,
                activeprojectname,
                audio_id,
                transcription_by)
            if t_data is not None and 'data' in t_data:
                t_data = t_data['data']

        # t_data = transcriptions.find_one({'audioId': audio_id},
                #  {'_id': 0, 'textGrid.sentence': 1})

        # logger.debug('t_data!!!!! %s', t_data)
        if t_data is not None:
            if 'textGrid' in t_data:
                transcription_data = t_data['textGrid']
            else:
                transcription_data = t_data
        # logger.debug('Transcription data %s', pformat(transcription_data))
        if 'sentence' in transcription_data:
            sentence = transcription_data['sentence']
        else:
            sentence = {}
        for boundary_id, value in sentence.items():
            # logger.debug("boundary_id: %s\nvalue: %s", boundary_id, pformat(value))
            transcription_region = {}
            # gloss = {}
            # transcription_region['sentence'] = {}
            transcription_region['data'] = {}
            transcription_region['boundaryID'] = boundary_id
            transcription_region['start'] = sentence[boundary_id]['start']
            transcription_region['end'] = sentence[boundary_id]['end']
            # transcription_region['sentence'] = {boundary_id: value}
            transcription_region['data'] = {'sentence': {boundary_id: value}}
            # logger.debug("transcription_region: %s", pformat(transcription_region))
            boundary_count += 1
            try:
                # logger.debug('!@!#!@!#!@!#!@!#!@!##!@!#!#!@!#!@!#!@!#!@!#!@!##!@!#!# %s', gloss)
                tempgloss = sentence[boundary_id]['gloss']
                # logger.debug('!@!#!@!#!@!#!@!#!@!##!@!#!#!@!#!@!#!@!#!@!#!@!##!@!#!# %s', tempgloss)
                gloss[boundary_id] = pd.json_normalize(
                    tempgloss, sep='.').to_dict(orient='records')[0]
                # logger.debug('!@!#!@!#!@!#!@!#!@!##!@!#!#!@!#!@!#!@!#!@!#!@!##!@!#!# %s', gloss)
                temppos = sentence[boundary_id]['pos']
                # logger.debug('!@!#!@!#!@!#!@!#!@!##!@!#!#!@!#!@!#!@!#!@!#!@!##!@!#!# %s', temppos)
                pos[boundary_id] = pd.json_normalize(
                    temppos, sep='.').to_dict(orient='records')[0]

                # logger.debug('288 %s', gloss)
            except:
                # logger.exception("")
                # logger.debug('=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1= %s', gloss)
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
        # logger.debug(transcription_regions)
    # logger.debug('303 %s %s', gloss, pos)
    except:
        logger.exception("")

    return (transcription_regions, gloss, pos, boundary_count)


def savetranscription(transcriptions,
                      activeprojectname,
                      activeprojectform,
                      scriptCode,
                      current_username,
                      transcription_regions,
                      audio_id,
                      activespeakerId,
                      accessedOnTime):
    """Module to work on the sentence details (transcription and all) through ajax.

    Args:
        transcription_details (_type_): _description_
    """
    # logger.debug("audio_id: %s", audio_id)
    # plogger.debug(activeprojectform)
    # plogger.debug(scriptCode)
    # transcription_details = {
    #     'updatedBy' : current_username,
    #     "textdeleteFLAG": 0
    # }
    # text_grid = {}
    try:
        text_grid = {}
        sentence = {}
        if transcription_regions is not None:
            transcription_regions = json.loads(transcription_regions)
            # plogger.debug(transcription_regions)
            for transcription_boundary in transcription_regions:
                transcription_boundary = transcription_boundary['data']
                if 'sentence' in transcription_boundary:
                    for boundary_id, value in transcription_boundary['sentence'].items():
                        # logger.debug(f"KEY: {type}\nVALUE: {value}")
                        # value["speakerId"] = activespeakerId
                        value["sentenceId"] = audio_id+'_'+boundary_id
                        sentence[boundary_id] = value
                # plogger.debug(sentence)
                #     logger.debug('transcription_boundary.keys() %s', transcription_boundary.keys())
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
                # logger.debug('371 %s', sentence)
                # plogger.debug(sentence)

        text_grid['sentence'] = sentence

        save_manual_transcription(transcriptions,
                                  activeprojectname,
                                  current_username,
                                  audio_id,
                                  text_grid,
                                  accessedOnTime,
                                  True)

    except:
        logger.exception("")


def save_manual_transcription(transcriptions,
                              activeprojectname,
                              current_username,
                              audio_id,
                              text_grid,
                              accessedOnTime,
                              overwrite):
    audio_details_dict = {}
    add_text_grid(audio_details_dict,
                  current_username,
                  text_grid,
                  '',
                  '',
                  save_for_user=overwrite)
    audio_details_dict['updatedBy'] = current_username
    audio_details_dict['transcriptionFLAG'] = 1

    save_text_grid_into_transcription(transcriptions,
                                      activeprojectname,
                                      current_username,
                                      audio_id,
                                      audio_details_dict,
                                      accessedOnTime)


def save_text_grid_into_transcription(transcriptions,
                                      activeprojectname,
                                      current_username,
                                      audio_id,
                                      audio_details_dict,
                                      accessedOnTime):
    updated_doc_id = transcriptions.update_one({'projectname': activeprojectname, 'audioId': audio_id},
                                               {'$set': audio_details_dict,
                                                '$push':
                                                {
                                                    'allAccess.'+current_username: accessedOnTime,
                                                    'allUpdate.'+current_username: datetime.now().strftime("%d/%m/%y %H:%M:%S")
                                                }
                                                })

    return updated_doc_id


def synctranscription(transcriptions,
                      activeprojectname,
                      activeprojectform,
                      source_script,
                      target_scripts,
                      audio_lang,
                      current_username,
                      transcription_regions,
                      audio_id,
                      accessedOnTime,
                      overwrite=False,
                      boundary_ids=['*']):
    """Module to work on the sentence details (transcription and all) through ajax.

    Args:
        transcription_details (_type_): _description_
    """
    # logger.debug("audio_id: %s", audio_id)
    # plogger.debug(activeprojectform)
    # plogger.debug(scriptCode)
    # transcription_details = {
    #     'updatedBy' : current_username,
    #     "textdeleteFLAG": 0
    # }
    # text_grid = {}
    try:
        audio_details_dict = {}
        text_grid = {}
        sentence = {}
        return_data = {}
        if transcription_regions is not None:
            transcription_regions = json.loads(transcription_regions)
            # plogger.debug(transcription_regions)
            for transcription_boundary in transcription_regions:
                transcription_boundary = transcription_boundary['data']
                if 'sentence' in transcription_boundary:
                    for boundary_id, value in transcription_boundary['sentence'].items():
                        # logger.debug(f"KEY: {type}\nVALUE: {value}")
                        # value["speakerId"] = activespeakerId

                        value["sentenceId"] = audio_id+'_'+boundary_id
                        sentence[boundary_id] = value

                        if '*' in boundary_ids or boundary_id in boundary_ids:
                            if 'transcription' in value:
                                source_val = value['transcription'][source_script].strip(
                                )

                                all_scripts = list(
                                    value['transcription'].keys())
                                other_transscripts = {}
                                for cur_script in all_scripts:
                                    if not cur_script in target_scripts:
                                        other_transscripts[cur_script] = value['transcription'][cur_script].strip(
                                        )

                                for target_script in target_scripts:
                                    if source_script != target_script:
                                        existing_transcript = value['transcription'][target_script].strip(
                                        )

                                        if overwrite:
                                            cur_transcript = predictFromLocalModels.get_transliteration(
                                                source_val, source_script, target_script, audio_lang, other_transcripts=other_transscripts)
                                            if cur_transcript.strip() == '':
                                                cur_transcript = existing_transcript
                                        else:
                                            if existing_transcript == '':
                                                cur_transcript = predictFromLocalModels.get_transliteration(
                                                    source_val, source_script, target_script, audio_lang, other_transcripts=other_transscripts)
                                                if cur_transcript.strip() == '':
                                                    cur_transcript = existing_transcript
                                            else:
                                                cur_transcript = existing_transcript

                                        value['transcription'][target_script] = cur_transcript

                                        if boundary_id in return_data:
                                            return_data[boundary_id][target_script] = cur_transcript
                                        else:
                                            return_data[boundary_id] = {
                                                target_script: cur_transcript}

                                # plogger.debug(sentence)
                                #     logger.debug('transcription_boundary.keys() %s', transcription_boundary.keys())
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
                                # logger.debug('371 %s', sentence)
                                # plogger.debug(sentence)
        text_grid['sentence'] = sentence

        save_manual_transcription(transcriptions,
                                  activeprojectname,
                                  current_username,
                                  audio_id,
                                  text_grid,
                                  accessedOnTime,
                                  overwrite)

        # transcriptions.update_one({'projectname': activeprojectname, 'audioId': audio_id},
        #                           {'$set':
        #                            {
        #                                'textGrid.sentence': sentence,
        #                                'updatedBy': current_username,
        #                                'transcriptionFLAG': 1,
        #                                current_username+'.textGrid.sentence': sentence
        #                            },
        #                            '$push':
        #                            {
        #                                'allAccess.'+current_username: accessedOnTime,
        #                                'allUpdate.'+current_username: datetime.now().strftime("%d/%m/%y %H:%M:%S")
        #                            }
        #                            })
    except:
        logger.exception("")

    return [return_data]


def toggle_transcription_complete_status(transcriptions,
                                         activeprojectname,
                                         current_username,
                                         audio_id,
                                         accessedOnTime
                                         ):
    """Module to toggle the complete status through ajax.

    Args:
        transcription_details (_type_): _description_
    """

    try:
        # logger.info('Audio ID %s', audio_id)
        # logger.info('Active project %s', activeprojectname)
        existing_status = transcriptions.find_one(
            {'projectname': activeprojectname, 'audioId': audio_id},
            {current_username +
             '.audioCompleteFLAG': 1, "_id": 0})

        if not existing_status or existing_status == None:
            # logger.info('Not found')
            status = 1
        else:
            status = not existing_status[current_username].get(
                'audioCompleteFLAG', 0)
        transcriptions.update_one({'projectname': activeprojectname, 'audioId': audio_id},
                                  {'$set':
                                   {
                                       current_username+'.audioCompleteFLAG': status

                                   },
                                   '$push':
                                   {
                                       'allAccess.'+current_username: accessedOnTime,
                                       'allUpdate.'+current_username: datetime.now().strftime("%d/%m/%y %H:%M:%S")
                                   }
                                   })
        # status = complete_status[current_username]['textGrid']['audioCompleteFLAG']
        # logger.info('Update status %s', update_status)
        logger.info('Updated Status %s', status)
        return status
    #
        # projection={current_username +
        #             '.textGrid.audioCompleteFLAG': 1, "_id": 0},
        # return_document=ReturnDocument.AFTER
    except:
        logger.exception("")


def get_transcription_complete_status(transcriptions,
                                      activeprojectname,
                                      current_username,
                                      audio_id
                                      ):
    """Module to toggle the complete status through ajax.

    Args:
        transcription_details (_type_): _description_
    """

    try:
        existing_status = transcriptions.find_one(
            {'projectname': activeprojectname, 'audioId': audio_id},
            {current_username +
             '.audioCompleteFLAG': 1, "_id": 0})

        if not existing_status or existing_status == None:
            # logger.info('Not found')
            status = 0
        else:
            status = existing_status[current_username].get(
                'audioCompleteFLAG', 0)

        return status
    except:
        logger.exception("")


def get_transcription_start_status(transcriptions,
                                   activeprojectname,
                                   audio_id
                                   ):
    """Module to toggle the complete status through ajax.

    Args:
        transcription_details (_type_): _description_
    """

    try:
        existing_status = transcriptions.find_one(
            {'projectname': activeprojectname, 'audioId': audio_id},
            {'transcriptionFLAG': 1, "_id": 0})

        if not existing_status or existing_status == None:
            # logger.info('Not found')
            status = 0
        else:
            status = existing_status.get(
                'transcriptionFLAG', 0)

        return status
    except:
        logger.exception("")


def getaudioprogressreport(projects,
                           transcriptions,
                           speakerdetails,
                           activeprojectname,
                           isharedwith):
    datatoshow = []
    users_speaker_ids = projects.find_one({'projectname': activeprojectname},
                                          {'_id': 0, 'speakerIds': 1})['speakerIds']
    # logger.debug('speaker_ids_1 %s', users_speaker_ids)
    if len(users_speaker_ids) != 0:
        # logger.debug('speaker_ids_2 %s', users_speaker_ids)
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

    # logger.debug('datatoshow %s', datatoshow)

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
    # logger.debug ("Added Speaker IDS %s", added_speaker_ids)
    return added_speaker_ids


def getaudiospeakerids(data_collection,
                       activeprojectname,
                       audio_id):
    """get the audio speaker ids of the audio file

    Args:
        data_collection (_type_): _description_
        file_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    all_speaker_ids = []
    audio_speakers = data_collection.find_one(
        {'projectname': activeprojectname, 'audioId': audio_id}, {'_id': 1, 'speakerId': 1})
    # logger.debug(audio_metadata)
    if audio_speakers is not None and 'speakerId' in audio_speakers:
        speaker_ids = audio_speakers['speakerId']
        if type(speaker_ids) == str:
            all_speaker_ids.append(speaker_ids)
        else:
            all_speaker_ids.extend(speaker_ids)

    return all_speaker_ids


def getaudiometadata(data_collection,
                     activeprojectname,
                     audio_id):
    """get the audio metadata details of the audio file

    Args:
        data_collection (_type_): _description_
        file_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    audio_metadata_details = dict({'audioMetadata': ''})
    audio_metadata = data_collection.find_one(
        {'projectname': activeprojectname, 'audioId': audio_id}, {'_id': 1, 'audioMetadata': 1})
    # logger.debug(audio_metadata)
    if audio_metadata is not None and 'audioMetadata' in audio_metadata:
        audio_metadata_details['audioMetadata'] = audio_metadata['audioMetadata']

    return audio_metadata_details


def get_audio_filename(data_collection,
                       activeprojectname,
                       audio_id):
    """get the audio filename of the audio file

    Args:
        data_collection (_type_): _description_
        file_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    audio_filename = data_collection.find_one(
        {'projectname': activeprojectname, 'audioId': audio_id}, {'_id': 1, 'audioFilename': 1})
    # logger.debug(audio_filename)
    if audio_filename is not None and 'audioFilename' in audio_filename:
        return audio_filename['audioFilename']
    else:
        return ''


def get_audio_speakerid(data_collection,
                        activeprojectname,
                        audio_id):
    """get the audio speaker id of the audio file

    Args:
        data_collection (_type_): _description_
        file_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        speaker_id = []
        audio_speakerid = data_collection.find_one(
            {'projectname': activeprojectname, 'audioId': audio_id},
            {'_id': 1, 'lifesourceid': 1, 'speakerId': 1})
        # logger.debug(audio_filename)
        if (audio_speakerid is not None and
                'lifesourceid' in audio_speakerid):
            speaker_id = audio_speakerid['lifesourceid']
        elif (audio_speakerid is not None and
              'speakerId' in audio_speakerid and
              audio_speakerid['speakerId'] != ''):
            speaker_id = audio_speakerid['speakerId']
        else:
            return None

        if (isinstance(speaker_id, str)):
            speaker_id = [speaker_id]
    except:
        logger.exception("")

    return speaker_id


def lastupdatedby(transcriptions,
                  activeprojectname,
                  audio_id):
    """get the transcription last updated by

    Args:
        transcriptions (_type_): _description_
        file_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    last_updated_by_details = dict({'updatedBy': ''})
    last_updated_by = transcriptions.find_one(
        {'projectname': activeprojectname, 'audioId': audio_id}, {'_id': 1, 'updatedBy': 1})
    # logger.debug(last_updated_by)
    if last_updated_by is not None and 'updatedBy' in last_updated_by:
        last_updated_by_details['updatedBy'] = last_updated_by['updatedBy']

    return last_updated_by_details


def merge_boundary_with_next(current_end, next_start, span_start, span_end, max_pause, max_boundary_size):
    return ((next_start-current_end) <= max_pause) and ((span_end-span_start) <= max_boundary_size)


def merge_with_next_boundary(i, current_boundary_start, boundaries, include_transcription, transcriptions, min_boundary_size, distance_from_previous=-1):
    # logger.debug('Current position: %s \tTotal Boundaries: %s',
    #              i, len(boundaries))
    # logger.debug('All boundaries: %s', boundaries)
    new_boundary_transcriptions = ''
    new_boundary_start = current_boundary_start
    new_boundary_end = boundaries[i+1]['end']
    if include_transcription:
        new_boundary_transcriptions = transcriptions[i] + \
            ' ' + transcriptions[i+1]
    next_i = i + 1
    if len(boundaries)-1 > next_i:
        while (new_boundary_end - new_boundary_start) < min_boundary_size:
            # while next_i < len(boundaries):
            new_boundary_start, new_boundary_end, new_boundary_transcriptions, next_i = merge_with_next_boundary(
                next_i, new_boundary_start, boundaries, include_transcription, transcriptions, min_boundary_size)
            previous_match = False
        # if next_boundary_end - new_boundary_start < min_boundary_size:
        #     new_boundary_end = next_boundary_end
        #     if include_transcription:
        #         new_boundary_transcriptions = new_boundary_transcriptions + \
        #             ' ' + transcriptions[next_i]
        #     next_i = next_i + 1
        # else:
        #     break
    # logger.debug('Next merge returned values %s, %s, %s',
            #  next_i+1, new_boundary_start, new_boundary_end)
    return new_boundary_start, new_boundary_end, new_boundary_transcriptions, next_i+1


def merge_with_previous_boundary(i, previous_boundary_start, current_boundary_end, boundaries, include_transcription, transcriptions):
    new_boundary_start = previous_boundary_start
    new_boundary_end = current_boundary_end
    if include_transcription:
        new_boundary_transcriptions = transcriptions[i -
                                                     1] + ' ' + transcriptions[i]
    else:
        new_boundary_transcriptions = ''
    next_i = i+1
    return new_boundary_start, new_boundary_end, new_boundary_transcriptions, next_i


def merge_smaller_boundaries(boundaries, include_transcription=False, transcriptions=[], min_boundary_size=2.0):
    new_boundaries = []
    new_transcriptions = []
    next_i = 0
    previous_match = False
    for i, boundary in enumerate(boundaries):
        if i == next_i:
            current_boundary_start = boundary['start']
            current_boundary_end = boundary['end']
            # logger.debug('Current boundaries %s, %s, %s', current_boundary_start,
            #  current_boundary_end, (current_boundary_end-current_boundary_start))
            if current_boundary_end - current_boundary_start < min_boundary_size:
                if len(boundaries) > 1:
                    if i == 0 and len(boundaries) > 1:
                        new_boundary_start, new_boundary_end, new_boundary_transcriptions, next_i = merge_with_next_boundary(
                            i, current_boundary_start, boundaries, include_transcription, transcriptions, min_boundary_size)
                        previous_match = False
                    elif i > 0 and len(boundaries)-1 > i:
                        next_boundary = boundaries[i+1]
                        previous_boundary_end = previous_boundary['end']
                        next_boundary_start = next_boundary['start']
                        distance_from_previous = current_boundary_start - previous_boundary_end
                        distance_from_next = next_boundary_start - current_boundary_end

                        if (distance_from_next < distance_from_previous):
                            new_boundary_start, new_boundary_end, new_boundary_transcriptions, next_i = merge_with_next_boundary(
                                i, current_boundary_start, boundaries, include_transcription, transcriptions, min_boundary_size, distance_from_previous)
                            previous_match = False
                        elif (distance_from_previous < distance_from_next):
                            new_boundary_start, new_boundary_end, new_boundary_transcriptions, next_i = merge_with_previous_boundary(
                                i, previous_boundary['start'], current_boundary_end, boundaries, include_transcription, transcriptions)
                            new_boundaries.pop()
                            if include_transcription:
                                new_transcriptions.pop()
                            previous_match = True
                        elif distance_from_next == distance_from_previous:
                            new_boundary_start, current_boundary_end, prev_boundary_transcriptions, next_i = merge_with_previous_boundary(
                                i, previous_boundary['start'], current_boundary_end, boundaries, include_transcription, transcriptions)
                            current_boundary_start, new_boundary_end, next_boundary_transcriptions, next_i = merge_with_next_boundary(
                                i, current_boundary_start, boundaries, include_transcription, transcriptions, min_boundary_size, distance_from_previous)
                            new_boundaries.pop()
                            if include_transcription:
                                new_transcriptions.pop()
                                new_boundary_transcriptions = transcriptions[i -
                                                                             1] + ' ' + next_boundary_transcriptions

                            previous_match = True
                    elif i == len(boundaries)-1:
                        new_boundary_start, new_boundary_end, new_boundary_transcriptions, next_i = merge_with_previous_boundary(
                            i, previous_boundary['start'], current_boundary_end, boundaries, include_transcription, transcriptions)
                        new_boundaries.pop()
                        if include_transcription:
                            new_boundary_transcriptions.pop()
                        previous_match = True
                else:
                    new_boundary_start = current_boundary_start
                    new_boundary_end = current_boundary_end

            else:
                # logger.debug('Boundary size fine!')
                new_boundary_start = current_boundary_start
                new_boundary_end = current_boundary_end
                next_i += 1

            new_boundary = {
                'start': new_boundary_start,
                'end': new_boundary_end
            }
            # logger.debug('New boundary to be added %s', new_boundary)
            new_boundaries.append(new_boundary)
            # logger.debug('All new boundaries %s', new_boundaries)
            if include_transcription:
                new_transcriptions.append(new_boundary_transcriptions)
            previous_boundary = new_boundary

    return new_boundaries, new_transcriptions


def get_new_boundaries(boundaries, max_pause, min_boundary_size=2.0, max_boundary_size=-1, slice_offset_value=0.0, include_transcription=False, transcriptions=None):
    new_boundaries = []
    new_transcriptions = []

    if max_boundary_size == -1:
        max_boundary_size = boundaries[-1]['end']

    span_start = 0
    span_end = 0
    logger.debug('Initial total boundaries %s', len(boundaries))
    logger.debug('Initial boundary %s', boundaries[0])
    # logger.debug('Second boundary %s', boundaries[1])
    # logger.debug('Initial end boundary %s', boundaries[-1])
    # logger.debug('Initial second end boundary %s', boundaries[-2:-5])

    if len(boundaries) > 1:
        for i in range(len(boundaries)-1):
            if include_transcription:
                current_transcription = transcriptions[i]

            current_boundary = boundaries[i]
            next_boundary = boundaries[i+1]
            current_start = current_boundary['start']
            # logger.debug(i, '%s out of %s %s', len(boundaries), current_boundary)
            # logger.debug(i+1, '%s out of %s %s', len(boundaries), next_boundary)

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

    # new_boundaries, new_transcriptions = merge_smaller_boundaries(
    #     new_boundaries, include_transcription, new_transcriptions, min_boundary_size)

    logger.debug('Final total boundaries %s', len(new_boundaries))
    logger.debug('Final start %s', new_boundaries[0])
    logger.debug('Final end %s', new_boundaries[-1])

    if include_transcription:
        return new_boundaries, new_transcriptions
    else:
        return new_boundaries


def get_boundary_id_from_number(number, length):
    return str(number).replace('.', '').zfill(length)


def insert_data_into_text_grid(text_grid, boundary_id, transcription_type, update_data={}, update_field='transcription'):
    data_to_update = update_data[transcription_type][update_field][boundary_id]
    field_to_update = text_grid[transcription_type][boundary_id][update_field]
    logger.debug('Text grid %s', text_grid)
    # logger.debug('Field to update %s %s', field_to_update,
    #              'eng-Latn' in field_to_update)
    for script_name, script_data in data_to_update.items():
        logger.debug('Script name %s Script Data %s', script_name, script_data)
        # logger.debug('Update Field %s %s Script Name %s %s',
        #              update_field, update_field == 'translation', script_name, script_name == 'English-Latin')
        if script_name in field_to_update:
            text_grid[transcription_type][boundary_id][update_field][script_name] = script_data
        elif (update_field == 'translation') and (script_name == 'English-Latin') and ('eng-Latn' in field_to_update):
            text_grid[transcription_type][boundary_id][update_field]['eng-Latn'] = script_data
    return text_grid


def update_existing_text_grid(text_grid, transcription_type, update_data={}, update_field='transcription', update_boundaries=['*']):
    # transcription_scripts = get_current_transcription_langscripts(mongo)
    # translation_langscripts = get_current_translation_langscripts(mongo)
    logger.debug('Existing TG %s', text_grid)
    logger.debug('Update Data %s', update_data)
    logger.debug('Transcription type %s', transcription_type)
    text_grid_boundaries = text_grid[transcription_type]
    if len(update_data) > 0:
        for boundary_id, boundary_elements in text_grid_boundaries.items():
            # all_fields=text_grid[boundary_id]
            # if update_field in update_data:
            if '*' in update_boundaries or boundary_id in update_boundaries:
                text_grid = insert_data_into_text_grid(
                    text_grid, boundary_id, transcription_type, update_data, update_field)

        # logger.debug('Data to update %s', data_to_update)
        # logger.debug(
        #     'Original Data %s', text_grid[transcription_type][boundary_id][update_field])

    logger.debug('Updated TG %s', text_grid)
    return text_grid


def update_blank_text_grid(mongo, text_grid, transcription_type, update_data={}, update_field='transcription'):
    try:
        # transcription_scripts = get_current_transcription_langscripts(mongo)
        # translation_langscripts = get_current_translation_langscripts(mongo)
        # logger.debug('Existing TG %s', text_grid)
        # logger.debug('Update Data %s', update_data)
        # logger.debug('Transcription type %s', transcription_type)
        text_grid_boundaries = update_data[transcription_type][update_field]

        for boundary_id, boundary_elements in text_grid_boundaries.items():
            # logger.debug('Boundary elements %s', boundary_elements)
            # all_fields=text_grid[boundary_id]
            # if update_field in update_data:

            # logger.debug('Data to update %s', data_to_update)
            # logger.debug(
            #     'Original Data %s', text_grid[transcription_type][boundary_id][update_field])
            data_to_update = update_data[transcription_type][update_field][boundary_id]

            boundary_vals = data_to_update.pop('boundary')
            # logger.debug('Data to update %s', data_to_update)
            # logger.debug('Boundary vals %s', boundary_vals)

            start_boundary = boundary_vals['start']
            end_boundary = boundary_vals['end']
            # start_boundary = boundary_elements['boundary']['start']
            # end_boundary = boundary_elements['boundary']['end']

            text_grid = generate_new_boundary(mongo, text_grid, start_boundary, end_boundary,
                                              transcription_type, boundary_id)

            text_grid = insert_data_into_text_grid(
                text_grid, boundary_id, transcription_type, update_data, update_field)

            # text_grid[transcription_type][boundary_id][update_field] = data_to_update

        # data_to_update = update_data[transcription_type]

        # text_grid[transcription_type] = data_to_update
        # logger.debug('Updated TG %s', text_grid)
    except:
        logger.exception("")

    return text_grid


def update_text_grid(mongo, text_grid, new_boundaries, transcription_type, include_transcription=False, transcriptions={}, boundary_offset_value=0.0, update_existing=False):
    logger.debug('Data type %s', transcription_type)

    # if include_transcription:
    #     transcription_scripts = list(transcriptions.keys())

    # logger.debug('Boundaries to update text grid', new_boundaries)
    logger.debug('Total expected boundaries %s', len(new_boundaries))
    logger.debug('Input Text Grid %s', text_grid)
    logger.debug('Input Boundaries %s', new_boundaries)

    for i in range(len(new_boundaries)):
        current_boundary = new_boundaries[i]

        start_boundary = round(float(
            current_boundary['start'] - boundary_offset_value), 2)
        end_boundary = round(
            float(current_boundary['end'] - boundary_offset_value), 2)

        # boundary_id_start = get_boundary_id_from_number(
        #     format(start_boundary, '.2f'), 5)
        # boundary_id_end = get_boundary_id_from_number(
        #     format(end_boundary, '.2f'), 5)

        # if (start_boundary == 0.0):
        #     boundary_id_start = '000'
        # else:
        #     boundary_id_start = str(start_boundary).replace('.', '')[:4]

        # if (end_boundary == 0.0):
        #     boundary_id_end = '000'
        # else:
        #     boundary_id_end = str(end_boundary).replace('.', '')[:4]

        boundary_id = generate_boundary_id(current_boundary)
        text_grid = generate_new_boundary(mongo, text_grid, start_boundary, end_boundary,
                                          transcription_type, boundary_id)

        # text_grid[transcription_type][boundary_id]['start'] = float(
        #     start_boundary - boundary_offset_value)
        # text_grid[transcription_type][boundary_id]['end'] = float(
        #     end_boundary - boundary_offset_value)

        # text_grid[boundary_id_key+'.transcription'] = ""

        # logger.debug(f"========Current Text Grid(%i)================ %s", i)
        # logger.debug(text_grid)
    logger.debug('Boundary Offset Value %s', boundary_offset_value)
    logger.debug('Output Text Grid %s', pformat(text_grid))

    return text_grid


def generate_new_boundary(mongo, text_grid, start_boundary, end_boundary, transcription_type, boundary_id):
    try:
        text_grid[transcription_type][boundary_id] = {}

        projects, userprojects = getdbcollections.getdbcollections(mongo,
                                                                   'projects',
                                                                   'userprojects')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        project_type = getprojecttype.getprojecttype(
            projects, activeprojectname)

        if (project_type == 'crawling'):
            transcription_scripts = projects.find_one({"projectname": activeprojectname},
                                                      {
                "_id": 0,
                "crawlerScript": 1})["crawlerScript"]
        else:
            transcription_scripts = get_current_transcription_langscripts(
                mongo)
        # transcription_scripts = list(transcriptions.keys())
        logger.debug('All transcription lang scripts %s',
                     transcription_scripts)

        translation_langscripts = get_current_translation_langscripts(mongo)
        logger.debug('All translation lang scripts %s',
                     translation_langscripts)

        text_grid[transcription_type][boundary_id]['start'] = start_boundary
        text_grid[transcription_type][boundary_id]['end'] = end_boundary
        text_grid[transcription_type][boundary_id]['speakerId'] = ""
        text_grid[transcription_type][boundary_id]['sentenceId'] = ""
        text_grid[transcription_type][boundary_id]['transcription'] = {}
        text_grid[transcription_type][boundary_id]['translation'] = {}
        text_grid[transcription_type][boundary_id]['sentencemorphemicbreak'] = {}
        text_grid[transcription_type][boundary_id]['morphemes'] = {}
        text_grid[transcription_type][boundary_id]['gloss'] = {}
        text_grid[transcription_type][boundary_id]['pos'] = {}

        if transcription_type == 'sentence':
            text_grid[transcription_type][boundary_id]['tags'] = ""

        # for langscript_code, script_name in transcription_scripts.items():
        #     logger.debug("langscript_code: %s\nscript_name: %s",
        #                  langscript_code, script_name)
        for script_name in transcription_scripts:
            logger.debug("Transcription script name %s", script_name)
            # if include_transcription and script_name in transcriptions:
            #     # text_grid[transcription_type][boundary_id]['transcription'][script_name] = transcriptions[script_name][i]
            #     text_grid[transcription_type][boundary_id]['transcription'][script_name] = transcriptions[
            #         transcription_type]['transcription'][boundary_id][script_name]

            # else:
            text_grid[transcription_type][boundary_id]['transcription'][script_name] = ""

            text_grid[transcription_type][boundary_id]['sentencemorphemicbreak'][script_name] = ""
            text_grid[transcription_type][boundary_id]['morphemes'][script_name] = ""
            text_grid[transcription_type][boundary_id]['gloss'][script_name] = ""
        if (len(translation_langscripts) != 0):
            for langscript_code, script_name in translation_langscripts.items():
                text_grid[transcription_type][boundary_id]['translation'][langscript_code] = ""
        else:
            text_grid[transcription_type][boundary_id]['translation'] = {}
    except:
        logger.exception("")

    return text_grid


def generate_text_grid_without_transcriptions(
        mongo, text_grid, boundaries, transcription_type, max_pause, min_boundary_size=2.0, offset_value=0.0):

    try:
        new_boundaries = get_new_boundaries(
            boundaries, max_pause)

        logger.debug('New boundaries before merge %s', new_boundaries)

        new_boundaries, new_transcriptions = merge_smaller_boundaries(
            new_boundaries, min_boundary_size=min_boundary_size)
        logger.debug('New boundaries after merge %s', new_boundaries)

        text_grid = update_text_grid(
            mongo, text_grid, new_boundaries, transcription_type, boundary_offset_value=offset_value)
    except:
        logger.exception("")

    return text_grid


def generate_text_grid_with_transcriptions(
        mongo, text_grid, boundaries, transcriptions, transcription_type, max_pause, min_boundary_size=2.0,  offset_value=0.0):

    try:
        new_boundaries, new_transcriptions = get_new_boundaries(
            boundaries, max_pause, include_transcription=True, transcriptions=transcriptions, )

        new_boundaries, new_transcriptions = merge_smaller_boundaries(
            new_boundaries, True, new_transcriptions, min_boundary_size)

        text_grid = update_text_grid(
            mongo, text_grid, new_boundaries, transcription_type, include_transcription=True, transcriptions=new_transcriptions, boundary_offset_value=offset_value)
    except:
        logger.exception("")

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


def generate_text_grid(mongo, text_grid, boundaries, transcriptions, transcription_type, max_pause, min_boundary_size=2.0, offset_value=0.0):
    logger.debug('Type of the data %s', transcription_type)
    if len(transcriptions) == 0:
        text_grid = generate_text_grid_without_transcriptions(
            mongo, text_grid, boundaries, transcription_type, max_pause, min_boundary_size, offset_value)
    else:
        text_grid = generate_text_grid_with_transcriptions(
            mongo, text_grid, boundaries, transcriptions, transcription_type, max_pause, min_boundary_size, offset_value)
    # if transcription_type == "sentence":
    #     text_grid = generate_sentence_text_grid(
    #         text_grid, boundaries, transcriptions, max_pause)
    return text_grid


def get_smaller_chunks_of_audio(
    boundaries, max_pause, max_new_file_duration, audio_duration
):
    new_audio_chunks = get_new_boundaries(
        boundaries, max_pause, max_boundary_size=max_new_file_duration)
    # new_audio_chunks[0]['start'] = 0
    # new_audio_chunks[-1]['end'] = audio_duration

    return new_audio_chunks


def get_boundary_lists_of_smaller_chunks(
        audio_chunk_boundaries, boundaries, audio_duration, slice_offset_value=0.0):

    logger.debug("All boundaries %s", boundaries)
    logger.debug("Audio chunk boundaries %s", audio_chunk_boundaries)
    all_chunk_boundaries = []
    offset_values = []
    slice_offset_values = []
    all_boundaries_start_values = [boundary['start']
                                   for boundary in boundaries]
    all_boundaries_end_values = [boundary['end'] for boundary in boundaries]

    for i, audio_chunk_boundary in enumerate(audio_chunk_boundaries):
        current_chunk_boundary_start = audio_chunk_boundary['start']
        current_chunk_boundary_end = audio_chunk_boundary['end']

        if current_chunk_boundary_start == 0:
            boundary_start_index = 0
        else:
            boundary_start_index = all_boundaries_start_values.index(
                current_chunk_boundary_start)

        if current_chunk_boundary_start == audio_duration:
            boundary_end_index = len(boundaries)-1
        else:
            boundary_end_index = all_boundaries_end_values.index(
                current_chunk_boundary_end)+1

        current_chunk_boundaries = boundaries[boundary_start_index: boundary_end_index]
        if i > 0:
            chunk_distance_prev = round(
                float(current_chunk_boundary_start - previous_chunk_end), 2)
            slice_offset_value_begin = round(
                float(slice_offset_value + chunk_distance_prev), 2)

            offset_values.append(current_chunk_boundary_start -
                                 slice_offset_value_begin)
            # for i, boundary in enumerate(current_chunk_boundaries):
            #     current_chunk_boundaries[i]['start'] += slice_offset_value
            #     current_chunk_boundaries[i]['end'] += slice_offset_value

            # current_chunk_boundaries = [{
            #     "start": boundary['start'],
            #     "end": boundary['end']-slice_offset_value_begin
            # } for boundary in current_chunk_boundaries]
        else:
            slice_offset_value_begin = 0.0
            offset_values.append(slice_offset_value_begin)

        all_chunk_boundaries.append(current_chunk_boundaries)

        slice_offset_values.append(slice_offset_value_begin)
        previous_chunk_end = current_chunk_boundary_end

    logger.debug("Total Slices with boundaries: %s; Total initial slices: %s", len(
        all_chunk_boundaries), len(audio_chunk_boundaries))
    logger.debug("Final Chunk Boundaries %s", all_chunk_boundaries)

    return all_chunk_boundaries, offset_values, slice_offset_values


def get_current_translation_langscripts(mongo):
    userprojects, projectsform = getdbcollections.getdbcollections(
        mongo, 'userprojects', 'projectsform')
    current_username = getcurrentusername.getcurrentusername()
    logger.debug('USERNAME: %s', current_username)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)

    current_project_scripts = projectsform.find_one({'projectname': activeprojectname}, {
        'Translation': 1, '_id': 0})

    try:
        translation = current_project_scripts['Translation'][1]
        # translations_langs = []
        # translation_scripts = []
        # for lang_script, script in translation.items():
        #     translations_langs.append(lang_script.split('-')[0])
        #     translation_scripts.append(script)

        # scriptCodeJSONFilePath = os.path.join(
        #     basedir_parent, 'static/json/scriptCode.json')
        # langScriptJSONFilePath = os.path.join(
        #     basedir_parent, 'static/json/langScript.json')

        # scriptCode = readJSONFile.readJSONFile(scriptCodeJSONFilePath)
        # langScript = readJSONFile.readJSONFile(langScriptJSONFilePath)

        # all_lang_scripts = {}
        # for current_lang, current_script in zip(translations_langs, translation_scripts):
        #     logger.debug("current_lang: %s\ncurrent_script: %s",
        #                  current_lang, current_script)
        #     current_script_code = scriptCode[current_script]
        #     current_language_code = current_lang[:3].lower()
        #     langscript_code = current_language_code + '-' + current_script_code
        #     all_lang_scripts[langscript_code] = langscript_code
        # return all_lang_scripts
        return translation
    except Exception as error:
        logger.debug(error)
        return dict()


def get_current_transcription_langscripts(mongo):
    try:
        userprojects, projectsform = getdbcollections.getdbcollections(
            mongo, 'userprojects', 'projectsform')
        current_username = getcurrentusername.getcurrentusername()
        logger.debug('USERNAME: %s', current_username)
        activeprojectname = getactiveprojectname.getactiveprojectname(
            current_username, userprojects)

        current_project_scripts = projectsform.find_one({'projectname': activeprojectname}, {
            'Transcription': 1, 'Audio Language': 1, '_id': 0})
        logger.debug("current_project_scripts: %s", current_project_scripts)
        project_language = current_project_scripts['Audio Language'][1]
        # project_language_code = project_language[0][:3].lower()

        project_scripts = current_project_scripts['Transcription'][1]

        # scriptCodeJSONFilePath = os.path.join(
        #     basedir_parent, 'static/json/scriptCode.json')
        # langScriptJSONFilePath = os.path.join(
        #     basedir_parent, 'static/json/langScript.json')

        # scriptCode = readJSONFile.readJSONFile(scriptCodeJSONFilePath)
        # langScript = readJSONFile.readJSONFile(langScriptJSONFilePath)

        # all_lang_scripts = {}
        # for current_script in project_scripts:
        #     current_script_code = scriptCode[current_script]
        #     langscript_code = project_language_code + '-' + current_script_code
        #     all_lang_scripts[langscript_code] = current_script
        # logger.debug("all_lang_scripts: %s", all_lang_scripts)
        return list(project_scripts)
    except:
        logger.exception("")


def get_audio_transcriptions(mongo, model_params, model_name, audio_data=[], model_langscript=["IPA"], model_type="local", transcription_type='sentence', hf_token=''):
    transcriptions = {}
    transcribed = 0
    # transcription_scripts = []
    if len(model_langscript) == 0:
        current_lang_scripts = get_current_transcription_langscripts(mongo)
    else:
        current_lang_scripts = model_langscript
    logger.debug('All current lang scripts %s', current_lang_scripts)

    if model_name == '':
        for transcription_model in all_model_names['transcription']:
            target = transcription_model['target']
            # target_val = current_lang_scripts[target]
            if target in current_lang_scripts:
                target_val = current_lang_scripts[target]
                if target_val not in transcriptions:
                    model_names = transcription_model['model']['local']
                    model_paths = transcription_model['model']['localpath']
                    model_params['model_path'] = model_paths[0]

                    if len(model_names) > 0:
                        model_name = model_names[0]
                        transcriptions[target_val] = predictFromLocalModels.getTranscription(
                            model_names[0], model_params)
                        transcribed = 1
    else:
        # for target_val in current_lang_scripts:
        # target_val = current_lang_scripts[target]
        transcriptions[transcription_type] = {'transcription': {}}
        # if current_lang_scripts not in transcriptions:
        if model_type == 'local':
            transcriptions[transcription_type]['transcription'] = predictFromLocalModels.getTranscription(
                model_name, model_params)
        elif model_type == 'hfapi':
            transcriptions[transcription_type]['transcription'] = predictFromAPI.predictFromHFModel(
                model_inputs=audio_data, model_url=model_name, hf_token=hf_token, model_params=model_params, script_names=current_lang_scripts)
        elif model_type == 'bhashini':
            transcriptions[transcription_type]['transcription'], transcribed = predictFromAPI.transcribe_using_bhashini(
                model_inputs=audio_data, model_url=model_name, model_params=model_params, script_names=current_lang_scripts)
        # transcribed = 1

    return transcriptions, transcribed, model_name


def get_audio_boundaries(model_params, model_name, model_type="local"):
    try:
        if model_name == '':
            for textgrid_boundary_model in all_model_names['textGrid_boundary']:
                model_names = textgrid_boundary_model['model']['local']
                model_paths = textgrid_boundary_model['model']['localpath']
                model_params['model_path'] = model_paths[0]

                if len(model_names) > 0:
                    model_name = model_names[0]
                    boundaries, cleaned_file = predictFromLocalModels.get_boundaries(
                        model_names[0], model_params)
                    break
        else:
            if model_type == 'local':
                boundaries, cleaned_file = predictFromLocalModels.get_boundaries(
                    model_name, model_params)
        logger.debug(boundaries)
    except:
        logger.exception("")

    return boundaries, cleaned_file, model_name


def get_audio_chunk_bytes(audio_file, start_boundary, end_boundary, boundary_id, audio_path):
    try:
        start_boundary = start_boundary*1000
        end_boundary = end_boundary*1000
        current_audio_file = audio_file[start_boundary: end_boundary]
        # write_path = audio_path.replace('.wav', '_'+boundary_id+'.wav')
        audio_segment_bytes = BytesIO()
        # current_audio_file.stream.seek(0)

        current_audio_file.export(audio_segment_bytes, format="wav")
        # current_audio_file.export(write_path, format="wav")

        # with open(write_path, "wb") as f:
        #     f.write(audio_segment_bytes.getbuffer())
    except:
        logger.exception("")

    return audio_segment_bytes.read()
    # return write_path


def generate_boundary_id(current_boundary):
    try:
        start_boundary = round(float(current_boundary['start']), 2)
        end_boundary = round(float(current_boundary['end']), 2)
        boundary_id_start = get_boundary_id_from_number(
            format(start_boundary, '.2f'), 5)
        boundary_id_end = get_boundary_id_from_number(
            format(end_boundary, '.2f'), 5)
        boundary_id = boundary_id_start+boundary_id_end
    except:
        logger.exception("")

    return boundary_id


def generate_boundaries(vad_model,
                        max_pause_boundary,
                        audio_path
                        ):
    try:
        boundaries = []
        min_speech_duration = 250
        min_silence_duration = 100
        vad_model_name = ''
        vad_model_type = 'local'
        max_pause_boundary_ms = max_pause_boundary*1000
        if max_pause_boundary < min_speech_duration:
            min_speech_duration = int(max_pause_boundary_ms)

            if max_pause_boundary < min_silence_duration:
                min_silence_duration = int(max_pause_boundary)

        # if 'textGrid_boundary' in all_model_names:
        vad_model_params = {
            "audio_file": audio_path,
            "SAMPLING_RATE": 16000,
            "remove_pauses": False,
            "USE_ONNX": False,
            "minimum_speech_duration": min_speech_duration,
            "minimum_silence_duration": min_silence_duration
        }
        # logger.debug('Vad Model %s', vad_model)
        if len(vad_model) > 0:
            vad_model_name = vad_model['model_name']
            add_vad_model_params = vad_model['model_params']
            vad_model_type = vad_model['model_type']
            vad_model_params.update(add_vad_model_params)

        vad_start = datetime.now()
        boundaries, cleaned_file, vad_model_name = get_audio_boundaries(
            vad_model_params, vad_model_name, vad_model_type)
        vad_end = datetime.now()
    except:
        logger.exception("")

    return boundaries, cleaned_file, vad_model_name, vad_start, vad_end, vad_model_params


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
                              min_boundary_size,
                              audio_duration,
                              slice_offset_value=0.0,
                              audio_filename='',
                              hf_token='',
                              all_audio_bytes={},
                              all_text_grids=[],
                              create_new_boundaries=False,
                              boundary_ids=['*']):
    # logger.debug("create_new_boundaries: %s", create_new_boundaries)
    try:
        model_details = {}
        # all_text_grids = []

        audio_chunk_boundaries = []

        boundaries = []
        offset_values = [0.0]
        slice_offset_values = [0.0]
        transcriptions = {}
        transcribed = 0
        transcription_data = {}

        # TODO: This needs to be improved and based on user-inputs regarding the choice
        # of a model. We could store project-specific prefeerences here.
        # Currently it gives preference to local models and select the first
        # model in the list.
        # logger.debug("Run vad: %s, Run ASR: %s, Split: %s",
        #             run_vad, run_asr, split_into_smaller_chunks)
        # logger.debug('All audio bytes keys %s \nLength: %s',
        #             all_audio_bytes.keys(), len(all_audio_bytes))

        if run_vad or split_into_smaller_chunks:
            # logger.debug('Boundaries received', boundaries)
            boundaries, cleaned_file, vad_model_name, vad_start, vad_end, vad_model_params = generate_boundaries(vad_model,
                                                                                                                 max_pause_boundary,
                                                                                                                 audio_path
                                                                                                                 )
            model_details.update([('vad_model_name', vad_model_name), ('vad_model_params',
                                                                       vad_model_params), ('vad_start', vad_start), ('vad_end', vad_end)])
            if split_into_smaller_chunks:
                audio_chunk_boundaries = get_smaller_chunks_of_audio(
                    boundaries, max_pause_slice, max_new_file_duration, audio_duration)

                audio_chunk_boundary_lists, offset_values, slice_offset_values = get_boundary_lists_of_smaller_chunks(
                    audio_chunk_boundaries, boundaries, audio_duration, slice_offset_value)

            else:
                audio_chunk_boundaries = [
                    {'start': boundaries[0], 'end': boundaries[-1]}]
                audio_chunk_boundary_lists = [boundaries]

            # logger.debug('Total audio chunk boundaries %s Total offset values %s Total slice offset values %s', len(
            #     audio_chunk_boundary_lists), len(offset_values), len(slice_offset_values))
            all_text_grids = []
            for audio_chunk_boundary_list, offset_value in zip(audio_chunk_boundary_lists, offset_values):
                logger.debug('Length of all text grids %s',
                             len(all_text_grids))
                blank_text_grid = get_blank_text_grid()
                # {
                #     "discourse": {},
                #     "sentence": {},
                #     "word": {},
                #     "phoneme": {}
                # }
                current_text_grid = generate_text_grid(
                    mongo, blank_text_grid, audio_chunk_boundary_list, transcriptions, transcription_type, max_pause_boundary, min_boundary_size, offset_value=offset_value)
                # print('length of current text grid %s', len(current_text_grid))
                all_text_grids.append(current_text_grid)

            # if run_asr and 'transcription' in all_model_names:
        elif run_asr:
            # audio_duration, audio_file = get_audio_duration_from_file(audio_path)
            logger.info('Running ASR on file %s', audio_path)
            audio_file = AudioSegment.from_file(audio_path)

            logger.info('Running ASR on existing boundaries')
            if len(all_text_grids) > 0:
                current_text_grid = all_text_grids[0][transcription_type]
            else:
                current_text_grid = {}
            # logger.debug('Full Text Grid %s \nTotal text grids %s',
            #             all_text_grids, len(all_text_grids))
            # logger.debug('Current Text Grid %s \nLength: %s',
            #             current_text_grid, len(current_text_grid))
            # logger.debug('All audio bytes keys %s \nLength: %s',
            #             all_audio_bytes.keys(), len(all_audio_bytes))

            # logger.debug("create_new_boundaries: %s", create_new_boundaries)
            create_vad = False
            if len(asr_model) > 0:
                inference_source = asr_model['model_params']['model_api']
                if inference_source == 'hfinference' and create_new_boundaries:
                    create_vad = True
                    create_new_boundaries = False
                elif inference_source == 'bhashini' and len(current_text_grid) == 0:
                    create_vad = True
                    create_new_boundaries = False
            # logger.debug("create_new_boundaries: %s", create_new_boundaries)
            if create_vad:
                # logger.debug('All audio bytes keys %s \nLength: %s',
                #             all_audio_bytes.keys(), len(all_audio_bytes))
                boundaries, __, vad_model_name, vad_start, vad_end, vad_model_params = generate_boundaries(vad_model,
                                                                                                           max_pause_boundary,
                                                                                                           audio_path
                                                                                                           )
                model_details.update([('vad_model_name', vad_model_name), ('vad_model_params',
                                                                           vad_model_params), ('vad_start', vad_start), ('vad_end', vad_end)])
                audio_chunk_boundaries = [
                    {'start': boundaries[0], 'end': boundaries[-1]}]
                audio_chunk_boundary_lists = [boundaries]

                blank_text_grid = get_blank_text_grid()
                all_text_grids = []
                for audio_chunk_boundary_list in audio_chunk_boundary_lists:
                    current_text_grid = generate_text_grid(
                        mongo, blank_text_grid, audio_chunk_boundary_list, transcriptions, transcription_type, max_pause_boundary, min_boundary_size)
                    all_text_grids.append(current_text_grid)

                logger.info('Current text grid after VAD %s\n Length: %s',
                            current_text_grid, len(current_text_grid))
                # logger.debug('All audio bytes keys %s \nLength: %s',
                #             all_audio_bytes.keys(), len(all_audio_bytes))
                current_text_grid = all_text_grids[0][transcription_type]
            # audio_file = AudioSegment.from_file(audio_path)

            # for i, current_boundary in enumerate(boundaries):
            #     start_boundary = round(float(current_boundary['start']), 2)
            #     end_boundary = round(float(current_boundary['end']), 2)
            #     boundary_id = generate_boundary_id(current_boundary)
            #     all_audio_bytes[boundary_id] = get_audio_chunk_bytes(
            #         audio_file, start_boundary, end_boundary, boundary_id, audio_path)
            # current_audio_file_segment = FileStorage(
            # audio_segment_bytes, filename=current_audio_filename)
            # else:
            # audio_file = AudioSegment.from_file(audio_path)
            # logger.debug("create_new_boundaries: %s", create_new_boundaries)
            if (len(current_text_grid) > 0) and (not create_new_boundaries):
                logger.info('All audio bytes keys %s \nLength: %s',
                            all_audio_bytes.keys(), len(all_audio_bytes))
                logger.info('All text grid keys %s \nLength: %s',
                            current_text_grid.keys(), len(current_text_grid))
                for boundary_id, boundary_details in current_text_grid.items():
                    if '*' in boundary_ids or boundary_id in boundary_ids:
                        start_boundary = round(
                            float(boundary_details['start']), 2)
                        end_boundary = round(float(boundary_details['end']), 2)
                        all_audio_bytes[boundary_id] = get_audio_chunk_bytes(
                            audio_file, start_boundary, end_boundary, boundary_id, audio_path)
                    # current_audio_file = audio_file[start_boundary: end_boundary]
                    # audio_segment_bytes = BytesIO()
                    # current_audio_file.export(audio_segment_bytes, format="wav")
                    # all_audio_bytes[boundary_id] = current_audio_file
            else:
                start_boundary = 0.0
                end_boundary = round(float(audio_duration), 2)
                current_boundary = {
                    'start': start_boundary, 'end': end_boundary}
                boundary_id = generate_boundary_id(current_boundary)
                all_audio_bytes[boundary_id] = get_audio_chunk_bytes(
                    audio_file, start_boundary, end_boundary, boundary_id, audio_path)

                # create_new_boundaries = True

                blank_text_grid = get_blank_text_grid()
                all_text_grids = [blank_text_grid]

                audio_chunk_boundaries = [
                    {'start': start_boundary, 'end': end_boundary}]
                boundaries.append(
                    {'start': start_boundary, 'end': end_boundary})
                audio_chunk_boundary_lists = [boundaries]
                for audio_chunk_boundary_list in audio_chunk_boundary_lists:
                    current_text_grid = generate_text_grid(
                        mongo, blank_text_grid, audio_chunk_boundary_list, transcriptions, transcription_type, max_pause_boundary, min_boundary_size)
                    all_text_grids.append(current_text_grid)

                # logger.debug('Full Text Grid %s \nTotal text grids %s',
                #             all_text_grids, len(all_text_grids))
                current_text_grid = all_text_grids[0][transcription_type]
                # logger.debug('Current Text Grid %s Length: %s',
                #             current_text_grid, len(current_text_grid))

            logger.info('All audio bytes keys %s \nLength: %s',
                        all_audio_bytes.keys(), len(all_audio_bytes))
            logger.info('All text grid keys %s \nLength: %s',
                        current_text_grid.keys(), len(current_text_grid))
            asr_model_name = ''
            asr_model_langscript = {}
            asr_model_type = 'local'
            asr_model_params = {
                "audio_file": audio_filename,
                "boundaries": boundaries
            }
            # logger.debug('ASR Model %s', asr_model)
            if len(asr_model) > 0:
                asr_model_name = asr_model['model_name']
                add_asr_model_params = asr_model['model_params']
                asr_model_langscript = asr_model['target']
                asr_model_type = asr_model['model_type']
                asr_model_params.update(add_asr_model_params)

            asr_start = datetime.now()
            transcriptions, transcribed, asr_model_name = get_audio_transcriptions(
                mongo, model_params=asr_model_params, model_name=asr_model_name, audio_data=all_audio_bytes, model_langscript=asr_model_langscript, model_type=asr_model_type, hf_token=hf_token)
            asr_end = datetime.now()

            transcription_data = transcriptions[transcription_type]['transcription']

            model_details.update([('asr_model_name', asr_model_name), ('asr_model_params',
                                                                       asr_model_params), ('asr_start', asr_start), ('asr_end', asr_end)])

            # if create_new_boundaries:
            #     blank_text_grid = get_blank_text_grid()
            #     for audio_chunk_boundary_list in audio_chunk_boundary_lists:
            #         current_text_grid = generate_text_grid(
            #             mongo, blank_text_grid, audio_chunk_boundary_list, transcriptions, transcription_type, max_pause_boundary, min_boundary_size)
            #         all_text_grids.append(current_text_grid)
            # else:
            # create_new_boundaries = True
            # logger.debug("create_new_boundaries: %s", create_new_boundaries)
            if create_new_boundaries:
                current_text_grid = get_blank_text_grid()
                current_text_grid = update_blank_text_grid(
                    mongo, current_text_grid, transcription_type, transcriptions)
            else:
                current_text_grid = all_text_grids[0]
                current_text_grid = update_existing_text_grid(
                    current_text_grid, transcription_type, transcriptions, update_boundaries=boundary_ids)
            all_text_grids = [current_text_grid]

        else:
            blank_text_grid = get_blank_text_grid()
            audio_chunk_boundaries = []
            all_text_grids = [blank_text_grid]
            model_details = {}
    except:
        logger.exception("")

    return audio_chunk_boundaries, transcription_data, all_text_grids, offset_values, slice_offset_values, transcribed, model_details


def save_uploaded_audio_in_localFs(audio_store_path,
                                   audio_store_dir,
                                   audio_id,
                                   new_audio_file,
                                   delete_previous_files):
    audioFolder = os.path.join(audio_store_path, audio_store_dir)
    logger.debug('Audio folder path %s', audioFolder)

    if delete_previous_files:
        if (os.path.exists(audioFolder)):
            logger.debug('Audio folder path exists %s',
                         audioFolder, 'deleting')
            shutil.rmtree(audioFolder)
        os.mkdir(audioFolder)
    else:
        if (not os.path.exists(audioFolder)):
            os.mkdir(audioFolder)

    file_path = ''
    if (new_audio_file is not None):
        file_name = audio_id
        logger.debug('File name %s', file_name)
        file_path = os.path.join(audio_store_dir, file_name)
        saved_path = os.path.join(audio_store_path, file_path)
        logger.debug('Save file path %s', saved_path)
        # open(saved_path, 'wb').write(new_audio_file)
        new_audio_file.save(saved_path)
        logger.debug('Audio saved path %s', saved_path)
    else:
        saved_path = ''

    return saved_path


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
                                    store_in_mongo=True,
                                    delete_previous_files=True):

    if store_in_mongo:
        fs_file_id = mongo.save_file(updated_audio_filename,
                                     new_audio_file,
                                     audioId=audio_id,
                                     username=projectowner,
                                     projectname=activeprojectname,
                                     updatedBy=current_username,
                                     filedeleteFLAG=0)
        if store_in_local:
            saved_path = getaudiowaveformfilefromfs(mongo,
                                                    audio_store_path,
                                                    audio_store_dir,
                                                    audio_id,
                                                    'audioId',
                                                    delete_previous_files)
            logger.debug('Audio saved path %s', saved_path)
        else:
            saved_path = ''
    else:
        fs_file_id = ''
        if store_in_local:
            saved_path = save_uploaded_audio_in_localFs(audio_store_path,
                                                        audio_store_dir,
                                                        audio_id,
                                                        new_audio_file,
                                                        delete_previous_files)
        else:
            saved_path = ''
    # logger.debug('audioLength %s', new_audio_file['audiofile'].content_length)

    # logger.debug('json_basedir %s', json_basedir)

    # # audiowaveform_json_path = os.path.join(audiowaveform_json, 'audiowaveform_json')

    # logger.debug('audiowaveform_json %s', audiowaveform_json)
    # logger.debug('audiowaveform_json_path %s', audiowaveform_json_path)

    # logger.debug('new_audio_file %s %s', type(new_audio_file), new_audio_file)
    # audiowaveform_file = new_audio_file.stream.seek(0)
    # audiowaveform_file.stream.seek(0)
    # getaudiofilefromfs(mongo,
    #                 audiowaveform_json,
    #                 audio_id,
    #                 'audio')

    return fs_file_id, saved_path


def get_audio_id_filename(audiofile, audio_filename="no_filename"):
    if audiofile['audiofile'].filename != '':
        audio_filename = audiofile['audiofile'].filename
        audio_filename = audio_filename[:audio_filename.rindex('.')] + '.wav'
    audio_id = 'A'+re.sub(r'[-: \.]', '', str(datetime.now()))
    # audio_filename = audio_id+

    return audio_id, audio_filename


def get_audio_waveform_json(audiowaveform_json, json_dir, audio_filename):
    audiowaveform_audio_path = os.path.join(
        audiowaveform_json, json_dir)
    audiowaveform_json_path = os.path.join(audiowaveform_json, json_dir)
    audiowaveform_audio_path = os.path.join(
        audiowaveform_audio_path, audio_filename)
    # logger.debug('audiowaveform_audio_path %s', audiowaveform_audio_path)
    # logger.debug('audiowaveform_json_path %s', audiowaveform_json_path)
    audiowaveform_json = createaudiowaveform(
        audiowaveform_audio_path, audiowaveform_json_path, audio_filename)

    return audiowaveform_json


def delete_one_audio_file(projects_collection,
                          transcriptions_collection,
                          project_name,
                          current_username,
                          active_speaker_id,
                          audio_id,
                          speaker_audio_ids,
                          update_latest_audio_id=1):
    try:
        # logger.debug("project_name: %s, audio_id: %s", project_name, audio_id)
        transcription_doc_id = transcriptions_collection.find_one_and_update({
            "projectname": project_name,
            "audioId": audio_id
        },
            {"$set": {"audiodeleteFLAG": 1}},
            projection={'_id': True},
            return_document=ReturnDocument.AFTER)['_id']
        # logger.debug('DELETED transcription_doc_id: %s, %s',
        #              transcription_doc_id, type(transcription_doc_id))

        if (update_latest_audio_id):
            latest_audio_id = getnewaudioid(projects_collection,
                                            project_name,
                                            audio_id,
                                            active_speaker_id,
                                            speaker_audio_ids,
                                            'next')
            # print(latest_audio_id)
            # logger.debug("latest_audio_id: %s", latest_audio_id)
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
    # logger.debug("%s, %s, %s", transcriptions_collection,
    #              project_name,
    #              audio_id)
    audio_delete_flag = transcriptions_collection.find_one({"projectname": project_name,
                                                            "audioId": audio_id},
                                                           {"_id": 0,
                                                            "audiodeleteFLAG": 1})["audiodeleteFLAG"]

    return audio_delete_flag


def revoke_deleted_audio(projects_collection,
                         transcriptions_collection,
                         project_name,
                         active_speaker_id,
                         audio_id,
                         speaker_audio_ids):
    try:
        # logger.debug("project_name: %s, audio_id: %s", project_name, audio_id)
        transcription_doc_id = transcriptions_collection.find_one_and_update({
            "projectname": project_name,
            "audioId": audio_id
        },
            {"$set": {"audiodeleteFLAG": 0}},
            projection={'_id': True},
            return_document=ReturnDocument.AFTER)['_id']
        # logger.debug('REVOKED transcription_doc_id: %s, %s',
        #              transcription_doc_id, type(transcription_doc_id))

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
                 current_username,
                 active_speaker_id,
                 speaker_audio_ids,
                 start_from=0,
                 number_of_audios=10,
                 audio_delete_flag=0,
                 all_data=False):
    # logger.debug(f"start_from: {start_from}\nnumber_of_audios: {number_of_audios}")
    # logger.debug(active_speaker_id)
    aggregate_output_list = []
    total_records = 0
    try:
        # logger.debug("speaker_audio_ids: %s", pformat(speaker_audio_ids))
        # logger.debug("speaker_audio_ids: %s", len(speaker_audio_ids))
        if (isinstance(active_speaker_id, str)):
            active_speaker_id = [active_speaker_id]
        aggregate_output = data_collection.aggregate([
            {
                "$match": {
                    "projectname": activeprojectname,
                    # "speakerId": active_speaker_id,
                    "speakerId": {'$in': active_speaker_id},
                    "audiodeleteFLAG": audio_delete_flag
                }
            },
            {
                "$sort": {
                    "audioId": 1
                }
            },
            {"$skip": start_from},
            {"$limit": number_of_audios-start_from},
            {
                "$project": {
                    "_id": 0,
                    "audioId": 1,
                    "audioFilename": 1,
                    "speakerId": 1,
                    current_username + '.audioCompleteFLAG': 1
                }
            }
        ])
        # logger.debug("aggregate_output: %s", aggregate_output)

        for doc in aggregate_output:
            # logger.debug("aggregate_output: %s", pformat(doc))
            if (doc['audioId'] in speaker_audio_ids):
                doc['Audio File'] = ''
                sids = doc['speakerId']
                if (isinstance(sids, str)):
                    sids = [sids]
                for sid in sids:
                    # logger.debug(sid)
                    doc['Shared With'] = audio_shared_with(activeprojectname,
                                                           sid,
                                                           doc['audioId'])
                    # logger.debug(doc['Shared With'])
                if current_username in doc:
                    doc['Transcribed'] = doc.pop(current_username, {}).get(
                        'audioCompleteFLAG', False)

                aggregate_output_list.append(doc)
                # logger.debug(len(aggregate_output_list))

        # logger.debug('aggregate_output_list: %s', pformat(aggregate_output_list))
        # total_records_aggregate = data_collection.aggregate([
        #     {
        #         "$match": {
        #             "projectname": activeprojectname,
        #             # "speakerId": active_speaker_id,
        #             "speakerId": {'$in': active_speaker_id},
        #             "audiodeleteFLAG": audio_delete_flag
        #         }
        #     },
        #     {
        #         "$count": "total_records"
        #     }
        # ])
        # for tr in total_records_aggregate:
        #     # logger.debug(tr)
        #     if ('total_records' in tr):
        #         total_records = tr['total_records']
        # # logger.debug('total_records AUDIO: %s', total_records)
        total_records = len(speaker_audio_ids)
    except:
        logger.exception("")

    return (total_records,
            aggregate_output_list)


def audio_shared_with(activeprojectname,
                      active_speaker_id,
                      audio_id):
    try:
        # logger.debug(active_speaker_id)
        # logger.debug(audio_id)
        shared_with_list = []
        projects_collection, = getdbcollections.getdbcollections(
            mongo, 'projects')

        shared_with_info = projects_collection.find_one({"projectname": activeprojectname},
                                                        {"_id": 0,
                                                        "speakerIds": 1,
                                                         "fileSpeakerIds": 1})
        # logger.debug(pformat(shared_with_info))
        if ('speakerIds' in shared_with_info):
            shared_with_list = [user for user, user_speaker_ids in shared_with_info['speakerIds'].items(
            ) if active_speaker_id in user_speaker_ids]
        # logger.debug(shared_with_list)
        if ('fileSpeakerIds' in shared_with_info):
            for user, user_speaker_ids in shared_with_info['fileSpeakerIds'].items():
                # logger.debug(user)
                # logger.debug(user_speaker_ids)
                if (active_speaker_id in user_speaker_ids and
                        audio_id in user_speaker_ids[active_speaker_id]):
                    shared_with_list.append(user)
                    # logger.debug(shared_with_list)
        shared_with_list = ', '.join(list(set(shared_with_list)))
    except:
        logger.exception("")
    # logger.debug(shared_with_list)
    return shared_with_list


def get_audio_sorting_subcategories(speakerdetails_collection,
                                    activeprojectname,
                                    speakerids,
                                    selected_audio_sorting_category
                                    ):
    # logger.debug("speakerids: %s", pformat(speakerids))
    selected_audio_sorting_subcategory = {
        "agegroup": "Age Group",
        "gender": "Gender",
        "educationlevel": "Education Level",
        "educationmediumupto12": "Education Medium Upto 12",
        "educationmediumafter12": "Education Medium After 12",
        "speakerspeaklanguage": "Speaker Speak Language"
    }
    aggregate_output = speakerdetails_collection.aggregate([
        {
            "$match": {
                "projectname": activeprojectname,
                "isActive": 1
            }
        },
        {
            "$project": {
                "_id": 0,
                # "current.sourceMetadata."+selected_audio_sorting_category: 1
                "current.sourceMetadata": 1,
                "lifesourceid": 1
            }
        }
    ])
    # logger.debug("aggregate_output: %s", aggregate_output)
    aggregate_output_dict = {}
    for doc in aggregate_output:
        # logger.debug("aggregate_output: %s", pformat(doc))
        try:
            speaker = doc["lifesourceid"]
            if (speaker in speakerids):
                # audio_sorting_subcategory = doc["current"]["sourceMetadata"][selected_audio_sorting_category]
                audio_sorting_subcategory = doc["current"]["sourceMetadata"]
                # logger.debug("aggregate_output: %s", pformat(audio_sorting_subcategory))
                for key, value in audio_sorting_subcategory.items():
                    # logger.debug('%s, %s', key, value)
                    if (key in list(selected_audio_sorting_subcategory_self_map.values())):
                        selected_audio_sorting_subcategory = selected_audio_sorting_subcategory_new
                    if (key in selected_audio_sorting_subcategory or
                            key in list(selected_audio_sorting_subcategory_self_map.values())):
                        # logger.debug(key)
                        # logger.debug(selected_audio_sorting_subcategory)
                        selected_audio_sorting_subcategory_value = selected_audio_sorting_subcategory[
                            key]
                        if (selected_audio_sorting_subcategory_value in aggregate_output_dict):
                            if (isinstance(value, list)):
                                for subcat in value:
                                    aggregate_output_dict[selected_audio_sorting_subcategory_value].append(
                                        subcat)
                            else:
                                aggregate_output_dict[selected_audio_sorting_subcategory_value].append(
                                    value)
                        else:
                            if (isinstance(value, list)):
                                aggregate_output_dict[selected_audio_sorting_subcategory_value] = value
                            else:
                                aggregate_output_dict[selected_audio_sorting_subcategory_value] = [
                                    value]
                        aggregate_output_dict[selected_audio_sorting_subcategory_value] = list(
                            set(aggregate_output_dict[selected_audio_sorting_subcategory_value]))
        except:
            logger.exception("")

    return aggregate_output_dict


def create_audio_sorting_subcategories_new(aggregate_output_dict,
                                           key,
                                           value):
    exclude = ['updatedBy',
               'current_date',
               'accessed_at',
               # 'audio_language',
               'published_date',
               'published_time',
               'publisher',
               'publisher_id',
               # 'searchKeywords',
               # 'sourceTags',
               # 'total_comments',
               # 'total_views',
               'video_description',
               'video_dislikes',
               # 'video_duration',
               'video_favourites',
               'video_likes',
               # 'video_link',
               # 'video_tags',
               # 'video_title',
               'lifespeakerid',
               'karyaaccesscode',
               'karyaspeakerid',
               ''
               ]
    if (key not in exclude):
        if (key not in aggregate_output_dict):
            aggregate_output_dict[key] = []
        if (isinstance(value, str)):
            if (len(value.strip()) != 0):
                aggregate_output_dict[key].extend([value])
                aggregate_output_dict[key] = list(
                    set(aggregate_output_dict[key]))
        elif (isinstance(value, list)):
            value = [x for x in value if x != '']
            aggregate_output_dict[key].extend(value)
            aggregate_output_dict[key] = list(set(aggregate_output_dict[key]))

    return aggregate_output_dict


def get_audio_sorting_subcategories_new(speakerdetails_collection,
                                        activeprojectname,
                                        speakerids):
    # logger.debug("speakerids: %s", pformat(speakerids))
    aggregate_output = speakerdetails_collection.aggregate([
        {
            "$match": {
                "projectname": activeprojectname,
                "isActive": 1
            }
        },
        {
            "$project": {
                "_id": 0,
                "current": 1,
                "lifesourceid": 1
            }
        }
    ])
    # logger.debug("aggregate_output: %s", aggregate_output)
    aggregate_output_dict = {}
    for doc in aggregate_output:
        # logger.debug("aggregate_output: %s", pformat(doc))
        try:
            speaker = doc["lifesourceid"]
            if (speaker in speakerids and
                    speaker != ''):
                # logger.debug("aggregate_output: %s", pformat(doc))
                # logger.debug(speaker)
                # audio_sorting_subcategory = doc["current"]["sourceMetadata"][selected_audio_sorting_category]
                audio_sorting_subcategory = doc["current"]
                # logger.debug("aggregate_output: %s", pformat(audio_sorting_subcategory))
                for key, value in audio_sorting_subcategory.items():
                    # logger.debug('%s, %s', key, value)
                    if (isinstance(value, dict)):
                        # logger.debug('%s, %s', key, value)
                        for k, v in value.items():
                            # logger.debug('%s, %s', k, v)
                            aggregate_output_dict = create_audio_sorting_subcategories_new(aggregate_output_dict,
                                                                                           k,
                                                                                           v)
                    else:
                        aggregate_output_dict = create_audio_sorting_subcategories_new(aggregate_output_dict,
                                                                                       key,
                                                                                       value)
                # logger.debug(pformat(aggregate_output_dict))
        except:
            logger.exception("")

    # logger.debug(pformat(aggregate_output_dict))
    return aggregate_output_dict


def get_audio_sorting_subcategories_derived(transcriptions_collection,
                                            activeprojectname,
                                            speakerids,
                                            audio_sorting_sub_categories
                                            ):
    # logger.debug("speakerids: %s", pformat(speakerids))
    aggregate_output = transcriptions_collection.aggregate([
        {
            "$match": {
                "projectname": activeprojectname,
                "audiodeleteFLAG": 0
            }
        },
        {
            "$project": {
                "_id": 0,
                # "current.sourceMetadata."+selected_audio_sorting_category: 1
                "prompt": 1,
                "speakerId": 1
            }
        }
    ])
    # logger.debug("aggregate_output: %s", aggregate_output)
    # audio_sorting_sub_categories = {}
    for doc in aggregate_output:
        # logger.debug("aggregate_output: %s", pformat(doc))
        try:
            speaker = doc["speakerId"]
            if (speaker != '' and
                    speaker in speakerids):
                # audio_sorting_subcategory = doc["current"]["sourceMetadata"][selected_audio_sorting_category]
                audio_sorting_subcategory = doc["prompt"]
                # logger.debug("aggregate_output: %s", pformat(audio_sorting_subcategory))
                for key, value in audio_sorting_subcategory.items():
                    if (key != 'content'):
                        selected_audio_sorting_subcategory_value = key
                        if (selected_audio_sorting_subcategory_value in audio_sorting_sub_categories):
                            if (isinstance(value, list)):
                                for subcat in value:
                                    audio_sorting_sub_categories[selected_audio_sorting_subcategory_value].append(
                                        subcat)
                            else:
                                audio_sorting_sub_categories[selected_audio_sorting_subcategory_value].append(
                                    value)
                        else:
                            if (isinstance(value, list)):
                                audio_sorting_sub_categories[selected_audio_sorting_subcategory_value] = value
                            else:
                                audio_sorting_sub_categories[selected_audio_sorting_subcategory_value] = [
                                    value]
                        audio_sorting_sub_categories[selected_audio_sorting_subcategory_value] = list(
                            set(audio_sorting_sub_categories[selected_audio_sorting_subcategory_value]))
        except:
            logger.exception("")

    return audio_sorting_sub_categories


def filter_on_category_path(speakerdetails_collection,
                            activeprojectname,
                            filter_options):
    aggregate_output = speakerdetails_collection.aggregate([
        {
            "$match": {
                "projectname": activeprojectname,
                "isActive": 1
            }
        },
        {
            "$project": {
                "_id": 0,
                "current": 1,
                "lifesourceid": 1
            }
        }
    ])
    # logger.debug("aggregate_output: %s", aggregate_output)
    aggregate_output_dict = {}
    used_filter_options = []
    for doc in aggregate_output:
        # logger.debug("aggregate_output: %s", pformat(doc))
        try:
            speaker = doc["lifesourceid"]
            if (speaker != ''):
                audio_sorting_subcategory = doc["current"]
                # logger.debug("aggregate_output: %s", pformat(audio_sorting_subcategory))
                for key, value in audio_sorting_subcategory.items():
                    # logger.debug('%s, %s', key, value)
                    if (isinstance(value, dict)):
                        # logger.debug('%s, %s', key, value)
                        for k, v in value.items():
                            # logger.debug('%s, %s', k, v)
                            # if (k in filter_options):
                            #     logger.debug(filter_options[k])
                            if (k in filter_options and
                                len(filter_options[k]) != 0 and
                                    'current.'+key+'.'+k not in aggregate_output_dict):
                                aggregate_output_dict['current.'+key +
                                                      '.'+k] = {"$in": filter_options[k]}
                                used_filter_options.append(k)
                    else:
                        if (key in filter_options and
                                len(filter_options[key]) != 0 and
                                'current.'+key not in aggregate_output_dict):
                            aggregate_output_dict['current.' +
                                                  key] = {"$in": filter_options[key]}
                            used_filter_options.append(key)
                    # logger.debug(pformat(used_filter_options))
        except:
            logger.exception("")

    # logger.debug(pformat(aggregate_output_dict))

    return (aggregate_output_dict, used_filter_options)


def filter_speakers(speakerdetails_collection,
                    activeprojectname,
                    filter_options,
                    logical_operator="and"):
    filter_on_category_path_dict, used_filter_options = filter_on_category_path(speakerdetails_collection,
                                                                                activeprojectname,
                                                                                filter_options)
    # selected_audio_sorting_subcategory = {
    #     "agegroup": "Age Group",
    #     "gender": "Gender",
    #     "educationlevel": "Education Level",
    #     "educationmediumupto12": "Education Medium Upto 12",
    #     "educationmediumafter12": "Education Medium After 12",
    #     "speakerspeaklanguage": "Speaker Speak Language"
    # }
    speakers_match = {
        "projectname": activeprojectname,
        "isActive": 1
    }
    speakers_match.update(filter_on_category_path_dict)
    # logger.debug(speakers_match)
    # for key, value in filter_options.items():
    #     # logger.debug("key: %s, value: %s", key, value)
    #     if (key in selected_audio_sorting_subcategory):
    #         # logger.debug("key: %s", key)
    #         key = selected_audio_sorting_subcategory_self_map[key]
    #         db_key = "current.sourceMetadata."+key
    #         value_list_len = len(value)
    #         if (value_list_len != 0):
    #             if (value_list_len == 1):
    #                 speakers_match[db_key] = value[0]
    #             else:
    #                 speakers_match[db_key] = {"$in": value}
    # logger.debug("speakers_match: %s", speakers_match)
    aggregate_output = []
    aggregate_output_list = []
    if (len(speakers_match) > 2):
        aggregate_output = speakerdetails_collection.aggregate([
            {
                "$match": speakers_match
            },
            {
                "$sort": {
                    "lifesourceid": 1
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "lifesourceid": 1
                }
            }
        ])
    # logger.debug("aggregate_output: %s", aggregate_output)
    for doc in aggregate_output:
        # logger.debug("aggregate_output: %s", pformat(doc))
        # logger.debug("doc['lifesourceid']: %s", pformat(doc["lifesourceid"]))
        aggregate_output_list.append(doc["lifesourceid"])
    # logger.debug('aggregate_output_list: %s', pformat(aggregate_output_list))

    return (list(set(aggregate_output_list)), used_filter_options)


def filter_speakers_derived(transcriptions_collection,
                            activeprojectname,
                            current_username,
                            filtered_speakers_list,
                            used_filter_options,
                            filter_options,
                            start_from=0,
                            number_of_audios=10,
                            logical_operator="and"):
    '''Get the audioIds and filename based on prompt filter options.'''
    aggregate_output_list = []
    total_records = 0
    try:
        # prompt_map = {
        #     'domain': 'Domain',
        #     'elicitationmethod': 'Elicitation Method',
        #     'target': 'Target',
        #     'Q_Id': 'Q_Id'
        # }
        # logger.debug(f"start_from: {start_from}\nnumber_of_audios: {number_of_audios}")
        speakers_match = {
            "projectname": activeprojectname,
            "audiodeleteFLAG": 0,
            # "speakerId": { "$not": { "$eq": '' } }
        }
        if (len(filtered_speakers_list) != 0):
            speakers_match['speakerId'] = {'$in': filtered_speakers_list}
        else:
            speakers_match['speakerId'] = {"$not": {"$eq": ''}}
        for key, value in filter_options.items():
            # if (key in prompt_map):
            # db_key = "prompt."+prompt_map[key]
            if (key not in used_filter_options):
                db_key = "prompt."+key
                value_list_len = len(value)
                if (value_list_len != 0):
                    speakers_match[db_key] = {"$in": value}
        # logger.debug("speakers_match: %s", speakers_match)
        aggregate_output = []
        # aggregate_output_list = []
        if (len(speakers_match) > 2):
            aggregate_output = transcriptions_collection.aggregate([
                {
                    "$match": speakers_match
                },
                {
                    "$sort": {
                        # "speakerId": 1
                        "audioId": 1
                    }
                },
                {"$skip": start_from},
                {"$limit": number_of_audios-start_from},
                {
                    "$project": {
                        "_id": 0,
                        "speakerId": 1,
                        "audioId": 1,
                        "audioFilename": 1,
                        # "prompt.Domain": 1,
                        current_username + '.audioCompleteFLAG': 1
                    }
                }
            ])
        for doc in aggregate_output:
            # logger.debug("aggregate_output: %s", pformat(doc))
            # if (doc['audioId'] in speaker_audio_ids):
            speaker = doc["speakerId"]
            if (isinstance(speaker, str)):
                speaker = [speaker]
            if (len(speaker) != 0):
                # logger.debug("aggregate_output: %s", pformat(doc))
                # if (len(filtered_speakers_list) != 0 and
                #     speaker not in filtered_speakers_list):
                #     continue
                # logger.debug("prompt.Domain: %s", doc["prompt"]["Domain"])
                doc['Audio File'] = ''
                for sid in speaker:
                    doc['Shared With'] = audio_shared_with(activeprojectname,
                                                           sid,
                                                           doc['audioId'])
                if current_username in doc:
                    doc['Transcribed'] = doc.pop(current_username, {}).get(
                        'audioCompleteFLAG', False)
                del doc["speakerId"]
                aggregate_output_list.append(doc)
        total_records_aggregate = transcriptions_collection.aggregate([
            {
                "$match": speakers_match
            },
            {
                "$count": "total_records"
            }
        ])
        for tr in total_records_aggregate:
            # logger.debug(tr)
            if ('total_records' in tr):
                total_records = tr['total_records']
        # logger.debug('total_records AUDIO: %s', total_records)
    except:
        logger.exception("")

    return (total_records,
            aggregate_output_list)
    # logger.debug("aggregate_output: %s", aggregate_output)
    # for doc in aggregate_output:
    #     logger.debug("aggregate_output: %s", pformat(doc))
    #     speaker = doc["speakerId"]
    #     if (speaker !=''):
    #         aggregate_output_list.append(speaker)
    # logger.debug('aggregate_output_list: %s', pformat(aggregate_output_list))

    # return (list(set(aggregate_output_list)))


def combine_speaker_ids(projects_collection,
                        activeprojectname,
                        current_username):
    '''Module to merge speaker ids in "speakerIds" and "fileSpeakerIds"'''
    speaker_ids = []
    file_speaker_ids = []
    try:
        speaker_ids = projects_collection.find_one({'projectname': activeprojectname},
                                                   {'_id': 0, 'speakerIds.'+current_username: 1})
        # logger.debug("speaker_ids: %s", pformat(speaker_ids))
        if (speaker_ids and
            'speakerIds' in speaker_ids and
                current_username in speaker_ids['speakerIds']):
            speaker_ids = speaker_ids['speakerIds'][current_username]
        else:
            speaker_ids = []
        file_speaker_ids = projects_collection.find_one({'projectname': activeprojectname},
                                                        {'_id': 0, 'fileSpeakerIds.'+current_username: 1})
        # logger.debug("file_speaker_ids: %s", pformat(file_speaker_ids))
        if (file_speaker_ids and
            'fileSpeakerIds' in file_speaker_ids and
                current_username in file_speaker_ids['fileSpeakerIds']):
            file_speaker_ids = list(
                file_speaker_ids['fileSpeakerIds'][current_username].keys())
        else:
            file_speaker_ids = []
        # logger.debug("file_speaker_ids: %s", file_speaker_ids)
        speaker_ids.extend(file_speaker_ids)
        speaker_ids = list(set(speaker_ids))
        # logger.debug("extended speaker ids: %s", pformat(speaker_ids))
    except:
        logger.exception("")

    return speaker_ids


def get_speaker_audio_ids_new(projects_collection,
                              activeprojectname,
                              current_username,
                              active_speaker_id,
                              audio_browse_action=0):
    '''Module to get speaker's audio_ids based on current user access(partial/full) to the speaker"'''
    speaker_audio_ids = []
    file_speaker_audio_ids = []
    try:
        if (audio_browse_action):
            speaker_ids = projects_collection.find_one({'projectname': activeprojectname},
                                                       {'_id': 0,
                                                        'speakerIds.'+current_username: 1,
                                                        "speakersAudioIdsDeleted."+active_speaker_id: 1})
            # logger.debug("speaker_ids: %s", pformat(speaker_ids))
            if (speaker_ids and
                'speakerIds' in speaker_ids and
                current_username in speaker_ids['speakerIds'] and
                active_speaker_id in speaker_ids['speakerIds'][current_username] and
                'speakersAudioIdsDeleted' in speaker_ids and
                    active_speaker_id in speaker_ids['speakersAudioIdsDeleted']):
                speaker_audio_ids = speaker_ids['speakersAudioIdsDeleted'][active_speaker_id]
        else:
            speaker_ids = projects_collection.find_one({'projectname': activeprojectname},
                                                       {'_id': 0,
                                                        'speakerIds.'+current_username: 1,
                                                        "speakersAudioIds."+active_speaker_id: 1})
            # logger.debug("speaker_ids: %s", pformat(speaker_ids))
            if (speaker_ids and
                'speakerIds' in speaker_ids and
                current_username in speaker_ids['speakerIds'] and
                active_speaker_id in speaker_ids['speakerIds'][current_username] and
                'speakersAudioIds' in speaker_ids and
                    active_speaker_id in speaker_ids['speakersAudioIds']):
                speaker_audio_ids = speaker_ids['speakersAudioIds'][active_speaker_id]
        # logger.debug("speaker_audio_ids: %s", pformat(speaker_audio_ids))
        if (len(speaker_audio_ids) != 0):
            # logger.debug("speaker_audio_ids: %s", pformat(speaker_audio_ids))
            return list(set(speaker_audio_ids))

        file_speaker_ids = projects_collection.find_one({'projectname': activeprojectname},
                                                        {'_id': 0,
                                                        'fileSpeakerIds.'+current_username: 1})
        # logger.debug("file_speaker_ids: %s", pformat(file_speaker_ids))
        if (file_speaker_ids and
            'fileSpeakerIds' in file_speaker_ids and
            current_username in file_speaker_ids['fileSpeakerIds'] and
                active_speaker_id in file_speaker_ids['fileSpeakerIds'][current_username]):
            file_speaker_audio_ids = file_speaker_ids['fileSpeakerIds'][current_username][active_speaker_id]
        if (len(file_speaker_audio_ids) != 0):
            return list(set(file_speaker_audio_ids))
    except:
        logger.exception("")

    return []


def get_speaker_metadata(speakerdetails_collection,
                         speakerids,
                         activeprojectname):
    speakers_metadata = {}
    try:
        # logger.debug('speakerids: %s', pformat(speakerids))
        speaker_metadata_cursor = speakerdetails_collection.find({"projectname": activeprojectname,
                                                                  "isActive": 1,
                                                                  "audioSubSource": 'youtube'},
                                                                 {"_id": 0,
                                                                  "lifesourceid": 1,
                                                                  "current.sourceMetadata": 1})
        # logger.debug(speaker_metadata_cursor)
        for speaker_metadata in speaker_metadata_cursor:
            # logger.debug(speaker_metadata)
            lifesourceid = speaker_metadata['lifesourceid']
            if (lifesourceid in speakerids):
                speakers_metadata[lifesourceid] = speaker_metadata['current']['sourceMetadata']
                # logger.debug('source_metadata: %s', pformat(source_metadata))
    except:
        logger.exception("")

    return speakers_metadata
