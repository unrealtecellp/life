"""Module to create validation type project new or derived"""

from app import mongo
from app.controller import (
    getprojecttype,
    getdbcollections,
    getprojectowner,
    life_logging
)
from pprint import pformat
logger = life_logging.get_logger()

def create_validation_type_project(projects_collection,
                                   validation_collection,
                                    project_name,
                                    derive_from_project_name,
                                    current_username,
                                    *args,
                                    **kwargs):
    try:
        derive_from_project_type = getprojecttype.getprojecttype(projects_collection, derive_from_project_name)
        # logger.debug('derive_from_project_type: %s', derive_from_project_type)
        if (derive_from_project_type == 'recordings'):
            derive_from_recordings(projects_collection,
                                    validation_collection,
                                    project_name,
                                    derive_from_project_name,
                                    current_username)
    except:
        logger.exception("")

def derive_from_recordings(projects_collection,
                            validation_collection,
                            project_name,
                            derive_from_project_name,
                            current_username,
                            *args,
                            **kwargs):
    try:
        recordings, = getdbcollections.getdbcollections(mongo, 'recordings')
        validation_data = []
        speaker_ids = set()
        speaker_last_active_id = {}
        for recording in recordings.find({"projectname": derive_from_project_name}):
            temp_speaker_id = recording['speakerId']
            if (temp_speaker_id != ''):
                # logger.debug('recording: %s', pformat(recording))
                speaker_ids.add(temp_speaker_id)
                if temp_speaker_id not in speaker_last_active_id:
                    speaker_last_active_id[temp_speaker_id] = recording['audioId']
                project_owner = getprojectowner.getprojectowner(projects_collection, project_name)
                recording['username'] = project_owner
                recording['projectname'] = project_name
                recording['updatedBy'] = current_username
                recording['derivedfromprojectdetails']['derivedfromprojectname'] = derive_from_project_name
                recording['derivedfromprojectdetails']['derivedfromprojectId'] = recording['_id']
                del recording["_id"]
                validation_data.append(recording)
        # logger.debug('validation_data: %s', pformat(validation_data))
        validation_collection.insert_many(validation_data)
        logger.debug("speaker_ids: %s\nspeaker_last_active_id: %s", speaker_ids, pformat(speaker_last_active_id))
        for speaker_id in speaker_ids:
            projects_collection.update_one({"projectname": project_name},
                                        {
                                            "$addToSet": {
                                                "speakerIds."+current_username: speaker_id,
                                            },
                                            "$set": {
                                                "lastActiveId."+current_username+'.'+speaker_id+'.audioId': speaker_last_active_id[speaker_id]
                                            }
                                        }
                                        )
    except:
        logger.exception("")
