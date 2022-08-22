"""Module to work on the sentence details (transcription and all) through ajax."""

import json
from pprint import pprint

def getnewsentence(transcriptionDetails):
    if (transcriptionDetails != None):
        transcriptionDetails = json.loads(transcriptionDetails)
        pprint(transcriptionDetails)
        print(transcriptionDetails)
        print(type(transcriptionDetails))
        print()
        with open("data_format/tempSentence.json", 'w') as f:
            json.dump(transcriptionDetails, f)

        # sentence = request.args.get('a').split(',')                    # data through ajax
        # sentenceFieldId = sentence[0]
        # split_sentence = sentence[1].split()
        # print(sentenceFieldId, split_sentence)
        # sentenceDetails = {}
        # # generate unique id using the datetime module
        # Id = re.sub(r'[-: \.]', '', str(datetime.now()))
        # sentenceDetails['username'] = current_user.username
        # sentenceDetails['projectname'] = activeprojectname
        # sentenceDetails['sentencedeleteFLAG'] = 0
        # sentenceDetails['updatedBy'] = current_user.username
        # sentenceDetails['sentenceId'] = 'S'+Id
        # sentenceDetails['sentence'] = sentence[1]
        # sentenceDetails['langscripts'] = {
        #                                     "langname": "English",
        #                                     "langcode": "eng",
        #                                     "sentencescripts": {
        #                                         "ipa": "International Phonetic Alphabet",
        #                                         "Latn": "Latin"
        #                                     },
        #                                     "glosslangs": {
        #                                         "eng": "English"        
        #                                     },
        #                                     "glossscripts": {
        #                                         "Latn": "Latin"
        #                                     },
        #                                     "translationlangs": {
        #                                         "eng": "English",
        #                                         "hin": "Hindi"
        #                                     },
        #                                     "translationscripts": {
        #                                         "Latn": "Latin",
        #                                         "Deva": "Devanagari"
        #                                     }
        #                                 }
        # # sentenceDetails['lexemeId'] = 'L'+Id
        # morphemes = {}
        # gloss = {}
        # for morpheme in split_sentence:
        #     remorpheme = re.sub(r'[#-]', '', morpheme)
        #     morphemes[remorpheme] = morpheme.lower()
        #     if ('#' in morpheme):
        #         # morpheme = re.sub(r'-', ' -', morpheme)
        #         morpheme = morpheme.split('#')
        #         mor = []
        #         for morph in morpheme:
        #             mor.append(morph)
        #         gloss[remorpheme] = mor
        #     else:
        #         gloss[morpheme] = [morpheme]        
        # sentenceDetails['morphemes'] = morphemes
        # # pprint(sentenceDetails) 
        # # print(gloss) 