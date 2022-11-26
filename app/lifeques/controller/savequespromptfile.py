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
                    new_file,
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
        new_file: uploaded audio file details.
    """

    print("last_active_ques_id in savequesaudiofiles()", last_active_ques_id)
    ques_form = projectsform.find_one({"projectname": activeprojectname}, {"_id": 0})
    pprint(ques_form)
    new_file_details = {}
    for kwargs_key, kwargs_value in kwargs.items():
        new_file_details[kwargs_key] = kwargs_value

    prompt_type_info = list(new_file.keys())[0]
    prompt_type = prompt_type_info.split('_')[1]
    prompt_lang = prompt_type_info.split('_')[-1]
    print(prompt_type_info, prompt_type, prompt_lang)
    if new_file[prompt_type_info].filename != '':
        filename = new_file[prompt_type_info].filename
        file_id = prompt_type[0]+re.sub(r'[-: \.]', '', str(datetime.now()))
        updated_filename = (file_id+
                                '_'+
                                filename)

    try:
        
        # questionnaire_doc_id = questionnaires.update_one({'quesId': last_active_ques_id},
        #                                                     {"$set": { 
        #                                                         "prompt.Transcription.audioFilename": updated_filename,
        #                                                         "prompt.Transcription.audioId": file_id,
        #                                                         "prompt.Transcription.audioLanguage": ques_form["Transcription"][1],
        #                                                         "prompt.otherInfo": new_file_details
        #                                                         }})
        questionnaire_doc_id = questionnaires.update_one({'quesId': last_active_ques_id},
                                                            {"$set": { 
                                                                "prompt.content."+prompt_lang+"."+prompt_type.lower()+".filename": updated_filename,
                                                                "prompt.content."+prompt_lang+"."+prompt_type.lower()+".fileId": file_id,
                                                                "prompt.content."+prompt_lang+"."+prompt_type.lower()+".otherInfo": new_file_details
                                                                }})
        # save audio file details in fs collection
        fs_file_id = mongo.save_file(updated_filename,
                        new_file[prompt_type_info],
                        fileId=file_id,
                        username=projectowner,
                        projectname=activeprojectname,
                        updatedBy=current_username)

        return (True, questionnaire_doc_id, fs_file_id)

    except Exception as e:
        print(e)
        flash(f"ERROR")
        return(False)
