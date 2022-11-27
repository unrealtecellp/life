import re
from ast import Break
from curses import meta
from inspect import getmembers
from lib2to3.pytree import convert
from operator import ne
from types import MemberDescriptorType   #, NoneType
from xml.etree.ElementTree import register_namespace

from xml.sax.handler import feature_namespace_prefixes
from xmlrpc.client import gzip_decode
from xxlimited import new
from zipfile import ZipFile
from flask import Blueprint, flash, redirect, render_template, url_for, request, json, jsonify, send_file
from pymongo import database
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash
# from karya_plugin import karya_plugin, mongo
# from karya_plugin.forms import UserLoginForm, RegistrationForm
# from karya_plugin.models import UserLogin

from app import app, mongo
from app.controller import getdbcollections, getactiveprojectname, getcurrentuserprojects
from app.controller import getprojectowner, getcurrentusername, readJSONFile, audiodetails
from app.controller import questionnairedetails, getuserprojectinfo
from app.controller import getprojecttype

from app.karya_ext import quesaudiodetails

# from app.forms import UserLoginForm, RegistrationForm
# from app.models import UserLogin
import pandas as pd
from flask_login import current_user, login_user, logout_user, login_required
import re
from flask import Flask, render_template, request
from werkzeug.datastructures import FileStorage
from app.lifeques.lifeques import questionnaire

from app.lifeques.controller import savequesaudiofiles, getquesfromprompttext, savequespromptfile
from app.lifeques.controller import getquesidlistofsavedaudios

from zipfile import ZipFile

from tqdm import tqdm

#############################################################################
#############################################################################
#############################################################################
#############################################################################
# neerav is adding after this
#############################################################################
#############################################################################
#############################################################################
#############################################################################

karya_bp = Blueprint('karya_bp', __name__, template_folder='templates', static_folder='static')



@karya_bp.route('/home_insert')
def home_insert():
    userprojects, accesscodedetails = getdbcollections.getdbcollections(mongo,
                                                                        'userprojects',
                                                                        'accesscodedetails')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                        current_username,
                                                        activeprojectname)

    fetch_access_codes = accesscodedetails.find({'projectname': activeprojectname,
                                                'fetchData': 1
                                                },
                                                {
                                                    '_id': 0,
                                                    'karyaaccesscode': 1,
                                                    'assignedBy': 1,
                                                    'uploadedBy': 1
                                                })


    fetch_access_code_list = []

    for fetch_access_code in fetch_access_codes:
        if (fetch_access_code['assignedBy'] != ''):
            if (fetch_access_code['assignedBy'] == current_username):
                fetch_access_code_list.append(fetch_access_code['karyaaccesscode'])
            else:
                if (current_username == fetch_access_code['uploadedBy']):
                    fetch_access_code_list.append(fetch_access_code['karyaaccesscode'])

    return render_template("home_insert.html",
                            projectName=activeprojectname,
                            shareinfo=shareinfo,
                            fetchaccesscodelist=fetch_access_code_list
                        )
    # return redirect(url_for('karya_bp.home_insert'))
    # return render_template("uploadfile.html")

##################################################################################
#########################################################################################################
##################################################################################
import requests
import gzip
import tarfile
from io import BytesIO
import requests
import gzip
import tarfile
from io import BytesIO
import io
import numpy as np
import scipy.io.wavfile
import soundfile as sf
from pymongo import MongoClient
import requests
from io import BytesIO
import json
import os




#############################################################################################################
##############################################################################################################
######################################   Upload Access-Code       ############################################
##############################################################################################################
##############################################################################################################

