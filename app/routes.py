# using local disk to download the files

from flask import flash, redirect, render_template, url_for, request, json, jsonify, send_file
from pymongo import database
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
# import sqlite3
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import joblib
from rdflib import Graph, Literal, RDF, URIRef, XSD
from rdflib.namespace import RDFS, FOAF, RDF, SKOS
from rdflib.namespace import Namespace

import pandas as pd
import json

basedir = os.path.abspath(os.path.dirname(__file__))

print(f'{"#"*80}Base directory:\n{basedir}\n{"#"*80}')


# home page route
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    # form = OpenExistingProjectForm()
    # print(f'{"#"*80}\n{mongo.db.list_collection_names()}')
    userprojects = mongo.db.userprojects              # collection of users and their respective projects

    currentuserprojectsname =  list(currentuserprojects())
    activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
                    {'_id' : 0, 'activeproject': 1})['activeproject']
    print(currentuserprojectsname, activeprojectname)
    return render_template('home.html',  data=currentuserprojectsname, activeproject=activeprojectname)


# new project route
# create lexeme entry form for the new project
@app.route('/newproject', methods=['GET', 'POST'])
@login_required
def newproject():
    # if 'projectnames' not in mongo.db.list_collection_names():
    #     projectnames = mongo.db.projectnames                # collection containing projects name
    #     projectnames.insert({'_id':10, 'projectname':{}})
    currentuserprojectsname =  currentuserprojects()
    return render_template('newproject.html', data=currentuserprojectsname)

# get lexeme from sentences and save them to lexemes collection
def sentence_lexeme_to_lexemes(oneSentenceDetail, oneLexemeDetail):
    print(f'{"="*80}')
    # pprint(oneSentenceDetail)
    # print(f'{"="*80}')
    # pprint(oneLexemeDetail)
    # print(f'{"="*80}')

    for key, value in oneLexemeDetail.items():
        print(key, ' : ', value)
        print(f'{"="*80}')
    # sentence_to_lexeme = {}
    # sentence_to_lexeme["username"] = oneSentenceDetail["username"]
    # sentence_to_lexeme["projectname"] = oneSentenceDetail["projectname"]
    # sentence_to_lexeme["updatedBy"] = oneSentenceDetail["updatedBy"]
    # sentence_to_lexeme["lexemedeleteFlag"] = oneLexemeDetail["lexemedeleteFlag"]
    # sentence_to_lexeme["username"] = oneSentenceDetail["username"]
    # sentence_to_lexeme["username"] = oneSentenceDetail["username"]


# enter new sentences route
# enter new sentences in the project
@app.route('/enternewsentences', methods=['GET', 'POST'])
@login_required
def enternewsentences():
    # getting the collections
    projects = mongo.db.projects                        # collection containing projects name
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    lexemes = mongo.db.lexemes                          # collection containing entry of each lexeme and its details
    sentences = mongo.db.sentences                          # collection containing entry of each sentence and its details
    # activeprojectnames = mongo.db.activeprojectnames    # collection containing username and his/her last seen project name

    # getting the name of all the projects created by current user
    currentuserprojectsname =  currentuserprojects()

        # getting the name of the active project
    activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
                    {'_id' : 0, 'activeproject': 1})['activeproject']

    if request.method == 'POST':
        # newLexemeData = request.form.to_dict()
        newSentencesData = dict(request.form.lists())
        newSentencesFiles = request.files.to_dict()
        pprint(newSentencesData)
        print(f'{"="*80}')
        # to see format of the data coming from the front end look for file name newSentencesData.txt in data_format folder
        
        # dictionary to store files name
        newSentencesFilesName = {}
        for key in newSentencesFiles:
            if newSentencesFiles[key].filename != '':
                # adding microseconds of current time to differ two files of same name
                newSentencesFilesName[key] = (datetime.now().strftime('%f')+newSentencesFiles[key].filename)

        sentenceFieldIds = []
        interlineargloss = {}
        for key in newSentencesData.keys():
            if ('sentenceField' in key):
                # print(key[-1])
                sentenceFieldIds.append(key[-1])

        for sFId in sentenceFieldIds:
            # print(type(sFId), sFId)
            sentenceFieldId = sFId
            sentence = newSentencesData['sentenceField'+sFId][0]
            # interlineargloss['level_3'] = sentence
            split_sentence = sentence.split()
            sentenceMorphemicBreak = newSentencesData['sentenceMorphemicBreak'+sFId][0]
            interlineargloss['level_1'] = sentenceMorphemicBreak.replace('#', '')
            split_sentenceMorphemicBreak = sentenceMorphemicBreak.split()
            # print(split_sentenceMorphemicBreak)
            
            # save details for each sentence as the format shown in file name sentenceEntry.json in data_format folder
            sentenceDetails = {}
            # generate unique id using the datetime module
            Id = re.sub(r'[-: \.]', '', str(datetime.now()))
            sentenceDetails['username'] = current_user.username
            sentenceDetails['projectname'] = activeprojectname
            sentenceDetails['sentencedeleteFLAG'] = 0
            sentenceDetails['updatedBy'] = current_user.username
            sentenceDetails['sentenceId'] = 'S'+Id
            sentenceDetails['sentence'] = sentence
            sentenceDetails['langscripts'] = {
                                            "langname": "English",
                                            "langcode": "eng",
                                            "sentencescripts": {
                                                "ipa": "International Phonetic Alphabet",
                                                "Latn": "Latin"
                                            },
                                            "glosslangs": {
                                                "eng": "English"        
                                            },
                                            "glossscripts": {
                                                "Latn": "Latin"
                                            },
                                            "translationlangs": {
                                                "eng": "English",
                                                "hin": "Hindi"
                                            },
                                            "translationscripts": {
                                                "Latn": "Latin",
                                                "Deva": "Devanagari"
                                            }
                                        }

            morphemes = {}
            gloss = {}
            pos = {}
            split_sentenceMorphemeWise = []
            morphemeId = sFId+str(0)
            lexglossId = 'morphemicgloss'+morphemeId
            lexemeId = sentenceDetails['sentenceId']+'L'+str(0)
            lextypeId = 'lextype'+morphemeId
            posId = 'pos'+morphemeId
            interlineargloss_level_2 = ''
            for i in range(len(split_sentenceMorphemicBreak)):
                morph = {}

                if ('#' in split_sentenceMorphemicBreak[i]):
                    # print(split_sentenceMorphemicBreak[i].split('#'))
                    morphemic = split_sentenceMorphemicBreak[i].split('#')
                    split_sentenceMorphemicBreak[i] = split_sentenceMorphemicBreak[i].replace('#', '')
                    morphemes[split_sentence[i]] = split_sentenceMorphemicBreak[i]
                    # print(morphemic)
                    for j in range(len(morphemic)):
                        lexglossId = lexglossId[:len(lexglossId)-1]+str(int(lexglossId[-1])+1)
                        lexemeId = lexemeId[:len(lexemeId)-1]+str(int(lexemeId[-1])+1)
                        lextypeId = lextypeId[:len(lextypeId)-1]+str(int(lextypeId[-1])+1)
                        posId = posId[:len(posId)-1]+str(int(posId[-1])+1)
                        # print(morphemeId, lexglossId, lexemeId, lextypeId, posId)
                        # print(m)
                        morph[morphemic[j]] = {'lexgloss': '.'.join(newSentencesData[lexglossId]), 
                                            'lexemeID': lexemeId,
                                            'lextype': newSentencesData[lextypeId][0]}
                        if ('-' in morphemic[j][0]):
                            interlineargloss_level_2 += '-'+'.'.join(newSentencesData[lexglossId])
                        elif ('-' in morphemic[j][-1]):
                            interlineargloss_level_2 += '.'.join(newSentencesData[lexglossId])+'-'
                        else:
                            interlineargloss_level_2 += '.'.join(newSentencesData[lexglossId])    
                        gloss[split_sentence[i]] = morph
                        if ('-' not in morphemic[j] and posId in newSentencesData):
                            pos[split_sentence[i]] = newSentencesData[posId][0]
                # print(morph)
                        split_sentenceMorphemeWise.append(morphemic[j])
                else:
                    lexglossId = lexglossId[:len(lexglossId)-1]+str(int(lexglossId[-1])+1)
                    lexemeId = lexemeId[:len(lexemeId)-1]+str(int(lexemeId[-1])+1)
                    lextypeId = lextypeId[:len(lextypeId)-1]+str(int(lextypeId[-1])+1)
                    posId = posId[:len(posId)-1]+str(int(posId[-1])+1)
                    # print(morphemeId, lexglossId, lexemeId, lextypeId, posId) 
                    #   
                    morphemes[split_sentence[i]] = split_sentenceMorphemicBreak[i]
                    morph[split_sentence[i]] = {'lexgloss': '.'.join(newSentencesData[lexglossId]), 
                                            'lexemeID': lexemeId,
                                            'lextype': newSentencesData[lextypeId][0]}
                    interlineargloss_level_2 += ' '+'.'.join(newSentencesData[lexglossId])+' '                       
                    gloss[split_sentence[i]] = morph
                    pos[split_sentence[i]] = newSentencesData[posId][0]
                    split_sentenceMorphemeWise.append(split_sentenceMorphemicBreak[i])

                sentenceDetails['morphemes'] = morphemes
                
            # print(split_sentenceMorphemicBreak)
            sentenceDetails['gloss'] = gloss
            sentenceDetails['pos'] = pos

            translation = {}
            translation['eng-Latn'] = newSentencesData['sentenceTranslation'+sFId][0]
            translation['hin-Deva'] = sentenceDetails['sentence'] 
            sentenceDetails['translation'] = translation
            
            interlineargloss['level_2'] = interlineargloss_level_2.strip().replace('  ', ' ')
            interlineargloss['level_3'] = translation['eng-Latn']
            sentenceDetails['interlineargloss'] = interlineargloss

            # save file names of a sentence in sentenceDetails dictionary with other details related to the sentence
            if len(newSentencesFilesName) != 0:    
                sentenceDetails['filesname'] = newSentencesFilesName

            pprint(sentenceDetails)
            print(f'{"="*80}')
            
            # sentence_lexeme_to_lexemes(sentenceDetails)

            # saving files for the new lexeme to the database in fs collection
            for (filename, key) in zip(newSentencesFilesName.values(), newSentencesFiles):
                mongo.save_file(filename, newSentencesFiles[key], sentenceId=sentenceDetails['sentenceId'], username=current_user.username,\
                                projectname=sentenceDetails['projectname'], sentence = sentenceDetails['sentence'],\
                                updatedBy=current_user.username)

            # enter the sentence details to the database
            sentences.insert(sentenceDetails)

    currentuserprojectsname =  currentuserprojects()

    # get the list of lexeme entries for current project to show in dictionary view table
    lst = list()
    # lst.append(activeprojectname)
    for interlineargloss in sentences.find({ 'projectname' : activeprojectname }, \
                            {'_id' : 0, 'sentenceId' : 1, 'interlineargloss' : 1}):
        lst.append(interlineargloss)
    # print(lst)

    # # getting the details of one sentence in the activeproject
    # oneSentenceDetail = sentences.find_one({ 'username' : current_user.username, 'projectname': '20211218_114658', \
    #                 'sentenceId': "S20211218163718533966"},\
    #                 {'_id' : 0})
    # # getting the details of one lexeme in the activeproject
    # oneLexemeDetail = lexemes.find_one({ 'username' : current_user.username, 'projectname': '20211218_114658', \
    #                 'lexemeId': "L20211218155932463521"},\
    #                 {'_id' : 0})
    # sentence_lexeme_to_lexemes(oneSentenceDetail, oneLexemeDetail)

    if  (len(lst) == 0):
        return render_template('enternewsentences.html', projectName=activeprojectname, data=currentuserprojectsname)        

    return render_template('enternewsentences.html', projectName=activeprojectname, sdata=lst, data=currentuserprojectsname)

