"""Module to get the project owner name."""

def getprojectowner(projects, activeprojectname):
    """_summary_

    Args:
        projects: instance of 'projects' collection.
        activeprojectname: name of the project activated by current active user.

    Returns:
        String: project owner name
    """

    # print(activeprojectname)
    projectowner = projects.find_one({ "projectname": activeprojectname },
                                        { "_id" : 0, "projectOwner" : 1 })
    # print(projectowner)
    if (projectowner != None):
        projectowner = projectowner["projectOwner"]
    else:
        projectowner = ''

    return projectowner
