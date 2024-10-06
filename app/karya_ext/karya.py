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
from bson import ObjectId
from werkzeug.datastructures import FileStorage
import requests
import gzip
import tarfile
import io
from io import BytesIO
import json
from datetime import datetime
from pprint import pprint, pformat
import gridfs
import base64
import csv
from io import StringIO
from flask import request, jsonify
# from pylatex.utils import bold, NoEscape
from app.controller import (manageAppConfig, questionnairedetails,
                            readJSONFile, removeallaccess, savenewlexeme,
                            savenewproject, savenewprojectform,
                            savenewsentence, unannotatedfilename, updateuserprojects,
                            userdetails, life_logging, processHTMLForm)

from flask_login import current_user, login_user, logout_user, login_required
from app.controller import (
    getdbcollections,
    getactiveprojectname,
    getcurrentuserprojects,
    getprojectowner,
    getcurrentusername,
    audiodetails,
    speakerDetails,
    getuserprojectinfo,
    getprojecttype,
    life_logging
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
logger = life_logging.get_logger()
# print('starting...')
'''Home page of karya Extension. This contain  '''


# @karya_bp.route('/home_insert')
# @login_required
# def home_insert():
#     # print('starting...home')
#     projects, userprojects, accesscodedetails = getdbcollections.getdbcollections(mongo,
#                                                                                   'projects',
#                                                                         'userprojects',
#                                                                         'accesscodedetails')
#     current_username = getcurrentusername.getcurrentusername()
#     activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
#                                                                   userprojects)
#     shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
#                                                       current_username,
#                                                       activeprojectname)

#     access_code_list = access_code_management.get_access_code_list(
#         accesscodedetails, activeprojectname, current_username)

#     transcription_access_code_list = access_code_management.get_transcription_access_code_list(
#         accesscodedetails, activeprojectname, current_username)

#     verification_access_code_list = access_code_management.get_verification_access_code_list(
#         accesscodedetails, activeprojectname, current_username)

#     print(verification_access_code_list)


#     karya_speaker_ids = karya_speaker_management.get_all_karya_speaker_ids(
#         accesscodedetails, activeprojectname)
#     activeprojectname = getactiveprojectname.getactiveprojectname(
#     current_username, userprojects)
#     projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
#     projectType = getprojecttype.getprojecttype(projects, activeprojectname)
#     print("projectType : ", projectType)

#     if projectType == "transcriptions":
#         dropdown_dict = {"newTranscription":"New Transcription", "completedVerification":"Completed Verification"}
#     elif projectType == "validation":
#         dropdown_dict = {"completedVerification":"Completed Verification","newVerification":"New Verification"}
#     else:
#         dropdown_dict = {"completedRecordings":"Completed Recordings"}

#     dropdown_list = [{"value": key, "name": value} for key, value in dropdown_dict.items()]


#     return render_template("home_insert.html",
#                            projectName=activeprojectname,
#                            shareinfo=shareinfo,
#                            fetchaccesscodelist=access_code_list,
#                            transcription_access_code_list =transcription_access_code_list,
#                            verification_access_code_list=verification_access_code_list,
#                            karya_speaker_ids=karya_speaker_ids,
#                            dropdown_list=dropdown_list)





@karya_bp.route('/home_insert')
@login_required
def home_insert():
    # print('starting...home')
    projects, userprojects, accesscodedetails = getdbcollections.getdbcollections(mongo,
                                                                                  'projects',
                                                                                  'userprojects',
                                                                                  'accesscodedetails')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                      current_username,
                                                      activeprojectname)

    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    projectType = getprojecttype.getprojecttype(projects, activeprojectname)
    print("projectType : ", projectType)
    # Find documents without "acodedeleteFlag" field
    query = {"acodedeleteFlag": {"$exists": False}}
    documents = accesscodedetails.find(query)

    # Update documents with "acodedeleteFlag: 0"
    for document in documents:
        document["acodedeleteFlag"] = 0
        accesscodedetails.update_one(
            {"_id": document["_id"], "projectname": activeprojectname}, {"$set": document})

    # finding acccesscode list on the basis of accesscodedetails "Task"
    access_code_list = access_code_management.get_access_code_list(
        accesscodedetails, activeprojectname, current_username)

    transcription_access_code_list = access_code_management.get_transcription_access_code_list(
        accesscodedetails, activeprojectname, current_username)

    verification_access_code_list = access_code_management.get_verification_access_code_list(
        accesscodedetails, activeprojectname, current_username)

    recording_access_code_list = access_code_management.get_recording_access_code_list(
        accesscodedetails, activeprojectname, current_username)

    # Add condition to check if the lists are empty
    # if not verification_access_code_list:
    #     verification_access_code_list = [""]
    # if not transcription_access_code_list:
    #     transcription_access_code_list = [""]

    # print(verification_access_code_list)

    # if projectType == "validation":
    karya_speaker_ids = karya_speaker_management.get_recording_karya_speaker_ids(
        accesscodedetails, activeprojectname, include_fetch=True)
    # else:
    #     karya_speaker_ids = karya_speaker_management.get_recording_karya_speaker_ids(
    # accesscodedetails, activeprojectname, include_fetch=True)

    if projectType == "transcriptions":
        dropdown_dict = {
            "newTranscription": "New Transcription",
            "completedVerification": "Completed Verification",
            "newVerification": "New Verification"
        }
    elif projectType == "validation":
        dropdown_dict = {
            "completedVerification": "Completed Verification",
            "newVerification": "New Verification"
        }
    elif projectType == "recordings":
        dropdown_dict = {
            "completedRecordings": "Completed Recordings",
            "newTranscription": "New Transcription",
            "completedVerification": "Completed Verification",
            "newVerification": "New Verification"
        }
    elif projectType == "questionnaires":
                dropdown_dict = {
            "newVerification": "New Verification"
                }

    else:
        dropdown_dict = {
            "newVerification": "New Verification",
            "completedRecordings": "Completed Recordings"
        }

    dropdown_list = [{"value": key, "name": value}
                     for key, value in dropdown_dict.items()]

    return render_template("home_insert.html",
                           projectName=activeprojectname,
                           shareinfo=shareinfo,
                           fetchaccesscodelist=access_code_list,
                           transcription_access_code_list=transcription_access_code_list,
                           verification_access_code_list=verification_access_code_list,
                           recording_access_code_list=recording_access_code_list,
                           karya_speaker_ids=karya_speaker_ids,
                           dropdown_list=dropdown_list)







# Karya Setup
@karya_bp.route('/karya_setupall', methods=['GET', 'POST'])
@login_required
def karya_setupall():
    userprojects, userlogin = getdbcollections.getdbcollections(
        mongo, 'userprojects', 'userlogin')
    current_username = getcurrentusername.getcurrentusername()
    usertype = userdetails.get_user_type(userlogin, current_username)
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_username, userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects, current_username, activeprojectname)
    print(activeprojectname)
    return render_template(
        'karya_setupall.html',
        data=currentuserprojectsname,
        activeprojectname=activeprojectname,
        shareinfo=shareinfo,
        usertype=usertype
    )




##############################################################################################################
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
    derived_from_project_type, derived_from_project_name = getprojecttype.getderivedfromprojectdetails(projects,
                                                                                                       activeprojectname)

    logger.debug("derived_from_project_type: %s\nderived_from_project_name: %s",
                 derived_from_project_type, derived_from_project_name)
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

    activeacode = karyaaccesscodedetails.find(
        {"projectname": activeprojectname, "isActive": 1})
    deactiveacode = karyaaccesscodedetails.find(
        {"projectname": activeprojectname, "isActive": 0})

    active_data_table = []
    deactive_data_table = []

    for item in activeacode:
        item_dict = {
            "id": str(item["_id"]),  # Convert ObjectId to string
            "karyaaccesscode": item["karyaaccesscode"],
            "karyaspeakerid": item["karyaspeakerid"],
            "isActive": item["isActive"],
            "fetchData": item["fetchData"]
            # Include other required fields from the item
        }
        active_data_table.append(item_dict)

    for item in deactiveacode:
        item_dict = {
            "id": str(item["_id"]),  # Convert ObjectId to string
            "karyaaccesscode": item["karyaaccesscode"],
            "karyaspeakerid": item["karyaspeakerid"],
            "isActive": item["isActive"],
            "fetchData": item["fetchData"]
            # Include other required fields from the item
        }
        deactive_data_table.append(item_dict)

    # Convert the ObjectId to string for serialization
    # active_data_table = [json.loads(json.dumps(item, default=str)) for item in activeacode]
    # deactive_data_table = [json.loads(json.dumps(item, default=str)) for item in deactiveacode]

    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                      current_username,
                                                      activeprojectname)

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
                           active_data_table=active_data_table,
                           deactive_data_table=deactive_data_table,
                           projectName=activeprojectname,
                           uploadacesscodemetadata=formacesscodemetadata,
                           projecttype=project_type,
                           shareinfo=shareinfo)


'''Getting active accesscode details form data base.'''
@karya_bp.route('/active_accesscodes', methods=['POST'])
@login_required
def active_accesscodes():
    activeacode = []
    accesscodedetails, userprojects = getdbcollections.getdbcollections(
        mongo, "accesscodedetails", "userprojects")
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    # Data through AJAX
    asycaccesscode = request.form.get('code')

    acodedetails = accesscodedetails.find_one({"isActive": 1, "projectname": activeprojectname, "karyaaccesscode": str(asycaccesscode)},
                                              {"karyaaccesscode": 1, "karyaspeakerid": 1, "isActive": 1, "fetchData": 1,
                                               "task": 1, "domain": 1, "elicitationmethod": 1, "phase": 1, "language": 1, "projectname": 1, "current.workerMetadata.name": 1,
                                               "current.workerMetadata.agegroup": 1, "current.workerMetadata.gender": 1, "current.workerMetadata.educationlevel": 1,
                                               "current.workerMetadata.educationmediumupto12": 1, "current.workerMetadata.educationmediumafter12": 1,
                                               "current.workerMetadata.speakerlanguage": 1, "current.workerMetadata.recordingplace": 1,
                                               "current.workerMetadata.typeofrecordingplace": 1, "current.workerMetadata.activeAccessCode": 1,
                                               "_id": 0})
    # acodedetails = accesscodedetails.find({"isActive": 1, "projectname": activeprojectname, "karyaaccesscode": str(asycaccesscode)})
    # print("Access Code:", asycaccesscode)
    # print(acodedetails)

    # details_list = []  # Create an empty list

    # for item in acodedetails:  # Iterate over the values of the acodedetails dictionary
    #     data = {"karyaaccesscode": item["karyaaccesscode"],"karyaspeakerid": item["karyaspeakerid"],"isActive": item["isActive"],"fetchData": item["fetchData"]}
    #     print(data)
    #     details_list.append(data)
    # print(details_list)
    print(jsonify(acodedetails))

    return jsonify(response=acodedetails)


'''Getting Inactive accesscode details form data base.'''
@karya_bp.route('/deactive_accesscodes', methods=['POST'])
@login_required
def deactive_accesscodes():
    deactiveacode = []
    accesscodedetails, userprojects = getdbcollections.getdbcollections(
        mongo, "accesscodedetails", "userprojects")
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    # Data through AJAX
    asycaccesscode = request.form.get('code')

    acodedetails = accesscodedetails.find_one({"isActive": 0, "projectname": activeprojectname, "karyaaccesscode": str(asycaccesscode)},
                                              {"karyaaccesscode": 1, "karyaspeakerid": 1, "isActive": 1, "fetchData": 1,
                                               "task": 1, "domain": 1, "elicitationmethod": 1, "phase": 1, "language": 1, "projectname": 1, "current.workerMetadata.name": 1,
                                               "current.workerMetadata.agegroup": 1, "current.workerMetadata.gender": 1, "current.workerMetadata.educationlevel": 1,
                                               "current.workerMetadata.educationmediumupto12": 1, "current.workerMetadata.educationmediumafter12": 1,
                                               "current.workerMetadata.speakerlanguage": 1, "current.workerMetadata.recordingplace": 1,
                                               "current.workerMetadata.typeofrecordingplace": 1, "current.workerMetadata.activeAccessCode": 1,
                                               "_id": 0})
    # acodedetails = accesscodedetails.find({"isActive": 1, "projectname": activeprojectname, "karyaaccesscode": str(asycaccesscode)})
    # print("Access Code:", asycaccesscode)
    # print(acodedetails)

    print(jsonify(acodedetails))

    return jsonify(response=acodedetails)


'''updating inactive accesscode'''


@karya_bp.route('/deactive_update_table_data', methods=['POST'])
def deactive_update_table_data():
    accesscodedetails, userprojects = getdbcollections.getdbcollections(
        mongo, "accesscodedetails", "userprojects")
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)

    # Get the data from the request
    # name = request.form.get('name')
    # age = request.form.get('age')
    # gender = request.form.get('gender')
    accessCode = request.form.get('accessCode')
    speakerID = request.form.get('speakerID')
    # status = request.form.get('status')
    fetchData = request.form.get('fetchData')
    elicitation = request.form.get('elicitationmethod')
    domain = request.form.get('domain')
    phase = request.form.get('phase')
    languagescript = request.form.get('languagescript')
    task = request.form.get('task')
    # educationlevel = request.form.get('educationalevel')
    # educationmediumupto12 = request.form.get('educationmediumupto12')
    # educationmediumafter12 = request.form.get('educationmediumafter12')
    # place = request.form.get('place')
    # typeofplace = request.form.get('typeofplace')

    # Print the received data
    # print("Access Code:", accessCode)
    # print("Speaker ID:", speakerID)
    # print("elicitation :", elicitation)
    # print("domain :", domain)
    # print("phase :", phase)
    # print("languagescript :", languagescript)

    current_speakerdetails = accesscodedetails.find_one({"karyaaccesscode": accessCode, "projectname": activeprojectname, "isActive": 0},
                                                        {"current.workerMetadata.name": 1, "current.workerMetadata.agegroup": 1, "_id": 1 })

    current_speakerdetails_name = current_speakerdetails['current']['workerMetadata']['name']
    current_speakerdetails_age = current_speakerdetails['current']['workerMetadata']['agegroup']
    current_speakerdetails_id = current_speakerdetails["_id"]
    print("current_speakerdetails_name: ", current_speakerdetails_name)
    print("current_speakerdetails_age: ", current_speakerdetails_age)

    

    # update_data = {"current.updatedBy":  current_username,
    #                "karyaaccesscode": accessCode,
    #                "karyaspeakerid": speakerID,
    #                "fetchData": int(fetchData),
    #                "elicitationmethod": [elicitation],
    #                "phase": phase,
    #                "domain": [domain],
    #                "language": languagescript,
    #                "task": task
    #                }





    # Split the elicitation and domain strings into lists
    elicitation_list = elicitation.split(',')
    domain_list = domain.split(',')
    languagescript_list = languagescript.split(',')
    update_data = {
        "current.updatedBy": current_username,
        "karyaaccesscode": accessCode,
        "karyaspeakerid": speakerID,
        "fetchData": int(fetchData),
        "elicitationmethod": elicitation_list,
        "phase": phase,
        "domain": domain_list,
        "language": languagescript_list,
        "task": task
    }


    date_of_modified = str(datetime.now()).replace(".", ":")

    # new_user_info
    # accesscodedetails.update_one({"karyaaccesscode": accessCode, "projectname": activeprojectname, "isActive": 0}, {
    #                              "$set": update_data}) 

    accesscodedetails.update_one({"karyaaccesscode": accessCode, "projectname": activeprojectname, "isActive": 0}, {
                                "$set": update_data}) 


    print("if condtion working inactive access code")

    # Return a response indicating the success or failure of the update operation
    return jsonify({'status': 'success', 'message': 'Deactivated Table data updated successfully'})


