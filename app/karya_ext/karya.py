from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
    request,
    jsonify
)
from app import mongo
import pandas as pd
from werkzeug.datastructures import FileStorage
import requests
import gzip
import tarfile
import io
from io import BytesIO
import json
from datetime import datetime
from pprint import pprint
# from pylatex.utils import bold, NoEscape

from flask_login import current_user, login_user, logout_user, login_required
from app.controller import (
    getdbcollections,
    getactiveprojectname,
    getcurrentuserprojects,
    getprojectowner,
    getcurrentusername,
    audiodetails,
    getuserprojectinfo,
    getprojecttype
)
from app.lifeques.controller import (
    getquesfromprompttext,
    savequespromptfile,
    getquesidlistofsavedaudios
)

karya_bp = Blueprint('karya_bp', __name__, template_folder='templates', static_folder='static')

# print('starting...')
'''Home page of karya Extension. This contain  ''' 
@karya_bp.route('/home_insert')
@login_required
def home_insert():
    # print('starting...home')
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
                                                'fetchData': 1},
                                                {'_id': 0,
                                                    'karyaaccesscode': 1,
                                                    'assignedBy': 1,
                                                    'uploadedBy': 1})
                                              
    fetch_access_code_list = []

    for fetch_access_code in fetch_access_codes:
        # print ('Current access code', fetch_access_code)
        if (fetch_access_code['assignedBy'] != ''):
            if (fetch_access_code['assignedBy'] == current_username):
                fetch_access_code_list.append(fetch_access_code['karyaaccesscode'])
            else:
                if (current_username == fetch_access_code['uploadedBy']):
                    fetch_access_code_list.append(fetch_access_code['karyaaccesscode'])
    
    # print ("Access code list for", activeprojectname, current_username, fetch_access_code_list)

    karya_speaker_ids = []

    speaker_ids = accesscodedetails.find({'projectname': activeprojectname,
                                                'fetchData': 0,
                                                'isActive': 1
                                                },
                                                {
                                                    '_id': 0,
                                                    'karyaspeakerid': 1,
                                                    'lifespeakerid': 1
                                                })

    for speakerid in speaker_ids:
        karyaspeakerid = speakerid['karyaspeakerid']
        lifespeakerid = speakerid['lifespeakerid']
        # karya_speaker_ids.append(karyaspeakerid)
        karya_speaker_ids.append({"id": karyaspeakerid, "text": lifespeakerid})


    return render_template("home_insert.html",
                            projectName=activeprojectname,
                            shareinfo=shareinfo,
                            fetchaccesscodelist=fetch_access_code_list,
                            karya_speaker_ids=karya_speaker_ids,
                        )

#############################################################################################################
##############################################################################################################
######################################   Upload Access-Code       ############################################
##############################################################################################################
##############################################################################################################
'''Upload Access Code'''
@karya_bp.route('/uploadfile' , methods=['GET', 'POST'])
@login_required
def uploadfile():
    projects, userprojects, projectsform, karyaaccesscodedetails = getdbcollections.getdbcollections(mongo,
                                                                                                        'projects',
                                                                                                        'userprojects',
                                                                                                        'projectsform',
                                                                                                        'accesscodedetails')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_username,
                                                                                userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
    project_type = getprojecttype.getprojecttype(projects, activeprojectname)

    if (project_type == 'questionnaires'):
        uploadacesscodemetadata = uploadfileforquestionnaire(projectsform, activeprojectname)
    if (project_type == 'transcriptions'):
        uploadacesscodemetadata = uploadfilefortranscription(projects, projectsform, activeprojectname)

    if request.method == "POST":
        access_code_file = request.files['accesscodefile']
        data = pd.read_csv(access_code_file)
        df = pd.DataFrame(data)

        df["id"] = df["id"].str[1:]
        df["access_code"] = df["access_code"].str[1:]
        df["phone_number"] = df["phone_number"].str[1:]
  
        for index,item in df.iterrows(): 
            current_dt = str(datetime.now()).replace('.', ':')
            checkaccesscode = item["access_code"]
            accesscode_exist = karyaaccesscodedetails.find_one(
                                                                {
                                                                    "projectname": activeprojectname,
                                                                    "karyaaccesscode": checkaccesscode
                                                                }
                                                            )
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
                            "isActive": 0,
                            "additionalInfo": {}
                        }
            return_obj = karyaaccesscodedetails.insert_one(insert_dict)
            # datafromdb = karyaaccesscodedetails.find({},{"_id" :0})

        return redirect(url_for('karya_bp.home_insert'))

    return render_template("uploadfile.html",
                            data=currentuserprojectsname,
                            projectName=activeprojectname,
                            uploadacesscodemetadata=uploadacesscodemetadata,
                            projecttype=project_type)

