# 6ae7e44db9ce6bad1ee4bbcf32e70edbc251fe65
"""Module containing the routes for the transcription part of the LiFE."""

from app import mongo, cache
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
    audiodetails,
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
from app.lifedata.controller import (
    copydatafromparentproject,
)
from app.lifedata.transcription.controller import (
    transcription_audiodetails,
    save_transcription_prompt,
    transcription_report,
    update_owner_speakers
)

from app.lifetagsets.controller import (
    tagset_details
)

from app.lifemodels.controller import modelManager
from app.languages.controller import languageManager

from flask_login import login_required
import os
from pprint import pformat
import json
from jsondiff import diff
from datetime import datetime
from zipfile import ZipFile
import glob
import pandas as pd
from tqdm import tqdm
import io

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
        projects, userprojects, projectsform, sentences, transcriptions, speakerdetails, questionnaires, tagsets_collection = getdbcollections.getdbcollections(mongo,
                                                                                                                                                                'projects',
                                                                                                                                                                'userprojects',
                                                                                                                                                                'projectsform',
                                                                                                                                                                'sentences',
                                                                                                                                                                'transcriptions',
                                                                                                                                                                'speakerdetails',
                                                                                                                                                                'questionnaires',
                                                                                                                                                                'tagsets')
        current_username = getcurrentusername.getcurrentusername()
        currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        if activeprojectname == '':
            flash(f"select a project from 'Change Active Project' to work on!")
            return redirect(url_for('home'))

        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                          current_username,
                                                          activeprojectname)
        # print(shareinfo)
        if (shareinfo["sharemode"] == 0):
            return redirect(url_for('lifedata.transcription.audiobrowse'))

        project_type = getprojecttype.getprojecttype(
            projects, activeprojectname)
        data_collection, = getdbcollections.getdbcollections(
            mongo, project_type)
        # logger.debug("data_collection: %s", data_collection)

        # if method is not 'POST'
        projectowner = getprojectowner.getprojectowner(
            projects, activeprojectname)
        activeprojectform = getactiveprojectform.getactiveprojectform(projectsform,
                                                                      projectowner,
                                                                      activeprojectname)
        # logger.debug('trancription active project form: %s',
        #              pformat(activeprojectform))
        all_ques_ids = ''
        derived_from_project_type, derived_from_project_name = getprojecttype.getderivedfromprojectdetails(projects,
                                                                                                           activeprojectname)
        # logger.debug("derived_from_project_type: %s, derived_from_project_name: %s",
        #              derived_from_project_type, derived_from_project_name)
        if (derived_from_project_type == 'questionnaires'):
            all_ques_ids = {'New': 'New'}
            aggregate_output = questionnaires.aggregate([
                {
                    "$match": {
                        "projectname": derived_from_project_name,
                        "quesdeleteFLAG": 0
                    }
                },
                {
                    "$sort": {
                        "Q_Id": 1
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "Q_Id": 1,
                        "quesId": 1,
                        'prompt.content': 1
                    }
                }
            ])
            for doc in aggregate_output:
                # logger.debug("aggregate_output: %s", pformat(doc))
                Q_Id = doc
                ques_id = doc['quesId']
                q_id = Q_Id["Q_Id"][:5]
                lang_list = list(Q_Id['prompt']['content'].keys())
                if ('English-Latin' in lang_list):
                    get_text = Q_Id['prompt']['content']['English-Latin']['text']
                    all_ques_ids[ques_id] = q_id+'_'+Q_Id['prompt']['content']['English-Latin']['text'][list(get_text.keys())[0]]['textspan']['Latin']
                else:
                    lang_script = lang_list[0]
                    script = lang_script.split('-')[-1]
                    get_text = Q_Id['prompt']['content'][lang_script]['text']
                    all_ques_ids[ques_id] = q_id+'_'+Q_Id['prompt']['content'][lang_script]['text'][list(get_text.keys())[0]]['textspan'][script]
            # logger.debug("all_ques_ids: %s", pformat(all_ques_ids))
        if activeprojectform is not None:
            try:
                activespeakerid = shareinfo['activespeakerId']
                # logger.debug(activespeakerid)

                # TODO: All audios where all the speakers are present together (currently returns all those where the active speaker is present as one of the speakers)
                speaker_audio_ids = transcription_audiodetails.get_speaker_audio_ids_new(projects,
                                                                                         activeprojectname,
                                                                                         current_username,
                                                                                         activespeakerid)
                # logger.debug("speaker_audio_ids: %s", pformat(speaker_audio_ids))
                total_comments, annotated_comments, remaining_comments = getcommentstats.getcommentstatsnew(projects,
                                                                                                            data_collection,
                                                                                                            activeprojectname,
                                                                                                            activespeakerid,
                                                                                                            'transcriptionFLAG',
                                                                                                            'audio')
                commentstats = [total_comments,
                                annotated_comments, remaining_comments]
                # logger.debug("commentstats: %s", commentstats)
                # logger.debug("total_comments: %s", total_comments)
                # if (total_comments == 0):
                #     flash(f"Change active source ID")
                #     return redirect(url_for('lifedata.transcription.audiobrowse'))
                    # audio_id = ''
                # TODO: Get active speaker ID of the first speaker - also do the same while storing
                # else:
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
                        # TODO: This will need to be rewritten so that next audio is fetched for current combination
                        latest_audio_id = transcription_audiodetails.getnewaudioid(projects,
                                                                                   activeprojectname,
                                                                                   audio_id,
                                                                                   activespeakerid,
                                                                                   speaker_audio_ids,
                                                                                   'next')
                        # logger.debug(latest_audio_id)
                        # TODO: Can we store it in such a way that storing combination becomes possible; or only for the first speaker?
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
                                                                              current_username)
                # logger.debug("transcription_by: %s", transcription_by)
                transcription_details = transcription_audiodetails.getaudiofiletranscription(data_collection,
                                                                                             activeprojectname,
                                                                                             audio_id,
                                                                                             transcription_by)
                # logger.debug("transcription_details: %s", pformat(transcription_details))
                audio_metadata = transcription_audiodetails.getaudiometadata(data_collection,
                                                                             activeprojectname,
                                                                             audio_id)
                activeprojectform['audioMetadata'] = audio_metadata['audioMetadata']
                audio_speaker_ids = transcription_audiodetails.getaudiospeakerids(data_collection,
                                                                                  activeprojectname,
                                                                                  audio_id)
                # logger.debug('audio_metadata: %s', pformat(audio_metadata))
                # pprint(audio_metadata)
                activeprojectform['audioSpeakerIds'] = audio_speaker_ids
                last_updated_by = transcription_audiodetails.lastupdatedby(data_collection,
                                                                           activeprojectname,
                                                                           audio_id)

                activeprojectform['lastUpdatedBy'] = last_updated_by['updatedBy']
                # file_path = transcription_audiodetails.getaudiofilefromfs(mongo,
                #                                             basedir,
                #                                             audio_id,
                #                                             'audioId')
                audio_filename = transcription_audiodetails.get_audio_filename(data_collection,
                                                                               activeprojectname,
                                                                               audio_id)
                file_path = url_for('retrieve', filename=audio_filename)
                # logger.debug("audio_filename: %s, file_path: %s", audio_filename, file_path)
                activeprojectform['lastActiveId'] = audio_id
                activeprojectform['transcriptionDetails'] = transcription_details
                # logger.debug('transcription_details: %s', pformat(transcription_details))
                activeprojectform['AudioFilePath'] = file_path
                # logger.debug('transcription_details: %s', pformat(transcription_details))
                transcription_regions, gloss, pos, boundary_count = transcription_audiodetails.getaudiotranscriptiondetails(
                    data_collection,
                    activeprojectname,
                    audio_id,
                    transcription_by,
                    transcription_details)
                # logger.debug('transcription_details: %s', pformat(transcription_details))
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
                    # speakerids.append('')
                except:
                    speakerids = []
                    added_speaker_ids = []
                speaker_metadata = transcription_audiodetails.get_speaker_metadata(speakerdetails,
                                                                                   speakerids,
                                                                                   activeprojectname)
                # logger.debug('speakerids: %s, added_speaker_ids: %s, activespeakerid: %s',
                #              speakerids, added_speaker_ids, activespeakerid)
                if (current_username == projectowner):
                    speakerids = update_owner_speakers.update_owner_speakers(projects,
                          activeprojectname,
                          projectowner,
                          speakerids,
                          added_speaker_ids)
                # logger.debug('speakerids: %s, added_speaker_ids: %s, activespeakerid: %s',
                #              speakerids, added_speaker_ids, activespeakerid)
                activeprojectform['speakerIds'] = speakerids
                activeprojectform['addedSpeakerIds'] = added_speaker_ids
                activeprojectform['activespeakerId'] = activespeakerid
                activeprojectform['sourceMetadata'] = speaker_metadata
                scriptCode = readJSONFile.readJSONFile(scriptCodeJSONFilePath)
                activeprojectform['scriptCode'] = scriptCode
                langScript = readJSONFile.readJSONFile(langScriptJSONFilePath)
                activeprojectform['langScript'] = langScript
                activeprojectform['accessedOnTime'] = datetime.now().strftime(
                    "%d/%m/%y %H:%M:%S")
                # print(audio_id)

                if ('Tagsets' in activeprojectform):
                    annotation_types = activeprojectform['Tagsets'][1]
                    for annotation_type, tagset_ids in annotation_types.items():
                        if (len(tagset_ids) != 0):
                            tagset_id = tagset_ids[0]
                            tagset_name = tagset_details.get_tagset_name(
                                tagsets_collection, tagset_id)
                            if (len(tagset_name) != 0):
                                activeprojectform[annotation_type] = tagset_details.get_full_tagset_with_metadata(
                                    tagsets_collection, tagset_name)
                            else:
                                continue
                        else:
                            continue

                # logger.debug("activeprojectform: %s", pformat(activeprojectform))

                return render_template('transcription.html',
                                       projectName=activeprojectname,
                                       newData=activeprojectform,
                                       data=currentuserprojectsname,
                                       speakerids=speakerids,
                                       addedspeakerids=added_speaker_ids,
                                       transcriptionsby=transcriptions_by,
                                       activetranscriptionby=transcription_by,
                                       activespeakerid=activespeakerid,
                                       audiospeakerids=audio_speaker_ids,
                                       commentstats=commentstats,
                                       shareinfo=shareinfo,
                                       allQuesIds=all_ques_ids,
                                       derivedFromProjectType=derived_from_project_type)
            except:
                logger.exception("")
                flash('Upload first audio file.')

        # logger.debug("activeprojectform: %s", pformat(activeprojectform))
        return render_template('transcription.html',
                               projectName=activeprojectname,
                               newData=activeprojectform,
                               data=currentuserprojectsname,
                               shareinfo=shareinfo,
                               derivedFromProjectType=derived_from_project_type)
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
        projects, userprojects, transcriptions, speakerdetails_collection = getdbcollections.getdbcollections(mongo,
                                                                                                              'projects',
                                                                                                              'userprojects',
                                                                                                              'transcriptions',
                                                                                                              'speakerdetails')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        # logger.debug(activeprojectname)
        if (activeprojectname != ''):
            projectowner = getprojectowner.getprojectowner(projects,
                                                        activeprojectname)
            shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                            current_username,
                                                            activeprojectname)

            project_shared_with = projectDetails.get_shared_with_users(projects, activeprojectname)
            # logger.debug(project_shared_with)
            project_shared_with.append("latest")
            speakerids = transcription_audiodetails.combine_speaker_ids(projects,
                                                                        activeprojectname,
                                                                        current_username)
            speakerids.append('')
            speaker_metadata = transcription_audiodetails.get_speaker_metadata(speakerdetails_collection,
                                                                            speakerids,
                                                                            activeprojectname)
            # logger.debug('speaker_metadata: %s', speaker_metadata)
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
                                                                                        current_username,
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
            new_data['sourceMetadata'] = speaker_metadata
            new_data['audioData'] = new_audio_data_list
            new_data['audioDataFields'] = [
                'audioId', 'audioFilename', 'Transcribed', 'Shared With', 'Audio File']
            new_data['totalRecords'] = total_records
            new_data['transcriptionsBy'] = project_shared_with
            # logger.debug(new_data)
        else:
            # logger.debug('activeprojectname')
            flash(f"select a project from 'Change Active Project' to work on!")
            return redirect(url_for('home'))
    except:
        logger.exception("")

    return render_template('transcriptionaudiobrowse.html',
                           projectName=activeprojectname,
                           newData=new_data,
                           shareinfo=shareinfo)


