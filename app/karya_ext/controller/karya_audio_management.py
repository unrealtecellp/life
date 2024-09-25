from app.lifeques.controller import (
    getquesfromprompttext,
    savequespromptfile
)

from app.controller import (
    audiodetails,
    life_logging,
    getdbcollections
)

logger = life_logging.get_logger()

from app.karya_ext.controller import (
    karya_api_access
)

project_types = ['transcriptions', 'recordings']


'''Getting audio file list from database.'''
def get_fetched_audio_list(accesscodedetails, accesscode, activeprojectname):
    # mongodb_info = mongo.db.accesscodedetails
    fetchedaudiodict = accesscodedetails.find_one({"projectname": activeprojectname, "karyaaccesscode": accesscode},
                                                  {"karyafetchedaudios": 1, "_id": 0}
                                                  )
    fetched_audio_list = fetchedaudiodict['karyafetchedaudios']
    print("fetched_audio_list : ", fetched_audio_list)
    return fetched_audio_list


def karya_new_get_fetched_audio_list(accesscodedetails, accesscode_of_speaker, activeprojectname):
    # mongodb_info = mongo.db.accesscodedetails
    fetchedaudiodict = accesscodedetails.find_one({"projectname": activeprojectname, "karyaaccesscode": accesscode_of_speaker, 
                                                   "additionalInfo.karya_version": "karya_main"},
                                                  {"karyafetchedaudios": 1, "_id": 0}
                                                  )
    fetched_audio_list = fetchedaudiodict['karyafetchedaudios']
    print("fetched_audio_list : ", fetched_audio_list)
    return fetched_audio_list

def save_audio_file_fetched_from_karya(
    mongo,
    projects, userprojects, projectowner,
    projectsform, questionnaires, transcriptions, recordings,
    activeprojectname, current_username,
    project_type, new_audio_file, derive_from_project_type,
    language, insert_audio_id,
    lifespeakerid, karyaspeakerId,
    current_file_id, current_audio_report
):
    logger.debug("Project_type: %s", project_type)
    logger.debug("derive_from_project_type: %s", derive_from_project_type)
    logger.debug("Project_types: %s", project_types)

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
    elif (project_type in project_types):
        project_type_collection, = getdbcollections.getdbcollections(mongo, project_type)
        if (derive_from_project_type == 'questionnaires'):
            save_status = audiodetails.karya_new_updateaudiofiles(mongo,
                                                        projects,
                                                        userprojects,
                                                        project_type_collection,
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
                                                            "verificationReport": current_audio_report},

                                                        additionalInfo={}
                                                        )
        else:
            logger.debug("Saving audio file to Transcription")
            save_status = audiodetails.saveaudiofiles(mongo,
                                                      projects,
                                                      userprojects,
                                                      project_type_collection,
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
    projectsform, questionnaires, transcriptions, recordings,
    activeprojectname, derive_from_project_type, derivedFromProjectName,
    current_sentence,
    project_type, exclude_ids
):
    """
    Function to retrieve the appropriate audio ID based on the project type and current sentence.
    """

    # Log the current project type
    logger.debug("%s", project_type)
    
    # Log the derived project type and name
    logger.debug("%s, %s", derive_from_project_type, derivedFromProjectName)
    
    # Handle the case where the project type is 'questionnaires'
    if (project_type == 'questionnaires'):
        # Retrieve the audio ID and message using the 'getquesfromprompttext' function
        insert_audio_id, message = getquesfromprompttext.getquesfromprompttext(
            projectsform,
            questionnaires,
            activeprojectname,
            current_sentence,
            exclude_ids
        )

    # Handle the case where the project type is 'transcriptions' and derived from 'questionnaires'
    elif (project_type == 'transcriptions' and
            derive_from_project_type == 'questionnaires'):
        # Retrieve the audio ID and message using the 'getaudiofromprompttext' function
        insert_audio_id, message = audiodetails.getaudiofromprompttext(
            projectsform,
            transcriptions,
            derivedFromProjectName,
            activeprojectname,
            current_sentence,
            exclude_ids
        )
        
        # Log the retrieved audio ID and message
        logger.debug("insert_audio_id: %s\nmessage: %s", insert_audio_id, message)
    
    # Handle the case where the project type is 'recordings' and derived from 'questionnaires'
    elif (project_type == 'recordings' and
            derive_from_project_type == 'questionnaires'):
        # Retrieve the audio ID and message using the 'getaudiofromprompttext' function
        insert_audio_id, message = audiodetails.getaudiofromprompttext(
            projectsform,
            recordings,
            derivedFromProjectName,
            activeprojectname,
            current_sentence,
            exclude_ids
        )
    
    # Return the retrieved audio ID and message
    return insert_audio_id, message

