import parselmouth as plm
import tgt
import audioread
from app.controller import (
    getfilefromfs,
    life_logging,
    audiodetails
)

import copy
import os
import shutil
import json
import pandas as pd
from io import StringIO
from app import mongo
from flask import flash
import re
from collections import defaultdict
from collections import OrderedDict

logger = life_logging.get_logger()


def downloadTextGridOld(transcriptions,
                        projectsform,
                        current_username,
                        activeprojectname,
                        latest,
                        filetype,
                        empty_string='',
                        merge_same_intervals=False,
                        download_audio=False,
                        merge_all_slices=False):

    basedir = os.path.abspath(os.path.dirname(__file__))
    basedir = basedir[:basedir.rfind('/')]
    basedir = os.path.join(basedir, 'downloads')
    if os.path.exists(basedir):
        print('Removing basedir: ', basedir)
        shutil.rmtree(basedir)
    os.makedirs(basedir)

    text_grid_dir = os.path.join(basedir, 'textgrids')

    if download_audio:
        audio_dir = text_grid_dir
    else:
        audio_dir = os.path.join(basedir, 'audio')

    zipfilename = activeprojectname+'_textgrids'
    zipfilepath = os.path.join(basedir, zipfilename)
    print('Zipfilepath', zipfilepath)

    if os.path.exists(audio_dir):
        shutil.rmtree(audio_dir)
    os.mkdir(audio_dir)

    if os.path.exists(text_grid_dir):
        shutil.rmtree(text_grid_dir)
    os.mkdir(text_grid_dir)

    print('Basedir', basedir)
    print('Format received', filetype)

    # TODO: Its a temporary fix for issues related to data not getting saved as per the
    # projectforms. Currently irrespective of what is there is projectsform, morphemic
    # break, gloss and translation are getting saved in 'transcriptions' project.
    # This is so even though these fields are not displayed on the interface.
    # This needs to be fixed - once done, this code will no longer be needed.
    formelement_textgrid_map = {
        'Transcription Script': 'transcription',
        'Interlinear Gloss Script': 'gloss',
        'Interlinear Gloss Language': 'sentencemorphemicbreak',
        'Translation Script': 'translation'
    }
    current_projectformelements = []
    projectformelements = projectsform.find({'projectname': activeprojectname},
                                            {'_id': 0, 'username': 0, 'projectname': 0})

    for current_element in projectformelements:
        # current_element_dict = projectformelements[current_element]
        for current_element_key in current_element:
            # print ('Current element', current_element)
            if current_element_key in formelement_textgrid_map:
                current_projectformelements.append(
                    formelement_textgrid_map[current_element_key])

    print('Current project form elements', current_projectformelements)

    # Currently it returns the full entry, excluding the audiowaveform 'data' -
    # anyway we may not be using that and its a HUGE list of just numbers, making
    # JSON unreadable but it could be included if one really wants to
    if filetype == 'lifejson':
        print('Lifejson format')
        all_entries = transcriptions.find({'projectname': activeprojectname,
                                           'transcriptionFLAG': 1, 'audiodeleteFLAG': 0}, {'_id': 0, 'audioMetadata.audiowaveform.data': 0})

        print('all_entries', all_entries)
        for cur_entry in all_entries:
            write_json(cur_entry, text_grid_dir, merge_all_slices)

    else:
        if latest:
            all_entries = transcriptions.find({'projectname': activeprojectname,
                                               'transcriptionFLAG': 1, 'audiodeleteFLAG': 0},
                                              {'textGrid': 1, 'audioId': 1, 'audioFilename': 1, 'additionalInfo.totalSlices': 1, 'additionalInfo.currentSliceNumber': 1, 'audioMetadata.currentSliceDuration': 1, '_id': 0})
        else:
            all_entries = transcriptions.find({'projectname': activeprojectname,
                                               'transcriptionFLAG': 1, 'audiodeleteFLAG': 0},
                                              {current_username+'.textGrid': 1, 'audioId': 1, 'audioFilename': 1, 'additionalInfo.totalSlices': 1, 'additionalInfo.currentSliceNumber': 1, 'audioMetadata.currentSliceDuration': 1, '_id': 0})

        # min_max = []
        total_slices = 1

        tiers = {}

        for cur_entry in all_entries:
            print("Current entry", cur_entry)
            if latest:
                text_grid = cur_entry['textGrid']
            else:
                if current_username in cur_entry:
                    text_grid = cur_entry[current_username]['textGrid']
                else:
                    text_grid = {}
            if 'audioMetadata' in all_entries:
                slice_duration = all_entries['audioMetadata'].get(
                    'currentSliceDuration', 0.0)

            print("Text Grid", text_grid)
            if len(text_grid) > 0:
                if filetype == 'json':
                    write_json(cur_entry, text_grid_dir, merge_all_slices)
                else:
                    xmin, xmax, tiers = get_boundaries_tiers(
                        activeprojectname, current_projectformelements, text_grid)

                    # if xmin > -1 and xmax > 0 and len(tiers) > 0:
                    if len(tiers) > 0:
                        # min_max.append(list([xmin, xmax]))

                        audio_id = cur_entry['audioId']
                        audio_filename = cur_entry['audioFilename']

                        original_audio_filename = get_original_audio_filename(
                            cur_entry, audio_filename, merge_all_slices)

                        overall_xmin = 0.0
                        if slice_duration == 0.0 or download_audio:
                            overall_xmax = get_audio_with_duration(
                                audio_dir, audio_id, original_audio_filename)
                        else:
                            overall_xmax = slice_duration

                        text_grid_path = get_text_grid_path(
                            original_audio_filename, text_grid_dir)

                        tgt_text_grid = get_tgt_text_grid(
                            tiers, xmin, xmax, overall_xmin, overall_xmax, text_grid_path)

                        write_tgt_text_grid(
                            tgt_text_grid, text_grid_path, filetype, empty_string, merge_same_intervals)

    if len(os.listdir(text_grid_dir)) > 0:
        print('Text grid dir', text_grid_dir)
        shutil.make_archive(zipfilepath, 'zip', text_grid_dir)
        return '200', zipfilepath+'.zip'
    else:
        print('Text grid dir empty', text_grid_dir)
        return '0', 'Empty Directory'


