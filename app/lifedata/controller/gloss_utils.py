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
    get_translation_model,
    get_translation_model_from_id
)

from datetime import datetime

import pandas as pd
import os

import stanza
from stanza import DownloadMethod

logger = life_logging.get_logger()

basedir = os.path.abspath(os.path.dirname(__file__))
basedir_parent = '/'.join(basedir.split('/')[:-2])

map_path = os.path.join(
    basedir_parent, 'jsonfiles/leipzig_ud_map.json')

# print('Path', map_path)
ud_leipzig_map = pd.read_json(map_path, dtype=str)

stanza_pipeline_token = {
    'hi': stanza.Pipeline(
        'hi', processors='tokenize', tokenize_no_ssplit=True, download_method=DownloadMethod.REUSE_RESOURCES),
    'en': stanza.Pipeline(
        'en', processors='tokenize', tokenize_no_ssplit=True, download_method=DownloadMethod.REUSE_RESOURCES),
    'ta': stanza.Pipeline(
        'ta', processors='tokenize', tokenize_no_ssplit=True, download_method=DownloadMethod.REUSE_RESOURCES),
    'te': stanza.Pipeline(
        'te', processors='tokenize', tokenize_no_ssplit=True, download_method=DownloadMethod.REUSE_RESOURCES),
    'mr': stanza.Pipeline(
        'mr', processors='tokenize', tokenize_no_ssplit=True, download_method=DownloadMethod.REUSE_RESOURCES)
}


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
                                 get_free_translation=False,
                                 translate_tokens=True,
                                 boundary_ids=['*']
                                 ):

    transcription_doc_id = ''

    audio_id = audio_filename.split('_')[0]

    if current_username in audio_details:
        existing_text_grid = [audio_details[current_username]['textGrid']]

        full_model_name = translation_model.get("model_name")

        text_grids, model_details, glossed_data = get_gloss_of_audio_transcription(gloss_model,
                                                                                   hf_token,
                                                                                   audio_details,
                                                                                   existing_text_grid,
                                                                                   get_free_translation,
                                                                                   translation_model,
                                                                                   transcription_type,
                                                                                   translate_tokens,
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
    return transcription_doc_id, glossed_data


def get_gloss_of_audio_transcription(gloss_model,
                                     hf_token,
                                     audio_details,
                                     existing_text_grids,
                                     get_free_translation=True,
                                     translation_model={},
                                     transcription_type='sentence',
                                     translate_tokens=True,
                                     boundary_ids=['*']):

    lang_script_map = {
        'hi': 'Devanagari',
        'en': 'Latin'
    }

    logger.debug('Existing Text Grid %s', existing_text_grids)
    model_details = {}
    final_text_grids = []
    translations = {}
    all_glossed_data = []
    if len(existing_text_grids) > 0:
        for text_grid in existing_text_grids:
            translations[transcription_type] = {'translation': {}}
            current_text_grid = text_grid[transcription_type]
            gloss_model_name = gloss_model['model_name']
            gloss_params = gloss_model['model_params']
            source_script = gloss_params['source_script']
            source_script_code = gloss_params['source_script_code']
            source_lang_code = gloss_params['source_language']
            source_lang_name = gloss_params['source_language_name']
            gloss_lang_code = gloss_params['gloss_lang_code']

            prepare_for_gloss = False
            if gloss_lang_code == 'en':
                if source_script_code != 'Latn':
                    prepare_for_gloss = True

            if get_free_translation or prepare_for_gloss:
                text_grids, model_details, input_data, _ = translation_utils.get_translation_of_audio_transcription(translation_model,
                                                                                                                    transcription_type,
                                                                                                                    hf_token,
                                                                                                                    audio_details,
                                                                                                                    [text_grid],
                                                                                                                    boundary_ids=boundary_ids)
                temp_text_grid = text_grids[0]
            else:
                temp_text_grid = text_grid
                input_data = translation_utils.get_input_data_for_translation(
                    current_text_grid, source_script, boundary_ids=boundary_ids)

            if prepare_for_gloss:
                target_lang_script = translation_model['model_params']['output_language']
                gloss_input_data = prepare_gloss_input_data(
                    temp_text_grid[transcription_type], input_data, translation_model, source_lang_code, 'en', target_lang_script, boundary_ids=boundary_ids)
            else:
                gloss_input_data = input_data

            gloss_start = datetime.now()
            gloss = predictFromLocalModels.get_gloss_stanza(
                gloss_input_data, gloss_lang_code)
            gloss_end = datetime.now()
            model_details.update([('gloss_model_name', gloss_model_name), ('gloss_model_params',
                                                                           gloss_params), ('gloss_start', gloss_start), ('gloss_end', gloss_end)])

            append_text_grid, glossed_data = update_existing_text_grid_with_gloss(temp_text_grid,
                                                                                  transcription_type,
                                                                                  model_details,
                                                                                  input_data,
                                                                                  translate_tokens=translate_tokens,
                                                                                  translation_model=translation_model,
                                                                                  glossed_data=gloss,
                                                                                  source_lang_name=source_lang_name,
                                                                                  source_lang_code=source_lang_code,
                                                                                  source_script_code=source_script_code,
                                                                                  source_script_name=source_script,
                                                                                  boundary_ids=boundary_ids)
            final_text_grids.append(append_text_grid)
            all_glossed_data.append(glossed_data)

    return final_text_grids, model_details, all_glossed_data


def generate_gloss_token_id(start, end, max_len=14):
    per_index_len = int(max_len/2)

    boundary_id_start = transcription_audiodetails.get_boundary_id_from_number(
        start, per_index_len)
    boundary_id_end = transcription_audiodetails.get_boundary_id_from_number(
        end, per_index_len)
    boundary_id = boundary_id_start+boundary_id_end
    return boundary_id


def get_token_translation(token, model, api_key, end_url, source_lang_code, target_lang_code):
    trans_output = "_"
    if model != '':
        try:
            transl = translate_data(
                token, model, api_key, end_url, source_lang_code, target_lang_code)
            trans_output = transl["pipelineResponse"][0]["output"][0]["target"]
            logger.debug('Input %s, Output %s',
                         token, trans_output)
        except:
            logger.exception('')
            trans_output = "_"
    return trans_output


def prepare_gloss_input_data(temp_text_grid, input_data, translation_model, source_lang_code, target_lang_code, target_lang_script, boundary_ids=['*']):
    gloss_input = {}
    logger.info('Text grid %s', temp_text_grid)
    logger.info('Input data %s', input_data)
    translation_model_id = translation_model.get("model_name")
    model, api_key, end_url = get_translation_model_from_id(
        translation_model_id)

    for boundary_id, boundary_grid in temp_text_grid.items():
        if '*' in boundary_ids or boundary_id in boundary_ids:
            original_data = input_data[boundary_id]
            translated_data = boundary_grid['translation'][target_lang_script]
            translate_data_length = len(translated_data.split(' '))
            original_data_length = len(original_data.split(' '))
            if translate_data_length == original_data_length:
                gloss_input[boundary_id] = translated_data
            else:
                word_translations = ''
                for token in original_data.split(' '):
                    token_trans = get_token_translation(
                        token, model, api_key, end_url, source_lang_code, target_lang_code)
                    token_trans = token_trans.replace(' ', '-')
                    word_translations = word_translations + ' ' + token_trans
                gloss_input[boundary_id] = word_translations.strip()
    return gloss_input


def conll_to_leipzig_gloss(feats, upos='', trans_output='_'):
    if len(feats) == 0 and trans_output == '_':
        # if trans_output == '_':
        #     output = upos
        # else:
        # output = trans_output.lower()
        output = trans_output+'.'+upos
    else:
        output = trans_output.lower()

        if len(feats) > 0:
            all_feats = feats.split('|')
            feat_dict = {}
            for feat in all_feats:
                feat_val_name = feat.split('=')
                feat_name = feat_val_name[0]
                feat_val = feat_val_name[1]
                feat_dict[feat_name] = (feat, feat_val)

            person_feat = feat_dict.pop('Person', '')
            if person_feat != '':
                person_feat_leipzig = ud_leipzig_map[ud_leipzig_map['udFeats']
                                                     == person_feat[0]]['leipzig'].values
                if len(person_feat_leipzig) >= 1:
                    output = output+'.'+person_feat_leipzig[0]
                else:
                    output = output+'.'+person_feat[1]

            number_feat = feat_dict.pop('Number', '')
            if number_feat != '':
                number_feat_leipzig = ud_leipzig_map[ud_leipzig_map['udFeats']
                                                     == number_feat[0]]['leipzig'].values
                if len(number_feat_leipzig) >= 1:
                    output = output+'.'+number_feat_leipzig[0]
                else:
                    output = output+'.'+number_feat[1]
                # output = output+'.'+number_feat.upper()

            gender_feat = feat_dict.pop('Gender', '')
            if gender_feat != '':
                gender_feat_leipzig = ud_leipzig_map[ud_leipzig_map['udFeats']
                                                     == gender_feat[0]]['leipzig'].values
                if len(gender_feat_leipzig) >= 1:
                    output = output+'.'+gender_feat_leipzig[0]
                else:
                    output = output+'.'+gender_feat[1]

                # output = output+'.'+gender_feat.upper()

            for feat_name, feat_val in feat_dict.items():
                feat_leipzig = ud_leipzig_map[ud_leipzig_map['udFeats']
                                              == feat_val[0]]['leipzig'].values
                if len(feat_leipzig) >= 1:
                    output = output+'.'+feat_leipzig[0]
                else:
                    output = output+'.'+feat_val[1]
                # output = output + '.' + feat_val.upper()

        # output = output.strip('_').strip()
        output = output.strip('.').strip()

    return output


def make_stanza_gloss(text, tid, start_index, end_index, lemma="", upos="", xpos="", feats="", head="", deprel=""):
    new_token_gloss = {
        'id': tid,
        'text': text,
        'lemma': lemma,
        'upos': upos,
        'xpos': xpos,
        'feats': feats,
        'head': head,
        'deprel': deprel,
        'start_char': start_index,
        'end_char': end_index,
    }
    return new_token_gloss


def update_existing_text_grid_with_gloss(current_text_grid,
                                         transcription_type,
                                         model_details,
                                         input_data,
                                         glossed_data={},
                                         translate_tokens=True,
                                         translation_model={},
                                         translate_token_categs=[
                                             'NOUN', 'VERB', 'ADJ', 'ADV', 'INTJ'],
                                         source_lang_name="",
                                         source_lang_code="",
                                         source_script_code="",
                                         source_script_name="",
                                         boundary_ids=['*']):
    try:
        logger.debug('Existing textgrid before gloss %s', current_text_grid)
        all_glossed_entries = {}
        if translate_tokens:
            target_lang_code = 'en'
            target_script_code = 'Latn'
            # model, api_key, end_url, source_script, target_script = get_translation_model(
            #     source_lang_code, target_lang_code)
            translation_model_id = translation_model.get("model_name")
            # model, api_key, end_url, source_script, target_script = get_translation_model_from_id(
            #     translation_model_id)
            model, api_key, end_url = get_translation_model_from_id(
                translation_model_id)
        for sent_id, sent_gloss in glossed_data.items():
            sent_gloss_entry = {}
            sent_token_entry = {source_script_name: {}}
            logger.info('Glossed Data: %s\n%s', sent_id, sent_gloss)
            original_sentence = input_data[sent_id]
            logger.info('Original sentence: %s\n%s',
                        sent_id, original_sentence)
            nlp = stanza_pipeline_token.get(source_lang_code, '')
            tokens = nlp(original_sentence)
            tokens = tokens.to_dict()
            if len(tokens) > 0:
                tokens = tokens[0]
            logger.info('Stanza tokens %s\n%s', tokens, len(tokens))
            # logger.info('My tokens %s\n%s', original_sentence.split(),
            #             len(original_sentence.split()))

            for i, token in enumerate(tokens):
                new_token_gloss = {}
                trans_output = '_'

                if i < len(sent_gloss):
                    token_gloss = sent_gloss[i]
                    text = token_gloss['text']
                else:
                    # current_token = token[i]
                    tid = token['id']
                    text = token['text']
                    start_index = str(token['start_char'])
                    end_index = str(token['end_char'])
                    token_gloss = make_stanza_gloss(
                        text, tid, start_index, end_index)

                upos = token_gloss['upos']
                lemma = token_gloss['lemma']
                start_index = str(token_gloss['start_char'])
                end_index = str(token_gloss['end_char'])
                token_id = generate_gloss_token_id(start_index, end_index)

                # if source_lang_code == 'en':
                #     trans_output = ''
                # if translate_tokens and upos in translate_token_categs:
                if translate_tokens and source_lang_code != target_lang_code:
                    # if model != '' and target_script_code == target_script and source_script_code == source_script:
                    if model != '':
                        try:
                            transl = translate_data(
                                lemma, model, api_key, end_url, source_lang_code, target_lang_code)
                            trans_output = transl["pipelineResponse"][0]["output"][0]["target"]
                            logger.debug('Input %s, Output %s',
                                         lemma, trans_output)
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
                new_token_gloss['languages'] = source_lang_name

                sent_gloss_entry[token_id] = new_token_gloss
                sent_token_entry[source_script_name].update({token_id: text})

            current_text_grid[transcription_type][sent_id]['gloss'] = sent_token_entry
            current_text_grid[transcription_type][sent_id]['glossTokenIdInfo'] = sent_gloss_entry
            all_glossed_entries[sent_id] = sent_gloss_entry
    except:
        logger.exception("")

    logger.debug('Final text grid after gloss %s', current_text_grid)
    return current_text_grid, all_glossed_entries
