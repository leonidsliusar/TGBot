import logging
import sys

path = './log.log'
logger_main = logging.getLogger(__name__)
logger_main.setLevel('DEBUG')

file_handler = logging.FileHandler(path)
file_handler.setLevel(logging.DEBUG)

file_format = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s - %(lineno)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_format)

# logger_main.addHandler(file_handler)


path_test = './tests/log_test.log'
logger_test = logging.getLogger(__name__)
logger_test.setLevel('DEBUG')

file_handler_test = logging.FileHandler(path_test)
file_handler_test.setLevel(logging.DEBUG)
file_handler_test.setFormatter(file_format)

logger_test.addHandler(file_handler_test)

# stream logger
logger_test_stream = logging.getLogger(__name__)
logger_test.setLevel('DEBUG')

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(file_format)
stream_format = logging.Formatter('%(filename)s - %(funcName)s - %(lineno)s - %(levelname)s - %(message)s')

logger_test_stream.addHandler(stream_handler)
