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

import onap_tests.components.vendor as vendor
import onap_tests.utils.utils as onap_utils

PROXY = onap_utils.get_config("general.proxy")


class Onboard(object):
    """
    Onboard classe to perform SDC operations
      * create/checkin/submit vendor
    """
    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        "Initialize Onboard object."
        super(Onboard, self).__init__()
        self.vendor = vendor.Vendor(**kwargs)

    def onboard(self):
        # onboard vendor
        # 1) vendor cration
        if self.vendor.check_vendor_exists(self.vendor.name):
            self.__logger.info("%s vendor already exists: skip creation",
                               self.vendor.name)
        else:
            self.__logger.info("Create vendor")

        # 2) Checkin
        if self.vendor.status == "Final" or self.vendor.status == "Available":
            self.__logger.info("State is Final or Available, skip checkin")
        else:
            self.__logger.info("Vendor status: %s: vendor checkin",
                               self.vendor.status)
            self.vendor.checkin_vendor()

        # 2) Submit
        if self.vendor.status == "Final":
            self.__logger.info("State is Final, skip submit")
        else:
            self.__logger.info("vendor submit")
            self.vendor.submit_vendor()

    def get_info(self):
        """
        Return information on SDC Objects
        """
        return {'vendor': self.vendor.get_info()}
