from flask import Flask, request, Response
#,stream_with_context
from flask_login import current_user
#, login_user, logout_user, login_required
import zlib
# import gzip
# import zipfile
import io
import zipstream
import json
# import requests
import os 
# import BytesIO
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import RDFS, FOAF, RDF, SKOS
from rdflib.namespace import Namespace

from app import app, mongo
# from app.forms import UserLoginForm, RegistrationForm
# from app.models import UserLogin


import pandas as pd
import json


# app = Flask(__name__)

# def generate_text():
#     for x in range(10000):
#         yield f"this is my line: {x}\n".encode()

# @app.route('/stream_text')
# def stream_text():
#     response = Response(stream_with_context(generate_text()))
#     return response

# def generate_zip():
#     compressor = zlib.compressobj()
#     for x in range(10):
#         chunk = compressor.compress(f"this is my line: {x}\n".encode())
#         if chunk:
#             yield chunk
#     yield compressor.flush()

# @app.route('/stream_zip')
# def stream_zip():
#     response = Response(stream_with_context(generate_zip()), mimetype='application/zip')
#     response.headers['Content-Disposition'] = 'attachment; filename=data.zip'
#     return response

def _generator_file(cur_file):
    # for chunk in r.iter_content(1024):
    yield cur_file.read()

def _generator_lexemes(projectname, format='json'):
    # download a file and stream it
    lexemes = mongo.db.lexemes # collection containing entry of each lexeme and its details
    
    headwords = request.args.get('data')    # data through ajax

    if headwords != None:
        headwords = eval(headwords)
    print(f'{"="*80}\nheadwords from downloadselectedlexeme route:\n {headwords}\n{"="*80}')
    
    download_format = headwords['downloadFormat']

    del headwords['downloadFormat']
    print(f'{"="*80}\ndelete download format:\n {headwords}\n{"="*80}')

    for lexemeId in headwords.keys():
        lexeme = lexemes.find_one({'projectname' : projectname, 'lexemeId' : lexemeId},\
                            {'_id' : 0 })

        if format == 'json':
            lex_formatted = json.dumps(lexeme, indent = 2, ensure_ascii=False)
        else:
            # This is to make the generation memory-friendly if we could 
            # get a way of doing it - currently we are taking all entries into
            # memory before generating the file
            lex_formatted = get_other_format_lexeme(lexeme, format=format)
        yield lex_formatted


def _generator_lexeme_full(projectname, format='json', rdf_format='turtle'):
    lexemes = mongo.db.lexemes # collection containing entry of each lexeme and its details
    
    headwords = request.args.get('data')    # data through ajax

    if headwords != None:
        headwords = eval(headwords)
    print(f'{"="*80}\nheadwords from downloadselectedlexeme route:\n {headwords}\n{"="*80}')
    
    download_format = headwords['downloadFormat']

    del headwords['downloadFormat']
    print(f'{"="*80}\ndelete download format:\n {headwords}\n{"="*80}')

    all_lexemes = []
    for lexemeId in headwords.keys():
        lexeme = lexemes.find_one({'projectname' : projectname, 'lexemeId' : lexemeId},\
                            {'_id' : 0 })
        all_lexemes.append(lexeme)
    # lex_json = json.dumps(lexeme, indent = 2, ensure_ascii=False)

    if ('rdf' in format):
        formatted_lex = download_lexicon(all_lexemes, format, rdf_format=rdf_format)
    else:
        formatted_lex = download_lexicon(all_lexemes, format)
    
    yield formatted_lex


