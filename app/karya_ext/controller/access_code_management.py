import pandas as pd
from datetime import datetime
from app.controller import (
    getprojecttype,
    life_logging
)

logger = life_logging.get_logger()


def get_access_code_list(accesscodedetails,
                         activeprojectname,
                         current_username):
    fetch_access_codes = accesscodedetails.find({'projectname': activeprojectname,
                                                 'fetchData': 1},
                                                {'_id': 0,
                                                 'karyaaccesscode': 1,
                                                 'assignedBy': 1,
                                                 'uploadedBy': 1})

    access_code_list = []

    for fetch_access_code in fetch_access_codes:
        # print ('Current access code', fetch_access_code)
        if (fetch_access_code['assignedBy'] != ''):
            if (fetch_access_code['assignedBy'] == current_username):
                access_code_list.append(fetch_access_code['karyaaccesscode'])
            else:
                if (current_username == fetch_access_code['uploadedBy']):
                    access_code_list.append(
                        fetch_access_code['karyaaccesscode'])

    return access_code_list


def get_transcription_access_code_list(accesscodedetails,
                                       activeprojectname,
                                       current_username):
    fetch_access_codes = accesscodedetails.find({'projectname': activeprojectname,
                                                 'fetchData': 1,
                                                 'task': 'SPEECH_TRANSCRIPTION'},
                                                {'_id': 0,
                                                 'karyaaccesscode': 1,
                                                 'assignedBy': 1,
                                                 'uploadedBy': 1})

    access_code_list = []

    for fetch_access_code in fetch_access_codes:
        # print ('Current access code', fetch_access_code)
        if (fetch_access_code['assignedBy'] != ''):
            if (fetch_access_code['assignedBy'] == current_username):
                access_code_list.append(fetch_access_code['karyaaccesscode'])
            else:
                if (current_username == fetch_access_code['uploadedBy']):
                    access_code_list.append(
                        fetch_access_code['karyaaccesscode'])

    return access_code_list


def get_verification_access_code_list(accesscodedetails,
                                      activeprojectname,
                                      current_username):
    fetch_access_codes = accesscodedetails.find({'projectname': activeprojectname,
                                                 'fetchData': 1,
                                                 'task': 'SPEECH_VERIFICATION'},
                                                {'_id': 0,
                                                 'karyaaccesscode': 1,
                                                 'assignedBy': 1,
                                                 'uploadedBy': 1})

    access_code_list = []

    for fetch_access_code in fetch_access_codes:
        # print ('Current access code', fetch_access_code)
        if (fetch_access_code['assignedBy'] != ''):
            if (fetch_access_code['assignedBy'] == current_username):
                access_code_list.append(fetch_access_code['karyaaccesscode'])
            else:
                if (current_username == fetch_access_code['uploadedBy']):
                    access_code_list.append(
                        fetch_access_code['karyaaccesscode'])

    return access_code_list


def get_recording_access_code_list(accesscodedetails,
                                   activeprojectname,
                                   current_username):
    fetch_access_codes = accesscodedetails.find({'projectname': activeprojectname,
                                                 'fetchData': 1,
                                                 'task': 'SPEECH_DATA_COLLECTION'},
                                                {'_id': 0,
                                                 'karyaaccesscode': 1,
                                                 'assignedBy': 1,
                                                 'uploadedBy': 1})

    access_code_list = []

    for fetch_access_code in fetch_access_codes:
        # print ('Current access code', fetch_access_code)
        if (fetch_access_code['assignedBy'] != ''):
            if (fetch_access_code['assignedBy'] == current_username):
                access_code_list.append(fetch_access_code['karyaaccesscode'])
            else:
                if (current_username == fetch_access_code['uploadedBy']):
                    access_code_list.append(
                        fetch_access_code['karyaaccesscode'])

    return access_code_list


def get_access_code_metadata_for_form(projects, projectsform, project_name, project_type, derived_from_project_type, derivedFromProjectName):
    # logger.debug("project_name: %s\
    #             \n\tproject_type: %s\
    #             \n\tderived_from_project_type: %s\
    #             \n\tderivedFromProjectName: %s",
    #             project_name,
    #             project_type,
    #             derived_from_project_type,
    #             derivedFromProjectName)
    try:
        if (project_type == 'questionnaires'):
            acesscodemetadata = get_access_code_metadata_questionnaire_for_form(
                projectsform, project_name)
        if (project_type == 'transcriptions'):
            acesscodemetadata = get_access_code_metadata_transcription_for_form(
                projects, projectsform, project_name, derived_from_project_type, derivedFromProjectName)
        if (project_type == 'recordings'):
            acesscodemetadata = get_access_code_metadata_transcription_for_form(
                projects, projectsform, project_name, derived_from_project_type, derivedFromProjectName)

        return acesscodemetadata
    except:
        logger.exception("")


