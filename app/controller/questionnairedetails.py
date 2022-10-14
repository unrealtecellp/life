"""Module to save the uploaded questionnaire file from 'newquestionnaire' route."""


import json
import os
import shutil
from datetime import datetime
import re
from pprint import pprint
import gridfs
from flask import flash
import pandas as pd
from app.controller import getcommentstats
import io

def savequesfiles(mongo,
                    projects,
                    userprojects,
                    questionnaires,
                    projectowner,
                    activeprojectname,
                    current_username,
                    new_ques_file,
                    **kwargs
                ):
    """mapping of this function is with the 'uploadaudiofiles' route.

    Args:
        mongo: instance of PyMongo
        projects: instance of 'projects' collection.
        userprojects: instance of 'userprojects' collection.
        transcriptions: instance of 'transcriptions' collection.
        projectowner: owner of the project.
        activeprojectname: name of the project activated by current active user.
        current_username: name of the current active user.
        new_ques_file: uploaded questionnaire file details.
    """

    text_grid = {
            "discourse": {},
            "sentence": {},
            "word": {},
            "phoneme": {}
        }
    # save audio file details in transcriptions collection
    new_ques_details = {
        "username": projectowner,
        "projectname": activeprojectname,
        "updatedBy": current_username,
        "quesdeleteFLAG": 0,
        "quesverifiedFLAG": 0,
        "quessaveFLAG": 0,
        "prompt": ""
    }
    try:
        print(new_ques_file)
        ques_data_df = pd.read_excel(io.BytesIO(new_ques_file['quesfile'].read()), dtype=str)
        df_header = list(ques_data_df.columns)
        print(df_header)
    except Exception as e:
        print(e)
        flash(f"ERROR")                    
