# 87bb4a4008392471de988181193f7e6e98e0d195
import glob
import json
import os
import pickle
import re
import shutil
import traceback
from datetime import datetime
from pprint import pprint, pformat
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import ElementTree
from zipfile import ZipFile

import gridfs
import joblib
import pandas as pd
from bson.objectid import ObjectId
from flask import (flash, json, jsonify, redirect, render_template, request,
                   send_file, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from jsondiff import diff
from pylatex import (Document, Foot, Head, LargeText, LineBreak, MediumText,
                     MiniPage, NewPage, PageStyle, Section, Tabularx,
                     TextColor, simple_page_number)
from pylatex.base_classes import Environment
from pylatex.package import Package
from pylatex.utils import NoEscape, bold
from rdflib import RDF, XSD, Graph, Literal, URIRef
from rdflib.namespace import FOAF, RDF, RDFS, SKOS, Namespace
from requests.utils import requote_uri
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from werkzeug.security import generate_password_hash
from werkzeug.urls import url_parse

from app import app, mongo
from app.controller import (audiodetails, createdummylexemeentry,
                            emailController, getactiveprojectform,
                            getactiveprojectname, getcommentstats,
                            getcurrentusername, getcurrentuserprojects,
                            getdbcollections, getprojectowner, getprojecttype,
                            getuserprojectinfo, langscriptutils,
                            lexicondetails, speakerDetails, projectDetails,
                            lifeshare)
from app.controller import latex_generator as lg
from app.controller import (manageAppConfig, questionnairedetails,
                            readJSONFile, removeallaccess, savenewlexeme,
                            savenewproject, savenewprojectform,
                            savenewsentence, unannotatedfilename, updateuserprojects,
                            userdetails, life_logging, processHTMLForm)
from app.forms import RegistrationForm, UserLoginForm
from app.models import UserLogin

from app.languages.controller import languageManager as lman
from app.lifemodels.controller import modelManager as mman

basedir = os.path.abspath(os.path.dirname(__file__))
scriptCodeJSONFilePath = os.path.join(basedir, 'static/json/scriptCode.json')
langScriptJSONFilePath = os.path.join(basedir, 'static/json/langScript.json')
ipatomeeteiFilePath = os.path.join(basedir, 'static/json/ipatomeetei.json')
appConfigPath = os.path.join(basedir, 'jsonfiles/app_config.json')
logger = life_logging.get_logger()

userlogin, = getdbcollections.getdbcollections(
    mongo, 'userlogin')
# ADMIN_USER, SUB_ADMINS = userdetails.get_admin_users(userlogin)
# userprofilelist = userdetails.getuserprofilestructure(userlogin)

# if ADMIN_USER is None:
ADMIN_USER = 'life_admin'

# logger.debug('admin', ADMIN_USER, SUB_ADMINS)
admin_reminder = f'App admin <<{ADMIN_USER}>> user created! Please create new password for this account to login'

# logger.debug(f'{"#"*80}\nBase directory:\n{basedir}\n{"#"*80}')

# home page route


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    userprojects, userlogin, projects = getdbcollections.getdbcollections(
        mongo, 'userprojects', 'userlogin', 'projects')
    current_username = getcurrentusername.getcurrentusername()
    # logger.debug('USERNAME: ', current_username)
    usertype = userdetails.get_user_type(
        userlogin, current_username)
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(
        current_username, userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(
        userprojects, current_username, activeprojectname)
    project_owner = getprojectowner.getprojectowner(
        projects, activeprojectname)

    add_to_share_info = ['downloadchecked', 'sharelatestchecked']
    for value in add_to_share_info:
        if (current_username == project_owner and value not in shareinfo):
            userprojects.update_one({'username': current_username},
                                    {'$set': {
                                        'myproject.'+activeprojectname+'.'+value: 'true'
                                    }})
            shareinfo[value] = 'true'

    project_type = getprojecttype.getprojecttype(projects, activeprojectname)
    # logger.debug('project_type: %s', project_type)
    # logger.debug(shareinfo)
    # logger.debug('activeprojectname', activeprojectname)

    return render_template('home.html',
                           data=currentuserprojectsname,
                           activeprojectname=activeprojectname,
                           shareinfo=shareinfo,
                           project_type=project_type,
                           usertype=usertype)

# Manage app level users


@app.route('/manageusers', methods=['GET', 'POST'])
@login_required
def manageusers():
    userlogin, = getdbcollections.getdbcollections(
        mongo, 'userlogin')
    current_username = getcurrentusername.getcurrentusername()
    # logger.debug('USERNAME: ', current_username)
    usertype = userdetails.get_user_type(
        userlogin, current_username)
    # logger.debug('USERTYPE: ', usertype)
    # logger.debug(ADMIN_USER, SUB_ADMINS)

    if 'ADMIN' in usertype:
        allusers = userdetails.getuserdetails(userlogin)
        userprofilelist = userdetails.getuserprofilestructure(userlogin)
        if 'username' not in userprofilelist:
            userprofilelist.insert(0, 'username')

        return render_template(
            'manageUsers.html',
            allusers=allusers,
            userprofilelist=userprofilelist,
            usertype=usertype
        )


@app.route('/getoneuserdetails', methods=['GET', 'POST'])
@login_required
def getoneuserdetails():
    userlogin, = getdbcollections.getdbcollections(
        mongo, 'userlogin')
    current_username = getcurrentusername.getcurrentusername()
    # logger.debug('USERNAME: ', current_username)
    usertype = userdetails.get_user_type(
        userlogin, current_username)
    # logger.debug('USERTYPE: ', usertype)
    # logger.debug(ADMIN_USER, SUB_ADMINS)

    if 'ADMIN' in usertype:
        required_username = request.args.get('username')
        required_user_details = userdetails.getuserdetails(
            userlogin, required_username)
        required_user_details['username'] = required_username

        # logger.debug(required_user_details)

    return jsonify(userdetails=required_user_details)


@app.route('/updateuserstatus', methods=['GET', 'POST'])
@login_required
def updateuserstatus():
    userlogin, = getdbcollections.getdbcollections(
        mongo, 'userlogin')
    current_username = getcurrentusername.getcurrentusername()
    # logger.debug('USERNAME: ', current_username)
    usertype = userdetails.get_user_type(
        userlogin, current_username)
    # logger.debug('USERTYPE: ', usertype)
    # logger.debug(ADMIN_USER, SUB_ADMINS)

    if 'ADMIN' in usertype:
        current_username = request.args.get('username')
        updateaction = request.args.get('action')
        userstatus = request.args.get('status')
        updated_user_details = userdetails.updateuserstatus(
            userlogin, updateaction, userstatus, current_username)

        # allusers = userdetails.getuserdetails(userlogin)
        # userprofilelist = userdetails.getuserprofilestructure(userlogin)

    # logger.debug('User details updated')
    flash(
        'The account details are successfully updated.')
    return redirect(url_for('manageusers'))

    # return render_template(
    #     'manageUsers.html',
    #     allusers=updated_user_details,
    #     userprofilelist=userprofilelist
    # )

    # logger.debug(required_user_details)

    # # return 'Ok'

    # return redirect(url_for('manageusers'))
    # return redirect(url_for('manageusers'))


# Manage Project-level settings
@app.route('/manageproject', methods=['GET', 'POST'])
@login_required
def manageproject():
    userprojects, userlogin = getdbcollections.getdbcollections(
        mongo, 'userprojects', 'userlogin')
    current_username = getcurrentusername.getcurrentusername()
    # logger.debug('USERNAME: ', current_username)
    usertype = userdetails.get_user_type(
        userlogin, current_username)
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(
        current_username, userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(
        userprojects, current_username, activeprojectname)
    return render_template(
        'manageProject.html',
        data=currentuserprojectsname,
        activeprojectname=activeprojectname,
        shareinfo=shareinfo,
        usertype=usertype
    )

# new project route
# create lexeme entry form for the new project


@app.route('/newproject', methods=['GET', 'POST'])
@login_required
def newproject():
    projects, userprojects, projectsform = getdbcollections.getdbcollections(mongo,
                                                                             'projects',
                                                                             'userprojects',
                                                                             'projectsform')
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                                                            userprojects)
    if request.method == 'POST':
        project_form_data = dict(request.form.lists())
        project_name = project_form_data['projectname'][0].strip()
        project_name = savenewproject.savenewproject(projects,
                                                     project_name,
                                                     current_user.username)
        if project_name == '':
            flash(f'Project Name : {project_name} already exist!')
            return redirect(url_for('newproject'))
        else:
            # logger.debug(project_name)
            updateuserprojects.updateuserprojects(userprojects,
                                                  project_name,
                                                  current_user.username)
            savenewprojectform.savenewprojectform(projectsform,
                                                  project_name,
                                                  project_form_data,
                                                  current_user.username)
            # dummylexemeentry()
            flash(f'Project Name : {project_name} created successfully :)')
            return redirect(url_for('home'))
    return render_template('newproject.html',
                           data=currentuserprojectsname)

# get lexeme from sentences and save them to lexemes collection


def sentence_lexeme_to_lexemes(oneSentenceDetail, oneLexemeDetail):
    for key, value in oneLexemeDetail.items():
        # logger.debug(key, ' : ', value)
        pass


# enter new sentences route
# enter new sentences in the project
@app.route('/enternewsentences', methods=['GET', 'POST'])
@login_required
def enternewsentences():
    project_types = ['recordings', 'validation', 'transcriptions']
    projects, userprojects, projectsform, sentences, transcriptions, speakerdetails = getdbcollections.getdbcollections(mongo,
                                                                                                                        'projects',
                                                                                                                        'userprojects',
                                                                                                                        'projectsform',
                                                                                                                        'sentences',
                                                                                                                        'transcriptions',
                                                                                                                        'speakerdetails')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                            userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                      current_username,
                                                      activeprojectname)
    # logger.debug(shareinfo)

    if activeprojectname == '':
        flash(f"select a project from 'Change Active Project' to work on!")
        return redirect(url_for('home'))

    project_type = getprojecttype.getprojecttype(projects, activeprojectname)
    data_collection, = getdbcollections.getdbcollections(mongo, project_type)
    # logger.debug("data_collection: %s", data_collection)
    if request.method == 'POST':
        newSentencesData = dict(request.form.lists())
        newSentencesFiles = request.files.to_dict()
        savenewsentence.savenewsentence(mongo,
                                        sentences,
                                        current_username,
                                        activeprojectname,
                                        newSentencesData,
                                        newSentencesFiles)

    # if method is not 'POST'
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    activeprojectform = getactiveprojectform.getactiveprojectform(projectsform,
                                                                  projectowner,
                                                                  activeprojectname)
    if activeprojectform is not None:
        try:
            # , audio_file_path, transcription_details
            # activespeakerid = getactivespeakerid.getactivespeakerid(userprojects, current_username)
            activespeakerid = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                    current_username,
                                                                    activeprojectname)['activespeakerId']
            speaker_audio_ids = audiodetails.get_speaker_audio_ids_new(projects,
                                                                       activeprojectname,
                                                                       current_username,
                                                                       activespeakerid)
            # logger.debug("speaker_audio_ids: %s", pformat(speaker_audio_ids))
            total_comments, annotated_comments, remaining_comments = getcommentstats.getcommentstats(projects,
                                                                                                     data_collection,
                                                                                                     activeprojectname,
                                                                                                     activespeakerid,
                                                                                                     speaker_audio_ids,
                                                                                                     'audio')
            commentstats = [total_comments,
                            annotated_comments, remaining_comments]
            # logger.debug("commentstats: %s", commentstats)
            audio_id = audiodetails.getactiveaudioid(projects,
                                                     activeprojectname,
                                                     activespeakerid,
                                                     current_username)
            # logger.debug("audio_id: %s", audio_id)
            if (audio_id != ''):
                audio_delete_flag = audiodetails.get_audio_delete_flag(transcriptions,
                                                                       activeprojectname,
                                                                       audio_id)
                if (audio_delete_flag or
                        audio_id not in speaker_audio_ids):
                    latest_audio_id = audiodetails.getnewaudioid(projects,
                                                                 activeprojectname,
                                                                 audio_id,
                                                                 activespeakerid,
                                                                 speaker_audio_ids,
                                                                 'next')
                    audiodetails.updatelatestaudioid(projects,
                                                     activeprojectname,
                                                     latest_audio_id,
                                                     current_username,
                                                     activespeakerid)
                    flash(f"Your last active audio seem to be deleted or revoked access by one of the shared user.\
                        Showing you the next audio in the list.")
                    return redirect(url_for('enternewsentences'))

            transcription_by = projectDetails.get_active_transcription_by(projects,
                                                                          activeprojectname,
                                                                          current_username,
                                                                          activespeakerid,
                                                                          audio_id)
            transcription_details = audiodetails.getaudiofiletranscription(data_collection,
                                                                           audio_id,
                                                                           transcription_by)

            audio_metadata = audiodetails.getaudiometadata(data_collection,
                                                           audio_id)
            # logger.debug('audio_metadata: %s', pformat(audio_metadata))
            # logger.debug(audio_metadata)
            activeprojectform['audioMetadata'] = audio_metadata['audioMetadata']
            last_updated_by = audiodetails.lastupdatedby(data_collection,
                                                         audio_id)
            activeprojectform['lastUpdatedBy'] = last_updated_by['updatedBy']
            # file_path = audiodetails.getaudiofilefromfs(mongo,
            #                                             basedir,
            #                                             audio_id,
            #                                             'audioId')
            audio_filename = audiodetails.get_audio_filename(data_collection,
                                                             audio_id)
            file_path = url_for('retrieve', filename=audio_filename)
            # logger.debug("audio_filename: %s, file_path: %s", audio_filename, file_path)
            activeprojectform['lastActiveId'] = audio_id
            activeprojectform['transcriptionDetails'] = transcription_details
            # logger.debug(transcription_details)
            activeprojectform['AudioFilePath'] = file_path
            transcription_regions, gloss, pos, boundary_count = audiodetails.getaudiotranscriptiondetails(
                data_collection, audio_id, transcription_by, transcription_details)
            activeprojectform['transcriptionRegions'] = transcription_regions
            # logger.debug(transcription_regions)
            activeprojectform['boundaryCount'] = boundary_count
            if (len(gloss) != 0):
                activeprojectform['glossDetails'] = gloss
            if (len(pos) != 0):
                activeprojectform['posDetails'] = pos
            try:
                # speakerids = projects.find_one({"projectname": activeprojectname},
                #                                {"_id": 0, "speakerIds." +
                #                                    current_username: 1}
                #                                )["speakerIds"][current_username]
                speakerids = audiodetails.combine_speaker_ids(projects,
                                                              activeprojectname,
                                                              current_username)
                added_speaker_ids = audiodetails.addedspeakerids(
                    speakerdetails, activeprojectname)

                transcriptions_by = audiodetails.get_audio_transcriptions_by(
                    projects, transcriptions, activeprojectname, audio_id)
                # logger.debug("transcriptions_by: %s", transcriptions_by)

            except:
                speakerids = ''
                added_speaker_ids = ''
            scriptCode = readJSONFile.readJSONFile(scriptCodeJSONFilePath)
            activeprojectform['scriptCode'] = scriptCode
            langScript = readJSONFile.readJSONFile(langScriptJSONFilePath)
            activeprojectform['langScript'] = langScript
            # ipaToMeetei = readJSONFile.readJSONFile(ipatomeeteiFilePath)
            # activeprojectform['ipaToMeetei'] = ipaToMeetei
            # logger.debug('currentuserprojectsname', currentuserprojectsname)
            # logger.debug('speakerids', speakerids)
            # logger.debug(activeprojectform)
            # logger.debug('activespeakerid: %s\ncommentstats: %s\nshareinfo: %s\ntranscriptions by: %s', activespeakerid, commentstats, shareinfo, transcriptions_by)
            # logger.debug('speaker IDs: %s', speakerids)
            # logger.debug(commentstats)
            return render_template('enternewsentences.html',
                                   projectName=activeprojectname,
                                   newData=activeprojectform,
                                   data=currentuserprojectsname,
                                   speakerids=speakerids,
                                   addedspeakerids=added_speaker_ids,
                                   transcriptionsby=transcriptions_by,
                                   activetranscriptionby=transcription_by,
                                   activespeakerid=activespeakerid,
                                   commentstats=commentstats,
                                   shareinfo=shareinfo)
        except:
            logger.exception("")
            flash('Upload first audio file.')

    return render_template('enternewsentences.html',
                           projectName=activeprojectname,
                           newData=activeprojectform,
                           data=currentuserprojectsname)


@app.route('/savetranscription', methods=['GET', 'POST'])
@login_required
def savetranscription():
    try:
        projects, userprojects, projectsform, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                                 'projects',
                                                                                                 'userprojects',
                                                                                                 'projectsform',
                                                                                                 'transcriptions')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        projectowner = getprojectowner.getprojectowner(
            projects, activeprojectname)
        activeprojectform = getactiveprojectform.getactiveprojectform(projectsform,
                                                                      projectowner,
                                                                      activeprojectname)
        # activespeakerid = getactivespeakerid.getactivespeakerid(userprojects, current_user.username)
        activespeakerid = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                current_username,
                                                                activeprojectname)['activespeakerId']
        # data through ajax
        transcription_data = json.loads(request.form['a'])
        # transcription_data = json.loads(request.args.get('a'))
        transcription_data = dict(transcription_data)
        # logger.debug("transcription_data: %s", pformat(transcription_data))
        lastActiveId = transcription_data['lastActiveId']
        transcription_regions = transcription_data['transcriptionRegions']
        # logger.debug("transcription_regions: %s", pformat(json.loads(transcription_regions)))
        # logger.debug(lastActiveId)
        # logger.debug(transcription_regions)
        speaker_audio_ids = audiodetails.get_speaker_audio_ids_new(projects,
                                                                   activeprojectname,
                                                                   current_username,
                                                                   activespeakerid)
        # logger.debug("speaker_audio_ids: %s", pformat(speaker_audio_ids))
        audio_delete_flag = audiodetails.get_audio_delete_flag(transcriptions,
                                                               activeprojectname,
                                                               lastActiveId)
        if (audio_delete_flag or
                lastActiveId not in speaker_audio_ids):
            latest_audio_id = audiodetails.getnewaudioid(projects,
                                                         activeprojectname,
                                                         lastActiveId,
                                                         activespeakerid,
                                                         speaker_audio_ids,
                                                         'next')
            # logger.debug("latest_audio_id: %s", latest_audio_id)
            if (latest_audio_id):
                audiodetails.updatelatestaudioid(projects,
                                                 activeprojectname,
                                                 latest_audio_id,
                                                 current_username,
                                                 activespeakerid)
            # return redirect(url_for('enternewsentences'))
            return jsonify(savedTranscription=0)

        scriptCode = readJSONFile.readJSONFile(scriptCodeJSONFilePath)
        audiodetails.savetranscription(transcriptions,
                                       activeprojectform,
                                       scriptCode,
                                       current_username,
                                       transcription_regions,
                                       lastActiveId,
                                       activespeakerid)
        return jsonify(savedTranscription=1)
    except:
        logger.exception("")


@app.route('/audiobrowse', methods=['GET', 'POST'])
@login_required
def audiobrowse():
    try:
        new_data = {}
        projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                   'projects',
                                                                                   'userprojects',
                                                                                   'transcriptions')
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
        project_shared_with.append("latest")
        # speakerids = projects.find_one({"projectname": activeprojectname},
        #                                {"_id": 0, "speakerIds." + current_username: 1})
        # # logger.debug('speakerids: %s', pformat(speakerids))
        # if ("speakerIds" in speakerids and speakerids["speakerIds"]):
        #     speakerids = speakerids["speakerIds"][current_username]
        #     speakerids.append('')
        # else:
        #     speakerids = ['']
        speakerids = audiodetails.combine_speaker_ids(projects,
                                                      activeprojectname,
                                                      current_username)
        speakerids.append('')
        active_speaker_id = shareinfo['activespeakerId']
        speaker_audio_ids = audiodetails.get_speaker_audio_ids_new(projects,
                                                                   activeprojectname,
                                                                   current_username,
                                                                   active_speaker_id)
        # logger.debug("speaker_audio_ids: %s", pformat(speaker_audio_ids))
        total_records = 0
        if (active_speaker_id != ''):
            total_records, audio_data_list = audiodetails.get_n_audios(transcriptions,
                                                                       activeprojectname,
                                                                       active_speaker_id,
                                                                       speaker_audio_ids)
        else:
            audio_data_list = []
        # get audio file src
        new_audio_data_list = audio_data_list
        # logger.debug("new_audio_data_list: %s", pformat(new_audio_data_list))
        # new_audio_data_list = []
        # for audio_data in audio_data_list:
        #     new_audio_data = audio_data
        #     audio_filename = audio_data['audioFilename']
        #     # if ("downloadchecked" in shareinfo and
        #     #     shareinfo["downloadchecked"] == 'true'):
        #     # new_audio_data['Audio File'] = url_for('retrieve', filename=audio_filename)
        #     # logger.debug("retrieved audio: %s", new_audio_data['Audio File'])
        #     new_audio_data_list.append(new_audio_data)
        new_data['currentUsername'] = current_username
        new_data['activeProjectName'] = activeprojectname
        new_data['projectOwner'] = projectowner
        new_data['shareInfo'] = shareinfo
        new_data['speakerIds'] = speakerids
        new_data['audioData'] = new_audio_data_list
        new_data['audioDataFields'] = [
            'audioId', 'audioFilename', 'Audio File']
        new_data['totalRecords'] = total_records
        new_data['transcriptionsBy'] = project_shared_with
    except:
        logger.exception("")

    return render_template('audiobrowse.html',
                           projectName=activeprojectname,
                           newData=new_data)
    #    data=currentuserprojectsname)


@app.route('/updateaudiosortingsubcategories', methods=['GET', 'POST'])
@login_required
def updateaudiosortingsubcategories():
    audio_sorting_sub_categories = ''
    audio_data_fields = ['audioId', 'audioFilename', 'Audio File']
    audio_data_list = []
    try:
        projects, userprojects, speakerdetails_collection, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                                              'projects',
                                                                                                              'userprojects',
                                                                                                              'speakerdetails',
                                                                                                              'transcriptions')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        # speakerids = projects.find_one({"projectname": activeprojectname},
        #                                 {"_id": 0, "speakerIds." + current_username: 1})
        # # logger.debug('speakerids: %s', pformat(speakerids))
        # if ("speakerIds" in speakerids and speakerids["speakerIds"]):
        #     speakerids = speakerids["speakerIds"][current_username]
        #     speakerids.append('')
        # else:
        #     speakerids = []
        # data through ajax
        data = json.loads(request.args.get('a'))
        # logger.debug('data: %s', pformat(data))
        audio_browse_info = data['audioBrowseInfo']
        audio_file_count = audio_browse_info['audioFilesCount']
        # logger.debug('audio_browse_info: %s', pformat(audio_browse_info))
        audio_browse_action = audio_browse_info['browseActionSelectedOption']
        selected_audio_sorting_category = data['selectedAudioSortingCategories']
        logger.debug('selected_audio_sorting_category: %s',
                     selected_audio_sorting_category)

        speakerids = audiodetails.combine_speaker_ids(projects,
                                                      activeprojectname,
                                                      current_username)
        speakerids.append('')

        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                          current_username,
                                                          activeprojectname)
        total_records = 0
        share_mode = shareinfo['sharemode']
        share_checked = shareinfo['sharechecked']
        download_checked = shareinfo['downloadchecked']
        if (selected_audio_sorting_category == 'sourcemetainfo'):
            audio_sorting_sub_categories = audiodetails.get_audio_sorting_subcategories(speakerdetails_collection,
                                                                                        activeprojectname,
                                                                                        speakerids,
                                                                                        selected_audio_sorting_category
                                                                                        )
            selected_audio_sorting_sub_categories = ''
        elif (selected_audio_sorting_category == 'lifespeakerid'):
            audio_sorting_sub_categories = speakerids
            active_speaker_id = shareinfo['activespeakerId']
            speaker_audio_ids = audiodetails.get_speaker_audio_ids_new(projects,
                                                                       activeprojectname,
                                                                       current_username,
                                                                       active_speaker_id)
            logger.debug("active_speaker_id: %s", active_speaker_id)
            selected_audio_sorting_sub_categories = active_speaker_id

            if (active_speaker_id != ''):
                total_records, audio_data_list = audiodetails.get_n_audios(transcriptions,
                                                                           activeprojectname,
                                                                           active_speaker_id,
                                                                           speaker_audio_ids,
                                                                           start_from=0,
                                                                           number_of_audios=audio_file_count,
                                                                           audio_delete_flag=audio_browse_action)
        new_audio_data_list = audio_data_list
    except:
        logger.exception("")

    return jsonify(audioSortingSubCategories=audio_sorting_sub_categories,
                   selectedAudioSortingSubCategories=selected_audio_sorting_sub_categories,
                   audioDataFields=audio_data_fields,
                   audioData=new_audio_data_list,
                   shareMode=share_mode,
                   totalRecords=total_records,
                   shareChecked=share_checked,
                   downloadChecked=download_checked)


@app.route('/filteraudiobrowsetable', methods=['GET', 'POST'])
@login_required
def filteraudiobrowsetable():
    audio_data_fields = ['audioId', 'audioFilename', 'Audio File']
    audio_data_list = []
    try:
        projects, userprojects, speakerdetails_collection, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                                              'projects',
                                                                                                              'userprojects',
                                                                                                              'speakerdetails',
                                                                                                              'transcriptions')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        # speakerids = projects.find_one({"projectname": activeprojectname},
        #                                 {"_id": 0, "speakerIds." + current_username: 1})
        # # logger.debug('speakerids: %s', pformat(speakerids))
        # if ("speakerIds" in speakerids and speakerids["speakerIds"]):
        #     speakerids = speakerids["speakerIds"][current_username]
        #     # speakerids.append('')
        # else:
        #     speakerids = []
        # data through ajax
        data = json.loads(request.args.get('a'))
        logger.debug('audio_browse_info: %s', pformat(data))
        audio_browse_info = data['audioBrowseInfo']
        audio_file_count = audio_browse_info['audioFilesCount']
        audio_browse_action = audio_browse_info['browseActionSelectedOption']
        page_id = audio_browse_info['pageId']
        start_from = ((page_id*audio_file_count)-audio_file_count)
        number_of_audios = page_id*audio_file_count
        filter_options = data['selectedFilterOptions']
        total_records = 0
        audio_data_list = []
        speakerids = audiodetails.combine_speaker_ids(projects,
                                                      activeprojectname,
                                                      current_username)
    #     # logger.debug(audio_browse_info['activeSpeakerId'])
    #     active_speaker_id = audio_browse_info['activeSpeakerId']

        filtered_speakers_list = audiodetails.filter_speakers(speakerdetails_collection,
                                                              activeprojectname,
                                                              filter_options=filter_options)
        for speaker in filtered_speakers_list:
            speaker_audio_ids = audiodetails.get_speaker_audio_ids_new(projects,
                                                                       activeprojectname,
                                                                       current_username,
                                                                       speaker,
                                                                       audio_browse_action=audio_browse_action)
            if (speaker in speakerids):
                temp_total_records, temp_audio_data_list = audiodetails.get_n_audios(transcriptions,
                                                                                     activeprojectname,
                                                                                     speaker,
                                                                                     speaker_audio_ids,
                                                                                     start_from=0,
                                                                                     number_of_audios=audio_file_count,
                                                                                     audio_delete_flag=audio_browse_action,
                                                                                     all_data=True)
                logger.debug("temp_audio_data_list count: %s",
                             len(temp_audio_data_list))
                logger.debug("temp_total_records count: %s",
                             temp_total_records)
                audio_data_list.extend(temp_audio_data_list)
                logger.debug("audio_data_list count: %s", len(audio_data_list))
                total_records += temp_total_records
                # if (len(audio_data_list) == audio_file_count):
                #     break
        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                          current_username,
                                                          activeprojectname)
        share_mode = shareinfo['sharemode']
        share_checked = shareinfo['sharechecked']
        download_checked = shareinfo['downloadchecked']
        new_audio_data_list = audio_data_list[start_from:number_of_audios]
        logger.debug("new_audio_data_list count: %s", len(new_audio_data_list))
        logger.debug("total_records count: %s", total_records)
    except:
        logger.exception("")

    return jsonify(audioDataFields=audio_data_fields,
                   audioData=new_audio_data_list,
                   shareMode=share_mode,
                   totalRecords=total_records,
                   shareChecked=share_checked,
                   activePage=page_id,
                   downloadChecked=download_checked)


