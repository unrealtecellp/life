from curses import meta
from inspect import getmembers
from lib2to3.pytree import convert
from operator import ne
from types import MemberDescriptorType

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



@karya_bp.route('/fetch_karya_audio', methods=['GET', 'POST'])
def fetch_karya_audio():
    karyaaudiodetails, = getdbcollections.getdbcollections(mongo, 'fetchkaryaaudio')


    urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=new&from=2021-05-11T07:23:40.654Z'
    # hederr= {'karya-id-token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImExNWE0MGQ0In0.eyJzdWIiOiIyODE0NzQ5NzY3MTA3MDMiLCJlbnRpdHkiOiJ3b3JrZXIiLCJpYXQiOjE2NjI5MDI1NTIsImV4cCI6MTY2NTQ5NDU1MiwiYXVkIjoia2FyeWEtc2VydmVyIiwiaXNzIjoia2FyeWEtc2VydmVyIn0.Dvq44bd0RDdQeAGBP39bU-Hsedd_PJs2XpIbPNuTeR0'}
    hederr = {'karya-id-token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImExNWE0MGQ0In0.eyJzdWIiOiIxNjc3NzIzNSIsImVudGl0eSI6IndvcmtlciIsImlhdCI6MTY2MzU5MDA2NiwiZXhwIjoxNjY2MTgyMDY2LCJhdWQiOiJrYXJ5YS1zZXJ2ZXIiLCJpc3MiOiJrYXJ5YS1zZXJ2ZXIifQ.UGpR4dGasm-FQNjHMHT3Ivx3-noKAF-R04vdFOAXJiE'}
    r = requests.get(headers = hederr, url = urll) 


    # r.json()["assignments"]
    r_j = r.json()

    projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo, 'projects', 'userprojects', 'transcriptions')
    current_username = getcurrentusername.getcurrentusername()
    print(current_username)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)
    if request.method == "POST":
        listWorkerId = []
        listrecording = []
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
        # files = fileAudio.getmembers()
        # # for j in files:
        # f = fileAudio.extractfile(files[0]) # if your docs.json is in the 0th position
        # file_data_json = f.read().decode("latin-1")
        # # print(type(file_data_json))
        # file_data_json = json.loads(file_data_json)
        # jsonWorkerId = file_data_json['worker_id']
        # jsonrecording = file_data_json['recording']
        # # print(list(jsonrecording," : ",jsonWorkerId)
        # listWorkerId.append(jsonWorkerId)
        # listrecording.append(jsonrecording)
        # workeridRecordingDict = {listrecording[i]: listWorkerId[i] for i in range(len(listrecording))}
        # print(workeridRecordingDict)
      #create loop to extract data 
      


        # file_data = audioZipUpload.read().decode("latin-1")
        # print(file_data)
        # file_data_json = json.loads(file_data)
        # print(type(file_data_json)) 
        # file_data = audioZipUpload.read().decode("latin-1")
        # print(file_data)
        # file_data_json = json.loads(file_data)
        # print(type(file_data_json))

        # jsonWorkerId = file_data_json['worker_id']
        # jsonrecording = file_data_json['recording']
        # # print(list(jsonrecording," : ",jsonWorkerId)
        # listWorkerId.append(jsonWorkerId)
        # listrecording.append(jsonrecording)
        # workeridRecordingDict = {listrecording[i]: listWorkerId[i] for i in range(len(listrecording))}
        
        # print(workeridRecordingDict.keys()) # speaker_ID
        # print(workeridRecordingDict.values()) #new_audio_file
        # speakerId = workeridRecordingDict.values()
        


        # for member in fileAudio.getmembers(): 
        #     f=fileAudio.extractfile(member)
        #     content=f.read()
        #     new_audio_file = {}
        #     new_audio_file['audiofile'] = FileStorage(content, filename =  fileAudio.getnames()[1])
        #     # print(new_audio_file["audiofile"])
        #     # print(new_audio_file)
        #     print('9', new_audio_file['audiofile'], type(new_audio_file['audiofile']))
        #     audiodetails.saveaudiofiles(mongo,
        #                     projects,
        #                     userprojects,
        #                     transcriptions,
        #                     projectowner,
        #                     activeprojectname,
        #                     current_username,
        #                     speakerId,
        #                     new_audio_file,
        #                     karyainfo = file_data_json,
        #                     karya_speaker_id=listWorkerId)
     

        return redirect(url_for('karya_bp.home_insert'))
