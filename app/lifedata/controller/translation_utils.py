from app.controller import (
    life_logging
)

from app.lifedata.transcription.controller import (
    transcription_audiodetails
)

from app.lifemodels.controller import (
    predictFromAPI
)

from datetime import datetime

logger = life_logging.get_logger()


def save_translation_of_one_audio_file(transcriptions,
                                       activeprojectname,
                                       current_username,
                                       audio_filename,
                                       translation_model,
                                       transcription_type,
                                       save_for_user,
                                       hf_token,
                                       audio_details,
                                       accessedOnTime,
                                       boundary_ids=['*']
                                       ):

    transcription_doc_id = ''

    audio_id = audio_filename.split('_')[0]

    if current_username in audio_details:
        existing_text_grid = [audio_details[current_username]['textGrid']]

        full_model_name = translation_model.get("model_name")

        text_grids, model_details, _, translated_data = get_translation_of_audio_transcription(translation_model,
                                                                                               transcription_type,
                                                                                               hf_token,
                                                                                               audio_details,
                                                                                               existing_text_grid,
                                                                                               boundary_ids=boundary_ids)

        for text_grid in text_grids:
            audio_details_dict = {}
            transcription_audiodetails.add_text_grid(audio_details_dict,
                                                     current_username,
                                                     text_grid,
                                                     full_model_name,
                                                     model_details,
                                                     save_for_user=save_for_user)

            logger.debug("Final Audio details dict %s", audio_details_dict)

            transcription_doc_id = transcription_audiodetails.save_text_grid_into_transcription(transcriptions,
                                                                                                activeprojectname,
                                                                                                current_username,
                                                                                                audio_id,
                                                                                                audio_details_dict,
                                                                                                accessedOnTime)
        # transcription_doc_id = transcriptions.update_one({"projectname": activeprojectname, "audioId": audio_id},
        #                                                  {"$set": audio_details_dict})
    return transcription_doc_id, translated_data


def get_translation_of_audio_transcription(translation_model,
                                           transcription_type,
                                           hf_token,
                                           audio_details,
                                           existing_text_grids,
                                           input_data={},
                                           update_text_grid=True,
                                           boundary_ids=['*']):

    logger.debug('Existing Text Grid %s', existing_text_grids)
    model_details = {}
    final_text_grids = []
    all_translated_data = []
    translations = {}
    translated = 0
    model_name = translation_model['model_name']
    model_params = translation_model['model_params']
    source_script = model_params['source_script']
    model_type = translation_model['model_type']

    if len(existing_text_grids) > 0:
        for text_grid in existing_text_grids:
            translations[transcription_type] = {'translation': {}}
            current_text_grid = text_grid[transcription_type]

            if len(input_data) == 0:
                input_data = get_input_data_for_translation(
                    current_text_grid, source_script, boundary_ids=boundary_ids)

            if 'bhashini' in model_type:
                translation_start = datetime.now()
                translated_data, translated = predictFromAPI.translate_using_bhashini(
                    input_data, model_params)
                translations[transcription_type]['translation'] = translated_data
                translation_end = datetime.now()
                all_translated_data.append(translated_data)
                logger.info('Bhashini translations %s', translations)
                model_details.update([('translation_model_name', model_name), ('asr_model_params',
                                                                               model_params), ('translation_start', translation_start), ('translation_end', translation_end)])

            if update_text_grid:
                final_text_grids.append(transcription_audiodetails.update_existing_text_grid(
                    text_grid, transcription_type, update_data=translations, update_field='translation', update_boundaries=boundary_ids))
            else:
                final_text_grids.append(
                    translations[transcription_type]['translation'])

            logger.debug('Final Text Grid %s', final_text_grids)

    return final_text_grids, model_details, input_data, all_translated_data


def get_input_data_for_translation(current_text_grid, source_script, boundary_ids=['*']):
    input_data = {}
    for boundary_id, boundary_content in current_text_grid.items():
        if '*' in boundary_ids or boundary_id in boundary_ids:
            source_data = boundary_content['transcription'][source_script]
            input_data[boundary_id] = source_data.replace('#', ' ')

    return input_data
