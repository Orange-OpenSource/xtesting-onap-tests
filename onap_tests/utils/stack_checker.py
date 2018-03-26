#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
#  pylint: disable=missing-docstring
import logging
import os
import time

from keystoneauth1 import loading
from keystoneauth1 import session
from heatclient import client

import onap_tests.utils.utils as onap_test_utils


class StackChecker(object):
    """
        Class used to check is the Stack does exist in openstack
        And if the status is complete
    """

    LOG_LEVEL = onap_test_utils.get_config("general.log.log_level")

    logging.basicConfig()
    __logger = logging.getLogger(__name__)
    logging.getLogger().setLevel(LOG_LEVEL)

    def __init__(self, **kwargs):
        """Initialize MRF object."""
        super(StackChecker, self).__init__()

        # get param from env variables
        auth_url = self.get("OS_AUTH_URL")
        username = self.get("OS_USERNAME")
        password = self.get("OS_PASSWORD")
        project_id = self.get("OS_PROJECT_ID")
        project_name = self.get("OS_PROJECT_NAME")
        user_domain_name = self.get("OS_USER_DOMAIN_NAME")
        loader = loading.get_plugin_loader('password')
        try:
            auth = loader.load_from_options(auth_url=auth_url,
                                            username=username,
                                            password=password,
                                            project_id=project_id,
                                            project_name=project_name,
                                            user_domain_name=user_domain_name)
            sess = session.Session(auth=auth)
            self.heat = client.Client('1', session=sess)
        except Exception:  # pylint: disable=broad-except
            self.__logger.error("Env variables not found, impossible to get"
                                " keystone client")
        try:
            self.stack_name = kwargs["stack_name"]
        except KeyError:
            self.__logger.info("No stack name provided at inititialization")

    @staticmethod
    def get(env_var):
        """
        Get env variable
        """
        return os.environ.get(env_var)

    def check_stack_exists(self, stack_name):
        """
        Check if the stack exists in openstack
        """
        stack_found = False
        nb_try = 0
        nb_try_max = 5

        while stack_found is False and nb_try < nb_try_max:
            stack_list = list(self.heat.stacks.list())
            if stack_name in str(stack_list):
                self.__logger.info("Stack found")
                return True
            nb_try += 1
            time.sleep(10)
        return stack_found

    def check_stack_is_complete(self, stack_name):
        """
        Check the status of a stack
        """
        # we assume that the stack does exist
        stack_status_complete = False
        nb_try = 0
        nb_try_max = 5
        while stack_status_complete is False and nb_try < nb_try_max:
            stack_list = list(self.heat.stacks.list())
            for stack in enumerate(stack_list):
                if stack_name in str(stack_list):
                    found_stack = stack[1]
                    if "COMPLETE" in found_stack.status:
                        return True
            nb_try += 1
            time.sleep(10)
        return stack_status_complete
