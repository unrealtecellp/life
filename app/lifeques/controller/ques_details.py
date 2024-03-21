from app.controller import (
    life_logging
)
from app.lifeques.controller import (
    getnewquesid,
    updatelatestquesid
)
from pymongo import ReturnDocument
from pprint import pformat

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


def get_n_ques(data_collection,
                 activeprojectname,
                 text_prompt_key,
                #  active_speaker_id,
                #  speaker_ques_ids,
                 start_from=0,
                 number_of_ques=10,
                 ques_delete_flag=0,
                 all_data=False):
    aggregate_output_list = []
    total_records = 0
    try:
        # logger.debug("speaker_ques_ids: %s", pformat(speaker_ques_ids))
        aggregate_output = data_collection.aggregate([
            {
                "$match": {
                    "projectname": activeprojectname,
                    # "speakerId": active_speaker_id,
                    "quesdeleteFLAG": ques_delete_flag
                }
            },
            {
                "$sort": {
                    "quesId": 1
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "quesId": 1,
                    # "quesFilename": 1
                    "Q_Id": 1,
                    "text": "$prompt.content."+text_prompt_key+".text"
                }
            }
        ])
        # logger.debug("aggregate_output: %s", aggregate_output)
        for doc in aggregate_output:
            # logger.debug("aggregate_output: %s", pformat(doc))
            # if (doc['quesId'] in speaker_ques_ids):
            #     doc['Audio File'] = ''
            prompt_text = doc["text"][list(doc["text"].keys())[0]]["textspan"][text_prompt_key.split('-')[-1]]
            # logger.debug(prompt_text)
            doc['prompt_text'] = prompt_text
            aggregate_output_list.append(doc)
        # logger.debug('aggregate_output_list: %s', pformat(aggregate_output_list))
        total_records = len(aggregate_output_list)
        # logger.debug('total_records QUES: %s', total_records)
        if (not all_data):
            aggregate_output_list = aggregate_output_list[start_from:number_of_ques]
    except:
        logger.exception("")

    return (total_records,
            aggregate_output_list)

def delete_one_ques_doc(projects_collection,
                          questionnaires_collection,
                          project_name,
                          current_username,
                          active_ques_id,
                          ques_ids,
                          update_latest_ques_id=1):
    try:
        # logger.debug("project_name: %s, active_ques_id: %s", project_name, active_ques_id)
        questionnaire_doc_id = questionnaires_collection.find_one_and_update({
            "projectname": project_name,
            "quesId": active_ques_id
        },
            {"$set": {"quesdeleteFLAG": 1}},
            projection={'_id': True},
            return_document=ReturnDocument.AFTER)['_id']
        # logger.debug('DELETED questionnaire_doc_id: %s, %s',
        #              questionnaire_doc_id, type(questionnaire_doc_id))

        if (update_latest_ques_id):
            latest_ques_id = getnewquesid.getnewquesid(projects_collection,
                                                        project_name,
                                                        active_ques_id,
                                                        'next')
            updatelatestquesid.updatelatestquesid(projects_collection,
                                                    project_name,
                                                    latest_ques_id,
                                                    current_username)

        projects_collection.update_one({"projectname": project_name},
                                       {"$pull": {"questionnaireIds": active_ques_id},
                                        "$addToSet": {"questionnaireIdsDeleted": active_ques_id}
                                        })
    except:
        logger.exception("")
        questionnaire_doc_id = False

    return questionnaire_doc_id

def revoke_deleted_ques(projects_collection,
                         questionnaires_collection,
                         project_name,
                        #  active_speaker_id,
                         ques_id,
                        #  speaker_ques_ids
                         ):
    try:
        # logger.debug("project_name: %s, ques_id: %s", project_name, ques_id)
        questionnaire_doc_id = questionnaires_collection.find_one_and_update({
            "projectname": project_name,
            "quesId": ques_id
        },
            {"$set": {"quesdeleteFLAG": 0}},
            projection={'_id': True},
            return_document=ReturnDocument.AFTER)['_id']
        # logger.debug('REVOKED questionnaire_doc_id: %s, %s',
        #              questionnaire_doc_id, type(questionnaire_doc_id))

        projects_collection.update_one({"projectname": project_name},
                                       {"$pull": {"questionnaireIdsDeleted": ques_id},
                                        "$addToSet": {"questionnaireIds": ques_id}
                                        })
    except:
        logger.exception("")
        questionnaire_doc_id = False

    return questionnaire_doc_id

def get_ques_delete_flag(questionnaires_collection,
                          project_name,
                          ques_id):
    # logger.debug("%s, %s, %s", questionnaires_collection,
    #              project_name,
    #              ques_id)
    ques_delete_flag = questionnaires_collection.find_one({"projectname": project_name,
                                                            "quesId": ques_id},
                                                           {"_id": 0,
                                                            "quesdeleteFLAG": 1})["quesdeleteFLAG"]

    return ques_delete_flag