import codecs
import os
from datetime import datetime
@karya_bp.route('/uploadfile' , methods=['GET', 'POST'])
def uploadfile():
    karyaaccesscodedetails, userprojects, projectsform = getdbcollections.getdbcollections(mongo,
                                                                                            'accesscodedetails',
                                                                                            'userprojects',
                                                                                            'projectsform')
    current_username = getcurrentusername.getcurrentusername()
    print('curent user : ', current_username)
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
    # projectowner = getprojectowner.getprojectowner(projects, activeprojectname)

    langscript = []
    projectform = projectsform.find_one({"projectname" : activeprojectname})  #domain, elictationmethod ,langscript-[1]
    langscripts = projectform["Prompt Type"][1]
    for lang_script, lang_info in langscripts.items():
        if ('Audio' in lang_info):
            langscript.append(lang_script)
    domain = projectform["Domain"][1]
    elicitation = projectform["Elicitation Method"][1]
    print(langscript, domain, elicitation)
    uploadacesscodemetadata = {
                                "langscript": langscript,
                                "domain": domain,
                                "elicitation": elicitation
                                }
    
    # mongodb_info = mongo.db.accesscodedetails

    if request.method == "POST":
    
        file = request.files['accesscodefile']
        data = pd.read_csv(file)
        df = pd.DataFrame(data)

        df["id"] = df["id"].str[1:]
        df["access_code"] = df["access_code"].str[1:]
        df["phone_number"] = df["phone_number"].str[1:]
        # print(data["id"],df["access_code"],df["phone_number"])
        # print(df["id"])
        # print(df)
  
        for index,item in df.iterrows(): 

            current_dt = str(datetime.now()).replace('.', ':')

            checkaccesscode = item["access_code"]
            accesscode_exist = karyaaccesscodedetails.find_one({"karyaaccesscode": checkaccesscode})
            if  accesscode_exist is not None: continue
            task = request.form.get('task')
            language = request.form.get('langscript') 
            domain = request.form.getlist('domain')
            phase =  request.form.get('phase') #=>numbers - 0,1,2,3, etc
            elicitationmethod = request.form.getlist("elicitation")
            fetch_data = request.form.get('fetchdata')

            if fetch_data == 'on':
                fetch_data = 1
            else:
                fetch_data = 0

            print (fetch_data)
            print(language, domain, elicitationmethod)

            insert_dict = {
                        "karyaspeakerid": item["id"], "karyaaccesscode": item["access_code"], "lifespeakerid": "", 
                        "task":task,"language": language, "domain": domain, 
                        "phase":phase, "elicitationmethod":elicitationmethod, "projectname": activeprojectname,
                        "uploadedBy":current_username,
                        "assignedBy":"",
                        "current": {"workerMetadata": {"name": "", "agegroup": "", "gender": "", 
                                                "educationlevel": "", "educationmediumupto12": "", 
                                                "educationmediumafter12": "", "speakerspeaklanguage" :"", 
                                                "recordingplace": "", "typeofrecordingplace" : "", 
                                                "activeAccessCode": ""}, "updatedBy":"","current_date":current_dt},
                        "previous": {},
                        "fetchData": fetch_data,
                        "karyafetchedaudios":[],                        
                        "isActive": 0}
                        

            # print ('Data to be inserted', insert_dict)
            return_obj = karyaaccesscodedetails.insert(insert_dict)
            # print ('Return object', return_obj)
            # print (return_obj.inserted_id)


            datafromdb = karyaaccesscodedetails.find({},{"_id" :0})
            # print(list(datafromdb))
        
        # flash('Successfully added new lexeme')
        return redirect(url_for('karya_bp.home_insert'))

    return render_template("uploadfile.html",
                            data=currentuserprojectsname,
                            projectName=activeprojectname,
                            uploadacesscodemetadata=uploadacesscodemetadata)




##############################################################################################################
##############################################################################################################
######################################       Add User         ###############################################
##############################################################################################################
##############################################################################################################

@karya_bp.route('/add', methods=['GET', 'POST'])
def add():
    print ('Adding speaker info into server')
    mongodb_info = mongo.db.accesscodedetails
    
    accesscodedetails, = getdbcollections.getdbcollections(mongo, "accesscodedetails")
    remaingkaryaaccesscode = mongodb_info.find({"isActive":0},{"karyaspeakerid":1, "_id" :0})
##########################
##########################
    # recordingremaingkaryaaccesscode = mongodb_info.find({"isActive":0, "taskname": "Recording"},{"karyaspeakerid":1, "_id" :0})
    # verificationremaingkaryaaccesscode = mongodb_info.find({"isActive":0, "taskname": "Verification"},{"karyaspeakerid":1, "_id" :0})
    # if task == "Recoding":
    #     do someting
    # else:
    #     do this
