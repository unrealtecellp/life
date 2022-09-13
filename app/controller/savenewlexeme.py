"""Module to save new lexeme details in database."""

import re
from datetime import datetime

def savenewlexeme(mongo,
                    projects,
                    lexemes,
                    scriptCode,
                    langScript,
                    new_lexeme_data,
                    new_lexeme_files,
                    projectowner,
                    current_username):
    """
    Args:
        mongo: instance of PyMongo.
        projects: instance of 'projects' collection.
        lexemes: instance of 'lexemes' collection.
        scriptCode: dictionary of script(language) and their code.
        langScript: dictionary of language and their script.
        new_lexeme_data: text data related to new lexeme details.
        new_lexeme_files: files related to new lexeme details.
        projectowner: name of the owner of the project.
        current_username: name of the current active user.

    Returns:
        _type_: _description_
    """

    newLexemeData = new_lexeme_data
    newLexemeFiles = new_lexeme_files
    newLexemeFilesName = {}
    for key in newLexemeFiles:
        if newLexemeFiles[key].filename != '':
            # adding microseconds of current time to differ two files of same name
            newLexemeFilesName[key] = (datetime.now().strftime('%f')+
                                        '_'+
                                        newLexemeFiles[key].filename)
    # format data filled in enter new lexeme form
    lexemeFormData = {}
    sense = {}
    variant = {}
    allomorph = {}
    lexemeFormData['username'] = projectowner

    def lexemeFormScript():
        """'List of dictionary' of lexeme form scripts"""
        lexemeFormScriptList = []
        for key, value in newLexemeData.items():
            if 'Script' in key:
                k = re.search(r'Script (\w+)', key)
                lexemeFormScriptList.append({k[1] : value[0]})
        lexemeFormData['headword'] =  list(lexemeFormScriptList[0].values())[0]
        return lexemeFormScriptList

    def senseListOfDict(senseCount):
        """'List of dictionary' of sense"""
        for num in range(1, int(newLexemeData['senseCount'][0])+1):
            senselist = []
            for key, value in newLexemeData.items():
                if 'Sense '+str(num) in key:
                    k = re.search(r'([\w+\s]+) Sense', key)
                    if k[1] == 'Semantic Domain' or k[1] == 'Lexical Relation':
                        senselist.append({k[1] : value})
                    else:
                        senselist.append({k[1] : value[0]})
            sense['Sense '+str(num)] = senselist
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
        return variant

    def allomorphListOfDict(allomorphCount):
        """'List of dictionary' of allomorph"""
        for num in range(1, int(newLexemeData['allomorphCount'][0])+1):
            # allomorphlist = []
            allomorphdict = {}
            for key, value in newLexemeData.items():
                if 'Allomorph '+str(num) in key:
                    k = re.search(r'([\w+\s]+) Allomorph', key)
                    allomorphdict[k[1]] = value[0]
            allomorph['Allomorph '+str(num)] = allomorphdict
        return allomorph

    def customFields():
        """'List of dictionary' of custom fields"""
        customFieldsDict = {}
        for key, value in newLexemeData.items():
            if 'Custom' in key:
                k = re.search(r'Field (\w+)', key)
                customFieldsDict[k[1]] = value[0]
        return customFieldsDict

    for key, value in newLexemeData.items():
        if 'Sense' in key or 'Variant' in key or 'Allomorph' in key: continue
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
    project = projects.find_one({}, {projectname : 1})
    lexemeCount = projects.find_one({}, {projectname : 1})[projectname]['lexemeInserted']+1
    lexemeId = projectname+lexemeFormData['headword']+str(lexemeCount)
    Id = re.sub(r'[-: \.]', '', str(datetime.now()))
    lexemeId = 'L'+Id

    # save file names of a lexeme in lexemeFormData
    # dictionary with other details related to the lexeme
    if len(newLexemeFilesName) != 0:
        lexemeFormData['filesname'] = newLexemeFilesName

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
    langscripts["headwordscript"] = {scriptCode[headwordscript]: headwordscript}
    lexemeformscripts = {}
    for i in range(len(lexemeFormData['Lexeme Form Script'])):
        for lfs in lexemeFormData['Lexeme Form Script'][i].keys():
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
        Gloss = {}
        Definition = {}
        for val in value:
            
            for k, v in val.items():
                if ("Gloss" in k):
                    Gloss[k.split()[1][:3].lower()] = v
                elif ("Definition" in k):
                    Definition[k.split()[1][:3].lower()] = v
                elif ("Lexical Relation" in k):
                    key['Lexical Relation'] = v[0]
                elif ("Semantic Domain" in k):
                    key['Semantic Domain'] = v[0]

                else:
                    key[k] = v
        
        key['Gloss'] = Gloss
        key['Definition'] = Definition     
        SenseNew[keyParent] = key

    lexemeFormData['SenseNew'] = SenseNew
    lexemeForm = {}
    for lexForm in lexemeFormData['Lexeme Form Script']:
        for lexKey, lexValue in lexForm.items():
            lexemeForm[scriptCode[lexKey]] = lexValue

    lexemeFormData['Lexeme Form'] = lexemeForm
    # keep only new updated keys as in 'lexemeEntry_sir.json' file in 'data_format folder
    # and delete old keys
    lexemeFormData.pop('Sense', None)
    lexemeFormData.pop('Lexeme Form Script', None)
    # when testing comment these to avoid any database update/changes
    # saving files for the new lexeme to the database in fs collection
    for (filename, key) in zip(newLexemeFilesName.values(), newLexemeFiles):
        mongo.save_file(filename,
                        newLexemeFiles[key],
                        lexemeId=lexemeId,
                        username=current_username,
                        projectname=lexemeFormData['projectname'],
                        headword=lexemeFormData['headword'],
                        updatedBy=current_username)
    # saving data for that new lexeme to database in lexemes collection
    lexemes.insert(lexemeFormData)
    # update lexemeInserted count of the project in projects collection
    project[projectname]['lexemeInserted'] = lexemeCount
    projects.update_one({}, { '$set' : { projectname : project[projectname] }})
