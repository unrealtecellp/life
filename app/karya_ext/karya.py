from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
    request,
    jsonify
)
from app import mongo
import pandas as pd
from werkzeug.datastructures import FileStorage
import requests
import gzip
import tarfile
import io
from io import BytesIO
import json
from datetime import datetime
from pprint import pprint
# from pylatex.utils import bold, NoEscape

from flask_login import current_user, login_user, logout_user, login_required
from app.controller import (
    getdbcollections,
    getactiveprojectname,
    getcurrentuserprojects,
    getprojectowner,
    getcurrentusername,
    audiodetails,
    getuserprojectinfo,
    getprojecttype
)
from app.lifeques.controller import (
    getquesfromprompttext,
    savequespromptfile,
    getquesidlistofsavedaudios
)

from app.karya_ext.controller import (
    access_code_management,
    karya_api_access,
    karya_speaker_management,
    karya_audio_management
)

karya_bp = Blueprint('karya_bp', __name__,
                     template_folder='templates', static_folder='static')

# print('starting...')
'''Home page of karya Extension. This contain  '''


@karya_bp.route('/home_insert')
@login_required
def home_insert():
    # print('starting...home')
    userprojects, accesscodedetails = getdbcollections.getdbcollections(mongo,
                                                                        'userprojects',
                                                                        'accesscodedetails')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                      current_username,
                                                      activeprojectname)

    access_code_list = access_code_management.get_access_code_list(
        accesscodedetails, activeprojectname, current_username)
    karya_speaker_ids = karya_speaker_management.get_all_karya_speaker_ids(
        accesscodedetails, activeprojectname)

    return render_template("home_insert.html",
                           projectName=activeprojectname,
                           shareinfo=shareinfo,
                           fetchaccesscodelist=access_code_list,
                           karya_speaker_ids=karya_speaker_ids,
                           )


#############################################################################################################
##############################################################################################################
######################################   Upload Access-Code       ############################################
##############################################################################################################
##############################################################################################################
'''Upload Access Code'''


@karya_bp.route('/uploadfile', methods=['GET', 'POST'])
@login_required
def uploadfile():
    projects, userprojects, projectsform, karyaaccesscodedetails = getdbcollections.getdbcollections(mongo,
                                                                                                     'projects',
                                                                                                     'userprojects',
                                                                                                     'projectsform',
                                                                                                     'accesscodedetails')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                            userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    project_type = getprojecttype.getprojecttype(projects, activeprojectname)
    derived_from_project_type, derived_from_project_name = getprojecttype.getderivedfromprojectdetails(
        projects, activeprojectname)

    # This metadata for pre-filling the form with metadata relevant only for
    # the current project
    formacesscodemetadata = access_code_management.get_access_code_metadata_for_form(
        projects,
        projectsform,
        activeprojectname,
        project_type,
        derived_from_project_type,
        derived_from_project_name
    )

    if request.method == "POST":
        access_code_file = request.files['accesscodefile']
        task = request.form.get('task')
        language = request.form.get('langscript')
        domain = request.form.getlist('domain')
        phase = request.form.get('phase')  # =>numbers - 0,1,2,3, etc
        elicitationmethod = request.form.getlist("elicitation")
        fetch_data = request.form.get('fetchdata')

        if fetch_data == 'on':
            fetch_data = 1
        else:
            fetch_data = 0

        uploaded_data = access_code_management.get_upload_df(access_code_file)
        upload_response = access_code_management.upload_access_code_metadata_from_file(
            karyaaccesscodedetails,
            activeprojectname,
            current_username,
            task,
            language,
            domain,
            phase,
            elicitationmethod,
            fetch_data,
            uploaded_data
        )

        return redirect(url_for('karya_bp.home_insert'))

    return render_template("uploadfile.html",
                           data=currentuserprojectsname,
                           projectName=activeprojectname,
                           uploadacesscodemetadata=formacesscodemetadata,
                           projecttype=project_type)


##############################################################################################################
##############################################################################################################
######################################       Add User         ###############################################
##############################################################################################################
##############################################################################################################
'''Add User'''