def download_lexicon(lex_json, output_format, rdf_format='turtle'):
    ontolex = Namespace('http://www.w3.org/ns/lemon/ontolex#')
    lexinfo = Namespace('http://www.lexinfo.net/ontology/2.0/lexinfo#')
    dbpedia = Namespace('http://dbpedia.org/resource/')
    pwn = Namespace('http://wordnet-rdf.princeton.edu/rdf/lemma/')


    domain_name = 'http://lifeapp.in'
    
    metadata = lex_json[0]
    project = metadata['projectname']

    lexicon = lex_json[1:]


    def add_canonical_form(g_form, life, lex_entry, lex_item, ipa, dict_lang):
        # g_form = Graph()
        # g_form.bind("ontolex", ontolex)
        # g_form.bind("life", life)

        g_form.add((
            URIRef(life[lex_item+'_form']),
            RDF.type,
            ontolex.form
        ))

        g_form.add((
            URIRef(life[lex_item+'_form']),
            ontolex.phoneticRep,
            Literal(ipa, lang="ipa")
        ))

        headword_script = list(lex_entry['langscripts']['headwordscript'])[0]
        print ('Headword script', headword_script)
        headword_lang = dict_lang+'-'+headword_script

        g_form.add((
            URIRef(life[lex_item+'_form']),
            ontolex.writtenRep,
            Literal(lex_item, lang=headword_lang)
        ))

        #If written reps are entered in other scripts, they are added
        other_scripts = lex_entry['langscripts']['lexemeformscripts']
        for other_script in other_scripts:
            lex_trans_forms = lex_entry['Lexeme Form']
            if other_script in lex_trans_forms:
                lex_trans = lex_trans_forms[other_script]
                g_form.add((
                    URIRef(life[lex_item+'_form']),
                    ontolex.writtenRep,
                    Literal(lex_trans, lang=dict_lang+'-'+other_script)
                ))
            

    def add_definition(g_form, life, lex_entry, lex_item, sense_defn):
        defn_langs = lex_entry['langscripts']['glosslangs']
        for defn_lang in defn_langs:
            if defn_lang in sense_defn:
                lex_defn = sense_defn[defn_lang]
                g_form.add((
                    URIRef(life[lex_item]),
                    ontolex.denotes,
                    URIRef(life[lex_item+'_definition'])
                ))

                g_form.add((
                    URIRef(life[lex_item+'_definition']),
                    SKOS.definition,
                    Literal(lex_defn, lang=defn_lang)
                ))

    def add_example(g_form, life, lex_item, example, ex_lang):
        g_form.add((
            URIRef(life[lex_item]),
            SKOS.example,
            Literal(example, lang=ex_lang)
        ))

    def add_other_forms(g_other_form, life, lex_entry, lex_item, other_form, dict_lang):
        # g_other_form = Graph()
        # g_other_form.bind("ontolex", ontolex)
        # g_other_form.bind("life", life)

        g_other_form.add((
            URIRef(life[lex_item+'_otherForm']),
            RDF.type,
            ontolex.form
        ))

        g_other_form.add((
            URIRef(life[lex_item+'_otherForm']),
            ontolex.writtenRep,
            Literal(other_form, lang=dict_lang)
        ))


    def add_sense(g_lex, life, lex_entry, sense_entry, lex_sense):
        g_lex.add((
            sense_entry,
            RDF.type,
            ontolex.LexicalSense
        ))

        if dbpedia_exists(lex_sense):
            g_lex.add((
                life[lex_entry],
                ontolex.denotes,
                dbpedia[lex_sense.capitalize()]
            ))

            g_lex.add((
                sense_entry,
                ontolex.reference,
                dbpedia[lex_sense.capitalize()]
            ))

        g_lex.add((
            sense_entry,
            ontolex.isSenseOf,
            life[lex_entry]
        ))
        

        wordnet_code = get_wordnet_code(lex_sense)
        if wordnet_code != '':
            g_lex.add((
                sense_entry,
                ontolex.isLexicalisedSenseOf,
                pwn[wordnet_code]
            ))
            g_lex.add((
                life[lex_entry],
                ontolex.evokes,
                pwn[wordnet_code]
            ))

        g_lex.add((
            sense_entry,
            ontolex.isSenseOf,
            life[lex_entry]
        ))

        #Creating dbpedia entry
        g_lex.add((
            dbpedia[lex_sense.capitalize()],
            ontolex.concept,
            pwn[wordnet_code]
        ))

        g_lex.add((
            dbpedia[lex_sense.capitalize()],
            ontolex.isReferenceOf,
            sense_entry
        ))

        g_lex.add((
            dbpedia[lex_sense.capitalize()],
            ontolex.isDenotedBy,
            ontolex.LexicalConcept
        ))


        #Creating WordNet entry
        g_lex.add((
            pwn[wordnet_code],
            RDF.type,
            life[lex_entry]
        ))
        
        g_lex.add((
            pwn[wordnet_code],
            ontolex.isEvokedBy,
            life[lex_entry]
        ))

        g_lex.add((
            pwn[wordnet_code],
            ontolex.lexicalizedSense,
            sense_entry
        ))

        g_lex.add((
            pwn[wordnet_code],
            ontolex.isConceptOf,
            dbpedia[lex_sense.capitalize()]
        ))


    def get_wordnet_code(lex_gloss):
        query = '''
        ASK WHERE {
        {<my-specific-URI> ?p ?o . }
        UNION
        {?s ?p <my-specific-URI> . }
        }
        '''
        return lex_gloss

    def dbpedia_exists(lex_gloss):
        query = '''
        ASK WHERE {
        {<my-specific-URI> ?p ?o . }
        UNION
        {?s ?p <my-specific-URI> . }
        }
        '''
        return True

    def json_to_rdf_lexicon(g_lex, lex_entry, domain_name,
                            project, output_format='turtle'):

        lex_item = lex_entry['headword']
        lex_pos = lex_entry['grammaticalcategory']
        # can_form = lex_item
        lex_pron = lex_entry['Pronunciation']
        lex_sense = lex_entry['SenseNew']
        dict_lang = lex_entry['langscripts']['langcode']

        # ontolex = URIRef('http://www.w3.org/ns/lemon/ontolex#')
        # lexinfo = URIRef('http://www.lexinfo.net/ontology/2.0/lexinfo#')

        life = Namespace(domain_name+'/'+project + '/word/')    

        g_lex.bind("ontolex", ontolex)
        g_lex.bind("lexinfo", lexinfo)
        g_lex.bind("skos", SKOS)
        g_lex.bind("life", life)
        g_lex.bind("pwnlemma", pwn)
        g_lex.bind("dbpedia", dbpedia)


        g_lex.add((
            URIRef(life[lex_item]),
            RDF.type,
            lexinfo.LexicalEntry
        ))

        g_lex.add((
            URIRef(life[lex_item]),
            lexinfo.partOfSpeech,
            lexinfo[lex_pos]
        ))

        # g_lex.add((
        #     URIRef(life[lex_item]),
        #     ontolex.lexicalForm,
        #     URIRef(life[lex_item+'_form'])
        # ))

        g_lex.add((
            URIRef(life[lex_item]),
            ontolex.canonicalForm,
            URIRef(life[lex_item+'_form'])
        ))

        # Add graph for the canonical form
        add_canonical_form(g_lex, life, lex_entry, lex_item, lex_pron, dict_lang)

        for i in range(1, len(lex_sense)):
            sense_gloss = lex_sense['Sense '+str(i)]["Gloss"]["eng"]
            sense_defn = lex_sense['Sense '+str(i)]["Definition"]        
            sense_ex = lex_sense['Sense '+str(i)]["Example"]

            sense_entry = life[lex_item+'_sense'+str(i)]
            g_lex.add((
                URIRef(life[lex_item]),
                ontolex.sense,
                URIRef(sense_entry)
            ))
            add_sense(g_lex, life, lex_item, sense_entry, sense_gloss)
            add_definition(g_lex, life, lex_entry, lex_item, sense_defn)
            add_example(g_lex, life, lex_item, sense_ex, dict_lang)


    def generate_rdf(lexicon, domain_name, project, rdf_format):
        g_lex = Graph()
        
        for lex_entry in lexicon:
            json_to_rdf_lexicon(g_lex, lex_entry, 
                            domain_name, project, rdf_format)
            
        # with open (write_path, 'w') as f_w:    
        rdf_out = g_lex.serialize(format=rdf_format)
            # f_w.write(rdf_out)
        return rdf_out

    def preprocess_csv_excel(lexicon):
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

        df.drop(columns=drop_cols, inplace=True)

        return df

    def generate_csv(lexicon):
        df = preprocess_csv_excel(lexicon)
        # with open (write_path, 'w') as f_w:
        csv_out = df.to_csv(index=False)
        return csv_out

    def generate_xlsx(lexicon):
        df = preprocess_csv_excel(lexicon)
        # with open (write_path, 'w') as f_w:
        write_file = io.BytesIO()
        writer = pd.ExcelWriter(write_file,engine='xlsxwriter')
        # df.to_excel(write_file, index=False, engine='xlsxwriter')
        df.to_excel(writer)
        writer.save()
        write_file.seek(0)
        return write_file
        
    def generate_ods(lexicon):
        df = preprocess_csv_excel(lexicon)
        # with open (write_path, 'w') as f_w:
        write_file = io.BytesIO()
        writer = pd.ExcelWriter(write_file,engine='openpyxl')
        # df.to_excel(write_file, index=False, engine='xlsxwriter')
        df.to_excel(writer)
        writer.save()
        write_file.seek(0)
        return write_file

    def generate_html(lexicon):
        df = preprocess_csv_excel(lexicon)
        # with open (write_path, 'w') as f_w:
        html_out = df.to_html(index=False)
        return html_out

    def generate_latex(lexicon):
        df = preprocess_csv_excel(lexicon)
        # with open (write_path, 'w') as f_w:
        latex_out = df.to_latex(index=False)
        return latex_out

    def generate_markdown(lexicon):
        df = preprocess_csv_excel(lexicon)
        # with open (write_path, 'w') as f_w:
        mdown_out = df.to_markdown(index=False)
        return mdown_out

    def generate_pdf(write_path, lexicon, project):
        return None

    def generate_json(lex_json):
        json_out = json.dumps(lex_json, indent = 2, ensure_ascii=False)
        # writing to currentprojectname.json 
        # with open(basedir+"/app/download/lexicon_"+activeprojectname+".json", "w") as outfile: 
        # with open(basedir+"/download/lexicon_"+activeprojectname+".json", "w") as outfile: 
        #     outfile.write(json_object)  
        return json_out


    # if (rdf_format in file_ext_map) or (output_format in file_ext_map):
    if output_format == 'rdf':
        # file_ext = file_ext_map[rdf_format]
        # write_file = os.path.join(write_path, 'lexicon_'+project+'_'+output_format+file_ext)
        formatted_lex = generate_rdf(lexicon, domain_name, project, rdf_format)
    else:
        # file_ext = file_ext_map[output_format]
        # write_file = os.path.join(write_path, 'lexicon_'+project+file_ext)
        if output_format == 'csv':
            formatted_lex = generate_csv(lexicon)
        elif output_format == 'xlsx':
            formatted_lex = generate_xlsx(lexicon)
        elif output_format == 'pdf':
            formatted_lex = generate_pdf(lexicon)
        elif output_format == 'markdown':
            formatted_lex = generate_markdown(lexicon)
        elif output_format == 'html':
            formatted_lex = generate_html(lexicon)
        elif output_format == 'latex':
            formatted_lex = generate_latex(lexicon)
        elif output_format == 'ods':
            formatted_lex = generate_ods(lexicon)
        elif output_format == 'json':
            formatted_lex = generate_json(lex_json)
