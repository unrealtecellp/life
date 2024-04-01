from app.controller import (
    life_logging,
    getcurrentusername,
    updateuserprojects
)
from flask import flash, redirect, url_for
import re

import os
import csv
import json
from pathlib import Path
from app import mongo
import pandas as pd
import timeit
import time
import copy
# import numpy as np

lang_list = [
    {"id": "", "text": ""},
    {"id": "Assamese", "text": "Assamese"},
    {"id": "Awadhi", "text": "Awadhi"},
    {"id": "Bajjika", "text": "Bajjika"},
    {"id": "Bangla", "text": "Bangla"},
    {"id": "Bhojpuri", "text": "Bhojpuri"},
    {"id": "Bodo", "text": "Bodo"},
    {"id": "Braj", "text": "Braj"},
    {"id": "Bundeli", "text": "Bundeli"},
    {"id": "Chokri", "text": "Chokri"},
    {"id": "English", "text": "English"},
    {"id": "Gujarati", "text": "Gujarati"},
    {"id": "Haryanvi", "text": "Haryanvi"},
    {"id": "Hindi", "text": "Hindi"},
    {"id": "Kannada", "text": "Kannada"},
    {"id": "Khortha", "text": "Khortha"},
    {"id": "Konkani", "text": "Konkani"},
    {"id": "KokBorok", "text": "Kok Borok"},
    {"id": "Magahi", "text": "Magahi"},
    {"id": "Maithili", "text": "Maithili"},
    {"id": "Malayalam", "text": "Malayalam"},
    {"id": "Marathi", "text": "Marathi"},
    {"id": "Meitei", "text": "Meitei"},
    {"id": "Nepali", "text": "Nepali"},
    {"id": "Nyishi", "text": "Nyishi"},
    {"id": "Odia", "text": "Odia"},
    {"id": "Punjabi", "text": "Punjabi"},
    {"id": "Santali", "text": "Santali"},
    {"id": "Tamil", "text": "Tamil"},
    {"id": "Telugu", "text": "Telugu"},
    {"id": "Toto", "text": "Toto"}
]

lang_list2 = [
    {"id": "", "text": ""},
    {"id": "Assamese", "text": "Assamese"},
    {"id": "Awadhi", "text": "Awadhi"},
    {"id": "Bajjika", "text": "Bajjika"},
    {"id": "Bangla", "text": "Bangla"},
    {"id": "Bhojpuri", "text": "Bhojpuri"},
    {"id": "Bodo", "text": "Bodo"},
    {"id": "Braj", "text": "Braj"},
    {"id": "Bundeli", "text": "Bundeli"},
    {"id": "Gujarati", "text": "Gujarati"},
    {"id": "Haryanvi", "text": "Haryanvi"},
    {"id": "Hindi", "text": "Hindi"},
    {"id": "Kannada", "text": "Kannada"},
    {"id": "Khortha", "text": "Khortha"},
    {"id": "Konkani", "text": "Konkani"},
    {"id": "Magahi", "text": "Magahi"},
    {"id": "Maithili", "text": "Maithili"},
    {"id": "Malayalam", "text": "Malayalam"},
    {"id": "Marathi", "text": "Marathi"},
    {"id": "Meitei", "text": "Meitei"},
    {"id": "Nepali", "text": "Nepali"},
    {"id": "Odia", "text": "Odia"},
    {"id": "Punjabi", "text": "Punjabi"},
    {"id": "Santali", "text": "Santali"},
    {"id": "Tamil", "text": "Tamil"},
    {"id": "Telugu", "text": "Telugu"},
    {"id": "Sambalpuri", "text": "Sambalpuri"},
    {"id": "Nagamese", "text": "Nagamese"},
    {"id": "Sadri", "text": "Sadri"},
    {"id": "Kannauji", "text": "Kannauji"},
    {"id": "Nagamese", "text": "Nagamese"}
]

lang_list.extend(lang_list2)

mapping = {'Nagamese': 'nag', 'Kannauji': 'bjj', 'Bodo': 'brx',
           'Punjabi': 'pan', 'Konkani': 'gom', 'Khortha': 'mag'}

