from pprint import pformat
from pymongo import ReturnDocument
from app.controller import (
    life_logging
)

logger = life_logging.get_logger()


def delete_one_data(projects_collection,
                    data_collection,
                    project_name,
                    current_username,
                    active_source_id,
                    data_id):
    try:
        logger.debug("project_name: %s, data_id: %s", project_name, data_id)
        crawled_data_doc_id = data_collection.find_one_and_update({
            "projectname": project_name,
            "dataId": data_id
        },
            {"$set": {"datadeleteFLAG": 1}},
            projection={'_id': True},
            return_document=ReturnDocument.AFTER)['_id']
        logger.debug('DELETED crawled_data_doc_id: %s, %s',
                     crawled_data_doc_id, type(crawled_data_doc_id))

        projects_collection.update_one({"projectname": project_name},
                                       {"$pull": {"sourcedataIds."+active_source_id: data_id},
                                        "$addToSet": {"sourcedataIdsDeleted."+active_source_id: data_id}
                                        })
    except:
        logger.exception("")
        crawled_data_doc_id = False

    return crawled_data_doc_id


def get_data_delete_flag(data_collection,
                         project_name,
                         data_id):
    logger.debug("%s, %s, %s", data_collection,
                 project_name,
                 data_id)
    data_delete_flag = data_collection.find_one({"projectname": project_name,
                                                 "dataId": data_id},
                                                {"_id": 0,
                                                 "datadeleteFLAG": 1})["datadeleteFLAG"]

    return data_delete_flag


def revoke_deleted_data(projects_collection,
                        data_collection,
                        project_name,
                        active_source_id,
                        data_id):
    try:
        logger.debug("project_name: %s, data_id: %s", project_name, data_id)
        crawled_data_doc_id = data_collection.find_one_and_update({
            "projectname": project_name,
            "dataId": data_id
        },
            {"$set": {"datadeleteFLAG": 0}},
            projection={'_id': True},
            return_document=ReturnDocument.AFTER)['_id']
        logger.debug('REVOKED crawled_data_doc_id: %s, %s',
                     crawled_data_doc_id, type(crawled_data_doc_id))

        projects_collection.update_one({"projectname": project_name},
                                       {"$pull": {"sourcedataIdsDeleted."+active_source_id: data_id},
                                        "$addToSet": {"sourcedataIds."+active_source_id: data_id}
                                        })
    except:
        logger.exception("")
        crawled_data_doc_id = False

    return crawled_data_doc_id


def get_n_crawled_data(data_collection,
                       activeprojectname,
                       active_source_id,
                       data_type="text",
                       start_from=0,
                       number_of_crawled_data=10,
                       crawled_data_delete_flag=0):

    aggregate_output = data_collection.aggregate([
        {
            "$match": {
                "projectname": activeprojectname,
                "lifesourceid": active_source_id,
                "dataType": data_type,
                "datadeleteFLAG": crawled_data_delete_flag
            }
        },
        {
            "$sort": {
                "dataId": 1
            }
        },
        {
            "$project": {
                "_id": 0,
                "dataId": 1,
                "Data": {
                    "$switch": {
                        "branches": [
                            {
                                "case": {"$eq": [data_type, "text"]},
                                "then": "$Data"
                            },
                            {
                                "case": {"$eq": [data_type, "audio"]},
                                "then": "$audioFilename"
                            },
                            {
                                "case": {"$eq": [data_type, "video"]},
                                "then": "$videoFilename"
                            }
                        ],
                        "default": ""
                    }
                }
            }
        }
    ])
    # logger.debug("aggregate_output: %s", aggregate_output)
    aggregate_output_list = []
    for doc in aggregate_output:
        # logger.debug("aggregate_output: %s", pformat(doc))
        aggregate_output_list.append(doc)
    # logger.debug('aggregate_output_list: %s', pformat(aggregate_output_list))
    total_records = len(aggregate_output_list)
    logger.debug('total_records: %s', total_records)

    return (total_records,
            aggregate_output_list[start_from:number_of_crawled_data])