@app.route('/updateaudiobrowsetable', methods=['GET', 'POST'])
@login_required
def updateaudiobrowsetable():
    audio_data_fields = ['audioId', 'audioFilename', 'Audio File']
    audio_data_list = []
    try:
        # data through ajax
        audio_browse_info = json.loads(request.args.get('a'))
        # logger.debug('audio_browse_info: %s', audio_browse_info)
        projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                   'projects',
                                                                                   'userprojects',
                                                                                   'transcriptions')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        # logger.debug(audio_browse_info['activeSpeakerId'])
        active_speaker_id = audio_browse_info['activeSpeakerId']
        audio_file_count = audio_browse_info['audioFilesCount']
        audio_browse_action = audio_browse_info['browseActionSelectedOption']
        total_records = 0
        speaker_audio_ids = audiodetails.get_speaker_audio_ids_new(projects,
                                                                   activeprojectname,
                                                                   current_username,
                                                                   active_speaker_id,
                                                                   audio_browse_action=audio_browse_action)
        if (active_speaker_id != ''):
            total_records, audio_data_list = audiodetails.get_n_audios(transcriptions,
                                                                       activeprojectname,
                                                                       active_speaker_id,
                                                                       speaker_audio_ids,
                                                                       start_from=0,
                                                                       number_of_audios=audio_file_count,
                                                                       audio_delete_flag=audio_browse_action)
        else:
            audio_data_list = []
        # logger.debug('audio_data_list: %s', pformat(audio_data_list))
        # get audio file src

        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                          current_username,
                                                          activeprojectname)
        share_mode = shareinfo['sharemode']
        share_checked = shareinfo['sharechecked']
        download_checked = shareinfo['downloadchecked']
        new_audio_data_list = audio_data_list
        # new_audio_data_list = []
        # for audio_data in audio_data_list:
        #     new_audio_data = audio_data
        #     audio_filename = audio_data['audioFilename']
        #     # if ("downloadchecked" in shareinfo and
        #     #     shareinfo["downloadchecked"] == 'true'):
        #     # new_audio_data['Audio File'] = url_for('retrieve', filename=audio_filename)
        #     new_audio_data_list.append(new_audio_data)
    except:
        logger.exception("")

    return jsonify(audioDataFields=audio_data_fields,
                   audioData=new_audio_data_list,
                   shareMode=share_mode,
                   totalRecords=total_records,
                   shareChecked=share_checked,
                   downloadChecked=download_checked)


@app.route('/audiobrowseaction', methods=['GET', 'POST'])
@login_required
def audiobrowseaction():
    try:
        projects_collection, userprojects, transcriptions_collection = getdbcollections.getdbcollections(mongo,
                                                                                                         'projects',
                                                                                                         'userprojects',
                                                                                                         'transcriptions')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(
            current_username, userprojects)
        # logger.debug("%s,%s", current_username, activeprojectname)
        # data from ajax
        data = json.loads(request.args.get('a'))
        # logger.debug('data: %s', pformat(data))
        audio_info = data['audioInfo']
        # logger.debug('audio_info: %s', pformat(audio_info))
        audio_browse_info = data['audioBrowseInfo']
        # logger.debug('audio_browse_info: %s', pformat(audio_browse_info))
        browse_action = audio_browse_info['browseActionSelectedOption']
        active_speaker_id = audio_browse_info['activeSpeakerId']
        audio_ids_list = list(audio_info.keys())
        speaker_audio_ids = audiodetails.get_speaker_audio_ids_new(projects_collection,
                                                                   activeprojectname,
                                                                   current_username,
                                                                   active_speaker_id,
                                                                   audio_browse_action=browse_action)
        active_audio_id = audiodetails.getactiveaudioid(projects_collection,
                                                        activeprojectname,
                                                        active_speaker_id,
                                                        current_username)
        update_latest_audio_id = 0
        for audio_id in audio_ids_list:
            if (browse_action):
                logger.info("audio id to revoke: %s, %s",
                            audio_id, type(audio_id))
            else:
                logger.info("audio id to delete: %s, %s",
                            audio_id, type(audio_id))
            if (audio_id == active_audio_id):
                update_latest_audio_id = 1
            if (browse_action):
                audiodetails.revoke_deleted_audio(projects_collection,
                                                  transcriptions_collection,
                                                  activeprojectname,
                                                  active_speaker_id,
                                                  audio_id,
                                                  speaker_audio_ids)
            else:
                audiodetails.delete_one_audio_file(projects_collection,
                                                   transcriptions_collection,
                                                   activeprojectname,
                                                   current_username,
                                                   active_speaker_id,
                                                   audio_id,
                                                   speaker_audio_ids,
                                                   update_latest_audio_id=update_latest_audio_id)
        if (browse_action):
            flash("Audio revoked successfully")
        else:
            flash("Audio deleted successfully")
    except:
        logger.exception("")

    return 'OK'


@app.route('/audiobrowseactionplay', methods=['GET', 'POST'])
@login_required
def audiobrowseactionplay():
    audio_data_fields = ['audioId', 'audioFilename', 'Audio File']
    audio_data_list = []
    try:
        projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                   'projects',
                                                                                   'userprojects',
                                                                                   'transcriptions')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        # logger.debug("%s,%s", current_username, activeprojectname)
        # logger.debug("THe data: %s", pformat(request.form['a']))
        # data from ajax
        if request.method == 'POST':
            data = json.loads(request.form['a'])
            # logger.debug('data: %s', pformat(data))

            # data = json.loads(request.args.get('a'))
            # logger.debug('data: %s', pformat(data))
            data_info = data['audioInfo']
            audio_browse_info = data['audioBrowseInfo']
            audio_filename = list(data_info.values())[0]
            audio_count = audio_browse_info['audioFilesCount']
            page_id = audio_browse_info['pageId']
            start_from = ((page_id*audio_count)-audio_count)
            number_of_audios = page_id*audio_count
            # logger.debug("audio_filename: %s", audio_filename)
            # audio_src = url_for('retrieve', filename=audio_filename)
            audio_src = os.path.join('retrieve', audio_filename)
            # logger.debug(audio_browse_info['activeSpeakerId'])
            active_speaker_id = audio_browse_info['activeSpeakerId']
            audio_browse_action = audio_browse_info['browseActionSelectedOption']
            speaker_audio_ids = audiodetails.get_speaker_audio_ids_new(projects,
                                                                       activeprojectname,
                                                                       current_username,
                                                                       active_speaker_id,
                                                                       audio_browse_action=audio_browse_action)
            # audio_file_count = audio_browse_info['audioFilesCount']
            total_records = 0
            if (active_speaker_id != ''):
                total_records, audio_data_list = audiodetails.get_n_audios(transcriptions,
                                                                           activeprojectname,
                                                                           active_speaker_id,
                                                                           speaker_audio_ids,
                                                                           start_from=start_from,
                                                                           number_of_audios=number_of_audios,
                                                                           audio_delete_flag=audio_browse_action
                                                                           )
            else:
                audio_data_list = []

            shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                              current_username,
                                                              activeprojectname)
            share_mode = shareinfo['sharemode']
            share_checked = shareinfo['sharechecked']
            download_checked = shareinfo['downloadchecked']
            new_audio_data_list = audio_data_list
            return jsonify(
                audioDataFields=audio_data_fields,
                audioData=new_audio_data_list,
                shareMode=share_mode,
                totalRecords=total_records,
                shareChecked=share_checked,
                audioSource=audio_src,
                downloadChecked=download_checked
            )
    except:
        logger.exception("")
        return jsonify(audioSource='')


@app.route('/audiobrowseactionshare', methods=['GET', 'POST'])
@login_required
def audiobrowseactionshare():
    try:
        userprojects, = getdbcollections.getdbcollections(mongo,
                                                          'userprojects')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(
            current_username, userprojects)
        logger.debug("%s,%s", current_username, activeprojectname)
        # data from ajax
        data = json.loads(request.args.get('a'))
        logger.debug('data: %s', pformat(data))
        data_info = data['audioInfo']
        # logger.debug('data_info: %s', pformat(data_info))
        audio_browse_info = data['audioBrowseInfo']
        # logger.debug('audio_browse_info: %s', pformat(audio_browse_info))
        # browse_action = audio_browse_info['browseActionSelectedOption']
        active_source_id = audio_browse_info['activeSpeakerId']
        data_id = list(data_info.keys())[0]
        logger.debug("data_id: %s", data_id)
        return jsonify(commentInfo={})
    except:
        logger.exception("")
        return jsonify(commentInfo={})


@app.route('/audiobrowsechangepage', methods=['GET', 'POST'])
@login_required
def audiobrowsechangepage():
    audio_data_fields = ['audioId', 'audioFilename', 'Audio File']
    audio_data_list = []
    try:
        # data through ajax
        audio_browse_info = json.loads(request.args.get('a'))
        logger.debug('audio_browse_info: %s', pformat(audio_browse_info))
        projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                   'projects',
                                                                                   'userprojects',
                                                                                   'transcriptions')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        # logger.debug(crawler_browse_info['activeSourceId'])
        active_speaker_id = audio_browse_info['activeSpeakerId']
        speaker_audio_ids = audiodetails.get_speaker_audio_ids_new(projects,
                                                                   activeprojectname,
                                                                   current_username,
                                                                   active_speaker_id)
        audio_count = audio_browse_info['audioFilesCount']
        audio_browse_action = audio_browse_info['browseActionSelectedOption']
        page_id = audio_browse_info['pageId']
        start_from = ((page_id*audio_count)-audio_count)
        number_of_audios = page_id*audio_count
        # logger.debug('pageId: %s, start_from: %s, number_of_audio_data: %s',
        #  page_id, start_from, number_of_audios)
        total_records = 0
        if (active_speaker_id != ''):
            total_records, audio_data_list = audiodetails.get_n_audios(transcriptions,
                                                                       activeprojectname,
                                                                       active_speaker_id,
                                                                       speaker_audio_ids,
                                                                       start_from=start_from,
                                                                       number_of_audios=number_of_audios,
                                                                       audio_delete_flag=audio_browse_action)
        else:
            audio_data_list = []
        # logger.debug('audio_data_list: %s', pformat(audio_data_list))
        # get audio file src

        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                          current_username,
                                                          activeprojectname)
        share_mode = shareinfo['sharemode']
        share_checked = shareinfo['sharechecked']
        download_checked = shareinfo['downloadchecked']
        new_audio_data_list = audio_data_list
        # new_audio_data_list = []
        # for audio_data in audio_data_list:
        #     new_audio_data = audio_data
        #     audio_filename = audio_data['audioFilename']
        #     # if ("downloadchecked" in shareinfo and
        #     #     shareinfo["downloadchecked"] == 'true'):
        #     # new_audio_data['Audio File'] = url_for('retrieve', filename=audio_filename)
        #     new_audio_data_list.append(new_audio_data)
    except:
        logger.exception("")

    return jsonify(audioDataFields=audio_data_fields,
                   audioData=new_audio_data_list,
                   shareMode=share_mode,
                   totalRecords=total_records,
                   shareChecked=share_checked,
                   activePage=page_id,
                   downloadChecked=download_checked)

# new automation route
# buttons working for different automation(POS, morph analyser)


@app.route('/automation', methods=['GET', 'POST'])
@login_required
def automation():
    userprojects, = getdbcollections.getdbcollections(mongo, 'userprojects')
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                                                            userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)

    return render_template('automation.html',
                           projectName=activeprojectname,
                           data=currentuserprojectsname)


def naiveBayes(corpus, y, x_test):
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus)

    # example for saving python object as pkl
    joblib.dump(vectorizer, "trainedModels/naiveBayesPOSVectorizer.pkl")
    clf = MultinomialNB()
    clf.fit(X, y)

    # save
    with open('trainedModels/naiveBayesPOSModel.pkl', 'wb') as f:
        pickle.dump(clf, f)


# new automation route
# buttons working for different automation(POS, morph analyser)
@app.route('/predictPOSNaiveBayes', methods=['GET', 'POST'])
@login_required
def predictPOSNaiveBayes():
    userprojects, = getdbcollections.getdbcollections(mongo, 'userprojects')
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                                                            userprojects)
    # data through ajax
    wordList = request.args.get('a').split(',')
    if (len(wordList) != 0):
        try:
            # load model
            with open('trainedModels/naiveBayesPOSModel.pkl', 'rb') as f:
                clf = pickle.load(f)
            # loading pickled vectorizer
            vectorizer = joblib.load("trainedModels/naiveBayesPOSVectorizer.pkl")
            x_test = vectorizer.transform(wordList)
            predictedpos = list(clf.predict(x_test))
            predictedPOS = []
            for word, pos in zip(wordList, predictedpos):
                predictedPOS.append([word, pos])
        except:
            logger.exception("")
            predictedPOS = []
            for word in wordList:
                predictedPOS.append([word, 'Determiner'])

        return jsonify(predictedPOS=predictedPOS)

    return render_template('automation.html',
                           data=currentuserprojectsname)


@app.route('/automatepos', methods=['GET', 'POST'])
@login_required
def automatepos():
    userprojects, sentences = getdbcollections.getdbcollections(mongo,
                                                                'userprojects',
                                                                'sentences')
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                                                            userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)

    sentence = request.args.get('a').split(
        ',')                    # data through ajax
    # create dataframe from the json type data
    posdf = {}
    word = []
    label = []
    for pos in sentences.find({'projectname': activeprojectname, 'sentencedeleteFLAG': 0},
                              {'_id': 0, 'pos': 1}):
        for key, value in pos['pos'].items():
            word.append(key)
            label.append(value)
        posdf['word'] = word
        posdf['label'] = label
    posdf = pd.DataFrame.from_dict(posdf)
    x_test = ['cow']
    naiveBayes(word, label, x_test)

    return render_template('automation.html',
                           data=currentuserprojectsname)

# create an empty lexeme entry in the lexemes collection whenever new project is created
# so that if user download the excel of lexeme form directly after creating the poject
# there are columns in the excel


def dummylexemeentry():
    projects, userprojects, projectsform, lexemes = getdbcollections.getdbcollections(mongo,
                                                                                      'projects',
                                                                                      'userprojects',
                                                                                      'projectsform',
                                                                                      'lexemes')
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)

    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    activeprojectform = getactiveprojectform.getactiveprojectform(projectsform,
                                                                  projectowner,
                                                                  activeprojectname)
    scriptCode = readJSONFile.readJSONFile(scriptCodeJSONFilePath)
    langScript = readJSONFile.readJSONFile(langScriptJSONFilePath)
    createdummylexemeentry.createdummylexemeentry(projects,
                                                  lexemes,
                                                  activeprojectform,
                                                  scriptCode,
                                                  langScript,
                                                  current_user.username)

# dictionary view route
# display lexeme entries for current project in a table


@app.route('/dictionaryview', methods=['GET', 'POST'])
@login_required
def dictionaryview():
    projects, userprojects, lexemes = getdbcollections.getdbcollections(mongo,
                                                                        'projects',
                                                                        'userprojects',
                                                                        'lexemes')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                            userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    scriptCode = readJSONFile.readJSONFile(scriptCodeJSONFilePath)
    langScript = readJSONFile.readJSONFile(langScriptJSONFilePath)
    if request.method == 'POST':
        new_lexeme_data = dict(request.form.lists())
        new_lexeme_files = request.files.to_dict()
        savenewlexeme.savenewlexeme(mongo,
                                    projects,
                                    lexemes,
                                    scriptCode,
                                    langScript,
                                    new_lexeme_data,
                                    new_lexeme_files,
                                    projectowner,
                                    current_username)
        flash('Successfully added new lexeme')
        return redirect(url_for('enternewlexeme'))
    try:
        my_projects = len(userprojects.find_one(
            {'username': current_username})["myproject"])
        shared_projects = len(userprojects.find_one(
            {'username': current_username})["projectsharedwithme"])
        # logger.debug(f"MY PROJECTS: {my_projects}, SHARED PROJECTS: {shared_projects}")
        if (my_projects+shared_projects) == 0:
            flash('Please create your first project')
            return redirect(url_for('home'))
    except:
        # logger.debug(f'{"#"*80}\nCurrent user details not in database!!!')
        flash('Please create your first project')
        return redirect(url_for('home'))
    # get the list of lexeme entries for current project to show in dictionary view table
    lst = list()
    try:
        # logger.debug(activeprojectname)
        # optionally takes field_list, if provided by the user for showing dictionary entries
        all_fields, lst = lexicondetails.get_all_lexicon_details(
            lexemes, activeprojectname)
    except:
        logger.exception("")
        flash('Enter first lexeme of the project')

    shareinfo = getuserprojectinfo.getuserprojectinfo(
        userprojects, current_username, activeprojectname)
    return render_template('dictionaryview.html',
                           projectName=activeprojectname,
                           fields=all_fields,
                           sdata=lst,
                           count=len(lst),
                           data=currentuserprojectsname,
                           shareinfo=shareinfo)


# enter new lexeme route
# display form for new lexeme entry for current project
@app.route('/enternewlexeme', methods=['GET', 'POST'])
@login_required
def enternewlexeme():
    projects, userprojects, projectsform = getdbcollections.getdbcollections(mongo,
                                                                             'projects',
                                                                             'userprojects',
                                                                             'projectsform')
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                                                            userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)

    # new project form containing dictionary fields and its type
    # if request.method == 'POST':
    #     project_form_data = dict(request.form.lists())
    #     project_name = project_form_data['projectname'][0]
    #     project_name = savenewproject.savenewproject(projects,
    #                                                     project_name,
    #                                                     current_user.username)
    #     if project_name == '':
    #         flash(f'Project Name : {project_name} already exist!')
    #         return redirect(url_for('newproject'))
    #     else:
    #         logger.debug(project_name)
    #         updateuserprojects.updateuserprojects(userprojects,
    #                                                 project_name,
    #                                                 current_user.username)
    #         savenewprojectform.savenewprojectform(projectsform,
    #                                                 project_name,
    #                                                 project_form_data,
    #                                                 current_user.username)

    # activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
    #                     userprojects)

    # project_form = projectsform.find_one_or_404({'projectname' : activeprojectname,
    #                                 'username' : current_user.username},
    #                                 { "_id" : 0 })
    # if project_form is not None:
    #     return render_template('enternewlexeme.html',
    #                             newData=project_form,
    #                             data=currentuserprojectsname)
    # return render_template('enternewlexeme.html')
    # if method is not 'POST'
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    project_form = projectsform.find_one_or_404({'projectname': activeprojectname,
                                                 'username': projectowner},
                                                {"_id": 0})
    if project_form is not None:
        return render_template('enternewlexeme.html',
                               newData=project_form,
                               data=currentuserprojectsname)
    return render_template('enternewlexeme.html')

# defining file_format and uploaded_file_content globally
# to solve the problem of accessing the variable later by some functions
# file_format = ''
# uploaded_file_content = ''


def enterlexemefromuploadedfile(alllexemedf):
    projects, userprojects, lexemes, projectsform = getdbcollections.getdbcollections(mongo,
                                                                                      'projects',
                                                                                      'userprojects',
                                                                                      'lexemes',
                                                                                      'projectsform')
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                                                            userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    projectname = activeprojectname
    project = projects.find_one({}, {projectname: 1})
    current_project_form = projectsform.find_one(
        {'projectname': projectname}, {'_id': 0})

    # logger.debug('df data', alllexemedf.keys())
    # if 'langscripts' in lexemedf.columns:
    #     logger.debug(lexemedf['langscripts'])

    def removelangscriptsblank(lexemedf):
        drop_cols = [
            c for c in lexemedf.columns if c.startswith('langscripts.')]
        lexemedf.drop(columns=drop_cols, inplace=True)
        # return lexemedf
    # logger.debug('Project form', project_form)
    # if projectname in project_form:
    #     current_projct_form = project_form[projectname]

    def lexmetadata():
        # create lexemeId
        project = projects.find_one({'projectname': projectname}, {
                                    'projectname': 1, 'lexemeInserted': 1})
        lexemeCount = project['lexemeInserted']+1
        # lexemeCount = projects.find_one({}, {projectname : 1})[projectname]['lexemeInserted']+1
        # lexemeId = projectname+lexemeFormData['headword']+str(lexemeCount)
        Id = re.sub(r'[-: \.]', '', str(datetime.now()))
        lexemeId = 'L'+Id

        return (lexemeId, lexemeCount)

    # when testing comment these to avoid any database update/changes
    # saving data for that new lexeme to database in lexemes collection
    # try:
    # logger.debug(lexemedf)
    for lexeme_type, lexemedf in alllexemedf.items():
        # logger.debug('Data key', lexeme_type)
        # logger.debug(lexemedf)
        for index, row in lexemedf.iterrows():
            uploadedFileLexeme = {
                "username": projectowner,
                "projectname": activeprojectname,
                "lexemedeleteFLAG": 0,
                "updatedBy": current_user.username,
            }

            langscripts = langscriptutils.get_langscripts_from_lexeme_form(
                current_project_form)
            uploadedFileLexeme['langscripts'] = langscripts
            # removes old blank langscripts columns
            removelangscriptsblank(lexemedf)

            lexemeId = str(row['lexemeId'])
            getlexemeId = None
            # logger.debug(f"{index}\t{lexemeId}\t{len(lexemeId)}\t{type(lexemeId)}")
            if (lexemeId == 'nan' or lexemeId == ''):
                lexemeId, lexemeCount = lexmetadata()
                # logger.debug(lexemeId, lexemeCount)
            else:
                getlexemeId = lexemes.find_one({'lexemeId': lexemeId},
                                               {'_id': 0, 'lexemeId': 1, 'projectname': 1})
                # logger.debug(getlexemeId)
                if (getlexemeId == None):
                    # logger.debug(f"lexemeId not in DB")
                    lexemeId, lexemeCount = lexmetadata()
                else:
                    if (getlexemeId['projectname'] != activeprojectname):
                        flash(
                            f"lexemeId: {lexemeId} if from different project!!!")
                        return redirect(url_for('enternewlexeme'))

            uploadedFileLexeme['lexemeId'] = lexemeId
            # logger.debug(uploadedFileLexeme)
            if (getlexemeId != None):
                # logger.debug(f"LEXEME ALREADY EXISTS")
                lexemes.update_one({'lexemeId': lexemeId}, {
                    '$set': uploadedFileLexeme})
            else:
                lexemes.insert_one(uploadedFileLexeme)
                # update lexemeInserted count of the project in projects collection
                # project[projectname]['lexemeInserted'] = lexemeCount
                # logger.debug(f'{"#"*80}\n{project}')
                projects.update_one({'projectname': projectname}, {
                                    '$set': {'lexemeInserted': lexemeCount}})
                # projects.update_one({}, { '$set' : { projectname : project[projectname] }})

            for column_name in list(lexemedf.columns):
                # logger.debug(column_name)
                # if (column_name.endswith('Example')):
                #     continue
                if (column_name not in uploadedFileLexeme):
                    value = str(row[column_name])
                    # logger.debug(value)
                    if (value == 'nan'):
                        value = ''
                    if ('Sense 1.Gloss.eng' in column_name):
                        uploadedFileLexeme['gloss'] = value
                    if ('Sense 1.Grammatical Category' in column_name):
                        uploadedFileLexeme['grammaticalcategory'] = value
                    uploadedFileLexeme[column_name] = value

            # logger.debug(f'{"="*80}\nLexeme Form :')
            # logger.debug(uploadedFileLexeme)
            # logger.debug(f'{"="*80}')

            lexemes.update_one({'lexemeId': lexemeId}, {
                '$set': uploadedFileLexeme})

            # logger.debug(f'{"="*80}\nLexeme Form :')
            # logger.debug(uploadedFileLexeme)
            # logger.debug(f'{"="*80}')

    flash('Successfully added new lexemes')
    return redirect(url_for('enternewlexeme'))
    # comment till here


