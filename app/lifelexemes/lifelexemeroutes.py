from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import current_user, login_required, login_user, logout_user
from app.controller import (
    getdbcollections,
    getcurrentusername,
    getactiveprojectname,
    userdetails,
    projectDetails,
    life_logging,
    getactiveprojectform,
    getprojectowner,
    getcurrentuserprojects,
    getuserprojectinfo,
    readJSONFile,
    savenewlexeme,
    lexicondetails,
    langscriptutils
)
from app import mongo
import os
from pprint import pformat
from datetime import datetime
import re

lifelexemes = Blueprint('lifelexemes', __name__,
                       template_folder='templates', static_folder='static')

basedir = os.path.abspath(os.path.dirname(__file__))
basedir_parent = '/'.join(basedir.split('/')[:-1])
scriptCodeJSONFilePath = os.path.join(basedir_parent, 'static/json/scriptCode.json')
langScriptJSONFilePath = os.path.join(basedir_parent, 'static/json/langScript.json')

logger = life_logging.get_logger()

# enter new lexeme route
# display form for new lexeme entry for current project
@lifelexemes.route('/enternewlexeme', methods=['GET', 'POST'])
@login_required
def enternewlexeme():
    try:
        projects, userprojects, projectsform = getdbcollections.getdbcollections(mongo,
                                                                                'projects',
                                                                                'userprojects',
                                                                                'projectsform')
        current_username = getcurrentusername.getcurrentusername()
        currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)
        # if method is not 'POST'
        projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
        project_form = projectsform.find_one_or_404({'projectname': activeprojectname,
                                                    'username': projectowner},
                                                    {"_id": 0})
        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                            current_username,
                                                            activeprojectname)
        if project_form is not None:
            return render_template('enternewlexeme.html',
                                newData=project_form,
                                data=currentuserprojectsname,
                                shareinfo=shareinfo)
    except:
        logger.exception("")
    return render_template('enternewlexeme.html')


@lifelexemes.route('/lexemelist', methods=['GET', 'POST'])
@login_required
def lexemelist():
    try:
        userprojects, lexemes = getdbcollections.getdbcollections(mongo,
                                                                    'userprojects',
                                                                    'lexemes')
        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(
            current_username, userprojects)
        lexeme_list = []
        search_key = request.args.get('search')
        if (search_key is not None and
            search_key != ''):
            logger.debug("search_key: %s", search_key)
            lexeme_list_cursor = lexemes.find({"projectname": activeprojectname,
                                               "headword": {'$regex':search_key}},
                                               {"_id": 0,
                                                "headword": 1,
                                                "lexemeId": 1})
            logger.debug(lexeme_list_cursor)
            for i, lexeme in enumerate(lexeme_list_cursor):
                logger.debug(i)
                logger.debug(pformat(lexeme))
                headword = lexeme['headword']
                lexeme_id = lexeme['lexemeId']
                lexeme_list.append({"id": lexeme_id, "text": headword})
    except:
        logger.exception("")

    return jsonify(lexemeList=lexeme_list)

# dictionary view route
# display lexeme entries for current project in a table
@lifelexemes.route('/dictionaryview', methods=['GET', 'POST'])
@login_required
def dictionaryview():
    try:
        projects, userprojects, lexemes = getdbcollections.getdbcollections(mongo,
                                                                            'projects',
                                                                            'userprojects',
                                                                            'lexemes')
        current_username = getcurrentusername.getcurrentusername()
        currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)
        projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
        scriptCode = readJSONFile.readJSONFile(scriptCodeJSONFilePath)
        langScript = readJSONFile.readJSONFile(langScriptJSONFilePath)
        if request.method == 'POST':
            new_lexeme_data = dict(request.form.lists())
            new_lexeme_files = request.files.to_dict()
            savenewlexeme.savenewlexeme(mongo,
                                        projects,
                                        lexemes,
                                        scriptCode,
                                        langScript,
                                        new_lexeme_data,
                                        new_lexeme_files,
                                        projectowner,
                                        current_username)
            flash('Successfully added new lexeme')
            return redirect(url_for('lifelexemes.enternewlexeme'))
        try:
            my_projects = len(userprojects.find_one(
                {'username': current_username})["myproject"])
            shared_projects = len(userprojects.find_one(
                {'username': current_username})["projectsharedwithme"])
            # logger.debug(f"MY PROJECTS: {my_projects}, SHARED PROJECTS: {shared_projects}")
            if (my_projects+shared_projects) == 0:
                flash('Please create your first project')
                return redirect(url_for('home'))
        except:
            # logger.debug(f'{"#"*80}\nCurrent user details not in database!!!')
            flash('Please create your first project')
            return redirect(url_for('home'))
        # get the list of lexeme entries for current project to show in dictionary view table
        lst = list()
        try:
            # logger.debug(activeprojectname)
            # optionally takes field_list, if provided by the user for showing dictionary entries
            all_fields, lst = lexicondetails.get_all_lexicon_details(
                lexemes, activeprojectname)
        except:
            logger.exception("")
            flash('Enter first lexeme of the project')

        shareinfo = getuserprojectinfo.getuserprojectinfo(
            userprojects, current_username, activeprojectname)
        return render_template('dictionaryview.html',
                                projectName=activeprojectname,
                                fields=all_fields,
                                sdata=lst,
                                count=len(lst),
                                data=currentuserprojectsname,
                                shareinfo=shareinfo)
    except:
        logger.exception("")
    return redirect(url_for('lifelexemes.enternewlexeme'))

