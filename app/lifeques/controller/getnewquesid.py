def getnewquesid(projects,
                    activeprojectname,
                    last_active_id,
                    which_one):
    """_summary_

    Args:
        projects (_type_): _description_
        activeprojectname (_type_): _description_
        last_active_id (_type_): _description_
        which_one (_type_): _description_
    """
    ques_ids_list = projects.find_one({ 'projectname': activeprojectname },
                                        { '_id': 0, 'questionnaireIds': 1 })
    # print('ques_ids_list', ques_ids_list)
    if len(ques_ids_list) != 0:
        ques_ids_list = ques_ids_list['questionnaireIds']                                   
        # print('ques_ids_list', ques_ids_list)
    ques_id_index = ques_ids_list.index(last_active_id)
    # print('latestquesId Index!!!!!!!', ques_id_index)
    if which_one == 'previous':
        ques_id_index = ques_id_index - 1
    elif which_one == 'next':
        if len(ques_ids_list) == (ques_id_index+1):
            ques_id_index = 0
        else:
            ques_id_index = ques_id_index + 1
    latest_ques_id = ques_ids_list[ques_id_index]
    # print('latest_ques_id quesDETAILS', latest_ques_id)

    return latest_ques_id