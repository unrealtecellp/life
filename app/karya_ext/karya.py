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
    print("Access Code:", asycaccesscode)
    print(acodedetails)

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
    print("Access Code:", asycaccesscode)
    print(acodedetails)

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
    print("Access Code:", accessCode)
    print("Speaker ID:", speakerID)
    print("elicitation :", elicitation)
    print("domain :", domain)
    print("phase :", phase)
    print("languagescript :", languagescript)

    current_speakerdetails = accesscodedetails.find_one({"karyaaccesscode": accessCode, "projectname": activeprojectname, "isActive": 0},
                                                        {"current.workerMetadata.name": 1, "current.workerMetadata.agegroup": 1, "_id": 0, })

    current_speakerdetails_name = current_speakerdetails['current']['workerMetadata']['name']
    current_speakerdetails_age = current_speakerdetails['current']['workerMetadata']['agegroup']
    print("current_speakerdetails_name: ", current_speakerdetails_name)
    print("current_speakerdetails_age: ", current_speakerdetails_age)

    update_data = {"current.updatedBy":  current_username,
                   "karyaaccesscode": accessCode,
                   "karyaspeakerid": speakerID,
                   "fetchData": fetchData,
                   "elicitationmethod": elicitation,
                   "phase": phase,
                   "domain": domain,
                   "language": languagescript,
                   "task": task
                   }

    date_of_modified = str(datetime.now()).replace(".", ":")

    accesscodedetails.update_one({"karyaaccesscode": accessCode, "projectname": activeprojectname, "isActive": 0}, {
                                 "$set": update_data})  # new_user_info
    print("if condtion working inactive access code")

    # Return a response indicating the success or failure of the update operation
    return jsonify({'status': 'success', 'message': 'Table data updated successfully'})


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
    print("Access Code:", accessCode)
    # print("Speaker ID:", speakerID)
    # print("Status:", status)
    print("Fetch Data:", fetchData)
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
    print('curent user : ', current_username)
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

        print("OTP : ", otp)
        print("project_type: ", project_type)
        # print("additional_task : ", additional_task)
        print("access_code_task : ", access_code_task)
        print("access_code : ", access_code)
        print("for_worker_id : ", for_worker_id)
        print("phone_number : ", phone_number)
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



                  

        # if project_type == 'validation' and access_code_task == "newVerification":
        #     assignment_url = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=new&from=2021-05-11T07:23:40.654Z'
        #     print("the project type is ", project_type,
        #           "and", access_code_task, "and", " New url")

        # elif project_type == 'validation' and access_code_task == "completedVerification":
        #     assignment_url = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=verified&includemt=true&from=2021-05-11T07:23:40.654Z'
        #     print("the project type is ", project_type, "and",
        #           access_code_task, "and", "verified url")

        # elif project_type == 'transcriptions' and access_code_task == "newTranscription":
        #     assignment_url = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=new&from=2021-05-11T07:23:40.654Z'
        #     print("the project type is ", project_type,
        #           "and", access_code_task, "and", "New url")

        # elif project_type == 'transcriptions' and access_code_task == "completedVerification":
        #     assignment_url = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=verified&includemt=true&from=2021-05-11T07:23:40.654Z'
        #     print("the project type is ", project_type, "and",
        #           access_code_task, "and", "verified url")

        # elif project_type == 'transcriptions' and access_code_task == "completedRecordings":
        #     assignment_url = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=verified&includemt=true&from=2021-05-11T07:23:40.654Z'
        #     print("the project type is ", project_type, "and",
        #           access_code_task, "and", "verified url")

        # elif project_type == 'recordings' and access_code_task == "completedRecordings":
        #     assignment_url = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=verified&includemt=true&from=2021-05-11T07:23:40.654Z'
        #     print("the project type is ", project_type, "and",
        #           access_code_task, "and", "verified url")

        else:
            flash(
                "This action is not allowed in this project. Please fetch the recording in a new/other project.")
            return redirect(url_for('karya_bp.home_insert'))

        ###############################   Get Assignments    ########################################

        r_j, hederr = karya_api_access.get_all_karya_assignments(
            verification_details, assignment_url)
        # r_j, hederr = karya_api_access.get_all_karya_assignments(
        #     verification_details, additional_task, project_type, access_code_task)

        print("line 790")

        logger.debug("r_j: %s\nhederr: %s", r_j, hederr)
        #############################################################################################
        language = accesscodedetails.find_one({"projectname": activeprojectname, "karyaaccesscode": access_code},
                                              {'language': 1, '_id': 0})['language']
        logger.debug("language: %s", language)
        ################################ Get already fetched audio list and quesIDs   ########################################
        fetched_audio_list = karya_audio_management.get_fetched_audio_list(
            accesscodedetails, access_code, activeprojectname)
        print("898", fetched_audio_list)
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

        fileid_sentence_map = karya_api_access.get_fileid_sentence_mapping(
            fileID_list, workerId_list, sentence_list, karya_audio_report
        )
        logger.debug("fileid_sentence_map: %s", fileid_sentence_map)
        #############################################################################################

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
        projects, userprojects, transcriptions, accesscodedetails = getdbcollections.getdbcollections(
            mongo, 'projects', 'userprojects', 'transcriptions', 'accesscodedetails')
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
            if "karyaInfo" in transcriptions_data and "karyaSpeakerId" in transcriptions_data["karyaInfo"] and "karyaFetchedAudioId" in transcriptions_data["karyaInfo"]:
                speaker_id = transcriptions_data["speakerId"]
                if speaker_id not in data:
                    data[speaker_id] = []
                data[speaker_id].append(transcriptions_data)

        for speaker_id, transcriptions_list in data.items():
            for transcription in transcriptions_list:
                karya_fetched_audio_id = transcription["karyaInfo"]["karyaFetchedAudioId"]
                if karya_fetched_audio_id in accesscodedetails.distinct("karyafetchedaudios"):
                    access_code = accesscodedetails.find_one(
                        {"karyafetchedaudios": karya_fetched_audio_id})["karyaaccesscode"]
                    transcription["accesscode"] = access_code
                    print("access_code : ", access_code)
        print(100*"#", "\n", data)

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

        print("accesscodedetails_result_find : ", "karya audio ids: ",
              accesscodedetails_result_find['karyafetchedaudios'])
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
                                           speaker_id,
                                           audio_id,
                                           update_latest_audio_id=1)

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