@transcription.route('/updateaudiosortingsubcategories', methods=['GET', 'POST'])
@login_required
def updateaudiosortingsubcategories():
    audio_sorting_sub_categories = {}
    audio_data_fields = ['audioId', 'audioFilename',
                         'Transcribed', 'Shared With', 'Audio File']
    audio_data_list = []
    speaker_metadata = {}
    try:
        projects, userprojects, speakerdetails_collection, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                                              'projects',
                                                                                                              'userprojects',
                                                                                                              'speakerdetails',
                                                                                                              'transcriptions')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
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
        # logger.debug("speakerids: %s", pformat(speakerids))

        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                          current_username,
                                                          activeprojectname)
        total_records = 0
        share_mode = shareinfo['sharemode']
        share_checked = shareinfo['sharechecked']
        download_checked = shareinfo['downloadchecked']
        selected_audio_sorting_sub_categories = ''

        derived_from_project_type, derived_from_project_name = getprojecttype.getderivedfromprojectdetails(projects,
                                                                                                           activeprojectname)
        # logger.debug(derived_from_project_type)
        # logger.debug(derived_from_project_name)
        if (selected_audio_sorting_category == 'sourcemetainfo'):
            # audio_sorting_sub_categories = transcription_audiodetails.get_audio_sorting_subcategories(speakerdetails_collection,
            #                                                                                           activeprojectname,
            #                                                                                           speakerids,
            #                                                                                           selected_audio_sorting_category
            #                                                                                           )
            audio_sorting_sub_categories = transcription_audiodetails.get_audio_sorting_subcategories_new(speakerdetails_collection,
                                                                                                            activeprojectname,
                                                                                                            speakerids)
            # logger.debug("audio_sorting_sub_categories: %s", audio_sorting_sub_categories)
            if (derived_from_project_type != '' and
                    derived_from_project_name != ''):
                if (derived_from_project_type == 'questionnaires'):
                    audio_sorting_sub_categories_derived = transcription_audiodetails.get_audio_sorting_subcategories_derived(transcriptions,
                                                                                                                              activeprojectname,
                                                                                                                              speakerids,
                                                                                                                              audio_sorting_sub_categories
                                                                                                                              )
                    # logger.debug("audio_sorting_sub_categories_derived: %s", pformat(audio_sorting_sub_categories_derived))
            # logger.debug("audio_sorting_sub_categories: %s", pformat(audio_sorting_sub_categories))
        elif (selected_audio_sorting_category == 'lifespeakerid'):
            audio_sorting_sub_categories = speakerids
            active_speaker_id = shareinfo['activespeakerId']
            speaker_audio_ids = transcription_audiodetails.get_speaker_audio_ids_new(projects,
                                                                                     activeprojectname,
                                                                                     current_username,
                                                                                     active_speaker_id)
            # logger.debug("active_speaker_id: %s", active_speaker_id)
            selected_audio_sorting_sub_categories = active_speaker_id

            if (active_speaker_id != ''):
                total_records, audio_data_list = transcription_audiodetails.get_n_audios(transcriptions,
                                                                                         activeprojectname,
                                                                                         current_username,
                                                                                         active_speaker_id,
                                                                                         speaker_audio_ids,
                                                                                         start_from=0,
                                                                                         number_of_audios=audio_file_count,
                                                                                         audio_delete_flag=audio_browse_action)
            speaker_metadata = transcription_audiodetails.get_speaker_metadata(speakerdetails_collection,
                                                                               speakerids,
                                                                               activeprojectname)
            # logger.debug('speaker_metadata: %s', speaker_metadata)
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
                   downloadChecked=download_checked,
                   sourceMetadata=speaker_metadata)

