#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
"""
   ONAP AA&I main operations
"""
import time
import requests

import onap_tests.utils.utils as onap_test_utils


class Aai(object):
    """
        ONAP AA&I main operations
    """

    def __init__(self, proxy, LOGGER):
        # Logger
        # pylint: disable=no-member
        requests.packages.urllib3.disable_warnings()
        self.aai_url = onap_test_utils.get_config("onap.aai.url")
        self.aai_headers = onap_test_utils.get_config("onap.aai.headers")
        self.proxy = proxy
        self.logger = LOGGER

    def check_service_instance(self, service_description, service_instance_id):
        """
        Check that a given service instance is created
        send request, wait, check
        max nb_try_max times
        """
        url = (self.aai_url + "/aai/v11/business/customers/customer/" +
               onap_test_utils.get_config("onap.customer") +
               "/service-subscriptions/service-subscription/" +
               service_description + "/service-instances/")
        try:
            service_instance_found = False
            nb_try = 0
            nb_try_max = 5
            while service_instance_found is False and nb_try < nb_try_max:
                response = requests.get(url, headers=self.aai_headers,
                                        proxies=self.proxy, verify=False)
                self.logger.info("AAI: looking for %s service instance....",
                                 service_instance_id)
                if service_instance_id in response.text:
                    self.logger.info("Service instance %s found in AAI",
                                     service_instance_id)
                    service_instance_found = True
                time.sleep(10)
                nb_try += 1
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error("impossible to perform the request on AAI: %s",
                              str(err))
        if service_instance_found is False:
            self.logger.info("Service instance not found")
        return service_instance_found

    def check_service_instance_cleaned(self, service_description,
                                       service_instance_id):
        """
        Check if the Service instance has been  cleaned in the AAI
        return True if it has been clean_preload
        return False elsewhere
        """
        # url2 = self.aai_url + "/aai/v11/service-design-and-creation/services"
        # url1 = self.aai_url + "/aai/v11/business/customers"
        url = (self.aai_url + "/aai/v11/business/customers/customer/" +
               onap_test_utils.get_config("onap.customer") +
               "/service-subscriptions/service-subscription/" +
               service_description + "/service-instances/")
        try:
            service_instance_found = True
            nb_try = 0
            nb_try_max = 5
            while service_instance_found is True and nb_try < nb_try_max:
                response = requests.get(url, headers=self.aai_headers,
                                        proxies=self.proxy, verify=False)
                self.logger.info("AAI: Has %s service instance been cleaned..",
                                 service_instance_id)
                if service_instance_id not in response.text:
                    self.logger.info("Service instance %s cleaned in AAI",
                                     service_instance_id)
                    service_instance_found = False
                time.sleep(10)
                nb_try += 1
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error("impossible to perform the request on AAI: %s",
                              str(err))
        if service_instance_found is True:
            self.logger.info("Service instance not cleaned")
        return not service_instance_found

    def check_vnf_instance(self, vnf_id):
        """
            Check the VNF declared in the AA&I
        """
        url = (self.aai_url + "/aai/v11/network/generic-vnfs")
        try:
            vnf_instance_found = False
            nb_try = 0
            nb_try_max = 5
            while vnf_instance_found is False and nb_try < nb_try_max:
                response = requests.get(url, headers=self.aai_headers,
                                        proxies=self.proxy, verify=False)
                self.logger.info("AAI: looking for %s vnf instance....",
                                 vnf_id)
                if vnf_id in response.text:
                    self.logger.info("Vnf instance %s found in AAI",
                                     vnf_id)
                    vnf_instance_found = True
                time.sleep(10)
                nb_try += 1
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error("impossible to perform the request on AAI: %s",
                              str(err))
        if vnf_instance_found is False:
            self.logger.info("VNF instance not found")
        return vnf_instance_found

    def check_vnf_instances(self, vnf_ids):
        """
            Check the VNF(s) declared in the AA&I
        """
        url = (self.aai_url + "/aai/v11/network/generic-vnfs")
        # if case of several VNFs, answer False if one is not found
        nb_vnf_found = 0
        for elt in vnf_ids:
            try:
                self.logger.info("AAI: looking for %s vnf instance....", elt)
                vnf_id = vnf_ids[elt]["id"]
                nb_try = 0
                nb_try_max = 5
                vnf_instance_found = False
                while vnf_instance_found is False and nb_try < nb_try_max:
                    response = requests.get(url, headers=self.aai_headers,
                                            proxies=self.proxy, verify=False)
                    if vnf_id in response.text:
                        self.logger.info("Vnf instance %s found in AAI",
                                         vnf_id)
                        nb_vnf_found += 1
                        vnf_instance_found = True
                    time.sleep(10)
                    nb_try += 1
            except Exception as err:  # pylint: disable=broad-except
                self.logger.error("impossible to perform the AAI request: %s",
                                  str(err))
            if nb_vnf_found == len(vnf_ids):
                self.logger.info("VNF instance not found")
                vnf_instance_found = True
            else:
                vnf_instance_found = False
                self.logger.error("%s VNF found (%s expected)",
                                  (nb_vnf_found, len(vnf_ids)))
        return vnf_instance_found

    def check_vnf_cleaned(self, vnf_id):
        """
            Check the VNF declared in the AA&I
        """
        url = self.aai_url + "/aai/v11/network/generic-vnfs"
        try:
            vnf_instance_found = True
            nb_try = 0
            nb_try_max = 5
            while vnf_instance_found is True and nb_try < nb_try_max:
                response = requests.get(url, headers=self.aai_headers,
                                        proxies=self.proxy, verify=False)
                self.logger.info("AAI: check if vnf %s instance been cleaned.",
                                 vnf_id)
                if vnf_id not in response.text:
                    self.logger.info("Vnf instance %s cleaned in AAI",
                                     vnf_id)
                    vnf_instance_found = False
                time.sleep(10)
                nb_try += 1
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error("impossible to perform the request on AAI: %s",
                              str(err))
        if vnf_instance_found is True:
            self.logger.info("VNF still in AAI, instance not cleaned")
        return not vnf_instance_found

    def check_module_instance(self, vnf_id, module_id):
        """
            Check the VNF declared in the AA&I
        """
        url = (self.aai_url + "/aai/v11/network/generic-vnfs/generic-vnf/" +
               vnf_id + "/vf-modules")
        try:
            module_instance_found = False
            nb_try = 0
            nb_try_max = 10
            while module_instance_found is False and nb_try < nb_try_max:
                response = requests.get(url, headers=self.aai_headers,
                                        proxies=self.proxy, verify=False)
                self.logger.info("AAI: looking for %s module instance....",
                                 module_id)
                if module_id in response.text:
                    self.logger.info("Module instance %s found in AAI",
                                     module_id)
                    module_instance_found = True
                time.sleep(10)
                nb_try += 1
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error("impossible to perform the request on AAI: %s",
                              str(err))
        if module_instance_found is False:
            self.logger.info("VFModule instance not found")
        return module_instance_found

    def check_module_cleaned(self, vnf_id, module_id):
        """
            Check that the VfModule declared in the AA&I has been cleaned
            return True if it has been cleaned
            return False is not
        """
        url = (self.aai_url + "/aai/v11/network/generic-vnfs/generic-vnf/" +
               vnf_id + "/vf-modules")
        try:
            module_instance_found = True
            nb_try = 0
            nb_try_max = 10
            while module_instance_found is True and nb_try < nb_try_max:
                response = requests.get(url, headers=self.aai_headers,
                                        proxies=self.proxy, verify=False)
                self.logger.info("AAI: Check if module  %s has been cleaned",
                                 module_id)
                if module_id not in response.text:
                    self.logger.info("Module instance %s cleaned in AAI",
                                     module_id)
                    module_instance_found = False
                time.sleep(15)
                nb_try += 1
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error("impossible to perform the request on AAI: %s",
                              str(err))
        if module_instance_found is True:
            self.logger.info("VFModule still in AAI, instance not cleaned")
        return not module_instance_found