###############################
###############################
    # jp = karyaaccesscode["lifespeakerid"]
    print ('Request method', request.method)

    speaker_data_accesscode = []
    speaker_data_name = []
    speaker_data_age = []
    speaker_data_gender = []
    mongodb_info = mongo.db.accesscodedetails

    #access-code
    # accode = mongodb_info.find({"isActive":1},{"current.workerMetadata.lifespeakerid":1,"_id" :0})
    # for data in accode:   
    #     speaker_accode = data["current"]["workerMetadata"]["lifespeakerid"]                                    
    #     speaker_data_accesscode.append(speaker_accode)
    # print(speaker_data_accesscode)   

    #speaker_name
    name = mongodb_info.find({"isActive":1},{"current.workerMetadata.name" :1,"_id" :0})
    for data in name:
        speaker_name = data["current"]["workerMetadata"]["name"]                                     
        speaker_data_name.append(speaker_name)
    print(speaker_data_name)

    #age
    age = mongodb_info.find({"isActive":1},{"current.workerMetadata.agegroup":1,"_id" :0})
    for data in age:   
        speaker_age = data["current"]["workerMetadata"]["agegroup"]                                    
        speaker_data_age.append(speaker_age)
    print(speaker_data_age)    

    #gender
    gender = mongodb_info.find({"isActive":1},{"current.workerMetadata.gender":1,"_id" :0})
    for data in gender:
        speaker_gender = data["current"]["workerMetadata"]["gender"]                                     
        speaker_data_gender.append(speaker_gender)
    print(speaker_data_gender)                                  
    print(speaker_data_accesscode)
    
    ##################################
    #######################
    karyaaccesscodedetails, userprojects, projectsform = getdbcollections.getdbcollections(mongo,
                                                                                            'accesscodedetails',
                                                                                            'userprojects',
                                                                                            'projectsform')
    current_username = getcurrentusername.getcurrentusername()          
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
    
    

    karyaaccesscodedetails, userprojects, projectsform = getdbcollections.getdbcollections(mongo,
                                                                                            'accesscodedetails',
                                                                                            'userprojects',
                                                                                            'projectsform')
    current_username = getcurrentusername.getcurrentusername()          
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)

    if request.method =='POST':
        # accesscode = request.form.get('accesscode')
        #remaingkaryaaccesscode = request.form.get('remaingkaryaaccesscode')
        print("####################################################### \n", "\n##########################################")
        accesscode = request.form.get('accode')
        print("this acc code at line 428", accesscode)
        fname = request.form.get('sname') 
        print(fname)
        fage = request.form.get('sagegroup')
        fgender = request.form.get('sgender')
        educlvl = request.form.get('educationalevel')

        moe12 = request.form.getlist('moe12')
        moea12 = request.form.getlist('moea12')
        # moe12 = request.form.get('moe12')
        # moea12 = request.form.get('moea12')
        
        sols = request.form.getlist('sols')
        por = request.form.get('por')
        toc = request.form.get('toc')
        if accesscode  == '':
            accesscodefor = int(request.form.get('accesscodefor'))
            task = request.form.get('task')
            language = request.form.get('langscript') 
            domain = request.form.getlist('domain')
            elicitationmethod = request.form.getlist("elicitation")
            #############################################################################################
            # namekaryaID = mongodb_info.find_one({"karyaaccesscode":accesscode},{"karyaspeakerid":1, "_id" :0})
            # namekaryaID = mongodb_info.find_one({"isActive":0},{"karyaspeakerid":1, "_id" :0})
            namekaryaID = mongodb_info.find_one({"isActive":0, "projectname":activeprojectname, 
                                "fetchData":accesscodefor, "task":task, 
                                "domain":domain, "elicitationmethod":elicitationmethod, 
                                "language":language},{"karyaspeakerid":1,"karyaaccesscode":1 , "_id" :0})
            
            # lifeID = mongodb_info.find_one({"karyaaccesscode":accesscode},{"lifespeakerid":1, "_id" :0})
            # lIfeid = lifeID["lifespeakerid"]
            # namekaryaIDDOB = mongodb_info.find_one({"isActive":0},{"current.workerMetadata.agegroup":1 , "_id" :0})
            # rDOB = namekaryaIDDOB["current"]["workerMetadata"]["agegroup"]
            # renameInFormDOB = rDOB.replace("-","")
            test = {"isActive":0, "projectname":activeprojectname, 
                                "fetchData":accesscodefor, "task":task, 
                                "domain":domain, "elicitationmethod":elicitationmethod, 
                                "language":language}
            print(test)                   
            print(namekaryaID)
            # for lidata in namekaryaID:
            #     print("574 ", lidata)
            if namekaryaID is None: 
                flash("Please Upload New Access Code")
                return redirect(url_for('karya_bp.home_insert'))

            namekaryaIDDOB = fage
            nameInForm = fname 
            if namekaryaIDDOB and nameInForm is not None:  
                
                print("230 ========================== >>>>>>>>>>>>>>>>>>>>     ",nameInForm , type(nameInForm))

                print("231 =========================  >>>>>>>>>>>>>>>>>>>>      ", namekaryaIDDOB, type(namekaryaIDDOB))
                # if namekaryaID is not None:
                #     try :
                renameInFormDOB = namekaryaIDDOB.replace("-","")
                print("227  ==========================================>>>>>>>>>>   ", renameInFormDOB)
                codes = namekaryaID["karyaspeakerid"]
                print(codes)
                
                renameInForm = nameInForm.replace(" ","")
                lowerRenameInForm = renameInForm.lower()
                renameDOB =  "".join([lowerRenameInForm,renameInFormDOB])
                print("232 =========================>>>>>>>>>>>>    " , renameDOB)
                renameCode ="_".join([renameDOB,codes])
                print("line 583", renameCode)  
                # namekaryaAddID.append(renameCode)
                update_data = {"lifespeakerid": renameCode,
                                        "assignedBy" :  current_username, 
                                        "current.updatedBy" :  current_username,
                                        "current.workerMetadata.name": fname, 
                                        "current.workerMetadata.agegroup": fage, 
                                        "current.workerMetadata.gender": fgender,
                                        "current.workerMetadata.educationlevel": educlvl,
                                        "current.workerMetadata.educationmediumupto12": moe12,
                                        "current.workerMetadata.educationmediumafter12": moea12,
                                        "current.workerMetadata.speakerspeaklanguage": sols,
                                        "current.workerMetadata.recordingplace": por,
                                        "current.workerMetadata.typeofrecordingplace": toc,
                                        "isActive": 1}
                         
                    # speaker_data_accesscode.append(data["lifespeakerid"])
            # print("587 ",namekaryaAddID)


            # update_data = {"lifespeakerid": renameCode,
            #                             "current.workerMetadata.name": fname, 
            #                             "current.workerMetadata.agegroup": fage, 
            #                             "current.workerMetadata.gender": fgender,
            #                             "current.workerMetadata.educationlevel": educlvl,
            #                             "current.workerMetadata.educationmediumupto12": moe12,
            #                             "current.workerMetadata.educationmediumafter12": moea12,
            #                             "current.workerMetadata.speakerspeaklanguage": sols,
            #                             "current.workerMetadata.recordingplace": por,
            #                             "current.workerMetadata.typeofrecordingplace": toc,
            #                             "isActive": 1}
            
            # update_data = {"current.workerMetadata.name": fname, 
            #                              "current.workerMetadata.agegroup": fage, 
            #                              "current.workerMetadata.gender": fgender,
            #                              "current.workerMetadata.educationlevel": educlvl,
            #                              "current.workerMetadata.educationmediumupto12": moe12,
            #                              "current.workerMetadata.educationmediumafter12": moea12,
            #                              "current.workerMetadata.speakerspeaklanguage": sols,
            #                              "current.workerMetadata.recordingplace": por,
            #                              "current.workerMetadata.typeofrecordingplace": toc,
            #                              "isActive": 1}
            # accesscode = request.form.get('accode')
    #########################################################################################################################
    #########################################################################################################################
            accesscode = request.form.get('accode')
            print("=======================> ",accesscode )
    #########################################################################################################################
    ##########################################################################################################################
            print("this acc code at line 460", accesscode)
            # if accesscode == '':
                # karyaaccesscode = mongodb_info.find_one({"isActive":0},{"karyaaccesscode":1, "_id" :0})
                
            karyaaccesscode = {"karyaaccesscode":namekaryaID["karyaaccesscode"]}
            if karyaaccesscode != None:
                accesscode = karyaaccesscode['karyaaccesscode']
            else:
                accesscode = ''
                print ('Karya access code', accesscode)
                print ('445 Update Data', update_data)
                # "lifespeakerid": renameCode
            mongodb_info.update_one({"karyaaccesscode": accesscode}, {"$set": update_data})
            
            # mongodb_info.insert_one({"karyaaccesscode": accesscode}, {"$set": update_data})
            # mongodb_info.update_one({"karyaaccesscode": accesscode},{"lifespeakerid": {"$exists": False}}, {"$set": {"lifespeakerid": renameCode}})
            # mongodb_info.update_one(filter={"karyaaccesscode": accesscode}, update={"$setOnInsert":{"lifespeakerid": ""},"$set":{"lifespeakerid": renameCode},})
            

        else:
            update_data = {"current.updatedBy" :  current_username,
                                "current.workerMetadata.gender": fgender,
                                    "current.workerMetadata.educationlevel": educlvl,
                                    "current.workerMetadata.educationmediumupto12": moe12,
                                    "current.workerMetadata.educationmediumafter12": moea12,
                                    "current.workerMetadata.speakerspeaklanguage": sols,
                                    "current.workerMetadata.recordingplace": por,
                                    "current.workerMetadata.typeofrecordingplace": toc,
                                    "isActive": 1}   
            previous_speakerdetails = mongodb_info.find_one({"karyaaccesscode": accesscode},
                                                {"current.workerMetadata": 1, "current.updatedBy":1, "_id": 0,})

            ###########################################
            ## TOdo: Add date to the previous metadata
            ###########################################


            # the document's content will change to this:
            # new_val = {"some text": "ObjectRocket: Database Management and Hosting"}

            # pass the 'new_val' obj to the method call
            
            date_of_modified = str(datetime.now()).replace(".", ":" )


            # update_old_data = {"previous."+date_of_modified+".workerMetadata.name": previous_speakerdetails["current"]["workerMetadata"]["name"], 
            #                                         "previous."+date_of_modified+".workerMetadata.agegroup": previous_speakerdetails["current"]["workerMetadata"]["agegroup"], 
            #                                         "previous."+date_of_modified+".workerMetadata.gender": previous_speakerdetails["current"]["workerMetadata"]["gender"],
            #                                         "previous."+date_of_modified+".workerMetadata.educationlevel": previous_speakerdetails["current"]["workerMetadata"]["educationlevel"],
            #                                         "previous."+date_of_modified+".workerMetadata.educationmediumupto12": previous_speakerdetails["current"]["workerMetadata"]["educationmediumupto12"],
            #                                         "previous."+date_of_modified+".workerMetadata.educationmediumafter12": previous_speakerdetails["current"]["workerMetadata"]["educationmediumafter12"],
            #                                         "previous."+date_of_modified+".workerMetadata.speakerspeaklanguage": previous_speakerdetails["current"]["workerMetadata"]["speakerspeaklanguage"],
            #                                         "previous."+date_of_modified+".workerMetadata.recordingplace": previous_speakerdetails["current"]["workerMetadata"]["recordingplace"]
            #                                         }
            update_old_data = {"previous."+date_of_modified+".workerMetadata.gender": previous_speakerdetails["current"]["workerMetadata"]["gender"],
                                                    "previous."+date_of_modified+".workerMetadata.educationlevel": previous_speakerdetails["current"]["workerMetadata"]["educationlevel"],
                                                    "previous."+date_of_modified+".workerMetadata.educationmediumupto12": previous_speakerdetails["current"]["workerMetadata"]["educationmediumupto12"],
                                                    "previous."+date_of_modified+".workerMetadata.educationmediumafter12": previous_speakerdetails["current"]["workerMetadata"]["educationmediumafter12"],
                                                    "previous."+date_of_modified+".workerMetadata.speakerspeaklanguage": previous_speakerdetails["current"]["workerMetadata"]["speakerspeaklanguage"],
                                                    "previous."+date_of_modified+".workerMetadata.recordingplace": previous_speakerdetails["current"]["workerMetadata"]["recordingplace"],
                                                    "previous."+date_of_modified+".updatedBy" : previous_speakerdetails["current"]["updatedBy"]
                                                    }

            mongodb_info.update_one({"karyaaccesscode": accesscode}, {"$set": update_old_data}) # Edit_old_user_info
            mongodb_info.update_one({"karyaaccesscode": accesscode}, {"$set": update_data}) #new_user_info

    return redirect(url_for('karya_bp.homespeaker'))
    # return render_template("homespeaker.html",
                            # projectName=activeprojectname,
                            # uploadacesscodemetadata=uploadacesscodemetadata)

   
