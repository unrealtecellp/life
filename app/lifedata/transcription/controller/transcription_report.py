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
    try:
        # aggregate_output = transcriptions_collection.aggregate(
        #     [
        #         {
        #             "$match": {
        #                 "projectname": project_name,
        #                 "speakerId": { "$ne": "" }
        #             },
        #         },
        #         {
        #             "$group": {
        #                 "_id": "",
        #                 "total_duration": { "$sum": "$audioMetadata.currentSliceDuration" },
        #                 "count": { "$sum": 1 }
        #             }
        #         }
        #     ]
        # )
        # logger.debug("aggregate_output: %s", aggregate_output)
        # for doc in aggregate_output:
        #     logger.debug("total_duration: %s", pformat(doc))
        #     total_duration = doc['total_duration']
        #     count = doc['count']
        logger.debug("total_duration: %s", total_duration)
        if (total_duration == 0):
            total_duration, count = missing_duration(mongo,
                                                transcriptions_collection,
                                                project_name)
    except:
        logger.exception("")

    return (total_duration, count)

def total_audio_duration_transcribed(mongo,
                                    transcriptions_collection,
                                    project_name):
    total_duration = 0
    try:
        # aggregate_output = transcriptions_collection.aggregate(
        #     [
        #         {
        #             "$match": {
        #                 "projectname": project_name,
        #                 "transcriptionFLAG": 1
        #             },
        #         },
        #         {
        #             "$group": {
        #                 "_id": "",
        #                 "total_duration": { "$sum": "$audioMetadata.currentSliceDuration" },
        #                 "count": { "$sum": 1 }
        #             }
        #         }
        #     ]
        # )
        # logger.debug("aggregate_output: %s", aggregate_output)
        # for doc in aggregate_output:
        #     logger.debug("total_duration: %s", pformat(doc))
        #     total_duration = doc['total_duration']
        #     count = doc['count']
        logger.debug("total_duration: %s", total_duration)
        if (total_duration == 0):
            total_duration, count = missing_duration_transcribed(mongo,
                                                            transcriptions_collection,
                                                            project_name)
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
                        "transcriptionFLAG": 1
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
        logger.debug("aggregate_output: %s", aggregate_output)
        for doc in aggregate_output:
            # logger.debug("textGrid: %s", pformat(doc['textGrid']['sentence']))
            for key, value in doc['textGrid']['sentence'].items():
                total_duration += value['end'] - value['start']
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
                     project_name):
    total_duration = 0
    count = 0
    try:
        aggregate_output = transcriptions_collection.aggregate(
            [
                {
                    "$match": {
                        "projectname": project_name,
                        "speakerId": { "$ne": "" }
                        
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
        # logger.debug("aggregate_output: %s", aggregate_output)
        for doc in aggregate_output:
            logger.debug("total_duration: %s", total_duration)
            audio_id = doc['audioId']
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
                                    project_name):
    total_duration = 0
    count = 0
    try:
        aggregate_output = transcriptions_collection.aggregate(
            [
                {
                    "$match": {
                        "projectname": project_name,
                        "transcriptionFLAG": 1
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
        # logger.debug("aggregate_output: %s", aggregate_output)
        for doc in aggregate_output:
            logger.debug("total_duration: %s", total_duration)
            audio_id = doc['audioId']
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