def downloadTextGrid(transcriptions,
                     projectsform,
                     current_username,
                     activeprojectname,
                     audio_ids,
                     transcription_by,
                     filetype,
                     empty_string='',
                     merge_same_intervals=False,
                     download_audio=False,
                     get_individual_slices=True,
                     merge_all_slices=True,
                     retain_original_filename=True):

    basedir = os.path.abspath(os.path.dirname(__file__))
    basedir = basedir[:basedir.rfind('/')]
    basedir = os.path.join(basedir, 'downloads')
    if os.path.exists(basedir):
        shutil.rmtree(basedir)
    os.makedirs(basedir)

    # audio_dir = os.path.join(basedir, 'audio')
    text_grid_dir = os.path.join(basedir, 'merged_textgrids')
    if download_audio or filetype == 'onlyaudio':
        audio_dir = text_grid_dir
    else:
        audio_dir = os.path.join(basedir, 'audio')
    zipfilename = activeprojectname+'_textgrids'
    zipfilepath = os.path.join(basedir, zipfilename)
    logger.debug('Zipfilepath %s', zipfilepath)

    if os.path.exists(audio_dir):
        shutil.rmtree(audio_dir)
    os.mkdir(audio_dir)

    if os.path.exists(text_grid_dir):
        shutil.rmtree(text_grid_dir)
    os.mkdir(text_grid_dir)

    logger.debug('Basedir %s', basedir)
    # print('Format received', filetype)

    logger.debug("original audio ids %s", audio_ids)
    grouped_audio_id = group_slices_by_audio_ids(audio_ids)
    logger.debug("Grouped audio id %s", grouped_audio_id)

    # TODO: Its a temporary fix for issues related to data not getting saved as per the
    # projectforms. Currently irrespective of what is there is projectsform, morphemic
    # break, gloss and translation are getting saved in 'transcriptions' project.
    # This is so even though these fields are not displayed on the interface.
    # This needs to be fixed - once done, this code will no longer be needed.
    formelement_textgrid_map = {
        'Transcription Script': 'transcription',
        'Interlinear Gloss Script': 'gloss',
        'Interlinear Gloss Language': 'sentencemorphemicbreak',
        'Translation Script': 'translation',
        'Transcription': 'transcription',
        'Translation': 'translation',
        'Interlinear Gloss': 'gloss'
    }
    new_form_elements = ['Transcription',
                         'Translation',
                         'Interlinear Gloss']
    current_projectformelements = []
    projectformelements = projectsform.find({'projectname': activeprojectname},
                                            {'_id': 0, 'username': 0, 'projectname': 0})

    for current_element in projectformelements:
        # current_element_dict = projectformelements[current_element]
        for current_element_key, current_element_vals in current_element.items():
            # print ('Current element', current_element)
            if current_element_key in formelement_textgrid_map:
                if current_element_key in new_form_elements:
                    current_element_val = current_element_vals[1]
                    logger.debug('Current element %s; its vals %s',
                                 current_element_key, current_element_vals)
                    if len(current_element_val) > 0:
                        current_projectformelements.append(
                            formelement_textgrid_map[current_element_key])
                else:
                    current_projectformelements.append(
                        formelement_textgrid_map[current_element_key])

    logger.info('Current Form elements (only these will be downloaded) %s',
                current_projectformelements)
    # print('Current project form elements', current_projectformelements)

    # Currently it returns the full entry, excluding the audiowaveform 'data' -
    # anyway we may not be using that and its a HUGE list of just numbers, making
    # JSON unreadable but it could be included if one really wants to

    if filetype == 'lifejson':
        logger.debug('Lifejson format')
        all_entries = transcriptions.find({'projectname': activeprojectname,
                                           'transcriptionFLAG': 1, 'audiodeleteFLAG': 0}, {'_id': 0, 'audioMetadata.audiowaveform.data': 0})

        # print('all_entries', all_entries)
        for cur_entry in all_entries:
            audio_id = cur_entry['audioId']
            audio_filename = cur_entry['audioFilename']

            if audio_id in audio_ids:
                write_json(cur_entry, text_grid_dir, download_audio)
    elif filetype == 'onlyaudio':
        all_entries = transcriptions.find({'projectname': activeprojectname,
                                           'audiodeleteFLAG': 0}, {'_id': 0, 'audioId': 1, 'audioFilename': 1, 'additionalInfo': 1})

        for cur_entry in all_entries:
            audio_id = cur_entry['audioId']
            audio_filename = cur_entry['audioFilename']

            if audio_id in audio_ids:
                original_audio_filename = get_original_audio_filename(
                    cur_entry, audio_filename)

                overall_xmax = get_audio_with_duration(
                    audio_dir, audio_id, original_audio_filename)

    else:

        if transcription_by == "latest":
            all_entries = transcriptions.find({'projectname': activeprojectname,
                                               'transcriptionFLAG': 1, 'audiodeleteFLAG': 0},
                                              {'textGrid': 1, 'audioId': 1, 'audioFilename': 1, 'additionalInfo': 1, 'audioMetadata': 1, '_id': 0})
        else:
            all_entries = transcriptions.find({'projectname': activeprojectname,
                                               'transcriptionFLAG': 1, 'audiodeleteFLAG': 0},
                                              {transcription_by+'.textGrid': 1, 'audioId': 1, 'audioFilename': 1, 'additionalInfo': 1, 'audioMetadata': 1, '_id': 0})

        # min_max = []
        total_slices = 1

        tiers = {}

        for cur_entry in all_entries:
            # print("Current entry", cur_entry)
            if transcription_by == "latest":
                text_grid = cur_entry['textGrid']
            else:
                if transcription_by in cur_entry:
                    text_grid = cur_entry[transcription_by]['textGrid']
                else:
                    text_grid = {}

            # print("Text Grid", text_grid)
            audio_id = cur_entry['audioId']
            audio_filename = cur_entry['audioFilename']
            logger.debug('Audio ID: %s, All Audio IDs %s', audio_id, audio_ids)
            if audio_id in audio_ids:
                logger.info('Processing Audio ID %s', audio_id)
                if 'audioMetadata' in cur_entry:
                    audio_duration = cur_entry['audioMetadata'].get(
                        'audioDuration', 0.0)
                    slice_duration = cur_entry['audioMetadata'].get(
                        'currentSliceDuration', 0.0)
                else:
                    slice_duration = get_audio_with_duration(
                        audio_dir, audio_id, original_audio_filename)

                if 'additionalInfo' in cur_entry:
                    total_slices = cur_entry['additionalInfo'].get(
                        'totalSlices', 1)
                    boundary_offset = cur_entry['additionalInfo'].get(
                        'boundaryOffsetValue', 0.0)
                    slice_offset = cur_entry['additionalInfo'].get(
                        'sliceOffsetValue', 0.0)
                    slice_overlap = cur_entry['additionalInfo'].get(
                        'sliceOverlapRegion', 0.0)
                    is_slice_of = cur_entry['additionalInfo'].get(
                        'isSliceOf', audio_id)
                    current_slice_number = cur_entry['additionalInfo'].get(
                        'currentSliceNumber', 0)
                else:
                    total_slices = 1
                    boundary_offset = 0.0
                    slice_offset = 0.0
                    slice_overlap = 0.0
                    is_slice_of = audio_id
                    current_slice_number = 0

                # print("Text Grid Length", len(text_grid))
                if len(text_grid) > 0:
                    # if filetype == 'json':
                    #     write_json(cur_entry, text_grid_dir, merge_all_slices)
                    # else:
                    # if xmin > -1 and xmax > 0 and len(tiers) > 0:
                    # print("Tiers Length", len(text_grid))

                    # min_max.append(list([xmin, xmax]))
                    overall_xmin = 0.0

                    # print("Total Slices",
                    #       total_slices)
                    # print("Merge all?",
                    #       merge_all_slices)
                    # print("Current slice number", current_slice_number)

                    if get_individual_slices or total_slices == 1:
                        logger.info("Getting single text grid of %s", audio_id)
                        if retain_original_filename:
                            original_audio_filename = get_original_audio_filename(
                                cur_entry, audio_filename)
                        else:
                            original_audio_filename = audio_filename

                        # print("Original Audio Filename",
                        #       original_audio_filename)

                        # xmin, xmax, tiers = get_boundaries_tiers(
                        #     activeprojectname, current_projectformelements, text_grid, offset=boundary_offset)
                        xmin, xmax, tiers = get_boundaries_tiers(
                            activeprojectname, current_projectformelements, text_grid, xmin=[], xmax=[], tiers={})
                        logger.debug('Tiers %s', tiers)

                        if audio_duration == 0.0 or download_audio:
                            overall_xmax = get_audio_with_duration(
                                audio_dir, audio_id, original_audio_filename)
                        else:
                            overall_xmax = audio_duration

                        if len(tiers) > 0:
                            logger.debug(
                                'Length of tiers single %s', len(tiers))
                            text_grid_path = get_text_grid_path(
                                original_audio_filename, text_grid_dir)

                            tgt_text_grid = get_tgt_text_grid(
                                tiers, xmin, xmax, overall_xmin, overall_xmax, text_grid_path)

                            write_tgt_text_grid(
                                tgt_text_grid, text_grid_path, filetype, empty_string, merge_same_intervals)

                    if merge_all_slices and total_slices > 1:
                        if current_slice_number == 0:
                            # logger.debug("Merging all text grids")
                            logger.info("merging text grids of %s", audio_id)

                            unsliced_audio_id = get_audio_id_without_slice(
                                audio_id)
                            total_present_slices = len(
                                grouped_audio_id.get(unsliced_audio_id, []))
                            logger.debug(
                                'Total present slices: %s, Total expected slices: %s', total_present_slices, total_slices)

                            if unsliced_audio_id in grouped_audio_id and (total_present_slices == total_slices):
                                if retain_original_filename:
                                    original_audio_filename = get_original_audio_filename(
                                        cur_entry, audio_filename, merge_all_slices)
                                else:
                                    original_audio_filename = get_audio_filename_without_slice(audio_filename,
                                                                                               '-slice', '_')
                                xmin, xmax, tiers, overall_xmax = get_merged_text_grid_of_multiple_slices(transcriptions,
                                                                                                          activeprojectname,
                                                                                                          is_slice_of,
                                                                                                          current_username,
                                                                                                          current_projectformelements,
                                                                                                          audio_dir,
                                                                                                          original_audio_filename,
                                                                                                          audio_duration,
                                                                                                          slice_duration,
                                                                                                          download_audio,
                                                                                                          transcription_by,
                                                                                                          get_individual_slices,
                                                                                                          retain_original_filename)
                                if len(tiers) > 0:
                                    logger.debug(
                                        'Length of tiers single %s', len(tiers))
                                    text_grid_path = get_text_grid_path(
                                        original_audio_filename, text_grid_dir)
                                    logger.debug(
                                        'Text grid path %s', text_grid_path)

                                    tgt_text_grid = get_tgt_text_grid(
                                        tiers, xmin, xmax, overall_xmin, overall_xmax, text_grid_path)

                                    write_tgt_text_grid(
                                        tgt_text_grid, text_grid_path, filetype, empty_string, merge_same_intervals)
                            # if audio_duration == 0.0:
                            # overall_xmax += slice_overall_xmax
                            # xmin.extend(slice_xmin)
                            # xmax.extend(slice_xmax)
                            # for k, v in slice_tiers.items():
                            #     tiers[k].extend(v)
                        else:
                            print("Continuing")
                            continue

                    # else:
                    #     tgt_text_grid = get_tgt_text_grid(
                    #         tiers, xmin, xmax, overall_xmin, overall_xmax, text_grid_path)

                    #     write_tgt_text_grid(
                    #         tgt_text_grid, text_grid_path, filetype, empty_string, merge_same_intervals)

    if len(os.listdir(text_grid_dir)) > 0:
        logger.debug('Text grid dir %s', text_grid_dir)
        shutil.make_archive(zipfilepath, 'zip', text_grid_dir)
        return '200', zipfilepath+'.zip'
    else:
        logger.debug('Text grid dir %s', text_grid_dir)
        return '0', 'Empty Directory'