##############################################################################################################
##############################################################################################################
######################################      View Table HomeSpeaker         ###################################
##############################################################################################################
##############################################################################################################



@karya_bp.route('/homespeaker')
def homespeaker():

    userprojects, projectsform = getdbcollections.getdbcollections(mongo,'userprojects', 'projectsform')

    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                            userprojects)
    
    print('curent user : ', current_username)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)
   
    projectform = projectsform.find_one({"projectname" : activeprojectname})  #domain, elictationmethod ,langscript-[1]
    langscript = []
    langscripts = projectform["Prompt Type"][1]
    for lang_script, lang_info in langscripts.items():
        if ('Audio' in lang_info):
            langscript.append(lang_script)
    domain = projectform["Domain"][1]
    elicitation = projectform["Elicitation Method"][1]
    print(langscript, domain, elicitation)
    uploadacesscodemetadata = {
                                "langscript": langscript,
                                "domain": domain,
                                "elicitation": elicitation
                                }
    
    # formremaingkaryaaccesscode = ', '.join([data['lifespeakerid'] for data in remaingkaryaaccesscode])
    # faccsess = formremaingkaryaaccesscode.count() 
    # acc = request.form.get('accessid') 
    # print("fname", acc)
    # namekaryaAddID = []
    # namekaryaAddIDtuple = tuple(namekaryaAddID)
    # speaker_data_accesscode = []
    karya_accesscode = []
    lifeId = []
    speaker_data_name = []
    speaker_data_age = []
    speaker_data_gender = []
    mongodb_info = mongo.db.accesscodedetails
    # print(mongodb_info)
    