@transcription.route('/filteraudiobrowsetable', methods=['GET', 'POST'])
@login_required
# @cache.cached(timeout=10)
def filteraudiobrowsetable():
    audio_data_fields = ['audioId', 'audioFilename',
                         'Transcribed', 'Shared With', 'Audio File']
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
        temp_audio_data_list_partial = []
        temp_audio_data_list = []
        temp_audio_data_list_derived = []
        total_records = 0
        audio_data_list = []
        speaker_audio_ids_all = []
        speaker_all = []
        speakerids = transcription_audiodetails.combine_speaker_ids(projects,
                                                                    activeprojectname,
                                                                    current_username)
        # logger.debug(speakerids)
    #     # logger.debug(audio_browse_info['activeSpeakerId'])
    #     active_speaker_id = audio_browse_info['activeSpeakerId']

        filtered_speakers_list, used_filter_options = transcription_audiodetails.filter_speakers(speakerdetails_collection,
                                                                            activeprojectname,
                                                                            filter_options=filter_options)
        # logger.debug("filtered_speakers_list: %s", filtered_speakers_list)
        # logger.debug(used_filter_options)
        for speaker in sorted(filtered_speakers_list):
            # logger.debug(speaker)
            speaker_audio_ids = transcription_audiodetails.get_speaker_audio_ids_new(projects,
                                                                                     activeprojectname,
                                                                                     current_username,
                                                                                     speaker,
                                                                                     audio_browse_action=audio_browse_action)
            # logger.debug(type(speaker_audio_ids))
            # logger.debug(speaker_audio_ids)
            speaker_audio_ids_all.extend(speaker_audio_ids)
            # logger.debug(speaker_audio_ids_all)
            if (speaker in speakerids):
                # logger.debug(speaker)
                speaker_all.append(speaker)
                # logger.debug(speaker_all)
        if (len(speaker_all) != 0):
            temp_total_records, temp_audio_data_list_partial = transcription_audiodetails.get_n_audios(transcriptions,
                                                                                                activeprojectname,
                                                                                                current_username,
                                                                                                # speaker,
                                                                                                # speaker_audio_ids,
                                                                                                # start_from=0,
                                                                                                # number_of_audios=audio_file_count,
                                                                                                speaker_all,
                                                                                                speaker_audio_ids_all,
                                                                                                start_from=start_from,
                                                                                                number_of_audios=number_of_audios,
                                                                                                audio_delete_flag=audio_browse_action,
                                                                                                all_data=True)
            # logger.debug("temp_audio_data_list_partial count: %s", len(temp_audio_data_list_partial))
            temp_audio_data_list.extend(temp_audio_data_list_partial)
            # logger.debug("temp_audio_data_list count: %s", len(temp_audio_data_list))
            total_records += temp_total_records
            # logger.debug("temp_audio_data_list count: %s",
            #              len(temp_audio_data_list))
            # logger.debug("temp_audio_data_list: %s",
            #              temp_audio_data_list)
            # logger.debug("temp_total_records count: %s",
            #              temp_total_records)
            # audio_data_list.extend(temp_audio_data_list)
            # logger.debug("audio_data_list count: %s", len(audio_data_list))
            # total_records += temp_total_records
            # if (len(audio_data_list) == audio_file_count):
            #     break

        derived_from_project_type, derived_from_project_name = getprojecttype.getderivedfromprojectdetails(projects,
                                                                                                           activeprojectname)
        if (derived_from_project_type != '' and
                derived_from_project_name != ''):
            if (derived_from_project_type == 'questionnaires'):
                # filtered_speakers_list_derived = transcription_audiodetails.filter_speakers_derived(transcriptions,
                #                                                                                     activeprojectname,
                #                                                                                     filter_options=filter_options)
                temp_total_records_derived, temp_audio_data_list_derived = transcription_audiodetails.filter_speakers_derived(transcriptions,
                                                                                                                                activeprojectname,
                                                                                                                                current_username,
                                                                                                                                filtered_speakers_list,
                                                                                                                                used_filter_options,
                                                                                                                                filter_options=filter_options,
                                                                                                                                start_from=start_from,
                                                                                                                                number_of_audios=number_of_audios,)
                if (len(temp_audio_data_list_derived) != 0):
                    temp_audio_data_list = []
                    total_records = temp_total_records_derived
                # logger.debug("temp_audio_data_list_derived count: %s",
                #             len(temp_audio_data_list_derived))
                # logger.debug("temp_audio_data_list_derived: %s",
                #             temp_audio_data_list_derived)
                # logger.debug("temp_total_records_derived count: %s",
                #             temp_total_records_derived)
                # audio_data_list.extend(temp_audio_data_list)
                # total_records += temp_total_records
                # logger.debug("filtered_speakers_list_derived: %s", filtered_speakers_list_derived)
                # filtered_speakers_list.extend(filtered_speakers_list_derived)
        # if (temp_audio_data_list):
        #     logger.debug("if (temp_audio_data_list): %s", temp_audio_data_list)
        # else:
        #     logger.debug("if (temp_audio_data_list): %s", temp_audio_data_list)
        for audio_info_derived in temp_audio_data_list_derived:
            if (temp_audio_data_list):
                if (audio_info_derived in temp_audio_data_list):
                    # logger.debug("audio_info_derived: %s", audio_info_derived)
                    if (audio_info_derived not in audio_data_list):
                        audio_data_list.append(audio_info_derived)
            else:
                audio_data_list = temp_audio_data_list_derived
        for audio_info in temp_audio_data_list:
            if (temp_audio_data_list_derived):
                if (audio_info in temp_audio_data_list_derived):
                    # logger.debug("audio_info: %s", audio_info)
                    if (audio_info not in audio_data_list):
                        audio_data_list.append(audio_info)
            else:
                audio_data_list = temp_audio_data_list
            # audio_id_derived = audio_info_derived["audioId"]
            # for audio_info in temp_audio_data_list:
            #     audio_id
        # total_records += len(audio_data_list)
        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                          current_username,
                                                          activeprojectname)
        share_mode = shareinfo['sharemode']
        share_checked = shareinfo['sharechecked']
        download_checked = shareinfo['downloadchecked']
        # new_audio_data_list = audio_data_list[start_from:number_of_audios]
        new_audio_data_list = audio_data_list
        # new_audio_data_list = list(set(new_audio_data_list))
        # logger.debug("new_audio_data_list: %s", new_audio_data_list)
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
    audio_data_fields = ['audioId', 'audioFilename',
                         'Transcribed', 'Shared With', 'Audio File']
    audio_data_list = []
    try:
        # data through ajax
        audio_browse_info = json.loads(request.args.get('a'))
        # logger.debug('audio_browse_info: %s', pformat(audio_browse_info))
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
                                                                                     current_username,
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
    audio_data_fields = ['audioId', 'audioFilename',
                         'Transcribed', 'Shared With', 'Audio File']
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
            audio_browse_action = audio_browse_info['browseActionSelectedOption']
            selected_audio_sorting_category = data['selectedAudioSortingCategories']
            filter_options = data['selectedFilterOptions']
            audio_filename = list(data_info.values())[0]
            audio_count = audio_browse_info['audioFilesCount']
            page_id = audio_browse_info['pageId']
            start_from = ((page_id*audio_count)-audio_count)
            number_of_audios = page_id*audio_count
            # logger.debug("audio_filename: %s", audio_filename)
            # audio_src = url_for('retrieve', filename=audio_filename)
            audio_src = os.path.join('retrieve', audio_filename)
            # logger.debug(f"audio_src: {audio_src}")
            # logger.debug(audio_browse_info['activeSpeakerId'])
            if (selected_audio_sorting_category == 'sourcemetainfo'):
                temp_audio_data_list_partial = []
                temp_audio_data_list = []
                temp_audio_data_list_derived = []
                total_records = 0
                audio_data_list = []
                speaker_audio_ids_all = []
                speaker_all = []
                speakerids = transcription_audiodetails.combine_speaker_ids(projects,
                                                                            activeprojectname,
                                                                            current_username)

                filtered_speakers_list, used_filter_options = transcription_audiodetails.filter_speakers(speakerdetails_collection,
                                                                                                            activeprojectname,
                                                                                                            filter_options=filter_options)
                for speaker in sorted(filtered_speakers_list):
                    # logger.debug(speaker)
                    speaker_audio_ids = transcription_audiodetails.get_speaker_audio_ids_new(projects,
                                                                                                activeprojectname,
                                                                                                current_username,
                                                                                                speaker,
                                                                                                audio_browse_action=audio_browse_action)
                    speaker_audio_ids_all.extend(speaker_audio_ids)
                    # logger.debug(speaker_audio_ids_all)
                    if (speaker in speakerids):
                        # logger.debug(speaker)
                        speaker_all.append(speaker)
                        # logger.debug(speaker_all)
                if (len(speaker_all) != 0):
                    temp_total_records, temp_audio_data_list_partial = transcription_audiodetails.get_n_audios(transcriptions,
                                                                                                                activeprojectname,
                                                                                                                current_username,
                                                                                                                speaker_all,
                                                                                                                speaker_audio_ids_all,
                                                                                                                start_from=start_from,
                                                                                                                number_of_audios=number_of_audios,
                                                                                                                audio_delete_flag=audio_browse_action,
                                                                                                                all_data=True)
                    # logger.debug("temp_audio_data_list_partial count: %s", len(temp_audio_data_list_partial))
                    temp_audio_data_list.extend(temp_audio_data_list_partial)
                    # logger.debug("temp_audio_data_list count: %s", len(temp_audio_data_list))
                    total_records += temp_total_records
                derived_from_project_type, derived_from_project_name = getprojecttype.getderivedfromprojectdetails(projects, activeprojectname)
                if (derived_from_project_type != '' and
                        derived_from_project_name != ''):
                    if (derived_from_project_type == 'questionnaires'):
                        temp_total_records_derived, temp_audio_data_list_derived = transcription_audiodetails.filter_speakers_derived(transcriptions,
                                                                                                                                        activeprojectname,
                                                                                                                                        current_username,
                                                                                                                                        filtered_speakers_list,
                                                                                                                                        used_filter_options,
                                                                                                                                        filter_options=filter_options,
                                                                                                                                        start_from=start_from,
                                                                                                                                        number_of_audios=number_of_audios,)
                        if (len(temp_audio_data_list_derived) != 0):
                            temp_audio_data_list = []
                            total_records = temp_total_records_derived
                for audio_info_derived in temp_audio_data_list_derived:
                    if (temp_audio_data_list):
                        if (audio_info_derived in temp_audio_data_list):
                            # logger.debug("audio_info_derived: %s", audio_info_derived)
                            if (audio_info_derived not in audio_data_list):
                                audio_data_list.append(audio_info_derived)
                    else:
                        audio_data_list = temp_audio_data_list_derived
                for audio_info in temp_audio_data_list:
                    if (temp_audio_data_list_derived):
                        if (audio_info in temp_audio_data_list_derived):
                            # logger.debug("audio_info: %s", audio_info)
                            if (audio_info not in audio_data_list):
                                audio_data_list.append(audio_info)
                    else:
                        audio_data_list = temp_audio_data_list
            elif (selected_audio_sorting_category == 'lifespeakerid'):
                active_speaker_id = audio_browse_info['activeSpeakerId']
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
                                                                                            current_username,
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
        # logger.debug("data_id: %s", data_id)
        return jsonify(commentInfo={})
    except:
        logger.exception("")
        return jsonify(commentInfo={})


