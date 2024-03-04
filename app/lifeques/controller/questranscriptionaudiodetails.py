import os
import shutil
import gridfs
from pprint import pprint

def getquesaudiofilefromfs(mongo,
                        basedir,
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
    file = fs.find_one({ file_type: file_id })
    audioFolder = os.path.join(basedir, 'static/audio')
    if (os.path.exists(audioFolder)):
        shutil.rmtree(audioFolder)
    os.mkdir(audioFolder)
    if (file is not None and
        'audio' in file.contentType):
        file_name = file.filename
        audiofile = fs.get_last_version(filename=file_name)
        audiofileBytes = audiofile.read()
        if len(audiofileBytes) != 0:
            file_path = os.path.join('static', 'audio', file_name)
            save_file_path = os.path.join(basedir, file_path)
            open(save_file_path, 'wb').write(audiofileBytes)
    else:
        file_path = ''

    return file_path

def getquesaudiotranscriptiondetails(questionnaires, quesId):
    
    transcription_data = {}
    transcription_regions = []
    gloss = {}
    pos = {}
    # print(quesId)
    try:
        # t_data = questionnaires.find_one({ 'quesId': quesId },
        #                                 { '_id': 0, 'prompt.Transcription.textGrid.sentence': 1 })
        t_data = questionnaires.find_one({ 'quesId': quesId },
                                        { '_id': 0, 'prompt.Audio.textGrid.sentence': 1 })
        # print('t_data!!!!!', t_data)
        # t_data = t_data['prompt']['Transcription']
        t_data = t_data['prompt']['Audio']
        if t_data is not None:
            transcription_data = t_data['textGrid']
        # pprint(transcription_data)
        sentence = transcription_data['sentence']
        for key, value in sentence.items():
            # print(key, value)
            transcription_region = {}
            # gloss = {}
            # transcription_region['sentence'] = {}
            transcription_region['data'] = {}
            transcription_region['boundaryID'] = key
            transcription_region['start'] = sentence[key]['start']
            transcription_region['end'] = sentence[key]['end']
            # transcription_region['sentence'] = {key: value}
            transcription_region['data'] = {'sentence': {key: value}}
            transcription_regions.append(transcription_region)
    except:
        pass
    
    # pprint(transcription_regions)
    # print(type(transcription_regions))
    return transcription_regions

def getquesfilefromfs(mongo,
                        basedir,
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
    file = fs.find_one({ file_type: file_id })
    audioFolder = os.path.join(basedir, 'static/audio')
    # if (os.path.exists(audioFolder)):
    #     shutil.rmtree(audioFolder)
    if not (os.path.exists(audioFolder)):
        os.mkdir(audioFolder)
    if (file is not None):
        file_name = file.filename
        audiofile = fs.get_last_version(filename=file_name)
        audiofileBytes = audiofile.read()
        if len(audiofileBytes) != 0:
            file_path = os.path.join('static', 'audio', file_name)
            save_file_path = os.path.join(basedir, file_path)
            open(save_file_path, 'wb').write(audiofileBytes)
    else:
        file_path = ''
        file_name = ''

    return (file_path, file_name)

def getquesfiletranscriptiondetails(questionnaires, quesId, lang, prompt_type,):
    
    transcription_data = {}
    transcription_regions = []
    gloss = {}
    pos = {}
    # print(quesId)
    try:
        text_grid_path = '.'.join(['prompt',
                                    'content',
                                    lang,
                                    prompt_type,
                                    'textGrid',
                                    'sentence'])
        # t_data = questionnaires.find_one({ 'quesId': quesId },
        #                                 { '_id': 0, 'prompt.Transcription.textGrid.sentence': 1 })
        t_data = questionnaires.find_one({ 'quesId': quesId },
                                        { '_id': 0, text_grid_path: 1 })
        # print('t_data!!!!!', t_data)
        # t_data = t_data['prompt']['Transcription']
        t_data = t_data['prompt']['content'][lang][prompt_type]
        # print(t_data)
        if t_data is not None:
            transcription_data = t_data['textGrid']
        # pprint(transcription_data)
        sentence = transcription_data['sentence']
        for key, value in sentence.items():
            # print(key, value)
            transcription_region = {}
            # gloss = {}
            # transcription_region['sentence'] = {}
            # print('155', transcription_region)
            transcription_region['data'] = {}
            # print('155', transcription_region)
            transcription_region['boundaryID'] = key
            # print('155', transcription_region)
            transcription_region['start'] = sentence[key]['startindex']
            transcription_region['end'] = sentence[key]['endindex']
            # transcription_region['sentence'] = {key: value}
            transcription_region['data'] = {'sentence': {key: value}}
            # print('155', transcription_region)
            transcription_regions.append(transcription_region)
    except Exception as e:
        print(e)
    
    # pprint(transcription_regions)
    # print(type(transcription_regions))
    return transcription_regions
