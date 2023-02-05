from flask import flash, redirect, render_template, url_for, request, json, jsonify, send_file
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash
from app import app, mongo
from app.forms import UserLoginForm, RegistrationForm
from app.models import UserLogin

from flask_login import current_user, login_user, logout_user, login_required

from pprint import pprint
from datetime import datetime
import gridfs
import os
import glob
from zipfile import ZipFile
import re
from jsondiff import diff
import pandas as pd
import io

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import joblib
from rdflib import Graph, Literal, RDF, URIRef, XSD
from rdflib.namespace import RDFS, FOAF, RDF, SKOS
from rdflib.namespace import Namespace

from pylatex import Document, PageStyle, Head, Foot, MiniPage, \
    LargeText, MediumText, Section, \
    LineBreak, NewPage, Tabularx, TextColor, simple_page_number
from pylatex.utils import bold, NoEscape

from pylatex.base_classes import Environment
from pylatex.package import Package
import json
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import ElementTree
from app.controller import (
                                audiodetails,
                                createdummylexemeentry,
                                getactiveprojectform,
                                getactiveprojectname,
                                getcommentstats,
                                getcurrentusername,
                                getcurrentuserprojects,
                                getdbcollections,
                                getprojectowner,
                                getprojecttype,
                                getuserprojectinfo,
                                latex_generator as lg,
                                questionnairedetails,
                                readJSONFile,
                                removeallaccess,
                                savenewlexeme,
                                savenewproject,
                                savenewprojectform,
                                savenewsentence,
                                unannotatedfilename,
                                updateuserprojects
                            )
# from app.controller import getdbcollections, getcurrentuserprojects, getactiveprojectname
# from app.controller import getprojectowner, getactiveprojectform, savenewsentence
# from app.controller import readJSONFile, createdummylexemeentry
# from app.controller import savenewproject, updateuserprojects, savenewprojectform
# from app.controller import audiodetails, getcurrentusername, getcommentstats
# from app.controller import unannotatedfilename, getuserprojectinfo
# from app.controller import questionnairedetails, removeallaccess
import shutil, traceback


basedir = os.path.abspath(os.path.dirname(__file__))
scriptCodeJSONFilePath = os.path.join(basedir, 'static/json/scriptCode.json')
langScriptJSONFilePath = os.path.join(basedir, 'static/json/langScript.json')
ipatomeeteiFilePath = os.path.join(basedir, 'static/json/ipatomeetei.json')

ADMIN_USER = 'life_admin'
admin_reminder = f'App admin <<{ADMIN_USER}>> user created! Please create new password for this account to login'

# print(f'{"#"*80}\nBase directory:\n{basedir}\n{"#"*80}')


# home page route
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    userprojects, = getdbcollections.getdbcollections(mongo, 'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    print('USERNAME: ', current_username)
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_username, userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects, current_username, activeprojectname)
    # print(shareinfo)

    return render_template('home.html',
                            data=currentuserprojectsname,
                            activeprojectname=activeprojectname,
                            shareinfo=shareinfo)

# new project route
# create lexeme entry form for the new project
@app.route('/newproject', methods=['GET', 'POST'])
@login_required
def newproject():
    projects, userprojects, projectsform = getdbcollections.getdbcollections(mongo,
                                                'projects',
                                                'userprojects',
                                                'projectsform')
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                userprojects)
    if request.method == 'POST':
        project_form_data = dict(request.form.lists())
        project_name = project_form_data['projectname'][0].strip()
        project_name = savenewproject.savenewproject(projects,
                                                        project_name,
                                                        current_user.username)
        if project_name == '':
            flash(f'Project Name : {project_name} already exist!')
            return redirect(url_for('newproject'))
        else:
            # print(project_name)
            updateuserprojects.updateuserprojects(userprojects,
                                                    project_name,
                                                    current_user.username)
            savenewprojectform.savenewprojectform(projectsform,
                                                    project_name,
                                                    project_form_data,
                                                    current_user.username)
            flash(f'Project Name : {project_name} created successfully :)')
            return redirect(url_for('home'))
    return render_template('newproject.html',
                            data=currentuserprojectsname)

# get lexeme from sentences and save them to lexemes collection
def sentence_lexeme_to_lexemes(oneSentenceDetail, oneLexemeDetail):
    for key, value in oneLexemeDetail.items():
        # print(key, ' : ', value)
        pass


# enter new sentences route
# enter new sentences in the project
@app.route('/enternewsentences', methods=['GET', 'POST'])
@login_required
def enternewsentences():
    projects, userprojects, projectsform, sentences, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                                        'projects',
                                                                                                        'userprojects',
                                                                                                        'projectsform',
                                                                                                        'sentences',
                                                                                                        'transcriptions')
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username, userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects, current_user.username, activeprojectname)
    # print(shareinfo)

    if activeprojectname == '':
        flash(f"select a project from 'All Projects' to work on!")
        return redirect(url_for('home'))
    if request.method == 'POST':
        newSentencesData = dict(request.form.lists())
        newSentencesFiles = request.files.to_dict()
        savenewsentence.savenewsentence(mongo,
                                        sentences,
                                        current_user.username,
                                        activeprojectname,
                                        newSentencesData,
                                        newSentencesFiles)

    # currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_user.username,
    #                             userprojects)


    # if method is not 'POST'
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    activeprojectform = getactiveprojectform.getactiveprojectform(projectsform,
                                                                    projectowner,
                                                                    activeprojectname)
    if activeprojectform is not None:
        try:
            # , audio_file_path, transcription_details
            # activespeakerid = getactivespeakerid.getactivespeakerid(userprojects, current_user.username)
            activespeakerid = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                    current_user.username,
                                                                    activeprojectname)['activespeakerId']
            total_comments, annotated_comments, remaining_comments = getcommentstats.getcommentstats(projects,
                                                                                                        transcriptions,
                                                                                                        activeprojectname,
                                                                                                        activespeakerid,
                                                                                                        'audio')
            commentstats = [total_comments, annotated_comments, remaining_comments]
            audio_id = audiodetails.getactiveaudioid(projects,
                                                        activeprojectname,
                                                        activespeakerid,
                                                        current_user.username)
            transcription_details = audiodetails.getaudiofiletranscription(transcriptions, audio_id)
            file_path = audiodetails.getaudiofilefromfs(mongo,
                                                        basedir,
                                                        audio_id,
                                                        'audioId')
            activeprojectform['lastActiveId'] = audio_id
            activeprojectform['transcriptionDetails'] = transcription_details
            # print(transcription_details)
            activeprojectform['AudioFilePath'] = file_path
            transcription_regions, gloss, pos = audiodetails.getaudiotranscriptiondetails(transcriptions, audio_id)
            activeprojectform['transcriptionRegions'] = transcription_regions
            # print(transcription_regions)
            if (len(gloss) != 0):
                activeprojectform['glossDetails'] = gloss
            if (len(pos) != 0):
                activeprojectform['posDetails'] = pos
            try:
                speakerids = projects.find_one({"projectname": activeprojectname},
                                                {"_id": 0, "speakerIds."+current_user.username: 1}
                                            )["speakerIds"][current_user.username]
            except:
                speakerids = ''
            scriptCode = readJSONFile.readJSONFile(scriptCodeJSONFilePath)
            activeprojectform['scriptCode'] = scriptCode
            langScript = readJSONFile.readJSONFile(langScriptJSONFilePath)
            activeprojectform['langScript'] = langScript
            # ipaToMeetei = readJSONFile.readJSONFile(ipatomeeteiFilePath)
            # activeprojectform['ipaToMeetei'] = ipaToMeetei
            # print('currentuserprojectsname', currentuserprojectsname)
            # print('speakerids', speakerids)
            # pprint(activeprojectform)
            # print(activespeakerid, commentstats, shareinfo)
            return render_template('enternewsentences.html',
                                    projectName=activeprojectname,
                                    newData=activeprojectform,
                                    data=currentuserprojectsname,
                                    speakerids=speakerids,
                                    activespeakerid=activespeakerid,
                                    commentstats=commentstats,
                                    shareinfo=shareinfo)
        except Exception as e:
            traceback.print_exc()
            flash('Upload first audio file.')

    return render_template('enternewsentences.html',
                                    projectName=activeprojectname,
                                    newData=activeprojectform,
                                    data=currentuserprojectsname)

    # return render_template('enternewsentences.html',
    #                         projectName=activeprojectname,
    #                         sdata=[],
    #                         data=currentuserprojectsname)

# get new sentences route
# get new sentences in the project coming throug ajax
@app.route('/savetranscription', methods=['GET', 'POST'])
@login_required
def savetranscription():
    projects, userprojects, projectsform, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                    'projects',
                                                                    'userprojects',
                                                                    'projectsform',
                                                                    'transcriptions')
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                    userprojects)                                                                    
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)                                                                    
    activeprojectform = getactiveprojectform.getactiveprojectform(projectsform,
                                                                    projectowner,
                                                                    activeprojectname)
    # activespeakerid = getactivespeakerid.getactivespeakerid(userprojects, current_user.username)
    activespeakerid = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                            current_user.username,
                                                            activeprojectname)['activespeakerId']
    # data through ajax
    transcription_data = json.loads(request.args.get('a'))
    transcription_data = dict(transcription_data)
    lastActiveId = transcription_data['lastActiveId']
    transcription_regions = transcription_data['transcriptionRegions']
    # print(lastActiveId)
    # print(transcription_regions)
    scriptCode = readJSONFile.readJSONFile(scriptCodeJSONFilePath)
    audiodetails.savetranscription(transcriptions,
                                    activeprojectform,
                                    scriptCode,
                                    current_user.username,
                                    transcription_regions,
                                    lastActiveId,
                                    activespeakerid)
    latest_audio_id = audiodetails.getnewaudioid(projects,
                                                    activeprojectname,
                                                    lastActiveId,
                                                    activespeakerid,
                                                    'next')
    audiodetails.updatelatestaudioid(projects,
                                        activeprojectname,
                                        latest_audio_id,
                                        current_user.username,
                                        activespeakerid)
    sentenceFieldId = ''
    gloss = ''
    sentence = ''

    return jsonify(sentenceFieldId=sentenceFieldId, gloss=gloss, result2=sentence)

# new automation route
# buttons working for different automation(POS, morph analyser)
@app.route('/automation', methods=['GET', 'POST'])
@login_required
def automation():
    userprojects, = getdbcollections.getdbcollections(mongo, 'userprojects')
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                            userprojects)

    return render_template('automation.html',
                            projectName=activeprojectname,
                            data=currentuserprojectsname)

def naiveBayes(corpus, y, x_test):
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus)

    # example for saving python object as pkl
    joblib.dump(vectorizer, "trainedModels/naiveBayesPOSVectorizer.pkl")
    clf = MultinomialNB()
    clf.fit(X, y)

    # save
    with open('trainedModels/naiveBayesPOSModel.pkl','wb') as f:
        pickle.dump(clf,f)


# new automation route
# buttons working for different automation(POS, morph analyser)
@app.route('/predictPOSNaiveBayes', methods=['GET', 'POST'])
@login_required
def predictPOSNaiveBayes():
    userprojects, = getdbcollections.getdbcollections(mongo, 'userprojects')
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                userprojects)
    # data through ajax
    wordList = request.args.get('a').split(',')                    
    if (len(wordList) != 0):
        # load model
        with open('trainedModels/naiveBayesPOSModel.pkl', 'rb') as f:
            clf = pickle.load(f)
        # loading pickled vectorizer
        vectorizer = joblib.load("trainedModels/naiveBayesPOSVectorizer.pkl")
        x_test = vectorizer.transform(wordList)
        predictedpos = list(clf.predict(x_test))
        predictedPOS = []
        for word, pos in zip(wordList, predictedpos):
            predictedPOS.append([word, pos])

        return jsonify(predictedPOS=predictedPOS)

    return render_template('automation.html',
                            data=currentuserprojectsname)

@app.route('/automatepos', methods=['GET', 'POST'])
@login_required
def automatepos():
    userprojects, sentences = getdbcollections.getdbcollections(mongo,
                                                'userprojects',
                                                'sentences')
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                            userprojects)

    sentence = request.args.get('a').split(',')                    # data through ajax
    # create dataframe from the json type data
    posdf = {}
    word = []
    label = []
    for pos in sentences.find({ 'projectname' : activeprojectname, 'sentencedeleteFLAG' : 0 }, \
                        {'_id' : 0, 'pos': 1}):
        for key, value in pos['pos'].items():
            word.append(key)
            label.append(value)
        posdf['word'] = word
        posdf['label'] = label
    posdf = pd.DataFrame.from_dict(posdf)
    x_test = ['cow']
    naiveBayes(word, label, x_test)

    return render_template('automation.html',
                            data=currentuserprojectsname)

# create an empty lexeme entry in the lexemes collection whenever new project is created
# so that if user download the excel of lexeme form directly after creating the poject
# there are columns in the excel
def dummylexemeentry():
    projects, userprojects, projectsform, lexemes = getdbcollections.getdbcollections(mongo,
                                                'projects',
                                                'userprojects',
                                                'projectsform',
                                                'lexemes')
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                            userprojects)

    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    activeprojectform = getactiveprojectform.getactiveprojectform(projectsform,
                                                                    projectowner,
                                                                    activeprojectname)
    scriptCode = readJSONFile.readJSONFile(scriptCodeJSONFilePath)
    langScript = readJSONFile.readJSONFile(langScriptJSONFilePath)
    createdummylexemeentry.createdummylexemeentry(projects,
                                                    lexemes,
                                                    activeprojectform,
                                                    scriptCode,
                                                    langScript,
                                                    current_user.username)

# dictionary view route
# display lexeme entries for current project in a table
@app.route('/dictionaryview', methods=['GET', 'POST'])
@login_required
def dictionaryview():
    projects, userprojects, lexemes = getdbcollections.getdbcollections(mongo,
                                                'projects',
                                                'userprojects',
                                                'lexemes')
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
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
                                        current_user.username)
        flash('Successfully added new lexeme')
        return redirect(url_for('enternewlexeme'))
    try:
        my_projects = len(userprojects.find_one({'username' : current_user.username})["myproject"])
        shared_projects = len(userprojects.find_one({'username' : current_user.username})["projectsharedwithme"])
        # print(f"MY PROJECTS: {my_projects}, SHARED PROJECTS: {shared_projects}")
        if  (my_projects+shared_projects) == 0:
            flash('Please create your first project')
            return redirect(url_for('home'))
    except:
        print(f'{"#"*80}\nCurrent user details not in database!!!')
        flash('Please create your first project')
        return redirect(url_for('home'))
    # get the list of lexeme entries for current project to show in dictionary view table
    lst = list()
    try:
        # print(activeprojectname)
        projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
        for lexeme in lexemes.find({ 'username' : projectowner, 'projectname' : activeprojectname, 'lexemedeleteFLAG' : 0 }, \
                                {'_id' : 0, 'headword' : 1, 'gloss' : 1, 'grammaticalcategory' : 1, 'lexemeId' : 1}):
            # pprint(lexeme)
            if (len(lexeme['headword']) != 0):
                lst.append(lexeme)
    except:
        flash('Enter first lexeme of the project')

    return render_template('dictionaryview.html',
                            projectName=activeprojectname,
                            sdata=lst,
                            count=len(lst),
                            data=currentuserprojectsname)


# enter new lexeme route
# display form for new lexeme entry for current project
@app.route('/enternewlexeme', methods=['GET', 'POST'])
@login_required
def enternewlexeme():
    projects, userprojects, projectsform = getdbcollections.getdbcollections(mongo,
                                                'projects',
                                                'userprojects',
                                                'projectsform')
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                            userprojects)

    # new project form containing dictionary fields and its type
    # if request.method == 'POST':
    #     project_form_data = dict(request.form.lists())
    #     project_name = project_form_data['projectname'][0]
    #     project_name = savenewproject.savenewproject(projects,
    #                                                     project_name,
    #                                                     current_user.username)
    #     if project_name == '':
    #         flash(f'Project Name : {project_name} already exist!')
    #         return redirect(url_for('newproject'))
    #     else:
    #         print(project_name)
    #         updateuserprojects.updateuserprojects(userprojects,
    #                                                 project_name,
    #                                                 current_user.username)
    #         savenewprojectform.savenewprojectform(projectsform,
    #                                                 project_name,
    #                                                 project_form_data,
    #                                                 current_user.username)

    # activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
    #                     userprojects)

    # project_form = projectsform.find_one_or_404({'projectname' : activeprojectname,
    #                                 'username' : current_user.username},
    #                                 { "_id" : 0 })
    # if project_form is not None:
    #     return render_template('enternewlexeme.html',
    #                             newData=project_form,
    #                             data=currentuserprojectsname)
    # return render_template('enternewlexeme.html')
    # if method is not 'POST'
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    project_form = projectsform.find_one_or_404({'projectname' : activeprojectname,
                                        'username' : projectowner},
                                        { "_id" : 0 })
    if project_form is not None:
        return render_template('enternewlexeme.html',
                                newData=project_form,
                                data=currentuserprojectsname)
    return render_template('enternewlexeme.html')

# defining file_format and uploaded_file_content globally
# to solve the problem of accessing the variable later by some functions
# file_format = ''
# uploaded_file_content = ''