def lifeuploader(fileFormat, uploadedFileContent, field_map={}, headword_mapped=False, all_mapped=False):
    lang_script_map = {
        'ipa': 'ipa',
        'hi': 'Deva',
        'bns': 'Deva',
        'hin': 'Deva',
        'guj': 'Gujr',
        'pun': 'Guru',
        'ban': 'Beng',
        'ass': 'Beng',
        'odi': 'Orya',
        'kan': 'Knda',
        'tam': 'Taml',
        'tel': 'Telu',
        'mal': 'Mlym',
        'mar': 'Deva',
        'bod': 'Deva',
        'kon': 'Deva',
        'nep': 'Deva',
        'mai': 'Deva',
        'mag': 'Deva',
        'bho': 'Deva',
        'awa': 'Deva',
        'har': 'Deva',
        'bra': 'Deva',
        'bun': 'Deva',
        'anp': 'Deva'
    }

    def get_lift_map():
        map = {
            'grammatical-info': 'Grammatical Category',
            'lexical-unit': 'headword',
            'lexical-unit-form': 'Lexical Form',
            'pronunciation': 'Pronunciation',
            'gloss': 'Gloss',
            'example': 'Example',
            'translation': 'Free Translation',
            'definition': 'Definition',
            'note': 'Encyclopedic Information',
            'semantic-domain': 'Semantic Domain',
            'variant': 'VariantNew.Variant 1',
            'relation': ''
        }

        return map

    def get_script_name(wordform):
        lang_name = wordform.attrib['lang']
        # logger.debug(lang_name)
        parts = lang_name.split('-')
        if len(parts) > 1:
            script_name = parts[1]
        else:
            script_name = lang_script_map.get(lang_name, lang_name)

        return script_name, lang_name

    def get_lang_name(wordform):
        lang_name_full = wordform.attrib['lang']
        # logger.debug(lang_name_full)
        lang_name = lang_name_full.split('-')[0]
        # if len(parts) > 1:
        #     script_name = parts[1]
        # else:
        #     script_name = lang_script_map.get(lang_name, lang_name)

        return lang_name, lang_name_full

    def get_scripts_map(lex_fields):
        scripts_map = {}
        # logger.debug(lex_fields)
        for lex_field in lex_fields:
            # logger.debug('Lex field', lex_field)
            script_name = lex_field.split('.')[-1]
            if 'langscripts.headwordscript' in lex_field:
                scripts_map['langscripts.headwordscript'] = script_name
            elif 'langscripts.lexemeformscripts' in lex_field:
                if 'langscripts.lexemeformscripts' in scripts_map:
                    scripts_map['langscripts.lexemeformscripts'].append(
                        script_name)
                else:
                    scripts_map['langscripts.lexemeformscripts'] = [
                        script_name]
            elif 'langscripts.glosslangs' in lex_field:
                if 'langscripts.glosslangs' in scripts_map:
                    scripts_map['langscripts.glosslangs'].append(script_name)
                else:
                    scripts_map['langscripts.glosslangs'] = [script_name]
                # scripts_map.get('langscripts.glosslangs', []).append(script_name)
        # logger.debug(f"{'-'*80}\nIN get_scripts_map(lex_fields) function\n\nscript_map:\n{scripts_map}")

        return scripts_map

    def map_lift(file_stream, field_map, lex_fields):
        # logger.debug(f"{'-'*80}\nIN map_lift(file_stream, field_map, lex_fields) function\n")
        mapped_lift = {}
        all_mapped = True

        life_scripts_map = get_scripts_map(lex_fields)
        # logger.debug(life_scripts_map)

        if len(field_map) == 0:
            field_map = get_lift_map()

        # logger.debug(f"{'-'*80}\nget_lift_map():\n{field_map}")
        # logger.debug(f"{'-'*80}\nFILE STREAM TYPE:{type(file_stream)}")
        # exit()
        # tree = ET.parse(file_stream)
        root = ET.fromstring(file_stream)
        # logger.debug(f"TYPE OF TREE: {type(tree)}")
        # exit()
        # root = tree.getroot()
        # logger.debug(f"{'-'*80}\nroot:\n{root}")
        # exit()
        entries = root.findall('.//entry')
        # logger.debug(f"entries:\n{entries}")
        # exit()
        mapped_life_langs_lexeme_form = []
        unmapped_lift_langs_lexeme_form = []

        mapped_life_langs_gloss = []
        unmapped_lift_langs_gloss = []

        mapped_life_langs_variant = []
        unmapped_lift_langs_variant = []

        life_headword_script = life_scripts_map['langscripts.headwordscript']
        life_lexeme_form_scripts = life_scripts_map['langscripts.lexemeformscripts']
        life_gloss_langs = life_scripts_map['langscripts.glosslangs']
        # life_variant_langs = life_scripts_map['langscripts.glosslangs']

        life_gloss_langs = [x.lower() for x in life_gloss_langs]

        highest_sense_num = 0
        highest_variant_num = 0
        for entry in entries:
            # pd_row = {}
            for entry_part in entry:
                sense_num = 0
                variant_num = 0
                entry_part_tag = entry_part.tag
                if entry_part_tag != 'entry':
                    # logger.debug(entry_part_tag)
                    if entry_part_tag == 'lexical-unit':
                        life_key_headword = field_map[entry_part_tag]

                        # lift_tag_other_lexemes = entry_part_tag+'-form'
                        # life_key_other_lexemes = field_map[lift_tag_other_lexemes]

                        for wordform in entry_part:
                            lift_script_name, lift_lang_name = get_script_name(
                                wordform)
                            # lift_tag = entry_part_tag + '.' + lift_lang_name
                            # lift_tag = './/entry/lexical-unit/form[@lang='+lift_lang_name+']/text'
                            # lift_tag = './lexical-unit/form[@lang='+lift_lang_name+']/text'
                            lift_tag = './lexical-unit/form[@lang="' + \
                                lift_lang_name+'"]'

                            if lift_script_name == life_headword_script:
                                if lift_tag not in mapped_lift:
                                    mapped_lift[lift_tag +
                                                '#headword'] = life_key_headword

                                if lift_script_name not in mapped_life_langs_lexeme_form:
                                    mapped_life_langs_lexeme_form.append(
                                        lift_script_name)

                            if lift_script_name in life_lexeme_form_scripts:
                                # mapped_lift[lift_tag] = life_key_other_lexemes+'.'+lift_script_name

                                mapped_lift[lift_tag] = lift_script_name
                                if lift_script_name not in mapped_life_langs_lexeme_form:
                                    mapped_life_langs_lexeme_form.append(
                                        lift_script_name)

                            else:
                                if lift_tag not in unmapped_lift_langs_lexeme_form:
                                    unmapped_lift_langs_lexeme_form.append(
                                        lift_tag)
                                # mapped_lift[other_lexeme_forms] = lexeme_form_scripts

                        #     logger.debug('Script', script_name)
                        #     # txt = wordform[0].text
                        #     life_val = life_key #+'.'+script_name
                        #     entry_part_tag = entry_part_tag + '.' + script_name
                        #     other_entries = other_entries + '.' + script_name
                        #     if entry_part_tag not in mapped_lift:
                        #         mapped_lift[entry_part_tag] = life_val
                        #     else:
                        #         old_val = mapped_lift[entry_part_tag]
                        #         if life_val not in old_val:
                        #             life_val_other = life_val.replace(life_key, life_key_other)

                        #             if type(old_val) == str:
                        #                 life_val_other_old = old_val.replace(life_key, life_key_other)
                        #                 life_val_other = [life_val_other_old, life_val_other]
                        #                 old_val = [old_val, life_val]
                        #                 mapped_lift[entry_part_tag] = old_val
                        #                 mapped_lift[other_entries] = life_val_other
                        #             else:
                        #                 mapped_lift[entry_part_tag].append(old_val)
                        #                 mapped_lift[other_entries].append(life_val_other)
                        # # else:
                        # #     script_name = get_script_name(wordforms[0])
                        # #     logger.debug('Script', script_name)
                        # #     mapped_lift[entry_part_tag] = life_key+'.'+script_name
                    elif entry_part_tag == 'sense':
                        sense_num += 1

                        if sense_num > highest_sense_num:
                            highest_sense_num = sense_num

                        for sense_part in entry_part:
                            sense_part_tag = sense_part.tag
                            # logger.debug('sense_part_tag', sense_part_tag, sense_part.attrib, sense_part.find('text'))
                            life_key_sense = field_map[sense_part_tag]

                            if sense_part_tag == 'gloss' or sense_part_tag == 'definition' or sense_part_tag == 'example':
                                if len(sense_part.attrib) == 0:
                                    sense_part_tag_form = sense_part.find(
                                        'form')
                                    logger.debug(sense_part_tag_form)
                                    lift_lang_name, lift_full_lang = get_script_name(
                                        sense_part_tag_form)
                                else:
                                    lift_lang_name, lift_full_lang = get_script_name(
                                        sense_part)
                                # lift_sense_tag = sense_part_tag + '.' + lift_lang_name
                                # lift_sense_tag = './/entry/sense/'+sense_part_tag+'[@lang='+lift_full_lang+']'
                                # lift_sense_tag = './sense/'+sense_part_tag+'[@lang='+lift_full_lang+']/text'
                                if len(sense_part.attrib) == 0:
                                    lift_sense_tag = './sense/'+sense_part_tag + \
                                        '/form[@lang="'+lift_full_lang+'"]'
                                else:
                                    lift_sense_tag = './sense/'+sense_part_tag + \
                                        '[@lang="'+lift_full_lang+'"]'

                                if lift_lang_name in life_gloss_langs:
                                    mapped_lift[lift_sense_tag] = 'SenseNew.Sense '+str(
                                        sense_num)+'.'+life_key_sense + '.' + lift_lang_name
                                    if lift_lang_name not in mapped_life_langs_gloss:
                                        mapped_life_langs_gloss.append(
                                            lift_lang_name)
                                else:
                                    if lift_sense_tag not in unmapped_lift_langs_gloss:
                                        unmapped_lift_langs_gloss.append(
                                            lift_sense_tag)
                            elif sense_part_tag == 'grammatical-info':
                                life_key = field_map.get(sense_part_tag, [])
                                # lift_tag = './/entry/sense/'+sense_part_tag
                                logger.debug(entry_part[0].tag)
                                # gram_categ = entry_part[0].attrib['value']

                                # +'[@value="'+gram_categ+'"]'
                                lift_tag = './sense/'+sense_part_tag
                                if lift_tag not in mapped_lift:
                                    mapped_lift[lift_tag] = life_key
                            else:
                                life_key = field_map.get(sense_part_tag, [])
                                # lift_tag = './/entry/sense/'+sense_part_tag
                                lift_tag = './sense/'+sense_part_tag
                                mapped_lift[lift_tag] = 'SenseNew.Sense ' + \
                                    str(sense_num)+'.'+life_key_sense
                    elif entry_part_tag == 'variant':
                        variant_num += 1

                        if variant_num > highest_variant_num:
                            highest_variant_num = variant_num

                        for variant_part in entry_part:
                            variant_part_tag = variant_part.tag
                            logger.debug('variant_part_tag', variant_part_tag,
                                  variant_part.attrib, variant_part.find('text'))
                            # life_key_sense = field_map[variant_part_tag]

                            if variant_part_tag == 'form':
                                if len(variant_part.attrib) == 0:
                                    variant_part_tag_form = variant_part.find(
                                        'form')
                                    logger.debug(variant_part_tag_form)
                                    lift_lang_name, lift_full_lang = get_script_name(
                                        variant_part_tag_form)
                                else:
                                    lift_lang_name, lift_full_lang = get_script_name(
                                        variant_part)
                                # lift_sense_tag = sense_part_tag + '.' + lift_lang_name
                                # lift_sense_tag = './/entry/sense/'+sense_part_tag+'[@lang='+lift_full_lang+']'
                                # lift_sense_tag = './sense/'+sense_part_tag+'[@lang='+lift_full_lang+']/text'
                                if len(variant_part.attrib) == 0:
                                    lift_variant_tag = './variant/'+variant_part_tag + \
                                        '/form[@lang="'+lift_full_lang+'"]'
                                else:
                                    lift_variant_tag = './variant/'+variant_part_tag + \
                                        '[@lang="'+lift_full_lang+'"]'

                                mapped_lift[lift_variant_tag] = 'Variant.Variant '+str(
                                    variant_num)+'.Variant Form'

                                # if lift_lang_name in life_variant_langs:
                                #     mapped_lift[lift_variant_tag] = 'Variant.Variant '+str(
                                #         sense_num)+'.Variant Form'
                                #     if lift_lang_name not in mapped_life_langs_variant:
                                #         mapped_life_langs_variant.append(
                                #             lift_lang_name)
                                # else:
                                #     if lift_variant_tag not in unmapped_lift_langs_variant:
                                #         unmapped_lift_langs_variant.append(
                                #             lift_variant_tag)

                    elif entry_part_tag == 'pronunciation':
                        life_key_pron = field_map[entry_part_tag]
                        for pronform in entry_part:
                            lift_lang_name, lift_full_lang = get_script_name(
                                pronform)
                            lift_pron_tag = './pronunciation/form[@lang="' + \
                                lift_full_lang+'"]'
                            mapped_lift[lift_pron_tag] = life_key_pron

                    # elif entry_part_tag == 'grammatical-info':
                    #     life_key_gr = field_map[entry_part_tag]
                    #     gram_categ = entry_part.attrib['value']
                    #     lift_gr_tag = './grammatical-info[@value="'+gram_categ+'"]'
                    #     mapped_lift[lift_gr_tag] = life_key_gr

                    else:
                        if 'trait' not in entry_part_tag:
                            life_key = field_map.get(entry_part_tag, [])
                            # lift_entry_tag = './/entry/'+entry_part_tag
                            lift_entry_tag = './'+entry_part_tag
                            mapped_lift[lift_entry_tag] = life_key
                # elif entry_part_tag == 'gloss':

        mapped_life_langs_lexeme_form_set = set(mapped_life_langs_lexeme_form)
        all_life_lexeme_form_scripts = set(life_lexeme_form_scripts)
        life_unmapped_lexeme_forms = all_life_lexeme_form_scripts - \
            mapped_life_langs_lexeme_form_set
        # unmapped_lift_langs_lexeme_form = []

        mapped_life_langs_gloss_set = set(mapped_life_langs_gloss)
        all_life_gloss_langs = set(life_gloss_langs)
        life_unmapped_gloss_langs = all_life_gloss_langs - mapped_life_langs_gloss_set
        # unmapped_lift_langs_gloss = []
        # logger.debug('Unmapped gloss', unmapped_lift_langs_gloss)

        # mapped_life_langs_variant_set = set(mapped_life_langs_variant)
        # all_life_variant_langs = set(life_variant_langs)
        # life_unmapped_variant_langs = all_life_variant_langs - mapped_life_langs_variant_set

        headword_mapped = False
        life_all_mapped = mapped_lift.values()
        for life_key_mapped in life_all_mapped:
            if 'headword' in life_key_mapped:
                headword_mapped = True

        # if headword_mapped:
        for lift_unmapped_lexeme_form in unmapped_lift_langs_lexeme_form:
            # lift_unmapped_entry = './/entry/lexical-unit/form[@lang='+lift_unmapped_lexeme_form+']/text'
            mapped_lift[lift_unmapped_lexeme_form] = list(
                life_unmapped_lexeme_forms)

        for lift_unmapped_gloss in unmapped_lift_langs_gloss:
            mapped_lift[lift_unmapped_gloss] = list(life_unmapped_gloss_langs)

        # for lift_unmapped_variant in unmapped_lift_langs_variant:
        #     mapped_lift[lift_unmapped_variant] = list(life_unmapped_variant_langs)
        # logger.debug(mapped_lift)
        # logger.debug(headword_mapped)

        if len(unmapped_lift_langs_lexeme_form) > 0 or len(unmapped_lift_langs_gloss) > 0:
            all_mapped = False

        if len(unmapped_lift_langs_lexeme_form) > 0 or len(unmapped_lift_langs_variant) > 0:
            all_mapped = False

        # logger.debug(f"{'-'*80}\nheadword_mapped:\n{headword_mapped}\nall_mapped:\n{all_mapped}\nmapped_lift:\n{mapped_lift}\nroot:\n{root}")
        logger.debug("All mapped", mapped_lift)
        return headword_mapped, all_mapped, mapped_lift, root

    def get_sense_col(lift_tag, field_name, lang_name):
        all_cols = []
        sense_num = 0
        for sense in lift_tag:
            sense_num += 1
            df_col = 'SenseNew.Sense ' + \
                str(sense_num)+'.'+field_name+'.'+lang_name
            all_cols.append(df_col)
        return all_cols

    def group_fields(field_map):
        new_map = {}
        for field, vals in field_map.items():
            field_parts = field.split('/')
            outer_part = field_parts[1]
            if outer_part in new_map:
                new_map[outer_part][field] = vals
            else:
                new_map[outer_part] = {field: vals}
        return new_map

    def append_new_column(first_field, current_field, current_field_column, data, data_len):
        if first_field in current_field_column and current_field not in current_field_column:
            new_field_column = current_field_column.replace(
                first_field, current_field)
            data[new_field_column] = ['']*data_len

    def create_df_columns(data, field_type, field_number):
        data_len = len(data)
        if field_number > 1:
            data_columns = list(data.columns)
            current_field_columns = [
                x for x in data_columns if x.startswith(field_type)]
            for current_field_column in current_field_columns:
                if 'SenseNew' in field_type:
                    new_field_type = 'Sense'
                else:
                    new_field_type = field_type

                first_field = new_field_type + ' 1'

                for current_field_number in range(2, field_number+1):
                    current_field = new_field_type + \
                        ' '+str(current_field_number)

                    if first_field in current_field_column:
                        append_new_column(
                            first_field, current_field, current_field_column, data, data_len)

            # data.columns = data_columns

    def lift_to_df(root, field_map, lex_fields):
        # logger.debug(f"{'-'*80}\nIN lift_to_df (root, field_map, lex_fields) function\n")
        all_data = {}

        # lex_fields_without_sense = [lex_field for lex_field in lex_fields if 'sense' not in lex_field]

        life_scripts_map = get_scripts_map(lex_fields)
        logger.debug(life_scripts_map)

        # if len(field_map) == 0:
        lift_life_field_map = get_lift_map()
        logger.debug(f"{'-'*80}\nIN lift_to_df (root, field_map, lex_fields) function: get_lift_map():\n{lift_life_field_map}")

        # tree = ET.parse(file_stream)
        # root = tree.getroot()
        entries = root.findall('.//entry')

        # mapped_life_langs_lexeme_form = []
        # unmapped_lift_langs_lexeme_form = []

        # mapped_life_langs_gloss = []
        # unmapped_lift_langs_gloss = []

        # life_headword_script = life_scripts_map['langscripts.headwordscript']
        # life_lexeme_form_scripts = life_scripts_map['langscripts.lexemeformscripts']
        # life_gloss_langs = life_scripts_map['langscripts.glosslangs']
        field_map = group_fields(field_map)

        logger.debug(
            f"{'-'*80}\nIN lift_to_df (root, field_map, lex_fields) function: {field_map}")

        # highest_sense_num = 0
        for entry in entries:
            df_row = {}
            sense_num = 0
            variant_num = 0
            senseNotAdded = True
            variantNotAdded = True
            for lift_tag_groups, life_key_maps in field_map.items():
                logger.debug('Entry', entry)
                if len(life_key_maps) > 0:
                    if 'lexical-unit' in lift_tag_groups:
                        # txt = entry.findall(lift_tag+'/text').text
                        # logger.debug(lift_tag)
                        for lift_tag, life_key in life_key_maps.items():
                            lexical_unit = entry.find('lexical-unit')
                            lexical_unit_text = lexical_unit.find('text')

                            if lexical_unit_text is None:
                                lexical_unit_text = lexical_unit.find(
                                    'form').find('text')

                            if not lexical_unit_text is None:
                                txt = lexical_unit_text.text

                            if 'headword' in life_key and 'headword' in lift_tag:
                                df_row['headword'] = txt

                            else:
                                df_row['Lexeme Form.'+life_key] = txt
                            # else:
                            #     df_row['Lexeme Form.'+life_key] = txt

                    elif 'pronunciation' in lift_tag_groups:
                        if len(life_key_maps) == 1:
                            lift_tag = list(life_key_maps.keys())[0]
                            life_key = life_key_maps[lift_tag]

                        txt_entry = entry.find(lift_tag+'/text')
                        # life_key = lift_life_field_map[lift_tag]

                        if not txt_entry is None:
                            txt = txt_entry.text

                        df_row[life_key] = txt

                    # elif '@lang' in lift_tag:
                    elif 'sense' in lift_tag_groups:
                        all_sense = entry.findall('.//sense')
                        for full_sense in all_sense:
                            sense_num += 1
                            logger.debug('Sense number', sense_num,
                                  full_sense)

                            for lift_tag, life_key in life_key_maps.items():
                                # for sense in full_sense:
                                if 'grammatical-info' in lift_tag:
                                    life_key_name = lift_life_field_map['grammatical-info']
                                    gram_info_tag = full_sense.find(
                                        'grammatical-info')
                                    logger.debug('Grammar tag', gram_info_tag,
                                          gram_info_tag.tag)
                                    # life_key = lift_life_field_map[lift_tag]

                                    if not gram_info_tag is None:
                                        try:
                                            gram_info = gram_info_tag.attrib['value']
                                            logger.debug('Gram info', gram_info)
                                        except Exception as e:
                                            logger.debug(
                                                'Exception in grammatical info', e)
                                            gram_info = ''
                                        df_col = 'SenseNew.Sense ' + \
                                            str(sense_num)+'.' + \
                                            life_key_name
                                        df_row[df_col] = gram_info
                                    # df_row[life_key] = gram_info
                                else:
                                    if 'gloss' in lift_tag:
                                        life_key_name = lift_life_field_map['gloss']
                                        current_sense_tag = full_sense.find(
                                            'gloss')
                                    elif 'definition' in lift_tag:
                                        life_key_name = lift_life_field_map['definition']
                                        current_sense_tag = full_sense.find(
                                            'definition')
                                    elif 'example' in lift_tag:
                                        life_key_name = lift_life_field_map['example']
                                        current_sense_tag = full_sense.find(
                                            'example')
                                    else:
                                        life_key_name = ''

                                    # logger.debug(sense.tag)
                                    if life_key_name != '':
                                        try:
                                            txt_entry = current_sense_tag.find(
                                                'text')
                                            if txt_entry is None:
                                                txt_entry = current_sense_tag.find(
                                                    'form').find('text')
                                        except:
                                            txt_entry = None

                                        if not txt_entry is None:
                                            txt = txt_entry.text
                                        else:
                                            txt = "NA"
                                    else:
                                        txt = ''

                                    if life_key_name != '':
                                        if 'example' in lift_tag:
                                            df_col = 'SenseNew.Sense ' + \
                                                str(sense_num)+'.' + \
                                                life_key_name
                                            df_row[df_col] = txt
                                        else:
                                            df_col = 'SenseNew.Sense ' + \
                                                str(sense_num)+'.' + \
                                                life_key_name+'.'+life_key
                                            df_row[df_col] = txt
                        # senseNotAdded = False
                    elif 'variant' in lift_tag_groups:
                        all_variants = entry.findall('.//variant')
                        for variant in all_variants:
                            variant_num += 1
                            # create_df_columns(data, 'Variant', variant_num)
                            logger.debug('Variant number', variant_num, variant)
                            # logger.debug('DF columns', data.columns)

                            # logger.debug(sense.tag)
                            for lift_tag, life_key in life_key_maps.items():
                                txt_entry = variant.find('text')
                                if txt_entry is None:
                                    txt_entry = variant.find(
                                        'form').find('text')

                                if not txt_entry is None:
                                    txt = txt_entry.text

                                # if txt != '':
                                df_col = 'Variant.Variant ' + \
                                    str(variant_num)+'.'+'Variant Form'
                                df_row[df_col] = txt
                        # variantNotAdded = False

                    else:
                        # logger.debug(lift_tag)
                        txt_entry = entry.find(lift_tag)
                        if lift_tag in lift_life_field_map:
                            life_key = lift_life_field_map[lift_tag]

                            if not txt_entry is None:
                                txt = txt_entry.text

                            df_row[life_key] = txt

            logger.debug('Current DF Row', df_row)
            current_sense_variant = (sense_num, variant_num)

            if current_sense_variant in all_data:
                data = all_data[current_sense_variant]
                data = data.append(df_row, ignore_index=True)
            else:
                data = pd.DataFrame(columns=lex_fields)
                if sense_num > 1:
                    create_df_columns(data, 'SenseNew', sense_num)

                if variant_num > 1:
                    create_df_columns(data, 'Variant', variant_num)

                logger.debug('DF columns', data.columns)
                data = data.append(df_row, ignore_index=True)

            data.fillna('', inplace=True)
            all_data[current_sense_variant] = data

        logger.debug('Final data', all_data)

        headword_mapped = True
        all_mapped = True

        # data.to_csv(os.path.join(basedir, 'testliftXML.tsv'), sep='\t', index=False)

        # logger.debug(f"{'-'*80}\nIN lift_to_df (root, field_map, lex_fields) FUNCTION\n\nheadword_mapped\n{headword_mapped}\n\nall_mapped:\n{all_mapped}\n\ndata:\n{data}\n\nroot:\n{root}")
        # logger.debug(f"{'-'*80}\nIN lift_to_df (root, field_map, lex_fields) FUNCTION\n\nheadword_mapped\n{type(headword_mapped)}\n\nall_mapped:\n{type(all_mapped)}\n\ndata:\n{type(data)}\n\nroot:\n{type(root)}")

        return headword_mapped, all_mapped, all_data, root

    def prepare_lex(lexicon):
        df = pd.json_normalize(lexicon)
        columns = df.columns
        # drop_cols = [c for c in df.columns if c.startswith('langscripts.')]
        drop_cols = []
        drop_cols.append('lexemedeleteFLAG')
        # drop_cols.append ('grammaticalcategory')
        drop_cols.append('projectname')

        if 'gloss' in columns:
            drop_cols.append('gloss')
        drop_oldsense = [c for c in df.columns if c.startswith('Sense.')]
        drop_oldvariant = [c for c in df.columns if c.startswith('Variant.')]
        drop_oldallomorph = [
            c for c in df.columns if c.startswith('Allomorph.')]
        drop_oldscript = [
            c for c in df.columns if c.startswith('Lexeme Form Script')]
        drop_files = [c for c in df.columns if c.startswith('filesname.')]

        drop_cols.extend(drop_oldsense)
        drop_cols.extend(drop_oldvariant)
        drop_cols.extend(drop_oldallomorph)
        drop_cols.extend(drop_oldscript)
        drop_cols.extend(drop_files)

        df.drop(columns=drop_cols, inplace=True)

        return df

    def generate_all_possible_mappings(key_cols, val_cols):
        final_map = {}
        for key_col in key_cols:
            final_map[key_col] = list(val_cols)
        # logger.debug(f"{'-'*80}\nIN generate_all_possible_mappings(key_cols, val_cols) function\nFINAL MAP:\n{final_map}")
        return final_map

    def map_excel(file_stream, lex_fields):
        # logger.debug(f"{'-'*80}\nIN MAP EXCEL function map_excel(file_stream, lex_fields)")
        excel_data = pd.read_excel(file_stream, engine="openpyxl")
        # logger.debug(excel_data)
        excel_data_cols = set(excel_data.columns)
        lex_field_cols = set(lex_fields)
        # logger.debug(f"{'-'*80}\nexcel_data_cols:\n{excel_data.columns}")
        # logger.debug(f"{'-'*80}\nNUMBER OF ELEMENTS IN excel_data_cols: {len(excel_data_cols)}")
        # logger.debug(f"{'-'*80}\nNUMBER OF ELEMENTS IN lex_field_cols: {len(lex_field_cols)}")

        # logger.debug(f"{'-'*80}\nlex_field_cols-excel_data_cols:\n{lex_field_cols-excel_data_cols}")

        if excel_data_cols == lex_field_cols:
            # logger.debug(f"{'-'*80}\nexcel_data_cols == lex_field_cols")
            mapped = True
            headword_mapped = True
            return headword_mapped, mapped, {}, excel_data
        else:
            # logger.debug(f"{'-'*80}\nexcel_data_cols != lex_field_cols")
            headword_mapped = True
            mapped = False
            excel_remaining = excel_data_cols - lex_field_cols
            lex_remaining = lex_field_cols - excel_data_cols
            # logger.debug(f"{'-'*80}\nexcel_remaining:\n{excel_remaining}\n{'-'*80}\nlex_remaining:\n{lex_remaining}")
            field_map = generate_all_possible_mappings(
                excel_remaining, lex_remaining)
            # logger.debug(f"{'-'*80}\nheadword_mapped\n{headword_mapped}\n\nmapped:\n{mapped}\n\nfield_map:\n{field_map}\n\nexcel_data:\n{excel_data}")
            return headword_mapped, mapped, field_map, excel_data

    def upload_excel(excel_data, field_map, lex_fields):
        # excel_data = pd.read_excel(file_stream)
        final_data = excel_data.rename(columns=field_map)
        mapped = True
        headword_mapped = True

        return headword_mapped, mapped, final_data

    def upload_lexicon(lexicon, file_stream, format, field_map, headword_mapped=False, all_mapped=False):
        lexicon = lexicon[1:]
        # logger.debug(f"{'-'*80}\nLEXICON:\n{lexicon}")
        norm_lex = prepare_lex(lexicon)
        # logger.debug(f"{'-'*80}\nNORM LEX:\n{norm_lex}")
        lex_fields = norm_lex.columns
        # logger.debug(f"{'-'*80}\nLEX FIELDS:\n{lex_fields}")
        # logger.debug(f"{'-'*80}\nFILE STREAM TYPE:{type(file_stream)}")

        if format == 'lift-xml':
            # logger.debug(f"{'-'*80}\nFIELD MAP:\n{len(field_map)}")
            if len(field_map) == 0:
                # logger.debug(f"{'-'*80}\nlift-xml: len(field_map) == 0")

                # headword_mapped, all_mapped, field_map, root = map_lift(
                # file_stream, field_map, lex_fields)

                if headword_mapped and all_mapped:
                    # logger.debug(f"{'-'*80}\nheadword_mapped and all_mapped")
                    headword_mapped, all_mapped, data, root = lift_to_df(
                        root, field_map, lex_fields)
                    # logger.debug(f"{'-'*80}\nheadword_mapped:\n{type(headword_mapped)}\nall_mapped:\n{type(all_mapped)}\nmapped_lift/data:\n{type(data)}\nroot:\n{type(root)}")
                    return headword_mapped, all_mapped, data, root

                else:
                    # logger.debug(f"{'-'*80}\nheadword_mapped and all_mapped: NOT")
                    # logger.debug(f"{'-'*80}\nheadword_mapped:\n{type(headword_mapped)}\nall_mapped:\n{type(all_mapped)}\nmapped_lift/data:\n{type(field_map)}\nroot:\n{type(root)}")
                    headword_mapped, all_mapped, field_map, root = map_lift(
                        file_stream, field_map, lex_fields)
                    return headword_mapped, all_mapped, field_map, root
            else:
                # logger.debug(f"{'-'*80}\nlift-xml: len(field_map) != 0")
                headword_mapped, all_mapped, life_df, root = lift_to_df(
                    file_stream, field_map, lex_fields)
                # logger.debug(life_df.head())
                # logger.debug(life_df.loc[0,:])
                return headword_mapped, all_mapped, life_df
        elif format == 'xlsx':
            if len(field_map) == 0:
                # logger.debug(f"{'-'*80}\nxlsx: len(field_map) == 0")
                headword_mapped, all_mapped, field_map, df = map_excel(
                    file_stream, lex_fields)
                return headword_mapped, all_mapped, field_map, df
            else:
                # logger.debug(f"{'-'*80}\nxlsx: len(field_map) != 0")
                headword_mapped, all_mapped, data = upload_excel(
                    file_stream, field_map, lex_fields)
                return headword_mapped, all_mapped, data

    working_dir = basedir
    # upload_file = os.path.join(working_dir, 'LiFE.lift')
    upload_file = uploadedFileContent
    # logger.debug(upload_file)
    # format = 'lift-xml'
    format = fileFormat
    # logger.debug(f"{'-'*80}\nFILE FORMAT:{fileFormat}")
    with open(os.path.join(working_dir, 'lexemeEntry.json')) as f_r:
        lex = json.load(f_r)

    return upload_lexicon(lex, upload_file, format, field_map, headword_mapped, all_mapped)

# upload lexeme form in excel/liftXML format


