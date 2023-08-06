"""Module containing the routes for the downloader part of the LiFe."""

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
    userdetails
)

from app.lifedownloader.controller import (
    downloadTextGrid
)


from flask import Blueprint, render_template

ld = Blueprint('lifedownloader', __name__,
               template_folder='templates', static_folder='static')


@ld.route('/downloadtranscriptions', methods=['GET', 'POST'])
def downloadtranscriptions():
    print('Fetching transcription')
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
        format_details = json.loads(
            request.args.get('data'))    # data through ajax
        print('format_details', format_details, type(format_details))
        data_format = format_details['format']
        download_audio = format_details['includeAudio']
        latest = format_details['latest']

        try:
            empty_string = request.form.get("empty_string")
            if empty_string == None:
                empty_string = '#'
        except:
            empty_string = '#'

        try:
            merge_same_intervals = request.form.get("merge_intervals")

            if merge_same_intervals == 'no':
                merge_same_intervals = False
            else:
                merge_same_intervals = True

        except:
            merge_same_intervals = True

        print('data_format', data_format)
        if download_audio:
            pass
        else:
            print('data_format', data_format)
            response_code, file_path = downloadTextGrid.downloadTextGridWihoutAudio(transcriptions,
                                                                                    projectsform,
                                                                                    current_username,
                                                                                    activeprojectname,
                                                                                    latest,
                                                                                    data_format,
                                                                                    empty_string,
                                                                                    merge_same_intervals)
        # return response_file
        if response_code == '200':
            print('Response Code', response_code, 'File path', file_path)
            return send_file(file_path, as_attachment=True)
        else:
            print('Response Code', response_code, 'File path', file_path)
            flash('No transcriptions are available to download.')
            return redirect(url_for('enternewsentences'))

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
