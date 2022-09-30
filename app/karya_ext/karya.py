from curses import meta
from inspect import getmembers
from lib2to3.pytree import convert
from operator import ne
from types import MemberDescriptorType
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
from app.controller import getprojectowner, getcurrentusername
from app.controller import audiodetails
# from app.forms import UserLoginForm, RegistrationForm
# from app.models import UserLogin
import pandas as pd
from flask_login import current_user, login_user, logout_user, login_required
from io import StringIO
import re
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from app.routes import activeprojectname
import wave
from zipfile import ZipFile

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
    return render_template("home_insert.html")


##################################################################################
#########################################################################################################
##################################################################################
import gridfs
import os
import glob
from pathlib import Path
import sys
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
from scipy.io.wavfile import read, write
import json
import os
import zipfile




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
    karyaaccesscodedetails, = getdbcollections.getdbcollections(mongo, 'accesscodedetails')

    if request.method == "POST":
    
        file = request.files['accesscodefile']
        data = pd.read_csv(file)
        df = pd.DataFrame(data)
        
        df["id"] = df["id"].str[1:]
        df["access_code"] = df["access_code"].str[1:]
        df["phone_number"] = df["phone_number"].str[1:]
        # print(data["id"],df["access_code"],df["phone_number"])
        print(df["id"])
        print(df)
        for index,item in df.iterrows(): 
            current_dt = str(datetime.now()).replace('.', ':')

            insert_dict = {
                        "lifespeakerid": item["id"], "karyaspeakerid": item["access_code"], "lifeid": "",
                        "karya_info":{"username": "", "projectname": ""}, 
                        "current": {"speakerMetadata": {"name": "", "agegroup": "", "gender": "", 
                                                "educationlevel": "", "educationmediumupto12": "", 
                                                "educationmediumafter12": "", "speakerspeaklanguage" :"", 
                                                "recordingplace": "", "typeofrecordingplace" : "", 
                                                "activeAccessCode": ""}, "current_date":current_dt},
                        "previous": {},
                        "isActive": 0}
                        

            print ('Data to be inserted', insert_dict)
            return_obj = karyaaccesscodedetails.insert (insert_dict)
            print ('Return object', return_obj)
            # print (return_obj.inserted_id)


            datafromdb = karyaaccesscodedetails.find({},{"_id" :0})
        print(list(datafromdb))
        
        # flash('Successfully added new lexeme')
        return redirect(url_for('karya_bp.home_insert'))
    return render_template("uploadfile.html")




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
    # jp = karyaaccesscode["lifespeakerid"]
    print ('Request method', request.method)

    speaker_data_accesscode = []
    speaker_data_name = []
    speaker_data_age = []
    speaker_data_gender = []
    mongodb_info = mongo.db.accesscodedetails

    #access-code
    # accode = mongodb_info.find({"isActive":1},{"current.speakerMetadata.lifespeakerid":1,"_id" :0})
    # for data in accode:   
    #     speaker_accode = data["current"]["speakerMetadata"]["lifespeakerid"]                                    
    #     speaker_data_accesscode.append(speaker_accode)
    # print(speaker_data_accesscode)   

    #speaker_name
    name = mongodb_info.find({"isActive":1},{"current.speakerMetadata.name" :1,"_id" :0})
    for data in name:
        speaker_name = data["current"]["speakerMetadata"]["name"]                                     
        speaker_data_name.append(speaker_name)
    print(speaker_data_name)

    #age
    age = mongodb_info.find({"isActive":1},{"current.speakerMetadata.agegroup":1,"_id" :0})
    for data in age:   
        speaker_age = data["current"]["speakerMetadata"]["agegroup"]                                    
        speaker_data_age.append(speaker_age)
    print(speaker_data_age)    

    #gender
    gender = mongodb_info.find({"isActive":1},{"current.speakerMetadata.gender":1,"_id" :0})
    for data in gender:
        speaker_gender = data["current"]["speakerMetadata"]["gender"]                                     
        speaker_data_gender.append(speaker_gender)
    print(speaker_data_gender)                                  
   
    print(speaker_data_accesscode)
    

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
        #############################################################################################
        namekaryaID = mongodb_info.find_one({"isActive":0},{"lifespeakerid":1, "_id" :0})
        # namekaryaIDDOB = mongodb_info.find_one({"isActive":0},{"current.speakerMetadata.agegroup":1 , "_id" :0})
        # rDOB = namekaryaIDDOB["current"]["speakerMetadata"]["agegroup"]
        # renameInFormDOB = rDOB.replace("-","")
        
        # for lidata in namekaryaID:
        #     print("574 ", lidata)  
        namekaryaIDDOB = fage
        renameInFormDOB = namekaryaIDDOB.replace("-","")
        print("227  ==========================================>>>>>>>>>>   ", renameInFormDOB)
        codes = namekaryaID["lifespeakerid"]
        print(codes)
        nameInForm = fname 
        print(nameInForm)
        renameInForm = nameInForm.replace(" ","")
        lowerRenameInForm = renameInForm.lower()
        renameDOB =  "".join([lowerRenameInForm,renameInFormDOB])
        print("232 =========================>>>>>>>>>>>>    " , renameDOB)
        renameCode ="_".join([renameDOB,codes])
        print("line 583", renameCode)  
            # namekaryaAddID.append(renameCode)
                        
                # speaker_data_accesscode.append(data["lifespeakerid"])
        # print("587 ",namekaryaAddID)


        update_data = {"lifeid": renameCode,
                                    "current.speakerMetadata.name": fname, 
                                    "current.speakerMetadata.agegroup": fage, 
                                    "current.speakerMetadata.gender": fgender,
                                    "current.speakerMetadata.educationlevel": educlvl,
                                    "current.speakerMetadata.educationmediumupto12": moe12,
                                    "current.speakerMetadata.educationmediumafter12": moea12,
                                    "current.speakerMetadata.speakerspeaklanguage": sols,
                                    "current.speakerMetadata.recordingplace": por,
                                    "current.speakerMetadata.typeofrecordingplace": toc,
                                    "isActive": 1}
        
        # accesscode = request.form.get('accode')
