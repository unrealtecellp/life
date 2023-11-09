from app.controller import (
    life_logging
)

logger = life_logging.get_logger()

def get_ques_ids(projects_collection,
                    activeprojectname,
                    current_username,
                    active_ques_id,
                    ques_browse_action=0):
    '''Module to get speaker's ques_ids based on current user access(partial/full) to the speaker"'''
    ques_ids = []
    file_ques_ids = []
    try:
        if (ques_browse_action):
            questionnaire_ids = projects_collection.find_one({'projectname': activeprojectname},
                                                       {'_id': 0,
                                                        "questionnaireIdsDeleted": 1})
            # logger.debug("questionnaire_ids: %s", pformat(questionnaire_ids))
            if (questionnaire_ids and
                'questionnaireIdsDeleted' in questionnaire_ids and
                    active_ques_id in questionnaire_ids['questionnaireIdsDeleted']):
                ques_ids = questionnaire_ids['questionnaireIdsDeleted']
        else:
            questionnaire_ids = projects_collection.find_one({'projectname': activeprojectname},
                                                       {'_id': 0,
                                                        "questionnaireIds": 1})
            # logger.debug("questionnaire_ids: %s", pformat(questionnaire_ids))
            if (questionnaire_ids and
                'questionnaireIds' in questionnaire_ids and
                    active_ques_id in questionnaire_ids['questionnaireIds']):
                ques_ids = questionnaire_ids['questionnaireIds']
        if (len(ques_ids) != 0):
            return ques_ids

        # file_questionnaire_ids = projects_collection.find_one({'projectname': activeprojectname},
        #                                                 {'_id': 0,
        #                                                 'fileSpeakerIds.'+current_username: 1})
        # # logger.debug("file_questionnaire_ids: %s", pformat(file_questionnaire_ids))
        # if (file_questionnaire_ids and
        #     'fileSpeakerIds' in file_questionnaire_ids and
        #     current_username in file_questionnaire_ids['fileSpeakerIds'] and
        #         active_ques_id in file_questionnaire_ids['fileSpeakerIds'][current_username]):
        #     file_ques_ids = file_questionnaire_ids['fileSpeakerIds'][current_username][active_ques_id]
        # if (len(file_ques_ids) != 0):
        #     return file_ques_ids
    except:
        logger.exception("")

    return []
