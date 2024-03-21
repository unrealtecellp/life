"""Module to read and preprocess different kinds of external files and return a Pnadas dataframe."""

import pandas as pd
from conll_df import conll_df
from io import open
from conllu import parse_incr
import io
from flask import flash, redirect, url_for
import xmltodict
import json
import re
import traceback
import unicodedata as ucd
# from app import mongo
# from app.controller import (getdbcollections, tagsetDetails)

# from app.controller import (
#     life_logging
# )

# logger = life_logging.get_logger()

# TODO: Implement the spell checker for Hindi


def spell_check_sentence_hin(sentence):
    return sentence


def merge_sentence_puncts_after_re_split(all_sentences_puncts):
    merged_sents = []
    for i in range(1, len(all_sentences_puncts), 2):
        sent = all_sentences_puncts[i-1]
        punct = all_sentences_puncts[i]
        merged_sent = sent + punct
        merged_sents.append(merged_sent)
    return merged_sents


def split_multiple_sentences(sentence, pattern):
    all_sentences_puncts = re.split(pattern, sentence)
    all_sentences = merge_sentence_puncts_after_re_split(all_sentences_puncts)

    return all_sentences


def split_tags_of_multiple_sentences(
        tags, sentence, split_sentences):
    # print('Original sentence', sentence)
    # print('Original Tags', tags)
    # print('Split sentences', split_sentences)
    split_tags = []
    tag_start = 0
    for count, sentence in enumerate(split_sentences):
        tokens = sentence.split()
        tag_end = tag_start + len(tokens)
        sentence_tags = tags[tag_start:tag_end]
        # sentence_tags = ' '.join(sentence_tags)
        split_tags.append(sentence_tags)
        tag_start = tag_end
    # print('Split tags', split_tags)
    return split_tags


def adjust_tag_token_alignment(sentence, corrected_sentence, tags):
    return tags


def remove_duplicate_sentences(sentences_df, column_name='Text'):
    '''Remove rows with duplicate sentences from the dataframe'''
    punctutaion_regex = '[,!?;:।\u0964\u0965।?!\(\)\{\}\[\],\'"`*]'

    print(sentences_df.head())
    # Remove all punctuations and multiple spaces from sentence
    sentences_df['Only_Text'] = sentences_df[column_name].apply(
        lambda x: re.sub(punctutaion_regex, '', x))
    sentences_df['Only_Text'] = sentences_df['Only_Text'].apply(
        lambda x: re.sub('\s+', ' ', x).strip())

    # Remove all rows with duplicate sentences
    sentences_df.drop_duplicates(subset=[column_name], inplace=True)
    return sentences_df


def preprocess_untagged_df(data_df, pipeline):
    data_df.rename({'Text': 'Original_Text'},
                   axis=1, inplace=True)

    print(data_df.head())

    data_df[['ID', 'Text']] = data_df.apply(
        preprocess_untagged_sentence, args=(pipeline,), axis=1, result_type='expand')

    # final_data_df = data_df.apply(pd.Series.explode).reset_index(drop=True)
    final_data_df = data_df.explode(
        ['ID', 'Text']).reset_index(drop=True)

    # final_data_df = remove_duplicate_sentences(final_data_df)

    print(final_data_df.head())

    return final_data_df


def preprocess_untagged_sentence(sentence, pipeline):
    text = sentence['Original_Text']
    text_id = sentence['ID']
    preprocessed_sentence = preprocess_sentence(
        text, pipeline)
    if len(preprocess_sentence) > 1:
        text_id = get_id_list(preprocessed_sentence, text_id)
    else:
        text_id = [text_id]

    return {'ID': text_id, 'Text': preprocessed_sentence}


def preprocess_sentence(sentence, pipeline, is_tagged=False, tags=[]):
    # pipeline_function = '_'.join(pipeline)
    preprocessed_sent = sentence
    preprocessed_tags = tags
    for current_pipeline in pipeline:
        preprocessed_sent, preprocessed_tags = globals(
        )['preprocess_'+current_pipeline](preprocessed_sent, is_tagged, preprocessed_tags)
    return preprocessed_sent, preprocessed_tags


