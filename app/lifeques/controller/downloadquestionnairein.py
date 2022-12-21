"""Module to download questionnaire in different format."""

from pprint import pprint
from app.controller.createprojectdirectory import createprojectdirectory
# from app.controller.createzip import createzip
from app.controller.getfilefromfs import getfilefromfs
import os
import json

def karyajson(mongo,
                base_dir,
                questionnaires,
                activeprojectname):
    print('karyajson')
    project_folder_path = createprojectdirectory(base_dir, activeprojectname)
    # dictionary containing lang-script as key and list of dictionaries(karya json format) as value
    lang_wise_ques = {}
    # karya_json_data = []
    saved_ques_data = questionnaires.find({'projectname': activeprojectname, 'quessaveFLAG': 1},
                                            {
                                                "_id": 0,
                                                "quesId": 1,
                                                "Q_Id": 1,
                                                "prompt": 1
                                            }
                                        )

    for ques_data in saved_ques_data:
        prompt = ques_data['prompt']
        content = prompt['content']
        for lang_script, lang_info in content.items():
            script = lang_script.split('-')[1]
            print(lang_script, lang_info)
            for prompt_type, prompt_data in lang_info.items():
                print(prompt_type, prompt_data)
                domain = prompt['Domain'][0]
                elicitation_method = prompt['Elicitation Method']
                temp_dict = {
                    "quesId": ques_data["quesId"],
                    "Q_Id": ques_data["Q_Id"],
                    "Domain": domain,
                    "Elicitation Method": elicitation_method
                }
                if (prompt_type == 'text'):
                    lang_wise_ques_key = lang_script.replace('-', '_')+'_'+prompt_type
                    boundaryId = list(prompt_data.keys())[0]
                    sentence = prompt_data[boundaryId]['textspan'][script]
                    temp_dict['sentence'] = sentence
                    temp_dict['hint'] = ''
                elif (prompt_type == 'audio'):
                    lang_wise_ques_key = lang_script.replace('-', '_')+'_'+prompt_type
                    boundaryId = list(prompt_data['textGrid']['sentence'].keys())[0]
                    sentence = prompt_data['textGrid']['sentence'][boundaryId]['transcription'][script]
                    temp_dict['sentence'] = sentence
                    temp_dict['hint'] = prompt_data['filename']
                    audio_fileId = prompt_data['fileId']
                    getfilefromfs(mongo,
                                    project_folder_path,
                                    audio_fileId,
                                    'audio')
                elif (prompt_type == 'multimedia'):
                    pass
                elif (prompt_type == 'image'):
                    pass
                
                if not os.path.exists(lang_wise_ques_key):
                    os.mkdir(lang_wise_ques_key)

                if (lang_wise_ques_key in lang_wise_ques):
                    lang_wise_ques[lang_wise_ques_key].append(temp_dict)
                else:
                    lang_wise_ques[lang_wise_ques_key] = [temp_dict]
                
                domain_wise_ques_key = lang_wise_ques_key+'_'+domain
                if not os.path.exists(domain_wise_ques_key):
                    os.mkdir(domain_wise_ques_key)
                
                if (domain_wise_ques_key in lang_wise_ques):
                    lang_wise_ques[domain_wise_ques_key].append(temp_dict)
                else:
                    lang_wise_ques[domain_wise_ques_key] = [temp_dict]
    pprint(lang_wise_ques)

    for key, value in lang_wise_ques.items():
        print(key, value)
        filename = key+'.json'
        save_file_path = os.path.join(project_folder_path, filename)
        with open(save_file_path, 'w') as json_file:
            json.dump(value, json_file, ensure_ascii=False, indent=2)
    
    return project_folder_path
