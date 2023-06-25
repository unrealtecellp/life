from pprint import pformat
from datetime import datetime
from app.controller import (
    getuserprojectinfo,
    getcommentstats,
    life_logging
)
from app.lifedata.controller import (
    sourceid_to_souremetadata
)

logger = life_logging.get_logger()

def get_annotation_data(projects_collection,
                        userprojects_collection,
                        annotation_collection,
                        tagsets_collection,
                        sourcedetails_collection,
                        current_username,
                        activeprojectname):
    project_details = {}
    try:
        project_info = projects_collection.find_one({"projectname": activeprojectname},
                                                  {
                                                      "_id": 0,
                                                      "sourceIds."+current_username: 1,
                                                      "tagsetId": 1,
                                                      "lastActiveId."+current_username: 1,
                                                      "projectOwner": 1,
                                                      "derivedFromProject": 1 
                                                    }
                                                )
        currentuser_projectinfo = getuserprojectinfo.getuserprojectinfo(userprojects_collection,
                                                                        current_username,
                                                                        activeprojectname)
        shareinfo = currentuser_projectinfo
        derive_from_project_name = project_info["derivedFromProject"][0]
        if (project_info["sourceIds"]):
            source_ids = project_info["sourceIds"][current_username]
            source_metadata = sourceid_to_souremetadata.get_source_metadata(sourcedetails_collection,
                                                                            source_ids,
                                                                            derive_from_project_name)
            source_ids.append('')
        else:
            source_ids = ['']
        projectowner = project_info['projectOwner']
        tag_set_id = project_info["tagsetId"]
        tag_set = tagsets_collection.find_one({"_id": tag_set_id})
        if ('activesourceId' in currentuser_projectinfo):
            active_source_id = currentuser_projectinfo['activesourceId']
        else:
            active_source_id = ''
        last_active_id = project_info["lastActiveId"][current_username][active_source_id]['dataId']
        total_comments, annotated_comments, remaining_comments = getcommentstats.getdatacommentstatsnew(annotation_collection,
                                                                                                        activeprojectname,
                                                                                                        active_source_id,
                                                                                                        'datadeleteFLAG')
        data_info = annotation_collection.find_one({
                                                    "projectname": activeprojectname,
                                                    "lifesourceid": active_source_id,
                                                    "dataId": last_active_id
                                                    },
                                                    {
                                                        "_id": 0,
                                                        "dataId": 1,
                                                        "Data": 1,
                                                        "dataMetadata": 1,
                                                        current_username: 1
                                                    }
                                                    )
        # logger.debug('data_info: %s', pformat(data_info))
        project_details["projectOwner"] = projectowner
        project_details['activesourceId'] = active_source_id
        project_details['sourceIds'] = source_ids
        project_details['shareInfo'] = shareinfo
        project_details['sourceMetadata'] = source_metadata
        project_details['tagSet'] = tag_set['tagSet']
        project_details['tagSetMetaData'] = tag_set['tagSetMetaData']
        project_details['lastActiveId'] = last_active_id
        project_details['totalComments'] = total_comments
        project_details["annotatedComments"] = annotated_comments
        project_details["remainingComments"]  = remaining_comments
        project_details['textData'] = {
                                                "ID": data_info["dataId"],
                                                "Text": data_info["Data"]
                                            }
        project_details['textMetadata'] = data_info['dataMetadata']
        if (current_username in data_info):
            project_details[current_username] = data_info[current_username]['annotationGrid']
            currentAnnotation = project_details[current_username]
            # logger.debug('currentAnnotation: %s', pformat(currentAnnotation))
            defaultAnnotation = project_details['tagSetMetaData']['defaultCategoryTags']
            project_details['tagSetMetaData']['defaultCategoryTags'] = {**defaultAnnotation, **currentAnnotation}
        project_details['accessedOnTime'] = datetime.now().strftime("%d/%m/%y %H:%M:%S")
        project_details["currentUser"] = current_username
        

        # logger.debug('project_details get_annotation_data() %s', pformat(project_details))
        # logger.debug('project_details get_annotation_data() %s', pformat(list(project_details.keys())))
    except:
        logger.exception("")

    return project_details

def get_annotation_ids_list(data_collection,
                            active_project_name,
                            active_source_id):
    allIds = []
    try:
        dataIds = data_collection.find({"projectname": active_project_name, 
                                        "lifesourceid": active_source_id},
                                        {"_id": 0, "dataId": 1})

        if (dataIds != None):
            for dataId in dataIds:
                allIds.append(dataId["dataId"])
    except:
        logger.exception("")

    return allIds

def getnewdataid(projects,
                  activeprojectname,
                  last_active_id,
                  active_source_id,
                  which_one):
    """_summary_

    Args:
        projects (_type_): _description_
        activeprojectname (_type_): _description_
        last_active_id (_type_): _description_
        which_one (_type_): _description_
    """
    data_ids_list = projects.find_one({'projectname': activeprojectname},
                                       {'_id': 0, 'sourcedataIds': 1})
    # logger.debug('data_ids_list', data_ids_list)
    if len(data_ids_list) != 0:
        data_ids_list = data_ids_list['sourcedataIds'][active_source_id]
        # logger.debug('data_ids_list: %s', data_ids_list)
    if (len(data_ids_list) != 0):
        if (last_active_id in data_ids_list):
            data_id_index = data_ids_list.index(last_active_id)
        else:
            data_id_index = 0
        # logger.debug('latestdataId Index!!!!!!!', data_id_index)
        if which_one == 'previous':
            data_id_index = data_id_index - 1
        elif which_one == 'next':
            if len(data_ids_list) == (data_id_index+1):
                data_id_index = 0
            else:
                data_id_index = data_id_index + 1
        latest_data_id = data_ids_list[data_id_index]
    else:
        latest_data_id = ''
    # logger.debug('latest_data_id dataDETAILS: %s', latest_data_id)

    return latest_data_id


def updatelatestdataid(projects,
                        activeprojectname,
                        latest_data_id,
                        current_username,
                        active_source_id):
    """_summary_

    Args:
        projects (_type_): _description_
        activeprojectname (_type_): _description_
        latest_data_id (_type_): _description_
        current_username (_type_): _description_
    """
    projects.update_one({'projectname': activeprojectname},
                        {'$set': {'lastActiveId.'+current_username+'.'+active_source_id+'.dataId':  latest_data_id}})