@lifelexemes.route('/lexemeview', methods=['GET'])
def lexemeview():
    y = {}
    lexeme = {}
    filen = {}
    try:
        projects, userprojects, projectsform, lexemes = getdbcollections.getdbcollections(mongo,
                                                                                        'projects',
                                                                                        'userprojects',
                                                                                        'projectsform',
                                                                                        'lexemes')

        current_username = getcurrentusername.getcurrentusername()
        activeprojectname = getactiveprojectname.getactiveprojectname(
            current_username, userprojects)
        projectOwner = getprojectowner.getprojectowner(projects, activeprojectname)
        # logger.debug('projectOwner: %s', projectOwner)
        # data through ajax
        headword = request.args.get('a').split(',')
        # logger.debug('headword: %s', headword)
        lexeme = lexemes.find_one({'username': projectOwner, 'lexemeId': headword[0], },
                                {'_id': 0, 'username': 0})
        # logger.debug('lexeme: %s', pformat(lexeme))

        filen = {}
        if 'filesname' in lexeme:
            for key, filename in lexeme['filesname'].items():
                logger.debug('key: %s, filename: %s', key, filename)
                filen[key] = url_for('retrieve', filename=filename)
        # logger.debug('filen: %s', pformat(filen))
        y = projectsform.find_one_or_404({'projectname': activeprojectname,
                                        'username': projectOwner}, {"_id": 0})
    except:
        logger.exception("")

    return jsonify(newData=y, result1=lexeme, result2=filen)


# modal view with complete detail of a lexeme for edit
# edit button on dictionary view table
@lifelexemes.route('/lexemeedit', methods=['GET', 'POST'])
def lexemeedit():
    y = {}
    lexeme = {}
    filen = {}
    try:
        # getting the collections
        # collection of project specific form created by the user
        projectsform = mongo.db.projectsform
        # collection containing entry of each lexeme and its details
        lexemes = mongo.db.lexemes
        # collection of users and their respective projects
        userprojects = mongo.db.userprojects
        projects = mongo.db.projects                        # collection of projects

        headword = request.args.get('a').split(',')                    # data through ajax
        logger.debug(headword)

        activeprojectname = userprojects.find_one({'username': current_user.username})['activeprojectname']
        # logger.debug(activeprojectname)

        projectOwner = projects.find_one({'projectname': activeprojectname}, {
                                        'projectOwner': 1})['projectOwner']
        # projectOwner = projects.find_one({}, {"_id" : 0, activeprojectname : 1})[activeprojectname]["projectOwner"]
        # logger.debug(projectOwner)

        if request.method == 'POST':

            newLexemeData = request.form.to_dict()
            # logger.debug(newLexemeData)
            return redirect(url_for('lifelexemes.dictionaryview'))

        # activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
        #                 {'_id' : 0, 'activeprojectname': 1})['activeprojectname']
        lexeme = lexemes.find_one({'username': projectOwner, 'lexemeId': headword[0], },
                                {'_id': 0, 'username': 0})

        logger.debug(lexeme)
        if (lexeme is not None):
            filen = []
            if 'filesname' in lexeme:
                for filename in lexeme['filesname']:
                    filen.append(url_for('retrieve', filename=filename))
        else:
            lexeme = {}
        y = projectsform.find_one_or_404({'projectname': activeprojectname,
                                            'username': projectOwner}, {"_id": 0})
    except:
        logger.exception("")

    return jsonify(newData=y, result1=lexeme, result2=filen)