#########################################################################################################################
#########################################################################################################################
        accesscode = request.form.get('accode')
        print("=======================> ",accesscode )
#########################################################################################################################
##########################################################################################################################

        print("this acc code at line 460", accesscode)
        if accesscode == '':
            karyaaccesscode = mongodb_info.find_one({"isActive":0},{"karyaspeakerid":1, "_id" :0})
            if karyaaccesscode != None:
                accesscode = karyaaccesscode['karyaspeakerid']
            else:
                accesscode = ''
                print ('Karya access code', accesscode)
            
                print ('445 Update Data', update_data)
            mongodb_info.update_one({"karyaspeakerid": accesscode}, {"$set": update_data})
        else:
            previous_speakerdetails = mongodb_info.find_one({"karyaspeakerid": accesscode},
                                                {"current.speakerMetadata": 1, "_id": 0,})

            ###########################################
            ## TOdo: Add date to the previous metadata
            ###########################################


            # the document's content will change to this:
            # new_val = {"some text": "ObjectRocket: Database Management and Hosting"}

            # pass the 'new_val' obj to the method call
            
            date_of_modified = str(datetime.now()).replace(".", ":" )


            update_old_data = {"previous."+date_of_modified+".speakerMetadata.name": previous_speakerdetails["current"]["speakerMetadata"]["name"], 
                                                    "previous."+date_of_modified+".speakerMetadata.agegroup": previous_speakerdetails["current"]["speakerMetadata"]["agegroup"], 
                                                    "previous."+date_of_modified+".speakerMetadata.gender": previous_speakerdetails["current"]["speakerMetadata"]["gender"],
                                                    "previous."+date_of_modified+".speakerMetadata.educationlevel": previous_speakerdetails["current"]["speakerMetadata"]["educationlevel"],
                                                    "previous."+date_of_modified+".speakerMetadata.educationmediumupto12": previous_speakerdetails["current"]["speakerMetadata"]["educationmediumupto12"],
                                                    "previous."+date_of_modified+".speakerMetadata.educationmediumafter12": previous_speakerdetails["current"]["speakerMetadata"]["educationmediumafter12"],
                                                    "previous."+date_of_modified+".speakerMetadata.speakerspeaklanguage": previous_speakerdetails["current"]["speakerMetadata"]["speakerspeaklanguage"],
                                                    "previous."+date_of_modified+".speakerMetadata.recordingplace": previous_speakerdetails["current"]["speakerMetadata"]["recordingplace"]
                                                    }


            mongodb_info.update_one({"karyaspeakerid": accesscode}, {"$set": update_old_data}) # Edit_old_user_info
            mongodb_info.update_one({"karyaspeakerid": accesscode}, {"$set": update_data}) #new_user_info

    return redirect(url_for('karya_bp.homespeaker'))

   
