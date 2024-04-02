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

    activeprojectform = projectsform.find_one({'projectname': activeprojectname,
                                               'username': projectowner}, {"_id": 0})
    return activeprojectform


def getaudiolanguage(projectsform, projectowner, activeprojectname):
    activeprojectform = getactiveprojectform(
        projectsform, projectowner, activeprojectname)
    if 'Sentence Language' in activeprojectform:
        audio_lang = activeprojectform['Sentence Language'][0]
    else:
        audio_lang = activeprojectform['Audio Language'][1][0]

    return audio_lang
