from datetime import datetime
import re
from pprint import pformat
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
            "audioId": "",
            "audioFilename": "",
            "videoId": "",
            "videoFilename": "",
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

def generate_meta(sub_meta):
    meta_header = ['Video_ID', 'Channel_ID', 'Comment_ID',
                       'File_Name', 'Parent_ID', 'Date_Time_of_Retrieval']
    meta_dict = {}
    for i, info in enumerate(meta_header):
        meta_dict[info] = sub_meta[i]

    # logger.debug("meta_dict: %s", pformat(meta_dict))

    return meta_dict

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
            "prompt": "",
            "audioId": "",
            "audioFilename": "",
            "videoId": "",
            "videoFilename": ""
        }
        crawling_doc_id = crawling_collection.insert_one(crawled_data)
        return(crawling_doc_id, True)
    except:
        logger.exception("")
        return (None, False)

def save_youtube_crawled_data(projects_collection,
                                userprojects_collection,
                                sourcedetails_collection,
                                crawling_collection,
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
        async_comment = xml_to_json_data["async_comment"]
        for i, comment in enumerate(csv_data):
            text_id = 'C'+re.sub(r'[-: \.]', '', str(datetime.now()))
            text = comment[1]
            meta_dict = generate_meta(meta[i])
            additional_info = meta_dict
            text_meta_data = {
                "ID": comment[0]
            }
            if (i != 0):
                additional_info['async_comment'] = async_comment[i-1]

            save_crawled_data(crawling_collection,
                                project_owner,
                                active_project_name,
                                text_id,
                                text,
                                life_source_id,
                                additional_info,
                                text_meta_data)
    except:
        logger.exception("")