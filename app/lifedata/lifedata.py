"""Module containing the routes for the data part of the LiFE."""

from app import mongo
from flask import (
    Blueprint,
    render_template,
    jsonify,
    request,
    flash,
    redirect,
    url_for,
    send_file
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
    projectDetails,
    life_logging,
    readzip,
    getactiveprojectform
)
from app.lifedata.controller import (
    annotationdetails,
    copydatafromparentproject,
    crawled_data_details,
    data_project_info,
    savenewdataform,
    create_validation_type_project,
    get_validation_data,
    youtubecrawl,
    sourceid_to_souremetadata,
    translation_utils,
    gloss_utils
)

from app.lifetagsets.controller import (
    saveTagset,
    tagset_details
)

from app.lifedata.transcription.controller import (
    save_new_transcription_form
)

from app.lifemodels.controller import modelManager
from app.languages.controller import languageManager

from flask_login import login_required
import os
from pprint import pformat
import json
from jsondiff import diff
from datetime import datetime
from zipfile import ZipFile
import glob
import pandas as pd

from isocodes import script_names as sn

lifedata = Blueprint('lifedata', __name__,
                     template_folder='templates', static_folder='static')
basedir = os.path.abspath(os.path.dirname(__file__))
logger = life_logging.get_logger()
jsonfilesdir = '/'.join(basedir.split('/')[:-1]+['jsonfiles'])
select2LanguagesJSONFilePath = os.path.join(
    jsonfilesdir, 'select2_languages.json')
select2CrawlerTypeJSONFilePath = os.path.join(
    jsonfilesdir, 'select2_crawler_type.json')


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
    projectslist = getcurrentuserprojects.getcurrentuserprojects(
        current_username, userprojects)

    return jsonify(projectslist=projectslist)


@lifedata.route('/gettagsetslist', methods=['GET', 'POST'])
@login_required
def gettagsetslist():
    """_summary_
    """
    tagsets_list = []
    try:
        tagsets_collection, = getdbcollections.getdbcollections(
            mongo, 'tagsets')
        current_username = getcurrentusername.getcurrentusername()
        tagsets_list = tagset_details.get_tagsets_list(tagsets_collection,
                                                       current_username)
    except:
        logger.exception("")

    return jsonify(tagsetsList=tagsets_list)


@lifedata.route('/newdataform', methods=['GET', 'POST'])
@login_required
def newdataform():
    """_summary_

    Returns:
        _type_: _description_
    """
    try:
        projects, userprojects, projectsform, questionnaires, transcriptions, crawling_collection = getdbcollections.getdbcollections(mongo,
                                                                                                                                      'projects',
                                                                                                                                      'userprojects',
                                                                                                                                      'projectsform',
                                                                                                                                      'questionnaires',
                                                                                                                                      'transcriptions',
                                                                                                                                      'crawling')
        current_username = getcurrentusername.getcurrentusername()

        include_speakerIds = ['transcriptions', 'recordings']

        if request.method == 'POST':
            new_data_form = dict(request.form.lists())
            logger.debug('new_data_form: %s', pformat(new_data_form))
            new_data_form_files = request.files.to_dict()
            logger.debug('new_data_form_files: %s',
                         pformat(new_data_form_files))
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

            updateuserprojects.updateuserprojects(userprojects,
                                                  projectname,
                                                  current_username
                                                  )

            # save_data_form = savenewdataform.savenewdataform(projectsform,
            #                                                  projectname,
            #                                                  new_data_form,
            #                                                  current_username,
            #                                                  project_type
            #                                                  )
            # logger.debug("save_data_form: %s", pformat(save_data_form))

            if (project_type == 'validation'):
                validation_collection, tagsets = getdbcollections.getdbcollections(mongo,
                                                                                   'validation',
                                                                                   'tagsets')
                # logger.debug("project_type: %s", project_type)

                validation_zip_file = new_data_form_files["tagsetZipFile"]
                tagset_project_ids = saveTagset.save_tagset(tagsets,
                                                            validation_zip_file,
                                                            project_name)
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
                derive_from_project_type = getprojecttype.getprojecttype(projects,
                                                                         derive_from_project_name)
                # logger.debug('derive_from_project_type: %s', derive_from_project_type)
                if (derive_from_project_type == 'questionnaires' and
                        project_type in include_speakerIds):
                    data_collection, = getdbcollections.getdbcollections(
                        mongo, project_type)
                    copydatafromparentproject.copydatafromquesproject(questionnaires,
                                                                      data_collection,
                                                                      derive_from_project_name,
                                                                      projectname,
                                                                      current_username)
                    if (project_type == 'transcriptions'):
                        new_transcription_form(project_name,
                                               new_data_form,
                                               new_data_form_files)
                elif (derive_from_project_type == 'crawling' and
                        project_type == 'annotation'):
                    data_collection, = getdbcollections.getdbcollections(
                        mongo, project_type)
                    copydatafromparentproject.copydatafromcrawlingproject(projects,
                                                                          userprojects,
                                                                          crawling_collection,
                                                                          data_collection,
                                                                          derive_from_project_name,
                                                                          projectname,
                                                                          current_username)
                    return redirect(url_for("lifedata.annotation"))
                elif (derive_from_project_type == 'crawling' and
                        project_type == 'transcriptions'):
                    data_collection, = getdbcollections.getdbcollections(
                        mongo, project_type)
                    new_transcription_form(project_name,
                                           new_data_form,
                                           new_data_form_files)
                    copydatafromparentproject.sync_transcription_project_from_crawling_project(mongo,
                                                                                               projects,
                                                                                               userprojects,
                                                                                               crawling_collection,
                                                                                               data_collection,
                                                                                               derive_from_project_name,
                                                                                               projectname,
                                                                                               current_username)
                    return redirect(url_for("lifedata.transcription.home"))
            else:
                if (project_type == 'annotation'):
                    annotation_collection, tagsets = getdbcollections.getdbcollections(mongo,
                                                                                       'annotation',
                                                                                       'tagsets')
                    # logger.debug("project_type: %s", project_type)
                    if 'annotationtagsetZipFile' in new_data_form_files:
                        annotation_zip_file = new_data_form_files["annotationtagsetZipFile"]
                        tagset_project_ids = saveTagset.save_tagset(tagsets,
                                                                    annotation_zip_file,
                                                                    project_name)
                    else:
                        tagset_name = new_data_form['tagsetname'][0]
                        tagset_project_ids = tagset_details.get_tagset_id(tagsets,
                                                                          tagset_name)
                        # logger.debug(tagset_project_ids)
                    projects.update_one({"projectname": project_name},
                                        {"$set": {
                                            "tagsetId": tagset_project_ids
                                        }})
                    if 'annotationdataZipFile' in data_zip_file:
                        data_zip_file = new_data_form_files["annotationdataZipFile"]
                        file_format = new_data_form_files["filetype"]
                        uploaded_sources = annotationdetails.save_multiple_files_data(projects,
                                                                                      userprojects,
                                                                                      data_collection,
                                                                                      projectname,
                                                                                      current_username,
                                                                                      data_zip_file,
                                                                                      file_format)

                    logger.info("Uploaded Files: %s",
                                pformat(uploaded_sources))

                    return redirect(url_for("lifedata.annotation"))
                elif (project_type == 'transcriptions'):
                    new_transcription_form(project_name,
                                           new_data_form,
                                           new_data_form_files)

            return redirect(url_for("lifedata.transcription.home"))
        return render_template("lifedatahome.html")
    except:
        logger.exception("")
        flash("Some error occured!!!")
        return render_template("lifedatahome.html")


