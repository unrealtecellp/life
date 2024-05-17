from datetime import datetime
import pandas as pd
import re
from app.controller import (
    life_logging
)

logger = life_logging.get_logger()


def getspeakerdetails(activeprojectname, speakermeta):

    allspeakerdetails = dict()
    allsubsources = []
    all_lengths = {}

    # TODO: Create this table dynamically based on keys being included
    all_keys = {
        'SPEED': [
            'Speaker ID',
            'Name',
            'Age Group',
            'Gender',
            'Created By',
            'Updated By'
        ],
        'LDCIL': [
            'Speaker ID',
            'Name',
            'Age Group',
            'Gender',
            'Created By',
            'Updated By'
        ],
        'MULTILILA': [
            'Speaker ID',
            'Name',
            'Age Group',
            'Gender',
            'Created By',
            'Updated By'
        ],
        'YOUTUBE': [
            'Source ID',
            'Channel Name',
            'Channel URL',
            'Created By',
            'Updated By'
        ]
    }

    all_audio_sources = speakermeta.find(
        {'projectname': activeprojectname, 'isActive': 1},
        {'audioSource': 1, 'audioSubSource': 1, 'metadataSchema': 1, '_id': 0}
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
                allspeakerdetails = get_field_speaker_details(
                    activeprojectname, speakermeta)
                # allspeakerdetails[current_schema.upper()] = metadata

    for source in allspeakerdetails:
        all_lengths[source] = len(allspeakerdetails[source])

    return allspeakerdetails, all_lengths, all_keys


def get_field_speaker_details(activeprojectname, speakermeta):
    data_table = {}
    # fieldspeakerdetails = speakermeta.find(
    #     {"isActive": 1, "projectname": activeprojectname,
    #      'audioSource': 'field'}, {
    #         "lifesourceid": 1,
    #         "audioSource": 1,
    #         "metadataSchema": 1,
    #         "current.updatedBy": 1,
    #         "current.sourceMetadata.name": 1,
    #         "current.sourceMetadata.ageGroup": 1,
    #         "current.sourceMetadata.gender": 1,
    #         "createdBy": 1,
    #         "_id": 0})
    fieldspeakerdetails = speakermeta.find(
        {"isActive": 1, "projectname": activeprojectname,
         'audioSource': 'field'}, {
            "lifesourceid": 1,
            "audioSource": 1,
            "metadataSchema": 1,
            "current.updatedBy": 1,
            "current.sourceMetadata": 1,
            "createdBy": 1,
            "_id": 0})

    for data in fieldspeakerdetails:
        meta_schema = data.get("metadataSchema", "").upper()
        # Mapping for old schema to new schema
        if meta_schema == "":
            new_meta = map_old_speed_to_new(
                data["current"]["sourceMetadata"])
            data["current"]["sourceMetadata"] = new_meta
            meta_schema = "SPEED"
        # data_table.append(data)
        # Grouped by schema
        # TODO: use aggregation to do this grouping in Mongo query itself
        if meta_schema in data_table:
            data_table[meta_schema].append(data)
        else:
            data_table[meta_schema] = [data]

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
                "audioSource": 1,
                "metadataSchema": 1,
                'current.updatedBy': 1,
                'current.sourceMetadata': 1,
                # 'current.sourceMetadata.channelName': 1,
                # 'current.sourceMetadata.channelUrl': 1,
                '_id': 0}
    )

    for data in youtube_speaker_details:
        meta_schema = data.get("metadataScheme", "")
        # Mapping for old schema to new schema
        if meta_schema == "":
            new_meta = map_old_speed_to_new(
                data["current"]["sourceMetadata"])
            data["current"]["sourceMetadata"] = new_meta
        data_table.append(data)

    return data_table


def getonespeakerdetails(activeprojectname, lifesourceid, speakermeta):
    speakerdetails = speakermeta.find_one({"projectname": activeprojectname, "lifesourceid": lifesourceid},
                                          {"_id": 0,
                                           "audioSource": 1,
                                           "metadataSchema": 1,
                                           "current.sourceMetadata": 1,
                                           "lifesourceid": 1})
    meta_schema = speakerdetails.get("metadataSchema", "")
    source = speakerdetails["audioSource"]
    # Mapping for old schema to new schema
    if meta_schema == "":
        new_speaker_meta = map_old_speed_to_new(
            speakerdetails["current"]["sourceMetadata"])
        speakerdetails["current"]["sourceMetadata"] = new_speaker_meta
        if source == "internet":
            speakerdetails["metadataSchema"] = "youtube"
        else:
            speakerdetails["metadataSchema"] = "speed"

    return speakerdetails


def map_columnname_to_mongo_key(columname):
    new_col_name = columname.title().replace(' ', '')
    new_col_name = new_col_name[0].lower() + new_col_name[1:].strip()
    new_col_name = new_col_name.replace('-List', '-list')
    return new_col_name


def map_old_speed_to_new(old_metadata):
    new_metadata = {}
    old_to_new_map = {
        "name": "name",
        "agegroup": "ageGroup",
        "gender": "gender",
        "educationlevel": "educationLevel",
        "educationmediumupto12": "educationMediumUpto12-list",
        "educationmediumafter12": "educationMediumAfter12-list",
        "speakerspeaklanguage": "otherLanguages-list",
        "recordingplace": "placeOfRecording",
        "typeofrecordingplace": "typeOfPlace",
        "channelName": "youtubeChannelName",
        "channelUrl": "youtubeChannelUrl"
    }

    for key, val in old_metadata.items():
        if key in old_to_new_map:
            new_metadata[old_to_new_map[key]] = val
            # del old_metadata[key]
        else:
            new_metadata[key] = val

    return new_metadata


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


