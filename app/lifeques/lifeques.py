from flask import Blueprint, redirect, render_template, url_for, request, flash, send_file, jsonify
from flask_login import login_required

from app import mongo

from app.controller import getdbcollections, getactiveprojectname, getcurrentuserprojects
from app.controller import getprojectowner, getcurrentusername, getactiveprojectform
from app.controller import savenewproject, updateuserprojects, getuserprojectinfo
from app.controller import getprojecttype

from app.lifeques.controller import savenewquestionnaireform, createdummyques, downloadquesformexcel
from app.lifeques.controller import uploadquesdataexcel, getactivequestionnaireid, updatelatestquesid
from app.lifeques.controller import getnewquesid, quesunannotatedfilename, saveques, savequesaudiofiles
from app.lifeques.controller import getderivedfromprojectform, copyquesfromparentproject, questranscriptionaudiodetails
from app.lifeques.controller import getquestionnairestats

import os
from pprint import pprint
import inspect

lifeques = Blueprint('lifeques', __name__, template_folder='templates', static_folder='static')
basedir = os.path.abspath(os.path.dirname(__file__))
print(f"LINE 17: lifeques basedir: {basedir}")

@lifeques.route('/', methods=['GET', 'POST'])
@lifeques.route('/home', methods=['GET', 'POST'])
def home():
    """_summary_

    Returns:
        _type_: _description_
    """
    print('lifeques home')
    
    return render_template("lifequeshome.html")

@lifeques.route('/getprojectslist', methods=['GET', 'POST'])
def getprojectslist():
    """_summary_
    """
    userprojects, = getdbcollections.getdbcollections(mongo, 'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    projectslist = getcurrentuserprojects.getcurrentuserprojects(current_username, userprojects)

    return jsonify(projectslist=projectslist)

@lifeques.route('/newquestionnaireform', methods=['GET', 'POST'])
def newquestionnaireform():
    projects, userprojects, projectsform, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                                            'projects',
                                                                                            'userprojects',
                                                                                            'projectsform',
                                                                                            'questionnaires'
                                                                                            )
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_username, userprojects)

    if request.method =='POST':
        new_ques_form = dict(request.form.lists())
        # pprint(new_ques_form)
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
        #     print("line no: 76, derivefromproject in new_ques_form")
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
            # pprint(derivedfromprojectform)
            all_keys = set(list(derivedfromprojectform.keys()) + list(new_ques_form.keys()))
            # for key, value in derivedfromprojectform.items():
            print(all_keys)
            for key in all_keys:
                if (key in derivedfromprojectform):
                    derivedfromprojectformvalue = derivedfromprojectform[key][1]
                    print(key, derivedfromprojectformvalue)
                    if isinstance(derivedfromprojectformvalue, list):
                        if (key in new_ques_form):
                            derivedfromprojectformvalue.extend(new_ques_form[key])
                        print(key, derivedfromprojectformvalue)
                        if("Transcription" in key): continue
                        if (key == "Language" or key == "Script"):
                            new_ques_form[key] = list(derivedfromprojectformvalue)
                        else:
                            new_ques_form[key] = list(set(derivedfromprojectformvalue))
                    if (key == "Prompt Type"):
                        derivedfromprojectformvalue = list(derivedfromprojectform[key][1].keys())
                        # new_ques_form[key] = derivedfromprojectformvalue
                        if (key in new_ques_form):
                            derivedfromprojectformvalue.extend(new_ques_form[key])
                            new_ques_form[key] = list(set(derivedfromprojectformvalue))
                            # print(new_ques_form[key])
                        if ('Transcription' in derivedfromprojectform):
                            new_ques_form['Transcription'] = derivedfromprojectform['Transcription'][1]
                        if ('Instruction' in derivedfromprojectform):
                            new_ques_form['Instruction'] = derivedfromprojectform['Instruction'][1]
        # print('LINE: 109')
        # pprint(new_ques_form)
        updateuserprojects.updateuserprojects(userprojects,
                                                projectname,
                                                current_username
                                                )
        
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

    return render_template("lifequeshome.html")

