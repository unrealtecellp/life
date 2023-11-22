"""Module containing the routes for the models part of the LiFe."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
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
    modelManager
)

from app import mongo

logger = life_logging.get_logger()

lifemodels = Blueprint('lifemodels', __name__, template_folder='templates', static_folder='static')

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
