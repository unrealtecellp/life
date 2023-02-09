def getspeakerdetails(activeprojectname, speakermeta):
    youtube_speaker_details = speakermeta.find(
        {'projectname': activeprojectname,
            'audioSubSource': 'youtube'}, {'lifesourceid': 1, 'createdBy': 1, 'audioSource': 1, 'audioSubSource': 1, 'current.updatebBy': 1}
    )
    return True