# def get_access_code_metadata_transcription_for_form(projects, projectsform, project_name, derived_from_project_type, derivedFromProjectName):
#     langscript = []
#     projectform = projectsform.find_one({"projectname": project_name})
#     if projectform["Transcription"][1] is None:
#         langscript.append(projectform["Sentence Language"][0])
#     else:
#         langscript = projectform["Transcription"][1]

#     derivedFromProject = projects.find_one({"projectname": project_name},
#                                            {"_id": 0, "derivedFromProject": 1})
#     derivedFromProjectName = derivedFromProject['derivedFromProject'][0]
#     derived_from_project_type = getprojecttype.getprojecttype(
#         projects, derivedFromProjectName)

#     if (derived_from_project_type == "questionnaires"):
#         derivefromprojectform = projectsform.find_one(
#             {"projectname": derivedFromProjectName})

#         domain = derivefromprojectform["Domain"][1]
#         elicitation = derivefromprojectform["Elicitation Method"][1]

#     acesscodemetadata = {
#         "langscript": langscript,
#         "domain": domain,
#         "elicitation": elicitation
#     }

#     return acesscodemetadata
def get_access_code_metadata_transcription_for_form(projects, projectsform, project_name, derived_from_project_type, derivedFromProjectName):
    langscript = []
    domain = None
    elicitation = None

    projectform = projectsform.find_one({"projectname": project_name})

    if projectform:
        if projectform.get("Transcription") is None:
            langscript.append(projectform.get("Sentence Language"))
        else:
            langscript = projectform.get("Transcription")
    else:
        # Handle situation when projectform is None or key values are missing
        print("Project form not found or data missing")

    derivedFromProject = projects.find_one(
        {"projectname": project_name}, {"_id": 0, "derivedFromProject": 1})
    
    if derivedFromProject and "derivedFromProject" in derivedFromProject:
        derivedFromProjectName = derivedFromProject['derivedFromProject'][0]
        derived_from_project_type = getprojecttype.getprojecttype(
            projects, derivedFromProjectName)

        if (derived_from_project_type == "questionnaires"):
            derivefromprojectform = projectsform.find_one(
                {"projectname": derivedFromProjectName})

            if derivefromprojectform and "Domain" in derivefromprojectform and "Elicitation Method" in derivefromprojectform:
                domain = derivefromprojectform["Domain"][1]
                elicitation = derivefromprojectform["Elicitation Method"][1]
            else:
                # Handle missing keys or data in the derived project form
                print("Keys 'Domain' or 'Elicitation Method' missing in derived project form")
    else:
        # Handle missing or invalid derivedFromProject data
        print("Derived project data not found or invalid")

    access_code_metadata = {
        "langscript": langscript,
        "domain": domain,
        "elicitation": elicitation
    }

    return access_code_metadata




# def get_access_code_metadata_questionnaire_for_form(projectsform, project_name):
#     langscript = []
#     # domain, elictationmethod ,langscript-[1]
#     projectform = projectsform.find_one({"projectname": project_name})
#     langscripts = projectform["Prompt Type"][1]

#     for lang_script, lang_info in langscripts.items():
#         if ('Audio' in lang_info):
#             langscript.append(lang_script)

#     domain = projectform["Domain"][1]
#     elicitation = projectform["Elicitation Method"][1]
#     acesscodemetadata = {
#         "langscript": langscript,
#         "domain": domain,
#         "elicitation": elicitation
#     }

#     return acesscodemetadata

def get_access_code_metadata_questionnaire_for_form(projectsform, project_name):
    langscript = []
    # domain, elictationmethod ,langscript-[1]
    projectform = projectsform.find_one({"projectname": project_name})
    langscripts = projectform["Prompt Type"][1]
    for lang_script, lang_info in langscripts.items():
        if ('Audio' in lang_info):
            langscript.append(lang_script)

    domain = projectform["Domain"][1]
    elicitation = projectform["Elicitation Method"][1]
    acesscodemetadata = {
        "langscript": langscript,
        "domain": domain,
        "elicitation": elicitation
    }

    return acesscodemetadata



