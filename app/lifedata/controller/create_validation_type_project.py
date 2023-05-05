"""Module to create validation type project new or derived"""

from app import mongo
from app.controller import (
    getprojecttype,
    getdbcollections,
    getprojectowner,
    life_logging
)
logger = life_logging.get_logger()

def create_validation_type_project(projects_collection,
                                   validation_collection,
                                    project_name,
                                    derive_from_project_name,
                                    current_username,
                                    *args,
                                    **kwargs):
    try:
        derive_from_project_type = getprojecttype.getprojecttype(projects_collection, project_name)
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
        recordings, = getdbcollections(mongo, 'recordings')
        validation_data = []
        for recording in recordings.find({"projectname": derive_from_project_name}):
            if (recording['speakerId'] != ''):
                project_owner = getprojectowner.getprojectowner(projects_collection, project_name)
                recording['username'] = project_owner
                recording['projectname'] = project_name
                recording['updatedBy'] = current_username
                recording['derivedfromprojectdetails']['derivedfromprojectname'] = derive_from_project_name
                recording['derivedfromprojectdetails']['derivedfromprojectId'] = recording['_id']
                validation_data.append(recording)
        validation_collection.insertMany(validation_data)
    except:
        logger.exception("")
