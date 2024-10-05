from flask import (
    Blueprint,
    redirect,
    render_template,
    url_for,
    request,
    flash,
    send_file,
    jsonify
)
from flask_login import login_required
from app import mongo
from app.controller import (
    createzip,
    getactiveprojectname,
    getactiveprojectform,
    getcurrentusername,
    getcurrentuserprojects,
    getdbcollections,
    getprojectowner,
    getprojecttype,
    getuserprojectinfo,
    savenewproject,
    updateuserprojects,
    life_logging,
    projectDetails
)
from app.lifeques.controller import (
    downloadquestionnairein,
    savenewquestionnaireform,
    createdummyques,
    downloadquesformexcel,
    uploadquesdataexcel,
    getactivequestionnaireid,
    updatelatestquesid,
    getnewquesid,
    quesunannotatedfilename,
    saveques,
    savequesaudiofiles,
    getderivedfromprojectform,
    copyquesfromparentproject,
    questranscriptionaudiodetails,
    getquestionnairestats,
    savequespromptfile,
    getquesfromprompttext,
    create_new_ques,
    ques_details,
)

import os
from pprint import pprint, pformat
import inspect
import json

lifeques = Blueprint('lifeques', __name__,
                     template_folder='templates', static_folder='static')
basedir = os.path.abspath(os.path.dirname(__file__))
lifeques_download_folder_path = os.path.join(basedir, 'lifequesdownload')
if not os.path.exists(lifeques_download_folder_path):
    os.mkdir(lifeques_download_folder_path)
logger = life_logging.get_logger()


@lifeques.route('/', methods=['GET', 'POST'])
@lifeques.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    """_summary_

    Returns:
        _type_: _description_
    """

    return render_template("lifequeshome.html")


@lifeques.route('/getprojectslist', methods=['GET', 'POST'])
@login_required
def getprojectslist():
    """_summary_
    """
    projects, userprojects = getdbcollections.getdbcollections(mongo,
                                                               'projects',
                                                               'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    projects_list = getcurrentuserprojects.getcurrentuserprojects(
        current_username, userprojects)
    ques_projects_list = []
    for project_name in projects_list:
        project_type = getprojecttype.getprojecttype(projects, project_name)
        # filter only questionnaires type project
        if (project_type == 'questionnaires'):
            questionnaireIds = projects.find_one({"projectname": project_name},
                                                 {'_id': 0, "questionnaireIds": 1})['questionnaireIds']
            # filter only project have some data
            if (len(questionnaireIds) != 0):
                ques_projects_list.append(project_name)

    return jsonify(projectslist=ques_projects_list)