@app.route('/uploadlexemeexcelliftxml', methods=['GET', 'POST'])
def uploadlexemeexcelliftxml():
    if request.method == 'POST':
        lexkeymapping = dict(request.form.lists())
        # lexkeymapping = lexkeymapping.keys().decode('unicode-escape')
        # logger.debug(lexkeymapping)
        # logger.debug(type(lexkeymapping))
        lexkeymappingNew = {}
        for key, value in lexkeymapping.items():
            key = key.replace('%22', '"')
            lexkeymappingNew[key] = value[0]
        # logger.debug(lexkeymappingNew)
        field_map = lexkeymappingNew
        life_uploaded_file_content_path = os.path.join(
            basedir, 'lifeUploadedFileContent.pkl')
        # Open the file in binary mode
        with open(life_uploaded_file_content_path, 'rb') as file:
            retrieve_uploaded_file_content = pickle.load(file)
            # logger.debug(retrieve_uploaded_file_content.keys())
            file_format = retrieve_uploaded_file_content['file_format']
            uploaded_file_content = retrieve_uploaded_file_content['uploaded_file_content']
        if (file_format == 'lift-xml'):
            life_lift_root_path = os.path.join(basedir, 'lifeliftroot.xml')
            tree = ET.parse(life_lift_root_path)
            root = tree.getroot()
            headword_mapped = True
            all_mapped = True
            # logger.debug(f"{'-'*80}\nIN uploadlexemeexcelliftxml() FUNCTION\n\nfile_format\n{file_format}\n\nfield_map:\n{field_map}\n\nroot:\n{root}")
            # logger.debug(f"{'-'*80}\nIN uploadlexemeexcelliftxml() FUNCTION\n\nfile_format\n{type(file_format)}\n\nfield_map:\n{type(field_map)}\n\nroot:\n{type(root)}")

            headword_mapped, all_mapped, life_df = lifeuploader(
                file_format, root, field_map, headword_mapped, all_mapped)
            # logger.debug(f"{'-'*80}\nIN uploadlexemeexcelliftxml() FUNCTION\n\nheadword_mapped\n{headword_mapped}\n\nall_mapped:\n{all_mapped}\n\nlife_df:\n{life_df}\n\nroot:\n{root}")
            # logger.debug(f"{'-'*80}\nIN uploadlexemeexcelliftxml() FUNCTION\n\nheadword_mapped\n{type(headword_mapped)}\n\nall_mapped:\n{type(all_mapped)}\n\nlife_df:\n{type(life_df)}\n\nroot:\n{type(root)}")
        elif (file_format == 'xlsx'):
            life_xlsx_root_path = os.path.join(basedir, 'lifexlsxdf.tsv')
            df = pd.read_csv(life_xlsx_root_path, sep='\t', dtype=str)
            headword_mapped, all_mapped, data = lifeuploader(
                file_format, df, field_map)
            # logger.debug(f"{'-'*80}\nIN uploadlexemeexcelliftxml() FUNCTION\n\nheadword_mapped\n{headword_mapped}\n\nall_mapped:\n{all_mapped}\n\ndata:\n{data}\n\ndf:\n{df}")
            # logger.debug(f"{'-'*80}\nIN uploadlexemeexcelliftxml() FUNCTION\n\nheadword_mapped\n{type(headword_mapped)}\n\nall_mapped:\n{type(all_mapped)}\n\ndata:\n{type(data)}\n\ndf:\n{type(df)}")

        if (not headword_mapped):
            flash("headword is missing from the file")
            return redirect(url_for('enternewlexeme'))

        elif (not all_mapped and len(field_map) != 0):
            not_mapped_data = field_map
            # logger.debug('create a modal/page where user can give the mapping of the columns')
            return render_template('lexemekeymapping.html', not_mapped_data=not_mapped_data)
        else:
            if (file_format == 'lift-xml'):
                enterlexemefromuploadedfile(life_df)
            elif (file_format == 'xlsx'):
                enterlexemefromuploadedfile(data)

    return redirect(url_for('enternewlexeme'))

# lexeme key mapping


@app.route('/lexemekeymapping', methods=['GET', 'POST'])
def lexemekeymapping():
    # getting the collections
    projects, userprojects, lexemes = getdbcollections.getdbcollections(mongo,
                                                                        'projects',
                                                                        'userprojects',
                                                                        'lexemes')
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)
    projectname = activeprojectname
    lst = []
    lst.append({'projectname': activeprojectname})
    for lexeme in lexemes.find({'projectname': projectname, 'lexemedeleteFLAG': 0}, {'_id': 0}):
        lst.append(lexeme)

    # logger.debug(lst)
    # Serializing json
    json_object = json.dumps(lst, indent=2, ensure_ascii=False)

    with open(basedir+"/lexemeEntry.json", "w") as outfile:
        outfile.write(json_object)

    if request.method == 'POST':
        newLexemeFiles = request.files.to_dict()
        # logger.debug(newLexemeFiles)
        key = 'Upload Excel LiftXML'
        # logger.debug(type(newLexemeFiles[key].read()))
        if newLexemeFiles[key].filename != '':
            filename = newLexemeFiles[key].filename
            # logger.debug(filename)
            file_format = filename.rsplit('.', 1)[-1]
            if (file_format == 'xlsx' or file_format == 'lift'):
                uploaded_file_content = newLexemeFiles[key].read()
                if (file_format == 'lift'):
                    file_format = file_format+'-xml'
                    uploaded_file_content = str(uploaded_file_content, 'UTF-8')
                # logger.debug(file_format)
                pass
                # flash(f"File format is correct")
                # return redirect(url_for('enternewlexeme'))
            else:
                flash("File should be in 'xlsx' or 'lift' format")
                return redirect(url_for('enternewlexeme'))
        # logger.debug("File format is correct")

        # df = pd.read_excel(uploaded_file_content)
        # logger.debug(df)
        # save uploaded file details in pickle file for future use
        store_uploaded_file_content = {}
        store_uploaded_file_content['file_format'] = file_format
        store_uploaded_file_content['uploaded_file_content'] = uploaded_file_content
        life_uploaded_file_content_path = os.path.join(
            basedir, 'lifeUploadedFileContent.pkl')
        with open(life_uploaded_file_content_path, 'wb') as file:
            pickle.dump(store_uploaded_file_content, file)
        if (file_format == 'lift-xml'):
            headword_mapped, all_mapped, field_map, root = lifeuploader(
                file_format, uploaded_file_content, field_map={})
            # logger.debug(f"{'-'*80}\nIN lexemekeymapping() FUNCTION\n\nheadword_mapped\n{headword_mapped}\n\nall_mapped:\n{all_mapped}\n\nfield_map:\n{field_map}\n\nroot:\n{root}")
            # logger.debug(f"{'-'*80}\nIN lexemekeymapping() FUNCTION\n\nheadword_mapped\n{type(headword_mapped)}\n\nall_mapped:\n{type(all_mapped)}\n\nfield_map:\n{type(field_map)}\n\nroot:\n{type(root)}")
            tree = ElementTree(root)
            life_lift_root_path = os.path.join(basedir, 'lifeliftroot.xml')
            with open(life_lift_root_path, 'wb') as f:
                tree.write(f, encoding='utf-8')
        elif (file_format == 'xlsx'):
            headword_mapped, all_mapped, field_map, df = lifeuploader(
                file_format, uploaded_file_content, field_map={})
            # logger.debug(f"{'-'*80}\nIN lexemekeymapping() FUNCTION\n\nheadword_mapped\n{headword_mapped}\n\nall_mapped:\n{all_mapped}\n\nfield_map:\n{field_map}\n\ndf:\n{df}")
            # logger.debug(f"{'-'*80}\nIN lexemekeymapping() FUNCTION\n\nheadword_mapped\n{type(headword_mapped)}\n\nall_mapped:\n{type(all_mapped)}\n\nfield_map:\n{type(field_map)}\n\ndf:\n{type(df)}")
            life_xlsx_root_path = os.path.join(basedir, 'lifexlsxdf.tsv')
            df.to_csv(life_xlsx_root_path, sep='\t', index=False)

        # headword_mapped = True
        # all_mapped = False
        if (not headword_mapped):
            flash("headword is missing from the file")
            return redirect(url_for('enternewlexeme'))

        elif (not all_mapped and len(field_map) != 0):
            # not_mapped_data = {
            #     './pronunciation/form[@lang="anp-Deva"]': 'Pronunciation',
            #     './sense/grammatical-info': 'grammaticalcategory',
            #     './lexical-unit/form[@lang="anp-Deva"]': ['Beng', 'Mlym'],
            #     './sense/gloss[@lang="anp"]': ['Odi', 'Ass', 'Eng'],
            #     './sense/gloss[@lang="en"]': ['Odi', 'Ass', 'Eng']
            # }
            logger.debug("Field Map", field_map)
            not_mapped_data = field_map
            # logger.debug('create a modal/page where user can give the mapping of the columns')
            return render_template('lexemekeymapping.html', not_mapped_data=not_mapped_data)
        else:
            if (file_format == 'xlsx'):
                enterlexemefromuploadedfile(df)

    return redirect(url_for('enternewlexeme'))


