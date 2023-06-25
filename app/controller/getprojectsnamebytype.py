"""Module to get all projects name created by the current active user."""

from flask import flash

def getprojectsnamebytype(projects,
                            projects_list,
                            project_type_list):
    """
    INPUT:

    OUTPUT:
    """

    try:
        projects  = projects.find({}, {"_id": 0, "projectname": 1, "projectType": 1})
        project_name = ''
        project_type  = ''
        for project in projects:
            # print(project)
            if ('projectname' in project):
                project_name = project['projectname']
            if ('projectType' in project):
                project_type = project['projectType']
            if (project_name in projects_list):
                if not (project_type in project_type_list):
                    projects_list.remove(project_name)
                else:
                    continue
            else:
                continue
    except:
        flash('Please create your first project.')
    # print(userprojectsname)
    return projects_list
