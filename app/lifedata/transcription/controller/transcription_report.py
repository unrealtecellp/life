from app.controller import (
    life_logging
)
from app.lifedata.transcription.controller import (
    transcription_audiodetails
)
from pprint import pformat
import gridfs

logger = life_logging.get_logger()

def total_audio_duration_project(mongo,
                                transcriptions_collection,
                                project_name):
    total_duration = 0
    count = 0
    try:
        aggregate_output = transcriptions_collection.aggregate(
            [
                {
                    "$match": {
                        "projectname": project_name,
                        "speakerId": { "$ne": "" },
                        "audiodeleteFLAG": 0
                    },
                },
                {
                    "$group": {
                        "_id": "",
                        "total_duration": { "$sum": "$audioMetadata.currentSliceDuration" },
                        "count": { "$sum": 1 }
                    }
                }
            ]
        )
        # logger.debug("aggregate_output: %s", aggregate_output)
        for doc in aggregate_output:
            logger.debug("doc: %s", pformat(doc))
            total_duration = doc['total_duration']
            count = doc['count']
        logger.debug("total_duration: %s", total_duration)
        currentSliceDuration_not_exist = transcriptions_collection.aggregate(
                                        [
                                            {
                                                "$match": {
                                                    "projectname": project_name,
                                                    "speakerId": { "$ne": "" },
                                                    "audiodeleteFLAG": 0,
                                                    "audioMetadata.currentSliceDuration": { "$exists": False }
                                                },
                                            },
                                            {
                                                "$project": {
                                                    "_id": 0,
                                                    "audioId": 1
                                                }
                                            }
                                        ]
                                    )
        # logger.debug(f"currentSliceDuration_not_exist: {currentSliceDuration_not_exist}")
        currentSliceDuration_not_exist_list = []
        for doc in currentSliceDuration_not_exist:
            # logger.debug(doc)
            currentSliceDuration_not_exist_list.append(doc['audioId'])
        logger.debug(currentSliceDuration_not_exist_list)
        logger.debug(len(currentSliceDuration_not_exist_list))
        # if (total_duration == 0):
        if (len(currentSliceDuration_not_exist_list) != 0):
            count = count - len(currentSliceDuration_not_exist_list)
            total_duration, count = missing_duration(mongo,
                                                transcriptions_collection,
                                                project_name,
                                                currentSliceDuration_not_exist_list,
                                                total_duration,
                                                count)
    except:
        logger.exception("")

    return (total_duration, count)

def total_audio_duration_transcribed(mongo,
                                    transcriptions_collection,
                                    project_name):
    total_duration = 0
    count = 0
    try:
        aggregate_output = transcriptions_collection.aggregate(
            [
                {
                    "$match": {
                        "projectname": project_name,
                        "speakerId": { "$ne": "" },
                        "transcriptionFLAG": 1,
                        "audiodeleteFLAG": 0
                    },
                },
                {
                    "$group": {
                        "_id": "",
                        "total_duration": { "$sum": "$audioMetadata.currentSliceDuration" },
                        "count": { "$sum": 1 }
                    }
                }
            ]
        )
        logger.debug("aggregate_output: %s", aggregate_output)
        for doc in aggregate_output:
            logger.debug("doc: %s", pformat(doc))
            total_duration = doc['total_duration']
            count = doc['count']
        logger.debug("total_duration: %s", total_duration)
        currentSliceDuration_not_exist = transcriptions_collection.aggregate(
                                        [
                                            {
                                                "$match": {
                                                    "projectname": project_name,
                                                    "speakerId": { "$ne": "" },
                                                    "transcriptionFLAG": 1,
                                                    "audiodeleteFLAG": 0,
                                                    "audioMetadata.currentSliceDuration": { "$exists": False }
                                                },
                                            },
                                            {
                                                "$project": {
                                                    "_id": 0,
                                                    "audioId": 1
                                                }
                                            }
                                        ]
                                    )
        # logger.debug(f"currentSliceDuration_not_exist: {currentSliceDuration_not_exist}")
        currentSliceDuration_not_exist_list = []
        for doc in currentSliceDuration_not_exist:
            # logger.debug(doc)
            currentSliceDuration_not_exist_list.append(doc['audioId'])
        logger.debug(currentSliceDuration_not_exist_list)
        logger.debug(len(currentSliceDuration_not_exist_list))
        # if (total_duration == 0):
        if (len(currentSliceDuration_not_exist_list) != 0):
            count = count - len(currentSliceDuration_not_exist_list)
            total_duration, count = missing_duration_transcribed(mongo,
                                                                transcriptions_collection,
                                                                project_name,
                                                                currentSliceDuration_not_exist_list,
                                                                total_duration,
                                                                count)
    except:
        logger.exception("")

    return (total_duration, count)

