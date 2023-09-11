import json
import os

import pandas as pd
import regex as re
from pylatex import (Center, Command, Document, Foot, Head, LargeText,
                     LineBreak, MediumText, MiniPage, NewPage, PageStyle,
                     Section, Tabularx, TextColor, UnsafeCommand,
                     simple_page_number)
from pylatex.base_classes import CommandBase, Environment, Options
from pylatex.package import Package
from pylatex.utils import NoEscape, bold

script_map = {
    'IPA': '\ipa',
    'Ipa': '\ipa',
    'ipa': '\ipa',
    'Deva': '\dev',
    'Gujr': '\guj',
    'Guru': '\gur',
    'Beng': '\iben',
    'Orya': '\odia',
    'Knda': '\kan',
    'Taml': '\itam',
    'Telu': '\itel',
    'Mlym': '\mal'
}

language_map = {
    'ipa': '\ipa',
    'hin': '\dev',
    'guj': '\guj',
    'pun': '\gur',
    'ban': '\iben',
    'ass': '\iben',
    'odi': '\odia',
    'kan': '\kan',
    'tam': '\itam',
    'tel': '\itel',
    'mal': '\mal',
    'mar': '\dev',
    'bod': '\dev',
    'kon': '\dev',
    'nep': '\dev',
    'mai': '\dev',
    'mag': '\dev',
    'bho': '\dev',
    'awa': '\dev',
    'har': '\dev',
    'bra': '\dev',
    'bun': '\dev',
    'anp': '\dev'
}


class Titlepage(Environment):
    content_separator = "\n"


class Entry(CommandBase):
    """
    A class representing the custom LaTeX command for dictionary entry.

    This class represents the custom LaTeX command named
    ``entry``.
    """

    _latex_name = 'entry'
    # packages = [Package('color')]


class IPA(CommandBase):
    """
    A class representing the custom LaTeX command for IPA.

    This class represents the custom LaTeX command named
    ``ipa``.
    """

    _latex_name = 'ipa'


class Multicols(Environment):
    """A class to wrap LaTeX's alltt environment."""

    packages = [Package('multicol')]
    # escape = False
    # content_separator = "\n"


def get_latex_entries(all_entries, fields, dict_headword, char_list, doc, headwordscript, otherscript):
    # class Multicols(Environment):
    #     """A class to wrap LaTeX's alltt environment."""

    #     packages = [Package('multicol')]
    #     # escape = False
    #     # content_separator = "\n"
    eng_pattern = '[A-Za-z ]+'
    # print('Fields', fields)
    # print("Headword script", headwordscript)
    headword_script = script_map[headwordscript]
    # print("headword script", headword_script)
    # print("All characters", char_list)
    for character in char_list:
        cur_entries = all_entries[all_entries['firstchar'] == character]
        cur_entries.dropna(axis=1, how='all', inplace=True)

        cur_entries_list = cur_entries.to_dict('records')
        print('Current entries first', cur_entries_list[0])
        with doc.create(Section(NoEscape(headword_script+'{'+character+'}'), numbering=False)):
            with doc.create(Multicols(arguments='2')):
                for cur_entry in cur_entries_list:
                    entry_args = []
                    final_val = r''
                    sense_start = False
                    prev_sense_number = 0
                    for field in fields:
                        if field in cur_entry:
                            cur_val = cur_entry[field]
                            print('Current value', cur_val)
                            if not pd.isna(cur_val):
                                if field == 'headword':
                                    final_val = '\markboth{'+headword_script+'{'+cur_val+'}}{'+headword_script + \
                                        '{'+cur_val+'}}'+'\\textbf{' + \
                                        headword_script+'{'+cur_val+'}} '
                                elif field == 'Pronunciation':
                                    final_val = final_val + \
                                        '/\ipa{'+cur_val+'}/ '
                                    print('Pronunciation', cur_val)
                                elif field == 'grammaticalcategory':
                                    final_val = final_val + \
                                        '\\textit{'+cur_val+'} '
                                elif 'Lexeme' in field or 'SenseNew' in field:
                                    sense_parts = field.split('.')
                                    script_name = sense_parts[-1]

                                    if 'SenseNew' in field:
                                        cur_sense_number = sense_parts[1].split(
                                        )[-1]

                                        if cur_sense_number != prev_sense_number:
                                            sense_start = False
                                            prev_sense_number = cur_sense_number

                                    if not sense_start and 'SenseNew' in field:
                                        sense_start = True
                                        final_val = final_val.strip(
                                        ) + '. \\newline\\textbf{' + sense_parts[1] + '} '
                                    elif cur_val.strip() != '':
                                        final_val = final_val.strip() + '. '

                                    if script_name in script_map:
                                        latex_script = script_map[script_name]
                                        if not 'Lexeme' in field:
                                            final_val = final_val + \
                                                latex_script+'{'+cur_val+'} '
                                        else:
                                            if headwordscript != latex_script:
                                                final_val = final_val + \
                                                    latex_script + \
                                                    '{'+cur_val+'} '
                                    elif script_name in language_map:
                                        latex_script = language_map[script_name]
                                        final_val = final_val + \
                                            latex_script+'{'+cur_val+'} '
                                    else:
                                        # If Latn / Roman script then no need of other font
                                        # If not Roman and Lang / Script map does not have this
                                        # then defaults to Devanagari script
                                        # TODO: This needs improvement
                                        if re.search(eng_pattern, cur_val):
                                            final_val = final_val + cur_val + ' '
                                        else:
                                            if cur_val.strip() != '':
                                                latex_script = '\dev'
                                                final_val = final_val + \
                                                    latex_script + \
                                                    '{'+cur_val+'} '
                            else:
                                print('Current value', cur_val,
                                      'is null; skipping')
                            # entry_args.append(cur_val)
                    # doc.append(Entry(arguments=entry_args))
                    final_val = final_val+'\n\n'
                    doc.append(NoEscape(final_val.replace(', ,', ',')))

    return doc

