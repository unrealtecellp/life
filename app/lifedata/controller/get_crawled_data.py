from pprint import pformat
from app.controller import (
    life_logging
)

logger = life_logging.get_logger()

def delete_one_audio_file(projects_collection,
                          transcriptions_collection,
                          project_name,
                          current_username,
                          active_speaker_id,
                          audio_id,
                          update_latest_audio_id=1):
    try:
        logger.debug("project_name: %s, audio_id: %s", project_name, audio_id)
        transcription_doc_id = transcriptions_collection.find_one_and_update({
            "projectname": project_name,
            "audioId": audio_id
            },
            {"$set": {"audiodeleteFLAG": 1}},
            projection={'_id': True},
            return_document=ReturnDocument.AFTER)['_id']
        logger.debug('DELETED transcription_doc_id: %s, %s', transcription_doc_id, type(transcription_doc_id))

        if (update_latest_audio_id):
            latest_audio_id = getnewaudioid(projects_collection,
                                            project_name,
                                            audio_id,
                                            active_speaker_id,
                                            'next')
            updatelatestaudioid(projects_collection,
                                project_name,
                                latest_audio_id,
                                current_username,
                                active_speaker_id)
            
        projects_collection.update_one({"projectname": project_name},
                                       {"$pull": {"speakersAudioIds."+active_speaker_id: audio_id},
                                        "$addToSet": {"speakersAudioIdsDeleted."+active_speaker_id: audio_id}
                                        })
    except:
        logger.exception("")
        transcription_doc_id = False

    return transcription_doc_id

def get_audio_delete_flag(transcriptions_collection,
                          project_name,
                          audio_id):
    logger.debug("%s, %s, %s", transcriptions_collection,
                          project_name,
                          audio_id)
    audio_delete_flag = transcriptions_collection.find_one({"projectname": project_name,
                                                            "audioId": audio_id},
                                                            {"_id": 0,
                                                             "audiodeleteFLAG": 1})["audiodeleteFLAG"]
    
    return audio_delete_flag

def revoke_deleted_audio(projects_collection,
                         transcriptions_collection,
                         project_name,
                         active_speaker_id,
                         audio_id):
    try:
        logger.debug("project_name: %s, audio_id: %s", project_name, audio_id)
        transcription_doc_id = transcriptions_collection.find_one_and_update({
            "projectname": project_name,
            "audioId": audio_id
            },
            {"$set": {"audiodeleteFLAG": 0}},
            projection={'_id': True},
            return_document=ReturnDocument.AFTER)['_id']
        logger.debug('REVOKED transcription_doc_id: %s, %s', transcription_doc_id, type(transcription_doc_id))

        projects_collection.update_one({"projectname": project_name},
                                        {"$pull": {"speakersAudioIdsDeleted."+active_speaker_id: audio_id},
                                        "$addToSet": {"speakersAudioIds."+active_speaker_id: audio_id}
                                        })
    except:
        logger.exception("")
        transcription_doc_id = False

    return transcription_doc_id

def get_n_crawled_data(data_collection,
                        activeprojectname,
                        active_speaker_id,
                        start_from=0,
                        number_of_audios=10,
                        text_delete_flag=0):
    aggregate_output = data_collection.aggregate( [
                                {
                                    "$match": {
                                        "projectname": activeprojectname,
                                        "lifesourceid": active_speaker_id,
                                        "textdeleteFLAG": text_delete_flag
                                                }
                                },
                                { 
                                    "$sort" : {
                                        "textId" : 1
                                        }
                                },
                                {
                                    "$project": {
                                        "_id": 0,
                                        "textId": 1,
                                        "Text": 1
                                    }
                                }
                                ] )
    # logger.debug("aggregate_output: %s", aggregate_output)
    aggregate_output_list = []
    for doc in aggregate_output:
        # logger.debug("aggregate_output: %s", pformat(doc))
        aggregate_output_list.append(doc)
    logger.debug('aggregate_output_list: %s', pformat(aggregate_output_list))

    return aggregate_output_list[start_from:number_of_audios]