# download lexeme form in excel format
@app.route('/downloadlexemeformexcel', methods=['GET', 'POST'])
def downloadlexemeformexcel():
    # getting the collections
    # collection of users and their respective projects
    userprojects = mongo.db.userprojects
    # collection containing entry of each lexeme and its details
    lexemes = mongo.db.lexemes

    activeprojectname = userprojects.find_one({'username': current_user.username})[
        'activeprojectname']
    projectname = activeprojectname
    lst = []
    lst.append({'projectname': activeprojectname})
    for lexeme in lexemes.find({'projectname': projectname, 'lexemedeleteFLAG': 0}, {'_id': 0}):
        if (len(lexeme['headword']) != 0):
            lst.append(lexeme)

    # logger.debug(lst)
    # Serializing json
    json_object = json.dumps(lst, indent=2, ensure_ascii=False)

    with open(basedir+"/lexemeEntry.json", "w") as outfile:
        outfile.write(json_object)

    def preprocess_csv_excel(lexicon):
        # logger.debug(lexicon)
        df = pd.json_normalize(lexicon)
        columns = df.columns
        drop_cols = [c for c in df.columns if c.startswith('langscripts.')]
        drop_cols.append('lexemedeleteFLAG')
        drop_cols.append('grammaticalcategory')
        drop_cols.append('projectname')

        if 'gloss' in columns:
            drop_cols.append('gloss')
        drop_oldsense = [c for c in df.columns if c.startswith('Sense.')]
        drop_oldvariant = [c for c in df.columns if c.startswith('Variant.')]
        drop_oldallomorph = [
            c for c in df.columns if c.startswith('Allomorph.')]
        drop_oldscript = [
            c for c in df.columns if c.startswith('Lexeme Form Script')]
        drop_files = [c for c in df.columns if c.startswith('filesname.')]

        drop_cols.extend(drop_oldsense)
        drop_cols.extend(drop_oldvariant)
        drop_cols.extend(drop_oldallomorph)
        drop_cols.extend(drop_oldscript)
        drop_cols.extend(drop_files)

        # logger.debug(list(df.columns))
        # logger.debug(drop_cols)
        # drop_cols = [c for c in df.columns if c.startswith('langscripts.')]
        df.drop(columns=drop_cols, inplace=True)

        return df

    def generate_xlsx(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        # df.drop([0], inplace=True)
        f_w = open(write_path, 'wb')
        df.to_excel(f_w, index=False, engine='xlsxwriter')

    def download_lexicon(lex_json, write_path,
                         output_format='xlsx'):
        file_ext_map = {'xlsx': '.xlsx'}

        # logger.debug(lex_json)
        metadata = lex_json[0]
        project = metadata['projectname']

        lexicon = lex_json[1:]
        # logger.debug(lexicon)
        if output_format == 'xlsx':
            file_ext = file_ext_map[output_format]
            write_file = os.path.join(write_path, 'lexicon_'+project+file_ext)
            generate_xlsx(write_file, lexicon)
        else:
            logger.debug('File type\t', output_format, '\tnot supported')
            logger.debug('Supported File Types', file_ext_map.keys())

    lexeme_dir = basedir
    working_dir = basedir+'/download'
    with open(os.path.join(lexeme_dir, 'lexemeEntry.json')) as f_r:
        lex = json.load(f_r)
        # logger.debug(lex)
        out_form = 'xlsx'
        download_lexicon(lex, working_dir, out_form)

    files = glob.glob(basedir+'/download/*')

    with ZipFile('download.zip', 'w') as zip:
        # writing each file one by one
        for file in files:
            zip.write(file, os.path.join(projectname, os.path.basename(file)))
    logger.debug('All files zipped successfully!')

    # deleting all files from storage
    for f in files:
        # logger.debug(f)
        os.remove(f)

    return send_file('../download.zip', as_attachment=True)
    # return 'OK'


# download route
@app.route('/downloadselectedlexeme', methods=['GET', 'POST'])
def downloadselectedlexeme():
    # getting the collections
    # collection containing projects name
    projects = mongo.db.projects
    # collection of users and their respective projects
    userprojects = mongo.db.userprojects
    # collection containing entry of each lexeme and its details
    lexemes = mongo.db.lexemes
    # sentences = mongo.db.sentences                          # collection containing entry of each sentence and its details
    # creating GridFS instance to get required files
    fs = gridfs.GridFS(mongo.db)

    ontolex = Namespace('http://www.w3.org/ns/lemon/ontolex#')
    lexinfo = Namespace('http://www.lexinfo.net/ontology/2.0/lexinfo#')
    dbpedia = Namespace('http://dbpedia.org/resource/')
    pwn = Namespace('http://wordnet-rdf.princeton.edu/rdf/lemma/')
    life = None

    lst = list()

    headwords = request.args.get('data')                   # data through ajax

    if headwords != None:
        headwords = eval(headwords)
    # logger.debug(f'{"="*80}\nheadwords from downloadselectedlexeme route:\n {headwords}\n{"="*80}')

    download_format = headwords['downloadFormat']
    # logger.debug(download_format)

    del headwords['downloadFormat']

    # logger.debug(f'{"="*80}\ndelete download format:\n {headwords}\n{"="*80}')

    activeprojectname = userprojects.find_one({'username': current_user.username})[
        'activeprojectname']
    lst.append({'projectname': activeprojectname})
    projectname = activeprojectname

    # for headword in headwords:
    #     lexeme = lexemes.find_one({'username' : current_user.username, 'projectname' : projectname, 'headword' : headword},\
    #                         {'_id' : 0, 'username' : 0, 'projectname' : 0})
    #     lst.append(lexeme)
    # for lexemeId in headwords.keys():
    #     lexeme = lexemes.find_one({'projectname' : projectname, 'lexemeId' : lexemeId},\
    #                         {'_id' : 0})
    #     lst.append(lexeme)

    for lexemeId in headwords.keys():
        lexeme = lexemes.find_one({'projectname': projectname, 'lexemeId': lexemeId},
                                  {'_id': 0})
        lst.append(lexeme)
        # save current user mutimedia files of each lexeme to local storage
        files = fs.find({'projectname': projectname, 'lexemeId': lexemeId})
        for file in files:
            name = file.filename
            # open(basedir+'/app/download/'+name, 'wb').write(file.read())
            open(os.path.join(basedir, 'download', name), 'wb').write(file.read())

    # Serializing json
    json_object = json.dumps(lst, indent=2, ensure_ascii=False)

    with open(basedir+"/lexemeEntry.json", "w") as outfile:
        outfile.write(json_object)

    # # writing to currentprojectname.json
    # with open(basedir+"/download/"+projectname+".json", "w") as outfile:
    #     outfile.write(json_object)

    def generate_json(lex_json):
        json_object = json.dumps(lex_json, indent=2, ensure_ascii=False)
        # writing to currentprojectname.json
        # with open(basedir+"/app/download/lexicon_"+activeprojectname+".json", "w") as outfile:
        with open(basedir+"/download/lexicon_"+activeprojectname+".json", "w") as outfile:
            outfile.write(json_object)

    # # def test():
    # #     g = Graph()
    # #     semweb = URIRef('http://dbpedia.org/resource/Semantic_Web')
    # #     type = g.value(semweb, RDFS.label)

    # #     g.add((
    # #         URIRef("http://example.com/person/nick"),
    # #         FOAF.givenName,
    # #         Literal("Nick", datatype=XSD.string)
    # #     ))

    # #     g.bind("foaf", FOAF)
    # #     g.bind("xsd", XSD)

    # #     logger.debug(g.serialize(format="turtle"))

    # def add_canonical_form(g_form, life, lex_entry, lex_item, ipa, dict_lang):
    #     # g_form = Graph()
    #     # g_form.bind("ontolex", ontolex)
    #     # g_form.bind("life", life)

    #     g_form.add((
    #         URIRef(life[lex_item+'_form']),
    #         RDF.type,
    #         ontolex.form
    #     ))

    #     g_form.add((
    #         URIRef(life[lex_item+'_form']),
    #         ontolex.phoneticRep,
    #         Literal(ipa, lang="ipa")
    #     ))

    #     headword_script = list(lex_entry['langscripts']['headwordscript'])[0]
    #     logger.debug('Headword script', headword_script)
    #     headword_lang = dict_lang+'-'+headword_script

    #     g_form.add((
    #         URIRef(life[lex_item+'_form']),
    #         ontolex.writtenRep,
    #         Literal(lex_item, lang=headword_lang)
    #     ))

    #     #If written reps are entered in other scripts, they are added
    #     other_scripts = lex_entry['langscripts']['lexemeformscripts']
    #     for other_script in other_scripts:
    #         lex_trans_forms = lex_entry['Lexeme Form']
    #         if other_script in lex_trans_forms:
    #             lex_trans = lex_trans_forms[other_script]
    #             g_form.add((
    #                 URIRef(life[lex_item+'_form']),
    #                 ontolex.writtenRep,
    #                 Literal(lex_trans, lang=dict_lang+'-'+other_script)
    #             ))

    # def add_definition(g_form, life, lex_entry, lex_item, sense_defn):
    #     defn_langs = lex_entry['langscripts']['glosslangs']
    #     for defn_lang in defn_langs:
    #         if defn_lang in sense_defn:
    #             lex_defn = sense_defn[defn_lang]
    #             g_form.add((
    #                 URIRef(life[lex_item]),
    #                 ontolex.denotes,
    #                 URIRef(life[lex_item+'_definition'])
    #             ))

    #             g_form.add((
    #                 URIRef(life[lex_item+'_definition']),
    #                 SKOS.definition,
    #                 Literal(lex_defn, lang=defn_lang)
    #             ))

    # def add_example(g_form, life, lex_item, example, ex_lang):
    #     g_form.add((
    #         URIRef(life[lex_item]),
    #         SKOS.example,
    #         Literal(example, lang=ex_lang)
    #     ))

    # # def add_other_forms(g_other_form, life, lex_entry, lex_item, other_form, dict_lang):
    # #     # g_other_form = Graph()
    # #     # g_other_form.bind("ontolex", ontolex)
    # #     # g_other_form.bind("life", life)

    # #     g_other_form.add((
    # #         URIRef(life[lex_item+'_otherForm']),
    # #         RDF.type,
    # #         ontolex.form
    # #     ))

    # #     g_other_form.add((
    # #         URIRef(life[lex_item+'_otherForm']),
    # #         ontolex.writtenRep,
    # #         Literal(other_form, lang=dict_lang)
    # #     ))

    # def add_sense(g_lex, life, lex_entry, sense_entry, lex_sense):
    #     g_lex.add((
    #         sense_entry,
    #         RDF.type,
    #         ontolex.LexicalSense
    #     ))

    #     if dbpedia_exists(lex_sense):
    #         g_lex.add((
    #             life[lex_entry],
    #             ontolex.denotes,
    #             dbpedia[lex_sense.capitalize()]
    #         ))

    #         g_lex.add((
    #             sense_entry,
    #             ontolex.reference,
    #             dbpedia[lex_sense.capitalize()]
    #         ))

    #     g_lex.add((
    #         sense_entry,
    #         ontolex.isSenseOf,
    #         life[lex_entry]
    #     ))

    #     wordnet_code = get_wordnet_code(lex_sense)
    #     if wordnet_code != '':
    #         g_lex.add((
    #             sense_entry,
    #             ontolex.isLexicalisedSenseOf,
    #             pwn[wordnet_code]
    #         ))
    #         g_lex.add((
    #             life[lex_entry],
    #             ontolex.evokes,
    #             pwn[wordnet_code]
    #         ))

    #     g_lex.add((
    #         sense_entry,
    #         ontolex.isSenseOf,
    #         life[lex_entry]
    #     ))

    #     #Creating dbpedia entry
    #     g_lex.add((
    #         dbpedia[lex_sense.capitalize()],
    #         ontolex.concept,
    #         pwn[wordnet_code]
    #     ))

    #     g_lex.add((
    #         dbpedia[lex_sense.capitalize()],
    #         ontolex.isReferenceOf,
    #         sense_entry
    #     ))

    #     g_lex.add((
    #         dbpedia[lex_sense.capitalize()],
    #         ontolex.isDenotedBy,
    #         ontolex.LexicalConcept
    #     ))

    #     #Creating WordNet entry
    #     g_lex.add((
    #         pwn[wordnet_code],
    #         RDF.type,
    #         life[lex_entry]
    #     ))

    #     g_lex.add((
    #         pwn[wordnet_code],
    #         ontolex.isEvokedBy,
    #         life[lex_entry]
    #     ))

    #     g_lex.add((
    #         pwn[wordnet_code],
    #         ontolex.lexicalizedSense,
    #         sense_entry
    #     ))

    #     g_lex.add((
    #         pwn[wordnet_code],
    #         ontolex.isConceptOf,
    #         dbpedia[lex_sense.capitalize()]
    #     ))

    # def get_wordnet_code(lex_gloss):
    #     query = '''
    #     ASK WHERE {
    #     {<my-specific-URI> ?p ?o . }
    #     UNION
    #     {?s ?p <my-specific-URI> . }
    #     }
    #     '''
    #     return lex_gloss

    # def dbpedia_exists(lex_gloss):
    #     query = '''
    #     ASK WHERE {
    #     {<my-specific-URI> ?p ?o . }
    #     UNION
    #     {?s ?p <my-specific-URI> . }
    #     }
    #     '''
    #     return True

    # def json_to_rdf_lexicon(g_lex, lex_entry, domain_name,
    #                         project, output_format='turtle'):

    #     lex_item = lex_entry['headword']
    #     lex_pos = lex_entry['grammaticalcategory']
    #     # can_form = lex_item
    #     lex_pron = lex_entry['Pronunciation']
    #     lex_sense = lex_entry['SenseNew']
    #     dict_lang = lex_entry['langscripts']['langcode']

    #     # ontolex = URIRef('http://www.w3.org/ns/lemon/ontolex#')
    #     # lexinfo = URIRef('http://www.lexinfo.net/ontology/2.0/lexinfo#')

    #     life = Namespace(domain_name+'/'+project + '/word/')

    #     g_lex.bind("ontolex", ontolex)
    #     g_lex.bind("lexinfo", lexinfo)
    #     g_lex.bind("skos", SKOS)
    #     g_lex.bind("life", life)
    #     g_lex.bind("pwnlemma", pwn)
    #     g_lex.bind("dbpedia", dbpedia)

    #     g_lex.add((
    #         URIRef(life[lex_item]),
    #         RDF.type,
    #         lexinfo.LexicalEntry
    #     ))

    #     g_lex.add((
    #         URIRef(life[lex_item]),
    #         lexinfo.partOfSpeech,
    #         lexinfo[lex_pos]
    #     ))

    #     # g_lex.add((
    #     #     URIRef(life[lex_item]),
    #     #     ontolex.lexicalForm,
    #     #     URIRef(life[lex_item+'_form'])
    #     # ))

    #     g_lex.add((
    #         URIRef(life[lex_item]),
    #         ontolex.canonicalForm,
    #         URIRef(life[lex_item+'_form'])
    #     ))

    #     # Add graph for the canonical form
    #     add_canonical_form(g_lex, life, lex_entry, lex_item, lex_pron, dict_lang)

    #     for i in range(1, len(lex_sense)):
    #         sense_gloss = lex_sense['Sense '+str(i)]["Gloss"]["eng"]
    #         sense_defn = lex_sense['Sense '+str(i)]["Definition"]
    #         sense_ex = lex_sense['Sense '+str(i)]["Example"]

    #         sense_entry = life[lex_item+'_sense'+str(i)]
    #         g_lex.add((
    #             URIRef(life[lex_item]),
    #             ontolex.sense,
    #             URIRef(sense_entry)
    #         ))
    #         add_sense(g_lex, life, lex_item, sense_entry, sense_gloss)
    #         add_definition(g_lex, life, lex_entry, lex_item, sense_defn)
    #         add_example(g_lex, life, lex_item, sense_ex, dict_lang)

    # def preprocess_csv_excel(lexicon):
    #     df = pd.json_normalize(lexicon)
    #     columns = df.columns
    #     drop_cols = [c for c in df.columns if c.startswith('langscripts.')]
    #     drop_cols.append ('lexemedeleteFLAG')
    #     drop_cols.append ('grammaticalcategory')
    #     drop_cols.append ('projectname')

    #     if 'gloss' in columns:
    #         drop_cols.append ('gloss')
    #     drop_oldsense = [c for c in df.columns if c.startswith('Sense.')]
    #     drop_oldvariant = [c for c in df.columns if c.startswith('Variant.')]
    #     drop_oldallomorph = [c for c in df.columns if c.startswith('Allomorph.')]
    #     drop_oldscript = [c for c in df.columns if c.startswith('Lexeme Form Script')]
    #     drop_files = [c for c in df.columns if c.startswith('filesname.')]

    #     drop_cols.extend(drop_oldsense)
    #     drop_cols.extend(drop_oldvariant)
    #     drop_cols.extend(drop_oldallomorph)
    #     drop_cols.extend(drop_oldscript)
    #     drop_cols.extend(drop_files)

    #     df.drop(columns=drop_cols, inplace=True)

    #     return df

    # def generate_rdf(write_path, lexicon, domain_name, project, rdf_format):
    #     g_lex = Graph()

    #     for lex_entry in lexicon:
    #         json_to_rdf_lexicon(g_lex, lex_entry,
    #                         domain_name, project, rdf_format)

    #     with open (write_path, 'wb') as f_w:
    #         rdf_out = g_lex.serialize(format=rdf_format)
    #         f_w.write(rdf_out)

    # def generate_csv(write_path, lexicon):
    #     df = preprocess_csv_excel(lexicon)
    #     with open (write_path, 'w') as f_w:
    #         df.to_csv(f_w, index=False)

    # def generate_xlsx(write_path, lexicon):
    #     df = preprocess_csv_excel(lexicon)
    #     f_w = open (write_path, 'wb')
    #     df.to_excel(f_w, index=False, engine='xlsxwriter')

    # def generate_ods(write_path, lexicon):
    #     df = preprocess_csv_excel(lexicon)
    #     f_w = open (write_path, 'wb')
    #     df.to_excel(f_w, index=False, engine='openpyxl')

    # def generate_html(write_path, lexicon):
    #     df = preprocess_csv_excel(lexicon)
    #     with open (write_path, 'w') as f_w:
    #         df.to_html(f_w, index=False)

    # def generate_latex(write_path, lexicon):
    #     df = preprocess_csv_excel(lexicon)
    #     with open (write_path, 'w') as f_w:
    #         df.to_latex(f_w, index=False)

    # def generate_markdown(write_path, lexicon):
    #     df = preprocess_csv_excel(lexicon)
    #     with open (write_path, 'w') as f_w:
    #         df.to_markdown(f_w, index=False)

    # def generate_pdf(write_path, lexicon, project):
    #     return None

    # def download_lexicon(lex_json, write_path,
    #     output_format='rdf', rdf_format='turtle'):
    #     file_ext_map = {'turtle': '.ttl', 'n3': '.n3',
    #     'ntriples': '.nt', 'rdfxml': '.rdf', 'json': '.json', 'csv': '.csv',
    #     'xlsx': '.xlsx', 'pdf': '.pdf', 'html': '.html', 'latex': '.tex',
    #     'markdown': '.md', 'ods': '.ods'}

    #     domain_name = 'http://lifeapp.in'

    #     logger.debug(lex_json)
    #     metadata = lex_json[0]
    #     project = metadata['projectname']

    #     lexicon = lex_json[1:]

    #     if (rdf_format in file_ext_map) or (output_format in file_ext_map):
    #         if output_format == 'rdf':
    #             file_ext = file_ext_map[rdf_format]
    #             write_file = os.path.join(write_path, 'lexicon_'+project+'_'+output_format+file_ext)
    #             generate_rdf(write_file, lexicon, domain_name, project, rdf_format)
    #         else:
    #             file_ext = file_ext_map[output_format]
    #             write_file = os.path.join(write_path, 'lexicon_'+project+file_ext)
    #             if output_format == 'csv':
    #                 generate_csv(write_file, lexicon)
    #             elif output_format == 'xlsx':
    #                 generate_xlsx(write_file, lexicon)
    #             elif output_format == 'pdf':
    #                 generate_pdf(write_file, lexicon)
    #             elif output_format == 'markdown':
    #                 generate_markdown(write_file, lexicon)
    #             elif output_format == 'html':
    #                 generate_html(write_file, lexicon)
    #             elif output_format == 'latex':
    #                 generate_latex(write_file, lexicon)
    #             elif output_format == 'ods':
    #                 generate_ods(write_file, lexicon)
    #             elif output_format == 'json':
    #                 generate_json(lex_json)
    #     else:
    #         logger.debug('File type\t', output_format, '\tnot supported')
    #         logger.debug('Supported File Types', file_ext_map.keys())

    def test():
        g = Graph()
        semweb = URIRef('http://dbpedia.org/resource/Semantic_Web')
        type = g.value(semweb, RDFS.label)

        g.add((
            URIRef("http://example.com/person/nick"),
            FOAF.givenName,
            Literal("Nick", datatype=XSD.string)
        ))

        g.bind("foaf", FOAF)
        g.bind("xsd", XSD)

        logger.debug(g.serialize(format="turtle"))

    def add_canonical_form(g_form, life, lex_entry, lex_item, enc_lex_form, ipa, dict_lang):
        # g_form = Graph()
        # g_form.bind("ontolex", ontolex)
        # g_form.bind("life", life)

        g_form.add((
            URIRef(life[enc_lex_form]),
            RDF.type,
            ontolex.form
        ))

        g_form.add((
            URIRef(life[enc_lex_form]),
            ontolex.phoneticRep,
            Literal(ipa, lang="ipa")
        ))

        headword_script = list(lex_entry['langscripts']['headwordscript'])[0]
        logger.debug('Headword script', headword_script)
        headword_lang = dict_lang+'-'+headword_script

        g_form.add((
            URIRef(life[enc_lex_form]),
            ontolex.writtenRep,
            Literal(lex_item, lang=headword_lang)
        ))

        # If written reps are entered in other scripts, they are added
        other_scripts = lex_entry['langscripts']['lexemeformscripts']
        for other_script in other_scripts:
            lex_trans_forms = lex_entry['Lexeme Form']
            if other_script in lex_trans_forms:
                lex_trans = lex_trans_forms[other_script]
                g_form.add((
                    URIRef(life[enc_lex_form]),
                    ontolex.writtenRep,
                    Literal(lex_trans, lang=dict_lang+'-'+other_script)
                ))

    def add_definition(g_form, life, lex_entry, enc_lex_item, enc_lex_defn, sense_defn):
        defn_langs = lex_entry['langscripts']['glosslangs']
        defn_langs = [x.casefold() for x in defn_langs]
        for defn_lang in defn_langs:
            if defn_lang in sense_defn:
                lex_defn = sense_defn[defn_lang].strip()
                if lex_defn != '':
                    g_form.add((
                        URIRef(life[enc_lex_item]),
                        ontolex.denotes,
                        URIRef(life[enc_lex_defn])
                    ))

                    g_form.add((
                        URIRef(life[enc_lex_defn]),
                        SKOS.definition,
                        Literal(lex_defn, lang=defn_lang)
                    ))

    def add_example(g_form, life, enc_lex_item, example, ex_lang):
        if example != '':
            g_form.add((
                URIRef(life[enc_lex_item]),
                SKOS.example,
                Literal(example, lang=ex_lang)
            ))

    def add_other_forms(g_other_form, life, lex_entry, enc_otherform, other_form, dict_lang):
        # g_other_form = Graph()
        # g_other_form.bind("ontolex", ontolex)
        # g_other_form.bind("life", life)

        g_other_form.add((
            URIRef(life[enc_otherform]),
            RDF.type,
            ontolex.form
        ))

        g_other_form.add((
            URIRef(life[enc_otherform]),
            ontolex.writtenRep,
            Literal(other_form, lang=dict_lang)
        ))

    def add_sense(g_lex, life, full_lex_entry, lex_entry, sense_entry, lex_senses):
        sense_langs = full_lex_entry['langscripts']['glosslangs']
        sense_langs = [x.casefold() for x in sense_langs]

        # this is mainly used for mapping to english dbpedia/wikipedia entries
        lex_sense = lex_senses['eng'].strip()
        for sense_lang in sense_langs:
            if sense_lang in lex_senses:
                sense_entry = lex_senses[sense_lang].strip()
                g_lex.add((
                    Literal(sense_entry, lang=sense_lang),
                    RDF.type,
                    ontolex.LexicalSense
                ))

                # if sense_lang == 'eng':
                if lex_sense != '':
                    if dbpedia_exists(lex_sense):
                        g_lex.add((
                            life[lex_entry],
                            ontolex.denotes,
                            dbpedia[lex_sense.capitalize()]
                        ))

                        g_lex.add((
                            Literal(sense_entry, lang=sense_lang),
                            ontolex.reference,
                            dbpedia[lex_sense.capitalize()]
                        ))

                    g_lex.add((
                        Literal(sense_entry, lang=sense_lang),
                        ontolex.isSenseOf,
                        life[lex_entry]
                    ))

                    wordnet_code = get_wordnet_code(lex_sense)
                    if wordnet_code != '':
                        g_lex.add((
                            Literal(sense_entry, lang=sense_lang),
                            ontolex.isLexicalisedSenseOf,
                            pwn[wordnet_code]
                        ))
                        g_lex.add((
                            life[lex_entry],
                            ontolex.evokes,
                            pwn[wordnet_code]
                        ))

                    g_lex.add((
                        Literal(sense_entry, lang=sense_lang),
                        ontolex.isSenseOf,
                        life[lex_entry]
                    ))

                    # Creating dbpedia entry

                    g_lex.add((
                        dbpedia[lex_sense.capitalize()],
                        ontolex.concept,
                        pwn[wordnet_code]
                    ))

                    g_lex.add((
                        dbpedia[lex_sense.capitalize()],
                        ontolex.isReferenceOf,
                        Literal(sense_entry, lang=sense_lang)
                    ))

                    g_lex.add((
                        dbpedia[lex_sense.capitalize()],
                        ontolex.isDenotedBy,
                        ontolex.LexicalConcept
                    ))

                    # Creating WordNet entry
                    g_lex.add((
                        pwn[wordnet_code],
                        RDF.type,
                        life[lex_entry]
                    ))

                    g_lex.add((
                        pwn[wordnet_code],
                        ontolex.isEvokedBy,
                        life[lex_entry]
                    ))

                    g_lex.add((
                        pwn[wordnet_code],
                        ontolex.lexicalizedSense,
                        Literal(sense_entry, lang=sense_lang)
                    ))

                    g_lex.add((
                        pwn[wordnet_code],
                        ontolex.isConceptOf,
                        dbpedia[lex_sense.capitalize()]
                    ))

    def get_wordnet_code(lex_gloss):
        query = '''
        ASK WHERE {
        {<my-specific-URI> ?p ?o . }
        UNION
        {?s ?p <my-specific-URI> . }
        }
        '''
        return lex_gloss

    def dbpedia_exists(lex_gloss):
        query = '''
        ASK WHERE {
        {<my-specific-URI> ?p ?o . }
        UNION
        {?s ?p <my-specific-URI> . }
        }
        '''
        return True

    def json_to_rdf_lexicon(g_lex, lex_entry, domain_name,
                            project, output_format='turtle'):

        lex_item = lex_entry['headword'].strip()
        enc_lex_item = requote_uri(lex_item)
        enc_lex_form = requote_uri(lex_item+'_form')
        enc_lex_def = requote_uri(lex_item+'_definition')
        enc_otherform = requote_uri(lex_item+'_otherForm')

        lex_pos = lex_entry['grammaticalcategory'].strip()
        enc_lex_pos = requote_uri(lex_pos)

        # can_form = lex_item
        lex_pron = lex_entry['Pronunciation'].strip()
        enc_lex_pron = requote_uri(lex_pron)

        lex_sense = lex_entry['SenseNew']
        # logger.debug("Entry", lex_entry)
        dict_lang = lex_entry['langscripts']['langcode'].strip()

        # ontolex = URIRef('http://www.w3.org/ns/lemon/ontolex#')
        # lexinfo = URIRef('http://www.lexinfo.net/ontology/2.0/lexinfo#')

        enc_project = requote_uri(project.strip())
        life = Namespace(domain_name+'/'+enc_project + '/word/')

        g_lex.bind("ontolex", ontolex)
        g_lex.bind("lexinfo", lexinfo)
        g_lex.bind("skos", SKOS)
        g_lex.bind("life", life)
        g_lex.bind("pwnlemma", pwn)
        g_lex.bind("dbpedia", dbpedia)

        g_lex.add((
            URIRef(life[enc_lex_item]),
            RDF.type,
            lexinfo.LexicalEntry
        ))

        g_lex.add((
            URIRef(life[enc_lex_item]),
            lexinfo.partOfSpeech,
            lexinfo[lex_pos]
        ))

        # g_lex.add((
        #     URIRef(life[lex_item]),
        #     ontolex.lexicalForm,
        #     URIRef(life[lex_item+'_form'])
        # ))

        g_lex.add((
            URIRef(life[enc_lex_item]),
            ontolex.canonicalForm,
            URIRef(life[enc_lex_form])
        ))

        # Add graph for the canonical form
        add_canonical_form(g_lex, life, lex_entry,
                           lex_item, enc_lex_form, lex_pron, dict_lang)

        for i in range(1, len(lex_sense)+1):
            sense_gloss = lex_sense['Sense '+str(i)]["Gloss"]
            sense_defn = lex_sense['Sense ' +
                                   str(i)]["Definition"]
            sense_ex = lex_sense['Sense '+str(i)]["Example"].strip()

            sense_entry = life[lex_item+'_sense'+str(i)].strip()
            enc_sense_entry = requote_uri(sense_entry)
            g_lex.add((
                URIRef(life[enc_lex_item]),
                ontolex.sense,
                URIRef(enc_sense_entry)
            ))
            add_sense(g_lex, life, lex_entry, enc_lex_item,
                      sense_entry, sense_gloss)
            add_definition(g_lex, life, lex_entry, enc_lex_item,
                           enc_lex_def, sense_defn)
            add_example(g_lex, life, enc_lex_item, sense_ex, dict_lang)

    def generate_rdf(write_path, lexicon, domain_name, project, rdf_format):
        g_lex = Graph()

        for lex_entry in lexicon:
            json_to_rdf_lexicon(g_lex, lex_entry,
                                domain_name, project, rdf_format)

        # with open (write_path, 'w') as f_w:
        # rdf_out = g_lex.serialize(format=rdf_format, destination=write_path)
        g_lex.serialize(format=rdf_format, destination=write_path)
        # logger.debug(type(rdf_out))
        # f_w.write(rdf_out)

    def preprocess_csv_excel(lexicon):
        df = pd.json_normalize(lexicon)
        columns = df.columns
        drop_cols = [c for c in df.columns if c.startswith('langscripts.')]
        drop_cols.append('lexemedeleteFLAG')
        drop_cols.append('grammaticalcategory')
        drop_cols.append('projectname')

        if 'gloss' in columns:
            drop_cols.append('gloss')
        drop_oldsense = [c for c in df.columns if c.startswith('Sense.')]
        drop_oldvariant = [c for c in df.columns if c.startswith('Variant.')]
        drop_oldallomorph = [
            c for c in df.columns if c.startswith('Allomorph.')]
        drop_oldscript = [
            c for c in df.columns if c.startswith('Lexeme Form Script')]
        drop_files = [c for c in df.columns if c.startswith('filesname.')]

        drop_cols.extend(drop_oldsense)
        drop_cols.extend(drop_oldvariant)
        drop_cols.extend(drop_oldallomorph)
        drop_cols.extend(drop_oldscript)
        drop_cols.extend(drop_files)

        df.drop(columns=drop_cols, inplace=True)

        return df

    def generate_csv(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        with open(write_path, 'w') as f_w:
            df.to_csv(f_w, index=False)

    def generate_xlsx(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        f_w = open(write_path, 'wb')
        df.to_excel(f_w, index=False, engine='xlsxwriter')

    def generate_ods(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        with open(write_path, 'w') as f_w:
            df.to_excel(f_w, index=False, engine='openpyxl')

    def generate_html(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        with open(write_path, 'w') as f_w:
            df.to_html(f_w, index=False)

    def generate_latex(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        with open(write_path, 'w') as f_w:
            df.to_latex(f_w, index=False)

    def generate_formatted_latex(write_path,
                                 lexicon,
                                 lexicon_df,
                                 project,
                                 editors=['Editor 1', 'Editor 2', 'Editor 3'],
                                 co_editors=['Co-ed 1', 'Co-ed 2', 'Co-ed 3'],
                                 metadata=['Scheme for Protection and Preservation of Indian Languages',
                                           'Central Institute of Indian Languages'],
                                 fields=[],
                                 # lexemeformscripts.ipa.., glosslangs.hin..
                                 dict_headword='headword',
                                 formatting_options={
            'documentclass': 'article',
            'document_options': 'a4paper, 12pt, twoside, xelatex',
                                     'geometry_options': {
                                         "top": "3.5cm",
                                         "bottom": "3.5cm",
                                         "left": "3.5cm",
                                         "right": "3.5cm",
                                         "columnsep": "30pt",
                                         "includeheadfoot": True
                                     }
                                     }):
        # geometry_options_1 = {"tmargin": "1cm", "lmargin": "10cm"}
        # lg.generate_formatted_latex(write_path, lexicon, project)
        lg.generate_formatted_latex(
            write_path, lexicon, lexicon_df, project, fields=fields)

    def generate_markdown(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        with open(write_path, 'w') as f_w:
            df.to_markdown(f_w, index=False)

    # write_file, lexicon, lexicon_df, project, fields=cur_fields
    def generate_pdf(write_path,
                     lexicon,
                     lexicon_df,
                     project,
                     editors=['Editor 1', 'Editor 2', 'Editor 3'],
                     co_editors=['Co-ed 1', 'Co-ed 2', 'Co-ed 3'],
                     metadata=['Scheme for Protection and Preservation of Indian Languages',
                               'Central Institute of Indian Languages'],
                     fields=[],
                     # lexemeformscripts.ipa.., glosslangs.hin..
                     dict_headword='headword',
                     formatting_options={
            'documentclass': 'article',
            'document_options': 'a4paper, 12pt, twoside, xelatex',
                         'geometry_options': {
                             "top": "3.5cm",
                             "bottom": "3.5cm",
                             "left": "3.5cm",
                             "right": "3.5cm",
                             "columnsep": "30pt",
                             "includeheadfoot": True
                         }
                         }):
        # lg.generate_formatted_latex(write_path, lexicon, project)
        lg.generate_formatted_latex(
            write_path, lexicon, lexicon_df, project, fields=fields)

        # return True

    # “xml”, “n3”, “turtle”, “nt”, “pretty-xml”, “trix”, “trig” and “nquads”
    def download_lexicon(lex_json, write_path,
                         output_format='rdf', rdf_format='turtle', fields=[]):
        file_ext_map = {'turtle': '.ttl', 'n3': '.n3',
                        'nt': '.nt', 'xml': '.rdf', 'pretty-xml': '.rdfp', 'trix': '.trix',
                        'trig': '.trig', 'nquads': 'nquad', 'json': '.json', 'csv': '.csv',
                        'xlsx': '.xlsx', 'pdf': '', 'html': '.html', 'latex_dict': '',
                        'markdown': '.md', 'ods': '.ods'}

        domain_name = 'http://lifeapp.in'

        metadata = lex_json[0]
        project = metadata['projectname']

        lexicon = lex_json[1:]

        # fields = ['headword', 'Lexeme Form.ipa', 'Lexeme Form.Deva', 'grammaticalcategory', ['SenseNew.Gloss.hin', 'SenseNew.Gloss.eng', 'SenseNew.Definition.hin', 'SenseNew.Definition.eng', 'SenseNew.Example']]
        if len(fields) == 0:
            lexicon_df = pd.json_normalize(lexicon)
            columns = lexicon_df.columns
            cur_fields = ['headword', 'Pronunciation']
            # sense_fields = ['', '', '']
            sense_fields = []
            for field in columns:
                if 'SenseNew' in field:
                    if 'Gloss' in field or 'Definition' in field or 'Example' in field:
                        sense_fields.append(field)
                elif 'Lexeme' in field:
                    cur_fields.append(field)
            cur_fields.append('grammaticalcategory')
            cur_fields.extend(sense_fields)
        else:
            cur_fields = fields

        if (rdf_format in file_ext_map) or (output_format in file_ext_map):
            if output_format == 'rdf':
                file_ext = file_ext_map[rdf_format]
                write_file = os.path.join(
                    write_path, 'lexicon_'+project+'_'+output_format+file_ext)
                generate_rdf(write_file, lexicon,
                             domain_name, project, rdf_format)
            else:
                file_ext = file_ext_map[output_format]
                write_file = os.path.join(
                    write_path, 'lexicon_'+project+file_ext)
                if output_format == 'csv':
                    generate_csv(write_file, lexicon)
                elif output_format == 'xlsx':
                    generate_xlsx(write_file, lexicon)
                elif output_format == 'pdf':
                    # logger.debug("...................cur_fields.................")
                    # logger.debug(cur_fields)
                    # generate_pdf(write_file, lexicon, project, fields=[], formatting_options={})
                    # generate_pdf(write_file, lexicon, lexicon_df, project, fields=cur_fields)
                    lg.generate_formatted_latex(
                        write_file, lexicon, lexicon_df, project, fields=cur_fields)
                elif output_format == 'markdown':
                    generate_markdown(write_file, lexicon)
                elif output_format == 'html':
                    generate_html(write_file, lexicon)
                elif output_format == 'latex':
                    generate_latex(write_file, lexicon)
                elif output_format == 'ods':
                    generate_ods(write_file, lexicon)
                elif output_format == 'latex_dict':
                    # logger.debug("...................cur_fields.................")
                    # logger.debug(cur_fields)
                    # generate_formatted_latex(write_file, lexicon, project, fields=[], formatting_options={})
                    # generate_formatted_latex(write_file, lexicon, project, fields=cur_fields, formatting_options={})
                    # generate_formatted_latex(
                    #     write_file, lexicon, lexicon_df, project, fields=cur_fields)
                    lg.generate_formatted_latex(
                        write_file, lexicon, lexicon_df, project, fields=cur_fields)
                elif output_format == 'json':
                    generate_json(lex_json)
        else:
            logger.debug('File type\t', output_format, '\tnot supported')
            logger.debug('Supported File Types', file_ext_map.keys())

    lexeme_dir = basedir
    # working_dir = basedir+'/app/download'
    working_dir = basedir+'/download'
    with open(os.path.join(lexeme_dir, 'lexemeEntry.json')) as f_r:
        lex = json.load(f_r)
        out_form = download_format
        # logger.debug(out_form)
        if ('rdf' in out_form):
            rdf_format = out_form[3:]
            out_form = 'rdf'
            # logger.debug(rdf_format)
            download_lexicon(lex, working_dir, out_form, rdf_format=rdf_format)
        else:
            download_lexicon(lex, working_dir, out_form)

    # save current user mutimedia files of each lexeme to local storage
    # files = fs.find({'username' : current_user.username, 'projectname' : projectname, 'headword' : headword})
    # for file in files:
    #     name = file.filename
    #     open(basedir+'/download/'+name, 'wb').write(file.read())

    # printing the list of all files to be zipped
    # files = glob.glob(basedir+'/app/download/*')
    files = glob.glob(basedir+'/download/*')

    with ZipFile('download.zip', 'w') as zip:
        # writing each file one by one
        for file in files:
            zip.write(file, os.path.join(projectname, os.path.basename(file)))
    logger.debug('All files zipped successfully!')

    # deleting all files from storage
    for f in files:
        # logger.debug(f)
        os.remove(f)

    # return send_file('../download.zip', as_attachment=True)
    return 'OK'

# download project route


@app.route('/downloadproject', methods=['GET', 'POST'])
def downloadproject():
    # getting the collections
    # collection containing projects name
    # projects = mongo.db.projects
    # collection of users and their respective projects
    # userprojects = mongo.db.userprojects
    # collection containing entry of each lexeme and its details
    lexemes = mongo.db.lexemes
    # collection containing entry of each sentence and its details
    sentences = mongo.db.sentences
    # creating GridFS instance to get required files
    fs = gridfs.GridFS(mongo.db)

    userprojects, userlogin, projects, lexemes, sentences, questionnaires, transcriptions = getdbcollections.getdbcollections(
        mongo, 'userprojects', 'userlogin', 'projects', 'lexemes', 'sentences',
        'questionnaires', 'transcriptions')
    current_username = getcurrentusername.getcurrentusername()
    logger.debug('USERNAME: ', current_username)
    # usertype = userdetails.get_user_type(
    #     userlogin, current_username)
    # currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(
    #     current_username, userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(
        userprojects, current_username, activeprojectname)

    if os.path.exists(basedir+"/download"):
        shutil.rmtree(basedir+"/download")
    os.mkdir(basedir+"/download")

    # if shareinfo['sharemode'] >= 1:
    if ('downloadchecked' in shareinfo and shareinfo['downloadchecked'] == 'true'):
        project_type = getprojecttype.getprojecttype(
            projects, activeprojectname)
        lst = list()

        if project_type == 'questionnaire':
            all_questions = questionnaires.find({'projectname': activeprojectname, 'quesdeleteFLAG': 0},
                                                {'_id': 0})
            for cur_ques in all_questions:
                lst.append(cur_ques)

            json_object = json.dumps(lst, indent=2, ensure_ascii=False)

            with open(basedir+"/download/questionnaire_"+activeprojectname+".json", "w") as outfile:
                outfile.write(json_object)

        elif project_type == 'transcription':
            all_transcriptions = transcriptions.find({'projectname': activeprojectname,
                                                      'transcriptionFLAG': 1, 'audiodeleteFLAG': 0}, {'_id': 0, 'audioMetadata.audiowaveform.data': 0})
            for cur_trans in all_transcriptions:
                lst.append(cur_trans)

            json_object = json.dumps(lst, indent=2, ensure_ascii=False)

            with open(basedir+"/download/transcription_"+activeprojectname+".json", "w") as outfile:
                outfile.write(json_object)

        elif project_type == '':
            projectname = activeprojectname

            for lexeme in lexemes.find({'projectname': activeprojectname, 'lexemedeleteFLAG': 0},
                                       {'_id': 0}):
                lst.append(lexeme)
                # save current user mutimedia files of each lexeme to local storage
                # logger.debug(lst)
            for lexeme in lst:
                for lexkey, lexvalue in lexeme.items():
                    if (lexkey == 'lexemeId'):
                        files = fs.find(
                            {'projectname': projectname, 'lexemeId': lexvalue})
                        for file in files:
                            name = file.filename
                            # logger.debug(f'{"#"*80}')
                            # logger.debug(basedir+'/app/download/'+name)
                            # logger.debug(f'{"#"*80}')
                            # open(basedir+'/app/download/'+name, 'wb').write(file.read())
                            open(basedir+'/download/'+name,
                                 'wb').write(file.read())

            # Serializing json
            json_object = json.dumps(lst, indent=2, ensure_ascii=False)

            # writing to currentprojectname.json
            # logger.debug(f'{"#"*80}')
            # logger.debug(basedir+"/app/download/lexicon_"+activeprojectname+".json")
            # logger.debug(f'{"#"*80}')
            # with open(basedir+"/app/download/lexicon_"+activeprojectname+".json", "w") as outfile:
            with open(basedir+"/download/lexicon_"+activeprojectname+".json", "w") as outfile:
                outfile.write(json_object)

            # get all sentences of the activeprojectname
            sentenceLst = []
            for sentence in sentences.find({'projectname': activeprojectname, 'sentencedeleteFLAG': 0},
                                           {'_id': 0}):
                sentenceLst.append(sentence)

            # logger.debug(sentenceLst)
                # save current user mutimedia files of each lexeme to local storage
            for sentence in sentenceLst:
                for sentkey, sentvalue in sentence.items():
                    if (sentkey == 'sentenceId'):
                        files = fs.find(
                            {'projectname': projectname, 'sentenceId': sentvalue})
                        for file in files:
                            name = file.filename
                            open(basedir+'/download/'+name,
                                 'wb').write(file.read())

            # Serializing json
            json_object = json.dumps(sentenceLst, indent=2, ensure_ascii=False)

            # writing to currentprojectname.json
            # with open(basedir+"/app/download/sentence_"+activeprojectname+".json", "w") as outfile:
            with open(basedir+"/download/sentence_"+activeprojectname+".json", "w") as outfile:
                outfile.write(json_object)

        # printing the list of all files to be zipped
        # files = glob.glob(basedir+'/app/download/*')
        files = glob.glob(basedir+'/download/*')

        with ZipFile('download.zip', 'w') as zip:
            # writing each file one by one
            for file in files:
                zip.write(file, os.path.join(
                    projectname, os.path.basename(file)))
        logger.debug('All files zipped successfully!')

        # # deleting all files from storage
        # for f in files:
        #     # logger.debug(files)
        #     os.remove(f)

        return send_file('../download.zip', as_attachment=True)
    else:
        return 'OK'

# download dictionary route


@app.route('/downloaddictionary', methods=['GET', 'POST'])
def downloaddictionary():
    # getting the collections
    # collection containing projects name
    projects = mongo.db.projects
    # collection of users and their respective projects
    userprojects = mongo.db.userprojects
    # collection containing entry of each lexeme and its details
    lexemes = mongo.db.lexemes
    # sentences = mongo.db.sentences                          # collection containing entry of each sentence and its details
    # creating GridFS instance to get required files
    fs = gridfs.GridFS(mongo.db)
    lst = list()
    download_format = 'pdf'
    activeprojectname = userprojects.find_one({'username': current_user.username})[
        'activeprojectname']
    lst.append({'projectname': activeprojectname})
    projectname = activeprojectname

    for lexeme in lexemes.find({'projectname': activeprojectname, 'lexemedeleteFLAG': 0},
                               {'_id': 0}):
        if (len(lexeme['headword']) != 0):
            lst.append(lexeme)
        # # save current user mutimedia files of each lexeme to local storage
        # files = fs.find({'projectname' : projectname, 'lexemeId' : lexemeId})
        # for file in files:
        #     name = file.filename
        #     # open(basedir+'/app/download/'+name, 'wb').write(file.read())
        #     open(os.path.join(basedir,'download', name), 'wb').write(file.read())

    # Serializing json
    json_object = json.dumps(lst, indent=2, ensure_ascii=False)

    with open(basedir+"/lexemeEntry.json", "w") as outfile:
        outfile.write(json_object)

    def preprocess_csv_excel(lexicon):
        df = pd.json_normalize(lexicon)
        columns = df.columns
        drop_cols = [c for c in df.columns if c.startswith('langscripts.')]
        drop_cols.append('lexemedeleteFLAG')
        drop_cols.append('grammaticalcategory')
        drop_cols.append('projectname')

        if 'gloss' in columns:
            drop_cols.append('gloss')
        drop_oldsense = [c for c in df.columns if c.startswith('Sense.')]
        drop_oldvariant = [c for c in df.columns if c.startswith('Variant.')]
        drop_oldallomorph = [
            c for c in df.columns if c.startswith('Allomorph.')]
        drop_oldscript = [
            c for c in df.columns if c.startswith('Lexeme Form Script')]
        drop_files = [c for c in df.columns if c.startswith('filesname.')]

        drop_cols.extend(drop_oldsense)
        drop_cols.extend(drop_oldvariant)
        drop_cols.extend(drop_oldallomorph)
        drop_cols.extend(drop_oldscript)
        drop_cols.extend(drop_files)

        df.drop(columns=drop_cols, inplace=True)

        return df

    def generate_latex(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        with open(write_path, 'w') as f_w:
            df.to_latex(f_w, index=False)

    def generate_formatted_latex(write_path,
                                 lexicon,
                                 lexicon_df,
                                 project,
                                 editors=['Editor 1', 'Editor 2', 'Editor 3'],
                                 co_editors=['Co-ed 1', 'Co-ed 2', 'Co-ed 3'],
                                 metadata=['Scheme for Protection and Preservation of Indian Languages',
                                           'Central Institute of Indian Languages'],
                                 fields=[],
                                 # lexemeformscripts.ipa.., glosslangs.hin..
                                 dict_headword='headword',
                                 formatting_options={
            'documentclass': 'article',
            'document_options': 'a4paper, 12pt, twoside, xelatex',
                                     'geometry_options': {
                                         "top": "3.5cm",
                                         "bottom": "3.5cm",
                                         "left": "3.5cm",
                                         "right": "3.5cm",
                                         "columnsep": "30pt",
                                         "includeheadfoot": True
                                     }
                                     }):
        lg.generate_formatted_latex(
            write_path, lexicon, lexicon_df, project, fields=fields)

    def generate_pdf(write_path,
                     lexicon,
                     project,
                     editors=['Editor 1', 'Editor 2', 'Editor 3'],
                     co_editors=['Co-ed 1', 'Co-ed 2', 'Co-ed 3'],
                     metadata=['Scheme for Protection and Preservation of Indian Languages',
                               'Central Institute of Indian Languages'],
                     fields=[],
                     # lexemeformscripts.ipa.., glosslangs.hin..
                     dict_headword='headword',
                     formatting_options={
            'documentclass': 'article',
            'document_options': 'a4paper, 12pt, twoside, xelatex',
                         'geometry_options': {
                             "top": "3.5cm",
                             "bottom": "3.5cm",
                             "left": "3.5cm",
                             "right": "3.5cm",
                             "columnsep": "30pt",
                             "includeheadfoot": True
                         }
                         }):
        lg.generate_formatted_latex(
            write_path, lexicon, project, fields=fields)

    # “xml”, “n3”, “turtle”, “nt”, “pretty-xml”, “trix”, “trig” and “nquads”
    def download_lexicon(lex_json, write_path,
                         output_format='rdf', rdf_format='turtle', fields=[]):
        file_ext_map = {'turtle': '.ttl', 'n3': '.n3',
                        'nt': '.nt', 'xml': '.rdf', 'pretty-xml': '.rdfp', 'trix': '.trix',
                        'trig': '.trig', 'nquads': 'nquad', 'json': '.json', 'csv': '.csv',
                        'xlsx': '.xlsx', 'pdf': '', 'html': '.html', 'latex_dict': '',
                        'markdown': '.md', 'ods': '.ods'}

        metadata = lex_json[0]
        project = metadata['projectname']

        lexicon = lex_json[1:]

        # fields = ['headword', 'Lexeme Form.ipa', 'Lexeme Form.Deva', 'grammaticalcategory', ['SenseNew.Gloss.hin', 'SenseNew.Gloss.eng', 'SenseNew.Definition.hin', 'SenseNew.Definition.eng', 'SenseNew.Example']]
        if len(fields) == 0:
            lexicon_df = pd.json_normalize(lexicon)
            columns = lexicon_df.columns
            cur_fields = ['headword', 'Pronunciation']
            # sense_fields = ['', '', '']
            sense_fields = []
            for field in columns:
                if 'SenseNew' in field:
                    if 'Gloss' in field or 'Definition' in field or 'Example' in field:
                        sense_fields.append(field)
                elif 'Lexeme' in field:
                    cur_fields.append(field)
            cur_fields.append('grammaticalcategory')
            cur_fields.extend(sense_fields)
        else:
            cur_fields = fields

        if (output_format in file_ext_map):
            logger.debug(f"pdf is match")
            file_ext = file_ext_map[output_format]
            write_file = os.path.join(write_path, 'lexicon_'+project+file_ext)
            if output_format == 'pdf':
                # logger.debug("...................cur_fields.................")
                # logger.debug(cur_fields)
                lg.generate_formatted_latex(
                    write_file, lexicon, lexicon_df, project, fields=cur_fields)
                # generate_pdf(write_file, lexicon, project, fields=fields, formatting_options={})
            elif output_format == 'latex':
                generate_latex(write_file, lexicon)
            elif output_format == 'latex_dict':
                # logger.debug("...................cur_fields.................")
                # logger.debug(cur_fields)
                lg.generate_formatted_latex(
                    write_file, lexicon, lexicon_df, project, fields=cur_fields)
                # generate_formatted_latex(write_file, lexicon, project, fields=fields, formatting_options={})
        else:
            logger.debug('File type\t', output_format, '\tnot supported')
            logger.debug('Supported File Types', file_ext_map.keys())

    lexeme_dir = basedir
    working_dir = basedir+'/download'
    with open(os.path.join(lexeme_dir, 'lexemeEntry.json')) as f_r:
        lex = json.load(f_r)
        out_form = download_format
        download_lexicon(lex, working_dir, out_form)

    # printing the list of all files to be zipped
    # files = glob.glob(basedir+'/app/download/*')
    files = glob.glob(basedir+'/download/*')

    with ZipFile('download.zip', 'w') as zip:
        # writing each file one by one
        for file in files:
            zip.write(file, os.path.join(projectname, os.path.basename(file)))
    logger.debug('All files zipped successfully!')

    # deleting all files from storage
    for f in files:
        # logger.debug(f)
        os.remove(f)

    return send_file('../download.zip', as_attachment=True)
    # return 'OK'

# download route


@app.route('/download', methods=['GET'])
def download():
    # getting the collections
    # collection containing entry of each lexeme and its details
    lexemes = mongo.db.lexemes
    # collection containing username and his/her last seen project name
    userprojects = mongo.db.userprojects
    # creating GridFS instance to get required files
    fs = gridfs.GridFS(mongo.db)

    lst = list()

    projectname = userprojects.find_one({'username': current_user.username},
                                        {'_id': 0, 'activeprojectname': 1})['activeprojectname']
    lst.append(projectname)
    # logger.debug(f'{"#"*80}\n{projectname}')
    for lexeme in lexemes.find({'username': current_user.username, 'projectname': projectname},
                               {'_id': 0, 'username': 0, 'projectname': 0}):
        lst.append(lexeme)

    # Serializing json
    json_object = json.dumps(lst, indent=2, ensure_ascii=False)

    # writing to currentprojectname.json
    with open(basedir+"/download/"+projectname+".json", "w") as outfile:
        outfile.write(json_object)

    # save current user mutimedia files of each lexeme to local storage
    files = fs.find({'username': current_user.username,
                     'projectname': projectname})
    for file in files:
        name = file.filename
        open(basedir+'/download/'+name, 'wb').write(file.read())

    # printing the list of all files to be zipped
    files = glob.glob(basedir+'/download/*')
    # logger.debug('Following files will be zipped:')
    # for file_name in files:
    #     logger.debug(file_name)

    # writing files to a zipfile
    with ZipFile('download.zip', 'w') as zip:
        # writing each file one by one
        for file in files:
            zip.write(file, os.path.join(projectname, os.path.basename(file)))
    logger.debug('All files zipped successfully!')

    # deleting all files from storage
    for f in files:
        os.remove(f)

    return send_file('../download.zip', as_attachment=True)

# download project in json format route


@app.route('/downloadjson', methods=['GET', 'POST'])
def downloadjson():
    return send_file('../download.zip', as_attachment=True)

# modal view with complete detail of a lexeme for edit
# edit button on dictionary view table


@app.route('/userslist', methods=['GET', 'POST'])
def userslist():

    userlogin, projects, userprojects = getdbcollections.getdbcollections(mongo,
                                                                          'userlogin',
                                                                          'projects',
                                                                          'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    try:
        data = json.loads(request.args.get('a'))
        logger.debug("data: %s, %s", data, type(data))
        share_action = data["shareAction"]
        selected_user = data["selectedUser"]
        logger.debug("share_action: %s, selected_user: %s",
                     share_action, selected_user)
        project_name, share_with_users_list, sourceList, share_info, current_user_sharemode, selected_user_shareinfo = lifeshare.get_users_list(projects,
                                                                                                                                                userprojects,
                                                                                                                                                userlogin,
                                                                                                                                                current_username,
                                                                                                                                                share_action=share_action,
                                                                                                                                                selected_user=selected_user)
    except:
        logger.exception("")

    return jsonify(projectName=project_name,
                   usersList=sorted(share_with_users_list),
                   sourceList=sorted(sourceList),
                   shareInfo=share_info,
                   sharemode=current_user_sharemode,
                   selectedUserShareInfo=selected_user_shareinfo)

# modal view with complete detail of a lexeme for edit
# edit button on dictionary view table


@app.route('/shareprojectwith', methods=['GET', 'POST'])
def shareprojectwith():
    projects, userprojects, userlogin, lifeappconfigs = getdbcollections.getdbcollections(mongo,
                                                                                          'projects',
                                                                                          'userprojects',
                                                                                          'userlogin',
                                                                                          'lifeappconfigs')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    # logger.debug('2758: activeprojectname', activeprojectname)

    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    project_type = getprojecttype.getprojecttype(projects,
                                                 activeprojectname)

    # data through ajax
    data = request.args.get('data')
    data = eval(data)
    logger.debug('Sharing Information: %s', pformat(data))
    shareaction = data['shareaction']
    users = data['sharewithusers']
    # logger.debug(type(users))
    speakers = data['sharespeakers']
    logger.debug("speakers: %s", speakers)
    sharemode = data['sharemode']
    # logger.debug(sharemode)
    if (sharemode == ''):
        sharemode = 0
    sharechecked = str(data['sharechecked'])
    downloadchecked = str(data['downloadchecked'])
    sharelatestchecked = str(data['sharelatestchecked'])

    # logger.debug('123', users, speakers, sharemode, sharechecked)

    if (len(users) != 0):
        # Sender email details
        sender_email_details = emailController.getSenderDetails(lifeappconfigs)

        # Get Base URL
        current_url = request.base_url
        base_url_index = current_url.rfind(os.sep)
        base_url = current_url[:base_url_index]

        # projectinfo of the user sharing the project
        projectinfo = userprojects.find_one(
            {
                'username': current_username
            },
            {
                '_id': 0,
                'myproject': 1,
                'projectsharedwithme': 1
            }
        )
        # loop on users with whom the project is to be shared
        for user in users:
            # logger.debug(user)
            userdict = {}
            # get list of projects shared with the user
            usershareprojectsname = userprojects.find_one(
                {
                    'username': user
                },
                {
                    '_id': 0,
                    'projectsharedwithme': 1
                }
            )
            usershareprojectsname = usershareprojectsname['projectsharedwithme']

            # if (sharemode == -1 and activeprojectname in usershareprojectsname):
            #         removed_user = removeallaccess.removeallaccess(projects,
            #                                         userprojects,
            #                                         activeprojectname,
            #                                         current_username,
            #                                         user)
            #         return removed_user
            # else:
            #     return f'This project: {activeprojectname} is not shared with this user: {user}'

            if activeprojectname in usershareprojectsname:
                if (sharemode == -1):
                    removed_user = removeallaccess.removeallaccess(projects,
                                                                   userprojects,
                                                                   activeprojectname,
                                                                   current_username,
                                                                   user,
                                                                   speakers)
                    return removed_user

                tomesharedby = usershareprojectsname[activeprojectname]['tomesharedby']
                tomesharedby.append(current_username)
                isharedwith = usershareprojectsname[activeprojectname]['isharedwith']
                usershareprojectsname[activeprojectname] = {
                    'sharemode': sharemode,
                    'tomesharedby': list(set(tomesharedby)),
                    'isharedwith': isharedwith,
                    'sharechecked': sharechecked,
                    'downloadchecked': downloadchecked,
                    'sharelatestchecked': sharelatestchecked,
                    'activespeakerId': '',
                    'activesourceId': ''
                }
            else:
                if (sharemode == -1):
                    return f'This project: {activeprojectname} is not shared with this user: {user}'

                usershareprojectsname[activeprojectname] = {
                    'sharemode': sharemode,
                    'tomesharedby': [current_user.username],
                    'isharedwith': [],
                    'sharechecked': sharechecked,
                    'downloadchecked': downloadchecked,
                    'sharelatestchecked': sharelatestchecked,
                    'activespeakerId': '',
                    'activesourceId': ''
                }

            projectdetails = projects.find_one(
                {
                    'projectname': activeprojectname
                },
                {
                    '_id': 0,
                    'sharedwith': 1,
                    'lastActiveId': 1,
                    'speakerIds': 1,
                    'sourceIds': 1
                }
            )

            # Give access only to user's own transcription if access to latest and other's transcriptions are not granted
            if not sharelatestchecked:
                projectDetails.save_active_transcription_by(
                    projects,
                    activeprojectname,
                    current_user.username,
                    current_user.username
                )
            # logger.debug(projectdetails)
            projectdetails['sharedwith'].append(user)
            # logger.debug(projectdetails)
            # update list of projects shared with the user in collection
            userprojects.update_one(
                {
                    'username': user
                },
                {
                    '$set':
                    {
                        'projectsharedwithme': usershareprojectsname
                    }
                }
            )
            projects.update_one(
                {
                    'projectname': activeprojectname
                },
                {
                    '$set':
                    {
                        'sharedwith': list(set(projectdetails['sharedwith']))
                    }
                }
            )

            if ('speakerIds' in projectdetails):
                if (len(speakers) != 0):
                    userprojectinfo = ''
                    for key, value in projectinfo.items():
                        if len(value) != 0:
                            if activeprojectname in value:
                                userprojectinfo = key+'.'+activeprojectname+".activespeakerId"
                    userprojects.update_one(
                        {
                            "username": current_username
                        },
                        {
                            "$set":
                            {
                                userprojectinfo: speakers[-1]
                            }
                        }
                    )

                    for speaker in speakers:
                        # logger.debug("speaker: %s", speaker)
                        projects.update_one(
                            {
                                'projectname': activeprojectname
                            },
                            {
                                '$addToSet':
                                {
                                    'speakerIds.'+user: speaker
                                }
                            }
                        )
                        userlastactiveId = projectdetails['lastActiveId'][current_username][speaker]['audioId']
                        projects.update_one(
                            {
                                'projectname': activeprojectname
                            },
                            {
                                '$set':
                                {
                                    'lastActiveId.'+user+'.'+speaker+'.audioId': userlastactiveId
                                }
                            }
                        )
                elif user not in projectdetails['speakerIds']:
                    projects.update_one(
                        {
                            'projectname': activeprojectname
                        },
                        {
                            '$set':
                            {
                                'lastActiveId.'+user: {}
                            }
                        }
                    )
            elif ('sourceIds' in projectdetails):
                logger.debug("FOUND sourceIds source[-1]: %s", speakers[-1])
                if (len(speakers) != 0):
                    userprojectinfo = ''
                    for key, value in projectinfo.items():
                        if len(value) != 0:
                            if activeprojectname in value:
                                userprojectinfo = key+'.'+activeprojectname+".activesourceId"
                    userprojects.update_one(
                        {
                            "username": current_username
                        },
                        {
                            "$set":
                            {
                                userprojectinfo: speakers[-1]
                            }
                        }
                    )

                    for speaker in speakers:
                        logger.debug("sourceId: %s", speaker)
                        projects.update_one(
                            {
                                'projectname': activeprojectname
                            },
                            {
                                '$addToSet':
                                {
                                    'sourceIds.'+user: speaker
                                }
                            }
                        )
                        if (project_type == 'annotation'):
                            userlastactiveId = projectdetails['lastActiveId'][current_username][speaker]['dataId']
                            projects.update_one(
                                {
                                    'projectname': activeprojectname
                                },
                                {
                                    '$set':
                                    {
                                        'lastActiveId.'+user+'.'+speaker+'.dataId': userlastactiveId
                                    }
                                }
                            )
                elif user not in projectdetails['sourceIds']:
                    projects.update_one(
                        {
                            'projectname': activeprojectname
                        },
                        {
                            '$set':
                            {
                                'lastActiveId.'+user: {}
                            }
                        }
                    )

            # update "isharedwith" of the current user and the projectowner
            for key, value in projectinfo.items():
                if (len(value) != 0 and
                        activeprojectname in value):
                    userprojects.update_one(
                        {
                            "username": current_username
                        },
                        {
                            "$addToSet":
                            {
                                key+'.'+activeprojectname+'.isharedwith': user
                            }
                        }
                    )
                    if projectowner != current_username:
                        userprojects.update_one(
                            {
                                "username": projectowner
                            },
                            {
                                "$addToSet":
                                {
                                    'myproject.'+activeprojectname+'.isharedwith': user
                                }
                            }
                        )

            # Send email to the user
            current_user_email = emailController.getCurrentUserEmail(
                userlogin, user)

            if current_user_email == '':
                current_user_email = 'unreal.tece@gmail.com'

            shared_with_user_email = sender_email_details['email']

            if current_user_email != '' and shared_with_user_email != '':
                logger.info('Sending email')
                purpose = 'share'  # share|OTP|notification

                email_status = emailController.sendEmail(
                    activeprojectname,
                    user,
                    base_url,
                    purpose,
                    shared_with_user_email,
                    current_user_email,
                    sender_email_details['password'],
                    sender_email_details['smtp_server'],
                    sender_email_details['port']
                )
            else:
                email_status = "Email not configured in the app. Project shared but email not sent"
                logger.info(email_status)

    # flash(email_status)
    return redirect(url_for('home'))
    # return 'OK'

# modal view with complete detail of a lexeme
# view button on dictionary view table


# retrieve files from database
# TODO: User not able to download the data
@app.route('/retrieve/<filename>', methods=['GET'])
@login_required
def retrieve(filename):
    # logger.debug('Now in retrieve')
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


@app.route('/lexemeview', methods=['GET'])
def lexemeview():
    projects, userprojects, projectsform, lexemes = getdbcollections.getdbcollections(mongo,
                                                                                      'projects',
                                                                                      'userprojects',
                                                                                      'projectsform',
                                                                                      'lexemes')

    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    projectOwner = getprojectowner.getprojectowner(projects, activeprojectname)
    logger.debug('projectOwner: %s', projectOwner)
    # data through ajax
    headword = request.args.get('a').split(',')
    logger.debug('headword: %s', headword)
    lexeme = lexemes.find_one({'username': projectOwner, 'lexemeId': headword[0], },
                              {'_id': 0, 'username': 0})

    # logger.debug(lexeme["lemon"])
    logger.debug('lexeme: %s', pformat(lexeme))

    filen = {}
    if 'filesname' in lexeme:
        for key, filename in lexeme['filesname'].items():
            logger.debug('key: %s, filename: %s', key, filename)
            filen[key] = url_for('retrieve', filename=filename)
    logger.debug('filen: %s', pformat(filen))
    y = projectsform.find_one_or_404({'projectname': activeprojectname,
                                      'username': projectOwner}, {"_id": 0})

    return jsonify(newData=y, result1=lexeme, result2=filen)


# modal view with complete detail of a lexeme for edit
# edit button on dictionary view table
@app.route('/lexemeedit', methods=['GET', 'POST'])
def lexemeedit():
    # getting the collections
    # collection of project specific form created by the user
    projectsform = mongo.db.projectsform
    # collection containing entry of each lexeme and its details
    lexemes = mongo.db.lexemes
    # collection of users and their respective projects
    userprojects = mongo.db.userprojects
    projects = mongo.db.projects                        # collection of projects

    headword = request.args.get('a').split(
        ',')                    # data through ajax
    # logger.debug(headword)

    activeprojectname = userprojects.find_one({'username': current_user.username})[
        'activeprojectname']
    # logger.debug(activeprojectname)

    projectOwner = projects.find_one({'projectname': activeprojectname}, {
                                     'projectOwner': 1})['projectOwner']
    # projectOwner = projects.find_one({}, {"_id" : 0, activeprojectname : 1})[activeprojectname]["projectOwner"]
    # logger.debug(projectOwner)

    if request.method == 'POST':

        newLexemeData = request.form.to_dict()
        # logger.debug(newLexemeData)
        return redirect(url_for('dictionaryview'))

    # activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
    #                 {'_id' : 0, 'activeprojectname': 1})['activeprojectname']
    lexeme = lexemes.find_one({'username': projectOwner, 'lexemeId': headword[0], },
                              {'_id': 0, 'username': 0})

    # logger.debug(lexeme)

    filen = []
    if 'filesname' in lexeme:
        for filename in lexeme['filesname']:
            filen.append(url_for('retrieve', filename=filename))

    y = projectsform.find_one_or_404({'projectname': activeprojectname,
                                      'username': projectOwner}, {"_id": 0})

    return jsonify(newData=y, result1=lexeme, result2=filen)

# enter new lexeme route
# display form for new lexeme entry for current project


@app.route('/editlexeme', methods=['GET', 'POST'])
@login_required
def editlexeme():
    return render_template('editlexeme.html')


@app.route('/lexemeupdate', methods=['GET', 'POST'])
def lexemeupdate():
    projects, userprojects, lexemes = getdbcollections.getdbcollections(mongo,
                                                                        'projects',
                                                                        'userprojects',
                                                                        'lexemes')
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                                                            userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    # logger.debug(f"PROJECT OWNER: {projectOwner}")
    # new lexeme details coming from current project form
    if request.method == 'POST':

        # newLexemeData = request.form.to_dict()
        newLexemeData = dict(request.form.lists())
        newLexemeFiles = request.files.to_dict()
        # logger.debug(newLexemeFiles)
        # logger.debug(newLexemeData)
        lexemeId = newLexemeData['lexemeId'][0]
        # dictionary to store files name
        newLexemeFilesName = {}
        for key in newLexemeFiles:
            if newLexemeFiles[key].filename != '':
                # adding microseconds of current time to differ two files of same name
                newLexemeFilesName[key] = (datetime.now().strftime(
                    '%f')+'_'+newLexemeFiles[key].filename)

        # format data filled in enter new lexeme form
        lexemeFormData = {}
        sense = {}
        variant = {}
        allomorph = {}
        lemon = ''

        lexemeFormData['username'] = projectowner

        def lexemeFormScript():
            """'List of dictionary' of lexeme form scripts"""
            lexemeFormScriptList = []
            for key, value in newLexemeData.items():
                if 'Script' in key:
                    k = re.search(r'Script (\w+)', key)
                    lexemeFormScriptList.append({k[1]: value[0]})
            lexemeFormData['headword'] = list(
                lexemeFormScriptList[0].values())[0]
            return lexemeFormScriptList

        def senseListOfDict(senseCount):
            """'List of dictionary' of sense"""
            for num in range(1, int(newLexemeData['senseCount'][-1])+1):
                senselist = []
                for key, value in newLexemeData.items():
                    if 'Sense '+str(num) in key:
                        k = re.search(r'([\w+\s]+) Sense', key)
                        if k[1] == 'Semantic Domain' or k[1] == 'Lexical Relation':
                            senselist.append({k[1]: value})
                        else:
                            senselist.append({k[1]: value[0]})
                sense['Sense '+str(num)] = senselist
            # logger.debug(sense)
            return sense

        def variantListOfDict(variantCount):
            """'List of dictionary' of variant"""
            for num in range(1, int(newLexemeData['variantCount'][-1])+1):
                # variantlist = []
                variantdict = {}
                for key, value in newLexemeData.items():
                    if 'Variant '+str(num) in key:
                        k = re.search(r'([\w+\s]+) Variant', key)
                        # variantlist.append({k[1] : value[0]})
                        variantdict[k[1]] = value[0]
                variant['Variant '+str(num)] = variantdict
            # logger.debug(variant)
            return variant

        def allomorphListOfDict(allomorphCount):
            """'List of dictionary' of allomorph"""
            for num in range(1, int(newLexemeData['allomorphCount'][-1])+1):
                # allomorphlist = []
                allomorphdict = {}
                for key, value in newLexemeData.items():
                    if 'Allomorph '+str(num) in key:
                        k = re.search(r'([\w+\s]+) Allomorph', key)
                        # allomorphlist.append({k[1] : value[0]})
                        allomorphdict[k[1]] = value[0]
                # allomorph['Allomorph '+str(num)] = allomorphlist
                allomorph['Allomorph '+str(num)] = allomorphdict
            # logger.debug(allomorph)
            return allomorph

        def customFields():
            """'List of dictionary' of custom fields"""
            # customFieldsList = []
            customFieldsDict = {}
            for key, value in newLexemeData.items():
                if 'Custom' in key:
                    k = re.search(r'Field (\w+)', key)
                    # customFieldsList.append({k[1] : value[0]})
                    customFieldsDict[k[1]] = value[0]
            # logger.debug(sense)
            return customFieldsDict

        for key, value in newLexemeData.items():
            if 'Sense' in key or 'Variant' in key or 'Allomorph' in key:
                continue
            elif key == 'senseCount':
                Sense = senseListOfDict(value[0])
                lexemeFormData['Sense'] = Sense
            elif key == 'variantCount':
                Variant = variantListOfDict(value[0])
                lexemeFormData['Variant'] = Variant
            elif key == 'allomorphCount':
                Allomorph = allomorphListOfDict(value[0])
                lexemeFormData['Allomorph'] = Allomorph
            elif 'Script' in key:
                lexemeFormData['Lexeme Form Script'] = lexemeFormScript()
            elif 'Custom' in key:
                lexemeFormData['Custom Fields'] = customFields()
            elif key == 'Lexeme Language':
                pass
            else:
                # logger.debug(lexemeFormData)
                # logger.debug(key)
                lexemeFormData[key] = value[0]

        # logger.debug(f"{'#'*80}\n{list(lexemeFormData['Sense']['Sense 1'][0].keys())}")
        gloss = list(lexemeFormData['Sense']['Sense 1'][0].keys())
        lexemeFormData['gloss'] = lexemeFormData['Sense']['Sense 1'][0][gloss[0]]
        # grammaticalcategory  = list(lexemeFormData['Sense']['Sense 1'][4].keys())
        # logger.debug(f"{'#'*80}\n{lexemeFormData['Sense']['Sense 1']}")
        for senseData in lexemeFormData['Sense']['Sense 1']:
            if list(senseData.keys())[0] == 'Grammatical Category':
                # logger.debug(f"{'#'*80}\n{list(senseData.values())[0]}")
                lexemeFormData['grammaticalcategory'] = list(senseData.values())[
                    0]
        lexemeFormData['lexemedeleteFLAG'] = 0
        lexemeFormData['updatedBy'] = current_user.username
        lexemeFormData['lexemeId'] = lexemeId

        langscripts = langscriptutils.get_langscripts(
            newLexemeData, lexemeFormData)
        lexemeFormData['langscripts'] = langscripts

        SenseNew = {}

        for key, value in lexemeFormData['Sense'].items():
            keyParent = key
            key = {}
            # logger.debug(keyParent)
            Gloss = {}
            Definition = {}
            Lexical_Relation = {}
            for val in value:

                for k, v in val.items():
                    if ("Gloss" in k):
                        Gloss[k.split()[1][:3].lower()] = v
                        # logger.debug(key, k, v)
                    elif ("Definition" in k):
                        Definition[k.split()[1][:3].lower()] = v
                    elif ("Lexical Relation" in k):
                        # Lexical_Relation[v[0]] = v[0]
                        key['Lexical Relation'] = v[0]
                    elif ("Semantic Domain" in k):
                        # Lexical_Relation[v[0]] = v[0]
                        key['Semantic Domain'] = v[0]

                    else:
                        key[k] = v

            key['Gloss'] = Gloss
            key['Definition'] = Definition
            # key['Lexical Relation'] = Lexical_Relation

            SenseNew[keyParent] = key
        # logger.debug(SenseNew)
        lexemeFormData['SenseNew'] = SenseNew

        lexemeForm = {}
        for lexForm in lexemeFormData['Lexeme Form Script']:
            for lexKey, lexValue in lexForm.items():
                # lexemeForm[lexKey[:4]] = lexValue
                lexemeForm[langscriptutils.get_script_code(lexKey)] = lexValue

        lexemeFormData['Lexeme Form'] = lexemeForm

        # keep only new updated keys as in 'lexemeEntry_sir.json' file in 'data_format folder
        # and delete old keys
        lexemeFormData.pop('Sense', None)
        lexemeFormData.pop('Lexeme Form Script', None)

        # when testing comment these to avoid any database update/changes
        # saving files for the new lexeme to the database in fs collection
        for (filename, key) in zip(newLexemeFilesName.values(), newLexemeFiles):
            # logger.debug(filename, key, newLexemeFiles[key])
            mongo.save_file(filename, newLexemeFiles[key], lexemeId=lexemeId, username=current_user.username,
                            projectname=lexemeFormData['projectname'], headword=lexemeFormData['headword'],
                            updatedBy=current_user.username)

       # prevent deletion of old files name from lexeme details
        oldFilesOfLexeme = lexemes.find_one(
            {'lexemeId': lexemeId}, {'_id': 0, 'filesname': 1})
        # logger.debug(oldFilesOfLexeme)
        if (len(oldFilesOfLexeme) != 0):
            oldFilesOfLexeme = oldFilesOfLexeme['filesname']
            for key, fname in oldFilesOfLexeme.items():
                if (key not in newLexemeFilesName):
                    newLexemeFilesName[key] = fname
        # save file names of a lexeme in lexemeFormData dictionary with other details related to the lexeme
        if len(newLexemeFilesName) != 0:
            lexemeFormData['filesname'] = newLexemeFilesName
        # saving data for that new lexeme to database in lexemes collection
        # lexemes.insert(lexemeFormData)
        # logger.debug(f'{"="*80}\nLexeme Form :')
        # logger.debug(lexemeFormData)
        # logger.debug(f'{"="*80}')
        lexemes.update_one({'lexemeId': lexemeId}, {'$set': lexemeFormData})

        flash('Successfully Updated lexeme')
        return redirect(url_for('dictionaryview'))
        # comment till here

    try:
        my_projects = len(userprojects.find_one(
            {'username': current_user.username})["myproject"])
        shared_projects = len(userprojects.find_one(
            {'username': current_user.username})["projectsharedwithme"])
        # logger.debug(f"MY PROJECTS: {my_projects}, SHARED PROJECTS: {shared_projects}")
        if (my_projects+shared_projects) == 0:
            flash('Please create your first project')
            return redirect(url_for('home'))
    except:
        # logger.debug(f'{"#"*80}\nCurrent user details not in database!!!')
        flash('Please create your first project')
        return redirect(url_for('home'))
    # get the list of lexeme entries for current project to show in dictionary view table
    lst = list()

    # projectOwner = projects.find_one({}, {"_id" : 0, activeprojectname : 1})[activeprojectname]["projectOwner"]
    # logger.debug(projectOwner)
    try:
        # logger.debug(activeprojectname)
        projectOwner = projects.find_one({}, {"_id": 0, activeprojectname: 1})[
            activeprojectname]["projectOwner"]
        # logger.debug(projectOwner)
        for lexeme in lexemes.find({'username': projectOwner, 'projectname': activeprojectname, 'lexemedeleteFLAG': 0},
                                   {'_id': 0, 'headword': 1, 'gloss': 1, 'grammaticalcategory': 1, 'lexemeId': 1}):
            # logger.debug(lexeme)
            if (len(lexeme['headword']) != 0):
                lst.append(lexeme)
    except:
        flash('Enter first lexeme of the project')

    # logger.debug(lst)
    return render_template('dictionaryview.html', projectName=activeprojectname, sdata=lst, count=len(lst), data=currentuserprojectsname)


# delete button on dictionary view table
@app.route('/lexemedelete', methods=['GET', 'POST'])
def lexemedelete():
    # getting the collections
    projects, userprojects, lexemes = getdbcollections.getdbcollections(mongo,
                                                                        'projects',
                                                                        'userprojects',
                                                                        'lexemes')
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)

    # data through ajax
    headword = request.args.get('a').split(',')
    lexemes.update_one({'username': projectowner, 'lexemeId': headword[0]},
                       {'$set': {'lexemedeleteFLAG': 1}})

    return jsonify(msg=headword[1]+' deletion successful')

# delete button on dictionary view table


@app.route('/deletemultiplelexemes', methods=['GET', 'POST'])
def deletemultiplelexemes():
    projects, userprojects, lexemes = getdbcollections.getdbcollections(mongo,
                                                                        'projects',
                                                                        'userprojects',
                                                                        'lexemes')
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    # data through ajax
    headwords = request.args.get('data')
    headwords = eval(headwords)

    # logger.debug(headwords)
    for headwordId in headwords.keys():
        lexemes.update_one({'username': projectowner, 'lexemeId': headwordId,
                            }, {'$set': {'lexemedeleteFLAG': 1}})

    return 'OK'


# save active project name for active user
@app.route('/activeprojectname', methods=['GET', 'POST'])
def activeprojectname():
    userprojects, = getdbcollections.getdbcollections(mongo, 'userprojects')

    projectname = str(request.args.get('a'))            # data through ajax

    # if userprojects.find_one({'username' : current_user.username}) is None:
    #     activeprojectnames.insert({ 'username' : current_user.username, 'projectname' : projectname })
    # else:
    #     activeprojectnames.update_one({ 'username' : current_user.username }, {'$set' : { 'projectname' : projectname }})

    userprojects.update_one({'username': current_user.username},
                            {'$set': {'activeprojectname':  projectname}})

    return 'OK'


def adminfirstlogin(userlogin, string_password):
    password = generate_password_hash(string_password)
    # logger.debug(user, password)

    userlogin.update_one({"username": ADMIN_USER},
                         {'$set': {"password": password,
                                   'userSince': datetime.now(),
                                   'isActive': 1,
                                   'isSuperAdmin': 1,
                                   'isAdmin': 1,
                                   'userdeleteFLAG': 0}})

    return password

# MongoDB Database
# user login form route


@app.route('/login', methods=['GET', 'POST'])
def login():
    userlogin = mongo.db.userlogin

    # collection of users and their login details
    generateadmin(userlogin)
    dummyUserandProject()
    manageAppConfig.generateDummyAppConfig()
    lman.generate_languages_database()
    mman.generate_models_database()

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = UserLoginForm()
    if form.validate_on_submit():
        # username = userlogin.find_one({"username": form.username.data})
        user = UserLogin(username=form.username.data)
        password = form.password.data
        # logger.debug('Original password', password)
        # logger.debug(user)
        if user.username == ADMIN_USER:
            if user.password_hash == '':
                admin_password = adminfirstlogin(userlogin, password)
                user.password_hash = admin_password

        # logger.debug('Create password', password)
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        isUserAvailable = userlogin.find_one(
            {'username': form.username.data}, {"_id": 1, "isActive": 1, "userdeleteFLAG": 1})
        # logger.debug(len(isUserActive))
        # if (len(isUserActive) != 0):
        if 'isActive' in isUserAvailable and 'userdeleteFLAG' in isUserAvailable:
            isUserActive = isUserAvailable['isActive']
            isUserDelete = isUserAvailable['userdeleteFLAG']
            # logger.debug('User active status %s', isUserActive)
            if (isUserActive == 1 and isUserDelete == 0):
                pass
                # logger.debug(isUserActive)
                # logger.debug('123')
            else:
                if (isUserDelete == 1):
                    if (isUserActive == 2):
                        flash(
                            'Your account has been deactivated and deleted. Please contact the administrator for more details.')
                    elif (isUserActive == 0):
                        flash(
                            'Your request for an account was not approved. Please contact the administrator for more details or apply again with lesser requirements.')
                else:
                    if (isUserActive == 2):
                        flash(
                            'Your account has been deactivated. Please contact the administrator for more details.')
                    # flash('Your request for an account is successfully submitted and is currently under review.')
                    elif (isUserActive == 0):
                        flash(
                            'Your request for an account is  currently under review. If approved, your account will be active in some time.')
                return redirect(url_for('login'))
        else:
            old_user_update(userlogin, user.username, ObjectId(
                isUserActive['_id']).generation_time)
            update_profile(userlogin, user.username, get_blank_profile())

        login_user(user, force=True)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', form=form)


def get_blank_profile():
    blank_profile = {
        "position": "",
        "organisation_name": "",
        "organisation_type": "",
        "country": "",
        "city": "",
        "email": "",
        "languages": "",
        "storage_requirement": "",
        "app_use_reason": ""
    }
    return blank_profile


def old_user_update(userlogin, username, userSince):
    userlogin.update_one({"username": username},
                         {"$set": {'userSince': userSince,
                                   'isActive': 1,
                                   'userdeleteFLAG': 0,
                                   'isSuperAdmin': 0,
                                   'isAdmin': 0
                                   }})


def update_profile(userlogin, username, userProfile):
    userlogin.update_one({"username": username},
                         {"$set": {
                             'userProfile': userProfile
                         }})

    # userprojects = mongo.db.userprojects
    # userprojects.insert({'username': form.username.data, 'myproject': {},
    #                          'projectsharedwithme': {}, 'activeprojectname': ''})
# MongoDB Database
# use logout


@app.route('/logout')
def logout():
    try:
        logout_user()
        return redirect(url_for('home'))
    except:
        return redirect(url_for('home'))


def generate_registration_form(userType=''):
    form = RegistrationForm()
    return form
    # flash('Congratulations, you are now a registered user!')


def save_registration_form(form, current_user):
    userlogin = mongo.db.userlogin
    userProfile = {}
    excludeFormFields = ['username', 'password',
                         'password2', 'csrf_token', 'submit']

    if form.validate_on_submit():
        # logger.debug(form)
        for form_data in form:
            # logger.debug(form_data)
            # logger.debug(type(form_data))
            # logger.debug(form_data.data)
            if (form_data.name not in excludeFormFields):
                userProfile[form_data.name] = form_data.data
        # logger.debug(userProfile)
        # user = UserLogin(username=form.username.data)
        password = generate_password_hash(form.password.data)
        # logger.debug(user, password)

        userlogin.insert_one({"username": form.username.data,
                              "password": password,
                              'userProfile': userProfile,
                              'userSince': datetime.now(),
                              'isActive': 0,
                              'userdeleteFLAG': 0,
                              'isSuperAdmin': 0,
                              'isAdmin': 0})

        # collection of users and their respective projectlist
        userprojects = mongo.db.userprojects
        # userprojects.insert({'username' : form.username.data, 'myproject': [], \
        #     'projectsharedwithme': [], 'activeprojectname' : ''})
        userprojects.insert_one({'username': form.username.data, 'myproject': {},
                                 'projectsharedwithme': {}, 'activeprojectname': ''})

    # if current_user.is_authenticated:
    #     current_username = getcurrentusername.getcurrentusername()
    #     if current_username == ADMIN_USER:
    #         flash(
    #             'The account details are successfully submitted. Please activate the account now.')
    #         return redirect(url_for('manageusers'))

    # flash('Your request for an account is successfully submitted and is currently under review.')
    # return redirect(url_for('login'))

# MongoDB Database
# new user registration


@app.route('/register', methods=['GET', 'POST'])
def register():
    # collection of users and their login details
    userlogin, = getdbcollections.getdbcollections(
        mongo, 'userlogin')

    dummyUserandProject()
    manageAppConfig.generateDummyAppConfig()

    form = generate_registration_form()
    current_username = ''

    if form.validate_on_submit():
        save_registration_form(form, current_user)
        if current_user.is_authenticated:
            current_username = getcurrentusername.getcurrentusername()
            logger.debug("Current username after submit", current_username)
            usertype = userdetails.get_user_type(userlogin, current_username)
            if 'ADMIN' in usertype:
                flash(
                    'The account details are successfully submitted. Please activate the account now.')
                return redirect(url_for('manageusers'))

        flash('Your request for an account is successfully submitted and is currently under review.')
        return redirect(url_for('login'))
    elif current_user.is_authenticated:
        current_username = getcurrentusername.getcurrentusername()
        usertype = userdetails.get_user_type(userlogin, current_username)
        if 'ADMIN' in usertype:
            return render_template('register.html', form=form)
            # return redirect(url_for('manageusers'))
        else:
            # logger.debug(current_user.get_id())
            return redirect(url_for('home'))
    else:
        return render_template('register.html', form=form)

    # return "Ok"

    # return render_template('register.html', form=form)


def dummyUserandProject():
    """ Creates dummy user and project if the database has no collection """
    logger.debug("Creates dummy user and project if the database has no collection")
    # collection of users and their projectlist and active project
    userprojects = mongo.db.userprojects
    projects = mongo.db.projects
    # collection containing projects name
    if len(mongo.db.list_collection_names()) == 0:
        userprojects.insert_one({'username': "dummyUser",
                                 'myproject':
                                 {"dummyProject1":
                                  {
                                      'sharemode': 0,
                                      'sharechecked': "false",
                                      'downloadchecked': "false",
                                      'sharelatestchecked': "false"
                                  }
                                  },
                                 'projectsharedwithme': {},
                                 'activeprojectname': "dummyActiveProject"
                                 })
        projects.insert_one({"projectname": "dummyProject1",
                             "projectOwner": "dummyUser",
                             "lexemeInserted": 0,
                             "lexemeDeleted": 0,
                             'sharedwith': ['dummyUser'],
                             'projectdeleteFLAG': 0
                             })


def insertadmin(userlogin):

    userprojects = mongo.db.userprojects

    # userlogin.insert({
    #     "username": ADMIN_USER,
    #     "password": "",
    #     "userProfile": {
    #         "username": ADMIN_USER,
    #         "position": "Administrator",
    #         "organisation_name": "Central Institute of Indian Languages",
    #         "organisation_type": "Academic",
    #         "country": "India",
    #         "city": "Mysuru",
    #         "email": "",
    #         "languages": "Maithili",
    #         "storage_requirement": "-1",
    #         "app_use_reason": "For LDCIL Project"
    #     }
    # })
    userlogin.insert_one({
        "username": ADMIN_USER,
        "password": "",
        "userProfile": {
            "position": "Administrator",
            "organisation_name": "",
            "organisation_type": "",
            "country": "",
            "city": "",
            "email": "",
            "languages": "",
            "storage_requirement": "",
            "app_use_reason": ""
        }
    })

    userprojects.insert_one({'username': ADMIN_USER, 'myproject': {},
                             'projectsharedwithme': {}, 'activeprojectname': ''})

    flash(admin_reminder)


def generateadmin(userlogin):
    """ Creates admin if the database does not have an admin user """

    if len(mongo.db.list_collection_names()) == 0:
        insertadmin(userlogin)
    else:
        admin_login = userlogin.find_one({'username': ADMIN_USER}, {
                                         'password': 1, '_id': 0})
        if admin_login == None:
            insertadmin(userlogin)
        elif admin_login['password'] == '':
            flash(admin_reminder)


# audio transcription route
@app.route('/', methods=['GET', 'POST'])
@app.route('/audiotranscription', methods=['GET', 'POST'])
@login_required
def audiotranscription():
    # collection of users and their respective projects
    userprojects = mongo.db.userprojects

    # currentuserprojectsname =  sorted(list(currentuserprojects()))
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                                                            userprojects)
    activeprojectname = userprojects.find_one({'username': current_user.username},
                                              {'_id': 0, 'activeprojectname': 1})['activeprojectname']

    # creating GridFS instance to get required files
    fs = gridfs.GridFS(mongo.db)
    files = fs.find({})
    audioFolder = os.path.join(basedir, 'static/audio')
    shutil.rmtree(audioFolder)
    os.mkdir(audioFolder)
    for file in files:
        if ('audio' in file.contentType):
            name = file.filename
            # logger.debug(file.projectname)
            # logger.debug(name)
            audiofile = fs.get_last_version(filename=name)
            audiofileBytes = audiofile.read()
            # logger.debug(len(audiofile.read()))
            if (len(audiofileBytes) != 0):
                open(basedir+'/static/audio/'+name, 'wb').write(audiofileBytes)

    if request.method == 'POST':

        newLexemeData = dict(request.form.lists())
        newLexemeFiles = request.files.to_dict()
        # logger.debug(newLexemeData)
        # dictionary to store files name
        newLexemeFilesName = {}
        for key in newLexemeFiles:
            if newLexemeFiles[key].filename != '':
                # adding microseconds of current time to differ two files of same name
                newLexemeFilesName[key] = (datetime.now().strftime(
                    '%f')+'_'+newLexemeFiles[key].filename)
        # logger.debug(newLexemeFiles)
        # logger.debug(newLexemeFilesName)

        return redirect(url_for('audiotranscription'))

    return render_template('audiotranscription.html',  data=currentuserprojectsname, activeprojectname=activeprojectname, audiofile=str(file.read()))


# karya access code assignment route
@app.route('/assignkaryaaccesscode', methods=['GET', 'POST'])
@login_required
def assignkaryaaccesscode():
    # logger.debug(f"IN KARYA ACCESS CODE ASSIGNMENT FUNCTION")
    return redirect(url_for('home'))


@app.route('/datetimeasid', methods=['GET'])
def datetimeasid():
    Id = re.sub(r'[-: \.]', '', str(datetime.now()))
    # logger.debug(Id)
    return jsonify(Id=Id)


@app.route('/loadpreviousaudio', methods=['GET', 'POST'])
@login_required
def loadpreviousaudio():
    projects, userprojects = getdbcollections.getdbcollections(mongo,
                                                               'projects',
                                                               'userprojects')
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)
    # activespeakerid = getactivespeakerid.getactivespeakerid(userprojects, current_user.username)
    current_username = getcurrentusername.getcurrentusername()
    activespeakerid = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                            current_user.username,
                                                            activeprojectname)['activespeakerId']
    # data through ajax
    lastActiveId = request.args.get('data')
    lastActiveId = eval(lastActiveId)
    latest_audio_id = ''
    # newAudioFilePath = getAudioFilename(lastActiveFilename, 'previous')
    if (len(lastActiveId) != 0):
        speaker_audio_ids = audiodetails.get_speaker_audio_ids_new(projects,
                                                                   activeprojectname,
                                                                   current_username,
                                                                   activespeakerid)
        latest_audio_id = audiodetails.getnewaudioid(projects,
                                                     activeprojectname,
                                                     lastActiveId,
                                                     activespeakerid,
                                                     speaker_audio_ids,
                                                     'previous')
        audiodetails.updatelatestaudioid(projects,
                                         activeprojectname,
                                         latest_audio_id,
                                         current_username,
                                         activespeakerid)

    return jsonify(newAudioId=latest_audio_id)
    # return jsonify(newAudioFilePath=newAudioFilePath)


@app.route('/loadnextaudio', methods=['GET', 'POST'])
@login_required
def loadnextaudio():
    projects, userprojects = getdbcollections.getdbcollections(mongo,
                                                               'projects',
                                                               'userprojects')
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)
    # activespeakerid = getactivespeakerid.getactivespeakerid(userprojects, current_user.username)
    current_username = getcurrentusername.getcurrentusername()
    activespeakerid = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                            current_user.username,
                                                            activeprojectname)['activespeakerId']
    # data through ajax
    lastActiveId = request.args.get('data')
    lastActiveId = eval(lastActiveId)
    # logger.debug('lastActiveId', type(lastActiveId), len(lastActiveId))
    latest_audio_id = ''
    if (len(lastActiveId) != 0):
        # newAudioFilePath = getAudioFilename(lastActiveFilename, 'previous')
        speaker_audio_ids = audiodetails.get_speaker_audio_ids_new(projects,
                                                                   activeprojectname,
                                                                   current_username,
                                                                   activespeakerid)
        latest_audio_id = audiodetails.getnewaudioid(projects,
                                                     activeprojectname,
                                                     lastActiveId,
                                                     activespeakerid,
                                                     speaker_audio_ids,
                                                     'next')
        # logger.debug('latest_audio_id ROUTES', latest_audio_id)
        audiodetails.updatelatestaudioid(projects,
                                         activeprojectname,
                                         latest_audio_id,
                                         current_username,
                                         activespeakerid)

    return jsonify(newAudioId=latest_audio_id)
    # return jsonify(newAudioFilePath=newAudioFilePath)


def getAudioFilename(lastActiveFilename, whichOne):
    audioFilesPath = 'static/audio'
    baseAudioFilesPath = os.path.join(basedir, audioFilesPath)
    audioFilesList = sorted(os.listdir(baseAudioFilesPath))
    # logger.debug(audioFilesList)
    audioFileIndex = audioFilesList.index(lastActiveFilename)
    if (whichOne == 'next'):
        audioFileIndex = audioFileIndex + 1
    elif (whichOne == 'previous'):
        audioFileIndex = audioFileIndex - 1
    newAudioFilePath = os.path.join(
        audioFilesPath, audioFilesList[audioFileIndex])

    return newAudioFilePath

# this is for the dropdown list of all the filenames.
# it could be use by the user to move to (load) some random audio using the filename


@app.route('/allunannotated', methods=['GET', 'POST'])
def allunannotated():
    projects, userprojects = getdbcollections.getdbcollections(mongo,
                                                               'projects',
                                                               'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    # activespeakerid = getactivespeakerid.getactivespeakerid(userprojects, current_user.username)
    project_type = getprojecttype.getprojecttype(projects, activeprojectname)
    data_collection, = getdbcollections.getdbcollections(mongo, project_type)
    activespeakerid = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                            current_user.username,
                                                            activeprojectname)['activespeakerId']
    # audioFilesPath = 'static/audio'
    # baseAudioFilesPath = os.path.join(basedir, audioFilesPath)
    # audioFilesList = sorted(os.listdir(baseAudioFilesPath))
    # logger.debug('Active speaker ID: %s', activespeakerid)
    annotated, unannotated = [], []
    if (activespeakerid != ''):
        speaker_audio_ids = audiodetails.get_speaker_audio_ids_new(projects,
                                                                   activeprojectname,
                                                                   current_username,
                                                                   activespeakerid)
        annotated, unannotated = unannotatedfilename.unannotatedfilename(data_collection,
                                                                         activeprojectname,
                                                                         activespeakerid,
                                                                         speaker_audio_ids,
                                                                         'audio')
    # logger.debug('Annotated: %s\nUnannotated: %s', annotated, unannotated)
    return jsonify(allanno=annotated, allunanno=unannotated)


@app.route('/loadunannotext', methods=['GET'])
@login_required
def loadunannotext():
    projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo, 'projects',
                                                                               'userprojects', 'transcriptions')

    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)
    # activespeakerid = getactivespeakerid.getactivespeakerid(userprojects, current_user.username)
    activespeakerid = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                            current_user.username,
                                                            activeprojectname)['activespeakerId']

    # logger.debug(f'{"="*80}\nUn-Anno\n{"="*80}')

    lastActiveId = request.args.get('data')
    lastActiveId = eval(lastActiveId)
    # logger.debug(lastActiveId)
    updateactivespeakeraudioid = 'lastActiveId.' + \
        current_user.username+'.'+activespeakerid+'.audioId'
    # logger.debug(updateactivespeakeraudioid)

    projects.update_one({"projectname": activeprojectname},
                        {'$set': {updateactivespeakeraudioid: lastActiveId}})

    # if (project_type == 'text'):
    #     return redirect(url_for('textAnno'))
    # elif (project_type == 'image'):
    #     return redirect(url_for('imageAnno'))
    return 'OK'