def preprocess_ldcil_pos_hin(sentence, is_tagged=False, tags=[]):
    # Punctuation Normalisation
    sentence = sentence.replace('|', '।').replace(
        ':', ':').replace("'", '"').replace("`", '"')

    # Spelling Correction
    corrected_sentence = spell_check_sentence_hin(sentence)
    if len(corrected_sentence.split()) != len(sentence.split()):
        corrected_tags = adjust_tag_token_alignment(
            sentence, corrected_sentence, tags)
    else:
        corrected_tags = tags

    # Sentence Splitting
    sentence_pattern = '''([।?!]+ ?["'\)]?)'''
    split_sentences = split_multiple_sentences(
        corrected_sentence, sentence_pattern)
    if is_tagged and len(split_sentences) > 1:
        new_tags = split_tags_of_multiple_sentences(
            corrected_tags, corrected_sentence, split_sentences)
    else:
        new_tags = tags

    return split_sentences, new_tags


def get_id_list(stripped_sent, text_id):
    id_list = []
    for i, sent in enumerate(stripped_sent, start=1):
        id_list.append(text_id+'.'+str(i))

    return id_list


def get_token_annotations(x, delimiter, preprocess, preprocess_pipeline):
    # print(type(x))
    # print(x['Ann_Text'])
    text = x['Ann_Text']
    text_id = x['ID']
    # print(type(text))
    # if delimiter == '\\':
    tag_pattern = delimiter+"([A-Za-z_-]+)\s*"
    # print(tag_pattern)
    # if delimiter
    all_tags = re.findall(tag_pattern, text)
    stripped_sent = re.sub(tag_pattern, ' ', text)

    # print(type(all_tags), all_tags)
    # print(type(stripped_sent), stripped_sent)

    # all_tokens = x.split()
    # for token in all_tokens:
    #     token_tag = token.split(delimiter)
    #     stripped_token = token_tag[0]
    #     stripped_tag = token_tag[1]

    # strip_tokens = [[0] for token in all_tokens]
    # strip_tags = [token.split(delimiter)[1] for token in all_tokens]

    # stripped_sent = ' '.join(all_words)
    # print('Sent', x)
    # print('Tags', stripped_tags, '\nSentence', stripped_sent)
    # print(len(all_tags), len(stripped_sent.split()))

    if preprocess:
        stripped_sent, stripped_tags = preprocess_sentence(
            stripped_sent, preprocess_pipeline, is_tagged=True, tags=all_tags)
        if len(stripped_sent) > 1:
            text_id = get_id_list(stripped_sent, text_id)
        else:
            text_id = [text_id]
            stripped_tags = [all_tags]

    else:
        stripped_tags = [all_tags]

    if len(text_id) == len(stripped_sent) == len(stripped_tags):
        pass
    else:
        print('Unequal lengths', text_id)

        print('Tags', stripped_tags, '\nSentence', stripped_sent)
    return {'ID': text_id, 'Text': stripped_sent, 'Tags': stripped_tags}


def get_span_annotationGrid(data, tagset):
    # print(data)
    # print(tagset)
    # data = data[0]
    annotation_grid = {}
    sentence = data['Text']
    tag = data['Tags']

    # print(data['Ann_Text'])
    # print(data['Text'])

    # word_pos = iter((match.group(), match.span(1)) )

    for i, match in enumerate(re.finditer(r'(\S+)\s*', sentence)):
        # print(i, match, len(tag))
        current_tag = tag[i]
        parent_category = tagset[current_tag][0]
        child_category = tagset[current_tag][1]
        word = match.group(1)
        word_start = match.start(1)
        word_end = match.end(1)
        span_id = get_span_id(word_start, word_end)
        if parent_category not in annotation_grid:
            annotation_grid[parent_category] = {}
        annotation_grid[parent_category][span_id] = {}
        annotation_grid[parent_category][span_id]["startindex"] = str(
            word_start)
        annotation_grid[parent_category][span_id]["endindex"] = str(word_end)
        annotation_grid[parent_category][span_id]["textspan"] = word
        annotation_grid[parent_category][span_id][child_category] = current_tag

    print(annotation_grid)

    return {'Annotation_Grid': annotation_grid}


def get_id_prefix_zeros(index_pos):
    prefix_zero = ''
    if index_pos < 10:
        prefix_zero = '0000'
    elif index_pos < 100:
        prefix_zero = '000'
    elif index_pos < 1000:
        prefix_zero = '00'
    elif index_pos < 10000:
        prefix_zero = '0'

    return prefix_zero


def get_span_id(word_start, word_end):
    return get_id_prefix_zeros(word_start) + str(word_start) + get_id_prefix_zeros(word_end) + str(word_end)


