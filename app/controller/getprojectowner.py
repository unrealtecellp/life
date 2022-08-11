"""Module to get the project owner"""

def getprojectowner(activeprojectname, projects):
    """
    INPUT:
        activeprojectname: name of the project activated by current active user
        projects: instance of 'projects' collection

    OUTPUT:
        projectowner: project owner name
    """

    projectowner = projects.find_one({}, {"_id" : 0,
                    activeprojectname : 1})[activeprojectname]["projectOwner"]

    return projectowner