'''updating active accesscode'''
@karya_bp.route('/update_table_data', methods=['POST'])
def update_table_data():
    accesscodedetails, userprojects = getdbcollections.getdbcollections(
        mongo, "accesscodedetails", "userprojects")
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)

    # Get the data from the request
    # name = request.form.get('name')
    # age = request.form.get('age')
    # gender = request.form.get('gender')
    accessCode = request.form.get('accessCode')
    # speakerID = request.form.get('speakerID')
    # status = request.form.get('status')
    fetchData = request.form.get('fetchData')
    # educationlevel = request.form.get('educationalevel')
    # educationmediumupto12 = request.form.get('educationmediumupto12')
    # educationmediumafter12 = request.form.get('educationmediumafter12')
    # place = request.form.get('place')
    # typeofplace = request.form.get('typeofplace')

    # Print the received data
    # print("Name:", name)
    # print("Age:", age)
    # print("Gender:", gender)
    # print("Access Code:", accessCode)
    # print("Speaker ID:", speakerID)
    # print("Status:", status)
    # print("Fetch Data:", fetchData)
    # print("Education Level:", educationlevel)
    # print("Education Medium Upto 12:", educationmediumupto12)
    # print("Education Medium After 12:", educationmediumafter12)
    # print("Place:", place)
    # print("Type of Place:", typeofplace)

    current_speakerdetails = accesscodedetails.find_one({"karyaaccesscode": accessCode, "projectname": activeprojectname, "isActive": 1},
                                                        {"current.workerMetadata.name": 1, "current.workerMetadata.agegroup": 1, "_id": 0, })

    current_speakerdetails_name = current_speakerdetails['current']['workerMetadata']['name']
    current_speakerdetails_age = current_speakerdetails['current']['workerMetadata']['agegroup']
    print("current_speakerdetails_name: ", current_speakerdetails_name)
    print("current_speakerdetails_age: ", current_speakerdetails_age)
    if current_speakerdetails_age != '' and current_speakerdetails_name != '':
        # update_data = {"current.updatedBy" :  current_username,
        #                                 "karyaaccesscode":accessCode,
        #                                 "karyaspeakerid": speakerID,
        #                                 "current.workerMetadata.name": name,
        #                                 "current.workerMetadata.agegroup": age,
        #                                 "current.workerMetadata.gender": gender,
        #                                 "current.workerMetadata.educationlevel": educationlevel,
        #                                 "current.workerMetadata.educationmediumupto12": educationmediumupto12,
        #                                 "current.workerMetadata.educationmediumafter12": educationmediumafter12,
        #                                 "current.workerMetadata.recordingplace": place,
        #                                 "current.workerMetadata.typeofrecordingplace": typeofplace,
        #                                 "isActive": int(status),
        #                                 "fetchData": int(fetchData)}

        update_data = {"current.updatedBy": current_username,
                       "karyaaccesscode": accessCode,
                       "fetchData": int(fetchData)}

        previous_speakerdetails = accesscodedetails.find_one({"karyaaccesscode": accessCode, "projectname": activeprojectname, "isActive": 1},
                                                             {"karyaaccesscode": 1, "karyaspeakerid": 1, "current.workerMetadata": 1,
                                                              "current.updatedBy": 1, "_id": 0, })

        date_of_modified = str(datetime.now()).replace(".", ":")

        # update_old_data = {"previous."+date_of_modified+".workerMetadata.karyaaccesscode": previous_speakerdetails["karyaaccesscode"],
        #                     "previous."+date_of_modified+".workerMetadata.karyaspeakerid": previous_speakerdetails["karyaspeakerid"],
        #                     "previous."+date_of_modified+".workerMetadata.name": previous_speakerdetails["current"]["workerMetadata"]["name"],
        #                     "previous."+date_of_modified+".workerMetadata.agegroup": previous_speakerdetails["current"]["workerMetadata"]["agegroup"],
        #                     "previous."+date_of_modified+".workerMetadata.gender": previous_speakerdetails["current"]["workerMetadata"]["gender"],
        #                     "previous."+date_of_modified+".workerMetadata.educationlevel": previous_speakerdetails["current"]["workerMetadata"]["educationlevel"],
        #                     "previous."+date_of_modified+".workerMetadata.educationmediumupto12": previous_speakerdetails["current"]["workerMetadata"]["educationmediumupto12"],
        #                     "previous."+date_of_modified+".workerMetadata.educationmediumafter12": previous_speakerdetails["current"]["workerMetadata"]["educationmediumafter12"],
        #                     "previous."+date_of_modified+".workerMetadata.speakerspeaklanguage": previous_speakerdetails["current"]["workerMetadata"]["speakerspeaklanguage"],
        #                     "previous."+date_of_modified+".workerMetadata.recordingplace": previous_speakerdetails["current"]["workerMetadata"]["recordingplace"],
        #                     "previous."+date_of_modified+".updatedBy" : previous_speakerdetails["current"]["updatedBy"]
        #                     }

        # accesscodedetails.update_one({"karyaaccesscode": accessCode, "projectname": activeprojectname, "isActive":1}, {"$set": update_old_data}) # Edit_old_user_info
        accesscodedetails.update_one({"karyaaccesscode": accessCode, "projectname": activeprojectname, "isActive": 1}, {
                                     "$set": update_data})  # new_user_info
        print("if condtion working")

    else:
        update_query = {"karyaaccesscode": accessCode,
                        "projectname": activeprojectname, "isActive": 1}
        # update_fields = {"$set": {"karyaaccesscode":accessCode, "karyaspeakerid": speakerID,
        #                       "isActive": int(status),"fetchData": int(fetchData),
        #                       "current.workerMetadata.name": name,
        #                       "current.workerMetadata.agegroup": age,
        #                       "current.workerMetadata.gender": gender,
        #                       "current.workerMetadata.educationalevel": educationlevel,
        #                       "current.workerMetadata.educationmediumupto12": educationmediumupto12,
        #                       "current.workerMetadata.educationmediumafter12": educationmediumafter12,
        #                       "current.workerMetadata.recordingplace": place,
        #                       "current.workerMetadata.typeofrecordingplace": typeofplace}}

        # update_fields = {"$set": {"karyaaccesscode":accessCode, "karyaspeakerid": speakerID,
        #                       "isActive": int(status),"fetchData": int(fetchData),
        #                       "current.workerMetadata.name": name,
        #                       "current.workerMetadata.agegroup": age,
        #                       "current.workerMetadata.gender": gender,
        #                       "current.workerMetadata.educationalevel": educationlevel,
        #                       "current.workerMetadata.educationmediumupto12": educationmediumupto12,
        #                       "current.workerMetadata.educationmediumafter12": educationmediumafter12,
        #                       "current.workerMetadata.recordingplace": place,
        #                       "current.workerMetadata.typeofrecordingplace": typeofplace}}
        # update_fields = {"$set": {"karyaaccesscode":accessCode, "fetchData": int(fetchData)}}

        # update_fields = {"$set": {"karyaspeakerid": speakerID,"isActive": int(status),"fetchData": int(fetchData)}}
        # print("else condtion working ")

        update_fields = {"$set": {"fetchData": int(fetchData)}}
        print("else condtion working ")

        result = accesscodedetails.update_one(update_query, update_fields)
        print("result : ", update_query)

    # Return a response indicating the success or failure of the update operation
    return jsonify({'status': 'success', 'message': 'Table data updated successfully'})


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
    accesscodedetails, userprojects, speakerdetails = getdbcollections.getdbcollections(mongo,
                                                                        'accesscodedetails',
                                                                        'userprojects', 
                                                                        'speakerdetails')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    
    accesscodedetails, userprojects, userlogin, speakermeta, projects = getdbcollections.getdbcollections(
	mongo, 'accesscodedetails', 'userprojects', 'userlogin', 'speakerdetails', 'projects')

    
    # current_username = getcurrentusername.getcurrentusername()
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
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)

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
                accesscodedetails=accesscodedetails,
                activeprojectname=activeprojectname,
                accesscodefor=accesscodefor,
                task=task,
                domain=domain,
                elicitationmethod=elicitationmethod,
                language=language)

            if accesscode == '' and karyaspeakerid == '':
                flash("Please Upload New Access Code")
                return redirect(url_for('karya_bp.home_insert'))

            if fage is not None and fname is not None:
                
                # new_metadata = {"current": {"updatedBy": current_username,
                #              "sourceMetadata": {"name": fname,
                #                                 "agegroup": fage,
                #                                 "gender": fgender,
                #                                 "educationlevel": educlvl,
                #                                 "educationmediumupto12": moe12,
                #                                 "educationmediumafter12": moea12,
                #                                 "speakerspeaklanguage": sols,
                #                                 "recordingplace": por,
                #                                 "typeofrecordingplace": toc},
                #                                 "current_date": current_dt}
                #                                 }


                #metadata save to accesscodedetails 
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

                #metadata save to speakerdetails 
                find_accesscodedetails = accesscodedetails.find_one({"karyaaccesscode": accesscode,
                                                        "projectname": activeprojectname},
                                                {"lifespeakerid":1,
                                                "karyaspeakerid": 1,
                                                "current.workerMetadata.name":1, 
                                                "current.workerMetadata.agegroup": 1,
                                                    "_id": 0})
                
                current_dt = str(datetime.now()).replace('.', ':')
                metadata_schema = 'speed'
                audio_source = 'field'
                upload_type = 'single'

                new_metadata = {"name": fname,
                                "agegroup": fage,
                                "gender": fgender,
                                "educationlevel": educlvl,
                                "educationmediumupto12": moe12,
                                "educationmediumafter12": moea12,
                                "speakerspeaklanguage": sols,
                                "recordingplace": por,
                                "typeofrecordingplace": toc,
                                "lifespeakerid": find_accesscodedetails['lifespeakerid'],
                                "karyaaccesscode": accesscode,
                                "karyaspeakerid": find_accesscodedetails["karyaspeakerid"]}
                                                

                speakerDetails.write_speaker_metadata_details(speakerdetails,
                                                      current_username,
                                                      activeprojectname,
                                                      current_username,
                                                      audio_source,
                                                      metadata_schema,
                                                      new_metadata,
                                                      upload_type)
        # Runs if a metadata of already assigned access code is to be updated
        else:
            #metadata save to speakerdetails 
            current_dt = str(datetime.now()).replace('.', ':')
            metadata_schema = 'speed'
            audio_source = 'field'
            upload_type = 'single'

            find_accesscodedetails = accesscodedetails.find_one({"karyaaccesscode": accesscode,
                                                                   "projectname": activeprojectname},
                                                         {"lifespeakerid":1,
                                                          "karyaspeakerid": 1,
                                                          "current.workerMetadata.name":1, 
                                                           "current.workerMetadata.agegroup": 1,
                                                             "_id": 0})
            
            previous_speakerdetails = speakerdetails.find_one({"current.sourceMetadata.lifespeakerid": find_accesscodedetails['lifespeakerid'],
                                                                   "projectname": activeprojectname},
                                                         {"lifesourceid":1, "_id": 0})
            
            print("speraker_id: ", previous_speakerdetails["lifesourceid"])
            
            edit_metadata = {"name": find_accesscodedetails["current"]["workerMetadata"]["name"],
                                "agegroup": find_accesscodedetails["current"]["workerMetadata"]["agegroup"],
                                "gender": fgender,
                                "educationlevel": educlvl,
                                "educationmediumupto12": moe12,
                                "educationmediumafter12": moea12,
                                "speakerspeaklanguage": sols,
                                "recordingplace": por,
                                "typeofrecordingplace": toc, 
                                "lifespeakerid": find_accesscodedetails['lifespeakerid'],
                                "karyaaccesscode": accesscode,
                                "karyaspeakerid": find_accesscodedetails["karyaspeakerid"]}

            # edit_metadata = {"name": find_accesscodedetails["current"]["workerMetadata"]["name"],
            #                     "agegroup": find_accesscodedetails["current"]["workerMetadata"]["agegroup"],
            #                     "gender": fgender,
            #                     "educationlevel": educlvl,
            #                     "educationmediumupto12": moe12,
            #                     "educationmediumafter12": moea12,
            #                     "speakerspeaklanguage": sols,
            #                     "recordingplace": por,
            #                     "typeofrecordingplace": toc}

            edit_update_metadata = {"current": {"updatedBy": current_username,
                                                "sourceMetadata": edit_metadata,
                                                "current_date": current_dt} }
            
            print('edit_metadata ................','\n',edit_update_metadata)
            
            logger.debug("Update Data %s", edit_update_metadata)
            updatestatus = speakerDetails.updateonespeakerdetails(
                activeprojectname, previous_speakerdetails['lifesourceid'], edit_update_metadata, speakerdetails)
            
            #metadata save to accesscodedetails
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


        #sync life speakeid with lifesourceid and more meta data to speakerdetalis    
        find_accesscodedetails = accesscodedetails.find({
        "projectname": activeprojectname, 'isActive':1},
                                            {"lifespeakerid": 1,
                                            "karyaaccesscode": 1,
                                            "karyaspeakerid": 1,
                                            "current.workerMetadata.name": 1,
                                            "current.workerMetadata.agegroup": 1,
                                            "current.workerMetadata.gender": 1,
                                            "current.workerMetadata.educationlevel": 1,
                                            "current.workerMetadata.educationmediumupto12": 1,
                                            "current.workerMetadata.educationmediumafter12": 1,
                                            "current.workerMetadata.speakerspeaklanguage": 1,
                                            "current.workerMetadata.recordingplace": 1,
                                            "current.workerMetadata.typeofrecordingplace": 1,
                                            "current.workerMetadata.activeAccessCode": 1,
                                            "_id": 0})

        total_documents = find_accesscodedetails.count()
        print("Total number of documents found from accesscodedetails:", total_documents)

        metadata_schema = 'speed'
        audio_source = 'field'
        upload_type = 'single'

        for document in find_accesscodedetails:
            try:
                new_metadata = {
                    "name": document["current"]["workerMetadata"].get("name", ""),
                    "agegroup": document["current"]["workerMetadata"].get("agegroup", ""),
                    "gender": document["current"]["workerMetadata"].get("gender", ""),
                    "educationlevel": document["current"]["workerMetadata"].get("educationlevel", ""),
                    "educationmediumupto12": document["current"]["workerMetadata"].get("educationmediumupto12", []),
                    "educationmediumafter12": document["current"]["workerMetadata"].get("educationmediumafter12", []),
                    "speakerspeaklanguage": document["current"]["workerMetadata"].get("speakerspeaklanguage", []),
                    "recordingplace": document["current"]["workerMetadata"].get("recordingplace", ""),
                    "typeofrecordingplace": document["current"]["workerMetadata"].get("typeofrecordingplace", ""),
                    "lifespeakerid": document["lifespeakerid"],
                    "karyaaccesscode": document["karyaaccesscode"],
                    "karyaspeakerid": document["karyaspeakerid"]
                }
                # print('new_metadata : ', new_metadata)

                # Additional conditions to replace None values
                if new_metadata["name"] is None:
                    new_metadata["name"] = ""
                if new_metadata["agegroup"] is None:
                    new_metadata["agegroup"] = ""
                if new_metadata["gender"] is None:
                    new_metadata["gender"] = ""
                if new_metadata["educationlevel"] is None:
                    new_metadata["educationlevel"] = ""
                if new_metadata["recordingplace"] is None:
                    new_metadata["recordingplace"] = ""
                if new_metadata["typeofrecordingplace"] is None:
                    new_metadata["typeofrecordingplace"] = ""
                # For array fields
                if new_metadata["educationmediumupto12"] is None:
                    new_metadata["educationmediumupto12"] = []
                if new_metadata["educationmediumafter12"] is None:
                    new_metadata["educationmediumafter12"] = []
                if new_metadata["speakerspeaklanguage"] is None:
                    new_metadata["speakerspeaklanguage"] = []

            except Exception as e:
                # Handle exception
                print("An error occurred:", e)
                continue  # Skip to the next document

            # Check if the metadata already exists in speakermeta (speakerdetails)
            existing_metadata = speakermeta.find_one({
                                            "projectname": activeprojectname,
                                            "current.sourceMetadata.lifespeakerid": new_metadata["lifespeakerid"],
                                            "current.sourceMetadata.karyaaccesscode":  new_metadata["karyaaccesscode"],
                                            "current.sourceMetadata.karyaspeakerid": new_metadata["karyaspeakerid"]
                                        })
            print('existing_metadata :', existing_metadata)

            if not existing_metadata:
                # Metadata does not exist, so write it to the speakermeta collection
                not_existing_metadata = speakerDetails.write_speaker_metadata_details(
                                                                                    speakermeta,
                                                                                    projectowner,
                                                                                    activeprojectname,
                                                                                    current_username,
                                                                                    audio_source,
                                                                                    metadata_schema,
                                                                                    new_metadata,
                                                                                    upload_type
                                                                                )
                # print('not existing_metadata')

        check_existing_lifesourceid = speakermeta.find({
                                                        "projectname": activeprojectname},
                                                        {"lifesourceid": 1,
                                                        "current.sourceMetadata.lifespeakerid": 1,
                                                        "current.sourceMetadata.karyaaccesscode":  1,
                                                        "current.sourceMetadata.karyaspeakerid": 1,
                                                            "_id": 0
                                                        })



        for existing_lifesourceid in check_existing_lifesourceid:
            if existing_lifesourceid["lifesourceid"] != existing_lifesourceid["current"]["sourceMetadata"]["lifespeakerid"]:
                # Define filter criteria to check if old_lifesourceid is already present
                filter_criteria_old_lifesourceid = {
                    "projectname": activeprojectname,
                    "current.sourceMetadata.lifespeakerid": existing_lifesourceid["current"]["sourceMetadata"]["lifespeakerid"],
                    # Check if old_lifesourceid does not exist
                    "old_lifesourceid": {"$exists": False}
                }
                # print('filter_criteria_old_lifesourceid :', filter_criteria_old_lifesourceid)

                # Define filter criteria to update lifespeakerid to lifesourceid
                filter_criteria_lifespeakerid_to_lifesourceid = {
                    "projectname": activeprojectname,
                    "current.sourceMetadata.lifespeakerid": existing_lifesourceid["current"]["sourceMetadata"]["lifespeakerid"]
                }
                # print('filter_criteria_lifespeakerid_to_lifesourceid :', filter_criteria_lifespeakerid_to_lifesourceid)
                # Define the data to be added
                lifesource_to_old_lifesourceid = {
                    "old_lifesourceid": existing_lifesourceid["lifesourceid"]}
                lifespeakerid_to_lifesourceid = {
                    "lifesourceid": existing_lifesourceid["current"]["sourceMetadata"]["lifespeakerid"]}
                
                # print('lifesource_to_old_lifesourceid :', lifesource_to_old_lifesourceid , 'lifespeakerid_to_lifesourceid :',lifespeakerid_to_lifesourceid  )

                # Update old_lifesourceid only if it does not exist in the document
                try:
                    # Update old_lifesourceid
                    result = speakermeta.update_many(filter_criteria_old_lifesourceid, {
                                                    "$set": lifesource_to_old_lifesourceid})

                    # Update lifespeakerid to lifesourceid
                    result = speakermeta.update_many(filter_criteria_lifespeakerid_to_lifesourceid, {
                                                    "$set": lifespeakerid_to_lifesourceid})

                except Exception as e:
                    print("An error occurred:", e)




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
    print(project_type)

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

    print("############################################################")
    print(projects)
    print(projectsform)
    print(activeprojectname)
    print(project_type)
    print(derived_from_project_name)
    print(derived_from_project_type)
    print('formacesscodemetadata', formacesscodemetadata)

    ###############################################################################################
    # langscript = []
    # # domain, elictationmethod ,langscript-[1]
    # projectform = projectsform.find_one({"projectname": activeprojectname})
    # langscripts = list((projectform["Prompt Type"][1]).keys())
    
    # for lang_script, lang_info in langscripts.items():
    #     if ('Audio' in lang_info):
    #         langscript.append(lang_script)
    # print('ques lang script :',langscript)

    ################################################################################################
 
    # projectform = projectsform.find_one({"projectname": activeprojectname})
    # # langscript.append(projectform["Sentence Language"][0])
    # langscript = projectform["Audio Language"][1]
    # print(langscript)
    # derivedFromProject = projects.find_one({"projectname": activeprojectname},
    #                                        {"_id": 0, "derivedFromProject": 1})
    # derivedFromProjectName = derivedFromProject['derivedFromProject'][0]
    # derived_from_project_type = getprojecttype.getprojecttype(
    #     projects, derivedFromProjectName)

    # if (derived_from_project_type == "questionnaires"):
    #     derivefromprojectform = projectsform.find_one(
    #         {"projectname": derivedFromProjectName})

    #     domain = derivefromprojectform["Domain"][1]
    #     elicitation = derivefromprojectform["Elicitation Method"][1]
    #     # elicitation = derivefromprojectform["Transcription"][1]
       

    # acesscodemetadata = {
    #     "langscript": langscript,
    #     "domain": domain,
    #     "elicitation": elicitation
    # }

    # print(acesscodemetadata)