# get new sentences route
# get new sentences in the project coming throug ajax
@app.route('/getnewsentences', methods=['GET', 'POST'])
@login_required
def getnewsentences():
    # getting the collections
    projects = mongo.db.projects                        # collection containing projects name
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    lexemes = mongo.db.lexemes                          # collection containing entry of each lexeme and its details
    sentences = mongo.db.sentences                          # collection containing entry of each sentence and its details
    # activeprojectnames = mongo.db.activeprojectnames    # collection containing username and his/her last seen project name

    # getting the name of all the projects created by current user
    currentuserprojectsname =  currentuserprojects()

        # getting the name of the active project
    activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
                    {'_id' : 0, 'activeproject': 1})['activeproject']

    sentence = request.args.get('a').split(',')                    # data through ajax
    sentenceFieldId = sentence[0]
    split_sentence = sentence[1].split()
    print(sentenceFieldId, split_sentence)
    
    sentenceDetails = {}
    # generate unique id using the datetime module
    Id = re.sub(r'[-: \.]', '', str(datetime.now()))
    sentenceDetails['username'] = current_user.username
    sentenceDetails['projectname'] = activeprojectname
    sentenceDetails['sentencedeleteFLAG'] = 0
    sentenceDetails['updatedBy'] = current_user.username
    sentenceDetails['sentenceId'] = 'S'+Id
    sentenceDetails['sentence'] = sentence[1]
    sentenceDetails['langscripts'] = {
                                        "langname": "English",
                                        "langcode": "eng",
                                        "sentencescripts": {
                                            "ipa": "International Phonetic Alphabet",
                                            "Latn": "Latin"
                                        },
                                        "glosslangs": {
                                            "eng": "English"        
                                        },
                                        "glossscripts": {
                                            "Latn": "Latin"
                                        },
                                        "translationlangs": {
                                            "eng": "English",
                                            "hin": "Hindi"
                                        },
                                        "translationscripts": {
                                            "Latn": "Latin",
                                            "Deva": "Devanagari"
                                        }
                                    }
    # sentenceDetails['lexemeId'] = 'L'+Id
    morphemes = {}
    gloss = {}
    for morpheme in split_sentence:
        remorpheme = re.sub(r'[#-]', '', morpheme)
        morphemes[remorpheme] = morpheme.lower()
        if ('#' in morpheme):
            # morpheme = re.sub(r'-', ' -', morpheme)
            morpheme = morpheme.split('#')
            mor = []
            for morph in morpheme:
                mor.append(morph)
            gloss[remorpheme] = mor
        else:
            gloss[morpheme] = [morpheme]        
    sentenceDetails['morphemes'] = morphemes
    pprint(sentenceDetails) 
    print(gloss)  

    return jsonify(sentenceFieldId=sentenceFieldId, gloss=gloss, result2=sentence)

    # currentuserprojectsname =  currentuserprojects()
    # return render_template('enternewsentences.html', data=currentuserprojectsname)

# new automation route
# buttons working for different automation(POS, morph analyser)
@app.route('/automation', methods=['GET', 'POST'])
@login_required
def automation():
    userprojects = mongo.db.userprojects              # collection of users and their respective projects

    # getting the name of the active project
    activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
                    {'_id' : 0, 'activeproject': 1})['activeproject']
    currentuserprojectsname =  currentuserprojects()
    return render_template('automation.html', projectName=activeprojectname, data=currentuserprojectsname)

