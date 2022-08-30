"""Module to save the uploaded audio file from 'enternewsenteces' route."""
from datetime import datetime
import re
from pprint import pprint

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
