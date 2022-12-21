"""Module to create the zip file."""

import os
import glob
from zipfile import ZipFile

def createzip(files_path, activeprojectname):
    # printing the list of all files to be zipped 
    files = glob.glob(files_path+'/*')
    # print('Following files will be zipped:')
    # for file_name in files: 
    #     print(file_name) 
    zip_file_path = os.path.join(files_path, activeprojectname+'.zip')
    # writing files to a zipfile 
    with ZipFile(zip_file_path, 'w') as zip:
        # writing each file one by one 
        for file in files: 
            zip.write(file, os.path.basename(file))
    print('All files zipped successfully!')

    # deleting all files from storage
    # for f in files:
    #     os.remove(f)

    return zip_file_path
    