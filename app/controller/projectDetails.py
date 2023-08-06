"""Module to get the details of the project."""
from app.controller import (
    life_logging
)
logger = life_logging.get_logger()


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
                                activespeakerid,
                                lastActiveAudioId
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
        logger.debug('Transcription by data: %s', transcription_by_data)
        if transcription_by_data is not None and 'lastActiveUserTranscription' in transcription_by_data:
            data = transcription_by_data['lastActiveUserTranscription']
            if current_username in data:
                transcription_by = data[current_username]

        logger.debug("Transcription by(): %s", transcription_by)
    except:
        logger.exception("")
        # project_type = ''
    # logger.debug('project_type: %s', project_type)
    return transcription_by