def uploadfilefortranscription(projects, projectsform, project_name):
    langscript = []
    projectform = projectsform.find_one({"projectname" : project_name})
    langscript.append(projectform["Sentence Language"][0])

    derivedFromProject = projects.find_one({"projectname" : project_name},
                                            {"_id": 0, "derivedFromProject": 1})
    derivedFromProjectName = derivedFromProject['derivedFromProject'][0]
    derive_from_project_type = getprojecttype.getprojecttype(projects, derivedFromProjectName)
    if (derive_from_project_type == "questionnaires"):
        derivefromprojectform = projectsform.find_one({"projectname" : derivedFromProjectName})
    
        domain = derivefromprojectform["Domain"][1]
        elicitation = derivefromprojectform["Elicitation Method"][1]

    uploadacesscodemetadata = {
                                "langscript": langscript,
                                "domain": domain,
                                "elicitation": elicitation
                                }

    return uploadacesscodemetadata

def uploadfileforquestionnaire(projectsform, project_name):
    langscript = []
    projectform = projectsform.find_one({"projectname" : project_name})  #domain, elictationmethod ,langscript-[1]
    langscripts = projectform["Prompt Type"][1]
    for lang_script, lang_info in langscripts.items():
        if ('Audio' in lang_info):
            langscript.append(lang_script)
    domain = projectform["Domain"][1]
    elicitation = projectform["Elicitation Method"][1]
    uploadacesscodemetadata = {
                                "langscript": langscript,
                                "domain": domain,
                                "elicitation": elicitation
                                }

    return uploadacesscodemetadata

##############################################################################################################
##############################################################################################################
######################################       Add User         ###############################################
##############################################################################################################
##############################################################################################################
'''Add User'''
@karya_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    # print ('Adding speaker info into server')
    mongodb_info, userprojects = getdbcollections.getdbcollections(mongo,
                                                                    "accesscodedetails",
                                                                    'userprojects')
    current_username = getcurrentusername.getcurrentusername()          
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)

    # speaker_data_accesscode = []
    # speaker_data_name = []
    # speaker_data_age = []
    # speaker_data_gender = []

    # #speaker_name
    # name = mongodb_info.find({ "projectname": activeprojectname, "isActive":1},{"current.workerMetadata.name" :1,"_id" :0})
    # for data in name:
    #     speaker_name = data["current"]["workerMetadata"]["name"]
    #     speaker_data_name.append(speaker_name)

    # #age
    # age = mongodb_info.find({ "projectname": activeprojectname, "isActive":1},{"current.workerMetadata.agegroup":1,"_id" :0})
    # for data in age:   
    #     speaker_age = data["current"]["workerMetadata"]["agegroup"]
    #     speaker_data_age.append(speaker_age)

    # #gender
    # gender = mongodb_info.find({ "projectname": activeprojectname, "isActive":1},{"current.workerMetadata.gender":1,"_id" :0})
    # for data in gender:
    #     speaker_gender = data["current"]["workerMetadata"]["gender"]
    #     speaker_data_gender.append(speaker_gender)

    if request.method =='POST':
        # accesscode = request.form.get('accesscode')
        #remaingkaryaaccesscode = request.form.get('remaingkaryaaccesscode')
        # print("####################################################### \n", "\n##########################################")
        accesscode = request.form.get('accode')
        # print("this acc code at line 428", accesscode)
        fname = request.form.get('sname') 
        fage = request.form.get('sagegroup')
        fgender = request.form.get('sgender')
        educlvl = request.form.get('educationalevel')
        moe12 = request.form.getlist('moe12')
        moea12 = request.form.getlist('moea12')
        sols = request.form.getlist('sols')
        por = request.form.get('por')
        toc = request.form.get('toc')

        # print("Line 354: ,","Name: ", fname, "Age: ",fage, "Gender: ",fgender, "EducationLvl: ",educlvl, "MOE12: ",moe12, "MOEA12: ",moea12, "SOLS: ",sols, "Placeofrecording: ",por, "TOC: ",toc)  
        if accesscode  == '':
            accesscodefor = int(request.form.get('accesscodefor'))
            task = request.form.get('task')
            language = request.form.get('langscript') 
            domain = request.form.getlist('domain')
            elicitationmethod = request.form.getlist("elicitation")
            # print("line 361  => accesscodefor :" , accesscodefor, "Task: ",task, "Lang: ", language, "Domain: ", domain, "ElicMethod: ",elicitationmethod)
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
            # print(test)
            # print(namekaryaID)
            # for lidata in namekaryaID:
            #     print("574 ", lidata)
            if namekaryaID is None: 
                flash("Please Upload New Access Code")
                return redirect(url_for('karya_bp.home_insert'))

            namekaryaIDDOB = fage
            nameInForm = fname 
            if namekaryaIDDOB and nameInForm is not None:  
                
                # print("230 ========================== >>>>>>>>>>>>>>>>>>>>     ",nameInForm , type(nameInForm))

                # print("231 =========================  >>>>>>>>>>>>>>>>>>>>      ", namekaryaIDDOB, type(namekaryaIDDOB))
                # if namekaryaID is not None:
                #     try :
                renameInFormDOB = namekaryaIDDOB.replace("-","")
                # print("227  ==========================================>>>>>>>>>>   ", renameInFormDOB)
                codes = namekaryaID["karyaspeakerid"]
                # print(codes)
                
                renameInForm = nameInForm.replace(" ","")
                lowerRenameInForm = renameInForm.lower()
                renameDOB =  "".join([lowerRenameInForm,renameInFormDOB])
                # print("232 =========================>>>>>>>>>>>>    " , renameDOB)
                renameCode ="_".join([renameDOB,codes])
                # print("line 583", renameCode)  
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
    #########################################################################################################################
    #########################################################################################################################
            accesscode = request.form.get('accode')
            # print("=======================> ",accesscode )
    #########################################################################################################################
    ##########################################################################################################################
            # print ("Data before updating")
            # print ("Karya Access Code", namekaryaID["karyaaccesscode"])
            # print ("Update Data", update_data)
            
            mongodb_info.update_one({"karyaaccesscode": namekaryaID["karyaaccesscode"], "projectname": activeprojectname},
                                    {"$set": update_data}
                                    )
            
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
            previous_speakerdetails = mongodb_info.find_one({"karyaaccesscode": accesscode, "projectname": activeprojectname},
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

            mongodb_info.update_one({"karyaaccesscode": accesscode, "projectname": activeprojectname}, {"$set": update_old_data}) # Edit_old_user_info
            mongodb_info.update_one({"karyaaccesscode": accesscode, "projectname": activeprojectname}, {"$set": update_data}) #new_user_info
    
    return redirect(url_for('karya_bp.homespeaker'))
    # return render_template("homespeaker.html",
                            # projectName=activeprojectname,
                            # uploadacesscodemetadata=uploadacesscodemetadata)

   
##############################################################################################################
##############################################################################################################
######################################      View Table HomeSpeaker         ###################################
##############################################################################################################
##############################################################################################################

'''Table of speaker details'''

@karya_bp.route('/homespeaker')
@login_required
def homespeaker():
    projects, userprojects, projectsform, accesscode_info = getdbcollections.getdbcollections(mongo,
                                                                                            'projects',
                                                                                            'userprojects',
                                                                                            'projectsform',
                                                                                            'accesscodedetails')

    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname = getcurrentuserprojects.getcurrentuserprojects(current_username, userprojects)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
   
    project_type = getprojecttype.getprojecttype(projects, activeprojectname)

    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                        current_username,
                                                        activeprojectname)
    share_level = shareinfo['sharemode']
    if (project_type == 'questionnaires'):
        uploadacesscodemetadata = uploadfileforquestionnaire(projectsform, activeprojectname)
    if (project_type == 'transcriptions'):
        uploadacesscodemetadata = uploadfilefortranscription(projects, projectsform, activeprojectname)

