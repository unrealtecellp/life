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
    
    speaker_data_accesscode = []
    speaker_data_name = []
    speaker_data_age = []
    speaker_data_gender = []
    mongodb_info = mongo.db.accesscodedetails
    # print(mongodb_info)

    #accesscode
    karyaaccesscode = mongodb_info.find({"isActive":1},{"lifespeakerid":1,"_id" :0})
    for data in karyaaccesscode:                                     
        speaker_data_accesscode.append(data["lifespeakerid"])
    print(speaker_data_accesscode)

    #name
    # ["karya_info"]["current"]["speaker_info"]["speakerMetadata"]["name"]
   
   
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
    table_data = [[speaker_data_accesscode[i], speaker_data_name[i], speaker_data_age[i], speaker_data_gender[i]] for i in range(0, len(speaker_data_accesscode))]
    print("this list\n",list(table_data))
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
    #rendring to main page
    # return render_template('homespeaker.html')
    # return render_template("homespeaker" , code = karyaaccesscode, remaingkaryaaccesscode = remaingkaryaaccesscode.count())


# @karya_bp.route('/viewoneuserdetail', methods=['GET', 'POST'])
# def viewoneuserdetail():
#     speaker_data_accesscode = []
#     speaker_data_name = []
#     speaker_data_age = []
#     speaker_data_gender = []
#     mongodb_info = mongo.db.accesscodedetails
#     # print(mongodb_info)

#     #accesscode
#     karyaaccesscode = mongodb_info.find_one({"isActive":1},{"lifespeakerid":1,"_id" :0})
#     # for data in karyaaccesscode:                                     
#     #     speaker_data_accesscode.append(data["lifespeakerid"])
#     # print(speaker_data_accesscode)

#     #name
#     # ["karya_info"]["current"]["speaker_info"]["speakerMetadata"]["name"]
   
#     name = mongodb_info.find_one({"isActive":1},{"karya_info.current.speaker_info.speakerMetadata.name" :1,"_id" :0})
#     for data in name:
#         speaker_name = data["karya_info"]["current"]["speaker_info"]["speakerMetadata"]["name"]                                     
#         speaker_data_name.append(speaker_name)
#     print(speaker_data_name)
#     #age
#     age = mongodb_info.find_one({"isActive":1},{"karya_info.current.speaker_info.speakerMetadata.agegroup":1,"_id" :0})
#     for data in age:   
#         speaker_age = data["karya_info"]["current"]["speaker_info"]["speakerMetadata"]["agegroup"]                                    
#         speaker_data_age.append(speaker_age)
#     print(speaker_data_age)    

#     #gender
#     gender = mongodb_info.find_one({"isActive":1},{"karya_info.current.speaker_info.speakerMetadata.gender":1,"_id" :0})
#     for data in gender:
#         speaker_gender = data["karya_info"]["current"]["speaker_info"]["speakerMetadata"]["gender"]                                     
#         speaker_data_gender.append(speaker_gender)
#     print(speaker_data_gender)                                  
  
#     # speaker_data = [speaker_data_accesscode, speaker_data_name, speaker_data_age, speaker_data_gender]
#     table_data = [[speaker_data_accesscode[i], speaker_data_name[i], speaker_data_age[i], speaker_data_gender[i]] for i in range(0, len(speaker_data_accesscode))]

#     # for speaker_data in speaker_data:
#     #     data = speaker_data
#     return redirect(url_for('karya_bp.homespeaker'))

# @karya_bp.route('/extend_assignakaryaccesscode', methods=['GET', 'POST'])
# def extend_assignakaryaccesscode():
#     # mongodb_info = mongo.db.accesscodedetails

#     # karyaaccesscode = mongodb_info.find_one({"isActive":0},{"lifespeakerid":1, "_id" :0})
    
#     # print("thissss isss ############################# \n \n", karyaaccesscode)

#     # if request.method =='POST':
#     #     accesscode = request.form.get('accesscode')
#     #     mongodb_info = mongo.db.accesscodedetails
#     #     accesscode = request.form.get('accesscode')
        
#         # return redirect(url_for('karya_bp.home_insert'))
#     #rendring to main page
#     return render_template("extend_assignakaryaccesscode.html")














# edit user data 

