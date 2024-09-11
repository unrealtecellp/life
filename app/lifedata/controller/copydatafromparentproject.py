"""Module to data in "questionnaires" collection """

from datetime import datetime
import re
from pprint import pformat
from app.lifedata.controller import (
    save_crawled_data
)
from app.controller import (
    life_logging,
    getprojectowner,
    getdbcollections
)
from app.lifedata.transcription.controller import (
    transcription_audiodetails
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

def copy_sourcedetails_to_speakerdetails(mongo,
                                         derived_from_project_name,
                                         project_name,
                                         project_owner,
                                         current_username,
                                         lifesourceid):
    '''copy from crawling type project to transcription type project.'''
    try:
        sourcedetails_collection, speakerdetails_collection = getdbcollections.getdbcollections(mongo,
                                                                                                'sourcedetails',
                                                                                                'speakerdetails')
        project_speakerdetail = speakerdetails_collection.find_one({ "projectname": project_name, "lifesourceid": lifesourceid })
        if (project_speakerdetail is None):
            # logger.debug(project_speakerdetail)
            project_sourcedetail = sourcedetails_collection.find_one({ "projectname": derived_from_project_name, "lifesourceid": lifesourceid })
            # logger.debug(project_sourcedetail)
            project_sourcedetail['derivedfromprojectdetails'] = {
                "derivedfromprojectname": derived_from_project_name,
                "source_doc_id": project_sourcedetail.pop('_id')
            }
            project_sourcedetail['username'] = project_owner
            project_sourcedetail['projectname'] = project_name
            project_sourcedetail['createdBy'] = current_username
            project_sourcedetail['audioSource'] = project_sourcedetail.pop('dataSource')
            project_sourcedetail['audioSubSource'] = project_sourcedetail.pop('dataSubSource')
            project_sourcedetail['metadataSchema'] = 'youtube'
            project_sourcedetail['uploadType'] = 'single'
            project_sourcedetail['additionalInfo'] = {}
            project_sourcedetail['current']['updatedBy'] = current_username
            project_sourcedetail['current']['current_date'] = str(datetime.now()).replace('.', ':')
            project_sourcedetail['uploadedAt'] = str(datetime.now()).replace('.', ':')
            del project_sourcedetail['dataType']
            del project_sourcedetail['audioFsId']
            del project_sourcedetail['audioDocumentId']
            del project_sourcedetail['videoFsid']
            del project_sourcedetail['videoId']
            del project_sourcedetail['videoFilename']
            del project_sourcedetail['videoDocumentId']
            del project_sourcedetail['commentCrawlingStatus']
            del project_sourcedetail['sourcedeleteFLAG']
            speakerdetails_collection.insert_one(project_sourcedetail)
        else:
            logger.debug(project_speakerdetail)
    except:
        logger.exception("")

def update_speakersIds(projects_collection,
                       userprojects_collection,
                       project_name,
                       current_username,
                       speaker_ids):
    try:
        # logger.debug("speaker_ids: %s", pformat(speaker_ids))
        speaker_Ids_list = []
        lastActiveId = {current_username: {}}
        for key in speaker_ids.keys():
            speaker_Ids_list.append(key)
            lastActiveId[current_username][key] = {
                "audioId": speaker_ids[key][0]}
            # logger.debug("speaker_Ids_list: %s", pformat(speaker_Ids_list))
        # logger.debug("lastActiveId: %s", pformat(lastActiveId))
            projects_collection.update_one({"projectname": project_name},
                                        {"$set": {
                                            "lastActiveId."+current_username+"."+key+".audioId": speaker_ids[key][0]
                                            # "speakerIds."+current_username: speaker_Ids_list,
                                            # "speakersAudioIds": speaker_ids
                                        },
                                        "$addToSet": {
                                            # "lastActiveId."+current_username: lastActiveId[current_username],
                                            "speakerIds."+current_username: {"$each": speaker_Ids_list},
                                            "speakersAudioIds."+key: {"$each": speaker_ids[key]}
                                        }
                                        })
        if (len(speaker_Ids_list) != 0):
            transcription_audiodetails.update_active_speaker_Id(userprojects_collection,
                                                    project_name,
                                                    current_username,
                                                    speaker_Ids_list[0])
    except:
        logger.exception("")

def sync_transcription_project_from_crawling_project(mongo,
                                                     projects_collection,
                                                        userprojects_collection,
                                                        crawling_collection,
                                                        data_collection,
                                                        derived_from_project_name,
                                                        project_name,
                                                        current_username):
    sync_audio_status = False
    try:
        projectowner = getprojectowner.getprojectowner(projects_collection, project_name)
        # all_crawled_audio_data = crawling_collection.find(
        #     {"projectname": derived_from_project_name, "audiodeleteFLAG": 0}, {"_id": 0})
        source_audio_ids = projects_collection.find_one({"projectname": derived_from_project_name},
                                                        {"_id": 0,
                                                         "sourceAudioIds": 1})
        if (source_audio_ids is not None and
            'sourceAudioIds' in source_audio_ids):
            source_audio_ids = source_audio_ids['sourceAudioIds']
        else:
            source_audio_ids = {}
        # logger.debug(source_audio_ids)
        speakers_audio_ids = projects_collection.find_one({"projectname": project_name},
                                                        {"_id": 0,
                                                         "speakersAudioIds": 1})
        if (speakers_audio_ids is not None and
            'speakersAudioIds' in speakers_audio_ids):
            speakers_audio_ids = speakers_audio_ids['speakersAudioIds']
        else:
            speakers_audio_ids = {}
        # logger.debug(speakers_audio_ids)
        # source_speaker_diff = []
        source_speaker_diff  = sorted(list(set(list(source_audio_ids.keys())).difference(list(speakers_audio_ids.keys()))))
        # logger.debug(source_speaker_diff)
        for source in source_speaker_diff:
            speaker_ids = {}
            # audio_ids = source_audio_ids[source]
            # speaker_ids[source] = audio_ids
            all_transcription_audio_data = []
            all_crawled_audio_data = crawling_collection.aggregate([
                                        {
                                            "$match": {
                                                "projectname": derived_from_project_name,
                                                # "audioId": {'$in': audio_ids},
                                                "lifesourceid": source,
                                                "audiodeleteFLAG": 0,
                                                "dataType": "audio"
                                            }
                                        },
                                        {
                                            "$sort": {
                                                "audioId": 1
                                            }
                                        },
                                        {
                                            "$project": {
                                                "_id": 0,
                                            }
                                        }
                                    ])
            for i, crawled_data in enumerate(all_crawled_audio_data):
                # logger.debug('crawled_data: %s -> %s', i, pformat(crawled_data))
                audioId = crawled_data['audioId']
                # logger.debug('crawled_data: %s', audioId)
                speaker_audiodetail = data_collection.find_one({ "projectname": project_name, "audioId": audioId })
                if (speaker_audiodetail is None):
                    # audio_filename = crawled_data['audioFilename']
                    # audio_duration = crawled_data['audioMetadata']['currentSliceDuration']
                    derived_from_project_details = {
                        "derivedfromprojectname": derived_from_project_name,
                        "audioId": audioId
                    }
                    audio_detail = crawled_data
                    audio_detail['username'] = current_username
                    audio_detail['projectname'] = project_name
                    audio_detail['lastUpdatedBy'] = current_username
                    audio_detail['derivedfromprojectdetails'] = derived_from_project_details
                    audio_detail['prompt'] = {}
                    # logger.debug('audio_detail: %s -> %s', i, pformat(audio_detail))
                    all_transcription_audio_data.append(audio_detail)
                lifesourceid = crawled_data['lifesourceid']
                if (lifesourceid in speaker_ids):
                    speaker_ids[lifesourceid].append(audioId)
                else:
                    speaker_ids[lifesourceid] = [audioId]
            # logger.debug(pformat(all_transcription_audio_data))
            if (len(all_transcription_audio_data) != 0):
                data_collection.insert_many(all_transcription_audio_data)
            # logger.debug(speaker_ids)
            if (speaker_ids):
                update_speakersIds(projects_collection,
                                    userprojects_collection,
                                    project_name,
                                    current_username,
                                    speaker_ids)
            copy_sourcedetails_to_speakerdetails(mongo,
                                                    derived_from_project_name,
                                                    project_name,
                                                    projectowner,
                                                    current_username,
                                                    source)
        if (len(source_speaker_diff) == 0):
            sync_audio_status = True
    except:
        logger.exception("")

    return sync_audio_status