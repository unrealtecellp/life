"""Module to get the name/names of project  share with."""

def getprojectnamesharedwith(projects, activeprojectname):
    """_summary_

    Args:
        projects: instance of 'projects' collection.
        activeprojectname: name of the project activated by current active user.

    Returns:
        String: project owner name
    """

    # print(activeprojectname)
    projectsharewith = projects.find_one({ "projectname": activeprojectname },
                                        { "_id" : 0, "sharedwith" : 1 })
    # print(projectowner)
    if (projectsharewith != None):
        projectsharewith = projectsharewith["sharedwith"]
    else:
        projectsharewith = ''

    return projectsharewith
