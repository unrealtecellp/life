from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    send_file,
    Blueprint
)
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash
from app import app, mongo
from app.forms import UserLoginForm, RegistrationForm
from app.models import UserLogin
from flask_login import current_user, login_user, logout_user, login_required
from zipfile import ZipFile
import pandas as pd
import io
import gridfs
from bson.objectid import ObjectId
from flask import Response, stream_with_context
import base64
import re
from datetime import datetime
from pprint import pprint
from jsondiff import diff
from pytesseract import image_to_string, image_to_osd
from PIL import Image
import os
import glob
import random
from math import ceil
import json

from app.controller import (
    getactiveprojectname,
    getcurrentusername,
    getcurrentuserprojects,
    getdbcollections,
    getprojectsnamebytype,
    getprojecttype,
    readJSONFile,
    savenewproject,
    updateuserprojects
)

easyAnno = Blueprint('easyAnno', __name__, template_folder='templates', static_folder='static')
basedir = os.path.abspath(os.path.dirname(__file__))
project_type_list = ['text', 'image']
# home page route
@easyAnno.route('/', methods=['GET', 'POST'])
@easyAnno.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    # projects = mongo.db.projects              # collection of users and their respective projects
    # userprojects = mongo.db.userprojects              # collection of users and their respective projects

    # currentuserprojectsname =  sorted(list(currentuserprojects()))
    # activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
    #                 {'_id' : 0, 'activeprojectname': 1})['activeprojectname']
    # print(currentuserprojectsname, activeprojectname)
    projects, userprojects, = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
    project_type_list = ['text', 'image']
    currentuserprojectsname = getprojectsnamebytype.getprojectsnamebytype(projects,
                                                                            currentuserprojectsname,
                                                                            project_type_list)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)
    projectcompleted = project_comments_stats(currentuserprojectsname)
    # projectcompleted = {'danger': 14, 'warning': 6, 'success': 1}

    active_project_type = getprojecttype.getprojecttype(projects, activeprojectname)
    if (active_project_type not in project_type_list):
        activeprojectname = ''

    if request.method == 'POST':

        zipFile = request.files['zipFile']
        file_type = request.form['fileType']
        annotated_text = request.form.get('annotatedTextZip')
        image_file_name = request.form.get('imageFileName')
        

        # print(file_type, annotated_text, image_file_name)

        if (file_type == 'text'):
            if (annotated_text == 'on'):
                createAnnotatedTextAnno(zipFile)
            else:    
                # createTextAnno(zipFile)
                createTextAnnoNew(zipFile)
        elif (file_type == 'image'):
            createImageAnno(zipFile, image_file_name)    

    # print(len(currentuserprojectsname))
    return render_template('easyannohome.html',
                            data=currentuserprojectsname,
                            activeproject=activeprojectname,
                            projectcompleted=projectcompleted
                        )

def checkEmptyRowInID(text_data_df, project_name):
    if(text_data_df["ID"].isnull().any()):
        flash(f'File Name : {project_name}  have empty cell in "ID" column', 'warning')
        return redirect(url_for('easyAnno.home'))

def userAlreadyAnnotated(project_name):
    textanno = mongo.db.textanno
    # check if file already exist then current user hasnt yet annotated atleast one text/comment
    for ann_text in textanno.find({"projectname": project_name},{'_id' : 0, current_user.username: 1}):
        if current_user.username in ann_text.keys():
            flash(f'File Name : {project_name} already exist! and some data already annotated by you', 'warning')
            return redirect(url_for('easyAnno.home'))

def compareTagSet(project_name, tag_set):
    projects = mongo.db.projects              # collection of users and their respective projects
    # check if tagset given by user and one saved with the project details match or not
    # when tagset file(tsv file already read from the zip file)
    existing_tag_set = projects.find_one({"projectname": project_name}, {'_id' : 0, "tagSet": 1})["tagSet"]
    
    tag_set_differ = diff(tag_set, existing_tag_set)
    # if difference in both tagset
    if bool(tag_set_differ):
        flash(f'Missing some tags in categories: {list(tag_set_differ.keys())} in tagset file textAnno_tags.tsv', 'warning')
        return redirect(url_for('easyAnno.home'))

def compareTagSetandFileColumn(text_data_df, tag_set, project_name):
    # check categories in the columns of the file and the tagset tsv file match or not
    uploaded_file_columns = list(text_data_df.columns)
    # print(uploaded_file_columns)
    uploaded_tagset_category  = list(tag_set.keys()) + ["ID", "Text"]
    # print(uploaded_tagset_category)
    if (len(uploaded_tagset_category) >= len(uploaded_file_columns)):
        tags_category_mismatch = list(set(uploaded_tagset_category) - set(uploaded_file_columns))
        if (len(tags_category_mismatch) != 0):
            flash(f'Missing categories: {tags_category_mismatch} in your data file: {project_name}.csv', 'warning')
            return redirect(url_for('easyAnno.home'))
    else:
        tags_category_mismatch = list(set(uploaded_file_columns) - set(uploaded_tagset_category))
        if (len(tags_category_mismatch) != 0):
            flash(f'Missing categories: {tags_category_mismatch} in your tagset file: textAnno_tags.tsv', 'warning')
            return redirect(url_for('easyAnno.home'))

def checkTextIds(project_name, text_data_df):
    projects = mongo.db.projects              # collection of users and their respective projects
    # check the IDs in the uploaded file and the existing file match or not
    textData = projects.find_one({"projectname": project_name}, {'_id' : 0, "textData": 1})["textData"]
    existing_text_ids = []
    # print(temp_text_IDs)
    for existing_text_id in textData.values():
        existing_text_ids.append(existing_text_id["ID"])
    # print(type(existing_text_ids))
    # print(existing_text_ids)

    # text_data_df = pd.read_csv(io.BytesIO(myfile.read()), sep='\t', dtype=str)
    uploaded_text_ids = text_data_df["ID"].dropna().tolist()
    # print(type(uploaded_text_ids))
    # print(uploaded_text_ids)
    if (len(existing_text_ids) >= len(uploaded_text_ids)):
        text_ids_mismatch = list(set(existing_text_ids) - set(uploaded_text_ids))
        if (len(text_ids_mismatch)) != 0:
            flash(f'Missing IDs: {text_ids_mismatch} in your data file: {project_name}.csv', 'warning')
            return redirect(url_for('easyAnno.home'))
    else:
        text_ids_mismatch = list(set(uploaded_text_ids) - set(existing_text_ids))
        if (len(text_ids_mismatch)) != 0:
            flash(f'Extra IDs: {text_ids_mismatch} in your data file: {project_name} compared to one already created', 'warning')
            return redirect(url_for('easyAnno.home'))    
    # print(text_ids_mismatch)

def saveNewProjectDetails(project_name, tag_set, text_data, tag_set_meta_data):
    projects = mongo.db.projects              # collection of users and their respective projects
    userprojects = mongo.db.userprojects              # collection of users and their respective projects

    project_owner = current_user.username
    project_details = {}
    lastActiveId = {current_user.username: list(text_data.keys())[0]}
    project_details["projectType"] = "text"
    project_details["projectname"] = project_name
    project_details["projectOwner"] = project_owner
    project_details["tagSet"] = tag_set
    project_details["tagSetMetaData"] = tag_set_meta_data
    project_details["textData"] = text_data
    project_details["lastActiveId"] = lastActiveId
    project_details["sharedwith"]  = [project_owner]
    project_details["projectdeleteFLAG"] = 0
    project_details["isPublic"] = 0
    project_details["derivedFromProject"] = []
    project_details["projectDerivatives"] = []
    project_details["aboutproject"] = ''

    # pprint(project_details)
    # get curent user project list and update
    userprojectnamelist = userprojects.find_one({'username' : current_user.username})["myproject"]
    # print(f'{"#"*80}\n{userprojectnamelist}')
    userprojectnamelist.append(project_name)
    # print(f'{"#"*80}\n{userprojectnamelist}')
    userprojects.update_one({ 'username' : current_user.username }, \
        { '$set' : { 'myproject' : userprojectnamelist, 'activeprojectname' :  project_name}})
    
    projects.insert_one(project_details)

    return project_details

def updateProjectDetails(project_name, project_shared_with):
    projects = mongo.db.projects              # collection of users and their respective projects
    userprojects = mongo.db.userprojects              # collection of users and their respective projects

    proj_detail_update = projects.find_one({ "projectname": project_name }, \
                        { "sharedwith": 1 , "lastActiveId": 1, "textData": 1})
    shared_with = proj_detail_update["sharedwith"]
    shared_with.append(project_shared_with)
    lastActiveId = proj_detail_update["lastActiveId"]
    lastActiveId[current_user.username] = list(proj_detail_update["textData"].keys())[0]
    
    # print(shared_with, lastActiveId)
    projects.update_one({ "projectname": project_name }, \
        { '$set' : { 'sharedwith' : list(set(shared_with)), "lastActiveId": lastActiveId}})
    # get curent user project list and update
    userprojectnamelist = userprojects.find_one({'username' : current_user.username})["myproject"]
    # print(f'{"#"*80}\n{userprojectnamelist}')
    userprojectnamelist.append(project_name)
    # print(userprojectnamelist)
    userprojects.update_one({ 'username' : current_user.username }, \
        { '$set' : { 'myproject' : list(set(userprojectnamelist)), 'activeprojectname' :  project_name}})

    # # print(project_details)   


def saveAnnotatedData(project_name, text_data_df):
    # print("Creatinggggggggggggg Newwwwwwwwwwwwwwwwwwwwwwww")
    textanno = mongo.db.textanno

    id_test_list = []
    text_data = {}

    col_names = dict(enumerate(text_data_df.columns))
    col_names = dict((v,k) for k,v in col_names.items())
    # print(col_names)
    col_names.pop("ID")
    col_names.pop("Text")
    for i in range(len(text_data_df)):
        NaN_count = 0
        text_id = 'T'+re.sub(r'[-: \.]', '', str(datetime.now()))
        id_test_list.append(text_id)
        single_row = {}
        single_row["ID"] = text_data_df.iloc[i, 0]
        single_row["Text"] = text_data_df.iloc[i, 1]
        text_data[text_id] = single_row
        # entry of each text in textanno colloection
        text_anno_detail = {}
        text_anno_detail["projectname"] = project_name
        text_anno_detail["textId"] = text_id
        text_anno_detail["ID"] = text_data_df.iloc[i, 0]
        text_anno_detail["Text"] = text_data_df.iloc[i, 1]
        if (len(col_names) != 0):
            user_annotation = {}
            for category, index in col_names.items():
                if pd.isna(text_data_df.iloc[i, index]):
                    NaN_count += 1
                    # print(text_data_df.iloc[i, index])
                    user_annotation[category] = ''
                else:    
                    user_annotation[category] = text_data_df.iloc[i, index]

            # version 1        
            # if (len(col_names.keys()) == NaN_count):
            #     user_annotation["annotatedFLAG"] = 0
            # else:    
            #     user_annotation["annotatedFLAG"] = 1

            # version 2
            if (NaN_count > 2):
                user_annotation["annotatedFLAG"] = 0
            else:    
                user_annotation["annotatedFLAG"] = 1

            user_annotation['Duplicate'] = "No"
            user_annotation['annotatorComment'] = ""
            # print(user_annotation)
            text_anno_detail[current_user.username] = user_annotation
        text_anno_detail['lastUpdatedBy'] = current_user.username
        all_access = {}
        text_anno_detail['allAccess'] = all_access
        all_updates = {}
        text_anno_detail['allUpdates'] = all_updates

        textanno.insert_one(text_anno_detail)
    # print(text_data)
    # print(text_anno_detail)
    # textanno.insert_one(text_anno_detail)

    return text_data

def updateAnnotatedData(project_name, text_data_df):
    # print("Updatinggggggggggggggggggggggggggggggggggggggg")
    projects = mongo.db.projects              # collection of users and their respective projects
    textanno = mongo.db.textanno

    proj_detail = projects.find_one({"projectname": project_name}, {"_id": 0, "textData": 1})
    textData = proj_detail["textData"]
    # map IDs in file(which is uploaded) to its respective textId
    ID_to_textId = {}
    for textId, value in textData.items():
        ID = list(value.values())[0]
        ID_to_textId[ID] = textId
    # print(ID_to_textId)    

    col_names = dict(enumerate(text_data_df.columns))
    col_names = dict((v,k) for k,v in col_names.items())
    # print(col_names)
    col_names.pop("ID")
    col_names.pop("Text")
    for i in range(len(text_data_df)):
        NaN_count = 0
        # entry of each text in textanno collection
        # uploaded_text_ID
        ID = text_data_df.iloc[i, 0]
        text_anno_detail = {}
        user_annotation = {}
        if (len(col_names) != 0):
            
            for category, index in col_names.items():
                if pd.isna(text_data_df.iloc[i, index]):
                    NaN_count += 1
                    # print(text_data_df.iloc[i, index])
                    user_annotation[category] = ''
                else:    
                    user_annotation[category] = text_data_df.iloc[i, index]

            # version 1        
            # if (len(col_names.keys()) == NaN_count):
            #     user_annotation["annotatedFLAG"] = 0
            # else:    
            #     user_annotation["annotatedFLAG"] = 1

            # version 2
            if (NaN_count > 2):
                user_annotation["annotatedFLAG"] = 0
            else:    
                user_annotation["annotatedFLAG"] = 1

            user_annotation['Duplicate'] = "No"
            user_annotation['annotatorComment'] = ""
            # text_anno_detail[current_user.username] = user_annotation
        # pprint(user_annotation)    
        lastUpdatedBy = current_user.username

        textanno.update_one({"projectname": project_name, "textId": ID_to_textId[ID], "ID": ID},\
                        { '$set' :{  current_user.username: user_annotation, "lastUpdatedBy": lastUpdatedBy }})
    # print(text_data)
    # pprint(text_anno_detail)
    # pprint(user_annotation)
    # textanno.insert_one(text_anno_detail)