def new_transcription_form(project_name,
                           new_data_form,
                           new_data_form_files):
    projects, projectsform, transcriptions_collection, tagsets = getdbcollections.getdbcollections(mongo,
                                                                                                   'projects',
                                                                                                   'projectsform',
                                                                                                   'transcriptions',
                                                                                                   'tagsets')
    current_username = getcurrentusername.getcurrentusername()
    final_tagset_project_ids = []
    tagset_project_ids = {}
    # logger.debug("project_type: %s", project_type)
    if ("transcriptionstagsetuploadcheckbox" in new_data_form and
            new_data_form["transcriptionstagsetuploadcheckbox"][0] == "on"):
        if 'transcriptionstagsetZipFile' in new_data_form_files:
            transcriptions_zip_file = new_data_form_files["transcriptionstagsetZipFile"]
            # logger.debug("transcriptions_zip_file: %s\n%s\n%s\n%s\n%s",
            #              type(transcriptions_zip_file),
            #              transcriptions_zip_file,
            #              transcriptions_zip_file.filename,
            #              len(transcriptions_zip_file.filename),
            #              transcriptions_zip_file.headers)
            transcriptions_zip_filename = transcriptions_zip_file.filename.split('.')[
                0]
            # logger.debug("transcriptions_zip_file: %s\n%s",
            #              transcriptions_zip_filename,
            #              len(transcriptions_zip_filename))
            if (len(transcriptions_zip_filename) != 0):
                tagset_project_ids["Audio Annotation"] = saveTagset.save_tagset(tagsets,
                                                                                transcriptions_zip_file,
                                                                                project_name)
            else:
                tagset_name = new_data_form['transcriptionstagsetuploadselect'][0]
                tagset_project_ids["Audio Annotation"] = tagset_details.get_tagset_id(tagsets,
                                                                                      tagset_name)
        else:
            tagset_name = new_data_form['transcriptionstagsetuploadselect'][0]
            tagset_project_ids["Audio Annotation"] = tagset_details.get_tagset_id(tagsets,
                                                                                  tagset_name)
        logger.debug("tagset_project_ids: %s,\nType: %s",
                     tagset_project_ids,
                     type(tagset_project_ids))
        final_tagset_project_ids.extend(tagset_project_ids["Audio Annotation"])
    if ("transcriptionsboundarytagsetuploadcheckbox" in new_data_form and
            new_data_form["transcriptionsboundarytagsetuploadcheckbox"][0] == "on"):
        if 'transcriptionsboundarytagsetZipFile' in new_data_form_files:
            transcriptions_zip_file = new_data_form_files["transcriptionsboundarytagsetZipFile"]
            # logger.debug("transcriptions_zip_file: %s\n%s\n%s\n%s\n%s",
            #              type(transcriptions_zip_file),
            #              transcriptions_zip_file,
            #              transcriptions_zip_file.filename,
            #              len(transcriptions_zip_file.filename),
            #              transcriptions_zip_file.headers)
            transcriptions_zip_filename = transcriptions_zip_file.filename.split('.')[
                0]
            # logger.debug("transcriptions_zip_file: %s\n%s",
            #              transcriptions_zip_filename,
            #              len(transcriptions_zip_filename))
            if (len(transcriptions_zip_filename) != 0):
                tagset_project_ids["Boundary Annotation"] = saveTagset.save_tagset(tagsets,
                                                                                   transcriptions_zip_file,
                                                                                   project_name)
            else:
                tagset_name = new_data_form['transcriptionsboundarytagsetuploadselect'][0]
                tagset_project_ids["Boundary Annotation"] = tagset_details.get_tagset_id(tagsets,
                                                                                         tagset_name)
        else:
            tagset_name = new_data_form['transcriptionsboundarytagsetuploadselect'][0]
            tagset_project_ids["Boundary Annotation"] = tagset_details.get_tagset_id(tagsets,
                                                                                     tagset_name)
        logger.debug("tagset_project_ids: %s,\nType: %s",
                     tagset_project_ids,
                     type(tagset_project_ids))
        final_tagset_project_ids.extend(
            tagset_project_ids["Boundary Annotation"])
    logger.debug("final tagset_project_ids: %s,\nType: %s",
                 final_tagset_project_ids,
                 type(final_tagset_project_ids))
    projects.update_one({"projectname": project_name},
                        {"$set": {
                            "tagsetId": final_tagset_project_ids
                        }})
    if (len(tagset_project_ids) != 0):
        new_data_form.update(tagset_project_ids)
    saved_new_transcription_form, save_status = save_new_transcription_form.save_new_transcription_form(projectsform,
                                                                                                        project_name,
                                                                                                        new_data_form,
                                                                                                        current_username)
    return redirect(url_for("lifedata.transcription.home"))


@lifedata.route('/annotation', methods=['GET', 'POST'])
@login_required
def annotation():
    projects_collection, userprojects_collection, annotation_collection, tagsets_collection, sourcedetails_collection = getdbcollections.getdbcollections(mongo,
                                                                                                                                                          "projects",
                                                                                                                                                          "userprojects",
                                                                                                                                                          "annotation",
                                                                                                                                                          "tagsets",
                                                                                                                                                          "sourcedetails")
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects_collection)

    project_details = annotationdetails.get_annotation_data(projects_collection,
                                                            userprojects_collection,
                                                            annotation_collection,
                                                            tagsets_collection,
                                                            sourcedetails_collection,
                                                            current_username,
                                                            activeprojectname)
    if not project_details:
        flash("Plese select a project from active project list")
        return redirect(url_for("home"))

    return render_template("lifedataannotation.html",
                           projectName=activeprojectname,
                           proj_data=project_details
                           )


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
        project_form = projectsform.find_one({"projectname": project_name})
        langscripts = project_form["Prompt Type"][1]
        languageslist = [{"id": "", "text": ""}]
        for lang_script, lang_info in langscripts.items():
            languageslist.append({"id": lang_script, "text": lang_script})
            # if ('data' in lang_info):
            #     langscript.append(lang_script)
    elif (project_type == "crawling"):
        project_data = projects.find_one({"projectname": project_name})
        langscripts = project_data["crawlerLanguage"]
        languageslist = [{"id": "", "text": ""}]
        for lang_script in langscripts:
            languageslist.append({"id": lang_script, "text": lang_script})

    return jsonify(languageslist=languageslist)


