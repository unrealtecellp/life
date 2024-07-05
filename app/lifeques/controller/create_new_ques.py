"""Module to save a new ques in the 'questionnaires' collection"""

from pprint import pprint
from app.lifeques.controller import (
    uploadquesdataexcel
)
from app.controller import (
    life_logging
)

logger = life_logging.get_logger()


def create_new_ques(questionnaires,
                    projectname,
                    save_ques_form,
                    current_username):
    """_summary_

    Args:
        questionnaire (_type_): _description_
        projectname (_type_): _description_
        save_ques_form (_type_): _description_
        current_username (_type_): _description_
    """
    quesId = uploadquesdataexcel.quesmetadata()
    quesId, questionnaire_id, save_state = (quesId, '', False)
    try:
        # pprint(save_ques_form);
        new_ques = {
            "username": current_username,
            "projectname": projectname,
            "quesId": quesId,
            "Q_Id": quesId,
            "lastUpdatedBy": current_username,
            "quesdeleteFLAG": 0,
            "quessaveFLAG": 0,
            "prompt": {}
        }

        for key, value in save_ques_form.items():
            # print(key, value)
            if (key == 'Script' or
                key == 'username' or
                    key == 'projectname'):
                continue
            elif (key == 'Domain' or
                  key == 'Target'):
                new_ques['prompt'][key] = []
            elif key == 'Elicitation Method':
                new_ques['prompt'][key] = ''
            elif (key == 'Prompt Type'):
                content = {}
                for prompt_key, prompt_value in value[1].items():
                    # print(prompt_key, prompt_value)
                    prompt_lang = prompt_key
                    prompt_lang_script = save_ques_form['LangScript'][1][prompt_lang]
                    content[prompt_lang] = {}
                    # print(prompt_lang, prompt_lang_script, content)
                    for prompt_type_key, prompt_type_value in prompt_value.items():
                        # print(prompt_type_key, prompt_type_value, prompt_type_value[0], prompt_type_value[1])
                        if (prompt_type_key == 'Text'):
                            content[prompt_lang]['text'] = {
                                "000000": {
                                    "startindex": "",
                                    "endindex": "",
                                    "textspan": {
                                        prompt_lang_script: ""
                                    }
                                }
                            }
                        elif (prompt_type_key == 'Audio'):
                            content[prompt_lang]['audio'] = {
                                "fileId": "",
                                "filename": ""
                            }
                            if (prompt_type_value[1] != '' and prompt_type_value[1] != 'text'):
                                content[prompt_lang]['audio']['instructions'] = ''
                            if (prompt_type_value[0] == 'waveform'):
                                content[prompt_lang]['audio']['textGrid'] = {
                                    "sentence": {
                                        "000000": {
                                            "startindex": "",
                                            "endindex": "",
                                            "transcription": {
                                                prompt_lang_script: ""
                                            }
                                        }
                                    }
                                }
                        elif (prompt_type_key == 'Multimedia'):
                            content[prompt_lang]['multimedia'] = {
                                "fileId": "",
                                "filename": ""
                            }
                            if (prompt_type_value[1] != '' and prompt_type_value[1] != 'text'):
                                content[prompt_lang]['multimedia']['instructions'] = ''
                            if (prompt_type_value[0] == 'waveform'):
                                content[prompt_lang]['multimedia']['textGrid'] = {
                                    "sentence": {
                                        "000000": {
                                            "startindex": "",
                                            "endindex": "",
                                            "transcription": {
                                                prompt_lang_script: ""
                                            }
                                        }
                                    }
                                }
                        elif (prompt_type_key == 'Image'):
                            content[prompt_lang]['image'] = {
                                "fileId": "",
                                "filename": ""
                            }
                            if (prompt_type_value[1] != '' and prompt_type_value[1] != 'text'):
                                content[prompt_lang]['image']['instructions'] = ''
                    # pprint(content)
                new_ques['prompt']['content'] = content
            elif ('Custom Field' in key):
                new_ques['prompt'][key] = ''
            # else:
            #     new_ques['prompt'][key] = ''
        # print(new_ques)
        # pprint(new_ques)

        questionnaire_id = questionnaires.insert_one(new_ques)
        save_state = True
        logger.debug("questionnaire_id from create_new_ques(): %s",
                     questionnaire_id)
        logger.debug("quesId: %s", quesId)
    except:
        logger.exception("")
        quesId = None

    return (quesId, questionnaire_id, save_state)