def createAnnotatedTextAnno(zipFile):
    projects = mongo.db.projects              # collection of users and their respective projects

    tag_set = {}
    # text_data = {}
    text_data_df = ''
    # id_test_list = []
    project_name = ''
    tag_set_meta_data = {}
    categoryDependency = {}
    defaultCategoryTags = {}
    try:
        with ZipFile(zipFile) as myzip:
            with myzip.open('textAnno_tags.tsv') as myfile:
                # print('textAnno_tags.tsv')
                tags_df = pd.read_csv(io.BytesIO(myfile.read()), sep='\t', dtype=str).dropna()

                # version 1
                # # print(type(tags))
                # # print(tags_df)
                # for i in range(len(tags_df)):
                #     tag_set[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 1]).split(',')

                # version 2
                if (len(tags_df.columns) == 2):
                    for i in range(len(tags_df)):
                        tag_set[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 1]).split(',')
                elif (len(tags_df.columns) == 4):
                    for i in range(len(tags_df)):
                        tag_set[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 1]).split(',')
                        if (re.sub(' ', '', tags_df.iloc[i, 2]).split(',')[0] != 'NONE'):
                            categoryDependency[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 2]).split(',')[0]
                        defaultCategoryTags[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 3]).split(',')[0]
                    tag_set_meta_data['categoryDependency'] = categoryDependency
                    tag_set_meta_data['defaultCategoryTags'] = defaultCategoryTags

            for file_name in myzip.namelist():
                with myzip.open(file_name) as myfile:
                    # print(myfile.read())
                    if (not file_name.endswith('.tsv')):
                        # print(file_name)
                        project_name = file_name.split('.')[0]

                        # check project/file name do not already exist
                        if projects.find_one({"projectname": project_name}, {'_id' : 0, "projectname": 1}) != None:
                            # check if file already exist then current user hasnt yet annotated any text/comment
                            if userAlreadyAnnotated(project_name):
                                return redirect(url_for('easyAnno.home'))

                            # check if tag_set is empty
                            if bool(tag_set):
                                # check if tagset given by user and one saved with the project details match or not
                                if compareTagSet(project_name, tag_set):
                                    return redirect(url_for('easyAnno.home'))

                            text_data_df = pd.read_csv(io.BytesIO(myfile.read()), sep='\t', dtype=str)

                            # check if any row in ID column is empty
                            if checkEmptyRowInID(text_data_df, project_name):
                                return redirect(url_for('easyAnno.home'))

                            # check categories in the columns of the file and the tagset tsv file match or not
                            if compareTagSetandFileColumn(text_data_df, tag_set, project_name):
                                return redirect(url_for('easyAnno.home'))

                            # check the IDs in the uploaded file and the existing file match or not
                            if checkTextIds(project_name, text_data_df):
                                return redirect(url_for('easyAnno.home'))
                            
                            
                            # when project/filename exist and all checks are passed
                            updateAnnotatedData(project_name, text_data_df)
                            updateProjectDetails(project_name, current_user.username)

                        else:
                            # when project/file name do not exist in the database
                            text_data_df = pd.read_csv(io.BytesIO(myfile.read()), sep='\t', dtype=str)
                            # print(text_data_df.head())
                            # check if any row in ID column is empty
                            if checkEmptyRowInID(text_data_df, project_name):
                                return redirect(url_for('easyAnno.home'))
                            if compareTagSetandFileColumn(text_data_df, tag_set, project_name):
                                return redirect(url_for('easyAnno.home'))
                            text_data = saveAnnotatedData(project_name, text_data_df)
                            saveNewProjectDetails(project_name, tag_set, text_data, tag_set_meta_data)
        
    except:
        # flash('Please check the imageAnno_tags.tsv file format!')
        flash('Please upload a zip file. Check the file format at the link provided for the Sample File', 'warning')

        return redirect(url_for('easyAnno.home'))

    flash('File created successfully :)', 'success')

    return redirect(url_for('easyAnno.home'))

def createTextAnno(zipFile):
    # projects = mongo.db.projects              # collection of users and their respective projects
    # userprojects = mongo.db.userprojects              # collection of users and their respective projects
    # textanno = mongo.db.textanno
    
    # currentuserprojectsname =  sorted(list(currentuserprojects()))
    # activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
    #                 {'_id' : 0, 'activeprojectname': 1})['activeprojectname']

    projects, userprojects, textanno = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'userprojects',
                                                                'textanno')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
    project_type_list = ['text', 'image']
    currentuserprojectsname = getprojectsnamebytype.getprojectsnamebytype(projects,
                                                                            currentuserprojectsname,
                                                                            project_type_list)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)

    # print(type(zipFile))
    # print(zipFile)
    tag_set = {}
    tag_set_meta_data = {}
    categoryDependency = {}
    defaultCategoryTags = {}
    try:
        with ZipFile(zipFile) as myzip:
            with myzip.open('textAnno_tags.tsv') as myfile:
                
                # print('textAnno_tags.tsv')
                tags_df = pd.read_csv(io.BytesIO(myfile.read()), sep='\t', dtype=str).dropna()

                # version 1
                # # print(type(tags))
                # # print(tags_df)
                # for i in range(len(tags_df)):
                #     tag_set[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 1]).split(',')

                # version 2
                if (len(tags_df.columns) == 2):
                    for i in range(len(tags_df)):
                        tag_set[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 1]).split(',')
                elif (len(tags_df.columns) == 4):
                    for i in range(len(tags_df)):
                        tag_set[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 1]).split(',')
                        if (re.sub(' ', '', tags_df.iloc[i, 2]).split(',')[0] != 'NONE'):
                            categoryDependency[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 2]).split(',')[0]
                        defaultCategoryTags[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 3]).split(',')[0]
                    tag_set_meta_data['categoryDependency'] = categoryDependency
                    tag_set_meta_data['defaultCategoryTags'] = defaultCategoryTags
                    # tag_set_meta_data['categoryFormType'] = defaultCategoryTags

            existing_projects = []
            for file_name in myzip.namelist():
                project_name = file_name.split('.')[0]
                if projects.find_one({"projectname": project_name}, {'_id' : 0, "projectname": 1}) != None:
                    existing_projects.append(project_name)
            if (len(existing_projects) > 0):
                flash(f'File Name : {", ".join(existing_projects)} already exist!', 'warning')
                return redirect(url_for('easyAnno.home'))

            for file_name in myzip.namelist():    
                # print(tag_set)
                text_data = {}
                text_data_df = ''
                id_test_list = []
                with myzip.open(file_name) as myfile:
                    # print(myfile.read())
                    if (not file_name.endswith('.tsv')):
                        # print(file_name)
                        project_name = file_name.split('.')[0]

                        if projects.find_one({"projectname": project_name}, {'_id' : 0, "projectname": 1}) != None:
                            # print(projects.find_one({"projectname": project_name}, {'_id' : 0, "projectname": 1}))
                            # for ann_text in textanno.find({"projectname": project_name},{'_id' : 0, current_user.username: 1}):
                            #     print(current_user.username in ann_text.keys())
                            flash(f'File Name : {project_name} already exist!', 'warning')
                            return redirect(url_for('easyAnno.home'))

                        text_data_df = pd.read_csv(io.BytesIO(myfile.read()), sep='\t', dtype=str)
                        df_header = list(text_data_df.columns)
                        if ('ID' not in df_header):
                            # print(df_header)
                            flash(f'File Name : {project_name} do not have "ID" as column header', 'warning')
                            return redirect(url_for('easyAnno.home'))
                        if ('Text' not in df_header):
                            # print(df_header)
                            flash(f'File Name : {project_name} do not have "Text" as column header', 'warning')
                            return redirect(url_for('easyAnno.home'))    

                        if(text_data_df["ID"].isnull().any()):
                            flash(f'File Name : {project_name}  have empty cell in "ID" column', 'warning')
                            return redirect(url_for('easyAnno.home'))

                        # print(text_data_df.head())
                        for i in range(len(text_data_df)): 
                            text_id = 'T'+re.sub(r'[-: \.]', '', str(datetime.now()))
                            id_test_list.append(text_id)
                            single_row = {}
                            single_row["ID"] = text_data_df.iloc[i, 0]
                            single_row["Text"] = text_data_df.iloc[i, 1]
                            text_data[text_id] = single_row
                            # entry of each text in textanno colloection
                            text_anno_detail = {}
                            text_anno_detail["projectname"] = project_name
                            text_anno_detail["textId"] = text_id
                            text_anno_detail["ID"] = text_data_df.iloc[i, 0]
                            text_anno_detail["Text"] = text_data_df.iloc[i, 1]
                            text_anno_detail['lastUpdatedBy'] = ""
                            all_access = {}
                            text_anno_detail['allAccess'] = all_access
                            all_updates = {}
                            text_anno_detail['allUpdates'] = all_updates

                            textanno.insert_one(text_anno_detail)
                        
                    else:
                        continue    
                    # else:
                    #     tags_df = pd.read_csv(io.BytesIO(myfile.read()), sep='\t', dtype=str)
                    #     # print(type(tags))
                    #     # print(tags_df)
                    #     for i in range(len(tags_df)):
                    #         tag_set[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 1]).split(',')


                project_owner = current_user.username
                project_details = {}
                # print(text_data.keys())
                lastActiveId = {current_user.username: list(text_data.keys())[0]}
                project_details["projectType"] = "text"
                project_details["projectname"] = project_name
                project_details["projectOwner"] = project_owner
                project_details["tagSet"] = tag_set
                project_details["tagSetMetaData"] = tag_set_meta_data
                project_details["textData"] = text_data
                project_details["lastActiveId"] = lastActiveId
                project_details["sharedwith"]  = [project_owner]
                project_details["projectdeleteFLAG"] = 0
                project_details["isPublic"] = 0
                project_details["derivedFromProject"] = []
                project_details["projectDerivatives"] = []
                project_details["aboutproject"] = ''

                projects.insert_one(project_details)
                # get curent user project list and update
                # userprojectnamelist = userprojects.find_one({'username' : current_user.username})["myproject"]
                # # print(f'{"#"*80}\n{userprojectnamelist}')
                # userprojectnamelist.append(project_details['projectname'])
                # userprojects.update_one({ 'username' : current_user.username }, \
                #     { '$set' : { 'myproject' : userprojectnamelist, 'activeprojectname' :  project_details['projectname']}})
                projectname = project_details['projectname']
                updateuserprojects.updateuserprojects(userprojects,
                                                projectname,
                                                current_username
                                                )

                # print(project_details)   
    except:
        flash('Please upload a zip file. Check the file format at the link provided for the Sample File', 'warning')

        return redirect(url_for('easyAnno.home'))

    flash('File created successfully :)', 'success')

    # return render_template('home.html',  data=currentuserprojectsname, activeproject=activeprojectname)
    return redirect(url_for('easyAnno.home'))

def createImageAnno(zipFile, proj_name):
    projects = mongo.db.projects              # collection of users and their respective projects
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    imageanno = mongo.db.imageanno

    currentuserprojectsname =  sorted(list(currentuserprojects()))
    activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
                    {'_id' : 0, 'activeprojectname': 1})['activeprojectname']

    tag_set = {}
    image_files = {}
    try:
        with ZipFile(zipFile) as myzip:
            for file_name in myzip.namelist():
                with myzip.open(file_name) as myfile:
                    # print(myfile.read())
                    if (not file_name.endswith('.tsv')):
                        print(file_name)
                        project_name = proj_name
                        if projects.find_one({"projectname": project_name}, {'_id' : 0, "projectname": 1}) != None:
                            flash(f'File Name : {project_name} already exist!', 'warning')
                            return redirect(url_for('easyAnno.home'))

                        image_anno_detail = {}
                        image_id = 'I'+re.sub(r'[-: \.]', '', str(datetime.now()))
                        image_file = io.BytesIO(myfile.read())
                        # store images to mongodb fs collection
                        mongo.save_file(file_name, image_file, imageId = image_id)
                        image_anno_detail["projectname"] = project_name
                        image_anno_detail["imageId"] = image_id
                        image_anno_detail["filename"] = file_name
                        img_scipt_to_lang = {"Latin": "EN", "Devanagari": "HI", "Bengali": "BN"}
                        try:
                            image_script = image_to_osd(Image.open(image_file)).split('\n')[4].split(':')[1].strip()
                            image_text = image_to_string(Image.open(image_file), lang='eng+hin+ben')
                            image_anno_detail["imageTextLang"] = img_scipt_to_lang[image_script]
                            image_anno_detail["imageText"] = image_text
                        except:
                            image_anno_detail["imageTextLang"] = "OTH"
                            image_anno_detail["imageText"] = ""
                        image_anno_detail['lastUpdatedBy'] = ''
                        all_access = {}
                        image_anno_detail['allAccess'] = all_access
                        all_updates = {}
                        image_anno_detail['allUpdates'] = all_updates
                        # print(image_anno_detail)
                        imageanno.insert_one(image_anno_detail)
                        image_files[image_id] = file_name
                    else:
                        tags_df = pd.read_csv(io.BytesIO(myfile.read()), sep='\t', dtype=str)
                        # print(type(tags))
                        # print(tags_df)
                        for i in range(len(tags_df)):
                            tag_set[tags_df.iloc[i, 0]] = tags_df.iloc[i, 1].split(',')
        
        project_owner = current_user.username
        project_details = {}
        lastActiveId = {current_user.username: list(image_files.keys())[0]}
        project_details["projectType"] = "image"
        project_details["projectname"] = project_name
        project_details["projectOwner"] = project_owner
        project_details["tagSet"] = tag_set
        project_details["imageFiles"] = image_files
        project_details["lastActiveId"] = lastActiveId
        project_details["sharedwith"]  = [project_owner]
        project_details["projectdeleteFLAG"] = 0
        project_details["isPublic"] = 0
        project_details["derivedFromProject"] = []
        project_details["projectDerivatives"] = []
        project_details["aboutproject"] = ''

        # print(project_details)
        projects.insert_one(project_details)
        # get curent user project list and update
        userprojectnamelist = userprojects.find_one({'username' : current_user.username})["myproject"]
        # print(f'{"#"*80}\n{userprojectnamelist}')
        userprojectnamelist.append(project_details['projectname'])
        userprojects.update_one({ 'username' : current_user.username }, \
            { '$set' : { 'myproject' : userprojectnamelist, 'activeprojectname' :  project_details['projectname']}})

    except:
        # flash('Please upload a zip file') 
        flash('Please upload a zip file. Check the file format at the link provided for the Sample File', 'warning')

        return redirect(url_for('easyAnno.home'))   

    flash('File created successfully :)', 'success')

    # return render_template('home.html',  data=currentuserprojectsname, activeproject=activeprojectname)
    return redirect(url_for('easyAnno.home'))