# def autoviML(df):
    from autoviml.Auto_ViML import Auto_ViML

    model, features, trainm, testm = Auto_ViML(
    train=df,
    target="label",
    test="",
    sample_submission="",
    hyper_param="RS",
    feature_reduction=True,
    scoring_parameter="weighted-f1",
    KMeans_Featurizer=False,
    Boosting_Flag=None,
    Binning_Flag=False,
    Add_Poly=False,
    Stacking_Flag=True,
    Imbalanced_Flag=True,
    verbose=3
    )

def naiveBayes(corpus, y, x_test):
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus)

    # example for saving python object as pkl
    joblib.dump(vectorizer, "trainedModels/naiveBayesPOSVectorizer.pkl")

    
    # print(vectorizer.get_feature_names_out())
    # print(x_test.toarray())
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
    # getting the collections
    projects = mongo.db.projects                        # collection containing projects name
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    lexemes = mongo.db.lexemes                          # collection containing entry of each lexeme and its details
    sentences = mongo.db.sentences                          # collection containing entry of each sentence and its details
    # activeprojectnames = mongo.db.activeprojectnames    # collection containing username and his/her last seen project name

    # getting the name of all the projects created by current user
    currentuserprojectsname =  currentuserprojects()

        # getting the name of the active project
    activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
                    {'_id' : 0, 'activeproject': 1})['activeproject']

    wordList = request.args.get('a').split(',')                    # data through ajax
    print(wordList)



    if (len(wordList) != 0):
        
        # load model
        with open('trainedModels/naiveBayesPOSModel.pkl', 'rb') as f:
            clf = pickle.load(f)

        # loading pickled vectorizer
        vectorizer = joblib.load("trainedModels/naiveBayesPOSVectorizer.pkl")
        x_test = vectorizer.transform(wordList)
        predictedpos = list(clf.predict(x_test))

        print(predictedpos)
        predictedPOS = []
        for word, pos in zip(wordList, predictedpos):
            # if ('-' in word): pass
            # else:
            print([word, pos])
            predictedPOS.append([word, pos])

        print(predictedPOS)        

        return jsonify(predictedPOS=predictedPOS)

    
    return render_template('automation.html', data=currentuserprojectsname)

@app.route('/automatepos', methods=['GET', 'POST'])
@login_required
def automatepos():

    # getting the collections
    projects = mongo.db.projects                        # collection containing projects name
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    lexemes = mongo.db.lexemes                          # collection containing entry of each lexeme and its details
    sentences = mongo.db.sentences                          # collection containing entry of each sentence and its details
    # activeprojectnames = mongo.db.activeprojectnames    # collection containing username and his/her last seen project name

    # getting the name of all the projects created by current user
    currentuserprojectsname =  currentuserprojects()

        # getting the name of the active project
    activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
                    {'_id' : 0, 'activeproject': 1})['activeproject']

    sentence = request.args.get('a').split(',')                    # data through ajax
    # create dataframe from the json type data
    posdf = {}
    word = []
    label = []
    for pos in sentences.find({ 'projectname' : activeprojectname, 'sentencedeleteFLAG' : 0 }, \
                        {'_id' : 0, 'pos': 1}):
        # print(pos['pos'])
        
        for key, value in pos['pos'].items():
            # print(key, value)
            word.append(key)
            label.append(value)
        posdf['word'] = word
        posdf['label'] = label
    # print(posdf)
    posdf = pd.DataFrame.from_dict(posdf)
    # print(word, label)
    x_test = ['cow']
    naiveBayes(word, label, x_test)
    # autoviML(posdf)
    # print(posdf)
    # print(type(posdf))
    # posdf.to_csv('data_format/posdf.csv', index=False)

    # lst.append(lexeme)
    print('In Automate POS')
    return render_template('automation.html', data=currentuserprojectsname)

# dictionary view route
# display lexeme entries for current project in a table
@app.route('/dictionaryview', methods=['GET', 'POST'])
@login_required
def dictionaryview():
    print(current_user.username)
    # getting the collections
    projects = mongo.db.projects                        # collection containing projects name
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    lexemes = mongo.db.lexemes                          # collection containing entry of each lexeme and its details
    # activeprojectnames = mongo.db.activeprojectnames    # collection containing username and his/her last seen project name

    # getting the name of all the projects created by current user
    currentuserprojectsname =  currentuserprojects()

    # getting the name of the active project
    activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
                    {'_id' : 0, 'activeproject': 1})['activeproject']
    # new lexeme details coming from current project form
    if request.method == 'POST':

        # newLexemeData = request.form.to_dict()
        newLexemeData = dict(request.form.lists())
        newLexemeFiles = request.files.to_dict()
        pprint(newLexemeData)
        # dictionary to store files name
        newLexemeFilesName = {}
        for key in newLexemeFiles:
            if newLexemeFiles[key].filename != '':
                # adding microseconds of current time to differ two files of same name
                newLexemeFilesName[key] = (datetime.now().strftime('%f')+newLexemeFiles[key].filename)

        # if len(newLexemeFilesName) != 0:    
        #     newLexemeData['filesname'] = newLexemeFilesName                   

        # format data filled in enter new lexeme form    
        lexemeFormData = {}
        sense = {}
        variant = {}
        allomorph = {}
        lemon = ''

        lexemeFormData['username'] = current_user.username

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
            for num in range(1, int(newLexemeData['senseCount'][0])+1):
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
            for num in range(1, int(newLexemeData['variantCount'][0])+1):
                variantlist = []
                for key, value in newLexemeData.items():
                    if 'Variant '+str(num) in key:
                        k = re.search(r'([\w+\s]+) Variant', key)
                        variantlist.append({k[1] : value[0]})
                variant['Variant '+str(num)] = variantlist
            # pprint.pprint(variant)
            return variant

        def allomorphListOfDict(allomorphCount):
            """'List of dictionary' of allomorph"""
            for num in range(1, int(newLexemeData['allomorphCount'][0])+1):
                allomorphlist = []
                for key, value in newLexemeData.items():
                    if 'Allomorph '+str(num) in key:
                        k = re.search(r'([\w+\s]+) Allomorph', key)
                        allomorphlist.append({k[1] : value[0]})
                allomorph['Allomorph '+str(num)] = allomorphlist
            # pprint.pprint(allomorph)
            return allomorph

        def customFields():
            """'List of dictionary' of custom fields"""
            customFieldsList = []
            for key, value in newLexemeData.items():
                if 'Custom' in key:
                    k = re.search(r'Field (\w+)', key)
                    customFieldsList.append({k[1] : value[0]})
            # pprint.pprint(sense)
            return customFieldsList

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

        # create lexemeId
        projectname = newLexemeData['projectname'][0]
        project = projects.find_one({}, {projectname : 1})
        lexemeCount = projects.find_one({}, {projectname : 1})[projectname]['lexemeInserted']+1
        lexemeId = projectname+lexemeFormData['headword']+str(lexemeCount)
        Id = re.sub(r'[-: \.]', '', str(datetime.now()))
        lexemeId = 'L'+Id
        

        # save file names of a lexeme in lexemeFormData dictionary with other details related to the lexeme
        if len(newLexemeFilesName) != 0:    
            lexemeFormData['filesname'] = newLexemeFilesName

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
        langscripts["headwordscript"] = {headwordscript[0]+headwordscript[1:4].lower(): headwordscript}
        lexemeformscripts = {}
        for i in range(len(lexemeFormData['Lexeme Form Script'])):
            for lfs in lexemeFormData['Lexeme Form Script'][i].keys():
                lexemeformscripts[lfs[0]+lfs[1:4]] = lfs
        langscripts["lexemeformscripts"] = lexemeformscripts
        glosslangs = {}
        for gl in newLexemeData.keys():
            if ('Gloss' in gl):
                gl = gl.split()[1]
                glosslangs[gl[0:3]] = gl
        langscripts["glosslangs"] = glosslangs
        langscripts["glossscripts"] = {
                                        "Deva": "Devanagari",
                                        "Gujr": "Gujarati",
                                        "Latn": "Latin"
                                    }
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
                        Lexical_Relation[v[0]] = v[0]
                    else:    
                        key[k] = v
            
            key['Gloss'] = Gloss
            key['Definition'] = Definition
            key['Lexical Relation'] = Lexical_Relation
            
            SenseNew[keyParent] = key
        # pprint(senseNew)
        lexemeFormData['SenseNew'] = SenseNew

        lexemeForm = {}
        for lexForm in lexemeFormData['Lexeme Form Script']:
            for lexKey, lexValue in lexForm.items():
                lexemeForm[lexKey[:4]] = lexValue

        lexemeFormData['Lexeme Form'] = lexemeForm

        # lexemeForm = lexemeFormData['Lexeme Form Script']
        # lemon += ':'+lexemeFormData['headword']+' a lemon:LexicalEntry ;\n\tlemon:canonicalForm [\n'
        # for i in range(len(lexemeForm)):
        #     key = list(lexemeForm[i].keys())[0]
        #     value = list(lexemeForm[i].values())[0]
        #     print(key, value)
        #     lemon += '\tlemon:writtenRep "'+value+'" @'+key+' ;\n'
        # lemon += '\tlexinfo:pronunciation "'+lexemeFormData["Pronunciation"]+'"\n] .'

        # lexemeFormData['lemon'] = lemon
        # pprint(f"{'#'*80}\n{lexemeFormData}")

        # saving files for the new lexeme to the database in fs collection
        for (filename, key) in zip(newLexemeFilesName.values(), newLexemeFiles):
            mongo.save_file(filename, newLexemeFiles[key], lexemeId=lexemeId, username=current_user.username,\
                            projectname=lexemeFormData['projectname'], headword=lexemeFormData['headword'],\
                            updatedBy=current_user.username)            
       
        # saving data for that new lexeme to database in lexemes collection
        lexemes.insert(lexemeFormData)
        print(f'{"="*80}\nLexeme Form :')
        pprint(lexemeFormData)
        print(f'{"="*80}')


        # update lexemeInserted count of the project in projects collection
        project[projectname]['lexemeInserted'] = lexemeCount
        # print(f'{"#"*80}\n{project}')
        projects.update_one({}, { '$set' : { projectname : project[projectname] }})

        flash('Successfully added new lexeme')
        return redirect(url_for('enternewlexeme'))

    try:
        my_projects = len(userprojects.find_one({'username' : current_user.username})["myproject"])
        shared_projects = len(userprojects.find_one({'username' : current_user.username})["projectsharedwithme"])
        print(my_projects, shared_projects)
        if  (my_projects+shared_projects)== 0:
            flash('Please create your first project')
            return redirect(url_for('home'))
    except:
        print(f'{"#"*80}\nCurrent user details not in database!!!')
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
            lst.append(lexeme)
    except:
        flash('Enter first lexeme of the project')

    # print(lst)
    return render_template('dictionaryview.html', projectName=activeprojectname, sdata=lst, count=len(lst), data=currentuserprojectsname)    


