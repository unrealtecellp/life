"""Module to save the tagset as a project."""

from zipfile import ZipFile
import pandas as pd
import io
from app.controller import(
    life_logging,
    getcurrentusername,
    updateuserprojects
)
from flask import flash, redirect, url_for
import re

logger = life_logging.get_logger()

def save_tagset(tagsets, zip_file):
    current_username = getcurrentusername.getcurrentusername()
    tag_set = {}
    tag_set_meta_data = {}
    categoryDependency = {}
    defaultCategoryTags = {}
    categoryHtmlElement = {}
    categoryHtmlElementProperties = {}
    try:
        with ZipFile(zip_file) as myzip:
            existing_tagset_projects = []
            tagset_project_ids = []
            for file_name in myzip.namelist():
                with myzip.open(file_name) as myfile:
                    try:
                        if file_name.endswith('.tsv'):
                            tagset_project_name = file_name.rsplit('.', 1)[0].replace('.', '_')
                            tags_df = pd.read_csv(io.BytesIO(myfile.read()), sep='\t', dtype=str)
                        elif file_name.endswith('.csv'):
                            tagset_project_name = file_name.rsplit('.', 1)[0].replace('.', '_')
                            tags_df = pd.read_csv(io.BytesIO(myfile.read()), sep='\t', dtype=str)
                        elif file_name.endswith('.xlsx'):
                            tagset_project_name = file_name.rsplit('.', 1)[0].replace('.', '_')
                            tags_df = pd.read_excel(io.BytesIO(myfile.read()), dtype=str)
                        else:
                            flash(f"Please upload valid tagset file format(.tsv, .csv. .xlsx).")
                    except:
                        logger.exception("")
                        flash(f"File: {file_name} is not in correct format. Please check")
                        return redirect(url_for('lifedata.home'))

                    # check if tagset already exist
                    if tagsets.find_one({"projectname": tagset_project_name},
                                        {'_id' : 0, "projectname": 1}) != None:
                        existing_tagset_projects.append(tagset_project_name)
                    
                if (len(tags_df.columns) >= 2):
                    for i in range(len(tags_df)):
                        # reading column 'Category', and 'Tags'
                        logger.debug("tags_df.iloc[i, 0]: %s", tags_df.iloc[i, 0])
                        logger.debug("tags_df.iloc[i, 1]: %s", tags_df.iloc[i, 1])
                        logger.debug(", type(tags_df.iloc[i, 1]: %s", type(tags_df.iloc[i, 1]))
                        if (str(tags_df.iloc[i, 1]) == 'nan'):
                            tag_set[tags_df.iloc[i, 0]] = ['']
                        else:
                            tag_set[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 1]).split(',')
                        if (len(tags_df.columns) == 3):
                            # reading column 'Default'
                            if (str(tags_df.iloc[i, 2]) == 'nan'):
                                defaultCategoryTags[tags_df.iloc[i, 0]] = ''
                            elif (len(tags_df.columns) == 4 and str(tags_df.iloc[i, 4]) == 'select'):
                                defaultCategoryTags[tags_df.iloc[i, 0]] = [re.sub(' ', '', tags_df.iloc[i, 2]).split(',')[0]]
                            else:
                                defaultCategoryTags[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 2]).split(',')[0]
                        if (len(tags_df.columns) == 4):
                            if (re.sub(' ', '', tags_df.iloc[i, 3]).split(',')[0] != 'NONE'):
                                categoryDependency[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 3]).split(',')[0]
                        if (len(tags_df.columns) == 6):
                            categoryHtmlElement[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 4]).split(',')[0]
                            categoryHtmlElementProperties[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 5]).split(',')[0]
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
                tagset_project_details["sharedwith"]  = [project_owner]
                tagset_project_details["projectdeleteFLAG"] = 0
                tagset_project_details["isPublic"] = 0
                tagset_project_details["derivedFromProject"] = []
                tagset_project_details["projectDerivatives"] = []
                tagset_project_details["aboutproject"] = ''

                tagset_project_id = tagsets.insert_one(tagset_project_details)
                tagset_project_ids.append(tagset_project_id)
                # projectname = tagset_project_details['projectname']
                # updateuserprojects.updateuserprojects(userprojects,
                #                                 projectname,
                #                                 current_username
                #                                 )
            if (len(existing_tagset_projects) > 0):
                flash(f'File Name : {", ".join(existing_tagset_projects)} already exist!', 'warning')
                return redirect(url_for('lifedata.home'))


    except:
        logger.exception("")
        flash('Please upload a zip file. Check the file format at the link provided for the Sample File')
        return redirect(url_for('lifedata.home'))

    return tuple(tagset_project_ids)