@easyAnno.route('/textAnno', methods=['GET', 'POST'])
@login_required
def textAnno():
    # print('textAnno')
    projects, userprojects, textanno = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'userprojects',
                                                                'textanno')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
    project_type_list = ['text']
    currentuserprojectsname = getprojectsnamebytype.getprojectsnamebytype(projects,
                                                                            currentuserprojectsname,
                                                                            project_type_list)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)
    
    project_details = projects.find_one({"projectname": activeprojectname},
                                        {"_id": 0, "projectType": 1, "tagSet": 1, "lastActiveId": 1})
    # pprint(project_details)
    # get all the data for active project
    try:
        my_projects = len(userprojects.find_one({'username' : current_user.username})["myproject"])
        shared_projects = len(userprojects.find_one({'username' : current_user.username})["projectsharedwithme"])
        # print("my_projects shared_projects", my_projects, shared_projects)
        if  (my_projects+shared_projects)== 0:
            flash('Please create your first project', 'info')
            return redirect(url_for('easyAnno.home'))
        elif (my_projects == 0 and
                shared_projects >= 1 and
                activeprojectname == "" or
                project_details["projectType"] not in project_type_list):
            flash('Please select your file from All Files/Change Active File', 'info')
            return redirect(url_for('easyAnno.home'))    
    except:
        # print(f'{"#"*80}\nCurrent user details not in database!!!')
        flash('Please create your first project', 'info')
        return redirect(url_for('easyAnno.home'))

    project_details = projects.find_one({"projectname": activeprojectname}, \
                                        {"_id": 0, "projectType": 1, "tagSet": 1, "lastActiveId": 1})
    if project_details != None:
        # print(project_details)
        if (project_details["projectType"] != "text"):
            flash("Active file is 'image' type. Plese select 'text' file to annotate.", 'info')
            return redirect(url_for('easyAnno.home'))
        last_active_id_user = project_details["lastActiveId"]
        if (current_username in last_active_id_user):
            last_active_id = project_details["lastActiveId"][current_user.username]
        else:
            if (project_details["projectType"] == 'text'):
                text_data = projects.find_one({"projectname": activeprojectname}, \
                                    {"_id" : 0, "textData": 1 })
            for id in text_data.values():
                tIds = list(id.keys())
            tIds = sorted(tIds)
            last_active_id = tIds[0]
            projects.update_one({ "projectname": activeprojectname },
                            { '$set' : { "lastActiveId": {current_username: last_active_id} }})

        # print(project_details["textData"][last_active_id])
        # print(last_active_id)
        
        project_details = projects.find_one({"projectname": activeprojectname},
            {"_id": 0, "tagSet": 1, "tagSetMetaData": 1, "textData."+last_active_id: 1, "textData": 1})
        # print(project_details)
        total_comments = len(project_details["textData"])
        annotated_comments = 0
        for comments in textanno.find({"projectname": activeprojectname}, \
                                        {"projectname": 1, current_user.username: 1 }):
            if (current_user.username in comments):                            
                annotatedFLAG = comments[current_user.username]["annotatedFLAG"]
                if (annotatedFLAG == 1):
                    annotated_comments += 1
        remaining_comments = total_comments - annotated_comments

        project_details['totalComments'] = total_comments
        project_details["annotatedComments"] = annotated_comments
        project_details["remainingComments"]  = remaining_comments   
        project_details["textData"] = project_details["textData"][last_active_id]
        project_details["lastActiveId"] = last_active_id

        # get current datetime upto seconds as data accessed time
        # use when 'Save' button is clicked
        project_details['accessedOnTime'] = datetime.now().strftime("%d/%m/%y %H:%M:%S")
        # pprint(project_details)
        # check if tagSetMetaData key is present int he project details
        # to check if the tagset contains any dependency and default tags list
        if ('tagSetMetaData' in project_details and \
            not bool(project_details["tagSetMetaData"])):
            # print(project_details["tagSetMetaData"])
            # print(not bool(project_details["tagSetMetaData"]))
            project_details.pop("tagSetMetaData")


        currentText = textanno.find_one({"projectname": activeprojectname, "textId": last_active_id}, \
                    {"_id": 0, current_user.username: 1})
        # print(len(currentText.keys()))
        # pprint(project_details)

        if (currentText != None and \
            len(currentText.keys()) != 0 and \
            current_user.username == list(currentText.keys())[0]):
            # print(currentText)
            # print(list(currentText.keys())[0])
            project_details[list(currentText.keys())[0]] = list(currentText.values())[0]
            project_details['currentUser'] = current_user.username
            # print(project_details)
            # pprint(project_details)
            currentAnnotation = project_details[current_username]
            defaultAnnotation = project_details['tagSetMetaData']['defaultCategoryTags']
            # pprint(currentAnnotation)
            # pprint(defaultAnnotation)
            project_details['tagSetMetaData']['defaultCategoryTags'] = {**defaultAnnotation, **currentAnnotation}

            # pprint(project_details)

            return render_template('textAnno.html',
                                   projectName=activeprojectname,
                                   proj_data=project_details,
                                   data=currentuserprojectsname)
        else:

            return render_template('textAnno.html',
                                   projectName=activeprojectname,
                                   proj_data=project_details,
                                   data=currentuserprojectsname)
        

    else:
        flash('File not in the database', 'danger') 
    
    return render_template('textAnno.html',
                           projectName=activeprojectname,
                           proj_data=project_details,
                           data=currentuserprojectsname)

@easyAnno.route('/savetextAnno', methods=['GET', 'POST'])
@login_required
def savetextAnno():
    # print('IN /savetextAnno')
    # projects = mongo.db.projects              # collection of users and their respective projects
    # userprojects = mongo.db.userprojects              # collection of users and their respective projects
    # textanno = mongo.db.textanno
    projects, userprojects, textanno = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'userprojects',
                                                                'textanno')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)

    if request.method == 'POST':
        # annotatedText = dict(request.form.lists())
        
        annotatedText = json.loads(request.form['a'])
        # pprint(annotatedText)

        lastActiveId = annotatedText['lastActiveId'][0]
        # lastActiveId = annotatedText['lastActiveId']
        project_details = projects.find_one({"projectname": activeprojectname}, {"_id": 0, "textData": 1})        
        # print(project_details.values())
        nextId = nextIdToAnnotate(project_details.values(), lastActiveId)
        # print(nextId)

        project_details = projects.find_one({"projectname": activeprojectname}, {"_id": 0, "tagSet": 1})
        # pprint(project_details)
        # print(project_details.values())
        tagSetMetaData = projects.find_one({"projectname": activeprojectname}, {"_id": 0, "tagSetMetaData": 1})['tagSetMetaData']
        # current user tags for the text
        currentAnnotatorTags = {}
        for tagset in project_details.values():
            categories = list(tagset.keys())
        for category in categories:
            # print(category)
            if category in annotatedText:
                if (len(annotatedText[category])) == 1:
                    if ('categoryHtmlElement' in tagSetMetaData):
                        if(tagSetMetaData['categoryHtmlElement'][category] == 'select'):
                            currentAnnotatorTags[category] =  annotatedText[category]
                        else:
                            currentAnnotatorTags[category] =  annotatedText[category][0]
                    else:
                        currentAnnotatorTags[category] =  annotatedText[category][0]
                elif (len(annotatedText[category])) > 1:
                    currentAnnotatorTags[category] =  annotatedText[category]
            elif category not in annotatedText:
                # print(tagset[category])
                if(tagset[category][0] == '#SPAN_TEXT#'):
                    continue
                # elif ('categoryDependency' in tagSetMetaData):
                #     saveTextAnnoCategoryDependency = tagSetMetaData['categoryDependency']

                else:
                    currentAnnotatorTags[category] = ''
        
        if "Duplicate" in currentAnnotatorTags:
            currentAnnotatorTags["Duplicate"] = annotatedText["Duplicate Text"][0]
    
        if 'annotatorComment' in currentAnnotatorTags:
            currentAnnotatorTags["annotatorComment"] = annotatedText["annotatorComment"][0]
    
        currentAnnotatorTags["annotatedFLAG"] = 1

        once_annotated = textanno.find_one({"projectname": activeprojectname, "textId": lastActiveId}, {"_id": 0})

        if once_annotated != None:
            # update with this user annotation and change lastUpdatedBy
            # print(once_annotated)
            currentAnnotatorTags = currentAnnotatorTags
            # print(currentAnnotatorTags, '\n=============\n', once_annotated[current_user.username])
            # if difference between new annotation and existing annotation is False
            # (user has used 'Save' in place of 'Next' button)
            # Then there should be no update in the allAccess and allUpdates timestamp
            if current_user.username in once_annotated and \
                not bool(diff(currentAnnotatorTags, once_annotated[current_user.username])):
                projects.update_one({"projectname": activeprojectname}, \
                                    { '$set' : { 'lastActiveId.'+current_user.username: nextId }})
                # print('matchedddddddddddddddddddddddd')
                return redirect(url_for('easyAnno.textAnno'))

            lastUpdatedBy = current_user.username

            all_access = once_annotated["allAccess"]
            all_updates = once_annotated["allUpdates"]

            if (current_user.username in all_access.keys()):
                # print(all_access, all_updates)
                all_access[current_user.username].append(annotatedText["accessedOnTime"][0])
                all_updates[current_user.username].append(datetime.now().strftime("%d/%m/%y %H:%M:%S"))
                # print(all_access, all_updates)
            else:
                all_access[current_user.username] = [annotatedText["accessedOnTime"][0]]
                all_updates[current_user.username] = [datetime.now().strftime("%d/%m/%y %H:%M:%S")]

            oldAnnotation = textanno.find_one({"projectname": activeprojectname, "textId": lastActiveId},
                                    {"_id": 0, current_username: 1})
            # print(oldAnnotation)
            if (current_username in oldAnnotation):
                oldAnnotation = oldAnnotation[current_username]
                mergeredAnnotation = {**oldAnnotation, **currentAnnotatorTags}
            else:
                mergeredAnnotation = currentAnnotatorTags
            textanno.update_one({"projectname": activeprojectname, "textId": lastActiveId}, \
                { '$set' : { 'lastUpdatedBy' : lastUpdatedBy, current_user.username: mergeredAnnotation,\
                    "allAccess": all_access, "allUpdates": all_updates}})
        else:
            text_anno = {}
            text_anno["projectname"] = activeprojectname
            text_anno["textId"] = lastActiveId
            text_anno["ID"] = annotatedText["ID"][0]
            text_anno["Text"] = annotatedText["Text"][0]
            text_anno[current_user.username] = currentAnnotatorTags
            text_anno['lastUpdatedBy'] = current_user.username
            all_access = {}
            all_access[current_user.username] = [annotatedText["accessedOnTime"][0]]
            text_anno['allAccess'] = all_access
            all_updates = {}
            all_updates[current_user.username] = [datetime.now().strftime("%d/%m/%y %H:%M:%S")]
            text_anno['allUpdates'] = all_updates


            textanno.insert_one(text_anno)

        projects.update_one({"projectname": activeprojectname}, \
                            { '$set' : { 'lastActiveId.'+current_user.username: nextId }})

        return redirect(url_for('easyAnno.textAnno'))

    return redirect(url_for('easyAnno.textAnno'))

@easyAnno.route('/savetextAnnoSpan', methods=['GET', 'POST'])
@login_required
def savetextAnnoSpan():
    # print('IN /savetextAnnoSpan')
    userprojects, textanno = getdbcollections.getdbcollections(mongo,
                                                                'userprojects',
                                                                'textanno')

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
        for key, value in annotatedTextSpan.items():
            for k, v in value.items():
                textanno.update_one({"projectname": activeprojectname, "textId": lastActiveId},
                                    {'$set': { 
                                                # "spanAnnotation.text."+spanId: annotatedTextSpan[spanId]
                                                current_username+'.'+key+'.'+k: v,
                                                current_username+".annotatedFLAG": 1
                                            }})
        return "OK"

    # return redirect(url_for('easyAnno.textAnno'))
    return "OK"

@easyAnno.route('/deletetextAnnoSpan', methods=['GET', 'POST'])
@login_required
def deletetextAnnoSpan():
    # print('IN /deletetextAnnoSpan')
    userprojects, textanno = getdbcollections.getdbcollections(mongo,
                                                                'userprojects',
                                                                'textanno')

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
        for key, value in annotatedTextSpan.items():
            for k, v in value.items():
                textanno.update_one({"projectname": activeprojectname, "textId": lastActiveId},
                                    {'$unset': { 
                                                # "spanAnnotation.text."+spanId: annotatedTextSpan[spanId]
                                                current_username+'.'+key+'.'+k: 1,
                                                # current_username+".annotatedFLAG": 1
                                            }})
        return "OK"

    return "OK"


