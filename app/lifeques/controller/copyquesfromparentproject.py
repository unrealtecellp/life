"""Module to create copy of all the ques data in "questionnaires" collection """

from datetime import datetime
import re
from pprint import pprint
import jsondiff

def quesmetadata():
    # create quesId
    Id = re.sub(r'[-: \.]', '', str(datetime.now()))
    quesId = 'Q'+Id

    return quesId

def copyquesfromparentproject(projects,
                                questionnaires,
                                projectsform,
                                derivedfromprojectname,
                                newprojectname,
                                current_username):

    # try:
        # get "newproject" questionnaire form
        projectform = projectsform.find_one({"projectname": newprojectname}, {"_id": 0})
        all_derived_ques = questionnaires.find({"projectname": derivedfromprojectname})
        # derivefromprojectform = projectsform.find_one({"projectname": derivedfromprojectname}, {"_id": 0})
        questionnaireIds = []

        # print(jsondiff.diff(derivefromprojectform, projectform))

        # print("LINE No. 27", projectform)

        for derived_ques in all_derived_ques:
            if ("dummy" in derived_ques['quesId']): continue
            # print('line 31: ', derived_ques)
            del derived_ques["_id"]

            derived_ques["username"] = current_username
            derived_ques["projectname"] = newprojectname
            derived_ques["lastUpdatedBy"] = current_username
            derived_ques["quesdeleteFLAG"] = 0
            derived_ques["quessaveFLAG"] = 0
            derived_ques["derivedfromprojectdetails"] = {
                "derivedfromprojectname": derivedfromprojectname,
                "quesId": derived_ques["quesId"]
            }
            quesId = quesmetadata()
            derived_ques["quesId"] = quesId
            questionnaireIds.append(quesId)
        #     # testquesdata = questionnaires.find_one({"quesId": "Q20221030143006093877"}, {"_id": 0})
        #     # pprint(testquesdata)
        #     print("LINE NO. 48")
            derived_quesprompt = derived_ques['prompt']
            derived_quesprompt_content = derived_quesprompt['content']
            lang_script = projectform['LangScript'][1]
            lang_list = list(lang_script.keys())
            for lang in lang_list:
                if (lang in derived_quesprompt_content): continue
                else:
                    content = {}
                    # print(lang)
                    prompt_lang = lang
                    prompt_lang_script = lang_script[prompt_lang]
                    prompt_value = projectform['Prompt Type'][1][prompt_lang]
                    content[prompt_lang] = {}
                    # print(prompt_lang, prompt_lang_script, content)
                    for prompt_type_key, prompt_type_value in prompt_value.items():
                        # print(prompt_type_key, prompt_type_value, prompt_type_value[0], prompt_type_value[1])
                        if (prompt_type_key == 'Text'):
                            content[prompt_lang]['text'] = {
                                                            "000000": {
                                                                "startindex": "",
                                                                "endindex": "",
                                                                "textspan": {
                                                                    prompt_lang_script: ""
                                                                }
                                                            }
                                                        }
                        elif (prompt_type_key == 'Audio'):
                            content[prompt_lang]['audio'] =  {
                                                                "fileId": "",
                                                                "filename": ""
                                                            }
                            if (prompt_type_value[1] != '' and prompt_type_value[1] != 'text'):
                                content[prompt_lang]['audio']['instructions'] = ''
                            if (prompt_type_value[0] == 'waveform'):
                                content[prompt_lang]['audio']['textGrid'] = {
                                                                                "sentence": {
                                                                                    "000000": {
                                                                                        "startindex": "",
                                                                                        "endindex": "",
                                                                                        "transcription": {
                                                                                            prompt_lang_script: ""
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                        elif (prompt_type_key == 'Multimedia'):
                            content[prompt_lang]['multimedia'] =  {
                                                                    "fileId": "",
                                                                    "filename": ""
                                                                }
                            if (prompt_type_value[1] != '' and prompt_type_value[1] != 'text'):
                                content[prompt_lang]['multimedia']['instructions'] = ''
                            if (prompt_type_value[0] == 'waveform'):
                                content[prompt_lang]['multimedia']['textGrid'] = {
                                                                                    "sentence": {
                                                                                        "000000": {
                                                                                            "startindex": "",
                                                                                            "endindex": "",
                                                                                            "transcription": {
                                                                                                prompt_lang_script: ""
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                }
                        elif (prompt_type_key == 'Image'):
                            content[prompt_lang]['image'] =  {
                                                                    "fileId": "",
                                                                    "filename": ""
                                                                }
                            if (prompt_type_value[1] != '' and prompt_type_value[1] != 'text'):
                                content[prompt_lang]['image']['instructions'] = ''
                derived_ques['prompt']['content'][prompt_lang] = content[prompt_lang]
        #     transcriptionlanglist = projectform['Transcription Language'][1]
        #     print()

        #     for key, value in projectform.items():
        #         print("LINE NO. 54", key, value)
        #         if (key == "Language"):
        #             for k, v in derived_quesprompt['text'].items():
        #                 for lang in value[1]:
        #                     if lang not in v:
        #                         derived_quesprompt['text'][k][lang] = ''
        #         elif (key == "Prompt Type"):
        #             # print('LINE 59:', key)
        #             for ptype in value[1]:
        #                 # if (ptype in derived_quesprompt):
        #                 #     print('LINE 62:', ptype)
        #                 #     continue
        #                 # else:
        #                 print('LINE 63:', ptype)
        #                 pt = {'fileId': '',
        #                         'filename': '',
        #                         'fileLanguage': transcriptionlanglist,
        #                         'textGrid': {'sentence': {'000000': {}}}}
        #                 if ("Transcription" in projectform):
        #                     pt['textGrid']['sentence']['000000']['start'] = ''
        #                     pt['textGrid']['sentence']['000000']['end'] = ''
        #                     transcription = {}
        #                     for l in transcriptionlanglist:
        #                         transcription[l] = ''
        #                     pt['textGrid']['sentence']['000000']['transcription'] = transcription
        #                 if ("instruction" in projectform):
        #                     pt['instruction'] = ''
        #                 derived_quesprompt[ptype] = pt
        #                 print('LINE 78:', pt)
        #                 print('LINE 79:', derived_quesprompt)
                
        #         # ("Transcription" not in derived_quesprompt or
        #         #     "Transcription" in derived_quesprompt)):
        #         # if ("Transcription" in projectform):
                    
        #         #     derived_quesprompt["Transcription"] = {
        #         #                     'audioFilename': '',
        #         #                     'audioId': '',
        #         #                     'audioLanguage': transcriptionlanglist,
        #         #                     'speakerId': '',
        #         #                     'textGrid': {'sentence': {'000000': {}}}
        #         #     }
        #         #     derived_quesprompt["Transcription"]['textGrid']['sentence']['000000']['start'] = ''
        #         #     derived_quesprompt["Transcription"]['textGrid']['sentence']['000000']['end'] = ''
        #         #     transcription = {}
        #         #     for l in transcriptionlanglist:
        #         #         transcription[l] = ''
        #         #     derived_quesprompt["Transcription"]['textGrid']['sentence']['000000']['transcription'] = transcription
                
        #         if ("Target" in derived_quesprompt and
        #             "Target" not in projectform):
        #             derived_quesprompt["Target"] = {[]}
            
        #     derived_ques["prompt"] = derived_quesprompt
        #     # pprint(derived_ques)

            questionnaires.insert_one(derived_ques)
        # # print('questionnaireIds', questionnaireIds)
        projects.update_one({"projectname": newprojectname},
                            {
                                "$set":{
                                    "questionnaireIds": questionnaireIds,
                                    "lastActiveId."+current_username+"."+newprojectname: questionnaireIds[-1]
                                }
                            })
    # except Exception as e:
    #     print(e)

        
        

        
# def enterquesfromuploadedfile(projects,
#                                 userprojects,
#                                 questionnaires,
#                                 projectowner,
#                                 activeprojectname,
#                                 quesdf,
#                                 current_username):
#     projectname = activeprojectname
#     project = projects.find_one({}, {projectname : 1})

#     for index, row in quesdf.iterrows():
#         uploadedFileQues = {
#             "username": projectowner,
#             "projectname": activeprojectname,
#             "lastUpdatedBy": current_username,
#             "quesdeleteFLAG": 0,
#             "quessaveFLAG": 0,
#             }
#         quesId = str(row['quesId'])
#         getquesId = None
#         if (quesId == 'nan' or quesId == ''):
#             quesId = quesmetadata()
#         else:
#             getquesId = questionnaires.find_one({ 'quesId' : quesId },
#                                             {'_id' : 0, 'quesId' : 1, 'projectname': 1})
#             if (getquesId == None):
#                 print(f"quesId not in DB")
#                 quesId = quesmetadata()
#             else:
#                 if (getquesId['projectname'] != activeprojectname):
#                     return (3, quesId)

#         uploadedFileQues['quesId'] = quesId
#         if (getquesId != None):
#             questionnaires.update_one({ 'quesId': quesId }, { '$set' : uploadedFileQues })
#         else:
#             questionnaires.insert_one(uploadedFileQues)
#         print(f"{inspect.currentframe().f_lineno}: {uploadedFileQues}")
#         for column_name in list(quesdf.columns):
#             print(f"{inspect.currentframe().f_lineno}: {column_name}")
#             if (column_name not in uploadedFileQues):
#                 value = str(row[column_name])
#                 print(f"{inspect.currentframe().f_lineno}: {value}")
#                 if ('[' in value and ']' in value):
#                     if (value.startswith('[') and value.endswith(']')):
#                         value = value.replace('[', '').replace(']', '').replace(' ', '').split(',')
#                     print(f"{inspect.currentframe().f_lineno}: {value}")
#                 elif (value == 'nan'):
#                     value = ''
#                 if ('content' in column_name):
#                     startindex = '0'
#                     endindex = str(len(value))
#                     for p in range(3):
#                         if (len(startindex) < 3):
#                             startindex = '0'+startindex
#                         if (len(endindex) < 3):
#                             endindex = '0'+endindex
#                     text_boundary_id = startindex+endindex
#                 if ('text.000000' in column_name):
#                     column_name = column_name.replace('000000', text_boundary_id)
#                     if ('startindex' in column_name):
#                         value = startindex
#                     if ('endindex' in column_name):
#                         value = endindex
#                 if ('Sense 1.Gloss.eng' in column_name):
#                     uploadedFileQues['gloss'] = value
#                 if ('Sense 1.Grammatical Category' in column_name):
#                     uploadedFileQues['grammaticalcategory'] = value
#                 uploadedFileQues[column_name] = value
        
#         projects.update_one({"projectname": activeprojectname},
#                             {
#                                 "$set": {
#                                     "lastActiveId."+current_username: {projectname: quesId}
#                                 },
#                                 "$addToSet": {
#                                     "questionnaireIds": quesId
#                                 }
#                             })

#         questionnaires.update_one({ 'quesId': quesId },
#                                     { '$set' : uploadedFileQues })

#     return (4, '')