def write_json(cur_entry, text_grid_dir, download_audio):
    audio_filename = cur_entry['audioFilename']
    audio_id = cur_entry['audioId']

    # original_audio_filename = audio_filename[audio_filename.find('_')+1:]
    # original_audio_filename = get_original_audio_filename(
    #     cur_entry, audio_filename)

    if download_audio:
        get_audio_with_duration(
            text_grid_dir, audio_id, audio_filename)

    text_grid_path = get_text_grid_path(audio_filename, text_grid_dir)

    json_path = text_grid_path.replace('.TextGrid', '.json')

    with open(json_path, "w") as outfile:
        str_json = json.dumps(cur_entry, indent=4, default=str)
        outfile.write(str_json)


def write_tgt_text_grid(original_tgt_text_grid, text_grid_path, filetype, empty_string='', merge_same_intervals=False):
    logger.debug('Writing Filetype %s', filetype)

    tgt_text_grid = correct_start_end_times_and_fill_gaps(
        original_tgt_text_grid, empty_string, merge_same_intervals)

    # if merge_same_intervals:
    #     tgt_text_grid = tgt_text_grid.get_copy_with_same_intervals_merged()

    if filetype == 'textgrid':
        # print ('Wriing to', tgt_text_grid.filename)
        tgt.io.write_to_file(tgt_text_grid, text_grid_path, format='long')
    elif filetype == 'tsv':
        text_grid_path_tsv = text_grid_path.replace('.TextGrid', '.tsv')
        tgt.io.write_to_file(tgt_text_grid, text_grid_path_tsv,
                             format='table', separator='\t')
    elif filetype == 'csv':
        text_grid_path_csv = text_grid_path.replace('.TextGrid', '.csv')
        tgt.io.write_to_file(tgt_text_grid, text_grid_path_csv,
                             format='table', separator=',')
    else:
        textgrid_pd = get_textgrid_df(tgt_text_grid)
        if filetype == 'xlsx':
            text_grid_path_xls = text_grid_path.replace('.TextGrid', '.xlsx')
            textgrid_pd.to_excel(text_grid_path_xls,
                                 index=False, engine='xlsxwriter')
        elif filetype == 'latex':
            text_grid_path_tex = text_grid_path.replace('.TextGrid', '.tex')
            textgrid_pd.to_latex(text_grid_path_tex, index=False)
        elif filetype == 'markdown':
            text_grid_path_md = text_grid_path.replace('.TextGrid', '.md')
            textgrid_pd.to_markdown(text_grid_path_md, index=False)
        elif filetype == 'html':
            text_grid_path_html = text_grid_path.replace('.TextGrid', '.html')
            textgrid_pd.to_html(text_grid_path_html, index=False)
        elif filetype == 'json':
            text_grid_path_html = text_grid_path.replace('.TextGrid', '.json')
            textgrid_pd.to_json(text_grid_path_html,
                                orient="table", index=False, indent=4)


