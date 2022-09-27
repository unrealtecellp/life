"""Module to get the list of all annotated and unannotated filename."""

def unannotatedfilename(transcriptions, activeprojectname, ID, idtype):


    annotated = []
    unannotated = []
    transcribedfiles = transcriptions.find({ "projectname": activeprojectname, "speakerId": ID },
                                        { "_id" : 0, "transcriptionFLAG" : 1, 'audioId': 1 })

    for transcribedfile in transcribedfiles:
        # print(transcribedfile, transcribedfile['transcriptionFLAG'])
        audioid = transcribedfile['audioId']
        if transcribedfile['transcriptionFLAG'] == 1:
            annotated.append(audioid)
        elif transcribedfile['transcriptionFLAG'] == 0:
            unannotated.append(audioid)
    # print(annotated, unannotated)

    return (sorted(annotated), sorted(unannotated))