def enterlexemefromuploadedfile(lexemedf):
    projects, userprojects, lexemes = getdbcollections.getdbcollections(mongo,
                                                'projects',
                                                'userprojects',
                                                'lexemes')
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                            userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    projectname = activeprojectname
    project = projects.find_one({}, {projectname : 1})
    def lexmetadata():
        # create lexemeId
        project = projects.find_one({'projectname': projectname}, {'projectname' : 1, 'lexemeInserted' : 1})
        lexemeCount = project['lexemeInserted']+1
        # lexemeCount = projects.find_one({}, {projectname : 1})[projectname]['lexemeInserted']+1
        # lexemeId = projectname+lexemeFormData['headword']+str(lexemeCount)
        Id = re.sub(r'[-: \.]', '', str(datetime.now()))
        lexemeId = 'L'+Id

        return (lexemeId, lexemeCount)

    # when testing comment these to avoid any database update/changes      
    # saving data for that new lexeme to database in lexemes collection
    # try:
    # print(lexemedf)
    for index, row in lexemedf.iterrows():
        uploadedFileLexeme = {
            "username": projectowner,
            "projectname": activeprojectname,
            "lexemedeleteFLAG": 0,
            "updatedBy": current_user.username,
            }
        lexemeId = str(row['lexemeId'])
        getlexemeId = None
        # print(f"{index}\t{lexemeId}\t{len(lexemeId)}\t{type(lexemeId)}")
        if (lexemeId == 'nan' or lexemeId == ''):
            lexemeId, lexemeCount = lexmetadata()
            # print(lexemeId, lexemeCount)
        else:
            getlexemeId = lexemes.find_one({ 'lexemeId' : lexemeId },
                                            {'_id' : 0, 'lexemeId' : 1, 'projectname': 1})
            # print(getlexemeId)
            if (getlexemeId == None):
                # print(f"lexemeId not in DB")
                lexemeId, lexemeCount = lexmetadata()
            else:
                if (getlexemeId['projectname'] != activeprojectname):
                    flash(f"lexemeId: {lexemeId} if from different project!!!")
                    return redirect(url_for('enternewlexeme'))    

        uploadedFileLexeme['lexemeId'] = lexemeId
        # pprint(uploadedFileLexeme)
        if (getlexemeId != None):
            # print(f"LEXEME ALREADY EXISTS")
            lexemes.update_one({ 'lexemeId': lexemeId }, { '$set' : uploadedFileLexeme })
        else:
            lexemes.insert(uploadedFileLexeme)
            # update lexemeInserted count of the project in projects collection
            # project[projectname]['lexemeInserted'] = lexemeCount
            # print(f'{"#"*80}\n{project}')
            projects.update_one({'projectname': projectname}, { '$set' : { 'lexemeInserted' : lexemeCount }})
            # projects.update_one({}, { '$set' : { projectname : project[projectname] }})

        for column_name in list(lexemedf.columns):
            if (column_name not in uploadedFileLexeme):
                value = str(row[column_name])
                if (value == 'nan'):
                    value = ''
                if ('Sense 1.Gloss.eng' in column_name):
                    uploadedFileLexeme['gloss'] = value
                if ('Sense 1.Grammatical Category' in column_name):
                    uploadedFileLexeme['grammaticalcategory'] = value
                uploadedFileLexeme[column_name] = value

        # print(f'{"="*80}\nLexeme Form :')
        # pprint(uploadedFileLexeme)
        # print(f'{"="*80}')

        lexemes.update_one({ 'lexemeId': lexemeId }, { '$set' : uploadedFileLexeme })

        # print(f'{"="*80}\nLexeme Form :')
        # pprint(uploadedFileLexeme)
        # print(f'{"="*80}')

    flash('Successfully added new lexeme')
    return redirect(url_for('enternewlexeme'))
    # comment till here

def lifeuploader(fileFormat, uploadedFileContent, field_map = {}):
    lang_script_map = {
    'ipa': 'ipa',
    'hin': 'Deva',
    'guj': 'Gujr',
    'pun': 'Guru',
    'ban': 'Beng',
    'ass': 'Beng',
    'odi': 'Orya',
    'kan': 'Knda',
    'tam': 'Taml',
    'tel': 'Telu',
    'mal': 'Mlym',
    'mar': 'Deva',
    'bod': 'Deva',
    'kon': 'Deva',
    'nep': 'Deva',
    'mai': 'Deva',
    'mag': 'Deva',
    'bho': 'Deva',
    'awa': 'Deva',
    'har': 'Deva',
    'bra': 'Deva',
    'bun': 'Deva',
    'anp': 'Deva'
    }

    def get_lift_map():
        map = {
            'grammatical-info': 'grammaticalcategory',
            'lexical-unit': 'headword',
            'lexical-unit-form': 'Lexical Form',
            'pronunciation': 'Pronunciation',
            'gloss': 'Gloss',
            'example': 'Example',
            'translation':'Free Translation',
            'definition': 'Definition',
            'note': 'Encyclopedic Information',
            'semantic-domain': 'Semantic Domain',
            'variant': 'VariantNew.Variant 1',
            'relation': ''
        }

        return map


    def get_script_name(wordform):
        lang_name = wordform.attrib['lang']
        # print (lang_name)
        parts = lang_name.split('-')
        if len(parts) > 1:
            script_name = parts[1]
        else:
            script_name = lang_script_map.get(lang_name, lang_name)
        
        return script_name, lang_name

    def get_lang_name(wordform):
        lang_name_full = wordform.attrib['lang']
        # print (lang_name_full)
        lang_name = lang_name_full.split('-')[0]
        # if len(parts) > 1:
        #     script_name = parts[1]
        # else:
        #     script_name = lang_script_map.get(lang_name, lang_name)
        
        return lang_name, lang_name_full


    def get_scripts_map(lex_fields):
        scripts_map = {}
        # print (lex_fields)
        for lex_field in lex_fields:
            # print ('Lex field', lex_field)
            script_name = lex_field.split('.')[-1]
            if 'langscripts.headwordscript' in lex_field:
                scripts_map['langscripts.headwordscript'] = script_name
            elif 'langscripts.lexemeformscripts' in lex_field:
                if 'langscripts.lexemeformscripts' in scripts_map:
                    scripts_map['langscripts.lexemeformscripts'].append(script_name)
                else:
                    scripts_map['langscripts.lexemeformscripts']= [script_name]
            elif 'langscripts.glosslangs' in lex_field:
                if 'langscripts.glosslangs' in scripts_map:
                    scripts_map['langscripts.glosslangs'].append(script_name)
                else:
                    scripts_map['langscripts.glosslangs']= [script_name]
                # scripts_map.get('langscripts.glosslangs', []).append(script_name)
        # print(f"{'-'*80}\nIN get_scripts_map(lex_fields) function\n\nscript_map:\n{scripts_map}")
        
        return scripts_map



    def map_lift(file_stream, field_map, lex_fields):
        # print(f"{'-'*80}\nIN map_lift(file_stream, field_map, lex_fields) function\n")
        mapped_lift = {}
        all_mapped = True

        life_scripts_map = get_scripts_map(lex_fields)
        print (life_scripts_map)

        if len(field_map) == 0:
            field_map = get_lift_map()
        
        # print(f"{'-'*80}\nget_lift_map():\n{field_map}")
        # print(f"{'-'*80}\nFILE STREAM TYPE:{type(file_stream)}")
        # exit()
        # tree = ET.parse(file_stream)
        root = ET.fromstring(file_stream)
        # print(f"TYPE OF TREE: {type(tree)}")
        # exit()
        # root = tree.getroot()
        # print(f"{'-'*80}\nroot:\n{root}")
        # exit()
        entries = root.findall('.//entry')
        # print(f"entries:\n{entries}")
        # exit()
        mapped_life_langs_lexeme_form = []
        unmapped_lift_langs_lexeme_form = []

        mapped_life_langs_gloss = []
        unmapped_lift_langs_gloss = []

        life_headword_script = life_scripts_map['langscripts.headwordscript']
        life_lexeme_form_scripts = life_scripts_map['langscripts.lexemeformscripts']
        life_gloss_langs = life_scripts_map['langscripts.glosslangs']

        highest_sense_num = 0
        for entry in entries:
            # pd_row = {}
            for entry_part in entry:
                sense_num = 0
                entry_part_tag = entry_part.tag
                if entry_part_tag != 'entry':
                    # print (entry_part_tag)
                    if entry_part_tag == 'lexical-unit':
                        life_key_headword = field_map[entry_part_tag]

                        # lift_tag_other_lexemes = entry_part_tag+'-form'
                        # life_key_other_lexemes = field_map[lift_tag_other_lexemes]

                        for wordform in entry_part:
                            lift_script_name, lift_lang_name = get_script_name(wordform)
                            # lift_tag = entry_part_tag + '.' + lift_lang_name
                            # lift_tag = './/entry/lexical-unit/form[@lang='+lift_lang_name+']/text'
                            # lift_tag = './lexical-unit/form[@lang='+lift_lang_name+']/text'
                            lift_tag = './lexical-unit/form[@lang="'+lift_lang_name+'"]'

                            if lift_script_name == life_headword_script:
                                if lift_tag not in mapped_lift:
                                    mapped_lift[lift_tag] = life_key_headword
                                
                                if lift_script_name not in mapped_life_langs_lexeme_form:
                                    mapped_life_langs_lexeme_form.append(lift_script_name)

                            elif lift_script_name in life_lexeme_form_scripts:                            
                                # mapped_lift[lift_tag] = life_key_other_lexemes+'.'+lift_script_name
                                mapped_lift[lift_tag] = lift_script_name
                                if lift_script_name not in mapped_life_langs_lexeme_form:
                                    mapped_life_langs_lexeme_form.append(lift_script_name)

                            else:
                                if lift_tag not in unmapped_lift_langs_lexeme_form:
                                    unmapped_lift_langs_lexeme_form.append(lift_tag)
                                # mapped_lift[other_lexeme_forms] = lexeme_form_scripts


                        #     print ('Script', script_name)
                        #     # txt = wordform[0].text
                        #     life_val = life_key #+'.'+script_name
                        #     entry_part_tag = entry_part_tag + '.' + script_name
                        #     other_entries = other_entries + '.' + script_name
                        #     if entry_part_tag not in mapped_lift:
                        #         mapped_lift[entry_part_tag] = life_val
                        #     else:
                        #         old_val = mapped_lift[entry_part_tag]
                        #         if life_val not in old_val:
                        #             life_val_other = life_val.replace(life_key, life_key_other)

                        #             if type(old_val) == str:
                        #                 life_val_other_old = old_val.replace(life_key, life_key_other)
                        #                 life_val_other = [life_val_other_old, life_val_other]
                        #                 old_val = [old_val, life_val]
                        #                 mapped_lift[entry_part_tag] = old_val
                        #                 mapped_lift[other_entries] = life_val_other
                        #             else:
                        #                 mapped_lift[entry_part_tag].append(old_val)
                        #                 mapped_lift[other_entries].append(life_val_other)
                        # # else:
                        # #     script_name = get_script_name(wordforms[0])
                        # #     print ('Script', script_name)
                        # #     mapped_lift[entry_part_tag] = life_key+'.'+script_name
                    elif entry_part_tag == 'sense':
                        sense_num += 1
                        
                        if sense_num > highest_sense_num:
                            highest_sense_num = sense_num

                        for sense_part in entry_part:                        
                            sense_part_tag = sense_part.tag             
                            # print (sense_part_tag)
                            life_key_sense = field_map[sense_part_tag]

                            if sense_part_tag == 'gloss' or sense_part_tag == 'definition' or sense_part_tag == 'example':
                                lift_lang_name, lift_full_lang = get_script_name(sense_part)
                                # lift_sense_tag = sense_part_tag + '.' + lift_lang_name
                                # lift_sense_tag = './/entry/sense/'+sense_part_tag+'[@lang='+lift_full_lang+']'
                                # lift_sense_tag = './sense/'+sense_part_tag+'[@lang='+lift_full_lang+']/text'
                                lift_sense_tag = './sense/'+sense_part_tag+'[@lang="'+lift_full_lang+'"]'
                                
                                if lift_lang_name in life_gloss_langs:
                                    mapped_lift[lift_sense_tag] = 'SenseNew.Sense '+str(sense_num)+'.'+life_key_sense + '.' + lift_lang_name
                                    if lift_lang_name not in mapped_life_langs_gloss:
                                        mapped_life_langs_gloss.append(lift_lang_name)
                                else:
                                    if lift_sense_tag not in unmapped_lift_langs_gloss:
                                        unmapped_lift_langs_gloss.append(lift_sense_tag)
                            elif sense_part_tag == 'grammatical-info':
                                life_key = field_map.get(sense_part_tag, [])
                                # lift_tag = './/entry/sense/'+sense_part_tag
                                print (entry_part[0].tag)
                                # gram_categ = entry_part[0].attrib['value']

                                lift_tag = './sense/'+sense_part_tag#+'[@value="'+gram_categ+'"]'
                                if lift_tag not in mapped_lift:
                                    mapped_lift[lift_tag] = life_key
                            else:
                                life_key = field_map.get(sense_part_tag, [])
                                # lift_tag = './/entry/sense/'+sense_part_tag
                                lift_tag = './sense/'+sense_part_tag
                                mapped_lift[lift_tag] = 'SenseNew.Sense '+str(sense_num)+'.'+life_key_sense
                    
                    elif entry_part_tag == 'pronunciation':
                        life_key_pron = field_map[entry_part_tag]
                        for pronform in entry_part:
                            lift_lang_name, lift_full_lang = get_script_name(pronform)
                            lift_pron_tag = './pronunciation/form[@lang="'+lift_full_lang+'"]'
                            mapped_lift[lift_pron_tag] = life_key_pron
                    
                    # elif entry_part_tag == 'grammatical-info':
                    #     life_key_gr = field_map[entry_part_tag]
                    #     gram_categ = entry_part.attrib['value']
                    #     lift_gr_tag = './grammatical-info[@value="'+gram_categ+'"]'
                    #     mapped_lift[lift_gr_tag] = life_key_gr
                                
                    else:
                        if 'trait' not in entry_part_tag:
                            life_key = field_map.get(entry_part_tag, [])
                            # lift_entry_tag = './/entry/'+entry_part_tag
                            lift_entry_tag = './'+entry_part_tag
                            mapped_lift[lift_entry_tag] = life_key
                # elif entry_part_tag == 'gloss':
        
        mapped_life_langs_lexeme_form_set = set(mapped_life_langs_lexeme_form)
        all_life_lexeme_form_scripts = set(life_lexeme_form_scripts)
        life_unmapped_lexeme_forms = all_life_lexeme_form_scripts - mapped_life_langs_lexeme_form_set
        # unmapped_lift_langs_lexeme_form = []
        

        mapped_life_langs_gloss_set = set(mapped_life_langs_gloss)
        all_life_gloss_langs = set(life_gloss_langs)
        life_unmapped_gloss_langs = all_life_gloss_langs - mapped_life_langs_gloss_set
        # unmapped_lift_langs_gloss = []
        # print ('Unmapped gloss', unmapped_lift_langs_gloss)

        headword_mapped = False
        life_all_mapped = mapped_lift.values()
        for life_key_mapped in life_all_mapped:
            if 'headword' in life_key_mapped:
                headword_mapped = True

        # if headword_mapped:
        for lift_unmapped_lexeme_form in unmapped_lift_langs_lexeme_form:
            # lift_unmapped_entry = './/entry/lexical-unit/form[@lang='+lift_unmapped_lexeme_form+']/text'
            mapped_lift[lift_unmapped_lexeme_form] = list(life_unmapped_lexeme_forms)

        for lift_unmapped_gloss in unmapped_lift_langs_gloss:
            mapped_lift[lift_unmapped_gloss] = list(life_unmapped_gloss_langs)

        # print (mapped_lift)
        # print (headword_mapped)

        if len (unmapped_lift_langs_lexeme_form) > 0 or len(unmapped_lift_langs_gloss) > 0:
            all_mapped = False
        
        # print(f"{'-'*80}\nheadword_mapped:\n{headword_mapped}\nall_mapped:\n{all_mapped}\nmapped_lift:\n{mapped_lift}\nroot:\n{root}")

        return headword_mapped, all_mapped, mapped_lift, root


    def get_sense_col(lift_tag, field_name, lang_name):
        all_cols = []
        sense_num = 0
        for sense in lift_tag:
            sense_num+=1
            df_col = 'SenseNew.Sense '+str(sense_num)+'.'+field_name+'.'+lang_name
            all_cols.append(df_col)
        return all_cols


    def lift_to_df (root, field_map, lex_fields):
        # print(f"{'-'*80}\nIN lift_to_df (root, field_map, lex_fields) function\n")
        data = pd.DataFrame(columns=lex_fields)
        # lex_fields_without_sense = [lex_field for lex_field in lex_fields if 'sense' not in lex_field]

        life_scripts_map = get_scripts_map(lex_fields)
        print (life_scripts_map)

        # if len(field_map) == 0:
        lift_life_field_map = get_lift_map()
        # print(f"{'-'*80}\nIN lift_to_df (root, field_map, lex_fields) function: get_lift_map():\n{lift_life_field_map}")
        
        # tree = ET.parse(file_stream)
        # root = tree.getroot()
        entries = root.findall('.//entry')

        # mapped_life_langs_lexeme_form = []
        # unmapped_lift_langs_lexeme_form = []

        # mapped_life_langs_gloss = []
        # unmapped_lift_langs_gloss = []

        # life_headword_script = life_scripts_map['langscripts.headwordscript']
        # life_lexeme_form_scripts = life_scripts_map['langscripts.lexemeformscripts']
        # life_gloss_langs = life_scripts_map['langscripts.glosslangs']

        print (f"{'-'*80}\nIN lift_to_df (root, field_map, lex_fields) function: {field_map}")

        # highest_sense_num = 0
        for entry in entries:
            df_row = {}
            for lift_tag, life_key in field_map.items():
                if len(life_key) > 0:
                    if 'lexical-unit' in lift_tag:
                        # txt = entry.findall(lift_tag+'/text').text
                        # print (lift_tag)
                        txt_entry = entry.find(lift_tag+'/text')

                        if not txt_entry is None:
                            txt = txt_entry.text
                        
                        if 'headword' in life_key:
                            df_row['headword'] = txt
                        else:
                            df_row['Lexeme Form.'+life_key] = txt
                    
                    elif 'pronunciation' in lift_tag:
                        txt_entry = entry.find(lift_tag+'/text')
                        # life_key = lift_life_field_map[lift_tag]

                        if not txt_entry is None:
                            txt = txt_entry.text
                            

                        df_row[life_key] = txt

                    elif '@lang' in lift_tag:
                        sense_num = 0
                        all_sense = entry.findall(lift_tag)
                        for sense in all_sense:
                            sense_num+=1                    
                            if 'gloss' in lift_tag:
                                life_key_name = lift_life_field_map['gloss']
                            elif 'definition' in lift_tag:
                                life_key_name = lift_life_field_map['definition']
                            elif 'example' in lift_tag:
                                life_key_name = lift_life_field_map['example']

                            # print (sense.tag)
                            txt_entry = sense.find('text')

                            if not txt_entry is None:
                                txt = txt_entry.text

                            df_col = 'SenseNew.Sense '+str(sense_num)+'.'+life_key_name+'.'+life_key
                            df_row[df_col] = txt
                    
                    elif 'grammatical-info' in lift_tag:
                        gram_info_tag = entry.find(lift_tag)
                        # print ('Grammar tag', gram_info_tag, gram_info_tag.tag)
                        # life_key = lift_life_field_map[lift_tag]

                        if not gram_info_tag is None:
                            try:
                                gram_info = gram_info_tag.attrib['value']
                            # print ('Gram info', gram_info)
                            except:
                                gram_info = ''
                        
                        df_row[life_key] = gram_info
                    
                    else:
                        # print (lift_tag)
                        txt_entry = entry.find(lift_tag)
                        life_key = lift_life_field_map[lift_tag]

                        if not txt_entry is None:
                            txt = txt_entry.text
                            

                        df_row[life_key] = txt

            data = data.append(df_row, ignore_index=True)
        
        data.fillna('', inplace=True)
        
        headword_mapped = True
        all_mapped = True

        # data.to_csv(os.path.join(basedir, 'testliftXML.tsv'), sep='\t', index=False)

        # print(f"{'-'*80}\nIN lift_to_df (root, field_map, lex_fields) FUNCTION\n\nheadword_mapped\n{headword_mapped}\n\nall_mapped:\n{all_mapped}\n\ndata:\n{data}\n\nroot:\n{root}")
        # print(f"{'-'*80}\nIN lift_to_df (root, field_map, lex_fields) FUNCTION\n\nheadword_mapped\n{type(headword_mapped)}\n\nall_mapped:\n{type(all_mapped)}\n\ndata:\n{type(data)}\n\nroot:\n{type(root)}")

        return headword_mapped, all_mapped, data, root


    def prepare_lex(lexicon):
        df = pd.json_normalize(lexicon)
        columns = df.columns
        # drop_cols = [c for c in df.columns if c.startswith('langscripts.')]
        drop_cols = []
        drop_cols.append ('lexemedeleteFLAG')
        # drop_cols.append ('grammaticalcategory')
        drop_cols.append ('projectname')

        if 'gloss' in columns:
            drop_cols.append ('gloss')
        drop_oldsense = [c for c in df.columns if c.startswith('Sense.')]
        drop_oldvariant = [c for c in df.columns if c.startswith('Variant.')]
        drop_oldallomorph = [c for c in df.columns if c.startswith('Allomorph.')]
        drop_oldscript = [c for c in df.columns if c.startswith('Lexeme Form Script')]
        drop_files = [c for c in df.columns if c.startswith('filesname.')]

        drop_cols.extend(drop_oldsense)
        drop_cols.extend(drop_oldvariant)
        drop_cols.extend(drop_oldallomorph)
        drop_cols.extend(drop_oldscript)
        drop_cols.extend(drop_files)

        df.drop(columns=drop_cols, inplace=True)

        return df


    def generate_all_possible_mappings(key_cols, val_cols):
        final_map = {}
        for key_col in key_cols:
            final_map[key_col] = list(val_cols)
        # print(f"{'-'*80}\nIN generate_all_possible_mappings(key_cols, val_cols) function\nFINAL MAP:\n{final_map}")
        return final_map


    def map_excel(file_stream, lex_fields):
        # print(f"{'-'*80}\nIN MAP EXCEL function map_excel(file_stream, lex_fields)")
        excel_data = pd.read_excel(file_stream, engine="openpyxl")
        # print(excel_data)
        excel_data_cols = set(excel_data.columns)
        lex_field_cols = set(lex_fields)
        # print(f"{'-'*80}\nexcel_data_cols:\n{excel_data.columns}")
        # print(f"{'-'*80}\nNUMBER OF ELEMENTS IN excel_data_cols: {len(excel_data_cols)}")
        # print(f"{'-'*80}\nNUMBER OF ELEMENTS IN lex_field_cols: {len(lex_field_cols)}")

        # print(f"{'-'*80}\nlex_field_cols-excel_data_cols:\n{lex_field_cols-excel_data_cols}")

        if excel_data_cols == lex_field_cols:
            # print(f"{'-'*80}\nexcel_data_cols == lex_field_cols")
            mapped = True
            headword_mapped = True
            return headword_mapped, mapped, {}, excel_data
        else:
            # print(f"{'-'*80}\nexcel_data_cols != lex_field_cols")
            headword_mapped = True
            mapped = False
            excel_remaining = excel_data_cols - lex_field_cols
            lex_remaining = lex_field_cols - excel_data_cols
            # print(f"{'-'*80}\nexcel_remaining:\n{excel_remaining}\n{'-'*80}\nlex_remaining:\n{lex_remaining}")
            field_map = generate_all_possible_mappings(excel_remaining, lex_remaining)
            # print(f"{'-'*80}\nheadword_mapped\n{headword_mapped}\n\nmapped:\n{mapped}\n\nfield_map:\n{field_map}\n\nexcel_data:\n{excel_data}")
            return headword_mapped, mapped, field_map, excel_data


    def upload_excel (excel_data, field_map, lex_fields):
        # excel_data = pd.read_excel(file_stream)
        final_data = excel_data.rename(columns=field_map)
        mapped = True
        headword_mapped = True

        return headword_mapped, mapped, final_data


    def upload_lexicon(lexicon, file_stream, format, field_map):
        lexicon = lexicon[1:]
        # print(f"{'-'*80}\nLEXICON:\n{lexicon}")
        norm_lex = prepare_lex(lexicon)
        # print(f"{'-'*80}\nNORM LEX:\n{norm_lex}")
        lex_fields = norm_lex.columns
        # print(f"{'-'*80}\nLEX FIELDS:\n{lex_fields}")
        # print(f"{'-'*80}\nFILE STREAM TYPE:{type(file_stream)}")

        if format == 'lift-xml':
            # print(f"{'-'*80}\nFIELD MAP:\n{len(field_map)}")
            if len(field_map) == 0:
                # print(f"{'-'*80}\nlift-xml: len(field_map) == 0")
                
                headword_mapped, all_mapped, field_map, root = map_lift(file_stream, field_map, lex_fields)
                
                if headword_mapped and all_mapped:
                    # print(f"{'-'*80}\nheadword_mapped and all_mapped")
                    headword_mapped, all_mapped, data, root = lift_to_df (root, field_map, lex_fields)
                    # print(f"{'-'*80}\nheadword_mapped:\n{type(headword_mapped)}\nall_mapped:\n{type(all_mapped)}\nmapped_lift/data:\n{type(data)}\nroot:\n{type(root)}")
                    return headword_mapped, all_mapped, data, root
                else:
                    # print(f"{'-'*80}\nheadword_mapped and all_mapped: NOT")
                    # print(f"{'-'*80}\nheadword_mapped:\n{type(headword_mapped)}\nall_mapped:\n{type(all_mapped)}\nmapped_lift/data:\n{type(field_map)}\nroot:\n{type(root)}")
                    return headword_mapped, all_mapped, field_map, root
            else:
                # print(f"{'-'*80}\nlift-xml: len(field_map) != 0")
                headword_mapped, all_mapped, life_df, root = lift_to_df (file_stream, field_map, lex_fields)
                # print (life_df.head())
                # print(life_df.loc[0,:])
                return headword_mapped, all_mapped, life_df
        elif format == 'xlsx':
            if len(field_map) == 0:
                # print(f"{'-'*80}\nxlsx: len(field_map) == 0")
                headword_mapped, all_mapped, field_map, df = map_excel(file_stream, lex_fields)
                return headword_mapped, all_mapped, field_map, df
            else:
                # print(f"{'-'*80}\nxlsx: len(field_map) != 0")
                headword_mapped, all_mapped, data = upload_excel(file_stream, field_map, lex_fields)
                return headword_mapped, all_mapped, data

    working_dir = basedir    
    # upload_file = os.path.join(working_dir, 'LiFE.lift')
    upload_file = uploadedFileContent
    # print(upload_file)
    # format = 'lift-xml'
    format = fileFormat
    # print(f"{'-'*80}\nFILE FORMAT:{fileFormat}")
    with open(os.path.join(working_dir, 'lexemeEntry.json')) as f_r:
        lex = json.load(f_r)

    return upload_lexicon(lex, upload_file, format, field_map)

