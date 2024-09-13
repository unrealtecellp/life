import os
import pickle
from xml.etree import ElementTree as ET
import pandas as pd
from datetime import datetime
import re
from zipfile import ZipFile
import io
from app.controller import (
    life_logging
)
from app.lifeques.controller import savequespromptfile
from werkzeug.datastructures import FileStorage

logger = life_logging.get_logger()

def quesmetadata():
    # create quesId
    Id = re.sub(r'[-: \.]', '', str(datetime.now()))
    quesId = 'Q'+Id

    return quesId

def lifeuploader(fileFormat, uploadedFileContent, basedir, allques, field_map = {}):
    lang_script_map = {
    'ipa': 'ipa',
    'hin': 'Deva',
    'guj': 'Gujr',
    'pun': 'Guru',
    'ban': 'Beng',
    'ass': 'Beng',
    'odi': 'Orya',
    'kan': 'Knda',
    'tam': 'Taml',
    'tel': 'Telu',
    'mal': 'Mlym',
    'mar': 'Deva',
    'bod': 'Deva',
    'kon': 'Deva',
    'nep': 'Deva',
    'mai': 'Deva',
    'mag': 'Deva',
    'bho': 'Deva',
    'awa': 'Deva',
    'har': 'Deva',
    'bra': 'Deva',
    'bun': 'Deva',
    'anp': 'Deva'
    }

    def get_lift_map():
        map = {
            'grammatical-info': 'grammaticalcategory',
            'lexical-unit': 'headword',
            'lexical-unit-form': 'Lexical Form',
            'pronunciation': 'Pronunciation',
            'gloss': 'Gloss',
            'example': 'Example',
            'translation':'Free Translation',
            'definition': 'Definition',
            'note': 'Encyclopedic Information',
            'semantic-domain': 'Semantic Domain',
            'variant': 'VariantNew.Variant 1',
            'relation': ''
        }

        return map


    def get_script_name(wordform):
        lang_name = wordform.attrib['lang']
        # print (lang_name)
        parts = lang_name.split('-')
        if len(parts) > 1:
            script_name = parts[1]
        else:
            script_name = lang_script_map.get(lang_name, lang_name)
        
        return script_name, lang_name

    def get_lang_name(wordform):
        lang_name_full = wordform.attrib['lang']
        # print (lang_name_full)
        lang_name = lang_name_full.split('-')[0]
        
        return lang_name, lang_name_full


    def get_scripts_map(lex_fields):
        scripts_map = {}
        # print (lex_fields)
        for lex_field in lex_fields:
            # print ('Lex field', lex_field)
            script_name = lex_field.split('.')[-1]
            if 'langscripts.headwordscript' in lex_field:
                scripts_map['langscripts.headwordscript'] = script_name
            elif 'langscripts.lexemeformscripts' in lex_field:
                if 'langscripts.lexemeformscripts' in scripts_map:
                    scripts_map['langscripts.lexemeformscripts'].append(script_name)
                else:
                    scripts_map['langscripts.lexemeformscripts']= [script_name]
            elif 'langscripts.glosslangs' in lex_field:
                if 'langscripts.glosslangs' in scripts_map:
                    scripts_map['langscripts.glosslangs'].append(script_name)
                else:
                    scripts_map['langscripts.glosslangs']= [script_name]
                # scripts_map.get('langscripts.glosslangs', []).append(script_name)
        # print(f"{'-'*80}\nIN get_scripts_map(lex_fields) function\n\nscript_map:\n{scripts_map}")
        
        return scripts_map



    def map_lift(file_stream, field_map, lex_fields):
        # print(f"{'-'*80}\nIN map_lift(file_stream, field_map, lex_fields) function\n")
        mapped_lift = {}
        all_mapped = True

        life_scripts_map = get_scripts_map(lex_fields)
        # print (life_scripts_map)

        if len(field_map) == 0:
            field_map = get_lift_map()
        
        # print(f"{'-'*80}\nget_lift_map():\n{field_map}")
        # print(f"{'-'*80}\nFILE STREAM TYPE:{type(file_stream)}")
        # exit()
        # tree = ET.parse(file_stream)
        root = ET.fromstring(file_stream)
        # print(f"TYPE OF TREE: {type(tree)}")
        # exit()
        # root = tree.getroot()
        # print(f"{'-'*80}\nroot:\n{root}")
        # exit()
        entries = root.findall('.//entry')
        # print(f"entries:\n{entries}")
        # exit()
        mapped_life_langs_lexeme_form = []
        unmapped_lift_langs_lexeme_form = []

        mapped_life_langs_gloss = []
        unmapped_lift_langs_gloss = []

        life_headword_script = life_scripts_map['langscripts.headwordscript']
        life_lexeme_form_scripts = life_scripts_map['langscripts.lexemeformscripts']
        life_gloss_langs = life_scripts_map['langscripts.glosslangs']

        highest_sense_num = 0
        for entry in entries:
            # pd_row = {}
            for entry_part in entry:
                sense_num = 0
                entry_part_tag = entry_part.tag
                if entry_part_tag != 'entry':
                    # print (entry_part_tag)
                    if entry_part_tag == 'lexical-unit':
                        life_key_headword = field_map[entry_part_tag]

                        for wordform in entry_part:
                            lift_script_name, lift_lang_name = get_script_name(wordform)
                            lift_tag = './lexical-unit/form[@lang="'+lift_lang_name+'"]'

                            if lift_script_name == life_headword_script:
                                if lift_tag not in mapped_lift:
                                    mapped_lift[lift_tag] = life_key_headword
                                
                                if lift_script_name not in mapped_life_langs_lexeme_form:
                                    mapped_life_langs_lexeme_form.append(lift_script_name)

                            elif lift_script_name in life_lexeme_form_scripts:                            
                                # mapped_lift[lift_tag] = life_key_other_lexemes+'.'+lift_script_name
                                mapped_lift[lift_tag] = lift_script_name
                                if lift_script_name not in mapped_life_langs_lexeme_form:
                                    mapped_life_langs_lexeme_form.append(lift_script_name)

                            else:
                                if lift_tag not in unmapped_lift_langs_lexeme_form:
                                    unmapped_lift_langs_lexeme_form.append(lift_tag)
                    elif entry_part_tag == 'sense':
                        sense_num += 1
                        
                        if sense_num > highest_sense_num:
                            highest_sense_num = sense_num

                        for sense_part in entry_part:                        
                            sense_part_tag = sense_part.tag             
                            # print (sense_part_tag)
                            life_key_sense = field_map[sense_part_tag]

                            if sense_part_tag == 'gloss' or sense_part_tag == 'definition' or sense_part_tag == 'example':
                                lift_lang_name, lift_full_lang = get_script_name(sense_part)
                                lift_sense_tag = './sense/'+sense_part_tag+'[@lang="'+lift_full_lang+'"]'
                                
                                if lift_lang_name in life_gloss_langs:
                                    mapped_lift[lift_sense_tag] = 'SenseNew.Sense '+str(sense_num)+'.'+life_key_sense + '.' + lift_lang_name
                                    if lift_lang_name not in mapped_life_langs_gloss:
                                        mapped_life_langs_gloss.append(lift_lang_name)
                                else:
                                    if lift_sense_tag not in unmapped_lift_langs_gloss:
                                        unmapped_lift_langs_gloss.append(lift_sense_tag)
                            elif sense_part_tag == 'grammatical-info':
                                life_key = field_map.get(sense_part_tag, [])
                                # lift_tag = './/entry/sense/'+sense_part_tag
                                # print (entry_part[0].tag)
                                # gram_categ = entry_part[0].attrib['value']

                                lift_tag = './sense/'+sense_part_tag#+'[@value="'+gram_categ+'"]'
                                if lift_tag not in mapped_lift:
                                    mapped_lift[lift_tag] = life_key
                            else:
                                life_key = field_map.get(sense_part_tag, [])
                                # lift_tag = './/entry/sense/'+sense_part_tag
                                lift_tag = './sense/'+sense_part_tag
                                mapped_lift[lift_tag] = 'SenseNew.Sense '+str(sense_num)+'.'+life_key_sense
                    
                    elif entry_part_tag == 'pronunciation':
                        life_key_pron = field_map[entry_part_tag]
                        for pronform in entry_part:
                            lift_lang_name, lift_full_lang = get_script_name(pronform)
                            lift_pron_tag = './pronunciation/form[@lang="'+lift_full_lang+'"]'
                            mapped_lift[lift_pron_tag] = life_key_pron
                                
                    else:
                        if 'trait' not in entry_part_tag:
                            life_key = field_map.get(entry_part_tag, [])
                            # lift_entry_tag = './/entry/'+entry_part_tag
                            lift_entry_tag = './'+entry_part_tag
                            mapped_lift[lift_entry_tag] = life_key
                # elif entry_part_tag == 'gloss':
        
        mapped_life_langs_lexeme_form_set = set(mapped_life_langs_lexeme_form)
        all_life_lexeme_form_scripts = set(life_lexeme_form_scripts)
        life_unmapped_lexeme_forms = all_life_lexeme_form_scripts - mapped_life_langs_lexeme_form_set
        # unmapped_lift_langs_lexeme_form = []
        

        mapped_life_langs_gloss_set = set(mapped_life_langs_gloss)
        all_life_gloss_langs = set(life_gloss_langs)
        life_unmapped_gloss_langs = all_life_gloss_langs - mapped_life_langs_gloss_set
        # unmapped_lift_langs_gloss = []
        # print ('Unmapped gloss', unmapped_lift_langs_gloss)

        headword_mapped = False
        life_all_mapped = mapped_lift.values()
        for life_key_mapped in life_all_mapped:
            if 'headword' in life_key_mapped:
                headword_mapped = True

        # if headword_mapped:
        for lift_unmapped_lexeme_form in unmapped_lift_langs_lexeme_form:
            # lift_unmapped_entry = './/entry/lexical-unit/form[@lang='+lift_unmapped_lexeme_form+']/text'
            mapped_lift[lift_unmapped_lexeme_form] = list(life_unmapped_lexeme_forms)

        for lift_unmapped_gloss in unmapped_lift_langs_gloss:
            mapped_lift[lift_unmapped_gloss] = list(life_unmapped_gloss_langs)

        # print (mapped_lift)
        # print (headword_mapped)

        if len (unmapped_lift_langs_lexeme_form) > 0 or len(unmapped_lift_langs_gloss) > 0:
            all_mapped = False
        
        # print(f"{'-'*80}\nheadword_mapped:\n{headword_mapped}\nall_mapped:\n{all_mapped}\nmapped_lift:\n{mapped_lift}\nroot:\n{root}")

        return headword_mapped, all_mapped, mapped_lift, root


    def get_sense_col(lift_tag, field_name, lang_name):
        all_cols = []
        sense_num = 0
        for sense in lift_tag:
            sense_num+=1
            df_col = 'SenseNew.Sense '+str(sense_num)+'.'+field_name+'.'+lang_name
            all_cols.append(df_col)
        return all_cols


    def lift_to_df (root, field_map, lex_fields):
        # print(f"{'-'*80}\nIN lift_to_df (root, field_map, lex_fields) function\n")
        data = pd.DataFrame(columns=lex_fields)
        # lex_fields_without_sense = [lex_field for lex_field in lex_fields if 'sense' not in lex_field]

        life_scripts_map = get_scripts_map(lex_fields)
        # print (life_scripts_map)

        # if len(field_map) == 0:
        lift_life_field_map = get_lift_map()
        # print(f"{'-'*80}\nIN lift_to_df (root, field_map, lex_fields) function: get_lift_map():\n{lift_life_field_map}")
        
        entries = root.findall('.//entry')

        # print (f"{'-'*80}\nIN lift_to_df (root, field_map, lex_fields) function: {field_map}")

        # highest_sense_num = 0
        for entry in entries:
            df_row = {}
            for lift_tag, life_key in field_map.items():
                if len(life_key) > 0:
                    if 'lexical-unit' in lift_tag:
                        txt_entry = entry.find(lift_tag+'/text')

                        if not txt_entry is None:
                            txt = txt_entry.text
                        
                        if 'headword' in life_key:
                            df_row['headword'] = txt
                        else:
                            df_row['Lexeme Form.'+life_key] = txt
                    
                    elif 'pronunciation' in lift_tag:
                        txt_entry = entry.find(lift_tag+'/text')
                        if not txt_entry is None:
                            txt = txt_entry.text
                            

                        df_row[life_key] = txt

                    elif '@lang' in lift_tag:
                        sense_num = 0
                        all_sense = entry.findall(lift_tag)
                        for sense in all_sense:
                            sense_num+=1                    
                            if 'gloss' in lift_tag:
                                life_key_name = lift_life_field_map['gloss']
                            elif 'definition' in lift_tag:
                                life_key_name = lift_life_field_map['definition']
                            elif 'example' in lift_tag:
                                life_key_name = lift_life_field_map['example']

                            # print (sense.tag)
                            txt_entry = sense.find('text')

                            if not txt_entry is None:
                                txt = txt_entry.text

                            df_col = 'SenseNew.Sense '+str(sense_num)+'.'+life_key_name+'.'+life_key
                            df_row[df_col] = txt
                    
                    elif 'grammatical-info' in lift_tag:
                        gram_info_tag = entry.find(lift_tag)

                        if not gram_info_tag is None:
                            try:
                                gram_info = gram_info_tag.attrib['value']
                            # print ('Gram info', gram_info)
                            except:
                                gram_info = ''
                        
                        df_row[life_key] = gram_info
                    
                    else:
                        # print (lift_tag)
                        txt_entry = entry.find(lift_tag)
                        life_key = lift_life_field_map[lift_tag]

                        if not txt_entry is None:
                            txt = txt_entry.text
                            

                        df_row[life_key] = txt

            data = data.append(df_row, ignore_index=True)
        
        data.fillna('', inplace=True)
        
        headword_mapped = True
        all_mapped = True

        # print(f"{'-'*80}\nIN lift_to_df (root, field_map, lex_fields) FUNCTION\n\nheadword_mapped\n{headword_mapped}\n\nall_mapped:\n{all_mapped}\n\ndata:\n{data}\n\nroot:\n{root}")
        # print(f"{'-'*80}\nIN lift_to_df (root, field_map, lex_fields) FUNCTION\n\nheadword_mapped\n{type(headword_mapped)}\n\nall_mapped:\n{type(all_mapped)}\n\ndata:\n{type(data)}\n\nroot:\n{type(root)}")

        return headword_mapped, all_mapped, data, root


    def prepare_lex(lexicon):
        # print(f"LINE 368: {lexicon}")
        df = pd.json_normalize(lexicon)
        columns = df.columns
        # drop_cols = [c for c in df.columns if c.startswith('langscripts.')]
        drop_cols = []
        # drop_cols.append ('lexemedeleteFLAG')
        # drop_cols.append ('grammaticalcategory')
        # drop_cols.append ('projectname')

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

        # print(f"drop_cols: {drop_cols}")
        df.drop(columns=drop_cols, inplace=True)

        return df


    def generate_all_possible_mappings(key_cols, val_cols):
        final_map = {}
        for key_col in key_cols:
            final_map[key_col] = list(val_cols)
        # print(f"{'-'*80}\nIN generate_all_possible_mappings(key_cols, val_cols) function\nFINAL MAP:\n{final_map}")
        return final_map


    def map_excel(file_stream, lex_fields):
        # print(f"{'-'*80}\nIN MAP EXCEL function map_excel(file_stream, lex_fields)")
        excel_data = pd.read_excel(file_stream, engine="openpyxl")
        # print(excel_data)
        excel_data_cols = set(excel_data.columns)
        lex_field_cols = set(lex_fields)
        # print(f"{'-'*80}\nexcel_data_cols:\n{excel_data.columns}")
        # print(f"{'-'*80}\nNUMBER OF ELEMENTS IN excel_data_cols: {len(excel_data_cols)}")
        # print(f"{'-'*80}\nNUMBER OF ELEMENTS IN lex_field_cols: {len(lex_field_cols)}")

        # print(f"{'-'*80}\nlex_field_cols-excel_data_cols:\n{lex_field_cols-excel_data_cols}")

        if excel_data_cols == lex_field_cols:
            # print(f"{'-'*80}\nexcel_data_cols == lex_field_cols")
            mapped = True
            headword_mapped = True
            return headword_mapped, mapped, {}, excel_data
        else:
            # print(f"{'-'*80}\nexcel_data_cols != lex_field_cols")
            headword_mapped = True
            mapped = False
            excel_remaining = excel_data_cols - lex_field_cols
            lex_remaining = lex_field_cols - excel_data_cols
            # print(f"{'-'*80}\nexcel_remaining:\n{excel_remaining}\n{'-'*80}\nlex_remaining:\n{lex_remaining}")
            field_map = generate_all_possible_mappings(excel_remaining, lex_remaining)
            # print(f"{'-'*80}\nheadword_mapped\n{headword_mapped}\n\nmapped:\n{mapped}\n\nfield_map:\n{field_map}\n\nexcel_data:\n{excel_data}")
            return headword_mapped, mapped, field_map, excel_data


    def upload_excel (excel_data, field_map, lex_fields):
        # excel_data = pd.read_excel(file_stream)
        final_data = excel_data.rename(columns=field_map)
        mapped = True
        headword_mapped = True

        return headword_mapped, mapped, final_data


    def upload_lexicon(lexicon, file_stream, format, field_map):
        lexicon = lexicon[1:]
        # print(f"{'-'*80}\nLEXICON:\n{lexicon}")
        norm_lex = prepare_lex(lexicon)
        # print(f"{'-'*80}\nNORM LEX:\n{norm_lex}")
        lex_fields = norm_lex.columns
        # print(f"{'-'*80}\nLEX FIELDS:\n{lex_fields}")
        # print(f"{'-'*80}\nFILE STREAM TYPE:{type(file_stream)}")

        if format == 'lift-xml':
            # print(f"{'-'*80}\nFIELD MAP:\n{len(field_map)}")
            if len(field_map) == 0:
                # print(f"{'-'*80}\nlift-xml: len(field_map) == 0")
                
                headword_mapped, all_mapped, field_map, root = map_lift(file_stream, field_map, lex_fields)
                
                if headword_mapped and all_mapped:
                    # print(f"{'-'*80}\nheadword_mapped and all_mapped")
                    headword_mapped, all_mapped, data, root = lift_to_df (root, field_map, lex_fields)
                    # print(f"{'-'*80}\nheadword_mapped:\n{type(headword_mapped)}\nall_mapped:\n{type(all_mapped)}\nmapped_lift/data:\n{type(data)}\nroot:\n{type(root)}")
                    return headword_mapped, all_mapped, data, root
                else:
                    # print(f"{'-'*80}\nheadword_mapped and all_mapped: NOT")
                    # print(f"{'-'*80}\nheadword_mapped:\n{type(headword_mapped)}\nall_mapped:\n{type(all_mapped)}\nmapped_lift/data:\n{type(field_map)}\nroot:\n{type(root)}")
                    return headword_mapped, all_mapped, field_map, root
            else:
                # print(f"{'-'*80}\nlift-xml: len(field_map) != 0")
                headword_mapped, all_mapped, life_df, root = lift_to_df (file_stream, field_map, lex_fields)
                # print (life_df.head())
                # print(life_df.loc[0,:])
                return headword_mapped, all_mapped, life_df
        elif format == 'xlsx':
            if len(field_map) == 0:
                # print(f"{'-'*80}\nxlsx: len(field_map) == 0")
                headword_mapped, all_mapped, field_map, df = map_excel(file_stream, lex_fields)
                return headword_mapped, all_mapped, field_map, df
            else:
                # print(f"{'-'*80}\nxlsx: len(field_map) != 0")
                headword_mapped, all_mapped, data = upload_excel(file_stream, field_map, lex_fields)
                return headword_mapped, all_mapped, data

    upload_file = uploadedFileContent
    
    format = fileFormat

    return upload_lexicon(allques, upload_file, format, field_map)

