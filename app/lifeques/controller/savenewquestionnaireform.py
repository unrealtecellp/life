"""Module to save new questionnaire project form in database."""

def savenewquestionnaireform(projectsform,
                                projectname,
                                new_ques_form,
                                current_username
                            ):

    save_ques_form = {}
    save_ques_form['username'] = current_username
    save_ques_form['projectname'] = projectname
    
    for key, value in new_ques_form.items():
        if key == 'Language':
            save_ques_form[key] = ["text", value]
        elif key == 'Script':
            save_ques_form[key] = ["", value]
        elif key == 'Prompt Type':
            save_ques_form[key] = ["file", value]
        elif key == 'Domain':
            save_ques_form[key] = ["multiselect", value]
        elif key == 'Elicitation Method':
            save_ques_form[key] = ["select", value]
        elif key =='Target':
            save_ques_form[key] = ['multiselect', value]
        elif 'customField' in key:
            save_ques_form[value[0]] = [new_ques_form['fieldType'+key[-1]][0], value]
    if 'Include Transcription' in new_ques_form:
        save_ques_form['Include Transcription'] = ['waveform', new_ques_form['Include Transcription']]
    else:
        save_ques_form['Include Transcription'] = ['', []]
    if 'Include Instruction' in new_ques_form:
        save_ques_form['Include Instruction'] = ['file', new_ques_form['Include Instruction']]
    else:
        save_ques_form['Include Instruction'] = ['', []]        
    # print(save_ques_form)
    projectsform.insert(save_ques_form)

    return save_ques_form