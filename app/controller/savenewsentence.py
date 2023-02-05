"""Module to save new sentences details in the database"""

from datetime import datetime
import re

def savenewsentence(mongo,
                    sentences,
                    current_username,
                    activeprojectname,
                    newSentencesData,
                    newSentencesFiles):
    """_summary_

    Args:
        mongo: instance of PyMongo.
        sentences: instance of 'sentences' collection.
        current_username: name of the current active user.
        activeprojectname: name of the project activated by current active user.
        newSentencesData: text data related to new sentence details.
        newSentencesFiles: files related to new sentence details.
    """
    # dictionary to store files name
    newSentencesFilesName = {}
    for key in newSentencesFiles:
        if newSentencesFiles[key].filename != '':
            # adding microseconds of current time to differ two files of same name
            newSentencesFilesName[key] = (datetime.now().strftime('%f')+newSentencesFiles[key].filename)

    sentenceFieldIds = []
    interlineargloss = {}
    for key in newSentencesData.keys():
        if ('sentenceField' in key):
            # print(key[-1])
            sentenceFieldIds.append(key[-1])

    for sFId in sentenceFieldIds:
        # print(type(sFId), sFId)
        sentenceFieldId = sFId
        sentence = newSentencesData['sentenceField'+sFId][0]
        # interlineargloss['level_3'] = sentence
        split_sentence = sentence.split()
        sentenceMorphemicBreak = newSentencesData['sentenceMorphemicBreak'+sFId][0]
        interlineargloss['level_1'] = sentenceMorphemicBreak.replace('#', '')
        split_sentenceMorphemicBreak = sentenceMorphemicBreak.strip().split()
        # print(split_sentenceMorphemicBreak)
        
        # save details for each sentence as the format shown in file name sentenceEntry.json in data_format folder
        sentenceDetails = {}
        # generate unique id using the datetime module
        Id = re.sub(r'[-: \.]', '', str(datetime.now()))
        sentenceDetails['username'] = current_username
        sentenceDetails['projectname'] = activeprojectname
        sentenceDetails['sentencedeleteFLAG'] = 0
        sentenceDetails['updatedBy'] = current_username
        sentenceDetails['sentenceId'] = 'S'+Id
        sentenceDetails['sentence'] = sentence
        sentenceDetails['langscripts'] = {
                                        "langname": "English",
                                        "langcode": "eng",
                                        "sentencescripts": {
                                            "ipa": "International Phonetic Alphabet",
                                            "Latn": "Latin"
                                        },
                                        "glosslangs": {
                                            "eng": "English"
                                        },
                                        "glossscripts": {
                                            "Latn": "Latin"
                                        },
                                        "translationlangs": {
                                            "eng": "English",
                                            "hin": "Hindi"
                                        },
                                        "translationscripts": {
                                            "Latn": "Latin",
                                            "Deva": "Devanagari"
                                        }
                                    }

        morphemes = {}
        gloss = {}
        pos = {}
        split_sentenceMorphemeWise = []
        morphemeId = sFId+str(0)
        lexglossId = 'morphemicgloss'+morphemeId
        lexemeId = sentenceDetails['sentenceId']+'L'+str(0)
        lextypeId = 'lextype'+morphemeId
        posId = 'pos'+morphemeId
        interlineargloss_level_2 = ''
        for i in range(len(split_sentenceMorphemicBreak)):
            morph = {}

            if ('#' in split_sentenceMorphemicBreak[i]):
                # print(split_sentenceMorphemicBreak[i].split('#'))
                morphemic = split_sentenceMorphemicBreak[i].split('#')
                split_sentenceMorphemicBreak[i] = split_sentenceMorphemicBreak[i].replace('#', '')
                morphemes[split_sentence[i]] = split_sentenceMorphemicBreak[i]
                # print(morphemic)
                for j in range(len(morphemic)):
                    lexglossId = lexglossId[:len(lexglossId)-1]+str(int(lexglossId[-1])+1)
                    lexemeId = lexemeId[:len(lexemeId)-1]+str(int(lexemeId[-1])+1)
                    lextypeId = lextypeId[:len(lextypeId)-1]+str(int(lextypeId[-1])+1)
                    posId = posId[:len(posId)-1]+str(int(posId[-1])+1)
                    # print(morphemeId, lexglossId, lexemeId, lextypeId, posId)
                    # print(m)
                    morph[morphemic[j]] = {'lexgloss': '.'.join(newSentencesData[lexglossId]),
                                        'lexemeID': lexemeId,
                                        'lextype': newSentencesData[lextypeId][0]}
                    if ('-' in morphemic[j][0]):
                        interlineargloss_level_2 += '-'+'.'.join(newSentencesData[lexglossId])
                    elif ('-' in morphemic[j][-1]):
                        interlineargloss_level_2 += '.'.join(newSentencesData[lexglossId])+'-'
                    else:
                        interlineargloss_level_2 += '.'.join(newSentencesData[lexglossId])
                    gloss[split_sentence[i]] = morph
                    if ('-' not in morphemic[j] and posId in newSentencesData):
                        pos[split_sentence[i]] = newSentencesData[posId][0]
            # print(morph)
                    split_sentenceMorphemeWise.append(morphemic[j])
            else:
                lexglossId = lexglossId[:len(lexglossId)-1]+str(int(lexglossId[-1])+1)
                lexemeId = lexemeId[:len(lexemeId)-1]+str(int(lexemeId[-1])+1)
                lextypeId = lextypeId[:len(lextypeId)-1]+str(int(lextypeId[-1])+1)
                posId = posId[:len(posId)-1]+str(int(posId[-1])+1)
                # print(morphemeId, lexglossId, lexemeId, lextypeId, posId) 
                #   
                morphemes[split_sentence[i]] = split_sentenceMorphemicBreak[i]
                morph[split_sentence[i]] = {'lexgloss': '.'.join(newSentencesData[lexglossId]),
                                        'lexemeID': lexemeId,
                                        'lextype': newSentencesData[lextypeId][0]}
                interlineargloss_level_2 += ' '+'.'.join(newSentencesData[lexglossId])+' '          
                gloss[split_sentence[i]] = morph
                pos[split_sentence[i]] = newSentencesData[posId][0]
                split_sentenceMorphemeWise.append(split_sentenceMorphemicBreak[i])

            sentenceDetails['morphemes'] = morphemes

        # print(split_sentenceMorphemicBreak)
        sentenceDetails['gloss'] = gloss
        sentenceDetails['pos'] = pos

        translation = {}
        translation['eng-Latn'] = newSentencesData['sentenceTranslation'+sFId][0]
        translation['hin-Deva'] = sentenceDetails['sentence']
        sentenceDetails['translation'] = translation

        interlineargloss['level_2'] = interlineargloss_level_2.strip().replace('  ', ' ')
        interlineargloss['level_3'] = translation['eng-Latn']
        sentenceDetails['interlineargloss'] = interlineargloss

        # save file names of a sentence in sentenceDetails dictionary
        # with other details related to the sentence
        if len(newSentencesFilesName) != 0:
            sentenceDetails['filesname'] = newSentencesFilesName

        # saving files for the new lexeme to the database in fs collection
        for (filename, key) in zip(newSentencesFilesName.values(), newSentencesFiles):
            mongo.save_file(filename, newSentencesFiles[key],
                            sentenceId=sentenceDetails['sentenceId'],
                            username=current_username,
                            projectname=sentenceDetails['projectname'],
                            sentence = sentenceDetails['sentence'],
                            updatedBy=current_username
                            )

        # enter the sentence details to the database
        sentences.insert(sentenceDetails)
