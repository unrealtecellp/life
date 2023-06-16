from datetime import datetime
from app.controller import (
    life_logging
)
from app.lifedata.controller import (
    data_project_info
)

logger = life_logging.get_logger()

def add_new_source_info(projects_collection,
                        userprojects_collection,
                        sourcedetails_collection,
                        project_owner,
                        active_project_name,
                        life_source_id,
                        current_username,
                        data_source,
                        data_sub_source,
                        source_metadata):
    try:
        source_info = {
            "username": project_owner,
            "projectname": active_project_name,
            "lifesourceid": life_source_id,
            "createdBy": current_username,
            "dataSource": data_source,
            "dataSubSource": data_sub_source,
            "current": {
                "updatedBy": current_username,
                "sourceMetadata": source_metadata,
                "current_date": str(datetime.now())
            },
            "isActive": 1
        }
        sourcedetails_doc_id = sourcedetails_collection.insert_one(source_info)
        return (sourcedetails_doc_id, True)
    except:
        logger.exception("")
        return (None, False)

def add_new_source_id(projects_collection,
                      active_project_name,
                      current_username,
                      life_source_id):
    try:
        projects_collection.update_one({"projectname": active_project_name},
                                       {
                                           "$addToSet": {
                                               "sourceIds."+current_username: life_source_id
                                           }
                                       })
        return True
    except:
        logger.exception("")
        return False

def update_active_source_id(userprojects_collection,
                            active_project_name,
                            project_owner,
                            current_username,
                            life_source_id):
    try:
        if(current_username == project_owner):
            key = 'myproject'
        else:
            key = 'projectsharedwithme'
        userprojects_collection.update_one({"username": current_username},
                                       {
                                           "$set": {
                                               key+'.'+active_project_name+".activesourceId": life_source_id
                                           }
                                       })
        return True
    except:
        logger.exception("")
        return False

def save_crawled_data(crawling_collection,
                      project_owner,
                      active_project_name,
                      text_id,
                      text,
                      life_source_id,
                      additional_info,
                      text_meta_data):
    try:
        crawled_data = {
            "username": project_owner,
            "projectname": active_project_name,
            "textId": text_id,
            "Text": text,
            "lastUpdatedBy": "",
            "lifesourceid": life_source_id,
            "textdeleteFLAG": 0,
            "textverifiedFLAG": 0,
            "additionalInfo": additional_info,
            "textMetadata": text_meta_data,
            "prompt": ""
        }
        crawling_doc_id = crawling_collection.insert_one(crawled_data)
        return(crawling_doc_id, True)
    except:
        logger.exception("")
        return (None, False)

def save_youtube_crawled_data(projects_collection,
                                userprojects_collection,
                                sourcedetails_collection,
                                project_owner,
                                current_username,
                                active_project_name,
                                xml_to_json,
                                csv_data,
                                meta,
                                video_id):
    try:
        life_source_id = video_id
        data_source = data_project_info.get_data_source(projects_collection,
                                                        active_project_name)
        data_sub_source = data_project_info.get_data_sub_source(projects_collection,
                                                                active_project_name)
        xml_to_json_data = xml_to_json["co3h"]["asynchronous"]["youtube_video"]
        source_metadata = {
            "async_info": xml_to_json_data["async_info"],
            "main_content": xml_to_json_data["main_content"]
        }
        sourcedetails_doc_id, added_new_source = add_new_source_info(projects_collection,
                                                                        userprojects_collection,
                                                                        sourcedetails_collection,
                                                                        project_owner,
                                                                        active_project_name,
                                                                        life_source_id,
                                                                        current_username,
                                                                        data_source,
                                                                        data_sub_source,
                                                                        source_metadata)
        if(added_new_source):
            add_new_source_id(projects_collection,
                                active_project_name,
                                current_username,
                                life_source_id)
            
            update_active_source_id(userprojects_collection,
                                    active_project_name,
                                    project_owner,
                                    current_username,
                                    life_source_id)
        for i, comment in enumerate(csv_data):
            

    except:
        logger.exception("")