"""Module to get the file from fs collection."""

import gridfs
import os
import shutil

def getfilefromfs(mongo,
                    folder_path,
                    file_id,
                    file_type):
    """get file from fs collection save it to local storage 'static' folder

    Args:
        mongo (_type_): _description_
        basedir (_type_): _description_
        file_id (_type_): _description_
        file_type (_type_): _description_

    Returns:
        _type_: _description_
    """
    # print(file_type, file_id)
    # creating GridFS instance to get required files
    fs =  gridfs.GridFS(mongo.db)
    if file_type == 'audio':
        file = fs.find_one({ 'audioId': file_id })
    else:
        file = fs.find_one({ 'fileId': file_id })
    # audioFolder = os.path.join(basedir, 'static/audio')
    # audioFolder = folder_path
    # if (os.path.exists(audioFolder)):
    #     shutil.rmtree(audioFolder)
    # os.mkdir(audioFolder)
    print ('file', file)
    print ('file_id', file_id)
    print ('content type', file.contentType)
    print ('file_type', file_type)
    print ('file_type in file.contentType', file_type in file.contentType)
    if (file is not None and
        file_type in file.contentType):
        file_name = file.filename
        audiofile = fs.get_last_version(filename=file_name)
        audiofileBytes = audiofile.read()
        if len(audiofileBytes) != 0:
            file_path = os.path.join(folder_path, file_name)
            # save_file_path = os.path.join(basedir, file_path)
            save_file_path = file_path
            open(save_file_path, 'wb').write(audiofileBytes)
    else:
        file_path = ''

    return file_path
