from phonemizer.backend import EspeakBackend
from phonemizer.separator import Separator
from phonemizer import phonemize
from app.controller import life_logging

logger = life_logging.get_logger()


def to_ipa(lemmas, lang_code, phone_separator='', word_separator=' '):
    space = ''
    if EspeakBackend.is_supported_language(lang_code):
        logger.info('Language %s supported in espeak for IPA', lang_code)
        backend = EspeakBackend(lang_code)
        separator = Separator(phone=phone_separator, word=word_separator)
        # no_space = backend.phonemize(lemmas)
        space = backend.phonemize(
            lemmas, separator=separator)
        # space = phonemize(
        #     lemmas, separator=separator, language_switch='keep-flags')
    else:
        # print('')
        logger.info(
            'Language %s not supported in espeak for IPA - skipping IPA generation', lang_code)
    return space
    # return no_space, space


# if __name__ == "__main__":
    # lang_code = 'hi'
    # # print(EspeakBackend.supported_languages())
    # # input_file = "test.txt"
    # data = ["लास्ट में एन और सेकंड लास्ट में वॉवेल ठीक है दिस इज़ द वे 2 कन्वर्ट थिन आर हो जाएगा 2 एन हो जाएंगे तो हमारा लास्ट में क्या है एन तो हम 2 एन कर देंगे सिंपल।",
    #         "अंडरस्टैंड।",
    #         "ओके",
    #         "ठीक है यस।",
    #         "बनाना ग्रेप्स ऑरेंज।",
    #         "और यहाँ पे आपको क्या लगने लगती है कैसे महसूस कर रहा है बहुत ही अच्छा क्यों अच्छा लगने लगती है?"]
    # # all_lemmas =
    # # fileinput = open(input_file, 'r')
    # # output_file_ipa = input_file.replace('.txt', '_ipa_output_espeak.txt')
    # # ipa_output_file = open(output_file_ipa, 'w')
    # # all_lemmas = fileinput.read().split()
    # for sent in data:
    #     output1 = to_ipa(sent.split(), 'hi', '', ' ')
    #     print(output1)
    # # for out1, out2 in zip(output1, output2):
    #     ipa_output_file.write(out1+'\t'+out2+'\n')