@lifedata.route('/datazipfile', methods=['GET', 'POST'])
@login_required
def datazipfile():
    try:
        projects, tagsets, = getdbcollections.getdbcollections(mongo,
                                                               'projects',
                                                               'tagsets')
        if request.method == "POST":
            form_data = dict(request.form.lists())
            logger.debug("form data: %s", pformat(form_data))
            derive_from_project_name = form_data['deriveFromProjectName'][0]
            project_type = form_data['projectType'][0]
            # logger.debug("derive_from_project_name: %s", derive_from_project_name)
            data_zip_file = request.files.to_dict()
            logger.debug("data_zip_file: %s", data_zip_file)
            if (project_type == 'validation'):
                data_zip_file = data_zip_file['tagsetZipFile']
            elif (project_type == 'transcriptions'):
                data_zip_file = data_zip_file['transcriptionstagsetZipFile']
            # logger.debug("data_zip_file: %s", data_zip_file)
            completed, message, data_tagset = readzip.read_zip(
                tagsets, data_zip_file)
            # logger.debug('completed: %s', completed)
            # logger.debug('message: %s', message)
            # logger.debug('data_tagset: %s', data_tagset)
            if (completed):
                if (project_type == 'transcriptions'):
                    return jsonify(completed=completed,
                                   message=message,
                                   mappingTagset={},
                                   validationTagsetKeys=[])
                else:
                    validation_tagset_keys = list(data_tagset.keys())
            else:
                return jsonify(completed=completed,
                               message=message,
                               mappingTagset={},
                               validationTagsetKeys=[])

            derive_from_project_type = getprojecttype.getprojecttype(
                projects, derive_from_project_name)
            # logger.debug("derive_from_project_type: %s", derive_from_project_type)
            if (derive_from_project_type == 'recordings'):
                derive_from_project_tagset = ['data_Recording']
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

        if request.method == 'POST':
            new_crawl_data_form = dict(request.form.lists())
            logger.debug('new_crawl_data_form: %s',
                         pformat(new_crawl_data_form))
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
            # flash("Crawling Complete.")
            return redirect(url_for("lifedata.crawler"))
        else:
            activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                          userprojects)
            shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                              current_username,
                                                              activeprojectname)
            data_sub_source = data_project_info.get_data_sub_source(projects,
                                                                    activeprojectname)
            if (shareinfo["sharemode"] == 0):
                return redirect(url_for('lifedata.crawlerbrowse'))

    except:
        logger.exception("")

    return render_template('crawler.html',
                           projectName=activeprojectname,
                           shareinfo=shareinfo,
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
        project_owner = getprojectowner.getprojectowner(
            projects_collection, activeprojectname)

        logger.debug("Current active project name %s", activeprojectname)

        if request.method == 'POST':
            to_crawl_video_ids = []
            youtube_crawler_info = dict(request.form.lists())
            logger.debug('youtube_crawler_info: %s',
                         pformat(youtube_crawler_info))
            # logger.debug('%s', pformat(youtube_crawler_info['dataLinks'][0].split('\r\n')))
            api_key = youtube_crawler_info['youtubeAPIKey'][0]
            youtube_data_for = youtube_crawler_info['youtubeDataFor'][0]
            youtube_data_type = youtube_crawler_info['youtubeDataType']
            data_links = {}
            # data_links_list = youtube_crawler_info['dataLinks'][0].split('\r\n')
            # data_links = {youtube_data_for: data_links_list}
            data_links_info = {}

            if youtube_data_for == 'topn':
                search_query = youtube_crawler_info['youtubeTopNSearchQuery'][0]
                video_count = youtube_crawler_info['youtubeTopNVideoCount'][0]
                video_license = youtube_crawler_info['youtubeVideoLicense'][0]

                searchkeywords_value = [search_query]
                topn_video_links = youtubecrawl.get_topn_videos(api_key,
                                                                search_query,
                                                                video_count,
                                                                video_license)
                if ('youtubeTopNSearchTags' in youtube_crawler_info):
                    searchkeywords_value.extend(
                        youtube_crawler_info['youtubeTopNSearchTags'])
                for link in topn_video_links:
                    data_links_info[link] = searchkeywords_value
                    video_id = link[link.find('?v=')+3:].strip()
                    to_crawl_video_ids.append(video_id)
            else:
                for key, value in youtube_crawler_info.items():
                    if ('videoschannelId' in key):
                        videoschannelId_count = key.split('_')[-1]
                        searchkeywords_key = 'searchkeywords_'+videoschannelId_count
                        if (searchkeywords_key in youtube_crawler_info):
                            searchkeywords_value = youtube_crawler_info[searchkeywords_key]
                        else:
                            searchkeywords_value = []
                        for link in value:
                            data_links_info[link] = searchkeywords_value
                            video_id = link[link.find('?v=')+3:].strip()
                            to_crawl_video_ids.append(video_id)
                        # logger.debug('key: %s, videoschannelId_count: %s, value: %s, searchkeywords_key: %s, searchkeywords_value: %s',
                        #              key, videoschannelId_count, value, searchkeywords_key, searchkeywords_value)
            data_links[youtube_data_for] = data_links_info
            logger.debug("data_links_info: %s", pformat(data_links_info))
            logger.debug("data_links: %s", pformat(data_links))

            logger.debug("Current active project name %s", activeprojectname)
            crawled_video_ids = youtubecrawl.run_youtube_crawler(mongo, projects_collection,
                                                                 userprojects_collection,
                                                                 sourcedetails_collection,
                                                                 crawling_collection,
                                                                 project_owner,
                                                                 current_username,
                                                                 activeprojectname,
                                                                 api_key,
                                                                 data_links,
                                                                 download_items=youtube_data_type)
            # logger.debug('to_crawl_video_ids: %s, crawled_video_ids: %s',
            #              to_crawl_video_ids,
            #              crawled_video_ids)
            crawl_video_ids_diff = list(
                set(to_crawl_video_ids)-set(crawled_video_ids))
            # logger.debug("crawl_video_ids_diff: %s", crawl_video_ids_diff)
            projects_collection.update_one(
                {
                    'projectname': activeprojectname
                },
                {
                    '$addToSet':
                    {
                        'sourceIds.'+current_username:
                        {
                            '$each': crawl_video_ids_diff
                        }
                    }
                }
            )
            flash("Crawling Complete.")
            return redirect(url_for("lifedata.crawler"))
    except:
        logger.exception("")

    return redirect(url_for("lifedata.crawler"))


@lifedata.route('/retrieve/<filename>', methods=['GET'])
@login_required
def retrieve(filename):
    logger.debug('Now in retrieve')
    x = ''
    try:
        userprojects, = getdbcollections.getdbcollections(mongo,
                                                          'userprojects')

        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)

        # share_info = getuserprojectinfo.getuserprojectinfo(userprojects,
        #                                                     current_username,
        #                                                     activeprojectname)
        # if ("downloadchecked" in share_info and
        #     share_info["downloadchecked"] == 'true'):
        # logger.debug("share_info: %s", share_info)
        x = mongo.send_file(filename)
        # logger.debug("mongo send file: %s, %s, %s, %s, %s, %s", x.response, x.status, x.headers, x.mimetype, x.content_type, x.direct_passthrough)
    except:
        logger.exception("")

    return x


@lifedata.route('/crawleraudiobrowseactionplay', methods=['GET', 'POST'])
@login_required
def crawleraudiobrowseactionplay():
    audio_data_fields = ['audioId', 'audioFilename', 'Audio File']
    audio_data_list = []
    try:
        projects, userprojects, crawling, sourcedetails_collection = getdbcollections.getdbcollections(mongo,
                                                                                                       'projects',
                                                                                                       'userprojects',
                                                                                                       'crawling',
                                                                                                       'sourcedetails')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        # logger.debug("%s,%s", current_username, activeprojectname)
        # logger.debug("THe data: %s", pformat(request.form['a']))
        # data from ajax
        if request.method == 'POST':
            data = json.loads(request.form['a'])
            # logger.debug('data lifedata/audiobrowseactionplay: : %s', pformat(data))

            # data = json.loads(request.args.get('a'))
            # logger.debug('data: %s', pformat(data))
            data_info = data['audioInfo']
            audio_browse_info = data['audioBrowseInfo']
            audio_filename = list(data_info.values())[0]
            audio_count = audio_browse_info['audioFilesCount']
            page_id = audio_browse_info['pageId']
            start_from = ((page_id*audio_count)-audio_count)
            number_of_crawled_data = page_id*audio_count
            # logger.debug("audio_filename: %s", audio_filename)
            # audio_src = url_for('retrieve', filename=audio_filename)
            audio_src = os.path.join('retrieve', audio_filename)
            # logger.debug(audio_browse_info['activeSpeakerId'])
            active_source_id = audio_browse_info['activeSpeakerId']
            crawled_data_browse_action = audio_browse_info['browseActionSelectedOption']
            # speaker_audio_ids = transcription_audiodetails.get_speaker_audio_ids_new(projects,
            #                                                                          activeprojectname,
            #                                                                          current_username,
            #                                                                          active_speaker_id,
            #                                                                          audio_browse_action=audio_browse_action)
            # audio_file_count = audio_browse_info['audioFilesCount']
            total_records = 0
            if (active_source_id != ''):
                source_data_types = sourceid_to_souremetadata.get_data_types(sourcedetails_collection,
                                                                             active_source_id,
                                                                             activeprojectname)

                # logger.debug("Source Data Types %s", source_data_types)

                if 'text' in source_data_types:
                    default_data_type = 'text'
                elif 'video' in source_data_types:
                    default_data_type = 'video'
                elif 'audio' in source_data_types:
                    default_data_type = 'audio'
                else:
                    default_data_type = 'text'

                logger.debug("Default Data Type %s", default_data_type)
                total_records, audio_data_list = crawled_data_details.get_n_crawled_data(crawling,
                                                                                         activeprojectname,
                                                                                         active_source_id,
                                                                                         data_type=default_data_type,
                                                                                         start_from=start_from,
                                                                                         number_of_crawled_data=number_of_crawled_data,
                                                                                         crawled_data_delete_flag=crawled_data_browse_action)
            else:
                audio_data_list = []

            if default_data_type == 'audio':
                # audio_filename = crawled_data_list['audioFilename']
                for i, crawled_data in enumerate(audio_data_list):
                    audio_filename = crawled_data['Data']
                    audio_data_list[i]['audioFilename'] = audio_filename
                    audio_data_list[i]['Audio File'] = url_for(
                        'retrieve', filename=audio_filename)
            # crawler_data_fields = ['audioId', 'audioFilename', 'Audio File']

            shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                              current_username,
                                                              activeprojectname)
            logger.debug("shareinfo: %s", shareinfo)
            share_mode = shareinfo['sharemode']
            share_checked = shareinfo['sharechecked']
            download_checked = shareinfo['downloadchecked']
            new_audio_data_list = audio_data_list
            return jsonify(
                audioDataFields=audio_data_fields,
                audioData=new_audio_data_list,
                shareMode=share_mode,
                totalRecords=total_records,
                shareChecked=share_checked,
                audioSource=audio_src,
                downloadChecked=download_checked
            )
    except:
        logger.exception("")
        return jsonify(audioSource='')