##########################################################################################

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
    print("URL FOR fetch_karya_otp: ", access_code)
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
    projects, userprojects, projectsform, recordings, transcriptions, questionnaires, accesscodedetails = getdbcollections.getdbcollections(mongo,
                                                                                                                                            'projects',
                                                                                                                                            'userprojects',
                                                                                                                                            'projectsform',
                                                                                                                                            'recordings',
                                                                                                                                            'transcriptions',
                                                                                                                                            'questionnaires',
                                                                                                                                            'accesscodedetails')
    current_username = getcurrentusername.getcurrentusername()
    # print('curent user : ', current_username)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    project_type = getprojecttype.getprojecttype(projects, activeprojectname)
    logger.debug("project_type: %s", project_type)
    logger.debug("activeprojectname: %s", activeprojectname)
    derivedFromProjectName = ''
    derive_from_project_type = ''
    if (project_type == 'transcriptions' or
            project_type == 'recordings'):

        derive_from_project_type, derivedFromProjectName = getprojecttype.getderivedfromprojectdetails(projects,
                                                                                                       activeprojectname)
        logger.debug("derive_from_project_type: %s, derivedFromProjectName: %s",
                     derive_from_project_type, derivedFromProjectName)

    if request.method == 'POST':

        project_type = projects.find_one({"projectname": activeprojectname}, {
                                         "projectType": 1})['projectType']

        access_code_task = request.form.get('additionalDropdown')
        # access_code = None
        access_code = request.form.get('transcriptionDropdown')

        if access_code_task == "newVerification" or access_code_task == "completedVerification":
            access_code = request.form.get('verificationDropdown')
        elif access_code_task == "newTranscription":
            access_code = request.form.get('transcriptionDropdown')
        elif access_code_task == "completedRecordings":
            access_code = request.form.get('recordingDropdown')

        for_worker_id = request.form.get("speaker_id")
        phone_number = request.form.get("mobile_number")
        otp = request.form.get("karya_otp")

        # print("OTP : ", otp)
        # print("project_type: ", project_type)
        # # print("additional_task : ", additional_task)
        # print("access_code_task : ", access_code_task)
        # print("access_code : ", access_code)
        # print("for_worker_id : ", for_worker_id)
        # print("phone_number : ", phone_number)
        ###############################   verify OTP    ##########################################
        otp_verified, verification_details = karya_api_access.verify_karya_otp(
            access_code, phone_number, otp
        )
        if not otp_verified:
            flash("Please Provide Correct OTP/Mobile Number")
            return redirect(url_for('karya_bp.home_insert'))
        #############################################################################################

        if project_type == 'validation' or project_type == 'transcriptions' or project_type == 'recordings' or project_type == "questionnaires":
            if "new" in access_code_task:
                assignment_url = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=new&from=2021-05-11T07:23:40.654Z'
                print("the project type is ", project_type,
                      "and", access_code_task, "and", " New url")
            elif "completed" in access_code_task:
                assignment_url = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=verified&includemt=true&from=2021-05-11T07:23:40.654Z'
                print("the project type is ", project_type, "and",
                      access_code_task, "and", "verified url")

        else:
            flash(
                "This action is not allowed in this project. Please fetch the recording in a new/other project.")
            return redirect(url_for('karya_bp.home_insert'))

        ###############################   Get Assignments    ########################################

        r_j, hederr = karya_api_access.get_all_karya_assignments(
            verification_details, assignment_url)
        # r_j, hederr = karya_api_access.get_all_karya_assignments(
        #     verification_details, additional_task, project_type, access_code_task)


        logger.debug("r_j: %s\nhederr: %s", r_j, hederr)
        #############################################################################################
        language = accesscodedetails.find_one({"projectname": activeprojectname,
                                                "karyaaccesscode": access_code},
                                              {'language': 1, '_id': 0})['language']
        logger.debug("language: %s", language)
        ################################ Get already fetched audio list and quesIDs   ########################################
        fetched_audio_list = karya_audio_management.get_fetched_audio_list(
            accesscodedetails, access_code, activeprojectname)
        # print("898", fetched_audio_list)
        logger.debug("fetched_audio_list: %s", fetched_audio_list)
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
        elif (project_type == 'recordings' and
                derive_from_project_type == 'questionnaires'):
            exclude_ids = audiodetails.getaudioidlistofsavedaudios(recordings,
                                                                   activeprojectname,
                                                                   language,
                                                                   exclude_ids,
                                                                   for_worker_id)
            logger.debug("exclude_ids: %s", exclude_ids)
        
        print("exclude_ids : ", exclude_ids)
        #############################################################################################

        ##############################  File ID and sentence mapping   #################################
        '''worker ID'''

        if "completedRecordings" in access_code_task:
            micro_task_ids, workerId_list, sentence_list, karya_audio_report, filename_list, fileID_list = karya_api_access.get_assignment_metadata_recording(
                accesscodedetails, activeprojectname,
                access_code,
                r_j, for_worker_id
            )
        else:
            micro_task_ids, workerId_list, sentence_list, karya_audio_report, filename_list, fileID_list = karya_api_access.get_assignment_metadata(
                accesscodedetails, activeprojectname,
                access_code,
                r_j, for_worker_id
            )

        
        # Get the file ID to sentence mapping using the get_fileid_sentence_mapping function from the api assignment 
        # The fileid_sentence_map is a dictionary that returns:
        # - If karya_audio_report is empty:
        #   A dictionary where each key is a tuple of (fileID, sentence), and each value is the corresponding worker ID.
        # - If karya_audio_report is not empty:
        #   A dictionary where each key is a tuple of (fileID, sentence), and each value is a tuple of (worker ID, audio report).


        fileid_sentence_map = karya_api_access.get_fileid_sentence_mapping(fileID_list, workerId_list, sentence_list, karya_audio_report)
        logger.debug("fileid_sentence_map: %s", fileid_sentence_map)
        # print("fileid_sentence_map", fileid_sentence_map)

        #Output fileid_sentence_map sample  from server
        # {('281474976758604', 'In which months / seasons are these vegetables grown?'): ('16784394',), ('281474976758605', 'What is the process of growing these vegetables?'): ('16784394',)}

        #this will find matched, unmatched and already fetched senteces and its file_id
        matched_unmathched_fetched_sentences = karya_audio_management.matched_unmatched_alreadyfetched_sentences(
            mongo,
            projects, userprojects, projectowner, accesscodedetails,
            projectsform, questionnaires, transcriptions, recordings,
            activeprojectname, derivedFromProjectName, current_username,
            project_type, derive_from_project_type,
            fileid_sentence_map, fetched_audio_list, exclude_ids,
            language, access_code
        )
        # print(matched_unmathched_fetched_sentences)  

        matched, unmatched, already_fetched = matched_unmathched_fetched_sentences
        # print("Matched Sentences:", matched)
        # print("Unmatched Sentences:", unmatched)
        # print("Already Fetched Sentences:", already_fetched)
        logger.debug("Matched Sentences: %s", matched)
        logger.debug("Unmatched Sentences: %s", unmatched)
        logger.debug("Already Fetched Sentences: %s", already_fetched)


        #############################################################################################
        # getnsave_karya_recordings -> get_insert_id -> getaudiofromprompttext
        karya_audio_management.getnsave_karya_recordings(
            mongo,
            projects, userprojects, projectowner, accesscodedetails,
            projectsform, questionnaires, transcriptions, recordings,
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


@karya_bp.route('/update_speaker_ids', methods=['GET', 'POST'])
@login_required
def update_speaker_ids():
    print("update_speaker_ids")
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
        print("karya.py line 425 - ",
              derive_from_project_type, derivedFromProjectName)

##############################################################
    homeinsertform_data = json.loads(request.form['a'])
    homeinsertform_data = dict(homeinsertform_data)
    print("homeinsertform_data :", homeinsertform_data)
 ##############################################################
    # if request.method == 'POST':

    access_code = homeinsertform_data["access_code"]
    for_worker_id = homeinsertform_data["speaker_id"]
    phone_number = homeinsertform_data["pimobilenumber"]
    otp = homeinsertform_data["karyaotp"]

    ###############################   verify OTP    ##########################################
    otp_verified, verification_details = karya_api_access.verify_karya_otp(
        access_code, phone_number, otp
    )
    if not otp_verified:
        flash("Please Provide Correct OTP/Mobile Number")
        return redirect(url_for('karya_bp.home_insert'))
    #############################################################################################

    ###############################   Get Assignments    ########################################

    # r_j = request json , hederr = token_Id
    r_j, hederr = karya_api_access.get_verified_karya_assignments(
        verification_details)
    # print(r_j)
    microtasks = r_j['microtasks']
    assignment = r_j['assignments']

    '''list of all required meta-data of verified assignments and microtasks'''
    filenames = [fileName["input"]["files"]["recording"]
                 for fileName in microtasks]
    domains = [doamin['input']['data']['Domain'] for doamin in microtasks]
    elicitationmethods = [elicitationmethod['input']['data']
                          ['Elicitation Method'] for elicitationmethod in microtasks]
    sentences = [sentence['input']['data']['sentence']
                 for sentence in microtasks]
    speakerIds = [speakerId["input"]["chain"]["workerId"]
                  for speakerId in microtasks]
    fileIds = [fileId["id"] for fileId in assignment]
    quesIds = [quesId['input']['data']['quesId'] for quesId in microtasks]

    # print("Filename : ",filenames, "\n")
    # print("domain: ", domains, "\n")
    # print("elicit_method : ", elicitationmethods, "\n")
    # print("sentence : ", sentences, "\n")
    # print("speakerids : ", speakerIds, "\n")
    # print("fileId : ", fileIds)

    # verified_dict = dict(zip(sentences, zip(fileIds, filenames, speakerIds, domains, elicitationmethods)))

    '''dictionary of all list of required meta-data where key is sentence'''
    verifiedMetadata_dict = {}
    for key in filenames:
        verifiedMetadata_dict[key] = {}

    # Loop through the keys and values lists and add each value to the corresponding nested dictionary
    for key, fileIds, speakerIds, domains, quesIds, sentences in zip(filenames, fileIds, speakerIds, domains, quesIds, sentences):
        verifiedMetadata_dict[key]['fileId'] = fileIds
        verifiedMetadata_dict[key]['speakerId'] = speakerIds
        # verifiedMetadata_dict[key]['fileName'] = filenames
        verifiedMetadata_dict[key]['domain'] = domains
        verifiedMetadata_dict[key]['quesId'] = quesIds
        verifiedMetadata_dict[key]['sentence'] = sentences

    print("\n verifiedMetadata_dict: ", verifiedMetadata_dict)

    # First, get the list of original file names from the transcriptions collection
    databaseFileNames = []
    for document in transcriptions.find({"projectname": activeprojectname},
                                        {"audioFilename": 1, "_id": 0}):
        if document["audioFilename"] != "":
            databaseFileNames.append(document["audioFilename"])
    print(" \n \n databaseFileNames : ", databaseFileNames)  # db file name list

    # Loop over each verified audio file and check if it matches with any of the original file names
    for verified_audiofile, verified_value in verifiedMetadata_dict.items():
        for databaseFileName in databaseFileNames:
            # matching karya file name with the db
            if databaseFileName.endswith(verified_audiofile):
                # If there's a match, update the karyaSpeakerId in the transcriptions collection
                # transcriptions.update_one({'_id': ObjectId(documentId)}, {"$set": {"audioFilename": orignalFileName}})

                find_speakerId = transcriptions.find_one({"projectname": activeprojectname, "audioFilename": databaseFileName},
                                                         {'karyaInfo.karyaSpeakerId': 1, "_id": 0})
                print(" \n old speakerId : ",
                      find_speakerId['karyaInfo']['karyaSpeakerId'])

                print("\n file found ", databaseFileName, " And ",
                      "New speakerId : ", verified_value['speakerId'])

                transcriptions.update_one({"projectname": activeprojectname, "audioFilename": databaseFileName},
                                          {"$set": {'karyaInfo.karyaSpeakerId': verified_value['speakerId']}})

                # audioId, orignalFileName = databaseFileName.rsplit("_", 1)
                # orignalFileName = orignalFileName.replace("_", "")
                # document = transcriptions.find_one({"audioFilename": databaseFileName}, {"_id": 1})
                # if document is not None and document.get("audioFilename", "") != "":
                #     documentId = document["_id"]
                #     print("documentId : ", documentId)
                #     # transcriptions.update_one({'_id': ObjectId(documentId)}, {"$set": {"karyaInfo.karyaSpeakerId": verified_value["speakerId"]}})
                #     if document["audioFilename"] != "":
                #         # transcriptions.update_one({'_id': ObjectId(documentId)}, {"$set": {"audioFilename": orignalFileName}})
                #         print("audioFilename :",document["audioFilename"])

    return "OK"


# @karya_bp.route('/karyaaudiobrowse', methods=['GET', 'POST'])
# @login_required
# def karyaaudiobrowse():
#     try:
#         projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo, 'projects', 'userprojects', 'transcriptions')
#         current_username = getcurrentusername.getcurrentusername()
#         activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
#         projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
#         shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects, current_username, activeprojectname)

#         active_speaker_id = shareinfo['activespeakerId']
#         print("activeprojectname:", activeprojectname)
#         print("active_speaker_id:", active_speaker_id)
#         data = {}
#         for transcriptions_data in transcriptions.find(
#                 {
#                     "projectname": activeprojectname,
#                     "audiodeleteFLAG": 0
#                 },
#                 {
#                     "_id": 0,
#                     "audioId": 1,
#                     "audioFilename": 1,
#                     "karyaInfo.karyaFetchedAudioId": 1,
#                     "speakerId": 1,
#                     "karyaInfo.karyaSpeakerId": 1
#                 }
#         ):
#             if "karyaInfo" in transcriptions_data and "karyaSpeakerId" in transcriptions_data["karyaInfo"] and "karyaFetchedAudioId" in transcriptions_data["karyaInfo"]:
#                 speaker_id = transcriptions_data["speakerId"]
#                 if speaker_id not in data:
#                     data[speaker_id] = []
#                 data[speaker_id].append(transcriptions_data)
#         # print(data)

#     except Exception as e:
#         logger.exception(e)

#     return render_template('karyaaudiobrowse.html', projectName=activeprojectname, data=data)

'''creating table of audio files with realted details'''
@karya_bp.route('/karyaaudiobrowse', methods=['GET', 'POST'])
@login_required
def karyaaudiobrowse():
    try:
        fs = gridfs.GridFS(mongo.db)
        projects, userprojects, transcriptions, accesscodedetails, fs_files, fs_chunks = getdbcollections.getdbcollections(
            mongo, 'projects', 'userprojects', 'transcriptions', 'accesscodedetails', 'fs.files', 'fs.chunks')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(
            current_username, userprojects)
        projectowner = getprojectowner.getprojectowner(
            projects, activeprojectname)
        shareinfo = getuserprojectinfo.getuserprojectinfo(
            userprojects, current_username, activeprojectname)

        active_speaker_id = shareinfo['activespeakerId']
        print("activeprojectname:", activeprojectname)
        print("active_speaker_id:", active_speaker_id)
        data = {}
        for transcriptions_data in transcriptions.find(
                {
                    "projectname": activeprojectname,
                    "audiodeleteFLAG": 0
                },
                {
                    "_id": 0,
                    "audioId": 1,
                    "audioFilename": 1,
                    "karyaInfo.karyaFetchedAudioId": 1,
                    "speakerId": 1,
                    "karyaInfo.karyaSpeakerId": 1
                }
        ):
            # print(transcriptions_data)
            if "karyaInfo" in transcriptions_data and "karyaSpeakerId" in transcriptions_data["karyaInfo"] and "karyaFetchedAudioId" in transcriptions_data["karyaInfo"]:
                speaker_id = transcriptions_data["speakerId"]
                if speaker_id not in data:
                    data[speaker_id] = []
                data[speaker_id].append(transcriptions_data)
        
        # for key, value in data.items():
        #     print("Key:", key)
        #     print("Value:", value)
        for speaker_id, transcriptions_list in data.items():
            for transcription in transcriptions_list:
                if "karyaInfo" in transcription and "karyaSpeakerId" in transcription["karyaInfo"] and "karyaFetchedAudioId" in transcription["karyaInfo"] and "audioFilename" in transcription:
                    karya_fetched_audio_id = transcription["karyaInfo"]["karyaFetchedAudioId"]
                    audio_filename = transcription["audioFilename"]
                    if karya_fetched_audio_id in accesscodedetails.distinct("karyafetchedaudios"):
                        access_code = accesscodedetails.find_one({"karyafetchedaudios": karya_fetched_audio_id, "isActive":1})["karyaaccesscode"]
                        transcription["accesscode"] = access_code
                        # print("access_code : ", access_code)

                    files = fs_files.find({"filename": audio_filename, "projectname": activeprojectname}, {"_id": 1, "filename": 1})
                    for file in files:
                        gridfs_file = fs.get(file['_id'])
                        audio_data = gridfs_file.read()
                        # print("File Name:", audio_filename)
                        # print("File Data:", type(audio_data))

                        
                        # Append the audio data to the transcription entry in data
                        
                        # transcription["audio_data_in_bytes"] = audio_data
                        
                        # Encode audio data as base64 for embedding in HTML

                        audio_data_base64 = base64.b64encode(audio_data).decode('utf-8')
                        transcription["audio_data_in_bytes"] = audio_data_base64
                        # transcription[audio_filename] = type(audio_data)
        for key, value in data.items():
            print("Key:", key)
            # print("Value:", value)
            # Append modified transcription entry to data
            # data[speaker_id].append(transcription)
            # print("data type : ", data)
########################################################################  
######################################################################## 
        # print(data)

    except Exception as e:
        logger.exception(e)

    return render_template('karyaaudiobrowse.html', projectName=activeprojectname, data=data)


@karya_bp.route('/karyadeleteaudiobrowse', methods=['GET', 'POST'])
@login_required
def karyadeleteaudiobrowse():

    projects, userprojects, transcriptions, accesscodedetails, fs_files, fs_chunks = getdbcollections.getdbcollections(
        mongo, 'projects', 'userprojects', 'transcriptions', 'accesscodedetails', 'fs.files', 'fs.chunks')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    shareinfo = getuserprojectinfo.getuserprojectinfo(
        userprojects, current_username, activeprojectname)
    active_speaker_id = shareinfo['activespeakerId']
    print("active_speaker_id : ", active_speaker_id)
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)

    selected_data = request.get_json()
    # Perform the delete operation using the selected_data
    # Replace this with your own delete logic
    # Here's an example of how you can access the data
    for item in selected_data:

        speaker_id = item['speakerId']
        audio_id = item['audioId']
        audio_filename = item['audioFilename']
        karya_fetchedAudio_ids = item['karyaFetchedAudioIds']
        acode = item['karyaacode']
        print("acode : ", acode)
        # print(item)

        # Perform the delete operation for the given speaker_id and audio_id
        # Split the speaker_id if needed to extract the actual speakerId and audioId
        print("Project Name : ", activeprojectname)
        print("speaker_id : ", speaker_id)
        print("audio_id : ", audio_id)
        print("audioFilename : ", audio_filename)
        print("karyaAudioId : ", karya_fetchedAudio_ids)
        print("####################################\n########################################\n#####################")

        # Rest of the delete logic...

        # accesscodedetails = remove matched karyafetchedaudios from list
        # accesscodedetails_result_find = accesscodedetails.find_one({"projectname": str(activeprojectname),
        #                                                             "isActive":1, 'fetchData':1,
        #                                                               'karyafetchedaudios':karya_fetchedAudio_ids},
        #                                                              {'karyafetchedaudios':1, "karyaaccesscode":1})#['karyafetchedaudios']['karyaaccesscode']

        accesscodedetails_result_find = accesscodedetails.find_one({'projectname': str(activeprojectname),
                                                                    "isActive": 1, 'fetchData': 1,
                                                                    'karyafetchedaudios': karya_fetchedAudio_ids, 'karyaaccesscode': acode},
                                                                   {'karyafetchedaudios': 1})

        # print("accesscodedetails_result_find : ","karya audio ids: ",accesscodedetails_result_find['karyafetchedaudios'],
        #                                         "accesscode: ",accesscodedetails_result_find['karyaaccesscode'])

        # print("accesscodedetails_result_find : ", "karya audio ids: ",
        #       accesscodedetails_result_find['karyafetchedaudios'])
        # delete karya audio id
        accesscodedetails_result = accesscodedetails.update_one(
            {
                "projectname": str(activeprojectname),
                'karyaaccesscode': acode,
                "isActive": 1, 'fetchData': 1,
                'karyafetchedaudios': karya_fetchedAudio_ids},
            {
                '$pull': {
                    'karyafetchedaudios':   karya_fetchedAudio_ids
                }
            }
        )

        print("####################################\n########################################\n#####################")

        # transcription deletefalg = 1
        transcriptions_result_find = transcriptions.find_one({"projectname": activeprojectname, 'speakerId': speaker_id,
                                                              'audioId': audio_id,
                                                              'audioFilename': audio_filename,
                                                              'karyaInfo.karyaFetchedAudioId': karya_fetchedAudio_ids}, {})

        transcription_id = transcriptions_result_find['_id']

        print(transcriptions.find_one({"_id": transcription_id}, {}))

        audiodetails.delete_one_audio_file(projects,
                                           transcriptions,
                                           activeprojectname,
                                           current_username,
                                           transcription_id,
                                           audio_id,
                                           speaker_id,
                                           update_latest_audio_id=1)

        # audiodetails.delete_one_audio_file(projects,
        #                                    transcriptions,
        #                                    activeprojectname,
        #                                    current_username,
        #                                    speaker_id,
        #                                    audio_id,
        #                                    update_latest_audio_id=1)

        # print("transcriptions_result_find : " ,transcriptions_result_find['_id'])

        # transcriptions_deleteFlag = transcriptions.update_one({"_id":ObjectId(transcription_id)},{'$set':{'audiodeleteFLAG':1}})
        # transcriptions remove whole document that is matched
        # delete_transcriptions_doc = transcriptions.delete_one({"_id":ObjectId(transcription_id)})

        print("####################################\n########################################\n#####################")

        # fs.files remove audio file

        # fsfiles_result_find = fs_files.find_one({'projectname': activeprojectname, "audioId":audio_id, "filename":audio_filename},{})
        # fsfile_id = fsfiles_result_find['_id']
        # print(fsfile_id)
        # delete_fsfile = fs_files.delete_one({"_id":ObjectId(fsfile_id)})
        # print("####################################\n########################################\n#####################")

        # fs.chunks remove audio bytes
        # fschunks_result_find = fs_chunks.find_one({'files_id':fsfile_id},{})
        # fschunk_id = fschunks_result_find['_id']
        # print(fschunk_id)
        # delete_fschunk = fs_chunks.delete_one({"_id":ObjectId(fschunk_id)})
        # print("####################################\n########################################\n#####################")

        # projects
        # speakersAudioIds_speakerid = str("speakersAudioIds."+speaker_id)
        # print(speakersAudioIds_speakerid)
        # projects_result_find = projects.find_one({"projectname":activeprojectname, speakersAudioIds_speakerid : audio_id},{})
        # print(projects_result_find)

        # print("Matched documents:", accesscodedetails_result.matched_count)
        # print("Modified documents:", accesscodedetails_result.modified_count)

        # transcriptions_result = transcriptions.update_one({
        #                     'projectname': activeprojectname,
        #                     'speakerId': speaker_id,
        #                     'audioId':audio_id,
        #                     'audioFilename':audioFilename,
        #                     'karyaInfo.karyaFetchedAudioId':karyaAudioId
        #                     },{"$set":
        #                        {
        #                         "audioFilename":"",
        #                         "speakerId":""
        #                         }, "$unset":{"karyaInfo":"", "audioMetadata":"", "additionalInfo":"" }})

        # print("Matched documents:", transcriptions_result.matched_count)
        # print("Modified documents:", transcriptions_result.modified_count)

        # else:
        # print("not matched")

    # Return a success response
    return jsonify({'message': 'Audio file(s) deleted successfully'})





