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
        if (len(added_speaker_ids) != 0):
            speaker_audio_ids = projects_collection.find_one({'projectname': activeprojectname},
                                                {'_id': 0, 'speakersAudioIds': 1})
            # logger.debug(speaker_audio_ids)
            if ('speakersAudioIds' in speaker_audio_ids):
                speaker_audio_ids = speaker_audio_ids['speakersAudioIds']
                # logger.debug(speaker_audio_ids)
                for speaker in added_speaker_ids:
                    # logger.debug("speaker: %s", speaker)
                    if (speaker not in speakerids and
                        speaker in speaker_audio_ids and
                        len(speaker_audio_ids[speaker]) != 0):
                        # logger.debug("speaker: %s", speaker)
                        # logger.debug(speaker_audio_ids[speaker][0])
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
                        speakerids.append(speaker)
                success = True
    except:
        logger.exception("")
    
    return speakerids
