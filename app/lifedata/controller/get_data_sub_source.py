def get_data_sub_source(projects_collection,
                        project_name):
    data_sub_source = projects_collection.find_one({"projectname": project_name},
                                                   {"_id": 0, "dataSubSource": 1})['dataSubSource']
    
    return data_sub_source