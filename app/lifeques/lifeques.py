import pty
from flask import Blueprint, redirect, render_template, url_for, request, flash
from flask_login import login_required

from app import mongo

from app.controller import getdbcollections, getactiveprojectname, getcurrentuserprojects
from app.controller import getprojectowner, getcurrentusername, getactiveprojectform
from app.controller import savenewproject, updateuserprojects, getuserprojectinfo

from app.lifeques.controller import savenewquestionnaireform, createdummyques

from pprint import pprint

lifeques = Blueprint('lifeques', __name__, template_folder='templates', static_folder='static')

@lifeques.route('/', methods=['GET', 'POST'])
@lifeques.route('/home', methods=['GET', 'POST'])
def home():
    """_summary_

    Returns:
        _type_: _description_
    """
    print('lifeques home')

    return render_template("lifequeshome.html")

@lifeques.route('/newquestionnaireform', methods=['GET', 'POST'])
def newquestionnaireform():
    projects, userprojects, projectsform, questionnaire = getdbcollections.getdbcollections(mongo,
                                                                                            'projects',
                                                                                            'userprojects',
                                                                                            'projectsform',
                                                                                            'questionnaire'
                                                                                            )
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_username, userprojects)

    if request.method =='POST':
        new_ques_form = dict(request.form.lists())
        pprint(new_ques_form)
        projectname = 'Q_'+new_ques_form['projectname'][0]
        about_project = new_ques_form['aboutproject'][0]
        project_type = "questionnaires"


        project_name = savenewproject.savenewproject(projects,
                                        projectname,
                                        current_username,
                                        aboutproject=about_project,
                                        projectType=project_type
                                        )
        if project_name == '':
            flash(f'Project Name : "{projectname}" already exist!')
            return redirect(url_for('lifeques.home'))

        updateuserprojects.updateuserprojects(userprojects,
                                                projectname,
                                                current_username
                                                )

        save_ques_form = savenewquestionnaireform.savenewquestionnaireform(projectsform,
                                                                            projectname,
                                                                            new_ques_form,
                                                                            current_username
                                                                            )
    
        createdummyques.createdummyques(questionnaire,
                                        projectname,
                                        save_ques_form,
                                        current_username
                                        )

        return redirect(url_for("lifeques.questionnaire"))

    return render_template("lifequeshome.html")

@lifeques.route('/questionnaire', methods=['GET', 'POST'])
@login_required
def questionnaire():
    projects, userprojects, projectsform, questionnaire, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                                        'projects',
                                                                                                        'userprojects',
                                                                                                        'projectsform',
                                                                                                        'questionnaire',
                                                                                                        'transcriptions')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)
    projectowner = getprojectowner.getprojectowner(projects,
                                                    activeprojectname)
    quesprojectform = getactiveprojectform.getactiveprojectform(projectsform,
                                                                projectowner,
                                                                activeprojectname)
    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                        current_username,
                                                        activeprojectname)

    # print('current_username', current_username)
    # print('currentuserprojectsname', currentuserprojectsname)
    # print('activeprojectname', activeprojectname)
    # print('projectowner', projectowner)
    # print('quesprojectform', quesprojectform)
    # print('shareinfo', shareinfo)

    return render_template('questionnaire.html',
                            projectName=activeprojectname,
                            quesprojectform=quesprojectform,
                            data=currentuserprojectsname,
                            shareinfo=shareinfo)

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
    if request.method == 'POST':
        new_ques_file = request.files.to_dict()
        print(new_ques_file)

    return redirect(url_for('lifeques.questionnaire'))

# download questionnaire form in excel
@lifeques.route('/downloadformexcel', methods=['GET', 'POST'])
@login_required
def downloadformexcel():
    print(f"I download questionnaire form.")

    return redirect(url_for('lifeques.questionnaire'))