@karya_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    # print ('Adding speaker info into server')
    accesscodedetails, userprojects = getdbcollections.getdbcollections(mongo,
                                                                        "accesscodedetails",
                                                                        'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)

    if request.method == 'POST':
        accesscode = request.form.get('accode')
        fname = request.form.get('sname')
        fage = request.form.get('sagegroup')
        fgender = request.form.get('sgender')
        educlvl = request.form.get('educationalevel')
        moe12 = request.form.getlist('moe12')
        moea12 = request.form.getlist('moea12')
        sols = request.form.getlist('sols')
        por = request.form.get('por')
        toc = request.form.get('toc')

        # Runs if a new access code is to be assigned
        if accesscode == '':
            accesscodefor = int(request.form.get('accesscodefor'))
            task = request.form.get('task')
            language = request.form.get('langscript')
            domain = request.form.getlist('domain')
            elicitationmethod = request.form.getlist("elicitation")

            karyaspeakerid, accesscode = access_code_management.get_new_accesscode_speakerid(
                accesscodedetails = accesscodedetails,
                activeprojectname = activeprojectname,
                accesscodefor = accesscodefor,
                task = task,
                domain = domain,
                elicitationmethod = elicitationmethod,
                language =language)

            if accesscode == '' and karyaspeakerid == '':
                flash("Please Upload New Access Code")
                return redirect(url_for('karya_bp.home_insert'))

            if fage is not None and fname is not None:
                access_code_management.add_access_code_metadata(
                    accesscodedetails,
                    activeprojectname,
                    current_username,
                    karyaspeakerid,
                    accesscode,
                    fname,
                    fage,
                    fgender,
                    educlvl,
                    moe12,
                    moea12,
                    sols,
                    por,
                    toc
                )
        # Runs if a metadata of already assigned access code is to be updated
        else:
            access_code_management.update_access_code_metadata(
                accesscodedetails,
                activeprojectname,
                current_username,
                accesscode,
                fgender,
                educlvl,
                moe12,
                moea12,
                sols,
                por,
                toc
            )

    return redirect(url_for('karya_bp.homespeaker'))
    # return render_template("homespeaker.html",
    # projectName=activeprojectname,
    # uploadacesscodemetadata=uploadacesscodemetadata)


##############################################################################################################
##############################################################################################################
######################################      View Table HomeSpeaker         ###################################
##############################################################################################################
##############################################################################################################

'''Table of speaker details'''


@karya_bp.route('/homespeaker')
@login_required
def homespeaker():
    projects, userprojects, projectsform, accesscode_info = getdbcollections.getdbcollections(mongo,
                                                                                              'projects',
                                                                                              'userprojects',
                                                                                              'projectsform',
                                                                                              'accesscodedetails')

    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(
        current_username, userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)

    project_type = getprojecttype.getprojecttype(projects, activeprojectname)

    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                      current_username,
                                                      activeprojectname)
    share_level = shareinfo['sharemode']

    derived_from_project_type, derived_from_project_name = getprojecttype.getderivedfromprojectdetails(
        projects, activeprojectname)
    formacesscodemetadata = access_code_management.get_access_code_metadata_for_form(
        projects,
        projectsform,
        activeprojectname,
        project_type,
        derived_from_project_type,
        derived_from_project_name
    )

    # This defines the minimum share level of the user who will get info
    # of all access codes (incl those assigned by the other users)
    # Users with share level lower than this will get info of only those
    # access codes which have been assigned by that specific user
    all_data_share_level = 10
    all_acode_metadata = access_code_management.get_access_code_metadata(
        accesscode_info,
        activeprojectname,
        share_level,
        all_data_share_level, 
        current_username
    )

    return render_template('homespeaker.html',
                           data=currentuserprojectsname,
                           projectName=activeprojectname,
                           uploadacesscodemetadata=formacesscodemetadata,
                           projecttype=project_type,
                           data_table=all_acode_metadata,
                           count=len(all_acode_metadata)
                           )


##############################################################################################################
##############################################################################################################
######################################     Get Speaker Details        ########################################
##############################################################################################################
##############################################################################################################
'''Getting user details. '''


