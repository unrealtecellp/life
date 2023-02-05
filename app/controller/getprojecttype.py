"""Module to get the type of the project."""

def getprojecttype(projects,
                    activeprojectname):
    """_summary_

    Args:
        projects (_type_): _description_
    """
    try:
        project_type = projects.find_one({"projectname": activeprojectname},
                                            {"_id": 0, "projectType": 1})

        project_type = project_type["projectType"]
    except:
        project_type = ''
        
    return project_type