# TODO: max_entries represent our assumption of max number of senses / variant forms /
# allomorphs that any entry could have - it should be made customisable and ideally equal to what
# it is in the dictionary


def expand_fields(lexicon, fields, max_entries=10):
    expanded_fields = []
    for field in fields:
        # if field not in columns:
        if type(field) == list:
            # if 'SenseNew' in field or 'VariantNew' in field or 'AllomorphNew' in field:
            base_field = field[0].split('.')
            base_field_name = base_field[0]
            # base_field_entries = lexicon[0][base_field_name]
            for i in range(max_entries):
                if 'SenseNew' in base_field_name:
                    insert_txt = 'Sense '+str(i+1)
                elif 'VariantNew' in base_field_name:
                    insert_txt = 'Variant '+str(i+1)
                elif 'AllomorphNew' in base_field_name:
                    insert_txt = 'Allomorph '+str(i+1)

                for field_type in lexicon:
                    base_parts = field_type.split('.')
                    rest_parts = '.'.join(base_parts[1:])
                    new_field_name = base_parts[0] + \
                        '.'+insert_txt + '.' + rest_parts
                    expanded_fields.append(new_field_name)
        else:
            expanded_fields.append(field)
    return expanded_fields


def get_relevant_data(lexicon, df, fields, dict_headword):
    # print('Fields', fields)
    # df = pd.json_normalize(lexicon)
    columns = df.columns

    # print ('New field', new_field)
    # print('Old columns', columns, len(columns))
    relevant_df = df[df.columns.intersection(fields)]

    # relevant_df = df[[new_field]]
    # print('Relevant df', relevant_df)
    # print('Headword col', dict_headword)

    relevant_df.sort_values(by=[dict_headword], inplace=True)
    relevant_df = relevant_df.reset_index()

    relevant_df['firstchar'] = relevant_df[dict_headword].apply(lambda x: x[0])
    # all_chars = df['firstchar'].unique()
    all_chars = relevant_df['firstchar'].drop_duplicates().sort_values()

    # print(all_chars)

    return relevant_df, all_chars