# upload lexeme form in excel/liftXML format
@app.route('/uploadlexemeexcelliftxml', methods=['GET', 'POST'])
def uploadlexemeexcelliftxml():
    if request.method == 'POST':
        lexkeymapping = dict(request.form.lists())
        # lexkeymapping = lexkeymapping.keys().decode('unicode-escape')
        # print(lexkeymapping)
        # print(type(lexkeymapping))
        lexkeymappingNew = {}
        for key, value in lexkeymapping.items():
            key = key.replace('%22', '"')
            lexkeymappingNew[key] = value[0]
        # print(lexkeymappingNew)
        field_map = lexkeymappingNew
        life_uploaded_file_content_path = os.path.join(basedir, 'lifeUploadedFileContent.pkl')
        # Open the file in binary mode
        with open(life_uploaded_file_content_path, 'rb') as file:
            retrieve_uploaded_file_content = pickle.load(file)
            # print(retrieve_uploaded_file_content.keys())
            file_format = retrieve_uploaded_file_content['file_format']
            uploaded_file_content = retrieve_uploaded_file_content['uploaded_file_content']
        if (file_format == 'lift-xml'):
            life_lift_root_path = os.path.join(basedir, 'lifeliftroot.xml')
            tree = ET.parse(life_lift_root_path)
            root = tree.getroot()
            # print(f"{'-'*80}\nIN uploadlexemeexcelliftxml() FUNCTION\n\nfile_format\n{file_format}\n\nfield_map:\n{field_map}\n\nroot:\n{root}")
            # print(f"{'-'*80}\nIN uploadlexemeexcelliftxml() FUNCTION\n\nfile_format\n{type(file_format)}\n\nfield_map:\n{type(field_map)}\n\nroot:\n{type(root)}")
            headword_mapped, all_mapped, life_df = lifeuploader(file_format, root, field_map)
            # print(f"{'-'*80}\nIN uploadlexemeexcelliftxml() FUNCTION\n\nheadword_mapped\n{headword_mapped}\n\nall_mapped:\n{all_mapped}\n\nlife_df:\n{life_df}\n\nroot:\n{root}")
            # print(f"{'-'*80}\nIN uploadlexemeexcelliftxml() FUNCTION\n\nheadword_mapped\n{type(headword_mapped)}\n\nall_mapped:\n{type(all_mapped)}\n\nlife_df:\n{type(life_df)}\n\nroot:\n{type(root)}")
        elif (file_format == 'xlsx'):
            life_xlsx_root_path = os.path.join(basedir, 'lifexlsxdf.tsv')
            df = pd.read_csv(life_xlsx_root_path, sep='\t', dtype=str)
            headword_mapped, all_mapped, data = lifeuploader(file_format, df, field_map)
            # print(f"{'-'*80}\nIN uploadlexemeexcelliftxml() FUNCTION\n\nheadword_mapped\n{headword_mapped}\n\nall_mapped:\n{all_mapped}\n\ndata:\n{data}\n\ndf:\n{df}")
            # print(f"{'-'*80}\nIN uploadlexemeexcelliftxml() FUNCTION\n\nheadword_mapped\n{type(headword_mapped)}\n\nall_mapped:\n{type(all_mapped)}\n\ndata:\n{type(data)}\n\ndf:\n{type(df)}")

        if (not headword_mapped):
            flash("headword is missing from the file")
            return redirect(url_for('enternewlexeme'))
        
        elif (not all_mapped and len(field_map) != 0):
            not_mapped_data = field_map
            # print('create a modal/page where user can give the mapping of the columns')
            return render_template('lexemekeymapping.html', not_mapped_data=not_mapped_data)
        else:
            if (file_format == 'lift-xml'):
                enterlexemefromuploadedfile(life_df)    
            elif (file_format == 'xlsx'):
                enterlexemefromuploadedfile(data)

    return redirect(url_for('enternewlexeme'))

# lexeme key mapping
@app.route('/lexemekeymapping', methods=['GET', 'POST'])
def lexemekeymapping():
    # getting the collections
    projects, userprojects, lexemes = getdbcollections.getdbcollections(mongo,
                                                'projects',
                                                'userprojects',
                                                'lexemes')
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                            userprojects)
    projectname =  activeprojectname
    lst = []
    lst.append({'projectname': activeprojectname})
    for lexeme in lexemes.find({'projectname' : projectname, 'lexemedeleteFLAG' : 0}, {'_id' : 0 }):
        lst.append(lexeme)

    # pprint(lst)
    # Serializing json  
    json_object = json.dumps(lst, indent = 2, ensure_ascii=False)

    with open(basedir+"/lexemeEntry.json", "w") as outfile:
        outfile.write(json_object)
            
    if request.method == 'POST':
        newLexemeFiles = request.files.to_dict()
        # print(newLexemeFiles)
        key = 'Upload Excel LiftXML'
        # print(type(newLexemeFiles[key].read()))
        if newLexemeFiles[key].filename != '':
            filename = newLexemeFiles[key].filename
            # print(filename)
            file_format = filename.rsplit('.', 1)[-1]
            if (file_format == 'xlsx' or file_format == 'lift'):
                uploaded_file_content = newLexemeFiles[key].read()
                if (file_format == 'lift'):
                    file_format = file_format+'-xml'
                    uploaded_file_content = str(uploaded_file_content, 'UTF-8')
                # print(file_format)    
                pass
                # flash(f"File format is correct")
                # return redirect(url_for('enternewlexeme'))
            else:
                flash("File should be in 'xlsx' or 'lift' format")
                return redirect(url_for('enternewlexeme'))
        # print("File format is correct")

        # df = pd.read_excel(uploaded_file_content)
        # print(df)
        # save uploaded file details in pickle file for future use
        store_uploaded_file_content = {}
        store_uploaded_file_content['file_format'] = file_format
        store_uploaded_file_content['uploaded_file_content'] = uploaded_file_content
        life_uploaded_file_content_path = os.path.join(basedir, 'lifeUploadedFileContent.pkl')
        with open(life_uploaded_file_content_path, 'wb') as file:
            pickle.dump(store_uploaded_file_content, file)
        if (file_format == 'lift-xml'):
            headword_mapped, all_mapped, field_map, root = lifeuploader(file_format, uploaded_file_content, field_map={})
            # print(f"{'-'*80}\nIN lexemekeymapping() FUNCTION\n\nheadword_mapped\n{headword_mapped}\n\nall_mapped:\n{all_mapped}\n\nfield_map:\n{field_map}\n\nroot:\n{root}")
            # print(f"{'-'*80}\nIN lexemekeymapping() FUNCTION\n\nheadword_mapped\n{type(headword_mapped)}\n\nall_mapped:\n{type(all_mapped)}\n\nfield_map:\n{type(field_map)}\n\nroot:\n{type(root)}")
            tree = ElementTree(root)
            life_lift_root_path = os.path.join(basedir, 'lifeliftroot.xml')
            with open(life_lift_root_path, 'wb') as f:
                tree.write(f, encoding='utf-8')
        elif (file_format == 'xlsx'):
            headword_mapped, all_mapped, field_map, df = lifeuploader(file_format, uploaded_file_content, field_map={})
            # print(f"{'-'*80}\nIN lexemekeymapping() FUNCTION\n\nheadword_mapped\n{headword_mapped}\n\nall_mapped:\n{all_mapped}\n\nfield_map:\n{field_map}\n\ndf:\n{df}")
            # print(f"{'-'*80}\nIN lexemekeymapping() FUNCTION\n\nheadword_mapped\n{type(headword_mapped)}\n\nall_mapped:\n{type(all_mapped)}\n\nfield_map:\n{type(field_map)}\n\ndf:\n{type(df)}")
            life_xlsx_root_path = os.path.join(basedir, 'lifexlsxdf.tsv')
            df.to_csv(life_xlsx_root_path, sep='\t', index=False)

        # headword_mapped = True
        # all_mapped = False
        if (not headword_mapped):
            flash("headword is missing from the file")
            return redirect(url_for('enternewlexeme'))
        
        elif (not all_mapped and len(field_map) != 0):
            # not_mapped_data = {
            #     './pronunciation/form[@lang="anp-Deva"]': 'Pronunciation', 
            #     './sense/grammatical-info': 'grammaticalcategory', 
            #     './lexical-unit/form[@lang="anp-Deva"]': ['Beng', 'Mlym'], 
            #     './sense/gloss[@lang="anp"]': ['Odi', 'Ass', 'Eng'], 
            #     './sense/gloss[@lang="en"]': ['Odi', 'Ass', 'Eng']
            # }
            not_mapped_data = field_map
            # print('create a modal/page where user can give the mapping of the columns')
            return render_template('lexemekeymapping.html', not_mapped_data=not_mapped_data)
        else:
            if (file_format == 'xlsx'):
                enterlexemefromuploadedfile(df)
        
    return redirect(url_for('enternewlexeme'))
    

