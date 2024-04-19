"""
Provides some scaffolding for convenient logging
"""

import logging as pylogging
import sys

DEFAULT_FORMAT = (
    "%(asctime)s %(levelname)s %(name)s:%(funcName)s:%(lineno)s - %(message)s"
)


class LevelFilter(pylogging.Filter):
    """Filters out log levels less than or equal to passlevel from a given handler"""

    def __init__(self, passlevel, reject=True, mode="min"):
        self.passlevel = passlevel  # Level to check
        self.reject = reject  # If false, exact match only
        self.mode = mode  # Or max

    def filter(self, record):
        if self.reject:
            if self.mode == "min":
                return record.levelno >= self.passlevel
            elif self.mode == "max":
                return record.levelno <= self.passlevel
            else:
                raise Exception("unknown mode %s" % self.mode)
        else:
            return record.levelno == self.passlevel


def set_basic_configuration(logger_name=None, loglevel=pylogging.DEBUG):
    logger = pylogging.getLogger(logger_name)
    logger.setLevel(loglevel)

    chout = pylogging.StreamHandler(sys.stdout)
    cherr = pylogging.StreamHandler(sys.stderr)

    chout.addFilter(LevelFilter(pylogging.WARNING, mode="max"))
    cherr.addFilter(LevelFilter(pylogging.ERROR, mode="min"))

    chout.setLevel(pylogging.DEBUG)
    cherr.setLevel(pylogging.ERROR)

    chout.setFormatter(pylogging.Formatter(DEFAULT_FORMAT))
    cherr.setFormatter(pylogging.Formatter(DEFAULT_FORMAT))

    logger.addHandler(chout)
    logger.addHandler(cherr)

    return logger
