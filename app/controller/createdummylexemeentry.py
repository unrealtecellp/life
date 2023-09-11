"""Module to create a dummy lexeme entry in the database"""

import re
from datetime import datetime


def createdummylexemeentry(projects,
                           lexemes,
                           activeprojectform,
                           scriptCode,
                           langScript,
                           current_username):
    """
    Args:
        projects: instance of 'projects' collection.
        lexemes: instance of 'lexemes' collection.
        activeprojectform: form created for the active project.
        scriptCode: dictionary of script(language) and their code.
        langScript: dictionary of language and their script.
        current_username: name of the current active user.

    Returns:
        _type_: _description_
    """

    newLexemeData = {
        'allomorphCount': ['1'],
        'senseCount': ['1'],
        'variantCount': ['1']
    }

    if activeprojectform is not None:
        for key, value in activeprojectform.items():
            if ('Upload' in key or
                    'username' in key):
                continue
            elif (key == 'projectname'):
                newLexemeData[key] = [value]
            elif (key == 'Lexeme Language'):
                newLexemeData[key] = [value]
            elif (key == 'Allomorph'):
                allomorphCount = int(newLexemeData['allomorphCount'][0])
                for i in range(allomorphCount):
                    newLexemeData['Stem Allomorph '+key+' '+str(i+1)] = ['']
                    newLexemeData['Morph Type '+key+' '+str(i+1)] = ['']
                    newLexemeData['Environment '+key+' '+str(i+1)] = ['']
            elif (key == 'Variant'):
                variantCount = int(newLexemeData['variantCount'][0])
                for i in range(variantCount):
                    newLexemeData['Variant Form '+key+' '+str(i+1)] = ['']
                    newLexemeData['Variant Type '+key+' '+str(i+1)] = ['']
            elif (key == 'Lexeme Form Script'):
                for script in activeprojectform['Lexeme Form Script']:
                    newLexemeData['Lexeme Form Script '+script] = ['']
            elif (key == 'Gloss Language'):
                senseCount = int(newLexemeData['senseCount'][0])
                for i in range(senseCount):
                    for lang in activeprojectform['Gloss Language']:
                        newLexemeData['Gloss '+lang +
                                      ' Sense'+' '+str(i+1)] = ['']
                        newLexemeData['Definition '+lang +
                                      ' Sense'+' '+str(i+1)] = ['']
                    newLexemeData['Grammatical Category Sense ' +
                                  str(i+1)] = ['']
                    newLexemeData['Example Sense '+str(i+1)] = ['']
                    newLexemeData['Free Translation Sense '+str(i+1)] = ['']
                    newLexemeData['Semantic Domain Sense '+str(i+1)] = ['']
                    newLexemeData['Lexical Relation Sense '+str(i+1)] = ['']
            elif (key == 'Custom Fields'):
                # print(value)
                for item in activeprojectform['Custom Fields']:
                    k = str(list(item.keys())[0])
                    v = str(list(item.values())[0])
                    if (v != 'multimedia'):
                        newLexemeData['Custom Field '+k] = ['']
            else:
                newLexemeData[key] = ['']

    # pprint(newLexemeData)
    # format data filled in enter new lexeme form
    lexemeFormData = {}
    sense = {}
    variant = {}
    allomorph = {}

    lexemeFormData['username'] = current_username

    def lexemeFormScript():
        """'List of dictionary' of lexeme form scripts"""
        lexemeFormScriptList = []
        for key, value in newLexemeData.items():
            if 'Script' in key:
                k = re.search(r'Script (\w+)', key)
                lexemeFormScriptList.append({k[1]: value[0]})
        lexemeFormData['headword'] = list(lexemeFormScriptList[0].values())[0]
        return lexemeFormScriptList

    def senseListOfDict(senseCount):
        """'List of dictionary' of sense"""
        for num in range(1, int(newLexemeData['senseCount'][0])+1):
            senselist = []
            for key, value in newLexemeData.items():
                if 'Sense '+str(num) in key:
                    k = re.search(r'([\w+\s]+) Sense', key)
                    if k[1] == 'Semantic Domain' or k[1] == 'Lexical Relation':
                        senselist.append({k[1]: value})
                    else:
                        senselist.append({k[1]: value[0]})
            sense['Sense '+str(num)] = senselist
        # pprint.pprint(sense)
        return sense

    def variantListOfDict(variantCount):
        """'List of dictionary' of variant"""
        for num in range(1, int(newLexemeData['variantCount'][0])+1):
            # variantlist = []
            variantdict = {}
            for key, value in newLexemeData.items():
                if 'Variant '+str(num) in key:
                    k = re.search(r'([\w+\s]+) Variant', key)
                    # variantlist.append({k[1] : value[0]})
                    variantdict[k[1]] = value[0]
            variant['Variant '+str(num)] = variantdict
        # pprint.pprint(variant)
        return variant

    def allomorphListOfDict(allomorphCount):
        """'List of dictionary' of allomorph"""
        for num in range(1, int(newLexemeData['allomorphCount'][0])+1):
            # allomorphlist = []
            allomorphdict = {}
            for key, value in newLexemeData.items():
                if 'Allomorph '+str(num) in key:
                    k = re.search(r'([\w+\s]+) Allomorph', key)
                    # allomorphlist.append({k[1] : value[0]})
                    allomorphdict[k[1]] = value[0]
            # allomorph['Allomorph '+str(num)] = allomorphlist
            allomorph['Allomorph '+str(num)] = allomorphdict
        # pprint.pprint(allomorph)
        return allomorph

    def customFields():
        """'List of dictionary' of custom fields"""
        # customFieldsList = []
        customFieldsDict = {}
        for key, value in newLexemeData.items():
            if 'Custom' in key:
                k = re.search(r'Field (\w+)', key)
                # customFieldsList.append({k[1] : value[0]})
                customFieldsDict[k[1]] = value[0]
        # pprint.pprint(sense)
        return customFieldsDict

    for key, value in newLexemeData.items():
        if ('Sense' in key or
            'Variant' in key or
                'Allomorph' in key):
            continue
        elif key == 'senseCount':
            Sense = senseListOfDict(value[0])
            lexemeFormData['Sense'] = Sense
        elif key == 'variantCount':
            Variant = variantListOfDict(value[0])
            lexemeFormData['Variant'] = Variant
        elif key == 'allomorphCount':
            Allomorph = allomorphListOfDict(value[0])
            lexemeFormData['Allomorph'] = Allomorph
        elif 'Script' in key:
            lexemeFormData['Lexeme Form Script'] = lexemeFormScript()
        elif 'Custom' in key:
            lexemeFormData['Custom Fields'] = customFields()
        elif key == 'Lexeme Language':
            pass
        else:
            lexemeFormData[key] = value[0]

    # create lexemeId
    projectname = newLexemeData['projectname'][0]
    project = projects.find_one({}, {projectname: 1})
    lexemeCount = projects.find_one({}, {projectname: 1})[
        projectname]['lexemeInserted']+1
    lexemeId = projectname+lexemeFormData['headword']+str(lexemeCount)
    Id = re.sub(r'[-: \.]', '', str(datetime.now()))
    lexemeId = 'L'+Id

    # print(f"{'#'*80}\n{list(lexemeFormData['Sense']['Sense 1'][0].keys())}")
    gloss = list(lexemeFormData['Sense']['Sense 1'][0].keys())
    lexemeFormData['gloss'] = lexemeFormData['Sense']['Sense 1'][0][gloss[0]]
    # grammaticalcategory  = list(lexemeFormData['Sense']['Sense 1'][4].keys())
    # print(f"{'#'*80}\n{lexemeFormData['Sense']['Sense 1']}")
    for senseData in lexemeFormData['Sense']['Sense 1']:
        if list(senseData.keys())[0] == 'Grammatical Category':
            # print(f"{'#'*80}\n{list(senseData.values())[0]}")
            lexemeFormData['grammaticalcategory'] = list(senseData.values())[0]
    lexemeFormData['lexemedeleteFLAG'] = 0
    lexemeFormData['updatedBy'] = current_username
    lexemeFormData['lexemeId'] = lexemeId

    langscripts = {}
    langscripts["langname"] = newLexemeData['Lexeme Language'][0]
    langscripts["langcode"] = newLexemeData['Lexeme Language'][0][:3].lower()
    headwordscript = list(lexemeFormData['Lexeme Form Script'][0].keys())[0]
    # langscripts["headwordscript"] = {headwordscript[0]+headwordscript[1:4].lower(): headwordscript}
    langscripts["headwordscript"] = {
        scriptCode[headwordscript]: headwordscript}
    lexemeformscripts = {}
    for i in range(len(lexemeFormData['Lexeme Form Script'])):
        for lfs in lexemeFormData['Lexeme Form Script'][i].keys():
            # lexemeformscripts[lfs[0]+lfs[1:4]] = lfs
            lexemeformscripts[scriptCode[lfs]] = lfs
    langscripts["lexemeformscripts"] = lexemeformscripts
    glosslangs = {}
    glossscripts = {}
    for gl in newLexemeData.keys():
        if ('Gloss' in gl):
            gl = gl.split()[1]
            glosslangs[gl[0:3]] = gl
            glossscripts[scriptCode[langScript[gl]]] = gl
    langscripts["glosslangs"] = glosslangs

    langscripts["glossscripts"] = glossscripts
    lexemeFormData['langscripts'] = langscripts

    SenseNew = {}

    for key, value in lexemeFormData['Sense'].items():
        keyParent = key
        key = {}
        # print(keyParent)
        Gloss = {}
        Definition = {}
        Lexical_Relation = {}
        for val in value:

            for k, v in val.items():
                if ("Gloss" in k):
                    Gloss[k.split()[1][:3].lower()] = v
                    # print(key, k, v)
                elif ("Definition" in k):
                    Definition[k.split()[1][:3].lower()] = v
                elif ("Lexical Relation" in k):
                    # Lexical_Relation[v[0]] = v[0]
                    key['Lexical Relation'] = v[0]
                elif ("Semantic Domain" in k):
                    # Lexical_Relation[v[0]] = v[0]
                    key['Semantic Domain'] = v[0]

                else:
                    key[k] = v

        key['Gloss'] = Gloss
        key['Definition'] = Definition
        # key['Lexical Relation'] = Lexical_Relation
        SenseNew[keyParent] = key
    # pprint(senseNew)
    lexemeFormData['SenseNew'] = SenseNew

    lexemeForm = {}
    for lexForm in lexemeFormData['Lexeme Form Script']:
        for lexKey, lexValue in lexForm.items():
            # lexemeForm[lexKey[:4]] = lexValue
            lexemeForm[scriptCode[lexKey]] = lexValue

    lexemeFormData['Lexeme Form'] = lexemeForm

    # keep only new updated keys as in 'lexemeEntry_sir.json' file in 'data_format folder
    # and delete old keys
    lexemeFormData.pop('Sense', None)
    lexemeFormData.pop('Lexeme Form Script', None)

    # saving data for that new lexeme to database in lexemes collection
    lexemes.insert_one(lexemeFormData)
    # print(f'{"="*80}\nLexeme Form :')
    # pprint(lexemeFormData)
    # print(f'{"="*80}')

    # update lexemeInserted count of the project in projects collection
    project[projectname]['lexemeInserted'] = lexemeCount
    # print(f'{"#"*80}\n{project}')
    projects.update_one({}, {'$set': {projectname: project[projectname]}})