@transcription.route('/audiobrowsechangepage', methods=['GET', 'POST'])
@login_required
def audiobrowsechangepage():
    audio_data_fields = ['audioId', 'audioFilename',
                         'Transcribed', 'Shared With', 'Audio File']
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
                                                                                     current_username,
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
        logger.info("All Form data %s", request.form)
        # logger.info("All Form data submitted %s", request.form.formData)
        logger.info("Form data %s", data)
        if ('quesId' in data):
            quesId = data['quesId'][0]
            # logger.debug("quesId: %s", quesId)
            found_prompt = questionnaires.find_one({"quesId": quesId},
                                                   {"_id": 0, "prompt": 1})
            if (found_prompt):
                prompt = found_prompt['prompt']
                # logger.debug("found prompt: %s", prompt)
                derived_from_project_type, derived_from_project_name = getprojecttype.getderivedfromprojectdetails(projects,
                                                                                                                   activeprojectname)
                derivedfromprojectdetails = {
                    "derivedfromprojectname": derived_from_project_name,
                    "quesId": quesId
                }
                # logger.debug("derivedfromprojectdetails: %s",
                #              derivedfromprojectdetails)
            else:
                logger.debug("not found prompt: %s", found_prompt)
        # return redirect(url_for('lifedata.transcription.home'))
        new_audio_file = request.files.to_dict()
        logger.info('New audio files %s', new_audio_file)
        # logger.info("Request %s", request)
        # logger.info("All Form data submitted %s\n%s\n%s",
        #             request.data, request.form, request.args)
        logger.info("request JSON %s", request.__dict__)
        # speakerId = data['speakerId']
        if ('speakerId' in data):
            speakerId = data['speakerId']
            if ('null' in speakerId):
                speakerId = [getuserprojectinfo.getuserprojectinfo(userprojects,
                                                            current_username,
                                                            activeprojectname)['activespeakerId']]
        else:
            speakerId = [getuserprojectinfo.getuserprojectinfo(userprojects,
                                                            current_username,
                                                            activeprojectname)['activespeakerId']]

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
        vad_model_name = data['vadAlgorithm'][0]
        # vad_model_name = 'vadsilero'
        if 'vadsilero' in vad_model_name:
            vad_model_type = 'local'
            vad_model_path = 'snakers4/silero-vad'

            vad_model_params = {
                "model_path": vad_model_path
            }

            vad_model = {
                'model_name': vad_model_name,
                'model_type': vad_model_type,
                'model_params': vad_model_params
            }
        else:
            vad_model = {}

        logger.info('VAD Model %s', vad_model)

        # if ('file' in new_audio_file):
        #     new_audio_file = new_audio_file['file']

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
                                                  vad_model=vad_model,
                                                  asr_model={},
                                                  transcription_type='sentence',
                                                  boundary_threshold=boundary_threshold,
                                                  slice_threshold=slice_threshold,
                                                  # max size of each slice (in seconds), if large audio is to be automatically divided into multiple parts
                                                  max_slice_size=slice_size,
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
        # logger.debug("Form data %s", data)
        speakerId = data['speakerId'][0]
        # new_audio_file = request.files.to_dict()
        audio_filename = data['audiofile'][0]
        # converts into seconds
        audio_duration = float(data['audioduration'][0]) * 60
        existing_audio_details = transcriptions.find_one(
            {'projectname': activeprojectname, 'audioFilename': audio_filename})
        # logger.debug("Existing audio data %s", existing_audio_details)

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

        accessed_time = data['accessedOnTime']
        logger.info('Accessed time %s', accessed_time)

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

        vad_model_name = data['vadAlgorithm-boundary'][0]
        # vad_model_name = 'vadsilero'
        if 'vadsilero' in vad_model_name:
            vad_model_type = 'local'
            vad_model_path = 'snakers4/silero-vad'

            vad_model_params = {
                "model_path": vad_model_path
            }

            vad_model = {
                'model_name': vad_model_name,
                'model_type': vad_model_type,
                'model_params': vad_model_params
            }
        else:
            vad_model = {}

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
                                                                     vad_model=vad_model,
                                                                     asr_model={},
                                                                     transcription_type='sentence',
                                                                     boundary_threshold=boundary_threshold,
                                                                     min_boundary_size=min_boundary_size,
                                                                     save_for_user=overwrite_user,
                                                                     accessed_time=accessed_time
                                                                     )
    return redirect(url_for('lifedata.transcription.home'))


