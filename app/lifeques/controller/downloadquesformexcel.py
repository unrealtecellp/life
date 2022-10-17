"""Module to download blank ques form in excel."""

import os
import json

def downloadquesformexcel(questionnaire,
                            basedir,
                            activeprojectname):

    def preprocess_csv_excel(lexicon):
        # pprint(lexicon)
        df = pd.json_normalize(lexicon)
        columns = df.columns
        drop_cols = [c for c in df.columns if c.startswith('langscripts.')]
        drop_cols.append ('lexemedeleteFLAG')
        drop_cols.append ('grammaticalcategory')
        drop_cols.append ('projectname')

        if 'gloss' in columns:
            drop_cols.append ('gloss')
        drop_oldsense = [c for c in df.columns if c.startswith('Sense.')]
        drop_oldvariant = [c for c in df.columns if c.startswith('Variant.')]
        drop_oldallomorph = [c for c in df.columns if c.startswith('Allomorph.')]
        drop_oldscript = [c for c in df.columns if c.startswith('Lexeme Form Script')]
        drop_files = [c for c in df.columns if c.startswith('filesname.')]

        drop_cols.extend(drop_oldsense)
        drop_cols.extend(drop_oldvariant)
        drop_cols.extend(drop_oldallomorph)
        drop_cols.extend(drop_oldscript)
        drop_cols.extend(drop_files)

        print(list(df.columns))
        print(drop_cols)
        df.drop(columns=drop_cols, inplace=True)

        return df

    def generate_xlsx(write_path, lexicon):
        df = preprocess_csv_excel(lexicon)
        # df.drop([0], inplace=True)
        f_w = open (write_path, 'wb')
        df.to_excel(f_w, index=False, engine='xlsxwriter')

    def download_lexicon(lex_json, write_path, 
        output_format='xlsx'):
        file_ext_map = {'xlsx': '.xlsx'}
        
        # pprint(lex_json)
        metadata = lex_json[0]
        project = metadata['projectname']

        lexicon = lex_json[1:]
        # pprint(lexicon)
        if output_format == 'xlsx':
            file_ext = file_ext_map[output_format]
            write_file = os.path.join(write_path, 'lexicon_'+project+file_ext)
            generate_xlsx(write_file, lexicon)
        else:
            print ('File type\t', output_format, '\tnot supported')
            print ('Supported File Types', file_ext_map.keys())        

    ques_dir = basedir
    working_dir = basedir+'/download'
    ques = questionnaire.find_one({"quesId": activeprojectname+"_dummy_ques"})
        out_form = 'xlsx'
        download_lexicon(lex, working_dir, out_form)

    files = glob.glob(basedir+'/download/*')
     
    with ZipFile('download.zip', 'w') as zip:
        # writing each file one by one 
        for file in files: 
            zip.write(file, os.path.join(projectname, os.path.basename(file)))
    print('All files zipped successfully!')

    # deleting all files from storage
    for f in files:
        print(f)
        os.remove(f)
    
    return send_file('../download.zip', as_attachment=True)
    # return 'OK'