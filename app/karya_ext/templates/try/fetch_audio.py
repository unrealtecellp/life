karyaaudiodetails, = getdbcollections.getdbcollections(mongo, 'fetchkaryaaudio')
    # urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignment/8432529100993245/input_file'
    # hederr= {'karya-id-token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImExNWE0MGQ0In0.eyJzdWIiOiIyODE0NzQ5NzY3MTA3MDMiLCJlbnRpdHkiOiJ3b3JrZXIiLCJpYXQiOjE2NjI5MDI1NTIsImV4cCI6MTY2NTQ5NDU1MiwiYXVkIjoia2FyeWEtc2VydmVyIiwiaXNzIjoia2FyeWEtc2VydmVyIn0.Dvq44bd0RDdQeAGBP39bU-Hsedd_PJs2XpIbPNuTeR0'}
    # r_api= requests.get(url = urll, headers = hederr)
    # print(r_api)
    # request_data = r_api.content
    # rate, data = scipy.io.wavfile.read(request_data)
    # b = np.array(request_data)

    # print(request_data)
    # # convert binary to FileStorage
    # convertedFile = FileStorage(stream=request_data, filename='convertedFilename')
    # print(type(convertedFile))
    # print(convertedFile)


    #get new assignment
    # import requests
    # karya_tokenid = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImExNWE0MGQ0In0.eyJzdWIiOiIyODE0NzQ5NzY3MTA3MDMiLCJlbnRpdHkiOiJ3b3JrZXIiLCJpYXQiOjE2NjI5MDI1NTIsImV4cCI6MTY2NTQ5NDU1MiwiYXVkIjoia2FyeWEtc2VydmVyIiwiaXNzIjoia2FyeWEtc2VydmVyIn0.Dvq44bd0RDdQeAGBP39bU-Hsedd_PJs2XpIbPNuTeR0'
    urll = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignments?type=new&from=2021-05-11T07:23:40.654Z'
    # hederr= {'karya-id-token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImExNWE0MGQ0In0.eyJzdWIiOiIyODE0NzQ5NzY3MTA3MDMiLCJlbnRpdHkiOiJ3b3JrZXIiLCJpYXQiOjE2NjI5MDI1NTIsImV4cCI6MTY2NTQ5NDU1MiwiYXVkIjoia2FyeWEtc2VydmVyIiwiaXNzIjoia2FyeWEtc2VydmVyIn0.Dvq44bd0RDdQeAGBP39bU-Hsedd_PJs2XpIbPNuTeR0'}
    hederr = {'karya-id-token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImExNWE0MGQ0In0.eyJzdWIiOiIxNjc3NzIzNSIsImVudGl0eSI6IndvcmtlciIsImlhdCI6MTY2MzU5MDA2NiwiZXhwIjoxNjY2MTgyMDY2LCJhdWQiOiJrYXJ5YS1zZXJ2ZXIiLCJpc3MiOiJrYXJ5YS1zZXJ2ZXIifQ.UGpR4dGasm-FQNjHMHT3Ivx3-noKAF-R04vdFOAXJiE'}
    r = requests.get(headers = hederr, url = urll) 

    r.json()["assignments"]
    r_j = r.json()

    id_find = r_j['assignments']
    new_dict = [item['id'] for item in id_find]
    # new_dict

    answer = ", ".join(new_dict)
    # answer
    hederr= {'karya-id-token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImExNWE0MGQ0In0.eyJzdWIiOiIxNjc3NzIzNSIsImVudGl0eSI6IndvcmtlciIsImlhdCI6MTY2MzU5MDA2NiwiZXhwIjoxNjY2MTgyMDY2LCJhdWQiOiJrYXJ5YS1zZXJ2ZXIiLCJpc3MiOiJrYXJ5YS1zZXJ2ZXIifQ.UGpR4dGasm-FQNjHMHT3Ivx3-noKAF-R04vdFOAXJiE'}

    rl = 'https://karyanltmbox.centralindia.cloudapp.azure.com/assignment/id/input_file'
    for new_d in new_dict:
        new_url = rl.replace("id", new_d )
        # print(str(new_url))
        # for ulr in :
        ra = requests.get(url = new_url, headers = hederr) 
        aa= ra.content
        # print(aa)
        projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo, 'projects', 'userprojects', 'transcriptions')
        projectowner = 'nmathur54'
        activeprojectname = 'PROJECT_1'
        current_username = 'nmathur54'
        filedata = FileStorage(io.BytesIO(aa), filename='myfile.tgz')
        # print(type(aa))
        # with BytesIO(gzip.decompress(aa)) as fh:
        #     filedata  = tarfile.TarFile(fileobj=fh)
             
            # tarf = tarfile.open(fileobj=fh)
            # op = tf.next()
            # print(type(tf))
            # namelist=tarf.getnames()
            # file = FileStorage(tarf)
            # print(file)

            # file = FileStorage(ra)
            # print(file) 
            # for mebers in tf.getmembers():
            #     f = tf.extractfile(mebers)
            #     print(f)

            # print(type(tf))
            # print(tf)
            # print(tf.getmembers())
            # print(tf.getnames())
            # fileName = tf.getnames()[0]
            # print(fileName)
            # fileObj = tf.extractfile(fileName)
            # print(type(fileObj))
            # print(fileObj)
            # print(tf.gettarinfo())
            # print()
            # op = tf.extractall('')
            # print(type(op))
        #     # print("File Saved", op)
        #     # with open(tf, 'wb') as outfile:
        #     #    pp =  outfile.write(tf.read())
        #     #    print(pp)


        audioformat_dict = {
                                "projects": "", "userprojects": "",
                                "transcriptions":"",
                                "activeprojectname":"",
                                "current_username": "",
                                "speakerId":"",
                                "new_audio_files":""}










    '''projects, userprojects, transcriptions = getdbcollections.getdbcollections(mongo, 'projects', 'userprojects', 'transcriptions')
    projectowner = 'nmathur54'
    activeprojectname = 'PROJECT_1'
    current_username = 'nmathur54'
    # filedata = FileStorage(io.BytesIO(request_data), filename='myfile.tgz')

    with BytesIO(gzip.decompress(r_api.content)) as fh:
        filedata = tarfile.TarFile(fileobj=fh)
        # tf.extractall('/home/kmi/Desktop/test')
        
        print("File Saved" , filedata)'''

    # with BytesIO(gzip.decompress(r_api.content)) as fh:
    #     tf = tarfile.TarFile(fileobj=fh)
    #     tf.extractall('/home/kmi/Desktop/test')
    #     print("File Saved")

    # new_audio_file = {'audiofile': filedata}
    # speakerId = '1234567890'

    # audiodetails.saveaudiofiles(mongo,
    #                     projects,
    #                     userprojects,
    #                     transcriptions,
    #                     projectowner,
    #                     activeprojectname,
    #                     current_username,
    #                     speakerId,
    #                     new_audio_file)

    """mapping of this function is with the 'uploadaudiofiles' route.
    Args:
        mongo: instance of PyMongo
        projects: instance of 'projects' collection.
        userprojects: instance of 'userprojects' collection.
        transcriptions: instance of 'transcriptions' collection.
        projectowner: owner of the project.
        activeprojectname: name of the project activated by current active user.
        current_username: name of the current active user.
        speakerId: speaker ID for this audio.
        new_audio_file: uploaded audio file details."""

    # audioformat_dict = {
    #                     "projects": "", "userprojects": "",
    #                     "transcriptions":"",
    #                     "activeprojectname":"",
    #                     "current_username": "",
    #                     "speakerId":"",
    #                     "new_audio_files":""}

    # # data, samplerate = sf.read(io.BytesIO(response))
    # data, samplerate = sf.read(io.BytesIO(request_data))
    # rate, data = read(BytesIO(request_data))
    # karyaaccesscodedetails.insert_one({"rate": rate,"data": data.tolist()})
    # return_audio_obj = karyaaudiodetails.insert (audioformat_dict)
    # print ('Return object', return_audio_obj)
    # mongodb_info = mongo.db.fetchkaryaaudio
    # update_audio_data = {"new_audio_files": request_data}
    # print ('Update Data', update_audio_data)
    # mongodb_info.update_one({}, {"$set": update_audio_data})




    # karyaaudiodetails.insert_one({()})
    return render_template("fetch_karya_audio.html")

