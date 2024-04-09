from phonemizer.backend import EspeakBackend
from phonemizer.separator import Separator
from app.controller import life_logging

logger = life_logging.get_logger()


def to_ipa(lemmas, lang_code, phone_separator='', word_separator=' '):
    space = ''
    if EspeakBackend.is_supported_language(lang_code):
        logger.info('Language %s supported in espeak for IPA', lang_code)
        backend = EspeakBackend(lang_code)
        separator = Separator(phone=phone_separator, word=word_separator)
        # no_space = backend.phonemize(lemmas)
        space = backend.phonemize(lemmas, separator=separator)
    else:
        logger.info(
            'Language %s not supported in espeak for IPA - skipping IPA generation', lang_code)
    return space
    # return no_space, space


# if __name__ == "__main__":
    # lang_code = 'hi'
    # print(EspeakBackend.supported_languages())
    # input_file = "test.txt"
    # fileinput = open(input_file, 'r')
    # output_file_ipa = input_file.replace('.txt', '_ipa_output_espeak.txt')
    # ipa_output_file = open(output_file_ipa, 'w')
    # all_lemmas = fileinput.read().split()
    # output1, output2 = to_ipa(all_lemmas, 'hi', ' ')
    # for out1, out2 in zip(output1, output2):
    #     ipa_output_file.write(out1+'\t'+out2+'\n')