def generate_formatted_latex(
        write_path,
        lexicon,
        lexicon_df,
        project,
        editors=['Editor 1', 'Editor 2', 'Editor 3'],
        co_editors=['Co-ed 1', 'Co-ed 2', 'Co-ed 3'],
        metadata=['Centre for Advanced Research in Underrepresented Languages',
                  'UnReaL-TecE LLP'],
        fields=[],
        dict_headword='headword',  # lexemeformscripts.ipa.., glosslangs.hin..
        formatting_options={
        'documentclass': 'article',
        'document_options': 'a4paper, 12pt, twoside, xelatex',
            'geometry_options': {
                "top": "3.5cm",
                "bottom": "3.5cm",
                "left": "3.5cm",
                "right": "3.5cm",
                "columnsep": "30pt",
                "includeheadfoot": True
            }
        }):
    try:
        # geometry_options_1 = {"tmargin": "1cm", "lmargin": "10cm"}

        # class Titlepage(Environment):
        #     content_separator = "\n"

        # class Entry(CommandBase):
        #     """
        #     A class representing the custom LaTeX command for dictionary entry.

        #     This class represents the custom LaTeX command named
        #     ``entry``.
        #     """

        #     _latex_name = 'entry'
        #     # packages = [Package('color')]

        # class IPA(CommandBase):
        #     """
        #     A class representing the custom LaTeX command for IPA.

        #     This class represents the custom LaTeX command named
        #     ``ipa``.
        #     """

        #     _latex_name = 'ipa'

        doc = Document(default_filepath=write_path, documentclass=formatting_options['documentclass'],
                       document_options=formatting_options['document_options'],
                       geometry_options=formatting_options['geometry_options'], fontenc=None, inputenc=None)

        doc.preamble.append(Package('multicol'))
        doc.preamble.append(Package('microtype'))
        doc.preamble.append(Package('fancyhdr'))
        doc.preamble.append(Package('fontspec'))
        doc.preamble.append(Package('titlesec', options=['bf', 'center']))
        # \usepackage[bf,sf,center]{titlesec}

        # SORT THIS OUT - DONE!
        # doc.preamble.append(Command('newfontfamily', arguments=Command('ipafont', arguments=r'Doulos SIL')))

        # doc.preamble.append(Command('newcommand', arguments=Command('ipa', arguments=(r'{\ipafont #1}'), options=Options('1'))))
        # doc.preamble.append(NoEscape(r"\newcommand\ipa[1]{{\ipafont #1}}"))

        # \newfontfamily\ipafont{Charis SIL}
        # \newcommand\ipa[1]{{\ipafont #1}}

        # \newfontfamily\devanagarifont[Script=Devanagari]{Lohit-Devanagari}
        # \newcommand{\hi}[1]{{\devanagarifont #1}}
        doc.preamble.append(NoEscape(r"\newfontfamily\ipafont{Doulos SIL}"))

        doc.preamble.append(NoEscape(
            r"\newfontfamily\devanagarifont[Script=Devanagari]{Lohit-Devanagari}"))
        doc.preamble.append(
            NoEscape(r"\newfontfamily\bengalifont[Script=Bengali]{Lohit-Bengali}"))
        doc.preamble.append(
            NoEscape(r"\newfontfamily\gujaratifont[Script=Gujarati]{Lohit-Gujarati}"))
        doc.preamble.append(
            NoEscape(r"\newfontfamily\gurumukhifont[Script=Gurmukhi]{Lohit-Gurmukhi}"))
        doc.preamble.append(
            NoEscape(r"\newfontfamily\odiafont[Script=Odia]{Lohit-Odia}"))

        doc.preamble.append(
            NoEscape(r"\newfontfamily\kannadafont[Script=Kannada]{Lohit-Kannada}"))
        doc.preamble.append(
            NoEscape(r"\newfontfamily\tamilfont[Script=Tamil]{Lohit-Tamil}"))
        doc.preamble.append(
            NoEscape(r"\newfontfamily\telugufont[Script=Telugu]{Lohit-Telugu}"))
        doc.preamble.append(
            NoEscape(r"\newfontfamily\malayalamfont[Script=Malayalam]{Lohit-Malayalam}"))

        # doc.preamble.append(NoEscape(r"\newfontfamily\meiteifont[Script=Meitei Mayek]{}"))
        # doc.preamble.append(NoEscape(r"\newfontfamily\olchikifont[Script=Ol Chiki]{}"))
        # doc.preamble.append(NoEscape(r"\newfontfamily\limbufont[Script=Limbu]{}"))
        # doc.preamble.append(NoEscape(r"\newfontfamily\tibetanfont[Script=Tibetan]{}"))
        # doc.preamble.append(NoEscape(r"\newfontfamily\assamesefont[Script=Bengali]{Lohit-Bengali}"))

    #     testfeature{Script=Bengali}{\bengalitext}
    # \testfeature{Script=Gujarati}{\gujaratitext}
    # \testfeature{Script=Malayalam}{\malayalamtext}
    # \testfeature{Script=Gurmukhi}{\gurmukhitext}
    # \testfeature{Script=Tamil}{\tamiltext}

        ipa_comm = UnsafeCommand('newcommand', '\ipa', options=1,
                                 extra_arguments=r'{\ipafont #1}')

        dev_comm = UnsafeCommand('newcommand', '\dev', options=1,
                                 extra_arguments=r'{\devanagarifont #1}')
        ben_comm = UnsafeCommand('newcommand', '\iben', options=1,
                                 extra_arguments=r'{\bengalifont #1}')
        guj_comm = UnsafeCommand('newcommand', '\guj', options=1,
                                 extra_arguments=r'{\gujaratifont #1}')
        gur_comm = UnsafeCommand('newcommand', '\gur', options=1,
                                 extra_arguments=r'{\gurmukhifont #1}')
        odia_comm = UnsafeCommand('newcommand', '\odia', options=1,
                                  extra_arguments=r'{\odiafont #1}')

        kan_comm = UnsafeCommand('newcommand', '\kan', options=1,
                                 extra_arguments=r'{\kannadafont #1}')
        tam_comm = UnsafeCommand('newcommand', '\itam', options=1,
                                 extra_arguments=r'{\tamilfont #1}')
        tel_comm = UnsafeCommand('newcommand', '\itel', options=1,
                                 extra_arguments=r'{\telugufont #1}')
        mal_comm = UnsafeCommand('newcommand', '\mal', options=1,
                                 extra_arguments=r'{\malayalamfont #1}')

        doc.preamble.append(ipa_comm)

        doc.preamble.append(dev_comm)
        doc.preamble.append(ben_comm)
        doc.preamble.append(guj_comm)
        doc.preamble.append(gur_comm)
        doc.preamble.append(odia_comm)

        doc.preamble.append(kan_comm)
        doc.preamble.append(tam_comm)
        doc.preamble.append(tel_comm)
        doc.preamble.append(mal_comm)

        doc.preamble.append(Command('fancyhead', arguments=Command(
            'textsf', arguments=Command('rightmark')), options=Options('L')))
        doc.preamble.append(Command('fancyhead', arguments=Command(
            'textsf', arguments=Command('leftmark')), options=Options('R')))
        doc.preamble.append(Command('renewcommand', arguments=Command(
            'headrulewidth'), extra_arguments='1.4pt'))
        doc.preamble.append(Command('fancyfoot', arguments=Command('textbf', arguments=Command(
            'textsf', arguments=Command('thepage'))), options=Options('C')))
        doc.preamble.append(Command('renewcommand', arguments=Command(
            'footrulewidth'), extra_arguments='1.4pt'))

        doc_style = Command("pagestyle", arguments="fancy")
        doc.preamble.append(doc_style)

        headwordscript = list(
            lexicon[0]['langscripts']['headwordscript'].keys())[0]
        otherscript = lexicon[0]['langscripts']['lexemeformscripts'].keys()

        print("headword script", headwordscript)

        # if 'ipa' not in otherscript:
        #     other = True
        # elif len(otherscript) > 1:
        #     other = True
        # else:
        #     other = False

        # if headwordscript == 'ipa' and other:
        #     if '.ipa' in fields[0]:
        #         minimal_entry_args = r'\markboth{#1}{#1}\textbf{\ipa{#1}}\ {#2}\ \textit{#3}.\ {#4}.'
        # elif headwordscript == 'ipa':
        #     minimal_entry_args = r'\markboth{#1}{#1}\textbf{\ipa{#1}}\ {#2}\ \textit{#3}.\ {#4}.'
        # else:
        #     minimal_entry_args = r'\markboth{#1}{#1}\textbf{#1}\ \ipa{#2}\ \textit{#3}.\ {#4}.'

        # entry_args = minimal_entry_args
        # # flattened_fields = [item for sublist in fields for item in sublist]
        # print ('Flattened fields', flattened_fields)

        # expanded_fields = expand_fields(lexicon, fields, max_entries=2)

        # for field_num in range(4, len(expanded_fields)):
        #     count = field_num + 1
        #     entry_args = entry_args + '\ {#'+str(count)+'}.'
        # for field_num in range(4, len(flattened_fields)):
        # field_type = expanded_fields[field_num]
        # if 'SenseNew' in field_type:
        #     all_senses = lexicon[0]['SenseNew']
        #     print ('All senses', all_senses)
        #     for sense in all_senses:
        #         count = field_num + 1
        #         entry_args = entry_args + '\ {#'+str(count)+'}.'
        # elif 'VariantNew' in field_type:
        #     all_variants = lexicon[0]['VariantNew']
        #     for variant in all_variants:
        #         count = field_num + 1
        #         entry_args = entry_args + '\ {#'+str(count)+'}.'
        # elif 'AllomorphNew' in field_type:
        #     all_allomorphs = lexicon[0]['AllomorphNew']
        #     for allomoprh in all_allomorphs:
        #         count = field_num + 1
        #         entry_args = entry_args + '\ {#'+str(count)+'}.'
        # else:
        #     count = field_num + 1
        #     entry_args = entry_args + '\ {#'+str(count)+'}.'

        # new_comm = UnsafeCommand('newcommand', '\entry', options=len(expanded_fields),
        #  extra_arguments=entry_args)
        # new_comm_str = NoEscape(r"\newcommand{\entry}["+str(len(fields))+"]{"+entry_args+"}")
        # doc.preamble.append(new_comm)
        # doc.preamble.append(new_comm_str)
        # \newcommand{\entry}[4]{\markboth{#1}{#1}\textbf{#1}\ {(#2)}\ \textit{#3}\ $\bullet$\ {#4}}

        # \fancyhead[LE]{\textsf{\rightmark}}
    #     \fancyhead[L]{\textsf{\rightmark}} % Top left header
    # \fancyhead[R]{\textsf{\leftmark}} % Top right header
    # \renewcommand{\headrulewidth}{1.4pt} % Rule under the header
    # \fancyfoot[C]{\textbf{\textsf{\thepage}}} % Bottom center footer
    # \renewcommand{\footrulewidth}{1.4pt} % Rule under the footer
    # \pagestyle{fancy} % Use the custom headers and footers

        # title_page = PageStyle("titlepage")
        # doc.preamble.append(title_page)

        # content_page = PageStyle("contentpage")

        # with content_page.create(Head("C")) as header:
        #     with header.create(MiniPage(width=NoEscape(r"0.49\textwidth"),
        #                                      pos='t', align='l')) as book_name:
        #         book_name.append("Dictionary of "+project)

        # with content_page.create(Foot("C")) as footer:
        #     with footer.create(MiniPage(width=NoEscape(r"0.49\textwidth"),
        #                                      pos='t', align='r')) as page_number:
        #         page_number.append(simple_page_number())

        # doc.preamble.append(content_page)

        # doc.change_document_style("titlepage")
        # with title_page.create(Titlepage()):
        with doc.create(Center()):

            # Ading Title
            doc.append(NoEscape(
                r'''\vspace*{1cm}

            \Huge'''))
            # \newline
            doc.append(NoEscape(
                r'''\center \textbf{A Dictionary of '''+project.title().replace('_', '\_')+'''}'''))

            # doc.append(project.title())
            doc.append('\n\n')

            # Adding editors
            doc.append(NoEscape(r'''\vspace{1.5cm}
            
            '''))
            for ed_num in range(len(editors)):
                if ed_num > 0:
                    doc.append(',')
                doc.append(
                    NoEscape(r'''\normalsize \textbf{'''+editors[ed_num]+'''}'''))
            doc.append('\n\n')

            # Adding Institute / Project Name
            doc.append(NoEscape(r'''\vfill
            
            '''))
            doc.append(NoEscape(
                r'''\normalsize'''))
            for item in metadata:
                doc.append(item+'\n')

        # doc.append(title_page)

        # doc.change_document_style("contentpage")
        doc.append(NewPage())

        required_entries, character_list = get_relevant_data(
            lexicon, lexicon_df, fields, dict_headword)

        print('Data', required_entries)
        print("Char list", character_list)

        doc = get_latex_entries(required_entries, fields,
                                dict_headword, character_list, doc, headwordscript, otherscript)
        # doc.append(doc)

        # doc.append(text.decode('utf-8'))
        doc.generate_pdf(write_path, clean_tex=False, compiler='xelatex')
    except Exception as e:
        print(e)
        return True