def is_span_category(tag_category, tagset, dependencies):
    is_span = False
    parent_category = ''
    if tag_category in dependencies:
        dependency_condition = dependencies[tag_category]
        if '|' in dependency_condition:
            all_conditions = dependency_condition.split('|')
        elif '&' in dependency_condition:
            all_conditions = dependency_condition.split('&')
        else:
            all_conditions = [dependency_condition]

        print('All conditions', all_conditions)
        for dependency_condition in all_conditions:
            if '!=' in dependency_condition:
                dependency_parent_category = dependency_condition.split('!=')[
                    0]
                dependency_parent_type = tagset[dependency_parent_category][0]
                print(dependency_parent_category, dependency_parent_type)
                if dependency_parent_type == '#SPAN_TEXT#':
                    return True, dependency_parent_category
                else:
                    is_span, parent_category = is_span_category(dependency_parent_category,
                                                                tagset, dependencies)
                    if is_span:
                        break
            else:
                dependency_parent_category = dependency_condition.split('=')[0]
                is_span, parent_category = is_span_category(
                    dependency_parent_category, tagset, dependencies)
                if is_span:
                    break

    return is_span, parent_category


def get_tagset_to_category_mapping(annotation_tagset):
    '''
    This is supported only when all the tags across all subcategories in the tagset are unique - otherwise only one mapping is returned and rest are lost.
    In cases where the same tag is used across different subcategories / spans (such as the CSDR tagset) an explicit mapping must be provided in the uploaded file
    to enable correct uploading of annotated data.
    '''
    mapping = {}
    tagset = annotation_tagset['tagSet']
    dependencies = annotation_tagset['tagSetMetaData']['categoryDependency']
    print('Tagset', tagset)
    print('Dependencies', dependencies)

    for category, tags in tagset.items():
        for tag in tags:
            if category in dependencies:
                span_category, parent_span_category = is_span_category(
                    category, tagset, dependencies)
                if span_category:
                    mapping[tag] = (parent_span_category, category)
                else:
                    mapping[tag] = (category,)
            else:
                mapping[tag] = (category,)
    return mapping


def strip_token_annotations(x, delimiter):
    all_tokens = x.split()
    strip_tokens = [token.split(delimiter)[0] for token in all_tokens]
    stripped_sent = ' '.join(strip_tokens)
    return stripped_sent


def strip_token_annotations_ldcil(data_df, annotation_tagset, delimiter, preprocess, preprocess_pipeline):
    data_df.rename({'Text': 'Ann_Text'},
                   axis=1, inplace=True)

    # data_df['Text'] = data_df['Ann_Text'].apply(
    #     strip_token_annotations, args=delimiter)
    print(data_df.head())

    data_df[['ID', 'Text', 'Tags']] = data_df.apply(
        get_token_annotations, args=(delimiter, preprocess, preprocess_pipeline), axis=1, result_type='expand')

    # final_data_df = data_df.apply(pd.Series.explode).reset_index(drop=True)
    final_data_df = data_df.explode(
        ['ID', 'Text', 'Tags']).reset_index(drop=True)

    print(final_data_df.head())

    return final_data_df


def df_to_life_span_annotationGrid(
        data_df, annotation_tagset):
    print('Tagset', annotation_tagset)

    data_df[['Annotation_Grid']] = data_df.apply(
        get_span_annotationGrid, args=[annotation_tagset], axis=1, result_type='expand')

    return data_df


def parse_ldcil_xml(file_content, file_name, data_delimiter=' ', is_annotated=False, annotation_tagset={}, annotation_types=[], annotation_delimiter='', preprocess=False, preprocess_pipeline=[], remove_duplicates=True):
    data_metadata = {}
    file_metadata = {}
    tag_category_mapping = get_tagset_to_category_mapping(annotation_tagset)
    all_data = xmltodict.parse(file_content)
    # sentences = full_data["Doc"]["body"]
    sentences = all_data["Doc"].pop("body", [])
    print('Initial sentences', len(sentences))

    file_metadata.update(all_data)

    file_df = pd.DataFrame(sentences)
    file_df.reset_index(inplace=True)
    file_df.rename({'index': 'ID', 'Sentence': 'Text'},
                   axis=1, inplace=True)
    file_name = file_name[:file_name.rfind('.')]
    file_df['ID'] = file_df['ID'].apply(lambda x: file_name+'#'+str(x))
    file_df['Text'] = file_df['Text'].apply(lambda x: x.replace('\n', ' '))

    if is_annotated and 'token' in annotation_types:
        file_df = strip_token_annotations_ldcil(
            file_df, annotation_tagset, annotation_delimiter, preprocess, preprocess_pipeline)
        print(file_df.head())
        if remove_duplicates:
            # Remove Duplicates
            file_df = remove_duplicate_sentences(file_df)
        file_df = df_to_life_span_annotationGrid(
            file_df, tag_category_mapping)
    elif preprocess:
        file_df = preprocess_untagged_df(
            file_df, preprocess_pipeline)
        if remove_duplicates:
            # Remove Duplicates
            file_df = remove_duplicate_sentences(file_df)

    print(file_df.head())
    current_file_data = file_df.to_dict(orient='index')

    print(current_file_data)

    print(len(sentences))
    return file_df, data_metadata, file_metadata