@easyAnno.route('/loadprevioustext', methods=['GET'])
@login_required
def loadprevioustext():
    # projects = mongo.db.projects              # collection of users and their respective projects
    # userprojects = mongo.db.userprojects              # collection of users and their respective projects
    # textanno = mongo.db.textanno

    # currentuserprojectsname =  sorted(list(currentuserprojects()))
    # activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
    #                 {'_id' : 0, 'activeprojectname': 1})['activeprojectname']
    # print(currentuserprojectsname, activeprojectname)

    # print(f'{"="*80}\nPrevious\n{"="*80}')

    projects, userprojects, textanno = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'userprojects',
                                                                'textanno')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
    project_type_list = ['text']
    currentuserprojectsname = getprojectsnamebytype.getprojectsnamebytype(projects,
                                                                            currentuserprojectsname,
                                                                            project_type_list)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)

    lastActiveId = request.args.get('data')
    lastActiveId = eval(lastActiveId)
    # print(lastActiveId)
    project_details = projects.find_one({"projectname": activeprojectname}, {"_id": 0, "textData": 1})        
    # print(project_details.values())
    previousId = previousIdToAnnotate(project_details.values(), lastActiveId)

    projects.update_one({"projectname": activeprojectname}, \
                        { '$set' : { 'lastActiveId.'+current_user.username: previousId }})

    # previousText = textanno.find_one({"projectname": activeprojectname, "textId": previousId}, \
    #                 {"_id": 0, current_user.username: 1})
    # if previousText != None:
    #     print(previousText)
    #     # return render_template('textAnno.html', projectName=activeprojectname, proj_data=project_details, data=currentuserprojectsname)
    # else:
    #     return redirect(url_for('easyAnno.textAnno'))

    return redirect(url_for('easyAnno.textAnno'))

@easyAnno.route('/loadnexttext', methods=['GET'])
@login_required
def loadnexttext():
    # projects = mongo.db.projects              # collection of users and their respective projects
    # userprojects = mongo.db.userprojects              # collection of users and their respective projects
    # textanno = mongo.db.textanno

    # currentuserprojectsname =  sorted(list(currentuserprojects()))
    # activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
    #                 {'_id' : 0, 'activeprojectname': 1})['activeprojectname']
    # print(currentuserprojectsname, activeprojectname)

    # print(f'{"="*80}\nNext\n{"="*80}')
    projects, userprojects, textanno = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'userprojects',
                                                                'textanno')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
    project_type_list = ['text']
    currentuserprojectsname = getprojectsnamebytype.getprojectsnamebytype(projects,
                                                                            currentuserprojectsname,
                                                                            project_type_list)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)
        

    lastActiveId = request.args.get('data')
    lastActiveId = eval(lastActiveId)
    # print(lastActiveId)
    project_details = projects.find_one({"projectname": activeprojectname}, {"_id": 0, "textData": 1})        
    # print(project_details.values())
    nextId = nextIdToAnnotate(project_details.values(), lastActiveId)

    projects.update_one({"projectname": activeprojectname}, \
                        { '$set' : { 'lastActiveId.'+current_user.username: nextId }})

    # nextText = textanno.find_one({"projectname": activeprojectname, "textId": nextId}, \
    #             {"_id": 0, current_user.username: 1})
    # if nextText != None:
    #     print(nextText)
    #     # return render_template('textAnno.html', projectName=activeprojectname, proj_data=project_details, data=currentuserprojectsname)
    # else:
    #     return redirect(url_for('easyAnno.textAnno'))

    return redirect(url_for('easyAnno.textAnno')) 

@easyAnno.route('/loadunannotext', methods=['GET'])
@login_required
def loadunannotext():
    # projects = mongo.db.projects              # collection of users and their respective projects
    # userprojects = mongo.db.userprojects              # collection of users and their respective projects
    # textanno = mongo.db.textanno

    # currentuserprojectsname =  sorted(list(currentuserprojects()))
    # activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
    #                 {'_id' : 0, 'activeprojectname': 1})['activeprojectname']
    # # print(currentuserprojectsname, activeprojectname)

    projects, userprojects, textanno = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'userprojects',
                                                                'textanno')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
    project_type_list = ['text']
    currentuserprojectsname = getprojectsnamebytype.getprojectsnamebytype(projects,
                                                                            currentuserprojectsname,
                                                                            project_type_list)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)
        
    project_type = projects.find_one({"projectname": activeprojectname}, \
                    {"_id": 0, "projectType": 1})["projectType"]

    # print(f'{"="*80}\nUn-Anno\n{"="*80}')

    lastActiveId = request.args.get('data')
    lastActiveId = eval(lastActiveId)
    # print(lastActiveId)

    projects.update_one({"projectname": activeprojectname}, \
                        { '$set' : { 'lastActiveId.'+current_user.username: lastActiveId }})

    if (project_type == 'text'):
        return redirect(url_for('easyAnno.textAnno'))
    elif (project_type == 'image'):
        return redirect(url_for('easyAnno.imageAnno'))    

@easyAnno.route('/imageAnno', methods=['GET', 'POST'])
@login_required
def imageAnno():
    # projects = mongo.db.projects              # collection of users and their respective projects
    # test_project = projects.find()
    # for proj in test_project:
    #     # print(proj)
    #     for i_id in proj['imagefiles']:
    #         image_name, image = fetch_image_files(i_id)
    #         return render_template('imageAnno.html', image_id = i_id, image_name=image_name, image=image.decode('utf-8'))
    # return render_template('imageAnno.html')


    # projects = mongo.db.projects              # collection of users and their respective projects
    # userprojects = mongo.db.userprojects              # collection of users and their respective projects
    # imageanno = mongo.db.imageanno
    
    # currentuserprojectsname =  sorted(list(currentuserprojects()))
    # activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
    #                 {'_id' : 0, 'activeprojectname': 1})['activeprojectname']
    
    # if (len(activeprojectname) == 0):
    #     flash('Please select your file from All Files')
    #     return redirect(url_for('easyAnno.home'))

    projects, userprojects, imageanno = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'userprojects',
                                                                'imageanno')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
    project_type_list = ['text']
    currentuserprojectsname = getprojectsnamebytype.getprojectsnamebytype(projects,
                                                                            currentuserprojectsname,
                                                                            project_type_list)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)

    # get all the data for active project
    try:
        my_projects = len(userprojects.find_one({'username' : current_user.username})["myproject"])
        shared_projects = len(userprojects.find_one({'username' : current_user.username})["projectsharedwithme"])
        # print("my_projects shared_projects", my_projects, shared_projects)
        if  (my_projects+shared_projects)== 0:
            flash('Please create your first project', 'info')
            return redirect(url_for('easyAnno.home'))
        elif (my_projects == 0 and shared_projects >= 1 and activeprojectname == ""):
            flash('Please select your file from All Files/Change Active File', 'info')
            return redirect(url_for('easyAnno.home'))    
    except:
        # print(f'{"#"*80}\nCurrent user details not in database!!!')
        flash('Please create your first project', 'info')
        return redirect(url_for('easyAnno.home'))

    project_details = projects.find_one({"projectname": activeprojectname}, \
                                        {"_id": 0, "projectType": 1, "tagSet": 1, "lastActiveId": 1})
    if project_details != None:
        # print(project_details)
        if (project_details["projectType"] != "image"):
            flash("Active file is 'text' type. Plese select 'image' file to annotate.", 'info')
            return redirect(url_for('easyAnno.home'))

        last_active_id = project_details["lastActiveId"][current_user.username]
        # print(project_details["textData"][last_active_id])
        # print(last_active_id)
        
        project_details = projects.find_one({"projectname": activeprojectname}, \
                                            {"_id": 0, "tagSet": 1, "imageFiles": 1})
        # print(project_details)
        total_images = len(project_details["imageFiles"])
        annotated_images = 0
        for images in imageanno.find({"projectname": activeprojectname}, \
                                        {"projectname": 1, current_user.username: 1, "annotatedFLAG": 1 }):
            if (current_user.username in images):
                annotatedFLAG = images[current_user.username]["annotatedFLAG"]
                if (annotatedFLAG == 1):
                    annotated_images += 1
        remaining_images = total_images - annotated_images

        project_details['totalImages'] = total_images
        project_details["annotatedImages"] = annotated_images
        project_details["remainingImages"]  = remaining_images 
        project_details["imageFiles"] = fetch_image_files(last_active_id)
        project_details["lastActiveId"] = last_active_id

        # get current datetime upto seconds as data accessed time
        # use when 'Save' button is clicked
        project_details['accessedOnTime'] = datetime.now().strftime("%d/%m/%y %H:%M:%S")

        currentImage = imageanno.find_one({"projectname": activeprojectname, "imageId": last_active_id}, \
                    {"_id": 0, current_user.username: 1 })
        image_text = imageanno.find_one({"projectname": activeprojectname, "imageId": last_active_id}, \
                    {"_id": 0, 'imageText': 1 })['imageText']
        # print(len(currentImage.keys()))
        # print(currentImage)
        # print(project_details)
        if (currentImage != None and \
            len(currentImage.keys()) != 0 and \
            current_user.username == list(currentImage.keys())[0]):
            # print(currentText)
            # print(list(currentImage.keys())[0])
            # print(list(currentImage.values())[0])
            project_details[list(currentImage.keys())[0]] = list(currentImage.values())[0]
            project_details['currentUser'] = current_user.username
            project_details[current_user.username]['imageText'] = image_text
            # print(project_details[current_user.username]['imageText'])
            if "imageBytes" in project_details["imageFiles"]:
                del project_details["imageFiles"]["imageBytes"]
            # print(project_details.keys())
            return render_template('imageAnno.html', projectName=activeprojectname, proj_data=project_details, data=currentuserprojectsname)
        else:
            try:
                currentImage = imageanno.find_one({"projectname": activeprojectname, "imageId": last_active_id}, \
                        {"_id": 0, "imageTextLang": 1, "imageText": 1})
                        
                project_details["imageTextLang"] = currentImage["imageTextLang"]
                project_details["imageText"] = currentImage["imageText"]
            except:
                project_details["imageTextLang"] = ""
                project_details["imageText"] = ""    
            if "imageBytes" in project_details["imageFiles"]:
                del project_details["imageFiles"]["imageBytes"]
            # print(project_details.keys())
            return render_template('imageAnno.html', projectName=activeprojectname, proj_data=project_details, data=currentuserprojectsname)

    else:
        flash('File not in the database', 'danger') 

    # print(project_details)

    return render_template('imageAnno.html', projectName=activeprojectname, proj_data=project_details, data=currentuserprojectsname)

@easyAnno.route('/saveimageAnno', methods=['GET', 'POST'])
@login_required
def saveimageAnno():
    projects = mongo.db.projects              # collection of users and their respective projects
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    imageanno = mongo.db.imageanno

    activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
                    {'_id' : 0, 'activeprojectname': 1})['activeprojectname']

    if request.method == 'POST':
        annotatedImage = dict(request.form.lists())
        # print(annotatedImage)

        lastActiveId = annotatedImage['lastActiveId'][0]
        project_details = projects.find_one({"projectname": activeprojectname}, {"_id": 0, "imageFiles": 1})        
        # print(project_details.values())
        nextId = nextIdToAnnotate(project_details.values(), lastActiveId)
        # print(nextId)

        project_details = projects.find_one({"projectname": activeprojectname}, {"_id": 0, "tagSet": 1})
        # current user tags for the image
        currentAnnotatorTags = {}
        for tagset in project_details.values():
            categories = list(tagset.keys())
        for category in categories:
            # print(category)
            if category in annotatedImage:
                currentAnnotatorTags[category] =  annotatedImage[category][0]
            elif category not in annotatedImage:
                currentAnnotatorTags[category] = ''
        currentAnnotatorTags["Duplicate"] = annotatedImage["Duplicate Image"][0]
        currentAnnotatorTags["annotatorComment"] = annotatedImage["annotatorComment"][0]
        currentAnnotatorTags["imageText"] = annotatedImage["imageText"][0]
        currentAnnotatorTags["annotatedFLAG"] = 1 
        # print(currentAnnotatorTags)

        # version 1
        once_annotated = imageanno.find_one({"projectname": activeprojectname, "imageId": lastActiveId}, \
                                            {"_id": 0 })

        # # version 2 : not take 'imageText' of current user as if the user once edited and re-edit to the  
        # # edit imageText(by other user) with his/her previous imageText then 
        # # json diff will pass it and it will not then be updated to the database
        # once_annotated = imageanno.find_one({"projectname": activeprojectname, "imageId": lastActiveId}, \
        #                                     {"_id": 0, current_user.username+'.imageText': 0})
        # print(once_annotated)
        if once_annotated != None:
            # update with this user annotation and change lastUpdatedBy
            # print(once_annotated)
            currentAnnotatorTags = currentAnnotatorTags
            # once_annotated[current_user.username]['imageText'] = currentAnnotatorTags["imageText"]
            # once_annotated[current_user.username]['imageText'] = currentAnnotatorTags["imageText"]
            # print(currentAnnotatorTags, '\n=============\n', once_annotated[current_user.username])
            # if difference between new annotation and existing annotation is False
            # (user has used 'Save' in place of 'Next' button)
            # Then there should be no update in the allAccess and allUpdates timestamp
            # print(diff(currentAnnotatorTags, once_annotated[current_user.username]))
            if current_user.username in once_annotated and \
                not bool(diff(currentAnnotatorTags, once_annotated[current_user.username])):
                projects.update_one({"projectname": activeprojectname}, \
                                    { '$set' : { 'lastActiveId.'+current_user.username : nextId }})
                return redirect(url_for('easyAnno.imageAnno'))

            lastUpdatedBy = current_user.username

            all_access = once_annotated["allAccess"]
            all_updates = once_annotated["allUpdates"]

            if (current_user.username in all_access.keys()):
                # print(all_access, all_updates)
                all_access[current_user.username].append(annotatedImage["accessedOnTime"][0])
                all_updates[current_user.username].append(datetime.now().strftime("%d/%m/%y %H:%M:%S"))
                # print(all_access, all_updates)
            else:
                all_access[current_user.username] = [annotatedImage["accessedOnTime"][0]]
                all_updates[current_user.username] = [datetime.now().strftime("%d/%m/%y %H:%M:%S")]

            # version 1
            # imageanno.update_one({"projectname": activeprojectname, "imageId": lastActiveId}, \
            #     { '$set' : { 'lastUpdatedBy' : lastUpdatedBy, current_user.username: currentAnnotatorTags,\
            #         "allAccess": all_access, "allUpdates": all_updates}})

            # version 2
            imageanno.update_one({"projectname": activeprojectname, "imageId": lastActiveId}, \
                { '$set' : { 'imageText': currentAnnotatorTags["imageText"],\
                    'lastUpdatedBy' : lastUpdatedBy, current_user.username: currentAnnotatorTags,\
                    "allAccess": all_access, "allUpdates": all_updates}})

            imageanno.update_one({"projectname": activeprojectname, "imageId": lastActiveId}, \
                { '$set' : { current_user.username+'.imageText': currentAnnotatorTags["imageText"] }})
        else:
            image_anno = {}
            image_anno["projectname"] = activeprojectname
            image_anno["imageId"] = lastActiveId
            image_anno["filename"] = annotatedImage["filename"][0]
            image_anno[current_user.username] = currentAnnotatorTags
            image_anno['lastUpdatedBy'] = current_user.username
            all_access = {}
            all_access[current_user.username] = [annotatedImage["accessedOnTime"][0]]
            image_anno['allAccess'] = all_access
            all_updates = {}
            all_updates[current_user.username] = [datetime.now().strftime("%d/%m/%y %H:%M:%S")]
            image_anno['allUpdates'] = all_updates


            imageanno.insert_one(image_anno)

        projects.update_one({"projectname": activeprojectname}, \
                            { '$set' : { 'lastActiveId.'+current_user.username: nextId }})

        return redirect(url_for('easyAnno.imageAnno'))

    return redirect(url_for('easyAnno.imageAnno'))