logger = life_logging.get_logger()


def generate_languages_database(regenerate=False):
    try:
        mongo.db.validate_collection("languages")
        logger.info('language Database found!')
        if regenerate:
            mongo.db.drop_collection("languages")
            langs_collection = mongo.db.languages
            update_all_available_databases(langs_collection)
    except Exception as e:
        logger.info('Creating Languages Database %s', e)
        langs_collection = mongo.db.languages
        update_all_available_databases(langs_collection)


def get_lang_database_path():
    # current_dir = os.getcwd()
    # logger.debug('Current directory %s', current_dir)
    base_dir = Path(os.path.abspath(os.path.dirname(__file__)))
    bp_dir = base_dir.parent.absolute()
    assets_dir = os.path.join(bp_dir, 'assets')
    logger.debug('Assets directory %s', assets_dir)
    return assets_dir


def update_all_available_databases(langs_collection):
    data_info = {}
    # other_data = {}
    lang_databases_path = get_lang_database_path()

    iso_info = get_iso639_info(langs_collection, lang_databases_path)
    # iso_data = iso_info.to_dict(orient="records")

    data_info = get_langtags_info(
        langs_collection, lang_databases_path, iso_info)
    # other_data['langtag'] = langtags_info
    # data_info = merge_iso_with_others(iso_data, other_data)
    logger.debug('Complete entries %s', data_info['bra'])

    data_info = get_glottolog_info(
        langs_collection, lang_databases_path, data_info)
    # other_data.append(glottlog_info)

    logger.debug('Complete entry braj %s', data_info['braj1242'])
    # varieties = data_info['braj1242']['glottologVarieties']
    # for i, variety in enumerate(varieties):
    #     logger.debug('Complete entry braj variety %s, %s, %s',
    #                  i, variety, data_info[variety])

    final_data = list(data_info.values())

    # all_lang_names = []
    # for data_entry in final_data:
    #     lang_name = data_entry['glottologName']
    #     all_lang_names.append(lang_name)
    # logger.debug('All lang names %s, %s',
    #              all_lang_names[:20], len(all_lang_names))

    # for entry in lang_list:
    #     current_lang_name = entry['text'].strip()
    #     # logger.debug('testing for %s', current_lang_name)
    #     if current_lang_name in all_lang_names:
    #         pass
    #         # logger.debug ('Lang name found %s, %s', current_lang_name, entry)
    #     else:
    #         logger.debug('Lang name not found %s, %s',
    #                      current_lang_name, entry)

    langs_collection.insert_many(final_data)


def update_original_lang_entry_with_variety_name(iso_code, key="glottologVarieties"):
    pass


def merge_iso_with_others(iso_data, other_data):
    merged_entries = []
    for entry in iso_data:
        # logger.debug('ISO entry %s', entry)
        iso_code = entry['codeISO6393']
        for dbase_type, dbase_data in other_data.items():
            langtag_data = dbase_data.get(iso_code, [])
            merged_entry = {dbase_type: langtag_data}
            merged_entry.update(entry)
            merged_entries.append(merged_entry)
    logger.debug('Merged entry %s, %s', merged_entries[0], merged_entries[-1])
    return merged_entries


# def get_cldf_csv_data(data_path="/home/ritesh/Dropbox/PROJECTS/LiFE/lifetestapp/app/languages/assets/glottolog", fname='languages.csv'):
#     fpath = os.path.join(data_path, fname)
#     overall_start = time.time()
#     start_time = time.time()
#     cldf_df = pd.read_csv(fpath)
#     logger.debug('Reading time %s', (time.time() - start_time))
#     start_time = time.time()
#     cldf_df = cldf_df.fillna('')
#     logger.debug('Fill na time %s', (time.time() - start_time))

#     start_time = time.time()
#     cldf_dict = cldf_df.groupby('ID').apply(lambda x: x.drop(
#         'ID', axis=1).to_dict('records')).to_dict()
#     logger.debug('Group by time %s', (time.time() - start_time))
#     logger.debug('Overall time %s Total records %s',
#                  (time.time() - overall_start), len(cldf_dict))
#     # cldf_dict = cldf_df.groupby('ID')
#     logger.debug('Grouped dict pandas %s', cldf_dict['fuln1247'])
#     return cldf_dict


