"""Module containing the routes for the downloader part of the LiFe."""

from flask import flash, redirect, render_template, url_for, request, json, jsonify, send_file
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash
from app import app, mongo

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
    unannotatedfilename,
    updateuserprojects,
    userdetails,
    speakerdetails
)

from app.lifedownloader.controller import (
    downloadTextGrid
)


from flask import Blueprint, render_template

ld = Blueprint('lifedownloader', __name__, template_folder='templates', static_folder='static')


@ld.route('/downloadtranscriptions', methods=['GET', 'POST'])
def downloadtranscriptions():
    print ('Fetching transcription')
    userprojects, projectsform, transcriptions = getdbcollections.getdbcollections(
        mongo, 'userprojects', 'projectsform', 'transcriptions')
    current_username = getcurrentusername.getcurrentusername()
    print('USERNAME: ', current_username)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(
        userprojects, current_username, activeprojectname)

    if shareinfo['sharemode'] >= 1:
        print (request.args)
        format_details = json.loads(request.args.get('data'))    # data through ajax
        print ('format_details', format_details, type(format_details))
        data_format = format_details['format']
        download_audio = format_details['includeAudio']
        latest = format_details['latest']

        print ('data_format', data_format)
        if download_audio:
            pass
        else:                
            print ('data_format', data_format)
            response_code, file_path = downloadTextGrid.downloadTextGridWihoutAudio (transcriptions,
                                                            projectsform,
                                                            current_username,
                                                            activeprojectname,
                                                            latest,
                                                            data_format)
        # return response_file
        return send_file(file_path, as_attachment=True)
    
    return send_file(file_path, as_attachment=True)


@ld.route('/tgdownloader', methods=['GET', 'POST'])
def downloader():
    userprojects, = getdbcollections.getdbcollections(
        mongo, 'userprojects', )
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    return send_file ('lifedownloader/downloads/'+activeprojectname+'_textgrids.zip', as_attachment=True)