def parse_conllu(file_content, file_name, data_delimiter=' ', is_annotated=False, annotation_tagset='', annotation_types=[], annotation_delimiter='', preprocess=False, preprocess_pipeline=[]):
    # file_df = conll_df(file_content, file_index=False)
    data_metadata = {}
    file_metadata = {}
    file_df = pd.DataFrame()
    file_df.columns = ['ID', 'Text']
    for tokenlist in parse_incr(file_content):
        current_data = {}
        current_data['ID'] = tokenlist.metadata['text_id']
        current_data['Text'] = tokenlist.metadata['text']
        file_df = file_df.append(current_data, ignore_index=True)

    return file_df, data_metadata, file_metadata


def parse_tsv(file_content, file_name, data_delimiter='\t', is_annotated=False, annotation_tagset='', annotation_types=[], annotation_delimiter='', preprocess=False, preprocess_pipeline=[]):
    data_metadata = {}
    file_metadata = {}
    data_df = pd.read_csv(file_content, sep='\t', dtype=str)
    return data_df, data_metadata, file_metadata


def parse_csv(file_content, file_name, data_delimiter=',', is_annotated=False, annotation_tagset='', annotation_types=[], annotation_delimiter='', preprocess=False, preprocess_pipeline=[]):
    data_metadata = {}
    file_metadata = {}
    data_df = pd.read_csv(file_content, sep=data_delimiter, dtype=str)
    return data_df, data_metadata, file_metadata


def parse_xlsx(file_content, file_name, data_delimiter=',', is_annotated=False, annotation_tagset='', annotation_types=[], annotation_delimiter='', preprocess=False, preprocess_pipeline=[]):
    data_metadata = {}
    file_metadata = {}
    data_df = pd.read_excel(file_content, dtype=str)
    return data_df, data_metadata, file_metadata


def parse_one_file_data(myfile, file_name, file_format, csv_delimiter, is_annotated, annotation_tagset, annotation_types, annotation_delimiter, preprocess, preprocess_pipeline):
    data_metadata = {}
    file_metadata = {}
    try:
        data_df, data_metadata, file_metadata = globals(
        )['parse_'+file_format](io.BytesIO(
            myfile.read()), file_name, csv_delimiter, is_annotated, annotation_tagset, annotation_types, annotation_delimiter, preprocess, preprocess_pipeline)
    except:
        data_df = pd.DataFrame({})
        flash(
            f"File: {file_name} is not a valid format and so not uploaded. Supported file formats are (.tsv, .csv. .xlsx, .xml, .conllu).")

    return data_df, data_metadata, file_metadata