@easyAnno.route('/loadpreviousimage', methods=['GET'])
@login_required
def loadpreviousimage():
    # projects = mongo.db.projects              # collection of users and their respective projects
    # userprojects = mongo.db.userprojects              # collection of users and their respective projects
    # imageanno = mongo.db.imageanno

    # currentuserprojectsname =  sorted(list(currentuserprojects()))
    # activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
    #                 {'_id' : 0, 'activeprojectname': 1})['activeprojectname']
    # print(currentuserprojectsname, activeprojectname)

    # print(f'{"="*80}\nPrevious\n{"="*80}')

    projects, userprojects, imageanno = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'userprojects',
                                                                'imageanno')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
    project_type_list = ['image']
    currentuserprojectsname = getprojectsnamebytype.getprojectsnamebytype(projects,
                                                                            currentuserprojectsname,
                                                                            project_type_list)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)
        

    lastActiveId = request.args.get('data')
    lastActiveId = eval(lastActiveId)
    # print(lastActiveId)
    project_details = projects.find_one({"projectname": activeprojectname}, {"_id": 0, "imageFiles": 1})        
    # print(project_details.values())
    previousId = previousIdToAnnotate(project_details.values(), lastActiveId)

    projects.update_one({"projectname": activeprojectname}, \
                        { '$set' : { 'lastActiveId.'+current_user.username: previousId }})

    return redirect(url_for('easyAnno.imageAnno'))

@easyAnno.route('/loadnextimage', methods=['GET'])
@login_required
def loadnextimage():
    # projects = mongo.db.projects              # collection of users and their respective projects
    # userprojects = mongo.db.userprojects              # collection of users and their respective projects
    # imageanno = mongo.db.imageanno

    # currentuserprojectsname =  sorted(list(currentuserprojects()))
    # activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
    #                 {'_id' : 0, 'activeprojectname': 1})['activeprojectname']
    # print(currentuserprojectsname, activeprojectname)

    # print(f'{"="*80}\nNext\n{"="*80}')

    projects, userprojects, imageanno = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'userprojects',
                                                                'imageanno')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
    project_type_list = ['image']
    currentuserprojectsname = getprojectsnamebytype.getprojectsnamebytype(projects,
                                                                            currentuserprojectsname,
                                                                            project_type_list)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)

    lastActiveId = request.args.get('data')
    lastActiveId = eval(lastActiveId)
    # print(lastActiveId)
    project_details = projects.find_one({"projectname": activeprojectname}, {"_id": 0, "imageFiles": 1})        
    # print(project_details.values())
    nextId = nextIdToAnnotate(project_details.values(), lastActiveId)

    projects.update_one({"projectname": activeprojectname}, \
                        { '$set' : { 'lastActiveId.'+current_user.username: nextId }})

    return redirect(url_for('easyAnno.imageAnno')) 

def fetch_image_files(i_id):
    # print(i_id)
    fs =  gridfs.GridFS(mongo.db)                       # creating GridFS instance to get required files
    files = fs.find({"imageId": i_id})
    # print(type(files))
    for file in files:
        # print(file.read())
        name = file.filename
        # print(name)
        # open('app/static/image/'+name, 'wb').write(file.read())
        image = file.read()
        # print(type(image))
        encoded_img_data = base64.b64encode(image)
        # print(type(image), type(encoded_img_data))
        # print({'filename': name, 'image': encoded_img_data})
        return {'filename': name, 'image': encoded_img_data.decode('utf-8'), 'imageBytes': image}

# get all projects name created by the current active user
# @easyAnno.route('/currentuserprojects')
def currentuserprojects():
    # getting the collections
    userprojects = mongo.db.userprojects              # collection of users and their respective projects

    # print(f'{"#"*80}\n{current_user.username}')
    userprojectsname = []
    # try:
    userprojects  = userprojects.find_one({ 'username' : current_user.username })
    myproject = userprojects['myproject']
    projectsharedwithme = userprojects['projectsharedwithme']
    userprojectsname = set(myproject + projectsharedwithme)
    # except:
        # flash('Please create your first project.', 'info')

    # print(f'{"#"*80}\n{userprojectsname}')
    
    return userprojectsname

# save active project name for active user
@easyAnno.route('/activeprojectname', methods=['GET', 'POST'])
def activeprojectname():
    userprojects = mongo.db.userprojects                # collection containing username and his/her last seen project name
    projectname = str(request.args.get('a'))            # data through ajax

    userprojects.update_one({ 'username' : current_user.username }, \
            { '$set' : { 'activeprojectname' :  projectname}})

    return 'OK'

# # MongoDB Database
# # user login form route
# @easyAnno.route('/login', methods=['GET', 'POST'])
# def login():
#     # userlogin = mongo.db.userlogin                          # collection of users and their login details
#     dummyUserandProject()
#     if current_user.is_authenticated:
#         return redirect(url_for('easyAnno.home'))
#     form = UserLoginForm()
#     if form.validate_on_submit():
#         # username = userlogin.find_one({"username": form.username.data})
#         user = UserLogin(username=form.username.data)
#         # print(user)
#         if user is None or not user.check_password(form.password.data):
#             flash('Invalid username or password', 'warning')
#             return redirect(url_for('login'))
#         login_user(user, force=True)
#         next_page = request.args.get('next')
#         if not next_page or url_parse(next_page).netloc != '':
#             next_page = url_for('home')
#         return redirect(next_page)
#     return render_template('login.html', form=form)

# # MongoDB Database
# # use logout
# @easyAnno.route('/logout')
# def logout():
#     try:
#         logout_user()
#         return redirect(url_for('easyAnno.home'))
#     except:
#         return redirect(url_for('easyAnno.home'))    

# # MongoDB Database
# # new user registration
# @easyAnno.route('/register', methods=['GET', 'POST'])
# def register():
#     userlogin = mongo.db.userlogin                          # collection of users and their login details
#     dummyUserandProject()
#     if current_user.is_authenticated:
#         # print(current_user.get_id())
#         return redirect(url_for('easyAnno.home'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         # user = UserLogin(username=form.username.data)
#         password = generate_password_hash(form.password.data)
#         # print(user, password)

#         userlogin.insert_one({"username": form.username.data, "password": password})

#         userprojects = mongo.db.userprojects              # collection of users and their respective projectlist
#         userprojects.insert_one({'username' : form.username.data, 'myproject': [], \
#             'projectsharedwithme': [], 'activeprojectname' : ''})

#         flash('Congratulations, you are now a registered user!', 'success')
#         return redirect(url_for('login'))
#     return render_template('register.html', form=form)

# @easyAnno.route('/userslist', methods=['GET', 'POST'])
# def userslist():
#     print('easyAnno userslist')
#     userlogin = mongo.db.userlogin                          # collection of users and their login details
#     projects = mongo.db.projects              # collection of users and their respective projects
#     userprojects = mongo.db.userprojects              # collection of users and their respective projects

    
#     activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
#                     {'_id' : 0, 'activeprojectname': 1})['activeprojectname']

#     usersList = []

#     proj_shared_with = projects.find({"projectname": activeprojectname}, \
#                         {"_id": 0, "sharedwith": 1})
    
#     for user in userlogin.find({}, {"_id": 0, "username": 1}):
#         # print(user)
#         usersList.append(user["username"])
#         # print(user)
#     # usersList.remove(current_user.username)
#     for sharer in proj_shared_with:
#         sharer  = sharer["sharedwith"]
#         usersList = [i for i in usersList if i not in sharer]
        
#     # print(usersList)
#     return jsonify(usersList=usersList)

# @easyAnno.route('/shareprojectwith', methods=['GET', 'POST'])
# def shareprojectwith():
#     # getting the collections
#     userprojects = mongo.db.userprojects              # collection of users and their respective projects
#     projects = mongo.db.projects              # collection of users and their respective projects

#     users = request.args.get('a').split(',')                    # data through ajax
#     # print(users)
#     activeprojectname = userprojects.find_one({ 'username' : current_user.username })['activeprojectname']
#     #get _id and project name in the collection projects
#     activeprojectdetails = projects.find_one({"projectname": activeprojectname}, \
#                             {"_id" : 1, "projectname" : 1, "sharedwith": 1, "projectType": 1, "lastActiveId": 1})
#     # print(activeprojectdetails)
#     project_id = activeprojectdetails["_id"]
#     project_name = activeprojectdetails["projectname"]
#     projectsharedwith = activeprojectdetails["sharedwith"]
#     # # print(activeprojectname)
#     lastActiveId = activeprojectdetails["lastActiveId"]

#     if (activeprojectdetails["projectType"] == 'text'):
#         text_data = projects.find_one({"projectname": activeprojectname}, \
#                             {"_id" : 0, "textData": 1 })
#     elif (activeprojectdetails["projectType"] == 'image'):
#             text_data = projects.find_one({"projectname": activeprojectname}, \
#                                 {"_id" : 0, "imageFiles": 1 }) 
#     for id in text_data.values():
#         tIds = list(id.keys())
#     tIds = sorted(tIds)
#     # print(tIds[0])                          
    
#     if (len(users[0]) != 0):
#         for user in users:
#             # get list of projects shared with the user
#             usershareprojectsname = userprojects.find_one({ 'username' : user })['projectsharedwithme']
#             myproject = userprojects.find_one({ 'username' : user })['myproject']
#             # print(myproject, usershareprojectsname)
#             if (activeprojectname in usershareprojectsname or \
#                 activeprojectname in myproject):
#                 # print("=====================================================================$%$%$%$%$%$%$%")
#                 continue
#             # update list of projects shared with the user
#             usershareprojectsname.append(activeprojectname)
#             usershareprojectsname = list(set(usershareprojectsname))
#             # update list of projects shared with the user in collection
#             userprojects.update_one({ 'username' : user }, { '$set' : { 'projectsharedwithme' : usershareprojectsname}})
#             # userprojectsname = userprojects.find_one({ 'username' : user })
#             # print(userprojectsname)

#             # update active project sharedwith list
#             projectsharedwith.append(user)
#             projectsharedwith = list(set(projectsharedwith))
#             lastActiveId[user] = tIds[0]
#             # print("WHYYYYYYYYYYYYYYYYYYYYYYYYY?????????????????????????????????????")

#     #     projectForm['username'] = current_user.username
#     # update projects collection
#     # activeprojectdetails["sharedwith"] = projectsharedwith
#         # flash(f"Project: {activeprojectname} is shared with {users}")
#     # print(lastActiveId)    
#     projects.update_one({ "_id" : project_id }, \
#         { '$set' : { "sharedwith": projectsharedwith, "lastActiveId": lastActiveId }})

#     # return "OK"
#     return jsonify(users=users)