@lifedata.route('/crawlerbrowse', methods=['GET', 'POST'])
@login_required
def crawlerbrowse():
    crawler_data_fields = ['dataId', 'Data']
    try:
        new_data = {}
        projects, userprojects, crawling, sourcedetails_collection = getdbcollections.getdbcollections(mongo,
                                                                                                       'projects',
                                                                                                       'userprojects',
                                                                                                       'crawling',
                                                                                                       'sourcedetails')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        projectowner = getprojectowner.getprojectowner(
            projects, activeprojectname)
        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                          current_username,
                                                          activeprojectname)
        sourceids = projects.find_one({"projectname": activeprojectname},
                                      {"_id": 0, "sourceIds." + current_username: 1})
        # logger.debug('sourceids: %s', pformat(sourceids))
        if (sourceids["sourceIds"]):
            sourceids = sourceids["sourceIds"][current_username]
            source_metadata = sourceid_to_souremetadata.get_source_metadata(sourcedetails_collection,
                                                                            sourceids,
                                                                            activeprojectname)
            # logger.debug('source_metadata: %s', source_metadata)
            # sourceids.append('')
        else:
            # sourceids = ['']
            source_metadata = {}
        if ('activesourceId' in shareinfo):
            active_source_id = shareinfo['activesourceId']
        else:
            active_source_id = ''
        total_records = 0
        if (active_source_id != ''):
            source_data_types = sourceid_to_souremetadata.get_data_types(sourcedetails_collection,
                                                                         active_source_id,
                                                                         activeprojectname)

            # logger.debug("Source Data Types %s", source_data_types)

            if 'text' in source_data_types:
                default_data_type = 'text'
            elif 'video' in source_data_types:
                default_data_type = 'video'
            elif 'audio' in source_data_types:
                default_data_type = 'audio'
            else:
                default_data_type = 'text'

            # logger.debug("Default Data Type %s", default_data_type)

            total_records, crawled_data_list = crawled_data_details.get_n_crawled_data(crawling,
                                                                                       activeprojectname,
                                                                                       active_source_id,
                                                                                       data_type=default_data_type)
        else:
            crawled_data_list = []
            default_data_type = ''
            source_data_types = []

        # logger.debug('crawled_data_list: %s', crawled_data_list)

        if default_data_type == 'audio':
            # audio_filename = crawled_data_list['audioFilename']
            for i, crawled_data in enumerate(crawled_data_list):
                audio_filename = crawled_data['Data']
                crawled_data_list[i]['audioFilename'] = audio_filename
                crawled_data_list[i]['Audio File'] = url_for(
                    'retrieve', filename=audio_filename)
            crawler_data_fields = ['audioId', 'audioFilename', 'Audio File']

        if default_data_type == 'video':
            video_filename = crawled_data_list['videoFilename']
            crawled_data_list['Video File'] = url_for(
                'retrieve', filename=video_filename)

        # logger.debug("Crawled data list %s", crawled_data_list)
        # get crawled file src
        # new_crawled_data_list = []
        # for crawled_data in crawled_data_list:
        #     new_crawled_data = crawled_data
        #     crawled_filename = crawled_data['crawledFilename']
        #     new_crawled_data['data File'] = url_for('retrieve', filename=crawled_filename)
        #     new_crawled_data_list.append(new_crawled_data)
        new_data['currentUsername'] = current_username
        new_data['activeProjectName'] = activeprojectname
        new_data['projectOwner'] = projectowner
        new_data['shareInfo'] = shareinfo
        new_data['sourceIds'] = sourceids
        new_data['crawlerData'] = crawled_data_list
        new_data['crawlerDataFields'] = crawler_data_fields
        new_data['sourceMetadata'] = source_metadata
        new_data['totalRecords'] = total_records
        new_data['dataTypes'] = source_data_types
        new_data['defaultDataType'] = default_data_type
        # logger.debug('new_data: %s', pformat(new_data))
    except:
        logger.exception("")

    return render_template('crawlerbrowse.html',
                           projectName=activeprojectname,
                           shareinfo=shareinfo,
                           newData=new_data)


@lifedata.route('/updatecrawlerbrowsetable', methods=['GET', 'POST'])
@login_required
def updatecrawlerbrowsetable():
    crawler_data_fields = ['dataId', 'Data']
    crawled_data_list = []
    try:
        # data through ajax
        crawler_browse_info = json.loads(request.args.get('a'))
        logger.debug('crawler_browse_info: %s', pformat(crawler_browse_info))
        userprojects, crawling = getdbcollections.getdbcollections(mongo,
                                                                   'userprojects',
                                                                   'crawling')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        logger.debug(crawler_browse_info['activeSourceId'])
        active_source_id = crawler_browse_info['activeSourceId']
        crawled_data_count = crawler_browse_info['crawledDataCount']
        crawled_data_browse_action = crawler_browse_info['browseActionSelectedOption']
        data_type = crawler_browse_info['dataType']
        if (active_source_id != ''):
            total_records, crawled_data_list = crawled_data_details.get_n_crawled_data(crawling,
                                                                                       activeprojectname,
                                                                                       active_source_id,
                                                                                       data_type=data_type,
                                                                                       start_from=0,
                                                                                       number_of_crawled_data=crawled_data_count,
                                                                                       crawled_data_delete_flag=crawled_data_browse_action)
        else:
            crawled_data_list = []

        if data_type == 'audio':
            # audio_filename = crawled_data_list['audioFilename']
            for i, crawled_data in enumerate(crawled_data_list):
                audio_filename = crawled_data['Data']
                crawled_data_list[i]['audioFilename'] = audio_filename
                crawled_data_list[i]['Audio File'] = url_for(
                    'retrieve', filename=audio_filename)
            crawler_data_fields = ['audioId', 'audioFilename', 'Audio File']

        if data_type == 'video':
            video_filename = crawled_data_list['videoFilename']
            crawled_data_list['Video File'] = url_for(
                'retrieve', filename=video_filename)
            # crawled_data_list.append(new_audio_data)
        # logger.debug('crawler_data_list: %s', pformat(crawler_data_list))
        # get crawler file src
        # new_crawled_data_list = []
        # for crawler_data in crawler_data_list:
        #     new_crawler_data = crawler_data
        #     crawler_filename = crawler_data['crawlerFilename']
        #     new_crawler_data['crawler File'] = url_for('retrieve', filename=crawler_filename)
        #     new_crawler_data_list.append(new_crawler_data)
        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                          current_username,
                                                          activeprojectname)
        share_mode = shareinfo['sharemode']
    except:
        logger.exception("")

    return jsonify(crawledDataFields=crawler_data_fields,
                   crawledData=crawled_data_list,
                   shareMode=share_mode,
                   totalRecords=total_records,
                   dataType=data_type)


@lifedata.route('/crawlerbrowseaction', methods=['GET', 'POST'])
@login_required
def crawlerbrowseaction():
    try:
        projects_collection, userprojects, crawling_collection = getdbcollections.getdbcollections(mongo,
                                                                                                   'projects',
                                                                                                   'userprojects',
                                                                                                   'crawling')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(
            current_username, userprojects)
        logger.debug("%s,%s", current_username, activeprojectname)
        # data from ajax
        data = json.loads(request.args.get('a'))
        logger.debug('data: %s', pformat(data))
        data_info = data['dataInfo']
        logger.debug('data_info: %s', pformat(data_info))
        crawler_browse_info = data['crawlerBrowseInfo']
        logger.debug('crawler_browse_info: %s', pformat(crawler_browse_info))
        browse_action = crawler_browse_info['browseActionSelectedOption']
        active_source_id = crawler_browse_info['activeSourceId']
        data_ids_list = list(data_info.keys())
        data_type = crawler_browse_info['dataType']

        for crawler_id in data_ids_list:
            if (browse_action):
                logger.info("crawler id to revoke: %s, %s",
                            crawler_id, type(crawler_id))
            else:
                logger.info("crawler id to delete: %s, %s",
                            crawler_id, type(crawler_id))
            if (browse_action):
                crawled_data_details.revoke_deleted_data(projects_collection,
                                                         crawling_collection,
                                                         activeprojectname,
                                                         active_source_id,
                                                         crawler_id,
                                                         data_type)
            else:
                crawled_data_details.delete_one_data(projects_collection,
                                                     crawling_collection,
                                                     activeprojectname,
                                                     current_username,
                                                     active_source_id,
                                                     crawler_id,
                                                     data_type)
        if (browse_action):
            flash("Data revoked successfully")
        else:
            flash("Data deleted successfully")
    except:
        logger.exception("")

    return 'OK'

