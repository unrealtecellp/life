"""Module to get the comment stats for a speaker/annotator."""

from app.controller import (
    life_logging
)
from pprint import pformat
logger = life_logging.get_logger()

def getcommentstats(projects,
                    transcriptions,
                    activeprojectname,
                    ID,
                    speaker_audio_ids,
                    idtype):
    """_summary_

    Args:
        id (_String_): _speakerId/annotatorId_
    """
    # print('getcommentstats(projects, activeprojectname, ID, idtype)')
    # print(ID)
    total_comments = 0
    transcribed = 0
    nottranscribed = 0
    try:
        # speakerinfo = projects.find_one({ "projectname": activeprojectname },
        #                                     { "_id" : 0, "speakersAudioIds."+str(ID) : 1 })
        # speakerfiles = speakerinfo['speakersAudioIds'][ID]
        speakerfiles = speaker_audio_ids
        # total_comments = len(speakerfiles)

        transcribedfiles = transcriptions.find({ "projectname": activeprojectname, "speakerId": ID },
                                            {"_id" : 0,
                                             "audioId": 1,
                                             "transcriptionFLAG" : 1,
                                             "audiodeleteFLAG": 1})
        # print(speakerinfo)
        # print(total_comments)
        for transcribedfile in transcribedfiles:
            # logger.debug('transcribedfile: %s, ', transcribedfile)
            audioId = transcribedfile['audioId']
            if (audioId in speakerfiles):
                if (transcribedfile['audiodeleteFLAG'] == 0):
                    if transcribedfile['transcriptionFLAG'] == 1:
                        transcribed += 1
                    elif transcribedfile['transcriptionFLAG'] == 0:
                        nottranscribed += 1
                elif (transcribedfile['audiodeleteFLAG'] == 1):
                    speakerfiles.remove(audioId)
        # print(transcribed, nottranscribed)
        # logger.debug('total_comments: %s, transcribed: %s, nottranscribed: %s', total_comments, transcribed, nottranscribed)
        total_comments = len(speakerfiles)
    except:
        logger.exception("")

    return (total_comments, transcribed, nottranscribed)

def getcommentstatsnew(projects_collection,
                        data_collection,
                        activeprojectname,
                        match_key,
                        groupBy_key,
                        idtype):
    
    aggregate_output = data_collection.aggregate( [
                                {
                                    "$match": { "projectname": activeprojectname,
                                               "speakerId": match_key }
                                },
                                {
                                    "$group": { "_id": "$"+groupBy_key,
                                               "count": { "$sum": 1 }
                                    }
                                }
                                ] )
    total_comments, annotated_comments, remaining_comments = (0, 0, 0)
    for doc in aggregate_output:
        # logger.debug("aggregated_output: %s", doc)
        if doc['_id'] == 0:
            remaining_comments = doc['count']
        elif doc['_id'] == 1:
            annotated_comments = doc['count']
    total_comments = remaining_comments+annotated_comments
    # logger.debug("total_comments: %s\nannotated_comments: %s\nremaining_comments: %s", total_comments, annotated_comments, remaining_comments)

    return (total_comments, annotated_comments, remaining_comments)

def getdatacommentstatsnew(data_collection,
                            activeprojectname,
                            match_key,
                            groupBy_key):
    
    aggregate_output = data_collection.aggregate( [
                                {
                                    "$match": { "projectname": activeprojectname,
                                                "lifesourceid": match_key,
                                                "datadeleteFLAG": 0 }
                                },
                                {
                                    "$group": { "_id": "$"+groupBy_key,
                                               "count": { "$sum": 1 }
                                    }
                                }
                                ] )
    total_comments, annotated_comments, remaining_comments = (0, 0, 0)
    for doc in aggregate_output:
        # logger.debug("aggregated_output: %s", doc)
        if doc['_id'] == 0:
            remaining_comments = doc['count']
        elif doc['_id'] == 1:
            annotated_comments = doc['count']
    total_comments = remaining_comments+annotated_comments
    # logger.debug("total_comments: %s\nannotated_comments: %s\nremaining_comments: %s", total_comments, annotated_comments, remaining_comments)

    return (total_comments, annotated_comments, remaining_comments)
