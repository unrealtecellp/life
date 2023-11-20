# 6ae7e44db9ce6bad1ee4bbcf32e70edbc251fe65
"""Module containing the routes for the transcription part of the LiFE."""

from app import mongo
from flask import (
    Blueprint,
    render_template,
    jsonify,
    request,
    flash,
    redirect,
    url_for,
    send_file
)
from app.controller import (
    getactiveprojectname,
    getcurrentusername,
    getcurrentuserprojects,
    getdbcollections,
    getprojecttype,
    getprojectowner,
    getuserprojectinfo,
    readJSONFile,
    savenewproject,
    updateuserprojects,
    life_logging,
    readzip,
    savenewsentence,
    getactiveprojectform,
    # audiodetails,
    getcommentstats,
    projectDetails,
    processHTMLForm,
    speakerDetails
)
from app.lifedata.transcription.controller import (
    transcription_audiodetails,
    save_transcription_prompt
)

from flask_login import login_required
import os
from pprint import pformat
import json
from jsondiff import diff
from datetime import datetime
from zipfile import ZipFile
import glob
import pandas as pd

transcription = Blueprint('transcription', __name__,
                          template_folder='templates', static_folder='static')
basedir = os.path.abspath(os.path.dirname(__file__))
logger = life_logging.get_logger()
jsonfilesdir = '/'.join(basedir.split('/')[:-2]+['jsonfiles'])
scriptCodeJSONFilePath = os.path.join(jsonfilesdir, 'scriptCode.json')
langScriptJSONFilePath = os.path.join(jsonfilesdir, 'langScript.json')