def get_cldf_csv_data(data_path, fname='languages.csv'):
    cldf_dict = {}
    fpath = os.path.join(data_path, fname)

    with open(fpath) as f_r:
        reader = csv.DictReader(f_r)
        for row in reader:
            cur_id = row['ID']
            if cur_id not in cldf_dict:
                cldf_dict[cur_id] = row
            else:
                cldf_dict[cur_id].append(row)
    logger.debug('Total records processed %s in file %s',
                 len(cldf_dict), fpath)
    return cldf_dict


def get_iso639_info(langs_collection, dirpath):
    iso_data = {}
    fname = 'iso-639-3.tab'
    fpath = os.path.join(dirpath, fname)
    isomap = {
        "Id": "codeISO6393",
        "Part2B": "part2bISO639",
        "Part2T": "part2tISO639",
        "Part1": "part1ISO639",
        "Scope": "scopeISO639",
        "Language_Type": "languageTypeISO639",
        "Ref_Name": "languageNameISO639"
    }
    with open(fpath) as f_r:
        reader = csv.DictReader(f_r, delimiter='\t')
        for row in reader:
            # logger.debug ('Row %s', row)
            lang_id = row['Id']
            iso_vals = {isomap.get(k, k): v for k, v in row.items()}
            iso_vals.pop("Comment", "")
            iso_data[lang_id] = iso_vals

    # lang_pd = pd.read_csv(fpath, sep='\t')
    # lang_pd = lang_pd.drop('Comment', axis=1)
    # lang_pd.columns = ["codeISO6393", "part2bISO639", "part2tISO639",
    #                    "part1ISO639", "scopeISO639", "languageTypeISO639", "languageNameISO639"]
    # lang_pd = lang_pd.fillna('')
    # lang_data = lang_pd.to_dict(orient="records")

    # with open(fpath) as f_r:
    #     lang_data = list(csv.DictReader(f_r, delimiter='\t'))

    # logger.debug("Lang Data ISO %s", lang_data)
    return iso_data

    # langs_collection.get_many(lang_data)


def get_langtags_info(langs_collection, dirpath, iso_data):
    fname = 'langtags.json'
    fpath = os.path.join(dirpath, fname)

    # iso_data = iso_info.to_dict(orient="records")
    # iso_info = pd.DataFrame(iso_data)

    merged_lang_json = {}

    lang_json = json.load(open(fpath))
    lang_json = lang_json[4:]
    logger.debug('JSON langtags %s', lang_json[:2])

    for entry in lang_json:
        if 'iso639_3' in entry:
            iso_code = entry['iso639_3']
        elif 'name' in entry:
            name = entry['name']
            for code, entry in iso_data.items():
                if entry['languageNameISO639'] == name:
                    iso_code = entry['codeISO6393']
            # iso_code = iso_info.loc[iso_info['languageNameISO639']
            #              == name, 'codeISO6393'].iloc[0]
            # # iso_code = iso_info.query(
            #     "languageNameISO639==name")['codeISO6393']
            # logger.debug('Name %s Code %s', name, iso_code)
        else:
            logger.debug('Entry %s', entry)

        iso_entry = iso_data.get(iso_code, {})
        # logger.debug('ISO Entry %s, %s', iso_code, iso_entry)

        if len(iso_entry) == 0:
            iso_entry = get_blank_iso()

        langtag_entry = iso_entry.get('langtag', [])

        # if iso_code not in merged_lang_json:
        #     merged_lang_json[iso_code] = []
        entry.pop('iso639_3', None)
        langtag_entry.append(entry)
        # langtag_entry['langtag'] = langtag_entry
        if iso_code in iso_data:
            iso_data[iso_code]['langtag'] = langtag_entry
        else:
            iso_data[iso_code] = get_blank_iso()
            iso_data[iso_code]["codeISO6393"] = iso_code
            iso_data[iso_code]["languageNameISO639"] = entry["name"]

        # iso_entry[iso_code] = langtag_entry
        # merged_lang_json[iso_code].append(entry)

    # lang_pd = pd.read_json(fpath, orient='records')
    logger.debug('Merged %s %s', iso_code, iso_data[iso_code])
    # pass
    # return merged_lang_json
    return iso_data


