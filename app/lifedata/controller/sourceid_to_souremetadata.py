from app.controller import (
    life_logging
)
from pprint import pformat

logger = life_logging.get_logger()


def get_source_metadata(sourcedetails_collection,
                        sourceids,
                        activeprojectname):
    sources_metadata = {}
    try:
        # logger.debug('sourceids: %s', pformat(sourceids))
        source_metadata_cursor = sourcedetails_collection.find({"projectname": activeprojectname, "sourcedeleteFLAG": 0},
                                                               {"_id": 0,
                                                                "lifesourceid": 1,
                                                                "current.sourceMetadata": 1})
        for source_metadata in source_metadata_cursor:
            lifesourceid = source_metadata['lifesourceid']
            if (lifesourceid in sourceids):
                sources_metadata[lifesourceid] = source_metadata['current']['sourceMetadata']
                # logger.debug('source_metadata: %s', pformat(source_metadata))
    except:
        logger.exception("")

    return sources_metadata


def get_data_types(sourcedetails_collection,
                   sourceid,
                   activeprojectname):
    data_type = []
    try:
        # logger.debug('sourceids: %s', pformat(sourceids))
        source_metadata_cursor = sourcedetails_collection.find_one({"projectname": activeprojectname, "lifesourceid": sourceid, "sourcedeleteFLAG": 0},
                                                                   {"_id": 0,
                                                                    "dataType": 1})
        if "dataType" in source_metadata_cursor:
            data_type = source_metadata_cursor["dataType"]
        else:
            data_type = []
            # logger.debug('source_metadata: %s', pformat(source_metadata))
    except:
        logger.exception("")

    return data_type
