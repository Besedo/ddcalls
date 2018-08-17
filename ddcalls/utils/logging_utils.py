# -*- coding: utf-8 -*-
"""
@author: Evgeny BAZAROV <baz.evgenii@gmail.com>
@brief:
"""

import os
import sys
import logging
import argparse

logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(logdir, logname, loglevel=logging.DEBUG):
    logger = logging.getLogger(__name__)
    logger.setLevel(loglevel)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Save log to file
    fh = logging.FileHandler(os.path.join(logdir, logname))
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Print log to console
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


def bool_flag(s):
    """
    Parse boolean arguments from the command line.
    """
    if s.lower() in ['no', 'off', 'false', '0']:
        return False
    if s.lower() in ['yes', 'on', 'true', '1']:
        return True
    raise argparse.ArgumentTypeError("{} invalid value for a boolean flag (yes, true, on, 1, no, false, off, 0)".format(s))


def file_flag(s):
    """
    Check path to file arguments from the command line.
    """
    if os.path.isfile(s):
        return s
    raise argparse.ArgumentTypeError("{} path to file doesn't exist".format(s))
