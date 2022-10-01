"""Module to get the share info of the project."""


def getsharinginfo(userprojects, current_username, activeprojectname):

    projectinfo = userprojects.find_one({'username' : current_username},
                                        {'_id': 0, 'myproject': 1, 'projectsharedwithme': 1})

    # print(projectinfo)
    for key, value in projectinfo.items():
        if (len(value) != 0):
            if (activeprojectname in value):
                # print(key, value, value[activeprojectname])
                shareinfo = value[activeprojectname]
                # print(shareinfo)

    return shareinfo