def get_wals_info(langs_collection, dirpath):
    pass


def get_autotyp_info(langs_collection, dirpath):
    pass


def get_grambank_info(langs_collection, dirpath):
    pass


def get_blank_iso():
    iso_entry = {
        "codeISO6393": '',
        "part2bISO639": '',
        "part2tISO639": '',
        "part1ISO639": '',
        "scopeISO639": '',
        "languageTypeISO639": '',
        "languageNameISO639": '',
        "glottologLevel": '',
        "glottologID": '',
        "glottologName": '',
        "glottologVarieties": [],
        "glottolog": {},
        "langtag": []
    }
    return iso_entry


def get_glottolog_info(langs_collection, dirpath, iso_info):
    glottolog_data = {}

    data_dir = 'glottolog'
    values_fname = 'values.csv'
    data_path = os.path.join(dirpath, data_dir)
    values_path = os.path.join(data_path, values_fname)

    languages_data = get_cldf_csv_data(data_path)
    codes_data = get_cldf_csv_data(data_path, fname='codes.csv')

    with open(values_path) as f_r:
        reader = csv.DictReader(f_r)
        for row in reader:
            parameter_code = row['Code_ID']
            parameter_details = codes_data.get(parameter_code, {})

            parameter_id = row['Parameter_ID'].strip()
            parameter_value = row['Value'].strip()

            classifications = {}

            if parameter_id == 'level':
                lang_code = row['Language_ID']
                lang_details = languages_data[lang_code]
                lang_name = lang_details['Name']

                if parameter_value == 'family':
                    iso_entry = get_blank_iso()
                else:
                    if parameter_value == 'language':
                        iso_code = languages_data[lang_code]['ISO639P3code']
                    elif parameter_value == 'dialect':
                        language_id = languages_data[lang_code]['Language_ID']
                        iso_code = languages_data[language_id]['ISO639P3code']

                        if language_id in glottolog_data:
                            lang_entry = glottolog_data.get(language_id)
                            if 'glottologVarieties' in lang_entry:
                                glottolog_data[language_id]['glottologVarieties'].append(
                                    lang_code)
                            else:
                                glottolog_data[language_id]['glottologVarieties'] = [
                                    lang_code]
                        elif iso_code in iso_info:
                            lang_entry = iso_info.get(iso_code)
                            if 'glottologVarieties' in lang_entry:
                                iso_info[iso_code]['glottologVarieties'].append(
                                    lang_code)
                            else:
                                iso_info[iso_code]['glottologVarieties'] = [
                                    lang_code]
                        else:
                            lang_entry = get_blank_iso()
                            glottolog_data[language_id]['glottologVarieties'].append(
                                lang_code)

                    iso_entry = iso_info.get(iso_code, get_blank_iso())

                    if len(iso_entry) == 0:
                        iso_entry = get_blank_iso()
                    else:
                        iso_entry = copy.deepcopy(iso_entry)

                iso_entry.update({
                    "glottologLevel": parameter_value,
                    "glottologID": lang_code,
                    "glottologName": lang_name,
                    "glottolog": {
                        "language_details": lang_details
                    }
                })
            elif parameter_id == 'classification':
                parameter_values = parameter_value.split('/')
                classifications = {}
                val_len = len(parameter_values)
                for i, val in enumerate(parameter_values):
                    classifications['Level_'+str(val_len-i)] = val
                    # {
                    #     'Level_0': parameter_values[-1],
                    #     'Level_1': parameter_values[-2],
                    #     'Level_2': parameter_values[-3]
                    # }

            iso_entry["glottolog"].update({
                parameter_id: {
                    'ID': row['ID'],
                    'Parameter_ID': parameter_id,
                    'Value': parameter_value,
                    'Classification': classifications,
                    'Code_ID': parameter_details,
                    'Comment': row['Comment'],
                    'Source': row['Source'],
                    'codeReference': row['codeReference']
                }
            })

            glottolog_data[lang_code] = iso_entry

    return glottolog_data


