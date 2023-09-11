"""Module contains processing related to share interface in LiFE."""

from app.controller import (
    getactiveprojectname,
    getprojectowner,
    getuserprojectinfo,
    getprojecttype,
    life_logging
)
from pprint import pformat

logger = life_logging.get_logger()

def get_users_list(projects,
                   userprojects,
                   userlogin,
                   current_username,
                   share_action='share',
                   selected_user=''):
    usersList = []
    sourceList = []
    current_user_sharemode = 0
    share_with_users_list = []
    selected_user_sourceList = []
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    projectowner = getprojectowner.getprojectowner(projects,
                                                   activeprojectname)
    # logger.debug("project owner: %s", projectowner)
    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                        current_username,
                                                        activeprojectname)
    current_user_sharemode = int(shareinfo['sharemode'])
    selected_user_shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                    selected_user,
                                                                    activeprojectname)
    project_type = getprojecttype.getprojecttype(projects,
                                                    activeprojectname)

    # get list of all the users registered in the application LiFE
    for user in userlogin.find({}, {"_id": 0, "username": 1, "isActive": 1}):
        if ('isActive' in user and user['isActive'] == 1):
            usersList.append(user["username"])
    if (current_username == projectowner):
        usersList.remove(projectowner)
        share_with_users_list = usersList

    else:
        # logger.debug("usersList: %s", usersList)
        usersList.remove(projectowner)
        usersList.remove(current_username)
        for username in usersList:
            usershareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                    username,
                                                                    activeprojectname)
            usersharemode = int(usershareinfo['sharemode'])
            # logger.debug("current_username: %s,\
            #               \ncurrent_user_sharemode: %s,\
            #               \nusername: %s,\
            #              \nusersharemode: %s",
            #              current_username,
            #              current_user_sharemode,
            #              username,
            #              usersharemode)
            if (current_user_sharemode <= usersharemode):
                pass
            else:
                share_with_users_list.append(username)
    if (project_type == 'recordings' or
            project_type == 'transcriptions'):
        speakersDict = projects.find_one({'projectname': activeprojectname},
                                            {'_id': 0, 'speakerIds.'+current_username: 1})
        # logger.debug("speakersDict: %s", pformat(speakersDict))
        if (len(speakersDict) != 0 and
            speakersDict['speakerIds']):
            sourceList = speakersDict['speakerIds'][current_username]
        if (selected_user != ''):
            selected_user_speakersDict = projects.find_one({'projectname': activeprojectname},
                                                            {'_id': 0, 'speakerIds.'+selected_user: 1})
            # logger.debug("speakersDict: %s", pformat(speakersDict))
            if (len(speakersDict) != 0 and
                selected_user_speakersDict['speakerIds']):
                selected_user_sourceList = selected_user_speakersDict['speakerIds'][selected_user]
    elif (project_type == 'crawling' or
            project_type == 'annotation'):
        sourceDict = projects.find_one({'projectname': activeprojectname},
                                        {'_id': 0, 'sourceIds.'+current_username: 1})
        if (len(sourceDict) != 0 and
            sourceDict['sourceIds']):
            sourceList = sourceDict['sourceIds'][current_username]
        if (selected_user != ''):
            selected_user_sourceDict = projects.find_one({'projectname': activeprojectname},
                                                    {'_id': 0, 'sourceIds.'+selected_user: 1})
            if (len(selected_user_sourceDict) != 0 and
                selected_user_sourceDict['sourceIds']):
                selected_user_sourceList = selected_user_sourceDict['sourceIds'][selected_user]
    if (share_action == 'update'):
        sourceList = list(set(sourceList).difference(set(selected_user_sourceList)))
    elif (share_action == 'remove'):
        sourceList = selected_user_sourceList

    return (activeprojectname,
            share_with_users_list,
            sourceList,
            shareinfo,
            current_user_sharemode,
            selected_user_shareinfo)