def group_slices_by_audio_ids(audio_ids):
    grouped_dict = defaultdict(list)
    for current_id in audio_ids:
        unsliced_audio_id = get_audio_id_without_slice(current_id)
        grouped_dict[unsliced_audio_id].append(current_id)
    return grouped_dict


def get_merged_text_grid_of_multiple_slices(transcriptions,
                                            activeprojectname,
                                            audio_id,
                                            current_username,
                                            current_projectformelements,
                                            audio_dir,
                                            original_audio_filename,
                                            audio_duration=0.0,
                                            slice_duration=0.0,
                                            download_audio=False,
                                            transcription_by="",
                                            get_individual_slices=False,
                                            retain_original_filename=True):

    # print("Audio ID", audio_id)
    if transcription_by == "latest":
        all_entries = transcriptions.find({'projectname': activeprojectname, 'additionalInfo.isSliceOf': audio_id,
                                           'audiodeleteFLAG': 0},
                                          {'textGrid': 1, 'audioId': 1, 'audioFilename': 1, 'additionalInfo': 1, 'audioMetadata': 1, '_id': 0})
    else:
        all_entries = transcriptions.find({'projectname': activeprojectname, 'additionalInfo.isSliceOf': audio_id,
                                           'audiodeleteFLAG': 0},
                                          {transcription_by+'.textGrid': 1, 'audioId': 1, 'audioFilename': 1, 'additionalInfo': 1, 'audioMetadata': 1, '_id': 0})

    tiers = {}
    xmin = []
    xmax = []
    overall_xmax = 0.0
    previous_slices_duration = 0.0
    previous_slice_offset = 0.0
    total_duration = 0.0
    adjusted_duration = 0.0
    total_expected = 0.0

    for i, cur_entry in enumerate(list(all_entries)):
        # print (cur_entry)
        if transcription_by == "latest":
            text_grid = cur_entry['textGrid']
        else:
            if transcription_by in cur_entry:
                text_grid = cur_entry[transcription_by]['textGrid']
            else:
                text_grid = {}
        # print("Length of text grid in merge", len(text_grid))

        audio_duration = cur_entry['audioMetadata'].get(
            'audioDuration', 0.0)
        total_slices = cur_entry['additionalInfo']['totalSlices']
        slice_number = cur_entry['additionalInfo']['currentSliceNumber']
        boundary_offset = cur_entry['additionalInfo']['boundaryOffsetValue']
        slice_offset = round(
            cur_entry['additionalInfo']['sliceOffsetValue'] / 1000, 2)
        slice_overlap = cur_entry['additionalInfo']['sliceOverlapRegion']
        slice_duration = cur_entry['audioMetadata'].get(
            'currentSliceDuration', 0.0)
        slice_offset += slice_overlap
        expected_duration_current = slice_duration - previous_slice_offset
        total_expected += expected_duration_current

        # if i == 0:
        current_slice_offset = slice_offset
        slice_offset = previous_slice_offset

        # slice_duration -= slice_overlap
        # elif i == 1:
        #     previous_slices_duration

        if len(text_grid) > 0:
            xmin, xmax, tiers = get_boundaries_tiers(
                activeprojectname, current_projectformelements, text_grid, offset=previous_slices_duration, slice_overlap=slice_offset, xmin=xmin, xmax=xmax, tiers=tiers)
            # xmin.extend(slice_xmin)
            # xmax.extend(slice_xmax)
            # for k, v in slice_tiers.items():
            #     if k in tiers:
            #         tiers[k].extend(v)
            #     else:
            #         tiers[k] = v

            if audio_duration == 0.0 or (download_audio and not get_individual_slices):
                current_slice_audio_id = cur_entry['audioId']

                current_slice_audio_filename = cur_entry['audioFilename']
                if retain_original_filename:
                    current_slice_audio_filename = get_original_audio_filename(
                        cur_entry, current_slice_audio_filename, merge_all_slices=False)

                slice_duration = get_audio_with_duration(
                    audio_dir, current_slice_audio_id, current_slice_audio_filename)

                if audio_duration == 0.0 and total_slices > 1:
                    overall_xmax += (slice_duration -
                                     previous_slice_offset)
                elif total_slices > 1:
                    overall_xmax = audio_duration
                else:
                    overall_xmax = slice_duration
        # effective_duration = slice_duration+slice_overlap
        # total_duration += (slice_duration)

        # if i >= 1:
        #     adjusted_duration += (slice_duration - slice_offset)
        # if i >= 1:
        #     slice_duration -= slice_overlap
        # if previous_slices_duration == 0.0:
        #     slice_duration += slice_overlap

        previous_slices_duration += round(slice_duration, 7)
        # if i >= 1:
        previous_slices_duration = round(previous_slices_duration, 7)
        previous_slices_duration -= round(previous_slice_offset, 7)
        previous_slice_offset = current_slice_offset
        logger.debug('Current slice duration %s Slice Offset %s, Total slice duration %s',
                     slice_duration, slice_offset, previous_slices_duration)
        logger.debug('Total duration till now %s, Audio duration %s',
                     previous_slices_duration, audio_duration)
        logger.debug('Current slice duration (excl overlap) %s, Total epected duration %s',
                     expected_duration_current, total_expected)
        logger.debug('Length of xmin %s Xmax %s, Tiers %s, Overall Xmax %s', len(
            xmin), len(xmax), len(tiers), overall_xmax)
        logger.debug('Tiers keys %s', tiers.keys())
        for k, v in tiers.items():
            logger.debug('Tier Length %s, %s', k, len(v))

    if 'audioMetadata' in cur_entry:
        overall_xmax = cur_entry['audioMetadata'].get(
            'audioDuration', 0.0)
        # slice_duration = cur_entry['audioMetadata'].get(
        #     'currentSliceDuration', 0.0)

    return xmin, xmax, tiers, overall_xmax


