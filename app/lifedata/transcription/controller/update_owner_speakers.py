from app.controller import (
    life_logging
)

logger = life_logging.get_logger()

def update_owner_speakers(projects_collection,
                          activeprojectname,
                          project_owner,
                          speakerids,
                          added_speaker_ids):
    success = False
    try:
        speaker_audio_ids = projects_collection.find_one({'projectname': activeprojectname},
                                            {'_id': 0, 'speakersAudioIds': 1})['speakersAudioIds']
        # logger.debug(speaker_audio_ids)
        for speaker in added_speaker_ids:
            if (speaker not in speakerids):
                logger.debug("speaker: %s", speaker)
                logger.debug(speaker_audio_ids[speaker][0])
                projects_collection.update_one(
                    {
                        'projectname': activeprojectname
                    },
                    {
                        '$addToSet':
                        {
                            'speakerIds.'+project_owner: speaker
                        }
                    }
                )
                projects_collection.update_one(
                    {
                        'projectname': activeprojectname
                    },
                    {
                        '$set':
                        {
                            'lastActiveId.'+project_owner+'.'+speaker+'.audioId': speaker_audio_ids[speaker][0]
                        }
                    }
                )
        success = True
    except:
        logger.exceprion("")
    
    return success