@lifeques.route('/newquestionnaireform', methods=['GET', 'POST'])
@login_required
def newquestionnaireform():
    try:
        projects, userprojects, projectsform, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                                                 'projects',
                                                                                                 'userprojects',
                                                                                                 'projectsform',
                                                                                                 'questionnaires'
                                                                                                 )
        current_username = getcurrentusername.getcurrentusername()
        currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(
            current_username, userprojects)

        if request.method == 'POST':
            new_ques_form = dict(request.form.lists())
            logger.debug('New ques form: %s', pformat(new_ques_form))
            projectname = 'Q_'+new_ques_form['projectname'][0]
            about_project = new_ques_form['aboutproject'][0]
            project_type = "questionnaires"
            questionnaireIds = []

            project_name = savenewproject.savenewproject(projects,
                                                         projectname,
                                                         current_username,
                                                         aboutproject=about_project,
                                                         projectType=project_type,
                                                         questionnaireIds=questionnaireIds
                                                         )
            if project_name == '':
                flash(f'Project Name : "{projectname}" already exist!')
                return redirect(url_for('lifeques.home'))

            if ("derivefromproject" in new_ques_form):
                derive_from_project_name = new_ques_form["derivefromproject"][0]
                projects.update_one({"projectname": derive_from_project_name},
                                    {"$addToSet": {
                                        "projectDerivatives": project_name
                                    }})
                projects.update_one({"projectname": project_name},
                                    {"$addToSet": {
                                        "derivedFromProject": derive_from_project_name
                                    }})
                # merge new project form and parent project form
                derivedfromprojectform = getderivedfromprojectform.getderivedfromprojectform(projectsform,
                                                                                             derive_from_project_name)
                all_keys = set(list(derivedfromprojectform.keys()
                                    ) + list(new_ques_form.keys()))
                for key in all_keys:
                    if (key in derivedfromprojectform):
                        derivedfromprojectformvalue = derivedfromprojectform[key][1]
                        if isinstance(derivedfromprojectformvalue, list):
                            if (key in new_ques_form):
                                derivedfromprojectformvalue.extend(
                                    new_ques_form[key])
                            new_ques_form[key] = list(
                                set(derivedfromprojectformvalue))
                        if (key == "Prompt Type"):
                            # derivedfromprojectformvalue = list(derivedfromprojectform[key][1].keys())
                            derivedfromprojectformvalues = dict(
                                derivedfromprojectform[key][1])
                            # new_ques_form[key][1].update(derivedfromprojectformvalues)
                            # new_ques_form[key] = derivedfromprojectformvalue
                            if (key in new_ques_form):
                                new_ques_form[key][1].update(
                                    derivedfromprojectformvalues)
                            else:
                                new_ques_form[key] = [
                                    "prompt", derivedfromprojectformvalues]

                        if (key == "LangScript"):
                            # derivedfromprojectformvalue = list(derivedfromprojectform[key][1].keys())
                            derivedfromprojectformvalues = dict(
                                derivedfromprojectform[key][1])
                            # new_ques_form[key][1].update(derivedfromprojectformvalues)
                            # new_ques_form[key] = derivedfromprojectformvalue
                            if (key in new_ques_form):
                                new_ques_form[key][1].update(
                                    derivedfromprojectformvalues)
                            else:
                                new_ques_form[key] = [
                                    "", derivedfromprojectformvalues]
            updateuserprojects.updateuserprojects(userprojects,
                                                  projectname,
                                                  current_username
                                                  )

            logger.debug('Intermediate New ques form: %s',
                         pformat(new_ques_form))
            save_ques_form = savenewquestionnaireform.savenewquestionnaireform(projectsform,
                                                                               projectname,
                                                                               new_ques_form,
                                                                               current_username
                                                                               )
            createdummyques.createdummyques(questionnaires,
                                            projectname,
                                            save_ques_form,
                                            current_username
                                            )
            if ("derivefromproject" in new_ques_form):
                # copy all the ques from the "derivedfromproject" to "newproject"
                copyquesfromparentproject.copyquesfromparentproject(projects,
                                                                    questionnaires,
                                                                    projectsform,
                                                                    derive_from_project_name,
                                                                    projectname,
                                                                    current_username)

            return redirect(url_for("lifeques.questionnaire"))
    except:
        logger.exception("")

    return render_template("lifequeshome.html")


