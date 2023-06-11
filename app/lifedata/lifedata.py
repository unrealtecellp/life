"""Module containing the routes for the data part of the LiFe."""

from app import mongo
from flask import (
    Blueprint,
    render_template,
    jsonify,
    request,
    flash,
    redirect,
    url_for
)
from app.controller import (
    getactiveprojectname,
    getcurrentusername,
    getcurrentuserprojects,
    getdbcollections,
    getprojecttype,
    readJSONFile,
    savenewproject,
    updateuserprojects,
    life_logging,
    readzip
)
from app.lifedata.controller import (
    copydatafromparentproject,
    savenewdataform,
    create_validation_type_project,
    save_tagset,
    get_validation_data
)
from flask_login import login_required
import os
from pprint import pformat

lifedata = Blueprint('lifedata', __name__, template_folder='templates', static_folder='static')
basedir = os.path.abspath(os.path.dirname(__file__))
logger = life_logging.get_logger()
jsonfilesdir = '/'.join(basedir.split('/')[:-1]+['jsonfiles'])
select2LanguagesJSONFilePath = os.path.join(jsonfilesdir, 'select2_languages.json')
select2CrawlerTypeJSONFilePath = os.path.join(jsonfilesdir, 'select2_crawler_type.json')

@lifedata.route('/', methods=['GET', 'POST'])
@lifedata.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    """_summary_

    Returns:
        _type_: _description_
    """
    # print('lifedata home')

    return render_template("lifedatahome.html")

@lifedata.route('/getprojectslist', methods=['GET', 'POST'])
@login_required
def getprojectslist():
    """_summary_
    """
    userprojects, = getdbcollections.getdbcollections(mongo, 'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    projectslist = getcurrentuserprojects.getcurrentuserprojects(current_username, userprojects)

    return jsonify(projectslist=projectslist)

@lifedata.route('/newdataform', methods=['GET', 'POST'])
@login_required
def newdataform():
    """_summary_

    Returns:
        _type_: _description_
    """
    try:
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
            # logger.debug('new_data_form: %s', pformat(new_data_form))
            new_data_form_files = request.files.to_dict()
            # logger.debug('new_data_form_files: %s', pformat(new_data_form_files))
            project_type = new_data_form['projectType'][0]
            projectname = 'D_'+new_data_form['projectname'][0]
            about_project = new_data_form['aboutproject'][0]
            derive_from_project_name = None

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
                                                                current_username,
                                                                project_type
                                                            )
            # logger.debug("save_data_form: %s", pformat(save_data_form))

            if (project_type == 'validation'):
                validation_collection, tagsets = getdbcollections.getdbcollections(mongo,
                                                                        'validation',
                                                                        'tagsets')
                # logger.debug("project_type: %s", project_type)

                validation_zip_file = new_data_form_files["tagsetZipFile"]
                tagset_project_ids, = save_tagset.save_tagset(tagsets, validation_zip_file, project_name)
                # logger.debug(tagset_project_ids)
                projects.update_one({"projectname": project_name},
                                    {"$set": {
                                        "tagsetId": tagset_project_ids
                                    }})
                create_validation_type_project.create_validation_type_project(projects,
                                                                            validation_collection,
                                                                            project_name,
                                                                            derive_from_project_name,
                                                                            current_username)

                return redirect(url_for("lifedata.validation"))
                # return redirect(url_for("enternewsentences"))

            if ("derivefromproject" in new_data_form):
            # copy all the data from the "derivedfromproject" to "newproject"
                derive_from_project_type = getprojecttype.getprojecttype(projects, derive_from_project_name)
                # logger.debug('derive_from_project_type: %s', derive_from_project_type)
                if (derive_from_project_type == 'questionnaires' and
                    project_type in include_speakerIds):
                    data_collection, = getdbcollections.getdbcollections(mongo, project_type)
                    copydatafromparentproject.copydatafromquesproject(questionnaires,
                                                                        data_collection,
                                                                        derive_from_project_name,
                                                                        projectname,
                                                                        current_username)

            return redirect(url_for("enternewsentences"))
    except:
        logger.exception("")
        flash("Some error occured!!!")
        return render_template("lifedatahome.html")

@lifedata.route('/validation', methods=['GET', 'POST'])
@login_required
def validation():
    projects_collection, userprojects_collection, validation_collection, tagsets_collection = getdbcollections.getdbcollections(mongo,
                                                                                                                                "projects",
                                                                                                                                "userprojects",
                                                                                                                                "validation",
                                                                                                                                "tagsets")
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects_collection)

    project_details = get_validation_data.get_validation_data(projects_collection,
                                                              userprojects_collection,
                                                              validation_collection,
                                                              tagsets_collection,
                                                              current_username,
                                                              activeprojectname)
    

    return render_template("lifedatavalidation.html",
                           projectName=activeprojectname,
                           proj_data=project_details
                           )

