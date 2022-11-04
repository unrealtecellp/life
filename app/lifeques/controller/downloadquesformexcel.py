"""Module to download blank ques form in excel."""

import os
import json
import glob
from zipfile import ZipFile
import pandas as pd

def downloadquesformexcel(questionnaires,
                            basedir,
                            activeprojectname):

    def preprocess_csv_excel(question):
        # pprint(lexicon)
        df = pd.json_normalize(question)
        # columns = df.columns
        # drop_cols = [c for c in df.columns if c.startswith('langscripts.')]
        # drop_cols.append ('lexemedeleteFLAG')
        # drop_cols.append ('grammaticalcategory')
        # drop_cols.append ('projectname')

        # if 'gloss' in columns:
        #     drop_cols.append ('gloss')
        # drop_oldsense = [c for c in df.columns if c.startswith('Sense.')]
        # drop_oldvariant = [c for c in df.columns if c.startswith('Variant.')]
        # drop_oldallomorph = [c for c in df.columns if c.startswith('Allomorph.')]
        # drop_oldscript = [c for c in df.columns if c.startswith('Lexeme Form Script')]
        # drop_files = [c for c in df.columns if c.startswith('filesname.')]

        # drop_cols.extend(drop_oldsense)
        # drop_cols.extend(drop_oldvariant)
        # drop_cols.extend(drop_oldallomorph)
        # drop_cols.extend(drop_oldscript)
        # drop_cols.extend(drop_files)

        # print(list(df.columns))
        # print(drop_cols)
        # df.drop(columns=drop_cols, inplace=True)

        return df

    def generate_xlsx(write_path, question):
        df = preprocess_csv_excel(question)
        # df.drop([0], inplace=True)
        f_w = open (write_path, 'wb')
        df.to_excel(f_w, index=False, engine='xlsxwriter')

    def download_ques(ques_json,
                        write_path, 
                        output_format='xlsx'):
        file_ext_map = {'xlsx': '.xlsx'}
        
        metadata = ques_json[0]
        project = metadata['projectname']

        question = ques_json[1:]
        if output_format == 'xlsx':
            file_ext = file_ext_map[output_format]
            write_file = os.path.join(write_path, 'questionnaireform_'+project+file_ext)
            generate_xlsx(write_file, question)
        else:
            print ('File type\t', output_format, '\tnot supported')
            print ('Supported File Types', file_ext_map.keys())        

    # code starts from here
    ques = []
    ques.append({'projectname': activeprojectname})
    # print(activeprojectname+"_dummy_ques")
    dummy_ques = questionnaires.find_one({"quesId": activeprojectname+"_dummy_ques"}, {
        "_id": 0,
        "username": 0,
        "projectname": 0,
        "lastUpdatedBy": 0,
        "quesdeleteFLAG": 0,
        "quessaveFLAG": 0
    })
    # print('LINE: 77', dummy_ques)
    dummy_ques['quesId'] = ''
    # print('LINE: 79', dummy_ques)
    ques.append(dummy_ques)
    working_dir = basedir+'/quesdownload'
    if (not os.path.exists(working_dir)):
        os.mkdir(working_dir)
    out_form = 'xlsx'
    # print(ques, working_dir, out_form
    download_ques(ques, working_dir, out_form)

    files = glob.glob(basedir+'/quesdownload/*')
     
    with ZipFile('questionnaireform.zip', 'w') as zip:
        # writing each file one by one 
        for file in files: 
            zip.write(file, os.path.join(activeprojectname, os.path.basename(file)))
    print('All files zipped successfully!')

    # deleting all files from storage
    for f in files:
        # print(f)
        os.remove(f)
    
    # return send_file('../download.zip', as_attachment=True)
    # return 'OK'