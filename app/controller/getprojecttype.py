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


def getderivedfromprojectdetails(projects, project_name):
    derived_from_project_type = ''
    derived_from_project_name = ''
    try:
        derivedFromProject = projects.find_one({"projectname": project_name},
                                               {"_id": 0, "derivedFromProject": 1})
        if (len(derivedFromProject['derivedFromProject']) != 0):
            derived_from_project_name = derivedFromProject['derivedFromProject'][0]
            derived_from_project_type = getprojecttype.getprojecttype(
                projects, derived_from_project_name)
    except:
        derived_from_project_type = ''
        derived_from_project_name = ''

    return derived_from_project_type, derived_from_project_name