# download lexeme form in excel format
@app.route('/downloadlexemeformexcel', methods=['GET', 'POST'])
def downloadlexemeformexcel():
    # getting the collections
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    lexemes = mongo.db.lexemes                          # collection containing entry of each lexeme and its details

    activeprojectname = userprojects.find_one({ 'username' : current_user.username })['activeprojectname']
    projectname =  activeprojectname
    lst = []
    lst.append({'projectname': activeprojectname})
    for lexeme in lexemes.find({'projectname' : projectname, 'lexemedeleteFLAG' : 0}, {'_id' : 0 }):
        if (len(lexeme['headword']) != 0):
            lst.append(lexeme)

    # pprint(lst)
    # Serializing json  
    json_object = json.dumps(lst, indent = 2, ensure_ascii=False)

    with open(basedir+"/lexemeEntry.json", "w") as outfile: 
            outfile.write(json_object) 

    def preprocess_csv_excel(lexicon):
        # pprint(lexicon)
        df = pd.json_normalize(lexicon)
        columns = df.columns
        drop_cols = [c for c in df.columns if c.startswith('langscripts.')]
        drop_cols.append ('lexemedeleteFLAG')
        drop_cols.append ('grammaticalcategory')
        drop_cols.append ('projectname')

        if 'gloss' in columns:
            drop_cols.append ('gloss')
        drop_oldsense = [c for c in df.columns if c.startswith('Sense.')]
        drop_oldvariant = [c for c in df.columns if c.startswith('Variant.')]
        drop_oldallomorph = [c for c in df.columns if c.startswith('Allomorph.')]
        drop_oldscript = [c for c in df.columns if c.startswith('Lexeme Form Script')]
        drop_files = [c for c in df.columns if c.startswith('filesname.')]

        drop_cols.extend(drop_oldsense)
        drop_cols.extend(drop_oldvariant)
        drop_cols.extend(drop_oldallomorph)
        drop_cols.extend(drop_oldscript)
        drop_cols.extend(drop_files)

        # print(list(df.columns))
        # print(drop_cols)
        df.drop(columns=drop_cols, inplace=True)

        return df

    def generate_xlsx(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        # df.drop([0], inplace=True)
        f_w = open (write_path, 'wb')
        df.to_excel(f_w, index=False, engine='xlsxwriter')

    def download_lexicon(lex_json, write_path, 
        output_format='xlsx'):
        file_ext_map = {'xlsx': '.xlsx'}
        
        # pprint(lex_json)
        metadata = lex_json[0]
        project = metadata['projectname']

        lexicon = lex_json[1:]
        # pprint(lexicon)
        if output_format == 'xlsx':
            file_ext = file_ext_map[output_format]
            write_file = os.path.join(write_path, 'lexicon_'+project+file_ext)
            generate_xlsx(write_file, lexicon)
        else:
            print ('File type\t', output_format, '\tnot supported')
            print ('Supported File Types', file_ext_map.keys())        

    lexeme_dir = basedir
    working_dir = basedir+'/download'
    with open(os.path.join(lexeme_dir, 'lexemeEntry.json')) as f_r:
        lex = json.load(f_r)
        # pprint(lex)
        out_form = 'xlsx'
        download_lexicon(lex, working_dir, out_form)

    files = glob.glob(basedir+'/download/*')
     
    with ZipFile('download.zip', 'w') as zip:
        # writing each file one by one 
        for file in files: 
            zip.write(file, os.path.join(projectname, os.path.basename(file)))
    print('All files zipped successfully!')

    # deleting all files from storage
    for f in files:
        # print(f)
        os.remove(f)
    
    return send_file('../download.zip', as_attachment=True)
    # return 'OK'


# download route
@app.route('/downloadselectedlexeme', methods=['GET', 'POST'])
def downloadselectedlexeme():
    # getting the collections
    projects = mongo.db.projects                        # collection containing projects name
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    lexemes = mongo.db.lexemes                          # collection containing entry of each lexeme and its details
    # sentences = mongo.db.sentences                          # collection containing entry of each sentence and its details
    fs =  gridfs.GridFS(mongo.db)                       # creating GridFS instance to get required files

    ontolex = Namespace('http://www.w3.org/ns/lemon/ontolex#')
    lexinfo = Namespace('http://www.lexinfo.net/ontology/2.0/lexinfo#')
    dbpedia = Namespace('http://dbpedia.org/resource/')
    pwn = Namespace('http://wordnet-rdf.princeton.edu/rdf/lemma/')
    life = None

    lst = list()

    headwords = request.args.get('data')                   # data through ajax



    if headwords != None:
        headwords = eval(headwords)
    # print(f'{"="*80}\nheadwords from downloadselectedlexeme route:\n {headwords}\n{"="*80}')
    
    download_format = headwords['downloadFormat']
    # print(download_format)

    del headwords['downloadFormat']

    # print(f'{"="*80}\ndelete download format:\n {headwords}\n{"="*80}')

    activeprojectname = userprojects.find_one({ 'username' : current_user.username })['activeprojectname']
    lst.append({'projectname': activeprojectname})
    projectname =  activeprojectname
    
    # for headword in headwords:
    #     lexeme = lexemes.find_one({'username' : current_user.username, 'projectname' : projectname, 'headword' : headword},\
    #                         {'_id' : 0, 'username' : 0, 'projectname' : 0})
    #     lst.append(lexeme)
    # for lexemeId in headwords.keys():
    #     lexeme = lexemes.find_one({'projectname' : projectname, 'lexemeId' : lexemeId},\
    #                         {'_id' : 0})
    #     lst.append(lexeme)

    for lexemeId in headwords.keys():
        lexeme = lexemes.find_one({'projectname' : projectname, 'lexemeId' : lexemeId},\
                            {'_id' : 0 })
        lst.append(lexeme)
        # save current user mutimedia files of each lexeme to local storage
        files = fs.find({'projectname' : projectname, 'lexemeId' : lexemeId})
        for file in files:
            name = file.filename
            # open(basedir+'/app/download/'+name, 'wb').write(file.read())
            open(os.path.join(basedir,'download', name), 'wb').write(file.read())

    

    # Serializing json  
    json_object = json.dumps(lst, indent = 2, ensure_ascii=False)

    with open(basedir+"/lexemeEntry.json", "w") as outfile: 
            outfile.write(json_object) 

  
    # # writing to currentprojectname.json 
    # with open(basedir+"/download/"+projectname+".json", "w") as outfile: 
    #     outfile.write(json_object)
    

    def generate_json(lex_json):
        json_object = json.dumps(lex_json, indent = 2, ensure_ascii=False)
        # writing to currentprojectname.json 
        # with open(basedir+"/app/download/lexicon_"+activeprojectname+".json", "w") as outfile: 
        with open(basedir+"/download/lexicon_"+activeprojectname+".json", "w") as outfile: 
            outfile.write(json_object)  

    # # def test():
    # #     g = Graph()
    # #     semweb = URIRef('http://dbpedia.org/resource/Semantic_Web')
    # #     type = g.value(semweb, RDFS.label)

    # #     g.add((
    # #         URIRef("http://example.com/person/nick"),
    # #         FOAF.givenName,
    # #         Literal("Nick", datatype=XSD.string)
    # #     ))

    # #     g.bind("foaf", FOAF)
    # #     g.bind("xsd", XSD)

    # #     print(g.serialize(format="turtle"))


    # def add_canonical_form(g_form, life, lex_entry, lex_item, ipa, dict_lang):
    #     # g_form = Graph()
    #     # g_form.bind("ontolex", ontolex)
    #     # g_form.bind("life", life)

    #     g_form.add((
    #         URIRef(life[lex_item+'_form']),
    #         RDF.type,
    #         ontolex.form
    #     ))

    #     g_form.add((
    #         URIRef(life[lex_item+'_form']),
    #         ontolex.phoneticRep,
    #         Literal(ipa, lang="ipa")
    #     ))

    #     headword_script = list(lex_entry['langscripts']['headwordscript'])[0]
    #     print ('Headword script', headword_script)
    #     headword_lang = dict_lang+'-'+headword_script

    #     g_form.add((
    #         URIRef(life[lex_item+'_form']),
    #         ontolex.writtenRep,
    #         Literal(lex_item, lang=headword_lang)
    #     ))

    #     #If written reps are entered in other scripts, they are added
    #     other_scripts = lex_entry['langscripts']['lexemeformscripts']
    #     for other_script in other_scripts:
    #         lex_trans_forms = lex_entry['Lexeme Form']
    #         if other_script in lex_trans_forms:
    #             lex_trans = lex_trans_forms[other_script]
    #             g_form.add((
    #                 URIRef(life[lex_item+'_form']),
    #                 ontolex.writtenRep,
    #                 Literal(lex_trans, lang=dict_lang+'-'+other_script)
    #             ))
            

    # def add_definition(g_form, life, lex_entry, lex_item, sense_defn):
    #     defn_langs = lex_entry['langscripts']['glosslangs']
    #     for defn_lang in defn_langs:
    #         if defn_lang in sense_defn:
    #             lex_defn = sense_defn[defn_lang]
    #             g_form.add((
    #                 URIRef(life[lex_item]),
    #                 ontolex.denotes,
    #                 URIRef(life[lex_item+'_definition'])
    #             ))

    #             g_form.add((
    #                 URIRef(life[lex_item+'_definition']),
    #                 SKOS.definition,
    #                 Literal(lex_defn, lang=defn_lang)
    #             ))

    # def add_example(g_form, life, lex_item, example, ex_lang):
    #     g_form.add((
    #         URIRef(life[lex_item]),
    #         SKOS.example,
    #         Literal(example, lang=ex_lang)
    #     ))

    # # def add_other_forms(g_other_form, life, lex_entry, lex_item, other_form, dict_lang):
    # #     # g_other_form = Graph()
    # #     # g_other_form.bind("ontolex", ontolex)
    # #     # g_other_form.bind("life", life)

    # #     g_other_form.add((
    # #         URIRef(life[lex_item+'_otherForm']),
    # #         RDF.type,
    # #         ontolex.form
    # #     ))

    # #     g_other_form.add((
    # #         URIRef(life[lex_item+'_otherForm']),
    # #         ontolex.writtenRep,
    # #         Literal(other_form, lang=dict_lang)
    # #     ))


    # def add_sense(g_lex, life, lex_entry, sense_entry, lex_sense):
    #     g_lex.add((
    #         sense_entry,
    #         RDF.type,
    #         ontolex.LexicalSense
    #     ))

    #     if dbpedia_exists(lex_sense):
    #         g_lex.add((
    #             life[lex_entry],
    #             ontolex.denotes,
    #             dbpedia[lex_sense.capitalize()]
    #         ))

    #         g_lex.add((
    #             sense_entry,
    #             ontolex.reference,
    #             dbpedia[lex_sense.capitalize()]
    #         ))

    #     g_lex.add((
    #         sense_entry,
    #         ontolex.isSenseOf,
    #         life[lex_entry]
    #     ))
        

    #     wordnet_code = get_wordnet_code(lex_sense)
    #     if wordnet_code != '':
    #         g_lex.add((
    #             sense_entry,
    #             ontolex.isLexicalisedSenseOf,
    #             pwn[wordnet_code]
    #         ))
    #         g_lex.add((
    #             life[lex_entry],
    #             ontolex.evokes,
    #             pwn[wordnet_code]
    #         ))

    #     g_lex.add((
    #         sense_entry,
    #         ontolex.isSenseOf,
    #         life[lex_entry]
    #     ))

    #     #Creating dbpedia entry
    #     g_lex.add((
    #         dbpedia[lex_sense.capitalize()],
    #         ontolex.concept,
    #         pwn[wordnet_code]
    #     ))

    #     g_lex.add((
    #         dbpedia[lex_sense.capitalize()],
    #         ontolex.isReferenceOf,
    #         sense_entry
    #     ))

    #     g_lex.add((
    #         dbpedia[lex_sense.capitalize()],
    #         ontolex.isDenotedBy,
    #         ontolex.LexicalConcept
    #     ))


    #     #Creating WordNet entry
    #     g_lex.add((
    #         pwn[wordnet_code],
    #         RDF.type,
    #         life[lex_entry]
    #     ))
        
    #     g_lex.add((
    #         pwn[wordnet_code],
    #         ontolex.isEvokedBy,
    #         life[lex_entry]
    #     ))

    #     g_lex.add((
    #         pwn[wordnet_code],
    #         ontolex.lexicalizedSense,
    #         sense_entry
    #     ))

    #     g_lex.add((
    #         pwn[wordnet_code],
    #         ontolex.isConceptOf,
    #         dbpedia[lex_sense.capitalize()]
    #     ))


    # def get_wordnet_code(lex_gloss):
    #     query = '''
    #     ASK WHERE {
    #     {<my-specific-URI> ?p ?o . }
    #     UNION
    #     {?s ?p <my-specific-URI> . }
    #     }
    #     '''
    #     return lex_gloss

    # def dbpedia_exists(lex_gloss):
    #     query = '''
    #     ASK WHERE {
    #     {<my-specific-URI> ?p ?o . }
    #     UNION
    #     {?s ?p <my-specific-URI> . }
    #     }
    #     '''
    #     return True

    # def json_to_rdf_lexicon(g_lex, lex_entry, domain_name,
    #                         project, output_format='turtle'):

    #     lex_item = lex_entry['headword']
    #     lex_pos = lex_entry['grammaticalcategory']
    #     # can_form = lex_item
    #     lex_pron = lex_entry['Pronunciation']
    #     lex_sense = lex_entry['SenseNew']
    #     dict_lang = lex_entry['langscripts']['langcode']

    #     # ontolex = URIRef('http://www.w3.org/ns/lemon/ontolex#')
    #     # lexinfo = URIRef('http://www.lexinfo.net/ontology/2.0/lexinfo#')

    #     life = Namespace(domain_name+'/'+project + '/word/')    

    #     g_lex.bind("ontolex", ontolex)
    #     g_lex.bind("lexinfo", lexinfo)
    #     g_lex.bind("skos", SKOS)
    #     g_lex.bind("life", life)
    #     g_lex.bind("pwnlemma", pwn)
    #     g_lex.bind("dbpedia", dbpedia)


    #     g_lex.add((
    #         URIRef(life[lex_item]),
    #         RDF.type,
    #         lexinfo.LexicalEntry
    #     ))

    #     g_lex.add((
    #         URIRef(life[lex_item]),
    #         lexinfo.partOfSpeech,
    #         lexinfo[lex_pos]
    #     ))

    #     # g_lex.add((
    #     #     URIRef(life[lex_item]),
    #     #     ontolex.lexicalForm,
    #     #     URIRef(life[lex_item+'_form'])
    #     # ))

    #     g_lex.add((
    #         URIRef(life[lex_item]),
    #         ontolex.canonicalForm,
    #         URIRef(life[lex_item+'_form'])
    #     ))

    #     # Add graph for the canonical form
    #     add_canonical_form(g_lex, life, lex_entry, lex_item, lex_pron, dict_lang)

    #     for i in range(1, len(lex_sense)):
    #         sense_gloss = lex_sense['Sense '+str(i)]["Gloss"]["eng"]
    #         sense_defn = lex_sense['Sense '+str(i)]["Definition"]        
    #         sense_ex = lex_sense['Sense '+str(i)]["Example"]

    #         sense_entry = life[lex_item+'_sense'+str(i)]
    #         g_lex.add((
    #             URIRef(life[lex_item]),
    #             ontolex.sense,
    #             URIRef(sense_entry)
    #         ))
    #         add_sense(g_lex, life, lex_item, sense_entry, sense_gloss)
    #         add_definition(g_lex, life, lex_entry, lex_item, sense_defn)
    #         add_example(g_lex, life, lex_item, sense_ex, dict_lang)


    # def preprocess_csv_excel(lexicon):
    #     df = pd.json_normalize(lexicon)
    #     columns = df.columns
    #     drop_cols = [c for c in df.columns if c.startswith('langscripts.')]
    #     drop_cols.append ('lexemedeleteFLAG')
    #     drop_cols.append ('grammaticalcategory')
    #     drop_cols.append ('projectname')

    #     if 'gloss' in columns:
    #         drop_cols.append ('gloss')
    #     drop_oldsense = [c for c in df.columns if c.startswith('Sense.')]
    #     drop_oldvariant = [c for c in df.columns if c.startswith('Variant.')]
    #     drop_oldallomorph = [c for c in df.columns if c.startswith('Allomorph.')]
    #     drop_oldscript = [c for c in df.columns if c.startswith('Lexeme Form Script')]
    #     drop_files = [c for c in df.columns if c.startswith('filesname.')]

    #     drop_cols.extend(drop_oldsense)
    #     drop_cols.extend(drop_oldvariant)
    #     drop_cols.extend(drop_oldallomorph)
    #     drop_cols.extend(drop_oldscript)
    #     drop_cols.extend(drop_files)

    #     df.drop(columns=drop_cols, inplace=True)

    #     return df

    # def generate_rdf(write_path, lexicon, domain_name, project, rdf_format):
    #     g_lex = Graph()
        
    #     for lex_entry in lexicon:
    #         json_to_rdf_lexicon(g_lex, lex_entry, 
    #                         domain_name, project, rdf_format)
            
    #     with open (write_path, 'wb') as f_w:    
    #         rdf_out = g_lex.serialize(format=rdf_format)
    #         f_w.write(rdf_out)

    # def generate_csv(write_path, lexicon):
    #     df = preprocess_csv_excel(lexicon)
    #     with open (write_path, 'w') as f_w:
    #         df.to_csv(f_w, index=False)

    # def generate_xlsx(write_path, lexicon):
    #     df = preprocess_csv_excel(lexicon)
    #     f_w = open (write_path, 'wb')
    #     df.to_excel(f_w, index=False, engine='xlsxwriter')

    # def generate_ods(write_path, lexicon):
    #     df = preprocess_csv_excel(lexicon)
    #     f_w = open (write_path, 'wb')
    #     df.to_excel(f_w, index=False, engine='openpyxl')

    # def generate_html(write_path, lexicon):
    #     df = preprocess_csv_excel(lexicon)
    #     with open (write_path, 'w') as f_w:
    #         df.to_html(f_w, index=False)

    # def generate_latex(write_path, lexicon):
    #     df = preprocess_csv_excel(lexicon)
    #     with open (write_path, 'w') as f_w:
    #         df.to_latex(f_w, index=False)

    # def generate_markdown(write_path, lexicon):
    #     df = preprocess_csv_excel(lexicon)
    #     with open (write_path, 'w') as f_w:
    #         df.to_markdown(f_w, index=False)

    # def generate_pdf(write_path, lexicon, project):
    #     return None

    # def download_lexicon(lex_json, write_path, 
    #     output_format='rdf', rdf_format='turtle'):
    #     file_ext_map = {'turtle': '.ttl', 'n3': '.n3', 
    #     'ntriples': '.nt', 'rdfxml': '.rdf', 'json': '.json', 'csv': '.csv',
    #     'xlsx': '.xlsx', 'pdf': '.pdf', 'html': '.html', 'latex': '.tex',
    #     'markdown': '.md', 'ods': '.ods'}

    #     domain_name = 'http://lifeapp.in'
        
    #     pprint(lex_json)
    #     metadata = lex_json[0]
    #     project = metadata['projectname']

    #     lexicon = lex_json[1:]

    #     if (rdf_format in file_ext_map) or (output_format in file_ext_map):
    #         if output_format == 'rdf':
    #             file_ext = file_ext_map[rdf_format]
    #             write_file = os.path.join(write_path, 'lexicon_'+project+'_'+output_format+file_ext)
    #             generate_rdf(write_file, lexicon, domain_name, project, rdf_format)
    #         else:
    #             file_ext = file_ext_map[output_format]
    #             write_file = os.path.join(write_path, 'lexicon_'+project+file_ext)
    #             if output_format == 'csv':
    #                 generate_csv(write_file, lexicon)
    #             elif output_format == 'xlsx':
    #                 generate_xlsx(write_file, lexicon)
    #             elif output_format == 'pdf':
    #                 generate_pdf(write_file, lexicon)
    #             elif output_format == 'markdown':
    #                 generate_markdown(write_file, lexicon)
    #             elif output_format == 'html':
    #                 generate_html(write_file, lexicon)
    #             elif output_format == 'latex':
    #                 generate_latex(write_file, lexicon)
    #             elif output_format == 'ods':
    #                 generate_ods(write_file, lexicon)
    #             elif output_format == 'json':
    #                 generate_json(lex_json)
    #     else:
    #         print ('File type\t', output_format, '\tnot supported')
    #         print ('Supported File Types', file_ext_map.keys())        
                    
    def test():
        g = Graph()
        semweb = URIRef('http://dbpedia.org/resource/Semantic_Web')
        type = g.value(semweb, RDFS.label)

        g.add((
            URIRef("http://example.com/person/nick"),
            FOAF.givenName,
            Literal("Nick", datatype=XSD.string)
        ))

        g.bind("foaf", FOAF)
        g.bind("xsd", XSD)

        print(g.serialize(format="turtle"))


    def add_canonical_form(g_form, life, lex_entry, lex_item, ipa, dict_lang):
        # g_form = Graph()
        # g_form.bind("ontolex", ontolex)
        # g_form.bind("life", life)

        g_form.add((
            URIRef(life[lex_item+'_form']),
            RDF.type,
            ontolex.form
        ))

        g_form.add((
            URIRef(life[lex_item+'_form']),
            ontolex.phoneticRep,
            Literal(ipa, lang="ipa")
        ))

        headword_script = list(lex_entry['langscripts']['headwordscript'])[0]
        print ('Headword script', headword_script)
        headword_lang = dict_lang+'-'+headword_script

        g_form.add((
            URIRef(life[lex_item+'_form']),
            ontolex.writtenRep,
            Literal(lex_item, lang=headword_lang)
        ))

        #If written reps are entered in other scripts, they are added
        other_scripts = lex_entry['langscripts']['lexemeformscripts']
        for other_script in other_scripts:
            lex_trans_forms = lex_entry['Lexeme Form']
            if other_script in lex_trans_forms:
                lex_trans = lex_trans_forms[other_script]
                g_form.add((
                    URIRef(life[lex_item+'_form']),
                    ontolex.writtenRep,
                    Literal(lex_trans, lang=dict_lang+'-'+other_script)
                ))
            

    def add_definition(g_form, life, lex_entry, lex_item, sense_defn):
        defn_langs = lex_entry['langscripts']['glosslangs']
        for defn_lang in defn_langs:
            if defn_lang in sense_defn:
                lex_defn = sense_defn[defn_lang]
                g_form.add((
                    URIRef(life[lex_item]),
                    ontolex.denotes,
                    URIRef(life[lex_item+'_definition'])
                ))

                g_form.add((
                    URIRef(life[lex_item+'_definition']),
                    SKOS.definition,
                    Literal(lex_defn, lang=defn_lang)
                ))

    def add_example(g_form, life, lex_item, example, ex_lang):
        g_form.add((
            URIRef(life[lex_item]),
            SKOS.example,
            Literal(example, lang=ex_lang)
        ))

    def add_other_forms(g_other_form, life, lex_entry, lex_item, other_form, dict_lang):
        # g_other_form = Graph()
        # g_other_form.bind("ontolex", ontolex)
        # g_other_form.bind("life", life)

        g_other_form.add((
            URIRef(life[lex_item+'_otherForm']),
            RDF.type,
            ontolex.form
        ))

        g_other_form.add((
            URIRef(life[lex_item+'_otherForm']),
            ontolex.writtenRep,
            Literal(other_form, lang=dict_lang)
        ))


    def add_sense(g_lex, life, lex_entry, sense_entry, lex_sense):
        g_lex.add((
            sense_entry,
            RDF.type,
            ontolex.LexicalSense
        ))

        if dbpedia_exists(lex_sense):
            g_lex.add((
                life[lex_entry],
                ontolex.denotes,
                dbpedia[lex_sense.capitalize()]
            ))

            g_lex.add((
                sense_entry,
                ontolex.reference,
                dbpedia[lex_sense.capitalize()]
            ))

        g_lex.add((
            sense_entry,
            ontolex.isSenseOf,
            life[lex_entry]
        ))
        

        wordnet_code = get_wordnet_code(lex_sense)
        if wordnet_code != '':
            g_lex.add((
                sense_entry,
                ontolex.isLexicalisedSenseOf,
                pwn[wordnet_code]
            ))
            g_lex.add((
                life[lex_entry],
                ontolex.evokes,
                pwn[wordnet_code]
            ))

        g_lex.add((
            sense_entry,
            ontolex.isSenseOf,
            life[lex_entry]
        ))

        #Creating dbpedia entry
        g_lex.add((
            dbpedia[lex_sense.capitalize()],
            ontolex.concept,
            pwn[wordnet_code]
        ))

        g_lex.add((
            dbpedia[lex_sense.capitalize()],
            ontolex.isReferenceOf,
            sense_entry
        ))

        g_lex.add((
            dbpedia[lex_sense.capitalize()],
            ontolex.isDenotedBy,
            ontolex.LexicalConcept
        ))


        #Creating WordNet entry
        g_lex.add((
            pwn[wordnet_code],
            RDF.type,
            life[lex_entry]
        ))
        
        g_lex.add((
            pwn[wordnet_code],
            ontolex.isEvokedBy,
            life[lex_entry]
        ))

        g_lex.add((
            pwn[wordnet_code],
            ontolex.lexicalizedSense,
            sense_entry
        ))

        g_lex.add((
            pwn[wordnet_code],
            ontolex.isConceptOf,
            dbpedia[lex_sense.capitalize()]
        ))


    def get_wordnet_code(lex_gloss):
        query = '''
        ASK WHERE {
        {<my-specific-URI> ?p ?o . }
        UNION
        {?s ?p <my-specific-URI> . }
        }
        '''
        return lex_gloss

    def dbpedia_exists(lex_gloss):
        query = '''
        ASK WHERE {
        {<my-specific-URI> ?p ?o . }
        UNION
        {?s ?p <my-specific-URI> . }
        }
        '''
        return True

    def json_to_rdf_lexicon(g_lex, lex_entry, domain_name,
                            project, output_format='turtle'):

        lex_item = lex_entry['headword']
        lex_pos = lex_entry['grammaticalcategory']
        # can_form = lex_item
        lex_pron = lex_entry['Pronunciation']
        lex_sense = lex_entry['SenseNew']
        dict_lang = lex_entry['langscripts']['langcode']

        # ontolex = URIRef('http://www.w3.org/ns/lemon/ontolex#')
        # lexinfo = URIRef('http://www.lexinfo.net/ontology/2.0/lexinfo#')

        life = Namespace(domain_name+'/'+project + '/word/')    

        g_lex.bind("ontolex", ontolex)
        g_lex.bind("lexinfo", lexinfo)
        g_lex.bind("skos", SKOS)
        g_lex.bind("life", life)
        g_lex.bind("pwnlemma", pwn)
        g_lex.bind("dbpedia", dbpedia)


        g_lex.add((
            URIRef(life[lex_item]),
            RDF.type,
            lexinfo.LexicalEntry
        ))

        g_lex.add((
            URIRef(life[lex_item]),
            lexinfo.partOfSpeech,
            lexinfo[lex_pos]
        ))

        # g_lex.add((
        #     URIRef(life[lex_item]),
        #     ontolex.lexicalForm,
        #     URIRef(life[lex_item+'_form'])
        # ))

        g_lex.add((
            URIRef(life[lex_item]),
            ontolex.canonicalForm,
            URIRef(life[lex_item+'_form'])
        ))

        # Add graph for the canonical form
        add_canonical_form(g_lex, life, lex_entry, lex_item, lex_pron, dict_lang)

        for i in range(1, len(lex_sense)):
            sense_gloss = lex_sense['Sense '+str(i)]["Gloss"]["eng"]
            sense_defn = lex_sense['Sense '+str(i)]["Definition"]        
            sense_ex = lex_sense['Sense '+str(i)]["Example"]

            sense_entry = life[lex_item+'_sense'+str(i)]
            g_lex.add((
                URIRef(life[lex_item]),
                ontolex.sense,
                URIRef(sense_entry)
            ))
            add_sense(g_lex, life, lex_item, sense_entry, sense_gloss)
            add_definition(g_lex, life, lex_entry, lex_item, sense_defn)
            add_example(g_lex, life, lex_item, sense_ex, dict_lang)


    def generate_rdf(write_path, lexicon, domain_name, project, rdf_format):
        g_lex = Graph()
        
        for lex_entry in lexicon:
            json_to_rdf_lexicon(g_lex, lex_entry, 
                            domain_name, project, rdf_format)
            
        # with open (write_path, 'w') as f_w:    
        # rdf_out = g_lex.serialize(format=rdf_format, destination=write_path)
        g_lex.serialize(format=rdf_format, destination=write_path)
            # print(type(rdf_out))
            # f_w.write(rdf_out)

    def preprocess_csv_excel(lexicon):
        df = pd.json_normalize(lexicon)
        columns = df.columns
        drop_cols = [c for c in df.columns if c.startswith('langscripts.')]
        drop_cols.append ('lexemedeleteFLAG')
        drop_cols.append ('grammaticalcategory')
        drop_cols.append ('projectname')

        if 'gloss' in columns:
            drop_cols.append ('gloss')
        drop_oldsense = [c for c in df.columns if c.startswith('Sense.')]
        drop_oldvariant = [c for c in df.columns if c.startswith('Variant.')]
        drop_oldallomorph = [c for c in df.columns if c.startswith('Allomorph.')]
        drop_oldscript = [c for c in df.columns if c.startswith('Lexeme Form Script')]
        drop_files = [c for c in df.columns if c.startswith('filesname.')]

        drop_cols.extend(drop_oldsense)
        drop_cols.extend(drop_oldvariant)
        drop_cols.extend(drop_oldallomorph)
        drop_cols.extend(drop_oldscript)
        drop_cols.extend(drop_files)

        df.drop(columns=drop_cols, inplace=True)

        return df

    def generate_csv(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        with open (write_path, 'w') as f_w:
            df.to_csv(f_w, index=False)

    def generate_xlsx(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        f_w = open (write_path, 'wb')
        df.to_excel(f_w, index=False, engine='xlsxwriter')

    def generate_ods(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        with open (write_path, 'w') as f_w:
            df.to_excel(f_w, index=False, engine='openpyxl')

    def generate_html(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        with open (write_path, 'w') as f_w:
            df.to_html(f_w, index=False)

    def generate_latex(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        with open (write_path, 'w') as f_w:
            df.to_latex(f_w, index=False)

    def generate_formatted_latex(write_path, 
        lexicon,
        lexicon_df, 
        project, 
        editors = ['Editor 1', 'Editor 2', 'Editor 3'],
        co_editors = ['Co-ed 1', 'Co-ed 2', 'Co-ed 3'],
        metadata = ['Scheme for Protection and Preservation of Indian Languages', 'Central Institute of Indian Languages'],
        fields=[],
        dict_headword='headword', #lexemeformscripts.ipa.., glosslangs.hin..
        formatting_options={
        'documentclass': 'article', 
        'document_options':'a4paper, 12pt, twoside, xelatex',
        'geometry_options': {
            "top": "3.5cm",
            "bottom": "3.5cm",
            "left": "3.5cm",
            "right": "3.5cm",
            "columnsep": "30pt",
            "includeheadfoot": True
        }
        }):
        # geometry_options_1 = {"tmargin": "1cm", "lmargin": "10cm"}
        # lg.generate_formatted_latex(write_path, lexicon, project)
        lg.generate_formatted_latex(write_path, lexicon, lexicon_df, project, fields=fields)

    def generate_markdown(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        with open (write_path, 'w') as f_w:
            df.to_markdown(f_w, index=False)


    # write_file, lexicon, lexicon_df, project, fields=cur_fields
    def generate_pdf(write_path, 
        lexicon,
        lexicon_df, 
        project, 
        editors = ['Editor 1', 'Editor 2', 'Editor 3'],
        co_editors = ['Co-ed 1', 'Co-ed 2', 'Co-ed 3'],
        metadata = ['Scheme for Protection and Preservation of Indian Languages', 'Central Institute of Indian Languages'],
        fields=[],
        dict_headword='headword', #lexemeformscripts.ipa.., glosslangs.hin..
        formatting_options={
        'documentclass': 'article', 
        'document_options':'a4paper, 12pt, twoside, xelatex',
        'geometry_options': {
            "top": "3.5cm",
            "bottom": "3.5cm",
            "left": "3.5cm",
            "right": "3.5cm",
            "columnsep": "30pt",
            "includeheadfoot": True
        }
        }):
        # lg.generate_formatted_latex(write_path, lexicon, project)
        lg.generate_formatted_latex(write_path, lexicon, lexicon_df, project, fields=fields)

        # return True


    #“xml”, “n3”, “turtle”, “nt”, “pretty-xml”, “trix”, “trig” and “nquads”
    def download_lexicon(lex_json, write_path, 
        output_format='rdf', rdf_format='turtle', fields=[]):
        file_ext_map = {'turtle': '.ttl', 'n3': '.n3', 
        'nt': '.nt', 'xml': '.rdf', 'pretty-xml': '.rdfp', 'trix': '.trix', 
        'trig': '.trig', 'nquads': 'nquad', 'json': '.json', 'csv': '.csv',
        'xlsx': '.xlsx', 'pdf': '', 'html': '.html', 'latex_dict': '',
        'markdown': '.md', 'ods': '.ods'}

        domain_name = 'http://lifeapp.in'
        
        metadata = lex_json[0]
        project = metadata['projectname']

        lexicon = lex_json[1:]

        # fields = ['headword', 'Lexeme Form.ipa', 'Lexeme Form.Deva', 'grammaticalcategory', ['SenseNew.Gloss.hin', 'SenseNew.Gloss.eng', 'SenseNew.Definition.hin', 'SenseNew.Definition.eng', 'SenseNew.Example']]
        if len(fields) == 0:
            lexicon_df = pd.json_normalize(lexicon)
            columns = lexicon_df.columns
            cur_fields = ['headword', 'Pronunciation']
            # sense_fields = ['', '', '']
            sense_fields = []
            for field in columns:
                if 'SenseNew' in field:
                    if 'Gloss' in field or 'Definition' in field or 'Example' in field:
                        sense_fields.append(field)
                elif 'Lexeme' in field:
                    cur_fields.append(field)
            cur_fields.append('grammaticalcategory')
            cur_fields.extend(sense_fields)
        else:
            cur_fields = fields

        if (rdf_format in file_ext_map) or (output_format in file_ext_map):
            if output_format == 'rdf':
                file_ext = file_ext_map[rdf_format]
                write_file = os.path.join(write_path, 'lexicon_'+project+'_'+output_format+file_ext)
                generate_rdf(write_file, lexicon, domain_name, project, rdf_format)
            else:
                file_ext = file_ext_map[output_format]
                write_file = os.path.join(write_path, 'lexicon_'+project+file_ext)
                if output_format == 'csv':
                    generate_csv(write_file, lexicon)
                elif output_format == 'xlsx':
                    generate_xlsx(write_file, lexicon)
                elif output_format == 'pdf':
                    # print("...................cur_fields.................")
                    # pprint(cur_fields)
                    # generate_pdf(write_file, lexicon, project, fields=[], formatting_options={})
                    # generate_pdf(write_file, lexicon, lexicon_df, project, fields=cur_fields)
                    lg.generate_formatted_latex(write_file, lexicon, lexicon_df, project, fields=cur_fields)
                elif output_format == 'markdown':
                    generate_markdown(write_file, lexicon)
                elif output_format == 'html':
                    generate_html(write_file, lexicon)
                elif output_format == 'latex':
                    generate_latex(write_file, lexicon)
                elif output_format == 'ods':
                    generate_ods(write_file, lexicon)
                elif output_format == 'latex_dict':
                    # print("...................cur_fields.................")
                    # pprint(cur_fields)
                    # generate_formatted_latex(write_file, lexicon, project, fields=[], formatting_options={})
                    # generate_formatted_latex(write_file, lexicon, project, fields=cur_fields, formatting_options={})
                    # generate_formatted_latex(
                    #     write_file, lexicon, lexicon_df, project, fields=cur_fields)
                    lg.generate_formatted_latex(write_file, lexicon, lexicon_df, project, fields=cur_fields)
                elif output_format == 'json':
                    generate_json(lex_json)
        else:
            print ('File type\t', output_format, '\tnot supported')
            print ('Supported File Types', file_ext_map.keys())        


    lexeme_dir = basedir
    # working_dir = basedir+'/app/download'
    working_dir = basedir+'/download'
    with open(os.path.join(lexeme_dir, 'lexemeEntry.json')) as f_r:
        lex = json.load(f_r)
        out_form = download_format
        # print(out_form)
        if ('rdf' in out_form):
            rdf_format = out_form[3:]
            out_form = 'rdf'
            # print(rdf_format)
            download_lexicon(lex, working_dir, out_form, rdf_format=rdf_format)
        else:
            download_lexicon(lex, working_dir, out_form)

    # save current user mutimedia files of each lexeme to local storage
    # files = fs.find({'username' : current_user.username, 'projectname' : projectname, 'headword' : headword})
    # for file in files:
    #     name = file.filename
    #     open(basedir+'/download/'+name, 'wb').write(file.read())
    
    # printing the list of all files to be zipped 
    # files = glob.glob(basedir+'/app/download/*')
    files = glob.glob(basedir+'/download/*')
     
    with ZipFile('download.zip', 'w') as zip:
        # writing each file one by one 
        for file in files: 
            zip.write(file, os.path.join(projectname, os.path.basename(file)))
    print('All files zipped successfully!')

    # deleting all files from storage
    for f in files:
        # print(f)
        os.remove(f)
    
    # return send_file('../download.zip', as_attachment=True)
    return 'OK'

# download project route
@app.route('/downloadproject', methods=['GET', 'POST'])
def downloadproject():
    # getting the collections
    projects = mongo.db.projects                        # collection containing projects name
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    lexemes = mongo.db.lexemes                          # collection containing entry of each lexeme and its details
    sentences = mongo.db.sentences                          # collection containing entry of each sentence and its details
    fs =  gridfs.GridFS(mongo.db)                       # creating GridFS instance to get required files

    lst = list()

    activeprojectname = userprojects.find_one({ 'username' : current_user.username })['activeprojectname']
    # lst.append(activeprojectname)
    projectname =  activeprojectname

    for lexeme in lexemes.find({ 'projectname' : activeprojectname, 'lexemedeleteFLAG' : 0 }, \
                            {'_id' : 0}):
        lst.append(lexeme)
        # save current user mutimedia files of each lexeme to local storage
        # print(lst)
    for lexeme in lst:
        for lexkey, lexvalue in lexeme.items():
            if (lexkey == 'lexemeId'):    
                files = fs.find({'projectname' : projectname, 'lexemeId' : lexvalue})
                for file in files:
                    name = file.filename
                    # print(f'{"#"*80}')
                    # print(basedir+'/app/download/'+name)
                    # print(f'{"#"*80}')
                    # open(basedir+'/app/download/'+name, 'wb').write(file.read())
                    open(basedir+'/download/'+name, 'wb').write(file.read())

    # Serializing json  
    json_object = json.dumps(lst, indent = 2, ensure_ascii=False) 
    
    # writing to currentprojectname.json 
    # print(f'{"#"*80}')
    # print(basedir+"/app/download/lexicon_"+activeprojectname+".json")
    # print(f'{"#"*80}')
    # with open(basedir+"/app/download/lexicon_"+activeprojectname+".json", "w") as outfile:
    with open(basedir+"/download/lexicon_"+activeprojectname+".json", "w") as outfile:
        outfile.write(json_object)  

    # get all sentences of the activeprojectname    
    sentenceLst = []
    for sentence in sentences.find({ 'projectname' : activeprojectname, 'sentencedeleteFLAG' : 0 }, \
                            {'_id' : 0}):
        sentenceLst.append(sentence)

    # print(sentenceLst)    
        # save current user mutimedia files of each lexeme to local storage
    for sentence in sentenceLst:
        for sentkey, sentvalue in sentence.items():
            if (sentkey == 'sentenceId'):    
                files = fs.find({'projectname' : projectname, 'sentenceId' : sentvalue})
                for file in files:
                    name = file.filename
                    open(basedir+'/download/'+name, 'wb').write(file.read())

    # Serializing json  
    json_object = json.dumps(sentenceLst, indent = 2, ensure_ascii=False) 


    # writing to currentprojectname.json 
    # with open(basedir+"/app/download/sentence_"+activeprojectname+".json", "w") as outfile:
    with open(basedir+"/download/sentence_"+activeprojectname+".json", "w") as outfile:
        outfile.write(json_object)  
    
    # printing the list of all files to be zipped 
    # files = glob.glob(basedir+'/app/download/*')
    files = glob.glob(basedir+'/download/*')
     
    with ZipFile('download.zip', 'w') as zip:
        # writing each file one by one 
        for file in files: 
            zip.write(file, os.path.join(projectname, os.path.basename(file)))
    print('All files zipped successfully!')

    # deleting all files from storage
    for f in files:
        # print(files)
        os.remove(f)
    
    return send_file('../download.zip', as_attachment=True)
    # return 'OK'

# download dictionary route
@app.route('/downloaddictionary', methods=['GET', 'POST'])
def downloaddictionary():
    # getting the collections
    projects = mongo.db.projects                        # collection containing projects name
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    lexemes = mongo.db.lexemes                          # collection containing entry of each lexeme and its details
    # sentences = mongo.db.sentences                          # collection containing entry of each sentence and its details
    fs =  gridfs.GridFS(mongo.db)                       # creating GridFS instance to get required files
    lst = list()
    download_format = 'pdf'
    activeprojectname = userprojects.find_one({ 'username' : current_user.username })['activeprojectname']
    lst.append({'projectname': activeprojectname})
    projectname =  activeprojectname

    for lexeme in lexemes.find({ 'projectname' : activeprojectname, 'lexemedeleteFLAG' : 0 }, \
                            {'_id' : 0}):
        if (len(lexeme['headword']) != 0):
            lst.append(lexeme)
        # # save current user mutimedia files of each lexeme to local storage
        # files = fs.find({'projectname' : projectname, 'lexemeId' : lexemeId})
        # for file in files:
        #     name = file.filename
        #     # open(basedir+'/app/download/'+name, 'wb').write(file.read())
        #     open(os.path.join(basedir,'download', name), 'wb').write(file.read())

    # Serializing json  
    json_object = json.dumps(lst, indent = 2, ensure_ascii=False)

    with open(basedir+"/lexemeEntry.json", "w") as outfile: 
            outfile.write(json_object) 

    def preprocess_csv_excel(lexicon):
        df = pd.json_normalize(lexicon)
        columns = df.columns
        drop_cols = [c for c in df.columns if c.startswith('langscripts.')]
        drop_cols.append ('lexemedeleteFLAG')
        drop_cols.append ('grammaticalcategory')
        drop_cols.append ('projectname')

        if 'gloss' in columns:
            drop_cols.append ('gloss')
        drop_oldsense = [c for c in df.columns if c.startswith('Sense.')]
        drop_oldvariant = [c for c in df.columns if c.startswith('Variant.')]
        drop_oldallomorph = [c for c in df.columns if c.startswith('Allomorph.')]
        drop_oldscript = [c for c in df.columns if c.startswith('Lexeme Form Script')]
        drop_files = [c for c in df.columns if c.startswith('filesname.')]

        drop_cols.extend(drop_oldsense)
        drop_cols.extend(drop_oldvariant)
        drop_cols.extend(drop_oldallomorph)
        drop_cols.extend(drop_oldscript)
        drop_cols.extend(drop_files)

        df.drop(columns=drop_cols, inplace=True)

        return df

    def generate_latex(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        with open (write_path, 'w') as f_w:
            df.to_latex(f_w, index=False)

    def generate_formatted_latex(write_path, 
        lexicon,
        lexicon_df, 
        project, 
        editors = ['Editor 1', 'Editor 2', 'Editor 3'],
        co_editors = ['Co-ed 1', 'Co-ed 2', 'Co-ed 3'],
        metadata = ['Scheme for Protection and Preservation of Indian Languages', 'Central Institute of Indian Languages'],
        fields=[],
        dict_headword='headword', #lexemeformscripts.ipa.., glosslangs.hin..
        formatting_options={
        'documentclass': 'article', 
        'document_options':'a4paper, 12pt, twoside, xelatex',
        'geometry_options': {
            "top": "3.5cm",
            "bottom": "3.5cm",
            "left": "3.5cm",
            "right": "3.5cm",
            "columnsep": "30pt",
            "includeheadfoot": True
        }
        }):
        lg.generate_formatted_latex(write_path, lexicon, lexicon_df, project, fields=fields)

    def generate_pdf(write_path, 
        lexicon, 
        project, 
        editors = ['Editor 1', 'Editor 2', 'Editor 3'],
        co_editors = ['Co-ed 1', 'Co-ed 2', 'Co-ed 3'],
        metadata = ['Scheme for Protection and Preservation of Indian Languages', 'Central Institute of Indian Languages'],
        fields=[],
        dict_headword='headword', #lexemeformscripts.ipa.., glosslangs.hin..
        formatting_options={
        'documentclass': 'article', 
        'document_options':'a4paper, 12pt, twoside, xelatex',
        'geometry_options': {
            "top": "3.5cm",
            "bottom": "3.5cm",
            "left": "3.5cm",
            "right": "3.5cm",
            "columnsep": "30pt",
            "includeheadfoot": True
        }
        }):
        lg.generate_formatted_latex(write_path, lexicon, project, fields=fields)

    #“xml”, “n3”, “turtle”, “nt”, “pretty-xml”, “trix”, “trig” and “nquads”
    def download_lexicon(lex_json, write_path, 
        output_format='rdf', rdf_format='turtle', fields=[]):
        file_ext_map = {'turtle': '.ttl', 'n3': '.n3', 
        'nt': '.nt', 'xml': '.rdf', 'pretty-xml': '.rdfp', 'trix': '.trix', 
        'trig': '.trig', 'nquads': 'nquad', 'json': '.json', 'csv': '.csv',
        'xlsx': '.xlsx', 'pdf': '', 'html': '.html', 'latex_dict': '',
        'markdown': '.md', 'ods': '.ods'}
        
        metadata = lex_json[0]
        project = metadata['projectname']

        lexicon = lex_json[1:]

        # fields = ['headword', 'Lexeme Form.ipa', 'Lexeme Form.Deva', 'grammaticalcategory', ['SenseNew.Gloss.hin', 'SenseNew.Gloss.eng', 'SenseNew.Definition.hin', 'SenseNew.Definition.eng', 'SenseNew.Example']]
        if len(fields) == 0:
            lexicon_df = pd.json_normalize(lexicon)
            columns = lexicon_df.columns
            cur_fields = ['headword', 'Pronunciation']
            # sense_fields = ['', '', '']
            sense_fields = []
            for field in columns:
                if 'SenseNew' in field:
                    if 'Gloss' in field or 'Definition' in field or 'Example' in field:
                        sense_fields.append(field)
                elif 'Lexeme' in field:
                    cur_fields.append(field)
            cur_fields.append('grammaticalcategory')
            cur_fields.extend(sense_fields)
        else:
            cur_fields = fields

        if (output_format in file_ext_map):
            print(f"pdf is match")
            file_ext = file_ext_map[output_format]
            write_file = os.path.join(write_path, 'lexicon_'+project+file_ext)
            if output_format == 'pdf':
                # print("...................cur_fields.................")
                # pprint(cur_fields)
                lg.generate_formatted_latex(write_file, lexicon, lexicon_df, project, fields=cur_fields)
                # generate_pdf(write_file, lexicon, project, fields=fields, formatting_options={})
            elif output_format == 'latex':
                generate_latex(write_file, lexicon)
            elif output_format == 'latex_dict':
                # print("...................cur_fields.................")
                # pprint(cur_fields)
                lg.generate_formatted_latex(write_file, lexicon, lexicon_df, project, fields=cur_fields)
                # generate_formatted_latex(write_file, lexicon, project, fields=fields, formatting_options={})
        else:
            print ('File type\t', output_format, '\tnot supported')
            print ('Supported File Types', file_ext_map.keys())        


    lexeme_dir = basedir
    working_dir = basedir+'/download'
    with open(os.path.join(lexeme_dir, 'lexemeEntry.json')) as f_r:
        lex = json.load(f_r)
        out_form = download_format
        download_lexicon(lex, working_dir, out_form)

    # printing the list of all files to be zipped 
    # files = glob.glob(basedir+'/app/download/*')
    files = glob.glob(basedir+'/download/*')
     
    with ZipFile('download.zip', 'w') as zip:
        # writing each file one by one 
        for file in files: 
            zip.write(file, os.path.join(projectname, os.path.basename(file)))
    print('All files zipped successfully!')

    # deleting all files from storage
    for f in files:
        # print(f)
        os.remove(f)
    
    return send_file('../download.zip', as_attachment=True)
    # return 'OK'

# download route
@app.route('/download', methods=['GET'])
def download():
    # getting the collections
    lexemes = mongo.db.lexemes                          # collection containing entry of each lexeme and its details
    userprojects = mongo.db.userprojects    # collection containing username and his/her last seen project name
    fs =  gridfs.GridFS(mongo.db)                       # creating GridFS instance to get required files

    lst = list()

    projectname =  userprojects.find_one({ 'username' : current_user.username },\
                {'_id' : 0, 'activeprojectname': 1})['activeprojectname']
    lst.append(projectname)
    # print(f'{"#"*80}\n{projectname}')
    for lexeme in lexemes.find({'username' : current_user.username, 'projectname' : projectname},\
                            {'_id' : 0, 'username' : 0, 'projectname' : 0}):
        lst.append(lexeme)

    # Serializing json  
    json_object = json.dumps(lst, indent = 2, ensure_ascii=False) 
  
    # writing to currentprojectname.json 
    with open(basedir+"/download/"+projectname+".json", "w") as outfile: 
        outfile.write(json_object)  

    # save current user mutimedia files of each lexeme to local storage
    files = fs.find({'username' : current_user.username, 'projectname' : projectname})
    for file in files:
        name = file.filename
        open(basedir+'/download/'+name, 'wb').write(file.read())
    
    # printing the list of all files to be zipped 
    files = glob.glob(basedir+'/download/*')
    # print('Following files will be zipped:')
    # for file_name in files: 
    #     print(file_name) 

    # writing files to a zipfile 
    with ZipFile('download.zip', 'w') as zip:
        # writing each file one by one 
        for file in files: 
            zip.write(file, os.path.join(projectname, os.path.basename(file)))
    print('All files zipped successfully!')

    # deleting all files from storage
    for f in files:
        os.remove(f)
    
    return send_file('../download.zip', as_attachment=True)
    
# download project in json format route
@app.route('/downloadjson', methods=['GET', 'POST'])
def downloadjson():
    return send_file('../download.zip', as_attachment=True)

# modal view with complete detail of a lexeme for edit
# edit button on dictionary view table
@app.route('/userslist', methods=['GET', 'POST'])
def userslist():

    userlogin, projects, userprojects = getdbcollections.getdbcollections(mongo,
                                                                            'userlogin',
                                                                            'projects',
                                                                            'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    usersList = []
    speakersList = []
    current_user_sharemode = 0
    share_with_users_list = []
    try:
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
        projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
        shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                            current_username,
                                                            activeprojectname)
        current_user_sharemode = int(shareinfo['sharemode'])

        # get list of all the users registered in the application LiFE
        for user in userlogin.find({}, {"_id": 0, "username": 1}):
            # print(user)
            usersList.append(user["username"])
            # print(user)
        if (current_username == projectowner):
            usersList.remove(projectowner)
            share_with_users_list = usersList
        else:
            # print(usersList)
            usersList.remove(projectowner)
            usersList.remove(current_username)
            # print(usersList)
            # share_with_users_list = usersList
            # print(usersList)
            for username in usersList:
                # print(username)
                usershareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                                        username,
                                                                        activeprojectname)
                usersharemode = int(usershareinfo['sharemode'])
                # print(current_username, current_user_sharemode, username, usersharemode)
                # print(current_username, type(current_user_sharemode), username, type(usersharemode))
                if (current_user_sharemode <= usersharemode):
                    # print(f"username!!!: {username}")
                    # share_with_users_list.remove(username)
                    pass
                else:
                    # print(f"username!!!: {username}")
                    share_with_users_list.append(username)
        # print(usersList, share_with_users_list)
        speakersDict = projects.find_one({'projectname': activeprojectname},
                                            {'_id':0, 'speakerIds.'+current_username: 1})
        if (len(speakersDict) != 0):
            speakersList = speakersDict['speakerIds'][current_username]
        # print(speakersList)
    except Exception as e:
        print(e)
        pass

    return jsonify(usersList=sorted(share_with_users_list),
                    speakersList=sorted(speakersList),
                    sharemode=current_user_sharemode)

# modal view with complete detail of a lexeme for edit
# edit button on dictionary view table
@app.route('/shareprojectwith', methods=['GET', 'POST'])
def shareprojectwith():
    projects, userprojects = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
    # print('2758: activeprojectname', activeprojectname)

    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)

    # data through ajax
    data = request.args.get('data')
    data = eval(data)
    # print('2765', data)
    users = data['sharewithusers']
    # print(type(users))
    speakers = data['sharespeakers']
    sharemode = data['sharemode']
    # print(sharemode)
    if (sharemode == ''):
        sharemode = 0
    sharechecked = str(data['sharechecked'])
    # print('123', users, speakers, sharemode, sharechecked)
    
    if (len(users) != 0):
        # projectinfo of the user sharing the project
        projectinfo = userprojects.find_one(
                                                {
                                                    'username' : current_username
                                                },
                                                {
                                                    '_id': 0,
                                                    'myproject': 1,
                                                    'projectsharedwithme': 1
                                                }
                                            )
        # loop on users with whom the project is to be shared
        for user in users:
            # print(user)
            userdict = {}
            # get list of projects shared with the user
            usershareprojectsname = userprojects.find_one(
                                                            {
                                                                'username' : user
                                                            },
                                                            {
                                                                '_id': 0,
                                                                'projectsharedwithme': 1
                                                            }
                                                        )
            usershareprojectsname = usershareprojectsname['projectsharedwithme']

            # if (sharemode == -1 and activeprojectname in usershareprojectsname):
            #         removed_user = removeallaccess.removeallaccess(projects,
            #                                         userprojects,
            #                                         activeprojectname,
            #                                         current_username,
            #                                         user)
            #         return removed_user
            # else:
            #     return f'This project: {activeprojectname} is not shared with this user: {user}'

            if activeprojectname in usershareprojectsname:
                if (sharemode == -1):
                    removed_user = removeallaccess.removeallaccess(projects,
                                                    userprojects,
                                                    activeprojectname,
                                                    current_username,
                                                    user)
                    return removed_user

                tomesharedby = usershareprojectsname[activeprojectname]['tomesharedby']
                tomesharedby.append(current_username)
                isharedwith = usershareprojectsname[activeprojectname]['isharedwith']
                usershareprojectsname[activeprojectname] = {
                                                                'sharemode': sharemode,
                                                                'tomesharedby': list(set(tomesharedby)),
                                                                'isharedwith': isharedwith,
                                                                'sharechecked': sharechecked,
                                                                'activespeakerId': ''
                                                            }
            else:
                if (sharemode == -1):
                    return f'This project: {activeprojectname} is not shared with this user: {user}'
                    
                usershareprojectsname[activeprojectname] = {
                                                                'sharemode': sharemode,
                                                                'tomesharedby': [current_user.username],
                                                                'isharedwith': [],
                                                                'sharechecked': sharechecked,
                                                                'activespeakerId': ''
                                                            }
            projectdetails = projects.find_one(
                                                {
                                                    'projectname': activeprojectname
                                                },
                                                {
                                                    '_id': 0,
                                                    'sharedwith': 1,
                                                    'lastActiveId': 1,
                                                    'speakerIds': 1
                                                }
                                            )
            # print(projectdetails)
            projectdetails['sharedwith'].append(user)
            # print(projectdetails)
            # update list of projects shared with the user in collection
            userprojects.update_one(
                                        {
                                            'username' : user
                                        },
                                        {
                                            '$set': 
                                                {
                                                    'projectsharedwithme' : usershareprojectsname
                                                }
                                        }
                                    )
            projects.update_one(
                                    {
                                        'projectname': activeprojectname
                                    },
                                    {
                                        '$set':
                                            {
                                                'sharedwith': list(set(projectdetails['sharedwith']))
                                            }
                                    }
                                )
            
            if ('speakerIds' in projectdetails):
                if (len(speakers) != 0):
                    userprojectinfo = ''
                    for key, value in projectinfo.items():
                        if len(value) != 0:
                            if activeprojectname in value:
                                userprojectinfo = key+'.'+activeprojectname+".activespeakerId"
                    userprojects.update_one(
                                                {
                                                    "username": current_username
                                                },
                                                {
                                                    "$set":
                                                        {
                                                            userprojectinfo: speakers[-1]
                                                        }
                                                }
                                            )
                    
                    for speaker in speakers:
                        # print(speaker)
                        projects.update_one(
                                                {
                                                    'projectname': activeprojectname
                                                },
                                                {
                                                    '$addToSet':
                                                        {
                                                            'speakerIds.'+user: speaker
                                                        }
                                                }
                                            )
                        userlastactiveId = projectdetails['lastActiveId'][current_username][speaker]['audioId']
                        projects.update_one(
                                                {
                                                    'projectname': activeprojectname
                                                },
                                                {
                                                    '$set': 
                                                            {
                                                                'lastActiveId.'+user+'.'+speaker+'.audioId': userlastactiveId
                                                            }
                                                }
                                            )
                elif user not in projectdetails['speakerIds']:
                    projects.update_one(
                                            {
                                                'projectname': activeprojectname
                                            },
                                            {
                                                '$set': 
                                                    {
                                                        'lastActiveId.'+user: {}
                                                    }
                                            }
                                        )

            # update "isharedwith" of the current user and the projectowner
            for key, value in projectinfo.items():
                if (len(value) != 0 and
                    activeprojectname in value):
                    userprojects.update_one(
                                                {
                                                    "username": current_username
                                                },
                                                {
                                                    "$addToSet":
                                                        {
                                                            key+'.'+activeprojectname+'.isharedwith': user
                                                        }
                                                }
                                            )
                    if projectowner != current_username:
                        userprojects.update_one(
                                                    {
                                                        "username": projectowner
                                                    },
                                                    {
                                                        "$addToSet":
                                                            {
                                                                'myproject.'+activeprojectname+'.isharedwith': user
                                                            }
                                                    }
                                                )

    return 'OK'

# modal view with complete detail of a lexeme
# view button on dictionary view table
@app.route('/lexemeview', methods=['GET'])
def lexemeview():
    # getting the collections
    projectsform = mongo.db.projectsform                # collection of project specific form created by the user
    lexemes = mongo.db.lexemes                          # collection containing entry of each lexeme and its details
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    projects = mongo.db.projects                        # collection of projects

    headword = request.args.get('a').split(',')                    # data through ajax
    # print(headword)

    activeprojectname = userprojects.find_one({ 'username' : current_user.username })['activeprojectname']
    # print(activeprojectname)
    projectOwner = projects.find_one({'projectname': activeprojectname}, {'projectOwner' : 1})['projectOwner']
    # projectOwner = projects.find_one({}, {"_id" : 0, activeprojectname : 1})[activeprojectname]["projectOwner"]
    # print(projectOwner)
    lexeme = lexemes.find_one({'username' : projectOwner, 'lexemeId' : headword[0], },\
                            {'_id' : 0, 'username' : 0})

    # print(lexeme["lemon"])
    # pprint(lexeme)

    filen = {}
    if 'filesname' in lexeme:
        for key, filename in lexeme['filesname'].items():
            # print(key, filename)
            filen[key] = url_for('retrieve', filename=filename)


    y = projectsform.find_one_or_404({'projectname' : activeprojectname,\
                                'username' : projectOwner}, { "_id" : 0 })

    return jsonify(newData=y, result1=lexeme, result2=filen)


# modal view with complete detail of a lexeme for edit
# edit button on dictionary view table
@app.route('/lexemeedit', methods=['GET', 'POST'])
def lexemeedit():
    # getting the collections
    projectsform = mongo.db.projectsform                # collection of project specific form created by the user
    lexemes = mongo.db.lexemes                          # collection containing entry of each lexeme and its details
    userprojects = mongo.db.userprojects                # collection of users and their respective projects
    projects = mongo.db.projects                        # collection of projects

    headword = request.args.get('a').split(',')                    # data through ajax
    # print(headword)

    activeprojectname = userprojects.find_one({ 'username' : current_user.username })['activeprojectname']
    # print(activeprojectname)
    
    projectOwner = projects.find_one({'projectname': activeprojectname}, {'projectOwner' : 1})['projectOwner']
    # projectOwner = projects.find_one({}, {"_id" : 0, activeprojectname : 1})[activeprojectname]["projectOwner"]
    # print(projectOwner)

    if request.method == 'POST':

        newLexemeData = request.form.to_dict()
        # print(newLexemeData)
        return redirect(url_for('dictionaryview'))
    
    # activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
    #                 {'_id' : 0, 'activeprojectname': 1})['activeprojectname']
    lexeme = lexemes.find_one({'username' : projectOwner, 'lexemeId' : headword[0], },\
                            {'_id' : 0, 'username' : 0})

    # pprint(lexeme)
    
    filen = []
    if 'filesname' in lexeme:
        for filename in lexeme['filesname']:
            filen.append(url_for('retrieve', filename=filename))

    y = projectsform.find_one_or_404({'projectname' : activeprojectname,\
                                'username' : projectOwner}, { "_id" : 0 })                             
    
    return jsonify(newData=y, result1=lexeme, result2=filen)

# enter new lexeme route
# display form for new lexeme entry for current project
@app.route('/editlexeme', methods=['GET', 'POST'])
@login_required
def editlexeme():
    return render_template('editlexeme.html') 

@app.route('/lexemeupdate', methods=['GET', 'POST'])
def lexemeupdate():
    projects, userprojects, lexemes = getdbcollections.getdbcollections(mongo,
                                                'projects',
                                                'userprojects',
                                                'lexemes')
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                            userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    # print(f"PROJECT OWNER: {projectOwner}")
    # new lexeme details coming from current project form
    if request.method == 'POST':

        # newLexemeData = request.form.to_dict()
        newLexemeData = dict(request.form.lists())
        newLexemeFiles = request.files.to_dict()
        # print(newLexemeFiles)
        # pprint(newLexemeData)
        lexemeId = newLexemeData['lexemeId'][0]
        # dictionary to store files name
        newLexemeFilesName = {}
        for key in newLexemeFiles:
            if newLexemeFiles[key].filename != '':
                # adding microseconds of current time to differ two files of same name
                newLexemeFilesName[key] = (datetime.now().strftime('%f')+'_'+newLexemeFiles[key].filename)
       
        # format data filled in enter new lexeme form    
        lexemeFormData = {}
        sense = {}
        variant = {}
        allomorph = {}
        lemon = ''
        scriptCode = {
            "Bengali": "Beng",
            "Devanagari": "Deva",
            "Gujarati": "Gujr",
            "Gurumukhi": "Guru",
            "IPA": "IPA",
            "Kannada": "Knda",
            "Latin": "Latn",
            "Malayalam": "Mlym",
            "Mayek": "Mtei",
            "Odia": "Orya",
            "Ol_Chiki": "Olck",
            "Tamil": "Taml",
            "Telugu": "Telu"
        }
        langScript = {
            "Assamese": "Bengali",
            "Awadhi": "Devanagari",
            "Bangla": "Bengali",
            "Bengali": "Bengali",
            "Bhojpuri": "Devanagari",
            "Bodo": "Devanagari",
            "Braj": "Devanagari",
            "Bundeli": "Devanagari",
            "English": "Latin",
            "Gujarati": "Gujarati",
            "Haryanvi": "Devanagari",
            "Hindi": "Devanagari",
            "IPA": "IPA",
            "Kannada": "Kannada",
            "Konkani": "Devanagari",
            "Magahi": "Devanagari",
            "Maithili": "Devanagari",
            "Malayalam": "Malayalam",
            "Marathi": "Devanagari",
            "Meitei": "Mayek",
            "Nepali": "Devanagari",
            "Odia": "Odia",
            "Punjabi": "Gurumukhi",
            "Santali":"Ol_Chiki",
            "Tamil": "Tamil",
            "Telugu": "Telugu"
        }

        lexemeFormData['username'] = projectowner

        def lexemeFormScript():
            """'List of dictionary' of lexeme form scripts"""
            lexemeFormScriptList = []
            for key, value in newLexemeData.items():
                if 'Script' in key:
                    k = re.search(r'Script (\w+)', key)
                    lexemeFormScriptList.append({k[1] : value[0]})
            lexemeFormData['headword'] =  list(lexemeFormScriptList[0].values())[0]
            return lexemeFormScriptList

        def senseListOfDict(senseCount):
            """'List of dictionary' of sense"""
            for num in range(1, int(newLexemeData['senseCount'][-1])+1):
                senselist = []
                for key, value in newLexemeData.items():
                    if 'Sense '+str(num) in key:
                        k = re.search(r'([\w+\s]+) Sense', key)
                        if k[1] == 'Semantic Domain' or k[1] == 'Lexical Relation':
                            senselist.append({k[1] : value})
                        else:
                            senselist.append({k[1] : value[0]})
                sense['Sense '+str(num)] = senselist
            # pprint.pprint(sense)
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
            # pprint.pprint(variant)
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
            # pprint.pprint(allomorph)
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
            # pprint.pprint(sense)
            return customFieldsDict

        for key, value in newLexemeData.items():
            if 'Sense' in key or 'Variant' in key or 'Allomorph' in key: continue
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
                # print(lexemeFormData)
                # print(key)
                lexemeFormData[key] = value[0]    

        # print(f"{'#'*80}\n{list(lexemeFormData['Sense']['Sense 1'][0].keys())}")
        gloss = list(lexemeFormData['Sense']['Sense 1'][0].keys())
        lexemeFormData['gloss'] = lexemeFormData['Sense']['Sense 1'][0][gloss[0]]
        # grammaticalcategory  = list(lexemeFormData['Sense']['Sense 1'][4].keys())
        # print(f"{'#'*80}\n{lexemeFormData['Sense']['Sense 1']}")
        for senseData in lexemeFormData['Sense']['Sense 1']:
            if list(senseData.keys())[0] == 'Grammatical Category':
                # print(f"{'#'*80}\n{list(senseData.values())[0]}")
                lexemeFormData['grammaticalcategory'] = list(senseData.values())[0]
        lexemeFormData['lexemedeleteFLAG'] = 0
        lexemeFormData['updatedBy'] = current_user.username
        lexemeFormData['lexemeId'] = lexemeId

        langscripts = {}
        langscripts["langname"] = newLexemeData['Lexeme Language'][0]
        langscripts["langcode"] = newLexemeData['Lexeme Language'][0][:3].lower()
        headwordscript = list(lexemeFormData['Lexeme Form Script'][0].keys())[0]
        # langscripts["headwordscript"] = {headwordscript[0]+headwordscript[1:4].lower(): headwordscript}
        langscripts["headwordscript"] = {scriptCode[headwordscript]: headwordscript}
        lexemeformscripts = {}
        for i in range(len(lexemeFormData['Lexeme Form Script'])):
            for lfs in lexemeFormData['Lexeme Form Script'][i].keys():
                # lexemeformscripts[lfs[0]+lfs[1:4]] = lfs
                lexemeformscripts[scriptCode[lfs]] = lfs
        langscripts["lexemeformscripts"] = lexemeformscripts
        glosslangs = {}
        glossscripts = {}
        for gl in newLexemeData.keys():
            if ('Gloss' in gl):
                gl = gl.split()[1]
                glosslangs[gl[0:3]] = gl
                glossscripts[scriptCode[langScript[gl]]] = gl
        langscripts["glosslangs"] = glosslangs

        langscripts["glossscripts"] = glossscripts
        lexemeFormData['langscripts'] = langscripts


        SenseNew = {}

        for key, value in lexemeFormData['Sense'].items():
            keyParent = key
            key = {}
            # print(keyParent)
            Gloss = {}
            Definition = {}
            Lexical_Relation = {}
            for val in value:
                
                for k, v in val.items():
                    if ("Gloss" in k):
                        Gloss[k.split()[1][:3].lower()] = v
                        # print(key, k, v)
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
        # pprint(SenseNew)
        lexemeFormData['SenseNew'] = SenseNew

        lexemeForm = {}
        for lexForm in lexemeFormData['Lexeme Form Script']:
            for lexKey, lexValue in lexForm.items():
                # lexemeForm[lexKey[:4]] = lexValue
                lexemeForm[scriptCode[lexKey]] = lexValue

        lexemeFormData['Lexeme Form'] = lexemeForm
        
        # keep only new updated keys as in 'lexemeEntry_sir.json' file in 'data_format folder
        # and delete old keys
        lexemeFormData.pop('Sense', None)
        lexemeFormData.pop('Lexeme Form Script', None)
        
        # when testing comment these to avoid any database update/changes
        # saving files for the new lexeme to the database in fs collection
        for (filename, key) in zip(newLexemeFilesName.values(), newLexemeFiles):
            # print(filename, key, newLexemeFiles[key])
            mongo.save_file(filename, newLexemeFiles[key], lexemeId=lexemeId, username=current_user.username,\
                            projectname=lexemeFormData['projectname'], headword=lexemeFormData['headword'],\
                            updatedBy=current_user.username)       
       
       # prevent deletion of old files name from lexeme details
        oldFilesOfLexeme = lexemes.find_one({ 'lexemeId': lexemeId }, { '_id': 0, 'filesname': 1 })
        # print(oldFilesOfLexeme)
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
        # print(f'{"="*80}\nLexeme Form :')
        # pprint(lexemeFormData)
        # print(f'{"="*80}')
        lexemes.update_one({ 'lexemeId': lexemeId }, { '$set' : lexemeFormData })

        flash('Successfully Updated lexeme')
        return redirect(url_for('dictionaryview'))
        # comment till here

    try:
        my_projects = len(userprojects.find_one({'username' : current_user.username})["myproject"])
        shared_projects = len(userprojects.find_one({'username' : current_user.username})["projectsharedwithme"])
        # print(f"MY PROJECTS: {my_projects}, SHARED PROJECTS: {shared_projects}")
        if  (my_projects+shared_projects) == 0:
            flash('Please create your first project')
            return redirect(url_for('home'))
    except:
        # print(f'{"#"*80}\nCurrent user details not in database!!!')
        flash('Please create your first project')
        return redirect(url_for('home'))
    # get the list of lexeme entries for current project to show in dictionary view table
    lst = list()
    
    # projectOwner = projects.find_one({}, {"_id" : 0, activeprojectname : 1})[activeprojectname]["projectOwner"]
    # print(projectOwner)
    try:
        # print(activeprojectname)
        projectOwner = projects.find_one({}, {"_id" : 0, activeprojectname : 1})[activeprojectname]["projectOwner"]
        # print(projectOwner)
        for lexeme in lexemes.find({ 'username' : projectOwner, 'projectname' : activeprojectname, 'lexemedeleteFLAG' : 0 }, \
                                {'_id' : 0, 'headword' : 1, 'gloss' : 1, 'grammaticalcategory' : 1, 'lexemeId' : 1}):
            # pprint(lexeme)
            if (len(lexeme['headword']) != 0):
                lst.append(lexeme)
    except:
        flash('Enter first lexeme of the project')

    # print(lst)
    return render_template('dictionaryview.html', projectName=activeprojectname, sdata=lst, count=len(lst), data=currentuserprojectsname)    


# delete button on dictionary view table
@app.route('/lexemedelete', methods=['GET', 'POST'])
def lexemedelete():
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
    lexemes.update_one({'username' : projectowner, 'lexemeId' : headword[0]},\
                        { '$set': { 'lexemedeleteFLAG': 1 }})
                    
    return jsonify(msg=headword[1]+' deletion successful')

# delete button on dictionary view table
@app.route('/deletemultiplelexemes', methods=['GET', 'POST'])
def deletemultiplelexemes():
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

    # print(headwords)
    for headwordId in headwords.keys():
        lexemes.update_one({'username' : projectowner, 'lexemeId' : headwordId, \
                        }, { '$set': { 'lexemedeleteFLAG': 1 }})

    return 'OK'


# save active project name for active user
@app.route('/activeprojectname', methods=['GET', 'POST'])
def activeprojectname():
    userprojects, = getdbcollections.getdbcollections(mongo, 'userprojects')
    
    projectname = str(request.args.get('a'))            # data through ajax

    # if userprojects.find_one({'username' : current_user.username}) is None:
    #     activeprojectnames.insert({ 'username' : current_user.username, 'projectname' : projectname })
    # else:
    #     activeprojectnames.update_one({ 'username' : current_user.username }, {'$set' : { 'projectname' : projectname }})

    userprojects.update_one({ 'username' : current_user.username },
            { '$set' : { 'activeprojectname' :  projectname}})

    return 'OK'

def adminfirstlogin(userlogin, string_password):
    password = generate_password_hash(string_password)
        # print(user, password)

    userlogin.update_one({"username": ADMIN_USER},
                        {'$set':{"password": password, 
                        'userSince': datetime.now(), 
                        'isActive': 1}})
    
    return password
# MongoDB Database
# user login form route
@app.route('/login', methods=['GET', 'POST'])
def login():
    userlogin = mongo.db.userlogin

    generateadmin(userlogin)                          # collection of users and their login details
    dummyUserandProject()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = UserLoginForm()
    if form.validate_on_submit():
        # username = userlogin.find_one({"username": form.username.data})
        user = UserLogin(username=form.username.data)
        password = form.password.data
        print ('Original password', password)
        # print(user)
        if user.username == ADMIN_USER:
            if user.password_hash == '':                                
                admin_password = adminfirstlogin(userlogin, password)
                user.password_hash = admin_password

        # print ('Create password', password)
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        isUserActive = userlogin.find_one({'username': form.username.data }, {"_id": 0, "isActive": 1})
        # print(len(isUserActive))
        if (len(isUserActive) != 0):
            isUserActive = isUserActive['isActive']
            if (isUserActive):
                pass
                # print(isUserActive)
                # print('123')
            else:
                # flash('Your request for an account is successfully submitted and is currently under review.')
                flash('Your request for an account is  currently under review. If approved, your account will be active in some time.')
                return redirect(url_for('login'))
        login_user(user, force=True)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', form=form)


# MongoDB Database
# use logout
@app.route('/logout')
def logout():
    try:
        logout_user()
        return redirect(url_for('home'))
    except:
        return redirect(url_for('home'))    



# MongoDB Database
# new user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    userlogin = mongo.db.userlogin                          # collection of users and their login details
    userProfile = {}
    excludeFormFields = ['username', 'password', 'password2', 'csrf_token', 'submit']
    dummyUserandProject()
    if current_user.is_authenticated:
        # print(current_user.get_id())
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # print(form)
        for form_data in form:
            # print(form_data)
            # print(type(form_data))
            # print(form_data.data)
            if (form_data.name not in excludeFormFields):
                userProfile[form_data.name] = form_data.data
        # print(userProfile)
        # user = UserLogin(username=form.username.data)
        password = generate_password_hash(form.password.data)
        # print(user, password)

        userlogin.insert({"username": form.username.data,
                            "password": password, 
                            'userProfile': userProfile,
                            'userSince': datetime.now(), 
                            'isActive': 0})

        userprojects = mongo.db.userprojects              # collection of users and their respective projectlist
        # userprojects.insert({'username' : form.username.data, 'myproject': [], \
        #     'projectsharedwithme': [], 'activeprojectname' : ''})
        userprojects.insert({'username' : form.username.data, 'myproject': {}, \
            'projectsharedwithme': {}, 'activeprojectname' : ''})

        # flash('Congratulations, you are now a registered user!')
        flash('Your request for an account is successfully submitted and is currently under review.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

def dummyUserandProject():
    """ Creates dummy user and project if the database has no collection """
    print("Creates dummy user and project if the database has no collection")
    userprojects = mongo.db.userprojects                # collection of users and their projectlist and active project
    projects = mongo.db.projects
                            # collection containing projects name
    if len(mongo.db.list_collection_names()) == 0:
        userprojects.insert({'username' : "dummyUser",
                            'myproject': 
                                {"dummyProject1": 
                                    {
                                        'sharemode': 0,
                                        'sharechecked': "false"
                                    }
                                },
                            'projectsharedwithme': {},
                            'activeprojectname' : "dummyActiveProject"
                            })
        projects.insert({"projectname": "dummyProject1",
                        "projectOwner" : "dummyUser",
                        "lexemeInserted" : 0,
                        "lexemeDeleted" : 0,\
                        'sharedwith': ['dummyUser'],
                        'projectdeleteFLAG' : 0
                        })

def insertadmin(userlogin):
    
    userprojects = mongo.db.userprojects        
    
    userlogin.insert ({
            "username": ADMIN_USER,
            "password": "",
            "userProfile": {
                "username": "",
                "position": "",
                "organisation_name": "",
                "organisation_type": "",
                "country": "",
                "city": "",
                "email": "",
                "languages": "",
                "memory_requirement": "",
                "app_use_reason": ""
            }
        })

    userprojects.insert({'username' : ADMIN_USER, 'myproject': {}, \
        'projectsharedwithme': {}, 'activeprojectname' : ''})
    
    flash(admin_reminder)
    


def generateadmin(userlogin):
    """ Creates admin if the database does not have an admin user """ 
    
    if len(mongo.db.list_collection_names()) == 0:
        insertadmin(userlogin)
    else:
        admin_login = userlogin.find_one({'username':ADMIN_USER}, {'password': 1, '_id': 0})
        if admin_login == None:
            insertadmin(userlogin)
        elif admin_login['password'] == '':
            flash(admin_reminder)




# audio transcription route
@app.route('/', methods=['GET', 'POST'])
@app.route('/audiotranscription', methods=['GET', 'POST'])
@login_required
def audiotranscription():
    userprojects = mongo.db.userprojects              # collection of users and their respective projects

    # currentuserprojectsname =  sorted(list(currentuserprojects()))
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_user.username,
                                userprojects)
    activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
                    {'_id' : 0, 'activeprojectname': 1})['activeprojectname']

    fs =  gridfs.GridFS(mongo.db)                       # creating GridFS instance to get required files                
    files = fs.find({})
    audioFolder = os.path.join(basedir, 'static/audio')
    shutil.rmtree(audioFolder)
    os.mkdir(audioFolder)
    for file in files:
        if ('audio' in file.contentType):
            name = file.filename
            # print(file.projectname)
            # print(name)
            audiofile = fs.get_last_version(filename=name)
            audiofileBytes = audiofile.read()
            # print(len(audiofile.read()))
            if (len(audiofileBytes) != 0):
                open(basedir+'/static/audio/'+name, 'wb').write(audiofileBytes)

    if request.method == 'POST':

        newLexemeData = dict(request.form.lists())
        newLexemeFiles = request.files.to_dict()
        # pprint(newLexemeData)
        # dictionary to store files name
        newLexemeFilesName = {}
        for key in newLexemeFiles:
            if newLexemeFiles[key].filename != '':
                # adding microseconds of current time to differ two files of same name
                newLexemeFilesName[key] = (datetime.now().strftime('%f')+'_'+newLexemeFiles[key].filename)
        # print(newLexemeFiles)
        # print(newLexemeFilesName)

        return redirect(url_for('audiotranscription'))       
    
    return render_template('audiotranscription.html',  data=currentuserprojectsname, activeprojectname=activeprojectname, audiofile=str(file.read()))


# karya access code assignment route
@app.route('/assignkaryaaccesscode', methods=['GET', 'POST'])
@login_required
def assignkaryaaccesscode():
    # print(f"IN KARYA ACCESS CODE ASSIGNMENT FUNCTION")
    return redirect(url_for('home'))

@app.route('/datetimeasid', methods=['GET'])
def datetimeasid():
    Id = re.sub(r'[-: \.]', '', str(datetime.now()))
    # print(Id)
    return jsonify(Id=Id)

@app.route('/loadpreviousaudio', methods=['GET', 'POST'])
@login_required
def loadpreviousaudio():
    projects, userprojects = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'userprojects')
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                            userprojects)
    # activespeakerid = getactivespeakerid.getactivespeakerid(userprojects, current_user.username)
    activespeakerid = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                            current_user.username,
                                                            activeprojectname)['activespeakerId']
    # data through ajax
    lastActiveId = request.args.get('data')
    lastActiveId = eval(lastActiveId)
    latest_audio_id = ''
    # newAudioFilePath = getAudioFilename(lastActiveFilename, 'previous')
    if (len(lastActiveId) != 0):
        latest_audio_id = audiodetails.getnewaudioid(projects,
                                                        activeprojectname,
                                                        lastActiveId,
                                                        activespeakerid,
                                                        'previous')
        audiodetails.updatelatestaudioid(projects,
                                            activeprojectname,
                                            latest_audio_id,
                                            current_user.username,
                                            activespeakerid)

    return jsonify(newAudioId=latest_audio_id)
    # return jsonify(newAudioFilePath=newAudioFilePath)

@app.route('/loadnextaudio', methods=['GET', 'POST'])
@login_required
def loadnextaudio():
    projects, userprojects = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'userprojects')
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                            userprojects)
    # activespeakerid = getactivespeakerid.getactivespeakerid(userprojects, current_user.username)
    activespeakerid = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                            current_user.username,
                                                            activeprojectname)['activespeakerId']
    # data through ajax
    lastActiveId = request.args.get('data')
    lastActiveId = eval(lastActiveId)
    # print('lastActiveId', type(lastActiveId), len(lastActiveId))
    latest_audio_id = ''
    if (len(lastActiveId) != 0):
    # newAudioFilePath = getAudioFilename(lastActiveFilename, 'previous')
        latest_audio_id = audiodetails.getnewaudioid(projects,
                                                        activeprojectname,
                                                        lastActiveId,
                                                        activespeakerid,
                                                        'next')
        # print('latest_audio_id ROUTES', latest_audio_id)
        audiodetails.updatelatestaudioid(projects,
                                            activeprojectname,
                                            latest_audio_id,
                                            current_user.username,
                                            activespeakerid)

    return jsonify(newAudioId=latest_audio_id)
    # return jsonify(newAudioFilePath=newAudioFilePath)