def download_lexicon(lex_json, write_path,
                     output_format='rdf', rdf_format='turtle', fields=[]):
    file_ext_map = {'turtle': '.ttl', 'n3': '.n3',
                    'nt': '.nt', 'xml': '.rdf', 'pretty-xml': '.rdfp', 'trix': '.trix',
                    'trig': '.trig', 'nquads': 'nquad', 'json': '.json', 'csv': '.csv',
                    'xlsx': '.xlsx', 'pdf': '', 'html': '.html', 'latex_dict': '',
                    'markdown': '.md', 'ods': '.ods'}

    domain_name = 'http://lifeapp.in'

    metadata = lex_json[0]
    project = metadata['projectname']

    lexicon = lex_json[1:]

    if (rdf_format in file_ext_map) or (output_format in file_ext_map):
        if output_format == 'rdf':
            file_ext = file_ext_map[rdf_format]
            write_file = os.path.join(
                write_path, 'lexicon_'+project+'_'+output_format+file_ext)
            generate_rdf(write_file, lexicon, domain_name, project, rdf_format)
        else:
            file_ext = file_ext_map[output_format]
            write_file = os.path.join(write_path, 'lexicon_'+project+file_ext)
            if output_format == 'csv':
                generate_csv(write_file, lexicon)
            elif output_format == 'xlsx':
                generate_xlsx(write_file, lexicon)
            elif output_format == 'pdf':
                generate_pdf(write_file, lexicon)
            elif output_format == 'markdown':
                generate_markdown(write_file, lexicon)
            elif output_format == 'html':
                generate_html(write_file, lexicon)
            elif output_format == 'latex':
                generate_latex(write_file, lexicon)
            elif output_format == 'ods':
                generate_ods(write_file, lexicon)
            elif output_format == 'latex_dict':
                print('Write File Name', write_file)
                # if len(fields) == 0:
                #     fields = ['headword', 'Pronunciation', 'Lexeme Form.ipa', 'Lexeme Form.Deva', 'grammaticalcategory', [
                #         'SenseNew.Gloss.hin', 'SenseNew.Gloss.eng', 'SenseNew.Definition.hin', 'SenseNew.Definition.eng', 'SenseNew.Example']]
                lexicon_df = pd.json_normalize(lexicon)
                columns = lexicon_df.columns
                cur_fields = ['headword', 'Pronunciation']
                # sense_fields = ['', '', '']
                sense_fields = []
                for field in columns:
                    if 'SenseNew' in field:
                        if 'Gloss' in field or 'Definition' in field or 'Example' in field:
                            sense_fields.append(field)
                    elif 'Lexeme' in field:
                        cur_fields.append(field)
                cur_fields.append('grammaticalcategory')
                cur_fields.extend(sense_fields)

                generate_formatted_latex(
                    write_file, lexicon, lexicon_df, project, fields=cur_fields)
    else:
        print('File type\t', output_format, '\tnot supported')
        print('Supported File Types', file_ext_map.keys())


if __name__ == "__main__":
    # working_dir = '/home/ritesh/Dropbox/kmi-my-project-stuffs/LiFE/json_to_rdf'
    # working_dir = '../../app/'
    working_dir = '/home/ritesh/Dropbox/kmi-my-project-stuffs/LiFE/downloader'
    if not os.path.exists(working_dir):
        working_dir = '/home/ritesh/Dropbox/kmi-my-project-stuffs/LiFE/downloader'
    with open(os.path.join(working_dir, 'lexicon_ciil_demo.json')) as f_r:
        lex = json.load(f_r)
        out_form = 'latex_dict'
        rdf_form = 'xml'
        fields = []
        download_lexicon(lex, working_dir, fields, out_form, rdf_form)
