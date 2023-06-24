from pprint import pformat
from datetime import datetime
from app.controller import (
    getuserprojectinfo,
    getcommentstats,
    life_logging
)

logger = life_logging.get_logger()

def get_annotation_data(projects_collection,
                        userprojects_collection,
                        annotation_collection,
                        tagsets_collection,
                        current_username,
                        activeprojectname):
    project_details = {}
    try:
        active_source_id = getuserprojectinfo.getuserprojectinfo(userprojects_collection,
                                                                    current_username,
                                                                    activeprojectname)['activesourceId']
        project_info = projects_collection.find_one({"projectname": activeprojectname},
                                                  {
                                                      "_id": 0,
                                                      "sourceIds."+current_username: 1,
                                                      "tagsetId": 1,
                                                      "lastActiveId."+current_username: 1
                                                    }
                                                )
        source_ids = project_info["sourceIds"][current_username]
        tag_set_id = project_info["tagsetId"]
        tag_set = tagsets_collection.find_one({"_id": tag_set_id})
        last_active_id = project_info["lastActiveId"][current_username][active_source_id]['dataId']
        total_comments, annotated_comments, remaining_comments = getcommentstats.getdatacommentstatsnew(annotation_collection,
                                                                                                        activeprojectname,
                                                                                                        active_source_id,
                                                                                                        'datadeleteFLAG')
        data_info = annotation_collection.find_one({
                                                    "projectname": activeprojectname,
                                                    "lifesourceid": active_source_id
                                                    },
                                                    {
                                                        "_id": 0,
                                                        "dataId": 1,
                                                        "Data": 1,
                                                        "dataMetadata": 1,
                                                        current_username: 1
                                                    }
                                                    )
        logger.debug('data_info: %s', pformat(data_info))
        project_details['activesourceId'] = active_source_id
        project_details['sourceIds'] = source_ids
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
            project_details[current_username] = data_info[current_username]
        project_details['accessedOnTime'] = datetime.now().strftime("%d/%m/%y %H:%M:%S")
        project_details["currentUser"] = current_username

        logger.debug('project_details get_annotation_data() %s', pformat(project_details))
        logger.debug('project_details get_annotation_data() %s', pformat(list(project_details.keys())))
    except:
        logger.exception("")
    # project_details = projects.find_one({"projectname": activeprojectname},
    #                                     {
    #                                         "_id": 0,
    #                                         "lastActiveId": 1
    #                                     })
    # if project_details != None:
    #     # print(project_details)
    #     if (project_details["projectType"] != "text"):
    #         flash("Active file is 'image' type. Plese select 'text' file to annotate.", 'info')
    #         return redirect(url_for('easyAnno.home'))
        
    #     last_active_id_user = project_details["lastActiveId"]
    #     if (current_username in last_active_id_user):
    #         last_active_id = project_details["lastActiveId"][current_username]
    #     else:
    #         if (project_details["projectType"] == 'text'):
    #             text_data = projects.find_one({"projectname": activeprojectname},
    #                                             {"_id" : 0, "textData": 1 })
    #         for id in text_data.values():
    #             tIds = list(id.keys())
    #         tIds = sorted(tIds)
    #         last_active_id = tIds[0]
    #         projects.update_one({ "projectname": activeprojectname },
    #                                 { '$set' : 
    #                                     { "lastActiveId": {current_username: last_active_id} }})

    #     # print(project_details["textData"][last_active_id])
    #     # print(last_active_id)
        
    #     project_details = projects.find_one({"projectname": activeprojectname},
    #                                         {"_id": 0, 
    #                                          "tagSet": 1, 
    #                                          "tagSetMetaData": 1,
    #                                          "textData."+last_active_id: 1, 
    #                                          "textData": 1})
    #     # print(project_details)
    #     total_comments = len(project_details["textData"])
    #     annotated_comments = 0
    #     for comments in textanno.find({"projectname": activeprojectname},
    #                                     {"projectname": 1, current_username: 1 }):
    #         if (current_username in comments):
    #             annotatedFLAG = comments[current_username]["annotatedFLAG"]
    #             if (annotatedFLAG == 1):
    #                 annotated_comments += 1
    #     remaining_comments = total_comments - annotated_comments

    #     project_details['totalComments'] = total_comments
    #     project_details["annotatedComments"] = annotated_comments
    #     project_details["remainingComments"]  = remaining_comments   
    #     project_details["textData"] = project_details["textData"][last_active_id]
    #     project_details["lastActiveId"] = last_active_id

    #     # print(last_active_id)
    #     text_meta_data = textanno.find_one({"projectname": activeprojectname, "textId": last_active_id},
    #                                         {"_id": 0, "textMetadata": 1 })
    #     if ('textMetadata' in text_meta_data):
    #         project_details["textMetadata"] = text_meta_data["textMetadata"]
    #     else:
    #         for text_data_key, text_data_value in project_details['textData'].items():
    #             # print(text_data_key, text_data_value)
    #             if (text_data_key != 'Text'):
    #                 text_meta_data[text_data_key] = text_data_value
    #         # print(text_meta_data)
    #         textanno.update_one({"projectname": activeprojectname, "textId": last_active_id},
    #                             { '$set' : 
    #                                 {   
    #                                     'textMetadata': text_meta_data
    #                                 }})
            
    #     missing_keys = textanno.find_one({"projectname": activeprojectname, "textId": last_active_id},
    #                                     {"_id": 0})
    #     if ('ID' in missing_keys):
    #         textanno.update_one({"projectname": activeprojectname, "textId": last_active_id},
    #                             {'$unset': {"ID": 1}})
    #     if ('username' not in missing_keys):
    #         textanno.update_one({"projectname": activeprojectname, "textId": last_active_id},
    #                             {'$set': 
    #                                 {
    #                                     "username": projectowner,
    #                                     'lifesourceid': '',
    #                                     'textdeleteFLAG': 0,
    #                                     'textverifiedFLAG': 0,
    #                                     'additionalInfo': {},
    #                                     'prompt': ''
    #                                 }})
    #     if (current_username in missing_keys and 'annotationGrid' not in missing_keys[current_username]):
    #         print('123')
    #         current_user_anno = missing_keys[current_username]
    #         del current_user_anno['annotatedFLAG']
    #         textanno.update_one({"projectname": activeprojectname, "textId": last_active_id},
    #                             {
    #                                 '$unset': {current_username: 1}
    #                             })
    #         textanno.update_one({"projectname": activeprojectname, "textId": last_active_id},
    #                             {
    #                                 '$set': 
    #                                     {
    #                                         current_username: {'annotationGrid': current_user_anno,
    #                                                        "annotatedFLAG": 1}
    #                                     }
    #                             })
    #     last_updated_by = missing_keys['lastUpdatedBy']
    #     if ('annotationGrid' not in missing_keys and last_updated_by != ''):
    #         last_updated_by_user_anno = missing_keys[last_updated_by]
    #         if ('annotationGrid' in last_updated_by_user_anno):
    #             last_updated_by_user_anno = last_updated_by_user_anno['annotationGrid']
    #         textanno.update_one({"projectname": activeprojectname, "textId": last_active_id},
    #                             {'$set': {"annotationGrid": last_updated_by_user_anno,
    #                                       "annotatedFLAG": 1}})

            

    #     # get current datetime upto seconds as data accessed time
    #     # use when 'Save' button is clicked
    #     project_details['accessedOnTime'] = datetime.now().strftime("%d/%m/%y %H:%M:%S")
    #     # pprint(project_details)
    #     # check if tagSetMetaData key is present int he project details
    #     # to check if the tagset contains any dependency and default tags list
    #     if ('tagSetMetaData' in project_details and \
    #         not bool(project_details["tagSetMetaData"])):
    #         # print(project_details["tagSetMetaData"])
    #         # print(not bool(project_details["tagSetMetaData"]))
    #         project_details.pop("tagSetMetaData")


    #     currentText = textanno.find_one({"projectname": activeprojectname, "textId": last_active_id},
    #                                         {"_id": 0, current_username: 1})
    #     # print(len(currentText.keys()))
    #     # pprint(project_details)

    #     if (currentText != None and
    #         len(currentText.keys()) != 0 and
    #         current_username == list(currentText.keys())[0]):
    #         # print('currentText', currentText)
    #         # print('list(currentText.keys())[0]', list(currentText.keys())[0])
    #         # print('list(currentText.values())[0]', list(currentText.values())[0])
    #         # project_details[list(currentText.keys())[0]] = list(currentText.values())[0]
    #         project_details[list(currentText.keys())[0]] = currentText[current_username]['annotationGrid']
    #         project_details['currentUser'] = current_username
    #         # print(project_details)
    #         # pprint(project_details)
    #         currentAnnotation = project_details[current_username]
    #         defaultAnnotation = project_details['tagSetMetaData']['defaultCategoryTags']
    #         # pprint(currentAnnotation)
    #         # pprint(defaultAnnotation)
    #         project_details['tagSetMetaData']['defaultCategoryTags'] = {**defaultAnnotation, **currentAnnotation}

    #         # pprint(project_details)

    #         return project_details
    #     else:

    #         return project_details
    # else:
    #     flash('File not in the database', 'danger')
    
    return project_details