@transcription.route('/', methods=['GET', 'POST'])
@transcription.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    try:
        projects, userprojects, projectsform, sentences, transcriptions, speakerdetails, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                                                                            'projects',
                                                                                                                            'userprojects',
                                                                                                                            'projectsform',
                                                                                                                            'sentences',
                                                                                                                            'transcriptions',
                                                                                                                            'speakerdetails',
                                                                                                                            'questionnaires')
        current_username = getcurrentusername.getcurrentusername()
        currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)
        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                        current_username,
                                                        activeprojectname)
        # print(shareinfo)
        if (shareinfo["sharemode"] == 0):
            return redirect(url_for('lifedata.transcription.audiobrowse'))

        if activeprojectname == '':
            flash(f"select a project from 'Change Active Project' to work on!")
            return redirect(url_for('home'))

        project_type = getprojecttype.getprojecttype(projects, activeprojectname)
        data_collection, = getdbcollections.getdbcollections(mongo, project_type)
        # logger.debug("data_collection: %s", data_collection)

        # if method is not 'POST'
        projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
        activeprojectform = getactiveprojectform.getactiveprojectform(projectsform,
                                                                    projectowner,
                                                                    activeprojectname)
        all_ques_ids = ''
        derived_from_project_type, derived_from_project_name = getprojecttype.getderivedfromprojectdetails(projects,
                                                                                                           activeprojectname)
        # logger.debug("derived_from_project_type: %s, derived_from_project_name: %s", 
        #              derived_from_project_type, derived_from_project_name)
        if (derived_from_project_type == 'questionnaires'):
            all_ques_ids = {'New': 'New'}
            ques_ids = projects.find_one({"projectname": derived_from_project_name},
                                         {
                                             "_id": 0,
                                             "questionnaireIds": 1
                                         })["questionnaireIds"]
            # all_ques_ids.extend(ques_ids)
            for ques_id in ques_ids:
                Q_Id = questionnaires.find_one({"projectname": derived_from_project_name,
                                                "quesId": ques_id,
                                                "quesdeleteFLAG": 0},
                                                {
                                                    "_id": 0,
                                                    "Q_Id": 1
                                                })["Q_Id"]
                all_ques_ids[ques_id] = Q_Id
            # logger.debug("all_ques_ids: %s", pformat(all_ques_ids))
        if activeprojectform is not None:
            try:
                # , audio_file_path, transcription_details
                # activespeakerid = getactivespeakerid.getactivespeakerid(userprojects, current_username)
                activespeakerid = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                        current_username,
                                                                        activeprojectname)['activespeakerId']
                speaker_audio_ids = transcription_audiodetails.get_speaker_audio_ids_new(projects,
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
                audio_id = transcription_audiodetails.getactiveaudioid(projects,
                                                        activeprojectname,
                                                        activespeakerid,
                                                        current_username)
                # logger.debug("audio_id: %s", audio_id)
                activeprojectform['prompt'] = ''
                if (audio_id != ''):

                    prompt = transcriptions.find_one({"projectname": activeprojectname,
                                                    "audioId": audio_id},
                                                    {"_id": 0, "prompt": 1}
                                                    )["prompt"]
                    activeprojectform['prompt'] = prompt
                    audio_delete_flag = transcription_audiodetails.get_audio_delete_flag(transcriptions,
                                                                        activeprojectname,
                                                                        audio_id)
                    if (audio_delete_flag or
                        audio_id not in speaker_audio_ids):
                        latest_audio_id = transcription_audiodetails.getnewaudioid(projects,
                                                                    activeprojectname,
                                                                    audio_id,
                                                                    activespeakerid,
                                                                    speaker_audio_ids,
                                                                    'next')
                        transcription_audiodetails.updatelatestaudioid(projects,
                                                        activeprojectname,
                                                        latest_audio_id,
                                                        current_username,
                                                        activespeakerid)
                        flash(f"Your last active audio seem to be deleted or revoked access by one of the shared user.\
                            Showing you the next audio in the list.")
                        return redirect(url_for('lifedata.transcription.home'))

                transcription_by = projectDetails.get_active_transcription_by(projects,
                                                                            activeprojectname,
                                                                            current_username,
                                                                            activespeakerid,
                                                                            audio_id)
                # logger.debug("transcription_by: %s", transcription_by)
                transcription_details = transcription_audiodetails.getaudiofiletranscription(data_collection,
                                                                            audio_id,
                                                                            transcription_by)

                audio_metadata = transcription_audiodetails.getaudiometadata(data_collection,
                                                            audio_id)
                # logger.debug('audio_metadata: %s', pformat(audio_metadata))
                # pprint(audio_metadata)
                activeprojectform['audioMetadata'] = audio_metadata['audioMetadata']
                last_updated_by = transcription_audiodetails.lastupdatedby(data_collection,
                                                            audio_id)
                activeprojectform['lastUpdatedBy'] = last_updated_by['updatedBy']
                # file_path = transcription_audiodetails.getaudiofilefromfs(mongo,
                #                                             basedir,
                #                                             audio_id,
                #                                             'audioId')
                audio_filename = transcription_audiodetails.get_audio_filename(data_collection,
                                                                audio_id)
                file_path = url_for('retrieve', filename=audio_filename)
                # logger.debug("audio_filename: %s, file_path: %s", audio_filename, file_path)
                activeprojectform['lastActiveId'] = audio_id
                activeprojectform['transcriptionDetails'] = transcription_details
                # print(transcription_details)
                activeprojectform['AudioFilePath'] = file_path
                transcription_regions, gloss, pos, boundary_count = transcription_audiodetails.getaudiotranscriptiondetails(
                    data_collection, audio_id, transcription_by, transcription_details)
                activeprojectform['transcriptionRegions'] = transcription_regions
                # print(transcription_regions)
                activeprojectform['boundaryCount'] = boundary_count
                # logger.debug("gloss: %s", gloss)
                if (len(gloss) != 0):
                    activeprojectform['glossDetails'] = gloss
                if (len(pos) != 0):
                    activeprojectform['posDetails'] = pos
                try:
                    # speakerids = projects.find_one({"projectname": activeprojectname},
                    #                                {"_id": 0, "speakerIds." +
                    #                                    current_username: 1}
                    #                                )["speakerIds"][current_username]
                    speakerids = transcription_audiodetails.combine_speaker_ids(projects,
                                                                activeprojectname,
                                                                current_username)
                    added_speaker_ids = transcription_audiodetails.addedspeakerids(
                        speakerdetails, activeprojectname)

                    transcriptions_by = transcription_audiodetails.get_audio_transcriptions_by(
                        projects, transcriptions, activeprojectname, audio_id)
                    # logger.debug("transcriptions_by: %s", transcriptions_by)

                except:
                    speakerids = ''
                    added_speaker_ids = ''
                scriptCode = readJSONFile.readJSONFile(scriptCodeJSONFilePath)
                activeprojectform['scriptCode'] = scriptCode
                langScript = readJSONFile.readJSONFile(langScriptJSONFilePath)
                activeprojectform['langScript'] = langScript
                # print(audio_id)
                # logger.debug("activeprojectform: %s", activeprojectform)

                return render_template('transcription.html',
                                    projectName=activeprojectname,
                                    newData=activeprojectform,
                                    data=currentuserprojectsname,
                                    speakerids=speakerids,
                                    addedspeakerids=added_speaker_ids,
                                    transcriptionsby=transcriptions_by,
                                    activetranscriptionby=transcription_by,
                                    activespeakerid=activespeakerid,
                                    commentstats=commentstats,
                                    shareinfo=shareinfo,
                                    allQuesIds=all_ques_ids)
            except:
                logger.exception("")
                flash('Upload first audio file.')
        
        # logger.debug("activeprojectform: %s", pformat(activeprojectform))
        return render_template('transcription.html',
                            projectName=activeprojectname,
                            newData=activeprojectform,
                            data=currentuserprojectsname,
                            shareinfo=shareinfo)
    except:
        logger.exception("")

# retrieve files from database
# TODO: User not able to download the data
@transcription.route('/retrieve/<filename>', methods=['GET'])
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

@transcription.route('/audiobrowse', methods=['GET', 'POST'])
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
        speakerids = transcription_audiodetails.combine_speaker_ids(projects,
                                                      activeprojectname,
                                                      current_username)
        speakerids.append('')
        active_speaker_id = shareinfo['activespeakerId']
        speaker_audio_ids = transcription_audiodetails.get_speaker_audio_ids_new(projects,
                                                                   activeprojectname,
                                                                   current_username,
                                                                   active_speaker_id)
        # logger.debug("speaker_audio_ids: %s", pformat(speaker_audio_ids))
        total_records = 0
        if (active_speaker_id != ''):
            total_records, audio_data_list = transcription_audiodetails.get_n_audios(transcriptions,
                                                                       activeprojectname,
                                                                       active_speaker_id,
                                                                       speaker_audio_ids)
        else:
            audio_data_list = []
        # get audio file src
        new_audio_data_list = audio_data_list
        # logger.debug("new_audio_data_list: %s", pformat(new_audio_data_list))
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

    return render_template('transcriptionaudiobrowse.html',
                           projectName=activeprojectname,
                           newData=new_data,
                           shareinfo=shareinfo)

@transcription.route('/updateaudiosortingsubcategories', methods=['GET', 'POST'])
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
        # logger.debug('selected_audio_sorting_category: %s',
        #              selected_audio_sorting_category)

        speakerids = transcription_audiodetails.combine_speaker_ids(projects,
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
            audio_sorting_sub_categories = transcription_audiodetails.get_audio_sorting_subcategories(speakerdetails_collection,
                                                                                        activeprojectname,
                                                                                        speakerids,
                                                                                        selected_audio_sorting_category
                                                                                        )
            selected_audio_sorting_sub_categories = ''
        elif (selected_audio_sorting_category == 'lifespeakerid'):
            audio_sorting_sub_categories = speakerids
            active_speaker_id = shareinfo['activespeakerId']
            speaker_audio_ids = transcription_audiodetails.get_speaker_audio_ids_new(projects,
                                                                       activeprojectname,
                                                                       current_username,
                                                                       active_speaker_id)
            logger.debug("active_speaker_id: %s", active_speaker_id)
            selected_audio_sorting_sub_categories = active_speaker_id

            if (active_speaker_id != ''):
                total_records, audio_data_list = transcription_audiodetails.get_n_audios(transcriptions,
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


@transcription.route('/filteraudiobrowsetable', methods=['GET', 'POST'])
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
        # logger.debug('audio_browse_info: %s', pformat(data))
        audio_browse_info = data['audioBrowseInfo']
        audio_file_count = audio_browse_info['audioFilesCount']
        audio_browse_action = audio_browse_info['browseActionSelectedOption']
        page_id = audio_browse_info['pageId']
        start_from = ((page_id*audio_file_count)-audio_file_count)
        number_of_audios = page_id*audio_file_count
        filter_options = data['selectedFilterOptions']
        total_records = 0
        audio_data_list = []
        speakerids = transcription_audiodetails.combine_speaker_ids(projects,
                                                      activeprojectname,
                                                      current_username)
    #     # logger.debug(audio_browse_info['activeSpeakerId'])
    #     active_speaker_id = audio_browse_info['activeSpeakerId']

        filtered_speakers_list = transcription_audiodetails.filter_speakers(speakerdetails_collection,
                                                              activeprojectname,
                                                              filter_options=filter_options)
        for speaker in filtered_speakers_list:
            speaker_audio_ids = transcription_audiodetails.get_speaker_audio_ids_new(projects,
                                                                       activeprojectname,
                                                                       current_username,
                                                                       speaker,
                                                                       audio_browse_action=audio_browse_action)
            if (speaker in speakerids):
                temp_total_records, temp_audio_data_list = transcription_audiodetails.get_n_audios(transcriptions,
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
        # logger.debug("new_audio_data_list count: %s", len(new_audio_data_list))
        # logger.debug("total_records count: %s", total_records)
    except:
        logger.exception("")

    return jsonify(audioDataFields=audio_data_fields,
                   audioData=new_audio_data_list,
                   shareMode=share_mode,
                   totalRecords=total_records,
                   shareChecked=share_checked,
                   activePage=page_id,
                   downloadChecked=download_checked)


@transcription.route('/updateaudiobrowsetable', methods=['GET', 'POST'])
@login_required
def updateaudiobrowsetable():
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
        # logger.debug(audio_browse_info['activeSpeakerId'])
        active_speaker_id = audio_browse_info['activeSpeakerId']
        audio_file_count = audio_browse_info['audioFilesCount']
        audio_browse_action = audio_browse_info['browseActionSelectedOption']
        total_records = 0
        speaker_audio_ids = transcription_audiodetails.get_speaker_audio_ids_new(projects,
                                                                   activeprojectname,
                                                                   current_username,
                                                                   active_speaker_id,
                                                                   audio_browse_action=audio_browse_action)
        if (active_speaker_id != ''):
            total_records, audio_data_list = transcription_audiodetails.get_n_audios(transcriptions,
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
    except:
        logger.exception("")

    return jsonify(audioDataFields=audio_data_fields,
                   audioData=new_audio_data_list,
                   shareMode=share_mode,
                   totalRecords=total_records,
                   shareChecked=share_checked,
                   downloadChecked=download_checked)


@transcription.route('/audiobrowseaction', methods=['GET', 'POST'])
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
        speaker_audio_ids = transcription_audiodetails.get_speaker_audio_ids_new(projects_collection,
                                                                   activeprojectname,
                                                                   current_username,
                                                                   active_speaker_id,
                                                                   audio_browse_action=browse_action)
        active_audio_id = transcription_audiodetails.getactiveaudioid(projects_collection,
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
                transcription_audiodetails.revoke_deleted_audio(projects_collection,
                                                  transcriptions_collection,
                                                  activeprojectname,
                                                  active_speaker_id,
                                                  audio_id,
                                                  speaker_audio_ids)
            else:
                transcription_audiodetails.delete_one_audio_file(projects_collection,
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


@transcription.route('/audiobrowseactionplay', methods=['GET', 'POST'])
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
            # logger.debug('data lifedata/transcription/audiobrowseactionplay: : %s', pformat(data))

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
            speaker_audio_ids = transcription_audiodetails.get_speaker_audio_ids_new(projects,
                                                                       activeprojectname,
                                                                       current_username,
                                                                       active_speaker_id,
                                                                       audio_browse_action=audio_browse_action)
            # audio_file_count = audio_browse_info['audioFilesCount']
            total_records = 0
            if (active_speaker_id != ''):
                total_records, audio_data_list = transcription_audiodetails.get_n_audios(transcriptions,
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
            # logger.debug("shareinfo: %s", shareinfo)
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


@transcription.route('/audiobrowseactionshare', methods=['GET', 'POST'])
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


@transcription.route('/audiobrowsechangepage', methods=['GET', 'POST'])
@login_required
def audiobrowsechangepage():
    audio_data_fields = ['audioId', 'audioFilename', 'Audio File']
    audio_data_list = []
    try:
        # data through ajax
        audio_browse_info = json.loads(request.args.get('a'))
        # logger.debug('audio_browse_info: %s', pformat(audio_browse_info))
        audio_count = audio_browse_info['audioFilesCount']
        audio_browse_action = audio_browse_info['browseActionSelectedOption']
        page_id = audio_browse_info['pageId']
        start_from = ((page_id*audio_count)-audio_count)
        number_of_audios = page_id*audio_count
        # logger.debug('pageId: %s, start_from: %s, number_of_audio_data: %s',
        #  page_id, start_from, number_of_audios)
        projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                   'projects',
                                                                                   'userprojects',
                                                                                   'transcriptions')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        # logger.debug(crawler_browse_info['activeSourceId'])
        active_speaker_id = audio_browse_info['activeSpeakerId']
        speaker_audio_ids = transcription_audiodetails.get_speaker_audio_ids_new(projects,
                                                                   activeprojectname,
                                                                   current_username,
                                                                   active_speaker_id,
                                                                   audio_browse_action=audio_browse_action)
        # logger.debug("speaker_audio_ids: %s", speaker_audio_ids)
        total_records = 0
        if (active_speaker_id != ''):
            total_records, audio_data_list = transcription_audiodetails.get_n_audios(transcriptions,
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
        # logger.debug("shareinfo: %s", pformat(shareinfo))
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

# uploadaudiofiles route
@transcription.route('/uploadaudiofiles', methods=['GET', 'POST'])
@login_required
def uploadaudiofiles():
    projects, userprojects, transcriptions, questionnaires = getdbcollections.getdbcollections(mongo,
                                                                               'projects',
                                                                               'userprojects',
                                                                               'transcriptions',
                                                                               'questionnaires')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    if request.method == 'POST':
        run_vad = False
        run_asr = False
        split_into_smaller_chunks = True
        get_audio_json = True
        prompt = {}
        derivedfromprojectdetails = {}

        data = dict(request.form.lists())
        logger.debug("Form data %s", data)
        if ('quesId' in data):
            quesId = data['quesId'][0]
            logger.debug("quesId: %s", quesId)
            found_prompt = questionnaires.find_one({"quesId": quesId},
                                             {"_id": 0, "prompt": 1})
            if (found_prompt):
                prompt = found_prompt['prompt']
                logger.debug("found prompt: %s", prompt)
                derived_from_project_type, derived_from_project_name = getprojecttype.getderivedfromprojectdetails(projects,
                                                                                                           activeprojectname)
                derivedfromprojectdetails = {
                    "derivedfromprojectname": derived_from_project_name,
                    "quesId": quesId
                }
                logger.debug("derivedfromprojectdetails: %s", derivedfromprojectdetails)
            else:
                logger.debug("not found prompt: %s", found_prompt)
        # return redirect(url_for('lifedata.transcription.home'))
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
        # print(get_audio_json)

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

        transcription_audiodetails.saveaudiofiles(mongo,
                                    projects,
                                    userprojects,
                                    transcriptions,
                                    projectowner,
                                    activeprojectname,
                                    current_username,
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
                                    prompt=prompt,
                                    update=False,
                                    slice_offset_value=slice_offset,
                                    min_boundary_size=min_boundary_size,
                                    derivedfromprojectdetails=derivedfromprojectdetails
                                    )

    return redirect(url_for('lifedata.transcription.home'))


# makeboundary route
@transcription.route('/makeboundary', methods=['GET', 'POST'])
@login_required
def makeboundary():
    projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                               'projects',
                                                                               'userprojects',
                                                                               'transcriptions')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
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
        # print(get_audio_json)

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

        transcription_audiodetails.save_boundaries_of_one_audio_file(mongo,
                                                       projects,
                                                       userprojects,
                                                       transcriptions,
                                                       projectowner,
                                                       activeprojectname,
                                                       current_username,
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

    return redirect(url_for('lifedata.transcription.home'))

@transcription.route('/addnewspeakerdetails', methods=['GET', 'POST'])
@login_required
def addnewspeakerdetails():
    projects, userprojects, speakerdetails = getdbcollections.getdbcollections(mongo,
                                                                               'projects',
                                                                               'userprojects',
                                                                               'speakerdetails')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
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
        if "managepage" in call_source:
            flash(
                'New source details added. Now you can upload the data for this source.')
            return redirect(url_for('managespeakermetadata'))
        else:
            flash(
                'New source details added. Now you can upload the data for this source.')
            return redirect(url_for('lifedata.transcription.home'))

    return redirect(url_for('lifedata.transcription.home'))


@transcription.route('/transcriptionpromptfile', methods=['GET', 'POST'])
@login_required
def transcriptionpromptfile():
    try:
        projects, userprojects, projectsform, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                                'projects',
                                                                                                'userprojects',
                                                                                                'projectsform',
                                                                                                'transcriptions'
                                                                                                )
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                        userprojects)
        projectowner = getprojectowner.getprojectowner(projects,
                                                        activeprojectname)
        
        # ques_audio_file = request.files
        # print(ques_audio_file)
        # last_active_ques_id = getactivequestionnaireid.getactivequestionnaireid(projects,
        #                                                                         activeprojectname,
        #                                                                         current_username)
        activespeakerid = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                current_username,
                                                                activeprojectname)['activespeakerId']
        audio_id = transcription_audiodetails.getactiveaudioid(projects,
                                                            activeprojectname,
                                                            activespeakerid,
                                                            current_username)
        
        if request.method == "POST":
            prompt_file = request.files.to_dict()
            logger.debug('prompt_file: %s', prompt_file)
            prompt_type = list(prompt_file.keys())[0].split('_')[1]
            # print(prompt_type)
        save_transcription_prompt.savepromptfile(mongo,
                                                projects,
                                                userprojects,
                                                projectsform,
                                                transcriptions,
                                                projectowner,
                                                activeprojectname,
                                                current_username,
                                                audio_id,
                                                prompt_file)
    except:
        logger.exception("")

    return redirect(url_for("lifedata.transcription.home"))

@transcription.route('/transcriptionprompttext', methods=['GET', 'POST'])
@login_required
def transcriptionprompttext():
    try:
        projects, userprojects, projectsform, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                                'projects',
                                                                                                'userprojects',
                                                                                                'projectsform',
                                                                                                'transcriptions'
                                                                                                )
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                        userprojects)
        projectowner = getprojectowner.getprojectowner(projects,
                                                        activeprojectname)
        
        # ques_audio_file = request.files
        # print(ques_audio_file)
        # last_active_ques_id = getactivequestionnaireid.getactivequestionnaireid(projects,
        #                                                                         activeprojectname,
        #                                                                         current_username)
        activespeakerid = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                current_username,
                                                                activeprojectname)['activespeakerId']
        audio_id = transcription_audiodetails.getactiveaudioid(projects,
                                                            activeprojectname,
                                                            activespeakerid,
                                                            current_username)
        
        if request.method == "POST":
            prompt_text = request.form.to_dict()
            logger.debug('prompt_text: %s', prompt_text)
            prompt_type = list(prompt_text.keys())[0].split('_')[1]
            # print(prompt_type)
        save_transcription_prompt.saveprompttext(mongo,
                                                projects,
                                                userprojects,
                                                projectsform,
                                                transcriptions,
                                                projectowner,
                                                activeprojectname,
                                                current_username,
                                                audio_id,
                                                prompt_text)
    except:
        logger.exception("")

    return redirect(url_for("lifedata.transcription.home"))