#################################################################################################
######################################### New Karya #############################################
#################################################################################################





@karya_bp.route('/karya_new_home')
@login_required
def karya_new_home():
    accesscodedetails, userprojects, speakerdetails = getdbcollections.getdbcollections(mongo,
                                                                        'accesscodedetails',
                                                                        'userprojects', 
                                                                        'speakerdetails')
    # Retrieve the current user's username and active project name
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)

    # Render the template with the active project name
    return render_template(
        "karya_new_home.html",
        activeprojectname=activeprojectname
    )



#updated_karya_new with access_code and speaker_id to uplaod the access code csv
@karya_bp.route('/karya_new_uploadacesscode', methods=['GET', 'POST'])
@login_required
def karya_new_uploadacesscode():
    projects, userprojects, projectsform, karyaaccesscodedetails, speakerdetails = getdbcollections.getdbcollections(mongo,
                                                                                                     'projects',
                                                                                                     'userprojects',
                                                                                                     'projectsform',
                                                                                                     'accesscodedetails', 
                                                                                                     'speakerdetails')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                            userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    project_type = getprojecttype.getprojecttype(projects, activeprojectname)
    derived_from_project_type, derived_from_project_name = getprojecttype.getderivedfromprojectdetails(projects,
                                                                                                       activeprojectname)

    logger.debug("derived_from_project_type: %s\nderived_from_project_name: %s",
                 derived_from_project_type, derived_from_project_name)
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

    activeacode = karyaaccesscodedetails.find(
        {"projectname": activeprojectname, "isActive": 1, "additionalInfo.karya_version":"karya_main"})
    deactiveacode = karyaaccesscodedetails.find(
        {"projectname": activeprojectname, "isActive": 0, "additionalInfo.karya_version":"karya_main"})

    active_data_table = []
    deactive_data_table = []

    for item in activeacode:
        item_dict = {
            "id": str(item["_id"]),  # Convert ObjectId to string
            "karyaaccesscode": item["karyaaccesscode"],
            "karyaspeakerid": item["karyaspeakerid"],
            "isActive": item["isActive"],
            "fetchData": item["fetchData"]
            # Include other required fields from the item
        }
        active_data_table.append(item_dict)

    for item in deactiveacode:
        item_dict = {
            "id": str(item["_id"]),  # Convert ObjectId to string
            "karyaaccesscode": item["karyaaccesscode"],
            "karyaspeakerid": item["karyaspeakerid"],
            "isActive": item["isActive"],
            "fetchData": item["fetchData"]
            # Include other required fields from the item
        }
        deactive_data_table.append(item_dict)

    # Convert the ObjectId to string for serialization
    # active_data_table = [json.loads(json.dumps(item, default=str)) for item in activeacode]
    # deactive_data_table = [json.loads(json.dumps(item, default=str)) for item in deactiveacode]

    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                      current_username,
                                                      activeprojectname)

    if request.method == "POST":
        access_code_file = request.files['accesscodefile']
        task = request.form.get('task')
        language = request.form.get('langscript')
        domain = request.form.getlist('domain')
        phase = request.form.get('phase')  # =>numbers - 0,1,2,3, etc
        elicitationmethod = request.form.getlist("elicitation")
        fetch_data = request.form.get('fetchdata')
        karya_version = 'karya_main'

        if fetch_data == 'on':
            fetch_data = 1
        else:
            fetch_data = 0

        # Call the function to get the processed DataFrame
        processed_dataframe_csv = access_code_management.process_access_code_csv_karya_new_update(access_code_file)

        # Extract each column into separate variables
        access_code = processed_dataframe_csv['access_code']
        avatar_id = processed_dataframe_csv['avatar_id']
        worker_id = processed_dataframe_csv['worker_id']
        yob = processed_dataframe_csv['yob']
        gender = processed_dataframe_csv['gender']
        full_name = processed_dataframe_csv['full_name']
        phone_number = processed_dataframe_csv['phone_number']
        income_source = processed_dataframe_csv['income_source']
        education_level = processed_dataframe_csv['education_level']

        # Now each variable holds the respective column from the DataFrame
        print("Access Code: ", type(access_code))
        print("Avatar ID: ", avatar_id)

        print(type(yob))
        
        
        upload_response = access_code_management.upload_access_code_metadata_for_karya_new_update(
            karyaaccesscodedetails,
            speakerdetails,
            activeprojectname,
            current_username,
            task,
            language,
            domain,
            phase,
            elicitationmethod,
            fetch_data,
            karya_version,
            access_code, avatar_id, worker_id, yob, gender, full_name, phone_number, education_level
        )


        flash("Access Code Uploaded")
        
        return redirect(url_for('karya_bp.karya_new_home'))

    return render_template("karya_new_uploadacesscode.html",
                           data=currentuserprojectsname,
                           active_data_table=active_data_table,
                           deactive_data_table=deactive_data_table,
                           projectName=activeprojectname,
                           uploadacesscodemetadata=formacesscodemetadata,
                           projecttype=project_type,
                           shareinfo=shareinfo)










