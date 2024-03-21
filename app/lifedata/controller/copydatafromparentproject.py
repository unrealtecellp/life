"""Module to data in "questionnaires" collection """

from datetime import datetime
import re
from pprint import pformat
from app.lifedata.controller import (
    save_crawled_data
)
from app.controller import (
    life_logging
)

logger = life_logging.get_logger()


def copydatafromquesproject(questionnaires,
                            data_collection,
                            derived_from_project_name,
                            newprojectname,
                            current_username):
    transcription_doc_id = ''
    try:
        all_derived_ques = questionnaires.find({"projectname": derived_from_project_name, "quesdeleteFLAG": 0},
                                               {"_id": 0, "quesId": 1, "Q_Id": 1, "prompt": 1})
        for derived_ques in all_derived_ques:
            # print(derived_ques)
            quesId = derived_ques['quesId']
            Q_Id = derived_ques['Q_Id']
            prompt = derived_ques['prompt']
            prompt['Q_Id'] = Q_Id
            derived_from_project_details = {
                "derivedfromprojectname": derived_from_project_name,
                "quesId": quesId
            }
            text_grid = {
                "discourse": {},
                "sentence": {},
                "word": {},
                "phoneme": {}
            }
            # save audio file details in data_collection collection
            new_audio_details = {
                "username": current_username,
                "projectname": newprojectname,
                "updatedBy": current_username,
                "audiodeleteFLAG": 0,
                "audioverifiedFLAG": 0,
                "transcriptionFLAG": 0,
                "speakerId": "",
                "prompt": prompt
            }

            audio_id = 'A'+re.sub(r'[-: \.]', '', str(datetime.now()))
            new_audio_details['audioId'] = audio_id
            new_audio_details['audioFilename'] = ""
            new_audio_details["textGrid"] = text_grid
            new_audio_details[current_username] = {}
            new_audio_details[current_username]["textGrid"] = text_grid
            new_audio_details['derivedfromprojectdetails'] = derived_from_project_details

            transcription_doc_id = data_collection.insert_one(
                new_audio_details)

        return transcription_doc_id
    except:
        logger.exception("")


def copydatafromcrawlingproject(projects_collection,
                                userprojects_collection,
                                crawling,
                                data_collection,
                                derived_from_project_name,
                                project_name,
                                current_username):
    try:
        all_crawled_data = crawling.find(
            {"projectname": derived_from_project_name, "datadeleteFLAG": 0}, {"_id": 0, "audioFsId": 0,
                                                                              "audioId": 0,
                                                                              "audioFilename": 0,
                                                                              "audioDocumentId": 0,
                                                                              "videoFsId": 0,
                                                                              "videoId": 0,
                                                                              "videoFilename": 0,
                                                                              "videoDocumentId": 0})
        sourcedata_ids = {}
        for i, crawled_data in enumerate(all_crawled_data):
            # logger.debug('crawled_data: %s -> %s', i, pformat(crawled_data))
            dataId = crawled_data['dataId']
            derived_from_project_details = {
                "derivedfromprojectname": derived_from_project_name,
                "dataId": dataId
            }
            data_anno_detail = crawled_data
            data_anno_detail['username'] = current_username
            data_anno_detail["projectname"] = project_name
            data_id = 'T'+re.sub(r'[-: \.]', '', str(datetime.now()))
            data_anno_detail["dataId"] = data_id
            lifesourceid = crawled_data['lifesourceid']
            if (lifesourceid in sourcedata_ids):
                sourcedata_ids[lifesourceid].append(data_id)
            else:
                sourcedata_ids[lifesourceid] = [data_id]
            data_anno_detail['lastUpdatedBy'] = current_username
            data_anno_detail['annotatedFLAG'] = 0
            # data_anno_detail['textverifiedFLAG'] = 0
            # data_anno_detail['textdeleteFLAG'] = 0
            # data_anno_detail['prompt'] = ""
            # data_anno_detail['dataType'] = "text"
            # data_anno_detail['textMetadata'] = {}
            data_anno_detail['annotationGrid'] = {}

            all_access = {}
            data_anno_detail['allAccess'] = all_access
            all_updates = {}
            data_anno_detail['allUpdates'] = all_updates
            data_anno_detail['derivedfromprojectdetails'] = derived_from_project_details
            # logger.debug('data_anno_detail: %s -> %s', i, pformat(data_anno_detail))
            data_collection.insert_one(data_anno_detail)

        # logger.debug("sourcedata_ids: %s", pformat(sourcedata_ids))
        source_Ids_list = []
        lastActiveId = {current_username: {}}
        for key in sourcedata_ids.keys():
            source_Ids_list.append(key)
            lastActiveId[current_username][key] = {
                "dataId": sourcedata_ids[key][0]}
        # logger.debug("source_Ids_list: %s", pformat(source_Ids_list))
        # logger.debug("lastActiveId: %s", pformat(lastActiveId))
        projects_collection.update_one({"projectname": project_name},
                                       {"$set": {
                                           "lastActiveId."+current_username: lastActiveId[current_username],
                                           "sourceIds."+current_username: source_Ids_list,
                                           "sourcedataIds": sourcedata_ids
                                       }})
        save_crawled_data.update_active_source_id(userprojects_collection,
                                                  project_name,
                                                  current_username,
                                                  current_username,
                                                  source_Ids_list[0])
    except:
        logger.exception("")
