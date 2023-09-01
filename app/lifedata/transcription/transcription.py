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
    audiodetails,
    getcommentstats,
    projectDetails
)
from app.lifedata.controller import (
    annotationdetails,
    copydatafromparentproject,
    crawled_data_details,
    data_project_info,
    savenewdataform,
    create_validation_type_project,
    get_validation_data,
    youtubecrawl,
    sourceid_to_souremetadata
)

from app.lifetagsets.controller import (
    save_tagset,
    tagset_details
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
                    return redirect(url_for('lifedata.transcription.home'))

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
            # pprint(audio_metadata)
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
            # print(transcription_details)
            activeprojectform['AudioFilePath'] = file_path
            transcription_regions, gloss, pos, boundary_count = audiodetails.getaudiotranscriptiondetails(
                data_collection, audio_id, transcription_by, transcription_details)
            activeprojectform['transcriptionRegions'] = transcription_regions
            # print(transcription_regions)
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

            except:
                speakerids = ''
                added_speaker_ids = ''
            scriptCode = readJSONFile.readJSONFile(scriptCodeJSONFilePath)
            activeprojectform['scriptCode'] = scriptCode
            langScript = readJSONFile.readJSONFile(langScriptJSONFilePath)
            activeprojectform['langScript'] = langScript
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
                                   shareinfo=shareinfo)
        except:
            logger.exception("")
            flash('Upload first audio file.')

    return render_template('transcription.html',
                           projectName=activeprojectname,
                           newData=activeprojectform,
                           data=currentuserprojectsname)

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
        new_audio_data_list = audio_data_list
        new_data['currentUsername'] = current_username
        new_data['activeProjectName'] = activeprojectname
        new_data['projectOwner'] = projectowner
        new_data['shareInfo'] = shareinfo
        new_data['speakerIds'] = speakerids
        new_data['audioData'] = new_audio_data_list
        new_data['audioDataFields'] = [
            'audioId', 'audioFilename', 'Audio File']
        new_data['totalRecords'] = total_records
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
                   shareChecked=share_checked)


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
                   activePage=page_id)


@transcription.route('/updateaudiobrowsetable', methods=['GET', 'POST'])
@login_required
def updateaudiobrowsetable():
    audio_data_fields = ['audioId', 'audioFilename', 'Audio File']
    audio_data_list = []
    try:
        # data through ajax
        audio_browse_info = json.loads(request.args.get('a'))
        logger.debug('audio_browse_info: %s', audio_browse_info)
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
                   shareChecked=share_checked)


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
            logger.debug('data: %s', pformat(data))

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
            new_audio_data_list = audio_data_list
            return jsonify(
                audioDataFields=audio_data_fields,
                audioData=new_audio_data_list,
                shareMode=share_mode,
                totalRecords=total_records,
                shareChecked=share_checked,
                audioSource=audio_src
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
                   activePage=page_id)
