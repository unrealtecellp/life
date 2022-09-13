from curses import meta
from xml.sax.handler import feature_namespace_prefixes
from flask import Blueprint, flash, redirect, render_template, url_for, request, json, jsonify, send_file
from pymongo import database
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash
# from karya_plugin import karya_plugin, mongo
# from karya_plugin.forms import UserLoginForm, RegistrationForm
# from karya_plugin.models import UserLogin
from app import app, mongo
from app.controller import getdbcollections
# from app.forms import UserLoginForm, RegistrationForm
# from app.models import UserLogin
import pandas as pd
from flask_login import current_user, login_user, logout_user, login_required
from io import StringIO
import re
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

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
        speakermeta  = {"speakerMetadata": {"name": "", "agegroup": "", "gender": "", 
                                                "educationlevel": "", "medium-of-education-upto-12th": "", 
                                                "medium-of-education-after-12th": "", "other-languages-speaker-could-speak" :"", 
                                                "place-of-recording": "", "type-of-place" : "", 
                                                "activeAccessCode": ""}}



        karyaaccesscodecollection = {}
        f = request.files['accesscodefile']
        print(f)
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
               
                insert_dict = {
                        "lifespeakerid": code, "karyaspeakerid": code,
                        "karya_info":{
                            "username": "",
                            "project/language name": "",
                            "current": {"speaker_info": speakermeta, "current_date":current_dt},
                            "previous": {"speaker_info": speakermeta, "previous_date":current_dt}   
                        },
                        "isActive": 0
                        
                    }

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


@karya_bp.route('/homespeaker')
def homespeaker():
   
    # formremaingkaryaaccesscode = ', '.join([data['lifespeakerid'] for data in remaingkaryaaccesscode])
    # faccsess = formremaingkaryaaccesscode.count() 
    acc = request.form.get('accessid') 
    print("fname", acc)
    speaker_data_accesscode = []
    speaker_data_name = []
    speaker_data_age = []
    speaker_data_gender = []
    mongodb_info = mongo.db.accesscodedetails
    # print(mongodb_info)
    
    #accesscode
    karyaaccesscode = mongodb_info.find({"isActive":1},{"lifespeakerid":1,"_id" :0})
    for data in karyaaccesscode:                                     
        speaker_data_accesscode.append(data)
        # speaker_data_accesscode.append(data["lifespeakerid"])
    print(speaker_data_accesscode)

    #name
    # ["karya_info"]["current"]["speaker_info"]["speakerMetadata"]["name"]
   
   
    name = mongodb_info.find({"isActive":1},{"karya_info.current.speaker_info.speakerMetadata.name" :1,"_id" :0})
    for data in name:
        # speaker_name = data["karya_info"]["current"]["speaker_info"]["speakerMetadata"]["name"]  
        speaker_name = data["karya_info"]["current"]["speaker_info"]["speakerMetadata"]                                    
        speaker_data_name.append(speaker_name)
    print(speaker_data_name)

    #age
    age = mongodb_info.find({"isActive":1},{"karya_info.current.speaker_info.speakerMetadata.agegroup":1,"_id" :0})
    for data in age:   
        # speaker_age = data["karya_info"]["current"]["speaker_info"]["speakerMetadata"]["agegroup"]
        speaker_age = data["karya_info"]["current"]["speaker_info"]["speakerMetadata"]                                    
        speaker_data_age.append(speaker_age)
    print(speaker_data_age)    

    #gender
    gender = mongodb_info.find({"isActive":1},{"karya_info.current.speaker_info.speakerMetadata.gender":1,"_id" :0})
    for data in gender:
        # speaker_gender = data["karya_info"]["current"]["speaker_info"]["speakerMetadata"]["gender"] 
        speaker_gender = data["karya_info"]["current"]["speaker_info"]["speakerMetadata"]                                    
        speaker_data_gender.append(speaker_gender)
    print(speaker_data_gender)                                  
  
    # speaker_data = [speaker_data_accesscode, speaker_data_name, speaker_data_age, speaker_data_gender]
    table_data = [[speaker_data_accesscode[i], speaker_data_name[i], speaker_data_age[i], speaker_data_gender[i]] for i in range(0, len(speaker_data_accesscode))]
    
    accessbycode = request.form.get('accessid') 
    print("hello, ", accessbycode)
    # print("this list\n",list(table_data))
    # for speaker_data in speaker_data:
    #     data = speaker_data
    return render_template('homespeaker.html', data = table_data )






# Add User 

@karya_bp.route('/add', methods=['GET', 'POST'])
def add():
    print ('Adding speaker info into server')
    mongodb_info = mongo.db.accesscodedetails
    remaingkaryaaccesscode = mongodb_info.find({"isActive":0},{"lifespeakerid":1, "_id" :0})

    # formremaingkaryaaccesscode = ', '.join([data['lifespeakerid'] for data in remaingkaryaaccesscode])
    # faccsess = formremaingkaryaaccesscode.count() 
    # print("################################################################\n",faccsess,"\n###############################################\n\n\n\n")

    # print(str(op))
    # values = list(all_values(remaingkaryaaccesscode) )
    # print(values)
