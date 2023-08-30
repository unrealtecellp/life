from datetime import datetime
import pandas as pd
import re


def getspeakerdetails(activeprojectname, speakermeta):

    allspeakerdetails = dict()
    allsubsources = []
    all_lengths = {}

    # TODO: Create this table dynamically based on keys being included
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
                metadata = get_internet_speaker_details(
                    activeprojectname, speakermeta)
                allspeakerdetails.update(metadata)

            elif 'field' in current_source:
                allsubsources.append(current_source)
                metadata = get_field_speaker_details(
                    activeprojectname, speakermeta)
                allspeakerdetails[current_source.upper()] = metadata

    for source in allspeakerdetails:
        all_lengths[source] = len(allspeakerdetails[source])

    return allspeakerdetails, all_lengths, all_keys


def get_field_speaker_details(activeprojectname, speakermeta):
    data_table = []
    fieldspeakerdetails = speakermeta.find(
        {"isActive": 1, "projectname": activeprojectname,
         'audioSource': 'field'}, {
            "lifesourceid": 1,
            "current.updatedBy": 1,
            "current.sourceMetadata.name": 1,
            "current.sourceMetadata.agegroup": 1,
            "current.sourceMetadata.gender": 1,
            "createdBy": 1,
            "_id": 0})

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
                current_data = get_youtube_details(
                    activeprojectname, speakermeta)
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
    print("All details", all_details)
    print("Life source ID", lifesourceid)
    status = speakermeta.update_one({"projectname": activeprojectname, "lifesourceid": lifesourceid},
                                    {"$set": all_details})

    return status.raw_result


def generate_speaker_id(name, age='000'):
    name = name.replace(" ", "").replace(".", "").lower()
    age = age.replace("-", "")
    if name == '':
        name = 'undefined'
    if age == '':
        age = '000'
    new_speaker_id = name+age+'_'+re.sub(r'[-: \.]', '', str(datetime.now()))

    return new_speaker_id


def get_source_id(audio_source, audio_subsource, metadata_data):
    source_id = ''
    if 'field' in audio_source:
        name = metadata_data['name']
        age = metadata_data['agegroup']
        source_id = generate_speaker_id(name, age)
    elif 'youtube' in audio_subsource:
        cname = metadata_data['channelName']
        source_id = generate_speaker_id(cname)
    else:
        source_id = generate_speaker_id('undefined')

    return source_id


def write_speaker_metadata(speakerdetails,
                           projectowner,
                           activeprojectname,
                           current_username,
                           audio_source,
                           audio_subsource,
                           metadata_data,
                           source_id,
                           upload_type,
                           additional_info):

    current_dt = str(datetime.now()).replace('.', ':')
    metadata_schema = audio_subsource
    if 'field' in audio_source:
        audio_subsource = ''
    source_data = {"username": projectowner,
                   "projectname": activeprojectname,
                   "lifesourceid": source_id,
                   "createdBy": current_username,
                   "audioSource": audio_source,
                   "audioSubSource": audio_subsource,
                   "metadataSchema": metadata_schema,
                   "uploadType": upload_type,
                   "additionalInfo": additional_info,
                   "current": {
                       "updatedBy": current_username,
                       "sourceMetadata": metadata_data,
                       "current_date": current_dt,
                   },
                   "isActive": 1}
    speakerdetails.insert_one(source_data)


def write_bulk_speaker_metadata(speakerdetails,
                                projectowner,
                                activeprojectname,
                                current_username,
                                audio_source,
                                audio_subsource,
                                metadata_file):
    excel_data = pd.read_excel(metadata_file, engine="openpyxl")
    data_columns = excel_data.columns
    data_columns = [col.lower().replace(' ', '') for col in data_columns]
    excel_data.columns = data_columns
    excel_data.fillna('', inplace=True)
    if 'field' in audio_source:
        if 'educationmediumupto12' in data_columns:
            excel_data['educationmediumupto12'] = excel_data['educationmediumupto12'].apply(
                lambda x: x.split(','))
        if 'educationmediumafter12' in data_columns:
            excel_data['educationmediumafter12'] = excel_data['educationmediumafter12'].apply(
                lambda x: x.split(','))
        if 'speakerspeaklanguage' in data_columns:
            excel_data['speakerspeaklanguage'] = excel_data['speakerspeaklanguage'].apply(
                lambda x: x.split(','))

    all_records = excel_data.to_dict(orient='records')

    for current_record in all_records:
        upload_type = 'single'
        write_speaker_metadata_details(speakerdetails,
                                       projectowner,
                                       activeprojectname,
                                       current_username,
                                       audio_source,
                                       audio_subsource,
                                       current_record,
                                       upload_type)


def write_speaker_metadata_details(speakerdetails,
                                   projectowner,
                                   activeprojectname,
                                   current_username,
                                   audio_source,
                                   audio_subsource,
                                   metadata_data,
                                   upload_type,
                                   **kwargs):

    additional_info = {}

    for key, val in kwargs.items():
        additional_info[key] = val

    if upload_type == 'bulk':
        metadata_data = write_bulk_speaker_metadata(speakerdetails,
                                                    projectowner,
                                                    activeprojectname,
                                                    current_username,
                                                    audio_source,
                                                    audio_subsource,
                                                    metadata_data)
    else:
        source_id = get_source_id(audio_source, audio_subsource, metadata_data)

        write_speaker_metadata(speakerdetails,
                               projectowner,
                               activeprojectname,
                               current_username,
                               audio_source,
                               audio_subsource,
                               metadata_data,
                               source_id,
                               upload_type,
                               additional_info)