##############################################################################################################
##############################################################################################################
######################################      View Table HomeSpeaker         ###################################
##############################################################################################################
##############################################################################################################



@karya_bp.route('/homespeaker')
def homespeaker():
   
    # formremaingkaryaaccesscode = ', '.join([data['lifespeakerid'] for data in remaingkaryaaccesscode])
    # faccsess = formremaingkaryaaccesscode.count() 
    # acc = request.form.get('accessid') 
    # print("fname", acc)
    namekaryaAddID = []
    namekaryaAddIDtuple = tuple(namekaryaAddID)
    speaker_data_accesscode = []
    karya_accesscode = []
    speaker_data_name = []
    speaker_data_age = []
    speaker_data_gender = []
    mongodb_info = mongo.db.accesscodedetails
    # print(mongodb_info)
    
##################################3 LifeID + Accesscode #####################################################################
    namekaryaID = mongodb_info.find({"isActive":1},{"lifeid":1, "_id" :0})
    for lidata in namekaryaID:
        namekaryaAddID.append(lidata)
        # speaker_data_accesscode.append(data["lifespeakerid"])
    print("587 ",namekaryaAddID)

    lifeaccesscode = mongodb_info.find({"isActive":1},{"lifespeakerid":1, "_id" :0})
    for data in lifeaccesscode:   
        codes = data["lifespeakerid"]
        speaker_data_accesscode.append(data)
        # speaker_data_accesscode.append(data["lifespeakerid"])
    print(speaker_data_accesscode)

