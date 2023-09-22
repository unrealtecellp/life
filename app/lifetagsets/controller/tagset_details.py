'''
Module to manage the tagset collection
'''
from app.controller import (
    life_logging
)

logger = life_logging.get_logger()


def get_full_tagset(tagset_collection, tagset_name):
    full_tagset = tagset_collection.find_one(
        {'projectname': tagset_name, 'projectDeleteFLAG': 0, 'projectType': 'tagset'}, {'tagSet': 1, '_id': 0})
    if 'tagSet' in full_tagset:
        return full_tagset['tagSet']
    else:
        return []


def get_full_tagset_with_metadata(tagset_collection, tagset_name):
    full_tagset = tagset_collection.find_one(
        {'projectname': tagset_name, 'projectDeleteFLAG': 0, 'projectType': 'tagset'}, {'tagSet': 1, 'tagSetMetaData': 1, '_id': 0})

    if 'tagSet' in full_tagset:
        return full_tagset
    else:
        return []


def get_tagset_id(tagset_collection, tagset_name):
    tagset_id = tagset_collection.find_one(
        {'projectname': tagset_name, 'projectDeleteFLAG': 0, 'projectType': 'tagset'}, {'_id': 1})
    if '_id' in tagset_id:
        return tuple(tagset_id['_id'])
    else:
        return tuple()


def get_all_tagset_details(tagset_collection, current_username):
    tagset_details = tagset_collection.find({
        "$or": [
            {'projectdeleteFLAG': 0, 'isPublic': 1},
            {'projectdeleteFLAG': 0, 'projectOwner': current_username},
            {'projectdeleteFLAG': 0, 'sharedwith': {"$in": [current_username]}}
        ]
    }, {
        'projectname': 1,
        'tagSetMetadata': 1,
        'tagSet': 1,
        'projectOwner': 1,
        'updatedBy': 1
    })

    all_tagset_details = list(tagset_details)
    all_tagsets = {'Tagsets': all_tagset_details}
    tagset_length = {'Tagsets': len(all_tagset_details)}
    all_keys = {'Tagsets': ['Tagset Name',
                            'Tagset', 'Created by', 'Updated by']}
    logger.debug('All tagsets %s', all_tagsets)

    return all_tagsets, tagset_length, all_keys
