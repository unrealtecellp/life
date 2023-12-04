"""Module to download questionnaire in different format."""

from pprint import pprint, pformat
from app.controller import (
    life_logging
)
from app.controller.createprojectdirectory import createprojectdirectory
from app.controller.createzip import createzip
from app.controller.getfilefromfs import getfilefromfs
import os
import json
import shutil
import ffmpeg
import librosa

logger = life_logging.get_logger()

def datafolder_stats(folder_path, file_type):
    try:
        if (file_type == 'audio'):
            audio_file_folder_stats = len(os.listdir(folder_path))
            if (audio_file_folder_stats == 0):
                return 'NO AUDIO'
            else:
                return audio_file_folder_stats
        elif (file_type == 'image'):
            image_file_folder_stats = len(os.listdir(folder_path))
            if (image_file_folder_stats == 0):
                return 'NO IMAGE'
            else:
                return image_file_folder_stats
        elif (file_type == 'multimedia'):
            multimedia_file_folder_stats = len(os.listdir(folder_path))
            if (multimedia_file_folder_stats == 0):
                return 'NO MULTIMEDIA'
            else:
                return multimedia_file_folder_stats
        elif (file_type == 'json'):
            for json_file in sorted(os.listdir(folder_path)):
                json_file_path = os.path.join(folder_path, json_file)
                with open(json_file_path, 'r') as read_json_file:
                    json_file_data = json.load(read_json_file)
                json_file_doc_folder_stats = len(json_file_data)
                return json_file_doc_folder_stats
        else:
            return 0
    except:
        logger.exception("")
        return 0

