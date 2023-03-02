def getspeakerdetails(activeprojectname, speakermeta):

    allspeakerdetails = dict()
    allsubsources = []
    all_lengths = {}

    ##TODO: Create this table dynamically based on keys being included
    all_keys = {
        'FIELD': [
            'Speaker ID',
            'Name',
            'Age Group',
            'Gender',
            'Created By',
            'Last Updated By'
        ],
        'YOUTUBE': [
            'Source ID',
            'Channel Name',
            'Channel URL',
            'Created By',
            'Last Updated By'
        ]
    }

    all_audio_sources = speakermeta.find(
        {'projectname': activeprojectname, 'isActive': 1},
        {'audioSource': 1, '_id': 0}
    )

    for current_audio_source in all_audio_sources:
        current_source = current_audio_source['audioSource']

        if current_source not in allsubsources:
            if current_source == 'internet':
                allsubsources.append(current_source)
                metadata = get_internet_speaker_details(activeprojectname, speakermeta)
                allspeakerdetails.update(metadata)
                
                
            elif current_source == 'field':
                allsubsources.append(current_source)
                metadata = get_field_speaker_details(activeprojectname, speakermeta)
                allspeakerdetails[current_source.upper()] = metadata
                
    
    for source in allspeakerdetails:
        all_lengths[source] = len(allspeakerdetails[source])
   
    return allspeakerdetails, all_lengths, all_keys



def get_field_speaker_details(activeprojectname, speakermeta):
    data_table = []
    fieldspeakerdetails = speakermeta.find(
        {"isActive":1, "projectname": activeprojectname,
        'audioSource': 'field'}, {
            "lifesourceid":1,
            "current.updatedBy":1,
            "current.sourceMetadata.name":1,
            "current.sourceMetadata.agegroup":1,
            "current.sourceMetadata.gender":1,
            "createdBy":1,
            "_id" :0})

    
    for data in fieldspeakerdetails:
        data_table.append(data)
    
    return data_table



def get_internet_speaker_details(activeprojectname, speakermeta):
    all_data_table = {}
    allsubsources = []

    internet_sub_sources = speakermeta.find(
        {'projectname': activeprojectname, 'audioSource': 'internet', 'isActive': 1},
        {'audioSubSource': 1, '_id': 0}
    )

    for current_audio_sub_source in internet_sub_sources:
        current_sub_source = current_audio_sub_source['audioSubSource']
        if current_sub_source not in allsubsources:
            allsubsources.append(current_audio_sub_source)
            if current_sub_source == 'youtube':
                current_data = get_youtube_details(activeprojectname, speakermeta)        
                all_data_table[current_sub_source.upper()] = current_data
    
    return all_data_table


def get_youtube_details(activeprojectname, speakermeta):
    data_table = []
    youtube_speaker_details = speakermeta.find(
        {'projectname': activeprojectname, 'isActive': 1,
            'audioSubSource': 'youtube'}, {
                'lifesourceid': 1, 
                'createdBy': 1, 
                'audioSource': 1, 
                'audioSubSource': 1, 
                'current.updatedBy': 1, 
                'current.sourceMetadata.channelName': 1, 
                'current.sourceMetadata.channelUrl': 1, 
                '_id': 0}
    )

    for data in youtube_speaker_details:
        data_table.append(data)

    return data_table


def getonespeakerdetails(activeprojectname, lifesourceid, speakermeta):
    speakerdetails = speakermeta.find_one({"projectname": activeprojectname, "lifesourceid": lifesourceid},
                                            {"_id": 0,
                                            "current.sourceMetadata": 1,
                                            "lifesourceid": 1})

    return speakerdetails


def updateonespeakerdetails(activeprojectname, lifesourceid, all_details, speakermeta):
    print ("All details", all_details)
    print ("Life source ID", lifesourceid)
    status = speakermeta.update_one({"projectname": activeprojectname, "lifesourceid": lifesourceid},
    {"$set": all_details})
    
    return status.raw_result