from pprint import pformat
from datetime import datetime
from zipfile import ZipFile
import pandas as pd
import xmltodict
import io
from flask import flash, redirect, url_for
import re
from app.controller import (
    getuserprojectinfo,
    getcommentstats,
    life_logging
)
from app.lifedata.controller import (
    sourceid_to_souremetadata,
    save_crawled_data
)

from app.lifeuploader.controller import (
    processExternalFiles
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
        # logger.debug("activeprojectname: %s", pformat(activeprojectname))
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
        # logger.debug("project_info: %s", pformat(project_info))
        if not project_info:
            return project_details
        currentuser_projectinfo = getuserprojectinfo.getuserprojectinfo(userprojects_collection,
                                                                        current_username,
                                                                        activeprojectname)
        last_active_id = ''
        shareinfo = currentuser_projectinfo
        # logger.debug("currentuser_projectinfo: %s", pformat(currentuser_projectinfo))
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
            # logger.debug("active_source_id: %s", active_source_id)
            if (len(active_source_id) != 0):
                last_active_id = project_info["lastActiveId"][current_username][active_source_id]['dataId']
        else:
            active_source_id = ''

        total_comments, annotated_comments, remaining_comments = getcommentstats.getdatacommentstatsnew(annotation_collection,
                                                                                                        activeprojectname,
                                                                                                        active_source_id,
                                                                                                        'annotatedFLAG')
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
        project_details["remainingComments"] = remaining_comments
        if (data_info):
            project_details['textData'] = {
                "ID": data_info["dataId"],
                "Text": data_info["Data"]
            }
            project_details['textMetadata'] = data_info['dataMetadata']
        else:
            project_details['textData'] = {
                "ID": '',
                "Text": ''
            }
            project_details['textMetadata'] = {}
        if (current_username in data_info):
            project_details[current_username] = data_info[current_username]['annotationGrid']
            currentAnnotation = project_details[current_username]
            # logger.debug('currentAnnotation: %s', pformat(currentAnnotation))
            defaultAnnotation = project_details['tagSetMetaData']['defaultCategoryTags']
            project_details['tagSetMetaData']['defaultCategoryTags'] = {
                **defaultAnnotation, **currentAnnotation}
        project_details['accessedOnTime'] = datetime.now().strftime(
            "%d/%m/%y %H:%M:%S")
        project_details["currentUser"] = current_username

        logger.debug('project_details get_annotation_data() %s',
                     pformat(project_details))
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


def get_text_data_id(id_prefix='F', id_suffix="no_filename"):
    data_id = id_prefix+re.sub(r'[-: \.]', '',
                               str(datetime.now())) + '_' + id_suffix

    return data_id


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


def update_source_id_list(projects_collection, project_name, sourcedata_ids, current_username):
    source_Ids_list = []
    lastActiveId = {current_username: {}}
    for key in sourcedata_ids.keys():
        source_Ids_list.append(key)
        lastActiveId[current_username][key] = {
            "dataId": sourcedata_ids[key][0]}
    # logger.debug("source_Ids_list: %s", pformat(source_Ids_list))
    # logger.debug("lastActiveId: %s", pformat(lastActiveId))
    projects_collection.update_one({"projectname": project_name},
                                   {"$set": {
                                       "lastActiveId."+current_username: lastActiveId[current_username],
                                       "sourceIds."+current_username: source_Ids_list,
                                       "sourcedataIds": sourcedata_ids
                                   }})
    return source_Ids_list


def save_multiple_files_data(projects_collection,
                             userprojects_collection,
                             data_collection,
                             project_name,
                             current_username,
                             zip_file,
                             file_format,
                             csv_delimiter=',',
                             preprocess=False,
                             preprocess_pipeline='ldcil_pos_hin',
                             is_annotated=False,
                             annotation_tagset='',
                             annotation_types=[],
                             annotation_delimiter='\\',
                             **kwargs):
    sourcedata_ids = {}

    file_metadata = {}

    for key, val in kwargs.items():
        file_metadata[key] = val
    try:
        with ZipFile(zip_file) as myzip:
            for file_name in myzip.namelist():
                with myzip.open(file_name) as myfile:
                    try:
                        # if file_name.endswith('.tsv'):
                        source_ids = save_one_file_data(data_collection,
                                                        project_name,
                                                        current_username,
                                                        myfile,
                                                        file_name,
                                                        file_format,
                                                        csv_delimiter,
                                                        file_metadata,
                                                        preprocess,
                                                        preprocess_pipeline,
                                                        is_annotated,
                                                        annotation_tagset,
                                                        annotation_types,
                                                        annotation_delimiter
                                                        )
                        sourcedata_ids.update(source_ids)
                    except:
                        logger.exception("")
                        flash(
                            f"File: {file_name} is not in correct format. Please check")
                        return redirect(url_for('lifedata.home'))

        # logger.debug("sourcedata_ids: %s", pformat(sourcedata_ids))

        if len(sourcedata_ids) > 0:
            source_Ids_list = update_source_id_list(projects_collection, project_name,
                                                    sourcedata_ids, current_username)

            save_crawled_data.update_active_source_id(userprojects_collection,
                                                      project_name,
                                                      current_username,
                                                      current_username,
                                                      source_Ids_list[0])
    except:
        logger.exception("")
        flash(f"File: {file_name} is not in correct format. Please check")
        return redirect(url_for('lifedata.home'))
    return source_Ids_list


def save_one_file_data(data_collection,
                       project_name,
                       current_username,
                       myfile,
                       file_name,
                       file_format,
                       csv_delimiter=',',
                       file_metadata={},
                       preprocess=False,
                       preprocess_pipeline='ldcil_pos_hin',
                       is_annotated=False,
                       annotation_tagset='',
                       annotation_types=[],
                       annotation_delimiter='\\',
                       **kwargs):
    data_metadata = {}
    source_ids = {}

    for key, val in kwargs.items():
        file_metadata[key] = val
    # metadata.update(data_metadata)
    try:
        current_file_data, metadata_data, metadata_file = processExternalFiles.parse_one_file_data(io.BytesIO(
            myfile.read()), file_name, file_format, csv_delimiter, is_annotated, annotation_tagset, annotation_types, annotation_delimiter, preprocess, preprocess_pipeline)
        data_metadata.update(metadata_data)
        file_metadata.update(metadata_file)

        if len(current_file_data) > 0:
            # if preprocess:
            #     data_df = processExternalFiles.preprocess_df(
            #         data_df, preprocess_pipeline)

            # current_file_data = data_df.to_dict(orient='index')

            for rec_index in current_file_data:
                current_record = current_file_data[rec_index]

                lifesourceid, data_id = save_one_text_data_instance(data_collection,
                                                                    project_name,
                                                                    current_username,
                                                                    current_record.get(
                                                                        'Text', ''),
                                                                    current_record.get(
                                                                        'ID', ''),
                                                                    len(current_file_data),
                                                                    rec_index,
                                                                    file_name,
                                                                    annotations=current_record.get(
                                                                        'Annotation_Grid', dict()),
                                                                    data_metadata=data_metadata,
                                                                    additional_info=file_metadata)
                if (lifesourceid in source_ids):
                    source_ids[lifesourceid].append(data_id)
                else:
                    source_ids[lifesourceid] = [data_id]
    except:
        logger.exception("")
        flash(
            f"File: {file_name} is not in correct format. Please check")
        return redirect(url_for('lifedata.home'))

    return source_ids


def save_one_text_data_instance(data_collection,
                                project_name,
                                current_username,
                                current_data,
                                current_data_id,
                                total_data_count,
                                current_data_count,
                                uploaded_file_name,
                                annotations={},
                                data_metadata={},
                                additional_info={},
                                **kwargs
                                ):
    data_anno_detail = {}

    try:
        # for current_data in all_data:
        # logger.debug('crawled_data: %s -> %s', i, pformat(crawled_data))
        # dataId = crawled_data['dataId']
        data_anno_detail['username'] = current_username
        data_anno_detail["projectname"] = project_name
        # data_id = 'T'+re.sub(r'[-: \.]', '', str(datetime.now()))
        data_id = get_text_data_id(
            id_prefix='T', id_suffix=current_data_id)
        data_anno_detail["dataId"] = data_id
        data_anno_detail['dataType'] = "text"
        data_anno_detail['Data'] = current_data
        data_anno_detail['createdBy'] = current_username
        data_anno_detail['lastUpdatedBy'] = current_username
        lifesourceid = get_text_data_id(
            id_prefix='F', id_suffix=uploaded_file_name)
        data_anno_detail['lifesourceid'] = lifesourceid

        data_anno_detail['datadeleteFLAG'] = 0
        data_anno_detail['dataverifiedFLAG'] = 0

        uploaded_file_details = {
            "uploadedFileName": uploaded_file_name,
            "uploadedDataId": current_data_id,
            "totalRows": total_data_count,
            "currentRowNumber": current_data_count
        }
        for key, val in kwargs.items():
            uploaded_file_details[key] = val
        uploaded_file_details.update(additional_info)
        data_anno_detail['additionalInfo'] = uploaded_file_details

        text_metadata = {
            "ID": current_data_id,
            "length": len(current_data),
            "token_count": len(current_data.split())
        }
        text_metadata.update(data_metadata)
        data_anno_detail['dataMetadata'] = text_metadata
        data_anno_detail['prompt'] = ""
        data_anno_detail['annotatedFLAG'] = 0

        # data_anno_detail["textFilename"] = uploaded_file_name
        data_anno_detail['annotationGrid'] = annotations
        if len(annotations) > 0:
            data_anno_detail[current_username] = annotations

        all_access = {}
        data_anno_detail['allAccess'] = all_access
        all_updates = {}
        data_anno_detail['allUpdates'] = all_updates
        data_anno_detail['derivedfromprojectdetails'] = {}
        # logger.debug('data_anno_detail: %s -> %s', i, pformat(data_anno_detail))
        data_collection.insert_one(data_anno_detail)
    except:
        logger.exception("")

    return lifesourceid, data_id
