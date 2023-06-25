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
        source_metadata_cursor = sourcedetails_collection.find({"projectname": activeprojectname},
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