################################## karya accesscode  #########################################################################
    karyaaccesscode = mongodb_info.find({"isActive":1},{"karyaaccesscode":1, "_id" :0})
    for data in karyaaccesscode:   
        codes = data["karyaaccesscode"]
        karya_accesscode.append(data)
        # speaker_data_accesscode.append(data["lifespeakerid"])
    print('596    ####################################### ',karya_accesscode)

##################################3 LifeID + Accesscode #####################################################################
    namekaryaID = mongodb_info.find({"isActive":1},{"lifespeakerid":1, "_id" :0})
    for lidata in namekaryaID:
        lifeId.append(lidata)
        # speaker_data_accesscode.append(data["lifespeakerid"])
    print("587 ===================================== >>>>>>>>>>>>>> ",lifeId)

############################################  Name #######################################################################
    name = mongodb_info.find({"isActive":1},{"current.workerMetadata.name" :1,"_id" :0})
    print(name)
    for data in name:
        # speaker_name = data["assignedBy"]["current"]["speaker_info"]["workerMetadata"]["name"]  
        # speaker_name = data["current"]["workerMetadata"]["name"]  
        speaker_name = data["current"]["workerMetadata"]                                
        speaker_data_name.append(speaker_name)
    print(speaker_data_name)

    ######################################  Age  ############################################################################
    age = mongodb_info.find({"isActive":1},{"current.workerMetadata.agegroup":1,"_id" :0})
    for data in age:   
        # speaker_age = data["assignedBy"]["current"]["speaker_info"]["workerMetadata"]["agegroup"]
        # speaker_age = data["current"]["workerMetadata"]["agegroup"]  
        speaker_age = data["current"]["workerMetadata"]                                
        speaker_data_age.append(speaker_age)
    print(speaker_data_age)    

    #################################   Gender   ###############################################################
    gender = mongodb_info.find({"isActive":1},{"current.workerMetadata.gender":1,"_id" :0})
    for data in gender:
        # speaker_gender = data["assignedBy"]["current"]["speaker_info"]["workerMetadata"]["gender"] 
        # speaker_gender = data["current"]["workerMetadata"]["gender"] 
        speaker_gender = data["current"]["workerMetadata"]                                 
        speaker_data_gender.append(speaker_gender)
    print(speaker_data_gender)                                  
  
    # speaker_data = [speaker_data_accesscode, speaker_data_name, speaker_data_age, speaker_data_gender]
    data_table = [[ karya_accesscode[i], lifeId[i], speaker_data_name[i], speaker_data_age[i], speaker_data_gender[i]] for i in range(0, len(karya_accesscode))]
    
    print(data_table)
    return render_template('homespeaker.html',
                            data=currentuserprojectsname,
                            projectName=activeprojectname,
                            uploadacesscodemetadata = uploadacesscodemetadata,
                            data_table=data_table)