@karya_bp.route('/getsharelevel', methods=['GET', 'POST'])
@login_required
def getsharelevel():
    userprojects,  = getdbcollections.getdbcollections(mongo,
                                                       'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                      current_username,
                                                      activeprojectname)

    return jsonify(shareinfo=shareinfo)


'''Getting one speaker details form data base.'''


@karya_bp.route('/getonespeakerdetails', methods=['GET', 'POST'])
def getonespeakerdetails():
    accesscodedetails, userprojects = getdbcollections.getdbcollections(
        mongo, "accesscodedetails", "userprojects")

    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)

    # data through ajax
    asycaccesscode = request.args.get('asycaccesscode')

    speakerdetails = karya_speaker_management.get_one_speaker_details(
        accesscodedetails,
        activeprojectname,
        asycaccesscode
    )

    return jsonify(speakerdetails=speakerdetails)


##############################################################################################################
##############################################################################################################
######################################   Fetch Audio        ###############################################
##############################################################################################################
##############################################################################################################
'''Getting OTP from karya server to fetch the audio files and audio files.'''


@karya_bp.route('/fetch_karya_otp', methods=['GET', 'POST'])
@login_required
def fetch_karya_otp():

    userprojects, accesscodedetails = getdbcollections.getdbcollections(mongo,
                                                                        'userprojects',
                                                                        'accesscodedetails')

    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)

    access_code = request.args.get("acode")
    phone_number = request.args.get("mob")

    karya_api_access.send_karya_otp(
        activeprojectname,
        accesscodedetails,
        access_code,
        phone_number
    )

    return jsonify(result="False")


# update audio metadata in transcription
# def update_audio_metadata_transcription(speakerid, activeprojectname, karya_audio_report):
# def update_audio_metadata_transcription(activeprojectname, karya_audio_report):
#     mongodb_info = mongo.db.transcription

#     updated_audio_metadata = {"additionalInfo":"", "audioMetadata":{"karyaVerificationMetadata": karya_audio_report, "verificationReport": karya_audio_report}}

#     audio_metadata_transcription = mongodb_info.update({'projectname': activeprojectname, 'speakerId': accesscode_speakerid},
#                                                             {"$set": {updated_audio_metadata}})
#     return audio_metadata_transcription
'''Fetching audio files from karya files. '''


@karya_bp.route('/fetch_karya_audio', methods=['GET', 'POST'])
@login_required
def fetch_karya_audio():
    projects, userprojects, projectsform, transcriptions, questionnaires, accesscodedetails = getdbcollections.getdbcollections(mongo,
                                                                                                                                'projects',
                                                                                                                                'userprojects',
                                                                                                                                'projectsform',
                                                                                                                                'transcriptions',
                                                                                                                                'questionnaires',
                                                                                                                                'accesscodedetails')
    current_username = getcurrentusername.getcurrentusername()
    # print('curent user : ', current_username)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    project_type = getprojecttype.getprojecttype(projects, activeprojectname)
    print("karya.py line 418 - ", project_type)
    print("karya.py line 419 - ", activeprojectname)
    derivedFromProjectName = ''
    derive_from_project_type = ''
    if (project_type == 'transcriptions'):
        
        derive_from_project_type, derivedFromProjectName = getprojecttype.getderivedfromprojectdetails(
            projects, activeprojectname)
        print("karya.py line 425 - ", derive_from_project_type, derivedFromProjectName)

    if request.method == 'POST':
        access_code = request.form.get("access_code")
        for_worker_id = request.form.get("speaker_id")
        phone_number = request.form.get("mobile_number")
        otp = request.form.get("karya_otp")

        ###############################   verify OTP    ##########################################
        otp_verified, verification_details = karya_api_access.verify_karya_otp(
            access_code, phone_number, otp
        )
        if not otp_verified:
            flash("Please Provide Correct OTP/Mobile Number")
            return redirect(url_for('karya_bp.home_insert'))
        #############################################################################################

        ###############################   Get Assignments    ########################################
        r_j, hederr = karya_api_access.get_all_karya_assignments(
            verification_details)
        #############################################################################################
        language = accesscodedetails.find_one({"projectname": activeprojectname, "karyaaccesscode": access_code},
                                              {'language': 1, '_id': 0})['language']

        ################################ Get already fetched audio list and quesIDs   ########################################
        fetched_audio_list = karya_audio_management.get_fetched_audio_list(
            accesscodedetails, access_code, activeprojectname)

        exclude_ids = []
        if (project_type == 'questionnaires'):
            exclude_ids = getquesidlistofsavedaudios.getquesidlistofsavedaudios(questionnaires,
                                                                                activeprojectname,
                                                                                language,
                                                                                exclude_ids)
        elif (project_type == 'transcriptions' and
                derive_from_project_type == 'questionnaires'):
            exclude_ids = audiodetails.getaudioidlistofsavedaudios(transcriptions,
                                                                   activeprojectname,
                                                                   language,
                                                                   exclude_ids,
                                                                   for_worker_id)
        #############################################################################################

        ##############################  File ID and sentence mapping   #################################
        '''worker ID'''
        micro_task_ids, workerId_list, sentence_list, karya_audio_report, filename_list, fileID_list = karya_api_access.get_assignment_metadata(
            accesscodedetails, activeprojectname,
            access_code,
            r_j, for_worker_id
        )

        fileid_sentence_map = karya_api_access.get_fileid_sentence_mapping(
            fileID_list, workerId_list, sentence_list, karya_audio_report
        )
        #############################################################################################

        
        karya_audio_management.getnsave_karya_recordings(
            mongo,
            projects, userprojects, projectowner, accesscodedetails,
            projectsform, questionnaires, transcriptions,
            activeprojectname, derivedFromProjectName, current_username,
            project_type, derive_from_project_type,
            fileid_sentence_map, fetched_audio_list, exclude_ids,
            language, hederr, access_code
        )
        return redirect(url_for('karya_bp.home_insert'))

    return render_template("fetch_karya_audio.html")


