"""Module to get the ques IDs list for which fileId not empty."""

from pprint import pprint

def getquesidlistofsavedaudios(questionnaires,
                            activeprojectname,
                            lang_script,
                            exclude):

    """_summary_
    """
    all_ques = questionnaires.find({"projectname": activeprojectname},
                                    {
                                        "_id": 0,
                                        "prompt.content": 1,
                                        "quesId": 1
                                    })

    for ques in all_ques:
        # print(ques)
        for lang, lang_info in ques["prompt"]["content"].items():
            # print(lang, lang_info)
            if (lang == lang_script):
                prompt_audio_fileId = lang_info['audio']['fileId']
                prompt_audio_filname = lang_info['audio']['filename']
                if (prompt_audio_fileId != '' and
                    prompt_audio_filname != ''):
                    quesId = ques['quesId']
                    exclude.append(quesId)

    return exclude