def matched_unmatched_alreadyfetched_sentences(mongo,
                                               projects, userprojects, projectowner, accesscodedetails,
                                               projectsform, questionnaires, transcriptions, recordings,
                                               activeprojectname, derivedFromProjectName, current_username,
                                               project_type, derive_from_project_type,
                                               fileid_sentence_map, fetched_audio_list, exclude_ids,
                                               language, access_code):
    logger.debug("%s, %s", derive_from_project_type, derivedFromProjectName)

    # Initialize dictionaries to store matched, unmatched, and already fetched sentences
    matched_sentences = {}
    unmatched_sentences = {}
    already_fetched_sentences = {}

    # Iterate over the dictionary keys (file ID and sentence pairs)
    for file_id_and_sentence in fileid_sentence_map.keys():
        file_id = file_id_and_sentence[0]
        sentence = file_id_and_sentence[1].strip()

        # Check if the file ID is already in the fetched list
        if file_id in fetched_audio_list:
            already_fetched_sentences[file_id] = sentence
        else:
            # Handle case where the file is not yet fetched
            if (project_type == 'transcriptions' and
                derive_from_project_type == 'questionnaires'):
                projectform = projectsform.find_one(
                    {"projectname": derivedFromProjectName}, {"_id": 0})
                lang_script = projectform['LangScript'][1]

                all_audio = transcriptions.find({"projectname": activeprojectname},
                                                {"_id": 0})
                
                found_match = False

                for audio in all_audio:
                    speaker_id = audio['speakerId']

                    for lang, lang_info in audio["prompt"]["content"].items():
                        script = lang_script[lang]

                        for prompt_type, prompt_info in lang_info.items():
                            if prompt_type == 'text':
                                for boundaryId in lang_info['text'].keys():
                                    prompt_text = lang_info['text'][boundaryId]['textspan'][script].strip()

                                    # Check for matched sentence
                                    if sentence == prompt_text and speaker_id == '':
                                        matched_sentences[file_id] = sentence
                                        found_match = True
                                        break
                                if found_match:
                                    break

                        if found_match:
                            break

                    if found_match:
                        break

                if not found_match:
                    unmatched_sentences[file_id] = sentence

    # Log and print the results
    logger.debug("Matched Sentences: %s, Total: %d", matched_sentences, len(matched_sentences))
    logger.debug("Unmatched Sentences: %s, Total: %d", unmatched_sentences, len(unmatched_sentences))
    logger.debug("Already Fetched Sentences: %s, Total: %d", already_fetched_sentences, len(already_fetched_sentences))

    # print("Matched Sentences:", matched_sentences, "Total:", len(matched_sentences))
    # print("Unmatched Sentences:", unmatched_sentences, "Total:", len(unmatched_sentences))
    # print("Already Fetched Sentences:", already_fetched_sentences, "Total:", len(already_fetched_sentences))

    # Return the results as dictionaries
    return matched_sentences, unmatched_sentences, already_fetched_sentences