def get_audio_id_without_slice(audio_id, slice_start='-slice', slice_end=''):
    fname_pattern = '(A[0-9]+)('+slice_start+'[0-9]+'+slice_end+')(.*)'
    new_audio_id = re.sub(fname_pattern, '\\1'+slice_end+'\\3', audio_id)
    return new_audio_id


def get_audio_filename_without_slice(audio_filename, slice_start='-slice', slice_end='_'):
    fname_pattern = '(A[0-9]+)('+slice_start+'[0-9]+'+slice_end+')(.*)'
    new_audio_filename = re.sub(
        fname_pattern, '\\1'+slice_end+'\\3', audio_filename)
    return new_audio_filename


def get_original_audio_filename(cur_entry, audio_filename, merge_all_slices=False, remove_slice_number=False):
    if 'additionalInfo' in cur_entry:
        total_slices = cur_entry['additionalInfo'].get(
            'totalSlices', 1)
    else:
        total_slices = 1
    if total_slices > 1:
        if merge_all_slices:
            original_audio_filename = audio_filename[audio_filename.find(
                '_')+1:]
        else:
            original_audio_filename = audio_filename[audio_filename.find(
                '-')+1:]
    else:
        original_audio_filename = audio_filename[audio_filename.find(
            '_')+1:]
    return original_audio_filename


