"""Module containing the routes for the models part of the LiFe."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import current_user, login_required, login_user, logout_user
from app.controller import (
    getdbcollections,
    getcurrentusername,
    getactiveprojectname,
    userdetails,
    projectDetails,
    life_logging,
    getactiveprojectform,
    getprojectowner
)

from app.lifemodels.controller import (
    huggingFaceUtils,
    bhashiniUtils,
    modelManager,
    modelsPlayground
)

from app.lifemodels.controller import modelManager
from app.languages.controller import languageManager

from app import mongo
import pandas as pd
import io
from datetime import datetime
import re
import os
from collections import Counter
import itertools
from pprint import pformat
import json
import openpyxl

logger = life_logging.get_logger()

lifemodels = Blueprint('lifemodels', __name__,
                       template_folder='templates', static_folder='static')

basedir = os.path.abspath(os.path.dirname(__file__))

download_folder_path = os.path.join(basedir, 'model_prediction_download')
if (not os.path.exists(download_folder_path)):
    os.mkdir(download_folder_path)


@lifemodels.route('/', methods=['GET', 'POST'])
@lifemodels.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    """_summary_

    Returns:
        _type_: _description_
    """
    # print('lifemodels home')

    return render_template("lifemodelshome.html")


@lifemodels.route('/syncExistingModels', methods=['GET', 'POST'])
@login_required
def syncExistingModels():
    userlogin, lifeappconfigs, models, languages = getdbcollections.getdbcollections(
        mongo, 'userlogin', 'lifeappconfigs', 'models', 'languages')
    current_username = getcurrentusername.getcurrentusername()
    logger.debug('USERNAME: %s', current_username)
    usertype = userdetails.get_user_type(
        userlogin, current_username)
    logger.debug('User Type: %s', usertype)
    logger.debug('Request method: %s', request.method)
    if request.method == 'POST':
        if 'ADMIN' in usertype:
            num_models = 0
            token = modelManager.get_hf_tokens(
                lifeappconfigs, current_username)
            logger.debug('HF Token: %s', token)
            num_models = modelManager.sync_hf_models(
                models, languages, token, current_username)
            flash_msg = str(num_models) + \
                ' models from HuggingFace Hub successfully synced!'
            flash(flash_msg)
            return redirect(url_for('hfmodelsetup'))
        else:
            flash('This action is not allowed for you. Please contact an administrator')
            return redirect(url_for('hfmodelsetup'))


@lifemodels.route('/getModelList', methods=['GET', 'POST'])
@login_required
def getModelList():
    try:
        userprojects, projectsform, models, languages, app_config = getdbcollections.getdbcollections(
            mongo, 'userprojects', 'projectsform', 'models', 'languages', 'lifeappconfigs')
        current_username = getcurrentusername.getcurrentusername()
        logger.debug('USERNAME: %s', current_username)
        # usertype = userdetails.get_user_type(
        #     userlogin, current_username)
        # logger.debug('User Type: %s', usertype)
        logger.debug('Request method: %s', request.method)
        activeprojectname = getactiveprojectname.getactiveprojectname(
            current_username, userprojects)
        language_scripts = projectDetails.get_all_audio_language_scripts(
            projectsform, activeprojectname)
        logger.debug('Language Scripts: %s', language_scripts)
        featured_authors = modelManager.get_featured_authors(
            app_config, current_username)
        # models = modelManager.get_model_list(models, languages, featured_authors, language_scripts['language'])
        if request.method == 'POST':
            all_langs = language_scripts['languages']
            all_models = []
            for current_lang in all_langs:
                all_models.extend(modelManager.get_model_list(
                    models, languages, featured_authors, current_lang))
        return jsonify({'models': all_models, 'scripts': language_scripts['scripts']})
    except:
        logger.exception("")


@lifemodels.route('/getTranslationModelList', methods=['GET', 'POST'])
@login_required
def getTranslationModelList():
    try:
        userprojects, projectsform, models, languages, app_config, projects = getdbcollections.getdbcollections(
            mongo, 'userprojects', 'projectsform', 'models', 'languages', 'lifeappconfigs', 'projects')
        current_username = getcurrentusername.getcurrentusername()
        logger.debug('USERNAME: %s', current_username)
        # usertype = userdetails.get_user_type(
        #     userlogin, current_username)
        # logger.debug('User Type: %s', usertype)
        logger.debug('Request method: %s', request.method)
        activeprojectname = getactiveprojectname.getactiveprojectname(
            current_username, userprojects)
        # projectowner = getprojectowner.getprojectowner(
        #     projects, activeprojectname)

        language_scripts = projectDetails.get_all_audio_language_scripts(
            projectsform, activeprojectname)

        logger.debug('Language Scripts: %s', language_scripts)
        translation_languages = projectDetails.get_translation_languages(
            projectsform, activeprojectname)
        logger.debug('Target Languages: %s', translation_languages)

        # featured_authors = modelManager.get_featured_authors(
        #     app_config, current_username)
        # models = modelManager.get_model_list(models, languages, featured_authors, language_scripts['language'])

        model_list = []
        if request.method == 'POST':
            current_model_list = {}
            # added_models = []
            # audio_language = getactiveprojectform.getaudiolanguage(
            # projectsform, projectowner, activeprojectname)
            audio_languages = language_scripts['languages']

            for audio_language in audio_languages:
                audio_lang_code = languageManager.get_bcp_language_code(
                    languages, audio_language)
                for translation_language in translation_languages:
                    trans_lang = translation_language.split('-')[0]
                    trans_lang_code = languageManager.get_bcp_language_code(
                        languages, trans_lang)
                    logger.debug('Source lang %s \tTarget Lang %s',
                                 audio_lang_code, trans_lang_code)
                    bhashini_model = bhashiniUtils.get_translation_model(
                        audio_lang_code, trans_lang_code)[0]
                    logger.debug('Bhashini Model %s', bhashini_model)
                    if bhashini_model != '':
                        display_model_name = 'bhashini_' + audio_language + \
                            translation_language+'-'+bhashini_model
                        current_model_list['text'] = display_model_name
                        current_model_list['id'] = 'bhashini_' + bhashini_model
                        model_list.append(current_model_list)
            # models = modelManager.get_model_list(
            #     models, languages, featured_authors, language_scripts['language'])
        return jsonify({'models': model_list, 'scripts': language_scripts['scripts'], 'targetLanguages': translation_languages})
    except:
        logger.exception("")


@lifemodels.route('/models_playground', methods=['GET', 'POST'])
def models_playground():
    """_summary_

    Returns:
        _type_: _description_
    """
    models, languages = getdbcollections.getdbcollections(
        mongo, 'models', 'languages')
    model_list = modelManager.get_model_list(models, languages)
    logger.debug(model_list)

    model_path = os.path.join(
        '/'.join(basedir.split('/')[:-2]), 'trainedModels')

    # logger.debug(basedir)
    # logger.debug((model_path))

    model_list.extend(os.listdir(model_path))
    # logger.debug(model_list)

    return render_template("lifemodelsplayground.html",
                           models=model_list)


@lifemodels.route('/models_playground_prediction', methods=['GET', 'POST'])
def models_playground_prediction():
    """_summary_

    Returns:
        _type_: _description_
    """
    model_path = os.path.join(
        '/'.join(basedir.split('/')[:-2]), 'trainedModels')
    model_type_mapping = {
        "ai4bharat": "albert",
        "distilbert": "distilbert"
    }
    data_info = {}
    selected_model = ''
    uploaded_data_ids = []
    input_data_dict = {}

    if (request.method == 'POST'):
        try:
            data = dict(request.form.lists())
            logger.debug("Form data %s", data)
            selected_models = data['modelId']
            if ('myModelPlaygroundCrawlerCheckbox' in data):
                search_keywords = []
                input_type = 'crawler'
                api_key = data['youtubeAPIKey'][0]
                for link in data['videoschannelId']:
                    if ('youtu.be' in link):
                        uploaded_data_id = link.split('?')[0].split('/')[-1]
                        uploaded_data_ids.append(uploaded_data_id)
                    elif ('youtube.com' in link):
                        uploaded_data_id = link[link.find('?v=')+3:].strip()
                        uploaded_data_ids.append(uploaded_data_id)
                    else:
                        if (len(search_keywords) < 5):
                            search_keywords.append(link)
                logger.debug('uploaded_data_ids: %s', uploaded_data_ids)
                logger.debug('search_keywords: %s', search_keywords)
                if (len(uploaded_data_ids) > 0):
                    uploaded_data_ids, input_data_dict = modelsPlayground.get_crawled_data_by_link(
                        api_key, uploaded_data_ids)
                if (len(search_keywords) > 0):
                    input_data_dict.update(
                        modelsPlayground.get_crawled_data_by_keywords(api_key, search_keywords))
                    uploaded_data_ids.extend(search_keywords)
                logger.debug('uploaded_data_ids: %s', uploaded_data_ids)
                # logger.debug('input_data_dict: %s', input_data_dict)
            elif ('myModelPlaygroundFileCheckbox' in data):
                input_type = 'file'
                uploaded_files = request.files.to_dict(flat=False)
                logger.debug('uploaded_files: %s', uploaded_files)
                uploaded_files = uploaded_files['myModelPlaygroundFile']
                for uploaded_file in uploaded_files[:5]:
                    file_name = uploaded_file.filename
                    logger.debug('%s', file_name)
                    uploaded_data_id = file_name.replace('.csv', '')
                    uploaded_data_ids.append(uploaded_data_id)
                    input_data = pd.read_csv(io.BytesIO(uploaded_file.read()),
                                             header=None,
                                             dtype=str)
                    input_data = input_data.iloc[:, 0].to_list()[:40]
                    # logger.debug('input_data: %s', input_data)
                    input_data_dict[uploaded_data_id] = input_data
            else:
                input_type = 'text'
                uploaded_data_id = 'textAreaData'
                uploaded_data_ids.append(uploaded_data_id)
                input_data = data['myModelPlaygroundTextArea'][0].strip().split(
                    '\r\n')
                input_data = [x for x in input_data if x != '']
                input_data = input_data[:200]
                input_data_dict[uploaded_data_id] = input_data
            for crossover in itertools.product(uploaded_data_ids, selected_models):
                logger.debug("%s", crossover)
                uploaded_data_id = crossover[0]
                selected_model = crossover[1]
                if (not uploaded_data_id in data_info):
                    data_info[uploaded_data_id] = {}
                model_input_data = input_data_dict[uploaded_data_id]
                if (len(model_input_data) > 0):
                    data_info[uploaded_data_id]['Text'] = model_input_data
                    logger.debug('%s, %s, %s', uploaded_data_id,
                                 selected_model, input_type)
                    # logger.debug('%s', model_input_data)
                    logger.debug('%s', len(model_input_data))

                    prediction_df = modelsPlayground.get_prediction(model_path,
                                                                    model_type_mapping,
                                                                    selected_model,
                                                                    model_input_data)
                    # logger.debug(prediction_df)
                    data_info[uploaded_data_id][selected_model] = {}
                    selected_model_prediction = prediction_df[selected_model].to_list(
                    )
                    data_info[uploaded_data_id][selected_model]['prediction'] = selected_model_prediction
                    data_analysis = dict(Counter(selected_model_prediction))
                    data_info[uploaded_data_id][selected_model]['dataAnalysis'] = [
                        {"value": value, "name": key} for key, value in data_analysis.items()]
                else:
                    del data_info[uploaded_data_id]
            # logger.debug('data_info: %s', data_info)
        except Exception as e:
            flash('Wrong file format!')
            logger.exception("")
            return redirect(url_for('lifemodels.models_playground'))

    return jsonify(data_info=data_info)


@lifemodels.route('/models_playground_file_download', methods=['GET', 'POST'])
def models_playground_file_download():
    if (request.method == 'POST'):
        try:
            data = json.loads(request.form['a'])
            logger.debug("data_info %s", data)
            timestamp = re.sub(
                r'[-: \.]', '', str(datetime.now())) + '_prediction.xlsx'
            # timestamp = 'prediction.xlsx'
            output_file_path = os.path.join(download_folder_path, timestamp)
            if (os.path.exists(output_file_path)):
                os.remove(output_file_path)
            prediction_df = pd.DataFrame(columns=[])
            with pd.ExcelWriter(output_file_path, engine="openpyxl") as writer:
                prediction_df.to_excel(
                    writer, header=True, index=False)
            for file_name, file_info in data.items():
                logger.debug(file_name)
                # df_cols = list(file_info.keys())
                # prediction_df = pd.DataFrame(columns=[])
                prediction_df['Text'] = file_info['Text']
                for key, value in file_info.items():
                    logger.debug(key)
                    logger.debug(value)
                    if (key == 'Text'):
                        continue
                    else:
                        prediction_df[key] = value['prediction']
                logger.debug(prediction_df)
                with pd.ExcelWriter(output_file_path, engine="openpyxl", mode='a') as writer:
                    prediction_df.to_excel(
                        writer, sheet_name=file_name, header=True, index=False)
                # csv_buffer, download_prediction_filename_zip = modelsPlayground.download_file(prediction_df, file_name)
            workbook = openpyxl.load_workbook(output_file_path)
            Sheet1 = workbook['Sheet1']
            workbook.remove(Sheet1)
            workbook.save(output_file_path)
        except:
            logger.exception("")

    return jsonify(fileName=timestamp)


@lifemodels.route('/file_download/<download_name>', methods=['GET', 'POST'])
def file_download(download_name):
    # download_name = 'prediction.xlsx'
    file_path = os.path.join(download_folder_path, download_name)
    return send_file(file_path,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     download_name=download_name,
                     as_attachment=True)
