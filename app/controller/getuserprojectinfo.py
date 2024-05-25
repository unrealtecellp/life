"""Module to get the user project info of the project."""

from app.controller import (
    life_logging
)

logger = life_logging.get_logger()


def getuserprojectinfo(userprojects,
                       current_username,
                       activeprojectname):

    projectinfo = userprojects.find_one({'username': current_username},
                                        {'_id': 0, 'myproject': 1, 'projectsharedwithme': 1})

    # logger.debug("current_username: %s, projectinfo: %s", current_username, projectinfo)
    userprojectinfo = {}
    if (projectinfo is not None):
        for key, value in projectinfo.items():
            if (len(value) != 0):
                if (activeprojectname in value):
                    # print(current_username, key, value, value[activeprojectname])
                    userprojectinfo = value[activeprojectname]
                    # print(shareinfo)
    if (len(userprojectinfo) == 0):
        userprojectinfo = {
            'sharemode': -1,
            'sharechecked': "false",
            'activespeakerId': "",
            'activesourceId': "",
            'sharelatestchecked': "false",
            'downloadchecked': "false",
            'isharedwith': [],
            'tomesharedby': []
        }

    return userprojectinfo