@app.route('/loadtranscriptionbyanyuser', methods=['GET'])
@login_required
def loadtranscriptionbyanyuser():
    projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo, 'projects',
                                                                               'userprojects', 'transcriptions')

    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)
    # activespeakerid = getactivespeakerid.getactivespeakerid(userprojects, current_user.username)
    activespeakerid = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                            current_user.username,
                                                            activeprojectname)['activespeakerId']

    # logger.debug(f'{"="*80}\nUn-Anno\n{"="*80}')

    # receivedData =
    lastActiveUser = request.args.get('transcriptionUser')
    lastActiveAudioId = request.args.get('activeId')
    logger.debug('Data receved from form %s\t%s',
                 lastActiveUser, lastActiveAudioId)
    # lastActiveUser = eval(lastActiveUser)
    # lastActiveAudioId = eval(lastActiveAudioId)
    # logger.debug('Final data %s\t%s', lastActiveUser, lastActiveAudioId)
    # logger.debug(lastActiveId)

    # Preference set for each Audio file separately
    # updateactiveuser = 'lastActiveUserTranscription.' + \
    #     current_user.username+'.'+activespeakerid+'.' + lastActiveAudioId
    # logger.debug(updateactivespeakeraudioid)

    # Preference set for a specific user in a project - all audio files will show the transcription of the user selected
    projectDetails.save_active_transcription_by(
        projects,
        activeprojectname,
        current_user.username,
        lastActiveUser
    )

    # if (project_type == 'text'):
    #     return redirect(url_for('textAnno'))
    # elif (project_type == 'image'):
    #     return redirect(url_for('imageAnno'))
    return 'OK'

