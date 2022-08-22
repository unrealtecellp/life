"""Module to save new project form in database."""

import re
from flask import flash, redirect, url_for

def savenewprojectform(projects,
                        userprojects,
                        projectsform,
                        project_form_data,
                        current_username):
    """
    Args:
        projects: instance of 'projects' collection.
        userprojects: instance of 'userprojects' collection.
        projectsform: instance of 'projectsform' collection.
        project_form_data: project form detail from frontend.
        current_username: name of the current active user.

    Returns:
        _type_: _description_
    """
    print(f'{"#"*80}\nprojectFormData\n{project_form_data}')
    dynamicFormField = []
    listOfCustomFields = []
    projectForm = {}
    projectForm['projectname'] = project_form_data['projectname'][0]
    if (projects.find_one({}) != None and
        projectForm["projectname"] in projects.find_one({}).keys()):
        # flash(f'Project Name : {projectForm["projectname"]} already exist!')
        return redirect(url_for('newproject'))
    #get _id in collection name projects
    if projects.find_one({}) is not None:
        projects_id = projects.find_one({}, {"_id" : 1})["_id"]
        projectForm['username'] = current_username
        # when testing comment these to avoid any database update/changes
        try:
            projects.update_one({ "_id" : projects_id }, \
                { '$set' : { projectForm['projectname'] : {"projectOwner" : current_username,
                        "lexemeInserted" : 0, "lexemeDeleted" : 0,
                        "sharedwith": [projectForm['username']], "projectdeleteFLAG" : 0} }})
        except:
            flash("Please enter the Project Name!!!")
            return redirect(url_for('newproject'))

        # get curent user project list and update
        userprojectnamelist = userprojects.find_one({'username' : current_username})["myproject"]
        # print(f'{"#"*80}\n{userprojectnamelist}')
        userprojectnamelist.append(projectForm['projectname'])
        # when testing comment these to avoid any database update/changes
        userprojects.update_one({ 'username' : current_username },
            { '$set' : { 'myproject' : userprojectnamelist,
                'activeproject' :  projectForm['projectname']}})
        dynamicFormField = []
        listOfCustomFields = []
        for key, value in project_form_data.items():
            if re.search(r'[0-9]+', key):
                dynamicFormField.append(value[0])
            elif key == 'Lexeme Form Script':
                projectForm[key] = value
            elif key == 'Gloss Language':
                value.insert(0, 'English')
                projectForm[key] = value
            elif key == 'Gloss Script':
                value.insert(0, 'Latin')
                projectForm[key] = value
            elif key == 'Interlinear Gloss Language':
                value.insert(0, 'English')
                projectForm[key] = value
            elif key == 'Interlinear Gloss Script':
                value.insert(0, 'Latin')
                projectForm[key] = value
            elif len(value) == 1:
                projectForm[key] = value[0]
            else:
                projectForm[key] = value
        # sentence form detail
        projectForm['Sentence Language'] = projectForm['Lexeme Language']
        projectForm['Transcription Script'] = projectForm['Lexeme Form Script']
        projectForm['Translation Language'] = projectForm['Gloss Language']
        projectForm['Translation Script']  = projectForm['Gloss Script']

        if ("Gloss Language" not in projectForm):
            projectForm["Gloss Language"] = ['English']
        if ("Gloss Script" not in projectForm):
            projectForm["Gloss Script"] = ['Latin']
        if ("Interlinear Gloss Language" not in projectForm):
            projectForm["Interlinear Gloss Language"] = ['English']
        if ("Interlinear Gloss Script" not in projectForm):
            projectForm["Interlinear Gloss Script"] = ['Latin']
        if len(dynamicFormField) > 1:
            for i in range(0,len(dynamicFormField),2):
                listOfCustomFields.append({dynamicFormField[i] : dynamicFormField[i+1]})
            projectForm['Custom Fields'] = listOfCustomFields
        # when testing comment these to avoid any database update/changes
        projectsform.insert(projectForm)