@lifedata.route('/crawlerbrowseactionviewdata', methods=['GET', 'POST'])
@login_required
def crawlerbrowseactionviewdata():
    try:
        userprojects, crawling_collection = getdbcollections.getdbcollections(mongo,
                                                                              'userprojects',
                                                                              'crawling')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(
            current_username, userprojects)
        # logger.debug("%s, %s", current_username, activeprojectname)
        # data from ajax
        data = json.loads(request.args.get('a'))
        # logger.debug('data: %s', pformat(data))
        data_info = data['dataInfo']
        # logger.debug('data_info: %s', pformat(data_info))
        crawler_browse_info = data['crawlerBrowseInfo']
        # logger.debug('crawler_browse_info: %s', pformat(crawler_browse_info))
        # browse_action = crawler_browse_info['browseActionSelectedOption']
        active_source_id = crawler_browse_info['activeSourceId']
        # logger.debug(active_source_id)
        data_id = list(data_info.keys())[0]
        # logger.debug(data_id)
        comment_info = crawling_collection.find_one({"projectname": activeprojectname,
                                                     "lifesourceid": active_source_id,
                                                     "$or": [
                                                        { "dataId": data_id },
                                                        { "audioId": data_id }
                                                    ]},
                                                    {"_id": 0,
                                                    #  "additionalInfo.comment_info": 1,
                                                    "additionalInfo": 1
                                                     })
        # logger.debug(pformat(comment_info))
        # comment_info = comment_info["additionalInfo"]["comment_info"]
        comment_info = comment_info["additionalInfo"]
        # logger.debug("comment_info: %s", pformat(comment_info))
        return jsonify(commentInfo=comment_info)
    except:
        logger.exception("")
        return jsonify(commentInfo={})


@lifedata.route('/crawlerbrowsechangepage', methods=['GET', 'POST'])
@login_required
def crawlerbrowsechangepage():
    crawler_data_fields = ['dataId', 'Data']
    crawled_data_list = []
    try:
        # data through ajax
        crawler_browse_info = json.loads(request.args.get('a'))
        # logger.debug('crawler_browse_info: %s', pformat(crawler_browse_info))
        userprojects, crawling = getdbcollections.getdbcollections(mongo,
                                                                   'userprojects',
                                                                   'crawling')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        # logger.debug(crawler_browse_info['activeSourceId'])
        data_type = crawler_browse_info['dataType']
        active_source_id = crawler_browse_info['activeSourceId']
        crawled_data_count = crawler_browse_info['crawledDataCount']
        crawled_data_browse_action = crawler_browse_info['browseActionSelectedOption']
        page_id = crawler_browse_info['pageId']
        start_from = ((page_id*crawled_data_count)-crawled_data_count)
        number_of_crawled_data = page_id*crawled_data_count
        # logger.debug('pageId: %s, start_from: %s, number_of_crawled_data: %s',
        #              page_id, start_from, number_of_crawled_data)
        total_records = 0
        if (active_source_id != ''):
            total_records, crawled_data_list = crawled_data_details.get_n_crawled_data(crawling,
                                                                                       activeprojectname,
                                                                                       active_source_id,
                                                                                       data_type=data_type,
                                                                                       start_from=start_from,
                                                                                       number_of_crawled_data=number_of_crawled_data,
                                                                                       crawled_data_delete_flag=crawled_data_browse_action)
        else:
            crawled_data_list = []
        # logger.debug('crawled_data_list: %s', pformat(crawled_data_list))

        if data_type == 'audio':
            # audio_filename = crawled_data_list['audioFilename']
            for i, crawled_data in enumerate(crawled_data_list):
                audio_filename = crawled_data['Data']
                crawled_data_list[i]['audioFilename'] = audio_filename
                crawled_data_list[i]['Audio File'] = url_for(
                    'retrieve', filename=audio_filename)
            crawler_data_fields = ['audioId', 'audioFilename', 'Audio File']

        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                          current_username,
                                                          activeprojectname)
        share_mode = shareinfo['sharemode']
    except:
        logger.exception("")

    return jsonify(crawledDataFields=crawler_data_fields,
                   crawledData=crawled_data_list,
                   shareMode=share_mode,
                   totalRecords=total_records,
                   activePage=page_id,
                   dataType=data_type)


@lifedata.route('/getIdList', methods=['GET', 'POST'])
def getIdList():
    '''
    get list of all Ids
    '''
    allIds = []
    try:
        projects_collection, userprojects_collection = getdbcollections.getdbcollections(mongo,
                                                                                         "projects",
                                                                                         "userprojects")
        current_username = getcurrentusername.getcurrentusername()
        active_project_name = getactiveprojectname.getactiveprojectname(current_username,
                                                                        userprojects_collection)
        active_source_id = getuserprojectinfo.getuserprojectinfo(userprojects_collection,
                                                                 current_username,
                                                                 active_project_name)
        if ('activesourceId' in active_source_id):
            active_source_id = active_source_id['activesourceId']
        else:
            active_source_id = ''
        project_type = getprojecttype.getprojecttype(projects_collection,
                                                     active_project_name)
        data_collection, = getdbcollections.getdbcollections(mongo,
                                                             project_type)
        allIds = annotationdetails.get_annotation_ids_list(data_collection,
                                                           active_project_name,
                                                           active_source_id)
    except:
        logger.exception("")

    return jsonify(allIds=allIds)


@lifedata.route('/allunannotated', methods=['GET', 'POST'])
def allunannotated():
    '''
    get list of all annotated and all unannotated data by that user for that file
    '''
    allunanno = []
    allanno = []
    try:
        projects, userprojects, annotation = getdbcollections.getdbcollections(mongo,
                                                                               'projects',
                                                                               'userprojects',
                                                                               'annotation')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        active_source_id = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                 current_username,
                                                                 activeprojectname)
        if ('activesourceId' in active_source_id):
            active_source_id = active_source_id['activesourceId']
        else:
            active_source_id = ''
        for unannodata in annotation.find({"projectname": activeprojectname, "lifesourceid": active_source_id},
                                          {"_id": 0, "dataId": 1, "dataMetadata.ID": 1, current_username: 1}):

            if (current_username not in unannodata):
                allunanno.append(unannodata)
            elif (current_username in unannodata and
                    unannodata[current_username]["annotatedFLAG"] == 0):
                unannodata.pop(current_username)
                allunanno.append(unannodata)
            elif (current_username in unannodata and
                    unannodata[current_username]["annotatedFLAG"] == 1):
                unannodata.pop(current_username)
                allanno.append(unannodata)
    except:
        logger.exception("")

    return jsonify(allunanno=allunanno, allanno=allanno)


@lifedata.route('/loadunannotext', methods=['GET'])
@login_required
def loadunannotext():
    try:
        projects, userprojects, annotation = getdbcollections.getdbcollections(mongo,
                                                                               'projects',
                                                                               'userprojects',
                                                                               'annotation')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        active_source_id = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                 current_username,
                                                                 activeprojectname)
        if ('activesourceId' in active_source_id):
            active_source_id = active_source_id['activesourceId']
        else:
            active_source_id = ''

        lastActiveId = request.args.get('data')
        lastActiveId = eval(lastActiveId)
        logger.debug("lastActiveId: %s", lastActiveId)

        projects.update_one({"projectname": activeprojectname},
                            {'$set': {'lastActiveId.'+current_username+'.'+active_source_id+'.dataId': lastActiveId}})
    except:
        logger.debug("")

    return redirect(url_for('lifedata.annotation'))


@lifedata.route('/loadpreviousdata', methods=['GET', 'POST'])
@login_required
def loadpreviousdata():
    newdataId = 0
    try:
        projects, userprojects = getdbcollections.getdbcollections(mongo,
                                                                   'projects',
                                                                   'userprojects')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        active_source_id = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                 current_username,
                                                                 activeprojectname)
        if ('activesourceId' in active_source_id):
            active_source_id = active_source_id['activesourceId']
        else:
            active_source_id = ''
        # data through ajax
        lastActiveId = request.args.get('data')
        lastActiveId = eval(lastActiveId)
        latest_data_id = ''
        if (len(lastActiveId) != 0):
            latest_data_id = annotationdetails.getnewdataid(projects,
                                                            activeprojectname,
                                                            lastActiveId,
                                                            active_source_id,
                                                            'previous')
            annotationdetails.updatelatestdataid(projects,
                                                 activeprojectname,
                                                 latest_data_id,
                                                 current_username,
                                                 active_source_id)
    except:
        logger.debug("")

    return jsonify(newdataId=latest_data_id)


@lifedata.route('/loadnextdata', methods=['GET', 'POST'])
@login_required
def loadnextdata():
    newdataId = 0
    try:
        projects, userprojects = getdbcollections.getdbcollections(mongo,
                                                                   'projects',
                                                                   'userprojects')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        active_source_id = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                 current_username,
                                                                 activeprojectname)
        if ('activesourceId' in active_source_id):
            active_source_id = active_source_id['activesourceId']
        else:
            active_source_id = ''
        # data through ajax
        lastActiveId = request.args.get('data')
        lastActiveId = eval(lastActiveId)
        latest_data_id = ''
        if (len(lastActiveId) != 0):
            latest_data_id = annotationdetails.getnewdataid(projects,
                                                            activeprojectname,
                                                            lastActiveId,
                                                            active_source_id,
                                                            'next')
            annotationdetails.updatelatestdataid(projects,
                                                 activeprojectname,
                                                 latest_data_id,
                                                 current_username,
                                                 active_source_id)
    except:
        logger.exception("")
    return jsonify(newdataId=latest_data_id)


