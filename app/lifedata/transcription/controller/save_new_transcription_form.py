"""Module to save new transcriptions type project form in database."""

from app.controller import (
    life_logging
)
from pprint import pformat

logger = life_logging.get_logger()

def save_new_transcription_form(projectsform_collection,
                                projectname,
                                new_transcription_form,
                                current_username):
    saved_form = {}
    save_status = False
    try:
        interlinear_gloss_array = {}
        translation_array = {}

        saved_form['username'] = current_username
        saved_form['projectname'] = projectname

        for key, value in new_transcription_form.items():
            print(key, value)
    except:
        logger.exception("")

    return (saved_form, save_status)

new_transcription_form = {'Interlinear Gloss Language': ['English', 'Haryanvi', 'Chokri'],
 'Interlinear Gloss Script': ['Latin', 'Devanagari', 'Latin'],
 'Audio Language': ['Hindi'],
 'Transcription Script': ['Devanagari', 'Bengali', 'Telugu'],
 'Translation Language': ['Kannada', 'Gujarati', 'Bangla'],
 'Translation Script': ['Kannada', 'Gujarati', 'Bengali'],
 'aboutproject': ['Transcription_Validation_2023-09-04_05-08-21'],
 'projectType': ['transcriptions'],
 'projectname': ['Transcription_Validation_2023-09-04_05-08-21'],
 'transcriptionstagsetuploadcheckbox': ['on']}
save_new_transcription_form("",
                            "",
                            new_transcription_form,
                            "")