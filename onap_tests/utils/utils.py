#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
#  pylint: disable=missing-docstring

from difflib import SequenceMatcher

import logging
import random
import string
import os
import requests
import yaml


# ----------------------------------------------------------
#
#               YAML UTILS
#
# -----------------------------------------------------------
def get_parameter_from_yaml(parameter, config_file):
    """
    Returns the value of a given parameter in file.yaml
    parameter must be given in string format with dots
    Example: general.openstack.image_name
    """
    with open(config_file) as my_file:
        file_yaml = yaml.safe_load(my_file)
    my_file.close()
    value = file_yaml

    # Ugly fix as workaround for the .. within the params in the yaml file
    ugly_param = parameter.replace("..", "##")
    for element in ugly_param.split("."):
        value = value.get(element.replace("##", ".."))
        if value is None:
            raise ValueError("The parameter %s is not defined" % parameter)
    return value


def get_config(parameter):
    """
    Get configuration parameter from yaml configuration file
    """
    local_path = os.path.dirname(os.path.abspath(__file__))
    yaml_ = local_path.replace("utils", "onap-testing.yaml")
    return get_parameter_from_yaml(parameter, yaml_)


def get_template_param(vnf_type, parameter):
    """
    Get VNF template
    """
    local_path = os.path.dirname(os.path.abspath(__file__))
    if "ims" in vnf_type:
        template_path = "templates/service-ClearwaterVims-template.yml"
    elif "vfw" in vnf_type:
        template_path = "templates/service-VfwService-template.yml"
    else:
        template_path = "templates/service-VmrfService-template.yml"

    yaml_ = local_path.replace("utils",
                               template_path)
    return get_parameter_from_yaml(parameter, yaml_)


# ----------------------------------------------------------
#
#               LOGGER UTILS
#
# -----------------------------------------------------------
def get_logger(module):
    """
    Get Logger
    """
    log_formatter = logging.Formatter("%(asctime)s [" +
                                      module +
                                      "] [%(levelname)-5.5s]  %(message)s")
    logger = logging.getLogger()
    log_file = get_config('general.log.log_file')
    log_level = get_config('general.log.log_level')

    file_handler = logging.FileHandler("{0}/{1}".format('.', log_file))
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)
    logger.setLevel(log_level)
    return logger


# ----------------------------------------------------------
#
#               Misc
#
# -----------------------------------------------------------
def random_string_generator(size=6,
                            chars=string.ascii_uppercase + string.digits):
    """
    Get a random String for VNF
    """
    return ''.join(random.choice(chars) for _ in range(size))


def get_vf_module_index(vnf_list, target):
    # until we understand how to match vnf & vf from the service template
    best_index = 0
    best_index_proba = 0
    for i, elt in enumerate(vnf_list):
        current_proba = SequenceMatcher(None,
                                        target.lower(),
                                        elt.lower()).ratio()
        if current_proba > best_index_proba:
            best_index = i
            best_index_proba = current_proba
    return best_index


# ----------------------------------------------------------
#
#               requests
#
# -----------------------------------------------------------
def get_simple_request(url, headers, proxy):
    try:
        response = requests.get(url, headers=headers,
                                proxies=proxy, verify=False)
        request_info = response.json()
    except Exception:  # pylint: disable=broad-except
        request_info = response.text
    return request_info
