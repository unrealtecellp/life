from app.controller import (
    life_logging
)
from zipfile import ZipFile
import pandas as pd
import io
import re

logger = life_logging.get_logger()

def read_zip(tagsets, zip_file):
    # logger.debug('tagsets: %s\nzip_file: %s', tagsets, zip_file)
    tag_set = {}
    message = 'Working on zip file'
    try:
        with ZipFile(zip_file) as myzip:
            # logger.debug('myzip: %s', myzip)
            for file_name in myzip.namelist():
                # logger.debug('file_name: %s', file_name)
                with myzip.open(file_name) as myfile:
                    try:
                        if file_name.endswith('.tsv'):
                            tagset_project_name = file_name.rsplit('.', 1)[0].replace('.', '_')
                            tags_df = pd.read_csv(io.BytesIO(myfile.read()), sep='\t', dtype=str)
                        elif file_name.endswith('.csv'):
                            tagset_project_name = file_name.rsplit('.', 1)[0].replace('.', '_')
                            tags_df = pd.read_csv(io.BytesIO(myfile.read()), sep='\t', dtype=str)
                        elif file_name.endswith('.xlsx'):
                            tagset_project_name = file_name.rsplit('.', 1)[0].replace('.', '_')
                            tags_df = pd.read_excel(io.BytesIO(myfile.read()), dtype=str)
                        else:
                            message = f"Please upload valid tagset file format(.tsv, .csv. .xlsx)."
                            return (False, message, tag_set)
                        # logger.debug('tags_df: %s', tags_df)
                    except:
                        logger.exception("")
                        message = f"File: {file_name} is not in correct format. Please check"
                        return (False, message, tag_set)

                    # check if tagset already exist
                    if tagsets.find_one({"projectname": tagset_project_name},
                                        {'_id' : 0, "projectname": 1}) != None:
                        message = f'File Name : {tagset_project_name} already exist!'
                        return (False, message, tag_set)
                    
                if (len(tags_df.columns) >= 2):
                    for i in range(len(tags_df)):
                        # reading column 'Category', and 'Tags'
                        # logger.debug("tags_df.iloc[i, 0]: %s", tags_df.iloc[i, 0])
                        # logger.debug("tags_df.iloc[i, 1]: %s", tags_df.iloc[i, 1])
                        # logger.debug("type(tags_df.iloc[i, 1]: %s", type(tags_df.iloc[i, 1]))
                        if (str(tags_df.iloc[i, 1]) == 'nan'):
                            tag_set[tags_df.iloc[i, 0]] = ['']
                        else:
                            tag_set[tags_df.iloc[i, 0]] = re.sub(' ', '', tags_df.iloc[i, 1]).split(',')
                    message = f"Successfully read tagset files."
    except:
        logger.exception("")
    # logger.debug('tag_set: %s', tag_set)
    return (True, message, tag_set)
