def get_script_code(scriptname):
    scriptCode = {
        "Bengali": "Beng",
        "Devanagari": "Deva",
        "Gujarati": "Gujr",
        "Gurumukhi": "Guru",
        "IPA": "IPA",
        "Kannada": "Knda",
        "Latin": "Latn",
        "Malayalam": "Mlym",
        "Mayek": "Mtei",
        "Odia": "Orya",
        "Ol_Chiki": "Olck",
        "Tamil": "Taml",
        "Telugu": "Telu",
        "Toto": "Toto"
    }

    return scriptCode[scriptname]


def get_script_name(langname):
    langScript = {
        "Assamese": "Bengali",
        "Awadhi": "Devanagari",
        "Bangla": "Bengali",
        "Bengali": "Bengali",
        "Bhojpuri": "Devanagari",
        "Bodo": "Devanagari",
        "Braj": "Devanagari",
        "Bundeli": "Devanagari",
        "English": "Latin",
        "Gujarati": "Gujarati",
        "Haryanvi": "Devanagari",
        "Hindi": "Devanagari",
        "IPA": "IPA",
        "Kannada": "Kannada",
        "Khortha": "Devanagari",
        "Konkani": "Devanagari",
        "Magahi": "Devanagari",
        "Maithili": "Devanagari",
        "Malayalam": "Malayalam",
        "Marathi": "Devanagari",
        "Meitei": "Mayek",
        "Nepali": "Devanagari",
        "Odia": "Odia",
        "Punjabi": "Gurumukhi",
        "Santali": "Ol_Chiki",
        "Tamil": "Tamil",
        "Telugu": "Telugu",
        "Toto": "Toto"
    }

    return langScript[langname]


def get_langscripts(newLexemeData, lexemeFormData):
    langscripts = {}
    langscripts["langname"] = newLexemeData['Lexeme Language'][0]
    langscripts["langcode"] = newLexemeData['Lexeme Language'][0][:3].lower()
    headwordscript = list(
        lexemeFormData['Lexeme Form Script'][0].keys())[0]
    # langscripts["headwordscript"] = {headwordscript[0]+headwordscript[1:4].lower(): headwordscript}
    langscripts["headwordscript"] = {
        get_script_code(headwordscript): headwordscript}
    lexemeformscripts = {}
    for i in range(len(lexemeFormData['Lexeme Form Script'])):
        for lfs in lexemeFormData['Lexeme Form Script'][i].keys():
            # lexemeformscripts[lfs[0]+lfs[1:4]] = lfs
            lexemeformscripts[get_script_code(lfs)] = lfs
    langscripts["lexemeformscripts"] = lexemeformscripts
    glosslangs = {}
    glossscripts = {}
    for gl in newLexemeData.keys():
        if ('Gloss' in gl):
            gl = gl.split()[1]
            glosslangs[gl[0:3]] = gl
            glossscripts[get_script_code(
                get_script_name(gl))] = gl
    langscripts["glosslangs"] = glosslangs

    langscripts["glossscripts"] = glossscripts

    return langscripts
    # lexemeFormData['langscripts'] = langscripts


def get_langscripts_from_lexeme_form(current_projct_form):
    langscripts = {}

    langscripts["langname"] = current_projct_form['Lexeme Language']
    langscripts["langcode"] = current_projct_form['Lexeme Language'][:3].lower()

    headwordscript = current_projct_form['Lexeme Form Script'][0]
    langscripts["headwordscript"] = {
        get_script_code(headwordscript): headwordscript}

    lexemeformscripts = {}
    for current_script in current_projct_form['Lexeme Form Script']:
        lexemeformscripts[get_script_code(current_script)] = current_script
    langscripts["lexemeformscripts"] = lexemeformscripts

    glosslangs = {}
    glossscripts = {}

    all_gloss_langs = current_projct_form['Gloss Language']
    all_gloss_scripts = current_projct_form['Gloss Script']

    for gl, gls in zip(all_gloss_langs, all_gloss_scripts):
        glosslangs[gl[0:3]] = gl
        glossscripts[get_script_code(gls)] = gl

    langscripts["glosslangs"] = glosslangs

    langscripts["glossscripts"] = glossscripts

    return langscripts