#################################################################################################
    ########################################## Zip File #############################################
    #################################################################################################
'''Upload zip files of audio.'''


@karya_bp.route('/fetch_karya_audio_zip', methods=['GET', 'POST'])
@login_required
def fetch_karya_audio_zip():
    projects, userprojects, transcriptions = getdbcollections.getdbcollections(
        mongo, 'projects', 'userprojects', 'transcriptions')
    current_username = getcurrentusername.getcurrentusername()
    # print('curent user', current_username)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)

    if request.method == "POST":
        # listWorkerId = []
        # listrecording = []
        audioZipUpload = request.files['accesscodefile']
        # print(type(audioZipUpload))
        # for audioZipUpload in audioZipUpload:
        fileAudio = tarfile.open(fileobj=audioZipUpload, mode='r')
        # print(type(fileAudio))
        # print('1', type(fileAudio))
        # print('2', fileAudio.getnames()) #3
        # print('3', fileAudio.getmembers()) #4
        for filename in fileAudio.getnames():
            if (filename.endswith('.json')):
                # print(filename)
                member = fileAudio.getmember(filename)
                f = fileAudio.extractfile(member)
                content = f.read()
                # print('4', type(member))
                # print('5', type(content))
                jsondata = json.load(io.BytesIO(content))
                # print(jsondata)
                speakerId = jsondata['worker_id']
                wavfilename = jsondata['recording']
                wavmember = fileAudio.getmember(wavfilename)
                wavf = fileAudio.extractfile(wavmember)
                wavcontent = wavf.read()
                # print('4', type(wavmember))
                # print('5', type(wavcontent))
                wavdata = io.BytesIO(wavcontent)

                new_audio_file = {}
                new_audio_file['audiofile'] = FileStorage(
                    wavdata, filename=wavfilename)
                # print('9', new_audio_file['audiofile'], type(new_audio_file['audiofile']))

                audiodetails.saveaudiofiles(mongo,
                                            projects,
                                            userprojects,
                                            transcriptions,
                                            projectowner,
                                            activeprojectname,
                                            current_username,
                                            speakerId,
                                            new_audio_file,
                                            karyainfo=jsondata,
                                            karya_peaker_id=speakerId)

        # return redirect(url_for('karya_bp.home_insert'))
        return redirect(url_for('karya_bp.home_insert'))
    return render_template("karya_bp.fetch_karya_audio_zip")
