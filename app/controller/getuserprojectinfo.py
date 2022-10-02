"""Module to get the user project info of the project."""


def getuserprojectinfo(userprojects, current_username, activeprojectname):

    projectinfo = userprojects.find_one({'username' : current_username},
                                        {'_id': 0, 'myproject': 1, 'projectsharedwithme': 1})

    # print(projectinfo)
    userprojectinfo = {}
    for key, value in projectinfo.items():
        if (len(value) != 0):
            if (activeprojectname in value):
                # print(key, value, value[activeprojectname])
                userprojectinfo = value[activeprojectname]
                # print(shareinfo)
    if (len(userprojectinfo) == 0):
        userprojectinfo = {
                        'sharemode': 100,
                        'sharechecked': "false",
                        'activespeakerId': ""
                    }

    return userprojectinfo