################################## karya accesscode  #########################################################################
    if share_level == 10:
        karyaaccesscodedetails = accesscode_info.find({"isActive":1, "projectname": activeprojectname},
                                                    {
                                                        "karyaaccesscode":1, 
                                                        "lifespeakerid":1,
                                                        "task": 1,
                                                        "fetchData": 1,
                                                        "assignedBy": 1,
                                                        "current.workerMetadata.name" :1,
                                                        "current.workerMetadata.agegroup":1,
                                                        "current.workerMetadata.gender":1,
                                                        "domain": 1,
                                                        "elicitationmethod": 1,
                                                        "_id" :0
                                                    }
                                                )
    else:
        karyaaccesscodedetails = accesscode_info.find({"isActive":1, "projectname": activeprojectname, "assignedBy": current_username},
                                                    {
                                                        "karyaaccesscode":1, 
                                                        "lifespeakerid":1,
                                                        "task": 1,
                                                        "fetchData": 1,
                                                        "assignedBy": 1,
                                                        "current.workerMetadata.name" :1,
                                                        "current.workerMetadata.agegroup":1,
                                                        "current.workerMetadata.gender":1,
                                                        "domain": 1,
                                                        "elicitationmethod": 1,
                                                        "_id" :0
                                                    }
                                                )
    
    data_table = []
    fetch_data = {
        0: "Data Collection Using Karya",
        1: "Syncing Karya Recording with LiFE"
    }
    task = {
        "SPEECH_DATA_COLLECTION": "Recording",
        "SPEECH_VERIFICATION": "Verification of Recordings",
        "SPEECH_TRANSCRIPTION": "Transcription of Recordings"
    }
    for data in karyaaccesscodedetails:
        data['fetchData'] = fetch_data[data['fetchData']]
        data['task'] = task[data['task']]
        data_table.append(data)

    return render_template('homespeaker.html',
                            data=currentuserprojectsname,
                            projectName=activeprojectname,
                            uploadacesscodemetadata = uploadacesscodemetadata,
                            projecttype=project_type,
                            data_table= data_table,
                            count=len(data_table)
                            )


##############################################################################################################
##############################################################################################################
######################################     Get Speaker Details        ########################################
##############################################################################################################
##############################################################################################################
'''Getting user details. '''
@karya_bp.route('/getsharelevel', methods=['GET', 'POST'])
@login_required
def getsharelevel():
    userprojects,  = getdbcollections.getdbcollections(mongo,
                                                        'userprojects')
    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username,
                                                                    userprojects)
    shareinfo = getuserprojectinfo.getuserprojectinfo(userprojects,
                                                        current_username,
                                                        activeprojectname)

    return jsonify(shareinfo=shareinfo)