# else:
#     print ('File type\t', output_format, '\tnot supported')
#     print ('Supported File Types', file_ext_map.keys())
    
    return formatted_lex


def _generator_sentences(projectname, format='json'):
    # download a file and stream it
    sentences = mongo.db.sentences # collection containing entry of each lexeme and its details
    
    for sentence in sentences.find({ 'projectname' : projectname, 'sentencedeleteFLAG' : 0 }, \
                                {'_id' : 0}):
        if format == 'json':
            sent_formatted = json.dumps(sentence, indent = 2, ensure_ascii=False)
        else:
            sent_formatted = get_other_format_sent(sentence, format=format)
        
        yield sent_formatted


def get_other_format_lexeme(lexemes, format):
    return lexemes


def get_other_format_sent(sentences, format):
    return sentences

def get_lexeme_files(projectname):
    # download a file and stream it
    lexemes = mongo.db.lexemes # collection containing entry of each lexeme and its details
    fs =  gridfs.GridFS(mongo.db) # creating GridFS instance to get required files
    
    headwords = request.args.get('data')    # data through ajax

    if headwords != None:
        headwords = eval(headwords)
    print(f'{"="*80}\nheadwords from downloadselectedlexeme route:\n {headwords}\n{"="*80}')
    
    del headwords['downloadFormat']
    print(f'{"="*80}\ndelete download format:\n {headwords}\n{"="*80}')

    all_files = {}
    for lexemeId in headwords.keys():
        lexeme = lexemes.find_one({'projectname' : projectname, 'lexemeId' : lexemeId},\
                            {'_id' : 0 })
        for lexkey, lexvalue in lexeme.items():
            if (lexkey == 'lexemeId'):    
                files = fs.find({'projectname' : projectname, 'lexemeId' : lexvalue})
                for entry_id, all_files in files.items():
                    for cur_file in all_files:
                        fname = cur_file.filename + '_' + entry_id
                        file_path = os.path.join("lexeme_files", fname)
                        all_files[file_path] = cur_file    
    return all_files   


