# ------------------------------------------------------------------------------
#  es7s/holms
#  (c) 2024 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import logging


class DummyLogger:
    def log(self, *args, **kwargs):
        ...
    debug = log
    info = log
    warning = log
    error = log


_logger: logging.Logger|DummyLogger = DummyLogger()


def init_log(verbose: int):
    level = logging.WARNING
    if verbose > 0:
        level = logging.DEBUG
    global _logger
    _logger = logging.getLogger(__package__)
    _logger.setLevel(level)
    hdlr = logging.StreamHandler()

    hdlr.setLevel(level)
    _logger.addHandler(hdlr)


def destroy_log():
    global _logger
    if not isinstance(_logger, logging.Logger):
        return
    _logger.handlers.clear()
    _logger = DummyLogger()


def logger(*, require=True) -> logging.Logger|DummyLogger:
    global _logger
    if require and not isinstance(_logger, logging.Logger):
        raise RuntimeError("Logger is not initialized")
    return _logger
