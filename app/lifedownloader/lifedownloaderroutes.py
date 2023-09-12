"""Module containing the routes for the downloader part of the LiFe."""

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


ld = Blueprint('lifedownloader', __name__,
               template_folder='templates', static_folder='static')


@ld.route('/downloadtranscriptions', methods=['GET', 'POST'])
def downloadtranscriptions():
    print('Fetching transcriptions in life downloader')
    userprojects, projectsform, transcriptions = getdbcollections.getdbcollections(
        mongo, 'userprojects', 'projectsform', 'transcriptions')
    current_username = getcurrentusername.getcurrentusername()
    print('USERNAME: ', current_username)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(
        userprojects, current_username, activeprojectname)

    # if shareinfo['sharemode'] >= 1:
    if ('downloadchecked' in shareinfo and shareinfo['downloadchecked'] == 'true'):
        print(request.args)
        if request.method == 'GET':
            format_details = json.loads(
                request.args.get('data'))    # data through ajax
            print('format_details', format_details, type(format_details))
            data_format = format_details['format']
            download_audio = format_details['includeAudio']
            latest = format_details['latest']

        elif request.method == 'POST':
            form_data = request.form
            logger.debug('Form data %s', form_data)

            try:
                data_format = form_data.get("downloadFormat", "textgrid")
                if data_format == '' or data_format == None:
                    data_format = "textgrid"
            except:
                data_format = "textgrid"

            try:
                transcription_by = form_data.get(
                    "transcriptionBy", current_username)
                if transcription_by == '' or transcription_by == None:
                    data_format = current_username
            except:
                transcription_by = current_username

            try:
                download_audio = form_data.get("includeAudio", "")
                if download_audio == 'on':
                    download_audio = True
                else:
                    download_audio = False
            except:
                download_audio = False

            try:
                merge_transcriptions = form_data.get("mergeTranscriptions", "")
                if merge_transcriptions == 'on':
                    merge_transcriptions = True
                else:
                    merge_transcriptions = False
            except:
                merge_transcriptions = False

            try:
                single_transcriptions = form_data.get(
                    "singleTranscriptions", "")
                if single_transcriptions == 'on':
                    single_transcriptions = True
                else:
                    single_transcriptions = False
            except:
                single_transcriptions = True

            try:
                merge_same_intervals = request.form.get("mergeIntervals")

                if merge_same_intervals == 'on':
                    merge_same_intervals = True
                else:
                    merge_same_intervals = False
            except:
                merge_same_intervals = False

            try:
                retain_original_filename = request.form.get("retainFilename")

                if retain_original_filename == 'on':
                    retain_original_filename = True
                else:
                    retain_original_filename = False
            except:
                retain_original_filename = False

            try:
                empty_string = str(request.form.get("silenceTag"))
                if empty_string == None:
                    empty_string = '0'
            except:
                empty_string = '0'

        if ('sharelatestchecked' in shareinfo and shareinfo['sharelatestchecked'] == 'false'):
            if latest == 'latest':
                flash('This action is not allowed for you.')
                return redirect(url_for('enternewsentences'))
        # response_code = '0'
        # file_path = ''

        logger.debug("data_format: %s, transcription_by: %s, download_audio: %s, merge_transcriptions: %s, single_transcriptions: %s. merge_same_intervals: %s, retain_original_filename: %s, empty_string: %s",
                     data_format, transcription_by, download_audio, merge_transcriptions, single_transcriptions, merge_same_intervals, retain_original_filename, empty_string)

        response_code, file_path = downloadTextGrid.downloadTextGrid(transcriptions,
                                                                     projectsform,
                                                                     current_username,
                                                                     activeprojectname,
                                                                     transcription_by,
                                                                     data_format,
                                                                     empty_string,
                                                                     merge_same_intervals,
                                                                     download_audio=download_audio,
                                                                     get_individual_slices=single_transcriptions,
                                                                     merge_all_slices=merge_transcriptions,
                                                                     retain_original_filename=retain_original_filename,
                                                                     )
    # return response_file
        if response_code == '200':
            print('Response Code', response_code, 'File path', file_path)
            return send_file(file_path, as_attachment=True)
        else:
            print('Response Code', response_code, 'File path', file_path)
            flash('No transcriptions are available to download.')
            return redirect(url_for('enternewsentences'))
    else:
        flash('This action is not allowed for you.')

    return redirect(url_for('enternewsentences'))
    # return send_file(file_path, as_attachment=True)


@ld.route('/tgdownloader', methods=['GET', 'POST'])
def downloader():
    userprojects, = getdbcollections.getdbcollections(
        mongo, 'userprojects', )
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)

    basedir = os.path.abspath(os.path.dirname(__file__))
    print('Base directory', basedir)
    download_file = 'downloads/'+activeprojectname+'_textgrids.zip'
    zip_full_path = os.path.join(basedir, download_file)

    zip_path = 'lifedownloader/downloads/'+activeprojectname+'_textgrids.zip'
    print('Zip full path', zip_full_path)

    if os.path.exists(zip_full_path):
        return send_file(zip_path, as_attachment=True)
        # return redirect(url_for('enternewsentences'))
    else:
        flash('No transcriptions are available to download.')
        return redirect(url_for('enternewsentences'))
