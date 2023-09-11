"""Module to get the comment stats for a ques/annotator."""

def getquestionnairestats(projects, questionnaires, activeprojectname, ID, idtype):
    """_summary_

    Args:
        id (_String_): _quesId/annotatorId_
    """
    # print('getquestats(projects, activeprojectname, ID, idtype)')
    # print(ID)
    total_ques = 0
    completed = 0
    notcompleted = 0
    try:
        quesinfo = projects.find_one({ "projectname": activeprojectname },
                                            { "_id" : 0 })
        quesfiles = quesinfo['questionnaireIds']
        total_ques = len(quesfiles)

        completedfiles = questionnaires.find({ "projectname": activeprojectname },
                                            { "_id" : 0, "quessaveFLAG" : 1 })
        # print(quesinfo)
        # print(total_ques)
        for completedfile in completedfiles:
            # print(completedfile, completedfile['quessaveFLAG'])
            if completedfile['quessaveFLAG'] == 1:
                completed += 1
            elif completedfile['quessaveFLAG'] == 0:
                notcompleted += 1
        # print('completed: ', completed, "notcompleted:", notcompleted)
    except:
        pass

    return (total_ques, completed, notcompleted)
    