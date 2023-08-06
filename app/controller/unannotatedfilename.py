"""Module to get the list of all annotated and unannotated filename."""

from app.controller import (
    life_logging
)
logger = life_logging.get_logger()

def unannotatedfilename(transcriptions,
                        activeprojectname,
                        ID,
                        speaker_audio_ids,
                        idtype):


    annotated = []
    unannotated = []
    transcribedfiles = transcriptions.find({"projectname": activeprojectname,
                                            "speakerId": ID
                                            },
                                            {"_id" : 0,
                                             "transcriptionFLAG" : 1,
                                             'audioId': 1,
                                             "audiodeleteFLAG": 1})

    for transcribedfile in transcribedfiles:
        logger.debug("transcribedfile: %s", transcribedfile)
        audioid = transcribedfile['audioId']
        if(audioid in speaker_audio_ids):
            audio_delete_flag = transcribedfile['audiodeleteFLAG']
            if (not audio_delete_flag):
                if transcribedfile['transcriptionFLAG'] == 1:
                    annotated.append(audioid)
                elif transcribedfile['transcriptionFLAG'] == 0:
                    unannotated.append(audioid)
    # print(annotated, unannotated)

    return (sorted(annotated), sorted(unannotated))
