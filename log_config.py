import logging

#  output in file
path = './log.log'
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

file_handler = logging.FileHandler(path)
file_handler.setLevel(logging.DEBUG)

file_format = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s - %(lineno)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)

logger.addHandler(file_handler)
