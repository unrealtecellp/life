"""Module to save each ques when 'Save' button clicked on the 'questionnaire' interface."""
from app.controller import (
    life_logging
)
from pprint import pprint, pformat

logger = life_logging.get_logger()

def saveques(questionnaires,
                ques_data,
                last_active_ques_id,
                current_username
            ):
    try:
        savedQuestionnaire = 0
        # print('saveques()', last_active_ques_id)
        quesdata = questionnaires.find_one({"quesId": last_active_ques_id}, {"_id": 0})
        # pprint(quesdata)
        # pprint(ques_data)
        prompt = quesdata['prompt']
        text = {}
        
        content = {}
        sentence = {}
        start = '000'
        end = '000'
        if ('start' in ques_data and 'end' in ques_data):
            start = ques_data['start'][0]
            end = ques_data['end'][0]
        transcription_boundaryId = start[:4].replace('.', '') + end[:4].replace('.', '')
        transcription_boundary_data = {}
        transcription = ''
        for key, value in ques_data.items():
            print(key)
            if (key == 'Q_Id'):
                qid = value[0]
            if (key in prompt):
                prompt[key] = value
            if ('Transcription' in key):
                # transcription_lang = key.split()[1]
                prompt_type = key.split()[1]
                lang_name = key.split(' Transcription ')[-1]
                # print(key.split(' Transcription '), lang_name)
                transcription_script = lang_name.split('-')[1]
                transcription = value[0]
                transcription_boundary_data[transcription_boundaryId] =  {
                                                                    "startindex": start,
                                                                    "endindex": end,
                                                                    "transcription": {
                                                                        transcription_script: transcription
                                                                    }
                                                                }
                sentence = transcription_boundary_data
                # prompt['Transcription']['textGrid']['sentence'] = sentence
                prompt['content'][lang_name][prompt_type.lower()]['textGrid']['sentence'] = sentence
            if (key == 'Elicitation Method'):
                # print(key, value)
                prompt[key] = value[0]
            if ('Language' in key):
                text_boundary_data = {}
                lang_name = key.split(' Language ')[-1]
                # print(key.split(' Language '), lang_name)
                lang_script = lang_name.split('-')[1]
                value = ques_data[key][0]
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
                # print(text_boundary_data)
                # content[lang_name] = value
                prompt['content'][lang_name]['text'] = text_boundary_data
            if ('Instruction' in key):
                # logger.debug("key: %s, value: %s",
                #              key, value)
                prompt_type = key.split()[0]
                prompt_type_lower = prompt_type.lower()
                lang_name = key.split()[-1]
                instruction_script = lang_name.split('-')[1]
                instruction = value[0]
                prompt['content'][lang_name][prompt_type_lower][prompt_type_lower+'Instruction'] = instruction
                # logger.debug("prompt: %s", pformat(prompt))

        saved_ques = questionnaires.update_one({"quesId": last_active_ques_id},
                                    {"$set" : { 
                                                'prompt': prompt,
                                                'quessaveFLAG': 1,
                                                'lastUpdatedBy': current_username,
                                                'Q_Id': qid
                                                }
                                    }
                                )
        # logger.debug('ques savedd: %s', saved_ques.acknowledged)
        savedQuestionnaire = saved_ques.acknowledged
    except:
        logger.exception("")

    return savedQuestionnaire