"""Module to save new questionnaire project form in database."""

from pprint import pprint

def savenewquestionnaireform(projectsform,
                                projectname,
                                new_ques_form,
                                current_username
                            ):
    """_summary_

    Args:
        projectsform (_type_): _description_
        projectname (_type_): _description_
        new_ques_form (_type_): _description_
        current_username (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    save_ques_form = {}
    
    if 'Prompt Type' in new_ques_form:
        prompt_array = new_ques_form['Prompt Type'][1]
    else:
        prompt_array = {}
    
    if 'LangScript' in new_ques_form:
        lang_script_array = new_ques_form['LangScript'][1]
    else:
        lang_script_array = {}

    save_ques_form['username'] = current_username
    save_ques_form['projectname'] = projectname
    
    print (new_ques_form.items())
    for key, value in new_ques_form.items():
        # if key == 'Language':
        
        if 'Language' in key:
            # save_ques_form[key] = ["text", value]
            key_id = key[key.find('_')+1:]

            script_name = new_ques_form['Script_'+key_id][0]

            print ('Value', value[0], 'Script name', script_name)
            lang_name = value[0]+'-'+script_name
            lang_script_array.update({lang_name: script_name})
            # if 'Language_Script' in save_ques_form:
            #     save_ques_form['Language_Script'][lang_name] = script_name
            # else:
            #     save_ques_form['Language_Script'] = {lang_name: script_name}
            
            prompt_array.update(createpromptform(new_ques_form, lang_name, key_id))
             
            # if 'Prompt Type' in save_ques_form:
            #     save_ques_form['Prompt Type'][1] = prompt_array
            # else:
            #     save_ques_form['Prompt Type'] = ["prompt", prompt_array]

        # elif key == 'Script':
        #     save_ques_form[key] = ["", value]
        # elif key == 'Prompt Type':
        #     prompt_array = createpromptform(new_ques_form, value)
        #     save_ques_form[key] = ["prompt", prompt_array]
        # elif ((key == 'Transcription Language' or
        #     key == 'Transcription Script') and
        #     'Transcription' in new_ques_form):
        #     save_ques_form[key] = ["", value]
        elif key == 'Domain':
            save_ques_form[key] = ["multiselect", value]
        elif key == 'Elicitation Method':
            save_ques_form[key] = ["select", value]
        elif key =='Target':
            save_ques_form[key] = ['multiselect', value]
        elif 'customField' in key:
            save_ques_form['Custom Field '+value[0]] = [new_ques_form['fieldType'+key[-1]][0], value]
    # if 'Transcription' in new_ques_form:
    #     # save_ques_form['Transcription'] = ['waveform', new_ques_form['Transcription Language']]
    #     save_ques_form['Transcription'] = ['', new_ques_form['Transcription']]
    # # else:
    # #     save_ques_form['Transcription'] = ['', []]
    # if 'Instruction' in new_ques_form:
    #     save_ques_form['Instruction'] = ['', new_ques_form['Instruction']]
    #     # save_ques_form['Instruction'] = new_ques_form['Instruction']
    # # else:
    # #     save_ques_form['Instruction'] = ['', []]
    # # pprint(save_ques_form)

    save_ques_form['LangScript'] = ["", lang_script_array]
    save_ques_form['Prompt Type'] = ["prompt", prompt_array]
    projectsform.insert(save_ques_form)

    if "_id" in save_ques_form:
        del save_ques_form["_id"]

    return save_ques_form

def createpromptform(new_ques_form, lang_name, key_id):
    # print(new_ques_form, prompt_type_value)
    # prompt_array = []
    prompt_type_dict = {}

    prompt_type_dict['Text'] = ['text', '']

    if 'Audio_'+key_id in new_ques_form:
        if 'TranscriptionAudio_'+key_id in new_ques_form:
            if ('Audio' in prompt_type_dict):
                prompt_type_dict['Audio'].insert(0, 'waveform')
            else:
                prompt_type_dict['Audio'] = ['waveform']
        else:
            # prompt_type_dict['Audio'] = ['file']
            if ('Audio' in prompt_type_dict):
                prompt_type_dict['Audio'].insert(0, 'file')
            else:
                prompt_type_dict['Audio'] = ['file']
        
        if 'InstructionAudio_'+key_id in new_ques_form:
            # prompt_type_dict['Audio'].extend(['Instruction'])
            # prompt_type_dict['Audio Instruction'] = ["text"]
            if ('Audio' in prompt_type_dict):
                prompt_type_dict['Audio'].insert(1, 'text')
            else:
                prompt_type_dict['Audio'] = ['text']
        else:
            # prompt_type_dict['Audio'] = ['file']
            if ('Audio' in prompt_type_dict):
                prompt_type_dict['Audio'].insert(1, '')
            else:
                prompt_type_dict['Audio'] = ['']
        
    if 'Multimedia_'+key_id in new_ques_form:
        if 'TranscriptionMM_'+key_id in new_ques_form:
            if ('Multimedia' in prompt_type_dict):
                prompt_type_dict['Multimedia'].insert(0, 'waveform')
            else:
                prompt_type_dict['Multimedia'] = ['waveform']
        else:
            if ('Multimedia' in prompt_type_dict):
                prompt_type_dict['Multimedia'].insert(0, 'file')
            else:
                prompt_type_dict['Multimedia'] = ['file']
        
        if 'InstructionMM_'+key_id in new_ques_form:
            # prompt_type_dict['Multimedia'].extend(['Instruction'])
            # prompt_type_dict['Multimedia Instruction'] = ["text"]
            if ('Multimedia' in prompt_type_dict):
                prompt_type_dict['Multimedia'].insert(1, 'text')
            else:
                prompt_type_dict['Multimedia'] = ['text']
        else:
            if ('Multimedia' in prompt_type_dict):
                prompt_type_dict['Multimedia'].insert(1, '')
            else:
                prompt_type_dict['Multimedia'] = ['']

    if 'Image_'+key_id in new_ques_form:
        if ('Image' in prompt_type_dict):
            prompt_type_dict['Image'].insert(0, 'file')
        else:
            prompt_type_dict['Image'] = ['file']
        
        if 'InstructionImage_'+key_id in new_ques_form:
            # prompt_type_dict['Image'].extend(['Instruction'])
            # prompt_type_dict['Image Instruction'] = ["text"]
            if ('Image' in prompt_type_dict):
                prompt_type_dict['Image'].insert(1, 'text')
            else:
                prompt_type_dict['Image'] = ['text']
        else:
            if ('Image' in prompt_type_dict):
                prompt_type_dict['Image'].insert(1, '')
            else:
                prompt_type_dict['Image'] = ['']
    # print(lang_name)
    # pprint(prompt_type_dict)

    return {lang_name: prompt_type_dict}

    # for prompt_type in prompt_types_value:
    #     # prompt_type_dict = {}
    #     if (prompt_type == 'Audio' or
    #         prompt_type == 'Multimedia'):
    #         prompt_type_dict[prompt_type] = []
    #         if ('Transcription' in new_ques_form):
    #             prompt_type_dict[prompt_type].extend(('waveform', new_ques_form['Transcription Language']))
    #         else:
    #             prompt_type_dict[prompt_type].extend(('file', []))
    #     elif (prompt_type == 'Image'):
    #         prompt_type_dict[prompt_type] = []
    #         prompt_type_dict[prompt_type].extend(('file', []))
    #         if ('Transcription' in new_ques_form):
    #             prompt_type_dict[prompt_type].extend(('text', new_ques_form['Transcription Language']))
    #         # else:
    #         #     prompt_type_dict[prompt_type].extend(('file', []))
    #     if ('Instruction' in new_ques_form):
    #             prompt_type_dict[prompt_type].extend(('text',))
    #     else:
    #         prompt_type_dict[prompt_type].extend(('',))
    #     # prompt_array.append(prompt_type_dict)
    
    # return prompt_array
    # return prompt_type_dict