def dummyUserandProject():

    """ Creates dummy user and project if the database has no collection """
    # print("Creates dummy user and project if the database has no collection")
    userprojects = mongo.db.userprojects                # collection of users and their projectlist and active project
    projects = mongo.db.projects                        # collection containing projects name
    if len(mongo.db.list_collection_names()) == 0:
        userprojects.insert_one({'username' : "dummyUser", 'myproject': ["dummyProject"], \
            'projectsharedwithme': [], 'activeprojectname' : "dummyProject"})

        
        project_details = {}
        project_details["projectType"] = "text"
        project_details["projectname"] = "dummyProject"
        project_details["projectOwner"] = "dummyUser"
        project_details["tagSet"] = {
                                        "category_1": "list of tags in that category",
                                        "category_2": "list of tags in that category"
                                    }
        textData = {
                        "text_id_1_system_generated" : 
                            {
                                "ID": "Actual ID of the comment in the file uploaded", 
                                "Text":"Actual comment"
                            },
                            "text_id_2_system_generated" : 
                            {
                                "ID": "Actual ID  of the comment in the file uploaded", 
                                "Text":"Actual comment"
                            }
                    }
        project_details["textData"] = textData
        project_details["lastActiveId"] = {"dummyUser": "text_id_1"}
        project_details["sharedwith"]  = ["dummyUser"]
        project_details["projectdeleteFLAG"] = 0
        project_details["isPublic"] = 0
        project_details["derivedFromProject"] = []
        project_details["projectDerivatives"] = []
        project_details["aboutproject"] = ''
        projects.insert_one(project_details)

def nextIdToAnnotate(projTIds, lastTId):
    for id in projTIds:
        tIds = list(id.keys())
    tIds = sorted(tIds)

    # print(lastTId)
    lastTIdIndex = tIds.index(lastTId)

    if (lastTIdIndex != len(tIds)-1):
        # print(lastTIdIndex)
        nextTIdIndex = lastTIdIndex+1
        # print(nextTIdIndex)
        nextTId = tIds[nextTIdIndex]
        # print(nextTId)
    else:
        nextTId = tIds[0]
        # print(nextTId)

    # print(nextTId)
    return nextTId

def previousIdToAnnotate(projTIds, lastTId):
    for id in projTIds:
        tIds = list(id.keys())
    tIds = sorted(tIds)

    # print(lastTId)
    lastTIdIndex = tIds.index(lastTId)

    if (lastTIdIndex != 0):
        # print(lastTIdIndex)
        previousTIdIndex = lastTIdIndex-1
        # print(previousTIdIndex)
        previousTId = tIds[previousTIdIndex]
        # print(previousTId)
    else:
        previousTId = tIds[len(tIds)-1]
        # print(previousTId)

    return previousTId

@easyAnno.route('/downloadannotationfile', methods=['GET', 'POST'])
def downloadannotationfile():
    # projects = mongo.db.projects              # collection of users and their respective projects
    # userprojects = mongo.db.userprojects              # collection of users and their respective projects
    # textanno = mongo.db.textanno
    # imageanno = mongo.db.imageanno
    # fs =  gridfs.GridFS(mongo.db)                       # creating GridFS instance to get required files
    
    projects, userprojects, textanno, imageanno = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'userprojects',
                                                                'textanno',
                                                                'imageanno')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
    project_type_list = ['text', 'image']
    currentuserprojectsname = getprojectsnamebytype.getprojectsnamebytype(projects,
                                                                            currentuserprojectsname,
                                                                            project_type_list)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)
    # currentuserprojectsname =  sorted(list(currentuserprojects()))
    # activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
    #                     {'_id' : 0, 'activeprojectname': 1})['activeprojectname']

    proj_detail = projects.find_one({'projectname': activeprojectname}, \
                    {"_id": 0, 'projectType': 1})

    # text_csv_columns = ['textId', 'ID', 'Text','Duplicate', 'annotatorComment']

    if (proj_detail["projectType"] == 'text'):
        proj_detail = projects.find_one({'projectname': activeprojectname}, \
                    {"_id": 0, 'tagSet': 1, 'textData': 1}) 
        text_data = proj_detail["textData"]
        tag_set = proj_detail["tagSet"]
        df_dict = {"textId": [], "ID": [], "Text": []}
        for category in list(tag_set.keys()):
            df_dict[category] = []
        df_dict["Duplicate"] = []
        df_dict["annotatorComment"] = []    
        # print(df)

        df = pd.DataFrame.from_dict(df_dict)
        # print(df)

        for text_id in list(text_data.keys()):
            annotated_text = textanno.find_one({ "textId": text_id },\
                        { "_id": 0, "ID": 1, "Text": 1, current_user.username: 1 })
            # print(annotated_text)
            if (annotated_text != None and current_user.username in annotated_text):
                annotated_text[current_user.username]["textId"] = text_id
                annotated_text[current_user.username]["ID"] = annotated_text["ID"]
                annotated_text[current_user.username]["Text"] = annotated_text["Text"]
                annotated_text =  annotated_text[current_user.username] 
                # print(annotated_text)
                annotated_text_df = pd.DataFrame.from_dict(annotated_text.items()).T
                annotated_text_df.columns = annotated_text_df.iloc[0]
                annotated_text_df = annotated_text_df[1:]
                # print(annotated_text_df, '\n')
                df = df.append(annotated_text_df, ignore_index=True)
            else:
                annotated_text = {}
                annotated_text["textId"] = text_id
                annotated_text["ID"]  = text_data[text_id]["ID"]
                annotated_text["Text"]  = text_data[text_id]["Text"]
                for category in list(tag_set.keys()):
                    annotated_text[category] = ''
                annotated_text["Duplicate"] = ''
                annotated_text["annotatorComment"] = ''
                # print(annotated_text)
                annotated_text_df = pd.DataFrame.from_dict(annotated_text.items()).T
                annotated_text_df.columns = annotated_text_df.iloc[0]
                annotated_text_df = annotated_text_df[1:]
                # print(annotated_text_df, '\n')
                df = df.append(annotated_text_df, ignore_index=True)
        # print(df.columns)
    elif (proj_detail["projectType"] == 'image'):
        proj_detail = projects.find_one({'projectname': activeprojectname}, \
                    {"_id": 0, 'tagSet': 1, 'imageFiles': 1}) 
        image_data = proj_detail["imageFiles"]
        tag_set = proj_detail["tagSet"]
        df_dict = {"imageId": [], "fileName": []}
        for category in list(tag_set.keys()):
            df_dict[category] = []
        df_dict["Duplicate"] = []
        df_dict["annotatorComment"] = []    
        # print(df)

        df = pd.DataFrame.from_dict(df_dict)
        # print(df)

        for image_id in list(image_data.keys()):
            annotated_image = imageanno.find_one({ "imageId": image_id },\
                        { "_id": 0, "filename": 1, current_user.username: 1 })
            # print(annotated_image)
            if (annotated_image != None and current_user.username in annotated_image):
                annotated_image[current_user.username]["imageId"] = image_id
                annotated_image[current_user.username]["fileName"] = annotated_image["filename"]
                annotated_image =  annotated_image[current_user.username] 
                # print(annotated_image)
                annotated_image_df = pd.DataFrame.from_dict(annotated_image.items()).T
                annotated_image_df.columns = annotated_image_df.iloc[0]
                annotated_image_df = annotated_image_df[1:]
                # print(annotated_image_df, '\n')
                df = df.append(annotated_image_df, ignore_index=True)
            else:
                annotated_image = {}
                annotated_image["imageId"] = image_id
                annotated_image["fileName"]  = image_data[image_id]
                for category in list(tag_set.keys()):
                    annotated_image[category] = ''
                annotated_image["Duplicate"] = ''
                annotated_image["annotatorComment"] = ''
                # print(annotated_image)
                annotated_image_df = pd.DataFrame.from_dict(annotated_image.items()).T
                annotated_image_df.columns = annotated_image_df.iloc[0]
                annotated_image_df = annotated_image_df[1:]
                # print(annotated_image_df, '\n')
                df = df.append(annotated_image_df, ignore_index=True)
        # print(df.columns)
            # # retrieve images from the database
            # imageFile = fetch_image_files(image_id)
            # filename = imageFile["filename"]
            # imageBytes = imageFile["imageBytes"]
            # open(basedir+'/download/'+filename, 'wb').write(imageBytes)
    
    annotated_file_path = basedir+'/download/'
    df.to_csv(annotated_file_path+activeprojectname+'.csv', sep='\t', index=False)

    files = glob.glob(basedir+'/download/*')
     
    with ZipFile('download.zip', 'w') as zip:
        # writing each file one by one 
        for file in files: 
            # zip.write(file, os.path.join(activeprojectname, os.path.basename(file)))
            zip.write(file, os.path.basename(file))
    print('All files zipped successfully!')

    # deleting all files from storage
    for f in files:
        # print(f)
        os.remove(f)
    
    return send_file('../download.zip', as_attachment=True)

@easyAnno.route('/allunannotated', methods=['GET', 'POST'])
def allunannotated():
    '''
    get list of all annotated and all unannotated data by that user for that file
    '''
    projects = mongo.db.projects              # collection of users and their respective projects
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    textanno = mongo.db.textanno
    imageanno = mongo.db.imageanno

    activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
                    {'_id' : 0, 'activeprojectname': 1})['activeprojectname']

    allunanno = []
    # list of all annotated
    allanno = []

    project_type = projects.find_one({"projectname": activeprojectname}, \
                    {"_id": 0, "projectType": 1})["projectType"]

    if (project_type =='text'):
        for unannodata in textanno.find({"projectname": activeprojectname}, \
                        {"_id": 0, "textId":1, "ID": 1, current_user.username: 1}):

            # print(unannodata)
            if (current_user.username not in unannodata):
                allunanno.append(unannodata)
            elif (current_user.username in unannodata and\
                    unannodata[current_user.username]["annotatedFLAG"] == 0):
                unannodata.pop(current_user.username)
                allunanno.append(unannodata)
            elif (current_user.username in unannodata and\
                    unannodata[current_user.username]["annotatedFLAG"] == 1):
                unannodata.pop(current_user.username)
                allanno.append(unannodata)

    elif (project_type =='image'):
        for unannodata in imageanno.find({"projectname": activeprojectname}, \
                        {"_id": 0, "imageId":1, "filename": 1, current_user.username: 1}):

            # print(unannodata)
            if (current_user.username not in unannodata):
                allunanno.append(unannodata)
            elif (current_user.username in unannodata and\
                    unannodata[current_user.username]["annotatedFLAG"] == 0):
                unannodata.pop(current_user.username)
                allunanno.append(unannodata)
            elif (current_user.username in unannodata and\
                    unannodata[current_user.username]["annotatedFLAG"] == 1):
                unannodata.pop(current_user.username)
                allanno.append(unannodata)            

    # print(allunanno[:10])
    # print(allanno[:10])     

    return jsonify(allunanno=allunanno, allanno=allanno)

def project_comments_stats(userprojectslist):
    projects = mongo.db.projects
    textanno = mongo.db.textanno
    imageanno = mongo.db.imageanno

    # print(userprojectslist)
    total_comments = 1
    remaining_comments = 1
    annotated_comments = 1
    project_completion_color = {}
    color_count = {}

    for projectname in userprojectslist:
        project_type = projects.find_one({"projectname": projectname},
                                            {"_id": 0, "projectType": 1})
        if (len(project_type) != 0):
            project_type = project_type["projectType"]
        else:
            continue
        if (project_type =='text'):
            project_details = projects.find_one({"projectname": projectname}, \
                    {"_id": 0, "textData": 1})
            # print(project_details)
            total_comments = len(project_details["textData"])
            annotated_comments = 0
            for comments in textanno.find({"projectname": projectname}, \
                                            {"projectname": 1, current_user.username: 1 }):
                if (current_user.username in comments):                            
                    annotatedFLAG = comments[current_user.username]["annotatedFLAG"]
                    if (annotatedFLAG == 1):
                        annotated_comments += 1
            remaining_comments = total_comments - annotated_comments
        elif (project_type =='image'):
            if (projectname == "ComMA_MEMES_1"): continue
            project_details = projects.find_one({"projectname": projectname}, \
                    {"_id": 0, "imageFiles": 1})
                # print(project_details)
            total_comments = len(project_details["imageFiles"])
            annotated_comments = 0
            for comments in imageanno.find({"projectname": projectname}, \
                                            {"projectname": 1, current_user.username: 1 }):
                if (current_user.username in comments):                            
                    annotatedFLAG = comments[current_user.username]["annotatedFLAG"]
                    if (annotatedFLAG == 1):
                        annotated_comments += 1
            remaining_comments = total_comments - annotated_comments

        # print(f'{projectname}, {total_comments}, {annotated_comments}, {remaining_comments}')
        # print(f'Remaining comments percentage: {ceil(remaining_comments/total_comments*100)}')  

        if (ceil(remaining_comments/total_comments*100) == 0):
            project_completion_color[projectname] = 'success'
        elif (ceil(remaining_comments/total_comments*100) == 100):
            project_completion_color[projectname] = 'danger'
        else:
            project_completion_color[projectname] = 'warning'
    
    # save file count of each color type to show in home UI
    for colorname in project_completion_color.values():
        color_count[colorname] = color_count.get(colorname, 0) + 1
        # print(color_count)

    project_completion_color.update(color_count)

    # pprint(project_completion_color)
    

    return project_completion_color    

