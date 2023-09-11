"""Module to get the data for the validation depending on the derived project."""

from app.controller import (
    getprojecttype,
    getuserprojectinfo,
    getcommentstats,
    life_logging
)
logger = life_logging.get_logger()

def get_recordings_validation_data(projects_collection,
                                    userprojects_collection,
                                    validation_collection,
                                    tagsets_collection,
                                    current_username,
                                    activeprojectname):
    project_details = {}
    try:
        active_speaker_id = getuserprojectinfo.getuserprojectinfo(userprojects_collection,
                                                                    current_username,
                                                                    activeprojectname)['activespeakerId']
        speaker_ids = projects_collection.find_one({"projectname": activeprojectname},
                                                {"_id": 0, "speakerIds."+current_username: 1}
                                                )["speakerIds"][current_username]
        project_details['activeSpeakerId'] = active_speaker_id
        project_details['speakerIds'] = speaker_ids
        total_comments, annotated_comments, remaining_comments = getcommentstats.getcommentstatsnew(projects_collection,
                                                                                                    validation_collection,
                                                                                                    activeprojectname,
                                                                                                    active_speaker_id,
                                                                                                    'audioverifiedFLAG',
                                                                                                    'audio')
        project_details['totalComments'] = total_comments
        project_details["annotatedComments"] = annotated_comments
        project_details["remainingComments"]  = remaining_comments

        tag_set_id = projects_collection.find_one({"projectname": activeprojectname},
                                                    {"_id": 0, "tagsetId": 1})["tagsetId"]
        tag_set = tagsets_collection.find_one({"_id": tag_set_id})
        project_details['tagSet'] = tag_set['tagSet']
        project_details['tagSetMetaData'] = tag_set['tagSetMetaData']
    except:
        logger.exception("")

    return project_details

def get_validation_data(projects_collection,
                        userprojects_collection,
                        validation_collection,
                        tagsets_collection,
                        current_username,
                        activeprojectname):
    project_details = {}
    try:
        derived_from_project_type, derived_from_project_name = getprojecttype.getderivedfromprojectdetails(projects_collection, activeprojectname)
        if (derived_from_project_type == 'recordings'):
            project_details = get_recordings_validation_data(projects_collection,
                                                            userprojects_collection,
                                                            validation_collection,
                                                            tagsets_collection,
                                                            current_username,
                                                            activeprojectname)
    except:
        logger.exception("")

    return project_details