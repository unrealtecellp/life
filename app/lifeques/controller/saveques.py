"""Module to save each ques when 'Save' button clicked on the 'questionnaire' interface."""

from pprint import pprint

def saveques(questionnaires, ques_data, last_active_ques_id):

    print('saveques()', last_active_ques_id)
    quesdata = questionnaires.find_one({"quesId": last_active_ques_id}, {"_id": 0})
    pprint(quesdata)
    prompt = quesdata['prompt']
    text = {}
    text_boundary_data = {}
    content = {}
    sentence = {}
    start = ques_data['start'][0]
    end = ques_data['end'][0]
    transcription_boundaryId = start[:4].replace('.', '') + end[:4].replace('.', '')
    transcription_boundary_data = {}
    transcription = ''
    for key, value in ques_data.items():
        if (key in prompt):
            prompt[key] = value
        if ('Transcription' in key):
            transcription_lang = key.split()[1]
            transcription = value[0]
            transcription_boundary_data[transcription_boundaryId] =  {
                                                                "start": start,
                                                                "end": end,
                                                                "transcription": {
                                                                    transcription_lang: transcription
                                                                }
                                                            }
            sentence = transcription_boundary_data
            prompt['Transcription']['textGrid']['sentence'] = sentence
        if (key == 'Elicitation Method'):
            prompt[key] = value[0]
        if ('Language' in key):
            lang_name = key.split(' ')[1]
            value = ques_data[key][0]
            startindex = '0'
            endindex = str(len(value))
            for p in range(3):
                if (len(startindex) < 3):
                    startindex = '0'+startindex
                if (len(endindex) < 3):
                    endindex = '0'+endindex
            text_boundary_id = startindex+endindex
            text_boundary_data[lang_name] = value
            content[lang_name] = value
    text_boundary_data['startindex'] = startindex
    text_boundary_data['endindex'] = endindex    
    text[text_boundary_id] = text_boundary_data
    text['content'] = content
    prompt['text'] = text

    print('saveques()')
    pprint(quesdata)

    questionnaires.update_one({"quesId": last_active_ques_id},
                                {"$set" : { 'prompt': prompt }})