'''Getting one speaker details form data base.'''
@karya_bp.route('/getonespeakerdetails', methods=['GET', 'POST'])
def getonespeakerdetails():
    accesscodedetails, userprojects = getdbcollections.getdbcollections(mongo, "accesscodedetails", "userprojects")

    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
    
    # data through ajax
    asycaccesscode = request.args.get('asycaccesscode')
    # print(f"{'='*80}\nasycaccesscode: {asycaccesscode}\n{'='*80}")
    speakerdetails = accesscodedetails.find_one({"projectname": activeprojectname, "karyaaccesscode": asycaccesscode},
                                                {"_id": 0,
                                                "current.workerMetadata": 1})
    accesscodetask = accesscodedetails.find_one({"projectname": activeprojectname, "karyaaccesscode": asycaccesscode},
                                                {"_id": 0,
                                                "task": 1})
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
    # print(f"SPEAKER DETAILS: {speakerdetails}")

    # speakerdetails['accesscode'] = asycaccesscode
    speakerdetails.update(accesscodetask)
    return jsonify(speakerdetails=speakerdetails)


##############################################################################################################
##############################################################################################################
######################################   Fetch Audio        ###############################################
##############################################################################################################
##############################################################################################################
'''Getting OTP from karya server to fetch the audio files and audio files.'''
@karya_bp.route('/fetch_karya_otp', methods=['GET', 'POST'])
@login_required
def fetch_karya_otp():
    
    userprojects, mongodb_info = getdbcollections.getdbcollections(mongo,
                                                                    'userprojects',
                                                                    'accesscodedetails')

    current_username = getcurrentusername.getcurrentusername()
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
    mongodb_info = mongo.db.accesscodedetails  
    accesscodedocs = mongodb_info.find({ "projectname": activeprojectname, "isActive":1},
                                        {"karyaaccesscode":1, "_id" :0}) 

    ##Registration
    registeruser_urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/worker/otp/generate'
    access_code = request.args.get("acode")
    phone_number = request.args.get("mob")
    
    for current_acodedoc in accesscodedocs:
        if access_code == current_acodedoc['karyaaccesscode']:
            registeruser_hederr= {'access-code':access_code, 'phone-number':phone_number}
            register_request = requests.put(url = registeruser_urll, headers = registeruser_hederr)

    return jsonify(result="False")

'''Getting audio file list from database.'''
def get_fetched_audio_list(accesscode, activeprojectname):
    mongodb_info = mongo.db.accesscodedetails  
    fetchedaudiodict = mongodb_info.find_one({"projectname": activeprojectname, "karyaaccesscode": accesscode},
                                                {"karyafetchedaudios":1, "_id" :0}
                                            )   
    fetched_audio_list = fetchedaudiodict['karyafetchedaudios']
    # print("3 : ", fetched_audio_list)
    return fetched_audio_list


#update audio metadata in transcription
# def update_audio_metadata_transcription(speakerid, activeprojectname, karya_audio_report):
# def update_audio_metadata_transcription(activeprojectname, karya_audio_report):
#     mongodb_info = mongo.db.transcription

#     updated_audio_metadata = {"additionalInfo":"", "audioMetadata":{"karyaVerificationMetadata": karya_audio_report, "verificationReport": karya_audio_report}}

#     audio_metadata_transcription = mongodb_info.update({'projectname': activeprojectname, 'speakerId': accesscode_speakerid},
#                                                             {"$set": {updated_audio_metadata}}) 

#     return audio_metadata_transcription

'''Fetching audio files from karya files. '''
@karya_bp.route('/fetch_karya_audio', methods=['GET', 'POST'])
@login_required
def fetch_karya_audio():
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
    project_type = getprojecttype.getprojecttype(projects, activeprojectname)

    derivedFromProjectName = ''
    derive_from_project_type = ''
    derivefromprojectform = ''
    if (project_type == 'transcriptions'):
        derivedFromProject = projects.find_one({"projectname" : activeprojectname},
                                            {"_id": 0, "derivedFromProject": 1})
        if (len(derivedFromProject['derivedFromProject']) != 0):
            derivedFromProjectName = derivedFromProject['derivedFromProject'][0]
            derive_from_project_type = getprojecttype.getprojecttype(projects, derivedFromProjectName)
            if (derive_from_project_type == "questionnaires"):
                derivefromprojectform = projectsform.find_one({"projectname" : derivedFromProjectName})

    # print('request.method', request.method)
    if request.method == 'POST':
        ###############################   verify OTP    ##########################################
        access_code = request.form.get("access_code")
        for_worker_id = request.form.get("speaker_id")

         ###### Get already fetched audio list
        fetched_audio_list = get_fetched_audio_list(access_code, activeprojectname)

        phone_number = request.form.get("mobile_number")

        otp = request.form.get("karya_otp")

        # print('access_code', access_code, 'for_worker_id', for_worker_id, 'otp', otp)

        verifyotp_urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/worker/otp/verify'
        verifyotp_hederr= {'access-code':access_code, 'phone-number':phone_number, 'otp':otp}
        verifyPh_request = requests.put(url = verifyotp_urll, headers = verifyotp_hederr) 
        if verifyPh_request.status_code != int(200):
            flash("Please Provide Correct OTP/Mobile Number")
            return redirect(url_for('karya_bp.home_insert'))
            
        # print (verifyPh_request.json())
            
        # print("working on next code", verifyPh_request.json())
        ##TODO: Put check for verifying if the OTP was correct or not. If correct then proceed otherwise send error
        getTokenid_assignment_hedder = verifyPh_request.json()['id_token']
        # print ("ID token : ", getTokenid_assignment_hedder)
         
        
        ###############################   Get Assignments    ##########################################
        hederr= {'karya-id-token':getTokenid_assignment_hedder}
        assignment_urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=new&from=2021-05-11T07:23:40.654Z'
        assignment_request = requests.get(headers = hederr, url = assignment_urll) 
   
        r_j = assignment_request.json()
        # print(dict(r_j))
        # print ('Lenght of JSON : ', len(r_j))