# enter new lexeme route
# display form for new lexeme entry for current project


@lifelexemes.route('/editlexeme', methods=['GET', 'POST'])
@login_required
def editlexeme():
    return render_template('editlexeme.html')


@lifelexemes.route('/lexemeupdate', methods=['GET', 'POST'])
def lexemeupdate():
    projects, userprojects, lexemes = getdbcollections.getdbcollections(mongo,
                                                                        'projects',
                                                                        'userprojects',
                                                                        'lexemes')
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                                                            userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                  userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    # logger.debug(f"PROJECT OWNER: {projectOwner}")
    # new lexeme details coming from current project form
    if request.method == 'POST':

        # newLexemeData = request.form.to_dict()
        newLexemeData = dict(request.form.lists())
        newLexemeFiles = request.files.to_dict()
        # logger.debug(newLexemeFiles)
        # logger.debug(newLexemeData)
        lexemeId = newLexemeData['lexemeId'][0]
        # dictionary to store files name
        newLexemeFilesName = {}
        for key in newLexemeFiles:
            if newLexemeFiles[key].filename != '':
                # adding microseconds of current time to differ two files of same name
                newLexemeFilesName[key] = (datetime.now().strftime(
                    '%f')+'_'+newLexemeFiles[key].filename)

        # format data filled in enter new lexeme form
        lexemeFormData = {}
        sense = {}
        variant = {}
        allomorph = {}
        lemon = ''

        lexemeFormData['username'] = projectowner

        def lexemeFormScript():
            """'List of dictionary' of lexeme form scripts"""
            lexemeFormScriptList = []
            for key, value in newLexemeData.items():
                if 'Script' in key:
                    k = re.search(r'Script (\w+)', key)
                    lexemeFormScriptList.append({k[1]: value[0]})
            lexemeFormData['headword'] = list(
                lexemeFormScriptList[0].values())[0]
            return lexemeFormScriptList

        def senseListOfDict(senseCount):
            """'List of dictionary' of sense"""
            for num in range(1, int(newLexemeData['senseCount'][-1])+1):
                senselist = []
                for key, value in newLexemeData.items():
                    if 'Sense '+str(num) in key:
                        k = re.search(r'([\w+\s]+) Sense', key)
                        if k[1] == 'Semantic Domain' or k[1] == 'Lexical Relation':
                            senselist.append({k[1]: value})
                        else:
                            senselist.append({k[1]: value[0]})
                sense['Sense '+str(num)] = senselist
            # logger.debug(sense)
            return sense

        def variantListOfDict(variantCount):
            """'List of dictionary' of variant"""
            for num in range(1, int(newLexemeData['variantCount'][-1])+1):
                # variantlist = []
                variantdict = {}
                for key, value in newLexemeData.items():
                    if 'Variant '+str(num) in key:
                        k = re.search(r'([\w+\s]+) Variant', key)
                        # variantlist.append({k[1] : value[0]})
                        variantdict[k[1]] = value[0]
                variant['Variant '+str(num)] = variantdict
            # logger.debug(variant)
            return variant

        def allomorphListOfDict(allomorphCount):
            """'List of dictionary' of allomorph"""
            for num in range(1, int(newLexemeData['allomorphCount'][-1])+1):
                # allomorphlist = []
                allomorphdict = {}
                for key, value in newLexemeData.items():
                    if 'Allomorph '+str(num) in key:
                        k = re.search(r'([\w+\s]+) Allomorph', key)
                        # allomorphlist.append({k[1] : value[0]})
                        allomorphdict[k[1]] = value[0]
                # allomorph['Allomorph '+str(num)] = allomorphlist
                allomorph['Allomorph '+str(num)] = allomorphdict
            # logger.debug(allomorph)
            return allomorph

        def customFields():
            """'List of dictionary' of custom fields"""
            # customFieldsList = []
            customFieldsDict = {}
            for key, value in newLexemeData.items():
                if 'Custom' in key:
                    k = re.search(r'Field (\w+)', key)
                    # customFieldsList.append({k[1] : value[0]})
                    customFieldsDict[k[1]] = value[0]
            # logger.debug(sense)
            return customFieldsDict

        for key, value in newLexemeData.items():
            if 'Sense' in key or 'Variant' in key or 'Allomorph' in key:
                continue
            elif key == 'senseCount':
                Sense = senseListOfDict(value[0])
                lexemeFormData['Sense'] = Sense
            elif key == 'variantCount':
                Variant = variantListOfDict(value[0])
                lexemeFormData['Variant'] = Variant
            elif key == 'allomorphCount':
                Allomorph = allomorphListOfDict(value[0])
                lexemeFormData['Allomorph'] = Allomorph
            elif 'Script' in key:
                lexemeFormData['Lexeme Form Script'] = lexemeFormScript()
            elif 'Custom' in key:
                lexemeFormData['Custom Fields'] = customFields()
            elif key == 'Lexeme Language':
                pass
            else:
                # logger.debug(lexemeFormData)
                # logger.debug(key)
                lexemeFormData[key] = value[0]

        # logger.debug(f"{'#'*80}\n{list(lexemeFormData['Sense']['Sense 1'][0].keys())}")
        gloss = list(lexemeFormData['Sense']['Sense 1'][0].keys())
        lexemeFormData['gloss'] = lexemeFormData['Sense']['Sense 1'][0][gloss[0]]
        # grammaticalcategory  = list(lexemeFormData['Sense']['Sense 1'][4].keys())
        # logger.debug(f"{'#'*80}\n{lexemeFormData['Sense']['Sense 1']}")
        for senseData in lexemeFormData['Sense']['Sense 1']:
            if list(senseData.keys())[0] == 'Grammatical Category':
                # logger.debug(f"{'#'*80}\n{list(senseData.values())[0]}")
                lexemeFormData['grammaticalcategory'] = list(senseData.values())[
                    0]
        lexemeFormData['lexemedeleteFLAG'] = 0
        lexemeFormData['updatedBy'] = current_user.username
        lexemeFormData['lexemeId'] = lexemeId

        langscripts = langscriptutils.get_langscripts(
            newLexemeData, lexemeFormData)
        lexemeFormData['langscripts'] = langscripts

        SenseNew = {}

        for key, value in lexemeFormData['Sense'].items():
            keyParent = key
            key = {}
            # logger.debug(keyParent)
            Gloss = {}
            Definition = {}
            Lexical_Relation = {}
            for val in value:

                for k, v in val.items():
                    if ("Gloss" in k):
                        Gloss[k.split()[1][:3].lower()] = v
                        # logger.debug(key, k, v)
                    elif ("Definition" in k):
                        Definition[k.split()[1][:3].lower()] = v
                    elif ("Lexical Relation" in k):
                        # Lexical_Relation[v[0]] = v[0]
                        key['Lexical Relation'] = v[0]
                    elif ("Semantic Domain" in k):
                        # Lexical_Relation[v[0]] = v[0]
                        key['Semantic Domain'] = v[0]

                    else:
                        key[k] = v

            key['Gloss'] = Gloss
            key['Definition'] = Definition
            # key['Lexical Relation'] = Lexical_Relation

            SenseNew[keyParent] = key
        # logger.debug(SenseNew)
        lexemeFormData['SenseNew'] = SenseNew

        lexemeForm = {}
        for lexForm in lexemeFormData['Lexeme Form Script']:
            for lexKey, lexValue in lexForm.items():
                # lexemeForm[lexKey[:4]] = lexValue
                lexemeForm[langscriptutils.get_script_code(lexKey)] = lexValue

        lexemeFormData['Lexeme Form'] = lexemeForm

        # keep only new updated keys as in 'lexemeEntry_sir.json' file in 'data_format folder
        # and delete old keys
        lexemeFormData.pop('Sense', None)
        lexemeFormData.pop('Lexeme Form Script', None)

        # when testing comment these to avoid any database update/changes
        # saving files for the new lexeme to the database in fs collection
        for (filename, key) in zip(newLexemeFilesName.values(), newLexemeFiles):
            # logger.debug(filename, key, newLexemeFiles[key])
            mongo.save_file(filename, newLexemeFiles[key], lexemeId=lexemeId, username=current_user.username,
                            projectname=lexemeFormData['projectname'], headword=lexemeFormData['headword'],
                            updatedBy=current_user.username)

       # prevent deletion of old files name from lexeme details
        oldFilesOfLexeme = lexemes.find_one(
            {'lexemeId': lexemeId}, {'_id': 0, 'filesname': 1})
        # logger.debug(oldFilesOfLexeme)
        if (len(oldFilesOfLexeme) != 0):
            oldFilesOfLexeme = oldFilesOfLexeme['filesname']
            for key, fname in oldFilesOfLexeme.items():
                if (key not in newLexemeFilesName):
                    newLexemeFilesName[key] = fname
        # save file names of a lexeme in lexemeFormData dictionary with other details related to the lexeme
        if len(newLexemeFilesName) != 0:
            lexemeFormData['filesname'] = newLexemeFilesName
        # saving data for that new lexeme to database in lexemes collection
        # lexemes.insert(lexemeFormData)
        # logger.debug(f'{"="*80}\nLexeme Form :')
        # logger.debug(lexemeFormData)
        # logger.debug(f'{"="*80}')
        lexemes.update_one({'lexemeId': lexemeId}, {'$set': lexemeFormData})

        flash('Successfully Updated lexeme')
        return redirect(url_for('lifelexemes.dictionaryview'))
        # comment till here

    try:
        my_projects = len(userprojects.find_one(
            {'username': current_user.username})["myproject"])
        shared_projects = len(userprojects.find_one(
            {'username': current_user.username})["projectsharedwithme"])
        # logger.debug(f"MY PROJECTS: {my_projects}, SHARED PROJECTS: {shared_projects}")
        if (my_projects+shared_projects) == 0:
            flash('Please create your first project')
            return redirect(url_for('home'))
    except:
        # logger.debug(f'{"#"*80}\nCurrent user details not in database!!!')
        flash('Please create your first project')
        return redirect(url_for('home'))
    # get the list of lexeme entries for current project to show in dictionary view table
    lst = list()

    # projectOwner = projects.find_one({}, {"_id" : 0, activeprojectname : 1})[activeprojectname]["projectOwner"]
    # logger.debug(projectOwner)
    try:
        # logger.debug(activeprojectname)
        projectOwner = projects.find_one({}, {"_id": 0, activeprojectname: 1})[
            activeprojectname]["projectOwner"]
        # logger.debug(projectOwner)
        for lexeme in lexemes.find({'username': projectOwner, 'projectname': activeprojectname, 'lexemedeleteFLAG': 0},
                                   {'_id': 0, 'headword': 1, 'gloss': 1, 'grammaticalcategory': 1, 'lexemeId': 1}):
            # logger.debug(lexeme)
            if (len(lexeme['headword']) != 0):
                lst.append(lexeme)
    except:
        flash('Enter first lexeme of the project')

    # logger.debug(lst)
    return render_template('dictionaryview.html', projectName=activeprojectname, sdata=lst, count=len(lst), data=currentuserprojectsname)


