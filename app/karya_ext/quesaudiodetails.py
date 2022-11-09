import json
import os
import shutil
from datetime import datetime
import re
from pprint import pprint
import gridfs
from flask import flash
import pandas as pd
from app.controller import getcommentstats



def quessaveaudiofiles(mongo,
                    projects,
                    userprojects,
                    questionnaire,
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
        "questionnaireFLAG": 0,
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
    new_audio_details[current_username] = {}
    new_audio_details[current_username]["textGrid"] = text_grid
    # pprint(new_audio_details)

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
        # print('speaker_audio_ids', speaker_audio_ids)
        if speakerId in speaker_audio_ids:
            speaker_audio_idskeylist = speaker_audio_ids[speakerId]
            speaker_audio_idskeylist.append(audio_id)
            speaker_audio_ids[speakerId] = speaker_audio_idskeylist
        else:
            # print('speakerId', speakerId)
            speaker_audio_ids[speakerId] = [audio_id]
        # pprint(speaker_audio_ids)
    else:
        speaker_audio_ids = {
            speakerId: [audio_id]
        }
    # pprint(speaker_audio_ids)
    try:
        projects.update_one({ 'projectname' : activeprojectname },
                { '$set' : {
                    'lastActiveId.'+current_username+'.'+speakerId+'.audioId' :  audio_id,
                    'speakerIds': speakerIds,
                    'speakersAudioIds': speaker_audio_ids
                }})
        # update active speaker ID in userprojects collection
        projectinfo = userprojects.find_one({'username' : current_username},
                                        {'_id': 0, 'myproject': 1, 'projectsharedwithme': 1})

        # print(projectinfo)
        userprojectinfo = ''
        for key, value in projectinfo.items():
            if len(value) != 0:
                if activeprojectname in value:
                    userprojectinfo = key+'.'+activeprojectname+".activespeakerId"
        userprojects.update_one({"username": current_username},
                                { "$set": {
                                    userprojectinfo: speakerId
                                }})
        questionnaire.insert(new_audio_details)
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