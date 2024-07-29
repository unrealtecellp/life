"""Module to get the details of the project."""
from app.controller import (
    life_logging,
    getuserprojectinfo,
    getprojectowner,
    getactiveprojectform
)
logger = life_logging.get_logger()


def get_public_projects_name(projects):
    public_projects = []

    try:
        all_public_projects = projects.find({"isPublic": 1, "projectdeleteFLAG": 0},
                                            {"_id": 0,
                                             "projectname": 1})
        if all_public_projects != None:
            for pub_proj in all_public_projects:
                public_projects.append(pub_proj["projectname"])
    except:
        logger.exception("")


def get_shared_with_users(projects,
                          activeprojectname):
    """_summary_

    Args:
        projects (_type_): _description_
    """
    project_shared_with = ''
    try:
        # logger.debug("projectname from getprojecttype(): %s", activeprojectname)
        project_shared_with = projects.find_one({"projectname": activeprojectname},
                                                {"_id": 0, "sharedwith": 1})
        # logger.debug('project_type: %s', project_type)
        if (project_shared_with):
            project_shared_with = project_shared_with["sharedwith"]
        else:
            project_shared_with = ''
    except:
        logger.exception("")
        # project_type = ''
    # logger.debug('project_type: %s', project_type)
    return project_shared_with


def get_active_transcription_by(projects,
                                activeprojectname,
                                current_username,
                                activespeakerid='',
                                lastActiveAudioId=''
                                ):
    # Preference set for each Audio file separately
    # transcription_by_key = 'lastActiveUserTranscription.' + \
    #     current_username+'.'+activespeakerid+'.' + lastActiveAudioId

    # Preference set for a specific user in a project - all audio files will show the transcription of the user selected
    transcription_by_key = 'lastActiveUserTranscription.' + current_username

    transcription_by = current_username
    try:
        # logger.debug("projectname from getprojecttype(): %s", activeprojectname)
        transcription_by_data = projects.find_one({"projectname": activeprojectname},
                                                  {"_id": 0, transcription_by_key: 1})
        # logger.debug('Transcription by data: %s', transcription_by_data)
        if transcription_by_data is not None and 'lastActiveUserTranscription' in transcription_by_data:
            data = transcription_by_data['lastActiveUserTranscription']
            if current_username in data:
                transcription_by = data[current_username]

        # logger.debug("Transcription by(): %s", transcription_by)
    except:
        logger.exception("")
        # project_type = ''
    # logger.debug('project_type: %s', project_type)
    return transcription_by


def get_audio_language_scripts(projectform,
                               activeprojectname):

    audio_info = projectform.find_one({"projectname": activeprojectname},
                                      {"_id": 0, "Audio Language": 1, "Transcription": 1})
    if not audio_info is None:
        audio_lang = audio_info.get("Audio Language")[1][0]
        scripts = audio_info.get("Transcription")[1]
    audio_info = {"language": audio_lang, "scripts": scripts}
    return audio_info


def get_all_audio_language_scripts(projectform,
                                   activeprojectname):

    audio_info = projectform.find_one({"projectname": activeprojectname},
                                      {"_id": 0, "Audio Language": 1, "Transcription": 1})
    if not audio_info is None:
        audio_lang = audio_info.get("Audio Language")[1]
        scripts = audio_info.get("Transcription")[1]
    audio_info = {"languages": audio_lang, "scripts": scripts}
    return audio_info


def get_translation_languages(projectform,
                              activeprojectname):
    trans_langs = []
    translation_info = projectform.find_one({"projectname": activeprojectname},
                                            {"_id": 0, "Translation": 1})
    if not translation_info is None:
        trans_langs = translation_info.get("Translation")[1]

    return trans_langs


def save_active_transcription_by(projects,
                                 activeprojectname,
                                 current_username,
                                 lastActiveUser):
    updateactiveuser = 'lastActiveUserTranscription.' + current_username

    projects.update_one({"projectname": activeprojectname},
                        {'$set': {updateactiveuser: lastActiveUser}})


def get_one_project_details(projects,
                            activeprojectname):
    projectdetails = projects.find_one({"projectname": activeprojectname},
                                       {"_id": 0,
                                        "projectOwner": 1,
                                        "sharedwith": 1,
                                        "projectdeleteFLAG": 1,
                                        "isPublic": 1,
                                        "projectType": 1,
                                        "aboutproject": 1,
                                        "derivedFromProject": 1,
                                        "projectDerivatives": 1
                                        })
    # print(projectowner)
    if (projectdetails == None):
        projectdetails = {
            "projectOwner": "",
            "sharedwith": [],
            "projectdeleteFLAG": 0,
            "isPublic": 0,
            "projectType": "",
            "aboutproject": "",
            "derivedFromProject": "",
            "projectDerivatives": []
        }

    return projectdetails


def get_one_public_project_details(projects,
                                   activeprojectname):
    projectdetails = projects.find_one({"projectname": activeprojectname, "projectdeleteFLAG": 0},
                                       {"_id": 0,
                                        "projectOwner": 1,
                                        "projectType": 1,
                                        "aboutproject": 1,
                                        "sharedwith": 1
                                        })
    # print(projectowner)
    if (projectdetails == None):
        projectdetails = {
            "projectOwner": "",
            "projectType": "",
            "aboutproject": "",
            "sharedwith": []
        }

    return projectdetails


def get_n_projects_info(projects,
                        userprojects,
                        projectsform,
                        current_username,
                        currentuserprojectsname,
                        n=-1
                        ):

    all_project_info = {}
    for currentproject in currentuserprojectsname:
        shareinfo = getuserprojectinfo.getuserprojectinfo(
            userprojects, current_username, currentproject)
        all_project_info[currentproject]['shareinfo'] = shareinfo

        projectdetails = get_one_project_details(
            projects, currentproject)
        all_project_info[currentproject]['details'] = projectdetails

        projectowner = projectdetails['projectOwner']
        projectform = getactiveprojectform.getactiveprojectform(
            projectsform, projectowner, currentproject)
        all_project_info[currentproject]['form'] = projectform

    return all_project_info


def get_n_public_projects_info(projects,
                               projectsform):
    public_projects = get_public_projects_name(projects)
    all_project_info = {}

    for currentproject in public_projects:
        projectdetails = get_one_project_details(
            projects, currentproject)
        all_project_info[currentproject]['details'] = projectdetails

        projectowner = projectdetails['projectOwner']
        projectform = getactiveprojectform.getactiveprojectform(
            projectsform, projectowner, currentproject)
        all_project_info[currentproject]['form'] = projectform

    return all_project_info
