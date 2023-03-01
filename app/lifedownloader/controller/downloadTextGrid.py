import parselmouth as plm
import tgt
import audioread
from app.controller import (
    getfilefromfs
)

import os
import shutil
import json
import pandas as pd
from io import StringIO
from app import mongo



def downloadTextGridWihoutAudio(transcriptions,
                                    current_username,
                                    activeprojectname,
                                    latest,
                                    filetype):

    basedir = os.path.abspath(os.path.dirname(__file__))
    basedir = basedir[:basedir.rfind('/')]
    basedir = os.path.join(basedir, 'downloads')
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    
    audio_dir = os.path.join(basedir, 'audio')
    text_grid_dir = os.path.join(basedir, 'textgrids')
    zipfilename = activeprojectname+'_textgrids'
    zipfilepath = os.path.join(basedir, zipfilename)
    print ('Zipfilepath', zipfilepath)

    if os.path.exists(audio_dir):
        shutil.rmtree(audio_dir)
    os.mkdir(audio_dir)

    if os.path.exists(text_grid_dir):
        shutil.rmtree(text_grid_dir)
    os.mkdir(text_grid_dir)

    print ('Basedir', basedir)
    print ('Format received', filetype)

    ## Currently it returns the full entry, excluding the audiowaveform 'data' - 
    ## anyway we may not be using that and its a HUGE list of just numbers, making
    ## JSON unreadable but it could be included if one really wants to
    if filetype == 'lifejson':
        print ('Lifejson format')
        all_entries = transcriptions.find({'projectname': activeprojectname,
        'transcriptionFLAG': 1, 'audiodeleteFLAG': 0}, {'_id': 0, 'audioMetadata.audiowaveform.data': 0})
        
        print ('all_entries', all_entries)
        for cur_entry in all_entries:
            write_json(cur_entry, text_grid_dir)
    
    else:
        if latest:
            all_entries = transcriptions.find({'projectname': activeprojectname,
            'transcriptionFLAG': 1, 'audiodeleteFLAG': 0}, 
            {'textGrid': 1, 'audioId': 1, 'audioFilename': 1, '_id': 0})
        else:
            all_entries = transcriptions.find({'projectname': activeprojectname,
            'transcriptionFLAG': 1, 'audiodeleteFLAG': 0}, 
            {current_username+'.textGrid': 1, 'audioId': 1, 'audioFilename': 1, '_id': 0})

        min_max = []
        tiers = {}

        for cur_entry in all_entries:
            # print (cur_entry)
            if latest:
                text_grid = cur_entry['textGrid']
            else:
                text_grid = cur_entry[current_username]['textGrid']
            
            if filetype == 'json':
                    write_json(cur_entry, text_grid_dir)
            else:            
                xmin, xmax, tiers = get_boundaries_tiers(activeprojectname, text_grid)

                # if xmin > -1 and xmax > 0 and len(tiers) > 0:
                if len(tiers) > 0:
                    # min_max.append(list([xmin, xmax]))

                    audio_id = cur_entry['audioId']
                    audio_filename = cur_entry['audioFilename']
                    original_audio_filename = audio_filename[audio_filename.find('_')+1:]

                    overall_xmin = 0.0
                    overall_xmax = get_audio_duration(audio_dir, audio_id)

                    text_grid_path = get_text_grid_path(original_audio_filename, text_grid_dir)
                    
                    tgt_text_grid = get_tgt_text_grid(tiers, xmin, xmax, overall_xmin, overall_xmax, text_grid_path)

                    write_tgt_text_grid(tgt_text_grid, text_grid_path, filetype)

    shutil.make_archive(zipfilepath, 'zip', text_grid_dir)

    return '200', zipfilepath+'.zip'


def write_json(cur_entry, text_grid_dir):    
    audio_filename = cur_entry['audioFilename']
    original_audio_filename = audio_filename[audio_filename.find('_')+1:]
    text_grid_path = get_text_grid_path(original_audio_filename, text_grid_dir)
    json_path = text_grid_path.replace('.TextGrid', '.json')
    with open(json_path, "w") as outfile:
        str_json = json.dumps(cur_entry, indent=4)
        outfile.write(str_json)