def getAudioFilename(lastActiveFilename, whichOne):
    audioFilesPath = 'static/audio'
    baseAudioFilesPath = os.path.join(basedir, audioFilesPath)
    audioFilesList = sorted(os.listdir(baseAudioFilesPath))
    # print(audioFilesList)
    audioFileIndex = audioFilesList.index(lastActiveFilename)
    if (whichOne == 'next'):
        audioFileIndex = audioFileIndex + 1
    elif (whichOne == 'previous'):
        audioFileIndex = audioFileIndex - 1  
    newAudioFilePath = os.path.join(audioFilesPath, audioFilesList[audioFileIndex])

    return newAudioFilePath

# this is for the dropdown list of all the filenames.
# it could be use by the user to move to (load) some random audio using the filename
@app.route('/allunannotated', methods=['GET', 'POST'])
def allunannotated():
    userprojects, transcriptions = getdbcollections.getdbcollections(mongo, 'userprojects', 'transcriptions')

    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                    userprojects)
    # activespeakerid = getactivespeakerid.getactivespeakerid(userprojects, current_user.username)
    activespeakerid = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                            current_user.username,
                                                            activeprojectname)['activespeakerId']
    # audioFilesPath = 'static/audio'
    # baseAudioFilesPath = os.path.join(basedir, audioFilesPath)
    # audioFilesList = sorted(os.listdir(baseAudioFilesPath))
    annotated, unannotated = [], []
    if (activespeakerid != ''):
        annotated, unannotated = unannotatedfilename.unannotatedfilename(transcriptions,
                                                                            activeprojectname,
                                                                            activespeakerid,
                                                                            'audio')
    # print(annotated, unannotated)
    return jsonify(allanno=annotated, allunanno=unannotated)

