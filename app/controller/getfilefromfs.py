"""Module to get the file from fs collection."""

import gridfs
import os

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
    print(file_type, file_id)
    fs =  gridfs.GridFS(mongo.db)                       # creating GridFS instance to get required files                
    file = fs.find_one({ 'fileId': file_id })
    # audioFolder = os.path.join(basedir, 'static/audio')
    # if (os.path.exists(audioFolder)):
    #     shutil.rmtree(audioFolder)
    # os.mkdir(audioFolder)
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
