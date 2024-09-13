"""Module containing the routes for the downloader part of the LiFE."""

from flask import Blueprint, render_template
from flask import flash, redirect, render_template, url_for, request, json, jsonify, send_file
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash
from app import app, mongo
import os

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

logger = life_logging.get_logger()


lu = Blueprint('lifeuploader', __name__,
               template_folder='templates', static_folder='static')


@lu.route('/uploadtextdata', methods=['GET', 'POST'])
def uploadtextdata():
    userprojects, projectsform, transcriptions = getdbcollections.getdbcollections(
        mongo, 'userprojects', 'projectsform', 'transcriptions')
    current_username = getcurrentusername.getcurrentusername()
    print('USERNAME: ', current_username)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(
        userprojects, current_username, activeprojectname)


@lu.route('/uploadlexicon', methods=['GET', 'POST'])
def uploadlexicon():
    print('Fetching transcription')
    userprojects, projectsform, transcriptions = getdbcollections.getdbcollections(
        mongo, 'userprojects', 'projectsform', 'transcriptions')
    current_username = getcurrentusername.getcurrentusername()
    print('USERNAME: ', current_username)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(
        userprojects, current_username, activeprojectname)


@lu.route('/uploadquestionnaire', methods=['GET', 'POST'])
def uploadquestionnaire():
    print('Fetching transcription')
    userprojects, projectsform, transcriptions = getdbcollections.getdbcollections(
        mongo, 'userprojects', 'projectsform', 'transcriptions')
    current_username = getcurrentusername.getcurrentusername()
    print('USERNAME: ', current_username)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(
        userprojects, current_username, activeprojectname)
