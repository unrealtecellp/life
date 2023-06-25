"""Module to create the zip file."""

import os
import glob
from zipfile import ZipFile
import tarfile
import subprocess

def createzip(files_path, activeprojectname):
    cwd = os.getcwd()
    # print('ACTUAL_1_CWD:', cwd)
    os.chdir(files_path)
    # print('TEMP_CWD:', os.getcwd())
    # printing the list of all files to be zipped
    files = glob.glob(files_path+'/*')
    # print('Following files will be zipped:')
    # for file_name in files: 
    #     print(file_name) 
    # zip_file_path = os.path.join(files_path, activeprojectname+'.tar.gz')
    zip_file_path = activeprojectname+'.tgz'
    # writing files to a zipfile 
    # with ZipFile(zip_file_path, 'w') as zip:
    #     # writing each file one by one 
    #     for file in files:
    #         zip.write(file, os.path.basename(file))

    with tarfile.open(zip_file_path, "w:gz") as tar:
        # for file in files:
        for file in sorted(os.listdir()):
            # print(file)
            tar.add(file)
    # print('All files zipped successfully!')
    os.chdir(cwd)
    # print('ACTUAL_2_CWD:', os.getcwd())

    # deleting all files from storage
    # for f in files:
    #     os.remove(f)

    return zip_file_path
    