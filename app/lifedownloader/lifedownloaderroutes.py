"""Module containing the routes for the downloader part of the LiFe."""

from flask import flash, redirect, render_template, url_for, request, json, jsonify, send_file
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash
from app import app, mongo

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
    updateuserprojects,
    userdetails,
    speakerdetails
)


from flask import Blueprint, render_template

ld = Blueprint('lifedownloader', __name__, template_folder='templates', static_folder='static')


@ld.route('/downloadtranscriptions', methods=['GET', 'POST'])
def downloadtranscriptions():
    userprojects, userlogin = getdbcollections.getdbcollections(
        mongo, 'userprojects', 'userlogin')
    current_username = getcurrentusername.getcurrentusername()
    print('USERNAME: ', current_username)
    usertype = userdetails.get_user_type(
        userlogin, current_username)
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(
        current_username, userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(
        current_username, userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(
        userprojects, current_username, activeprojectname)

        
    projects = mongo.db.projects
    # collection of users and their respective projects
    userprojects = mongo.db.userprojects
    # collection containing entry of each lexeme and its details
    lexemes = mongo.db.lexemes
    # sentences = mongo.db.sentences                          # collection containing entry of each sentence and its details
    # creating GridFS instance to get required files
    fs = gridfs.GridFS(mongo.db)
    
    lst = []
    headwords = request.args.get('data')                   # data through ajax

    if headwords != None:
        headwords = eval(headwords)
    # print(f'{"="*80}\nheadwords from downloadselectedlexeme route:\n {headwords}\n{"="*80}')

    download_format = headwords['downloadFormat']
    # print(download_format)

    del headwords['downloadFormat']

    # print(f'{"="*80}\ndelete download format:\n {headwords}\n{"="*80}')

    activeprojectname = userprojects.find_one({'username': current_user.username})[
        'activeprojectname']
    lst.append({'projectname': activeprojectname})
    projectname = activeprojectname

    # for headword in headwords:
    #     lexeme = lexemes.find_one({'username' : current_user.username, 'projectname' : projectname, 'headword' : headword},\
    #                         {'_id' : 0, 'username' : 0, 'projectname' : 0})
    #     lst.append(lexeme)
    # for lexemeId in headwords.keys():
    #     lexeme = lexemes.find_one({'projectname' : projectname, 'lexemeId' : lexemeId},\
    #                         {'_id' : 0})
    #     lst.append(lexeme)

    for lexemeId in headwords.keys():
        lexeme = lexemes.find_one({'projectname': projectname, 'lexemeId': lexemeId},
                                  {'_id': 0})
        lst.append(lexeme)
        # save current user mutimedia files of each lexeme to local storage
        files = fs.find({'projectname': projectname, 'lexemeId': lexemeId})
        for file in files:
            name = file.filename
            # open(basedir+'/app/download/'+name, 'wb').write(file.read())
            open(os.path.join(basedir, 'download', name), 'wb').write(file.read())

    return send_file('../download.zip', as_attachment=True)