def total_audio_duration_boundary(transcriptions_collection,
                         project_name):
    total_duration = 0
    try:
        aggregate_output = transcriptions_collection.aggregate(
            [
                {
                    "$match": {
                        "projectname": project_name,
                        "speakerId": { "$ne": "" },
                        "transcriptionFLAG": 1,
                        "audiodeleteFLAG": 0
                    },
                },
                {
                    "$project": {
                        "_id": 0,
                        "textGrid": 1
                    }
                }
            ]
        )
        logger.debug("total_duration: %s", total_duration)
        # logger.debug("aggregate_output: %s", aggregate_output)
        for doc in aggregate_output:
            # logger.debug("textGrid: %s", pformat(doc['textGrid']['sentence']))
            for key, value in doc['textGrid']['sentence'].items():
                total_duration += value['end'] - value['start']
                logger.debug(value['end'])
                logger.debug(value['start'])
                logger.debug(f"{value['end'] - value['start']}")
                logger.debug("total_duration: %s", total_duration)
        logger.debug("total_duration: %s", total_duration)
    except:
        logger.exception("")
    
    return total_duration

def total_audio_duration_speaker(transcriptions_collection,
                         project_name,
                         speaker_name):
    try:
        aggregate_output = transcriptions_collection.aggregate(
            [
                {
                    "$match": {
                        "projectname": project_name
                    },
                },
                {
                    "$group": {
                        "_id": "",
                        "total_duration": { "$sum": "$audioMetadata.currentSliceDuration" }
                    }
                }
            ]
        )
        logger.debug("aggregate_output: %s", aggregate_output)
        for doc in aggregate_output:
            logger.debug("total_duration: %s", pformat(doc))
    except:
        logger.exception("")

def missing_duration(mongo,
                     transcriptions_collection,
                     project_name,
                     currentSliceDuration_not_exist_list,
                     total_duration = 0,
                     count = 0):
    try:
        # aggregate_output = transcriptions_collection.aggregate(
        #     [
        #         {
        #             "$match": {
        #                 "projectname": project_name,
        #                 "speakerId": { "$ne": "" },
        #                 "audiodeleteFLAG": 0
                        
        #             },
        #         },
        #         {
        #             "$project": {
        #                 "_id": 0,
        #                 "audioId": 1
        #             }
        #         }
        #     ]
        # )
        # # logger.debug("aggregate_output: %s", aggregate_output)
        for audio_id in currentSliceDuration_not_exist_list:
        # for doc in aggregate_output:
        #     logger.debug("total_duration: %s", total_duration)
        #     audio_id = doc['audioId']
            logger.debug(audio_id)
            fs = gridfs.GridFS(mongo.db)
            file = fs.find_one({'audioId': audio_id})
            if (file is not None):
                mongo_filename = file.filename
                audiofile = fs.get_last_version(filename=mongo_filename)
                audio_duration, audio_file = transcription_audiodetails.get_audio_duration_from_file(audiofile)
                logger.debug(audio_duration)
                logger.debug(audio_file)
                total_duration += audio_duration
                count += 1
        logger.debug("total_duration: %s", total_duration)
    except:
        logger.exception("")
    
    return (total_duration, count)

def missing_duration_transcribed(mongo,
                                    transcriptions_collection,
                                    project_name,
                                    currentSliceDuration_not_exist_list,
                                    total_duration = 0,
                                    count = 0):
    try:
        # aggregate_output = transcriptions_collection.aggregate(
        #     [
        #         {
        #             "$match": {
        #                 "projectname": project_name,
        #                 "transcriptionFLAG": 1,
        #                 "audiodeleteFLAG": 0
        #             },
        #         },
        #         {
        #             "$project": {
        #                 "_id": 0,
        #                 "audioId": 1
        #             }
        #         }
        #     ]
        # )
        # # logger.debug("aggregate_output: %s", aggregate_output)
        for audio_id in currentSliceDuration_not_exist_list:
        # for doc in aggregate_output:
        #     logger.debug("total_duration: %s", total_duration)
            # audio_id = doc['audioId']
            logger.debug(audio_id)
            fs = gridfs.GridFS(mongo.db)
            file = fs.find_one({'audioId': audio_id})
            if (file is not None):
                mongo_filename = file.filename
                audiofile = fs.get_last_version(filename=mongo_filename)
                audio_duration, audio_file = transcription_audiodetails.get_audio_duration_from_file(audiofile)
                logger.debug(audio_duration)
                logger.debug(audio_file)
                total_duration += audio_duration
                count += 1
        logger.debug("total_duration: %s", total_duration)
    except:
        logger.exception("")
    
    return (total_duration, count)