# maketranscription route
@transcription.route('/maketranscription', methods=['GET', 'POST'])
@login_required
def maketranscription():
    projects, userprojects, transcriptions, lifeappconfigs, projectsform, languages = getdbcollections.getdbcollections(mongo,
                                                                                                                        'projects',
                                                                                                                        'userprojects',
                                                                                                                        'transcriptions',
                                                                                                                        'lifeappconfigs',
                                                                                                                        'projectsform',
                                                                                                                        'languages')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    audio_language = getactiveprojectform.getaudiolanguage(
        projectsform, projectowner, activeprojectname)
    audio_lang_code = languageManager.get_bcp_language_code(
        languages, audio_language)

    if request.method == 'POST':
        run_vad = False
        run_asr = True
        get_audio_json = False
        split_into_smaller_chunks = False
        # overwrite_user = False

        data = dict(request.form.lists())
        # logger.debug("Form data %s", data)
        transcription_source = data['transcribeUsingSelect2'][0]

        if transcription_source == 'hfinference':
            if not 'hfinferenceagree' in data:
                # flash('')
                flash(
                    'We do not have sufficient permission to send the data to HF Inference Server.', category='error')
                return redirect(url_for('lifedata.transcription.home'))

        speakerId = data['asrSpeakerId'][0]
        # new_audio_file = request.files.to_dict()
        audio_filename = data['audiofile'][0]
        # converts into seconds
        audio_duration = float(data['audioduration'][0]) * 60
        existing_audio_details = transcriptions.find_one(
            {'projectname': activeprojectname, 'audioFilename': audio_filename})
        # logger.debug("Existing audio data %s", existing_audio_details)

        if 'modelId' in data:
            model_name = data['modelId'][0]
        else:
            model_name = ''

        if 'scriptName' in data:
            script_name = data['scriptName']
        else:
            script_name = []

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
            boundary_level = data['overwrite-my-boundaries'][0].strip()
            if boundary_level == '':
                create_boundaries = False
            else:
                create_boundaries = True
        else:
            create_boundaries = False

        if 'overwrite-my-transcriptions' in data:
            save_for_user = True
        else:
            save_for_user = False
        # print(get_audio_json)

        if 'minBoundarySize' in data:
            min_boundary_size = float(data['minBoundarySize'][0])
        else:
            min_boundary_size = 2.0

        if 'get-roman' in data:
            script_name.append('Latin')

        if 'get-ipa' in data:
            script_name.append('IPA')

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
        accessed_time = data['accessedOnTime'][0]

        # logger.debug(model_name)
        model_info = model_name.split('##')
        model_name = model_info[1]
        model_lang_code = model_info[0]
        if 'bhashini' in transcription_source:
            hf_token = ''
            model_name = model_name.replace('bhashini_', '')
            model_type = 'bhashini'
            create_boundaries = False
        else:
            hf_token = modelManager.get_hf_tokens(
                lifeappconfigs, current_username)
            model_type = 'hfapi'

        asr_model = {
            'model_name': model_name,
            'model_type': model_type,
            'model_params': {
                'model_path': model_name,
                'model_api': transcription_source,
                'boundary_level': boundary_level,
                'language_code': audio_lang_code,
                'model_language_code': model_lang_code
            },
            'target': script_name
        }
        # logger.debug("create_new_boundaries: %s", create_boundaries)
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
                                                                     asr_model=asr_model,
                                                                     transcription_type='sentence',
                                                                     boundary_threshold=boundary_threshold,
                                                                     min_boundary_size=min_boundary_size,
                                                                     save_for_user=save_for_user,
                                                                     hf_token=hf_token,
                                                                     audio_details=existing_audio_details,
                                                                     create_boundaries=create_boundaries,
                                                                     accessed_time=accessed_time
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

        # logger.debug("All form %s", form_data)

        metadata_schema, audio_source, call_source, upload_type, exclude_fields = processHTMLForm.get_metadata_header_details(
            form_data)

        # logger.debug("Metadata Schema %s", metadata_schema)
        # logger.debug("Call source %s", call_source)

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


