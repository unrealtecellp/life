"""Module to get the project form of the project which is being derived."""

def getderivedfromprojectform(projectsform,
                                derive_from_project_name):
    derivedfromprojectform = projectsform.find_one({"projectname": derive_from_project_name},
                                                    {
                                                        "_id": 0,
                                                        "projectname": 0,
                                                        "aboutproject": 0
                                                    })

    return derivedfromprojectform