def modalCategory(category, tagset, saveannotationCategoryDependency):
    try:
        modal_category = False
        # print('saveannotationCategoryDependency', saveannotationCategoryDependency[category])
        while (modal_category != True):
            # if (category in saveannotationCategoryDependency):
            # print(category, 'saveannotationCategoryDependency', saveannotationCategoryDependency[category])
            for tag_set_key, tag_set_value in tagset.items():
                if (category in saveannotationCategoryDependency):
                    # print(category, tag_set_key, tag_set_value)
                    if (tag_set_key in saveannotationCategoryDependency[category]):
                        # print(category, tag_set_key, tag_set_value)
                        if (tag_set_value[0] == '#SPAN_TEXT#'):
                            return (True, tag_set_key)
                        else:
                            # return (False, tag_set_key)
                            modal_category = False
                            category = tag_set_key
                            # print(modal_category, category, tag_set_key, tag_set_value)
                            # print('2. saveannotationCategoryDependency', saveannotationCategoryDependency[category])
                else:
                    return (False, category)
    except:
        logger.exception("")


@lifedata.route('/saveannotation', methods=['GET', 'POST'])
@login_required
def saveannotation():
    try:
        projects, userprojects, annotation, tagsets = getdbcollections.getdbcollections(mongo,
                                                                                        'projects',
                                                                                        'userprojects',
                                                                                        'annotation',
                                                                                        'tagsets')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)

        if request.method == 'POST':
            annotatedText = json.loads(request.form['a'])
            # logger.debug("annotatedText saveannotation() : %s", pformat(annotatedText))
            lastActiveId = annotatedText['lastActiveId'][0]
            active_source_id = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                     current_username,
                                                                     activeprojectname)
            if ('activesourceId' in active_source_id):
                active_source_id = active_source_id['activesourceId']
            else:
                active_source_id = ''
            nextId = annotationdetails.getnewdataid(projects,
                                                    activeprojectname,
                                                    lastActiveId,
                                                    active_source_id,
                                                    'next')
            project_details = projects.find_one({"projectname": activeprojectname},
                                                {"_id": 0, "tagsetId": 1})
            tag_set_id = project_details["tagsetId"]
            tag_set = tagsets.find_one({"_id": tag_set_id})
            tagset = tag_set['tagSet']
            tagSetMetaData = tag_set['tagSetMetaData']
            annotationGrid = {}
            # current user tags for the text
            currentAnnotatorTags = {}
            # for tagset in project_details.values():
            # print('tagset', tagset)
            categories = list(tagset.keys())
            # print('\n\ncategories\n\n', categories)
            for category in categories:
                if category in annotatedText:
                    # print(category, annotatedText[category], len(annotatedText[category]), type(annotatedText[category]))
                    if isinstance(annotatedText[category], dict):
                        currentAnnotatorTags[category] = annotatedText[category]
                    elif (len(annotatedText[category])) == 1:
                        if ('categoryHtmlElement' in tagSetMetaData):
                            if (tagSetMetaData['categoryHtmlElement'][category] == 'select'):
                                currentAnnotatorTags[category] = annotatedText[category]
                            else:
                                currentAnnotatorTags[category] = annotatedText[category][0]
                        else:
                            currentAnnotatorTags[category] = annotatedText[category][0]
                    elif (len(annotatedText[category])) > 1:
                        currentAnnotatorTags[category] = annotatedText[category]
                elif category not in annotatedText:
                    # print(tagset[category])
                    if (tagset[category][0] == '#SPAN_TEXT#'):
                        continue
                    elif ('categoryDependency' in tagSetMetaData):
                        saveannotationCategoryDependency = tagSetMetaData['categoryDependency']
                        modal_category, next_category = modalCategory(
                            category, tagset, saveannotationCategoryDependency)
                        # print(modal_category, next_category)
                        # print()
                        if (modal_category):
                            continue
                        else:
                            currentAnnotatorTags[category] = ''
            if "Duplicate" in currentAnnotatorTags:
                currentAnnotatorTags["Duplicate"] = annotatedText["Duplicate Text"][0]

            if 'annotatorComment' in currentAnnotatorTags:
                currentAnnotatorTags["annotatorComment"] = annotatedText["annotatorComment"][0]

            once_annotated = annotation.find_one({"projectname": activeprojectname,
                                                  "lifesourceid": active_source_id,
                                                  "dataId": lastActiveId},
                                                 {"_id": 0})

            if once_annotated != None:
                # update with this user annotation and change lastUpdatedBy
                currentAnnotatorTags = currentAnnotatorTags
                # print(currentAnnotatorTags, '\n=============\n', once_annotated[current_username])
                # if difference between new annotation and existing annotation is False
                # (user has used 'Save' in place of 'Next' button)
                # Then there should be no update in the allAccess and allUpdates timestamp
                # print(diff(currentAnnotatorTags, once_annotated[current_username]))
                if (current_username in once_annotated and
                        not bool(diff(currentAnnotatorTags, once_annotated[current_username]['annotationGrid']))):
                    projects.update_one({"projectname": activeprojectname},
                                        {'$set': {'lastActiveId.'+current_username+'.'+active_source_id+'.dataId': nextId}})
                    logger.info('matchedddddddddddddddddddddddd')
                    return redirect(url_for('lifedata.annotation'))

                lastUpdatedBy = current_username

                all_access = once_annotated["allAccess"]
                all_updates = once_annotated["allUpdates"]

                if (current_username in all_access.keys()):
                    # print(all_access, all_updates)
                    all_access[current_username].append(
                        annotatedText["accessedOnTime"][0])
                    all_updates[current_username].append(
                        datetime.now().strftime("%d/%m/%y %H:%M:%S"))
                    # print(all_access, all_updates)
                else:
                    all_access[current_username] = [
                        annotatedText["accessedOnTime"][0]]
                    all_updates[current_username] = [
                        datetime.now().strftime("%d/%m/%y %H:%M:%S")]

                oldAnnotation = annotation.find_one({"projectname": activeprojectname,
                                                    "lifesourceid": active_source_id,
                                                     "dataId": lastActiveId},
                                                    {"_id": 0, current_username: 1})
                # print(oldAnnotation)
                if (current_username in oldAnnotation):
                    oldAnnotation = oldAnnotation[current_username]['annotationGrid']
                    mergeredAnnotation = {
                        **oldAnnotation, **currentAnnotatorTags}
                else:
                    mergeredAnnotation = currentAnnotatorTags

                annotation.update_one({"projectname": activeprojectname,
                                       "lifesourceid": active_source_id,
                                       "dataId": lastActiveId},
                                      {'$set':
                                       {'lastUpdatedBy': lastUpdatedBy,
                                        current_username: {'annotationGrid': mergeredAnnotation,
                                                           "annotatedFLAG": 1},
                                        "allAccess": all_access,
                                        "allUpdates": all_updates,
                                        'annotationGrid': mergeredAnnotation,
                                        "annotatedFLAG": 1}})
            else:
                text_anno = {}
                text_anno[current_username]['annotationGrid'] = currentAnnotatorTags
                text_anno[current_username]['annotatedFLAG'] = 1
                text_anno['lastUpdatedBy'] = current_username
                all_access = {}
                all_access[current_username] = [
                    annotatedText["accessedOnTime"][0]]
                text_anno['allAccess'] = all_access
                all_updates = {}
                all_updates[current_username] = [
                    datetime.now().strftime("%d/%m/%y %H:%M:%S")]
                text_anno['allUpdates'] = all_updates

                # annotation.insert_one(text_anno)
                annotation.update_one({"projectname": activeprojectname,
                                       "lifesourceid": active_source_id,
                                       "dataId": lastActiveId},
                                      {'$set':
                                       {current_username: {'annotationGrid': currentAnnotatorTags,
                                                           'annotatedFLAG': 1},
                                        'lastUpdatedBy': current_username,
                                        'allUpdates': all_updates,
                                        'allAccess':  all_access,
                                        'annotationGrid': currentAnnotatorTags,
                                        'annotatedFLAG': 1
                                        }})

            projects.update_one({"projectname": activeprojectname},
                                {'$set': {'lastActiveId.'+current_username+'.'+active_source_id+'.dataId': nextId}})

            return redirect(url_for('lifedata.annotation'))
    except:
        logger.exception("")

    return redirect(url_for('lifedata.annotation'))