def get_upload_df(access_code_file):
    data = pd.read_csv(access_code_file)
    df = pd.DataFrame(data)

    df["id"] = df["id"].str[1:]
    df["access_code"] = df["access_code"].str[1:]
    df["phone_number"] = df["phone_number"].str[1:]
    return data


def upload_access_code_metadata_from_file(
    karyaaccesscodedetails,
    activeprojectname,
    current_username,
    task,
    language,
    domain,
    phase,
    elicitationmethod,
    fetch_data,
    data_df,
):

    return_obj = None  # Initialize return_obj outside the loop

    for index, item in data_df.iterrows():
        current_dt = str(datetime.now()).replace('.', ':')
        checkaccesscode = item["access_code"]
        accesscode_exist = karyaaccesscodedetails.find_one(
            {
                "projectname": activeprojectname,
                "karyaaccesscode": checkaccesscode
            }
        )
        if accesscode_exist is not None:
            continue

        insert_dict = {
            "karyaspeakerid": item["id"], "karyaaccesscode": item["access_code"], "lifespeakerid": "",
            "task": task, "language": language, "domain": domain,
            "phase": phase, "elicitationmethod": elicitationmethod, "projectname": activeprojectname,
            "uploadedBy": current_username,
            "assignedBy": "",
            "current": {"workerMetadata": {"name": "", "agegroup": "", "gender": "",
                                                       "educationlevel": "", "educationmediumupto12": "",
                                                       "educationmediumafter12": "", "speakerspeaklanguage": "",
                                                       "recordingplace": "", "typeofrecordingplace": "",
                                                       "activeAccessCode": ""}, "updatedBy": "", "current_date": current_dt},
            "previous": {},
            "fetchData": fetch_data,
            "karyafetchedaudios": [],
            "isActive": 0,
            "additionalInfo": {}
        }
        
        return_obj = karyaaccesscodedetails.insert_one(insert_dict)
        
    return return_obj

"""
finding a new access code = isActive:0, if there is any blank access code that doesn't have speaker details and isActive:0
it will find that access code randomly ... Note - this is not saving any data; this is just to find the new/fresh access code
which is uploaded from the karya extension - fetch/upload access code button
"""
def get_new_accesscode_speakerid(
    accesscodedetails,
    activeprojectname,
    accesscodefor,
    task,
    domain,
    elicitationmethod,
    language
):

    new_acode_spkrid = accesscodedetails.find_one({"isActive": 0, "projectname": activeprojectname,
                                                   "fetchData": accesscodefor, "task": task,
                                                   "domain": domain, "elicitationmethod": elicitationmethod,
                                                   "language": language}, {"karyaspeakerid": 1, "karyaaccesscode": 1, "_id": 0})

    try:
        if new_acode_spkrid is not None:
            speakerid = new_acode_spkrid['karyaspeakerid']
            acode = new_acode_spkrid['karyaaccesscode']
        else:
            speakerid = ''
            acode = ''
    except:
        speakerid = ''
        acode = ''

    return speakerid, acode

""" Adding speaker details for new/fresh access code {Manage access code -> Get new access code button } in accesscodedetails
 collection """
def add_access_code_metadata(
    accesscodedetails,
    activeprojectname,
    current_username,
    karyaspeakerid,
    karyaaccesscode,
    fname,
    fage,
    fgender,
    educlvl,
    moe12,
    moea12,
    sols,
    por,
    toc
):

    renameInFormDOB = fage.replace("-", "")
    renameInForm = fname.replace(" ", "")
    lowerRenameInForm = renameInForm.lower()
    renameDOB = "".join([lowerRenameInForm, renameInFormDOB])
    renameCode = "_".join([renameDOB, karyaspeakerid])

    update_data = {"lifespeakerid": renameCode,
                   "assignedBy":  current_username,
                   "current.updatedBy":  current_username,
                   "current.workerMetadata.name": fname,
                   "current.workerMetadata.agegroup": fage,
                   "current.workerMetadata.gender": fgender,
                   "current.workerMetadata.educationlevel": educlvl,
                   "current.workerMetadata.educationmediumupto12": moe12,
                   "current.workerMetadata.educationmediumafter12": moea12,
                   "current.workerMetadata.speakerspeaklanguage": sols,
                   "current.workerMetadata.recordingplace": por,
                   "current.workerMetadata.typeofrecordingplace": toc,
                   "isActive": 1}

    accesscodedetails.update_one({"karyaaccesscode": karyaaccesscode, "projectname": activeprojectname},
                                 {"$set": update_data}
                                 )


