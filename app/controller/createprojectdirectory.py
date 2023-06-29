"""Module to create new directory/folder."""

import os
import shutil

def createprojectdirectory(base_dir, folder_name):
    folder_path = os.path.join(base_dir, 'lifequesdownload', folder_name)
    if (os.path.exists(folder_path)):
        shutil.rmtree(folder_path)
    os.mkdir(folder_path)

    return folder_path
