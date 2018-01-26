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


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected (yes, true, t, y ,1, no, false, f, n, 0).')
