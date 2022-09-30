"""Module to save the uploaded audio file from 'enternewsenteces' route."""


import json
# from pprint import pprint
import os
import shutil
from datetime import datetime
import re
from pprint import pprint
import gridfs
from flask import flash
import pandas as pd

def saveaudiofiles(mongo,
                    projects,
                    userprojects,
                    transcriptions,
                    projectowner,
                    activeprojectname,
                    current_username,
                    speakerId,
                    new_audio_file,
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

    text_grid = {
            "discourse": {},
            "sentence": {},
            "word": {},
            "phoneme": {}
        }
    # save audio file details in transcriptions collection
    new_audio_details = {
        "username": projectowner,
        "projectname": activeprojectname,
        "updatedBy": current_username,
        "audiodeleteFLAG": 0,
        "audioverifiedFLAG": 0,
        "transcriptionFLAG": 0,
        "prompt": "",
        "speakerId": speakerId
    }
    for kwargs_key, kwargs_value in kwargs.items():
        new_audio_details[kwargs_key] = kwargs_value

    if new_audio_file['audiofile'].filename != '':
        audio_filename = new_audio_file['audiofile'].filename
        audio_id = 'A'+re.sub(r'[-: \.]', '', str(datetime.now()))
        new_audio_details['audioId'] = audio_id
        updated_audio_filename = (audio_id+
                                    '_'+
                                    audio_filename)
        new_audio_details['audioFilename'] = updated_audio_filename
    new_audio_details["textGrid"] = text_grid
    pprint(new_audio_details)

    # save audio file details and speaker ID in projects collection
    speakerIds = projects.find_one({ 'projectname': activeprojectname },
                                        { '_id': 0, 'speakerIds': 1 })
    # print(f"SPEAKER IDS: {speakerIds}")
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
        # print(speakerIds)

    speaker_audio_ids = projects.find_one({'projectname': activeprojectname},
                                    {'_id': 0, 'speakersAudioIds': 1})
    # print(len(speaker_audio_ids))
    # print(speaker_audio_ids)
    if len(speaker_audio_ids) != 0:
        speaker_audio_ids = speaker_audio_ids['speakersAudioIds']
        print('speaker_audio_ids', speaker_audio_ids)
        if speakerId in speaker_audio_ids:
            speaker_audio_idskeylist = speaker_audio_ids[speakerId]
            speaker_audio_idskeylist.append(audio_id)
            speaker_audio_ids[speakerId] = speaker_audio_idskeylist
        else:
            print('speakerId', speakerId)
            speaker_audio_ids[speakerId] = [audio_id]
        pprint(speaker_audio_ids)
    else:
        speaker_audio_ids = {
            speakerId: [audio_id]
        }
    pprint(speaker_audio_ids)
    try:
        projects.update_one({ 'projectname' : activeprojectname },
                { '$set' : {
                    'lastActiveId.'+current_username+'.'+speakerId+'.audioId' :  audio_id,
                    'speakerIds': speakerIds,
                    'speakersAudioIds': speaker_audio_ids
                }})
        # update active speaker ID in userprojects collection
        userprojects.update_one({"username": current_username},
                                { "$set": {
                                    "activespeakerId": speakerId
                                }})
        transcriptions.insert(new_audio_details)
        # save audio file details in fs collection
        mongo.save_file(updated_audio_filename,
                        new_audio_file['audiofile'],
                        audioId=audio_id,
                        username=projectowner,
                        projectname=activeprojectname,
                        updatedBy=current_username)
    except Exception as e:
        print(e)
        flash(f"ERROR")                    

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
        # print(last_active_audio_id)
        if len(last_active_audio_id) != 0:
            last_active_audio_id = last_active_audio_id['lastActiveId'][current_username][activespeakerId]['audioId']
    except:
        last_active_audio_id = ''

    return last_active_audio_id

def getaudiofiletranscription(transcriptions, audio_id):
    """get the transcription details of the audio file

    Args:
        transcriptions (_type_): _description_
        file_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    transcription_details = {}
    transcription_data = transcriptions.find_one({'audioId': audio_id})
    if transcription_data is not None:
        transcription_details['data'] = transcription_data['textGrid']

    return transcription_details

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
    print(file_type, file_id)
    fs =  gridfs.GridFS(mongo.db)                       # creating GridFS instance to get required files                
    file = fs.find_one({ file_type: file_id })
    audioFolder = os.path.join(basedir, 'static/audio')
    shutil.rmtree(audioFolder)
    os.mkdir(audioFolder)
    if (file is not None and
        'audio' in file.contentType):
        file_name = file.filename
        audiofile = fs.get_last_version(filename=file_name)
        audiofileBytes = audiofile.read()
        if len(audiofileBytes) != 0:
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
    audio_ids_list = projects.find_one({ 'projectname': activeprojectname },
                                        { '_id': 0, 'speakersAudioIds': 1 })
    # print('audio_ids_list', audio_ids_list)
    if len(audio_ids_list) != 0:
        audio_ids_list = audio_ids_list['speakersAudioIds'][activespeakerId]                                   
        # print('audio_ids_list', audio_ids_list)
    audio_id_index = audio_ids_list.index(last_active_id)
    # print('latestAudioId Index!!!!!!!', audio_id_index)
    if which_one == 'previous':
        audio_id_index = audio_id_index - 1
    elif which_one == 'next':
        if len(audio_ids_list) == (audio_id_index+1):
            audio_id_index = 0
        else:
            audio_id_index = audio_id_index + 1
    latest_audio_id = audio_ids_list[audio_id_index]
    # print('latest_audio_id AUDIODETAILS', latest_audio_id)

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
    projects.update_one({ 'projectname' : activeprojectname }, \
            { '$set' : { 'lastActiveId.'+current_username+'.'+activespeakerId+'.audioId' :  latest_audio_id }})

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
    try:
        t_data = transcriptions.find_one({ 'audioId': audio_id },
                                        { '_id': 0, 'textGrid.sentence': 1 })
        # print('t_data!!!!!', t_data)
        if t_data is not None:
            transcription_data = t_data['textGrid']
        # pprint(transcription_data)
        sentence = transcription_data['sentence']
        for key, value in sentence.items():
            # print(key, value)
            transcription_region = {}
            # gloss = {}
            # transcription_region['sentence'] = {}
            transcription_region['data'] = {}
            transcription_region['boundaryID'] = key
            transcription_region['start'] = sentence[key]['start']
            transcription_region['end'] = sentence[key]['end']
            # transcription_region['sentence'] = {key: value}
            transcription_region['data'] = {'sentence': {key: value}}
            # pprint(transcription_region)
            try:
                # print('!@!#!@!#!@!#!@!#!@!##!@!#!#!@!#!@!#!@!#!@!#!@!##!@!#!#', gloss)
                tempgloss = sentence[key]['gloss']
                # print('!@!#!@!#!@!#!@!#!@!##!@!#!#!@!#!@!#!@!#!@!#!@!##!@!#!#', tempgloss)
                gloss[key] = pd.json_normalize(tempgloss, sep='.').to_dict(orient='records')[0]
                # print('!@!#!@!#!@!#!@!#!@!##!@!#!#!@!#!@!#!@!#!@!#!@!##!@!#!#', gloss)
                temppos = sentence[key]['pos']
                pos[key] = pd.json_normalize(temppos, sep='.').to_dict(orient='records')[0]

                # print('288', gloss)
            except:
                # print('=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=1=', gloss)
                gloss = {}
                pos = {}

        # pprint(transcription_region)
    #     if (key == 'speakerId' or
    #         key == 'sentenceId'):
    #         continue
    #     sentence['boundaryID'] = key
    #     for k, v in value.items():
    #         transcription_region[k] = v
    #         sentence[k] = v
    #     transcription_region['data']['sentence'] = sentence
            transcription_regions.append(transcription_region)
        # pprint(transcription_regions)
    # print('303', gloss, pos)
    except:
        pass

    return (transcription_regions, gloss, pos)

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

    # pprint(activeprojectform)
    # pprint(scriptCode)
    # transcription_details = {
    #     'updatedBy' : current_username,
    #     "textdeleteFLAG": 0
    # }
    # text_grid = {}
    sentence = {}
    if transcription_regions is not None:
        transcription_regions = json.loads(transcription_regions)
        pprint(transcription_regions)
        for transcription_boundary in transcription_regions:
            transcription_boundary = transcription_boundary['data']
            if 'sentence' in transcription_boundary:
                for key, value in transcription_boundary['sentence'].items():
                    print(f"KEY: {key}\nVALUE: {value}")
                    value["speakerId"] = activespeakerId
                    value["sentenceId"] = audio_id
                    sentence[key] = value
            # pprint(sentence)
            #     print('transcription_boundary.keys()', transcription_boundary.keys())
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
            #     for key in list(transcription_data['data'].keys()):
            #         if key == 'sentence':
            #             print(key)

            # text_grid['sentence'] = sentence
            # print(text_grid)
            # transcription_details['textGrid'] = text_grid
            # transcriptions.insert(transcription_details)
            print("'sentence' in transcription_boundary")
            print('371', sentence)
            pprint(sentence)
    transcriptions.update_one({ 'audioId': audio_id },
                                {'$set': { 'textGrid.sentence': sentence,
                                            'updatedBy': current_username,
                                            'transcriptionFLAG': 1 }})