@transcription.route('/updateaudiosettings', methods=['GET', 'POST'])
@login_required
def updateaudiosettings():
    projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                               'projects',
                                                                               'userprojects',
                                                                               'transcriptions')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    # projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    if request.method == 'POST':
        form_data = request.form
        audio_filename = form_data.get('settingsaudiofile')
        audio_id = [audio_filename[:audio_filename.find('_')]]
        speaker_ids = form_data.getlist('speakerIdEdit')
        # logger.info('Submitted info %s', form_data)
        # logger.info('Data %s %s', speaker_ids, audio_id)

        transcription_audiodetails.update_audio_speaker_ids(projects,
                                                            userprojects,
                                                            transcriptions,
                                                            activeprojectname,
                                                            current_username,
                                                            speaker_ids,
                                                            audio_id)
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
            # logger.debug('prompt_file: %s', prompt_file)
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
            # logger.debug('prompt_text: %s', prompt_text)
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


@transcription.route('/syncaudio', methods=['GET', 'POST'])
@login_required
def syncaudio():
    try:
        projects, userprojects, crawling, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                             'projects',
                                                                                             'userprojects',
                                                                                             'crawling',
                                                                                             'transcriptions'
                                                                                             )
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        derive_from_project_type, derive_from_project_name = getprojecttype.getderivedfromprojectdetails(projects,
                                                                                                         activeprojectname)
        sync_audio_status = False
        if (derive_from_project_name != ''):
            if (derive_from_project_type == 'crawling'):
                copydatafromparentproject.sync_transcription_project_from_crawling_project(mongo,
                                                                                           projects,
                                                                                           userprojects,
                                                                                           crawling,
                                                                                           transcriptions,
                                                                                           derive_from_project_name,
                                                                                           activeprojectname,
                                                                                           current_username)
                sync_audio_status = True
    except:
        logger.exception("")

    return jsonify(syncAudioStatus=sync_audio_status)