#########################################################  
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

    hederr= {'karya-id-token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImExNWE0MGQ0In0.eyJzdWIiOiIxNjc3NzIzNSIsImVudGl0eSI6IndvcmtlciIsImlhdCI6MTY2MzU5MDA2NiwiZXhwIjoxNjY2MTgyMDY2LCJhdWQiOiJrYXJ5YS1zZXJ2ZXIiLCJpc3MiOiJrYXJ5YS1zZXJ2ZXIifQ.UGpR4dGasm-FQNjHMHT3Ivx3-noKAF-R04vdFOAXJiE'}

    rl = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignment/id/input_file'
    for new_d in audio_speaker_merge.keys():
        new_url = rl.replace("id", new_d )
        # print(new_url)
        ra = requests.get(url = new_url, headers = hederr)
        print(type(ra))
        filebytes= ra.content
        print(type(filebytes))

        # # testing easyAnno save files code
        # with ZipFile(gzip.decompress(filebytes)) as myzip:
        #     for file_name in myzip.namelist():
        #         with myzip.open(file_name) as myfile:
        #             # print(myfile.read())
        #             # if (not file_name.endswith('.tsv')):
        #             print(file_name)
        #             # project_name = proj_name
        #             # if projects.find_one({"projectName": project_name}, {'_id' : 0, "projectName": 1}) != None:
        #             #     flash(f'File Name : {project_name} already exist!', 'warning')
        #             #     return redirect(url_for('home'))

        #             # image_anno_detail = {}
        #             image_id = 'I'+re.sub(r'[-: \.]', '', str(datetime.now()))
        #             image_file = io.BytesIO(myfile.read())
        #             # store images to mongodb fs collection
        #             mongo.save_file(file_name, image_file, imageId = image_id)
        #             return redirect(url_for('karya_bp.home_insert'))

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
                # audiodetails.saveaudiofiles(mongo,
                #             projects,
                #             userprojects,
                #             transcriptions,
                #             projectowner,
                #             activeprojectname,
                #             current_username,
                #             speakerId,
                #             new_audio_file,
                #             karyainfo = r_j,
                #             karya_peaker_id=speakerId)
    return redirect(url_for('karya_bp.home_insert'))
#             # extracted_audio = fileAudio.extractall('/home/kmi/Desktop/Sid')
#             # audio_read = extracted_audio.read()
#             # print(audio_read)
#         # zero = []
#     # path = "/home/kmi/Desktop/sid"
#     # files = os.listdir(path)

#     # # for filename in sorted(os.listdir(path)):
#     # for filename in glob.glob(os.path.join(path, '*.wav')):
#     #     filePath = os.path.join(path, filename)
#     #     with open(filePath, 'rb') as f:
#     #     # input_wav = wave.open(filePath, 'rb')
#     #         input_wav = f.read()
#         # print(input_wav)

    
# ####################################################################################################################
# # ############################        ###############################    #################      ###################################             

#     # def read_text_file(file_path):
#     #     with open(file_path, 'rb') as f:
#     #         print(f.read())

#     # # iterate through all file
#     # for file in os.listdir():
#     #     # Check whether file is in text format or not
#     #     if file.endswith(".wav"):
#     #         file_path = f"{path}/{file}"

#     # # call read text file function
#     # input_wav = read_text_file(file_path) 

# # here, input_wav is a bytes object representing the wav object
#         # rate, data = read(io.BytesIO(input_wav))
#         # bytes_wav = bytes()
#         # byte_io = io.BytesIO(bytes_wav)
#         # # write(byte_io, rate, reversed_data)
#         # write(byte_io, rate, data)
#         # output_wav = byte_io.read() # and back to bytes, tadaaa
#         # # output_wav can be written to a file, of sent over the network as a binary
#         # print(output_wav)
#         # filedata = FileStorage(output_wav, filename =  filename)
# ########################################################################################################################
# # #############################    ############################# #########################   ################################## 
#         # db = mongo.db
#         # fs = gridfs.GridFS(db)
#         # filedata = fs.put(input_wav, filename = filename)

