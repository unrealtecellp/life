import requests
import gzip
import tarfile
import io
from io import BytesIO
from werkzeug.datastructures import FileStorage
from app.controller import(
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


def get_all_karya_assignments(
    verifyPh_request, access_code_task
):
    getTokenid_assignment_hedder = verifyPh_request.json()['id_token']
    hederr = {'karya-id-token': getTokenid_assignment_hedder}

    if access_code_task == "transcriptionAccessCode":
        print("transcriptionAccessCode URL")
        # assignment_urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=verified&includemt=true&from=2021-05-11T07:23:40.654Z'
        assignment_urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=new&from=2021-05-11T07:23:40.654Z'
    else:
        print("verificationAccessCode URL")
        # assignment_urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=new&from=2021-05-11T07:23:40.654Z'
        assignment_urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=verified&includemt=true&from=2021-05-11T07:23:40.654Z'


    assignment_request = requests.get(headers=hederr, url=assignment_urll)

    r_j = assignment_request.json()

    return r_j, hederr


def get_assignment_metadata(
    accesscodedetails, activeprojectname,
    access_code,
    r_j, for_worker_id
):
    #for_worker_id = spekaer_id recived from form
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
            worker_id = findWorker_id['workerId'] #recorder_id is colection speaker_id
            logger.debug("worker_id: %s", worker_id)

        except:
            # print('worker_id', worker_id, 'for_worker_id', for_worker_id)
            worker_id = assignment_data['recorder_id'] # 
            logger.debug("recorder_id: %s", worker_id) # recorder_id is colection speaker_id
        

      

        try:
            if (worker_id == for_worker_id):  #for_worker_id = spekaer_id recived from form
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


def get_fileid_sentence_mapping(
    fileID_list, workerId_list, sentence_list, karya_audio_report
):
    if len(karya_audio_report) == 0:
        fileID_sentence_list = tuple(zip(fileID_list, sentence_list))
        # print("line 859 ", fileID_sentence_list)

        # put check condiotn -> if the speakerId and fileID  previouls fetched or not / Fetch on the basis of fileID assign to speakerID
        audio_speaker_merge = {key: (value,) for key, value in zip(
            fileID_sentence_list, workerId_list)}  # speakerID = fileID_list(fieldID)
    else:
        fileID_sentence_list = tuple(
            zip(fileID_list, sentence_list))

        worderId_report_list = tuple(
            zip(workerId_list, karya_audio_report))

        audio_speaker_merge = {key: value for key, value in zip(
            fileID_sentence_list, worderId_report_list)}  # speakerID = fileID_list(fieldID)

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
            print(new_audio_file['audiofile'])

    return new_audio_file




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
    
    #for_worker_id = spekaer_id recived from form
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
            if (worker_id == for_worker_id):  #for_worker_id = spekaer_id recived from form
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
