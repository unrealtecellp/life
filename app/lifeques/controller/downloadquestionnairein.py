"""Module to download questionnaire in different format."""

from pprint import pprint

def karyajson(questionnaires,
                activeprojectname):
    print('karyajson')
    karya_json_data = []
    saved_ques_data = questionnaires.find({'projectname': activeprojectname, 'quessaveFLAG': 1},
                                            {
                                                "_id": 0,
                                                "quesId": 1,
                                                "Q_Id": 1,
                                                "prompt": 1
                                            }
                                        )

    for ques_data in saved_ques_data:
        temp_dict = {
            "quesId": ques_data["quesId"],
            "Q_Id": ques_data["Q_Id"]
        }
        prompt = ques_data['prompt']
        for key, value in prompt.items():
            print(key, value)
            if (key == 'Domain'):
                temp_dict[key] = value[0]
            elif (key == 'Elicitation Method'):
                temp_dict[key] = value
            elif (key == 'content'):
                for lang_script, lang_info in value.items():
                    print(lang_script, lang_info)
                    for prompt_type, prompt_data in lang_info.items():
                        print(prompt_type, prompt_data)
