def get_all_karya_speaker_ids(accesscodedetails, activeprojectname):
    karya_speaker_ids = []

    speaker_ids = accesscodedetails.find({'projectname': activeprojectname,
                                                'fetchData': 0,
                                                'isActive': 1,
                                                'task': 'SPEECH_DATA_COLLECTION'
                                                },
                                                {
                                                    '_id': 0,
                                                    'karyaspeakerid': 1,
                                                    'lifespeakerid': 1
                                                })

    for speakerid in speaker_ids:
        karyaspeakerid = speakerid['karyaspeakerid']
        lifespeakerid = speakerid['lifespeakerid']
        # karya_speaker_ids.append(karyaspeakerid)
        karya_speaker_ids.append({"id": karyaspeakerid, "text": lifespeakerid})

    return karya_speaker_ids


def get_one_speaker_details(
    accesscodedetails,
    activeprojectname,
    asycaccesscode
):
    speakerdetails = accesscodedetails.find_one({"projectname": activeprojectname, "karyaaccesscode": asycaccesscode},
                                                {"_id": 0,
                                                "current.workerMetadata": 1})
    accesscodetask = accesscodedetails.find_one({"projectname": activeprojectname, "karyaaccesscode": asycaccesscode},
                                                {"_id": 0,
                                                "task": 1})
    
    speakerdetails.update(accesscodetask)

    return speakerdetails