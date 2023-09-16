
def getactivequestionnaireid(projects,
                    activeprojectname,
                    current_username):
    """get last active questionnaire id for current user from projects collections

    Args:
        projects (_type_): _description_
        activeprojectname (_type_): _description_
        current_username (_type_): _description_

    Returns:
        _type_: _description_
    """
    # print('lastActiveId.'+current_username+'.'+activeprojectname)
    try:
        last_active_ques_id = projects.find_one({'projectname': activeprojectname},
                                                    {
                                                        '_id': 0,
                                                        'lastActiveId.'+current_username+'.'+activeprojectname: 1
                                                    }
                                                )
        # print(last_active_ques_id)
        if len(last_active_ques_id) != 0:
            last_active_ques_id = last_active_ques_id['lastActiveId'][current_username][activeprojectname]
    except:
        last_active_ques_id = ''

    return last_active_ques_id