@karya_bp.route('/karya_new_uploadacesscode_old', methods=['GET', 'POST'])
@login_required
def karya_new_uploadacesscode_old():
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
    derived_from_project_type, derived_from_project_name = getprojecttype.getderivedfromprojectdetails(projects,
                                                                                                       activeprojectname)

    logger.debug("derived_from_project_type: %s\nderived_from_project_name: %s",
                 derived_from_project_type, derived_from_project_name)
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

    activeacode = karyaaccesscodedetails.find(
        {"projectname": activeprojectname, "isActive": 1, "additionalInfo.karya_version":"karya_main"})
    deactiveacode = karyaaccesscodedetails.find(
        {"projectname": activeprojectname, "isActive": 0, "additionalInfo.karya_version":"karya_main"})

    active_data_table = []
    deactive_data_table = []

    for item in activeacode:
        item_dict = {
            "id": str(item["_id"]),  # Convert ObjectId to string
            "karyaaccesscode": item["karyaaccesscode"],
            "karyaspeakerid": item["karyaspeakerid"],
            "isActive": item["isActive"],
            "fetchData": item["fetchData"]
            # Include other required fields from the item
        }
        active_data_table.append(item_dict)

    for item in deactiveacode:
        item_dict = {
            "id": str(item["_id"]),  # Convert ObjectId to string
            "karyaaccesscode": item["karyaaccesscode"],
            "karyaspeakerid": item["karyaspeakerid"],
            "isActive": item["isActive"],
            "fetchData": item["fetchData"]
            # Include other required fields from the item
        }
        deactive_data_table.append(item_dict)

    # Convert the ObjectId to string for serialization
    # active_data_table = [json.loads(json.dumps(item, default=str)) for item in activeacode]
    # deactive_data_table = [json.loads(json.dumps(item, default=str)) for item in deactiveacode]

    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                      current_username,
                                                      activeprojectname)

    if request.method == "POST":
        access_code_file = request.files['accesscodefile']
        task = request.form.get('task')
        language = request.form.get('langscript')
        domain = request.form.getlist('domain')
        phase = request.form.get('phase')  # =>numbers - 0,1,2,3, etc
        elicitationmethod = request.form.getlist("elicitation")
        fetch_data = request.form.get('fetchdata')
        karya_version = 'karya_main'

        if fetch_data == 'on':
            fetch_data = 1
        else:
            fetch_data = 0

        accesscode_from_csv = access_code_management.process_access_code_csv_karya_new(access_code_file)
        print("accesscode_from_csv: ", accesscode_from_csv)
        upload_response = access_code_management.upload_access_code_metadata_for_karya_new(
            karyaaccesscodedetails,
            activeprojectname,
            current_username,
            task,
            language,
            domain,
            phase,
            elicitationmethod,
            fetch_data,
            karya_version,
            accesscode_from_csv
        )
        
        return redirect(url_for('karya_bp.karya_new_home'))

    return render_template("karya_new_uploadacesscode_old.html",
                           data=currentuserprojectsname,
                           active_data_table=active_data_table,
                           deactive_data_table=deactive_data_table,
                           projectName=activeprojectname,
                           uploadacesscodemetadata=formacesscodemetadata,
                           projecttype=project_type,
                           shareinfo=shareinfo)




@karya_bp.route('/karya_new_manage_accesscode', methods=['GET', 'POST'])
@login_required
def karya_new_manage_accesscode():
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
    print(project_type)

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

    print("############################################################")
    print(projects)
    print(projectsform)
    print(activeprojectname)
    print(project_type)
    print(derived_from_project_name)
    print(derived_from_project_type)
    print('formacesscodemetadata', formacesscodemetadata)

    # This defines the minimum share level of the user who will get info
    # of all access codes (incl those assigned by the other users)
    # Users with share level lower than this will get info of only those
    # access codes which have been assigned by that specific user
    all_data_share_level = 10
    all_acode_metadata = access_code_management.karya_new_get_access_code_metadata(
        accesscode_info,
        activeprojectname,
        share_level,
        all_data_share_level,
        current_username
    )

    return render_template('karya_new_manage_accesscode.html',
                           data=currentuserprojectsname,
                           projectName=activeprojectname,
                           uploadacesscodemetadata=formacesscodemetadata,
                           projecttype=project_type,
                           data_table=all_acode_metadata,
                           count=len(all_acode_metadata)
                           )