def karyajson(mongo,
                base_dir,
                questionnaires,
                activeprojectname):
    # print('karyajson')
    project_folder_path = createprojectdirectory(base_dir, activeprojectname)
    # logger.debug('project_folder_path: %s', project_folder_path)
    try:
        trimmed_audio_folder_path = os.path.join(project_folder_path, 'trimmed_audio')
        if not os.path.exists(trimmed_audio_folder_path):
            os.mkdir(trimmed_audio_folder_path)
        ques_image_folder_path = os.path.join(project_folder_path, 'ques_image')
        if not os.path.exists(ques_image_folder_path):
            os.mkdir(ques_image_folder_path)
        ques_multimedia_folder_path = os.path.join(project_folder_path, 'ques_multimedia')
        if not os.path.exists(ques_multimedia_folder_path):
            os.mkdir(ques_multimedia_folder_path)
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
            # logger.debug("Q_Id: %s", ques_data["Q_Id"])
            prompt = ques_data['prompt']
            content = prompt['content']
            # logger.debug('prompt: %s, content: %s', prompt, content)
            for lang_script, lang_info in content.items():
                script = lang_script.split('-')[1]
                # print(lang_script, lang_info)
                for prompt_type, prompt_data in lang_info.items():
                    # logger.debug('prompt_type: %s', prompt_type)
                    # logger.debug('prompt_data: %s', prompt_data)
                    lang_wise_ques_key = ''
                    domain = prompt['Domain'][0]
                    # print('domain:', domain)
                    elicitation_method = prompt['Elicitation Method']
                    temp_dict = {
                        "quesId": ques_data["quesId"],
                        "Q_Id": ques_data["Q_Id"],
                        "Domain": domain,
                        "Elicitation Method": elicitation_method
                    }
                    if (prompt_type+'Instruction' in prompt_data):
                        temp_dict['instruction'] = prompt_data[prompt_type+'Instruction']
                    audio_fileId = ''
                    audio_file_path = ''
                    image_fileId = ''
                    image_file_path = ''
                    multimedia_fileId = ''
                    multimedia_file_path = ''
                    if (prompt_type == 'text'):
                        lang_wise_ques_key = lang_script.replace('-', '_')+'_'+prompt_type
                        boundaryId = list(prompt_data.keys())[0]
                        sentence = prompt_data[boundaryId]['textspan'][script]
                        temp_dict['sentence'] = sentence
                        temp_dict['hint'] = ''
                    elif (prompt_type == 'audio'):
                        # logger.debug("lang_wise_ques_key: %s", lang_wise_ques_key)
                        lang_wise_ques_key = lang_script.replace('-', '_')+'_'+prompt_type
                        # logger.debug("lang_wise_ques_key: %s", lang_wise_ques_key)
                        boundaryId = list(prompt_data['textGrid']['sentence'].keys())[0]
                        sentence = prompt_data['textGrid']['sentence'][boundaryId]['transcription'][script]
                        temp_dict['sentence'] = sentence
                        temp_dict['hint'] = prompt_data['filename']
                        audio_fileId = prompt_data['fileId']
                        # get the file to local storage from database 'fs' collection
                        # print(mongo,
                        #         project_folder_path,
                        #         audio_fileId,
                        #         'fileId')
                        audio_file_path = getfilefromfs(mongo,
                                                        project_folder_path,
                                                        audio_fileId,
                                                        'audio',
                                                        'fileId')
                        logger.debug('audio_file_path: %s', audio_file_path)
                        if (audio_file_path != ''):
                            # crop audio from start to end time
                            start_time = prompt_data['textGrid']['sentence'][boundaryId]['startindex']
                            end_time = prompt_data['textGrid']['sentence'][boundaryId]['endindex']
                            # logger.debug("Audio duration: %s", librosa.get_duration(filename=audio_file_path))
                            if (start_time == ''):
                                start_time = 0
                            if (end_time == ''):
                                end_time = librosa.get_duration(filename=audio_file_path)
                            # logger.debug("start time: %s, end time: %s", start_time, end_time)
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
                        else:
                            continue
                    elif (prompt_type == 'multimedia'):
                        # logger.debug("lang_wise_ques_key: %s", lang_wise_ques_key)
                        lang_wise_ques_key = lang_script.replace('-', '_')+'_'+prompt_type
                        # logger.debug("lang_wise_ques_key: %s", lang_wise_ques_key)
                        # boundaryId = list(prompt_data['textGrid']['sentence'].keys())[0]
                        # sentence = prompt_data['textGrid']['sentence'][boundaryId]['transcription'][script]
                        # temp_dict['sentence'] = sentence
                        multimedia_fileId = prompt_data['fileId']
                        if (multimedia_fileId != ''):
                            temp_dict['hint'] = prompt_data['filename']
                            multimedia_file_path = getfilefromfs(mongo,
                                                            project_folder_path,
                                                            multimedia_fileId,
                                                            'video',
                                                            'fileId')
                        else:
                            continue
                    elif (prompt_type == 'image'):
                        # logger.debug("lang_wise_ques_key: %s", lang_wise_ques_key)
                        lang_wise_ques_key = lang_script.replace('-', '_')+'_'+prompt_type
                        # logger.debug("lang_wise_ques_key: %s", lang_wise_ques_key)
                        # boundaryId = list(prompt_data['textGrid']['sentence'].keys())[0]
                        # sentence = prompt_data['textGrid']['sentence'][boundaryId]['transcription'][script]
                        # temp_dict['sentence'] = sentence
                        image_fileId = prompt_data['fileId']
                        if (image_fileId != ''):
                            temp_dict['hint'] = prompt_data['filename']
                            image_file_path = getfilefromfs(mongo,
                                                            project_folder_path,
                                                            image_fileId,
                                                            'image',
                                                            'fileId')
                        else:
                            continue
                    lang_wise_ques_key_path = os.path.join(project_folder_path, lang_wise_ques_key)
                    # logger.debug("prompt_type: %s, lang_wise_ques_key_path: %s",
                    #                         prompt_type, lang_wise_ques_key_path)
                    lang_wise_ques_key_json_path = os.path.join(lang_wise_ques_key_path, 'json')
                    # lang_wise_ques_key_audio_path = os.path.join(lang_wise_ques_key_path, 'audio')
                    # lang_wise_ques_key_image_path = os.path.join(lang_wise_ques_key_path, 'image')
                    # lang_wise_ques_key_multimedia_path = os.path.join(lang_wise_ques_key_path, 'multimedia')
                    # logger.debug("lang_wise_ques_key_path: %s", lang_wise_ques_key_path)
                    # logger.debug("lang_wise_ques_key_audio_path: %s", lang_wise_ques_key_audio_path)
                    if not os.path.exists(lang_wise_ques_key_path):
                        os.mkdir(lang_wise_ques_key_path)
                        # lang_wise_ques_key_json_path = os.path.join(lang_wise_ques_key_path, 'json')
                        os.mkdir(lang_wise_ques_key_json_path)
                        # lang_wise_ques_key_audio_path = os.path.join(lang_wise_ques_key_path, 'audio')
                        # if (prompt_type in lang_wise_ques_key_path):
                    lang_wise_ques_key_prompt_type_path = os.path.join(lang_wise_ques_key_path, prompt_type)
                    if not os.path.exists(lang_wise_ques_key_prompt_type_path):
                        os.mkdir(lang_wise_ques_key_prompt_type_path)
                        # logger.debug("prompt_type: %s, lang_wise_ques_key_prompt_type_path: %s",
                        #                 prompt_type, lang_wise_ques_key_prompt_type_path)
                        # os.mkdir(lang_wise_ques_key_audio_path)
                        # os.mkdir(lang_wise_ques_key_image_path)
                        # os.mkdir(lang_wise_ques_key_multimedia_path)
                    if (lang_wise_ques_key != ''):
                        if (lang_wise_ques_key in lang_wise_ques):
                            # logger.debug('prompt_type: %s', prompt_type)
                            # logger.debug("lang_wise_ques_key: %s", lang_wise_ques_key)
                            # logger.debug("temp_dict: %s", pformat(temp_dict))
                            lang_wise_ques[lang_wise_ques_key].append(temp_dict)
                        else:
                            lang_wise_ques[lang_wise_ques_key] = [temp_dict]
                            # logger.debug('lang_wise_ques: %s', pformat(lang_wise_ques))

                        domain_wise_ques_key = lang_wise_ques_key+'_'+domain
                        domain_wise_ques_key_path = os.path.join(project_folder_path, domain_wise_ques_key)
                        domain_wise_ques_key_json_path = os.path.join(domain_wise_ques_key_path, 'json')
                        # domain_wise_ques_key_audio_path = os.path.join(domain_wise_ques_key_path, 'audio')
                        # domain_wise_ques_key_image_path = os.path.join(domain_wise_ques_key_path, 'image')
                        # domain_wise_ques_key_multimedia_path = os.path.join(domain_wise_ques_key_path, 'multimedia')
                        if not os.path.exists(domain_wise_ques_key_path):
                            os.mkdir(domain_wise_ques_key_path)
                            # domain_wise_ques_key_json_path = os.path.join(domain_wise_ques_key_path, 'json')
                            os.mkdir(domain_wise_ques_key_json_path)
                            # domain_wise_ques_key_audio_path = os.path.join(domain_wise_ques_key_path, 'audio')
                        domain_wise_ques_key_prompt_type_path = os.path.join(domain_wise_ques_key_path, prompt_type)
                        if not os.path.exists(domain_wise_ques_key_prompt_type_path):
                            os.mkdir(domain_wise_ques_key_prompt_type_path)
                            # os.mkdir(domain_wise_ques_key_audio_path)
                            # os.mkdir(domain_wise_ques_key_image_path)
                            # os.mkdir(domain_wise_ques_key_multimedia_path)
                        
                        if (domain_wise_ques_key in lang_wise_ques):
                            lang_wise_ques[domain_wise_ques_key].append(temp_dict)
                        else:
                            lang_wise_ques[domain_wise_ques_key] = [temp_dict]

                    if (audio_fileId != '' and audio_file_path != ''):
                        # logger.debug("prompt_type: %s, lang_wise_ques_key_prompt_type_path: %s",
                        #                      prompt_type, lang_wise_ques_key_prompt_type_path)
                        # logger.debug("trimmed_audio_file_path: %s, lang_wise_ques_key_prompt_type_path: %s",
                        #              trimmed_audio_file_path, lang_wise_ques_key_prompt_type_path)
                        # logger.debug("trimmed_audio_file_path: %s, domain_wise_ques_key_prompt_type_path: %s",
                        #              trimmed_audio_file_path, domain_wise_ques_key_prompt_type_path)
                        # shutil.copy2(audio_file_path, lang_wise_ques_key_audio_path)
                        # shutil.copy2(audio_file_path, domain_wise_ques_key_audio_path)
                        # os.remove(audio_file_path)
                        # shutil.copy2(trimmed_audio_file_path, lang_wise_ques_key_audio_path)
                        shutil.copy2(trimmed_audio_file_path, lang_wise_ques_key_prompt_type_path)
                        # shutil.copy2(trimmed_audio_file_path, domain_wise_ques_key_audio_path)
                        shutil.copy2(trimmed_audio_file_path, domain_wise_ques_key_prompt_type_path)
                        os.remove(trimmed_audio_file_path)
                        # print('trimmed_audio_file_path:\n', trimmed_audio_file_path)
                        # print('lang_wise_ques_key_audio_path:\n', lang_wise_ques_key_audio_path)
                        # print("domain_wise_ques_key:", domain_wise_ques_key)
                        # print("domain_wise_ques_key_path:", domain_wise_ques_key_path)
                        # print('domain_wise_ques_key_audio_path:\n', domain_wise_ques_key_audio_path)
                    # print(
                    #     "lang_wise_ques_key:", lang_wise_ques_key,
                    #     "lang_wise_ques_key_path:", lang_wise_ques_key_path,
                    #     "domain_wise_ques_key:", domain_wise_ques_key,
                    #     "domain_wise_ques_key_path:", domain_wise_ques_key_path
                    # )

                    if (image_fileId != '' and image_file_path != ''):
                        # logger.debug("image_file_path: %s, lang_wise_ques_key_prompt_type_path: %s",
                        #              image_file_path, lang_wise_ques_key_prompt_type_path)
                        # logger.debug("image_file_path: %s, domain_wise_ques_key_prompt_type_path: %s",
                        #              image_file_path, domain_wise_ques_key_prompt_type_path)
                        # shutil.copy2(image_file_path, lang_wise_ques_key_image_path)
                        # shutil.copy2(image_file_path, domain_wise_ques_key_image_path)
                        # os.remove(image_file_path)
                        # shutil.copy2(image_file_path, lang_wise_ques_key_image_path)
                        shutil.copy2(image_file_path, lang_wise_ques_key_prompt_type_path)
                        # shutil.copy2(image_file_path, domain_wise_ques_key_image_path)
                        shutil.copy2(image_file_path, domain_wise_ques_key_prompt_type_path)
                        os.remove(image_file_path)
                    
                    if (multimedia_fileId != '' and multimedia_file_path != ''):
                        # logger.debug("multimedia_file_path: %s, lang_wise_ques_key_prompt_type_path: %s",
                        #              multimedia_file_path, lang_wise_ques_key_prompt_type_path)
                        # logger.debug("multimedia_file_path: %s, domain_wise_ques_key_prompt_type_path: %s",
                        #              multimedia_file_path, domain_wise_ques_key_prompt_type_path)
                        # shutil.copy2(multimedia_file_path, lang_wise_ques_key_multimedia_path)
                        # shutil.copy2(multimedia_file_path, domain_wise_ques_key_multimedia_path)
                        # os.remove(multimedia_file_path)
                        # shutil.copy2(multimedia_file_path, lang_wise_ques_key_multimedia_path)
                        shutil.copy2(multimedia_file_path, lang_wise_ques_key_prompt_type_path)
                        # shutil.copy2(multimedia_file_path, domain_wise_ques_key_multimedia_path)
                        shutil.copy2(multimedia_file_path, domain_wise_ques_key_prompt_type_path)
                        os.remove(multimedia_file_path)
                    # logger.debug("temp_dict: %s", temp_dict)
                    
        # pprint(lang_wise_ques)
        folder_stats = {}
        for key, value in lang_wise_ques.items():
            # print('LINE NO. 127', key, len(value), folder_stats)
            # folder_stats[key] = len(value)
            filename = key+'.json'
            save_file_path = os.path.join(project_folder_path, key, 'json', filename)
            with open(save_file_path, 'w') as json_file:
                json.dump(value, json_file, ensure_ascii=False, indent=2)
        # pprint(folder_stats)
        for folder_name in sorted(os.listdir(project_folder_path)):
            # logger.debug("folder_name: %s", folder_name)
            
            if ('trimmed_audio' in folder_name or
                'ques_image' in folder_name or
                'ques_multimedia' in folder_name):
                continue
            folder_stats[folder_name] = {}
            json_folder_path = os.path.join(project_folder_path, folder_name, 'json')
            # print(json_folder_path)
            folder_stats[folder_name]['json'] = datafolder_stats(json_folder_path, 'json')
            zip_file_path = createzip(json_folder_path, folder_name+'_json')

            audio_folder_path = os.path.join(project_folder_path, folder_name, 'audio')
            # print(audio_folder_path)
            if (os.path.exists(audio_folder_path)):
                folder_stats[folder_name]['audio'] = datafolder_stats(audio_folder_path, 'audio')
                zip_file_path = createzip(audio_folder_path, folder_name+'_recordings')

            image_folder_path = os.path.join(project_folder_path, folder_name, 'image')
            # print(image_folder_path)
            if (os.path.exists(image_folder_path)):
                folder_stats[folder_name]['image'] = datafolder_stats(image_folder_path, 'image')
                zip_file_path = createzip(image_folder_path, folder_name+'_image')

            multimedia_folder_path = os.path.join(project_folder_path, folder_name, 'multimedia')
            # print(multimedia_folder_path)
            if (os.path.exists(multimedia_folder_path)):
                folder_stats[folder_name]['multimedia'] = datafolder_stats(multimedia_folder_path, 'multimedia')
                zip_file_path = createzip(multimedia_folder_path, folder_name+'_multimedia')
        
        shutil.rmtree(trimmed_audio_folder_path)
        shutil.rmtree(ques_image_folder_path)
        shutil.rmtree(ques_multimedia_folder_path)
        # pprint(folder_stats)
        folder_stats_path = os.path.join(project_folder_path, 'folder_stats.json')
        with open(folder_stats_path, 'w') as json_file:
            json.dump(folder_stats, json_file, ensure_ascii=False, indent=2)
    except:
        logger.exception("")

    return project_folder_path