@lifeques.route('/questionnaire', methods=['GET', 'POST'])
@login_required
def questionnaire():
    try:
        audioWaveform = 0
        projects, userprojects, projectsform, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                                                 'projects',
                                                                                                 'userprojects',
                                                                                                 'projectsform',
                                                                                                 'questionnaires')
        current_username = getcurrentusername.getcurrentusername()
        currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)

        lastActiveIdDetails = projects.find_one({"projectname": activeprojectname},
                                                {'_id': 0, 'lastActiveId': 1, "questionnaireIds": 1})

        if (current_username not in lastActiveIdDetails['lastActiveId']):
            lastActiveId = lastActiveIdDetails['questionnaireIds'][0]
            updatequesid = 'lastActiveId.'+current_username+'.'+activeprojectname
            projects.update_one({"projectname": activeprojectname},
                                {'$set': {updatequesid: lastActiveId}})

        projectowner = getprojectowner.getprojectowner(projects,
                                                       activeprojectname)
        quesprojectform = getactiveprojectform.getactiveprojectform(projectsform,
                                                                    projectowner,
                                                                    activeprojectname)
        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                          current_username,
                                                          activeprojectname)
        last_active_ques_id = getactivequestionnaireid.getactivequestionnaireid(projects,
                                                                                activeprojectname,
                                                                                current_username)
        # logger.debug("last_active_ques_id: %s", last_active_ques_id)
        if (last_active_ques_id != ''):
            ques_delete_flag = ques_details.get_ques_delete_flag(questionnaires,
                                                                 activeprojectname,
                                                                 last_active_ques_id)
            if (ques_delete_flag):
                last_active_ques_id = getnewquesid.getnewquesid(projects,
                                                                activeprojectname,
                                                                last_active_ques_id,
                                                                'next')
                updatelatestquesid.updatelatestquesid(projects,
                                                      activeprojectname,
                                                      last_active_ques_id,
                                                      current_username)
                flash(f"This question seem to be deleted or revoked access by one of the shared user.\
                                Showing you the next question in the queue.")
                return redirect(url_for('lifeques.questionnaire'))
        quesdata = questionnaires.find_one(
            {"quesId": last_active_ques_id}, {"_id": 0})
        # logger.debug("quesdata: %s", pformat(quesdata))
        quesprojectform['quesdata'] = quesdata
        file_path = ''
        # if (quesdata is not None and 'Transcription' in quesdata['prompt']):

        if (quesdata is not None):
            ques_data_prompt = quesdata['prompt']
            if ('content' in ques_data_prompt):
                ques_data_prompt_content = quesdata['prompt']['content']
                # ques_id = quesdata['prompt']['Transcription']['quesId']
                for lang, lang_info in ques_data_prompt_content.items():
                    for prompt_type, prompt_type_info in lang_info.items():
                        # logger.debug('prompt_type: %s, prompt_type_info: %s',
                        #              prompt_type, prompt_type_info)
                        if (prompt_type != 'text'):
                            fileId = prompt_type_info['fileId']
                            if (fileId != ''):
                                file_path, file_name = questranscriptionaudiodetails.getquesfilefromfs(mongo,
                                                                                                       basedir,
                                                                                                       fileId,
                                                                                                       'fileId')
                                # logger.debug('file_path: %s, %s',
                                #              type(file_path),
                                #              file_path)
                                file_path = file_path.replace(
                                    'static/audio/', 'retrieve/')
                                file_path_key = '_'.join(
                                    [lang, prompt_type, 'FilePath'])
                                # logger.debug('file_path_key: %s', file_path_key)
                                quesprojectform[file_path_key] = file_path
                                if ('textGrid' in prompt_type_info and
                                        not audioWaveform):
                                    # logger.debug("prompt_type_info: %s\naudioWaveform: %s",
                                    #              pformat(prompt_type_info),
                                    #              audioWaveform)
                                    quesprojectform['QuesAudioFilePath'] = file_path
                                    transcription_regions = questranscriptionaudiodetails.getquesfiletranscriptiondetails(
                                        questionnaires, last_active_ques_id, lang, prompt_type)
                                    quesprojectform['transcriptionRegions'] = transcription_regions
                                    audioWaveform = 1
        if ('QuesAudioFilePath' not in quesprojectform):
            quesprojectform['QuesAudioFilePath'] = ''
        # logger.debug("quesprojectform: %s", pformat(quesprojectform))
        total_ques, completed, notcompleted = getquestionnairestats.getquestionnairestats(projects,
                                                                                          questionnaires,
                                                                                          activeprojectname,
                                                                                          'ID',
                                                                                          'idtype')
        questats = [total_ques, completed, notcompleted]
        # logger.debug('questats: %s', questats)
    except:
        logger.exception("")

    # logger.debug(quesprojectform)

    return render_template('questionnaire.html',
                           projectName=activeprojectname,
                           quesprojectform=quesprojectform,
                           data=currentuserprojectsname,
                           questats=questats,
                           shareinfo=shareinfo)


@lifeques.route('/questranscriptionaudio', methods=['GET', 'POST'])
@login_required
def questranscriptionaudio():
    projects, userprojects, projectsform, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                                             'projects',
                                                                                             'userprojects',
                                                                                             'projectsform',
                                                                                             'questionnaires'
                                                                                             )
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    projectowner = getprojectowner.getprojectowner(projects,
                                                   activeprojectname)

    ques_audio_file = request.files.to_dict()
    last_active_ques_id = getactivequestionnaireid.getactivequestionnaireid(projects,
                                                                            activeprojectname,
                                                                            current_username)
    ques_audio_file['Transcription Audio'] = ques_audio_file['Prompt Type Audio']
    savequesaudiofiles.savequesaudiofiles(mongo,
                                          projects,
                                          userprojects,
                                          projectsform,
                                          questionnaires,
                                          projectowner,
                                          activeprojectname,
                                          current_username,
                                          last_active_ques_id,
                                          ques_audio_file)

    return redirect(url_for("lifeques.questionnaire"))