def get_models_of_language(languages, lang_name, task_name='asr'):
    all_models = []
    model_info = languages.find_one({'$or': [{'codeISO6393': lang_name},
                                            {'part2bISO639': lang_name}, 
                                            {'part2tISO639': lang_name},
                                            {'part1ISO639': lang_name},
                                            {'languageNameISO639': lang_name},
                                            {'glottologName': lang_name}]},
                                            {'models.'+task_name: 1,
                                            'codeISO6393': 1,
                                            'languageNameISO639': 1,
                                            '_id': 0})
    # logger.debug ('Lang name, %s, models %s', lang_name, model_info)
    if not model_info is None:
        all_model_details = model_info.get('models', {})
        task_model_details = all_model_details.get(task_name, [])
        for model_detail in task_model_details:
            current_model_id = model_detail['modelId']
            all_models.append(current_model_id)
        lang_code = model_info.get('codeISO6393', '')
        lang_name = model_info.get('languageNameISO639', '')
    return {lang_code: all_models}, {lang_code: lang_name}


def get_models_of_multiple_languages(languages, lang_names, task_name='automatic-speech-recognition'):
    all_models = {}
    all_langs = {}
    model_infos = languages.find({'codeISO6393': {'$in': lang_names}},
                                 {'models.'+task_name: 1,
                                  'codeISO6393': 1,
                                  'languageNameISO639': 1,
                                  '_id': 0})
    if not model_infos is None:
        for model_info in model_infos:
            all_model_details = model_info.get('models', {})
            task_model_details = all_model_details.get(task_name, [])
            lang_code = model_info.get('codeISO6393', '')
            lang_name = model_info.get('languageNameISO639', '')
            all_langs[lang_code] = lang_name
            for model_detail in task_model_details:
                current_model_id = model_detail['modelId']
                if lang_code in all_models:
                    all_models[lang_code].append(current_model_id)
                else:
                    all_models[lang_code] = [current_model_id]
    return all_models, all_langs


def get_family_of_lang(languages, lang_name):
    family_info = languages.find_one({'$or': [{'codeISO6393': lang_name},
                                              {'part2bISO639': lang_name},
                                              {'part2tISO639': lang_name},
                                              {'part1ISO639': lang_name},
                                              {'languageNameISO639': lang_name},
                                              {'glottologName': lang_name}]},
                                     {'glottolog.language_details.Family_ID': 1,
                                      '_id': 0})
    if not family_info is None:
        lang_family = family_info['glottolog']['language_details']['Family_ID']
    else:
        lang_family = ''
    return lang_family


def get_langs_related_by_family(languages, lang_name):
    all_langs = {}
    lang_family = get_family_of_lang(languages, lang_name)
    langs_info = languages.find({'glottolog.language_details.Family_ID': lang_family},
                                {'codeISO6393': 1, 'languageNameISO639': 1, '_id': 0})
    if not langs_info is None:
        for lang in langs_info:
            all_langs[lang['codeISO6393']] = lang['languageNameISO639']
    return all_langs


def get_countries_of_lang(languages, lang_name):
    country_info = languages.find_one({'$or': [{'codeISO6393': lang_name},
                                               {'part2bISO639': lang_name},
                                               {'part2tISO639': lang_name},
                                               {'part1ISO639': lang_name},
                                               {'languageNameISO639': lang_name},
                                               {'glottologName': lang_name}]},
                                      {'glottolog.language_details.Countries': 1,
                                       '_id': 0})
    if not country_info is None:
        country = country_info['glottolog']['language_details']['Countries']
        country = country.split(';')
    else:
        country = []
    return country


def get_langs_related_by_country(languages, lang_name):
    all_langs = {}
    countries = get_countries_of_lang(languages, lang_name)
    for country in countries:
        langs_info = languages.find({'glottolog.language_details.Countries': {'$regex': country}},
                                    {'codeISO6393': 1, 'languageNameISO639': 1, '_id': 0})
        if not langs_info is None:
            for lang in langs_info:
                all_langs[lang['codeISO6393']] = lang['languageNameISO639']
    return all_langs