@lifedata.route('/getlanguagelist', methods=['GET', 'POST'])
@login_required
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

@lifedata.route('/datazipfile', methods=['GET', 'POST'])
@login_required
def datazipfile():
    try:
        projects, tagsets, = getdbcollections.getdbcollections(mongo,
                                                            'projects',
                                                                'tagsets')
        if request.method == "POST":
            derive_from_project_name = dict(request.form.lists())
            derive_from_project_name = derive_from_project_name['deriveFromProjectName'][0]
            # logger.debug("derive_from_project_name: %s", derive_from_project_name)
            validation_zip_file = request.files.to_dict()
            validation_zip_file = validation_zip_file['tagsetZipFile']
            # logger.debug("validation_zip_file: %s", validation_zip_file)
            completed, message, validation_tagset = readzip.read_zip(tagsets, validation_zip_file)
            # logger.debug('completed: %s', completed)
            # logger.debug('message: %s', message)
            # logger.debug('validation_tagset: %s', validation_tagset)
            if (completed):
                validation_tagset_keys = list(validation_tagset.keys())
            else:
                return jsonify(completed=completed,
                               message=message,
                               mappingTagset={},
                               validationTagsetKeys=[])

            derive_from_project_type = getprojecttype.getprojecttype(projects, derive_from_project_name)
            # logger.debug("derive_from_project_type: %s", derive_from_project_type)
            if (derive_from_project_type == 'recordings'):
                derive_from_project_tagset = ['Audio_Recording']
            else:
                derive_from_project_tagset = []

            if (len(derive_from_project_tagset) != 0):
                mapping_tagset = {}
                for category in derive_from_project_tagset:
                    mapping_tagset[category] = validation_tagset_keys
            return jsonify(completed=completed,
                            message=message,
                            mappingTagset=mapping_tagset,
                            validationTagsetKeys=validation_tagset_keys)
    except:
        logger.exception("")

@lifedata.route('/datasubsource', methods=['GET', 'POST'])
@login_required
def datasubsource():
    data_sub_source = readJSONFile.readJSONFile(select2CrawlerTypeJSONFilePath)

    return jsonify(dataSubSource=data_sub_source)

@lifedata.route('/crawler', methods=['GET', 'POST'])
@login_required
def crawler():
    try:
        projects, userprojects, projectsform, speakerdetails = getdbcollections.getdbcollections(mongo,
                                                                                                    'projects',
                                                                                                    'userprojects',
                                                                                                    'projectsform',
                                                                                                    'speakerdetails')
        current_username = getcurrentusername.getcurrentusername()

        if request.method =='POST':
            new_crawl_data_form = dict(request.form.lists())
            logger.debug('new_crawl_data_form: %s', pformat(new_crawl_data_form))
            # logger.debug('new_crawl_data_form_files: %s', pformat(new_crawl_data_form_files))
            project_type = new_crawl_data_form['projectType'][0]
            projectname = 'D_'+new_crawl_data_form['projectname'][0]
            about_project = new_crawl_data_form['aboutproject'][0]

            # project_name = savenewproject.savenewproject(projects,
            #                                                 projectname,
            #                                                 current_username,
            #                                                 aboutproject=about_project,
            #                                                 projectType=project_type
            #                                                 )
            # if project_name == '':
            #     flash(f'Project Name : "{projectname}" already exist!')
            #     return redirect(url_for('lifedata.home'))

            # updateuserprojects.updateuserprojects(userprojects,
            #                                         projectname,
            #                                         current_username
            #                                         )

            # save_data_form = savenewdataform.savenewdataform(projectsform,
            #                                                     projectname,
            #                                                     new_data_form,
            #                                                     current_username,
            #                                                     project_type
            #                                                 )
            
            datasubsource = request.form.get('datasubsource')
        #     source_data = {"username": projectowner,
        #                     "projectname": activeprojectname,
        #                     "lifesourceid": source_id,
        #                     "createdBy": current_username,
        #                     "dataSource": data_source,
        #                     "dataSubSource": datasubsource,
        #                     "current": {
        #                         "updatedBy": current_username,
        #                         "sourceMetadata": {
        #                             "channelName": channelname,
        #                             "channelUrl": channelurl
        #                         },
        #                         "current_date": current_dt
        #                     },
        #                     "isActive": 1}
        # # pprint(source_data)
        # # speakerdetails.insert_one(source_data, check_keys=False)
        # speakerdetails.insert_one(source_data)
            return redirect(url_for("lifedata.crawler"))
    except:
        logger.exception("")

    return render_template('crawler.html',
                           projectName='project_name')