def write_tgt_text_grid(tgt_text_grid, text_grid_path, filetype):
    print ('Filetype', filetype)
    if filetype == 'textgrid':
        # print ('Wriing to', tgt_text_grid.filename)
        tgt.io.write_to_file(tgt_text_grid, text_grid_path, format='long')
    elif filetype == 'tsv':    
        text_grid_path_tsv = text_grid_path.replace('.TextGrid', '.tsv')
        tgt.io.write_to_file(tgt_text_grid, text_grid_path_tsv, format='table', separator='\t')
    elif filetype == 'csv':
        text_grid_path_csv = text_grid_path.replace('.TextGrid', '.csv')
        tgt.io.write_to_file(tgt_text_grid, text_grid_path_csv, format='table', separator=',')
    else:
        textgrid_pd = get_textgrid_df(tgt_text_grid)
        if filetype == 'xlsx':
            text_grid_path_xls = text_grid_path.replace('.TextGrid', '.xlsx')        
            textgrid_pd.to_excel(text_grid_path_xls, index=False, engine='xlsxwriter')
        elif filetype == 'latex':
            text_grid_path_tex = text_grid_path.replace('.TextGrid', '.tex')
            textgrid_pd.to_latex(text_grid_path_tex, index=False)
        elif filetype == 'markdown':
            text_grid_path_md = text_grid_path.replace('.TextGrid', '.md')
            textgrid_pd.to_markdown(text_grid_path_md, index=False)
        elif filetype == 'html':
            text_grid_path_html = text_grid_path.replace('.TextGrid', '.html')
            textgrid_pd.to_html(text_grid_path_html, index=False)
        

def get_textgrid_df(tgt_text_grid):    
    csv_textgrid = tgt.io.export_to_table(tgt_text_grid)
    csv_textgridIO = StringIO(csv_textgrid)
    textgrid_pd = pd.read_csv(csv_textgridIO)
    return textgrid_pd



def get_tgt_text_grid(tiers, xmin, xmax, overall_xmin, overall_xmax, text_grid_path):
    tgt_text_grid = tgt.core.TextGrid(filename=text_grid_path)

    for cur_tier in tiers:
        tier_transcriptions = tiers[cur_tier]
        for current_min, current_max, cur_transcription in zip(xmin, xmax, tier_transcriptions):
            boundary_interval = tgt.core.Interval(current_min, current_max, cur_transcription)

            if tgt_text_grid.has_tier(cur_tier):
                tgt_text_grid.get_tier_by_name(cur_tier).add_interval(boundary_interval)
            else:
                current_tgt_tier = tgt.core.IntervalTier(overall_xmin, overall_xmax, cur_tier)
                current_tgt_tier.add_interval(boundary_interval)
                tgt_text_grid.add_tier(current_tgt_tier)
    return tgt_text_grid
    

def get_text_grid_path(original_audio_filename, text_grid_dir):
    audio_extension = original_audio_filename[original_audio_filename.rfind('.'):]
    text_grid_filename = original_audio_filename.replace(audio_extension, '.TextGrid')
    text_grid_path = os.path.join(text_grid_dir, text_grid_filename)
    return text_grid_path


def get_audio_duration (audio_dir, audio_id):
    audio_file_path = getfilefromfs.getfilefromfs(mongo, audio_dir, audio_id, 'audio', 'audioId')
    print ('Audio file path', audio_file_path)
    with audioread.audio_open(audio_file_path) as f:
        overall_xmax = f.duration
    
    return overall_xmax


def get_boundaries_tiers(activeprojectname, text_grid):
    xmin = []
    xmax = []
    tiers = {}

    for tier in text_grid:
        # print ('Tier', tier)
        if len(tier) > 0:
            tier_name = tier
            all_boundary_ids = text_grid[tier]
            # print('All boundary IDs', all_boundary_ids)
            for cur_boundary_id in all_boundary_ids:
                # print ('Boundary ID', cur_boundary_id)
                boundary_element = all_boundary_ids[cur_boundary_id]
                # print('Boundary element', boundary_element)
                for cur_boundary_element in boundary_element:
                    # print ('Boundary element', cur_boundary_element)
                    if cur_boundary_element == 'start':
                        xmin.append(boundary_element['start'])
                    elif cur_boundary_element == 'end':
                        xmax.append(boundary_element['end'])
                    else:
                        value_type = boundary_element[cur_boundary_element]
                        # print ('Value type', boundary_element, value_type)

                        if (type(value_type) is dict) and (len(value_type) > 0):
                            for script_name in value_type:                                
                                tier_name = tier+'-'+script_name
                                tier_value = value_type[script_name]
                                # if len(tier_value) > 0:
                                # print ('Tier name', tier_name)
                                # print ('Tiers', tiers)
                                if (type(tier_value) is str):
                                    if tier_name in tiers:
                                        # print (activeprojectname, 'Length of current tier', tier_name, len(tiers[tier_name]))
                                        tiers[tier_name].append(tier_value)
                                    else:
                                        tiers[tier_name] = [tier_value]
                                    
                                # else:
                                #     print (activeprojectname, 'Boundary ID', cur_boundary_id)
                                #     print (activeprojectname, 'Boundary element', cur_boundary_element, value_type)
                                #     print (activeprojectname, 'current tier', tier_name)
                                #     print (activeprojectname, 'Tier value', tier_value)
                                    # print ('xmin', xmin)
                                    # print ('xmax', xmax)
                                    # print ('tier_name', tier_name)
                                    # print ('tier_value', tier_value)



    return xmin, xmax, tiers
                
