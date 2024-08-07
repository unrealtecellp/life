"""Module to save the tagset as a project."""

from zipfile import ZipFile
import pandas as pd
import io
from app.controller import (
    life_logging,
    getcurrentusername,
    updateuserprojects
)
from flask import flash, redirect, url_for
import re

logger = life_logging.get_logger()


def save_tagset(tagsets, zip_file, use_in_project='', about_project='', is_public='', derived_from=[], derivatives=[], supported_languages=[], supported_tasks={}):
    current_username = getcurrentusername.getcurrentusername()
    try:
        with ZipFile(zip_file) as myzip:
            existing_tagset_projects = []
            tagset_project_ids = []
            for file_name in myzip.namelist():
                with myzip.open(file_name) as myfile:
                    try:
                        if file_name.endswith('.tsv'):
                            tagset_project_name = file_name.rsplit(
                                '.', 1)[0].replace('.', '_')
                            tags_df = pd.read_csv(io.BytesIO(
                                myfile.read()), sep='\t', dtype=str)
                        elif file_name.endswith('.csv'):
                            tagset_project_name = file_name.rsplit(
                                '.', 1)[0].replace('.', '_')
                            tags_df = pd.read_csv(io.BytesIO(
                                myfile.read()), sep='\t', dtype=str)
                        elif file_name.endswith('.xlsx'):
                            tagset_project_name = file_name.rsplit(
                                '.', 1)[0].replace('.', '_')
                            tags_df = pd.read_excel(
                                io.BytesIO(myfile.read()), dtype=str)
                        else:
                            flash(
                                f"Please upload valid tagset file format(.tsv, .csv. .xlsx).")
                    except:
                        logger.exception("")
                        flash(
                            f"File: {file_name} is not in correct format. Please check")
                        return redirect(url_for('lifedata.home'))

                    # check if tagset already exist
                    if tagsets.find_one({"projectname": tagset_project_name},
                                        {'_id': 0, "projectname": 1}) != None:
                        existing_tagset_projects.append(tagset_project_name)
                        continue
                tag_set = {}
                tag_set_meta_data = {}
                categoryDependency = {}
                defaultCategoryTags = {}
                categoryHtmlElement = {}
                categoryHtmlElementProperties = {}
                if (len(tags_df.columns) >= 2):
                    for i in range(len(tags_df)):
                        # reading column 'Category', and 'Tags'
                        # logger.debug("tags_df.iloc[i, 0]: %s", tags_df.iloc[i, 0])
                        # logger.debug("tags_df.iloc[i, 1]: %s", tags_df.iloc[i, 1])
                        # logger.debug(", type(tags_df.iloc[i, 1]: %s", type(tags_df.iloc[i, 1]))
                        if (str(tags_df.iloc[i, 1]) == 'nan'):
                            tag_set[tags_df.iloc[i, 0]] = ['']
                        else:
                            tag_set[tags_df.iloc[i, 0]] = re.sub(
                                ' ', '', tags_df.iloc[i, 1]).split(',')
                        if (len(tags_df.columns) >= 3):
                            # reading column 'Default'
                            # logger.debug("tags_df.iloc[i, 2]: %s", tags_df.iloc[i, 2])
                            if (str(tags_df.iloc[i, 2]) == 'nan'):
                                defaultCategoryTags[tags_df.iloc[i, 0]] = ''
                            elif (len(tags_df.columns) >= 4 and str(tags_df.iloc[i, 4]) == 'select'):
                                defaultCategoryTags[tags_df.iloc[i, 0]] = [
                                    re.sub(' ', '', tags_df.iloc[i, 2]).split(',')[0]]
                            else:
                                defaultCategoryTags[tags_df.iloc[i, 0]] = re.sub(
                                    ' ', '', tags_df.iloc[i, 2]).split(',')[0]
                        if (len(tags_df.columns) >= 4):
                            # logger.debug("tags_df.iloc[i, 3]: %s", tags_df.iloc[i, 3])
                            if (re.sub(' ', '', tags_df.iloc[i, 3]).split(',')[0] != 'NONE'):
                                categoryDependency[tags_df.iloc[i, 0]] = re.sub(
                                    ' ', '', tags_df.iloc[i, 3]).split(',')[0]
                        if (len(tags_df.columns) >= 6):
                            # logger.debug("tags_df.iloc[i, 4]: %s", tags_df.iloc[i, 4])
                            # logger.debug("tags_df.iloc[i, 5]: %s", tags_df.iloc[i, 5])
                            categoryHtmlElement[tags_df.iloc[i, 0]] = re.sub(
                                ' ', '', tags_df.iloc[i, 4]).split(',')[0]
                            categoryHtmlElementProperties[tags_df.iloc[i, 0]] = re.sub(
                                ' ', '', tags_df.iloc[i, 5]).split(',')[0]
                    tag_set_meta_data['categoryDependency'] = categoryDependency
                    tag_set_meta_data['defaultCategoryTags'] = defaultCategoryTags
                    tag_set_meta_data['categoryHtmlElement'] = categoryHtmlElement
                    tag_set_meta_data['categoryHtmlElementProperties'] = categoryHtmlElementProperties
                project_owner = current_username
                tagset_project_details = {}
                tagset_project_details["projectType"] = "tagset"
                tagset_project_details["projectname"] = tagset_project_name
                tagset_project_details["projectOwner"] = project_owner
                tagset_project_details["tagSet"] = tag_set
                tagset_project_details["tagSetMetaData"] = tag_set_meta_data
                tagset_project_details["sharedwith"] = [project_owner]
                tagset_project_details["projectdeleteFLAG"] = 0
                tagset_project_details["isPublic"] = is_public
                tagset_project_details["derivedFromProject"] = derived_from
                tagset_project_details["projectDerivatives"] = derivatives
                tagset_project_details["aboutproject"] = about_project
                tagset_project_details["useInProjects"] = [use_in_project]
                tagset_project_details["supportedLanguages"] = supported_languages
                tagset_project_details["supportedTasks"] = supported_tasks
                tagset_project_details["updatedBy"] = project_owner

                tagset_project_id = tagsets.insert_one(tagset_project_details)
                # logger.debug('tagset_project_id: %s', tagset_project_id)
                logger.debug("insertedId: %s\nType: %s",
                             tagset_project_id.inserted_id,
                             type(tagset_project_id.inserted_id))
                tagset_project_ids.append(tagset_project_id.inserted_id)
                # projectname = tagset_project_details['projectname']
                # updateuserprojects.updateuserprojects(userprojects,
                #                                 projectname,
                #                                 current_username
                #                                 )
            if (len(existing_tagset_projects) > 0):
                flash(
                    f'File Name : {", ".join(existing_tagset_projects)} already exist!', 'warning')
                # return redirect(url_for('lifedata.home'))
    except:
        logger.exception("")
        flash('Please upload a zip file. Check the file format at the link provided for the Sample File')
        return redirect(url_for('lifedata.home'))

    logger.debug('tagset_project_ids from save_tagset: %s', tagset_project_ids)
    return tagset_project_ids


def update_use_in_project(tagset_collection, tagset_name, use_in_project):
    tagset_collection.update_one(
        {'projectname': tagset_name, 'projectDeleteFLAG': 0, 'projectType': 'tagset'},
        {'$addToSet': {'useInProjects': use_in_project}})