def enterquesfromuploadedfile(mongo, projects,
                                userprojects,
                                projectsform,
                                questionnaires,
                                projectowner,
                                activeprojectname,
                                quesdf,
                                mainfile,
                                current_username):
    projectname = activeprojectname
    project = projects.find_one({}, {projectname : 1})

    mainfile_name = mainfile.filename
    allFilesInZip=[]
    if mainfile_name.endswith('.zip'):
        with ZipFile(mainfile) as myzip:
            allFilesInZip = myzip.namelist()

    for index, row in quesdf.iterrows():
        filesToBeUploaded = {}
        uploadedFileQues = {
            "username": projectowner,
            "projectname": activeprojectname,
            "lastUpdatedBy": current_username,
            "quesdeleteFLAG": 0,
            "quessaveFLAG": 0,
            }
        quesId = str(row['quesId'])
        getquesId = None
        if (quesId == 'nan' or quesId == ''):
            quesId = quesmetadata()
        else:
            getquesId = questionnaires.find_one({ 'quesId' : quesId },
                                            {'_id' : 0, 'quesId' : 1, 'projectname': 1})
            if (getquesId == None):
                logger.info(f"quesId {quesId} not in DB")
                quesId = quesmetadata()
            else:
                if (getquesId['projectname'] != activeprojectname):
                    return (3, quesId)

        uploadedFileQues['quesId'] = quesId
        if (getquesId != None):
            questionnaires.update_one({ 'quesId': quesId }, { '$set' : uploadedFileQues })
        else:
            questionnaires.insert_one(uploadedFileQues)
        # logger.debug(f"uploadedFileQues: {uploadedFileQues}")
        all_columns = list(quesdf.columns)
        for column_name in all_columns:
            if (column_name == 'quessaveFLAG'):
                uploadedFileQues["quessaveFLAG"] = int(row[column_name])
            if (column_name not in uploadedFileQues):
                value = str(row[column_name])
                if ('[' in value and ']' in value):
                    if (value.startswith('[') and value.endswith(']')):
                        value = value.replace('[', '').replace(']', '').replace(' ', '').split(',')
                elif (value == 'nan'):
                    value = ''
                if ('text.000000' in column_name and 'textspan' in column_name):
                    startindex = '0'
                    endindex = str(len(value))
                    for p in range(3):
                        if (len(startindex) < 3):
                            startindex = '0'+startindex
                        if (len(endindex) < 3):
                            endindex = '0'+endindex
                    text_boundary_id = startindex+endindex
                    column_name = column_name.replace('000000', text_boundary_id)
                    column_name_startindex = '.'.join(column_name.split('.')[:-2])+'.startindex'
                    column_name_endindex = '.'.join(column_name.split('.')[:-2])+'.endindex'
                    uploadedFileQues[column_name_startindex] = startindex
                    uploadedFileQues[column_name_endindex] = endindex
                uploadedFileQues[column_name] = value

                ## for upload of file
                if ('filename' in column_name):
                    uploadfilename = str(row[column_name])
                    if uploadfilename in allFilesInZip:
                        file_type_info = column_name.split('.')
                        data_type = file_type_info[-2]
                        lang_script = file_type_info[2]
                        file_type = "_".join([
                            file_type_info[0], 
                            data_type, 
                            lang_script])
                        filesToBeUploaded[file_type] = uploadfilename
        # logger.debug(f"uploadedFileQues: {uploadedFileQues}")
        uploadedFileQuesKeysList = list(uploadedFileQues.keys())
        for ak in uploadedFileQuesKeysList:
            if ('text.000000' in ak and
                ('startindex' in ak or 'endindex' in ak)):
                del uploadedFileQues[ak]
        # logger.debug(f"uploadedFileQues: {uploadedFileQues}")
        projects.update_one({"projectname": activeprojectname},
                            {
                                "$set": {
                                    "lastActiveId."+current_username: {projectname: quesId}
                                },
                                "$addToSet": {
                                    "questionnaireIds": quesId
                                }
                            })

        questionnaires.update_one({ 'quesId': quesId },
                                    { '$set' : uploadedFileQues })

        # for upload of file
        with ZipFile(mainfile) as myzip:        
            for fileType, fileName in filesToBeUploaded.items():            
                with myzip.open(fileName) as myfile:
                    upload_file_full = {}
                    file_content = io.BytesIO(myfile.read())
                    upload_file_full[fileType] = FileStorage(file_content, filename = fileName)
                    savequespromptfile.savequespromptfile(mongo,
                                    projects,
                                    userprojects,
                                    projectsform,
                                    questionnaires,
                                    projectowner,
                                    activeprojectname,
                                    current_username,
                                    quesId,
                                    upload_file_full)

    return (4, '')

