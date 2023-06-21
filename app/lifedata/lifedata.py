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
    getprojectowner,
    getuserprojectinfo,
    readJSONFile,
    savenewproject,
    updateuserprojects,
    life_logging,
    readzip
)
from app.lifedata.controller import (
    copydatafromparentproject,
    data_project_info,
    savenewdataform,
    create_validation_type_project,
    save_tagset,
    get_validation_data,
    youtubecrawl,
    get_crawled_data
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
        projects, userprojects = getdbcollections.getdbcollections(mongo,
                                                                    'projects',
                                                                    'userprojects')
        current_username = getcurrentusername.getcurrentusername()
        
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                        userprojects)
        data_sub_source = data_project_info.get_data_sub_source(projects,
                                                                  activeprojectname)

        if request.method =='POST':
            new_crawl_data_form = dict(request.form.lists())
            logger.debug('new_crawl_data_form: %s', pformat(new_crawl_data_form))
            # logger.debug('new_crawl_data_form_files: %s', pformat(new_crawl_data_form_files))
            project_type = new_crawl_data_form['projectType'][0]
            projectname = 'D_'+new_crawl_data_form['projectname'][0]
            about_project = new_crawl_data_form['aboutproject'][0]
            datasource = new_crawl_data_form['datasource'][0]
            datasubsource = new_crawl_data_form['datasubsource'][0]
            crawlerlanguage = new_crawl_data_form['crawlerlanguage']
            crawlerscript = new_crawl_data_form['crawlerscript']

            project_name = savenewproject.savenewproject(projects,
                                                            projectname,
                                                            current_username,
                                                            aboutproject=about_project,
                                                            projectType=project_type,
                                                            dataSource=datasource,
                                                            dataSubSource=datasubsource,
                                                            crawlerLanguage=crawlerlanguage,
                                                            crawlerScript=crawlerscript
                                                            )
            if project_name == '':
                flash(f'Project Name : "{projectname}" already exist!')
                return redirect(url_for('lifedata.home'))

            updateuserprojects.updateuserprojects(userprojects,
                                                    projectname,
                                                    current_username
                                                    )
            flash("Crawling Complete.")
            return redirect(url_for("lifedata.crawler"))
    except:
        logger.exception("")

    return render_template('crawler.html',
                           projectName=activeprojectname,
                           dataSubSource=data_sub_source)

@lifedata.route('/youtubecrawler', methods=['GET', 'POST'])
@login_required
def youtubecrawler():
    try:
        projects_collection, userprojects_collection, sourcedetails_collection, crawling_collection = getdbcollections.getdbcollections(mongo,
                                                                                                                                        'projects',
                                                                                                                                        'userprojects',
                                                                                                                                        'sourcedetails',
                                                                                                                                        'crawling')
        current_username = getcurrentusername.getcurrentusername()
        
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                        userprojects_collection)
        project_owner = getprojectowner.getprojectowner(projects_collection, activeprojectname)

        if request.method =='POST':
            youtube_crawler_info = dict(request.form.lists())
            logger.debug('youtube_crawler_info: %s', pformat(youtube_crawler_info))
            # logger.debug('%s', pformat(youtube_crawler_info['dataLinks'][0].split('\r\n')))
            api_key = youtube_crawler_info['youtubeAPIKey'][0]
            youtube_data_for = youtube_crawler_info['youtubeDataFor'][0]
            data_links = {}
            # data_links_list = youtube_crawler_info['dataLinks'][0].split('\r\n')
            # data_links = {youtube_data_for: data_links_list}
            data_links_info = {}
            for key, value in youtube_crawler_info.items():
                if('videoschannelId' in key):
                    videoschannelId_count = key.split('_')[1]
                    searchkeywords_key = 'searchkeywords_'+videoschannelId_count
                    if (searchkeywords_key in youtube_crawler_info):
                        searchkeywords_value = youtube_crawler_info[searchkeywords_key]
                    else:
                        searchkeywords_value = []
                    data_links_info[value[0]] = searchkeywords_value
                    logger.debug('key: %s, videoschannelId_count: %s, value: %s, searchkeywords_key: %s, searchkeywords_value: %s', 
                                 key, videoschannelId_count, value, searchkeywords_key, searchkeywords_value)
            data_links[youtube_data_for] = data_links_info
            logger.debug("data_links_info: %s", pformat(data_links_info))
            logger.debug("data_links: %s", pformat(data_links))
            youtubecrawl.run_youtube_crawler(projects_collection,
                                                userprojects_collection,
                                                sourcedetails_collection,
                                                crawling_collection,
                                                project_owner,
                                                current_username,
                                                activeprojectname,
                                                api_key,
                                                data_links)
    except:
        logger.exception("")

    return redirect(url_for("lifedata.crawler"))

@lifedata.route('/crawlerbrowse', methods=['GET', 'POST'])
@login_required
def crawlerbrowse():
    try:
        new_data = {}
        projects, userprojects, crawling = getdbcollections.getdbcollections(mongo,
                                                                                'projects',
                                                                                'userprojects',
                                                                                'crawling')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)
        projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                        current_username,
                                                        activeprojectname)
        sourceids = projects.find_one({"projectname": activeprojectname},
                                        {"_id": 0, "sourceIds." +current_username: 1})
        logger.debug('sourceids: %s', pformat(sourceids))
        if (sourceids["sourceIds"]):
            sourceids = sourceids["sourceIds"][current_username]
            sourceids.append('')
        else:
            sourceids = ['']
        if ('activesourceId' in shareinfo):
            active_source_id = shareinfo['activesourceId']
        else:
            active_source_id = ''
        
        if (active_source_id != ''):
            crawled_data_list = get_crawled_data.get_n_crawled_data(crawling,
                                                                    activeprojectname,
                                                                    active_source_id)
        else:
            crawled_data_list = []
        # get crawled file src
        # new_crawled_data_list = []
        # for crawled_data in crawled_data_list:
        #     new_crawled_data = crawled_data
        #     crawled_filename = crawled_data['crawledFilename']
        #     new_crawled_data['Audio File'] = url_for('retrieve', filename=crawled_filename)
        #     new_crawled_data_list.append(new_crawled_data)
        new_data['currentUsername'] = current_username
        new_data['activeProjectName'] = activeprojectname
        new_data['projectOwner'] = projectowner
        new_data['shareInfo'] = shareinfo
        new_data['sourceIds'] = sourceids
        new_data['crawlerData'] = crawled_data_list
        new_data['crawlerDataFields'] = ['dataId', 'Data']
    except:
        logger.exception("")

    return render_template('crawlerbrowse.html',
                           projectName=activeprojectname,
                           newData=new_data)
