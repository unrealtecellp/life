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
            'Participant Id',
            'Participant Role',
            'Age Group',
            'Gender',
            'Class Section',
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

def karya_new_updateonespeakerdetails(activeprojectname, lifesourceid, all_details, speakermeta):
    print("All details", all_details)
    print("Life source ID", lifesourceid)
    status = speakermeta.update_one({"projectname": activeprojectname, "lifesourceid": lifesourceid, 
                                     "additionalInfo.karya_version":"karya_main"},
                                    {"$set": all_details})

    return status.raw_result


def update_bulk_multilila_data(metadata_data):
    logger.info("Updating bulk data %s", metadata_data)
    update_vals = {}

    multilila_medium = {
        "Only English": "1",
        "Telugu+English": "2",
        "Hindi+English": "3",
        "Assamese+English": "4"
    }
    site_types = {
        "Slum": "1",
        "Non-slum": "2",
        "Remote Rural": "3",
        "Non-remote Rural": "4"
    }
    cities = {
        "Delhi": "1",
        "Hyderabad": "2",
        "Patna": "3",
        "Guwahati": "4"
    }

    participant_type = metadata_data.get('participantRole', '')
    participant_type = map_columnname_to_mongo_key(participant_type)
    update_vals['participantRole'] = participant_type

    medium = metadata_data.get('mediumOfEducation-list', [''])
    new_medium = []
    for i, current_medium in enumerate(medium):
        current_medium = current_medium.strip()
        if len(current_medium) > 0:
            new_medium.append(multilila_medium.get(
                current_medium.strip(), current_medium.strip()))
    if len(new_medium) > 0:
        update_vals['mediumOfEducation-list'] = new_medium

    subject = metadata_data.get('subjectArea', '')
    if len(subject) > 0:
        update_vals['subjectArea'] = subject[0]

    school_type = metadata_data.get('schoolType', '')
    if len(school_type) > 0:
        update_vals['schoolType'] = school_type[0]

    site_type = metadata_data.get('siteType', '')
    if len(site_type) > 0 and site_type in site_types:
        update_vals['siteType'] = site_types.get(site_type, site_type)

    city = metadata_data.get('city', '')
    if len(city) > 0 and city in cities:
        update_vals['city'] = cities.get(city, city)

    logger.info("Updated Values %s\nOriginal Val %s",
                update_vals, metadata_data)

    insert_ids_into_multilila_data(metadata_data, data=update_vals)


def generate_speaker_id(name, age='000'):
    name = name.replace(" ", "").replace(".", "").lower()
    age = age.replace("-", "")
    if name == '':
        name = 'undefined'
    if age == '':
        age = '000'
    elif age == '-1':
        age = ''
    new_speaker_id = name+age+'_'+re.sub(r'[-: \.]', '', str(datetime.now()))

    return new_speaker_id


def insert_ids_into_multilila_data(metadata_data, **kwargs):
    for data_type, vals in kwargs.items():
        for field, field_val in vals.items():
            metadata_data[field] = field_val
    # metadata_data['learnerId'] = learner_id
    # metadata_data['teacherId'] = teacher_id
    # metadata_data['researcherId'] = ra_id


def get_speed_source_id(metadata_data):
    name = metadata_data.get('name', "")
    age = metadata_data.get('ageGroup', "")
    source_id = generate_speaker_id(name, age)
    return source_id


def get_ldcil_source_id(metadata_data):
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
    return source_id


def get_multilila_ids_and_source_id(metadata_schema, metadata_data):
    additional_vals = {}

    learner_id = ''
    teacher_id = ''
    ra_id = ''

    participant_type = metadata_data.get('participantRole', '')
    # participant_type = map_columnname_to_mongo_key(participant_type)
    # logger.info('Participant Type %s', participant_type)

    school_sno = str(metadata_data.get('schoolSerialNumber', '0'))
    school_type = str(metadata_data.get('schoolType', '0'))
    site_type = str(metadata_data.get('siteType', '0'))
    city = str(metadata_data.get('city', '0'))

    school_id = city+site_type+school_type+school_sno
    additional_vals['schoolId'] = school_id

    if participant_type == 'learner':
        class_section = metadata_data.get('classSection', '0')
        gender = metadata_data.get('gender', 'N')
        name = metadata_data.get('name', '')
        initials = ''.join([x[0].upper() for x in name.split(' ')])
        learner_id = school_id+class_section+gender[0]+initials
        participant_id = learner_id
        source_id = generate_speaker_id('L'+learner_id, '-1')
    elif participant_type == 'teacher':
        gender = metadata_data.get('gender', 'N')
        subject = metadata_data.get('subjectArea', 'N')
        teacher_id = school_id+subject[0]+gender[0]
        participant_id = teacher_id
        source_id = generate_speaker_id('T'+teacher_id, '-1')
    elif participant_type == 'researchAssistant':
        name = metadata_data.get('name', '')
        ra_id = ''.join(name.split(' '))
        participant_id = ra_id
        source_id = generate_speaker_id('R'+ra_id, '-1')
    else:
        source_id = generate_speaker_id(metadata_schema+'speaker')
        participant_id = source_id

    additional_vals['learnerId'] = learner_id
    additional_vals['researcherId'] = ra_id
    additional_vals['teacherId'] = teacher_id
    additional_vals['participantId'] = participant_id
    insert_ids_into_multilila_data(metadata_data, data=additional_vals)

    return source_id


