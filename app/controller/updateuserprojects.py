"""Module to update new project in 'userprojects' collection in the database."""

def updateuserprojects(userprojects,
                        projectname,
                        current_username):
    """
    Args:
        userprojects: instance of 'userprojects' collection.
        projectname: name of the project.
        current_username: name of the current active user.

    Returns:
        _type_: _description_
    """

    # get curent user project list and update
    userprojectnamelist = userprojects.find_one({'username' : current_username})["myproject"]
    userprojectnamelist.append(projectname)
    # when testing comment these to avoid any database update/changes
    userprojects.update_one({ 'username' : current_username },
                            { '$set' : { 'myproject' : userprojectnamelist,
                                        'activeprojectname' :  projectname }})
