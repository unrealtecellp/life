"""Module to data in "questionnaires" collection """

from datetime import datetime
import re

def copydatafromquesproject(questionnaires,
                                transcriptions,
                                derived_from_project_name,
                                newprojectname,
                                current_username):

    all_derived_ques = questionnaires.find({"projectname": derived_from_project_name, "quesdeleteFLAG": 0},
                                            {"_id": 0, "quesId": 1, "Q_Id": 1, "prompt": 1})
    for derived_ques in all_derived_ques:
        print(derived_ques)
        quesId = derived_ques['quesId']
        Q_Id = derived_ques['Q_Id']
        prompt = derived_ques['prompt']
        prompt['Q_Id'] = Q_Id
        derived_from_project_details = {
                                        "derivedfromprojectname": derived_from_project_name,
                                        "quesId": quesId
                                    }
        text_grid = {
                "discourse": {},
                "sentence": {},
                "word": {},
                "phoneme": {}
            }
        # save audio file details in transcriptions collection
        new_audio_details = {
            "username": current_username,
            "projectname": newprojectname,
            "updatedBy": current_username,
            "audiodeleteFLAG": 0,
            "audioverifiedFLAG": 0,
            "transcriptionFLAG": 0,
            "speakerId": "",
            "prompt": prompt
        }

        audio_id = 'A'+re.sub(r'[-: \.]', '', str(datetime.now()))
        new_audio_details['audioId'] = audio_id
        new_audio_details['audioFilename'] = ""
        new_audio_details["textGrid"] = text_grid
        new_audio_details[current_username] = {}
        new_audio_details[current_username]["textGrid"] = text_grid
        new_audio_details['derivedfromprojectdetails'] = derived_from_project_details

        transcription_doc_id = transcriptions.insert(new_audio_details)

    return transcription_doc_id
