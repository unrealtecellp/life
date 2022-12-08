"""Module to remove all kind of access to a project."""

def removeallaccess(projects,
                    userprojects,
                    activeprojectname,
                    current_username,
                    user_to_remove):
    # print(f"In removeallaccess()")

    projects.update_one({ "projectname": activeprojectname },
                        {
                            "$unset": { "lastActiveId."+user_to_remove: ""},
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

    return user_to_remove