def getnsave_karya_recordings(mongo,
                              projects, userprojects, projectowner, accesscodedetails,
                              projectsform, questionnaires, transcriptions, recordings,
                              activeprojectname, derivedFromProjectName, current_username,
                              project_type, derive_from_project_type,
                              audio_speaker_merge, fetched_audio_list, exclude_ids,
                              language, hederr, access_code
                              ):
    logger.debug("%s, %s", derive_from_project_type , derivedFromProjectName)

    # print(fetched_audio_list)

    # Initialize a list to store file IDs
    file_id_list = []

     # Iterate over the dictionary keys (file ID and sentence pairs)
     #fileid_sentence_map is audio_speaker_merge this contain sentences, 
    for file_id_and_sent in list(audio_speaker_merge.keys()):
        audio_speaker_merge_vals = audio_speaker_merge[file_id_and_sent]

        # Extract speaker ID from the audio_speaker_merge dictionary
        karyaspeakerId = audio_speaker_merge_vals[0]
 
        # Retrieve the life speaker ID associated with the Karya speaker ID
        lifespeakerid = accesscodedetails.find_one(
            {'karyaspeakerid': karyaspeakerId, 'projectname': activeprojectname}, {'lifespeakerid': 1, '_id': 0})
        
        # Attempt to get the current audio report, handle if it doesn't exist
        try:
            current_audio_report = audio_speaker_merge_vals[1]
        except:
            current_audio_report = {}
        logger.debug("karyaspeakerId: %s", karyaspeakerId)

        # Extract the file ID and sentence from the key
        current_file_id = file_id_and_sent[0]
        current_sentence = file_id_and_sent[1].strip()

        # Add the current file ID to the file ID list
        file_id_list.append(current_file_id)

        # Checking if the file is already fetched or not
        if current_file_id not in fetched_audio_list:

            # Generate or retrieve the insert audio ID and a message
            insert_audio_id, message = get_insert_id(
                projectsform, questionnaires, transcriptions, recordings,
                activeprojectname, derive_from_project_type, derivedFromProjectName,
                current_sentence,
                project_type, exclude_ids
            )
            logger.debug("insert_audio_id: %s\nmessage: %s", insert_audio_id, message)

            # If the insert audio ID is not valid, skip the current iteration
            if insert_audio_id == 'False':
                logger.debug("insert_audio_id: %s\nmessage: %s\ncurrent_sentence: %s", insert_audio_id, message, current_sentence)
                continue
            
            # If the life speaker ID is found, proceed to fetch and save the audio file
            if lifespeakerid is not None:
                logger.debug('lifespeakerid: %s', lifespeakerid)
                lifespeakerid = lifespeakerid["lifespeakerid"]

                # Fetch the audio file from Karya
                new_audio_file = karya_api_access.get_audio_file_from_karya(
                    current_file_id, hederr)

                # Save the fetched audio file and retrieve the save status
                save_status = save_audio_file_fetched_from_karya(
                    mongo,
                    projects, userprojects, projectowner,
                    projectsform, questionnaires, transcriptions, recordings,
                    activeprojectname, current_username,
                    project_type, new_audio_file, derive_from_project_type,
                    language, insert_audio_id,
                    lifespeakerid, karyaspeakerId,
                    current_file_id, current_audio_report
                )

                logger.debug('save_status: %s', save_status)

                # If the audio file was saved successfully, update the list of fetched audios and access code details
                if save_status[0]:
                    # save in the list of fetched audios
                    # Add the insert audio ID to the list of excluded IDs
                    exclude_ids.append(insert_audio_id)
                    # if (project_type == 'questionnaires'):
                    #     exclude_ids.append(insert_audio_id)
                    # elif (project_type == 'transcriptions' and
                    #         derive_from_project_type == 'questionnaires'):
                    #     exclude_ids.append(
                    #         insert_audio_id)
                    # print("status of save_status : ", save_status)
                    
                    # Update the access code details with the newly fetched audio file ID
                    accesscodedetails.update_one({"projectname": activeprojectname, "karyaaccesscode": access_code},
                                                 {"$addToSet": {"karyafetchedaudios": current_file_id}})
                else:
                    logger.debug("lifespeakerid not found!: %s, %s", karyaspeakerId, lifespeakerid)
            else:
                logger.debug("lifespeakerid not found!: %s, %s", karyaspeakerId, lifespeakerid)
        else:
            logger.debug("Audio already fetched: %s", current_sentence)
            print("audio already fetched", current_sentence )