@lifedata.route('/saveannotationspan', methods=['GET', 'POST'])
@login_required
def saveannotationspan():
    try:
        # print('IN /saveannotationSpan')
        userprojects, annotation = getdbcollections.getdbcollections(mongo,
                                                                     'userprojects',
                                                                     'annotation')

        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)

        if request.method == 'POST':
            # annotatedText = dict(request.form.lists())

            annotatedTextSpan = json.loads(request.form['a'])
            # pprint(annotatedTextSpan)

            # lastActiveId = annotatedTextSpan['lastActiveId'][0]
            lastActiveId = annotatedTextSpan['lastActiveId']
            del annotatedTextSpan['lastActiveId']
            # annotatedTextSpan['annotatedFLAG'] = 1
            # pprint(annotatedTextSpan)
            # print(lastActiveId)
            active_source_id = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                     current_username,
                                                                     activeprojectname)
            if ('activesourceId' in active_source_id):
                active_source_id = active_source_id['activesourceId']
            else:
                active_source_id = ''
            for key, value in annotatedTextSpan.items():
                for k, v in value.items():
                    annotation.update_one({"projectname": activeprojectname,
                                           "lifesourceid": active_source_id,
                                           "dataId": lastActiveId},
                                          {'$set': {
                                              # "spanAnnotation.text."+spanId: annotatedTextSpan[spanId]
                                              current_username+'.annotationGrid.'+key+'.'+k: v,
                                              current_username+".annotatedFLAG": 1,
                                              'annotationGrid.'+key+'.'+k: v,
                                              "annotatedFLAG": 1,
                                              "lastUpdatedBy": current_username
                                          }})
    except:
        logger.exception("")

    return "OK"


@lifedata.route('/deleteannotationspan', methods=['GET', 'POST'])
@login_required
def deleteannotationspan():
    try:
        # print('IN /deleteannotationSpan')
        userprojects, annotation = getdbcollections.getdbcollections(mongo,
                                                                     'userprojects',
                                                                     'annotation')

        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)

        if request.method == 'POST':
            # annotatedText = dict(request.form.lists())

            annotatedTextSpan = json.loads(request.form['a'])
            # pprint(annotatedTextSpan)

            # # lastActiveId = annotatedTextSpan['lastActiveId'][0]
            lastActiveId = annotatedTextSpan['lastActiveId']
            del annotatedTextSpan['lastActiveId']
            # # annotatedTextSpan['annotatedFLAG'] = 1
            # # pprint(annotatedTextSpan)
            # # print(lastActiveId)
            active_source_id = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                     current_username,
                                                                     activeprojectname)
            if ('activesourceId' in active_source_id):
                active_source_id = active_source_id['activesourceId']
            else:
                active_source_id = ''
            for key, value in annotatedTextSpan.items():
                for k, v in value.items():
                    annotation.update_one({"projectname": activeprojectname,
                                           "lifesourceid": active_source_id,
                                           "dataId": lastActiveId},
                                          {'$unset': {
                                              # "spanAnnotation.text."+spanId: annotatedTextSpan[spanId]
                                              current_username+'.annotationGrid.'+key+'.'+k: 1,
                                              'annotationGrid.'+key+'.'+k: 1,
                                              # current_username+".annotatedFLAG": 1
                                          }})
    except:
        logger.exception("")

    return "OK"


@lifedata.route('/downloadannotationfile', methods=['GET', 'POST'])
def downloadannotationfile():
    try:
        projects, userprojects, annotation, tagsets = getdbcollections.getdbcollections(mongo,
                                                                                        'projects',
                                                                                        'userprojects',
                                                                                        'annotation',
                                                                                        'tagsets')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                      userprojects)
        project_type = getprojecttype.getprojecttype(projects,
                                                     activeprojectname)
        project_details = projects.find_one({"projectname": activeprojectname},
                                            {"_id": 0, "tagsetId": 1})
        tag_set_id = project_details["tagsetId"]
        tag_set = tagsets.find_one({"_id": tag_set_id})
        tagset = tag_set['tagSet']
        df_dict = {"dataId": [], "ID": [], "Data": []}
        for category in list(tagset.keys()):
            df_dict[category] = []
        df_dict["Duplicate"] = []
        df_dict["annotatorComment"] = []
        df = pd.DataFrame.from_dict(df_dict)
        logger.debug("df.columns: %s", pformat(list(df.columns)))
        active_source_id = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                 current_username,
                                                                 activeprojectname)
        if ('activesourceId' in active_source_id):
            active_source_id = active_source_id['activesourceId']
        else:
            active_source_id = ''
        allIds = annotationdetails.get_annotation_ids_list(annotation,
                                                           activeprojectname,
                                                           active_source_id)

        for data_id in list(allIds):
            annotated_text = {}
            logger.debug("data_id: %s", data_id)
            data_info = annotation.find_one({
                "projectname": activeprojectname,
                "lifesourceid": active_source_id,
                "dataId": data_id
            },
                {
                "_id": 0,
                "dataId": 1,
                "Data": 1,
                "dataMetadata": 1,
                current_username: 1
            }
            )
            logger.debug("data_info: %s", pformat(data_info))

            annotated_text["dataId"] = data_id
            annotated_text["ID"] = data_info["dataMetadata"]["ID"]
            annotated_text["Data"] = data_info["Data"]
            if (data_info != None and current_username in data_info):
                current_user_annotated_text = data_info[current_username]['annotationGrid']
                for category in list(tagset.keys()):
                    logger.debug("category: %s", category)
                    if (category in current_user_annotated_text):
                        tag = current_user_annotated_text[category]
                        logger.debug("tag: %s", tag)
                        annotated_text[category] = tag
                    else:
                        annotated_text[category] = ''
                annotated_text_df = pd.DataFrame.from_dict(
                    annotated_text.items()).T
                annotated_text_df.columns = annotated_text_df.iloc[0]
                annotated_text_df = annotated_text_df[1:]
                # print(annotated_text_df, '\n')
                df = df.append(annotated_text_df, ignore_index=True)
            else:
                for category in list(tagset.keys()):
                    annotated_text[category] = ''
                annotated_text["Duplicate"] = ''
                annotated_text["annotatorComment"] = ''
                annotated_text_df = pd.DataFrame.from_dict(
                    annotated_text.items()).T
                annotated_text_df.columns = annotated_text_df.iloc[0]
                annotated_text_df = annotated_text_df[1:]
                df = df.append(annotated_text_df, ignore_index=True)
        logger.debug("df: %s", df.head())
        download_folder_path = os.path.join(basedir, 'download')
        if not (os.path.exists(download_folder_path)):
            os.mkdir(download_folder_path)
        logger.debug("download_folder_path: %s", download_folder_path)
        current_user_download_folder_path = os.path.join(
            download_folder_path, current_username)
        if not (os.path.exists(current_user_download_folder_path)):
            os.mkdir(current_user_download_folder_path)
        logger.debug("current_user_download_folder_path: %s",
                     current_user_download_folder_path)
        current_user_download_file_path = os.path.join(
            current_user_download_folder_path, activeprojectname+'_'+active_source_id+'.tsv')
        logger.debug("current_user_download_file_path: %s",
                     current_user_download_file_path)
        df.to_csv(current_user_download_file_path, sep='\t', index=False)

        files = glob.glob(current_user_download_folder_path+'/*')
        logger.debug("files: %s", pformat(files))
        zip_file_path = os.path.join(
            download_folder_path, current_username+'_'+activeprojectname+'.zip')
        with ZipFile(zip_file_path, 'w') as zip:
            # writing each file one by one
            for file in files:
                # zip.write(file, os.path.join(activeprojectname, os.path.basename(file)))
                zip.write(file, os.path.basename(file))
        print('All files zipped successfully!')

        # deleting all files from storage
        for f in files:
            # print(f)
            os.remove(f)
    except:
        logger.exception("")

    return send_file(zip_file_path, as_attachment=True)


@lifedata.route('/datasetexplorer', methods=['GET', 'POST'])
def datasetexplorer():
    projects, projectsform = getdbcollections.getdbcollections(
        mongo, 'projects', 'projectsform')
    # activeprojectname = getactiveprojectname.getactiveprojectname(
    #     current_username, userprojects)
    all_public_project_info = projectDetails.get_n_public_projects_info(projects,
                                                                        projectsform
                                                                        )

    return render_template(
        'datasetExplorer.html',
        allprojectinfo=all_public_project_info
    )


