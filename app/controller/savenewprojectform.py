"""Module to save new project form in database."""

import re

def savenewprojectform(projectsform,
                        projectname,
                        project_form_data,
                        current_username):
    """
    Args:
        projectsform: instance of 'projectsform' collection.
        projectname: name of the project.
        project_form_data: project form detail from frontend.
        current_username: name of the current active user.

    Returns:
        _type_: _description_
    """
    
    # print(f'{"#"*80}\nprojectFormData\n{project_form_data}')
    project_form = {}
    project_form['username'] = current_username
    project_form['projectname'] = projectname
    dynamic_form_field = []
    list_of_custom_fields = []
    for key, value in project_form_data.items():
        if re.search(r'[0-9]+', key):
            dynamic_form_field.append(value[0])
        elif key == 'Lexeme Form Script':
            project_form[key] = value
        elif key == 'Gloss Language':
            value.insert(0, 'English')
            project_form[key] = value
        elif key == 'Gloss Script':
            value.insert(0, 'Latin')
            project_form[key] = value
        elif key == 'Interlinear Gloss Language':
            value.insert(0, 'English')
            project_form[key] = value
        elif key == 'Interlinear Gloss Script':
            value.insert(0, 'Latin')
            project_form[key] = value
        elif len(value) == 1:
            project_form[key] = value[0]
        else:
            project_form[key] = value

    if "Gloss Language" not in project_form:
        project_form["Gloss Language"] = ['English']
    if "Gloss Script" not in project_form:
        project_form["Gloss Script"] = ['Latin']
    if "Interlinear Gloss Language" not in project_form:
        project_form["Interlinear Gloss Language"] = ['English']
    if "Interlinear Gloss Script" not in project_form:
        project_form["Interlinear Gloss Script"] = ['Latin']
    if len(dynamic_form_field) > 1:
        for i in range(0,len(dynamic_form_field),2):
            list_of_custom_fields.append({dynamic_form_field[i] : dynamic_form_field[i+1]})
        project_form['Custom Fields'] = list_of_custom_fields
    # sentence form detail
    project_form['Sentence Language'] = project_form['Lexeme Language']
    project_form['Transcription Script'] = project_form['Lexeme Form Script']
    project_form['Translation Language'] = project_form['Gloss Language']
    project_form['Translation Script']  = project_form['Gloss Script']
    # print(project_form)
    # when testing comment these to avoid any database update/changes
    projectsform.insert(project_form)