def get_youtube_source_id(metadata_data):
    cname = metadata_data.get('youtubeChannelName', "")
    source_id = generate_speaker_id(cname)
    return source_id


def get_source_id(audio_source, metadata_schema, metadata_data):
    source_id = ''
    if 'speed' in metadata_schema:
        source_id = get_speed_source_id(metadata_data)
    elif 'ldcil' in metadata_schema:
        source_id = get_ldcil_source_id(metadata_data)
    elif 'multilila' in metadata_schema:
        source_id = get_multilila_ids_and_source_id(
            metadata_schema, metadata_data)
    elif 'youtube' in metadata_schema:
        source_id = get_youtube_source_id(metadata_data)
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

def karya_new_write_speaker_metadata(speakerdetails,
                           projectowner,
                           activeprojectname,
                           current_username,
                           audio_source,
                           metadata_schema,
                           metadata_data,
                           lifespeakerid_var,
                           source_id,
                           upload_type,
                           additionalInfo_var):

    current_dt = str(datetime.now()).replace('.', ':')
    logger.debug('Metadata schema %s', metadata_schema)
    # metadata_schema = audio_subsource
    # if 'field' in audio_source:
    #     audio_subsource = ''
    print('###################################################')
    print('additional_info from the function karya_new_write_speaker_metadata: ', additionalInfo_var)
    print('###################################################')

    source_data = {"username": projectowner,
                   "projectname": activeprojectname,
                   "lifesourceid": lifespeakerid_var,
                   "createdBy": current_username,
                   "audioSource": audio_source,
                   "audioSubSource": metadata_schema,
                   "metadataSchema": metadata_schema,
                   "uploadType": upload_type,
                   "additionalInfo": additionalInfo_var,
                   "current": {
                       "updatedBy": current_username,
                       "sourceMetadata": metadata_data,
                       "current_date": current_dt,
                   },
                   "uploadedAt": current_dt,
                   "isActive": 1,
                   "old_lifesourceid": source_id}
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
    excel_data = pd.read_excel(metadata_file, engine="openpyxl", dtype=str)
    data_columns = excel_data.columns
    data_columns = [map_columnname_to_mongo_key(col) for col in data_columns]
    excel_data.columns = data_columns
    excel_data = excel_data.dropna(how="all", axis=1)
    excel_data = excel_data.fillna('')

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
        if metadata_schema == 'multilila':
            update_bulk_multilila_data(current_record)
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







def karya_new_write_speaker_metadata_details(speakerdetails,
                                   projectowner,
                                   activeprojectname,
                                   current_username,
                                   audio_source,
                                   metadata_schema,
                                   lifespeakerid_var,
                                   metadata_data,
                                   upload_type,
                                   additionalInfo_var,
                                   **kwargs):

    logger.debug('Metadata schema %s', metadata_schema)

    # for key, val in kwargs.items():
    #     additionalInfo_var[key] = val
    print("additionalInfo_var from function karya_new_write_speaker_metadata_details:" ,  additionalInfo_var)

    if upload_type == 'bulk':
        write_bulk_speaker_metadata(speakerdetails,
                                                projectowner,
                                                activeprojectname,
                                                current_username,
                                                audio_source,
                                                metadata_schema,
                                                metadata_data,
                                                additionalInfo_var)
    else:
        source_id = get_source_id(audio_source, metadata_schema, metadata_data)
        logger.debug('Source ID %s', source_id)

        karya_new_write_speaker_metadata(speakerdetails,
                               projectowner,
                               activeprojectname,
                               current_username,
                               audio_source,
                               metadata_schema,
                               metadata_data,
                               lifespeakerid_var,
                               source_id,
                               upload_type,
                               additionalInfo_var)