##############################################################################################################
##############################################################################################################
######################################     Get Speaker Details        ########################################
##############################################################################################################
##############################################################################################################

@karya_bp.route('/getonespeakerdetails', methods=['GET', 'POST'])
def getonespeakerdetails():
    accesscodedetails, = getdbcollections.getdbcollections(mongo, "accesscodedetails")
    
    # data through ajax
    asycaccesscode = request.args.get('asycaccesscode')
    print(f"{'='*80}\nasycaccesscode: {asycaccesscode}\n{'='*80}")
    speakerdetails = accesscodedetails.find_one({"karyaaccesscode": asycaccesscode},
                                                {"_id": 0,
                                                "current.workerMetadata": 1})
    # mongodb_info = mongo.db.accesscodedetails

    # speakerdetails = mongodb_info.find_one({"lifespeakerid": asycaccesscode}, {"speaker_info.workerMetadata.name": 1, 
    #                                                 "assignedBy.current.speaker_info.workerMetadata.agegroup": 1, 
    #                                                 "assignedBy.current.speaker_info.workerMetadata.gender": 1,
    #                                                 "assignedBy.current.speaker_info.workerMetadata.educationlevel": 1,
    #                                                 "assignedBy.current.speaker_info.workerMetadata.medium-of-education-upto-12th": 1,
    #                                                 "assignedBy.current.speaker_info.workerMetadata.medium-of-education-after-12th": 1,
    #                                                 "assignedBy.current.speaker_info.workerMetadata.other-languages-speaker-could-speak": 1,
    #                                                 "assignedBy.current.speaker_info.workerMetadata.place-of-recording": 1,
    #                                                 "assignedBy.current.speaker_info.workerMetadata.type-of-place": 1,"_id": 0})

    # speakerdetails = speakerdetails["assignedBy"]["current"]["speaker_info"]["workerMetadata"]
    print(f"SPEAKER DETAILS: {speakerdetails}")                                                

    # speakerdetails['accesscode'] = asycaccesscode
    return jsonify(speakerdetails=speakerdetails)


##############################################################################################################
##############################################################################################################
######################################   Fetch Audio        ###############################################
##############################################################################################################
##############################################################################################################

@karya_bp.route('/fetch_karya_otp', methods=['GET', 'POST'])
def fetch_karya_otp():
    # accesscodedetails, = getdbcollections.getdbcollections(mongo, "accesscodedetails")
    mongodb_info = mongo.db.accesscodedetails  
    accesscodedocs = mongodb_info.find({"isActive":1},{"karyaaccesscode":1, "_id" :0}) 

    ##Registration
    registeruser_urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/worker/otp/generate'
    access_code = request.args.get("acode")
    phone_number = request.args.get("mob")
    
    for current_acodedoc in accesscodedocs:
        if access_code == current_acodedoc['karyaaccesscode']:
            registeruser_hederr= {'access-code':access_code, 'phone-number':phone_number}
            register_request = requests.put(url = registeruser_urll, headers = registeruser_hederr)

    return jsonify(result="False")


def get_fetched_audio_list(accesscode):
    mongodb_info = mongo.db.accesscodedetails  
    fetchedaudiodict = mongodb_info.find_one({"karyaaccesscode": accesscode},{"karyafetchedaudios":1, "_id" :0})   
    fetched_audio_list = fetchedaudiodict['karyafetchedaudios']
    print("3 : ", fetched_audio_list)
    return fetched_audio_list



@karya_bp.route('/fetch_karya_audio', methods=['GET', 'POST'])
def fetch_karya_audio():
    # karyaaudiodetails, = getdbcollections.getdbcollections(mongo, 'fetchkaryaaudio')
    # questionnaire, = getdbcollections.getdbcollections(mongo, 'questionnaire')

    projects, userprojects, projectsform, transcriptions, questionnaires, accesscodedetails = getdbcollections.getdbcollections(mongo,
                                                                                                            'projects',
                                                                                                            'userprojects',
                                                                                                            'projectsform',
                                                                                                            'transcriptions',
                                                                                                            'questionnaires',
                                                                                                            'accesscodedetails')
    current_username = getcurrentusername.getcurrentusername()
    # print('curent user : ', current_username)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)


    if request.method == 'POST':
        ###############################   verify OTP    ##########################################
        access_code = request.form.get("access_code")

         ###### Get already fetched audio list
        fetched_audio_list = get_fetched_audio_list (access_code)

        phone_number = request.form.get("mobile_number")
        otp = request.form.get("karya_otp")

        # print ("OTP", otp)
        print ("access_code", access_code)
        # print ("Mobile", phone_number)

        verifyotp_urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/worker/otp/verify'
        verifyotp_hederr= {'access-code':access_code, 'phone-number':phone_number, 'otp':otp}
        verifyPh_request = requests.put(url = verifyotp_urll, headers = verifyotp_hederr) 
        # print (verifyPh_request.json())

        ##TODO: Put check for verifying if the OTP was correct or not. If correct then proceed otherwise send error
        getTokenid_assignment_hedder = verifyPh_request.json()['id_token']
        # print ("ID token : ", getTokenid_assignment_hedder)
        
        ###############################   Get Assignments    ##########################################
        hederr= {'karya-id-token':getTokenid_assignment_hedder}
        assignment_urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=new&from=2021-05-11T07:23:40.654Z'
        assignment_request = requests.get(headers = hederr, url = assignment_urll) 
   
        r_j = assignment_request.json()
        # print ('Lenght of JSON : ', len(r_j))        

    
