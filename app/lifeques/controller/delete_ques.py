from app.controller import (
    life_logging
)
from app.lifeques.controller import (
    getnewquesid,
    updatelatestquesid
)
from pymongo import ReturnDocument

logger = life_logging.get_logger()

def delete_one_ques_doc(projects_collection,
                          questionnaires_collection,
                          project_name,
                          current_username,
                          active_ques_id,
                          ques_ids,
                          update_latest_active_ques_id=1):
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

        if (update_latest_active_ques_id):
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