def get_textgrid_df(tgt_text_grid):
    csv_textgrid = tgt.io.export_to_table(tgt_text_grid)
    csv_textgridIO = StringIO(csv_textgrid)
    textgrid_pd = pd.read_csv(csv_textgridIO)
    return textgrid_pd


def get_tgt_text_grid(tiers, xmin, xmax, overall_xmin, overall_xmax, text_grid_path):

    tgt_text_grid = tgt.core.TextGrid(filename=text_grid_path)

    for cur_tier in tiers:
        tier_transcriptions = tiers[cur_tier]
        i = 0
        for current_min, current_max, cur_transcription in zip(xmin, xmax, tier_transcriptions):
            i += 1
            logger.debug('%s Current Xmin %s \tCurrent Xmax %s',
                         i, current_min, current_max)
            boundary_interval = tgt.core.Interval(
                current_min, current_max, cur_transcription)

            if tgt_text_grid.has_tier(cur_tier):
                tgt_text_grid.get_tier_by_name(
                    cur_tier).add_interval(boundary_interval)
            else:
                current_tgt_tier = tgt.core.IntervalTier(
                    overall_xmin, overall_xmax, cur_tier)
                current_tgt_tier.add_interval(boundary_interval)
                tgt_text_grid.add_tier(current_tgt_tier)
    return tgt_text_grid


def get_text_grid_path(original_audio_filename, text_grid_dir):
    audio_extension = original_audio_filename[original_audio_filename.rfind(
        '.'):]
    text_grid_filename = original_audio_filename.replace(
        audio_extension, '.TextGrid')
    text_grid_path = os.path.join(text_grid_dir, text_grid_filename)
    return text_grid_path


def get_audio_with_duration(audio_dir, audio_id, audio_filename):
    # print('Input audio dir', audio_dir)
    # print('Input audio ID', audio_id)
    audio_file_path = getfilefromfs.getfilefromfs(
        mongo, audio_dir, audio_id, 'audio', 'audioId', file_name=audio_filename)
    logger.debug('Audio file path %s', audio_file_path)
    with audioread.audio_open(audio_file_path) as f:
        overall_xmax = f.duration

    return overall_xmax