if __name__ == "__main__":
    file_path = '/home/ritesh/Dropbox/PROJECTS/LiFE/samples/PoS_testing/HN00040.xml'
    file_name = 'HN00040.xml'
    is_annotated = True
    # annotation_tagset = {"Tag": "BIS"}
    annotation_tagset = 'BIS'
    annotation_types = ['token']  # token, span, document
    annotation_delimiter = '\\\\'
    preprocess = True
    preprocess_pipeline = ['ldcil_pos_hin']
    data_delimiter = ''
    file_format = 'ldcil_xml'

    annotation_tagset = {"tagSet": {
        "00-TOKEN-LEVEL": ["#SPAN_TEXT#"],
        "A-POS": ["N_NN", "N_NNP", "N_NST", "PR_PRP", "PR_PRF", "PR_PRL", "PR_PRC", "PR_PRQ", "PR_PRI", "DM_DMD", "DM_DMR", "DM_DMQ", "DM_DMI", "V_VM", "V_VAUX", "JJ", "RB", "PSP", "CC_CCD", "CC_CCS", "CC_UT", "RP_RPD", "RP_INJ", "RP_INTF", "RP_NEG", "QT_QTF", "QT_QTC", "QT_QTO", "RD_RDF", "RD_SYM", "RD_PUNC", "RD_UNK", "RD_ECH"],
        "B-MORPH-GENDER": ["M", "F"],
        "C-MORPH-NUMBER": ["S", "P"],
        "D-CASE": ["NOM", "ACC", "DAT", "GEN", "LOC", "ABL", "BEN"],
        "E-TENSE": ["PRS", "PST"],
        "F-ASPECT": ["HAB", "IMP", "PERF", "PROG"],
        "G-MOOD": ["IND", "IMP", "IRR", "COND", "SUBJ", "OPT"],
        "H-PERSON": ["1", "2", "3"],
        "I-VOICE": ["ACT", "PAS"],
        "J-POLITE": ["FORM", "INFORM"],
        "01-Validation-Score": ["0", "1", "2"],
        "02-COMMENTS": [""]
    },
        "tagSetMetaData": {
        "categoryDependency": {
            "A-POS": "00-TOKEN-LEVEL!=''",
            "B-MORPH-GENDER": "00-TOKEN-LEVEL!=''",
            "C-MORPH-NUMBER": "00-TOKEN-LEVEL!=''",
            "D-CASE": "00-TOKEN-LEVEL!=''",
            "E-TENSE": "00-TOKEN-LEVEL!=''",
            "F-ASPECT": "00-TOKEN-LEVEL!=''",
            "G-MOOD": "00-TOKEN-LEVEL!=''",
            "H-PERSON": "00-TOKEN-LEVEL!=''",
            "I-VOICE": "00-TOKEN-LEVEL!=''",
            "J-POLITE": "00-TOKEN-LEVEL!=''"
        },
        "defaultCategoryTags": {
            "00-TOKEN-LEVEL": "",
            "A-POS-OUTER": ["NOUN"],
            "A-POS": ["NOUN"],
            "B-MORPH-GENDER": ["F"],
            "C-MORPH-NUMBER": "S",
            "D-CASE": "NOM",
            "E-TENSE": "PRS",
            "F-ASPECT": "IMP",
            "G-MOOD": "IND",
            "H-PERSON": "3",
            "I-VOICE": "ACT",
            "J-POLITE": "FORM",
            "01-Validation-Score": "2",
            "02-COMMENTS": ""
        },
        "categoryHtmlElement": {
            "00-TOKEN-LEVEL": "modal+textarea",
            "A-POS-OUTER": "select",
            "A-POS": "select",
            "B-MORPH-GENDER": "select",
            "C-MORPH-NUMBER": "radio",
            "D-CASE": "radio",
            "E-TENSE": "radio",
            "F-ASPECT": "radio",
            "G-MOOD": "radio",
            "H-PERSON": "radio",
            "I-VOICE": "radio",
            "J-POLITE": "radio",
            "01-Validation-Score": "radio",
            "02-COMMENTS": "textarea"
        },
        "categoryHtmlElementProperties": {
            "00-TOKEN-LEVEL": "'’",
            "A-POS-OUTER": "required",
            "A-POS": "required",
            "B-MORPH-GENDER": "multiple=multiple",
            "C-MORPH-NUMBER": "'’",
            "D-CASE": "'’",
            "E-TENSE": "'’",
            "F-ASPECT": "'’",
            "G-MOOD": "'’",
            "H-PERSON": "'’",
            "I-VOICE": "'’",
            "J-POLITE": "'’",
            "01-Validation-Score": "required",
            "02-COMMENTS": "'’"
        }
    }
    }
    # tagsets = getdbcollections.getdbcollections(mongo,
    # 'tagsets')

    # tag_category_mapping = get_tagset_to_category_mapping(annotation_tagset)
    # print(tag_category_mapping)

    with open(file_path, 'rb') as myfile:
        # file_content = io.BytesIO(f_r.read())
        try:
            data_df, data_metadata, file_metadata = globals(
            )['parse_'+file_format](io.BytesIO(
                myfile.read()), file_name, data_delimiter, is_annotated, annotation_tagset, annotation_types, annotation_delimiter, preprocess, preprocess_pipeline)
        except Exception as e:
            data_df = pd.DataFrame({})
            print('exception', e)
            traceback.print_exc()
            # flash(
            #     f"File: {file_name} is not a valid format and so not uploaded. Supported file formats are (.tsv, .csv. .xlsx, .xml, .conllu).")

    # parse_ldcil_xml(io.BytesIO(
    #     myfile.read()), file_name, data_delimiter, is_annotated, annotation_tagset, annotation_types, annotation_delimiter, preprocess, preprocess_pipeline)
