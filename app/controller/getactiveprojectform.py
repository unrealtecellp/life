"""Module to get the active project form."""

def getactiveprojectform(projectsform, projectowner, activeprojectname):
    """
    Args:
        projectsform: instance of 'projectsform' collection.
        projectowner: name of the project owner.
        activeprojectname: name of the project activated by current active user.

    Returns:
        activeprojectform: form for the active project (JSON type data)
    """

    activeprojectform = projectsform.find_one({'projectname' : activeprojectname,
                                                'username' : projectowner}, { "_id" : 0 })
    return activeprojectform