@karya_bp.route('/edituserdetails', methods=['GET', 'POST'])
def edituserdetails():
    mongodb_info = mongo.db.accesscodedetails
    karyaaccesscode = mongodb_info.find_one({"isActive":0},{"accesscode":1, "_id" :0})
    #print("thissss isss ############################# \n \n",type(karyaaccesscode))

    if request.method =='POST':
        accesscode = request.form.get('accesscode')
        fname = request.form.get('sname')
        fage = request.form.get('sage')
        fgender = request.form.get('sgender')
        mongodb_info = mongo.db.accesscodedetails



        mongodb_info.update_one({"accesscode": accesscode}, 
                                                {"$set": {"trap": {"name":fname, 
                                                    "age": fage, 
                                                        "gender": fgender}}})
                                                


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

# @karya_bp.route('/add', methods=['GET', 'POST'])
# def add():
#     mongodb_info = mongo.db.accesscodedetails
#     accesscode_code = mongodb_info['accesscode']
#     # print("this \n \n \n  ", mongodb_info)
#     # taking info from form
    
#     # putting form data into mongodb

#     accesscode = mongodb_info.find({},{"accesscode":1, "_id" :0})
#     # print("this accesscode: \n", list(accesscode))

#     uname = mongodb_info.find({}, {"karya_info.previous.speaker_info.speakerMetadata.name": 1, "_id" :0})
#     # print("this accesscode: \n", list(uname))
#     uage = mongodb_info.find({}, {"karya_info.previous.speaker_info.speakerMetadata.age": 1, "_id" :0})
#     ugender = mongodb_info.find({}, {"karya_info.previous.speaker_info.speakerMetadata.gender": 1, "_id" :0})
    
#     # print("this is active code status \n", list(isactive))

#     #calling data on the bassis of accesscode and active status
#     # isactive = mongodb_info.find({}, {"accesscode":1, "karya_info.isActive": 1, "_id" :0})
#     # list_search = list(isactive) # converting mongodb data stored in varibale "isactive" to the list 
#     # res = None #empty dictionary
#     # for sub in list_search: #loop the data to search one by one 
#     #     if sub['karya_info']['isActive'] == 0: #find this condtion in the loop
#     #         res = sub # if condtion get satisfied put it into empty dictionary 
#     #         break # if condtion matched break the loop/ stop the loop
#     # print("\n ################# \n The filtered dictionary value is : " + str(res)+ "\n######################## \n ")


#     isactive = mongodb_info.find({}, { "_id" :0})
#     list_search = list(isactive) # converting mongodb data stored in varibale "isactive" to the list 
#     res = None #empty dictionary
#     for sub in list_search: #loop the data to search one by one 
#         if sub['karya_info']['isActive'] == 0: #find this condtion in the loop
#             res = sub # if condtion get satisfied put it into empty dictionary 
#             break # if condtion matched break the loop/ stop the loop
#     print("\n ################# \n The filtered dictionary value is : " + str(res)+ "\n######################## \n ")

#     # for inactive in isactive:
#     #     if inactive == 0:
#     #         print("this is access code allot to user \n", list("accesscode"))
#     #         break
#     #aj = name, age, gender
#     if request.method =='POST':
#         fname = request.form.get('sname')
#         fage = request.form.get('sage')
#         fgender = request.form.get('sgender')
#         # add_user = getdbcollections.getdbcollections(mongo, 'accesscodedetail')

#         add_one_user_metadata = mongodb_info.find_one_and_update_one({"accesscode": access}, 
#                 {"$set": {"karya_info.previous.speaker_info.speakerMetadata.name": fname, 
#                     "karya_info.previous.speaker_info.speakerMetadata.age": fage, 
#                         "karya_info.previous.speaker_info.speakerMetadata.gender": fgender},
#                             "$currentDate": {"lastModified": True}})
#                 # return f"User added \n", add_one_user_metadata.json_dump()
#                 # return add
                
#         return redirect(url_for('karya_bp.home_insert'))
#         return render_template("add.html")
                          
#             # else:
#             #     # return f"All access codes are alloted. Please contact to your PI." 
                
            