###################################################################################
##############################  File ID and sentence mapping   #################################
###################################################################################
        '''worker ID'''

        workerId_list = []
        for micro_metadata in r_j["microtasks"]:
            sentences = micro_metadata["input"]["data"]
            findWorker_id = micro_metadata["input"]["chain"]
            worker_id = findWorker_id["workerId"]
            workerId_list.append(worker_id)
        # print(workerId_list)
        
        sentence_list = []
        for micro_metadata in r_j["microtasks"]:
            sentences = micro_metadata["input"]["data"]["sentence"]
            #find_file_name = micro_metadata["input"]["files"]["recording"]
            sentence_list.append(sentences)

        fileID_list = [] 
        for item in r_j['assignments']:
            fileID_lists = item['id'] 
            fileID_list.append(fileID_lists)
       
        fileID_sentence_list = tuple(zip(fileID_list, sentence_list))
        # print(fileID_sentence_list)

        #put check condiotn -> if the speakerId and fileID  previouls fetched or not / Fetch on the basis of fileID assign to speakerID
        audio_speaker_merge = {key:value for key, value in zip(fileID_sentence_list , workerId_list)} #speakerID = fileID_list(fieldID)
        print(len(audio_speaker_merge))
        # print(audio_speaker_merge.keys())
        language = accesscodedetails.find_one({"karyaaccesscode": access_code}, {'language': 1,'_id': 0})['language']
        exclude_ids = []
        exclude_ids = getquesidlistofsavedaudios.getquesidlistofsavedaudios(questionnaires,
                                                                            activeprojectname,
                                                                            language,
                                                                            exclude_ids)

        # print(f"LanguageScript: {language}\nExcludeIds: {exclude_ids}")
        file_id_list = []
        print(f"Length of fileIdList: {file_id_list}\nLength of fileIdSet: {set(file_id_list)}")
        for file_id_and_sent in list(audio_speaker_merge.keys()):
            
            current_file_id = file_id_and_sent[0]
            current_sentence = file_id_and_sent[1].strip()

            file_id_list.append(current_file_id)

            ### Checking if the file is already fetched or not
            if current_file_id not in fetched_audio_list:
                
                last_active_ques_id, message =  getquesfromprompttext.getquesfromprompttext(projectsform,
                                                                                    questionnaires,
                                                                                    activeprojectname,
                                                                                    current_sentence,
                                                                                    exclude_ids)
                if last_active_ques_id == 'False': 
                    print(f"{last_active_ques_id}: {message}: {current_sentence}")
                    continue

                rl = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignment/id/input_file'
                    
                # current_sentence = file_id_and_sent[1]
                # print(f"0 current_file_id : {current_file_id}")

                new_url = rl.replace("id", current_file_id)
                # print(new_url)

                ## Fetching audio
                ra = requests.get(url = new_url, headers = hederr)
                # print(type(ra))

                ##Audio Content
                filebytes= ra.content
                # print(type(filebytes))

                karyaspeakerId = audio_speaker_merge[file_id_and_sent]
                # print("Checking line no. 618: ", karyaspeakerId)
                lifespeakerid = accesscodedetails.find_one({'karyaspeakerid': karyaspeakerId}, {'lifespeakerid': 1,'_id': 0})
                
                if lifespeakerid is not None:
                    lifespeakerid = lifespeakerid["lifespeakerid"]
                    # print("lifespeakerid : ", lifespeakerid)
                    # savedFiles = accesscodedetails.find_one({'karyaspeakerid': karyaspeakerId}, {'_id': 0, 'lifespeakerid': 1})['karyasavedfiles']

                    #####################################################
                    '''DATA'''
                    # print("###################################\n",filebytes.getmembers())
                    ''' zip_path = ""
                            with BytesIO(gzip.decompress(zip_path)) as zp:
                            '''

                    with BytesIO(gzip.decompress(filebytes)) as fh: #1
                        fileAudio = tarfile.TarFile(fileobj=fh) #2
                        # print('1', type(fileAudio))
                        # print('2', fileAudio.getnames()) #3
                        # print('2.1', len(fileAudio.getnames())) #3
                        # print('3', fileAudio.getmembers()) #4

                        for member in fileAudio.getmembers():
                            f = fileAudio.extractfile(member)
                            content = f.read()
                            # print('4', type(member))
                            # print('5', type(content))
                            # print ('6', member, content.count)
                            # print ('7', member, content.count)
                            # print ('8', member, len(content))
                            # mongo.save_file(fileAudio.getnames()[0], io.BytesIO(content), audioID='1234567890')
                            new_audio_file = {}
                            new_audio_file['audiofile'] = FileStorage(io.BytesIO(content), filename =  fileAudio.getnames()[0])
                            # print('9', new_audio_file['audiofile'], type(new_audio_file['audiofile']))
                            # print('10', new_audio_file['audiofile'].filename)
                            # if new_audio_file['audiofile'] == 
                            # print(new_audio_file)                            
                            
                            projtyp = getprojecttype.getprojecttype(projects, activeprojectname)
                            # findqId = mongodb_qidinfo.find_one({"projectname": "Q_nmathur54_project_1"},
                            #  
                            # print("line 671 :",current_sentence)
                            # findprojectname = getcurrentuserprojects.getcurrentuserprojects(current_username, userprojects) 
                            
                            # last_active_ques_id =  getquesfromprompttext.getquesfromprompttext(projectsform,
                            #                                                                     questionnaires,
                            #                                                                     activeprojectname,
                            #                                                                     current_sentence,
                            #                                                                     exclude_ids)


                            if projtyp == "questionnaires":
                                # language = accesscodedetails.find_one({"karyaaccesscode": access_code}, {'language': 1,'_id': 0})['language']
                                new_audio_file['Prompt_Audio'+"_"+language] = new_audio_file['audiofile'] # new_audio_file['Transcription Audio']  i have to do this code
                                del new_audio_file['audiofile']
                                #savequespromptfile
                                save_status = savequespromptfile.savequespromptfile(mongo,
                                                                        projects,
                                                                        userprojects,
                                                                        projectsform,
                                                                        questionnaires,
                                                                        projectowner,
                                                                        activeprojectname,
                                                                        current_username,
                                                                        last_active_ques_id, 
                                                                        new_audio_file)
                                # print("last_active_ques_id: ", last_active_ques_id) 
                                # print("activeprojectname :", activeprojectname)                                       
                                # print("11  Saving to Questtionnaire collection")
                            else:
                                save_status = audiodetails.saveaudiofiles(mongo,
                                                                projects,
                                                                userprojects,
                                                                transcriptions,
                                                                projectowner,
                                                                activeprojectname,
                                                                current_username,
                                                                lifespeakerid,
                                                                new_audio_file,
                                                                karyainfo=r_j,
                                                                karya_peaker_id = karyaspeakerId)
                                # print("11  Saving to Transcription collection")
                            # print(exclude_ids)

                            if save_status[0]:
                                ## save in the list of fetched audios
                                exclude_ids.append(last_active_ques_id)
                                # print("status of save_status : ", save_status)
                                accesscodedetails.update_one({"karyaaccesscode": access_code}, {"$addToSet": {"karyafetchedaudios":current_file_id}})
                else:
                    print(f"lifespeakerid not found!: {karyaspeakerId}")
            else:
                print(f"Audio already fetched: {current_sentence}")

            print(f"Length of fileIdList: {len(file_id_list)}\nLength of fileIdSet: {len(set(file_id_list))}")
        return redirect(url_for('karya_bp.home_insert'))

    return render_template("fetch_karya_audio.html")