def update_access_code_metadata(
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
):

    update_data = {"current.updatedBy":  current_username,
                   "current.workerMetadata.gender": fgender,
                   "current.workerMetadata.educationlevel": educlvl,
                   "current.workerMetadata.educationmediumupto12": moe12,
                   "current.workerMetadata.educationmediumafter12": moea12,
                   "current.workerMetadata.speakerspeaklanguage": sols,
                   "current.workerMetadata.recordingplace": por,
                   "current.workerMetadata.typeofrecordingplace": toc,
                   "isActive": 1}
    previous_speakerdetails = accesscodedetails.find_one({"karyaaccesscode": accesscode, "projectname": activeprojectname},
                                                         {"current.workerMetadata": 1, "current.updatedBy": 1, "_id": 0, })

    date_of_modified = str(datetime.now()).replace(".", ":")

    update_old_data = {"previous."+date_of_modified+".workerMetadata.gender": previous_speakerdetails["current"]["workerMetadata"]["gender"],
                       "previous."+date_of_modified+".workerMetadata.educationlevel": previous_speakerdetails["current"]["workerMetadata"]["educationlevel"],
                       "previous."+date_of_modified+".workerMetadata.educationmediumupto12": previous_speakerdetails["current"]["workerMetadata"]["educationmediumupto12"],
                       "previous."+date_of_modified+".workerMetadata.educationmediumafter12": previous_speakerdetails["current"]["workerMetadata"]["educationmediumafter12"],
                       "previous."+date_of_modified+".workerMetadata.speakerspeaklanguage": previous_speakerdetails["current"]["workerMetadata"]["speakerspeaklanguage"],
                       "previous."+date_of_modified+".workerMetadata.recordingplace": previous_speakerdetails["current"]["workerMetadata"]["recordingplace"],
                       "previous."+date_of_modified+".updatedBy": previous_speakerdetails["current"]["updatedBy"]
                       }

    accesscodedetails.update_one({"karyaaccesscode": accesscode, "projectname": activeprojectname}, {
                                 "$set": update_old_data})  # Edit_old_user_info
    accesscodedetails.update_one({"karyaaccesscode": accesscode, "projectname": activeprojectname}, {
                                 "$set": update_data})  # new_user_info


def get_access_code_metadata(
        accesscode_info,
        activeprojectname,
        share_level,
        all_data_share_level,
        current_username
):
    karyaaccesscodedetails = ''
    if share_level >= all_data_share_level:
        karyaaccesscodedetails = accesscode_info.find({"isActive": 1, "projectname": activeprojectname},
                                                      {
            "karyaaccesscode": 1,
            "lifespeakerid": 1,
            "task": 1,
            "fetchData": 1,
            "assignedBy": 1,
            "current.workerMetadata.name": 1,
            "current.workerMetadata.agegroup": 1,
            "current.workerMetadata.gender": 1,
            "domain": 1,
            "elicitationmethod": 1,
            "_id": 0
        }
        )
    else:
        karyaaccesscodedetails = accesscode_info.find({"isActive": 1, "projectname": activeprojectname, "assignedBy": current_username},
                                                      {
            "karyaaccesscode": 1,
            "lifespeakerid": 1,
            "task": 1,
            "fetchData": 1,
            "assignedBy": 1,
            "current.workerMetadata.name": 1,
            "current.workerMetadata.agegroup": 1,
            "current.workerMetadata.gender": 1,
            "domain": 1,
            "elicitationmethod": 1,
            "_id": 0
        }
        )

    data_table = []
    fetch_data = {
        0: "Data Collection Using Karya",
        1: "Syncing Karya Recording with LiFE"
    }
    task = {
        "SPEECH_DATA_COLLECTION": "Recording",
        "SPEECH_VERIFICATION": "Verification of Recordings",
        "SPEECH_TRANSCRIPTION": "Transcription of Recordings"
    }
    for data in karyaaccesscodedetails:
        data['fetchData'] = fetch_data[data['fetchData']]
        data['task'] = task[data['task']]
        data_table.append(data)

    return data_table
