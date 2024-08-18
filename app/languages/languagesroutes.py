"""Module containing the routes for the downloader part of the LiFE."""

from flask import Blueprint, render_template
from flask import flash, redirect, render_template, url_for, request, json, jsonify, send_file
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash
from app import app, mongo
import os
from flask import (flash, json, jsonify, redirect, render_template, request,
                   send_file, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from datetime import datetime

from app.controller import (
    audiodetails,
    createdummylexemeentry,
    getactiveprojectform,
    getactiveprojectname,
    getcommentstats,
    getcurrentusername,
    getcurrentuserprojects,
    getdbcollections,
    getprojectowner,
    getprojecttype,
    getuserprojectinfo,
    latex_generator as lg,
    questionnairedetails,
    readJSONFile,
    removeallaccess,
    savenewlexeme,
    savenewproject,
    savenewprojectform,
    savenewsentence,
    speakerDetails,
    unannotatedfilename,
    updateuserprojects,
    userdetails,
    life_logging
)

from app.lifedownloader.controller import (
    downloadTextGrid
)

from app.lifetagsets.controller import (
    tagset_details
)

logger = life_logging.get_logger()


langs = Blueprint('languages', __name__,
                  template_folder='templates', static_folder='static')


@langs.route('/managelanguages', methods=['GET', 'POST'])
@login_required
def managetagset():
    userprojects, userlogin, tagsets = getdbcollections.getdbcollections(
        mongo, 'userprojects', 'userlogin', 'tagsets')
    current_username = getcurrentusername.getcurrentusername()
    print('USERNAME: ', current_username)
    usertype = userdetails.get_user_type(
        userlogin, current_username)
    # activeprojectname = getactiveprojectname.getactiveprojectname(
    #     current_username, userprojects)
    # shareinfo = getuserprojectinfo.getuserprojectinfo(
    #     userprojects, current_username, activeprojectname)

    alltagsetdetails, alldatalengths, allkeys = tagset_details.get_all_tagset_details(
        tagsets, current_username)

    return render_template("manageTagsets.html",
                           tagset_data=alltagsetdetails,
                           usertype=usertype,
                           count=alldatalengths,
                           table_headers=allkeys)
