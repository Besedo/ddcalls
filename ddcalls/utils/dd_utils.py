# -*- coding: utf-8 -*-
"""
@author: Evgeny BAZAROV <baz.evgenii@gmail.com>
@brief:
"""

def dd_put_service(dd, config, for_predict=False):
    if for_predict:
        # removing template for prediction because network weights exist
        config["parameters"]["mllib"].pop("template", None)

    dd_response = dd.put_service(
        sname=config["sname"],
        model=config["model"],
        description=config["description"],
        mllib=config["mllib"],
        parameters_input=config["parameters"]["input"],
        parameters_mllib=config["parameters"]["mllib"],
        parameters_output=config["parameters"]["output"],
        mltype=config["type"]
    )
    assert dd_response['status']['code'] == 201 and dd_response['status']['msg'] == "Created", dd_response
    return dd_response

def dd_post_train(dd, sname, config):
    dd_response = dd.post_train(
        sname=sname,
        data=config["data"],
        parameters_input=config["parameters"]["input"],
        parameters_mllib=config["parameters"]["mllib"],
        parameters_output=config["parameters"]["output"],
        async=config["async"]
    )
    assert dd_response['status']['code'] == 201 and dd_response['status']['msg'] == "Created", dd_response
    return dd_response

def dd_post_predict(dd, sname, data, config):
    dd_response = dd.post_predict(
        sname=sname,
        data=data,
        parameters_input=config["parameters"]["input"],
        parameters_mllib=config["parameters"]["mllib"],
        parameters_output=config["parameters"]["output"]
    )
    return dd_response

def dd_sname_exist(dd, sname):
    # Check if service name exist
    for service in dd.info()['head']['services']:
        if service['name'] == sname:
            return True
    return False

def dd_delete_service(dd, sname):
    dd_response = dd.delete_service(
        sname=sname,
        clear="mem"
    )
    return dd_response

def dd_get_train(dd, sname):
    dd_response = dd.get_train(
        sname=sname,
        job=1,
        timeout=2,
        measure_hist=True
    )
    return dd_response

