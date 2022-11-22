"""Module to get the ques info from prompt text."""

from pprint import pprint

def getquesfromprompttext(projectsform,
                            questionnaires,
                            activeprojectname,
                            text):

    """_summary_
    """

    projectform = projectsform.find_one({"projectname": activeprojectname}, {"_id": 0})
    lang_script = projectform['LangScript'][1]
    # print(lang_script)
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
            script = lang_script[lang]
            # print(script)
            for boundaryId in lang_info['text'].keys():
                # print(boundaryId)
                prompt_text = lang_info['text'][boundaryId]['textspan'][script]
                if (text == prompt_text):
                    quesId = ques['quesId']
                    # pprint(ques)
                    print(prompt_text, quesId)

                    return quesId

    return False
