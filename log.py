import logging
import logging.handlers as handlers
import sys  # for grabbing the program directory
import os  # for splitting sys.argv
PROGRAM_PATH = os.path.split(sys.argv[0])[0]
CORE_LOG_PATH = os.path.join(PROGRAM_PATH, 'logs', 'core.log')
MAIN_LOG_PATH = os.path.join(PROGRAM_PATH, 'logs', 'main.log')
PLOT_LOG_PATH = os.path.join(PROGRAM_PATH, 'logs', 'plot.log')

# BEGIN Logger setup
file_formatter = logging.Formatter(
    '%(asctime)s:'
    '%(filename)-24s:'
    '%(name)-24s:'
    '%(levelname)-10s:'
    '%(funcName)-24s:'
    '%(lineno)-4d:'
    '%(message)s'
)

stream_formatter = logging.Formatter(
    '%(levelname)-10s:'
    '%(name)-20s:'
    '%(message)s'
)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(stream_formatter)
stream_handler.setLevel(logging.INFO)

core_handler = handlers.RotatingFileHandler(CORE_LOG_PATH,
                                            maxBytes=500000, backupCount=5)
core_handler.setFormatter(file_formatter)
core_handler.setLevel(logging.DEBUG)

main_handler = handlers.RotatingFileHandler(MAIN_LOG_PATH,
                                            maxBytes=500000, backupCount=5)
main_handler.setFormatter(file_formatter)
main_handler.setLevel(logging.DEBUG)

plot_handler = handlers.RotatingFileHandler(PLOT_LOG_PATH,
                                            maxBytes=500000, backupCount=5)
plot_handler.setFormatter(file_formatter)
plot_handler.setLevel(logging.DEBUG)

core_logger = logging.getLogger('base.core')
core_logger.setLevel(logging.DEBUG)
core_logger.addHandler(core_handler)
core_logger.addHandler(stream_handler)

main_logger = logging.getLogger('base.main')
main_logger.setLevel(logging.DEBUG)
main_logger.addHandler(main_handler)
main_logger.addHandler(stream_handler)

plot_logger = logging.getLogger('base.plot')
plot_logger.setLevel(logging.DEBUG)
plot_logger.addHandler(plot_handler)
plot_logger.addHandler(stream_handler)
