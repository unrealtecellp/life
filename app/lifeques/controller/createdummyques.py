"""Module to save a dummy ques in the 'questionnaires' collection for the newly created questionnaire project form."""

from pprint import pprint

def createdummyques(questionnaires,
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

    dummy_ques = {
            "username": current_username,
            "projectname": projectname,
            "quesId": projectname+"_dummy_ques",
            "Q_Id": "",
            "lastUpdatedBy": "",
            "quesdeleteFLAG": "",
            "quessaveFLAG": "",
            "prompt": {
                "text": {
                    "content": {},
                    "000000": {
                        "startindex": "",
                        "endindex": ""
                    }
                }
            }
        }
    prompt_lang = {}
    for lang in save_ques_form['Language'][1]:
        prompt_lang[lang] = ''
        dummy_ques['prompt']['text']['content'][lang] = ''
        dummy_ques['prompt']['text']['000000'][lang] = '' 
    for key, value in save_ques_form.items():
        print(key, value)
        if (key == 'Script' or
            key == 'username' or
            key == 'projectname'):
            continue
        elif (key == 'Domain' or
            key == 'Target'):
            dummy_ques['prompt'][key] = []
        elif key == 'Elicitation Method':
            dummy_ques['prompt'][key] = ''
        elif (key == 'Transcription'):
            transcription = {
                "audioId": "",
                "audioFilename": "",
                "speakerId": "",
                "textGrid": {
                    "sentence": {
                        "000000": prompt_lang
                    }
                }
            }
            dummy_ques['prompt']['Transcription'] = transcription
        elif (key == 'Prompt Type'):
            for ptype in value[1]:
                dummy_ques['prompt'][ptype] = {
                                                "fileId": "",
                                                "filename": "",
                                                "Instruction": ""
                                            }
        elif ('Custom Field' in key):
            dummy_ques['prompt'][key] = ''
        # else:
        #     dummy_ques['prompt'][key] = ''
    # print(dummy_ques)
    # pprint(dummy_ques)

    questionnaires.insert(dummy_ques)
    