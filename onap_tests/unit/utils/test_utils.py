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

import onap_tests.utils.utils as onap_test_utils

__author__ = "Morgan Richomme <morgan.richomme@orange.com>"


class UtilsTestingBase(unittest.TestCase):

    """The super class which testing classes could inherit."""

    logging.disable(logging.CRITICAL)

    _vfw_node1 = "vFWCL_vPKG-vf 0"
    _vfw_node2 = "vFWCL_vFWSNK-vf 0"
    _vfw_group1 = "vfwcl_vfwsnkvf0..VfwclVfwsnkVf..base_vfw..module-0"
    _vfw_group2 = "vfwcl_vpkgvf0..VfwclVpkgVf..base_vpkg..module-0"
    _vfw_list = [_vfw_node1, _vfw_node2]
    _vims_node = "Clearwater 0"
    _vims_group = "clearwater0..Clearwater..base_clearwater..module-0"
    _vims_list = [_vims_node]

    def setUp(self):
        pass

    def test_get_vf_module_index_fw(self):
        self.assertEqual(1, onap_test_utils.get_vf_module_index(
            self._vfw_list,
            self._vfw_group1))
        self.assertEqual(0, onap_test_utils.get_vf_module_index(
            self._vfw_list,
            self._vfw_group2))

    def test_get_vf_module_index_vims(self):
        self.assertEqual(0, onap_test_utils.get_vf_module_index(
            self._vims_list,
            self._vims_group))


if __name__ == "__main__":
    # logging must be disabled else it calls time.time()
    # what will break these unit tests.
    logging.disable(logging.CRITICAL)
    unittest.main(verbosity=2)
