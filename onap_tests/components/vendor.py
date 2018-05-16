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
import json
import requests

import onap_tests.utils.utils as onap_utils

PROXY = onap_utils.get_config("general.proxy")
SDC_URL = onap_utils.get_config("onap.sdc.url")
SDC_HEADERS = onap_utils.get_config("onap.sdc.headers")


class Vendor(object):
    """
        ONAP Vendor Object
        Used for SDC operations
    """
    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        # pylint: disable=invalid-name
        self.id = ""
        if "name" in kwargs:
            self.name = kwargs['name']
        else:
            self.name = "Generic-Vendor"
        self.version = ""
        self.status = ""

    def get_info(self):
        """
            Get vendor Object when vendor name set at Object instantiation
        """
        return self.get_vendor_info_from_sdc(self.name)

    def update_vendor(self, **kwargs):
        """
            Update vendor values
        """
        if "id" in kwargs:
            self.id = kwargs['id']
        if "name" in kwargs:
            self.name = kwargs['name']
        if "version" in kwargs:
            self.version = kwargs['version']
        if "status" in kwargs:
            self.status = kwargs['status']

# ---------------------------------------------------------------------------
    def get_sdc_vendor_payload(self, **kwargs):
        """
            Build SDC vendor payload
        """
        try:
            payload = {}
            if kwargs['action'] == "create":
                # create SDC vendor payload for POST
                payload = onap_utils.get_config(
                    "vlm_payload.vlm_create_data")
                if "vendor_name" in kwargs:
                    payload['vendorName'] = kwargs['vendor_name']
                else:
                    payload['vendorName'] = "Generic-Vendor"
            else:
                # by Default if method not set, it is assumed it is a PUT
                # create SDC vendor payload for PUT
                if kwargs['action'] == "Checkin":
                    payload = onap_utils.get_config(
                        "vlm_payload.vlm_checkin_data")
                else:
                    payload = onap_utils.get_config(
                        "vlm_payload.vlm_submit_data")
        except KeyError:
            self.__logger.error("No payload set")
        return json.dumps(payload)

# ---------------------------------------------------------------------------
    def get_vendor_list(self):
        """
            Get SDC vendor list
        """
        # now it is time to request data to ONAP SDC
        url = SDC_URL + onap_utils.get_config(
            "onap.sdc.list_vlm_url")
        vendor_list = {}
        try:
            response = requests.get(url, headers=SDC_HEADERS,
                                    proxies=PROXY, verify=False)
            vendor_list = response.json()
        except Exception as err:  # pylint: disable=broad-except
            self.__logger.error("Impossible to get SDC vendor list: %s", err)
        return vendor_list

    def check_vendor_exists(self, vendor_name):
        """
            Check if provided vendor exists in SDC vendor list
        """
        vendor_list = self.get_vendor_list()

        vendor_found = False

        for result in vendor_list['results']:
            if result['vendorName'] == vendor_name:
                vendor_found = True
                self.update_vendor(status=result['status'],
                                   id=result['id'],
                                   version=result['version'])
                break
        return vendor_found

    def create_vendor(self, vendor_name="Generic-Vendor"):
        """
            Create vendor in SDC (only if he/she does not exist)
        """
        # we check if vendor exists or not, if not we create it
        create_vendor = False
        if not self.check_vendor_exists(vendor_name):
            try:
                url = SDC_URL + onap_utils.get_config(
                    "onap.sdc.create_vlm_url")
                response = requests.post(url, headers=SDC_HEADERS,
                                         proxies=PROXY, verify=False,
                                         data=self.get_sdc_vendor_payload(
                                             action="create",
                                             vendor_name=vendor_name))
                if response.status_code == 200:
                    create_vendor = True
            except Exception as err:  # pylint: disable=broad-except
                self.__logger.error("Impossible to create SDC vendor: %s", err)
        return create_vendor

    def get_vendor_info_from_sdc(self, vendor_name):
        """
            Get vendor detail
        """
        vendor_list = self.get_vendor_list()

        for result in vendor_list['results']:
            if result['vendorName'] == vendor_name:
                return result
        return None

    def checkin_vendor(self):
        """
            Checkin SDC Vendor
        """
        checkin_vendor = False
        old_str = onap_utils.get_config("onap.sdc.checkin_vlm_url")
        new_str = old_str.replace("{{vlm_id}}", self.id)
        old_str = new_str
        new_str = old_str.replace("{{vlm_version}}", self.version['id'])
        url = SDC_URL + new_str
        try:
            response = requests.put(url,
                                    headers=SDC_HEADERS,
                                    proxies=PROXY,
                                    verify=False,
                                    data=self.get_sdc_vendor_payload(
                                        action="Checkin"))
            if response.status_code == 200:
                checkin_vendor = True
        except Exception as err:  # pylint: disable=broad-except
            self.__logger.error("Was not possible to perform checkin\
                SDC vendor: %s", err)
        return checkin_vendor

    def submit_vendor(self):
        """
            Submit SDC Vendor
        """
        submit_vendor = False
        old_str = onap_utils.get_config("onap.sdc.submit_vlm_url")
        new_str = old_str.replace("{{vlm_id}}", self.id)
        old_str = new_str
        new_str = old_str.replace("{{vlm_version}}", self.version['id'])
        url = SDC_URL + new_str
        try:
            response = requests.put(url,
                                    headers=SDC_HEADERS,
                                    proxies=PROXY, verify=False,
                                    data=self.get_sdc_vendor_payload(
                                        action="Submit"))
            if response.status_code == 200:
                submit_vendor = True
        except Exception as err:  # pylint: disable=broad-except
            self.__logger.error("Impossible to perform SDC vendor submit: %s",
                                err)
        return submit_vendor