@transcription.route('/getScriptsList', methods=['GET', 'POST'])
@login_required
def getScriptsList():
    try:
        userprojects, projectsform = getdbcollections.getdbcollections(
            mongo, 'userprojects', 'projectsform')
        current_username = getcurrentusername.getcurrentusername()
        # logger.debug('USERNAME: %s', current_username)
        activeprojectname = getactiveprojectname.getactiveprojectname(
            current_username, userprojects)
        language_scripts = projectDetails.get_audio_language_scripts(
            projectsform, activeprojectname)
        logger.info('Language scripts: %s', language_scripts)
        return jsonify({'scripts': language_scripts['scripts']})
    except:
        logger.exception("")


@transcription.route('/toggleComplete', methods=['GET', 'POST'])
@login_required
def toggleComplete():
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
        # logger.info("transcription_data receieved: %s",
        #             pformat(transcription_data))
        lastActiveId = transcription_data['lastActiveId']
        lastActiveId = transcription_data['lastActiveId']
        accessedOnTime = transcription_data['accessedOnTime']

        speaker_audio_ids = audiodetails.get_speaker_audio_ids_new(projects,
                                                                   activeprojectname,
                                                                   current_username,
                                                                   activespeakerid)
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
            return jsonify({'status': -1})

        complete_status = transcription_audiodetails.toggle_transcription_complete_status(transcriptions,
                                                                                          activeprojectname,
                                                                                          current_username,
                                                                                          lastActiveId,
                                                                                          accessedOnTime)
        # logger.debug('Status %s', complete_status)
        return jsonify({'status': complete_status})
    except:
        logger.exception("")


