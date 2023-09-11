def updatelatestquesid(projects,
                        activeprojectname,
                        last_active_ques_id,
                        current_username):
    """_summary_

    Args:
        projects (_type_): _description_
        activeprojectname (_type_): _description_
        latest_audio_id (_type_): _description_
        current_username (_type_): _description_
    """
    projects.update_one({ 'projectname' : activeprojectname }, \
            { '$set' : {
                        'lastActiveId.'+current_username+'.'+activeprojectname: last_active_ques_id
                        }})
