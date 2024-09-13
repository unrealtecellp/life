"""Module to remove all/partial kind of access to a project."""

from app.controller import (
    life_logging
)
logger = life_logging.get_logger()

def remove_partial_access(projects,
                            userprojects,
                            activeprojectname,
                            user_to_remove,
                            speakers_to_remove,
                            sourceIdsKeyName):
    try:
        activeIdKeyName = 'active'+sourceIdsKeyName[:-1]
        # logger.debug("activeIdKeyName: %s", activeIdKeyName)
        for speaker in speakers_to_remove:
            projects.update_one({ "projectname": activeprojectname },
                        {
                            "$unset": { "lastActiveId."+user_to_remove+'.'+speaker: "",
                                       "fileSpeakerIds."+user_to_remove+'.'+speaker: ""},
                            "$pull": {sourceIdsKeyName+"."+user_to_remove: speaker}
                        })
            userprojectsdetails = userprojects.find_one({"username": user_to_remove})
            user_activespeakerid = userprojectsdetails["projectsharedwithme"][activeprojectname][activeIdKeyName]
            if (speaker == user_activespeakerid):
                userprojects.update_one({"username": user_to_remove},
                                        {"$set": 
                                            { 
                                                "projectsharedwithme."+activeprojectname+"."+activeIdKeyName: ""
                                            }
                                        })
    except:
        logger.exception("")

    return user_to_remove

def removeallaccess(projects,
                    userprojects,
                    activeprojectname,
                    current_username,
                    user_to_remove,
                    speakers_to_remove,
                    sourceIdsKeyName):
    try:
        # print(f"In removeallaccess()")
        if (len(speakers_to_remove) == 0):
            projects.update_one({ "projectname": activeprojectname },
                                {
                                    "$unset": { "lastActiveId."+user_to_remove: "",
                                            sourceIdsKeyName+"."+user_to_remove: "",
                                            "fileSpeakerIds."+user_to_remove: ""
                                            },
                                    "$pull": {"sharedwith": user_to_remove}
                                })
            
            userprojectsdetails = userprojects.find_one({"username": user_to_remove})

            userprojects.update_one({"username": user_to_remove},
                                    {"$unset": { "projectsharedwithme."+activeprojectname: ""},
                                    "$set": { "projectwassharedwithme."+activeprojectname: userprojectsdetails["projectsharedwithme"][activeprojectname]}
                                    })
            if activeprojectname == userprojectsdetails['activeprojectname']:
                userprojects.update_one({"username": user_to_remove},
                                        {"$set": { "activeprojectname": ""}
                                        })

            currentuserprojectsdetails = userprojects.find_one({"username": current_username},
                                                                {"_id": 0,
                                                                    "myproject": 1,
                                                                    "projectsharedwithme": 1
                                                                })

            if activeprojectname in currentuserprojectsdetails["myproject"]:
                userprojects.update_one({ "username": current_username },
                            {
                                "$pull": {"myproject."+activeprojectname+".isharedwith": user_to_remove}
                            })
            elif activeprojectname in currentuserprojectsdetails["projectsharedwithme"]:
                userprojects.update_one({ "username": current_username },
                            {
                                "$pull": {"projectsharedwithme."+activeprojectname+".isharedwith": user_to_remove}
                            })
        else:
            remove_partial_access(projects,
                                    userprojects,
                                    activeprojectname,
                                    user_to_remove,
                                    speakers_to_remove,
                                    sourceIdsKeyName)
    except:
        logger.exception("")
    
    return user_to_remove
