"""Module containing the routes for the models part of the LiFe."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import current_user, login_required, login_user, logout_user
from app.controller import (
    getdbcollections,
    getcurrentusername,
    getactiveprojectname,
    userdetails,
    projectDetails,
    life_logging
)

from app.lifemodels.controller import (
    huggingFaceUtils,
    modelManager,
    modelPrediction
)

from app import mongo
import pandas as pd
import io
from datetime import datetime
import re
import os

logger = life_logging.get_logger()

lifemodels = Blueprint('lifemodels', __name__, template_folder='templates', static_folder='static')

basedir = os.path.abspath(os.path.dirname(__file__))

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
            num_models=0
            token = modelManager.get_hf_tokens(lifeappconfigs, current_username)
            logger.debug('HF Token: %s', token)
            num_models = modelManager.sync_hf_models(models, languages, token, current_username)
            flash_msg = str(num_models) + ' models from HuggingFace Hub successfully synced!'
            flash (flash_msg)
            return redirect(url_for('hfmodelsetup'))
        else:
            flash ('This action is not allowed for you. Please contact an administrator')
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
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
        language_scripts = projectDetails.get_audio_language_scripts(projectsform, activeprojectname)
        logger.debug('Language Scripts: %s', language_scripts)
        featured_authors = modelManager.get_featured_authors(app_config, current_username)
        # models = modelManager.get_model_list(models, languages, featured_authors, language_scripts['language'])
        if request.method == 'POST':
            models = modelManager.get_model_list(models, languages, featured_authors, language_scripts['language'])
        return jsonify({'models': models, 'scripts': language_scripts['scripts']})
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

    model_path = os.path.join('/'.join(basedir.split('/')[:-2]), 'trainedModels')

    logger.debug(basedir)
    logger.debug((model_path))

    model_list.extend(os.listdir(model_path))
    logger.debug(model_list)

    model_type_mapping = {
        "ai4bharat": "albert",
        "distilbert": "distilbert"
    }

    if (request.method == 'POST'):
        try:
            data = dict(request.form.lists())
            logger.debug("Form data %s", data)
            selected_model = data['modelId'][0]
            if ('myModelPlaygroundFileCheckbox' in data):
                input_type = 'file'
                input_data = request.files.to_dict()                
                file_name = input_data['myModelPlaygroundFile'].filename
                logger.debug('%s', file_name)
                input_data = pd.read_csv(io.BytesIO(input_data['myModelPlaygroundFile'].read()),
                                         header=None,
                                         dtype=str)
                input_data = input_data.iloc[:, 0].to_list()
            else:
                input_type = 'text'
                file_name = '.csv'
                input_data = data['myModelPlaygroundTextArea'][0].strip().split('\r\n')
                input_data = [x for x in input_data if x != '']
            input_data = input_data[:50]
            logger.debug('%s, %s, %s, %s', selected_model, input_type, input_data, len(input_data))

            # create file for prediction
            prediction_df = pd.DataFrame(columns=['Text', 'labels'])
            prediction_df['Text'] = input_data
            selected_model_path = os.path.join(model_path, selected_model)
            model_type = model_type_mapping[selected_model.split('_')[-1]]
            prediction_df['labels'] = modelPrediction.model_prediction(model_type,
                                                                       selected_model_path,
                                                                       input_data)

            logger.debug(prediction_df)
            
            timestamp = '_' + re.sub(r'[-: \.]', '', str(datetime.now())) + '_prediction.csv'
            download_prediction_filename = file_name.replace('.csv', timestamp)
            download_prediction_filename_zip = download_prediction_filename.replace('.csv', '.zip')
            logger.debug('%s, %s', download_prediction_filename, download_prediction_filename_zip)
            
            compression_opts = dict(method='zip', archive_name=download_prediction_filename)

            csv_buffer = io.BytesIO()
            prediction_df.to_csv(csv_buffer, 
                                    index=False,
                                    compression=compression_opts)
            csv_buffer.seek(0)

            return send_file(csv_buffer,
                             mimetype='application/zip',
                             download_name=download_prediction_filename_zip,
                             as_attachment=True)
        except Exception as e:
            flash('Wrong file format!')
            logger.exception("")
        return redirect(url_for('lifemodels.models_playground'))

    return render_template("lifemodelsplayground.html",
                           models=model_list)
