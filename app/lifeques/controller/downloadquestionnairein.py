"""Module to download questionnaire in different format."""

def karyajson(questionnaires,
                activeprojectname):
    print('karyajson')
    saved_ques_data = questionnaires.find({}, {})
