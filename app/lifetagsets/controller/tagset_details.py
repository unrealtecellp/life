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


def get_tagset_details(tagset_collection, current_username):
    tagset_details = tagset_collection.find({
        "$or": [
            {'projectDeleteFLAG': 0, 'isPublic': 1},
            {'projectDeleteFLAG': 0, 'projectOwner': current_username},
            {'projectDeleteFLAG': 0, 'sharedwith': {"$in": [current_username]}}
        ]
    }, {
        'projectname': 1,
        'tagSetMetadata': 1
    })


def update_use_in_project(tagset_collection, tagset_name, use_in_project):
    tagset_collection.update_one(
        {'projectname': tagset_name, 'projectDeleteFLAG': 0, 'projectType': 'tagset'},
        {'$addToSet': {'useInProjects': use_in_project}})
