from app.controller import (
    life_logging
)
from pprint import pformat

logger = life_logging.get_logger()

def total_audio_duration_project(transcriptions_collection,
                         project_name):
    total_duration = 0
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
            total_duration = doc['total_duration']
        logger.debug("total_duration: %s", total_duration)
    except:
        logger.exception("")

    return total_duration

def total_audio_duration_transcribed(transcriptions_collection,
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
            total_duration = doc['total_duration']
        logger.debug("total_duration: %s", total_duration)
    except:
        logger.exception("")

    return total_duration

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