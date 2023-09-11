"""Module to save new data project form in database."""

from app.controller import (
    life_logging
)
from datetime import datetime
from zipfile import ZipFile
import pandas as pd
import io
from flask import flash, redirect, url_for
import re

logger = life_logging.get_logger()


def savenewdataform(projectsform,
                    projectname,
                    new_data_form,
                    current_username,
                    project_type
                    ):
    project_form = {}
    try:
        project_form['username'] = current_username
        project_form['projectname'] = projectname
        if (project_type == 'recordings' or
                project_type == 'transcriptions'):
            project_form = createprojectform(new_data_form, project_form)
        elif (project_type == 'validation'):
            project_form = createvalidationprojectform(
                new_data_form, project_form)
        elif (project_type == 'annotation'):
            return project_form

        projectsform.insert_one(project_form)
    except:
        logger.exception("")

    return project_form


def createprojectform(new_data_form, project_form):
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

    return project_form


def createvalidationprojectform(new_data_form, project_form):
    for key, value in new_data_form.items():
        if ('mapped' in key):
            project_form[key.replace('_mapped', '')] = {
                "onValidationCategories": value
            }

    return project_form
