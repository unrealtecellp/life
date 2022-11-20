# home page route
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    projects = mongo.db.projects              # collection of users and their respective projects
    userprojects = mongo.db.userprojects              # collection of users and their respective projects

    currentuserprojectsname =  sorted(list(currentuserprojects()))
    activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
                    {'_id' : 0, 'activeproject': 1})['activeproject']
    # print(currentuserprojectsname, activeprojectname)
    projectcompleted = project_comments_stats(currentuserprojectsname)

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
                createTextAnno(zipFile)
        elif (file_type == 'image'):
            createImageAnno(zipFile, image_file_name)    

    # return render_template('home.html')
    # print(len(currentuserprojectsname))
    return render_template('home.html',  data=currentuserprojectsname, activeproject=activeprojectname, projectcompleted=projectcompleted)
    
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
                        print(file_name)
                        project_name = file_name.split('.')[0]

                        # check project/file name do not already exist
                        if projects.find_one({"projectName": project_name}, {'_id' : 0, "projectName": 1}) != None:
                            # check if file already exist then current user hasnt yet annotated any text/comment
                            if userAlreadyAnnotated(project_name):
                                return redirect(url_for('home'))

                            # check if tag_set is empty
                            if bool(tag_set):
                                # check if tagset given by user and one saved with the project details match or not
                                if compareTagSet(project_name, tag_set):
                                    return redirect(url_for('home'))

                            text_data_df = pd.read_csv(io.BytesIO(myfile.read()), sep='\t', dtype=str)

                            # check if any row in ID column is empty
                            if checkEmptyRowInID(text_data_df, project_name):
                                return redirect(url_for('home'))

                            # check categories in the columns of the file and the tagset tsv file match or not
                            if compareTagSetandFileColumn(text_data_df, tag_set, project_name):
                                return redirect(url_for('home'))

                            # check the IDs in the uploaded file and the existing file match or not
                            if checkTextIds(project_name, text_data_df):
                                return redirect(url_for('home'))
                            
                            
                            # when project/filename exist and all checks are passed
                            updateAnnotatedData(project_name, text_data_df)
                            updateProjectDetails(project_name, current_user.username)

                        else:
                            # when project/file name do not exist in the database
                            text_data_df = pd.read_csv(io.BytesIO(myfile.read()), sep='\t', dtype=str)
                            # print(text_data_df.head())
                            # check if any row in ID column is empty
                            if checkEmptyRowInID(text_data_df, project_name):
                                return redirect(url_for('home'))
                            if compareTagSetandFileColumn(text_data_df, tag_set, project_name):
                                return redirect(url_for('home'))
                            text_data = saveAnnotatedData(project_name, text_data_df)
                            saveNewProjectDetails(project_name, tag_set, text_data, tag_set_meta_data)
        
    except:
        # flash('Please check the imageAnno_tags.tsv file format!')
        flash('Please upload a zip file. Check the file format at the link provided for the Sample File', 'warning')

        return redirect(url_for('home'))

    flash('File created successfully :)', 'success')

    return redirect(url_for('home'))

def createImageAnno(zipFile, proj_name):
    projects = mongo.db.projects              # collection of users and their respective projects
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    imageanno = mongo.db.imageanno

    currentuserprojectsname =  sorted(list(currentuserprojects()))
    activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
                    {'_id' : 0, 'activeproject': 1})['activeproject']

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
                        if projects.find_one({"projectName": project_name}, {'_id' : 0, "projectName": 1}) != None:
                            flash(f'File Name : {project_name} already exist!', 'warning')
                            return redirect(url_for('home'))

                        image_anno_detail = {}
                        image_id = 'I'+re.sub(r'[-: \.]', '', str(datetime.now()))
                        image_file = io.BytesIO(myfile.read())
                        # store images to mongodb fs collection
                        mongo.save_file(file_name, image_file, imageId = image_id)
                        image_anno_detail["projectName"] = project_name
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
        project_details["projectName"] = project_name
        project_details["projectOwner"] = project_owner
        project_details["tagSet"] = tag_set
        project_details["imageFiles"] = image_files
        project_details["lastActiveId"] = lastActiveId
        project_details["sharedWith"]  = [project_owner]
        project_details["projectdeleteFLAG"] = 0

        # print(project_details)
        projects.insert_one(project_details)
        # get curent user project list and update
        userprojectnamelist = userprojects.find_one({'username' : current_user.username})["myproject"]
        # print(f'{"#"*80}\n{userprojectnamelist}')
        userprojectnamelist.append(project_details['projectName'])
        userprojects.update_one({ 'username' : current_user.username }, \
            { '$set' : { 'myproject' : userprojectnamelist, 'activeproject' :  project_details['projectName']}})

    except:
        # flash('Please upload a zip file') 
        flash('Please upload a zip file. Check the file format at the link provided for the Sample File', 'warning')

        return redirect(url_for('home'))   

    flash('File created successfully :)', 'success')

    # return render_template('home.html',  data=currentuserprojectsname, activeproject=activeprojectname)
    return redirect(url_for('home'))