def toHHMMSS(secs):
    sec_num = secs
    hours   = sec_num / 3600
    minutes = (sec_num / 60) % 60
    seconds = sec_num % 60

    return "%02d:%02d:%02d" % (hours, minutes, seconds)

@transcription.route('/transcriptionreport', methods=['GET', 'POST'])
@login_required
def transcriptionreport():
    userprojects, transcriptions_collection = getdbcollections.getdbcollections(mongo,
                                                                                'userprojects',
                                                                                'transcriptions')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)

    audio_duration_project, doc_count_project = transcription_report.total_audio_duration_project(mongo,
                                                                                                  transcriptions_collection,
                                                                                                  activeprojectname)
    audio_duration_transcribed, doc_count_transcribed = transcription_report.total_audio_duration_transcribed(mongo,
                                                                                                              transcriptions_collection,
                                                                                                              activeprojectname)
    audio_duration_transcribed_boundary = transcription_report.total_audio_duration_boundary(transcriptions_collection,
                                                                                             activeprojectname)

    # logger.debug(f"audio_duration_project: {audio_duration_project}\ndoc_count_project: {doc_count_project}")
    # logger.debug(f"audio_duration_transcribed: {audio_duration_transcribed}\ndoc_count_transcribed: {doc_count_transcribed}")
    # logger.debug(f"audio_duration_transcribed_boundary: {audio_duration_transcribed_boundary}")

    transcription_report_df = pd.DataFrame(columns=['Project Name',
                                              'Audio Duration Project(HH:MM:SS)',
                                              'File Count Project',
                                              'Audio Duration Transcribed',
                                              'File Count Transcribed',
                                              'Audio Duration Transcribed(Boundary)'])

    transcription_report_df['Project Name'] = [activeprojectname]
    transcription_report_df['Audio Duration Project(HH:MM:SS)'] = [toHHMMSS(audio_duration_project)]
    transcription_report_df['File Count Project'] = [doc_count_project]
    transcription_report_df['Audio Duration Transcribed'] = [toHHMMSS(audio_duration_transcribed)]
    transcription_report_df['File Count Transcribed'] = [doc_count_transcribed]
    transcription_report_df['Audio Duration Transcribed(Boundary)'] = [toHHMMSS(audio_duration_transcribed_boundary)]
    download_transcription_report_filename = activeprojectname+'_transcription_report.csv'
    csv_buffer = io.BytesIO()
    transcription_report_df.to_csv(csv_buffer, 
                            index=False)
    csv_buffer.seek(0)

    return send_file(csv_buffer,
                        mimetype='text/csv',
                        download_name=download_transcription_report_filename,
                        as_attachment=True)
    # return jsonify(totalAudioDurationProject=audio_duration_project,
    #                docCountProject=doc_count_project,
    #                totalAudioDurationTranscribed=audio_duration_transcribed,
    #                docCountTranscribed=doc_count_transcribed,
    #                totalAudioDurationTranscribedBoundary=audio_duration_transcribed_boundary)