def queskeymapping(mongo, projects,
                    userprojects,
                    projectsform,
                    questionnaires,
                    activeprojectname,
                    projectowner,
                    basedir,
                    new_ques_file,
                    current_username):

    allques = []
    allques.append({'projectname': activeprojectname})
    for ques in questionnaires.find({'projectname': activeprojectname,
                                        'quesdeleteFLAG': 0},
                                        {"_id": 0}):
        allques.append(ques)
    
    # print(f"allques: {allques}")
    key = 'uploadquesfile'
    # print ('New ques file', new_ques_file)

    if new_ques_file[key].filename != '':
        current_file = new_ques_file[key]
        # print ("Filepath", filepath)
        cur_filename = current_file.filename
        # print("Filename", cur_filename)
        file_format = cur_filename.rsplit('.', 1)[-1]
        if (file_format == 'xlsx'):
            quesstate, quesextra = processExcelUpload(mongo, projects,
                                            userprojects,
                                            projectsform,
                                            questionnaires,
                                            activeprojectname,
                                            projectowner,
                                            basedir,
                                            current_file,
                                            allques,
                                            current_username)
            
        elif (file_format == 'zip'):
            quesstate, quesextra = processZipUpload(mongo, projects,
                                            userprojects,
                                            projectsform,
                                            questionnaires,
                                            activeprojectname,
                                            projectowner,
                                            basedir,
                                            current_file,
                                            allques,
                                            current_username)
        else:
            return (1, '')

    return (quesstate, quesextra)




