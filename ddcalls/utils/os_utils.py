# -*- coding: utf-8 -*-
"""
@author: Evgeny BAZAROV <baz.evgenii@gmail.com>
@brief:
"""

import os
import time
import json
import shutil
import pickle


def _gen_signature():
    # get pid and current time
    pid = int(os.getpid())
    now = int(time.time())
    # signature
    signature = "%d_%d" % (pid, now)
    return signature


def _create_dirs(dirs):
    for dir in dirs:
        os.makedirs(dir, exist_ok=True)


def _remove_files(files):
    for file in files:
        os.remove(file)


def _remove_dirs(dirs):
    for dir in dirs:
        shutil.rmtree(dir)


def json_save(path, data, indent=2, cls=json.JSONEncoder, sort=True):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, cls=cls, sort_keys=sort)


def json_load(path):
    assert os.path.isfile(path), "Wrong path to json file: {}".format(path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data


def pickle_save(path, data, protocol=4):
    with open(path, 'wb') as f:
        pickle.dump(data, f, protocol=protocol)


def pickle_load(path):
    with open(path, 'rb') as f:
        return pickle.load(f)


def print_pickle(paths=[]):
    if not paths:
        import sys
        paths = sys.argv[1:]

    for path in paths:
        print(pickle_load(path))


class bcolors:
    HEADER = '\033[104m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'