# add speaker details


@app.route('/addnewspeakerdetails', methods=['GET', 'POST'])
@login_required
def addnewspeakerdetails():
    projects, userprojects, speakerdetails = getdbcollections.getdbcollections(mongo,
                                                                               'projects',
                                                                               'userprojects',
                                                                               'speakerdetails')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    if request.method == 'POST':
        form_data = request.form
        uploaded_files = request.files

        logger.debug("All form %s", form_data)

        metadata_schema, audio_source, call_source, upload_type, exclude_fields = processHTMLForm.get_metadata_header_details(
            form_data)

        logger.debug("Metadata Schema %s", metadata_schema)
        logger.debug("Call source %s", call_source)

        metadata_data = processHTMLForm.get_metadata_data(form_data,
                                                          form_files=uploaded_files,
                                                          upload_type=upload_type,
                                                          exclude_fields=exclude_fields)

        speakerDetails.write_speaker_metadata_details(speakerdetails,
                                                      projectowner,
                                                      activeprojectname,
                                                      current_username,
                                                      audio_source,
                                                      metadata_schema,
                                                      metadata_data,
                                                      upload_type)

        # if ('field' in audio_source):

        # if field_name in metadata_data:
        #     current_data = metadata_data[field_name]
        #     if type(current_data) == str:
        #         metadata_data[field_name] = [current_data]

        #     metadata_data[field_name].append(
        #         form_data[field_name])
        # else:
        #     metadata_data[field_name] = form_data[field_name]

        # fname = request.form.get('sname', '')
        # fage = request.form.get('sagegroup', '')
        # fgender = request.form.get('sgender', '')
        # educlvl = request.form.get('educationalevel', '')
        # moe12 = request.form.getlist('moe12')
        # moea12 = request.form.getlist('moea12')
        # sols = request.form.getlist('sols')
        # por = request.form.get('por', '')
        # toc = request.form.get('toc', '')
        # metadata_data.update({"name": fname,
        #                       "agegroup": fage,
        #                       "gender": fgender,
        #                       "educationlevel": educlvl,
        #                       "educationmediumupto12": moe12,
        #                       "educationmediumafter12": moea12,
        #                       "speakerspeaklanguage": sols,
        #                       "recordingplace": por,
        #                       "typeofrecordingplace": toc})

        # elif (audio_source == 'internet'):
        #     # internet sub source
        #     audio_subsource = request.form.get('audiosubsource')
        #     if (audio_subsource == 'youtube'):
        #         if upload_type == 'single':
        #             channelname = request.form.get('ytchannelname', '')
        #             channelurl = request.form.get('ytchannelurl', '')
        #             metadata_data.update({"channelName": channelname,
        #                                   "channelUrl": channelurl})
        # logger.debug('Metadata info %s', metadata_data)
        # excel_data = pd.read_excel(
        #     metadata_data, engine="openpyxl")
        # excel_data['educationmediumupto12'] = excel_data['educationmediumupto12'].apply(
        #     lambda x: x.split(','))
        # logger.debug('File data %s', excel_data.to_dict(orient='records'))

        if "managepage" in call_source:
            flash(
                'New source details added. Now you can upload the data for this source.')
            return redirect(url_for('managespeakermetadata'))
        else:
            flash(
                'New source details added. Now you can upload the data for this source.')
            return redirect(url_for('enternewsentences'))

    return redirect(url_for('enternewsentences'))


# Manage Speaker Metadata
@app.route('/managespeakermetadata', methods=['GET', 'POST'])
@login_required
def managespeakermetadata():
    userprojects, userlogin, speakermeta = getdbcollections.getdbcollections(
        mongo, 'userprojects', 'userlogin', 'speakerdetails')
    current_username = getcurrentusername.getcurrentusername()
    logger.debug('USERNAME: ', current_username)
    usertype = userdetails.get_user_type(
        userlogin, current_username)
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(
        current_username, userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(
        userprojects, current_username, activeprojectname)
    allspeakerdetails, alldatalengths, allkeys = speakerDetails.getspeakerdetails(
        activeprojectname, speakermeta)

    # logger.debug(allspeakerdetails)
    # logger.debug(alldatalengths)

    return render_template(
        'manageSpeakers.html',
        speaker_data=allspeakerdetails,
        activeprojectname=activeprojectname,
        shareinfo=shareinfo,
        usertype=usertype,
        count=alldatalengths,
        table_headers=allkeys
    )


@app.route('/getonespeakermetadata', methods=['GET', 'POST'])
def getonespeakermetadata():
    speakermeta, userprojects = getdbcollections.getdbcollections(
        mongo, "speakerdetails", "userprojects")

    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)

    # data through ajax
    lifesourceid = request.args.get('lifespeakerid')
    logger.debug("Life source ID", lifesourceid)
    speakermetadata = speakerDetails.getonespeakerdetails(
        activeprojectname, lifesourceid, speakermeta)

    logger.debug("Speaker Metadata", speakermetadata)
    return jsonify(onespeakerdetails=speakermetadata)


@app.route('/editsourcemetadata', methods=['GET', 'POST'])
def editsourcemetadata():
    projects, userprojects, speakerdetails = getdbcollections.getdbcollections(mongo,
                                                                               'projects',
                                                                               'userprojects',
                                                                               'speakerdetails')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)
    # projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    # exclude_fields = ['audiosource', 'sourcecallpage',
    #                   'fieldmetadataschema', 'metadataentrytype', 'audioInternetSource', 'lifespeakerid']

    if request.method == 'POST':
        # add_new_speaker_form_data = dict(request.form.lists())
        # logger.debug(add_new_speaker_form_data)
        current_dt = str(datetime.now()).replace('.', ':')
        form_data = request.form
        lifesourceid = form_data.get('lifespeakerid')

        logger.debug("All form %s", form_data)
        metadata_data = processHTMLForm.get_metadata_data(
            form_data
        )

        update_data = {
            "current": {
                "updatedBy": current_username,
                "sourceMetadata": metadata_data,
                "current_date": current_dt,
            }
        }
        logger.debug("Update Data %s", update_data)
        updatestatus = speakerDetails.updateonespeakerdetails(
            activeprojectname, lifesourceid, update_data, speakerdetails)

    return redirect(url_for('managespeakermetadata'))


@app.route('/editfieldspeakermetadata', methods=['GET', 'POST'])
def editfieldspeakermetadata():
    speakermeta, userprojects = getdbcollections.getdbcollections(
        mongo, "speakerdetails", "userprojects")

    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)

    current_dt = str(datetime.now()).replace('.', ':')
    # data through ajax
    lifesourceid = request.form.get('lifespeakerid')

    fname = request.form.get('sname')
    fage = request.form.get('sagegroup')
    fgender = request.form.get('sgender')
    educlvl = request.form.get('educationalevel')
    moe12 = request.form.getlist('moe12')
    moea12 = request.form.getlist('moea12')
    sols = request.form.getlist('sols')
    por = request.form.get('por')
    toc = request.form.get('toc')
    update_data = {
        "current": {
            "updatedBy": current_username,
            "sourceMetadata": {
                "name": fname,
                "agegroup": fage,
                "gender": fgender,
                "educationlevel": educlvl,
                "educationmediumupto12": moe12,
                "educationmediumafter12": moea12,
                "speakerspeaklanguage": sols,
                "recordingplace": por,
                "typeofrecordingplace": toc
            },
            "current_date": current_dt,
        }
    }

    updatestatus = speakerDetails.updateonespeakerdetails(
        activeprojectname, lifesourceid, update_data, speakermeta)

    return redirect(url_for('managespeakermetadata'))


