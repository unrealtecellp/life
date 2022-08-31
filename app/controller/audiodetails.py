"""Module to save the uploaded audio file from 'enternewsenteces' route."""

from email.mime import audio
import os
import shutil
from datetime import datetime
import re
from pprint import pprint
import gridfs

def saveaudiofiles(mongo,
                    projects,
                    transcriptions,
                    projectowner,
                    activeprojectname,
                    current_username,
                    new_audio_file,):
    """mapping of this function is with the 'uploadaudiofiles' route.

    Args:
        mongo: instance of PyMongo
        projects: instance of 'projects' collection.
        transcriptions: instance of 'transcriptions' collection.
        projectowner: owner of the project.
        activeprojectname: name of the project activated by current active user.
        current_username: name of the current active user.
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
        "prompt": "",
    }
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
    transcriptions.insert(new_audio_details)
    # save audio file details in projects collection
    audio_ids = projects.find_one({'projectname': activeprojectname},
                                    {'_id': 0, 'audioIds': 1})
    print(len(audio_ids))
    if len(audio_ids) == 0:
        audio_ids = [audio_id]
    else:
        audio_ids = audio_ids['audioIds']
        audio_ids.append(audio_id)
    projects.update_one({ 'projectname' : activeprojectname }, \
            { '$set' : { 'lastActiveId.'+current_username+'.audioId' :  audio_id,
                            'audioIds': audio_ids }})
    # save audio file details in fs collection
    mongo.save_file(updated_audio_filename,
                    new_audio_file['audiofile'],
                    audioId=audio_id,
                    username=projectowner,
                    projectname=activeprojectname,
                    updatedBy=current_username)

def getactiveaudioid(projects,
                    activeprojectname,
                    current_username):
    """get last active audio id for current user from projects collections

    Args:
        projects (_type_): _description_
        activeprojectname (_type_): _description_
        current_username (_type_): _description_

    Returns:
        _type_: _description_
    """

    last_active_audio_id = projects.find_one({'projectname': activeprojectname},
                                                {
                                                    '_id': 0,
                                                    'lastActiveId.'+current_username+'.audioId': 1
                                                }
                                            )['lastActiveId'][current_username]['audioId']
    print(last_active_audio_id)

    return last_active_audio_id

def getaudiofiletranscription(transcriptions, file_id):
    """get the transcription details of the audio file

    Args:
        transcriptions (_type_): _description_
        file_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    transcription_details = {}
    transcription_data = transcriptions.find_one({'audioId': file_id})
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
                    which_one):
    """_summary_

    Args:
        projects (_type_): _description_
        activeprojectname (_type_): _description_
        last_active_id (_type_): _description_
        which_one (_type_): _description_
    """
    audio_ids_list = projects.find_one({ 'projectname': activeprojectname },
                                        { '_id': 0, 'audioIds': 1 })['audioIds']
    audio_id_index = audio_ids_list.index(last_active_id)
    print('latestAudioId Index!!!!!!!', audio_id_index)
    if which_one == 'previous':
        audio_id_index = audio_id_index - 1
    elif which_one == 'next':
        if len(audio_ids_list) == (audio_id_index+1):
            audio_id_index = 0
        else:
            audio_id_index = audio_id_index + 1
    latest_audio_id = audio_ids_list[audio_id_index]

    return latest_audio_id

def updatelatestaudioid(projects,
                        activeprojectname,
                        latest_audio_id,
                        current_username):
    """_summary_

    Args:
        projects (_type_): _description_
        activeprojectname (_type_): _description_
        latest_audio_id (_type_): _description_
        current_username (_type_): _description_
    """
    projects.update_one({ 'projectname' : activeprojectname }, \
            { '$set' : { 'lastActiveId.'+current_username+'.audioId' :  latest_audio_id }})

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
    transcription_data['data'] = transcriptions.find_one({ 'audioId': audio_id },
                                                    { '_id': 0, 'textGrid': 1 })['textGrid']
    print(transcription_data)
    for key, value in transcription_data['data']['sentence'].items():
        transcription_region = {}
        transcription_region['data'] = {}
        sentence = {}
        print(key, value)
        transcription_region['boundaryID'] = key
        sentence['boundaryID'] = key
        for k, v in value.items():
            transcription_region[k] = v
            sentence[k] = v
        transcription_region['data']['sentence'] = sentence
        transcription_regions.append(transcription_region)
    print(transcription_regions)

    return transcription_regions
