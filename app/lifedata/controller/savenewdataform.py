"""Module to save new data project form in database."""

from pprint import pprint
import re

def savenewdataform(projectsform,
                    projectname,
                    new_data_form,
                    current_username
                ):

        
    # print(f'{"#"*80}\nprojectFormData\n{new_data_form}')
    project_form = {}
    project_form['username'] = current_username
    project_form['projectname'] = projectname
    for key, value in new_data_form.items():
        if key == 'Sentence Language':
            project_form[key] = value
        elif key == 'Transcription Script':
            project_form[key] = value
        elif key == 'Translation Language':
            # value.insert_many(0, 'English')
            project_form[key] = value
        elif key == 'Translation Script':
            # value.insert_many(0, 'Latin')
            project_form[key] = value
        elif key == 'Interlinear Gloss Language':
            # value.insert_many(0, 'English')
            project_form[key] = value
        elif key == 'Interlinear Gloss Script':
            # value.insert_many(0, 'Latin')
            project_form[key] = value

    # if "Translation Language" not in project_form:
    #     project_form["Translation Language"] = ['English']
    # if "Translation Script" not in project_form:
    #     project_form["Translation Script"] = ['Latin']
    # if "Interlinear Gloss Language" not in project_form:
    #     project_form["Interlinear Gloss Language"] = ['English']
    # if "Interlinear Gloss Script" not in project_form:
    #     project_form["Interlinear Gloss Script"] = ['Latin']
        
    # pprint(project_form)
    # when testing comment these to avoid any database update/changes
    projectsform.insert_one(project_form)

    return project_form