@lifeques.route('/savequestionnaire', methods=['GET', 'POST'])
@login_required
def savequestionnaire():
    try:
        projects, userprojects, projectsform, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                                                 'projects',
                                                                                                 'userprojects',
                                                                                                 'projectsform',
                                                                                                 'questionnaires'
                                                                                                 )
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)

        if request.method == 'POST':
            # ques_data = dict(request.form.lists())
            ques_data = json.loads(request.form['a'])
            # logger.debug('ques_data: %s', pformat(ques_data))
            last_active_ques_id = getactivequestionnaireid.getactivequestionnaireid(projects,
                                                                                    activeprojectname,
                                                                                    current_username)
            savedQuestionnaire = saveques.saveques(questionnaires,
                                                   ques_data,
                                                   last_active_ques_id,
                                                   current_username
                                                   )

            # load next ques
            # latest_ques_id = getnewquesid.getnewquesid(projects,
            #                                         activeprojectname,
            #                                         last_active_ques_id,
            #                                         'next')
            # updatelatestquesid.updatelatestquesid(projects,
            #                                 activeprojectname,
            #                                 latest_ques_id,
            #                                 current_username)

        return jsonify(savedQuestionnaire=savedQuestionnaire)
    except:
        logger.exception("")
    # return redirect(url_for("lifeques.questionnaire"))

# uploadquesfiles route


@lifeques.route('/uploadquesfiles', methods=['GET', 'POST'])
@login_required
def uploadquesfiles():
    projects, userprojects, projectsform, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                                             'projects',
                                                                                             'userprojects',
                                                                                             'projectsform',
                                                                                             'questionnaires'
                                                                                             )
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    flashmgs = {
        1: "File should be in 'xlsx' format",
        2: "headword is missing from the file",
        3: "quesId from different project!!!",
        4: "Successfully added new questionnaire",
        5: "",
        6: "create a modal/page where user can give the mapping of the columns"
    }
    if request.method == 'POST':
        new_ques_file = request.files.to_dict()
        questate, quesextra = uploadquesdataexcel.queskeymapping(mongo,
                                                                 projects,
                                                                 userprojects,
                                                                 projectsform,
                                                                 questionnaires,
                                                                 activeprojectname,
                                                                 projectowner,
                                                                 basedir,
                                                                 new_ques_file,
                                                                 current_username)

        if (1 <= questate <= 4):
            flash(f"{flashmgs[questate]} {quesextra}")
            return redirect(url_for('lifeques.questionnaire'))
        elif (6 <= questate <= 6):
            flash(f"{flashmgs[questate]}")
            return render_template('queskeymapping.html', not_mapped_data=quesextra)

    return redirect(url_for('lifeques.questionnaire'))

# download questionnaire form in excel


@lifeques.route('/downloadformexcel', methods=['GET', 'POST'])
@login_required
def downloadformexcel():
    userprojects, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                     'userprojects',
                                                                     'questionnaires')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    downloadquesformexcel.downloadquesformexcel(questionnaires,
                                                basedir,
                                                activeprojectname)

    # return redirect(url_for('lifeques.questionnaire'))
    return send_file('../questionnaireform.zip', as_attachment=True)


@lifeques.route('/loadpreviousques', methods=['GET', 'POST'])
@login_required
def loadpreviousques():
    projects, userprojects = getdbcollections.getdbcollections(mongo,
                                                               'projects',
                                                               'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    # data through ajax
    lastActiveId = request.args.get('data')
    lastActiveId = eval(lastActiveId)
    latest_ques_id = getnewquesid.getnewquesid(projects,
                                               activeprojectname,
                                               lastActiveId,
                                               'previous')
    updatelatestquesid.updatelatestquesid(projects,
                                          activeprojectname,
                                          latest_ques_id,
                                          current_username)

    return jsonify(newQuesId=latest_ques_id)


@lifeques.route('/loadnextques', methods=['GET', 'POST'])
@login_required
def loadnextques():
    projects, userprojects = getdbcollections.getdbcollections(mongo,
                                                               'projects',
                                                               'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    # data through ajax
    lastActiveId = request.args.get('data')
    lastActiveId = eval(lastActiveId)
    latest_ques_id = getnewquesid.getnewquesid(projects,
                                               activeprojectname,
                                               lastActiveId,
                                               'next')
    updatelatestquesid.updatelatestquesid(projects,
                                          activeprojectname,
                                          latest_ques_id,
                                          current_username)

    return jsonify(newQuesId=latest_ques_id)


@lifeques.route('/allunannotated', methods=['GET', 'POST'])
def allunannotated():
    userprojects, questionnaires = getdbcollections.getdbcollections(
        mongo, 'userprojects', 'questionnaires')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)

    annotated, unannotated = quesunannotatedfilename.quesunannotatedfilename(questionnaires,
                                                                             activeprojectname,
                                                                             'ques')

    return jsonify(allanno=annotated, allunanno=unannotated)

# both for unanno and anno


@lifeques.route('/loadunannoques', methods=['GET'])
@login_required
def loadunannotext():
    projects, userprojects, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                               'projects',
                                                                               'userprojects',
                                                                               'questionnaires')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)

    lastActiveId = request.args.get('data')
    lastActiveId = eval(lastActiveId)
    updatequesid = 'lastActiveId.'+current_username+'.'+activeprojectname

    projects.update_one({"projectname": activeprojectname},
                        {'$set': {updatequesid: lastActiveId}})

    return 'OK'


