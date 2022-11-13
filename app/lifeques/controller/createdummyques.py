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
        # print(key, value)
        if (key == 'Script' or
            key == 'username' or
            key == 'projectname'):
            continue
        elif (key == 'Domain' or
            key == 'Target'):
            dummy_ques['prompt'][key] = []
        elif key == 'Elicitation Method':
            dummy_ques['prompt'][key] = ''
        # elif (key == 'Transcription'):
        #     transcription_lang = {}
        #     for lang in save_ques_form["Transcription"][1]:
        #         transcription_lang[lang] = ''
        #     transcription = {
        #         "audioId": "",
        #         "audioFilename": "",
        #         "audioLanguage": [],
        #         "speakerId": "",
        #         "textGrid": {
        #             "sentence": {
        #                 "000000": {
        #                     "start": 0.00,
        #                     "end": 0.00,
        #                     "transcription": transcription_lang
        #                 }
        #             }
        #         }
        #     }
        #     dummy_ques['prompt']['Transcription'] = transcription
        elif (key == 'Prompt Type'):
            for ptype in list(value[1].keys()):
                ptype_values = value[1][ptype]
                transcription_lang = {}
                for lang in ptype_values[1]:
                    transcription_lang[lang] = ''
                dummy_ques['prompt'][ptype] = {
                                                "fileId": "",
                                                "filename": "",
                                                "Instruction": "",
                                                "fileLanguage": [],
                                                "textGrid": {
                                                    "sentence": {
                                                        "000000": {
                                                            "start": 0.00,
                                                            "end": 0.00,
                                                            "transcription": transcription_lang
                                                        }
                                                    }
                                                }
                                            }
        elif ('Custom Field' in key):
            dummy_ques['prompt'][key] = ''
        # else:
        #     dummy_ques['prompt'][key] = ''
    # print(dummy_ques)
    pprint(dummy_ques)

    questionnaires.insert(dummy_ques)
    