@karya_bp.route('/karya_new_assign_access_code_user', methods=['GET', 'POST'])
@login_required
def karya_new_assign_access_code_user():
    # print ('Adding speaker info into server')
    accesscodedetails, userprojects, speakerdetails = getdbcollections.getdbcollections(mongo,
                                                                        'accesscodedetails',
                                                                        'userprojects', 
                                                                        'speakerdetails')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    
    accesscodedetails, userprojects, userlogin, speakermeta, projects = getdbcollections.getdbcollections(
	mongo, 'accesscodedetails', 'userprojects', 'userlogin', 'speakerdetails', 'projects')

    
    # current_username = getcurrentusername.getcurrentusername()
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
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)

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
            print(accesscodefor)
            task = request.form.get('task')
            print(task)
            language = request.form.get('langscript')
            domain = request.form.getlist('domain')
            elicitationmethod = request.form.getlist("elicitation")

            #finding speakerid and access code which is not assigned to ueser
            karyaspeakerid, accesscode = access_code_management.karya_new_get_new_accesscode_and_speakerid(
                accesscodedetails=accesscodedetails,
                activeprojectname=activeprojectname,
                accesscodefor=accesscodefor,
                task=task,
                domain=domain,
                elicitationmethod=elicitationmethod,
                language=language)


            if accesscode == '' and karyaspeakerid == '':
                flash("Please Upload New Access Code")
                return redirect(url_for('karya_bp.karya_new_home'))

            if fage is not None and fname is not None:

                #metadata save to accesscodedetails 
                access_code_management.karya_new_add_access_code_metadata(
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
     
                #metadata save to accesscodedetails currten and old metadata transfer to old maetadata in accesscode details 
                access_code_management.karya_new_update_access_code_metadata(
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


    return redirect(url_for('karya_bp.karya_new_manage_accesscode'))










@karya_bp.route('/register_speaker_get_otp', methods=['POST'])
def register_speaker_get_otp():
    data = request.get_json()
    phone_number = data.get('phone_number')
    
    url = 'https://main-karya.centralindia.cloudapp.azure.com/api_auth/v5/otp/generate'
    headers = {'phone_number': phone_number}
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            otp_id = response_data['otp_id']
            # print("otp_id gentrated from get otp: ", otp_id)
            return jsonify({'success': True, 'otp_id': otp_id})
        else:
            return jsonify({'success': False, 'message': 'Failed to generate OTP'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    

@karya_bp.route('/register_speaker_verify_otp', methods=['POST'])
def register_speaker_verify_otp():
    data = request.get_json()
    phone_number = data.get('phone_number')
    otp = data.get('otp')
    otp_id = data.get('otp_id')

    # Check if otp_id is None before proceeding
    if otp_id is None:
        return jsonify({'success': False, 'message': 'Missing OTP ID'}), 400

    # Verify OTP
    url = 'https://main-karya.centralindia.cloudapp.azure.com/api_auth/v5/otp/verify'
    headers = {
        'phone_number': phone_number,
        'otp_id': otp_id,
        'otp': otp
    }

    try:
        otp_response = requests.put(url, headers=headers)
        if otp_response.status_code == 200:
            response_data = otp_response.json()

            # Extract token_id from the OTP response
            token_id = [p['id_token'] for p in response_data][0]
            # print("Token ID: ", token_id)

            # Use token_id to fetch worker metadata
            metadata_url = 'https://main-karya.centralindia.cloudapp.azure.com/api_worker/v5/avatars'
            metadata_headers = {'karya_worker_id_token': token_id}

            worker_response = requests.get(metadata_url, headers=metadata_headers)

            if worker_response.status_code == 200:
                worker_data = json.loads(worker_response.text)

                # Collect all access_code and worker_id pairs
                results = [{'access_code': worker['access_code'], 'worker_id': worker['worker_id']}
                           for worker in worker_data if 'access_code' in worker and 'worker_id' in worker]

                if results:
                    # Return success with the list of access_code and worker_id pairs
                    return jsonify({'success': True, 'results': results})
                else:
                    # If no matching access_code/worker_id found
                    return jsonify({'success': False, 'message': 'Access code or worker ID not found'}), 404
            else:
                return jsonify({'success': False, 'message': 'Failed to fetch worker metadata'}), 500
        else:
            return jsonify({'success': False, 'message': 'Incorrect OTP'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# assigning the the karya speaker_id and life speaker_id to active access code and assign active access code details 
# to the speakerdetails and replace existing_lifesourceid with lifespeaker_id from accesscocdedetails
# and existing_lifesourceid put in old_lifesourcedid so if existing_lifesourceid is needed that can be find in old_lifesourcedid
@karya_bp.route('/karya_new_assign_karya_life_id', methods=['POST'])
def karya_new_assign_karya_life_id():
    try:
        # Consolidate collection retrieval
        accesscodedetails, userprojects, userlogin, speakermeta, projects, speakerdetails = getdbcollections.getdbcollections(
            mongo, 'accesscodedetails', 'userprojects', 'userlogin', 'speakermeta', 'projects', 'speakerdetails'
        )

        # Retrieve current username and active project name
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)

        usertype = userdetails.get_user_type(userlogin, current_username)
        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects, current_username, activeprojectname)
        projectowner = getprojectowner.getprojectowner(projects, activeprojectname)

        data = request.json
        access_code = list(data.keys())[0]
        worker_id = data[access_code]

        if not access_code or not worker_id:
            return jsonify({'status': 'Access code or worker ID is missing'}), 400

        # Check if the access_code exists in the database and is active
        speaker_record = accesscodedetails.find_one({
            'karyaaccesscode': access_code,
            "additionalInfo.karya_version": "karya_main", 
            "projectname": activeprojectname, 
            "isActive": 1
        })

        if speaker_record:
            existing_karyaspeakerid = speaker_record.get('karyaspeakerid')

            if existing_karyaspeakerid:
                # If karyaspeakerid already exists, return that the speaker is already registered
                return jsonify({'status': 'Speaker registered already!', 'access_code': access_code})

            # Retrieve worker metadata
            worker_metadata = speaker_record.get('current', {}).get('workerMetadata', {})
            name = worker_metadata.get('name', '')
            age_group = worker_metadata.get('agegroup', '')

            if name and age_group:
                # Create the lifespeakerid
                rename_in_form_dob = age_group.replace("-", "")
                rename_in_form = name.replace(" ", "").lower()
                lifespeakerid = f"{rename_in_form}{rename_in_form_dob}_{worker_id}"

                # Update both karyaspeakerid and lifespeakerid
                update_result = accesscodedetails.update_one(
                    {"karyaaccesscode": access_code, 
                     "additionalInfo.karya_version": "karya_main",
                     "projectname": activeprojectname, 
                     "isActive": 1},
                    {'$set': {
                        "karyaspeakerid": worker_id,
                        "lifespeakerid": lifespeakerid
                    }}
                )

                # Retrieve updated document for metadata insertion
                document = accesscodedetails.find_one({
                    "karyaaccesscode": access_code, 
                    "karyaspeakerid": worker_id,
                    "projectname": activeprojectname, 
                    "isActive": 1,
                    "additionalInfo.karya_version": "karya_main"
                }, {
                    "lifespeakerid": 1, "karyaaccesscode": 1, "karyaspeakerid": 1,
                    "current.workerMetadata": 1, "additionalInfo": 1, "_id": 0
                })

                try:
                    new_metadata = {
                        "name": document["current"]["workerMetadata"].get("name", ""),
                        "agegroup": document["current"]["workerMetadata"].get("agegroup", ""),
                        "gender": document["current"]["workerMetadata"].get("gender", ""),
                        "educationlevel": document["current"]["workerMetadata"].get("educationlevel", ""),
                        "educationmediumupto12": document["current"]["workerMetadata"].get("educationmediumupto12", []),
                        "educationmediumafter12": document["current"]["workerMetadata"].get("educationmediumafter12", []),
                        "speakerspeaklanguage": document["current"]["workerMetadata"].get("speakerspeaklanguage", []),
                        "recordingplace": document["current"]["workerMetadata"].get("recordingplace", ""),
                        "typeofrecordingplace": document["current"]["workerMetadata"].get("typeofrecordingplace", ""),
                        "lifespeakerid": document["lifespeakerid"],
                        "karyaaccesscode": document["karyaaccesscode"],
                        "karyaspeakerid": document["karyaspeakerid"]
                    }

                    # Replace None values
                    for field in ["name", "agegroup", "gender", "educationlevel", "recordingplace", "typeofrecordingplace"]:
                        if new_metadata[field] is None:
                            new_metadata[field] = ""
                    for field in ["educationmediumupto12", "educationmediumafter12", "speakerspeaklanguage"]:
                        if new_metadata[field] is None:
                            new_metadata[field] = []

                    lifespeakerid_var = new_metadata["lifespeakerid"]
                    additionalInfo_var = document["additionalInfo"]
                    print('###################################################')
                    print('additional_info from the function karya_new_write_speaker_metadata: ', additionalInfo_var)
                    print('###################################################')

                    # Insert metadata into speakerdetails
                    speakerDetails.karya_new_write_speaker_metadata_details(
                        speakerdetails, current_username, activeprojectname,
                        current_username, 'field', 'speed', lifespeakerid_var, new_metadata, 'single',
                        additionalInfo_var
                    )
                except Exception as e:
                    print(f"Error inserting metadata: {e}")

                if update_result.modified_count > 0:
                    return jsonify({'status': 'Speaker updated successfully!', 'access_code': access_code})
                else:
                    return jsonify({'status': 'No updates made to the database for access code', 'access_code': access_code}), 400
            else:
                return jsonify({'status': 'Missing worker metadata for lifespeakerid creation.'}), 400
        else:
            return jsonify({'status': 'Access code not found or inactive', 'access_code': access_code}), 404

    except Exception as e:
        return jsonify({'status': 'Error occurred during operation', 'error': str(e)}), 500

import csv
from io import StringIO
from flask import request, jsonify
'''
@karya_bp.route('/upload_csv_update_karya_speaker', methods=['POST'])
def upload_csv_update_karya_speaker():
    try:
        # Consolidate collection retrieval
        accesscodedetails, userprojects, userlogin, speakermeta, projects, speakerdetails = getdbcollections.getdbcollections(
            mongo, 'accesscodedetails', 'userprojects', 'userlogin', 'speakermeta', 'projects', 'speakerdetails'
        )

        # Retrieve current username and active project name
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)

        usertype = userdetails.get_user_type(userlogin, current_username)
        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects, current_username, activeprojectname)
        projectowner = getprojectowner.getprojectowner(projects, activeprojectname)


        # Get the uploaded file
        file = request.files.get('csvFile')

        if not file:
            flash("No file uploaded Or Check The File Format")
            return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400

        # Read the CSV file
        stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)

        # # Retrieve relevant collections
        # accesscodedetails, userprojects, userlogin, speakerdetails = getdbcollections.getdbcollections(
        #     mongo, 'accesscodedetails', 'userprojects', 'userlogin', 'speakerdetails'
        # )

        # Iterate over rows and update database
        for row in csv_reader:
            access_code = row['access_code']
            worker_id = row['worker_id']
            avatar_id = row['avatar_id']  # This is the karyaspeakerid

            # Check if the access_code exists in the database and is active
        speaker_record = accesscodedetails.find_one({
            'karyaaccesscode': access_code,
            "additionalInfo.karya_version": "karya_main", 
            "projectname": activeprojectname, 
            "isActive": 1
        })

        if speaker_record:
            existing_karyaspeakerid = speaker_record.get('karyaspeakerid')

            if existing_karyaspeakerid:
                # If karyaspeakerid already exists, return that the speaker is already registered
                return jsonify({'status': 'Speaker registered already!', 'access_code': access_code})

            # Retrieve worker metadata
            worker_metadata = speaker_record.get('current', {}).get('workerMetadata', {})
            name = worker_metadata.get('name', '')
            age_group = worker_metadata.get('agegroup', '')

            if name and age_group:
                # Create the lifespeakerid
                rename_in_form_dob = age_group.replace("-", "")
                rename_in_form = name.replace(" ", "").lower()
                lifespeakerid = f"{rename_in_form}{rename_in_form_dob}_{worker_id}"

                # Update both karyaspeakerid and lifespeakerid
                update_result = accesscodedetails.update_one(
                    {"karyaaccesscode": access_code, 
                     "additionalInfo.karya_version": "karya_main",
                     "projectname": activeprojectname, 
                     "isActive": 1},
                    {'$set': {
                        "karyaspeakerid": worker_id,
                        "lifespeakerid": lifespeakerid,
                        "avatar_id" : avatar_id
                    }}
                )

                # Retrieve updated document for metadata insertion
                document = accesscodedetails.find_one({
                    "karyaaccesscode": access_code, 
                    "karyaspeakerid": worker_id,
                    "projectname": activeprojectname, 
                    "isActive": 1,
                    "additionalInfo.karya_version": "karya_main"
                }, {
                    "lifespeakerid": 1, "karyaaccesscode": 1, "karyaspeakerid": 1,
                    "current.workerMetadata": 1, "additionalInfo": 1, "avatar_id": 1, "_id": 0
                })

                try:
                    new_metadata = {
                        "name": document["current"]["workerMetadata"].get("name", ""),
                        "agegroup": document["current"]["workerMetadata"].get("agegroup", ""),
                        "gender": document["current"]["workerMetadata"].get("gender", ""),
                        "educationlevel": document["current"]["workerMetadata"].get("educationlevel", ""),
                        "educationmediumupto12": document["current"]["workerMetadata"].get("educationmediumupto12", []),
                        "educationmediumafter12": document["current"]["workerMetadata"].get("educationmediumafter12", []),
                        "speakerspeaklanguage": document["current"]["workerMetadata"].get("speakerspeaklanguage", []),
                        "recordingplace": document["current"]["workerMetadata"].get("recordingplace", ""),
                        "typeofrecordingplace": document["current"]["workerMetadata"].get("typeofrecordingplace", ""),
                        "lifespeakerid": document["lifespeakerid"],
                        "karyaaccesscode": document["karyaaccesscode"],
                        "karyaspeakerid": document["karyaspeakerid"], 
                        "avatar_id" : document["avatar_id"]
                    }

                    # Replace None values
                    for field in ["name", "agegroup", "gender", "educationlevel", "recordingplace", "typeofrecordingplace"]:
                        if new_metadata[field] is None:
                            new_metadata[field] = ""
                    for field in ["educationmediumupto12", "educationmediumafter12", "speakerspeaklanguage"]:
                        if new_metadata[field] is None:
                            new_metadata[field] = []

                    lifespeakerid_var = new_metadata["lifespeakerid"]
                    additionalInfo_var = document["additionalInfo"]
                    print('###################################################')
                    print('additional_info from the function karya_new_write_speaker_metadata: ', additionalInfo_var)
                    print('###################################################')

                    # Insert metadata into speakerdetails
                    speakerDetails.karya_new_write_speaker_metadata_details(
                        speakerdetails, current_username, activeprojectname,
                        current_username, 'field', 'speed', lifespeakerid_var, new_metadata, 'single',
                        additionalInfo_var
                    )
        
        return jsonify({'status': 'success', 'message': 'CSV processed successfully!'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    '''

@karya_bp.route('/karya_new_upload_bulk_metadata', methods=['POST'])
def karya_new_upload_bulk_metadata():
    try:
        # Consolidate collection retrieval
        accesscodedetails, userprojects, userlogin, speakermeta, projects, speakerdetails = getdbcollections.getdbcollections(
            mongo, 'accesscodedetails', 'userprojects', 'userlogin', 'speakermeta', 'projects', 'speakerdetails'
        )

        # Retrieve current username and active project name
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
                                    
        # Check if the POST request has the file part
        if 'jsonFile' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part'})

        file = request.files['jsonFile']

        # If the user does not select a file
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No selected file'})

        # Read the file and load the JSON
        file_content = file.read()
        try:
            data = json.loads(file_content)
            
            # Iterate over each record
            for item in data:
                # Access the 'data' and 'props' fields from each record
                own_access_code = item['data'].get('own_access_code')
                OutputTypeofPlace = item['data'].get('OutputTypeofPlace')
                OutputEducationLevel = item['data'].get('OutputEducationLevel')
                OutputOtherLanguages = item['data'].get('OutputOtherLanguages')
                OutputplaceofRecording = item['data'].get('OutputplaceofRecording')
                OutputMediumofEducationUpto12th = item['data'].get('OutputMediumofEducationUpto12th')
                OutputMediumofEducationAbove12th = item['data'].get('OutputMediumofEducationAbove12th')

                generated_by = item['props'].get('generated_by')
                task_id = generated_by.get('task_id')
                avatar_id = generated_by.get('avatar_id')
                worker_id = generated_by.get('worker_id')
                microtask_id = generated_by.get('microtask_id')
                assignment_id = generated_by.get('assignment_id')

                # Check if the access_code exists in the database and is active
                speaker_record = accesscodedetails.find_one({
                    'karyaaccesscode': own_access_code,
                    'karyaspeakerid': worker_id,
                    "projectname": activeprojectname, 
                    "isActive": 1
                })

                if speaker_record:
                    # Extract 'additionalInfo' safely from the speaker_record
                    accesscodedetails_additionalinfo = speaker_record.get('additionalInfo', {})
                    
                    # Ensure OutputTypeofPlace and OutputplaceofRecording are strings
                    if isinstance(OutputTypeofPlace, list):
                        OutputTypeofPlace = ', '.join(OutputTypeofPlace)  # Convert array to string
                    if isinstance(OutputplaceofRecording, list):
                        OutputplaceofRecording = ', '.join(OutputplaceofRecording)  # Convert array to string

                    # Mapping dictionaries remain the same:
                    education_level_map = {
                        'কোনওটিই নয়': 'No Schooling',
                        'প্রাথমিক বিদ্যালয়': 'Upto 12ᵗʰ',
                        'দশম শ্রেণি': 'Upto 12ᵗʰ',
                        'দ্বাদশ শ্রেণি': 'Upto 12ᵗʰ',
                        'স্নাতক': 'Graduate',
                        'স্নাতকোত্তর': 'Post-Graduate',
                        'এম.ফিল/পি এইচ ডি': 'Above PG'
                    }

                    other_languages_map = {
                        'বাংলা': 'Bangla',
                        'নেপালি': 'Nepali',
                        'রাজবংশী': 'Rajbanshi',
                        'হিন্দি': 'Hindi',
                        'ইংরেজি': 'English',
                        'জংখা': 'Dzongkha',
                        'বোড়ো': 'Bodo'
                    }

                    medium_of_education_map = {
                        'টোটো': 'Toto',
                        'ইংরেজি': 'English',
                        'হিন্দি': 'Hindi',
                        'বাংলা': 'Bangla',
                        'নেপালি': 'Nepali'
                    }

                    type_of_place_map = {
                        'ছোটো শহর': 'Town',
                        'শহর': 'City',
                        'গ্রাম': 'Village'
                    }

                    # Function to handle mapping for lists of values (like languages)
                    def map_list_values(input_list, mapping_dict):
                        if isinstance(input_list, list):
                            # If it's a list, map each individual value in the list
                            return [mapping_dict.get(value.strip(), value) for value in input_list]
                        elif isinstance(input_list, str):
                            # If it's a string, return the single mapped value (if found)
                            return mapping_dict.get(input_list.strip(), input_list)
                        return input_list  # Fallback for unexpected types

                    # Handle OutputOtherLanguages as list
                    if isinstance(OutputOtherLanguages, list):
                        OutputOtherLanguages = [lang.strip() for sublist in OutputOtherLanguages for lang in sublist.split(',')]
                        OutputOtherLanguages = map_list_values(OutputOtherLanguages, other_languages_map)

                    # Map medium of education for each value in the list
                    OutputMediumofEducationUpto12th = map_list_values(OutputMediumofEducationUpto12th, medium_of_education_map)
                    OutputMediumofEducationAbove12th = map_list_values(OutputMediumofEducationAbove12th, medium_of_education_map)

                    # Map single string values directly
                    OutputEducationLevel = map_list_values(OutputEducationLevel, education_level_map)
                    OutputTypeofPlace = map_list_values(OutputTypeofPlace, type_of_place_map)

                    # Now construct the update_data with mapped values
                    update_data_accesscodedetials = {
                        "additionalInfo.task_id": task_id,
                        "additionalInfo.microtask_id": microtask_id,
                        "additionalInfo.assignment_id": assignment_id,
                        "current.workerMetadata.educationmediumupto12": OutputMediumofEducationUpto12th,  # List of mapped values
                        "current.workerMetadata.educationmediumafter12": OutputMediumofEducationAbove12th,  # List of mapped values
                        "current.workerMetadata.educationlevel": OutputEducationLevel,  # Single mapped value
                        "current.workerMetadata.speakerspeaklanguage": OutputOtherLanguages,  # List of mapped values
                        "current.workerMetadata.recordingplace": OutputTypeofPlace,  # Single mapped value
                        "current.workerMetadata.typeofrecordingplace": OutputplaceofRecording,  # String as is
                        "current.updatedBy": current_username  # Your current username variable
                    }

                    # Update the accesscodedetails
                    accesscodedetails.update_one(
                        {'karyaaccesscode': own_access_code,
                         'karyaspeakerid': worker_id,
                         "additionalInfo.karya_version": "karya_main", 
                         "projectname": activeprojectname, 
                         "isActive": 1},  # Match the record by unique keys
                        {'$set': update_data_accesscodedetials}  # Set the new values
                    )

                    # Fetch the corresponding speaker details from the speakerdetails collection
                    find_speaker_details = accesscodedetails.find_one({
                        "karyaaccesscode": own_access_code,
                        "karyaspeakerid": worker_id,
                        "projectname": activeprojectname, 
                        "isActive": 1
                    }, {
                        "lifespeakerid": 1, "karyaaccesscode": 1, "karyaspeakerid": 1,
                        "current.workerMetadata": 1, "additionalInfo": 1, "_id": 0
                    })

                    # Update the speaker details collection with the new metadata
                    if find_speaker_details and 'lifespeakerid' in find_speaker_details:
                        speakerdetails.update_one(
                            {
                                "projectname": activeprojectname,
                                "lifesourceid": find_speaker_details["lifespeakerid"]
                            },
                            {
                                '$set': {
                                    "current.sourceMetadata.educationMediumUpto12-list": OutputMediumofEducationUpto12th,
                                    "current.sourceMetadata.educationMediumAfter12-list": OutputMediumofEducationAbove12th,
                                    "current.sourceMetadata.otherLanguages-list": OutputOtherLanguages,
                                    "current.sourceMetadata.placeOfRecording": OutputplaceofRecording,
                                    "current.sourceMetadata.educationLevel": OutputEducationLevel,
                                    "current.sourceMetadata.typeOfPlace": OutputTypeofPlace,
                                    "current.sourceMetadata.updatedBy": current_username
                                }
                            }
                        )

                    flash("Speaker/User Id Updated")

            return jsonify({'status': 'success', 'message': 'Data processed successfully'})
        
        except json.JSONDecodeError:
            return jsonify({'status': 'error', 'message': 'Invalid JSON format'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})





@karya_bp.route('/upload_csv_update_karya_speaker', methods=['POST'])
def upload_csv_update_karya_speaker():
    try:
        # Consolidate collection retrieval
        accesscodedetails, userprojects, userlogin, speakermeta, projects, speakerdetails = getdbcollections.getdbcollections(
            mongo, 'accesscodedetails', 'userprojects', 'userlogin', 'speakermeta', 'projects', 'speakerdetails'
        )

        # Retrieve current username and active project name
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)

        # Get the uploaded file
        file = request.files.get('csvFile')
        

        if not file:
            print("csv file : ", file )
            flash("No file uploaded Or Check The File Format")
            return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400

        # Read the CSV file
        stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)

        # Iterate over rows and update database
        for row in csv_reader:
            access_code_uncleaned = row['access_code']
            worker_id = row['worker_id']
            avatar_id = row['avatar_id']  # This is the karyaspeakerid


            # Clean the access code
            access_code = access_code_management.clean_access_code(access_code_uncleaned)

            print("access_code : ", access_code, "\n", "worker_id : ", worker_id, "\n", "avatar_id : ", avatar_id)


            print("access_code : ", access_code, "\n", "worker_id : ", worker_id, "\n", "avatar_id : ", avatar_id )



            # Check if the access_code exists in the database and is active
            speaker_record = accesscodedetails.find_one({
                'karyaaccesscode': access_code,
                "additionalInfo.karya_version": "karya_main", 
                "projectname": activeprojectname, 
                "isActive": 1
            })

            if speaker_record:
                existing_karyaspeakerid = speaker_record.get('karyaspeakerid')

                if existing_karyaspeakerid:
                    # If karyaspeakerid already exists, skip this speaker
                    continue

                # Retrieve worker metadata
                worker_metadata = speaker_record.get('current', {}).get('workerMetadata', {})
                name = worker_metadata.get('name', '')
                age_group = worker_metadata.get('agegroup', '')

                if name and age_group:
                    # Create the lifespeakerid
                    rename_in_form_dob = age_group.replace("-", "")
                    rename_in_form = name.replace(" ", "").lower()
                    lifespeakerid = f"{rename_in_form}{rename_in_form_dob}_{worker_id}"

                    # Update both karyaspeakerid and lifespeakerid
                    accesscodedetails.update_one(
                        {"karyaaccesscode": access_code, 
                         "additionalInfo.karya_version": "karya_main",
                         "projectname": activeprojectname, 
                         "isActive": 1},
                        {'$set': {
                            "karyaspeakerid": worker_id,
                            "lifespeakerid": lifespeakerid,
                            "avatar_id": avatar_id
                        }}
                    )

                    # Retrieve updated document for metadata insertion
                    document = accesscodedetails.find_one({
                        "karyaaccesscode": access_code, 
                        "karyaspeakerid": worker_id,
                        "projectname": activeprojectname, 
                        "isActive": 1,
                        "additionalInfo.karya_version": "karya_main"
                    }, {
                        "lifespeakerid": 1, "karyaaccesscode": 1, "karyaspeakerid": 1,
                        "current.workerMetadata": 1, "additionalInfo": 1, "avatar_id": 1, "_id": 0
                    })

                    try:
                        new_metadata = {
                            "name": document["current"]["workerMetadata"].get("name", ""),
                            "agegroup": document["current"]["workerMetadata"].get("agegroup", ""),
                            "gender": document["current"]["workerMetadata"].get("gender", ""),
                            "educationlevel": document["current"]["workerMetadata"].get("educationlevel", ""),
                            "educationmediumupto12": document["current"]["workerMetadata"].get("educationmediumupto12", []),
                            "educationmediumafter12": document["current"]["workerMetadata"].get("educationmediumafter12", []),
                            "speakerspeaklanguage": document["current"]["workerMetadata"].get("speakerspeaklanguage", []),
                            "recordingplace": document["current"]["workerMetadata"].get("recordingplace", ""),
                            "typeofrecordingplace": document["current"]["workerMetadata"].get("typeofrecordingplace", ""),
                            "lifespeakerid": document["lifespeakerid"],
                            "karyaaccesscode": document["karyaaccesscode"],
                            "karyaspeakerid": document["karyaspeakerid"], 
                            "avatar_id": document["avatar_id"]
                        }

                        # Replace None values
                        for field in ["name", "agegroup", "gender", "educationlevel", "recordingplace", "typeofrecordingplace"]:
                            if new_metadata[field] is None:
                                new_metadata[field] = ""
                        for field in ["educationmediumupto12", "educationmediumafter12", "speakerspeaklanguage"]:
                            if new_metadata[field] is None:
                                new_metadata[field] = []

                        # Insert metadata into speakerdetails
                        speakerDetails.karya_new_write_speaker_metadata_details(
                            speakerdetails, current_username, activeprojectname,
                            current_username, 'field', 'speed', new_metadata["lifespeakerid"], new_metadata, 'single',
                            document["additionalInfo"]
                        )
                        flash("Speaker/User Id Updated")

                    except Exception as e:
                        print(f"Error inserting metadata: {e}")

        return jsonify({'status': 'success', 'message': 'CSV processed successfully!'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


    
    # access_code_speakerid_map = access_code_management.karya_new_get_assigned_accesscode_and_speakerid(
    #     accesscodedetails=accesscodedetails,
    #     activeprojectname=activeprojectname,
    #     accesscodefor=accesscodefor,
    #     task=task,
    #     domain=domain,
    #     elicitationmethod=elicitationmethod,
    #     language=language)

    
    










@karya_bp.route('/karya_new_get_otp', methods=['GET', 'POST'])
@login_required
def karya_new_get_otp():
    phone_number = request.args.get("mob")
    # print("karya_new_get_otp phone number: ", phone_number)

    # Generate the otp_id using the phone number
    otp_id = karya_api_access.karya_new_get_otp_id(phone_number)
    
    if not otp_id:
        flash("Failed to generate OTP. Please try again.")
        return jsonify(result="False")

    # Send the OTP and return the otp_id to the frontend for verification
    return jsonify(result="True", otp_id=otp_id)



@karya_bp.route('/karya_new_fetch_audio', methods=['GET', 'POST'])
@login_required
def karya_new_fetch_audio():
    projects, userprojects, projectsform, recordings, transcriptions, questionnaires, accesscodedetails = getdbcollections.getdbcollections(mongo,
                                                                                                                                            'projects',
                                                                                                                                            'userprojects',
                                                                                                                                            'projectsform',
                                                                                                                                            'recordings',
                                                                                                                                            'transcriptions',
                                                                                                                                            'questionnaires',
                                                                                                                                            'accesscodedetails')
    current_username = getcurrentusername.getcurrentusername()
    # print('curent user : ', current_username)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    project_type = getprojecttype.getprojecttype(projects, activeprojectname)
    logger.debug("project_type: %s", project_type)
    logger.debug("activeprojectname: %s", activeprojectname)
    derivedFromProjectName = ''
    derive_from_project_type = ''
    if (project_type == 'transcriptions' or
            project_type == 'recordings'):

        derive_from_project_type, derivedFromProjectName = getprojecttype.getderivedfromprojectdetails(projects,
                                                                                                       activeprojectname)
        logger.debug("derive_from_project_type: %s, derivedFromProjectName: %s",
                     derive_from_project_type, derivedFromProjectName)

    if request.method == 'POST':

        project_type = projects.find_one({"projectname": activeprojectname}, {
                                         "projectType": 1})['projectType']

        access_code_task = request.form.get('additionalDropdown')
        # access_code = None
        access_code = request.form.get('transcriptionDropdown')

        if access_code_task == "newVerification" or access_code_task == "completedVerification":
            access_code = request.form.get('verificationDropdown')
        elif access_code_task == "newTranscription":
            access_code = request.form.get('transcriptionDropdown')
        elif access_code_task == "completedRecordings":
            access_code = request.form.get('recordingDropdown')

        for_worker_id = request.form.get("speaker_id")
        phone_number = request.form.get("mobile_number")
        otp = request.form.get("karya_otp")
        get_otp_id = request.form.get('otp_id')
        otp_id = get_otp_id.split(',')[0]
        access_code_of_speaker = accesscodedetails.find_one({"projectname": activeprojectname,
                                        "karyaspeakerid": for_worker_id,
                                            "additionalInfo.karya_version": "karya_main"},
                                        {'karyaaccesscode': 1, '_id': 0})['karyaaccesscode']


        # print("OTP : ", otp)
        # print("OTP ID : ", otp_id)
        # print("project_type: ", project_type)
        # # print("additional_task : ", additional_task)
        # print("access_code_task : ", access_code_task)
        # print("access_code : ", access_code)
        # print("for_worker_id : ", for_worker_id) #karyaspeakerid
        # print("phone_number : ", phone_number)
        # print("access_code_for_worker_id: ", access_code_of_speaker)
        ###############################   verify OTP    ##########################################
        # Verify OTP using the otp_id
        # Returning multiple values: 
        # 1. Whether the status code is 200 (successful verification)
        # 2. Extracted tokeotp_verified_status, otp_verification_details = karya_api_access.karya_new_verify_karya_otp(phone_number, otp, otp_id)
        # 3. The parsed verification request (response content)
        # 4. The full response object

        # Call the function from the karya_api_access module and get all returned values
        is_verified, token_id, otp_verification_request, otp_verification_details = karya_api_access.karya_new_verify_karya_otp(phone_number, otp, otp_id)

        
       
        # print(token_id)
        # print("Token ID : " ,token_id)

        if not is_verified:
            flash("Invalid OTP OR Mobile number is not registered with this project. Please try again.")
            return redirect(url_for('karya_bp.karya_new_home'))

        # Fetch assignments based on project type and access code task
        if project_type in ['validation', 'transcriptions', 'recordings', 'questionnaires']:
            if "new" in access_code_task:
                assignment_url = 'https://main-karya.centralindia.cloudapp.azure.com/api_worker/v5/assignments?type=new&from=2024-01-17T20:11:35.213Z'
                print("new api")
                #assignment_url = 'https://main-karya.centralindia.cloudapp.azure.com/api_worker/v5/assignments?type=verified&from=2024-01-17T20:11:35.213Z'
                # print("Fetching new assignments for project type:", project_type)
            elif "completed" in access_code_task:
                assignment_url = 'https://main-karya.centralindia.cloudapp.azure.com/api_worker/v5/assignments?type=verified&includemt=true&from=2021-05-11T07:23:40.654Z'
                # print("Fetching completed assignments for project type:", project_type)
                print("verified api")
            # Fetch and process the assignment URL here
        else:
            flash("Action not allowed for this project type.")
            return redirect(url_for('karya_bp.karya_new_home'))

        ###############################  Get All API Meta-Data   ########################################

        flash("Please wait, LiFE is fetching the data for you! You will receive a notification once the data has been fetched.")

        karya_new_api_metadata = karya_api_access.karya_new_get_all_karya_assignments(token_id, access_code, assignment_url)
        # r_j, hederr = karya_api_access.get_all_karya_assignments(
        #     verification_details, additional_task, project_type, access_code_task)
        

        # print("karya_new_api_metadata:", karya_new_api_metadata)

        # print("token_id_header : ", token_id_header)
        # logger.debug("token_id_json: %s\n token_id_header: %s", token_id_json, token_id_header)
        #############################################################################################
        language = accesscodedetails.find_one({"projectname": activeprojectname,
                                                "karyaaccesscode": access_code,
                                                 "additionalInfo.karya_version": "karya_main"},
                                              {'language': 1, '_id': 0})['language']
        logger.debug("language: %s", language)
        ################################ Get already fetched audio list and quesIDs   ########################################

        #getting already fetched audio list form the data base - "karyafetchedaudios": 1
        fetched_audio_list = karya_audio_management.karya_new_get_fetched_audio_list(
            accesscodedetails, access_code_of_speaker, activeprojectname)
        # print("898", fetched_audio_list) 
        logger.debug("fetched_audio_list: %s", fetched_audio_list)

        exclude_ids = []
        #condition ot append exclude_ids
        if (project_type == 'questionnaires'):
            exclude_ids = getquesidlistofsavedaudios.getquesidlistofsavedaudios(questionnaires,
                                                                                activeprojectname,
                                                                                language,
                                                                                exclude_ids)
        elif (project_type == 'transcriptions' and
                derive_from_project_type == 'questionnaires'):
            #for_worker_id=karyaspeakerid that is slected from fetch form page, empty_list to collect already existing =exclude_ids
            exclude_ids = audiodetails.getaudioidlistofsavedaudios(transcriptions,
                                                                   activeprojectname,
                                                                   language,
                                                                   exclude_ids,
                                                                   for_worker_id)
        elif (project_type == 'recordings' and
                derive_from_project_type == 'questionnaires'):
            exclude_ids = audiodetails.getaudioidlistofsavedaudios(recordings,
                                                                   activeprojectname,
                                                                   language,
                                                                   exclude_ids,
                                                                   for_worker_id)
            logger.debug("exclude_ids: %s", exclude_ids)

        #############################################################################################

        ##############################  File ID and sentence mapping   #################################
        '''worker ID'''

        if "completedRecordings" in access_code_task:
            print('recording')
            # Fetch metadata for completed recordings
            micro_task_ids, workerId_list, sentence_list, karya_audio_report, filename_list, fileID_list = karya_api_access.karya_new_get_assignment_metadata_recording(
                                                                                                                        accesscodedetails, activeprojectname,
                                                                                                                        access_code,
                                                                                                                        karya_new_api_metadata, for_worker_id
                                                                                                                    )           

            # Call to map fileID to sentence and workerId for completed recordings
            fileid_sentence_map = karya_api_access.karya_new_get_fileid_sentence_mapping(
                                                            fileID_list, workerId_list, sentence_list, karya_audio_report, filename_list
                                                        )
            
            # Log and process the fileID-sentence map
            logger.debug("fileid_sentence_map: %s", fileid_sentence_map)
            # print("fileid_sentence_map :", fileid_sentence_map)

            karya_audio_management.karya_new_getnsave_karya_recordings(
                                                                        mongo,
                                                                        projects, userprojects, projectowner, accesscodedetails,
                                                                        projectsform, questionnaires, transcriptions, recordings,
                                                                        activeprojectname, derivedFromProjectName, current_username,
                                                                        project_type, derive_from_project_type,
                                                                        fileid_sentence_map, fetched_audio_list, exclude_ids,
                                                                        language, file_download_header, access_code
                                                                        )
        else:
            print('verified')
            # Fetch metadata for verified assignments
            micro_task_ids, sepaker_access_code_list, sentence_list, karya_audio_report, filename_list, fileID_list = karya_api_access.karya_verified_get_assignment_metadata(
                accesscodedetails, activeprojectname,
                access_code_of_speaker,
                karya_new_api_metadata, for_worker_id,
            )

            # Call to map fileID to sentence and speaker access code for verified assignments
            fileid_sentence_map = karya_api_access.karya_new_get_fileid_sentence_mapping(
                fileID_list, sepaker_access_code_list, sentence_list, karya_audio_report, filename_list
            )
            # Log and process the fileID-sentence map
            logger.debug("fileid_sentence_map: %s", fileid_sentence_map)
            # print("fileid_sentence_map :", fileid_sentence_map)


            file_download_header = {"karya_worker_id_token" : token_id, 'access_code': access_code}
            # getnsave_karya_recordings -> get_insert_id -> getaudiofromprompttext
            karya_audio_management.karya_new_getnsave_karya_recordings_from_verified(
                mongo,
                projects, userprojects, projectowner, accesscodedetails,
                projectsform, questionnaires, transcriptions, recordings,
                activeprojectname, derivedFromProjectName, current_username,
                project_type, derive_from_project_type,
                fileid_sentence_map, fetched_audio_list, exclude_ids,
                language, file_download_header, access_code_of_speaker
            )
            flash("Karya Audio/s Successfully Fetched!")
            
        # print('\n','\n','\n','\n', '############################################################################################', '\n', '\n', '\n')
        # print(sepaker_access_code_list,'\n' ,sentence_list, '\n',karya_audio_report,'\n', filename_list, '\n',fileID_list)
        # print('\n','\n','\n','\n', '############################################################################################', '\n', '\n', '\n')
        
        # Get the file ID to sentence mapping using the get_fileid_sentence_mapping function from the api assignment 
        # The fileid_sentence_map is a dictionary that returns:
        # - If karya_audio_report is empty:
        #   A dictionary where each key is a tuple of (fileID, sentence), and each value is the corresponding worker ID.
        # - If karya_audio_report is not empty:
        #   A dictionary where each key is a tuple of (fileID, sentence), and each value is a tuple of (worker ID, audio report).

        
        # fileid_sentence_map = karya_api_access.karya_new_get_fileid_sentence_mapping(fileID_list, workerId_list, sentence_list, karya_audio_report, filename_list)

        # fileid_sentence_map = karya_api_access.karya_new_get_fileid_sentence_mapping(fileID_list, sepaker_access_code_list, sentence_list, karya_audio_report, filename_list)
        # logger.debug("fileid_sentence_map: %s", fileid_sentence_map)
        # # print("fileid_sentence_map", fileid_sentence_map)
        # print("fileid_sentence_map :", fileid_sentence_map)

        #Output fileid_sentence_map sample  from server
        # {('281474976758604', 'In which months / seasons are these vegetables grown?'): ('16784394',), ('281474976758605', 'What is the process of growing these vegetables?'): ('16784394',)}

        #this will find matched, unmatched and already fetched senteces and its file_id
        matched_unmathched_fetched_sentences = karya_audio_management.matched_unmatched_alreadyfetched_sentences(
            mongo,
            projects, userprojects, projectowner, accesscodedetails,
            projectsform, questionnaires, transcriptions, recordings,
            activeprojectname, derivedFromProjectName, current_username,
            project_type, derive_from_project_type,
            fileid_sentence_map, fetched_audio_list, exclude_ids,
            language, access_code
        )
        # print(matched_unmathched_fetched_sentences)  

        matched, unmatched, already_fetched = matched_unmathched_fetched_sentences
        # print("Matched Sentences:", matched)
        # print("Unmatched Sentences:", unmatched)
        # print("Already Fetched Sentences:", already_fetched)
        logger.debug("Matched Sentences: %s", matched)
        logger.debug("Unmatched Sentences: %s", unmatched)
        # logger.debug("Already Fetched Sentences: %s", already_fetched)


        #############################################################################################

        # file_download_header = {"karya_worker_id_token" : token_id, 'access_code': access_code}
        # # getnsave_karya_recordings -> get_insert_id -> getaudiofromprompttext
        # karya_audio_management.karya_new_getnsave_karya_recordings_from_verified(
        #     mongo,
        #     projects, userprojects, projectowner, accesscodedetails,
        #     projectsform, questionnaires, transcriptions, recordings,
        #     activeprojectname, derivedFromProjectName, current_username,
        #     project_type, derive_from_project_type,
        #     fileid_sentence_map, fetched_audio_list, exclude_ids,
        #     language, file_download_header, access_code
        # )
        # '''karya_audio_management.karya_new_getnsave_karya_recordings(
        #     mongo,
        #     projects, userprojects, projectowner, accesscodedetails,
        #     projectsform, questionnaires, transcriptions, recordings,
        #     activeprojectname, derivedFromProjectName, current_username,
        #     project_type, derive_from_project_type,
        #     fileid_sentence_map, fetched_audio_list, exclude_ids,
        #     language, file_download_header, access_code
        # )'''
        return redirect(url_for('karya_bp.karya_new_home'))

    return render_template("fetch_karya_audio.html")



@karya_bp.route('/karya_new_fetch_karya')
@login_required
def karya_new_fetch_karya():
    # print('starting...home')
    projects, userprojects, accesscodedetails = getdbcollections.getdbcollections(mongo,
                                                                                  'projects',
                                                                                  'userprojects',
                                                                                  'accesscodedetails')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                      current_username,
                                                      activeprojectname)

    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    projectType = getprojecttype.getprojecttype(projects, activeprojectname)
    print("projectType : ", projectType)
    # Find documents without "acodedeleteFlag" field
    query = {"acodedeleteFlag": {"$exists": False}}
    documents = accesscodedetails.find(query)

    # Update documents with "acodedeleteFlag: 0"
    for document in documents:
        document["acodedeleteFlag"] = 0
        accesscodedetails.update_one(
            {"_id": document["_id"], "projectname": activeprojectname}, {"$set": document})

    # finding acccesscode list on the basis of accesscodedetails "Task"
    access_code_list = access_code_management.get_access_code_list(
        accesscodedetails, activeprojectname, current_username)

    transcription_access_code_list = access_code_management.get_transcription_access_code_list(
        accesscodedetails, activeprojectname, current_username)

    verification_access_code_list = access_code_management.get_verification_access_code_list(
        accesscodedetails, activeprojectname, current_username)

    recording_access_code_list = access_code_management.get_recording_access_code_list(
        accesscodedetails, activeprojectname, current_username)

    # Add condition to check if the lists are empty
    # if not verification_access_code_list:
    #     verification_access_code_list = [""]
    # if not transcription_access_code_list:
    #     transcription_access_code_list = [""]

    # print(verification_access_code_list)

    # if projectType == "validation":
    karya_speaker_ids = karya_speaker_management.get_recording_karya_speaker_ids(
        accesscodedetails, activeprojectname, include_fetch=True)
    # else:
    #     karya_speaker_ids = karya_speaker_management.get_recording_karya_speaker_ids(
    # accesscodedetails, activeprojectname, include_fetch=True)

    if projectType == "transcriptions":
        dropdown_dict = { "newVerification": "Unverified Recordings",
            "completedVerification": "Verified Recordings"}
    elif projectType == "validation":
        dropdown_dict = { "newVerification": "Unverified Recordings",
            "completedVerification": "Verified Recordings"}
        
    elif projectType == "recordings":
        dropdown_dict = {
            "completedRecordings": "Completed Recordings",
            "newVerification": "Unverified Recordings",
            "completedVerification": "Verified Recordings"
        }
    elif projectType == "questionnaires":
                dropdown_dict = {
            "newVerification": "Unverified Recordings"
                }

    else:
        dropdown_dict = {
            "newVerification": "Unverified Recordings",
            "completedRecordings": "Verified Recordings"
        }

    dropdown_list = [{"value": key, "name": value}
                     for key, value in dropdown_dict.items()]

    return render_template("karya_new_fetch_karya.html",
                           projectName=activeprojectname,
                           shareinfo=shareinfo,
                           fetchaccesscodelist=access_code_list,
                           transcription_access_code_list=transcription_access_code_list,
                           verification_access_code_list=verification_access_code_list,
                           recording_access_code_list=recording_access_code_list,
                           karya_speaker_ids=karya_speaker_ids,
                           dropdown_list=dropdown_list)









