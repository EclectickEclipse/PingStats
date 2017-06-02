import logging
import logging.handlers as handlers

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

core_handler = handlers.RotatingFileHandler('logs/core.log',
                                            maxBytes=500000, backupCount=5)
core_handler.setFormatter(file_formatter)
core_handler.setLevel(logging.DEBUG)

plot_handler = handlers.RotatingFileHandler('logs/plot.log',
                                            maxBytes=500000, backupCount=5)
plot_handler.setFormatter(file_formatter)
plot_handler.setLevel(logging.DEBUG)

core_logger = logging.getLogger('base.core')
core_logger.setLevel(logging.DEBUG)
core_logger.addHandler(core_handler)
core_logger.addHandler(stream_handler)

plot_logger = logging.getLogger('base.plot')
plot_logger.setLevel(logging.DEBUG)
plot_logger.addHandler(plot_handler)
plot_logger.addHandler(stream_handler)
