import logging


logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

file_handler = logging.FileHandler('log.log')
file_handler.setLevel(logging.DEBUG)

file_format = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s - %(lineno)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)

logger.addHandler(file_handler)