def get_sent_files(projectname):
    # download a file and stream it
    sentences = mongo.db.sentences # collection containing entry of each lexeme and its details
    fs =  gridfs.GridFS(mongo.db) # creating GridFS instance to get required files
    
    all_files = {}
    for sentence in sentences.find({ 'projectname' : projectname, 'sentencedeleteFLAG' : 0 }, \
                                {'_id' : 0}):
        for sentkey, sentvalue in sentence.items():
            if (sentkey == 'sentenceId'):
                files = fs.find({'projectname' : projectname, 'sentenceId' : sentvalue})
                file_path = os.path.join("sent_files", sentvalue)
                all_files[file_path] = files
    return all_files
    

@app.route('/downloadproject', methods=['GET', 'POST'], endpoint='downloadproject')
def downloadproject():
    def generator(proj_name):
        lex_files = get_lexeme_files(proj_name)
        sent_files = get_sent_files(proj_name)

        z = zipstream.ZipFile(mode='w', compression=zlib.DEFLATED)

        z.write_iter("lexicon_"+proj_name+".json", _generator_lexemes(proj_name))
        z.write_iter("sentence_"+proj_name+".json", _generator_sentences(proj_name))

        for file_path, cur_file in lex_files.items():
            z.write_iter(file_path, _generator_file(cur_file))

        for file_path, cur_file in sent_files.items():
            z.write_iter(file_path, _generator_file(cur_file))

        # here is where the magic happens. Each call will iterate the generator we wrote for each file
        # one at a time until all files are completed.
        for chunk in z:
            yield chunk

    userprojects = mongo.db.userprojects # collection of users and their respective projects
    proj_name = userprojects.find_one({ 'username' : current_user.username })['activeproject']
    
    response = Response(generator(proj_name), mimetype='application/zip')
    response.headers['Content-Disposition'] = 'attachment; filename={}.zip'.format(proj_name)
    return response