# download all annotation files of current user
@easyAnno.route('/downloadallannotationfiles', methods=['GET', 'POST'])
def downloadallannotationfiles():
    projects = mongo.db.projects              # collection of users and their respective projects
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    textanno = mongo.db.textanno
    imageanno = mongo.db.imageanno
    fs =  gridfs.GridFS(mongo.db)                       # creating GridFS instance to get required files
    
    proj_count = 0

    projects_detail = projects.find({}, \
                    {"_id": 0, "projectname": 1, "projectType": 1, "sharedwith": 1, \
                        'tagSet': 1, 'textData': 1, 'imageFiles': 1})

    for proj_detail in projects_detail:
        projectname = proj_detail["projectname"]
        # print(projectname, proj_detail["sharedwith"], current_user.username, current_user.username in proj_detail["sharedwith"])

        if current_user.username in proj_detail["sharedwith"]:
            # print(proj_count)  
            # print(proj_detail["projectType"])
            proj_count += 1
            # print(proj_count, projectname)

            if (proj_detail["projectType"] == 'text'):
                text_data = proj_detail["textData"]
                tag_set = proj_detail["tagSet"]
                df_dict = {"textId": [], "ID": [], "Text": []}
                for category in list(tag_set.keys()):
                    df_dict[category] = []
                df_dict["Duplicate"] = []
                df_dict["annotatorComment"] = []    
                # print(df)

                df = pd.DataFrame.from_dict(df_dict)
                # print(df)

                for text_id in list(text_data.keys()):
                    annotated_text = textanno.find_one({ "textId": text_id },\
                                { "_id": 0, "ID": 1, "Text": 1, current_user.username: 1 })
                    # print(annotated_text)
                    if (annotated_text != None and current_user.username in annotated_text):
                        annotated_text[current_user.username]["textId"] = text_id
                        annotated_text[current_user.username]["ID"] = annotated_text["ID"]
                        annotated_text[current_user.username]["Text"] = annotated_text["Text"]
                        annotated_text =  annotated_text[current_user.username] 
                        # print(annotated_text)
                        annotated_text_df = pd.DataFrame.from_dict(annotated_text.items()).T
                        annotated_text_df.columns = annotated_text_df.iloc[0]
                        annotated_text_df = annotated_text_df[1:]
                        # print(annotated_text_df, '\n')
                        df = df.append(annotated_text_df, ignore_index=True)
                    else:
                        annotated_text = {}
                        annotated_text["textId"] = text_id
                        annotated_text["ID"]  = text_data[text_id]["ID"]
                        annotated_text["Text"]  = text_data[text_id]["Text"]
                        for category in list(tag_set.keys()):
                            annotated_text[category] = ''
                        annotated_text["Duplicate"] = ''
                        annotated_text["annotatorComment"] = ''
                        # print(annotated_text)
                        annotated_text_df = pd.DataFrame.from_dict(annotated_text.items()).T
                        annotated_text_df.columns = annotated_text_df.iloc[0]
                        annotated_text_df = annotated_text_df[1:]
                        # print(annotated_text_df, '\n')
                        df = df.append(annotated_text_df, ignore_index=True)
                # print(df.columns)
            elif (proj_detail["projectType"] == 'image'):
                image_data = proj_detail["imageFiles"]
                tag_set = proj_detail["tagSet"]
                df_dict = {"imageId": [], "fileName": []}
                for category in list(tag_set.keys()):
                    df_dict[category] = []
                df_dict["Duplicate"] = []
                df_dict["annotatorComment"] = []    
                # print(df)

                df = pd.DataFrame.from_dict(df_dict)
                # print(df)

                for image_id in list(image_data.keys()):
                    annotated_image = imageanno.find_one({ "imageId": image_id },\
                                { "_id": 0, "filename": 1, current_user.username: 1 })
                    # print(annotated_image)
                    if (annotated_image != None and current_user.username in annotated_image):
                        annotated_image[current_user.username]["imageId"] = image_id
                        annotated_image[current_user.username]["fileName"] = annotated_image["filename"]
                        annotated_image =  annotated_image[current_user.username] 
                        # print(annotated_image)
                        annotated_image_df = pd.DataFrame.from_dict(annotated_image.items()).T
                        annotated_image_df.columns = annotated_image_df.iloc[0]
                        annotated_image_df = annotated_image_df[1:]
                        # print(annotated_image_df, '\n')
                        df = df.append(annotated_image_df, ignore_index=True)
                    else:
                        annotated_image = {}
                        annotated_image["imageId"] = image_id
                        annotated_image["fileName"]  = image_data[image_id]
                        for category in list(tag_set.keys()):
                            annotated_image[category] = ''
                        annotated_image["Duplicate"] = ''
                        annotated_image["annotatorComment"] = ''
                        # print(annotated_image)
                        annotated_image_df = pd.DataFrame.from_dict(annotated_image.items()).T
                        annotated_image_df.columns = annotated_image_df.iloc[0]
                        annotated_image_df = annotated_image_df[1:]
                        # print(annotated_image_df, '\n')
                        df = df.append(annotated_image_df, ignore_index=True)
                # print(df.columns)
                    # # retrieve images from the database
                    # imageFile = fetch_image_files(image_id)
                    # filename = imageFile["filename"]
                    # imageBytes = imageFile["imageBytes"]
                    # open(basedir+'/download/'+filename, 'wb').write(imageBytes)
            
            annotated_file_path = basedir+'/download/'
            df.to_csv(annotated_file_path+projectname+'.csv', sep='\t', index=False)

    files = glob.glob(basedir+'/download/*')
     
    with ZipFile('download.zip', 'w') as zip:
        # writing each file one by one 
        for file in sorted(files): 
            # zip.write(file, os.path.join(activeprojectname, os.path.basename(file)))
            zip.write(file, os.path.basename(file))
    print('All files zipped successfully!')

    # deleting all files from storage
    for f in files:
        # print(f)
        os.remove(f)
    
    return send_file('../download.zip', as_attachment=True)

# download all annotation files of all users
@easyAnno.route('/downloadallusersallannotationfiles', methods=['GET', 'POST'])
def downloadallusersallannotationfiles():
    projects = mongo.db.projects              # collection of users and their respective projects
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    textanno = mongo.db.textanno
    imageanno = mongo.db.imageanno
    fs =  gridfs.GridFS(mongo.db)                       # creating GridFS instance to get required files

    if (current_user.username == 'ritesh' or current_user.username == 'siddharth'):            

        proj_count = 0

        projects_detail = projects.find({}, \
                        {"_id": 0, "projectname": 1, "projectType": 1, "sharedwith": 1, \
                            'tagSet': 1, 'textData': 1, 'imageFiles': 1})

        for proj_detail in projects_detail:
            # print(proj_detail["projectType"])
            projectname = proj_detail["projectname"]
            # print(projectname, proj_detail["sharedwith"])

            for username in proj_detail["sharedwith"]:
                # print(proj_count)  
                # print(proj_detail["projectType"])
                proj_count += 1
                # print(proj_count, projectname, username)

                if (projectname == 'dummyProject'): 
                    # print("dummyyyyyyy")
                    continue

                elif (proj_detail["projectType"] == 'text'):
                    text_data = proj_detail["textData"]
                    tag_set = proj_detail["tagSet"]
                    df_dict = {"textId": [], "ID": [], "Text": []}
                    for category in list(tag_set.keys()):
                        df_dict[category] = []
                    df_dict["Duplicate"] = []
                    df_dict["annotatorComment"] = []    
                    # print(df)

                    df = pd.DataFrame.from_dict(df_dict)
                    # print(df)

                    for text_id in list(text_data.keys()):
                        annotated_text = textanno.find_one({ "textId": text_id },\
                                    { "_id": 0, "ID": 1, "Text": 1, username: 1 })
                        # print(annotated_text)
                        if (annotated_text != None and username in annotated_text):
                            annotated_text[username]["textId"] = text_id
                            annotated_text[username]["ID"] = annotated_text["ID"]
                            annotated_text[username]["Text"] = annotated_text["Text"]
                            annotated_text =  annotated_text[username] 
                            # print(annotated_text)
                            annotated_text_df = pd.DataFrame.from_dict(annotated_text.items()).T
                            annotated_text_df.columns = annotated_text_df.iloc[0]
                            annotated_text_df = annotated_text_df[1:]
                            # print(annotated_text_df, '\n')
                            df = df.append(annotated_text_df, ignore_index=True)
                        else:
                            annotated_text = {}
                            annotated_text["textId"] = text_id
                            annotated_text["ID"]  = text_data[text_id]["ID"]
                            annotated_text["Text"]  = text_data[text_id]["Text"]
                            for category in list(tag_set.keys()):
                                annotated_text[category] = ''
                            annotated_text["Duplicate"] = ''
                            annotated_text["annotatorComment"] = ''
                            # print(annotated_text)
                            annotated_text_df = pd.DataFrame.from_dict(annotated_text.items()).T
                            annotated_text_df.columns = annotated_text_df.iloc[0]
                            annotated_text_df = annotated_text_df[1:]
                            # print(annotated_text_df, '\n')
                            df = df.append(annotated_text_df, ignore_index=True)
                    # print(df.columns)
                elif (proj_detail["projectType"] == 'image'):
                    image_data = proj_detail["imageFiles"]
                    tag_set = proj_detail["tagSet"]
                    df_dict = {"imageId": [], "fileName": []}
                    for category in list(tag_set.keys()):
                        df_dict[category] = []
                    df_dict["Duplicate"] = []
                    df_dict["annotatorComment"] = []    
                    # print(df)

                    df = pd.DataFrame.from_dict(df_dict)
                    # print(df)

                    for image_id in list(image_data.keys()):
                        annotated_image = imageanno.find_one({ "imageId": image_id },\
                                    { "_id": 0, "filename": 1, username: 1 })
                        # print(annotated_image)
                        if (annotated_image != None and username in annotated_image):
                            annotated_image[username]["imageId"] = image_id
                            annotated_image[username]["fileName"] = annotated_image["filename"]
                            annotated_image =  annotated_image[username] 
                            # print(annotated_image)
                            annotated_image_df = pd.DataFrame.from_dict(annotated_image.items()).T
                            annotated_image_df.columns = annotated_image_df.iloc[0]
                            annotated_image_df = annotated_image_df[1:]
                            # print(annotated_image_df, '\n')
                            df = df.append(annotated_image_df, ignore_index=True)
                        else:
                            annotated_image = {}
                            annotated_image["imageId"] = image_id
                            annotated_image["fileName"]  = image_data[image_id]
                            for category in list(tag_set.keys()):
                                annotated_image[category] = ''
                            annotated_image["Duplicate"] = ''
                            annotated_image["annotatorComment"] = ''
                            # print(annotated_image)
                            annotated_image_df = pd.DataFrame.from_dict(annotated_image.items()).T
                            annotated_image_df.columns = annotated_image_df.iloc[0]
                            annotated_image_df = annotated_image_df[1:]
                            # print(annotated_image_df, '\n')
                            df = df.append(annotated_image_df, ignore_index=True)
                    # print(df.columns)
                        # # retrieve images from the database
                        # imageFile = fetch_image_files(image_id)
                        # filename = imageFile["filename"]
                        # imageBytes = imageFile["imageBytes"]
                        # open(basedir+'/download/'+filename, 'wb').write(imageBytes)
                
                annotated_file_path = basedir+'/download/'
                df.to_csv(annotated_file_path+projectname+'_'+username+'.csv', sep='\t', index=False)

        files = glob.glob(basedir+'/download/*')
        
        with ZipFile('download.zip', 'w') as zip:
            # writing each file one by one 
            for file in sorted(files):
                # print(file)
                # zip.write(file, os.path.join(activeprojectname, os.path.basename(file)))
                zip.write(file, os.path.basename(file))
        print('All files zipped successfully!')

        # deleting all files from storage
        for f in files:
            # print(f)
            os.remove(f)
        
        return send_file('../download.zip', as_attachment=True)

    else:
        print('You are not ritesh or siddharth :(', current_user.username)
        return redirect(url_for('easyAnno.home'))