###################################################################################
##############################  File ID and sentence mapping   #################################
###################################################################################
        '''worker ID'''

        workerId_list = []
        sentence_list = []
        karya_audio_report = []
        filename_list = []
        fileID_list = [] # filname        


        
        
        ##todo : take the report from karya api 
        micro_task_ids = dict((item['id'], item) for item in r_j["microtasks"])

        # for item in r_j["microtasks"]:
        #     karyareport = item['input']['data']['report']
        #     print('line 692', karyareport)


        # pprint(r_j)
        for item in r_j['assignments']:
            micro_task_id = item['microtask_id']
            
            findWorker_id = micro_task_ids[micro_task_id]["input"]["chain"]
            worker_id = findWorker_id["workerId"]
            print("line 699", worker_id)
            # print('worker_id', worker_id, 'for_worker_id', for_worker_id)
            try:
                if (worker_id == for_worker_id):
                    workerId_list.append(worker_id)
                    
                    sentences = micro_task_ids[micro_task_id]["input"]["data"]["sentence"]
                    sentence_list.append(sentences)

                    fileID_lists = item['id'] 
                    fileID_list.append(fileID_lists)

                    #appending karya report to list
                    karyareport = micro_task_ids[micro_task_id]['input']['data']['report']
                    karya_audio_report.append(karyareport)

                    #appending audio file name
                    karya_file_name = micro_task_ids[micro_task_id]['input']['files']['recording']
                    filename_list.append(karya_file_name)

                #speakerid of accesscode
                accesscode_speakerid = accesscodedetails.find_one({"projectname": activeprojectname, "karyaaccesscode": access_code},
                                                                        {'karyaInfo.karyaSpeakerId': 1,'_id': 0})['karyaInfo.karyaSpeakerId']

                #task 
                task = accesscodedetails.find_one({"projectname": activeprojectname, "karyaInfo.karyaSpeakerId": accesscode_speakerid,
                                                                "karyaaccesscode": access_code},{'task': 1,'_id': 0})['task']

            except:
                pass

            else:
                if (worker_id == for_worker_id):
                    workerId_list.append(worker_id)
                    
                    sentences = micro_task_ids[micro_task_id]["input"]["data"]["sentence"]
                    sentence_list.append(sentences)

                    fileID_lists = item['id'] 
                    fileID_list.append(fileID_lists)


        

        print("line 842", karya_audio_report)
        print("line 843", sentence_list)
        print("line 844",workerId_list)




        ####### yha pr try condition de kr mujhe report dalna hia agr report blank hai to niche ka code else mai dlana hia (upto line 859 audio_speaker_merge)
        if karya_audio_report == 0:
            fileID_sentence_list = tuple(zip(fileID_list, sentence_list))
            print("line 859 " , fileID_sentence_list)

        #put check condiotn -> if the speakerId and fileID  previouls fetched or not / Fetch on the basis of fileID assign to speakerID
            audio_speaker_merge = {key:value for key, value in zip(fileID_sentence_list , workerId_list)} #speakerID = fileID_list(fieldID)
            # print(len("line 860", audio_speaker_merge))
            print("line 869", audio_speaker_merge)
            # print(audio_speaker_merge.keys())


            language = accesscodedetails.find_one({"projectname": activeprojectname, "karyaaccesscode": access_code},
                                                    {'language': 1,'_id': 0})['language']
            exclude_ids = []
            if (project_type == 'questionnaires'):
                exclude_ids = getquesidlistofsavedaudios.getquesidlistofsavedaudios(questionnaires,
                                                                                    activeprojectname,
                                                                                    language,
                                                                                    exclude_ids)
            elif (project_type == 'transcriptions' and
                    derive_from_project_type == 'questionnaires'):
                exclude_ids = audiodetails.getaudioidlistofsavedaudios(transcriptions,
                                                                        activeprojectname,
                                                                        language,
                                                                        exclude_ids,
                                                                        for_worker_id)
            

            # print(f"LanguageScript: {language}\nExcludeIds: {exclude_ids}\nLENGTH ExcludeIds: {len(exclude_ids)}")
            file_id_list = []
            # print(f"Length of fileIdList: {file_id_list}\nLength of fileIdSet: {set(file_id_list)}")

            for file_id_and_sent in list(audio_speaker_merge.keys()):

                karyaspeakerId = audio_speaker_merge[file_id_and_sent]
                print("\n \n Checking line no. 618: ", karyaspeakerId)
                
                current_file_id = file_id_and_sent[0]
                current_sentence = file_id_and_sent[1].strip()
                # current_audio_report = file_id_and_sent[2].strip() #audio report 

                file_id_list.append(current_file_id)

                ### Checking if the file is already fetched or not
                if current_file_id not in fetched_audio_list:
                    if (project_type == 'questionnaires'):
                        last_active_ques_id, message =  getquesfromprompttext.getquesfromprompttext(projectsform,
                                                                                                        questionnaires,
                                                                                                        activeprojectname,
                                                                                                        current_sentence,
                                                                                                        exclude_ids)
                        if last_active_ques_id == 'False': 
                            print(f"665: {last_active_ques_id}: {message}: {current_sentence}")
                            continue

                    elif (project_type == 'transcriptions' and
                            derive_from_project_type == 'questionnaires'):
                            transcription_audio_id, message  = audiodetails.getaudiofromprompttext(projectsform,
                                                                                            transcriptions,
                                                                                            derivedFromProjectName,
                                                                                            activeprojectname,
                                                                                            current_sentence,
                                                                                            exclude_ids)
                            if transcription_audio_id == 'False': 
                                print(f"677: {transcription_audio_id}: {message}: {current_sentence}")
                                continue



                    # if last_active_ques_id == 'False': 
                    #     print(f"{last_active_ques_id}: {message}: {current_sentence}")
                    #     continue

                    rl = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignment/id/input_file'

                    new_url = rl.replace("id", current_file_id)
                    # print(new_url)

                    ## Fetching audio
                    ra = requests.get(url = new_url, headers = hederr)
                    # print(type(ra))

                    ##Audio Content
                    filebytes= ra.content
                    # print(type(filebytes))

                    karyaspeakerId = audio_speaker_merge[file_id_and_sent]
                    print("\n \n Checking line no. 618: ", karyaspeakerId)
                    lifespeakerid = accesscodedetails.find_one({'karyaspeakerid': karyaspeakerId}, {'lifespeakerid': 1,'_id': 0})
                    


                    if lifespeakerid is not None:
                        lifespeakerid = lifespeakerid["lifespeakerid"]
                        with BytesIO(gzip.decompress(filebytes)) as fh: #1
                            fileAudio = tarfile.TarFile(fileobj=fh) #2
                            for member in fileAudio.getmembers():
                                f = fileAudio.extractfile(member)
                                content = f.read()
                                new_audio_file = {}
                                new_audio_file['audiofile'] = FileStorage(io.BytesIO(content), filename =  fileAudio.getnames()[0])
                                print(new_audio_file['audiofile'])

                                if project_type == "questionnaires":
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
                                                                                        new_audio_file,
                                                                                        karyaSpeakerId=karyaspeakerId
                                                                                    )
                                ##Todo: provied score                                                    
                                elif (project_type == 'transcriptions'):
                                    if (derive_from_project_type == 'questionnaires'):
                                        save_status = audiodetails.updateaudiofiles(mongo,
                                                                                        projects,
                                                                                        userprojects,
                                                                                        transcriptions,
                                                                                        projectowner,
                                                                                        activeprojectname,
                                                                                        current_username,
                                                                                        lifespeakerid,
                                                                                        new_audio_file,
                                                                                        transcription_audio_id,
                                                                                        karyaInfo={
                                                                                            "karyaSpeakerId": karyaspeakerId,
                                                                                            "karyaFetchedAudioId": current_file_id
                                                                                        },
                                                                                        audioMetadata={
                                                                                            "karyaVerificationMetadata": "", 
                                                                                            "verificationReport": ""},

                                                                                        additionalInfo= {}  
                                                                                    )
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
                                                                                    karyaInfo={
                                                                                        "karyaSpeakerId": karyaspeakerId,
                                                                                        "karyaFetchedAudioId": current_file_id
                                                                                    }
                                                                                )
                                    # print("11  Saving to Transcription collection")
                                # print(exclude_ids)

                                if save_status[0]:
                                    ## save in the list of fetched audios
                                    if (project_type == 'questionnaires'):
                                        exclude_ids.append(last_active_ques_id)
                                    elif (project_type == 'transcriptions' and
                                            derive_from_project_type == 'questionnaires'):
                                            exclude_ids.append(transcription_audio_id)
                                    # print("status of save_status : ", save_status)
                                    accesscodedetails.update_one({"projectname": activeprojectname, "karyaaccesscode": access_code},
                                                                    {"$addToSet": {"karyafetchedaudios":current_file_id}})
                    else:
                        print(f"lifespeakerid not found!: {karyaspeakerId}")
                else:
                    print(f"Audio already fetched: {current_sentence}")

        else:
            # fileID_sentence_lis = tuple(zip(fileID_list, sentence_list, karya_audio_report))
            # print("line 862 " , fileID_sentence_lis)
            

            karya_audio_report_key = []
            karya_audio_report_value = []

            # fileID_sentence_list = tuple(zip(f, s, r))
            # print(fileID_sentence_list)


            for report_key_value in karya_audio_report:
                karya_audio_report_value.append(report_key_value.values())
                karya_audio_report_key.append(report_key_value.keys())
            #     fileID_sentence_list = tuple(zip(f, s, p))
            #     print(fileID_sentence_list)
            # print("#############################")
            # print(karya_audio_report_key)
            # print("#############################")
            # print(karya_audio_report_value)

            fileID_sentence_list = tuple(zip(fileID_list, sentence_list, karya_audio_report_value))
            # print("line 1052 " , fileID_sentence_list)
            #put check condiotn -> if the speakerId and fileID  previouls fetched or not / Fetch on the basis of fileID assign to speakerID
            audio_speaker_merge = {key:value for key, value in zip(fileID_sentence_list , workerId_list)} #speakerID = fileID_list(fieldID)
            # print(len("line 860", audio_speaker_merge))
            # print("line 1056 ", audio_speaker_merge)
            # print(audio_speaker_merge.keys())


            language = accesscodedetails.find_one({"projectname": activeprojectname, "karyaaccesscode": access_code},
                                                    {'language': 1,'_id': 0})['language']
            exclude_ids = []
            if (project_type == 'questionnaires'):
                exclude_ids = getquesidlistofsavedaudios.getquesidlistofsavedaudios(questionnaires,
                                                                                    activeprojectname,
                                                                                    language,
                                                                                    exclude_ids)
            elif (project_type == 'transcriptions' and
                    derive_from_project_type == 'questionnaires'):
                exclude_ids = audiodetails.getaudioidlistofsavedaudios(transcriptions,
                                                                        activeprojectname,
                                                                        language,
                                                                        exclude_ids,
                                                                        for_worker_id)
            

            # print(f"LanguageScript: {language}\nExcludeIds: {exclude_ids}\nLENGTH ExcludeIds: {len(exclude_ids)}")


            karya_report_uniquekey = []
            for report_key in karya_audio_report_key: #karya_report_key
                if report_key not in karya_report_uniquekey:
                    karya_report_uniquekey.append(report_key) 
            # print(ress)
            # print("unique_key" , karya_report_uniquekey)


            karya_report_uniquekey_flattened_list = [item for sublist in karya_report_uniquekey for item in sublist]
            karya_report_list = []
            for report_value_sublist in karya_audio_report_value:
                karya_report_list.append(dict(zip(karya_report_uniquekey_flattened_list, report_value_sublist)))

            print(karya_report_list)
            


            file_id_list = []
            # print(f"Length of fileIdList: {file_id_list}\nLength of fileIdSet: {set(file_id_list)}")

            for file_id_and_sent, karya_report in zip(list(audio_speaker_merge.keys()), karya_report_list):

                # print("this dictonary of report of audio", karya_report_merge)
                
                current_file_id = file_id_and_sent[0]
                print(current_file_id)

                current_sentence = file_id_and_sent[1].strip()
                # current_audio_report = file_id_and_sent[2] #audio report vlaue
                # print("line 1087", current_audio_report)
                # print("line 1087", type(current_audio_report))
                current_audio_report = karya_report
                print("\n \n ",current_audio_report, "\n \n ")

                file_id_list.append(current_file_id)

                    
                # for karya_report in karya_report_merge:
                    ### Checking if the file is already fetched or not
                if current_file_id not in fetched_audio_list:
                    if (project_type == 'questionnaires'):
                        last_active_ques_id, message =  getquesfromprompttext.getquesfromprompttext(projectsform,
                                                                                                        questionnaires,
                                                                                                        activeprojectname,
                                                                                                        current_sentence,
                                                                                                        exclude_ids)
                        if last_active_ques_id == 'False': 
                            print(f"665: {last_active_ques_id}: {message}: {current_sentence}")
                            continue

                    elif (project_type == 'transcriptions' and
                            derive_from_project_type == 'questionnaires'):
                            transcription_audio_id, message  = audiodetails.getaudiofromprompttext(projectsform,
                                                                                            transcriptions,
                                                                                            derivedFromProjectName,
                                                                                            activeprojectname,
                                                                                            current_sentence,
                                                                                            exclude_ids)
                            if transcription_audio_id == 'False': 
                                print(f"677: {transcription_audio_id}: {message}: {current_sentence}")
                                continue



                    # if last_active_ques_id == 'False': 
                    #     print(f"{last_active_ques_id}: {message}: {current_sentence}")
                    #     continue

                    rl = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignment/id/input_file'

                    new_url = rl.replace("id", current_file_id)
                    print(new_url)

                    ## Fetching audio
                    ra = requests.get(url = new_url, headers = hederr)
                    # print(type(ra))

                    ##Audio Content
                    filebytes= ra.content
                    # print(type(filebytes))

                    karyaspeakerId = audio_speaker_merge[file_id_and_sent]
                    print("Checking line no. 1154: ", karyaspeakerId)

                    lifespeakerid = accesscodedetails.find_one({'karyaspeakerid': karyaspeakerId}, {'lifespeakerid': 1,'_id': 0})
                    


                    if lifespeakerid is not None:
                        lifespeakerid = lifespeakerid["lifespeakerid"]
                        with BytesIO(gzip.decompress(filebytes)) as fh: #1
                            fileAudio = tarfile.TarFile(fileobj=fh) #2
                            for member in fileAudio.getmembers():
                                f = fileAudio.extractfile(member)
                                content = f.read()
                                new_audio_file = {}
                                new_audio_file['audiofile'] = FileStorage(io.BytesIO(content), filename =  fileAudio.getnames()[0])
                                print(new_audio_file['audiofile'])

                                if project_type == "questionnaires":
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
                                                                                        new_audio_file,
                                                                                        karyaSpeakerId=karyaspeakerId
                                                                                    )
                                ##Todo: provied score                                                    
                                elif (project_type == 'transcriptions'):
                                    if (derive_from_project_type == 'questionnaires'):
                                        # for karya_report in karya_report_merge:
                                        save_status = audiodetails.updateaudiofiles(mongo,
                                                                                        projects,
                                                                                        userprojects,
                                                                                        transcriptions,
                                                                                        projectowner,
                                                                                        activeprojectname,
                                                                                        current_username,
                                                                                        lifespeakerid,
                                                                                        new_audio_file,
                                                                                        transcription_audio_id,
                                                                                        karyaInfo={
                                                                                            "karyaSpeakerId": karyaspeakerId,
                                                                                            "karyaFetchedAudioId": current_file_id
                                                                                        },
                                                                                        audioMetadata={
                                                                                            "karyaVerificationMetadata":current_audio_report, 
                                                                                            "verificationReport": current_audio_report},

                                                                                        additionalInfo= {}  
                                                                                    )
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
                                                                                    karyaInfo={
                                                                                        "karyaSpeakerId": karyaspeakerId,
                                                                                        "karyaFetchedAudioId": current_file_id
                                                                                    }
                                                                                )
                                    # print("11  Saving to Transcription collection")
                                # print(exclude_ids)

                                if save_status[0]:
                                    ## save in the list of fetched audios
                                    if (project_type == 'questionnaires'):
                                        exclude_ids.append(last_active_ques_id)
                                    elif (project_type == 'transcriptions' and
                                            derive_from_project_type == 'questionnaires'):
                                            exclude_ids.append(transcription_audio_id)
                                    # print("status of save_status : ", save_status)
                                    accesscodedetails.update_one({"projectname": activeprojectname, "karyaaccesscode": access_code},
                                                                    {"$addToSet": {"karyafetchedaudios":current_file_id}})
                    else:
                        print(f"lifespeakerid not found!: {karyaspeakerId}")
                else:
                    print(f"Audio already fetched: {current_sentence}")

            # print(f"Length of fileIdList: {len(file_id_list)}\nLength of fileIdSet: {len(set(file_id_list))}")
        return redirect(url_for('karya_bp.home_insert'))

    return render_template("fetch_karya_audio.html")

