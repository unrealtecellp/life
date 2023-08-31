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
                    return redirect(url_for('lifedata.transcription'))

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