@easyAnno.route('/downloadoneuserallannotatedfiles/<username>')
def downloadoneuserallannotatedfiles(username):
    if (current_user.username == 'ritesh' or current_user.username == 'ComMA' or current_user.username == 'siddharth'):
        log = ''
        log += f"{username}\n"
        projects = mongo.db.projects              # collection of users and their respective projects
    
        proj_count = 0

        projects_detail = projects.find({}, \
                        {"_id": 0, "projectname": 1, "projectType": 1, "sharedwith": 1, \
                            'tagSet': 1, 'textData': 1, 'imageFiles': 1})

        for proj_detail in projects_detail:
            projectname = proj_detail["projectname"]
            log += f"{'-'*80}\n"
            log += f'Project Name: {projectname}, Shared With: {str(proj_detail["sharedwith"])},  Shared with {username}: {str(username in proj_detail["sharedwith"])}\n'
            # print(os.listdir('download'))
            if projectname+'.csv' in os.listdir(basedir+'/download'): 
                log += f'Already downloaded :)\n'
                continue
            
            if username in proj_detail["sharedwith"]:
                # print(proj_count) 
                project_type = proj_detail["projectType"]
                log += f'{proj_detail["projectType"]}\n'
                proj_count += 1
                log += f'{str(proj_count)}. {projectname}\n'
                
                if (proj_detail["projectType"] == 'text'):
                    text_data = proj_detail["textData"]
                    tag_set = proj_detail["tagSet"]
                    df_dict = {"textId": [], "ID": [], "Text": []}
                    for category in list(tag_set.keys()):
                        df_dict[category] = []
                    df_dict["Duplicate"] = []
                    df_dict["annotatorComment"] = []    
                    # print(df)

                    df = pd.DataFrame.from_dict(df_dict)
                    # print(df)
                    total_comments = len(text_data)
                    annotated_comments = 0
                    for annotated_text in get_file_data(mongo.db, projectname, project_type, username):
                        # pprint(annotated_text)
                        if (annotated_text != None and username in annotated_text):
                            annotated_text[username]["textId"] = annotated_text["textId"]
                            annotated_text[username]["ID"] = annotated_text["ID"]
                            annotated_text[username]["Text"] = annotated_text["Text"] 
                            # get annotated comments count
                            annotatedFLAG = annotated_text[username]["annotatedFLAG"]
                            if (annotatedFLAG == 1):
                                annotated_comments += 1
                            annotated_text =  annotated_text[username]    
                        else:
                            for category in list(tag_set.keys()):
                                annotated_text[category] = ''
                            annotated_text["Duplicate"] = ''
                            annotated_text["annotatorComment"] = ''
                        # print(annotated_text)
                        annotated_text_df = pd.DataFrame.from_dict(annotated_text.items()).T
                        annotated_text_df.columns = annotated_text_df.iloc[0]
                        annotated_text_df = annotated_text_df[1:]
                        # print(annotated_text_df, '\n')
                        df = df.append(annotated_text_df, ignore_index=True)
                    # print(df.columns)
                    remaining_comments = total_comments - annotated_comments
                elif (proj_detail["projectType"] == 'image'):
                    # continue
                    image_data = proj_detail["imageFiles"]
                    tag_set = proj_detail["tagSet"]
                    df_dict = {"imageId": [], "fileName": []}
                    for category in list(tag_set.keys()):
                        df_dict[category] = []
                    df_dict["Duplicate"] = []
                    df_dict["annotatorComment"] = []    
                    # print(df)

                    df = pd.DataFrame.from_dict(df_dict)
                    # print(df)
                    total_comments = len(image_data)
                    annotated_comments = 0
                    for annotated_image in get_file_data(mongo.db, projectname, project_type, username):
                        if (annotated_image != None and username in annotated_image):
                            annotated_image[username]["imageId"] = annotated_image["imageId"]
                            annotated_image[username]["fileName"] = annotated_image["filename"]
                            # get annotated comments count
                            annotatedFLAG = annotated_image[username]["annotatedFLAG"]
                            if (annotatedFLAG == 1):
                                annotated_comments += 1
                            annotated_image =  annotated_image[username] 
                        else:
                            for category in list(tag_set.keys()):
                                annotated_image[category] = ''
                            annotated_image["Duplicate"] = ''
                            annotated_image["annotatorComment"] = ''
                        # print(annotated_image)
                        annotated_image_df = pd.DataFrame.from_dict(annotated_image.items()).T
                        annotated_image_df.columns = annotated_image_df.iloc[0]
                        annotated_image_df = annotated_image_df[1:]
                        # print(annotated_image_df, '\n')
                        df = df.append(annotated_image_df, ignore_index=True)
                    # print(df.columns)
                        # # retrieve images from the database
                        # imageFile = fetch_image_files(image_id)
                        # filename = imageFile["filename"]
                        # imageBytes = imageFile["imageBytes"]
                        # open(basedir+'/download/'+filename, 'wb').write(imageBytes)
                    remaining_comments = total_comments - annotated_comments

                annotated_file_path = basedir+'/download/'
                log += f'Total Comments: {total_comments}\nAnnotated Comments: {annotated_comments}\nRemaining Comments: {remaining_comments}\n'
                if (remaining_comments == 0):
                    df.to_csv(annotated_file_path+projectname+'.csv', sep='\t', index=False)

        with open(basedir+'/download/log.txt', 'w') as logFile:
            logFile.write(log)

        files = glob.glob(basedir+'/download/*')
        
        if (os.path.exists('download.zip')):
            os.remove('download.zip')

        with ZipFile('download.zip', 'w') as zip:
            # writing each file one by one 
            for file in sorted(files): 
                # zip.write(file, os.path.join(activeprojectname, os.path.basename(file)))
                zip.write(file, os.path.basename(file))
        print('All files zipped successfully!')

        # deleting all files from storage
        for f in files:
            # print(f)
            os.remove(f)
        
        return send_file('../download.zip', as_attachment=True)
    else:
        print('You are not ritesh or ComMA :(', current_user.username)
        return redirect(url_for('easyAnno.home'))

def get_file_data(db, file_name, file_type, username):
    '''
    get all the text and their detail present in the file
    '''
    # print(f'Getting all the text and their detail present in the file...\n{"="*80}')

    if (file_type == 'text'):
        textanno = db.textanno
        file_detail = textanno.find({ "projectname": file_name },\
                        { "_id": 0, "textId": 1, "ID": 1, "Text": 1, username: 1 })

    elif (file_type == 'image'):
        imageanno = db.imageanno
        file_detail = imageanno.find({ "projectname": file_name },\
                        { "_id": 0, "imageId": 1, "filename": 1, username: 1 })

    return file_detail

@easyAnno.route('/browse', methods=['GET', 'POST'])
@login_required
def browse():
    return redirect(url_for('easyAnno.home'))

@easyAnno.route('/multimediaAnno', methods=['GET', 'POST'])
@login_required
def multimediaAnno():
    return redirect(url_for('easyAnno.home'))

def createTextAnnoNew(zipFile):
    # projects = mongo.db.projects              # collection of users and their respective projects
    # userprojects = mongo.db.userprojects              # collection of users and their respective projects
    # textanno = mongo.db.textanno
    
    # currentuserprojectsname =  sorted(list(currentuserprojects()))
    # activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
    #                 {'_id' : 0, 'activeprojectname': 1})['activeprojectname']

    projects, userprojects, textanno = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'userprojects',
                                                                'textanno')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
    project_type_list = ['text', 'image']
    currentuserprojectsname = getprojectsnamebytype.getprojectsnamebytype(projects,
                                                                            currentuserprojectsname,
                                                                            project_type_list)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)

    # print(type(zipFile))
    # print(zipFile)
    tag_set = {}
    tag_set_meta_data = {}
    categoryDependency = {}
    defaultCategoryTags = {}
    categoryHtmlElement = {}
    categoryHtmlElementProperties = {}
    try:
        with ZipFile(zipFile) as myzip:
            with myzip.open('textAnno_tags.tsv') as myfile:
                
                # print('textAnno_tags.tsv')
                # tags_df = pd.read_csv(io.BytesIO(myfile.read()), sep='\t', dtype=str).dropna()
                tags_df = pd.read_csv(io.BytesIO(myfile.read()), sep='\t', dtype=str)

                # version 1
                # # print(type(tags))
                # print(tags_df)
                # for i in range(len(tags_df)):
                #     tag_set[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 1]).split(',')

                # version 2
                if (len(tags_df.columns) == 2):
                    for i in range(len(tags_df)):
                        tag_set[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 1]).split(',')
                elif (len(tags_df.columns) == 3):
                    for i in range(len(tags_df)):
                        tag_set[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 1]).split(',')
                        defaultCategoryTags[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 2]).split(',')[0]
                    tag_set_meta_data['defaultCategoryTags'] = defaultCategoryTags
                elif (len(tags_df.columns) == 4):
                    for i in range(len(tags_df)):
                        tag_set[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 1]).split(',')
                        if (re.sub(' ', '', tags_df.iloc[i, 3]).split(',')[0] != 'NONE'):
                            categoryDependency[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 3]).split(',')[0]
                        defaultCategoryTags[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 2]).split(',')[0]
                    tag_set_meta_data['categoryDependency'] = categoryDependency
                    tag_set_meta_data['defaultCategoryTags'] = defaultCategoryTags
                    # tag_set_meta_data['categoryFormType'] = defaultCategoryTags
                elif (len(tags_df.columns) == 6):
                    for i in range(len(tags_df)):
                        print(tags_df.iloc[i, 0], tags_df.iloc[i, 1], type(tags_df.iloc[i, 1]))
                        if (str(tags_df.iloc[i, 1]) == 'nan'):
                            tag_set[tags_df.iloc[i, 0]] = ['']
                        else:
                            tag_set[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 1]).split(',')
                        if (re.sub(' ', '', tags_df.iloc[i, 3]).split(',')[0] != 'NONE'):
                            categoryDependency[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 3]).split(',')[0]
                        if (str(tags_df.iloc[i, 2]) == 'nan'):
                            defaultCategoryTags[tags_df.iloc[i, 0]] = ''
                        elif (str(tags_df.iloc[i, 4]) == 'select'):
                            defaultCategoryTags[tags_df.iloc[i, 0]] = [re.sub(' ', '', tags_df.iloc[i, 2]).split(',')[0]]
                        else:
                            defaultCategoryTags[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 2]).split(',')[0]
                        categoryHtmlElement[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 4]).split(',')[0]
                        categoryHtmlElementProperties[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 5]).split(',')[0]
                    tag_set_meta_data['categoryDependency'] = categoryDependency
                    tag_set_meta_data['defaultCategoryTags'] = defaultCategoryTags
                    tag_set_meta_data['categoryHtmlElement'] = categoryHtmlElement
                    tag_set_meta_data['categoryHtmlElementProperties'] = categoryHtmlElementProperties
                # pprint(tag_set)
                # pprint(tag_set_meta_data)
                with open('app/jsonfiles/tagSet.json', 'w') as writejson:
                    jsondata = json.dumps(tag_set, indent=2, ensure_ascii=False)
                    writejson.write(jsondata)
                with open('app/jsonfiles/tagSetMetaData.json', 'w') as writejson:
                    jsondata = json.dumps(tag_set_meta_data, indent=2, ensure_ascii=False)
                    writejson.write(jsondata)
# commented from here
            existing_projects = []
            for file_name in myzip.namelist():
                project_name = file_name.split('.')[0]
                if projects.find_one({"projectname": project_name}, {'_id' : 0, "projectname": 1}) != None:
                    existing_projects.append(project_name)
            if (len(existing_projects) > 0):
                flash(f'File Name : {", ".join(existing_projects)} already exist!', 'warning')
                return redirect(url_for('easyAnno.home'))

            for file_name in myzip.namelist():    
                # print(tag_set)
                text_data = {}
                text_data_df = ''
                id_test_list = []
                with myzip.open(file_name) as myfile:
                    # print(myfile.read())
                    if (not file_name.endswith('.tsv')):
                        # print(file_name)
                        project_name = file_name.split('.')[0]

                        if projects.find_one({"projectname": project_name}, {'_id' : 0, "projectname": 1}) != None:
                            flash(f'File Name : {project_name} already exist!', 'warning')
                            return redirect(url_for('easyAnno.home'))

                        text_data_df = pd.read_csv(io.BytesIO(myfile.read()), sep='\t', dtype=str)
                        df_header = list(text_data_df.columns)
                        if ('ID' not in df_header):
                            # print(df_header)
                            flash(f'File Name : {project_name} do not have "ID" as column header', 'warning')
                            return redirect(url_for('easyAnno.home'))
                        if ('Text' not in df_header):
                            # print(df_header)
                            flash(f'File Name : {project_name} do not have "Text" as column header', 'warning')
                            return redirect(url_for('easyAnno.home'))    

                        if(text_data_df["ID"].isnull().any()):
                            flash(f'File Name : {project_name}  have empty cell in "ID" column', 'warning')
                            return redirect(url_for('easyAnno.home'))

                        # print(text_data_df.head())
                        # print('text_data_df - COLUMNS', text_data_df.columns, list(text_data_df.columns))
                        for i in range(len(text_data_df)): 
                            text_id = 'T'+re.sub(r'[-: \.]', '', str(datetime.now()))
                            id_test_list.append(text_id)
                            single_row = {}
                            single_row["ID"] = text_data_df.iloc[i, 0]
                            single_row["Text"] = text_data_df.iloc[i, 1]
                            text_data_df_col_list = list(text_data_df.columns)
                            for col_name in text_data_df_col_list:
                                if (col_name == 'ID' or col_name == 'Text'): continue
                                else:
                                    col_name_index = text_data_df_col_list.index(col_name)
                                    # print(col_name, text_data_df_col_list.index(col_name))
                                    single_row[col_name] = text_data_df.iloc[i, col_name_index]
                            text_data[text_id] = single_row
                            # entry of each text in textanno colloection
                            text_anno_detail = {}
                            text_anno_detail["projectname"] = project_name
                            text_anno_detail["textId"] = text_id
                            text_anno_detail["ID"] = text_data_df.iloc[i, 0]
                            text_anno_detail["Text"] = text_data_df.iloc[i, 1]
                            text_anno_detail['lastUpdatedBy'] = ""
                            all_access = {}
                            text_anno_detail['allAccess'] = all_access
                            all_updates = {}
                            text_anno_detail['allUpdates'] = all_updates

                            textanno.insert_one(text_anno_detail)
                        
                    else:
                        continue


                project_owner = current_user.username
                project_details = {}
                # print(text_data.keys())
                lastActiveId = {current_user.username: list(text_data.keys())[0]}
                project_details["projectType"] = "text"
                project_details["projectname"] = project_name
                project_details["projectOwner"] = project_owner
                project_details["tagSet"] = tag_set
                project_details["tagSetMetaData"] = tag_set_meta_data
                project_details["textData"] = text_data
                project_details["lastActiveId"] = lastActiveId
                project_details["sharedwith"]  = [project_owner]
                project_details["projectdeleteFLAG"] = 0
                project_details["isPublic"] = 0
                project_details["derivedFromProject"] = []
                project_details["projectDerivatives"] = []
                project_details["aboutproject"] = ''

                projects.insert_one(project_details)
                projectname = project_details['projectname']
                updateuserprojects.updateuserprojects(userprojects,
                                                projectname,
                                                current_username
                                                )

                # print(project_details)
                # print(project_details["textData"])
    except Exception as e:
        print(e)
        flash('Please upload a zip file. Check the file format at the link provided for the Sample File', 'warning')

        return redirect(url_for('easyAnno.home'))

    flash('File created successfully :)', 'success')
# commented till here
    # return render_template('home.html',  data=currentuserprojectsname, activeproject=activeprojectname)
    return redirect(url_for('easyAnno.home'))

@easyAnno.route('/getIdList', methods=['GET', 'POST'])
def getIdList():
    '''
    get list of all Ids
    '''
    projects, userprojects = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)

    allIds = []
    project_info = projects.find_one({'projectname': activeprojectname}, {"_id": 0, "textData": 1})
    textData = project_info['textData']
    for value in textData.values():
        Id = value['ID']
        allIds.append(Id)

    # print(allIds)
    return jsonify(allIds=allIds)
