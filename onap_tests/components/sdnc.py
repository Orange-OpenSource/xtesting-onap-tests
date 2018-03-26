#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
#  pylint: disable=missing-docstring
import json
import requests
import onap_tests.utils.utils as onap_test_utils


class Sdnc(object):
    """
        SDNC main operations
    """

    def __init__(self, proxy, LOGGER):
        # Logger
        # pylint: disable=no-member
        requests.packages.urllib3.disable_warnings()

        self.sdnc_url = onap_test_utils.get_config("onap.sdnc.url")
        self.sdnc_headers = onap_test_utils.get_config("onap.sdnc.headers")
        self.proxy = proxy
        self.logger = LOGGER

    def get_preload_list(self):
        """
            get Preload List
        """
        url = (self.sdnc_url +
               "/restconf/config/VNF-API:preload-vnfs")
        self.logger.debug("SDNC url: %s", url)
        try:
            response = requests.get(url, headers=self.sdnc_headers,
                                    proxies=self.proxy, verify=False)
            self.logger.info("SDNC response on get preload list: %s",
                             response.text)
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error("impossible to perform the request on SDNC: %s",
                              str(err))

    def get_preload_item(self, vnf_name, vnf_type, item):
        """
            get Preload item
        """
        url = (self.sdnc_url +
               "/restconf/config/VNF-API:preload-vnfs/vnf-preload-list/" +
               vnf_name + "/" + vnf_type)
        self.logger.debug("SDNC url: %s", url)
        try:
            response = requests.get(url, headers=self.sdnc_headers,
                                    proxies=self.proxy, verify=False)
            self.logger.info("SDNC response on get preload %s: %s",
                             (item, response.text))
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error("impossible to perform the request on SNDC: %s",
                              str(err))

    @staticmethod
    def get_preload_payload(vnf_parameters, vnf_topology_identifier):
        """
            Get preload payload
        """
        # pylint: disable=anomalous-backslash-in-string
        svc_notif = "http:\/\/onap.org:8080\/adapters\/rest\/SDNCNotify"
        return json.dumps({
            "input": {
                "request-information": {
                    "notification-url": "onap.org",
                    "order-number": "1",
                    "order-version": "1",
                    "request-action": "PreloadVNFRequest",
                    "request-id": "test"
                    },
                "sdnc-request-header": {
                    "svc-action": "reserve",
                    "svc-notification-url": svc_notif,
                    "svc-request-id": "test"
                    },
                "vnf-topology-information": {
                    "vnf-assignments": {
                        "availability-zones": [],
                        "vnf-networks": [],
                        "vnf-vms": []
                    },
                    "vnf-parameters": vnf_parameters,
                    "vnf-topology-identifier": vnf_topology_identifier
                }
            }})

    def preload(self, sdnc_preload_payload):
        """
            Preload VNF
        """
        preload_response = ""
        # preload_payload =
        url = (self.sdnc_url +
               "/restconf/operations/VNF-API:preload-vnf-topology-operation")
        self.logger.debug("SDNC url: %s", url)
        try:
            response = requests.post(url, headers=self.sdnc_headers,
                                     proxies=self.proxy, verify=False,
                                     data=sdnc_preload_payload)
            self.logger.info("SDNC response on get preload %s",
                             response.text)
            preload_response = response.text
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error("impossible to perform the request on SNDC: %s",
                              str(err))

        return preload_response

    def delete_preload(self, vnf_name, vnf_type):
        """
            Delete Preload
        """
        preload_response = ""
        url = (self.sdnc_url +
               "/restconf/config/VNF-API:preload-vnfs/vnf-preload-list/" +
               vnf_name + "/" + vnf_type)
        self.logger.debug("SDNC url: %s", url)
        try:
            response = requests.delete(url, headers=self.sdnc_headers,
                                       proxies=self.proxy, verify=False)
            self.logger.info("SDNC response on delete preload: %s",
                             response.text)
            preload_response = response.status_code
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error("impossible to perform the request on SNDC: %s",
                              str(err))
        return preload_response