def karyajson2(mongo,
                base_dir,
                questionnaires,
                activeprojectname):
    # print('karyajson')
    project_folder_path = createprojectdirectory(base_dir, activeprojectname)
    # logger.debug('project_folder_path: %s', project_folder_path)
    try:
        trimmed_audio_folder_path = os.path.join(project_folder_path, 'trimmed_audio')
        if not os.path.exists(trimmed_audio_folder_path):
            os.mkdir(trimmed_audio_folder_path)
        ques_image_folder_path = os.path.join(project_folder_path, 'ques_image')
        if not os.path.exists(ques_image_folder_path):
            os.mkdir(ques_image_folder_path)
        ques_multimedia_folder_path = os.path.join(project_folder_path, 'ques_multimedia')
        if not os.path.exists(ques_multimedia_folder_path):
            os.mkdir(ques_multimedia_folder_path)
        # dictionary containing lang-script as key and list of dictionaries(karya json format) as value
        lang_wise_ques = {}
        # karya_json_data = []
        saved_ques_data = questionnaires.find({'projectname': activeprojectname, 'quessaveFLAG': 1, 'quesdeleteFLAG': 0},
                                                {
                                                    "_id": 0,
                                                    "quesId": 1,
                                                    "Q_Id": 1,
                                                    "prompt": 1
                                                }
                                            )

        for ques_data in saved_ques_data:
            # logger.debug("Q_Id: %s", ques_data["Q_Id"])
            prompt = ques_data['prompt']
            content = prompt['content']
            # logger.debug('prompt: %s, content: %s', prompt, content)
            for lang_script, lang_info in content.items():
                script = lang_script.split('-')[1]
                # print(lang_script, lang_info)
                for prompt_type, prompt_data in lang_info.items():
                    # logger.debug('prompt_type: %s', prompt_type)
                    # logger.debug('prompt_data: %s', prompt_data)
                    lang_wise_ques_key = ''
                    domain = prompt['Domain'][0]
                    # print('domain:', domain)
                    elicitation_method = prompt['Elicitation Method']
                    final_temp_dict = {}
                    temp_dict = {
                        "quesId": ques_data["quesId"],
                        "Q_Id": ques_data["Q_Id"],
                        "Domain": domain,
                        "Elicitation Method": elicitation_method
                    }
                    files = {}
                    if (prompt_type+'Instruction' in prompt_data):
                        temp_dict['instruction'] = prompt_data[prompt_type+'Instruction']
                    audio_fileId = ''
                    audio_file_path = ''
                    image_fileId = ''
                    image_file_path = ''
                    multimedia_fileId = ''
                    multimedia_file_path = ''
                    if (prompt_type == 'text'):
                        lang_wise_ques_key = lang_script.replace('-', '_')+'_'+prompt_type
                        boundaryId = list(prompt_data.keys())[0]
                        sentence = prompt_data[boundaryId]['textspan'][script]
                        temp_dict['sentence'] = sentence
                        # temp_dict['hint'] = ''
                        # files['hint'] = ''
                    elif (prompt_type == 'audio'):
                        # logger.debug("lang_wise_ques_key: %s", lang_wise_ques_key)
                        lang_wise_ques_key = lang_script.replace('-', '_')+'_'+prompt_type
                        # logger.debug("lang_wise_ques_key: %s", lang_wise_ques_key)
                        boundaryId = list(prompt_data['textGrid']['sentence'].keys())[0]
                        sentence = prompt_data['textGrid']['sentence'][boundaryId]['transcription'][script]
                        temp_dict['sentence'] = sentence
                        # temp_dict['hint'] = prompt_data['filename']
                        files['hint'] = prompt_data['filename']
                        # logger.debug("files: %s", files)
                        audio_fileId = prompt_data['fileId']
                        # get the file to local storage from database 'fs' collection
                        # print(mongo,
                        #         project_folder_path,
                        #         audio_fileId,
                        #         'fileId')
                        audio_file_path = getfilefromfs(mongo,
                                                        project_folder_path,
                                                        audio_fileId,
                                                        'audio',
                                                        'fileId')
                        logger.debug('audio_file_path: %s', audio_file_path)
                        if (audio_file_path != ''):
                            # crop audio from start to end time
                            start_time = prompt_data['textGrid']['sentence'][boundaryId]['startindex']
                            end_time = prompt_data['textGrid']['sentence'][boundaryId]['endindex']
                            # logger.debug("Audio duration: %s", librosa.get_duration(filename=audio_file_path))
                            if (start_time == ''):
                                start_time = 0
                            if (end_time == ''):
                                end_time = librosa.get_duration(filename=audio_file_path)
                            # logger.debug("start time: %s, end time: %s", start_time, end_time)
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
                        else:
                            continue
                    elif (prompt_type == 'multimedia'):
                        # logger.debug("lang_wise_ques_key: %s", lang_wise_ques_key)
                        lang_wise_ques_key = lang_script.replace('-', '_')+'_'+prompt_type
                        # logger.debug("lang_wise_ques_key: %s", lang_wise_ques_key)
                        # boundaryId = list(prompt_data['textGrid']['sentence'].keys())[0]
                        # sentence = prompt_data['textGrid']['sentence'][boundaryId]['transcription'][script]
                        # temp_dict['sentence'] = sentence
                        multimedia_fileId = prompt_data['fileId']
                        if (multimedia_fileId != ''):
                            # temp_dict['hint'] = prompt_data['filename']
                            files['hint'] = prompt_data['filename']
                            multimedia_file_path = getfilefromfs(mongo,
                                                            project_folder_path,
                                                            multimedia_fileId,
                                                            'video',
                                                            'fileId')
                        else:
                            continue
                    elif (prompt_type == 'image'):
                        # logger.debug("lang_wise_ques_key: %s", lang_wise_ques_key)
                        lang_wise_ques_key = lang_script.replace('-', '_')+'_'+prompt_type
                        # logger.debug("lang_wise_ques_key: %s", lang_wise_ques_key)
                        # boundaryId = list(prompt_data['textGrid']['sentence'].keys())[0]
                        # sentence = prompt_data['textGrid']['sentence'][boundaryId]['transcription'][script]
                        # temp_dict['sentence'] = sentence
                        image_fileId = prompt_data['fileId']
                        if (image_fileId != ''):
                            # temp_dict['hint'] = prompt_data['filename']
                            files['hint'] = prompt_data['filename']
                            image_file_path = getfilefromfs(mongo,
                                                            project_folder_path,
                                                            image_fileId,
                                                            'image',
                                                            'fileId')
                        else:
                            continue
                    lang_wise_ques_key_path = os.path.join(project_folder_path, lang_wise_ques_key)
                    # logger.debug("prompt_type: %s, lang_wise_ques_key_path: %s",
                    #                         prompt_type, lang_wise_ques_key_path)
                    lang_wise_ques_key_json_path = os.path.join(lang_wise_ques_key_path, 'json')
                    # lang_wise_ques_key_audio_path = os.path.join(lang_wise_ques_key_path, 'audio')
                    # lang_wise_ques_key_image_path = os.path.join(lang_wise_ques_key_path, 'image')
                    # lang_wise_ques_key_multimedia_path = os.path.join(lang_wise_ques_key_path, 'multimedia')
                    # logger.debug("lang_wise_ques_key_path: %s", lang_wise_ques_key_path)
                    # logger.debug("lang_wise_ques_key_audio_path: %s", lang_wise_ques_key_audio_path)
                    if not os.path.exists(lang_wise_ques_key_path):
                        os.mkdir(lang_wise_ques_key_path)
                        # lang_wise_ques_key_json_path = os.path.join(lang_wise_ques_key_path, 'json')
                        os.mkdir(lang_wise_ques_key_json_path)
                        # lang_wise_ques_key_audio_path = os.path.join(lang_wise_ques_key_path, 'audio')
                        # if (prompt_type in lang_wise_ques_key_path):
                    lang_wise_ques_key_prompt_type_path = os.path.join(lang_wise_ques_key_path, prompt_type)
                    if not os.path.exists(lang_wise_ques_key_prompt_type_path):
                        os.mkdir(lang_wise_ques_key_prompt_type_path)
                        # logger.debug("prompt_type: %s, lang_wise_ques_key_prompt_type_path: %s",
                        #                 prompt_type, lang_wise_ques_key_prompt_type_path)
                        # os.mkdir(lang_wise_ques_key_audio_path)
                        # os.mkdir(lang_wise_ques_key_image_path)
                        # os.mkdir(lang_wise_ques_key_multimedia_path)
                    final_temp_dict = {
                                "data": temp_dict,
                                "files": files
                            }
                    if (lang_wise_ques_key != ''):
                        if (lang_wise_ques_key in lang_wise_ques):
                            # logger.debug('prompt_type: %s', prompt_type)
                            # logger.debug("lang_wise_ques_key: %s", lang_wise_ques_key)
                            # logger.debug("temp_dict: %s", pformat(temp_dict))
                            # lang_wise_ques[lang_wise_ques_key].append(temp_dict)
                            lang_wise_ques[lang_wise_ques_key].append(final_temp_dict)
                        else:
                            # lang_wise_ques[lang_wise_ques_key] = [temp_dict]
                            lang_wise_ques[lang_wise_ques_key] = [final_temp_dict]
                            # logger.debug('lang_wise_ques: %s', pformat(lang_wise_ques))

                        domain_wise_ques_key = lang_wise_ques_key+'_'+domain
                        domain_wise_ques_key_path = os.path.join(project_folder_path, domain_wise_ques_key)
                        domain_wise_ques_key_json_path = os.path.join(domain_wise_ques_key_path, 'json')
                        # domain_wise_ques_key_audio_path = os.path.join(domain_wise_ques_key_path, 'audio')
                        # domain_wise_ques_key_image_path = os.path.join(domain_wise_ques_key_path, 'image')
                        # domain_wise_ques_key_multimedia_path = os.path.join(domain_wise_ques_key_path, 'multimedia')
                        if not os.path.exists(domain_wise_ques_key_path):
                            os.mkdir(domain_wise_ques_key_path)
                            # domain_wise_ques_key_json_path = os.path.join(domain_wise_ques_key_path, 'json')
                            os.mkdir(domain_wise_ques_key_json_path)
                            # domain_wise_ques_key_audio_path = os.path.join(domain_wise_ques_key_path, 'audio')
                        domain_wise_ques_key_prompt_type_path = os.path.join(domain_wise_ques_key_path, prompt_type)
                        if not os.path.exists(domain_wise_ques_key_prompt_type_path):
                            os.mkdir(domain_wise_ques_key_prompt_type_path)
                            # os.mkdir(domain_wise_ques_key_audio_path)
                            # os.mkdir(domain_wise_ques_key_image_path)
                            # os.mkdir(domain_wise_ques_key_multimedia_path)
                        
                        if (domain_wise_ques_key in lang_wise_ques):
                            # lang_wise_ques[domain_wise_ques_key].append(temp_dict)
                            lang_wise_ques[domain_wise_ques_key].append(final_temp_dict)
                        else:
                            # lang_wise_ques[domain_wise_ques_key] = [temp_dict]
                            lang_wise_ques[domain_wise_ques_key] = [final_temp_dict]

                    if (audio_fileId != '' and audio_file_path != ''):
                        # logger.debug("prompt_type: %s, lang_wise_ques_key_prompt_type_path: %s",
                        #                      prompt_type, lang_wise_ques_key_prompt_type_path)
                        # logger.debug("trimmed_audio_file_path: %s, lang_wise_ques_key_prompt_type_path: %s",
                        #              trimmed_audio_file_path, lang_wise_ques_key_prompt_type_path)
                        # logger.debug("trimmed_audio_file_path: %s, domain_wise_ques_key_prompt_type_path: %s",
                        #              trimmed_audio_file_path, domain_wise_ques_key_prompt_type_path)
                        # shutil.copy2(audio_file_path, lang_wise_ques_key_audio_path)
                        # shutil.copy2(audio_file_path, domain_wise_ques_key_audio_path)
                        # os.remove(audio_file_path)
                        # shutil.copy2(trimmed_audio_file_path, lang_wise_ques_key_audio_path)
                        shutil.copy2(trimmed_audio_file_path, lang_wise_ques_key_prompt_type_path)
                        # shutil.copy2(trimmed_audio_file_path, domain_wise_ques_key_audio_path)
                        shutil.copy2(trimmed_audio_file_path, domain_wise_ques_key_prompt_type_path)
                        os.remove(trimmed_audio_file_path)
                        # print('trimmed_audio_file_path:\n', trimmed_audio_file_path)
                        # print('lang_wise_ques_key_audio_path:\n', lang_wise_ques_key_audio_path)
                        # print("domain_wise_ques_key:", domain_wise_ques_key)
                        # print("domain_wise_ques_key_path:", domain_wise_ques_key_path)
                        # print('domain_wise_ques_key_audio_path:\n', domain_wise_ques_key_audio_path)
                    # print(
                    #     "lang_wise_ques_key:", lang_wise_ques_key,
                    #     "lang_wise_ques_key_path:", lang_wise_ques_key_path,
                    #     "domain_wise_ques_key:", domain_wise_ques_key,
                    #     "domain_wise_ques_key_path:", domain_wise_ques_key_path
                    # )

                    if (image_fileId != '' and image_file_path != ''):
                        # logger.debug("image_file_path: %s, lang_wise_ques_key_prompt_type_path: %s",
                        #              image_file_path, lang_wise_ques_key_prompt_type_path)
                        # logger.debug("image_file_path: %s, domain_wise_ques_key_prompt_type_path: %s",
                        #              image_file_path, domain_wise_ques_key_prompt_type_path)
                        # shutil.copy2(image_file_path, lang_wise_ques_key_image_path)
                        # shutil.copy2(image_file_path, domain_wise_ques_key_image_path)
                        # os.remove(image_file_path)
                        # shutil.copy2(image_file_path, lang_wise_ques_key_image_path)
                        shutil.copy2(image_file_path, lang_wise_ques_key_prompt_type_path)
                        # shutil.copy2(image_file_path, domain_wise_ques_key_image_path)
                        shutil.copy2(image_file_path, domain_wise_ques_key_prompt_type_path)
                        os.remove(image_file_path)
                    
                    if (multimedia_fileId != '' and multimedia_file_path != ''):
                        # logger.debug("multimedia_file_path: %s, lang_wise_ques_key_prompt_type_path: %s",
                        #              multimedia_file_path, lang_wise_ques_key_prompt_type_path)
                        # logger.debug("multimedia_file_path: %s, domain_wise_ques_key_prompt_type_path: %s",
                        #              multimedia_file_path, domain_wise_ques_key_prompt_type_path)
                        # shutil.copy2(multimedia_file_path, lang_wise_ques_key_multimedia_path)
                        # shutil.copy2(multimedia_file_path, domain_wise_ques_key_multimedia_path)
                        # os.remove(multimedia_file_path)
                        # shutil.copy2(multimedia_file_path, lang_wise_ques_key_multimedia_path)
                        shutil.copy2(multimedia_file_path, lang_wise_ques_key_prompt_type_path)
                        # shutil.copy2(multimedia_file_path, domain_wise_ques_key_multimedia_path)
                        shutil.copy2(multimedia_file_path, domain_wise_ques_key_prompt_type_path)
                        os.remove(multimedia_file_path)
                    # logger.debug("temp_dict: %s", temp_dict)
                    
        # pprint(lang_wise_ques)
        folder_stats = {}
        for key, value in lang_wise_ques.items():
            # print('LINE NO. 127', key, len(value), folder_stats)
            # folder_stats[key] = len(value)
            filename = key+'.json'
            save_file_path = os.path.join(project_folder_path, key, 'json', filename)
            with open(save_file_path, 'w') as json_file:
                json.dump(value, json_file, ensure_ascii=False, indent=2)
        # pprint(folder_stats)
        for folder_name in sorted(os.listdir(project_folder_path)):
            # logger.debug("folder_name: %s", folder_name)
            
            if ('trimmed_audio' in folder_name or
                'ques_image' in folder_name or
                'ques_multimedia' in folder_name):
                continue
            folder_stats[folder_name] = {}
            json_folder_path = os.path.join(project_folder_path, folder_name, 'json')
            # print(json_folder_path)
            folder_stats[folder_name]['json'] = datafolder_stats(json_folder_path, 'json')
            zip_file_path = createzip(json_folder_path, folder_name+'_json')

            audio_folder_path = os.path.join(project_folder_path, folder_name, 'audio')
            # print(audio_folder_path)
            if (os.path.exists(audio_folder_path)):
                folder_stats[folder_name]['audio'] = datafolder_stats(audio_folder_path, 'audio')
                zip_file_path = createzip(audio_folder_path, folder_name+'_recordings')

            image_folder_path = os.path.join(project_folder_path, folder_name, 'image')
            # print(image_folder_path)
            if (os.path.exists(image_folder_path)):
                folder_stats[folder_name]['image'] = datafolder_stats(image_folder_path, 'image')
                zip_file_path = createzip(image_folder_path, folder_name+'_image')

            multimedia_folder_path = os.path.join(project_folder_path, folder_name, 'multimedia')
            # print(multimedia_folder_path)
            if (os.path.exists(multimedia_folder_path)):
                folder_stats[folder_name]['multimedia'] = datafolder_stats(multimedia_folder_path, 'multimedia')
                zip_file_path = createzip(multimedia_folder_path, folder_name+'_multimedia')
        
        shutil.rmtree(trimmed_audio_folder_path)
        shutil.rmtree(ques_image_folder_path)
        shutil.rmtree(ques_multimedia_folder_path)
        # pprint(folder_stats)
        folder_stats_path = os.path.join(project_folder_path, 'folder_stats.json')
        with open(folder_stats_path, 'w') as json_file:
            json.dump(folder_stats, json_file, ensure_ascii=False, indent=2)
    except:
        logger.exception("")

    return project_folder_path