############## Access Code - KaryaID ###############################################################
    karyaaccesscode = mongodb_info.find({"isActive":1},{"karyaspeakerid":1,"_id" :0})
    for karyadata in karyaaccesscode:   
        karyacodes = karyadata["karyaspeakerid"]
        karya_accesscode.append(karyadata)
        
        # speaker_data_accesscode.append(data["lifespeakerid"])
    print('596    ####################################### ',karya_accesscode)


    name = mongodb_info.find({"isActive":1},{"current.speakerMetadata.name" :1,"_id" :0})
    print(name)
    for data in name:
        # speaker_name = data["karya_info"]["current"]["speaker_info"]["speakerMetadata"]["name"]  
        # speaker_name = data["current"]["speakerMetadata"]["name"]  
        speaker_name = data["current"]["speakerMetadata"]                                
        speaker_data_name.append(speaker_name)
    print(speaker_data_name)

    #age"
    age = mongodb_info.find({"isActive":1},{"current.speakerMetadata.agegroup":1,"_id" :0})
    for data in age:   
        # speaker_age = data["karya_info"]["current"]["speaker_info"]["speakerMetadata"]["agegroup"]
        # speaker_age = data["current"]["speakerMetadata"]["agegroup"]  
        speaker_age = data["current"]["speakerMetadata"]                                
        speaker_data_age.append(speaker_age)
    print(speaker_data_age)    

    #gender
    gender = mongodb_info.find({"isActive":1},{"current.speakerMetadata.gender":1,"_id" :0})
    for data in gender:
        # speaker_gender = data["karya_info"]["current"]["speaker_info"]["speakerMetadata"]["gender"] 
        # speaker_gender = data["current"]["speakerMetadata"]["gender"] 
        speaker_gender = data["current"]["speakerMetadata"]                                 
        speaker_data_gender.append(speaker_gender)
    print(speaker_data_gender)                                  
  
    # speaker_data = [speaker_data_accesscode, speaker_data_name, speaker_data_age, speaker_data_gender]
    data_table = [[ karya_accesscode[i], namekaryaAddID[i], speaker_data_name[i], speaker_data_age[i], speaker_data_gender[i]] for i in range(0, len(karya_accesscode))]
    
    print(data_table)
    return render_template('homespeaker.html', data = data_table)


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
    speakerdetails = accesscodedetails.find_one({"karyaspeakerid": asycaccesscode},
                                                {"_id": 0,
                                                "current.speakerMetadata": 1})
    # mongodb_info = mongo.db.accesscodedetails

    # speakerdetails = mongodb_info.find_one({"lifespeakerid": asycaccesscode}, {"speaker_info.speakerMetadata.name": 1, 
    #                                                 "karya_info.current.speaker_info.speakerMetadata.agegroup": 1, 
    #                                                 "karya_info.current.speaker_info.speakerMetadata.gender": 1,
    #                                                 "karya_info.current.speaker_info.speakerMetadata.educationlevel": 1,
    #                                                 "karya_info.current.speaker_info.speakerMetadata.medium-of-education-upto-12th": 1,
    #                                                 "karya_info.current.speaker_info.speakerMetadata.medium-of-education-after-12th": 1,
    #                                                 "karya_info.current.speaker_info.speakerMetadata.other-languages-speaker-could-speak": 1,
    #                                                 "karya_info.current.speaker_info.speakerMetadata.place-of-recording": 1,
    #                                                 "karya_info.current.speaker_info.speakerMetadata.type-of-place": 1,"_id": 0})

    # speakerdetails = speakerdetails["karya_info"]["current"]["speaker_info"]["speakerMetadata"]
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
    ##Registration
    registeruser_urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/worker/otp/generate'
    access_code = request.args.get("acode")
    phone_number = request.args.get("mob")

    registeruser_hederr= {'access-code':access_code, 'phone-number':phone_number}
    register_request = requests.put(url = registeruser_urll, headers = registeruser_hederr)

    return jsonify(result="False")



@karya_bp.route('/fetch_karya_audio', methods=['GET', 'POST'])
def fetch_karya_audio():
    karyaaudiodetails, = getdbcollections.getdbcollections(mongo, 'fetchkaryaaudio')


