from app.lifeques.controller import (
    getquesfromprompttext,
    savequespromptfile
)

from app.controller import (
    audiodetails
)


from app.karya_ext.controller import (
    karya_api_access
)

'''Getting audio file list from database.'''


def get_fetched_audio_list(accesscodedetails, accesscode, activeprojectname):
    # mongodb_info = mongo.db.accesscodedetails
    fetchedaudiodict = accesscodedetails.find_one({"projectname": activeprojectname, "karyaaccesscode": accesscode},
                                                  {"karyafetchedaudios": 1, "_id": 0}
                                                  )
    fetched_audio_list = fetchedaudiodict['karyafetchedaudios']
    # print("3 : ", fetched_audio_list)
    return fetched_audio_list


def save_audio_file_fetched_from_karya(
    mongo,
    projects, userprojects, projectowner,
    projectsform, questionnaires, transcriptions,
    activeprojectname, current_username,
    project_type, new_audio_file, derive_from_project_type,
    language, insert_audio_id,
    lifespeakerid, karyaspeakerId,
    current_file_id, current_audio_report
):
    if project_type == "questionnaires":
        new_audio_file['Prompt_Audio'+"_" +
                       language] = new_audio_file['audiofile']
        del new_audio_file['audiofile']

        # savequespromptfile
        save_status = savequespromptfile.savequespromptfile(mongo,
                                                            projects,
                                                            userprojects,
                                                            projectsform,
                                                            questionnaires,
                                                            projectowner,
                                                            activeprojectname,
                                                            current_username,
                                                            insert_audio_id,
                                                            new_audio_file,
                                                            karyaSpeakerId=karyaspeakerId
                                                            )
    # Todo: provied score
    elif (project_type == 'transcriptions'):
        if (derive_from_project_type == 'questionnaires'):
            save_status = audiodetails.updateaudiofiles(mongo,
                                                        projects,
                                                        userprojects,
                                                        transcriptions,
                                                        projectowner,
                                                        activeprojectname,
                                                        current_username,
                                                        lifespeakerid,
                                                        new_audio_file,
                                                        insert_audio_id,
                                                        karyaInfo={
                                                            "karyaSpeakerId": karyaspeakerId,
                                                            "karyaFetchedAudioId": current_file_id
                                                        },
                                                        audioMetadata={
                                                            "karyaVerificationMetadata": current_audio_report,
                                                            "verificationReport": current_audio_report},

                                                        additionalInfo={}
                                                        )
        else:
            save_status = audiodetails.saveaudiofiles(mongo,
                                                      projects,
                                                      userprojects,
                                                      transcriptions,
                                                      projectowner,
                                                      activeprojectname,
                                                      current_username,
                                                      lifespeakerid,
                                                      new_audio_file,
                                                      karyaInfo={
                                                          "karyaSpeakerId": karyaspeakerId,
                                                          "karyaFetchedAudioId": current_file_id
                                                      }
                                                      )
    return save_status


def get_insert_id(
    projectsform, questionnaires, transcriptions,
    activeprojectname, derive_from_project_type, derivedFromProjectName,
    current_sentence,
    project_type, exclude_ids
):
    if (project_type == 'questionnaires'):
        insert_audio_id, message = getquesfromprompttext.getquesfromprompttext(projectsform,
                                                                               questionnaires,
                                                                               activeprojectname,
                                                                               current_sentence,
                                                                               exclude_ids)

    elif (project_type == 'transcriptions' and
            derive_from_project_type == 'questionnaires'):
        insert_audio_id, message = audiodetails.getaudiofromprompttext(projectsform,
                                                                       transcriptions,
                                                                       derivedFromProjectName,
                                                                       activeprojectname,
                                                                       current_sentence,
                                                                       exclude_ids)
    return insert_audio_id, message


def getnsave_karya_recordings(mongo,
                              projects, userprojects, projectowner, accesscodedetails,
                              projectsform, questionnaires, transcriptions,
                              activeprojectname, derivedFromProjectName, current_username,
                              project_type, derive_from_project_type,
                              audio_speaker_merge, fetched_audio_list, exclude_ids,
                              language, hederr, access_code
                              ):

    file_id_list = []
    for file_id_and_sent in list(audio_speaker_merge.keys()):
        audio_speaker_merge_vals = audio_speaker_merge[file_id_and_sent]
        karyaspeakerId = audio_speaker_merge_vals[0]
        lifespeakerid = accesscodedetails.find_one(
            {'karyaspeakerid': karyaspeakerId}, {'lifespeakerid': 1, '_id': 0})

        try:
            current_audio_report = audio_speaker_merge_vals[1]
        except:
            current_audio_report = {}
        print("\n \n Checking line no. 618: ", karyaspeakerId)

        current_file_id = file_id_and_sent[0]
        current_sentence = file_id_and_sent[1].strip()

        file_id_list.append(current_file_id)

        # Checking if the file is already fetched or not
        if current_file_id not in fetched_audio_list:
            insert_audio_id, message = get_insert_id(
                projectsform, questionnaires, transcriptions,
                activeprojectname, derive_from_project_type, derivedFromProjectName,
                current_sentence,
                project_type, exclude_ids
            )

            if insert_audio_id == 'False':
                print(
                    f"665: {insert_audio_id}: {message}: {current_sentence}")
                continue

            if lifespeakerid is not None:
                lifespeakerid = lifespeakerid["lifespeakerid"]
                new_audio_file = karya_api_access.get_audio_file_from_karya(
                    current_file_id, hederr)

                save_status = save_audio_file_fetched_from_karya(
                    mongo,
                    projects, userprojects, projectowner,
                    projectsform, questionnaires, transcriptions,
                    activeprojectname, current_username,
                    project_type, new_audio_file, derive_from_project_type,
                    language, insert_audio_id,
                    lifespeakerid, karyaspeakerId,
                    current_file_id, current_audio_report
                )

                if save_status[0]:
                    # save in the list of fetched audios
                    exclude_ids.append(insert_audio_id)
                    # if (project_type == 'questionnaires'):
                    #     exclude_ids.append(insert_audio_id)
                    # elif (project_type == 'transcriptions' and
                    #         derive_from_project_type == 'questionnaires'):
                    #     exclude_ids.append(
                    #         insert_audio_id)
                    # print("status of save_status : ", save_status)
                    accesscodedetails.update_one({"projectname": activeprojectname, "karyaaccesscode": access_code},
                                                 {"$addToSet": {"karyafetchedaudios": current_file_id}})
            else:
                print(f"lifespeakerid not found!: {karyaspeakerId}")
        else:
            print(f"Audio already fetched: {current_sentence}")
