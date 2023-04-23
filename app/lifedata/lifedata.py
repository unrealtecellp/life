"""Module containing the routes for the data part of the LiFe."""

from flask import (
    Blueprint,
    render_template,
    jsonify,
    request,
    flash,
    redirect,
    url_for
)
from app import mongo
import os
from app.controller import (
    getactiveprojectname,
    getcurrentusername,
    getcurrentuserprojects,
    getdbcollections,
    getprojecttype,
    readJSONFile,
    savenewproject,
    updateuserprojects
)
from app.lifedata.controller import (
    copydatafromparentproject,
    savenewdataform
)

lifedata = Blueprint('lifedata', __name__, template_folder='templates', static_folder='static')
basedir = os.path.abspath(os.path.dirname(__file__))
jsonfilesdir = '/'.join(basedir.split('/')[:-1]+['jsonfiles'])
select2LanguagesJSONFilePath = os.path.join(jsonfilesdir, 'select2_languages.json')

@lifedata.route('/', methods=['GET', 'POST'])
@lifedata.route('/home', methods=['GET', 'POST'])
def home():
    """_summary_

    Returns:
        _type_: _description_
    """
    # print('lifedata home')

    return render_template("lifedatahome.html")

@lifedata.route('/getprojectslist', methods=['GET', 'POST'])
def getprojectslist():
    """_summary_
    """
    userprojects, = getdbcollections.getdbcollections(mongo, 'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    projectslist = getcurrentuserprojects.getcurrentuserprojects(current_username, userprojects)

    return jsonify(projectslist=projectslist)

@lifedata.route('/newdataform', methods=['GET', 'POST'])
def newdataform():
    """_summary_

    Returns:
        _type_: _description_
    """
    # print('lifedata newdataform')
    projects, userprojects, projectsform, questionnaires, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                                            'projects',
                                                                                                            'userprojects',
                                                                                                            'projectsform',
                                                                                                            'questionnaires',
                                                                                                            'transcriptions')
    current_username = getcurrentusername.getcurrentusername()

    include_speakerIds = ['transcriptions', 'recordings']

    if request.method =='POST':
        new_data_form = dict(request.form.lists())
        # print('New Data form', new_data_form)
        project_type = new_data_form['projectType'][0]
        projectname = 'D_'+new_data_form['projectname'][0]
        about_project = new_data_form['aboutproject'][0]

        project_name = savenewproject.savenewproject(projects,
                                        projectname,
                                        current_username,
                                        aboutproject=about_project,
                                        projectType=project_type
                                        )
        if project_name == '':
            flash(f'Project Name : "{projectname}" already exist!')
            return redirect(url_for('lifedata.home'))

        if ("derivefromproject" in new_data_form):
        #     print("line no: 76, derivefromproject in new_data_form")
            derive_from_project_name = new_data_form["derivefromproject"][0]
            projects.update_one({"projectname": derive_from_project_name},
                                {"$addToSet": {
                                    "projectDerivatives": project_name
                                }})
            projects.update_one({"projectname": project_name},
                                {"$addToSet": {
                                    "derivedFromProject": derive_from_project_name
                                }})

        updateuserprojects.updateuserprojects(userprojects,
                                                projectname,
                                                current_username
                                                )

        save_data_form = savenewdataform.savenewdataform(projectsform,
                                                            projectname,
                                                            new_data_form,
                                                            current_username
                                                        )
        if ("derivefromproject" in new_data_form):
        # copy all the data from the "derivedfromproject" to "newproject"
            derive_from_project_type = projects.find_one({'projectname': derive_from_project_name},
                                                            {"_id": 0, "projectType": 1})["projectType"]
            if (derive_from_project_type == 'questionnaires' and
                project_type in include_speakerIds):
                data_collection, = getdbcollections.getdbcollections(mongo, project_type)
                copydatafromparentproject.copydatafromquesproject(questionnaires,
                                                                    data_collection,
                                                                    derive_from_project_name,
                                                                    projectname,
                                                                    current_username)

        return redirect(url_for("enternewsentences"))

    return render_template("lifedatahome.html")

@lifedata.route('/getlanguagelist', methods=['GET', 'POST'])
def getlanguagelist():
    """_summary_
    """
    projects, projectsform = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'projectsform')
    project_name = request.args.get('projectname')
    project_type = getprojecttype.getprojecttype(projects, project_name)
    languageslist = []
    
    if (project_type == 'transcriptions'):
        languageslist = readJSONFile.readJSONFile(select2LanguagesJSONFilePath)
    elif (project_type == "questionnaires"):
        project_form = projectsform.find_one({"projectname" : project_name})
        langscripts = project_form["Prompt Type"][1]
        languageslist = [{"id": "", "text": ""}]
        for lang_script, lang_info in langscripts.items():
            languageslist.append({"id": lang_script, "text": lang_script})
            # if ('Audio' in lang_info):
            #     langscript.append(lang_script)

    return jsonify(languageslist=languageslist)