#         filedata = FileStorage(stream = input_wav , filename= filename)
#         # print("##################################","Filedatr", filedata , "################################")

#     # # with BytesIO(gzip.decompress(filebytes)) as fh:
#     # #     filedata = tarfile.TarFile(fileobj=fh)
#     # #     # tf.extractall('/home/kmi/Desktop/test')
#         new_audio_file = {'audiofile': filedata}
# ##################################################################################################################
#         speakerId = worker_id
#         # print(speakerId)


#         # print(type(filedata))
#         # print(new_audio_file)
# ############################################################################################################
#         audiodetails.saveaudiofiles(mongo,
#                             projects,
#                             userprojects,
#                             transcriptions,
#                             projectowner,
#                             activeprojectname,
#                             current_username,
#                             speakerId,
#                             new_audio_file)


# #################################################################################################
#         # mapping of this function is with the 'uploadaudiofiles' route.
            
#     # print("File Saved")






#         # audioformat_dict = {
#         #                         "projects": "", 
#         #                         "userprojects": "",
#         #                         "transcriptions":"",
#         #                         "activeprojectname":"",
#         #                         "current_username": "",
#         #                         "speakerId":"",
#         #                         "new_audio_files":""}













    # karyaaudiodetails.insert_one({()})
    return render_template("fetch_karya_audio.html")







##################################################################################
#########################################################################################################
##################################################################################