# def get_adjusted_xmin(i, current_xmin, all_boundary_ids, threshold=0.001):
#     if i > 0:
#         previous_boundary_id = all_boundary_ids[i-1]
#         logger.debug('%s Previous boundary id %s', i-1, previous_boundary_id)
#     return current_xmin
def get_boundary_ids_sorted_by_start(boundaries):
    all_starts = {}
    for i, cur_boundary_id in enumerate(boundaries):
        boundary_element = boundaries[cur_boundary_id]
        current_start = boundary_element['start']
        all_starts[cur_boundary_id] = current_start

    sorted_boundaries = sorted(all_starts, key=all_starts.get)
    return sorted_boundaries


def get_boundaries_tiers(activeprojectname, projectelements, text_grid, offset=0.0, slice_overlap=0.0, xmin=[], xmax=[], tiers={}):
    # xmin = []
    # xmax = []
    # tiers = {}

    for i, tier in enumerate(text_grid):
        # print ('Tier', tier)
        # logger.debug('Tier %s', tier)
        if len(tier) > 0:
            tier_name = tier
            all_boundary_ids = OrderedDict(text_grid[tier])
            sorted_boundary_ids = get_boundary_ids_sorted_by_start(
                all_boundary_ids)

            # logger.debug('All boundary IDs %s %s', all_boundary_ids,
            #              type(all_boundary_ids))
            # for i, cur_boundary_id in enumerate(sorted(all_boundary_ids, key=lambda x: int(x))):
            for i, cur_boundary_id in enumerate(sorted_boundary_ids):
                add_bundary = False
                logger.debug('%s \tCurrent Boundary ID %s', i, cur_boundary_id)

                boundary_element = all_boundary_ids[cur_boundary_id]

                current_xmin = boundary_element['start']
                current_xmin = round(current_xmin, 2)

                current_xmax = boundary_element['end']
                current_xmax = round(current_xmax, 2)

                logger.debug('Received xmin %s Offset %s Overlap %s',
                             current_xmin, offset, slice_overlap)
                logger.debug('Received xmax %s Offset %s Overlap %s',
                             current_xmax, offset, slice_overlap)
                if current_xmin < slice_overlap:
                    # previous_without_overlap = offset-slice_overlap
                    # previous_xmax = xmax[-1]
                    # logger.debug('Previous without overlap %s Previous xmax %s', previous_without_overlap, previous_xmax)
                    # if previous_xmax < previous_without_overlap:
                    # if overlap_boundary > 0:
                    # overlap_boundary = current_xmin-slice_overlap
                    # overlap_boundary = slice_overlap - current_xmin
                    # overlap_with_max = slice_overlap - current_xmax
                    if current_xmax > slice_overlap:
                        # original_slice_overlap = slice_overlap
                        previous_without_overlap = offset-slice_overlap
                        previous_xmax = xmax[-1]
                        logger.debug('Previous without overlap %s',
                                     previous_without_overlap)
                        # previous_no_boundary = previous_xmax - previous_without_overlap
                        if previous_xmax > previous_without_overlap:
                            logger.debug('Previous max covering overlap')
                            previous_covered_overlap = previous_xmax - previous_without_overlap
                            if previous_covered_overlap > slice_overlap:
                                previous_covered_overlap = slice_overlap
                            logger.debug(
                                'Covered overlap portion in previous %s', previous_covered_overlap)
                            overlap_remaining_in_previous = slice_overlap - previous_covered_overlap
                            logger.debug('Free portion in previous %s',
                                         overlap_remaining_in_previous)
                            remaining_overlap_for_current = slice_overlap - overlap_remaining_in_previous
                            logger.debug('Adjusted Overlap %s',
                                         remaining_overlap_for_current)
                            overlap_covered_in_previous = slice_overlap - previous_covered_overlap

                            slice_overlap = remaining_overlap_for_current
                            offset -= overlap_covered_in_previous
                        else:
                            # previous_covered_overlap = 0.0
                            logger.debug('Previous max without overlap')
                            offset -= slice_overlap

                            # slice_overlap = -slice_overlap
                            slice_overlap = 0.0

                            # overlap_remaining_in_previous = slice_overlap
                            # remaining_overlap_for_current = slice_overlap

                        # slice_overlap += overlap_covered_in_previous

                        # current_starting_point =

                        # current_xmin = 0.0
                        logger.debug('Adjusted offset %s', offset)
                        logger.debug(
                            'Adjusted Slice Overlap %s', slice_overlap)
                        current_xmin -= slice_overlap
                        if current_xmin < 0.0:
                            current_xmin = 0.0
                        current_xmin += offset
                        xmin.append(current_xmin)

                        current_xmax -= slice_overlap
                        current_xmax += offset
                        xmax.append(current_xmax)
                        add_bundary = True
                        # else:
                        #     current_xmin -= slice_overlap
                        #     xmin.append(current_xmin+offset)

                        #     current_xmax -= slice_overlap
                        #     xmax.append(current_xmax+offset)

                        #     add_bundary = True
                        #     # slice_overlap -= overlap_boundary
                        # offset -= overlap_boundary
                        # add_boundary = True
                        # offset -= slice_overlap
                        # slice_overlap = 0.0
                        # xmin.append(current_xmin+offset)
                        # xmax.append(current_xmax+offset)
                        # add_bundary = True

                        # current_xmax = boundary_element['end']
                        # current_xmax = round(current_xmax, 2)
                        # current_xmax -= slice_overlap
                        # logger.debug('Added Xmax value %s', xmax[-1])
                    # else:
                    #     current_xmin = 0.0
                    #     xmin.append(current_xmin+offset)
                else:
                    current_xmin -= slice_overlap
                    xmin.append(current_xmin+offset)

                    current_xmax -= slice_overlap
                    xmax.append(current_xmax+offset)

                    add_bundary = True

                logger.debug('Added Xmin value %s', xmin[-1])
                logger.debug('Added Xmax value %s', xmax[-1])

                # if (len(xmin) - len(xmax)) == 1:
                # current_xmax = boundary_element['end']
                # current_xmax = round(current_xmax, 2)
                # # overlap_boundary = original_slice_overlap - current_xmax
                # # logger.debug('Received xmax value %s Offset %s Overlap %s',
                # #              current_xmax, offset, slice_overlap)
                # # # if current_xmax < slice_overlap:
                # # if overlap_boundary > 0:
                # #     # if (len(xmin) - len(xmax)) == 1:
                # #     if previous_xmax <= previous_without_overlap:
                # #         xmax.append(current_xmax+offset)
                # #     else:
                # #         xmin.pop()
                # # else:
                # current_xmax -= slice_overlap
                # xmax.append(current_xmax+offset)
                # logger.debug('Added Xmax value %s', xmax[-1])
                if add_bundary:
                    boundary_element.pop('start', 'start not found')
                    boundary_element.pop('end', 'end not found')
                    # logger.debug('Boundary element %s', boundary_element)
                    for cur_boundary_element in boundary_element:
                        # If the element is in projectelements only then
                        # its tiers are being fetched
                        if cur_boundary_element in projectelements:
                            value_type = boundary_element[cur_boundary_element]
                            # print('Value type', value_type)

                            if (type(value_type) is dict) and (len(value_type) > 0):
                                for script_name in value_type:
                                    tier_name = tier+'-'+script_name+'-'+cur_boundary_element
                                    tier_value = value_type[script_name]
                                    # if len(tier_value) > 0:
                                    # print ('Tier name', tier_name)
                                    # print ('Tiers', tiers)

                                    # TODO: This will only work for transcription and translation
                                    # Fix needed for gloss and morphemic break which are dicts and
                                    # need to be converged into a string.
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

    # print('All tiers', tiers)
    # for tier in tiers:
    #     print(activeprojectname, 'Tier', tier, len(tiers[tier]))
    #     print(tiers[tier])

    logger.debug("Project: %s, XMin lenngth: %s", activeprojectname, len(xmin))
    logger.debug("Project: %s, XMax lenngth: %s", activeprojectname, len(xmax))
    logger.debug("All tiers length: %s", len(tiers))
    # print(activeprojectname, 'Xmax', len(xmax))
    # print(xmin)
    # print(xmax)
    return xmin, xmax, tiers


