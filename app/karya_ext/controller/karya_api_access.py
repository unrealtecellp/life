from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
    request,
    jsonify
)

import os
import requests
import gzip
import tarfile
import io
from io import BytesIO
from werkzeug.datastructures import FileStorage
from app.controller import (
    life_logging
)
logger = life_logging.get_logger()


def send_karya_otp(
    activeprojectname,
    accesscodedetails,
    input_access_code,
    phone_number
):
    accesscodeindb = accesscodedetails.find_one({"projectname": activeprojectname, "karyaaccesscode": input_access_code, "isActive": 1},
                                                {"karyaaccesscode": 1, "_id": 0})

    # Registration
    registeruser_urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/worker/otp/generate'

    # for current_acodedoc in accesscodedocs:
    #     if input_access_code == current_acodedoc['karyaaccesscode']:
    if 'karyaaccesscode' in accesscodeindb:
        registeruser_hederr = {
            'access-code': input_access_code, 'phone-number': phone_number}
        register_request = requests.put(
            url=registeruser_urll, headers=registeruser_hederr)
        


def karya_new_get_otp_id(phone_number):
    url = 'https://main-karya.centralindia.cloudapp.azure.com/api_auth/v5/otp/generate'
    headers = {'phone_number': phone_number}
    
    response = requests.post(url=url, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        otp_id = response_json.get('otp_id')
        print("function karya_new_get_otp_id", otp_id)
        return otp_id, True
    else:
        return None, False


def verify_karya_otp(
    access_code,
    phone_number,
    otp
):
    verifyotp_urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/worker/otp/verify'
    verifyotp_hederr = {'access-code': access_code,
                        'phone-number': phone_number, 'otp': otp}
    verification_details = requests.put(
        url=verifyotp_urll, headers=verifyotp_hederr)

    return verification_details.status_code == int(200), verification_details


# def karya_new_verify_karya_otp(phone_number, otp, otp_id):
#     url = 'https://main-karya.centralindia.cloudapp.azure.com/api_auth/v5/otp/verify'
#     headers = {
#         'phone_number': phone_number,
#         'otp_id': otp_id,
#         'otp': otp
#     }
#     # print("verify headers: ", headers)
#     otp_verification_details = requests.put(url=url, headers=headers)
    
    
#     return otp_verification_details.status_code == int(200), otp_verification_details

import requests
import json

def karya_new_verify_karya_otp(phone_number, otp, otp_id):
    # URL for the OTP verification API
    url = 'https://main-karya.centralindia.cloudapp.azure.com/api_auth/v5/otp/verify'
    
    # Headers required for the API request
    headers = {
        'phone_number': phone_number,  # Phone number to verify
        'otp_id': otp_id,              # OTP ID received
        'otp': otp                     # OTP entered by the user
    }

    # Sending the PUT request to the OTP verification API
    otp_verification_details = requests.put(url=url, headers=headers)
    
    # Parsing the response JSON
    otp_verification_request = json.loads(otp_verification_details.text)
    
    # Extracting the token ID from the response
    token_id_list = [token['id_token'] for token in otp_verification_request]
    token_id = token_id_list[0]
    
    # Printing the extracted token ID for debugging purposes
    # print("function karya_new_verify_karya_otp Token ID: ", token_id)
    
    # Returning multiple values: 
    # 1. Whether the status code is 200 (successful verification)
    # 2. Extracted token ID
    # 3. The parsed verification request (response content)
    # 4. The full response object
    return otp_verification_details.status_code == int(200), token_id, otp_verification_request, otp_verification_details


# def get_all_karya_assignments(verifyPh_request, additional_task, project_type, access_code_task):
def get_all_karya_assignments(verifyPh_request, assignment_url):

    getTokenid_assignment_hedder = verifyPh_request.json()['id_token']
    hederr = {'karya-id-token': getTokenid_assignment_hedder}
    assignment_request = requests.get(url=assignment_url, headers=hederr)
    r_j = assignment_request.json()
    
    return r_j, hederr




def karya_new_get_all_karya_assignments(token_id, accesscode_of_speaker, assignment_url):
    # Debugging: Print token_id, access_code, and URL
    print(f"Token ID: {token_id}\nAccess Code: {accesscode_of_speaker}\nAssignment URL: {assignment_url}")

    # Set headers with token ID and access code
    tokenid_accesscode_header = {
        'karya_worker_id_token': token_id,
        'access_code': accesscode_of_speaker
    }

    # Make the API request
    karya_new_api_metadata_request = requests.get(url=assignment_url, headers=tokenid_accesscode_header)
    
    # Extract status code
    karya_new_api_metadata_status_code = karya_new_api_metadata_request.status_code

    # Debugging: Print status code
    print(f"Status Code: {karya_new_api_metadata_status_code}")

    # Handle non-200 status codes
    if karya_new_api_metadata_status_code == 403:
        flash('Phone Number Not Registered To This Access Code')
        return None
    elif karya_new_api_metadata_status_code != 200:
        flash(f"Server Issue or Unexpected Error: {karya_new_api_metadata_status_code}")
        return None
    else:
        try:
            # Parse response as JSON
            karya_new_api_metadata = json.loads(karya_new_api_metadata_request.text)

            # Debugging: Print parsed JSON (optional)
            # print(karya_new_api_metadata)

            return karya_new_api_metadata

        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
            flash("Error: Unable to parse the response as JSON")
            return None


def get_assignment_metadata_recording(
    accesscodedetails, activeprojectname,
    access_code,
    r_j, for_worker_id
):
    # for_worker_id = spekaer_id recived from form
    workerId_list = []
    sentence_list = []
    karya_audio_report = []
    filename_list = []
    fileID_list = []  # filname

    micro_task_ids = dict((item['id'], item) for item in r_j["microtasks"])

    # for item in r_j["microtasks"]:
    #     karyareport = item['input']['data']['report']
    #     print('line 692', karyareport)

    # pprint(r_j)
    for item in r_j['assignments']:
        micro_task_id = item['microtask_id']
        assignment_input = micro_task_ids[micro_task_id]['input']
        assignment_data = assignment_input['data']
        # assignment_files = assignment_input['files']
        # findWorker_id = assignment_input['chain']
        # findWorker_id = item['worker_id']

        try:
            # recorder_id is colection speaker_id
            # worker_id = assignment_data['recorder_id']
            worker_id = item['worker_id']
            # recorder_id is colection speaker_id
            logger.debug("recorder_id: %s", worker_id)

        except:
            # print('worker_id', worker_id, 'for_worker_id', for_worker_id)
            # worker_id = findWorker_id['workerId']
            logger.exception("")
            # logger.debug("worker_id: %s", worker_id)

        try:
            if (worker_id == for_worker_id):  # for_worker_id = spekaer_id recived from form
                workerId_list.append(worker_id)

                fileID_lists = item['id']
                fileID_list.append(fileID_lists)

                sentences = assignment_data["sentence"]
                sentence_list.append(sentences)

                # appending karya report to list
                try:
                    karyareport = assignment_data['report']
                    karya_audio_report.append(karyareport)
                except:
                    karyareport = {}
                    karya_audio_report.append(karyareport)
                # appending audio file name
                # karya_file_name = assignment_files['recording']
                # filename_list.append(karya_file_name)

            # speakerid of accesscode
            # accesscode_speakerid = accesscodedetails.find_one({"projectname": activeprojectname, "karyaaccesscode": access_code},
            #                                                   {'karyaInfo.karyaSpeakerId': 1, '_id': 0})['karyaInfo.karyaSpeakerId']

            # # task
            # task = accesscodedetails.find_one({"projectname": activeprojectname, "karyaInfo.karyaSpeakerId": accesscode_speakerid,
            #                                    "karyaaccesscode": access_code}, {'task': 1, '_id': 0})['task']

        except:
            if (worker_id == for_worker_id):
                workerId_list.append(worker_id)

                sentences = assignment_data["sentence"]
                sentence_list.append(sentences)

                fileID_lists = item['id']
                fileID_list.append(fileID_lists)

    logger.debug("karya_audio_report: %s", karya_audio_report)
    logger.debug("sentence_list: %s", sentence_list)
    logger.debug("workerId_list: %s", workerId_list)

    return micro_task_ids, workerId_list, sentence_list, karya_audio_report, filename_list, fileID_list


def karya_new_get_assignment_metadata_recording(
    accesscodedetails, activeprojectname,
    access_code,
    karya_new_api_metadata, for_worker_id
):

    workerId_list = []
    sentence_list = []
    karya_audio_report = []
    filename_list = []
    fileID_list = []  # file names

    # Create a dictionary of microtasks with their IDs as keys
    micro_task_ids = {item['id']: item for item in karya_new_api_metadata["microtasks"]}
    # print("micro_task_ids keys:", micro_task_ids.keys())
    
    # Process each assignment
    for assignment in karya_new_api_metadata['assignments']:
        # print("\nProcessing assignment:", assignment)  # Debug the whole assignment
        micro_task_id = assignment['microtask_id']
        # print("micro_task_id:", micro_task_id)
        
        # Get the input and data from the related microtask
        if micro_task_id in micro_task_ids:
            assignment_input = micro_task_ids[micro_task_id]['input']
            # print("assignment_input:", assignment_input)
            assignment_data = assignment_input['data']
            # print("assignment_data:", assignment_data)
            findWorker_id = assignment.get('worker_id')
            # print("findWorker_id:", findWorker_id)

            # Determine worker_id based on 'recorder_id' or 'chain'
            try:
                worker_id = assignment_data['recorder_id']
                # print("recorder_id (from assignment_data):", worker_id)
            except KeyError:
                worker_id = findWorker_id
                # print("worker_id (from findWorker_id):", worker_id)

            # print('for_worker_id:', for_worker_id)
            # print('Worker_id:', worker_id)

            # If the worker_id matches the for_worker_id from the form
            if worker_id == for_worker_id:
                workerId_list.append(worker_id)
                # print("Added worker_id to workerId_list:", workerId_list)

                # Append microtask ID (assignment ID) to fileID_list
                fileID_lists = assignment['id']
                fileID_list.append(fileID_lists)
                # print("Added assignment ID to fileID_list:", fileID_list)

                # Append sentence from the microtask data
                sentences = assignment_data.get("sentence", "")
                sentence_list.append(sentences)
                # print("Added sentence to sentence_list:", sentence_list)

                # Append karya audio report if present in assignment data
                karyareport = assignment_data.get('report', None)
                # print("karyareport:", karyareport)
                if karyareport:
                    karya_audio_report.append(karyareport)
                    # print("Added karyareport to karya_audio_report:", karya_audio_report)

                # Append filename of the recording if available in the output
                output = assignment.get('output', {})
                # print("Output:", output)

                if output is None:
                    print("Error: 'output' is None for assignment:", assignment)
                else:
                    data = output.get('data', {})
                    # print("Data from output:", data)

                    files = output.get('files', {})
                    # print("Files from data:", files)  # Should print the 'files' dictionary

                    karya_file_name = files.get('OutputRecording', "")
                    # print('karya_file_name:', karya_file_name)
                    if karya_file_name:
                        filename_list.append(karya_file_name)
                        # print("Added karya_file_name to filename_list:", filename_list)

    # Log the lists before returning them
    print("Final karya_audio_report:", karya_audio_report)
    print("Final sentence_list:", sentence_list)
    print("Final workerId_list:", workerId_list)
    print("Final filename_list:", filename_list)
    print("Final fileID_list:", fileID_list)

    return micro_task_ids, workerId_list, sentence_list, karya_audio_report, filename_list, fileID_list



def get_assignment_metadata(
    accesscodedetails, activeprojectname,
    access_code,
    r_j, for_worker_id
):
    # for_worker_id = spekaer_id recived from form
    workerId_list = []
    sentence_list = []
    karya_audio_report = []
    filename_list = []
    fileID_list = []  # filname

    micro_task_ids = dict((item['id'], item) for item in r_j["microtasks"])

    # for item in r_j["microtasks"]:
    #     karyareport = item['input']['data']['report']
    #     print('line 692', karyareport)

    # pprint(r_j)
    for item in r_j['assignments']:
        micro_task_id = item['microtask_id']
        assignment_input = micro_task_ids[micro_task_id]['input']
        assignment_data = assignment_input['data']
        # assignment_files = assignment_input['files']
        findWorker_id = assignment_input['chain']

        try:
            # recorder_id is colection speaker_id
            worker_id = assignment_data['recorder_id']
            # recorder_id is colection speaker_id
            logger.debug("recorder_id: %s", worker_id)

        except:
            # print('worker_id', worker_id, 'for_worker_id', for_worker_id)
            worker_id = findWorker_id['workerId']
            logger.debug("worker_id: %s", worker_id)

        try:
            if (worker_id == for_worker_id):  # for_worker_id = spekaer_id recived from form
                workerId_list.append(worker_id)

                fileID_lists = item['id']
                fileID_list.append(fileID_lists)

                sentences = assignment_data["sentence"]
                sentence_list.append(sentences)

                # appending karya report to list
                karyareport = assignment_data['report']
                karya_audio_report.append(karyareport)

                # appending audio file name
                # karya_file_name = assignment_files['recording']
                # filename_list.append(karya_file_name)

            # speakerid of accesscode
            # accesscode_speakerid = accesscodedetails.find_one({"projectname": activeprojectname, "karyaaccesscode": access_code},
            #                                                   {'karyaInfo.karyaSpeakerId': 1, '_id': 0})['karyaInfo.karyaSpeakerId']

            # # task
            # task = accesscodedetails.find_one({"projectname": activeprojectname, "karyaInfo.karyaSpeakerId": accesscode_speakerid,
            #                                    "karyaaccesscode": access_code}, {'task': 1, '_id': 0})['task']

        except:
            if (worker_id == for_worker_id):
                workerId_list.append(worker_id)

                sentences = assignment_data["sentence"]
                sentence_list.append(sentences)

                fileID_lists = item['id']
                fileID_list.append(fileID_lists)

    logger.debug("karya_audio_report: %s", karya_audio_report)
    logger.debug("sentence_list: %s", sentence_list)
    logger.debug("workerId_list: %s", workerId_list)

    return micro_task_ids, workerId_list, sentence_list, karya_audio_report, filename_list, fileID_list



def karya_verified_get_assignment_metadata(
    accesscodedetails, activeprojectname, accesscode_of_speaker,
    karya_new_api_metadata, for_worker_id
):
    # for_worker_id = speaker_id received from the form
    # workerId_list = []
    sepaker_access_code_list =[]
    sentence_list = []
    karya_audio_report = []
    filename_list = []
    fileID_list = []  # to store file IDs

    # Create a dictionary of microtasks for quick lookup by 'id'
    micro_task_ids = {item['id']: item for item in karya_new_api_metadata["microtasks"]}
    # print("micro_task_ids: ", micro_task_ids)
    # Iterate through assignments in the metadata
    for assignment in karya_new_api_metadata['assignments']:
        micro_task_id = assignment['microtask_id']
        
        # Look up the corresponding microtask using the micro_task_id
        assignment_input = micro_task_ids.get(micro_task_id, {}).get('input', {})
        # print('assignment_input : ', assignment_input)
        assignment_data = assignment_input.get('data', {})

        assignment_output = micro_task_ids.get(micro_task_id, {}).get('output', {})

        # Extract worker_id from assignment
        # worker_id = assignment.get('worker_id')
        #now worker_id is not avialble now we have to find the own_access_code 
        sepaker_access_code = assignment_data.get("own_access_code")
        print("sepaker_access_code: ", sepaker_access_code)

        if not sepaker_access_code:
            continue  # Skip this iteration if worker_id is missing

        try:
            if sepaker_access_code == accesscode_of_speaker:  # for_worker_id is speaker_id from the form
                sepaker_access_code_list.append(sepaker_access_code)
                print("condtion sepaker_access_code: ", sepaker_access_code)

                # Extract fileID from assignment
                fileID_lists = assignment['id']
                fileID_list.append(fileID_lists)

                # Extract sentence from microtask input data
                sentence = assignment_data.get("sentence")
                sentence_list.append(sentence)

                # Attempt to extract report if available
            
                # Build the report based on the 'accepted' value
                report_data = assignment_output.get('data', {})
                if report_data.get('accepted', False):
                    report = {
                        'data': {
                            'accepted': report_data['accepted']
                        }
                    }
                else:
                    report = {
                        'data': {
                            'accepted': report_data['accepted'],
                            'accuracy': report_data.get('accuracy', [])
                        }
                    }
                
                # Append the constructed report to karya_audio_report
                karya_audio_report.append(report)

                # Extract the filename for the audio file
                try:
                    # filename = assignment['output']['files']['OutputRecording']
                    files = assignment_input.get('files', {})
                    # print("Files from data:", files)  # Should print the 'files' dictionary

                    karya_file_name = files.get('OutputRecording')
                    filename_list.append(karya_file_name)
                except KeyError:
                    # If no recording is found, append None
                    filename_list.append(None)

        except Exception as e:
            logger.exception(f"Error processing worker_id {sepaker_access_code}: {e}")
            continue

    logger.debug("karya_audio_report: %s", karya_audio_report)
    logger.debug("sentence_list: %s", sentence_list)
    logger.debug("workerId_list: %s", sepaker_access_code_list)

    return micro_task_ids, sepaker_access_code_list, sentence_list, karya_audio_report, filename_list, fileID_list





def get_fileid_sentence_mapping(
    fileID_list, workerId_list, sentence_list, karya_audio_report
):
    """
    Function to create a mapping between file IDs, sentences, and worker IDs,
    with optional inclusion of audio report data.
    """

    # Check if karya_audio_report is empty
    if len(karya_audio_report) == 0:
        # Create a list of tuples pairing file IDs with sentences
        fileID_sentence_list = tuple(zip(fileID_list, sentence_list))
        
        # Merge file ID-sentence pairs with worker IDs into a dictionary
        # Each key is a (fileID, sentence) pair, and the value is the corresponding worker ID
        audio_speaker_merge = {key: (value,) for key, value in zip(
            fileID_sentence_list, workerId_list)}
    else:
        # Create a list of tuples pairing file IDs with sentences
        fileID_sentence_list = tuple(zip(fileID_list, sentence_list))

        # Create a list of tuples pairing worker IDs with audio report data
        workerId_report_list = tuple(zip(workerId_list, karya_audio_report))

        # Merge file ID-sentence pairs with worker ID-audio report pairs into a dictionary
        # Each key is a (fileID, sentence) pair, and the value is the corresponding (worker ID, audio report) tuple
        audio_speaker_merge = {key: value for key, value in zip(
            fileID_sentence_list, workerId_report_list)}

    # Return the resulting dictionary
    return audio_speaker_merge

def karya_new_get_fileid_sentence_mapping(
    fileID_list, workerId_list, sentence_list, karya_audio_report, filename_list
):
    """
    Function to create a mapping between file IDs, sentences, filenames, and worker IDs,
    with optional inclusion of audio report data.
    """

    # Check if karya_audio_report is empty
    if len(karya_audio_report) == 0:
        # Create a list of tuples pairing file IDs, sentences, and filenames
        fileID_sentence_filename_list = tuple(zip(fileID_list, sentence_list, filename_list))
        
        # Merge file ID-sentence-filename pairs with worker IDs into a dictionary
        # Each key is a (fileID, sentence, filename) tuple, and the value is the corresponding worker ID
        audio_speaker_merge = {key: (value,) for key, value in zip(
            fileID_sentence_filename_list, workerId_list)}
    else:
        # Create a list of tuples pairing file IDs, sentences, and filenames
        fileID_sentence_filename_list = tuple(zip(fileID_list, sentence_list, filename_list))

        # Create a list of tuples pairing worker IDs with audio report data
        workerId_report_list = tuple(zip(workerId_list, karya_audio_report))

        # Merge file ID-sentence-filename pairs with worker ID-audio report pairs into a dictionary
        # Each key is a (fileID, sentence, filename) tuple, and the value is the corresponding (worker ID, audio report) tuple
        audio_speaker_merge = {key: value for key, value in zip(
            fileID_sentence_filename_list, workerId_report_list)}

    # Return the resulting dictionary
    return audio_speaker_merge



def get_audio_file_from_karya(current_file_id, hederr):
    rl = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignment/id/input_file'

    new_url = rl.replace("id", current_file_id)
    # print(new_url)

    # Fetching audio
    ra = requests.get(url=new_url, headers=hederr)
    # print(type(ra))

    # Audio Content
    filebytes = ra.content
    # print(type(filebytes))

    with BytesIO(gzip.decompress(filebytes)) as fh:  # 1
        fileAudio = tarfile.TarFile(fileobj=fh)  # 2
        for member in fileAudio.getmembers():
            f = fileAudio.extractfile(member)
            content = f.read()
            new_audio_file = {}
            new_audio_file['audiofile'] = FileStorage(
                io.BytesIO(content), filename=fileAudio.getnames()[0])
            # print(new_audio_file['audiofile'])

    return new_audio_file




def karya_new_get_audio_file_from_karya(current_file_name, hederr):
    """
    Fetches the SAS URL for the audio file from the Karya API, then uses that URL to download and save the file.
    
    Arguments:
    - current_file_name: The name of the file to fetch.
    - hederr: The headers required for the request.
    
    Returns:
    - local_file_path: The path of the saved audio file.
    """
    # Define the URL to get the SAS URL for the audio file
    sas_url_request = f'https://main-karya.centralindia.cloudapp.azure.com/fileserver/v1/worker/file_download_sas_url?filename={current_file_name}'

    # Fetch the SAS URL
    response = requests.get(url=sas_url_request, headers=hederr)

    # Check if the request for the SAS URL was successful
    if response.status_code == 200:
        # Extract the SAS URL from the response
        sas_url = response.json().get('sasURL')

        if not sas_url:
            raise Exception("SAS URL not found in the response.")

        # Use the SAS URL to download the actual file
        file_response = requests.get(sas_url)
        # print("file_response type : " , file_response)
        logger.debug("file_response type : %s", file_response)

        if file_response.status_code == 200:        
            # Prepare the audio file as a FileStorage object
            new_audio_file = {
                'audiofile': FileStorage(io.BytesIO(file_response.content), filename=current_file_name)
            }
            
        return new_audio_file
    else:
        print("file not fetched")
        # Handle any errors that occurred during the request
        raise Exception(f"Failed to fetch file. Status code: {response.status_code}")





# import os
# import requests

# def karya_new_get_audio_file_from_karya(current_file_name, hederr):
#     """
#     Fetches the SAS URL for the audio file from the Karya API, then uses that URL to download and save the file.
    
#     Arguments:
#     - current_file_name: The name of the file to fetch.
#     - hederr: The headers required for the request.
    
#     Returns:
#     - local_file_path: The path of the saved audio file.
#     """
#     # Define the URL to get the SAS URL for the audio file
#     sas_url_request = f'https://main-karya.centralindia.cloudapp.azure.com/fileserver/v1/worker/file_download_sas_url?filename={current_file_name}'

#     # Fetch the SAS URL
#     response = requests.get(url=sas_url_request, headers=hederr)

#     # Check if the request for the SAS URL was successful
#     if response.status_code == 200:
#         # Extract the SAS URL from the response
#         sas_url = response.json().get('sasURL')

#         if not sas_url:
#             raise Exception("SAS URL not found in the response.")

#         # Use the SAS URL to download the actual file
#         file_response = requests.get(sas_url)

#         if file_response.status_code == 200:
#             # Save the file to the local system
#             local_directory = "/home/kmi/Desktop/karya-main/audio"
#             os.makedirs(local_directory, exist_ok=True)  # Create the directory if it doesn't exist
#             local_file_path = os.path.join(local_directory, current_file_name)

#             # Save the file to the local path
#             with open(local_file_path, 'wb') as file:
#                 file.write(file_response.content)

#             return local_file_path
#         else:
#             raise Exception(f"Failed to download file using SAS URL. Status code: {file_response.status_code}")
#     else:
#         raise Exception(f"Failed to fetch SAS URL. Status code: {response.status_code}")





def get_verified_karya_assignments(
    verifyPh_request
):
    getTokenid_assignment_hedder = verifyPh_request.json()['id_token']
    hederr = {'karya-id-token': getTokenid_assignment_hedder}
    # assignment_urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=new&from=2021-05-11T07:23:40.654Z'
    assignment_urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=verified&includemt=true&from=2021-05-11T07:23:40.654Z'
    assignment_request = requests.get(headers=hederr, url=assignment_urll)

    r_j = assignment_request.json()

    return r_j, hederr


def get_verified_assignment_metadata(
        activeprojectname,
        r_j, for_worker_id):

    # for_worker_id = spekaer_id recived from form
    workerId_list = []
    sentence_list = []
    karya_audio_report = []
    filename_list = []
    fileID_list = []  # filname

    micro_task_ids = dict((item['id'], item) for item in r_j["microtasks"])

    # for item in r_j["microtasks"]:
    #     karyareport = item['input']['data']['report']
    #     print('line 692', karyareport)

    # pprint(r_j)
    for item in r_j['assignments']:
        micro_task_id = item['microtask_id']
        assignment_input = micro_task_ids[micro_task_id]['input']
        assignment_data = assignment_input['data']
        # assignment_files = assignment_input['files']

        findWorker_id = assignment_input['chain']
        worker_id = findWorker_id['workerId']
        print("line 699", worker_id)
        # print('worker_id', worker_id, 'for_worker_id', for_worker_id)
        try:
            if (worker_id == for_worker_id):  # for_worker_id = spekaer_id recived from form
                workerId_list.append(worker_id)

                fileID_lists = item['id']
                fileID_list.append(fileID_lists)

                sentences = assignment_data["sentence"]
                sentence_list.append(sentences)

                # appending karya report to list
                karyareport = assignment_data['report']
                karya_audio_report.append(karyareport)

                # appending audio file name
                # karya_file_name = assignment_files['recording']
                # filename_list.append(karya_file_name)

            # speakerid of accesscode
            # accesscode_speakerid = accesscodedetails.find_one({"projectname": activeprojectname, "karyaaccesscode": access_code},
            #                                                   {'karyaInfo.karyaSpeakerId': 1, '_id': 0})['karyaInfo.karyaSpeakerId']

            # # task
            # task = accesscodedetails.find_one({"projectname": activeprojectname, "karyaInfo.karyaSpeakerId": accesscode_speakerid,
            #                                    "karyaaccesscode": access_code}, {'task': 1, '_id': 0})['task']

        except:
            if (worker_id == for_worker_id):
                workerId_list.append(worker_id)

                sentences = assignment_data["sentence"]
                sentence_list.append(sentences)

                fileID_lists = item['id']
                fileID_list.append(fileID_lists)

    print("line 842", karya_audio_report)
    print("line 843", sentence_list)
    print("line 844", workerId_list)

    return micro_task_ids, workerId_list, sentence_list, karya_audio_report, filename_list, fileID_list


if __name__ == '__main__':
    fileID_list = ['F21', 'F22', 'F23']
    workerId_list = ['W21', 'W22', 'W23']
    sentence_list = ['S21', 'S22', 'S23']
    karya_audio_report = [
        {'R1': '1', 'R2': '2', 'R3': '3'},
        {'R21': '0', 'R22': '1', 'R23': '2'},
        {'R31': '2', 'R32': '3', 'R33': '0'}
    ]
    karya_audio_report2 = []

    audio_speaker_merge = get_fileid_sentence_mapping(
        fileID_list, workerId_list, sentence_list, karya_audio_report2
    )

    print(audio_speaker_merge)
    for key, val in audio_speaker_merge.items():
        if len(val) == 1:
            print(val)
        print(val[0])
