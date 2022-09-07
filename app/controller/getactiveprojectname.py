"""Module to get the active project name of the current user"""

def getactiveprojectname(current_username, userprojects):
    """
    INPUT:
        current_username: name of the current active user
        userprojects: instance of 'userprojects' collection

    OUTPUT:
        activeprojectname: current user active project name
    """

    activeprojectname = userprojects.find_one({ 'username' : current_username },\
                    {'_id' : 0, 'activeprojectname': 1})
    if len(activeprojectname) != 0:
        activeprojectname = activeprojectname['activeprojectname']
    else:
        activeprojectname = ''    

    return activeprojectname
