import re
from datetime import datetime
from app.controller import (
    life_logging
)
logger = life_logging.get_logger()

def saveprompttext(mongo,
                    projects,
                    userprojects,
                    projectsform,
                    transcriptions,
                    projectowner,
                    activeprojectname,
                    current_username,
                    last_active_transcription_id,
                    prompt_text,
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
        prompt_text: uploaded audio file details.
    """
    try:
        # print("last_active_ques_id in savequesaudiofiles()", last_active_ques_id)
        transcription_form = projectsform.find_one({"projectname": activeprojectname},
                                                {"_id": 0})
        # pprint(ques_form)
        prompt_text_details = {}
        for kwargs_key, kwargs_value in kwargs.items():
            prompt_text_details[kwargs_key] = kwargs_value

        prompt_type_info = list(prompt_text.keys())[0]
        prompt_type = prompt_type_info.split('_')[1]
        prompt_lang = prompt_type_info.split('_')[-1]
        logger.debug('prompt_type_info: %s, prompt_type: %s, prompt_lang: %s',
                     prompt_type_info, prompt_type, prompt_lang)
        text_boundary_data = {}
        lang_name = prompt_lang
        # print(key.split(' Language '), lang_name)
        lang_script = lang_name.split('-')[1]
        value = prompt_text[prompt_type_info]
        # print(key, lang_name, lang_script, value)
        startindex = '0'
        endindex = str(len(value))
        for p in range(3):
            if (len(startindex) < 3):
                startindex = '0'+startindex
            if (len(endindex) < 3):
                endindex = '0'+endindex
        text_boundary_id = startindex+endindex
        text_boundary_data[text_boundary_id] = {
                                                    "startindex": startindex,
                                                    "endindex": endindex,
                                                    "textspan": {
                                                        lang_script: value
                                                    }
        }
        text_boundary_data['otherInfo' ] = prompt_text_details
        # print(text_boundary_data)
        # content[lang_name] = value
        # prompt['content'][lang_name]['text'] = text_boundary_data
        transcription_doc_id = transcriptions.update_one({'audioId': last_active_transcription_id},
                                                            {"$set": { 
                                                                "prompt.content."+prompt_lang+"."+prompt_type.lower(): text_boundary_data,
                                                                # "prompt.content."+prompt_lang+"."+prompt_type.lower()+".otherInfo": prompt_text_details
                                                                }})
        return (True, transcription_doc_id)

    except Exception as e:
        logger.exception("")
        return(False,"")


def savepromptfile(mongo,
                    projects,
                    userprojects,
                    projectsform,
                    transcriptions,
                    projectowner,
                    activeprojectname,
                    current_username,
                    last_active_transcription_id,
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
    try:
        # print("last_active_ques_id in savequesaudiofiles()", last_active_ques_id)
        transcription_form = projectsform.find_one({"projectname": activeprojectname},
                                                {"_id": 0})
        # pprint(ques_form)
        new_file_details = {}
        for kwargs_key, kwargs_value in kwargs.items():
            new_file_details[kwargs_key] = kwargs_value

        prompt_type_info = list(new_file.keys())[0]
        prompt_type = prompt_type_info.split('_')[1]
        prompt_lang = prompt_type_info.split('_')[-1]
        logger.debug('prompt_type_info: %s, prompt_type: %s, prompt_lang: %s',
                     prompt_type_info, prompt_type, prompt_lang)
        if new_file[prompt_type_info].filename != '':
            filename = new_file[prompt_type_info].filename
            file_id = prompt_type[0]+re.sub(r'[-: \.]', '', str(datetime.now()))
            updated_filename = (file_id+
                                    '_'+
                                    filename)
            logger.debug('filename: %s, file_id: %s',
                         filename, file_id)
            prompt = transcriptions.find_one({"projectname": activeprojectname,
                                                  "audioId": last_active_transcription_id},
                                                   {"_id": 0, "prompt": 1}
                                                   )["prompt"]
            transcription_doc_id = transcriptions.update_one({'audioId': last_active_transcription_id},
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

            return (True, transcription_doc_id, fs_file_id)

    except Exception as e:
        logger.exception("")
        return(False,"","")
