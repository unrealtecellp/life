"""Module to save new questionnaire project form in database."""

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
    save_ques_form['username'] = current_username
    save_ques_form['projectname'] = projectname
    
    for key, value in new_ques_form.items():
        if key == 'Language':
            save_ques_form[key] = ["text", value]
        elif key == 'Script':
            save_ques_form[key] = ["", value]
        elif key == 'Prompt Type':
            save_ques_form[key] = ["file", value]
        elif key == 'Transcription Language':
            save_ques_form[key] = ["", value]
        elif key == 'Transcription Script':
            save_ques_form[key] = ["", value]
        elif key == 'Domain':
            save_ques_form[key] = ["multiselect", value]
        elif key == 'Elicitation Method':
            save_ques_form[key] = ["select", value]
        elif key =='Target':
            save_ques_form[key] = ['multiselect', value]
        elif 'customField' in key:
            save_ques_form['Custom Field '+value[0]] = [new_ques_form['fieldType'+key[-1]][0], value]
    if 'Transcription' in new_ques_form:
        save_ques_form['Transcription'] = ['waveform', new_ques_form['Transcription Language']]
    # else:
    #     save_ques_form['Transcription'] = ['', []]
    if 'Instruction' in new_ques_form:
        save_ques_form['Instruction'] = ['text', new_ques_form['Instruction']]
    # else:
    #     save_ques_form['Instruction'] = ['', []]
    # print(save_ques_form)

    projectsform.insert(save_ques_form)

    if "_id" in save_ques_form:
        del save_ques_form["_id"]

    return save_ques_form