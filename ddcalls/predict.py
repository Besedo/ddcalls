# -*- coding: utf-8 -*-
"""
@author: Evgeny BAZAROV <baz.evgenii@gmail.com>
@brief:
"""

import os
import sys
import json
import argparse
from itertools import islice
from datetime import datetime

from ddcalls.utils import os_utils
from ddcalls.utils import dd_utils
from ddcalls.utils import config_utils
from ddcalls.utils.dd_client import DD
from ddcalls.utils.os_utils import bcolors
from ddcalls.utils.logging_utils import get_logger, str2bool


def get_opt():
    parser = argparse.ArgumentParser("""DeepDetect prediction script""")
    parser.add_argument("--path_dd_config", type=str)
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=8080)
    # Options that will overwrite config parameters
    parser.add_argument("--sname", type=str, default=None)
    parser.add_argument("--data", type=str, default=None)
    parser.add_argument("--repository", type=str, default=None)
    parser.add_argument("--gpu", type=str2bool, default=None)
    parser.add_argument("--gpuid", type=int, default=None)
    parser.add_argument("--templates", type=str, default=None)

    opt = parser.parse_args()
    return opt


def predict(opt=None):

    # script execution timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # loading config file
    config = os_utils.json_load(opt["path_dd_config"])

    # overwrite parameters if needed
    config = config_utils.update_config(
        stage="predict",
        config=config,
        new_params=opt
    )

    # repository path check
    repository = config["service"]["model"]["repository"]
    assert os.path.isdir(repository), "Wrong path to repository: {}".format(repository)

    # logger for logs
    log = get_logger(repository, "{}_predict.log".format(timestamp))

    log.info(bcolors.HEADER + "running PREDICTION script" + bcolors.ENDC)
    log.info("-> checking paths to prediction data")
    for path_data in config["predict"]["data"]:
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
        for_predict=True
    )
    log.info(" - {}".format(dd_response))

    ####### Prediction
    log.info(bcolors.HEADER + "-> model predictions" + bcolors.ENDC)
    log.info(json.dumps(config["predict"], indent=4, sort_keys=True))
    path_preds = os.path.join(repository, "predictions")
    os.makedirs(path_preds, exist_ok=True)

    for data in config["predict"]["data"]:
        log.info(bcolors.OKGREEN + "-> prediction for: {}".format(data) + bcolors.ENDC)
        if data.endswith(".svm") or data.endswith(".csv"):
            # note csv file should be one line here with header
            dd_preds = []
            batch_size = config["predict"]["parameters"]["mllib"]["net"]["test_batch_size"]
            with open(data, encoding="utf-8") as f:
                if data.endswith(".csv"):
                    # skip header fo csv file
                    next(f)
                while True:
                    batch = list(islice(f, batch_size))
                    if not batch:
                        break
                    batch = [line.strip() for line in batch]
                    dd_response = dd_utils.dd_post_predict(
                        dd=dd,
                        sname=sname,
                        data=batch,
                        config=config["predict"]
                    )
                    dd_preds.append(dd_response)
        else:
            dd_response = dd_utils.dd_post_predict(
                dd=dd,
                sname=sname,
                data=[data],
                config=config["predict"]
            )
            dd_preds = [dd_response]
        path_pred = os.path.join(path_preds, "{}.json".format(os.path.basename(data).split(".")[0]))
        log.info("-> saving predictions to:")
        log.info(" - {}".format(path_pred))
        os_utils.json_save(path_pred, dd_preds, sort=False)

    log.info(bcolors.OKGREEN + "-> prediction finished" + bcolors.ENDC)

    log.info("-> deleting service from DeepDetect")
    dd_response = dd_utils.dd_delete_service(
        dd=dd,
        sname=sname
    )
    log.info(" - {}".format(dd_response))


def main():
    opt = vars(get_opt())
    predict(opt)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("Uncaught error running DeepDetect prediction script")
        print(e)
        raise