def karya_new_getnsave_karya_recordings_from_verified(
    mongo, projects, userprojects, projectowner, accesscodedetails,
    projectsform, questionnaires, transcriptions, recordings,
    activeprojectname, derivedFromProjectName, current_username,
    project_type, derive_from_project_type, audio_speaker_merge,
    fetched_audio_list, exclude_ids, language, hederr, accesscode_of_speaker
):
    logger.debug("%s, %s", derive_from_project_type , derivedFromProjectName)

    # Initialize a list to store file IDs
    file_id_list = []

    # Iterate over the dictionary keys (file ID, sentence, and filename tuples)
    for file_id_and_sent in list(audio_speaker_merge.keys()):
        audio_speaker_merge_vals = audio_speaker_merge[file_id_and_sent]

        # Extract speaker ID from the audio_speaker_merge dictionary
        # karyaspeakerId = audio_speaker_merge_vals[0]
        karyaaccesscode = audio_speaker_merge_vals[0]
        print("karyaaccesscode: ", karyaaccesscode)

        # Retrieve the life speaker ID associated with the Karya speaker ID
        karyaspeakerId = accesscodedetails.find_one(
            {'karyaaccesscode': karyaaccesscode, 'projectname': activeprojectname}, {'karyaspeakerid': 1, '_id': 0})['karyaspeakerid']
        
        lifespeakerid = accesscodedetails.find_one(
            {'karyaspeakerid': karyaspeakerId, 'projectname': activeprojectname}, {'lifespeakerid': 1, '_id': 0})
        
        # Attempt to get the current audio report, handle if it doesn't exist
        try:
            current_audio_report = audio_speaker_merge_vals[1]
        except:
            current_audio_report = {}
        logger.debug("karyaspeakerId: %s", karyaspeakerId)

        # Extract the file ID, sentence, and file name from the key
        current_file_id = file_id_and_sent[0]
        current_sentence = file_id_and_sent[1].strip()
        current_file_name = file_id_and_sent[2]  # Extract the file name

        # Add the current file ID to the file ID list
        file_id_list.append(current_file_id)

        # Checking if the file is already fetched or not
        if current_file_id not in fetched_audio_list:

            # Generate or retrieve the insert audio ID and a message
            insert_audio_id, message = get_insert_id(
                projectsform, questionnaires, transcriptions, recordings,
                activeprojectname, derive_from_project_type, derivedFromProjectName,
                current_sentence,
                project_type, exclude_ids
            )
            logger.debug("insert_audio_id: %s\nmessage: %s", insert_audio_id, message)

            # If the insert audio ID is not valid, skip the current iteration
            if insert_audio_id == 'False':
                logger.debug("insert_audio_id: %s\nmessage: %s\ncurrent_sentence: %s", insert_audio_id, message, current_sentence)
                continue
            
            # If the life speaker ID is found, proceed to fetch and save the audio file
            if lifespeakerid is not None:
                logger.debug('lifespeakerid: %s', lifespeakerid)
                lifespeakerid = lifespeakerid["lifespeakerid"]

                # Print the file name that will be sent to the Karya API
                print(f"Sending file name to karya_new_get_audio_file_from_karya: {current_file_name}")
                logger.debug('current_file_name: %s', current_file_name)

                # Fetch the audio file using the file name instead of the file ID
                new_audio_file = karya_api_access.karya_new_get_audio_file_from_karya(
                    current_file_name, hederr)  # Use `current_file_name` here
                print("new_audio_file : ", new_audio_file)
                logger.debug('new_audio_file: %s', new_audio_file)

                # Save the fetched audio file and retrieve the save status
                save_status = save_audio_file_fetched_from_karya(
                    mongo,
                    projects, userprojects, projectowner,
                    projectsform, questionnaires, transcriptions, recordings,
                    activeprojectname, current_username,
                    project_type, new_audio_file, derive_from_project_type,
                    language, insert_audio_id,
                    lifespeakerid, karyaspeakerId,
                    current_file_id, current_audio_report
                )

                logger.debug('save_status: %s', save_status)

                # If the audio file was saved successfully, update the list of fetched audios and access code details
                if save_status[0]:
                    # Save in the list of fetched audios
                    exclude_ids.append(insert_audio_id)
                    
                    # Update the access code details with the newly fetched audio file ID
                    accesscodedetails.update_one({"projectname": activeprojectname, "karyaaccesscode": accesscode_of_speaker},
                                                 {"$addToSet": {"karyafetchedaudios": current_file_id}})
                else:
                    logger.debug("lifespeakerid not found!: %s, %s", karyaspeakerId, lifespeakerid)
            else:
                logger.debug("lifespeakerid not found!: %s, %s", karyaspeakerId, lifespeakerid)
        else:
            logger.debug("Audio already fetched: %s", current_sentence)
            print("audio already fetched", current_sentence)

