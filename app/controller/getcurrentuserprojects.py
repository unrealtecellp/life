"""Module to get all projects name created by the current active user."""

from flask import flash

def getcurrentuserprojects(current_username, userprojects):
    """
    INPUT:
        current_username: name of the current active user
        userprojects: instance of 'userprojects' collection

    OUTPUT:
        userprojectsname: sorted list of current user projects name
    """

    userprojectsname = []
    try:
        userprojects  = userprojects.find_one({ 'username' : current_username })
        myproject = userprojects['myproject']
        myprojectlist = list(myproject.keys())
        projectsharedwithme = userprojects['projectsharedwithme']
        projectsharedwithmelist = list(projectsharedwithme.keys())
        # userprojectsname = set(myproject + projectsharedwithme)
        userprojectsname = set(myprojectlist + projectsharedwithmelist)
    except:
        flash('Please create your first project.')
    # print(userprojectsname)
    return sorted(list(userprojectsname))