# ############################   verify OTP
    if request.method == 'POST':
        access_code = request.form.get("access_code")
        phone_number = request.form.get("mobile_number")
        otp = request.form.get("karya_otp")

        print ("OTP", otp)
        print ("access_code", access_code)
        print ("Mobile", phone_number)

        verifyotp_urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/worker/otp/verify'
        verifyotp_hederr= {'access-code':access_code, 'phone-number':phone_number, 'otp':otp}
        verifyPh_request = requests.put(url = verifyotp_urll, headers = verifyotp_hederr) 
        print (verifyPh_request.json())
        ##TODO: Put check for verifying if the OTP was correct or not. If correct then proceed otherwise send error
        getTokenid_assignment_hedder = verifyPh_request.json()['id_token']
        print ("ID token", getTokenid_assignment_hedder)
        
    #     ###get new assignment
    #     import requests
    #     # karya_tokenid = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImExNWE0MGQ0In0.eyJzdWIiOiIyODE0NzQ5NzY3MTA3MDMiLCJlbnRpdHkiOiJ3b3JrZXIiLCJpYXQiOjE2NjI5MDI1NTIsImV4cCI6MTY2NTQ5NDU1MiwiYXVkIjoia2FyeWEtc2VydmVyIiwiaXNzIjoia2FyeWEtc2VydmVyIn0.Dvq44bd0RDdQeAGBP39bU-Hsedd_PJs2XpIbPNuTeR0'
        assignment_urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=new&from=2021-05-11T07:23:40.654Z'
        # hederr= {'karya-id-token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImExNWE0MGQ0In0.eyJzdWIiOiIyODE0NzQ5NzY3MTA3MDMiLCJlbnRpdHkiOiJ3b3JrZXIiLCJpYXQiOjE2NjI5MDI1NTIsImV4cCI6MTY2NTQ5NDU1MiwiYXVkIjoia2FyeWEtc2VydmVyIiwiaXNzIjoia2FyeWEtc2VydmVyIn0.Dvq44bd0RDdQeAGBP39bU-Hsedd_PJs2XpIbPNuTeR0'}
        # assignment_hederr = {'karya-id-token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImExNWE0MGQ0In0.eyJzdWIiOiIxNjc3NzIzNSIsImVudGl0eSI6IndvcmtlciIsImlhdCI6MTY2MzU5MDA2NiwiZXhwIjoxNjY2MTgyMDY2LCJhdWQiOiJrYXJ5YS1zZXJ2ZXIiLCJpc3MiOiJrYXJ5YS1zZXJ2ZXIifQ.UGpR4dGasm-FQNjHMHT3Ivx3-noKAF-R04vdFOAXJiE'}
        assignment_request = requests.get(headers = {'karya-id-token': getTokenid_assignment_hedder}, url = assignment_urll) 
        # assignment_request_json = assignmentRequest_json.json()
        
        # assignmentRequest_json = assignment_request.json()["assignments"]
            


        ################################
        # urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=new&from=2021-05-11T07:23:40.654Z'
        # # hederr= {'karya-id-token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImExNWE0MGQ0In0.eyJzdWIiOiIyODE0NzQ5NzY3MTA3MDMiLCJlbnRpdHkiOiJ3b3JrZXIiLCJpYXQiOjE2NjI5MDI1NTIsImV4cCI6MTY2NTQ5NDU1MiwiYXVkIjoia2FyeWEtc2VydmVyIiwiaXNzIjoia2FyeWEtc2VydmVyIn0.Dvq44bd0RDdQeAGBP39bU-Hsedd_PJs2XpIbPNuTeR0'}
        # hederr = {'karya-id-token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImExNWE0MGQ0In0.eyJzdWIiOiIxNjc3NzIzNSIsImVudGl0eSI6IndvcmtlciIsImlhdCI6MTY2MzU5MDA2NiwiZXhwIjoxNjY2MTgyMDY2LCJhdWQiOiJrYXJ5YS1zZXJ2ZXIiLCJpc3MiOiJrYXJ5YS1zZXJ2ZXIifQ.UGpR4dGasm-FQNjHMHT3Ivx3-noKAF-R04vdFOAXJiE'}
        # r = requests.get(headers = hederr, url = urll) 


        # r.json()["assignments"]
        r_j = assignment_request.json()
        print ('Lenght of JSON', len(r_j))

        projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo, 'projects', 'userprojects', 'transcriptions')
        current_username = getcurrentusername.getcurrentusername()
        print(current_username)
        activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
        projectowner = getprojectowner.getprojectowner(projects, activeprojectname)

    #################################################################################################
    ########################################## Zip File #############################################
    #################################################################################################
    # if request.method == "POST":
    #     listWorkerId = []
    #     listrecording = []
    #     audioZipUpload = request.files['accesscodefile']
    #     print(type(audioZipUpload))
    #     # for audioZipUpload in audioZipUpload:
    #     fileAudio = tarfile.open(fileobj=audioZipUpload, mode= 'r')
    #     print(type(fileAudio))
    #     print('1', type(fileAudio))
    #     print('2', fileAudio.getnames()) #3
    #     print('3', fileAudio.getmembers()) #4
    #     for filename in fileAudio.getnames():
    #         if (filename.endswith('.json')):
    #             print(filename)
    #             member = fileAudio.getmember(filename)
    #             f=fileAudio.extractfile(member)
    #             content=f.read()
    #             print('4', type(member))
    #             print('5', type(content))
    #             jsondata = json.load(io.BytesIO(content))
    #             print(jsondata)
    #             speakerId = jsondata['worker_id']
    #             wavfilename = jsondata['recording']
    #             wavmember = fileAudio.getmember(wavfilename)
    #             wavf=fileAudio.extractfile(wavmember)
    #             wavcontent=wavf.read()
    #             print('4', type(wavmember))
    #             print('5', type(wavcontent))
    #             wavdata = io.BytesIO(wavcontent)

    #             new_audio_file = {}
    #             new_audio_file['audiofile'] = FileStorage(wavdata, filename=wavfilename)
    #             print('9', new_audio_file['audiofile'], type(new_audio_file['audiofile']))
    #             audiodetails.saveaudiofiles(mongo,
    #                         projects,
    #                         userprojects,
    #                         transcriptions,
    #                         projectowner,
    #                         activeprojectname,
    #                         current_username,
    #                         speakerId,
    #                         new_audio_file,
    #                         karyainfo=jsondata,
    #                         karya_peaker_id=speakerId)

     

    #     return redirect(url_for('karya_bp.home_insert'))