@lifeques.route('/questionnaire', methods=['GET', 'POST'])
@login_required
def questionnaire():
    projects, userprojects, projectsform, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                                            'projects',
                                                                                            'userprojects',
                                                                                            'projectsform',
                                                                                            'questionnaires')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)
    
    lastActiveIdDetails = projects.find_one({"projectname": activeprojectname},
                                        {'_id': 0, 'lastActiveId': 1, "questionnaireIds": 1})
    
    if (current_username not in lastActiveIdDetails['lastActiveId']):
        lastActiveId = lastActiveIdDetails['questionnaireIds'][0]
        # print(lastActiveId)
        updatequesid = 'lastActiveId.'+current_username+'.'+activeprojectname
        # print(updatequesid)

        projects.update_one({"projectname": activeprojectname},
            { '$set' : { updatequesid: lastActiveId }})

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
    # print(last_active_ques_id)
    quesdata = questionnaires.find_one({"quesId": last_active_ques_id}, {"_id": 0})
    # print(f"{inspect.currentframe().f_lineno}: {quesprojectform}")
    # print(f"{inspect.currentframe().f_lineno}: {type(quesdata)}")
    # print(f"{inspect.currentframe().f_lineno}: {quesdata}")
    quesprojectform['quesdata'] = quesdata
    # print(f"{inspect.currentframe().f_lineno}: {quesdata}")
    file_path = ''
    # if (quesdata is not None and 'Transcription' in quesdata['prompt']):
    if (quesdata is not None and 'Audio' in quesdata['prompt']):
        # audio_id = quesdata['prompt']['Transcription']['audioId']
        audio_id = quesdata['prompt']['Audio']['fileId']
        if (audio_id != ''):
            file_path = questranscriptionaudiodetails.getquesaudiofilefromfs(mongo,
                                                                            basedir,
                                                                            audio_id,
                                                                            'audioId')
    # print('file_path', type(file_path), file_path)
    quesprojectform['QuesAudioFilePath'] = file_path

    transcription_regions = questranscriptionaudiodetails.getquesaudiotranscriptiondetails(questionnaires, last_active_ques_id)
    # print(type(transcription_regions))
    quesprojectform['transcriptionRegions'] = transcription_regions
    # print(f"{inspect.currentframe().f_lineno}: {quesprojectform}")

    # project_type = getprojecttype.getprojecttype(projects, activeprojectname)
    # print('project_type', project_type)

    total_ques, completed, notcompleted = getquestionnairestats.getquestionnairestats(projects,
                                                                                        questionnaires,
                                                                                        activeprojectname,
                                                                                        'ID',
                                                                                        'idtype')
    quesstats = [total_ques, completed, notcompleted]

    return render_template('questionnaire.html',
                            projectName=activeprojectname,
                            quesprojectform=quesprojectform,
                            data=currentuserprojectsname,
                            quesstats=quesstats,
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
    # print(ques_audio_file)
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
    projects, userprojects, projectsform, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                                            'projects',
                                                                                            'userprojects',
                                                                                            'projectsform',
                                                                                            'questionnaires'
                                                                                            )
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)

    if request.method =='POST':
        ques_data = dict(request.form.lists())
        print('LINE 241: ')
        pprint(ques_data)
        ques_data_file = request.files.to_dict()
        # pprint(ques_data_file)

        last_active_ques_id = getactivequestionnaireid.getactivequestionnaireid(projects,
                                                                                activeprojectname,
                                                                                current_username)
        saveques.saveques(questionnaires, ques_data, last_active_ques_id)

        # load next ques
        latest_ques_id = getnewquesid.getnewquesid(projects,
                                                activeprojectname,
                                                last_active_ques_id,
                                                'next')
        updatelatestquesid.updatelatestquesid(projects,
                                        activeprojectname,
                                        latest_ques_id,
                                        current_username)

    return redirect(url_for("lifeques.questionnaire"))

# uploadquesfiles route
@lifeques.route('/uploadquesfiles', methods=['GET', 'POST'])
@login_required
def uploadquesfiles():
    projects, userprojects, questionnaires = getdbcollections.getdbcollections(mongo,
                                                'projects',
                                                'userprojects',
                                                'questionnaires')
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
        print(new_ques_file)
        print(projects,
                userprojects,
                questionnaires,
                activeprojectname,
                projectowner,
                basedir,
                new_ques_file,
                current_username)
        quesstate, quesextra = uploadquesdataexcel.queskeymapping(projects,
                                                                    userprojects,
                                                                    questionnaires,
                                                                    activeprojectname,
                                                                    projectowner,
                                                                    basedir,
                                                                    new_ques_file,
                                                                    current_username)

        if (1 <= quesstate <= 4):
            flash(f"{flashmgs[quesstate]} {quesextra}")
            return redirect(url_for('lifeques.questionnaire'))
        elif (6 <= quesstate <= 6):
            flash(f"{flashmgs[quesstate]}")
            return render_template('queskeymapping.html', not_mapped_data=quesextra)

    return redirect(url_for('lifeques.questionnaire'))

# download questionnaire form in excel
@lifeques.route('/downloadformexcel', methods=['GET', 'POST'])
@login_required
def downloadformexcel():
    # print(f"I download questionnaire form.")
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
    print(lastActiveId)
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
    print(lastActiveId)
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
    userprojects, questionnaires = getdbcollections.getdbcollections(mongo, 'userprojects', 'questionnaires')
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
    print(lastActiveId)
    updatequesid = 'lastActiveId.'+current_username+'.'+activeprojectname
    print(updatequesid)

    projects.update_one({"projectname": activeprojectname},
        { '$set' : { updatequesid: lastActiveId }})

    return 'OK'  