# @karya_bp.route('/update_user_try', methods=['GET', 'POST'])
# def update_user_try():
#     uname = getdbcollections.getdbcollections.accesscodedetails.find_one({"sname": uname}, {"_id" :0})
#     uage = getdbcollections.getdbcollections.accesscodedetails.find_one({"sage": uage}, {"_id" :0})
#     ugender = getdbcollections.getdbcollections.accesscodedetails.find_one({"sgender": ugender}, {"_id" :0})
#     aj = name, age, gender
#     if request.method =='POST':
#         add_user = getdbcollections.getdbcollections(mongo, 'accesscodedetail')
#         add_all_user_metadata = add_user.update_one({"accesscode":accesscode}, 
#                                                         {"$set": {"current.name": "uname",
#                                                             "previous.age": "uage", 
#                                                                 "previous.gender": "ugender"},
#                                                                     "$currentDate": {"lastModified": True}})


# @karya_bp.route('/user_table_details', methods = ['Get', 'POST'])                                                                   
# def user_table_details():





# @karya_bp.route('/updatekayrauserdetail' , methods=['POST'])
# def updatekaryauserdetail():
#     accesscode = request.form['accesscode']
#     name = request.form['name']
#     age = request.form['age']
#     gender = request.form['gender']
#     activeaccesscode = request.form['activeAccesscode']
#     user_detail = getdbcollections.getdbcollections.accesscodedetail.objects(id= accesscode).first()
#     if not user_detail:
#         return json.dumps({'error':'data not found'})
#     else:
#         if name == 'name':
#             user_detail.update(name = name)
#         elif age == 'age':
#             user_detail.update(age = age)
#         elif gender == 'gneder':
#             user_detail.update(gender = gender)
#     return json.dumps({'status':'OK'})






# @karya_bp.route('/edit_jam/<jam_id>', methods=['POST', 'GET'])
# def edit_userdetail("accesscode"):
#     user_logged_in = 'username' in session
#     the_jam =  mongo.db.accesscodedetails.find_one({"accesscode": ObjectId(jam_id)})
#     username=session['username']

#     if request.method == 'POST':
#         if user_logged_in:
#             jams = mongo.db.jam_or_event
#             jams.update( {'_id': ObjectId(jam_id)},
#             {
#                 'jam_title':request.form.get('jam_title'),
#                 'genre':request.form.get('genre'),
#                 'date_of_jam': request.form.get('date_of_jam'),
#                 'jam_location': request.form.get('jam_location'),
#                 'jam_county':request.form.get('jam_county'),
#                 'jam_member_1':request.form.get('jam_member_1'),
#                 'member_instrument_1':request.form.get('member_instrument_1'),
#                 'jam_notes':request.form.get('jam_notes'),
#             })
#             return redirect(url_for('get_jams'))
#     return render_template('editjam.html',
#         jam=the_jam,
#         instruments=mongo.db.instruments.find(),
#         counties=mongo.db.counties.find(),
#         username=session['username'])






# # karya access code assignment route
# @karya_bp.route('/assignkaryaaccesscode', methods=['GET', 'POST'])
# @login_required
# def assignkaryaaccesscode():
#     print(f"IN KARYA ACCESS CODE ASSIGNMENT FUNCTION")
#     return redirect(url_for('home_insert'))






# @karya_bp.route('/try')
# def tryy():
#     data_info = getdbcollections.getdbcollections(mongo, 'accesscodedetail')
#     name = getdbcollections.getdbcollections.accesscodedetails.find_one({"sname": name}, {"_id" :0})
#     age = getdbcollections.getdbcollections.accesscodedetails.find_one({"sage": age}, {"_id" :0})
#     gender = getdbcollections.getdbcollections.accesscodedetails.find_one({"sgender": gender}, {"_id" :0})
#     aj = name, age, gender
#     print(aj)
#     if request.method == 'post':
#         user_update = getdbcollections.getdbcollections.accesscodedetails
#         user_update.update({"access_code": accesscode}, 
#         {
#             "name" :request.form.get("sname"),
#             "age" :request.form.get("sage"),
#             "gender" :request.form.get("sgender")

#         })
#         return redirect(url_for('karya_bp.home_insert'))
#     return render_template('updatekaryauserdetail.html',
#         user=uname,
#         instruments=getdbcollections.getdbcollections.accesscodedetails.find(),
#         username= accesscode