def karya_new_getnsave_karya_recordings(
    mongo, projects, userprojects, projectowner, accesscodedetails,
    projectsform, questionnaires, transcriptions, recordings,
    activeprojectname, derivedFromProjectName, current_username,
    project_type, derive_from_project_type, audio_speaker_merge,
    fetched_audio_list, exclude_ids, language, hederr, access_code
):
    logger.debug("%s, %s", derive_from_project_type , derivedFromProjectName)

    # Initialize a list to store file IDs
    file_id_list = []

    # Iterate over the dictionary keys (file ID, sentence, and filename tuples)
    for file_id_and_sent in list(audio_speaker_merge.keys()):
        audio_speaker_merge_vals = audio_speaker_merge[file_id_and_sent]

        # Extract speaker ID from the audio_speaker_merge dictionary
        karyaspeakerId = audio_speaker_merge_vals[0]
        print("karyaspeakerId: ", karyaspeakerId)

        # Retrieve the life speaker ID associated with the Karya speaker ID
        lifespeakerid = accesscodedetails.find_one(
            {'karyaspeakerid': karyaspeakerId, 'projectname': activeprojectname}, {'lifespeakerid': 1, '_id': 0})
        
        # Attempt to get the current audio report, handle if it doesn't exist
        try:
            current_audio_report = audio_speaker_merge_vals[1]
        except:
            current_audio_report = {}
        logger.debug("karyaspeakerId: %s", karyaspeakerId)

        # Extract the file ID, sentence, and file name from the key
        current_file_id = file_id_and_sent[0]
        current_sentence = file_id_and_sent[1].strip()
        current_file_name = file_id_and_sent[2]  # Extract the file name

        # Add the current file ID to the file ID list
        file_id_list.append(current_file_id)

        # Checking if the file is already fetched or not
        if current_file_id not in fetched_audio_list:

            # Generate or retrieve the insert audio ID and a message
            insert_audio_id, message = get_insert_id(
                projectsform, questionnaires, transcriptions, recordings,
                activeprojectname, derive_from_project_type, derivedFromProjectName,
                current_sentence,
                project_type, exclude_ids
            )
            logger.debug("insert_audio_id: %s\nmessage: %s", insert_audio_id, message)

            # If the insert audio ID is not valid, skip the current iteration
            if insert_audio_id == 'False':
                logger.debug("insert_audio_id: %s\nmessage: %s\ncurrent_sentence: %s", insert_audio_id, message, current_sentence)
                continue
            
            # If the life speaker ID is found, proceed to fetch and save the audio file
            if lifespeakerid is not None:
                logger.debug('lifespeakerid: %s', lifespeakerid)
                lifespeakerid = lifespeakerid["lifespeakerid"]

                # Print the file name that will be sent to the Karya API
                print(f"Sending file name to karya_new_get_audio_file_from_karya: {current_file_name}")
                logger.debug('current_file_name: %s', current_file_name)

                # Fetch the audio file using the file name instead of the file ID
                new_audio_file = karya_api_access.karya_new_get_audio_file_from_karya(
                    current_file_name, hederr)  # Use `current_file_name` here
                print("new_audio_file : ", new_audio_file)
                logger.debug('new_audio_file: %s', new_audio_file)

                # Save the fetched audio file and retrieve the save status
                save_status = save_audio_file_fetched_from_karya(
                    mongo,
                    projects, userprojects, projectowner,
                    projectsform, questionnaires, transcriptions, recordings,
                    activeprojectname, current_username,
                    project_type, new_audio_file, derive_from_project_type,
                    language, insert_audio_id,
                    lifespeakerid, karyaspeakerId,
                    current_file_id, current_audio_report
                )

                logger.debug('save_status: %s', save_status)

                # If the audio file was saved successfully, update the list of fetched audios and access code details
                if save_status[0]:
                    # Save in the list of fetched audios
                    exclude_ids.append(insert_audio_id)
                    
                    # Update the access code details with the newly fetched audio file ID
                    accesscodedetails.update_one({"projectname": activeprojectname, "karyaaccesscode": access_code},
                                                 {"$addToSet": {"karyafetchedaudios": current_file_id}})
                else:
                    logger.debug("lifespeakerid not found!: %s, %s", karyaspeakerId, lifespeakerid)
            else:
                logger.debug("lifespeakerid not found!: %s, %s", karyaspeakerId, lifespeakerid)
        else:
            logger.debug("Audio already fetched: %s", current_sentence)
            print("audio already fetched", current_sentence)





