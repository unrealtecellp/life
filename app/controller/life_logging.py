import logging
import logging.config

print('in logging')

def get_logger():

    logging.config.fileConfig('logging.config')

    # create logger
    logger = logging.getLogger('life')

    return logger