# enter new lexeme route
# display form for new lexeme entry for current project
@app.route('/enternewlexeme', methods=['GET', 'POST'])
@login_required
def enternewlexeme():
    # getting the collections
    projects = mongo.db.projects                        # collection containing projects name
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    projectsform = mongo.db.projectsform                # collection of project specific form created by the user
    # activeprojectnames = mongo.db.activeprojectnames    # collection containing username and his/her last seen project name
    # projectnames = mongo.db.projectnames                # collection containing projects name
    
    # getting the name of all the projects created by current user
    currentuserprojectsname =  currentuserprojects()

    # getting the name of the active project
    # activeprojectname = activeprojectnames.find_one({ 'username' : current_user.username })
    activeprojectname = userprojects.find_one({ 'username' : current_user.username })['activeproject']

    # new project form containing dictionary fields and its type
    if request.method == 'POST':
        projectFormData = dict(request.form.lists())

        # print(f'{"#"*80}\nprojectFormData\n{projectFormData}')

        dynamicFormField = []
        listOfCustomFields = []
        projectForm = {}
        projectForm['projectname'] = projectFormData['projectname'][0]
        
        # print(f'{"#"*80}\n{projectnames.find_one({"_id":10})["projectname"]}')

        # chech uniqueness of the project name and update projectname list
        # projectnamelist = projectnames.find_one({"_id":10})["projectname"]
        if projects.find_one({}) != None and projectForm["projectname"] in projects.find_one({}).keys():
            flash(f'Project Name : {projectForm["projectname"]} already exist!')
            return redirect(url_for('newproject'))
        # projectslist = list(projectsCollection["projectname"].keys())
        #get _id in collection name projects
        if projects.find_one({}) != None:
            projects_id = projects.find_one({}, {"_id" : 1})["_id"]
            # print(f'{"#"*80}\n{projects_id}\n')
            # for proname in projectslist:
            #     # print(f'{"#"*80}\n{proname}\n')
            #     if proname == projectForm['projectname']:
            #         flash(f'Project Name : {projectForm["projectname"]} already exist!')
            #         return redirect(url_for('newproject'))

            projectForm['username'] = current_user.username

            projects.update_one({ "_id" : projects_id }, \
                { '$set' : { projectForm['projectname'] : {"projectOwner" : current_user.username,"lexemeInserted" : 0, "lexemeDeleted" : 0, \
                    'sharedwith': [projectForm['username']], 'projectdeleteFLAG' : 0} }})

            
            # print(usersprojects.find_one({ 'username' : current_user.username }))

            # print(f'{"#"*80}\n{usersprojects.find_one({"username" : current_user.username})["projectname"]}')

            # get curent user project list and update
            userprojectnamelist = userprojects.find_one({'username' : current_user.username})["myproject"]
            # print(f'{"#"*80}\n{userprojectnamelist}')
            userprojectnamelist.append(projectForm['projectname'])
            userprojects.update_one({ 'username' : current_user.username }, \
                { '$set' : { 'myproject' : userprojectnamelist, 'activeproject' :  projectForm['projectname']}})

            # dynamicFormField = []
            # listOfCustomFields = []

            for key, value in projectFormData.items():
                if re.search(r'[0-9]+', key):
                    dynamicFormField.append(value[0])
                elif key == 'Lexeme Form Script':
                    projectForm[key] = value
                elif key == 'Gloss Language':
                    value.append('English')
                    projectForm[key] = value    
                elif len(value) == 1:
                    projectForm[key] = value[0]
                else:
                    projectForm[key] = value

            # print(f'{"#"*80}\ndynamicFormField\n{len(dynamicFormField)}')
            if len(dynamicFormField) > 1:
                for i in range(0,len(dynamicFormField),2):
                    listOfCustomFields.append({dynamicFormField[i] : dynamicFormField[i+1]})

                projectForm['Custom Fields'] = listOfCustomFields

            # print(f'{"#"*80}\nProject Form :\n{projectForm}')
            projectsform.insert(projectForm)
            # else:
            #     flash(f'Project Name : {projectForm["projectname"]} already created by {current_user.username}')
            #     return redirect(url_for('newproject'))

            # if activeprojectnames.find_one({'username' : current_user.username}) is None:
            #     activeprojectnames.insert({ 'username' : current_user.username, 'projectname' : projectForm['projectname'] })
            # else:
            # activeprojectnames.update_one({ 'username' : current_user.username }, \
            #                             {'$set' : { 'projectname' : projectForm['projectname'] }})

            currentuserprojectsname =  currentuserprojects()
            activeprojectname = userprojects.find_one({ 'username' : current_user.username })['activeproject']

            x = projectsform.find_one_or_404({'projectname' : activeprojectname,\
                                            'username' : current_user.username}, { "_id" : 0 })
            
            # x = change(x)

            # print(f'{"#"*80}\nx:\n{x}')
            if x is not None:
                return render_template('enternewlexeme.html', newData=x, data=currentuserprojectsname)
            return render_template('enternewlexeme.html')

    # if method is not 'POST'
    projectOwner = projects.find_one({}, {"_id" : 0, activeprojectname : 1})[activeprojectname]["projectOwner"]
    print(projectOwner)
    y = projectsform.find_one_or_404({'projectname' : activeprojectname,'username' : projectOwner}, { "_id" : 0 }) 
    # y = change(y)
    # print(f'{"#"*80}\ny:\n{y}')

    if y is not None:
        return render_template('enternewlexeme.html',  newData=y, data=currentuserprojectsname)
    return render_template('enternewlexeme.html')   