@lifeques.route('/quespromptfile', methods=['GET', 'POST'])
@login_required
def quespromptfile():
    try:
        projects, userprojects, projectsform, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                                                 'projects',
                                                                                                 'userprojects',
                                                                                                 'projectsform',
                                                                                                 'questionnaires'
                                                                                                 )
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        projectowner = getprojectowner.getprojectowner(projects,
                                                       activeprojectname)
        last_active_ques_id = getactivequestionnaireid.getactivequestionnaireid(projects,
                                                                                activeprojectname,
                                                                                current_username)

        if request.method == "POST":
            prompt_file = request.files.to_dict()
            # logger.info('prompt_file: %s, type(prompt_file): %s',prompt_file, type(prompt_file))
        savequespromptfile.savequespromptfile(mongo,
                                              projects,
                                              userprojects,
                                              projectsform,
                                              questionnaires,
                                              projectowner,
                                              activeprojectname,
                                              current_username,
                                              last_active_ques_id,
                                              prompt_file)
    except:
        logger.info('prompt_file: %s, type(prompt_file): %s, prompt file keys: %s',
                    prompt_file, type(prompt_file), prompt_file.keys())
        logger.exception("")

    return redirect(url_for("lifeques.questionnaire"))


@lifeques.route('/downloadquestionnaire', methods=['GET', 'POST'])
@login_required
def downloadquestionnaire():
    userprojects, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                     "userprojects",
                                                                     "questionnaires"
                                                                     )
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    questionnaire_data = request.args.get('data')
    questionnaire_data = eval(questionnaire_data)
    download_format = questionnaire_data['downloadFormat']

    if (download_format == 'karyajson'):
        project_folder_path = downloadquestionnairein.karyajson(mongo,
                                                                basedir,
                                                                questionnaires,
                                                                activeprojectname)
    elif (download_format == 'karyajson2'):
        project_folder_path = downloadquestionnairein.karyajson2(mongo,
                                                                 basedir,
                                                                 questionnaires,
                                                                 activeprojectname)
    elif (download_format == 'xlsx'):
        project_folder_path = downloadquestionnairein.excel(mongo,
                                                            basedir,
                                                            questionnaires,
                                                            activeprojectname)

    zip_file_path = createzip.createzip(project_folder_path, activeprojectname)

    return 'OK'

@lifeques.route('/lifequesdownloadquestionnaire', methods=['GET', 'POST'])
def lifequesdownloadquestionnaire():
    userprojects, = getdbcollections.getdbcollections(mongo,
                                                      "userprojects"
                                                      )
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)

    zip_file_path = os.path.join(
        basedir, 'lifequesdownload', activeprojectname, activeprojectname+'.tgz')

    return send_file(zip_file_path, as_attachment=True)


@lifeques.route('/createnewques', methods=['GET', 'POST'])
def createnewques():
    try:
        projects, userprojects, projectsform, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                                                 'projects',
                                                                                                 'userprojects',
                                                                                                 'projectsform',
                                                                                                 'questionnaires')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        projectowner = getprojectowner.getprojectowner(projects,
                                                       activeprojectname)
        quesprojectform = getactiveprojectform.getactiveprojectform(projectsform,
                                                                    projectowner,
                                                                    activeprojectname)
        quesId, questionnaire_id, save_state = create_new_ques.create_new_ques(questionnaires,
                                                                               activeprojectname,
                                                                               quesprojectform,
                                                                               current_username)
        logger.debug("quesId: %s", quesId)
        if (quesId):
            updatelatestquesid.updatelatestquesid(projects,
                                                  activeprojectname,
                                                  quesId,
                                                  current_username)
            projects.update_one({"projectname": activeprojectname},
                                {
                                "$addToSet": {
                                    "questionnaireIds": quesId
                                }
                                })
    except:
        logger.exception("")

    return jsonify(saveState=save_state)

