"""Module to save new project in 'projects' collection in the database."""

def savenewproject(projects,
                    projectname,
                    current_username,
                    **kwargs):
    """
    Args:
        projects: instance of 'projects' collection.
        projectname: name of the project.
        current_username: name of the current active user.

    Returns:
        empty string
    """
    if projects.find_one({ 'projectname': projectname }) is None:
        project_details = {
            "projectname": projectname,
            "projectOwner" : current_username,
            "lexemeInserted" : 0,
            "lexemeDeleted" : 0,
            "sharedwith": [current_username],
            "lastActiveId": {
                current_username: {}
            },
            "projectdeleteFLAG" : 0,
            "isPublic": 0,
            "derivedFromProject": [],
            "projectDerivatives": [],
        }
        for key, value in kwargs.items():
            project_details[key] = value
            if (key == 'projectType' and value == 'transcriptions'):
                project_details['speakerIds'] = {current_username: []}
            
        projects.insert_one(project_details)
        # pprint(project_details)
    else:
        projectname = ''

    return projectname
