import pandas as pd
import re
from datetime import datetime
from app.controller import (
    getprojecttype,
    life_logging, 
    speakerDetails,
)

from dateutil.relativedelta import relativedelta
from datetime import date

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


'''
def get_upload_df(access_code_file):
    data = pd.read_csv(access_code_file)
    data = data.fillna('')
    # df = pd.DataFrame(data)

    # df["id"] = df["id"].str[1:]
    # df["access_code"] = df["access_code"].str[1:]
    # df["phone_number"] = df["phone_number"].str[1:]
    df = pd.DataFrame(data)
    df["id"] = df["id"].str[1:]
    df["access_code"] = df["access_code"].str[1:]
    df["phone_number"] = df["phone_number"].str[1:]
    return data
'''
def get_upload_df(access_code_file):
    data = pd.read_csv(access_code_file)
    data = data.fillna('')

    # Function to remove leading alphabet if present for string columns
    #here id is worker_id
    def remove_leading_alpha(value):
        if isinstance(value, str) and value and value[0].isalpha():
            return value[1:]
        return value

    # Process 'id' column as string without decimal and leading alphabet
    if 'id' in data.columns:
        data['id'] = data['id'].astype(str).apply(remove_leading_alpha).str.split('.').str[0]
    
    # Process 'access_code' column
    if 'access_code' in data.columns:
        data['access_code'] = data['access_code'].apply(remove_leading_alpha).astype(str)
    
    # Process 'phone_number' column if it exists
    if 'phone_number' in data.columns:
        data['phone_number'] = data['phone_number'].apply(remove_leading_alpha).astype(str)

    return data

# Function to clean the access code
def clean_access_code(value, prefix=None, suffix=None):
    # Remove prefix if provided and present in the value
    if prefix and value.startswith(prefix):
        value = value[len(prefix):]
    # Remove suffix if provided and present in the value
    if suffix and value.endswith(suffix):
        value = value[:-len(suffix)]
    # Remove all non-numeric characters using regex
    value = re.sub(r'\D', '', value)  # \D matches any non-digit character
    return value


def process_access_code_csv_karya_new(access_code_file, prefix=None, suffix=None):
    # Read the CSV file into a pandas DataFrame and fill any missing values with an empty string
    data = pd.read_csv(access_code_file)
    data = data.fillna('')

    # Function to remove a specific prefix, suffix, or non-numeric characters
    def remove_affixes(value):
        if isinstance(value, str):
            # Remove prefix if provided and present in the value
            if prefix and value.startswith(prefix):
                value = value[len(prefix):]
            # Remove suffix if provided and present in the value
            if suffix and value.endswith(suffix):
                value = value[:-len(suffix)]
            # Remove all non-numeric characters using regex
            value = re.sub(r'\D', '', value)  # \D matches any non-digit character
        return value

    # Process 'access_code' column to remove prefix, suffix, and non-numeric characters
    if 'access_code' in data.columns:
        data['access_code'] = data['access_code'].apply(remove_affixes)

    return data



def process_access_code_csv_karya_new_update(access_code_file, prefix=None, suffix=None):
    # Read the CSV file into a pandas DataFrame and fill any missing values with an empty string
    data = pd.read_csv(access_code_file)
    data = data.fillna('')

    # Function to remove a specific prefix, suffix, or non-numeric characters
    def remove_affixes(value):
        if isinstance(value, str):
            # Remove prefix if provided and present in the value
            if prefix and value.startswith(prefix):
                value = value[len(prefix):]
            # Remove suffix if provided and present in the value
            if suffix and value.endswith(suffix):
                value = value[:-len(suffix)]
            # Remove all non-numeric characters using regex
            value = re.sub(r'\D', '', value)  # \D matches any non-digit character
        return value

    # Process 'access_code' column to remove prefix, suffix, and non-numeric characters
    if 'access_code' in data.columns:
        data['access_code'] = data['access_code'].apply(remove_affixes)

    # Return the required columns
    required_columns = ['access_code', 'avatar_id', 'worker_id', 'yob', 'gender', 'full_name', 'phone_number', 'income_source', 'education_level']
    return data[required_columns]


# Example usage:
# df = process_access_code_csv("path_to_your_file.csv", prefix="A-", suffix=None)
# print(df)


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




