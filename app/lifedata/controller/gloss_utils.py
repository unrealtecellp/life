from app.controller import (
    life_logging
)

from app.lifedata.transcription.controller import (
    transcription_audiodetails
)

from app.lifemodels.controller import (
    predictFromAPI,
    predictFromLocalModels
)

from app.lifedata.controller import (
    translation_utils
)

from app.lifemodels.controller.bhashiniUtils import (
    translate_data,
    get_translation_model
)

from datetime import datetime

logger = life_logging.get_logger()


def save_gloss_of_one_audio_file(transcriptions,
                                 activeprojectname,
                                 current_username,
                                 audio_filename,
                                 translation_model,
                                 gloss_model,
                                 transcription_type,
                                 save_for_user,
                                 hf_token,
                                 audio_details,
                                 accessedOnTime,
                                 get_free_translation=False
                                 ):

    transcription_doc_id = ''

    audio_id = audio_filename.split('_')[0]

    if current_username in audio_details:
        existing_text_grid = [audio_details[current_username]['textGrid']]

        full_model_name = translation_model.get("model_name")

        text_grids, model_details = get_gloss_of_audio_transcription(gloss_model,
                                                                     hf_token,
                                                                     audio_details,
                                                                     existing_text_grid,
                                                                     get_free_translation,
                                                                     translation_model,
                                                                     transcription_type)

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
    return transcription_doc_id


def get_gloss_of_audio_transcription(gloss_model,
                                     hf_token,
                                     audio_details,
                                     existing_text_grids,
                                     get_free_translation=True,
                                     translation_model={},
                                     transcription_type='sentence'):

    logger.debug('Existing Text Grid %s', existing_text_grids)
    model_details = {}
    final_text_grids = []
    translations = {}
    if len(existing_text_grids) > 0:
        for text_grid in existing_text_grids:
            translations[transcription_type] = {'translation': {}}
            current_text_grid = text_grid[transcription_type]
            gloss_model_name = gloss_model['model_name']
            gloss_params = gloss_model['model_params']
            source_script = gloss_params['source_script']
            source_script_code = gloss_params['source_script_code']
            source_lang_code = gloss_params['source_language']

            if get_free_translation:
                text_grids, model_details, input_data = translation_utils.get_translation_of_audio_transcription(translation_model,
                                                                                                                 transcription_type,
                                                                                                                 hf_token,
                                                                                                                 audio_details,
                                                                                                                 [text_grid])
                temp_text_grid = text_grids[0]
            else:
                temp_text_grid = text_grid

            input_data = translation_utils.get_input_data_for_translation(
                current_text_grid, source_script)

            gloss_start = datetime.now()
            gloss = predictFromLocalModels.get_gloss_stanza(
                input_data, source_lang_code)
            gloss_end = datetime.now()
            model_details.update([('gloss_model_name', gloss_model_name), ('gloss_model_params',
                                                                           gloss_params), ('gloss_start', gloss_start), ('gloss_end', gloss_end)])

            final_text_grids.append(
                update_existing_text_grid_with_gloss(temp_text_grid,
                                                     transcription_type,
                                                     model_details,
                                                     glossed_data=gloss,
                                                     source_lang_code=source_lang_code,
                                                     source_script_code=source_script_code,
                                                     source_script_name=source_script))

    return final_text_grids, model_details


def generate_gloss_token_id(start, end, max_len=14):
    per_index_len = int(max_len/2)

    boundary_id_start = transcription_audiodetails.get_boundary_id_from_number(
        start, per_index_len)
    boundary_id_end = transcription_audiodetails.get_boundary_id_from_number(
        end, per_index_len)
    boundary_id = boundary_id_start+boundary_id_end
    return boundary_id


def conll_to_leipzig_gloss(feats, upos='', trans_output='_'):
    if feats == '':
        if trans_output == '_':
            output = upos
        else:
            output = trans_output.lower()
    else:
        output = trans_output.lower()
        all_feats = feats.split('|')
        feat_dict = {}
        for feat in all_feats:
            feat_val_name = feat.split('=')
            feat_name = feat_val_name[0]
            feat_val = feat_val_name[1]
            feat_dict[feat_name] = feat_val

        person_feat = feat_dict.pop('Person', '')
        if person_feat != '':
            output = output+'.'+person_feat.upper()
        number_feat = feat_dict.pop('Number', '')
        if number_feat != '':
            output = output+'.'+number_feat.upper()
        gender_feat = feat_dict.pop('Gender', '')
        if gender_feat != '':
            output = output+'.'+gender_feat.upper()

        for feat_name, feat_val in feat_dict.items():
            output = output + '.' + feat_val.upper()

        output = output.strip('.').strip()

    return output


def update_existing_text_grid_with_gloss(current_text_grid,
                                         transcription_type,
                                         model_details,
                                         glossed_data={},
                                         translate_tokens=True,
                                         translate_token_categs=[
                                             'NOUN', 'VERB', 'ADJ', 'ADV', 'INTJ'],
                                         source_lang_code="",
                                         source_script_code="",
                                         source_script_name=""):
    try:
        logger.debug('Existing textgrid before gloss %s', current_text_grid)
        if translate_tokens:
            target_lang_code = 'en'
            target_script_code = 'Latn'
            model, api_key, end_url, source_script, target_script = get_translation_model(
                source_lang_code, target_lang_code)
        for sent_id, sent_gloss in glossed_data.items():
            sent_gloss_entry = {}
            sent_token_entry = {source_script_name: {}}
            for token_gloss in sent_gloss:
                new_token_gloss = {}
                trans_output = '_'
                text = token_gloss['text']
                upos = token_gloss['upos']
                start_index = str(token_gloss['start_char'])
                end_index = str(token_gloss['end_char'])
                token_id = generate_gloss_token_id(start_index, end_index)

                if translate_tokens and upos in translate_token_categs:
                    if model != '' and target_script_code == target_script and source_script_code == source_script:
                        try:
                            transl = translate_data(
                                text, model, api_key, end_url, source_lang_code, target_lang_code)
                            trans_output = transl["pipelineResponse"][0]["output"][0]["target"]
                            logger.debug('Input %s, Output %s', text, trans_output)
                            model_details.update(
                                [('gloss_translation_model_name', model)])
                        except:
                            logger.exception('')
                            trans_output = "_"
                else:
                    trans_output = "_"
                
                if (trans_output == ''):
                    trans_output = '_'
                feats = token_gloss.get('feats', '')

                leipzig_gloss_feats = conll_to_leipzig_gloss(
                    feats, upos, trans_output)
                
                logger.debug(leipzig_gloss_feats)

                new_token_gloss.update({"gloss": leipzig_gloss_feats})
                new_token_gloss.update(token_gloss)

                sent_gloss_entry[token_id] = new_token_gloss
                sent_token_entry[source_script_name].update({token_id: text})

            current_text_grid[transcription_type][sent_id]['gloss'] = sent_token_entry
            current_text_grid[transcription_type][sent_id]['glossTokenIdInfo'] = sent_gloss_entry
    except:
        logger.exception("")

    logger.debug('Final text grid after gloss %s', current_text_grid)
    return current_text_grid
