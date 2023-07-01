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
                        source_metadata,
                        search_keywords,
                        data_type,
                        audio_id="",
                        audio_filename="",
                        video_id="",
                        video_filename="",
                        audio_doc_id="",
                        video_doc_id="",
                        crawling_status=1):
    try:
        life_audio_id = ''
        if audio_filename != '':
            life_audio_id = audio_filename.split('_')[0]

        life_video_id = ''
        if video_filename != '':
            life_video_id = video_filename.split('_')[0]

        source_info = {
            "username": project_owner,
            "projectname": active_project_name,
            "lifesourceid": life_source_id,
            "createdBy": current_username,
            "dataSource": data_source,
            "dataSubSource": data_sub_source,
            "dataType": data_type,
            "current": {
                "updatedBy": current_username,
                "searchKeywords": search_keywords,
                "sourceTags": search_keywords,
                "sourceMetadata": source_metadata,
                "current_date": str(datetime.now())
            },
            "audioFsId": audio_id,
            "audioId": life_audio_id,
            "audioFilename": audio_filename,
            "audioDocumentId": audio_doc_id,
            "videoFsid": video_id,
            "videoId": life_video_id,
            "videoFilename": video_filename,
            "videoDocumentId": video_doc_id,
            "isActive": 1,
            "commentCrawlingStatus": crawling_status,
            "sourcedeleteFLAG": 0
        }
        logger.debug("Source to be written %s", source_info)
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

        logger.debug(
            "Adding new source ID %s Current active project name during save %s", life_source_id, active_project_name)
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


def add_new_source_data_id(projects_collection,
                           active_project_name,
                           life_source_id,
                           data_id):
    try:

        logger.debug(
            "Adding new source ID %s Current active project name during save %s", life_source_id, active_project_name)
        projects_collection.update_one({"projectname": active_project_name},
                                       {
                                           "$addToSet": {
                                               "sourcedataIds."+life_source_id: data_id
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
        if (current_username == project_owner):
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
        if (info == 'File_Name'):
            continue
        meta_dict[info] = sub_meta[i]

    # logger.debug("meta_dict: %s", pformat(meta_dict))

    return meta_dict


def save_crawled_data(crawling_collection,
                      project_owner,
                      active_project_name,
                      current_username,
                      data_id,
                      data,
                      life_source_id,
                      additional_info,
                      data_meta_data,
                      audio_id="",
                      audio_filename="",
                      video_id="",
                      video_filename="",
                      audio_doc_id="",
                      video_doc_id="",
                      prompt="",
                      data_type='text'):
    try:
        life_audio_id = ''
        if audio_filename != '':
            life_audio_id = audio_filename.split('_')[0]

        life_video_id = ''
        if video_filename != '':
            life_video_id = video_filename.split('_')[0]

        crawled_data = {
            "username": project_owner,
            "projectname": active_project_name,
            "dataId": data_id,
            "dataType": data_type,
            "Data": data,
            "createdBy": current_username,
            "lastUpdatedBy": current_username,
            "lifesourceid": life_source_id,
            "datadeleteFLAG": 0,
            "dataverifiedFLAG": 0,
            "additionalInfo": additional_info,
            "dataMetadata": data_meta_data,
            "prompt": prompt,
            "audioFsId": audio_id,
            "audioId": life_audio_id,
            "audioFilename": audio_filename,
            "audioDocumentId": audio_doc_id,
            "videoFsid": video_id,
            "videoId": life_video_id,
            "videoFilename": video_filename,
            "videoDocumentId": video_doc_id,
        }
        logger.debug("Crawled data to be written %s", crawled_data)
        crawling_doc_id = crawling_collection.insert_one(crawled_data)
        return (crawling_doc_id, True)
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
                              youtube_video_id,
                              search_keywords,
                              fs_audio_id="",
                              life_audio_filename="",
                              fs_video_id="",
                              life_video_filename="",
                              life_audio_doc_id="",
                              life_video_doc_id="",
                              crawling_status=1
                              ):
    try:
        dataType = []
        life_source_id = youtube_video_id
        data_source = data_project_info.get_data_source(projects_collection,
                                                        active_project_name)
        data_sub_source = data_project_info.get_data_sub_source(projects_collection,
                                                                active_project_name)
        xml_to_json_data = xml_to_json["co3h"]["asynchronous"]["youtube_video"]
        async_info = xml_to_json_data["async_info"]
        async_info['video_link'] = xml_to_json_data["main_content"]['original_script']['#text']
        source_metadata = async_info

        if "async_comment" in xml_to_json_data:
            dataType.append('text')

        if life_audio_doc_id != "":
            dataType.append('audio')

        if life_video_doc_id != "":
            dataType.append('video')

        sourcedetails_doc_id, added_new_source = add_new_source_info(projects_collection,
                                                                     userprojects_collection,
                                                                     sourcedetails_collection,
                                                                     project_owner,
                                                                     active_project_name,
                                                                     life_source_id,
                                                                     current_username,
                                                                     data_source,
                                                                     data_sub_source,
                                                                     source_metadata,
                                                                     search_keywords,
                                                                     data_type=dataType,
                                                                     audio_id=fs_audio_id,
                                                                     audio_filename=life_audio_filename,
                                                                     video_id=fs_video_id,
                                                                     video_filename=life_video_filename,
                                                                     audio_doc_id=life_audio_doc_id,
                                                                     video_doc_id=life_video_doc_id,
                                                                     crawling_status=crawling_status)
        if (added_new_source):
            logger.debug(
                "Current source id %s active project name before save %s", life_source_id, active_project_name)
            add_new_source_id(projects_collection,
                              active_project_name,
                              current_username,
                              life_source_id)

            update_active_source_id(userprojects_collection,
                                    active_project_name,
                                    project_owner,
                                    current_username,
                                    life_source_id)

        if "async_comment" in xml_to_json_data:
            additional_info = {}
            async_comments = xml_to_json_data["async_comment"]
            logger.debug('async_comments TYPE: %s', type(async_comments))
            if (isinstance(async_comments, dict)):
                async_comments = [async_comments]
            for i, comment in enumerate(csv_data):
                text_id = 'C'+re.sub(r'[-: \.]', '', str(datetime.now()))
                text = comment[1]
                meta_dict = generate_meta(meta[i])
                additional_info = meta_dict
                text_meta_data = {}
                if (i == 0):
                    text_meta_data["ID"] = youtube_video_id+'.0'
                elif (i != 0):
                    async_comment = async_comments[i-1]
                    async_comment['comment_number'] = async_comment['@id']
                    del async_comment['@id']
                    additional_info.update(async_comment)
                    text_meta_data["ID"] = youtube_video_id+'.' + \
                        async_comment['comment_number']
                # additional_info['searchKeywords'] = search_keywords
                save_crawled_data(crawling_collection,
                                  project_owner,
                                  active_project_name,
                                  current_username,
                                  text_id,
                                  text,
                                  life_source_id,
                                  additional_info,
                                  text_meta_data,
                                  audio_id=fs_audio_id,
                                  audio_filename=life_audio_filename,
                                  video_id=fs_video_id,
                                  video_filename=life_video_filename,
                                  audio_doc_id=life_audio_doc_id,
                                  video_doc_id=life_video_doc_id,
                                  data_type='text')

                add_new_source_data_id(projects_collection,
                                       active_project_name,
                                       life_source_id,
                                       text_id)
    except:
        logger.exception("")
