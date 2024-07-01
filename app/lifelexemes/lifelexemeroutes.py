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
    getprojectowner,
    getcurrentuserprojects,
    getuserprojectinfo
)
from app import mongo
import os

lifelexemes = Blueprint('lifelexemes', __name__,
                       template_folder='templates', static_folder='static')

basedir = os.path.abspath(os.path.dirname(__file__))

# enter new lexeme route
# display form for new lexeme entry for current project
@lifelexemes.route('/enternewlexeme', methods=['GET', 'POST'])
@login_required
def enternewlexeme():
    projects, userprojects, projectsform = getdbcollections.getdbcollections(mongo,
                                                                             'projects',
                                                                             'userprojects',
                                                                             'projectsform')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                            userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    # if method is not 'POST'
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    project_form = projectsform.find_one_or_404({'projectname': activeprojectname,
                                                 'username': projectowner},
                                                {"_id": 0})
    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                          current_username,
                                                          activeprojectname)
    if project_form is not None:
        return render_template('enternewlexeme.html',
                               newData=project_form,
                               data=currentuserprojectsname,
                               shareinfo=shareinfo)
    return render_template('enternewlexeme.html')
