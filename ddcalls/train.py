# -*- coding: utf-8 -*-
"""
@author: Evgeny Bazarov <baz.evgenii@gmail.com>
@brief:
"""

import os
import sys
import time
import json
import argparse
import shutil
from datetime import datetime

from ddcalls.utils import os_utils
from ddcalls.utils import dd_utils
from ddcalls.utils import config_utils
from ddcalls.utils.dd_client import DD
from ddcalls.utils.os_utils import bcolors
from ddcalls.utils.dd_board_logger import DDBoard
from ddcalls.utils.logging_utils import get_logger, str2bool


def get_opt():
    parser = argparse.ArgumentParser("""DeepDetect training script""")
    parser.add_argument("--path_dd_config", type=str)
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--logdir_ddboard", type=str, default=None)
    parser.add_argument("--use_ddboard", type=str2bool, default=False)
    # Options that will overwrite config parameters
    parser.add_argument("--sname", type=str, default=None)
    parser.add_argument("--data", type=str, default=None)
    parser.add_argument("--repository", type=str, default=None)
    parser.add_argument("--gpu", type=str2bool, default=None)
    parser.add_argument("--gpuid", type=int, default=None)
    parser.add_argument("--templates", type=str, default=None)
    parser.add_argument("--resume", type=str2bool, default=None)    

    opt = parser.parse_args()
    return opt


def train(opt=None):

    # script execution timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # loading config file
    config = os_utils.json_load(opt["path_dd_config"])

    # overwrite parameters if needed
    config = config_utils.update_config(
        stage="train",
        config=config,
        new_params=opt
    )

    # repository path check, create repository if needed
    repository = config["service"]["model"]["repository"]
    if not os.path.isdir(repository):
        print("Repository doesn't exist, will create:", repository)
        os.makedirs(repository)

    # logger for logs
    log = get_logger(repository, "{}_train.log".format(timestamp))

    log.info(bcolors.HEADER + "running TRAINING script" + bcolors.ENDC)
    log.info("-> checking paths to training data")
    for path_data in config["train"]["data"]:
        assert os.path.exists(path_data), "Path doesn't exist: {}".format(path_data)

    ####### Connecting to DeepDetect
    log.info(bcolors.OKGREEN + "-> connecting to DeepDetect server" + bcolors.ENDC)
    dd = DD(opt["host"], opt["port"])
    dd.set_return_format(dd.RETURN_PYTHON)

    ####### Check of service name
    log.info("-> checking service name")
    sname = config_utils.format_sname(config["service"]["sname"])
    log.info(" - will use service name: {}".format(sname))
    if dd_utils.dd_sname_exist(dd, sname):
        log.info(bcolors.WARNING + " - service with same name already exist" + bcolors.ENDC)
        sname = "{}_{}".format(sname, timestamp)
        log.info(bcolors.WARNING + " - will use other name for service: {}".format(sname) + bcolors.ENDC)
    config["service"]["sname"] = sname

    ####### Saving config
    log.info(bcolors.OKGREEN + "-> saving DeepDetect config" + bcolors.ENDC)
    path_config = os.path.join(repository, os.path.basename(opt["path_dd_config"]))
    log.info(" - {}".format(path_config))
    os_utils.json_save(path=path_config, data=config)
    # remove null values from config
    config = config_utils.dict_remove_empty(config)

    ####### Service creation
    log.info(bcolors.HEADER + "-> service creation" + bcolors.ENDC)
    log.info(json.dumps(config["service"], indent=4, sort_keys=True))
    dd_response = dd_utils.dd_put_service(
        dd=dd,
        config=config["service"],
        resume_or_predict=opt['resume']
    )
    log.info(" - {}".format(dd_response))

    ####### Training
    log.info(bcolors.HEADER + "-> training model" + bcolors.ENDC)
    log.info(json.dumps(config["train"], indent=4, sort_keys=True))
    dd_response = dd_utils.dd_post_train(
        dd=dd,
        sname=sname,
        config=config["train"]
    )
    log.info(" - {}".format(dd_response))

    ####### Metrics logs
    time.sleep(10)

    read_dd = None
    if opt["use_ddboard"]:
        # Duplicate ddboard dump into the folder accessible to the TensorBoard
        if opt["logdir_ddboard"]:
            logdir_copy = os.path.join(opt["logdir_ddboard"], repository.split('/')[-1])
            os.makedirs(logdir_copy, exist_ok=True)

        logdir = os.path.join(repository, 'dd_board')
        os.makedirs(logdir, exist_ok=True)
        read_dd = DDBoard(logdir, repository.split('/')[-1])

    metrics = {}
    while True:
        train_log = dd_utils.dd_get_train(dd, sname)
        if train_log["head"]["status"] == "running":
            metrics = train_log["body"]
            train_stats = metrics["measure"]
            log.info(train_stats)
            if train_stats and opt["use_ddboard"]:
                read_dd.ddb_logger(train_stats)
                if opt["logdir_ddboard"]:
                    for log_ in os.listdir(read_dd.run_dir):
                        # Copy the file, catch and pass if it does not exit yet
                        try:
                            shutil.copy(os.path.join(read_dd.run_dir, log_), logdir_copy)
                        except:
                            pass
        else:
            log.info(train_log)
            break

    log.info(bcolors.OKGREEN + "-> training finished" + bcolors.ENDC)

    # Saving metrics
    path_metrics = os.path.join(repository, "train_metrics.json")
    log.info("-> saving training metrics:")
    log.info(" - {}".format(path_metrics))
    os_utils.json_save(path_metrics, metrics)

    log.info(bcolors.OKGREEN + "-> model saved to:" + bcolors.ENDC)
    log.info(bcolors.OKGREEN + " - {}".format(repository) + bcolors.ENDC)

    log.info("-> deleting service from DeepDetect")
    dd_response = dd_utils.dd_delete_service(
        dd=dd,
        sname=sname
    )
    log.info(" - {}".format(dd_response))

def main():
    opt = vars(get_opt())
    train(opt)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("Uncaught error running DeepDetect train script")
        print(e)
        raise
