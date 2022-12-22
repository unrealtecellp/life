"""Module to download questionnaire in different format."""

from pprint import pprint
from app.controller.createprojectdirectory import createprojectdirectory
from app.controller.createzip import createzip
from app.controller.getfilefromfs import getfilefromfs
import os
import json
import shutil
import ffmpeg

def karyajson(mongo,
                base_dir,
                questionnaires,
                activeprojectname):
    # print('karyajson')
    project_folder_path = createprojectdirectory(base_dir, activeprojectname)
    trimmed_audio_folder_path = os.path.join(project_folder_path, 'trimmed_audio')
    if not os.path.exists(trimmed_audio_folder_path):
        os.mkdir(trimmed_audio_folder_path)
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
            # print(lang_script, lang_info)
            for prompt_type, prompt_data in lang_info.items():
                # print(prompt_type, prompt_data)
                domain = prompt['Domain'][0]
                elicitation_method = prompt['Elicitation Method']
                temp_dict = {
                    "quesId": ques_data["quesId"],
                    "Q_Id": ques_data["Q_Id"],
                    "Domain": domain,
                    "Elicitation Method": elicitation_method
                }
                audio_fileId = ''
                audio_file_path = ''
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
                    # get the file to local storage from database 'fs' collection
                    audio_file_path = getfilefromfs(mongo,
                                    project_folder_path,
                                    audio_fileId,
                                    'audio')
                    # print(audio_file_path)
                    # crop audio from start to end time
                    start_time = prompt_data['textGrid']['sentence'][boundaryId]['startindex']
                    end_time = prompt_data['textGrid']['sentence'][boundaryId]['endindex']
                    # print(f"start time: {start_time}, end time: {end_time}")
                    # TODO: use ffmpeg to trim audio. Try using 'ffmpeg-python' library
                    # link: https://github.com/kkroening/ffmpeg-python
                    actual_audio_file = ffmpeg.input(audio_file_path)
                    # print(type(actual_audio_file))
                    actual_audio_file = actual_audio_file.filter('atrim', start=start_time, end=end_time)
                    # print(type(actual_audio_file))
                    trimmed_audio_file_path = trimmed_audio_folder_path + '/'+audio_file_path.split('/')[-1]
                    save_audio_file = ffmpeg.output(actual_audio_file, trimmed_audio_file_path)
                    save_audio_file = ffmpeg.overwrite_output(save_audio_file)
                    ffmpeg.run(save_audio_file)
                    os.remove(audio_file_path)
                elif (prompt_type == 'multimedia'):
                    pass
                elif (prompt_type == 'image'):
                    pass
                
                lang_wise_ques_key_path = os.path.join(project_folder_path, lang_wise_ques_key)
                if not os.path.exists(lang_wise_ques_key_path):
                    os.mkdir(lang_wise_ques_key_path)
                    lang_wise_ques_key_json_path = os.path.join(lang_wise_ques_key_path, 'json')
                    os.mkdir(lang_wise_ques_key_json_path)
                    lang_wise_ques_key_audio_path = os.path.join(lang_wise_ques_key_path, 'audio')
                    os.mkdir(lang_wise_ques_key_audio_path)

                if (lang_wise_ques_key in lang_wise_ques):
                    lang_wise_ques[lang_wise_ques_key].append(temp_dict)
                else:
                    lang_wise_ques[lang_wise_ques_key] = [temp_dict]
                
                domain_wise_ques_key = lang_wise_ques_key+'_'+domain
                domain_wise_ques_key_path = os.path.join(project_folder_path, domain_wise_ques_key)
                if not os.path.exists(domain_wise_ques_key_path):
                    os.mkdir(domain_wise_ques_key_path)
                    domain_wise_ques_key_json_path = os.path.join(domain_wise_ques_key_path, 'json')
                    os.mkdir(domain_wise_ques_key_json_path)
                    domain_wise_ques_key_audio_path = os.path.join(domain_wise_ques_key_path, 'audio')
                    os.mkdir(domain_wise_ques_key_audio_path)
                
                if (domain_wise_ques_key in lang_wise_ques):
                    lang_wise_ques[domain_wise_ques_key].append(temp_dict)
                else:
                    lang_wise_ques[domain_wise_ques_key] = [temp_dict]

                if (audio_fileId != '' and audio_file_path != ''):
                    # shutil.copy2(audio_file_path, lang_wise_ques_key_audio_path)
                    # shutil.copy2(audio_file_path, domain_wise_ques_key_audio_path)
                    # os.remove(audio_file_path)
                    shutil.copy2(trimmed_audio_file_path, lang_wise_ques_key_audio_path)
                    shutil.copy2(trimmed_audio_file_path, domain_wise_ques_key_audio_path)
                    os.remove(trimmed_audio_file_path)
    # pprint(lang_wise_ques)

    for key, value in lang_wise_ques.items():
        # print(key, value)
        filename = key+'.json'
        save_file_path = os.path.join(project_folder_path, key, 'json', filename)
        with open(save_file_path, 'w') as json_file:
            json.dump(value, json_file, ensure_ascii=False, indent=2)
    
    for folder_name in sorted(os.listdir(project_folder_path)):
        # print(folder_name)
        if ('trimmed_audio' in folder_name): continue
        json_folder_path = os.path.join(project_folder_path, folder_name, 'json')
        zip_file_path = createzip(json_folder_path, folder_name+'_json')
        audio_folder_path = os.path.join(project_folder_path, folder_name, 'audio')
        zip_file_path = createzip(audio_folder_path, folder_name+'_recordings')
    
    shutil.rmtree(trimmed_audio_folder_path)

    return project_folder_path
