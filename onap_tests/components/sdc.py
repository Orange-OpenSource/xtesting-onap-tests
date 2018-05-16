#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
#  pylint: disable=missing-docstring
import requests

import onap_tests.utils.utils as onap_test_utils


class Sdc(object):
    """
        ONAP SDC main operations
    """

    def __init__(self, proxy, LOGGER):
        # Logger
        # pylint: disable=no-member
        requests.packages.urllib3.disable_warnings()
        self.sdc_url = onap_test_utils.get_config("onap.sdc.url")
        self.sdc_headers = onap_test_utils.get_config("onap.sdc.headers")
        self.proxy = proxy
        self.logger = LOGGER

    def get_url(self):
        """
            Return SDC url
        """
        return "SDC class url" + self.sdc_url

    def get_info(self):
        pass