@app.route('/loadunannotext', methods=['GET'])
@login_required
def loadunannotext():
    projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo, 'projects',
    'userprojects', 'transcriptions')

    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                                                                    userprojects)
    # activespeakerid = getactivespeakerid.getactivespeakerid(userprojects, current_user.username)
    activespeakerid = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                            current_user.username,
                                                            activeprojectname)['activespeakerId']

    # print(f'{"="*80}\nUn-Anno\n{"="*80}')

    lastActiveId = request.args.get('data')
    lastActiveId = eval(lastActiveId)
    # print(lastActiveId)
    updateactivespeakeraudioid = 'lastActiveId.'+current_user.username+'.'+activespeakerid+'.audioId'
    # print(updateactivespeakeraudioid)

    projects.update_one({"projectname": activeprojectname},
        { '$set' : { updateactivespeakeraudioid: lastActiveId }})

    # if (project_type == 'text'):
    #     return redirect(url_for('textAnno'))
    # elif (project_type == 'image'):
    #     return redirect(url_for('imageAnno'))
    return 'OK'  

# uploadaudiofiles route
@app.route('/uploadaudiofiles', methods=['GET', 'POST'])
@login_required
def uploadaudiofiles():
    projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo,
                                                'projects',
                                                'userprojects',
                                                'transcriptions')
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                            userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    if request.method == 'POST':
        speakerId = dict(request.form.lists())['speakerId'][0]
        new_audio_file = request.files.to_dict()
        audiodetails.saveaudiofiles(mongo,
                                    projects,
                                    userprojects,
                                    transcriptions,
                                    projectowner,
                                    activeprojectname,
                                    current_user.username,
                                    speakerId,
                                    new_audio_file
                                    )

    return redirect(url_for('enternewsentences'))