def get_source_id(audio_source, metadata_schema, metadata_data):
    source_id = ''
    if 'speed' in metadata_schema:
        name = metadata_data.get('name', "")
        age = metadata_data.get('ageGroup', "")
        source_id = generate_speaker_id(name, age)
    elif 'ldcil' in metadata_schema:
        age_map = {'16To20': '1', '21To50': '2', 'Above50': '3'}
        name = metadata_data.get('name', "")
        age = metadata_data.get('ageGroup', "")
        age = age_map.get(age, "4")
        language = metadata_data.get('language', "")
        language = language[0:2]
        gender = metadata_data.get('gender', "")
        gender = gender[0]
        first_arg = language+gender+age
        source_id = generate_speaker_id(first_arg, name).upper()
    elif 'youtube' in metadata_schema:
        cname = metadata_data.get('youtubeChannelName', "")
        source_id = generate_speaker_id(cname)
    else:
        source_id = generate_speaker_id(metadata_schema+'speaker')

    return source_id


def write_speaker_metadata(speakerdetails,
                           projectowner,
                           activeprojectname,
                           current_username,
                           audio_source,
                           metadata_schema,
                           metadata_data,
                           source_id,
                           upload_type,
                           additional_info):

    current_dt = str(datetime.now()).replace('.', ':')
    logger.debug('Metadata schema %s', metadata_schema)
    # metadata_schema = audio_subsource
    # if 'field' in audio_source:
    #     audio_subsource = ''
    source_data = {"username": projectowner,
                   "projectname": activeprojectname,
                   "lifesourceid": source_id,
                   "createdBy": current_username,
                   "audioSource": audio_source,
                   "audioSubSource": metadata_schema,
                   "metadataSchema": metadata_schema,
                   "uploadType": upload_type,
                   "additionalInfo": additional_info,
                   "current": {
                       "updatedBy": current_username,
                       "sourceMetadata": metadata_data,
                       "current_date": current_dt,
                   },
                   "uploadedAt": current_dt,
                   "isActive": 1}
    logger.debug('Data to inser %s', source_data)
    speakerdetails.insert_one(source_data)


def write_bulk_speaker_metadata(speakerdetails,
                                projectowner,
                                activeprojectname,
                                current_username,
                                audio_source,
                                metadata_schema,
                                metadata_file,
                                additional_info):
    excel_data = pd.read_excel(metadata_file, engine="openpyxl")
    data_columns = excel_data.columns
    data_columns = [map_columnname_to_mongo_key(col) for col in data_columns]
    excel_data.columns = data_columns
    excel_data.fillna('', inplace=True)

    for data_column in data_columns:
        if data_column.endswith('-list'):
            excel_data[data_column] = excel_data[data_column].apply(
                lambda x: x.split(','))
    # if 'field' in audio_source:
    # if 'educationmediumupto12' in data_columns:
    #     excel_data['educationmediumupto12'] = excel_data['educationmediumupto12'].apply(
    #         lambda x: x.split(','))
    # if 'educationmediumafter12' in data_columns:
    #     excel_data['educationmediumafter12'] = excel_data['educationmediumafter12'].apply(
    #         lambda x: x.split(','))
    # if 'speakerspeaklanguage' in data_columns:
    #     excel_data['speakerspeaklanguage'] = excel_data['speakerspeaklanguage'].apply(
    #         lambda x: x.split(','))

    all_records = excel_data.to_dict(orient='records')
    additional_info['totalRecordsUploaded'] = len(all_records)

    for i, current_record in enumerate(all_records):
        additional_info['currentRecordNumber'] = i
        # upload_type = 'single'
        # write_speaker_metadata_details(speakerdetails,
        #                                projectowner,
        #                                activeprojectname,
        #                                current_username,
        #                                audio_source,
        #                                audio_subsource,
        #                                current_record,
        #                                upload_type)
        source_id = get_source_id(
            audio_source, metadata_schema, current_record)
        upload_type = 'bulk'
        write_speaker_metadata(speakerdetails,
                               projectowner,
                               activeprojectname,
                               current_username,
                               audio_source,
                               metadata_schema,
                               current_record,
                               source_id,
                               upload_type,
                               additional_info)


def write_speaker_metadata_details(speakerdetails,
                                   projectowner,
                                   activeprojectname,
                                   current_username,
                                   audio_source,
                                   metadata_schema,
                                   metadata_data,
                                   upload_type,
                                   **kwargs):

    logger.debug('Metadata schema %s', metadata_schema)
    additional_info = {}

    for key, val in kwargs.items():
        additional_info[key] = val

    if upload_type == 'bulk':
        metadata_data = write_bulk_speaker_metadata(speakerdetails,
                                                    projectowner,
                                                    activeprojectname,
                                                    current_username,
                                                    audio_source,
                                                    metadata_schema,
                                                    metadata_data,
                                                    additional_info)
    else:
        source_id = get_source_id(audio_source, metadata_schema, metadata_data)
        logger.debug('Source ID %s', source_id)

        write_speaker_metadata(speakerdetails,
                               projectowner,
                               activeprojectname,
                               current_username,
                               audio_source,
                               metadata_schema,
                               metadata_data,
                               source_id,
                               upload_type,
                               additional_info)
