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
    logger.debug("new_transcription_form: %s", pformat(new_transcription_form))
    saved_form = {}
    save_status = False
    try:
        interlinear_gloss_dict = {}
        translation_dict = {}
        tagsets_dict = {}
        additional_transcription_dict = {}

        saved_form['username'] = current_username
        saved_form['projectname'] = projectname

        for key, value in new_transcription_form.items():
            # logger.debug("key: %s,\nvalue: %s", key, value)
            if (key == 'Audio Language' or
                key == 'Sentence Language'):
                if ('-' in value[0]):
                    value = [value[0].split('-')[0]]
                    # logger.debug("key: %s,\nvalue: %s", key, value)
                saved_form['Audio Language'] = ["text", value]
            elif key == 'Transcription Script':
                saved_form['Transcription'] = ["textarea", value]
            elif key == 'Translation Language':
                for i in range(len(value)):
                    script = new_transcription_form['Translation Script'][i]
                    lang_script = value[i]+'-'+script
                    translation_dict[lang_script] = script
            elif key == 'Interlinear Gloss Language':
                for i in range(len(value)):
                    script = new_transcription_form['Interlinear Gloss Script'][i]
                    lang_script = value[i]+'-'+script
                    interlinear_gloss_dict[lang_script] = script
            elif key == 'Interlinear Gloss Format':
                interlinear_gloss_dict['Interlinear Gloss Format'] = value
            elif key == 'Customize Gloss':
                interlinear_gloss_dict['Customize Gloss'] = value
            elif key == 'Additional Transcription Name':
                additional_transcription_scripts = new_transcription_form['Additional Transcription Script']
                for i, additional_transcription_name in enumerate(value):
                    additional_transcription_script = additional_transcription_scripts[i]
                    additional_transcription_key = additional_transcription_name+'-'+additional_transcription_script
                    additional_transcription_dict[additional_transcription_key] = additional_transcription_script
            elif key == 'Audio Annotation':
                tagsets_dict["Audio Annotation"] = value
            elif key == 'Boundary Annotation':
                tagsets_dict["Boundary Annotation"] = value
        logger.debug("%s, %s, %s",
                     len(translation_dict),
                     len(interlinear_gloss_dict),
                     len(tagsets_dict))
        if (len(translation_dict) != 0):
            saved_form['Translation'] = ["textarea", translation_dict]
        if (len(interlinear_gloss_dict) != 0):
            saved_form['Interlinear Gloss'] = ["interlineargloss", interlinear_gloss_dict]
        if (len(tagsets_dict) != 0):
            saved_form['Tagsets'] = ["tagsets", tagsets_dict]
        if (len(additional_transcription_dict) != 0):
            saved_form['Additional Transcription'] = ["additionaltranscription", additional_transcription_dict]
            saved_form['Transcription'][1].extend(list(additional_transcription_dict.keys()))

        logger.debug("saved form: %s", pformat(saved_form))
        projectsform_collection.insert_one(saved_form)
        save_status = True
    except:
        logger.exception("")

    return (saved_form, save_status)

# new_transcription_form = {
#     'Audio Language': ['Bhojpuri'],
#     'Interlinear Gloss Language': ['Bangla', 'Bangla', 'English'],
#     'Interlinear Gloss Script': ['Bengali', 'Devanagari', 'Latin'],
#     'Transcription Script': ['Devanagari', 'IPA', 'Latin'],
#     'Translation Language': ['Assamese', 'Assamese', 'Hindi'],
#     'Translation Script': ['Bengali', 'Latin', 'Devanagari'],
#     'aboutproject': ['Transcription_Validation_2023-09-24_23-11-21'],
#     'projectType': ['transcriptions'],
#     'projectname': ['Transcription_Validation_2023-09-24_23-14-21'],
#     'transcriptionsboundarytagsetuploadcheckbox': ['on'],
#     'transcriptionsboundarytagsetuploadselect': ['textAnno_tags_1'],
#     'transcriptionstagsetuploadcheckbox': ['on'],
#     'transcriptionstagsetuploadselect': ['textAnno_tags'],
#     "Audio Annotation": "",
#     "Boundary Annotation": ""
#     }

# save_new_transcription_form("",
#                             "",
#                             new_transcription_form,
#                             "")