import codecs
import os
from datetime import datetime
@karya_bp.route('/uploadfile' , methods=['GET', 'POST'])
def uploadfile():
    karyaaccesscodedetails, = getdbcollections.getdbcollections(mongo, 'accesscodedetails')
    # print ('FInd', karyaaccesscodedetail.find_one({}))
    # print ('FInd details', karyaaccesscodedetails.find_one({}))
    # print ('karyaaccesscodedetails', karyaaccesscodedetails)
    # print ('Mongo', mongo)
    
    if request.method == "POST":
        # speakermeta  = {"speakerMetadata": {"name": "", "agegroup": "", "gender": "", 
        #                                         "educationlevel": "", "medium-of-education-upto-12th": "", 
        #                                         "medium-of-education-after-12th": "", "other-languages-speaker-could-speak" :"", 
        #                                         "place-of-recording": "", "type-of-place" : "", 
        #                                         "activeAccessCode": ""}}
        # speakermeta  = {"speakerMetadata": {"name": "", "agegroup": "", "gender": "", 
        #                                         "educationlevel": "", "educationmediumupto12": "", 
        #                                         "educationmediumafter12": "", "speakerspeaklanguage" :"", 
        #                                         "recordingplace": "", "typeofrecordingplace" : "", 
        #                                         "activeAccessCode": ""}


        karyaaccesscodecollection = {}
        # f = request.files['accesscodefile']
        f = request.files.to_dict()
        print(f"LINE NUMBER: 145: {type(f)}")
        print(f"LINE NUMBER: 146: {f}")
        f= f['accesscodefile']
        
        filename = secure_filename(f.filename)
        cur_dir = os.getcwd()
        print (cur_dir)
        fpath = os.path.join(cur_dir, 'app', 'karya_ext', 'static', filename)

        f.save(fpath)

        # acode_f = open(fpath,"r")

        if os.path.exists(fpath):
            print (fpath, 'found')

        # content = acode_f.readlines()
        with open (fpath) as content:
            for line in content:
                code = line.strip()
                print (code)
                # karyaaccesscodecollection[code] = accesscodebp
                current_dt = str(datetime.now()).replace('.', ':')
               
                # insert_dict = {
                #         "lifespeakerid": code, "karyaspeakerid": code,
                #         "karya_info":{
                #             "username": "",
                #             "project/language name": "",
                #             "current": {"speaker_info": speakermeta, "current_date":current_dt},
                #             "previous": {"speaker_info": speakermeta, "previous_date":current_dt}   
                #         },
                #         "isActive": 0
                        
                #     }

                insert_dict = {
                        "lifespeakerid": code, "karyaspeakerid": code,
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
        
        flash('Successfully added new lexeme')
        return redirect(url_for('karya_bp.home_insert'))
    return render_template("uploadfile.html")



# class accesscodedetails(mongo.db.Document):
#     accesscode = mongo.db.StringField()
#     name = mongo.db.StringField()
#     agegroup = mongo.db.StringField()
#     gender = mongo.db.StringField()
############################################################################
###############################################################################################################
###########################################################################




@karya_bp.route('/homespeaker')
def homespeaker():
   
    # formremaingkaryaaccesscode = ', '.join([data['lifespeakerid'] for data in remaingkaryaaccesscode])
    # faccsess = formremaingkaryaaccesscode.count() 
    # acc = request.form.get('accessid') 
    # print("fname", acc)
    speaker_data_accesscode = []
    speaker_data_name = []
    speaker_data_age = []
    speaker_data_gender = []
    mongodb_info = mongo.db.accesscodedetails
    # print(mongodb_info)
    
    #accesscode
    karyaaccesscode = mongodb_info.find({"isActive":1},{"lifespeakerid":1,"current.speakerMetadata.name" :1,"_id" :0})
    for data in karyaaccesscode:   
        codes = data["lifespeakerid"]
        nameInForm = data["current"]["speakerMetadata"]["name"] 
######################################################################################
        # renameInForm = nameInForm.replace(" ","")
        # lowerRenameInForm = renameInForm.lower()
        # renameCode ="_".join([lowerRenameInForm,codes])
        # print("line 5670", renameCode)  
########################################################################################

        speaker_data_accesscode.append(data)
        
        # speaker_data_accesscode.append(data["lifespeakerid"])
    print(speaker_data_accesscode)

    #name
    # ["karya_info"]["current"]["speaker_info"]["speakerMetadata"]["name"]
    # {
    #                     "lifespeakerid": code, "karyaspeakerid": code,
    #                     "karya_info":{"username": "", "projectname": ""}, 
    #                     "current": {"speakerMetadata": {"name": "", "agegroup": "", "gender": "", 
    #                                             "educationlevel": "", "educationmediumupto12": "", 
    #                                             "educationmediumafter12": "", "speakerspeaklanguage" :"", 
    #                                             "recordingplace": "", "typeofrecordingplace" : "", 
    #                                             "activeAccessCode": ""}, "current_date":current_dt},
    #                     "previous": {"speakerMetadata": {"name": "", "agegroup": "", "gender": "", 
    #                                             "educationlevel": "", "educationmediumupto12": "", 
    #                                             "educationmediumafter12": "", "speakerspeaklanguage" :"", 
    #                                             "recordingplace": "", "typeofrecordingplace" : "", 
    #                                             "activeAccessCode": ""}, "previous_date":current_dt},
    #                     "isActive": 0}
   
   
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
    data_table = [[speaker_data_accesscode[i], speaker_data_name[i], speaker_data_age[i], speaker_data_gender[i]] for i in range(0, len(speaker_data_accesscode))]
    
    print(data_table)
    # for i in range(0, len(speaker_data_accesscode)):
 
 

    # print("this list\n",list(table_data))
    # for speaker_data in speaker_data:
    #     data = speaker_data
    return render_template('homespeaker.html', data = data_table)


#######################################################################################
#####################################################################################################################
#######################################################################################



# Add User 

@karya_bp.route('/add', methods=['GET', 'POST'])
def add():
    print ('Adding speaker info into server')
    mongodb_info = mongo.db.accesscodedetails
    
    accesscodedetails, = getdbcollections.getdbcollections(mongo, "accesscodedetails")

    remaingkaryaaccesscode = mongodb_info.find({"isActive":0},{"lifespeakerid":1, "_id" :0})

    # formremaingkaryaaccesscode = ', '.join([data['lifespeakerid'] for data in remaingkaryaaccesscode])
    # faccsess = formremaingkaryaaccesscode.count() 
    # print("################################################################\n",faccsess,"\n###############################################\n\n\n\n")

    # print(str(op))
    # values = list(all_values(remaingkaryaaccesscode) )
    # print(values)

    # mongodb_info.update_one(
    #                                 { "lifespeakerid" : "678" },
    #                                 {
    #                                     "$set": { "current.speakerMetadata.name": "$previous.speakerMetadata.name"},
    #                                 })

    
########################################################################################
    
    # jp = karyaaccesscode["lifespeakerid"]
    print ('Request method', request.method)
 #######################################################################################
 # ###################### ################# ##########################################   
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
  
    # speaker_data = [speaker_data_accesscode, speaker_data_name, speaker_data_age, speaker_data_gender]
    # table_data = [[speaker_data_accesscode[i], speaker_data_name[i], speaker_data_age[i], speaker_data_gender[i]] for i in range(0, len(speaker_data_accesscode))]
    # print("this list\n",list(table_data)) 
###########################################################
######################################################
#######################################################
    # data = table_data, speaker_data_accesscode= speaker_data_accesscode, speaker_data_name = speaker_data_name, 
    #                                                     speaker_data_age =speaker_data_age, speaker_data_gender=speaker_data_gender) 

    
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

        update_data = {"current.speakerMetadata.name": fname, 
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
            karyaaccesscode = mongodb_info.find_one({"isActive":0},{"lifespeakerid":1, "_id" :0})
            if karyaaccesscode != None:
                accesscode = karyaaccesscode['lifespeakerid']
            else:
                accesscode = ''
                print ('Karya access code', accesscode)
            
                print ('445 Update Data', update_data)
            mongodb_info.update_one({"lifespeakerid": accesscode}, {"$set": update_data})
        else:
            previous_speakerdetails = mongodb_info.find_one({"lifespeakerid": accesscode},
                                                {"current.speakerMetadata": 1, "_id": 0,})

            ###########################################
            ## TOdo: Add date to the previous metadata
            ###########################################


            # the document's content will change to this:
            # new_val = {"some text": "ObjectRocket: Database Management and Hosting"}

            # pass the 'new_val' obj to the method call
            
            date_of_modified = str(datetime.now()).replace(".", ":" )

            # update_date = mongodb_info.insert(current_date)

            
            # previous_update_data = {"previous.current_date."+current_date+".name": previous_speakerdetails["current.speakerMetadata.name"], 
            #                                         "previous."+current_date+".speakerMetadata.agegroup": previous_speakerdetails["current.speakerMetadata.agegroup"], 
            #                                         "previous."+current_date+".speakerMetadata.gender": previous_speakerdetails["current.speakerMetadata.gender"],
            #                                         "previous."+current_date+".speakerMetadata.educationlevel": previous_speakerdetails["current.speakerMetadata.educationlevel"],
            #                                         "previous."+current_date+".speakerMetadata.educationmediumupto12": previous_speakerdetails["current.speakerMetadata.educationmediumupto12"],
            #                                         "previous."+current_date+".speakerMetadata.educationmediumafter12": previous_speakerdetails["current.speakerMetadata.educationmediumafter12"],
            #                                         "previous."+current_date+".speakerMetadata.speakerspeaklanguage": previous_speakerdetails["current.speakerMetadata.speakerspeaklanguage"],
            #                                         "previous."+current_date+".speakerMetadata.recordingplace": previous_speakerdetails["current.speakerMetadata.recordingplace"],
            #                                         "isActive": 1}
            update_old_data = {"previous."+date_of_modified+".speakerMetadata.name": previous_speakerdetails["current"]["speakerMetadata"]["name"], 
                                                    "previous."+date_of_modified+".speakerMetadata.agegroup": previous_speakerdetails["current"]["speakerMetadata"]["agegroup"], 
                                                    "previous."+date_of_modified+".speakerMetadata.gender": previous_speakerdetails["current"]["speakerMetadata"]["gender"],
                                                    "previous."+date_of_modified+".speakerMetadata.educationlevel": previous_speakerdetails["current"]["speakerMetadata"]["educationlevel"],
                                                    "previous."+date_of_modified+".speakerMetadata.educationmediumupto12": previous_speakerdetails["current"]["speakerMetadata"]["educationmediumupto12"],
                                                    "previous."+date_of_modified+".speakerMetadata.educationmediumafter12": previous_speakerdetails["current"]["speakerMetadata"]["educationmediumafter12"],
                                                    "previous."+date_of_modified+".speakerMetadata.speakerspeaklanguage": previous_speakerdetails["current"]["speakerMetadata"]["speakerspeaklanguage"],
                                                    "previous."+date_of_modified+".speakerMetadata.recordingplace": previous_speakerdetails["current"]["speakerMetadata"]["recordingplace"]
                                                    }

            # update_old_data = {"previous.speakerMetadata": previous_speakerdetails["current"]["speakerMetadata"]}
        
            # mongodb_info.find().forEach(function(x){db.getSiblingDB['previous']['current'].insert(x);});     
            # mongodb_info.find().forEach(function(result) 
            #                         { 
            #                         db.<collectionName>.update({"_id" : result._id}, {$set : {"slug_url" : result.name}}); 
            #                         })   
            # # mongodb_info.update_one(
            #                         { "lifespeakerid" : "678" },
            #                         [{
            #                             "$set": { "current.speakerMetadata.name": "previous.speakerMetadata.$name"},
            #                         }])
            
                               
            mongodb_info.update_one({"lifespeakerid": accesscode}, {"$set": update_old_data}) # Edit_old_user_info
            mongodb_info.update_one({"lifespeakerid": accesscode}, {"$set": update_data}) #new_user_info

        # acode = request.form.get('accode')

        
        # print("\n#################################\n ", toc)

        # {
    #                     "lifespeakerid": code, "karyaspeakerid": code,
    #                     "karya_info":{"username": "", "projectname": ""}, 
    #                     "current": {"speakerMetadata": {"name": "", "agegroup": "", "gender": "", 
    #                                             "educationlevel": "", "educationmediumupto12": "", 
    #                                             "educationmediumafter12": "", "speakerspeaklanguage" :"", 
    #                                             "recordingplace": "", "typeofrecordingplace" : "", 
    #                                             "activeAccessCode": ""}, "current_date":current_dt},
    #                     "previous": {"speakerMetadata": {"name": "", "agegroup": "", "gender": "", 
    #                                             "educationlevel": "", "educationmediumupto12": "", 
    #                                             "educationmediumafter12": "", "speakerspeaklanguage" :"", 
    #                                             "recordingplace": "", "typeofrecordingplace" : "", 
    #                                             "activeAccessCode": ""}, "previous_date":current_dt},
    #                     "isActive": 0}
   
        # print("line 444 name ==", fname)
        

        # msg = "Your access code is {} ".format(accesscode)
        # print(msg)
        # # print(accesscode)
        # flash(msg)
    return redirect(url_for('karya_bp.homespeaker'))
    
######################################################################################
##############################################################################################################################
######################################################################################


# # edit user data 
@karya_bp.route('/getonespeakerdetails', methods=['GET', 'POST'])
def getonespeakerdetails():
    accesscodedetails, = getdbcollections.getdbcollections(mongo, "accesscodedetails")
    
    # data through ajax
    asycaccesscode = request.args.get('asycaccesscode')
    print(f"{'='*80}\nasycaccesscode: {asycaccesscode}\n{'='*80}")
    speakerdetails = accesscodedetails.find_one({"lifespeakerid": asycaccesscode},
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







# @karya_bp.route('/edit_form/,edit_id>/edit', methods=['GET', 'POST'])
# def edit_form(edit_id):
#     mongodb_info = mongo.db.accesscodedetails
#     karyaaccesscode = mongodb_info.find_one({"lifespeakerid":"{{row[0]}}"},{"_id" :0})
#     comment = edit_button_id.query.get("row[0]")
#     accesscode = request.form.get('aceescode_bp')



@karya_bp.route('/edituserdetails', methods=['GET', 'POST'])
def edituserdetails():
    mongodb_info = mongo.db.accesscodedetails
    karyaaccesscode = mongodb_info.find_one({"isActive":0},{"accesscode":1, "_id" :0})
    #print("thissss isss ############################# \n \n",type(karyaaccesscode))

    if request.method =='POST':
        # accesscode = request.form.get('accesscode')
        # fname = request.form.get('sname')
        # fage = request.form.get('sage')
        # fgender = request.form.get('sgender')
        # mongodb_info = mongo.db.accesscodedetails

        fname = request.form.get('sname') 
        fage = request.form.get('sagegroup')
        fgender = request.form.get('sgender')
        educlvl = request.form.get('educationalevel')
        moe12 = request.form.getlist('moe12')
        moea12 = request.form.getlist('moea12')
        sols = request.form.getlist('sols')
        por = request.form.get('por')
        toc = request.form.get('toc')
        # print("\n####################)
        mongodb_info = mongo.db.accesscodedetails
        edit_data = {"current.speakerMetadata.name": fname, 
                                                    "current.speakerMetadata.agegroup": fage, 
                                                    "current.speakerMetadata.gender": fgender,
                                                    "current.speakerMetadata.educationlevel": educlvl,
                                                    "current.speakerMetadata.educationmediumupto12": moe12,
                                                    "current.speakerMetadata.educationmediumafter12": moea12,
                                                    "current.speakerMetadata.speakerspeaklanguage": sols,
                                                    "current.speakerMetadata.recordingplace": por,
                                                    "current.speakerMetadata.typeofrecordingplace": toc
                                                    }

        mongodb_info.update_one({"accesscode": accesscode}, 
                                                {"$set": edit_data})
                                                


        return redirect(url_for('karya_bp.home_insert'))
    #rendring to main page
    return render_template("edituserdetails.html", code = karyaaccesscode)







from pymongo import MongoClient
import ast
@karya_bp.route('/assignaccesscodeform' , methods=['GET', 'POST'])
def assignaccesscodeform():
    #create new collection
    accesscodedetail, = getdbcollections.getdbcollections(mongo, 'accesscodedetail')
    #accesscodedetail = mongo.db.accesscodedetail              # collection of users and their respective projectlist
    if request.method == "POST":
        #creating form input data value as dictionary
        speakerData = dict(request.form.lists())
        #print(speakerData)
        #seprating key and value into list
        keys = []
        values = []
        for i in speakerData:
            keys.append(i)
            values.append(speakerData[i])
        #replacing array with string into a new list    
        new_values_type = [''.join(ele) for ele in values] 
        #creating new dictionary
        new_from_of_data = {}
        for key in keys:
            for value in new_values_type:
                new_from_of_data[key] = value
                new_values_type.remove(value)
                break 
        #print(str(new_from_of_data)) 
        # printing keys and values separately
        '''convert dictionary to string to change the data format i.e creating nested dictionary'''    
        speakerData_to_string = str(new_from_of_data)
        speakerData_new_string = speakerData_to_string.replace('\'speakerName\'', '\'speakerMetadata\': {\'speakerName\'').replace(', \'isactive\'', '}, \'isactive\'')
        result = ast.literal_eval(speakerData_new_string)
        
        #print(result)
        #join access code with data 

        #putting data into mongodb data base
        accesscodedetail.insert(result)
        
 
        #datafromdb = accesscodedetail.find()
        datafromdb = accesscodedetail.find({},{"_id" :0})
        # print(list(datafromdb))
        flash('Successfully added new lexeme')
        #return new url/page
        return redirect(url_for('karya_bp.accesscodemainpage'))
    #rendring to main page
    return render_template("assignaccesscodeform.html")




        # add_one_user_metadata = mongodb_info.find_one_and_update_one({"accesscode": access}, 
        #         {"$set": {"karya_info.previous.speaker_info.speakerMetadata.name": fname, 
        #             "karya_info.previous.speaker_info.speakerMetadata.age": fage, 
        #                 "karya_info.previous.speaker_info.speakerMetadata.gender": fgender},
        #                     "$currentDate": {"lastModified": True}})








#######################################################
######################################################
########################################################