@lifedata.route('/maketranslation', methods=['GET', 'POST'])
@login_required
def maketranslation():
    projects, userprojects, transcriptions, lifeappconfigs, projectsform, languages = getdbcollections.getdbcollections(mongo,
                                                                                                                        'projects',
                                                                                                                        'userprojects',
                                                                                                                        'transcriptions',
                                                                                                                        'lifeappconfigs',
                                                                                                                        'projectsform',
                                                                                                                        'languages')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    audio_language = getactiveprojectform.getaudiolanguage(
        projectsform, projectowner, activeprojectname)
    audio_lang_code = languageManager.get_bcp_language_code(
        languages, audio_language)

    if request.method == 'POST':
        data = dict(request.form.lists())
        logger.debug("Form data %s", data)

        translation_source = data['translateUsingSelect2'][0]

        if translation_source == 'hfinference':
            if not 'hfinferenceagree' in data:
                # flash('')
                flash(
                    'We do not have sufficient permission to send the data to HF Inference Server.', category='error')
                return redirect(url_for('lifedata.transcription.home'))

        speakerId = data['translationSpeakerId'][0]
        # new_audio_file = request.files.to_dict()
        audio_filename = data['translationfile'][0]

        existing_audio_details = transcriptions.find_one(
            {'projectname': activeprojectname, 'audioFilename': audio_filename})
        # logger.debug("Existing audio data %s", existing_audio_details)

        if 'modelId' in data:
            model_name = data['modelId'][0]
        else:
            model_name = ''

        if 'sourceScriptName' in data:
            source_script_name = data['sourceScriptName'][0]
            source_script_code = sn.get(
                name=source_script_name).get("alpha_4", source_script_name)
        else:
            source_script_name = ''

        if 'targetLanguageName' in data:
            output_language_name = data['targetLanguageName'][0]
            lang_scripts = output_language_name.split('-')
            output_lang = lang_scripts[0]
            output_script = lang_scripts[1]
            output_lang_code = languageManager.get_bcp_language_code(
                languages, output_lang)
            # output_script_code = sn.get(
            #     name=output_script).get("alpha_4", output_script)
            if output_script == "Latin":
                output_script_code = "Latn"
            else:
                output_script_code = sn.get(
                    name=output_script).get("alpha_4", output_script)
        else:
            output_language_name = ''

        if 'overwrite-my-translations' in data:
            save_for_user = True
        else:
            save_for_user = False

        '''
        Translation Model

        translation_model = {
            'model_name': "name_1",
            'model_type': "local", (or "api")
            'model_params': {
                'model_path': "path_1",
                'model_api': 'api_endpoint'
            },
            'target': 'hin-Deva'
        }

        '''
        access_time = data['accessedOnTime'][0]

        if 'bhashini' in translation_source:
            hf_token = ''
            model_name = model_name.replace('bhashini_', '')
            model_type = 'bhashini'
        else:
            hf_token = modelManager.get_hf_tokens(
                lifeappconfigs, current_username)
            model_type = 'hfapi'

        translation_model = {
            'model_name': model_name,
            'model_type': model_type,
            'model_params': {
                'model_path': model_name,
                'model_api': translation_source,
                'output_language': output_language_name,
                'source_language': audio_lang_code,
                'source_script': source_script_name,
                'source_script_code': source_script_code,
                'target_language': output_lang_code,
                'target_script': output_script_code
            },
            'target': output_language_name
        }

        logger.debug('Translation model vals %s', translation_model)
        logger.debug('Access time %s', access_time)

        translation_utils.save_translation_of_one_audio_file(transcriptions,
                                                             activeprojectname,
                                                             current_username,
                                                             audio_filename,
                                                             translation_model,
                                                             transcription_type='sentence',
                                                             save_for_user=save_for_user,
                                                             hf_token=hf_token,
                                                             audio_details=existing_audio_details,
                                                             accessedOnTime=access_time
                                                             )

    return redirect(url_for('lifedata.transcription.home'))


@lifedata.route('/makegloss', methods=['GET', 'POST'])
@login_required
def makegloss():
    projects, userprojects, transcriptions, lifeappconfigs, projectsform, languages = getdbcollections.getdbcollections(mongo,
                                                                                                                        'projects',
                                                                                                                        'userprojects',
                                                                                                                        'transcriptions',
                                                                                                                        'lifeappconfigs',
                                                                                                                        'projectsform',
                                                                                                                        'languages')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                  userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    audio_language = getactiveprojectform.getaudiolanguage(
        projectsform, projectowner, activeprojectname)
    audio_lang_code = languageManager.get_bcp_language_code(
        languages, audio_language)

    if request.method == 'POST':
        data = dict(request.form.lists())
        logger.debug("Form data %s", data)

        translation_source = data['translateUsingSelect2'][0]

        if translation_source == 'hfinference':
            if not 'hfinferenceagree' in data:
                # flash('')
                flash(
                    'We do not have sufficient permission to send the data to HF Inference Server.', category='error')
                return redirect(url_for('lifedata.transcription.home'))

        speakerId = data['glossingSpeakerId'][0]
        # new_audio_file = request.files.to_dict()
        audio_filename = data['glossingfile'][0]

        existing_audio_details = transcriptions.find_one(
            {'projectname': activeprojectname, 'audioFilename': audio_filename})
        # logger.debug("Existing audio data %s", existing_audio_details)

        if 'glossModelId' in data:
            gloss_model_name = data['glossModelId'][0]
        else:
            gloss_model_name = ''

        if 'translationModelId' in data:
            translation_model_name = data['translationModelId'][0]
        else:
            translation_model_name = ''

        if 'sourceScriptName' in data:
            source_script_name = data['sourceScriptName'][0]
            source_script_code = sn.get(
                name=source_script_name).get("alpha_4", source_script_name)
        else:
            source_script_name = ''

        if 'targetLanguageName' in data:
            output_language_name = data['targetLanguageName'][0]
            lang_scripts = output_language_name.split('-')
            output_lang = lang_scripts[0]
            output_script = lang_scripts[1]
            output_lang_code = languageManager.get_bcp_language_code(
                languages, output_lang)
            # output_script_code = sn.get(
            #     name=output_script).get("alpha_4", output_script)
            if output_script == "Latin":
                output_script_code = "Latn"
            else:
                output_script_code = sn.get(
                    name=output_script).get("alpha_4", output_script)
        else:
            output_language_name = ''

        if 'overwrite-my-gloss' in data:
            save_for_user = True
        else:
            save_for_user = False

        if 'overwrite-my-freetranslation' in data:
            free_translation = True
        else:
            free_translation = False

        '''
        Translation Model

        translation_model = {
            'model_name': "name_1",
            'model_type': "local", (or "api")
            'model_params': {
                'model_path': "path_1",
                'model_api': 'api_endpoint'
            },
            'target': 'hin-Deva'
        }

        '''
        access_time = data['accessedOnTime'][0]

        if 'bhashini' in translation_source:
            hf_token = ''
            translation_model_name = translation_model_name.replace(
                'bhashini_', '')
            model_type = 'bhashini'
        else:
            hf_token = modelManager.get_hf_tokens(
                lifeappconfigs, current_username)
            model_type = 'hfapi'

        translation_model = {
            'model_name': translation_model_name,
            'model_type': model_type,
            'model_params': {
                'model_path': translation_model_name,
                'model_api': translation_source,
                'output_language': output_language_name,
                'source_language': audio_lang_code,
                'source_script': source_script_name,
                'source_script_code': source_script_code,
                'target_language': output_lang_code,
                'target_script': output_script_code
            },
            'target': output_language_name
        }

        gloss_model = {
            'model_name': gloss_model_name,
            'model_type': "local",
            'model_params': {
                'model_path': gloss_model_name,
                'source_language': audio_lang_code,
                'source_language_name': audio_language,
                'source_script': source_script_name,
                'source_script_code': source_script_code,
                'target_language': output_lang_code,
                'target_script': output_script_code
            },
            'target': output_language_name
        }

        logger.debug('Translation model vals %s', translation_model)
        logger.debug('Gloss model vals %s', gloss_model)
        logger.debug('Access time %s', access_time)

        gloss_utils.save_gloss_of_one_audio_file(transcriptions,
                                                 activeprojectname,
                                                 current_username,
                                                 audio_filename,
                                                 translation_model,
                                                 gloss_model,
                                                 transcription_type='sentence',
                                                 save_for_user=save_for_user,
                                                 hf_token=hf_token,
                                                 audio_details=existing_audio_details,
                                                 accessedOnTime=access_time,
                                                 get_free_translation=free_translation
                                                 )

    return redirect(url_for('lifedata.transcription.home'))