# change speaker ID
@app.route('/changespeakerid', methods=['GET', 'POST'])
@login_required
def changespeakerid():
    userprojects, = getdbcollections.getdbcollections(mongo, 'userprojects')
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username, userprojects)

    # data through ajax
    speakerId = str(request.args.get('a'))
    # print(speakerId)
    projectinfo = userprojects.find_one({'username' : current_user.username},
                                        {'_id': 0, 'myproject': 1, 'projectsharedwithme': 1})

    # print(projectinfo)
    userprojectinfo = ''
    for key, value in projectinfo.items():
        if len(value) != 0:
            if activeprojectname in value:
                userprojectinfo = key+'.'+activeprojectname+".activespeakerId"
    # print(userprojectinfo)
    userprojects.update_one({"username": current_user.username},
                            { "$set": {
                                userprojectinfo: speakerId
                            }})
    # userprojects.update_one({ 'username' : current_user.username },
    #                         { '$set' : { 'activespeakerId' :  speakerId}})

    return 'OK'

# get progress report
@app.route('/progressreport', methods=['GET'])
@login_required
def progressreport():
    projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                'projects',
                                                                                'userprojects',
                                                                                'transcriptions')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)

    progressreport = ''

    # print(current_username, activeprojectname)
    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects, current_username, activeprojectname)
    # print(shareinfo)

    if 'isharedwith' in shareinfo:
        isharedwith = shareinfo['isharedwith']
        # print('isharedwith', isharedwith)
        isharedwith.append(current_username)
        # print('isharedwith_2', isharedwith)
        progressreport = audiodetails.getaudioprogressreport(projects, transcriptions, activeprojectname, isharedwith)

    # print(progressreport)

    return jsonify(progressreport=progressreport)