@app.route('/downloadselectedlexeme', methods=['GET', 'POST'], endpoint='downloadselectedlexeme()')
def downloadselectedlexeme():    
    file_ext_map = {'turtle': '.ttl', 'n3': '.n3', 
    'nt': '.nt', 'xml': '.rdf', 'pretty-xml': '.rdfp', 'trix': '.trix', 
    'trig': '.trig', 'nquads': 'nquad', 'json': '.json', 'csv': '.csv',
    'xlsx': '.xlsx', 'pdf': '.pdf', 'html': '.html', 'latex': '.tex',
    'markdown': '.md', 'ods': '.ods'}

    userprojects = mongo.db.userprojects # collection of users and their respective projects
    proj_name = userprojects.find_one({ 'username' : current_user.username })['activeproject']
    headwords = request.args.get('data')    # data through ajax

    if headwords != None:
        headwords = eval(headwords)
    print(f'{"="*80}\nheadwords from downloadselectedlexeme route:\n {headwords}\n{"="*80}')
    
    download_format = headwords['downloadFormat']
    del headwords['downloadFormat']
    print(f'{"="*80}\ndelete download format:\n {headwords}\n{"="*80}')
    
    
    if ('rdf' in download_format):
        rdf_format = download_format[3:]
        download_format = 'rdf'
        file_ext = file_ext_map[rdf_format]
        data = _generator_lexeme_full(proj_name, download_format, rdf_format)
        print(rdf_format)
    else:
        file_ext = file_ext_map[download_format]
        data = _generator_lexeme_full(proj_name, download_format)
    
    if download_format == 'xlsx':
        response = Response(data.getvalue(), mimetype='application/octet-stream')
    elif download_format == 'json':
        response = Response(data, mimetype='application/json')
    elif download_format == 'latex':
        response = Response(data, mimetype='application/latex')
    elif download_format == 'markdown':
        response = Response(data, mimetype='application/markdown')
    elif download_format == 'html':
        response = Response(data, mimetype='application/html')
    elif download_format == 'csv':
        response = Response(data, mimetype='application/csv')
    elif 'rdf' in download_format:
        response = Response(data, mimetype='application/rdf')

    response.headers['Content-Disposition'] = 'attachment; filename={}.{}'.format(proj_name, file_ext)
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)