########################################################################################
    karyaaccesscode = mongodb_info.find_one({"isActive":0},{"lifespeakerid":1, "_id" :0})
    if karyaaccesscode != None:
        accesscode = karyaaccesscode['lifespeakerid']
    else:
        accesscode = ''
    print ('Karya access code', accesscode)

    
    # jp = karyaaccesscode["lifespeakerid"]
    print ('Request method', request.method)
 #######################################################################################
 # ###################### ################# ##########################################   
    speaker_data_accesscode = []
    speaker_data_name = []
    speaker_data_age = []
    speaker_data_gender = []
    mongodb_info = mongo.db.accesscodedetails
    name = mongodb_info.find({"isActive":1},{"karya_info.current.speaker_info.speakerMetadata.name" :1,"_id" :0})
    for data in name:
        speaker_name = data["karya_info"]["current"]["speaker_info"]["speakerMetadata"]["name"]                                     
        speaker_data_name.append(speaker_name)
    print(speaker_data_name)
    #age
    age = mongodb_info.find({"isActive":1},{"karya_info.current.speaker_info.speakerMetadata.agegroup":1,"_id" :0})
    for data in age:   
        speaker_age = data["karya_info"]["current"]["speaker_info"]["speakerMetadata"]["agegroup"]                                    
        speaker_data_age.append(speaker_age)
    print(speaker_data_age)    

    #gender
    gender = mongodb_info.find({"isActive":1},{"karya_info.current.speaker_info.speakerMetadata.gender":1,"_id" :0})
    for data in gender:
        speaker_gender = data["karya_info"]["current"]["speaker_info"]["speakerMetadata"]["gender"]                                     
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
    

    if request.method =='POST' and accesscode != '':
        # accesscode = request.form.get('accesscode')
        #remaingkaryaaccesscode = request.form.get('remaingkaryaaccesscode')
        # print("####################################################### \n",remaingkaryaaccesscode, "\n##########################################")
        fname = request.form.get('sname') 
        fage = request.form.get('sagegroup')
        fgender = request.form.get('sgender')
        educlvl = request.form.get('educationalevel')
        moe12 = request.form.getlist('moe12')
        moea12 = request.form.getlist('moea12')
        sols = request.form.getlist('sols')
        por = request.form.get('por')
        toc = request.form.get('toc')
        # print("\n#################################\n ", toc)
      
        update_data = {"karya_info.current.speaker_info.speakerMetadata.name": fname, 
                                                    "karya_info.current.speaker_info.speakerMetadata.agegroup": fage, 
                                                    "karya_info.current.speaker_info.speakerMetadata.gender": fgender,
                                                    "karya_info.current.speaker_info.speakerMetadata.educationlevel": educlvl,
                                                    "karya_info.current.speaker_info.speakerMetadata.medium-of-education-upto-12th": moe12,
                                                    "karya_info.current.speaker_info.speakerMetadata.medium-of-education-after-12th": moea12,
                                                    "karya_info.current.speaker_info.speakerMetadata.other-languages-speaker-could-speak": sols,
                                                    "karya_info.current.speaker_info.speakerMetadata.place-of-recording": por,
                                                    "karya_info.current.speaker_info.speakerMetadata.type-of-place": toc,
                                                    "isActive": 1}
        print ('Update Data', update_data)
        mongodb_info.update_one({"lifespeakerid": accesscode}, {"$set": update_data})

        # msg = "Your access code is {} ".format(accesscode)
        # print(msg)
        # # print(accesscode)
        # flash(msg)
    return redirect(url_for('karya_bp.homespeaker'))
    



# # edit user data 
@karya_bp.route('/getonespeakerdetails', methods=['GET', 'POST'])
def getonespeakerdetails():
    accesscodedetails, = getdbcollections.getdbcollections(mongo, "accesscodedetails")
    
    # data through ajax
    asycaccesscode = request.args.get('asycaccesscode')
    print(f"{'='*80}\nasycaccesscode: {asycaccesscode}\n{'='*80}")
    speakerdetails = accesscodedetails.find_one({"lifespeakerid": asycaccesscode},
                                                {"_id": 0,
                                                "karya_info.current.speaker_info.speakerMetadata": 1})
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


    return jsonify(speakerdetails=speakerdetails)







# @karya_bp.route('/edit_form/,edit_id>/edit', methods=['GET', 'POST'])
# def edit_form(edit_id):
#     mongodb_info = mongo.db.accesscodedetails
#     karyaaccesscode = mongodb_info.find_one({"lifespeakerid":"{{row[0]}}"},{"_id" :0})
#     comment = edit_button_id.query.get("row[0]")
#     accesscode = request.form.get('aceescode_bp')



# @karya_bp.route('/edituserdetails', methods=['GET', 'POST'])
# def edituserdetails():
#     mongodb_info = mongo.db.accesscodedetails
#     karyaaccesscode = mongodb_info.find_one({"isActive":0},{"accesscode":1, "_id" :0})
#     #print("thissss isss ############################# \n \n",type(karyaaccesscode))

#     if request.method =='POST':
#         accesscode = request.form.get('accesscode')
#         fname = request.form.get('sname')
#         fage = request.form.get('sage')
#         fgender = request.form.get('sgender')
#         mongodb_info = mongo.db.accesscodedetails



#         mongodb_info.update_one({"accesscode": accesscode}, 
#                                                 {"$set": {"trap": {"name":fname, 
#                                                     "age": fage, 
#                                                         "gender": fgender}}})
                                                


#         return redirect(url_for('karya_bp.home_insert'))
#     #rendring to main page
#     return render_template("edituserdetails.html", code = karyaaccesscode)







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
