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

from onap_tests.components import so
import onap_tests.utils.utils as onap_test_utils


class SoComponentTesting(unittest.TestCase):

    _LOGGER = onap_test_utils.getLogger("onap_tests")
    _PROXY = onap_test_utils.get_config("general.proxy")

    def setUp(self):
        self.my_so = so.So(proxy=self._PROXY, LOGGER=self._LOGGER)

    def test_get_request_info(self):
        pass

    def _test_get_cloud_config(self):
        pass

    def test_get_cloud_config(self):
        pass

    def test_get_subscriber_info(self):
        pass

    def test_get_request_param(self):
        pass

    def test_get_service_model_info(self):
        pass

    def test_get_vnf_model_info(self):
        pass

    def test_get_vnf_related_instance(self):
        pass

    def test_get_module_model_info(self):
        pass

    def test_get_module_related_instance(self):
        pass

    def test_get_service_payload(self):
        pass

    def test_get_vnf_payload(self):
        pass

    def test_get_module_payload(self):
        pass

    def test_create_instance(self):
        pass

    def test_create_vnf(self):
        pass

    def test_create_module(self):
        pass

    def test_delete_instance(self):
        pass

    def test_delete_vnf(self):
        pass

    def test_delete_module(self):
        pass

if __name__ == "__main__":
    # logging must be disabled else it calls time.time()
    # what will break these unit tests.
    logging.disable(logging.CRITICAL)
    unittest.main(verbosity=2)
    # Create Instance
    # http://10.4.2.15:8080
    # "POST /ecomp/mso/infra/serviceInstances/v4 HTTP/1.1" 202 126
    # {"requestReferences":
    # {"instanceId":"d86832f7-d5e2-41ec-ac90-ba78ffddf764",
    #  "requestId":"cd6505ba-d7cb-4b9b-bfd5-349e956173c5"}}
    #
    # Create VNF
    #  http://10.4.2.15:8080
    # "POST /ecomp/mso/infra/serviceInstances/v4/
    # d86832f7-d5e2-41ec-ac90-ba78ffddf764/vnfs HTTP/1.1" 202 126
    # 2018-01-25 16:13:51,112 [onap_tests] [DEBUG]
    # SO response {"requestReferences":
    # {"instanceId":"1522e0a1-203b-4631-9778-67ddfe325a36",
    # "requestId":"e5ffb17f-5602-4b0e-a72e-71cb652aafd6"}}
    #
    # ----------------------------
    #
    # Delete Instance
    # SO request: http://10.4.2.15:8080/
    # ecomp/mso/infra/serviceInstances/v4/d86832f7-d5e2-41ec-ac90-ba78ffddf764
    # http://10.4.2.15:8080
    # "DELETE /ecomp/mso/infra/serviceInstances/v4/
    # d86832f7-d5e2-41ec-ac90-ba78ffddf764 HTTP/1.1" 202 126
    #
    # Delete vnf 1522e0a1-203b-4631-9778-67ddfe325a36
    # SO request: http://10.4.2.15:8080/ecomp/mso/infra/serviceInstances/v4/
    # d86832f7-d5e2-41ec-ac90-ba78ffddf764/vnfs/
    # 1522e0a1-203b-4631-9778-67ddfe325a36
    # http://10.4.2.15:8080
    # "DELETE /ecomp/mso/infra/serviceInstances/v4/
    # d86832f7-d5e2-41ec-ac90-ba78ffddf764/vnfs/
    # 1522e0a1-203b-4631-9778-67ddfe325a36 HTTP/1.1" 202 126