#################################################################################################
    ########################################## Zip File #############################################
    #################################################################################################
'''Upload zip files of audio.'''
@karya_bp.route('/fetch_karya_audio_zip', methods=['GET', 'POST'])
@login_required
def fetch_karya_audio_zip():
    projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo, 'projects', 'userprojects', 'transcriptions')
    current_username = getcurrentusername.getcurrentusername()
    # print('curent user', current_username)
    activeprojectname = getactiveprojectname.getactiveprojectname(current_username, userprojects)
    projectowner = getprojectowner.getprojectowner(projects, activeprojectname)

    if request.method == "POST":
        # listWorkerId = []
        # listrecording = []
        audioZipUpload = request.files['accesscodefile']
        # print(type(audioZipUpload))
        # for audioZipUpload in audioZipUpload:
        fileAudio = tarfile.open(fileobj=audioZipUpload, mode= 'r')
        # print(type(fileAudio))
        # print('1', type(fileAudio))
        # print('2', fileAudio.getnames()) #3
        # print('3', fileAudio.getmembers()) #4
        for filename in fileAudio.getnames():
            if (filename.endswith('.json')):
                # print(filename)
                member = fileAudio.getmember(filename)
                f=fileAudio.extractfile(member)
                content=f.read()
                # print('4', type(member))
                # print('5', type(content))
                jsondata = json.load(io.BytesIO(content))
                # print(jsondata)
                speakerId = jsondata['worker_id']
                wavfilename = jsondata['recording']
                wavmember = fileAudio.getmember(wavfilename)
                wavf=fileAudio.extractfile(wavmember)
                wavcontent=wavf.read()
                # print('4', type(wavmember))
                # print('5', type(wavcontent))
                wavdata = io.BytesIO(wavcontent)

                new_audio_file = {}
                new_audio_file['audiofile'] = FileStorage(wavdata, filename=wavfilename)
                # print('9', new_audio_file['audiofile'], type(new_audio_file['audiofile']))


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