def upload_access_code_metadata_for_karya_new(
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
    accesscode_from_csv,
):

    return_obj = None  # Initialize return_obj outside the loop

    for index, item in accesscode_from_csv.iterrows():
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
            "karyaspeakerid": '', "karyaaccesscode": item["access_code"], "lifespeakerid": "",
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
            "additionalInfo": {"karya_version":karya_version}
        }
        
        return_obj = karyaaccesscodedetails.insert_one(insert_dict)
        
    return return_obj





def upload_access_code_metadata_for_karya_new_update(
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
):
    return_obj = None  # Initialize return_obj outside the loop

    # Loop through each row of the access_code DataFrame
    for index in range(len(access_code)):
        current_dt = str(datetime.now()).replace('.', ':')
        
        # Get access_code for the current row
        checkaccesscode = str(access_code.iloc[index])  # Convert to string
        
        # Check if the access_code already exists
        accesscode_exist = karyaaccesscodedetails.find_one(
            {
                "projectname": activeprojectname,
                "karyaaccesscode": checkaccesscode
            }
        )
        if accesscode_exist is not None:
            continue
        
        # Prepare data for insertion (convert all relevant fields to strings)
        worker_name = str(full_name.iloc[index])
        worker_age_group = int(yob.iloc[index])  # Convert yob to string
        worker_gender = str(gender.iloc[index])
        worker_id_value = str(worker_id.iloc[index])
        worker_phone = str(phone_number.iloc[index])
        worker_avatar_id = str(avatar_id.iloc[index])  # Convert avatar_id to string
        

        dob = get_life_age_group(worker_age_group)


        # Create life speaker ID using name and yob
        rename_in_form_dob = dob.replace("-", "")  # yob as string
        rename_in_form = worker_name.replace(" ", "").lower()
        lifespeakerid = f"{rename_in_form}{rename_in_form_dob}_{worker_id_value}"
        # print(type(lifespeakerid),"\n",type(rename_in_form_dob))

        # Build insert dictionary (ensure everything is converted to strings)
        insert_dict = {
            "karyaspeakerid": worker_id_value,  # worker_id is karyaspeakerid
            "karyaaccesscode": checkaccesscode, 
            "lifespeakerid": lifespeakerid,     # Generated lifespeakerid
            "task": task, 
            "language": language, 
            "domain": domain,
            "phase": phase, 
            "elicitationmethod": elicitationmethod, 
            "projectname": activeprojectname,
            "uploadedBy": current_username,
            "assignedBy": current_username,
            "current": {
                "updatedBy":current_username, 
                "workerMetadata": {
                    "name": worker_name,               # full_name
                    "agegroup": dob,    # yob (renamed as age_)
                    "gender": worker_gender,           # gender
                    "educationlevel": str(education_level.iloc[index]),  # Convert education_level to string
                    "educationMediumUpto12": "",       # You can fill these later if needed
                    "educationmediumafter12": "",
                    "speakerspeaklanguage": "",
                    "recordingplace": "",
                    "typeofrecordingplace": ""
                },
                
                "current_date": current_dt
            },
            "previous": {},
            "fetchData": fetch_data,
            "karyafetchedaudios": [],
            "isActive": 1,
            "additionalInfo": {
                "karya_version": str(karya_version),       # Convert karya_version to string
                "avatar_id": worker_avatar_id,             # avatar_id as string
                "phone_number": worker_phone               # phone_number as string
            }
        }
        

        # Insert the record into the database
        return_obj = karyaaccesscodedetails.insert_one(insert_dict)

        speakerdetails_meta_data ={
                                    "name": worker_name,                # full_name
                                    "ageGroup": dob,     # yob (renamed as age_)
                                    "gender": worker_gender,            # gender
                                    "educationLevel": "",  # Convert education_level to string str(education_level.iloc[index])
                                    "educationMediumUpto12-list": "",        # This can be filled later if needed
                                    "educationMediumAfter12-list": "",       # This can be filled later if needed
                                    "otherLanguages-list": "",         # Fill this if language details are available
                                    "placeOfRecording": "",               # Can be filled with the recording place
                                    "typeOfPlace": "",         # Can be filled with the type of recording place
                                    "current_date": current_dt,         # The current date
                                    "isActive": 1                    # Flag to indicate active status
                                    
                                }
        speakerdetails_additionalInfo = {
                                        "karya_version": str(karya_version),  # Convert karya_version to string
                                        "avatar_id": worker_avatar_id,        # Avatar ID as string
                                        "phone_number": worker_phone          # Phone number as string
                                    }


        #saving to speakerdetails:
        speakerDetails.karya_new_update_write_speaker_metadata_details(
            speakerdetails, current_username, activeprojectname,
            current_username, 'field', 'speed', insert_dict["lifespeakerid"], speakerdetails_meta_data,  speakerdetails_additionalInfo,  'bulk' )
        
    return return_obj




