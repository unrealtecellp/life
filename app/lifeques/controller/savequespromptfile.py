import re
from datetime import datetime
from pprint import pprint

from flask import flash


def savequespromptfile(mongo,
                    projects,
                    userprojects,
                    projectsform,
                    questionnaires,
                    projectowner,
                    activeprojectname,
                    current_username,
                    last_active_ques_id,
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

    print("last_active_ques_id in savequesaudiofiles()", last_active_ques_id)
    ques_form = projectsform.find_one({"projectname": activeprojectname}, {"_id": 0})
    pprint(ques_form)
    new_audio_details = {}
    for kwargs_key, kwargs_value in kwargs.items():
        new_audio_details[kwargs_key] = kwargs_value

    if new_audio_file['Transcription Audio'].filename != '':
        audio_filename = new_audio_file['Transcription Audio'].filename
        audio_id = 'A'+re.sub(r'[-: \.]', '', str(datetime.now()))
        updated_audio_filename = (audio_id+
                                    '_'+
                                    audio_filename)
    
    transcription_language = []
    if ('Transcription Language' in ques_form):
        transcription_language = ques_form["Transcription Language"][1]

    try:
        
        # questionnaire_doc_id = questionnaires.update_one({'quesId': last_active_ques_id},
        #                                                     {"$set": { 
        #                                                         "prompt.Transcription.audioFilename": updated_audio_filename,
        #                                                         "prompt.Transcription.audioId": audio_id,
        #                                                         "prompt.Transcription.audioLanguage": ques_form["Transcription"][1],
        #                                                         "prompt.otherInfo": new_audio_details
        #                                                         }})
        questionnaire_doc_id = questionnaires.update_one({'quesId': last_active_ques_id},
                                                            {"$set": { 
                                                                "prompt.Audio.filename": updated_audio_filename,
                                                                "prompt.Audio.fileId": audio_id,
                                                                "prompt.Audio.fileLanguage": transcription_language,
                                                                "prompt.otherInfo": new_audio_details
                                                                }})
        # save audio file details in fs collection
        fs_file_id = mongo.save_file(updated_audio_filename,
                        new_audio_file['Transcription Audio'],
                        audioId=audio_id,
                        username=projectowner,
                        projectname=activeprojectname,
                        updatedBy=current_username)

        return (questionnaire_doc_id, fs_file_id)

    except Exception as e:
        print(e)
        flash(f"ERROR")
