from app.controller import (
    life_logging
)

logger = life_logging.get_logger()


def get_metadata_header_details(form_data, exclude_fields=[]):
    if len(exclude_fields) == 0:
        exclude_fields = ['audiosource', 'sourcecallpage',
                          'fieldMetadataSchema', 'metadataentrytype', 'audioInternetSource']

    audio_source = form_data.get('audiosource', '')
    call_source = form_data.get('sourcecallpage', '')

    if audio_source == 'field' and 'fieldMetadataSchema' in form_data:
        logger.debug('Metadata schema found!')
        metadata_schema = form_data.get('fieldMetadataSchema', '')
        logger.debug('Metadata schema name %s', metadata_schema)
    # if metadata_schema == '':
    elif audio_source == 'internet' and 'audioInternetSource' in form_data:
        metadata_schema = form_data.get('audioInternetSource', '')
    else:
        logger.debug('Metadata schema not found found!')
        metadata_schema = ''

    upload_type = form_data.get('metadataentrytype', '')

    return metadata_schema, audio_source, call_source, upload_type, exclude_fields


def get_metadata_data(form_data, form_files=None, upload_type='single', exclude_fields=[]):
    metadata_data = {}

    if upload_type == 'single':
        for field_name in form_data:
            if field_name not in exclude_fields:
                field_data = form_data.getlist(field_name)
                logger.debug('Field name %s', field_name)
                if (not field_name.endswith('-list')) and (len(field_data) == 1):
                    field_data = field_data[0]
                metadata_data[field_name] = field_data
    else:
        if form_files is not None:
            metadata_data = form_files.to_dict().get('metadatafile', '')

    return metadata_data