def processExcelUpload(mongo, projects,
                    userprojects,
                    projectsform,
                    questionnaires,
                    activeprojectname,
                    projectowner,
                    basedir,
                    new_ques_file,
                    allques,
                    current_username):
    file_format = 'xlsx'
    uploaded_file_content = new_ques_file.read()
    headword_mapped, all_mapped, field_map, df = lifeuploader(file_format, uploaded_file_content, basedir, allques, field_map={})
    # print(f"{'-'*80}\nIN lexemekeymapping() FUNCTION\n\nheadword_mapped\n{headword_mapped}\n\nall_mapped:\n{all_mapped}\n\nfield_map:\n{field_map}\n\ndf:\n{df}")
    # print(f"{'-'*80}\nIN lexemekeymapping() FUNCTION\n\nheadword_mapped\n{type(headword_mapped)}\n\nall_mapped:\n{type(all_mapped)}\n\nfield_map:\n{type(field_map)}\n\ndf:\n{type(df)}")
    life_xlsx_root_path = os.path.join(basedir, 'lifexlsxdf.tsv')
    df.to_csv(life_xlsx_root_path, sep='\t', index=False)
    quesstate, quesextra = enterquesfromuploadedfile(mongo,projects,
                                            userprojects,
                                            projectsform,
                                            questionnaires,
                                            projectowner,
                                            activeprojectname,
                                            df,
                                            new_ques_file,
                                            current_username)

    return (quesstate, quesextra)
    
