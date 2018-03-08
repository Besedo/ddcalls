# -*- coding: utf-8 -*-
"""
@author: Evgeny BAZAROV <baz.evgenii@gmail.com>
@brief:
"""

import re

def format_sname(sname):
    # DD lowercasing service names
    new_sname = sname.lower()

    pattern = "[!@#$]"
    if re.search(pattern, new_sname):
        print("sname (service name): {} contains unsupported patterns ({})".format(sname, pattern))
        # Remove special characters that can affect
        new_sname = re.sub(pattern, "_", sname)
        print("sname old >> new: {} >> {}".format(sname, new_sname))

    return new_sname


def dict_remove_empty(d):
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (dict_remove_empty(v) for v in d) if v is not None]
    return {k: v for k, v in ((k, dict_remove_empty(v)) for k, v in d.items()) if v is not None}


def update_config(config, new_params, stage="train"):
    # sname
    if new_params.get("sname"):
        config["service"]["sname"] = new_params["sname"]
    # repository
    if new_params.get("repository"):
        config["service"]["model"]["repository"] = new_params["repository"]
    # templates
    if new_params.get("templates"):
        config["service"]["model"]["templates"] = new_params["templates"]
    # gpu
    if new_params.get("gpu"):
        config["service"]["parameters"]["mllib"]["gpu"] = new_params["gpu"]
        if config.get("train"):
            config["train"]["parameters"]["mllib"]["gpu"] = new_params["gpu"]
        if config.get("predict"):
            config["predict"]["parameters"]["mllib"]["gpu"] = new_params["gpu"]
    # gpuid
    if new_params.get("gpuid") is not None:
        config["service"]["parameters"]["mllib"]["gpuid"] = new_params["gpuid"]
        if config.get("train"):
            config["train"]["parameters"]["mllib"]["gpuid"] = new_params["gpuid"]
        if config.get("predict"):
            config["predict"]["parameters"]["mllib"]["gpuid"] = new_params["gpuid"]
    # data
    if stage == "train" and config.get("train"):
        if new_params.get("data"):
            config["train"]["data"] = [d.strip() for d in new_params["data"].split(",")]
    elif stage == "predict" and config.get("predict"):
        if new_params.get("data"):
            config["predict"]["data"] = [d.strip() for d in new_params["data"].split(",")]
    # class weights should be float DD has a problem to parse int to float
    try:
        cw = config["train"]["parameters"]["mllib"]["class_weights"]
        cw = [float(w) for w in cw]
        config["train"]["parameters"]["mllib"]["class_weights"] = cw
    except KeyError:
        pass
    return config