def correct_start_end_times_and_fill_gaps(textgrid, empty_string='', merge_same_intervals=False, joined_interval_threshold=0.001, delete_flag='@@##DELETE ME##@@'):
    '''Correct the start/end times of all tiers and fill gaps.
    Returns a copy of a textgrid, where empty gaps between intervals
    are filled with empty intervals and where start and end times are
    unified with the start and end times of the whole textgrid.
    '''
    textgrid_copy = copy.deepcopy(textgrid)
    for tier in textgrid_copy:
        if isinstance(tier, tgt.core.IntervalTier):
            tier_corrected = tier.get_copy_with_gaps_filled(
                textgrid.start_time, textgrid.end_time, empty_string)

            if merge_same_intervals:
                tier_corrected = tier_corrected.get_copy_with_same_intervals_merged()

            for i in range(1, len(tier_corrected.intervals) - 1):
                current_start_time = tier_corrected.intervals[i].start_time
                current_end_time = tier_corrected.intervals[i].end_time
                current_interval_annotation = tier_corrected.get_annotation_by_start_time(
                    current_start_time)
                current_interval_text = current_interval_annotation.text
                logger.debug('Current interval text %s \t Empty String %s',
                             current_interval_text, empty_string)
                if current_interval_text == empty_string:
                    interval_duration = round(
                        current_end_time - current_start_time, 3)
                    # logger.debug('Current Interval Duration %s \t Threshold %s',
                    #              interval_duration, joined_interval_threshold)
                    if interval_duration <= joined_interval_threshold:
                        tier_corrected.intervals[i -
                                                 1].end_time = current_end_time
                        # tier_corrected.intervals[i +
                        #                          1].start_time = tier_corrected.intervals[i].end_time
                        tier_corrected.intervals[i].text = delete_flag
                        # tier_corrected.delete_annotation_by_start_time(
                        #     current_start_time)

            tier_corrected.delete_annotations_with_text(delete_flag)

            position = textgrid_copy.tiers.index(tier)
            textgrid_copy.tiers[position] = tier_corrected

    return textgrid_copy