def processZipUpload(mongo, projects,
                    userprojects,
                    projectsform,
                    questionnaires,
                    activeprojectname,
                    projectowner,
                    basedir,
                    new_ques_file,
                    allques,
                    current_username):

    # fnames_dict = {}
    
    # all_files = []
    # with ZipFile(new_ques_file) as myzip:        
    #     for full_file_name in myzip.namelist():
    #         if (not full_file_name.endswith('.xlsx')):
    #             all_files.append(full_file_name)
 
    
    with ZipFile(new_ques_file) as myzip:
        for file_name in myzip.namelist():
            if (file_name.endswith('.xlsx')):
                with myzip.open(file_name) as myfile:
                    file_format = 'xlsx'
                    uploaded_file_content = myfile.read()
                    headword_mapped, all_mapped, field_map, df = lifeuploader(file_format, uploaded_file_content, basedir, allques, field_map={})
                    # print(f"{'-'*80}\nIN lexemekeymapping() FUNCTION\n\nheadword_mapped\n{headword_mapped}\n\nall_mapped:\n{all_mapped}\n\nfield_map:\n{field_map}\n\ndf:\n{df}")
                    # print(f"{'-'*80}\nIN lexemekeymapping() FUNCTION\n\nheadword_mapped\n{type(headword_mapped)}\n\nall_mapped:\n{type(all_mapped)}\n\nfield_map:\n{type(field_map)}\n\ndf:\n{type(df)}")
                    life_xlsx_root_path = os.path.join(basedir, 'lifexlsxdf.tsv')
                    df.to_csv(life_xlsx_root_path, sep='\t', index=False)

                    # df, fnames_dict = drop_filenames (df)

                    quesstate, quesextra = enterquesfromuploadedfile(mongo, projects,
                                            userprojects,
                                            projectsform,
                                            questionnaires,
                                            projectowner,
                                            activeprojectname,
                                            df,
                                            new_ques_file,
                                            current_username)

    return (quesstate, quesextra)
    
    
    
                # file_name = full_file_name[:full_file_name.rfind('.')]
                
                # if file_name in audio_files:
                #     image_id = 'I'+re.sub(r'[-: \.]', '', str(datetime.now()))
                #     image_file = io.BytesIO(myfile.read())
                    
                # elif file_name in image_files:
                #     image_id = 'I'+re.sub(r'[-: \.]', '', str(datetime.now()))
                #     image_file = io.BytesIO(myfile.read())
                    
                # elif file_name in mm_files:
                    





    
        
        # print(f"uploaded_file_content: {uploaded_file_content}")

    # save uploaded file details in pickle file for future use
    store_uploaded_file_content = {}
    store_uploaded_file_content['file_format'] = file_format
    store_uploaded_file_content['uploaded_file_content'] = uploaded_file_content
    life_uploaded_file_content_path = os.path.join(basedir, 'lifeUploadedFileContent.pkl')
    with open(life_uploaded_file_content_path, 'wb') as file:
        pickle.dump(store_uploaded_file_content, file)
    

    # if (not headword_mapped):
    #     return (2, '')
    
    # elif (not all_mapped and len(field_map) != 0):
    #     not_mapped_data = field_map
    #     print(f"not_mapped_data: {not_mapped_data}")
    #     return (6, not_mapped_data)
    # else:
    #     if (file_format == 'xlsx'):
    #         enterquesfromuploadedfile(df)

# def drop_filenames(df):
#     columns = df.columns
#     drop_cols = [c for c in df.columns if c.endswith('.filename')]

#     filename_df = df[drop_cols]
#     filename_cols = filename_df.columns
#     renamed_cols = []

#     for filename_col in filename_cols:
#         if 'audio' in filename_col:
#             renamed_cols.append('audio')
#         elif 'multimedia' in filename_col:
#             renamed_cols.append('multimedia')
#         elif 'image' in filename_col:
#             renamed_cols.append('image')
    
#     filename_df.columns = renamed_cols
#     filename_dict = filename_df.to_dict('list')
#     print ('Filenames of the upload', filename_dict)

#     df.drop(columns=drop_cols, inplace=True)

#     return df, filename_dict