#################################################################################################
    ########################################## Zip File #############################################
    #################################################################################################

@karya_bp.route('/fetch_karya_audio_zip', methods=['GET', 'POST'])
def fetch_karya_audio_zip():
    projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo, 'projects', 'userprojects', 'transcriptions')
    current_username = getcurrentusername.getcurrentusername()
    print('curent user', current_username)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)

    if request.method == "POST":
        # listWorkerId = []
        # listrecording = []
        audioZipUpload = request.files['accesscodefile']
        print(type(audioZipUpload))
        # for audioZipUpload in audioZipUpload:
        fileAudio = tarfile.open(fileobj=audioZipUpload, mode= 'r')
        print(type(fileAudio))
        print('1', type(fileAudio))
        print('2', fileAudio.getnames()) #3
        print('3', fileAudio.getmembers()) #4
        for filename in fileAudio.getnames():
            if (filename.endswith('.json')):
                print(filename)
                member = fileAudio.getmember(filename)
                f=fileAudio.extractfile(member)
                content=f.read()
                print('4', type(member))
                print('5', type(content))
                jsondata = json.load(io.BytesIO(content))
                print(jsondata)
                speakerId = jsondata['worker_id']
                wavfilename = jsondata['recording']
                wavmember = fileAudio.getmember(wavfilename)
                wavf=fileAudio.extractfile(wavmember)
                wavcontent=wavf.read()
                print('4', type(wavmember))
                print('5', type(wavcontent))
                wavdata = io.BytesIO(wavcontent)

                new_audio_file = {}
                new_audio_file['audiofile'] = FileStorage(wavdata, filename=wavfilename)
                print('9', new_audio_file['audiofile'], type(new_audio_file['audiofile']))


                audiodetails.saveaudiofiles(mongo,
                            projects,
                            userprojects,
                            transcriptions,
                            projectowner,
                            activeprojectname,
                            current_username,
                            speakerId,
                            new_audio_file,
                            karyainfo=jsondata,
                            karya_peaker_id=speakerId)

     

        # return redirect(url_for('karya_bp.home_insert'))
        return redirect(url_for('karya_bp.home_insert'))
    return render_template("karya_bp.fetch_karya_audio_zip")