@lifeques.route('/deleteques', methods=['GET', 'POST'])
@login_required
def deleteques():
    try:
        projects_collection, userprojects, questionnaires_collection = getdbcollections.getdbcollections(mongo,
                                                                                                         'projects',
                                                                                                         'userprojects',
                                                                                                         'questionnaires')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(
            current_username, userprojects)
        logger.debug("%s,%s", current_username, activeprojectname)
        last_active_id = json.loads(request.form['a'])
        logger.info("last active ques id to delete: %s, %s",
                    last_active_id, type(last_active_id))

        # ques_ids = ques_details.get_ques_ids(projects_collection,
        #                                         activeprojectname,
        #                                         current_username,
        #                                         last_active_id)
        ques_details.delete_one_ques_doc(projects_collection,
                                         questionnaires_collection,
                                         activeprojectname,
                                         current_username,
                                         last_active_id,
                                         ques_ids=[])
    except:
        logger.exception("")
    flash("Question deleted successfully")

    return "OK"


@lifeques.route('/quesbrowse', methods=['GET', 'POST'])
@login_required
def quesbrowse():
    try:
        new_data = {}
        projects, projectsform, userprojects, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                                                 'projects',
                                                                                                 'projectsform',
                                                                                                 'userprojects',
                                                                                                 'questionnaires')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        projectowner = getprojectowner.getprojectowner(projects,
                                                       activeprojectname)
        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                          current_username,
                                                          activeprojectname)

        project_shared_with = projectDetails.get_shared_with_users(
            projects, activeprojectname)
        quesprojectform = getactiveprojectform.getactiveprojectform(projectsform,
                                                                    projectowner,
                                                                    activeprojectname)
        # logger.debug(quesprojectform)
        text_prompt_key = list(quesprojectform['Prompt Type'][1].keys())[0]
        # logger.debug(text_prompt_key)
        # project_shared_with.append("latest")
        # speakerids = projects.find_one({"projectname": activeprojectname},
        #                                {"_id": 0, "speakerIds." + current_username: 1})
        # # logger.debug('speakerids: %s', pformat(speakerids))
        # if ("speakerIds" in speakerids and speakerids["speakerIds"]):
        #     speakerids = speakerids["speakerIds"][current_username]
        #     speakerids.append('')
        # else:
        #     speakerids = ['']
        # speakerids = ques_details.combine_speaker_ids(projects,
        #                                               activeprojectname,
        #                                               current_username)
        # speakerids.append('')
        # active_speaker_id = shareinfo['activespeakerId']
        # speaker_ques_ids = ques_details.get_speaker_ques_ids_new(projects,
        #                                                            activeprojectname,
        #                                                            current_username,
        #                                                            active_speaker_id)
        # logger.debug("speaker_ques_ids: %s", pformat(speaker_ques_ids))
        total_records = 0
        ques_data_list = []
        # if (active_speaker_id != ''):
        total_records, ques_data_list = ques_details.get_n_ques(questionnaires,
                                                                activeprojectname,
                                                                text_prompt_key)
        # logger.debug(ques_data_list)
        # else:
        #     ques_data_list = []
        # get ques file src
        new_ques_data_list = ques_data_list
        new_data['currentUsername'] = current_username
        new_data['activeProjectName'] = activeprojectname
        new_data['projectOwner'] = projectowner
        new_data['shareInfo'] = shareinfo
        # new_data['speakerIds'] = speakerids
        new_data['quesData'] = new_ques_data_list
        new_data['quesDataFields'] = ['quesId', 'Q_Id', 'prompt_text']
        new_data['totalRecords'] = total_records
        # new_data['questionnairesBy'] = project_shared_with
    except:
        logger.exception("")

    return render_template('quesbrowse.html',
                           projectName=activeprojectname,
                           newData=new_data)
    #    data=currentuserprojectsname)


