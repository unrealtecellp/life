"""Module to get the comment stats for a speaker/annotator."""

def getcommentstats(projects, transcriptions, activeprojectname, ID, idtype):
    """_summary_

    Args:
        id (_String_): _speakerId/annotatorId_
    """
    # print('getcommentstats(projects, activeprojectname, ID, idtype)')
    # print(ID)
    speakerinfo = projects.find_one({ "projectname": activeprojectname },
                                        { "_id" : 0, "speakersAudioIds."+str(ID) : 1 })
    speakerfiles = speakerinfo['speakersAudioIds'][ID]                                        
    total_comments = len(speakerfiles)
    transcribed = 0
    nottranscribed = 0
    transcribedfiles = transcriptions.find({ "projectname": activeprojectname, "speakerId": ID },
                                        { "_id" : 0, "transcriptionFLAG" : 1 })
    # print(speakerinfo)
    # print(total_comments)
    for transcribedfile in transcribedfiles:
        # print(transcribedfile, transcribedfile['transcriptionFLAG'])
        if transcribedfile['transcriptionFLAG'] == 1:
            transcribed += 1
        elif transcribedfile['transcriptionFLAG'] == 0:
            nottranscribed += 1
    # print(transcribed, nottranscribed)

    return (total_comments, transcribed, nottranscribed)
    