#!/usr/bin/env python

# Copyright (c) 2017 Orange and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

# pylint: disable=missing-docstring

import unittest


class SdncTestingBase(unittest.TestCase):
    pass

# {"input": {"sdnc-request-header":
# {"svc-notification-url":
# "http:\\/\\/onap.org:8080\\/adapters\\/rest\\/SDNCNotify",
# "svc-request-id": "test", "svc-action": "reserve"},
# "request-information":
# {"request-action": "PreloadVNFRequest", "order-version": "1",
# "notification-url": "onap.org", "order-number": "1", "request-id": "test"},
# "vnf-topology-information": {"vnf-assignments": {"vnf-vms": [],
# "availability-zones": [], "vnf-networks": []},
# "vnf-parameters":
# [{"vnf-parameter-name": "netconf_user_1",
# "vnf-parameter-value": "netconfuser1"},
# {"vnf-parameter-name": "netconf_password_1",
# "vnf-parameter-value": "ncuser1Pass"},
# {"vnf-parameter-name": "netconf_ssh_public_key_1",
# "vnf-parameter-value": "vmrf_key_pair"}],
# "vnf-topology-identifier":
# {"service-type": "a674f0ce-3f7e-4f75-96f7-39830e9a1b61",
# "generic-vnf-type": "vMRFaaS3/vMRF3 0",
# "vnf-name": "be1e0d5e-4c89-4467-b2ef-c1c3f8a5b136",
# "generic-vnf-name": "vMRFaaS3-service-instance-0DP8AF",
# "vnf-type": "vmrf30..Vmrf3..base_swms..module-0"}}}}
#
# SDNC url: /restconf/operations/VNF-API:preload-vnf-topology-operation
#
# {"output":{"svc-request-id":"test",
# "response-code":"200","ack-final-indicator":"Y"}}
