from flask import Blueprint, redirect, render_template, url_for, request
from app import mongo
from app.controller import getdbcollections, getactiveprojectname, getcurrentuserprojects
from app.controller import getprojectowner, getcurrentusername
from app.controller import savenewproject, updateuserprojects
from pprint import pprint

life_ques = Blueprint('life_ques', __name__, template_folder='templates', static_folder='static')

@life_ques.route('/life_ques_home')
def life_ques_home():
    return render_template("life_ques_home.html")




@life_ques.route('/questionnaireform', methods=['GET', 'POST'])
def questionnaireform():
    projects, userprojects, projectsform = getdbcollections.getdbcollections(mongo,
                                                'projects',
                                                'userprojects',
                                                'projectsform')
    current_username = getcurrentusername.getcurrentusername()
    currentuserprojectsname =  getcurrentuserprojects.getcurrentuserprojects(current_username, userprojects)
    # life_quess, = getdbcollections.getdbcollections(mongo, 'projectsform')

    # insert_projectforms_data =  {
    #                                 "Project Name":{"", ""},
    #                                 "About the Questionnaire":{"", ""},
    #                                 "Prompt Description in ":{"", ""},
    #                                 "Promt Type":{"",""},
    #                                 "Include Transcription":{"", ""},
    #                                 "Include Instruction":{"",""},
    #                                 "Domain":{"",""},
    #                                 "Elicitation Method":{"",""},
    #                                 "Target":{"",""},
    #                                 "Add Custom Fields for Lexicon":{"",""}
    #                                     }


    # insert_projectforms_data =  {"Project Name":{"projectnametype":"", "fprojectname":""},
    #                                     "About the Questionnaire":{"abouttype":"", "fabout":""},
    #                                     "Prompt Description in ":{"typepromt":"", "fpromt":""},
    #                                     "Promt Type":{"promttype":"", "fpromttype":""},
    #                                     "Include Transcription":{"includetranscriptiontype":"", "fincludetranscription":""},
    #                                     "Include Instruction":{"includeinstructiontype":"", "fincludeinstruction":""},
    #                                     "Domain":{"domaintype":"", "fdomain":""},
    #                                     "Elicitation Method":{"elicitationmethodtype":"", "felicitationmethod":""},
    #                                     "Target":{"targettype":"", "ftarget":""},
    #                                     "Add Custom Fields for Lexicon":{"customfieldtype":"", "fcustomfield":""}
    #                                     }

    # questionaireprojectform = {
    #                                 "username": "alice",
    #                                 "projectname": "alice_project_1",
    #                                 "Language": ["text", ["English", "Hindi"]],
    #                                 "Script": ["", ["latin", "devanagari"]],
    #                                 "Prompt Audio": ["file", ["audio"]],
    #                                 "Domain": ["multiselect", ["General", "Agriculture", "Sports"]],
    #                                 "Elicitation Method": ["select", ["Translation", "Agriculture", "Sports"]],
    #                                 "Target": ["multiselect", ["case", "classifier", "adposition"]]
    #                             }


    # save_insert_projectforms_data = life_quess.insert(questionaireprojectform)
    # print(save_insert_projectforms_data)
    
    if request.method =='POST':
        new_ques_form = dict(request.form.lists())
        print(new_ques_form)
        projectname = new_ques_form['Project Name'][0]
        save_ques_form = {}
        save_ques_form['username'] = current_username
        save_ques_form['projectname'] = projectname
        for key, value in new_ques_form.items():
            if key == 'Language':
                save_ques_form[key] = ["text", value]
            elif key == 'Script':
                save_ques_form[key] = ["", value]
            elif key == 'Prompt Type':
                save_ques_form[key] = ["file", value]
            elif key == 'Domain':
                save_ques_form[key] = ["multiselect", value]
            elif key == 'Elicitation Method':
                save_ques_form[key] = ["select", value]
            elif key =='Target':
                save_ques_form[key] = ['multiselect', value]
            elif 'customField' in key:
                save_ques_form[value[0]] = [new_ques_form['fieldType'+key[-1]][0], value]
        if 'Include Transcription' in new_ques_form:
            save_ques_form['Include Transcription'] = ['waveform', new_ques_form['Include Transcription']]
        else:
            save_ques_form['Include Transcription'] = ['', []]
        if 'Include Instruction' in new_ques_form:
            save_ques_form['Include Instruction'] = ['file', new_ques_form['Include Instruction']]
        else:
            save_ques_form['Include Instruction'] = ['', []]        
        print(save_ques_form)
        projectsform.insert(save_ques_form)


############## Save User name ###############################################
        savenewproject.savenewproject(projects,
                                        projectname,
                                        current_username
                                    )
#######################################################################
        print(projectname)
        updateuserprojects.updateuserprojects(userprojects,
                                                projectname,
                                                current_username
                                            )

        return redirect(url_for("life_ques.life_ques_home"))
    return render_template("questionnaireform.html")             