# get progress report
@app.route('/test', methods=['GET'])
@login_required
def test():
    projects, userprojects, projectsform, questionnaire, transcriptions = getdbcollections.getdbcollections(mongo,
                                                                                                        'projects',
                                                                                                        'userprojects',
                                                                                                        'projectsform',
                                                                                                        'questionnaire',
                                                                                                        'transcriptions')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)
    projectowner = getprojectowner.getprojectowner(projects,
                                                    activeprojectname)
    quesprojectform = getactiveprojectform.getactiveprojectform(projectsform,
                                                                projectowner,
                                                                activeprojectname)
    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                        current_username,
                                                        activeprojectname)

    # print('current_username', current_username)
    # print('currentuserprojectsname', currentuserprojectsname)
    # print('activeprojectname', activeprojectname)
    # print('projectowner', projectowner)
    # print('quesprojectform', quesprojectform)
    # print('shareinfo', shareinfo)

    return render_template('test.html',
                            projectName=activeprojectname,
                            quesprojectform=quesprojectform,
                            data=currentuserprojectsname,
                            shareinfo=shareinfo)

# uploadquesfiles route
@app.route('/uploadquesfiles', methods=['GET', 'POST'])
@login_required
def uploadquesfiles():
    projects, userprojects, questionnaires = getdbcollections.getdbcollections(mongo,
                                                'projects',
                                                'userprojects',
                                                'questionnaires')
    activeprojectname = getactiveprojectname.getactiveprojectname(current_user.username,
                            userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    current_username = getcurrentusername.getcurrentusername()

    questionaireprojectform = {
                                "username": "alice",
                                "projectname": "alice_project_1",
                                "Language": ["text", ["English", "Hindi"]],
                                "Script": ["", ["latin", "devanagari"]],
                                "Prompt Audio": ["file", ["audio"]],
                                "Domain": ["multiselect", ["General", "Agriculture", "Sports"]],
                                "Elicitation Method": ["select", ["Translation", "Agriculture", "Sports"]],
                                "Target": ["multiselect", ["case", "classifier", "adposition"]]
                                }
                                
    if request.method == 'POST':
        # speakerId = dict(request.form.lists())['speakerId'][0]
        new_ques_file = request.files.to_dict()
        
        questionnairedetails.savequesfiles(mongo,
                                            projects,
                                            userprojects,
                                            questionnaires,
                                            projectowner,
                                            activeprojectname,
                                            current_username,
                                            new_ques_file
                                        )

    return redirect(url_for('test'))

# Contact Us route
# create contact us form for the LiFE
@app.route('/contactus', methods=['GET', 'POST'])
# @login_required
def contactus():
    return render_template('contactus.html')

# LiFE Documentation route
@app.route('/documentation', methods=['GET', 'POST'])
# @login_required
def documentation():
    return render_template('documentation.html')

@app.route('/projecttype', methods=['GET', 'POST'])
@login_required
def projecttype():
    projects, userprojects = getdbcollections.getdbcollections(mongo,
                                                                'projects',
                                                                'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
    project_type = getprojecttype.getprojecttype(projects, activeprojectname)

    return jsonify(projectType=project_type)
