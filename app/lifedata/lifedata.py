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
from app.controller import (
    getcurrentusername,
    getcurrentuserprojects,
    getdbcollections,
    savenewproject,
    updateuserprojects
)
from app.lifedata.controller import (
    copydatafromparentproject,
    savenewdataform
)

lifedata = Blueprint('lifedata', __name__, template_folder='templates', static_folder='static')

@lifedata.route('/', methods=['GET', 'POST'])
@lifedata.route('/home', methods=['GET', 'POST'])
def home():
    """_summary_

    Returns:
        _type_: _description_
    """
    print('lifedata home')

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
    print('lifedata newdataform')
    projects, userprojects, projectsform, questionnaires, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'userprojects',
                                                                'projectsform',
                                                                'questionnaires',
                                                                'transcriptions')
    current_username = getcurrentusername.getcurrentusername()

    if request.method =='POST':
        new_data_form = dict(request.form.lists())
        print('New Data form', new_data_form)
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
        # createdummyques.createdummyques(questionnaires,
        #                                 projectname,
        #                                 save_ques_form,
        #                                 current_username
        #                                 )
        if ("derivefromproject" in new_data_form):
        # copy all the data from the "derivedfromproject" to "newproject"
            derive_from_project_type = projects.find_one({'projectname': derive_from_project_name},
                                                            {"_id": 0, "projectType": 1})["projectType"]
            if (derive_from_project_type == 'questionnaires' and
                project_type == 'transcriptions'):
                copydatafromparentproject.copydatafromquesproject(questionnaires,
                                                                    transcriptions,
                                                                    derive_from_project_name,
                                                                    projectname,
                                                                    current_username)

        return redirect(url_for("enternewsentences"))

    return render_template("lifedatahome.html")