def get_life_age_group(yob):
    agroup = ''
    dob = date(int(yob), 1, 1)
    today = date.today()
    age = relativedelta(today, dob).years
    if age <= 30:
        agroup = '18-30'
    elif age > 30 and age <= 45:
        agroup = '30-45'
    elif age > 45 and age <= 60:
        agroup = '45-60'
    else:
        agroup = '60+'

    return agroup






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


def karya_new_get_new_accesscode_and_speakerid(
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
                                                   "language": language, "additionalInfo.karya_version":"karya_main"}, {"karyaspeakerid": 1, "karyaaccesscode": 1, "_id": 0})
   
   # "additionalInfo.karya_version":"karya_main" this might be creating issue 
    print(new_acode_spkrid)
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



def karya_new_get_assigned_accesscode_and_speakerid(
    accesscodedetails,
    activeprojectname,
    accesscodefor,
    task,
    domain,
    elicitationmethod,
    language
):
    # Retrieve all documents matching the criteria
    results = accesscodedetails.find(
        {"isActive": 1, "projectname": activeprojectname,
         "fetchData": accesscodefor, "task": task,
         "domain": domain, "elicitationmethod": elicitationmethod,
         "language": language, "additionalInfo.karya_version": "karya_main"},
        {"karyaspeakerid": 1, "karyaaccesscode": 1, "_id": 0}
    )

    # Initialize a dictionary to store the access codes and speaker IDs
    access_code_speakerid_map = {}

    # Process each document and populate the dictionary
    for result in results:
        speakerid = result.get('karyaspeakerid', '')
        acode = result.get('karyaaccesscode', '')
        
        if speakerid != '':
            access_code_speakerid_map[acode] = {
                'karyaspeakerid': speakerid
            }

    return access_code_speakerid_map


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

def karya_new_add_access_code_metadata(
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

    # renameInFormDOB = fage.replace("-", "")
    # renameInForm = fname.replace(" ", "")
    # lowerRenameInForm = renameInForm.lower()
    # renameDOB = "".join([lowerRenameInForm, renameInFormDOB])
    # renameCode = "_".join([renameDOB, karyaspeakerid])

    update_data = {"lifespeakerid": "",
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

    accesscodedetails.update_one({"karyaaccesscode": karyaaccesscode, "projectname": activeprojectname, "additionalInfo.karya_version":"karya_main"},
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
    


def karya_new_update_access_code_metadata(
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
    previous_speakerdetails = accesscodedetails.find_one({"karyaaccesscode": accesscode, "projectname": activeprojectname, 
                                                          "additionalInfo.karya_version":"karya_main"},
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

    accesscodedetails.update_one({"karyaaccesscode": accesscode, "projectname": activeprojectname, 
                                  "additionalInfo.karya_version":"karya_main"}, {
                                 "$set": update_old_data})  # Edit_old_user_info
    accesscodedetails.update_one({"karyaaccesscode": accesscode, "projectname": activeprojectname, "additionalInfo.karya_version":"karya_main"}, {
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


def karya_new_get_access_code_metadata(
        accesscode_info,
        activeprojectname,
        share_level,
        all_data_share_level,
        current_username
):
    karyaaccesscodedetails = ''
    if share_level >= all_data_share_level:
        karyaaccesscodedetails = accesscode_info.find({"isActive": 1, "projectname": activeprojectname, "additionalInfo.karya_version": "karya_main"},
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
        karyaaccesscodedetails = accesscode_info.find({"isActive": 1, "projectname": activeprojectname, "assignedBy": current_username, "additionalInfo.karya_version": "karya_main"},
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