@app.route('/edityoutubesourcemetadata', methods=['GET', 'POST'])
def edityoutubesourcemetadata():
    speakermeta, userprojects = getdbcollections.getdbcollections(
        mongo, "speakerdetails", "userprojects")

    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)

    current_dt = str(datetime.now()).replace('.', ':')
    # data through ajax
    lifesourceid = request.form.get('lifespeakerid')

    channelname = request.form.get('ytchannelname')
    channelurl = request.form.get('ytchannelurl')

    update_data = {
        "current": {
            "updatedBy": current_username,
            "sourceMetadata": {
                "channelName": channelname,
                "channelUrl": channelurl
            },
            "current_date": current_dt
        }
    }

    updatestatus = speakerDetails.updateonespeakerdetails(
        activeprojectname, lifesourceid, update_data, speakermeta)

    return redirect(url_for('managespeakermetadata'))


# uploadaudiofiles route
@app.route('/uploadaudiofiles', methods=['GET', 'POST'])
@login_required
def uploadaudiofiles():
    projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                               'projects',
                                                                               'userprojects',
                                                                               'transcriptions')
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    if request.method == 'POST':
        run_vad = False
        run_asr = False
        split_into_smaller_chunks = True
        get_audio_json = True

        data = dict(request.form.lists())
        logger.debug("Form data %s", data)
        speakerId = data['speakerId'][0]
        new_audio_file = request.files.to_dict()

        if 'uploadparameters-vad' in data:
            run_vad = True

        if 'boundaryPause' in data:
            boundary_threshold = float(data['boundaryPause'][0])
        else:
            boundary_threshold = 0.3

        if 'sliceOffsetValue' in data:
            slice_offset = float(data['sliceOffsetValue'][0])
        else:
            slice_offset = 0.1

        slice_threshold = float(data['fileSplitThreshold'][0])
        slice_size = float(data['maxFileSize'][0])

        if 'uploadparameters-optimisefor' in data:
            get_audio_json = data['uploadparameters-optimisefor'][0] == 'True'
        # logger.debug(get_audio_json)

        if 'minBoundarySize' in data:
            min_boundary_size = float(data['minBoundarySize'][0])
        else:
            min_boundary_size = 2.0

        '''
        ASR Model and VAD Model Dict Formats

        asr_model = {
            'model_name': "name_1",
            'model_type': "local", (or "api")
            'model_params': {
                'model_path': "path_1",
                'model_api': 'api_endpoint'
            },
            'target': 'hin-Deva'
        }


        vad_model = {
            'model_name': "name_1",
            'model_type': "local", (or "api")
            'model_params': {
                'model_path': "path_1",
                'model_api': 'api_endpoint'
            }
        }
        '''

        audiodetails.saveaudiofiles(mongo,
                                    projects,
                                    userprojects,
                                    transcriptions,
                                    projectowner,
                                    activeprojectname,
                                    current_user.username,
                                    speakerId,
                                    new_audio_file,
                                    # change this and boundary_threshold for automatic detection of boundaries of different kinds
                                    run_vad=run_vad,
                                    run_asr=run_asr,
                                    split_into_smaller_chunks=split_into_smaller_chunks,
                                    get_audio_json=get_audio_json,
                                    vad_model={},
                                    asr_model={},
                                    transcription_type='sentence',
                                    boundary_threshold=boundary_threshold,
                                    slice_threshold=slice_threshold,
                                    # max size of each slice (in seconds), if large audio is to be automatically divided into multiple parts
                                    slice_size=slice_size,
                                    data_type="audio",
                                    new_audio_details={},
                                    prompt="",
                                    update=False,
                                    slice_offset_value=slice_offset,
                                    min_boundary_size=min_boundary_size
                                    )

    return redirect(url_for('enternewsentences'))


# makeboundary route
@app.route('/makeboundary', methods=['GET', 'POST'])
@login_required
def makeboundary():
    projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                               'projects',
                                                                               'userprojects',
                                                                               'transcriptions')
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    if request.method == 'POST':
        run_vad = True
        run_asr = False
        get_audio_json = False
        split_into_smaller_chunks = False
        overwrite_user = False

        data = dict(request.form.lists())
        logger.debug("Form data %s", data)
        speakerId = data['speakerId'][0]
        # new_audio_file = request.files.to_dict()
        audio_filename = data['audiofile'][0]
        # converts into seconds
        audio_duration = float(data['audioduration'][0]) * 60
        existing_audio_details = transcriptions.find_one(
            {'projectname': activeprojectname, 'audioFilename': audio_filename})
        logger.debug("Existing audio data %s", existing_audio_details)

        if 'boundaryPause' in data:
            boundary_threshold = float(data['boundaryPause'][0])
        else:
            boundary_threshold = 0.3

        if 'sliceOffsetValue' in data:
            slice_offset = float(data['sliceOffsetValue'][0])
        else:
            slice_offset = 0.1

        slice_threshold = 2.0
        slice_size = 150.0

        if 'createaudiojson' in data:
            get_audio_json = True

        if 'overwrite-my-boundaries' in data:
            overwrite_user = True
        # logger.debug(get_audio_json)

        if 'minBoundarySize' in data:
            min_boundary_size = float(data['minBoundarySize'][0])
        else:
            min_boundary_size = 2.0

        '''
        ASR Model and VAD Model Dict Formats

        asr_model = {
            'model_name': "name_1",
            'model_type': "local", (or "api")
            'model_params': {
                'model_path': "path_1",
                'model_api': 'api_endpoint'
            },
            'target': 'hin-Deva'
        }


        vad_model = {
            'model_name': "name_1",
            'model_type': "local", (or "api")
            'model_params': {
                'model_path': "path_1",
                'model_api': 'api_endpoint'
            }
        }
        '''

        audiodetails.save_boundaries_of_one_audio_file(mongo,
                                                       projects,
                                                       userprojects,
                                                       transcriptions,
                                                       projectowner,
                                                       activeprojectname,
                                                       current_user.username,
                                                       audio_filename,
                                                       audio_duration,
                                                       # change this and boundary_threshold for automatic detection of boundaries of different kinds
                                                       run_vad=run_vad,
                                                       run_asr=run_asr,
                                                       split_into_smaller_chunks=split_into_smaller_chunks,
                                                       get_audio_json=get_audio_json,
                                                       vad_model={},
                                                       asr_model={},
                                                       transcription_type='sentence',
                                                       boundary_threshold=boundary_threshold,
                                                       min_boundary_size=min_boundary_size,
                                                       save_for_user=overwrite_user
                                                       )

    return redirect(url_for('enternewsentences'))

# change speaker ID


@app.route('/changespeakerid', methods=['GET', 'POST'])
@login_required
def changespeakerid():
    userprojects, = getdbcollections.getdbcollections(mongo, 'userprojects')
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_user.username, userprojects)

    # data through ajax
    speakerId = str(request.args.get('a'))
    # logger.debug(speakerId)
    projectinfo = userprojects.find_one({'username': current_user.username},
                                        {'_id': 0, 'myproject': 1, 'projectsharedwithme': 1})

    # logger.debug(projectinfo)
    userprojectinfo = ''
    for key, value in projectinfo.items():
        if len(value) != 0:
            if activeprojectname in value:
                userprojectinfo = key+'.'+activeprojectname+".activespeakerId"
    # logger.debug(userprojectinfo)
    userprojects.update_one({"username": current_user.username},
                            {"$set": {
                                userprojectinfo: speakerId
                            }})
    # userprojects.update_one({ 'username' : current_user.username },
    #                         { '$set' : { 'activespeakerId' :  speakerId}})

    return 'OK'


@app.route('/changesourceid', methods=['GET', 'POST'])
@login_required
def changesourceid():
    userprojects, = getdbcollections.getdbcollections(mongo, 'userprojects')
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)

    # data through ajax
    sourceId = str(request.args.get('a'))
    # logger.debug(sourceId)
    projectinfo = userprojects.find_one({'username': current_user.username},
                                        {'_id': 0, 'myproject': 1, 'projectsharedwithme': 1})

    # logger.debug(projectinfo)
    userprojectinfo = ''
    for key, value in projectinfo.items():
        if len(value) != 0:
            if activeprojectname in value:
                userprojectinfo = key+'.'+activeprojectname+".activesourceId"
    # logger.debug(userprojectinfo)
    userprojects.update_one({"username": current_user.username},
                            {"$set": {
                                userprojectinfo: sourceId
                            }})

    return 'OK'


# get progress report
@app.route('/progressreport', methods=['GET'])
@login_required
def progressreport():
    projects, userprojects, transcriptions, speakerdetails = getdbcollections.getdbcollections(mongo,
                                                                                               'projects',
                                                                                               'userprojects',
                                                                                               'transcriptions',
                                                                                               'speakerdetails')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)

    progressreport = ''

    # logger.debug(current_username, activeprojectname)
    shareinfo = getuserprojectinfo.getuserprojectinfo(
        userprojects, current_username, activeprojectname)
    # logger.debug(shareinfo)

    if 'isharedwith' in shareinfo:
        isharedwith = shareinfo['isharedwith']
        # logger.debug('isharedwith', isharedwith)
        isharedwith.append(current_username)
        # logger.debug('isharedwith_2', isharedwith)
        progressreport = audiodetails.getaudioprogressreport(projects,
                                                             transcriptions,
                                                             speakerdetails,
                                                             activeprojectname,
                                                             isharedwith)

    # logger.debug(progressreport)

    return jsonify(progressreport=progressreport)


# get progress report
@app.route('/test', methods=['GET'])
@login_required
def test():
    projects, userprojects, projectsform, questionnaire, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                                            'projects',
                                                                                                            'userprojects',
                                                                                                            'projectsform',
                                                                                                            'questionnaire',
                                                                                                            'transcriptions')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_username,
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

    # logger.debug('current_username', current_username)
    # logger.debug('currentuserprojectsname', currentuserprojectsname)
    # logger.debug('activeprojectname', activeprojectname)
    # logger.debug('projectowner', projectowner)
    # logger.debug('quesprojectform', quesprojectform)
    # logger.debug('shareinfo', shareinfo)

    return render_template('test.html',
                           projectName=activeprojectname,
                           quesprojectform=quesprojectform,
                           data=currentuserprojectsname,
                           shareinfo=shareinfo)

# uploadquesfiles route


@app.route('/uploadquesfiles', methods=['GET', 'POST'])
@login_required
def uploadquesfiles():
    projects, userprojects, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                               'projects',
                                                                               'userprojects',
                                                                               'questionnaires')
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    current_username = getcurrentusername.getcurrentusername()

    questionaireprojectform = {
        "username": "alice",
        "projectname": "alice_project_1",
        "Language": ["text", ["English", "Hindi"]],
        "Script": ["", ["latin", "devanagari"]],
        "Prompt Audio": ["file", ["audio"]],
        "Domain": ["multiselect", ["General", "Agriculture", "Sports"]],
        "Elicitation Method": ["select", ["Translation", "Agriculture", "Sports"]],
        "Target": ["multiselect", ["case", "classifier", "adposition"]]
    }

    if request.method == 'POST':
        # speakerId = dict(request.form.lists())['speakerId'][0]
        new_ques_file = request.files.to_dict()

        questionnairedetails.savequesfiles(mongo,
                                           projects,
                                           userprojects,
                                           questionnaires,
                                           projectowner,
                                           activeprojectname,
                                           current_username,
                                           new_ques_file
                                           )

    return redirect(url_for('test'))

# Contact Us route
# create contact us form for the LiFE


@app.route('/contactus', methods=['GET', 'POST'])
# @login_required
def contactus():
    return render_template('contactus.html')

# LiFE Documentation route


@app.route('/documentation', methods=['GET', 'POST'])
# @login_required
def documentation():
    return render_template('documentation.html')


@app.route('/projecttype', methods=['GET', 'POST'])
@login_required
def projecttype():
    projects, userprojects, projectsform = getdbcollections.getdbcollections(mongo,
                                                                             'projects',
                                                                             'userprojects',
                                                                             'projectsform')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    project_type = getprojecttype.getprojecttype(projects, activeprojectname)
    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                      current_username,
                                                      activeprojectname)
    current_user_sharemode = int(shareinfo['sharemode'])

    projectowner = getprojectowner.getprojectowner(projects,
                                                   activeprojectname)
    activeprojectform = getactiveprojectform.getactiveprojectform(projectsform,
                                                                  projectowner,
                                                                  activeprojectname)

    return jsonify(projectType=project_type,
                   shareMode=current_user_sharemode,
                   activeprojectform=activeprojectform)


@app.route('/manageapp', methods=['GET', 'POST'])
@login_required
def manageapp():
    userlogin, = getdbcollections.getdbcollections(
        mongo, 'userlogin')
    current_username = getcurrentusername.getcurrentusername()
    logger.debug('USERNAME: ', current_username)
    usertype = userdetails.get_user_type(
        userlogin, current_username)
    logger.debug('USERTYPE: ', usertype)
    # logger.debug(ADMIN_USER, SUB_ADMINS)

    if 'ADMIN' in usertype:
        allusers = userdetails.getuserdetails(userlogin)
        userprofilelist = userdetails.getuserprofilestructure(userlogin)

        return render_template(
            'manageApp.html',
            allusers=allusers,
            userprofilelist=userprofilelist,
            usertype=usertype
        )


@app.route('/emailsetup', methods=['GET', 'POST'])
@login_required
def emailsetup():
    userlogin, lifeappconfigs = getdbcollections.getdbcollections(
        mongo, 'userlogin', 'lifeappconfigs')
    current_username = getcurrentusername.getcurrentusername()
    logger.debug('USERNAME: ', current_username)
    usertype = userdetails.get_user_type(
        userlogin, current_username)
    logger.debug('USERTYPE: ', usertype)
    # logger.debug(ADMIN_USER, SUB_ADMINS)
    manageAppConfig.generateDummyAppConfig()

    if 'SUPER-ADMIN' in usertype:
        if request.method == 'POST':

            email = request.form.get('name++notificationEmail')
            pwd = request.form.get('name++notificationEmailPwd')
            port = request.form.get('name++smtpPort')
            server = request.form.get('name++smtpServer')
            emailconfig = {
                'notificationEmail': email,
                'notificationEmailPwd': pwd,
                'smtpPort': port,
                'smtpServer': server
            }
            labelmap = manageAppConfig.updateAppSendEmailDetails(
                lifeappconfigs, emailconfig)

        else:
            emailconfig, labelmap = manageAppConfig.getAppSendEmailDetails(
                lifeappconfigs)

    return render_template(
        'appemailsetup.html',
        emailconfig=emailconfig,
        labelmap=labelmap,
        usertype=usertype
    )


@app.route('/hfmodelsetup', methods=['GET', 'POST'])
@login_required
def hfmodelsetup():
    userlogin, lifeappconfigs = getdbcollections.getdbcollections(
        mongo, 'userlogin', 'lifeappconfigs')
    current_username = getcurrentusername.getcurrentusername()
    logger.debug('USERNAME: ', current_username)
    usertype = userdetails.get_user_type(
        userlogin, current_username)
    logger.debug('USERTYPE: ', usertype)
    # logger.debug(ADMIN_USER, SUB_ADMINS)
    # manageAppConfig.generateDummyAppConfig()
    hfmodelconfig = {}
    labelmap = []
    hfmodelconfigglobal = {}
    hfmodelconfiguser = {}

    featured_authors_default = ['ai4bharat', 'Harveenchadha', 'facebook', 'meta-llama',
                                'google', 'microsoft', 'allenai', 'Intel', 'openai', 'openchat', 'writer', 'amazon',
                                'assemblyai', 'EleutherAI', 'tiiuae', 'bigscience', 'Salesforce', 'lmsys', 'mosaicml', 'databricks',
                                'stabilityai', 'Open-Orca', 'mistralai', 'HuggingFaceH4', 'distil-whisper', 'sarvamai']

    if request.method == 'POST':
        authors_list = request.form.getlist('nameglobal++authorsList')
        task_type = request.form.get('nameglobal++taskType')
        if 'SUPER-ADMIN' in usertype:
            hfmodelconfigglobal = {
                'globals': {
                    task_type: {
                        'authorsList': authors_list
                    }
                }
            }
            hfmodelconfig.update(hfmodelconfigglobal)

        api_tokens = request.form.getlist('nameuser++apiTokens')
        hfmodelconfiguser = {
            'usersData': {
                current_username: {
                    'apiTokens': api_tokens,
                    'globals': {
                        task_type: {
                            'authorsList': authors_list
                        }
                    }
                }
            }
        }
        hfmodelconfig.update(hfmodelconfiguser)

        logger.debug("Final config sent %s", hfmodelconfig)

        labelmap = manageAppConfig.updateHuggingFaceModelConfig(
            lifeappconfigs, hfmodelconfig)
    else:
        hfmodelconfig, labelmap = manageAppConfig.getHuggingFaceModelConfig(
            lifeappconfigs, current_username, usertype)

    if 'SUPER-ADMIN' in usertype:
        global_config = hfmodelconfig['globals']
    else:
        global_config = hfmodelconfig['usersData'].get(
            current_username, {'globals': {}})

    # TODO: Write a function to get the list of authors given a task - this will be used
    # for calling it via AJAX and getting Author List when a specific task is selected
    # on the manage page. At present only ASR is being implemented and supported
    # hfmodelconfigval = global_config.get(
    #     'automatic-speech-recognition', {'authorsList': featured_authors_default})
    # logger.debug('Model config %s %s', hfmodelconfigval,
    #              len(hfmodelconfigval['authorsList']))
    # if len(hfmodelconfigval['authorsList']) > 0:
    #     hfmodelconfigglobal['automatic-speech-recognition'] = hfmodelconfigval['authorsList']
    # else:
    #     hfmodelconfigglobal['automatic-speech-recognition'] = featured_authors_default

    logger.debug('Model config Global %s', hfmodelconfigglobal)

    for task_type, author_list in global_config.items():
        # if task_type == current_username:
        author_list = author_list.get(
            'authorsList', featured_authors_default)
        if len(author_list) == 0:
            author_list = featured_authors_default
        hfmodelconfigglobal[task_type] = author_list

    logger.debug('Model config Global %s', hfmodelconfigglobal)
    # hfmodelconfigglobal['taskType'] = 'automatic-speech-recognition'
    hfmodelconfiguser = hfmodelconfig['usersData'].get(
        current_username, {'apiTokens': []})['apiTokens']

    logger.debug('Model config Global %s', hfmodelconfigglobal)
    logger.debug('Model config user %s', hfmodelconfiguser)

    return render_template(
        'hfmodelsetup.html',
        hfmodelconfiguser=hfmodelconfiguser,
        hfmodelconfigadmin=hfmodelconfigglobal,
        labelmap=labelmap,
        usertype=usertype
    )


@app.route('/languagesetup', methods=['GET', 'POST'])
@login_required
def languagesetup():
    userlogin, lifeappconfigs = getdbcollections.getdbcollections(
        mongo, 'userlogin', 'lifeappconfigs')
    current_username = getcurrentusername.getcurrentusername()
    logger.debug('USERNAME: ', current_username)
    usertype = userdetails.get_user_type(
        userlogin, current_username)
    logger.debug('USERTYPE: ', usertype)
    if 'SUPER-ADMIN' in usertype:
        return render_template(
            'languagesetup.html'
        )
    else:
        flash("This action is not allowed for you")
        return "Permission denied"


@app.route('/regeneratelanguages', methods=['GET', 'POST'])
@login_required
def regeneratelanguages():
    userlogin, lifeappconfigs = getdbcollections.getdbcollections(
        mongo, 'userlogin', 'lifeappconfigs')
    current_username = getcurrentusername.getcurrentusername()
    logger.debug('USERNAME: ', current_username)
    usertype = userdetails.get_user_type(
        userlogin, current_username)
    logger.debug('USERTYPE: ', usertype)
    if 'SUPER-ADMIN' in usertype:
        lman.generate_languages_database(regenerate=True)
        flash("The languages databse is successfully regenerated. You will need to sync models again now!")
        return redirect(url_for('languagesetup'))
    else:
        flash("This action is not allowed for you")
        return "Permission denied"


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    # note that we set the 500 status explicitly
    return render_template('500.html'), 500


@app.route('/deleteaudio', methods=['GET', 'POST'])
@login_required
def deleteaudio():
    try:
        projects_collection, userprojects, transcriptions_collection = getdbcollections.getdbcollections(mongo,
                                                                                                         'projects',
                                                                                                         'userprojects',
                                                                                                         'transcriptions')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(
            current_username, userprojects)
        logger.debug("%s,%s", current_username, activeprojectname)
        last_active_id = json.loads(request.form['a'])
        logger.info("last active audio id to delete: %s, %s",
                    last_active_id, type(last_active_id))
        active_speaker_id = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                  current_username,
                                                                  activeprojectname)['activespeakerId']

        speaker_audio_ids = audiodetails.get_speaker_audio_ids_new(projects_collection,
                                                                   activeprojectname,
                                                                   current_username,
                                                                   active_speaker_id)
        audiodetails.delete_one_audio_file(projects_collection,
                                           transcriptions_collection,
                                           activeprojectname,
                                           current_username,
                                           active_speaker_id,
                                           last_active_id,
                                           speaker_audio_ids)
    except:
        logger.exception("")
    flash("Audio deleted successfully")

    return "OK"


@app.route('/browseshareuserslist', methods=['GET', 'POST'])
def browseshareuserslist():

    userlogin, projects, userprojects = getdbcollections.getdbcollections(mongo,
                                                                          'userlogin',
                                                                          'projects',
                                                                          'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    usersList = []
    sourceList = []
    current_user_sharemode = 0
    share_with_users_list = []
    try:
        activeprojectname = getactiveprojectname.getactiveprojectname(
            current_username, userprojects)
        projectowner = getprojectowner.getprojectowner(
            projects, activeprojectname)
        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                          current_username,
                                                          activeprojectname)
        current_user_sharemode = int(shareinfo['sharemode'])
        project_type = getprojecttype.getprojecttype(projects,
                                                     activeprojectname)

        # get list of all the users registered in the application LiFE
        for user in userlogin.find({}, {"_id": 0, "username": 1, "isActive": 1}):
            # logger.debug(user)
            if ('isActive' in user and user['isActive'] == 1):
                usersList.append(user["username"])
                # logger.debug(user)
        if (current_username == projectowner):
            usersList.remove(projectowner)
            share_with_users_list = usersList
        else:
            # logger.debug(usersList)
            usersList.remove(projectowner)
            usersList.remove(current_username)
            # logger.debug(usersList)
            # share_with_users_list = usersList
            # logger.debug(usersList)
            for username in usersList:
                # logger.debug(username)
                usershareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                      username,
                                                                      activeprojectname)
                usersharemode = int(usershareinfo['sharemode'])
                # logger.debug(current_username, current_user_sharemode, username, usersharemode)
                # logger.debug(current_username, type(current_user_sharemode), username, type(usersharemode))
                if (current_user_sharemode <= usersharemode):
                    # logger.debug(f"username!!!: {username}")
                    # share_with_users_list.remove(username)
                    pass
                else:
                    # logger.debug(f"username!!!: {username}")
                    share_with_users_list.append(username)
        # project_shared_with = projects.find_one({'projectname': activeprojectname},
        #                                         {'_id': 0, 'sharedwith': 1})["sharedwith"]
        # share_with_users_list = list(set(share_with_users_list) & set(project_shared_with))
        share_with_users_list = shareinfo["isharedwith"]
    except:
        logger.exception("")

    return jsonify(usersList=sorted(share_with_users_list),
                   sourceList=sorted(sourceList),
                   sharemode=current_user_sharemode)


@app.route('/browsefilesharedwithuserslist', methods=['GET', 'POST'])
def browsefilesharedwithuserslist():
    browse_file_sharedwith_userslist = []
    try:
        userlogin, projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                              'userlogin',
                                                                                              'projects',
                                                                                              'userprojects',
                                                                                              'transcriptions')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)

        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                          current_username,
                                                          activeprojectname)

        # projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
        # project_type = getprojecttype.getprojecttype(projects,
        #                                             activeprojectname)

        # data through ajax
        data = json.loads(request.args.get('a'))
        logger.debug('Sharing Information: %s', pformat(data))
        audio_info = data['audioInfo']
        audio_ids_list = audio_info
        # audio_ids_list = list(audio_info.keys())
        file_speaker_ids = projects.find_one({"projectname": activeprojectname},
                                             {"_id": 0,
                                              "fileSpeakerIds": 1})
        file_speaker_ids = file_speaker_ids["fileSpeakerIds"]
        logger.debug("file_speaker_ids: %s", file_speaker_ids)
        for audio_id in audio_ids_list:
            speakerid = audiodetails.get_audio_speakerid(
                transcriptions, audio_id)
            if (speakerid is not None and file_speaker_ids is not None):
                for user, speaker_ids in file_speaker_ids.items():
                    if (speakerid in speaker_ids and
                            audio_id in speaker_ids[speakerid] and
                            user in shareinfo["isharedwith"]):
                        browse_file_sharedwith_userslist.append(user)
        browse_file_sharedwith_userslist.remove(current_username)
        for user_name in shareinfo["tomesharedby"]:
            browse_file_sharedwith_userslist.remove(user_name)
    except:
        logger.exception("")

    return jsonify(sharedWithUsers=browse_file_sharedwith_userslist)


@app.route('/browsesharewith', methods=['GET', 'POST'])
def browsesharewith():
    try:
        projects, userprojects, userlogin, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                              'projects',
                                                                                              'userprojects',
                                                                                              'userlogin',
                                                                                              'transcriptions')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(
            current_username, userprojects)

        # projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
        # project_type = getprojecttype.getprojecttype(projects,
        #                                             activeprojectname)

        # data through ajax
        data = json.loads(request.args.get('a'))
        logger.debug('Sharing Information: %s', pformat(data))
        browse_share_selected_mode = data["browseShareSelectedMode"]
        users = data["users"]
        audio_info = data["audioInfo"]
        # audio_browse_info = data["audioBrowseInfo"]
        # browse_action = audio_browse_info['browseActionSelectedOption']
        # active_speaker_id = audio_browse_info['activeSpeakerId']
        audio_ids_list = audio_info
        # audio_ids_list = list(audio_info.keys())
        speaker_audioids = {}
        for audio_id in audio_ids_list:
            speakerid = audiodetails.get_audio_speakerid(
                transcriptions, audio_id)
            if (speakerid is not None):
                if (speakerid in speaker_audioids):
                    speaker_audioids[speakerid].append(audio_id)
                else:
                    speaker_audioids[speakerid] = [audio_id]
        logger.debug("speaker_audioids: %s", pformat(speaker_audioids))
        speaker_ids = projects.find_one({'projectname': activeprojectname},
                                        {'_id': 0, 'speakerIds': 1})
        if (speaker_ids):
            speaker_ids = speaker_ids['speakerIds']
        for user in users:
            if (browse_share_selected_mode == 'share'):
                if (user in speaker_ids):
                    user_speaker_ids = speaker_ids[user]
                    for speaker, audio_ids in speaker_audioids.items():
                        if (speaker in user_speaker_ids):
                            continue
                        else:
                            projects.update_one({"projectname": activeprojectname},
                                                {"$addToSet": {
                                                    "fileSpeakerIds."+user+"."+speaker: {"$each": audio_ids}
                                                }})
                else:
                    file_speaker_ids = projects.find_one({'projectname': activeprojectname},
                                                         {'_id': 0, 'fileSpeakerIds': 1})
                    logger.debug("file_speaker_ids: %s",
                                 pformat(file_speaker_ids))
                    if (file_speaker_ids):
                        file_speaker_ids = file_speaker_ids['fileSpeakerIds']
                        if (user in file_speaker_ids):
                            for speaker, audio_ids in speaker_audioids.items():
                                projects.update_one({"projectname": activeprojectname},
                                                    {"$addToSet": {
                                                        "fileSpeakerIds."+user+"."+speaker: {"$each": audio_ids}
                                                    }})
                            continue
                    projects.update_one({"projectname": activeprojectname},
                                        {"$set": {
                                            "fileSpeakerIds."+user: speaker_audioids
                                        }})
            elif (browse_share_selected_mode == 'remove'):
                for speaker, audio_ids in speaker_audioids.items():
                    projects.update_one({"projectname": activeprojectname},
                                        {"$pull": {
                                            "fileSpeakerIds."+user+"."+speaker: {"$in": audio_ids}
                                        }})
    except:
        logger.exception("")

    return jsonify(users=users)


@app.route('/get_jsonfile_data', methods=['GET', 'POST'])
@login_required
def get_jsonfile_data():
    # data through ajax
    data = json.loads(request.args.get('data'))
    # logger.debug('JSON Files name: %s', pformat(data))
    json_data = {}
    for var, filename in data.items():
        # logger.debug('JSON File name: %s', filename)
        JSONFilePath = os.path.join(basedir, 'jsonfiles', filename)
        json_data[var] = readJSONFile.readJSONFile(JSONFilePath)
    # logger.debug('json_data: %s', pformat(json_data))

    return jsonify(jsonData=json_data)
