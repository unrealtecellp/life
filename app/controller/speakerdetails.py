def getspeakerdetails(activeprojectname, speakermeta):
    youtube_speaker_details = speakermeta.find(
        {'projectname': activeprojectname, 'isActive': 1,
            'audioSubSource': 'youtube'}, {'lifesourceid': 1, 'createdBy': 1, 'audioSource': 1, 'audioSubSource': 1, 'current.updatebBy': 1, 'current.sourceMetadata.channelName': 1, 'current.sourceMetadata.channelUrl': 1, '_id': 0}
    )
    return youtube_speaker_details
