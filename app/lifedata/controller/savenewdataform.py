"""Module to save new data project form in database."""

from app.controller import (
    life_logging
)
logger = life_logging.get_logger()

def savenewdataform(projectsform,
                    projectname,
                    new_data_form,
                    current_username
                ):
    project_form = {}
    try:
        project_form['username'] = current_username
        project_form['projectname'] = projectname
        for key, value in new_data_form.items():
            if key == 'Sentence Language':
                project_form[key] = value
            elif key == 'Transcription Script':
                project_form[key] = value
            elif key == 'Translation Language':
                project_form[key] = value
            elif key == 'Translation Script':
                project_form[key] = value
            elif key == 'Interlinear Gloss Language':
                project_form[key] = value
            elif key == 'Interlinear Gloss Script':
                project_form[key] = value

        projectsform.insert_one(project_form)
    except:
        logger.exception("")

    return project_form