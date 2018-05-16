#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
"""
   ONAP NBI main operations
"""
import datetime
import json
import requests
import time

import onap_tests.utils.utils as onap_test_utils


class Nbi(object):
    """
        ONAP NBI main operations
    """

    def __init__(self, proxy, LOGGER):
        # Logger
        # pylint: disable=no-member
        requests.packages.urllib3.disable_warnings()
        self.nbi_url = onap_test_utils.get_config("onap.nbi.url")
        self.nbi_headers = onap_test_utils.get_config("onap.nbi.headers")
        self.proxy = proxy
        self.logger = LOGGER
        self.name = ""
        self.customer = "generic"
        self.external_id = ""
        self.service_id = ""


    def get_request_info(self):
        """
            Get NBI Request Info
        """
        return {
            "instanceName": self.name,
            "source": "NBI",
            "suppressRollback": False,
            "productFamilyId": self.name,
            "requestorId": "NBI"
        }

    def get_nbi_service_order_payload(self):
        """
            Get SO Service paylod
        """
        format_iso_now = datetime.datetime.now().isoformat()[:-3] + "Z"
        return json.dumps({
            "externalId": self.external_id,
            "priority": "1",
            "description": "Service Order",
            "category": "Consumer",
            "requestedStartDate": format_iso_now,
            "requestedCompletionDate": format_iso_now,
            "relatedParty": [{
                "id": self.customer,
                "role": "ONAPcustomer",
                "name": self.customer,
                "@referredType": "individual"}],
            "orderItem": [{
                "id": "1",
                "action": "add",
                "service": {
                    "name": self.name,
                    "serviceState": "active",
                    "serviceSpecification": {
                        "id": self.service_id}}}]
        })

    def get_service_instance_id_from_order(self, service_order_id):
        """
            Get NBI Service Catalog
        """
        try:
            url = self.nbi_url + "/serviceOrder/" + service_order_id
            self.logger.debug("NBI request: %s", url)
            service_instance_found = False
            instance_id = None
            nb_try = 0
            nb_try_max = 5
            while service_instance_found is False and nb_try < nb_try_max:
                response = onap_test_utils.get_simple_request(
                    url, self.nbi_headers, self.proxy)
                self.logger.info("NBI: looking for service instance id....")
                if response["state"] == "COMPLETED":
                    self.logger.info("NBI request COMPLETED")
                    service_instance_found = True
                    instance_id = response["orderItem"][0]["service"]["id"]
                    self.logger.info("Instance ID found %s", instance_id)
                time.sleep(10)
                nb_try += 1
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error("impossible to perform the request on NBI: %s",
                              str(err))
        if service_instance_found is False:
            self.logger.info("Service instance not found")
        return instance_id


    def create_service_order_nbi(self, nbi_service_payload):
        """
            NBI create servbice order
        """
        url = self.nbi_url + "/serviceOrder"
        self.logger.debug("NBI request: %s", url)
        try:
            response = requests.post(url, headers=self.nbi_headers,
                                     proxies=self.proxy, verify=False,
                                     data=nbi_service_payload)
            self.logger.info("NBI create service order request: %s",
                             response.text)
            instance_id = response.json()
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error("impossible to perform the request on NBI: %s",
                              str(err))
            instance_id = None
        return instance_id

    def get_nbi_service_order(self, **kwargs):
        """
            Get NBI Service order
            If an order_id is precised as kwargs, retrieve only related info
        """
        url = self.nbi_url + "/serviceOrder"
        if "order_id" in kwargs:
            url += "/" + kwargs["order_id"]
        self.logger.debug("NBI request: %s", url)
        return onap_test_utils.get_simple_request(url,
                                                  self.nbi_headers,
                                                  self.proxy)

    def get_nbi_service_catalog(self):
        """
            Get NBI Service Catalog
        """
        url = self.nbi_url + "/serviceSpecification"
        self.logger.debug("NBI request: %s", url)
        return onap_test_utils.get_simple_request(url,
                                                  self.nbi_headers,
                                                  self.proxy)

    def get_nbi_service_inventory(self):
        """
            Get NBI service inventory
        """
        url = self.nbi_url + "/service"
        self.logger.debug("NBI request: %s", url)
        return onap_test_utils.get_simple_request(url,
                                                  self.nbi_headers,
                                                  self.proxy)