# enter new lexeme route
# display form for new lexeme entry for current project
@app.route('/editlexeme', methods=['GET', 'POST'])
@login_required
def editlexeme():
    return render_template('editlexeme.html')  

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
    print(f'{"="*80}\nheadwords from downloadselectedlexeme route:\n {headwords}\n{"="*80}')
    
    download_format = headwords['downloadFormat']
    # print(download_format)

    del headwords['downloadFormat']

    print(f'{"="*80}\ndelete download format:\n {headwords}\n{"="*80}')

    activeprojectname = userprojects.find_one({ 'username' : current_user.username })['activeproject']
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

    # def test():
    #     g = Graph()
    #     semweb = URIRef('http://dbpedia.org/resource/Semantic_Web')
    #     type = g.value(semweb, RDFS.label)

    #     g.add((
    #         URIRef("http://example.com/person/nick"),
    #         FOAF.givenName,
    #         Literal("Nick", datatype=XSD.string)
    #     ))

    #     g.bind("foaf", FOAF)
    #     g.bind("xsd", XSD)

    #     print(g.serialize(format="turtle"))


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

    # def add_other_forms(g_other_form, life, lex_entry, lex_item, other_form, dict_lang):
    #     # g_other_form = Graph()
    #     # g_other_form.bind("ontolex", ontolex)
    #     # g_other_form.bind("life", life)

    #     g_other_form.add((
    #         URIRef(life[lex_item+'_otherForm']),
    #         RDF.type,
    #         ontolex.form
    #     ))

    #     g_other_form.add((
    #         URIRef(life[lex_item+'_otherForm']),
    #         ontolex.writtenRep,
    #         Literal(other_form, lang=dict_lang)
    #     ))


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

    def generate_rdf(write_path, lexicon, domain_name, project, rdf_format):
        g_lex = Graph()
        
        for lex_entry in lexicon:
            json_to_rdf_lexicon(g_lex, lex_entry, 
                            domain_name, project, rdf_format)
            
        with open (write_path, 'wb') as f_w:    
            rdf_out = g_lex.serialize(format=rdf_format)
            f_w.write(rdf_out)

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
        f_w = open (write_path, 'wb')
        df.to_excel(f_w, index=False, engine='openpyxl')

    def generate_html(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        with open (write_path, 'w') as f_w:
            df.to_html(f_w, index=False)

    def generate_latex(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        with open (write_path, 'w') as f_w:
            df.to_latex(f_w, index=False)

    def generate_markdown(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        with open (write_path, 'w') as f_w:
            df.to_markdown(f_w, index=False)

    def generate_pdf(write_path, lexicon, project):
        return None

    def download_lexicon(lex_json, write_path, 
        output_format='rdf', rdf_format='turtle'):
        file_ext_map = {'turtle': '.ttl', 'n3': '.n3', 
        'ntriples': '.nt', 'rdfxml': '.rdf', 'json': '.json', 'csv': '.csv',
        'xlsx': '.xlsx', 'pdf': '.pdf', 'html': '.html', 'latex': '.tex',
        'markdown': '.md', 'ods': '.ods'}

        domain_name = 'http://lifeapp.in'
        
        metadata = lex_json[0]
        project = metadata['projectname']

        lexicon = lex_json[1:]

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
                    generate_pdf(write_file, lexicon)
                elif output_format == 'markdown':
                    generate_markdown(write_file, lexicon)
                elif output_format == 'html':
                    generate_html(write_file, lexicon)
                elif output_format == 'latex':
                    generate_latex(write_file, lexicon)
                elif output_format == 'ods':
                    generate_ods(write_file, lexicon)
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
            print(rdf_format)
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
        print(f)
        os.remove(f)
    
    # return send_file('../download.zip', as_attachment=True)
    return 'OK'

# download route
@app.route('/downloadproject', methods=['GET', 'POST'])
def downloadproject():
    # getting the collections
    projects = mongo.db.projects                        # collection containing projects name
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    lexemes = mongo.db.lexemes                          # collection containing entry of each lexeme and its details
    sentences = mongo.db.sentences                          # collection containing entry of each sentence and its details
    fs =  gridfs.GridFS(mongo.db)                       # creating GridFS instance to get required files

    lst = list()

    activeprojectname = userprojects.find_one({ 'username' : current_user.username })['activeproject']
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
                    print(f'{"#"*80}')
                    # print(basedir+'/app/download/'+name)
                    print(f'{"#"*80}')
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

    
    # get all sentences of the activeproject    
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
        print(files)
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
                {'_id' : 0, 'activeproject': 1})['activeproject']
    lst.append(projectname)
    print(f'{"#"*80}\n{projectname}')
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
    ## SQLite Database 
    # con = sqlite3.connect('app.db')
    # cur = con.cursor()

    # usersList = []
    # for user in cur.execute('SELECT username FROM UserLogin'):
    #     usersList.append(user[0])
    #     # print(user)
    # usersList.remove(current_user.username)
    # # print(usersList)
    # MongoDB Database
    userlogin = mongo.db.userlogin                          # collection of users and their login details
    usersList = []
    for user in userlogin.find({}, {"_id": 0, "username": 1}):
        # print(user)
        usersList.append(user["username"])
        # print(user)
    usersList.remove(current_user.username)
    print(usersList)
    return jsonify(usersList=usersList)

# modal view with complete detail of a lexeme for edit
# edit button on dictionary view table
@app.route('/shareprojectwith', methods=['GET', 'POST'])
def shareprojectwith():
    # getting the collections
    projectsform = mongo.db.projectsform                # collection of project specific form created by the user
    lexemes = mongo.db.lexemes                          # collection containing entry of each lexeme and its details
    userprojects = mongo.db.userprojects              # collection of users and their respective projects
    projects = mongo.db.projects              # collection of users and their respective projects

    users = request.args.get('a').split(',')                    # data through ajax
    print(users)
    activeprojectname = userprojects.find_one({ 'username' : current_user.username })['activeproject']
    #get _id and project name in the collection projects
    activeprojectdetails = projects.find_one({}, {"_id" : 1, activeprojectname : 1})
    project_id = activeprojectdetails["_id"]
    project_name = activeprojectdetails[activeprojectname]
    projectsharedwith = project_name["sharedwith"]
    # # print(activeprojectname)
    if (len(users[0]) != 0):
        for user in users:
            # get list of projects shared with the user
            usershareprojectsname = userprojects.find_one({ 'username' : user })['projectsharedwithme']
            # update list of projects shared with the user
            usershareprojectsname.append(activeprojectname)
            usershareprojectsname = list(set(usershareprojectsname))
            # update list of projects shared with the user in collection
            userprojects.update_one({ 'username' : user }, { '$set' : { 'projectsharedwithme' : usershareprojectsname}})
            # userprojectsname = userprojects.find_one({ 'username' : user })
            # print(userprojectsname)

            # update active project sharedwith list
            projectsharedwith.append(user)
            projectsharedwith = list(set(projectsharedwith))

    #     projectForm['username'] = current_user.username
    # update projects collection
    project_name["sharedwith"] = projectsharedwith
    projects.update_one({ "_id" : project_id }, { '$set' : { activeprojectname : project_name }})
    # print(project_id)
    # print(activeprojectname)
    # print(project_name)
    # print(projectsharedwith)
    # return jsonify(users=users)
    # return render_template('dictionaryview.html')
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
    print(headword)

    activeprojectname = userprojects.find_one({ 'username' : current_user.username })['activeproject']
    # print(activeprojectname)
    
    projectOwner = projects.find_one({}, {"_id" : 0, activeprojectname : 1})[activeprojectname]["projectOwner"]
    # print(projectOwner)
    lexeme = lexemes.find_one({'username' : projectOwner, 'lexemeId' : headword[0], },\
                            {'_id' : 0, 'username' : 0})

    # print(lexeme["lemon"])

    filen = []
    if 'filesname' in lexeme:
        for filename in lexeme['filesname']:
            filen.append(url_for('retrieve', filename=filename))

    # lexeme = change(lexeme)
    # print(lexeme)

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
    print(headword)

    activeprojectname = userprojects.find_one({ 'username' : current_user.username })['activeproject']
    # print(activeprojectname)
    
    projectOwner = projects.find_one({}, {"_id" : 0, activeprojectname : 1})[activeprojectname]["projectOwner"]
    # print(projectOwner)

    if request.method == 'POST':

        newLexemeData = request.form.to_dict()
        print(newLexemeData)
        return redirect(url_for('dictionaryview'))
    
    # activeprojectname = userprojects.find_one({ 'username' : current_user.username },\
    #                 {'_id' : 0, 'activeproject': 1})['activeproject']
    lexeme = lexemes.find_one({'username' : projectOwner, 'lexemeId' : headword[0], },\
                            {'_id' : 0, 'username' : 0})
    
    filen = []
    if 'filesname' in lexeme:
        for filename in lexeme['filesname']:
            filen.append(url_for('retrieve', filename=filename))

    # lexeme = change(lexeme)
    # pprint(lexeme)

    y = projectsform.find_one_or_404({'projectname' : activeprojectname,\
                                'username' : projectOwner}, { "_id" : 0 })                             
    # y = change(y)
    # print(y)
    return jsonify(newData=y, result1=lexeme, result2=filen)


# delete button on dictionary view table
@app.route('/lexemedelete', methods=['GET', 'POST'])
def lexemedelete():
    # getting the collections
    projectsform = mongo.db.projectsform                # collection of project specific form created by the user
    lexemes = mongo.db.lexemes                          # collection containing entry of each lexeme and its details
    userprojects = mongo.db.userprojects                # collection of users and their respective projects
    projects = mongo.db.projects                        # collection of projects


    headword = request.args.get('a').split(',')                    # data through ajax
    print(headword[0])
    
    activeprojectname = userprojects.find_one({ 'username' : current_user.username })['activeproject']
    # print(activeprojectname)
    
    projectOwner = projects.find_one({}, {"_id" : 0, activeprojectname : 1})[activeprojectname]["projectOwner"]
    # print(projectOwner)

    # l = lexemes.find_one({ 'username' : projectOwner, 'projectname' : activeprojectname, 'lexemeId' : headword[0] }, \
    #                             {'_id' : 0, 'headword' : 1, 'gloss' : 1, 'grammaticalcategory' : 1, 'lexemeId' : 1})
    # print(l)

    lexemes.update_one({'username' : projectOwner, 'lexemeId' : headword[0]},\
                        { '$set': { 'lexemedeleteFLAG': 1 }})
                    
    return jsonify(msg=headword[1]+' deletion successful')
    # return 'OK'

# delete button on dictionary view table
@app.route('/deletemultiplelexemes', methods=['GET', 'POST'])
def deletemultiplelexemes():
    # getting the collections
    projectsform = mongo.db.projectsform                # collection of project specific form created by the user
    lexemes = mongo.db.lexemes                          # collection containing entry of each lexeme and its details
    userprojects = mongo.db.userprojects                # collection of users and their respective projects
    projects = mongo.db.projects                        # collection of projects
    
    activeprojectname = userprojects.find_one({ 'username' : current_user.username })['activeproject']
    
    projectOwner = projects.find_one({}, {"_id" : 0, activeprojectname : 1})[activeprojectname]["projectOwner"]
    print(projectOwner)

    headwords = request.args.get('data')                   # data through ajax
    headwords = eval(headwords)

    # print(headwords)
    for headwordId in headwords.keys():
        lexemes.update_one({'username' : projectOwner, 'lexemeId' : headwordId, \
                        }, { '$set': { 'lexemedeleteFLAG': 1 }})

    return 'OK'

@app.route('/lexemeupdate', methods=['GET', 'POST'])
def lexemeupdate():
    # getting the collections
    lexemes = mongo.db.lexemes                          # collection containing entry of each lexeme and its details
    activeprojectnames = mongo.db.activeprojectnames    # collection containing username and his/her last seen project name

    # getting the name of all the projects created by current user
    currentuserprojectsname =  currentuserprojects()

    # getting the name of the active project
    activeprojectname = activeprojectnames.find_one({ 'username' : current_user.username })

    # new lexeme details coming from current project form
    if request.method == 'POST':

        # newLexemeData = request.form.to_dict()
        newLexemeData = dict(request.form.lists())                   

        # format data filled in enter new lexeme form    
        lexemeFormData = {}
        sense = {}
        variant = {}
        allomorph = {}

        lexemeFormData['username'] = current_user.username

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
            for num in range(1, int(newLexemeData['senseCount'][0])+1):
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
            for num in range(1, int(newLexemeData['variantCount'][0])+1):
                variantlist = []
                for key, value in newLexemeData.items():
                    if 'Variant '+str(num) in key:
                        k = re.search(r'([\w+\s]+) Variant', key)
                        variantlist.append({k[1] : value[0]})
                variant['Variant '+str(num)] = variantlist
            # pprint.pprint(variant)
            return variant

        def allomorphListOfDict(allomorphCount):
            """'List of dictionary' of allomorph"""
            for num in range(1, int(newLexemeData['allomorphCount'][0])+1):
                allomorphlist = []
                for key, value in newLexemeData.items():
                    if 'Allomorph '+str(num) in key:
                        k = re.search(r'([\w+\s]+) Allomorph', key)
                        allomorphlist.append({k[1] : value[0]})
                allomorph['Allomorph '+str(num)] = allomorphlist
            # pprint.pprint(allomorph)
            return allomorph

        def customFields():
            """'List of dictionary' of custom fields"""
            customFieldsList = []
            for key, value in newLexemeData.items():
                if 'Custom' in key:
                    k = re.search(r'Field (\w+)', key)
                    customFieldsList.append({k[1] : value[0]})
            # pprint.pprint(sense)
            return customFieldsList

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
            else:
                # print(lexemeFormData)
                # print(key)
                lexemeFormData[key] = value[0]


        # if len(newLexemeFilesName) != 0:    
        #     lexemeFormData['filesname'] = newLexemeFilesName
        lexemeFormData['gloss'] = lexemeFormData['Sense']['Sense 1'][0]['Gloss English']
        lexemeFormData['grammaticalcategory'] = lexemeFormData['Sense']['Sense 1'][4]['Grammatical Category']
        lexemeFormData['projectname'] = activeprojectname['projectname']
        lexemeFormData['Flag'] = 1

        # pprint(lexemeFormData)
        dbfilter = {'username' : current_user.username, 'projectname' : activeprojectname['projectname'], \
                                'headword' : lexemeFormData['headword']}
        lexeme = lexemes.find_one(dbfilter, {'_id' : 0, 'filesname' : 0})

        pprint(lexeme)

        lexemediff = eval(diff(lexeme, lexemeFormData, dump=True))
        if len(lexemediff) > 0:
            updatevalues = {}

            for keys, values in lexemediff.items():
                if (
                        keys == "Lexeme Form Script" or
                        keys == "Custom Fields"
                    ):
                    for key, value in values.items():
                        x = list(value.keys())
                        y = list(value.values())
                        updatevalues[keys+'.'+key+'.'+x[0]] = y[0]
                elif (
                        keys=="Sense" or
                        keys=="Variant" or
                        keys=="Allomorph"
                    ):
                    for key, value in values.items():
                        for k, v in value.items():
                            x = list(v.keys())
                            y = list(v.values())
                            if (x[0]=='Semantic Domain' or x[0]=='Lexical Relation'):
                                updatevalues[keys+'.'+key+'.'+k+'.'+x[0]] = lexemeFormData[keys][key][int(k)][x[0]]
                            else:        
                                updatevalues[keys+'.'+key+'.'+k+'.'+x[0]] = y[0]        
                else :
                    updatevalues[keys] = values
            setvalues = {'$set': updatevalues}
            # pprint(setvalues)
            # pprint(len(lexemediff))
            lexemes.find_one_and_update(dbfilter, setvalues)

    # get the list of lexeme entries for current project to show in dictionary view table
    lst = list()
    for lexeme in lexemes.find({ 'username' : current_user.username, 'projectname' : activeprojectname['projectname'] }, \
                            {'_id' : 0, 'headword' : 1, 'gloss' : 1, 'grammaticalcategory' : 1}):
        lst.append(lexeme)
         
    return render_template('dictionaryview.html', sdata=lst, count=len(lst), data=currentuserprojectsname)


# save active project name for active user
@app.route('/activeprojectname', methods=['GET', 'POST'])
def activeprojectname():
    userprojects = mongo.db.userprojects                # collection containing username and his/her last seen project name
    
    projectname = str(request.args.get('a'))            # data through ajax

    # if userprojects.find_one({'username' : current_user.username}) is None:
    #     activeprojectnames.insert({ 'username' : current_user.username, 'projectname' : projectname })
    # else:
    #     activeprojectnames.update_one({ 'username' : current_user.username }, {'$set' : { 'projectname' : projectname }})

    userprojects.update_one({ 'username' : current_user.username }, \
            { '$set' : { 'activeproject' :  projectname}})
    return 'OK'


# MongoDB Database
# user login form route
@app.route('/login', methods=['GET', 'POST'])
def login():
    # userlogin = mongo.db.userlogin                          # collection of users and their login details
    dummyUserandProject()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = UserLoginForm()
    if form.validate_on_submit():
        # username = userlogin.find_one({"username": form.username.data})
        user = UserLogin(username=form.username.data)
        # print(user)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
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
    dummyUserandProject()
    if current_user.is_authenticated:
        # print(current_user.get_id())
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # user = UserLogin(username=form.username.data)
        password = generate_password_hash(form.password.data)
        # print(user, password)

        userlogin.insert({"username": form.username.data, "password": password})

        userprojects = mongo.db.userprojects              # collection of users and their respective projectlist
        userprojects.insert({'username' : form.username.data, 'myproject': [], \
            'projectsharedwithme': [], 'activeproject' : ''})

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# # SQLite Database
# # user login form route
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     dummyUserandProject()
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     form = UserLoginForm()
#     if form.validate_on_submit():
#         user = UserLogin.query.filter_by(username=form.username.data).first()
#         print(user)
#         if user is None or not user.check_password(form.password.data):
#             flash('Invalid username or password')
#             return redirect(url_for('login'))
#         login_user(user)
#         next_page = request.args.get('next')
#         if not next_page or url_parse(next_page).netloc != '':
#             next_page = url_for('home')
#         return redirect(next_page)
#     return render_template('login.html', form=form)


# # SQLite Database
# # use logout
# @app.route('/logout')
# def logout():
#     try:
#         logout_user()
#         return redirect(url_for('home'))
#     except:
#         return redirect(url_for('home'))    


# # SQLite Database
# # new user registration
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     dummyUserandProject()
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = UserLogin(username=form.username.data)
#         user.set_password(form.password.data)
#         # print(user)
#         db.session.add(user)
#         db.session.commit()

#         userprojects = mongo.db.userprojects              # collection of users and their respective projectlist
#         userprojects.insert({'username' : form.username.data, 'myproject': [], \
#             'projectsharedwithme': [], 'activeproject' : ''})

#         flash('Congratulations, you are now a registered user!')
#         return redirect(url_for('login'))
#     return render_template('register.html', form=form)


# get all projects name created by the current active user
@app.route('/currentuserprojects')
def currentuserprojects():
    # getting the collections
    userprojects = mongo.db.userprojects              # collection of users and their respective projects

    # print(f'{"#"*80}\n{current_user.username}')
    userprojectsname = []
    try:
        userprojects  = userprojects.find_one({ 'username' : current_user.username })
        myproject = userprojects['myproject']
        projectsharedwithme = userprojects['projectsharedwithme']
        userprojectsname = set(myproject + projectsharedwithme)
    except:
        flash('Please create your first project.')

    # print(f'{"#"*80}\n{userprojectsname}')
    
    return userprojectsname

# contact us route
# create contact us form for the LiFE
@app.route('/contactus', methods=['GET', 'POST'])
# @login_required
def contactus():
    # if 'projectnames' not in mongo.db.list_collection_names():
    #     projectnames = mongo.db.projectnames                # collection containing projects name
    #     projectnames.insert({'_id':10, 'projectname':{}})
    # currentuserprojectsname =  currentuserprojects()
    return render_template('contactus.html')

# retrieve files from database
@app.route('/retrieve/<filename>')
def retrieve(filename):
    x = mongo.send_file(filename)
    return x


# change presentation of keys retrieved from database
@app.route('/change/<data>')
def change(data):

    # print(data)

    # if 'headword' in data:
    #     data['Head Word'] = data.pop('headword')
    # if 'pronunciation' in data:
    #     data['Pronunciation'] = data.pop('pronunciation')
    # if 'gloss' in data:
    #     data['Gloss'] = data.pop('gloss')
    # if 'grammaticalcategory' in data:
    #     data['Grammatical Category'] = data.pop('grammaticalcategory')
    # if 'additionalmetadatainformation' in data:
    #     data['Additional Metadata Information'] = data.pop('additionalmetadatainformation')
    #     # print(k)
    # if 'uploadsoundfile' in data:
    #     data['Upload Sound File'] = data.pop('uploadsoundfile')
    # if 'uploadmoviefile' in data:
    #     data['Upload Movie File'] = data.pop('uploadmoviefile')

    # num = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    # d = data
    lst = list()
    print()
    # print(d)
    for k, v in data.items():
        n = re.findall('[0-9]+', k)
        # print(n)
        # if k[-1] in num:
        if len(n) != 0:
            # print(k)
            # nk = k[0:len(k)-1] + ''
            index = k.index(n[0])
            # print(index)
            nk = k[:index] + ''
            # print(nk)
            lst.append({nk : v})
            # print(lst)
        else:    
            lst.append({k : v})
            # print(lst)
    print(lst)

    return lst


# test route for quick testing before adding any new feature
@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        projectFormData = dict(request.form.lists())

        # print(f'{"#"*80}\nprojectFormData\n{projectFormData}')

        dynamicFormField = []
        listOfCustomFields = []
        projectForm = {}
        projectForm['projectname'] = projectFormData['projectname'][0]
        
        # print(f'{"#"*80}\n{projectnames.find_one({"_id":10})["projectname"]}')

        # chech uniqueness of the project name and update projectname list
        # projectnamelist = projectnames.find_one({"_id":10})["projectname"]
        # if projectForm["projectname"] in projects.find_one({}).keys():
        #     flash(f'Project Name : {projectForm["projectname"]} already exist!')
        #     return redirect(url_for('newproject'))
        # # projectslist = list(projectsCollection["projectname"].keys())
        # #get _id in collection name projects
        # projects_id = projects.find_one({}, {"_id" : 1})["_id"]
        # print(f'{"#"*80}\n{projects_id}\n')
        # for proname in projectslist:
        #     # print(f'{"#"*80}\n{proname}\n')
        #     if proname == projectForm['projectname']:
        #         flash(f'Project Name : {projectForm["projectname"]} already exist!')
        #         return redirect(url_for('newproject'))

        projectForm['username'] = current_user.username

        # projects.update_one({ "_id" : projects_id }, \
        #     { '$set' : { projectForm['projectname'] : {"projectOwner" : current_user.username,"lexemeInserted" : 0, "lexemeDeleted" : 0, \
        #         'sharedwith': [projectForm['username']], 'projectdeleteFLAG' : 0} }})

        
        # print(usersprojects.find_one({ 'username' : current_user.username }))

        # print(f'{"#"*80}\n{usersprojects.find_one({"username" : current_user.username})["projectname"]}')

        # get curent user project list and update
        # userprojectnamelist = userprojects.find_one({'username' : current_user.username})["myproject"]
        # # print(f'{"#"*80}\n{userprojectnamelist}')
        # userprojectnamelist.append(projectForm['projectname'])
        # userprojects.update_one({ 'username' : current_user.username }, \
        #     { '$set' : { 'myproject' : userprojectnamelist, 'activeproject' :  projectForm['projectname']}})

        # dynamicFormField = []
        # listOfCustomFields = []

        for key, value in projectFormData.items():
            if re.search(r'[0-9]+', key):
                dynamicFormField.append(value[0])
            elif key == 'Lexeme Form Script':
                projectForm[key] = value
            elif key == 'Gloss Language':
                value.append('English')
                projectForm[key] = value
            elif len(value) == 1:
                projectForm[key] = value[0]
            else:
                projectForm[key] = value

        # print(f'{"#"*80}\ndynamicFormField\n{len(dynamicFormField)}')
        if len(dynamicFormField) > 1:
            for i in range(0,len(dynamicFormField),2):
                listOfCustomFields.append({dynamicFormField[i] : dynamicFormField[i+1]})

            projectForm['Custom Fields'] = listOfCustomFields

        print(f'{"="*80}\nProject Form :\n{projectForm}\n{"="*80}')
        # projectsform.insert(projectForm)
        # else:
        #     flash(f'Project Name : {projectForm["projectname"]} already created by {current_user.username}')
        #     return redirect(url_for('newproject'))

        # if activeprojectnames.find_one({'username' : current_user.username}) is None:
        #     activeprojectnames.insert({ 'username' : current_user.username, 'projectname' : projectForm['projectname'] })
        # else:
        # activeprojectnames.update_one({ 'username' : current_user.username }, \
        #                             {'$set' : { 'projectname' : projectForm['projectname'] }})

        # currentuserprojectsname =  currentuserprojects()
        # activeprojectname = userprojects.find_one({ 'username' : current_user.username })['activeproject']

        # x = projectsform.find_one_or_404({'projectname' : activeprojectname,\
        #                                 'username' : current_user.username}, { "_id" : 0 })
        
        # x = change(x)

        # print(f'{"#"*80}\nx:\n{x}')
        # if x is not None:
        #     return render_template('enternewlexeme.html', newData=x, data=currentuserprojectsname)
        # return render_template('enternewlexeme.html')

    # return render_template('test.html', filen=url_for('retrieve', filename='20200622-030356011433mail.jpeg')) 
    return render_template('test.html')

def dummyUserandProject():
    """ Creates dummy user and project if the database has no collection """
    print("Creates dummy user and project if the database has no collection")
    userprojects = mongo.db.userprojects                # collection of users and their projectlist and active project
    projects = mongo.db.projects                        # collection containing projects name
    if len(mongo.db.list_collection_names()) == 0:
        userprojects.insert({'username' : "dummyUser", 'myproject': ["dummyProject1"], \
            'projectsharedwithme': [], 'activeproject' : "dummyActiveProject"})
        projects.insert({"dummyProject1" : {"projectOwner" : "dummyUser", "lexemeInserted" : 0, "lexemeDeleted" : 0,\
            'sharedwith': ['dummyUser'], 'projectdeleteFLAG' : 0}})



# @app.errorhandler(InternalServerError)
# def handle_500(e):
#     original = getattr(e, "original_exception", None)

#     if original is None:
#         # direct 500 error, such as abort(500)
#         return render_template("500.html"), 500

#     # wrapped unhandled error
#     return render_template("500_unhandled.html", e=original), 500



# for instant testing in terminal
# with app.test_request_context():

    # activeprojectnames = mongo.db.activeprojectnames  
# #     # projectsForm = mongo.db.projectsForm
#     lexemes = mongo.db.lexemes
    # fs =  gridfs.GridFS(mongo.db)
    # fs = mongo.db.fs.files
#     lst = list()
#     for lexeme in lexemes.find({ 'username' : 'alice', 'projectname' : 'Project_1' }, \
#                             {'_id' : 0, 'headword' : 1, 'gloss' : 1, 'grammaticalcategory' : 1}):
#         lst.append(lexeme)    
#     pprint.pprint(lst)
#     for i in lst:
#         print(i['gloss'])
#     # for projectForm in projectsForm.find({}):
#     #     print('###################################################################################################')
#     #     pprint.pprint(projectForm['NewProject'])
#     #     print('###################################################################################################')
    
#     for lexeme in lexemes.find({'Tisra.projectName' : 'Third'}):
#         print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n')
#         pprint.pprint(lexeme['Tisra']['filesName'])
#         print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n')
    # data = lexemes.find_one({})
    # pprint.pprint(data['bobTesting'])

    # for f in fs.find({'projectName' : 'Third'}):
    #     print('######################################################################\n')
    #     pprint.pprint(f['filename'])
    #     print('######################################################################\n')    
        

    # if fs.exists({"filename" : "20200622-030356011362patr.jpeg"}):
    #     print('H!')
    # file = fs.find({})
    # for f in file:
    #     name = f.filename
    #     open(basedir + name, 'wb').write(f.read())
    # print('Done')
    # filen = fs.find_one({"filename" : "20200622-030356011362patr.jpeg"})
    # print(filen)
    # print(fs.list())
    # x = fs.get({"filename" : "20200622-030356011362patr.jpeg"})
    # print(x.upload_date)
    # for f in forms.find({}):
    #     pprint.pprint(f['First'])
    # form = forms.find_one_or_404({'pronunciation' : 'text'})
    # filename = user['filename']
    # print(form)

    # activeprojectname = activeprojectnames.find_one({ 'username' : 'alice' },{'_id' : 0})
    # print(activeprojectname)