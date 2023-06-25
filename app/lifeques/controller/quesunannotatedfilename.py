"""Module to get the list of all annotated and unannotated filename."""

def quesunannotatedfilename(questionnaires, activeprojectname, idtype):

    annotated = []
    unannotated = []
    quessavedfiles = questionnaires.find({ "projectname": activeprojectname},
                                        { "_id" : 0, "quessaveFLAG" : 1, 'quesId': 1, "Q_Id": 1 })

    for quessavedfile in quessavedfiles:
        # print(quessavedfile)
        try:
            quesid = quessavedfile['quesId']
            Q_Id = quessavedfile['Q_Id']
            quesIdDict = {
                "quesId": quesid,
                "Q_Id": Q_Id
            }
            if quessavedfile['quessaveFLAG'] == 1:
                annotated.append(quesIdDict)
            elif quessavedfile['quessaveFLAG'] == 0:
                unannotated.append(quesIdDict)
        except:
            continue

    # print(sorted(annotated), sorted(unannotated))

    # return (sorted(annotated), sorted(unannotated))
    return (annotated, unannotated)