# delete button on dictionary view table
@lifelexemes.route('/lexemedelete', methods=['GET', 'POST'])
def lexemedelete():
    headword = ['', '']
    try:
        # getting the collections
        projects, userprojects, lexemes = getdbcollections.getdbcollections(mongo,
                                                                            'projects',
                                                                            'userprojects',
                                                                            'lexemes')
        activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                    userprojects)
        projectowner = getprojectowner.getprojectowner(projects, activeprojectname)

        # data through ajax
        headword = request.args.get('a').split(',')
        lexemes.update_one({'username': projectowner, 'lexemeId': headword[0]},
                        {'$set': {'lexemedeleteFLAG': 1}})
    except:
        logger.exception("")

    return jsonify(msg=headword[1]+' deletion successful')

# delete button on dictionary view table
@lifelexemes.route('/deletemultiplelexemes', methods=['GET', 'POST'])
def deletemultiplelexemes():
    try:
        projects, userprojects, lexemes = getdbcollections.getdbcollections(mongo,
                                                                            'projects',
                                                                            'userprojects',
                                                                            'lexemes')
        activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                    userprojects)
        projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
        # data through ajax
        headwords = request.args.get('data')
        headwords = eval(headwords)

        # logger.debug(headwords)
        for headwordId in headwords.keys():
            lexemes.update_one({'username': projectowner, 'lexemeId': headwordId,
                                }, {'$set': {'lexemedeleteFLAG': 1}})
    except:
        logger.exception("")

    return 'OK'
