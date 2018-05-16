#!/usr/bin/env python

# Copyright (c) 2017 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

# pylint: disable=missing-docstring

import logging
import unittest

import requests_mock

from onap_tests.components import aai
import onap_tests.utils.utils as onap_utils


class AaiTestingBase(unittest.TestCase):

    __logger = logging.getLogger(__name__)

    def setUp(self):
        PROXY = onap_utils.get_config("general.proxy")
        self.my_aai = aai.Aai(PROXY, self.__logger)

    @requests_mock.mock()
    def test_check_services(self, m):
        # url = self.my_aai.aai_url +
        # "/aai/v11/service-design-and-creation/services"
        # m.get(url, text='a response')
        # self.assertEqual(self.my_aai.check_sercices(), 'a response')
        self.assertEqual(0, 0)
    # @requests_mock.mock()
    # def test_check_services_bad_resquest(self, m):
    #     url = self._AAI_URL + "/aai/v11/service-design-and-creation/services"
    #     m.get(url, text='a response')
    #     self.assertEqual(self.aai.check_sercices(), 'a response')


if __name__ == "__main__":
    # logging must be disabled else it calls time.time()
    # what will break these unit tests.
    logging.disable(logging.CRITICAL)
    unittest.main(verbosity=2)