###################################################################################
##############################  API Fetch Audio   #################################
###################################################################################
        '''worker ID'''
        # list_workerID = []
        # getWorker_id = r_j['microtasks']
        # for findWorker_id in getWorker_id:
        #     workerid = findWorker_id["input"]["chain"]
        #     worker_id = workerid["workerId"]
        #     tt = list_workerID.append[worker_id]
        # print(list_workerID)  
        workerId_list = []
        for micro_metadata in r_j["microtasks"]:
            sentences = micro_metadata["input"]["data"]
            findWorker_id = micro_metadata["input"]["chain"]
            worker_id = findWorker_id["workerId"]
            workerId_list.append(worker_id)
        # print(workerId_list)
            
        sentence = []
        for micro_metadata in r_j["microtasks"]:
            sentences = micro_metadata["input"]["data"]
            sentence.append(sentences)
    ###################################################################
        id_find = r_j['assignments']
        speakerID = [item['id'] for item in id_find] #new_dict
        # print(len(new_dict))

    ###################################################################
        # res = {workerId_list: new_dict}
        # print(res)
        # res = dict(zip(workerId_list, new_dict))
        # print(res)
        audio_speaker_merge = {key:value for key, value in zip(speakerID , workerId_list)}
        # print(audio_speaker_merge)
        # print(audio_speaker_merge.keys())

        hederr= {'karya-id-token':getTokenid_assignment_hedder}

        rl = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignment/id/input_file'
        for new_d in list(audio_speaker_merge.keys()):
            print(f"0 {new_d}")
            new_url = rl.replace("id", new_d )
            # print(new_url)
            ra = requests.get(url = new_url, headers = hederr)
            print(type(ra))
            filebytes= ra.content
            print(type(filebytes))

            projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo, 'projects', 'userprojects', 'transcriptions')
            
            current_username = getcurrentusername.getcurrentusername()
            activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
            projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
            
            speakerId = audio_speaker_merge[new_d]

            #####################################################
            '''DATA'''
            # print("###################################\n",filebytes.getmembers())
            ''' zip_path = ""
                    with BytesIO(gzip.decompress(zip_path)) as zp:
                    '''
    
        

            with BytesIO(gzip.decompress(filebytes)) as fh: #1
                fileAudio = tarfile.TarFile(fileobj=fh) #2
                print('1', type(fileAudio))
                print('2', fileAudio.getnames()) #3
                print('2.1', len(fileAudio.getnames())) #3
                print('3', fileAudio.getmembers()) #4
                for member in fileAudio.getmembers(): 
                    f=fileAudio.extractfile(member)
                    content=f.read()
                    print('4', type(member))
                    print('5', type(content))
                    print ('6', member, content.count)
                    print ('7', member, content.count)
                    print ('8', member, len(content))
                    # mongo.save_file(fileAudio.getnames()[0], io.BytesIO(content), audioID='1234567890')
                    new_audio_file = {}
                    new_audio_file['audiofile'] = FileStorage(io.BytesIO(content), filename =  fileAudio.getnames()[0])
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
                            karyainfo=r_j,
                            karya_peaker_id=speakerId)
                
        return redirect(url_for('karya_bp.home_insert'))

    return render_template("fetch_karya_audio.html")

