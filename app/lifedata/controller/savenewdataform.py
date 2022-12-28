"""Module to save new data project form in database."""

from pprint import pprint
import re

def savenewdataform(projectsform,
                    projectname,
                    new_data_form,
                    current_username
                ):

        
    print(f'{"#"*80}\nprojectFormData\n{new_data_form}')
    project_form = {}
    project_form['username'] = current_username
    project_form['projectname'] = projectname
    # sentence form detail
    project_form['Sentence Language'] = new_data_form['Sentence Language']
    project_form['Transcription Script'] = new_data_form['Transcription Script']
    print(project_form)
    # when testing comment these to avoid any database update/changes
    projectsform.insert(project_form)

    return project_form