@lifeques.route('/updatequesbrowsetable', methods=['GET', 'POST'])
@login_required
def updatequesbrowsetable():
    ques_data_fields = ['quesId', 'Q_Id', 'prompt_text']
    ques_data_list = []
    try:
        # data through ajax
        ques_browse_info = json.loads(request.args.get('a'))
        # logger.debug('ques_browse_info: %s', ques_browse_info)
        projects, projectsform, userprojects, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                                                 'projects',
                                                                                                 'projectsform',
                                                                                                 'userprojects',
                                                                                                 'questionnaires')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        projectowner = getprojectowner.getprojectowner(projects,
                                                       activeprojectname)
        # logger.debug(ques_browse_info['activeSpeakerId'])
        # active_speaker_id = ques_browse_info['activeSpeakerId']
        ques_file_count = ques_browse_info['quesFilesCount']
        ques_browse_action = ques_browse_info['browseActionSelectedOption']
        total_records = 0
        ques_data_list = []
        # speaker_ques_ids = ques_details.get_speaker_ques_ids_new(projects,
        #                                                            activeprojectname,
        #                                                            current_username,
        #                                                            active_speaker_id,
        #                                                            ques_browse_action=ques_browse_action)
        # if (active_speaker_id != ''):

        quesprojectform = getactiveprojectform.getactiveprojectform(projectsform,
                                                                    projectowner,
                                                                    activeprojectname)
        # logger.debug(quesprojectform)
        text_prompt_key = list(quesprojectform['Prompt Type'][1].keys())[0]
        total_records, ques_data_list = ques_details.get_n_ques(questionnaires,
                                                                activeprojectname,
                                                                text_prompt_key,
                                                                # active_speaker_id,
                                                                # speaker_ques_ids,
                                                                start_from=0,
                                                                number_of_ques=ques_file_count,
                                                                ques_delete_flag=ques_browse_action)
        # else:
        #     ques_data_list = []
        # logger.debug('ques_data_list: %s', pformat(ques_data_list))
        # get ques file src

        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                          current_username,
                                                          activeprojectname)
        share_mode = shareinfo['sharemode']
        share_checked = shareinfo['sharechecked']
        download_checked = shareinfo['downloadchecked']
        new_ques_data_list = ques_data_list
    except:
        logger.exception("")

    return jsonify(quesDataFields=ques_data_fields,
                   quesData=new_ques_data_list,
                   shareMode=share_mode,
                   totalRecords=total_records,
                   shareChecked=share_checked,
                   downloadChecked=download_checked)


@lifeques.route('/quesbrowseaction', methods=['GET', 'POST'])
@login_required
def quesbrowseaction():
    try:
        projects_collection, userprojects, questionnaires_collection = getdbcollections.getdbcollections(mongo,
                                                                                                         'projects',
                                                                                                         'userprojects',
                                                                                                         'questionnaires')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(
            current_username, userprojects)
        # logger.debug("%s,%s", current_username, activeprojectname)
        # data from ajax
        data = json.loads(request.args.get('a'))
        # logger.debug('data: %s', pformat(data))
        ques_info = data['quesInfo']
        # logger.debug('ques_info: %s', pformat(ques_info))
        ques_browse_info = data['quesBrowseInfo']
        # logger.debug('ques_browse_info: %s', pformat(ques_browse_info))
        browse_action = ques_browse_info['browseActionSelectedOption']
        # active_speaker_id = ques_browse_info['activeSpeakerId']
        ques_ids_list = list(ques_info.keys())
        # speaker_ques_ids = ques_details.get_speaker_ques_ids_new(projects_collection,
        #                                                            activeprojectname,
        #                                                            current_username,
        #                                                            active_speaker_id,
        #                                                            ques_browse_action=browse_action)
        active_ques_id = getactivequestionnaireid.getactivequestionnaireid(projects_collection,
                                                                           activeprojectname,
                                                                           current_username)
        update_latest_ques_id = 0
        for ques_id in ques_ids_list:
            if (browse_action):
                logger.info("ques id to revoke: %s, %s",
                            ques_id, type(ques_id))
            else:
                logger.info("ques id to delete: %s, %s",
                            ques_id, type(ques_id))
            if (ques_id == active_ques_id):
                update_latest_ques_id = 1
            if (browse_action):
                ques_details.revoke_deleted_ques(projects_collection,
                                                 questionnaires_collection,
                                                 activeprojectname,
                                                 #   active_speaker_id,
                                                 ques_id,
                                                 #   speaker_ques_ids
                                                 )
            else:
                ques_details.delete_one_ques_doc(projects_collection,
                                                 questionnaires_collection,
                                                 activeprojectname,
                                                 current_username,
                                                 ques_id,
                                                 ques_ids=[],
                                                 update_latest_ques_id=update_latest_ques_id)
        if (browse_action):
            flash("Question revoked successfully")
        else:
            flash("Question deleted successfully")
    except:
        logger.exception("")

    return 'OK'


@lifeques.route('/quesbrowsechangepage', methods=['GET', 'POST'])
@login_required
def quesbrowsechangepage():
    ques_data_fields = ['quesId', 'Q_Id', 'prompt_text']
    ques_data_list = []
    try:
        # data through ajax
        ques_browse_info = json.loads(request.args.get('a'))
        # logger.debug('ques_browse_info: %s', pformat(ques_browse_info))
        projects, projectsform, userprojects, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                                                 'projects',
                                                                                                 'projectsform',
                                                                                                 'userprojects',
                                                                                                 'questionnaires')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        projectowner = getprojectowner.getprojectowner(projects,
                                                       activeprojectname)
        # logger.debug(crawler_browse_info['activeSourceId'])
        # active_speaker_id = ques_browse_info['activeSpeakerId']
        # speaker_ques_ids = ques_details.get_speaker_ques_ids_new(projects,
        #                                                            activeprojectname,
        #                                                            current_username,
        #                                                            active_speaker_id)
        ques_count = ques_browse_info['quesFilesCount']
        ques_browse_action = ques_browse_info['browseActionSelectedOption']
        page_id = ques_browse_info['pageId']
        start_from = ((page_id*ques_count)-ques_count)
        number_of_ques = page_id*ques_count
        # logger.debug('pageId: %s, start_from: %s, number_of_ques_data: %s',
        #  page_id, start_from, number_of_ques)
        total_records = 0
        ques_data_list = []
        # if (active_speaker_id != ''):

        quesprojectform = getactiveprojectform.getactiveprojectform(projectsform,
                                                                    projectowner,
                                                                    activeprojectname)
        # logger.debug(quesprojectform)
        text_prompt_key = list(quesprojectform['Prompt Type'][1].keys())[0]
        total_records, ques_data_list = ques_details.get_n_ques(questionnaires,
                                                                activeprojectname,
                                                                text_prompt_key,
                                                                # active_speaker_id,
                                                                # speaker_ques_ids,
                                                                start_from=start_from,
                                                                number_of_ques=number_of_ques,
                                                                ques_delete_flag=ques_browse_action)
        # else:
        # ques_data_list = []
        # logger.debug('ques_data_list: %s', pformat(ques_data_list))
        # get ques file src

        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                          current_username,
                                                          activeprojectname)
        share_mode = shareinfo['sharemode']
        share_checked = shareinfo['sharechecked']
        download_checked = shareinfo['downloadchecked']
        new_ques_data_list = ques_data_list
    except:
        logger.exception("")

    return jsonify(quesDataFields=ques_data_fields,
                   quesData=new_ques_data_list,
                   shareMode=share_mode,
                   totalRecords=total_records,
                   shareChecked=share_checked,
                   activePage=page_id,
                   downloadChecked=download_checked)


@lifeques.route('/quesbrowseview', methods=['GET', 'POST'])
@login_required
def quesbrowseview():
    try:
        route = 'questionnaire'
        projects_collection, userprojects, questionnaires_collection = getdbcollections.getdbcollections(mongo,
                                                                                                         'projects',
                                                                                                         'userprojects',
                                                                                                         'questionnaires')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(
            current_username, userprojects)
        # logger.debug("%s,%s", current_username, activeprojectname)
        # data from ajax
        data = json.loads(request.args.get('a'))
        logger.debug('data: %s', pformat(data))
        ques_info = data['quesInfo']
        # logger.debug('ques_info: %s', pformat(ques_info))
        ques_browse_info = data['quesBrowseInfo']
        # logger.debug('ques_browse_info: %s', pformat(ques_browse_info))
        browse_action = ques_browse_info['browseActionSelectedOption']
        # active_speaker_id = ques_browse_info['activeSpeakerId']
        latest_ques_id = list(ques_info.keys())[0]
        updatelatestquesid.updatelatestquesid(projects_collection,
                                              activeprojectname,
                                              latest_ques_id,
                                              current_username)
    except:
        logger.exception("")

    return jsonify(route=route)


# retrieve files from database
# TODO: User not able to download the data
@lifeques.route('/retrieve/<filename>', methods=['GET'])
@login_required
def retrieve(filename):
    logger.debug('Now in retrieve')
    x = ''
    try:
        userprojects, = getdbcollections.getdbcollections(mongo,
                                                          'userprojects')

        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)

        # share_info = getuserprojectinfo.getuserprojectinfo(userprojects,
        #                                                     current_username,
        #                                                     activeprojectname)
        # if ("downloadchecked" in share_info and
        #     share_info["downloadchecked"] == 'true'):
        # logger.debug("share_info: %s", share_info)
        x = mongo.send_file(filename)
        # logger.debug("mongo send file: %s, %s, %s, %s, %s, %s", x.response, x.status, x.headers, x.mimetype, x.content_type, x.direct_passthrough)
    except:
        logger.exception("")

    return x
