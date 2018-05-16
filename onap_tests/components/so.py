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


class So(object):
    """
        Service orchestrator (SO) main operations
    """

    def __init__(self, proxy, LOGGER):
        # Logger
        # pylint: disable=no-member
        requests.packages.urllib3.disable_warnings()

        self.so_url = onap_test_utils.get_config("onap.so.url")
        self.so_headers = onap_test_utils.get_config("onap.so.headers")
        self.proxy = proxy
        self.logger = LOGGER

    @classmethod
    def get_request_info(cls, instance_name):
        """
            Get Request Info
        """
        return {
            "instanceName": instance_name,
            "source": "VID",
            "suppressRollback": False,
            "productFamilyId": instance_name,
            "requestorId": "test"
        }

    @classmethod
    def get_cloud_config(cls):
        """
            Get Cloud configuration
        """
        tenant_id = onap_test_utils.get_config("openstack.tenant_id")
        return {
            "lcpCloudRegionId": "RegionOne",
            "tenantId": tenant_id
            }

    @classmethod
    def get_subscriber_info(cls):
        """
            Get Subscriber Info
        """
        subscriber_id = onap_test_utils.get_config("onap.customer")
        return {
            "globalSubscriberId": subscriber_id
        }

    @classmethod
    def get_request_param(cls, vnf, alacarte=False, subscription=False):
        """
            Get Request parameters
        """
        subscription_type = onap_test_utils.get_config(
            vnf + ".subscription_type")
        request_params = {
            "userParams": [],
            "cascadeDelete": True,
        }
        if subscription:
            request_params.update(
                {"subscriptionServiceType": subscription_type})

        if alacarte:
            request_params.update(
                {"aLaCarte": True})
        return request_params

    @classmethod
    def get_service_model_info(cls, invariant_uuid, uuid):
        """
            Return VNF model info
        """
        return {
            "modelType": "service",
            "modelName": "test-service",
            "modelInvariantId": invariant_uuid,
            "modelVersion": "1.0",
            "modelVersionId": uuid
        }

    @classmethod
    # pylint: disable=too-many-arguments
    def get_vnf_model_info(cls, vnf_invariant_id, vnf_version_id,
                           vnf_model_name, vnf_customization_id,
                           vnf_customization_name):
        """
            get VNF model info
        """
        return {
            "modelType": "vnf",
            "modelInvariantId": vnf_invariant_id,
            "modelVersionId": vnf_version_id,
            "modelName": vnf_model_name,
            "modelCustomizationId": vnf_customization_id,
            "modelCustomizationName": vnf_customization_name,
            "modelVersion": "1.0"
        }

    def get_vnf_related_instance(self, instance_id, invariant_uuid, uuid):
        """
            Get VNF related instance
            a VNF references:
            * an instance
        """
        return {
            "instanceId": instance_id,
            "modelInfo": self.get_service_model_info(invariant_uuid, uuid)
        }

    @classmethod
    #  pylint: disable=too-many-arguments
    def get_module_model_info(cls, module_invariant_id, module_name_version_id,
                              module_name, module_customization_id,
                              module_version_id):
        """
            get Module model info
        """
        return {
            "modelType": "vfModule",
            "modelInvariantId": module_invariant_id,
            "modelNameVersionId": module_name_version_id,
            "modelName": module_name,
            "modelVersion": "1.0",
            "modelCustomizationId": module_customization_id,
            "modelVersionId": module_version_id
            }

    #  pylint: disable=too-many-arguments
    def get_module_related_instance(self, vnf_id, vnf_invariant_id,
                                    vnf_version_id, vnf_model_name,
                                    vnf_custom_id, vnf_custom_name):
        """
            Get module related Instance.
            A module references:
            * an instance
            * a VNF
        """
        return {
            "instanceId": vnf_id,
            "modelInfo": self.get_vnf_model_info(vnf_invariant_id,
                                                 vnf_version_id,
                                                 vnf_model_name,
                                                 vnf_custom_id,
                                                 vnf_custom_name)
            }


# ---------------------------------------------------------------------
# Payloads
# ---------------------------------------------------------------------

    def get_service_payload(self, vnf, request_info, model_info):
        """
            Get SO Service paylod
        """
        return json.dumps({
            "requestDetails": {
                "requestInfo": request_info,
                "modelInfo": model_info,
                "requestParameters": self.get_request_param(vnf, False, True),
                "cloudConfiguration": self.get_cloud_config(),
                "subscriberInfo": self.get_subscriber_info()
            }
        })

    def get_vnf_payload(self, vnf, request_info, vnf_model_info,
                        vnf_related_instance):
        """
            Get SO VNF payload
        """
        return json.dumps({
            "requestDetails": {
                "requestInfo": request_info,
                "modelInfo": vnf_model_info,
                "requestParameters": self.get_request_param(vnf, True, True),
                "relatedInstanceList": [{
                    "relatedInstance": vnf_related_instance
                }],
                "cloudConfiguration": self.get_cloud_config(),
            }
        })

    def get_module_payload(self, vnf, request_info, module_model_info,
                           vnf_related_instance,
                           module_related_instance):
        """
            Get SO Module Instance payload
        """
        return json.dumps({
            "requestDetails": {
                "requestInfo": request_info,
                "modelInfo": module_model_info,
                "requestParameters": self.get_request_param(vnf, False, False),
                "relatedInstanceList": [
                    {"relatedInstance": vnf_related_instance},
                    {"relatedInstance": module_related_instance}],
                "cloudConfiguration": self.get_cloud_config(),
                }
            })

    def create_instance(self, so_service_payload):
        """
            SO create instance
        """
        url = self.so_url + "/ecomp/mso/infra/serviceInstances/v4"
        self.logger.debug("SO request: %s", url)
        try:
            response = requests.post(url, headers=self.so_headers,
                                     proxies=self.proxy, verify=False,
                                     data=so_service_payload)
            self.logger.info("SO create service request: %s",
                             response.text)
            so_instance_id_response = response.json()
            instance_id = (
                so_instance_id_response['requestReferences']['instanceId'])
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error("impossible to perform the request on AAI: %s",
                              str(err))
            instance_id = None
        return instance_id

    def create_vnf(self, instance_id, so_vnf_json_payload):
        """
            SO create vnf
        """
        url = (self.so_url + "/ecomp/mso/infra/serviceInstances/v4/" +
               instance_id + "/vnfs")
        self.logger.debug("SO request: %s", url)
        try:
            response = requests.post(url, headers=self.so_headers,
                                     proxies=self.proxy, verify=False,
                                     data=so_vnf_json_payload)
            vnf_id_response = response.json()
            self.logger.debug("SO create VNF response %s", response.text)
            vnf_id = vnf_id_response['requestReferences']['instanceId']
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error("Impossible to create SO vnf %s", str(err))
            vnf_id = None
        return vnf_id

    def create_module(self, instance_id, vnf_id, so_module_payload):
        """
            SO module instance
        """
        url = (self.so_url + "/ecomp/mso/infra/serviceInstances/v4/" +
               instance_id + "/vnfs/" + vnf_id + "/vfModules")
        self.logger.info("SO create module request: %s", url)
        try:
            response = requests.post(url, headers=self.so_headers,
                                     proxies=self.proxy, verify=False,
                                     data=so_module_payload)
            module_id = response.json()
            # module_id = module_id_response['requestReferences']['instanceId']
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error("Impossible to create SO vnf: %s", err)
            module_id = None
        return module_id

    def delete_instance(self, instance_id, so_service_json_payload):
        """
            Delete SO instance
        """
        delete_instance = False
        self.logger.info("Delete instance %s", instance_id)
        try:
            url = (self.so_url + "/ecomp/mso/infra/serviceInstances/v4/" +
                   instance_id)
            self.logger.debug("SO request: %s", url)
            response = requests.delete(url, headers=self.so_headers,
                                       proxies=self.proxy, verify=False,
                                       data=so_service_json_payload)
            if "202" in response.text:
                delete_instance = True
        except TypeError:
            self.logger.error("Instance ID not defined")
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error("Impossible to delete the instance %s: %s",
                              (instance_id, str(err)))
        return delete_instance

    def delete_vnf(self, instance_id, vnf_id, so_vnf_payload):
        """
            Delete vnf instance
        """
        delete_instance = False
        self.logger.info("Delete vnf %s", vnf_id)
        try:
            url = (self.so_url + "/ecomp/mso/infra/serviceInstances/v4/" +
                   instance_id + "/vnfs/" + vnf_id)
            self.logger.debug("SO request: %s", url)
            response = requests.delete(url, headers=self.so_headers,
                                       proxies=self.proxy, verify=False,
                                       data=so_vnf_payload)
            if "202" in response.text:
                delete_instance = True
        except TypeError:
            self.logger.error("Vnf ID not defined")
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error("Impossible to delete the vnf %s: %s",
                              (vnf_id, str(err)))
        return delete_instance

    def delete_module(self, so_module_payload, instance_id, vnf_id, module_id):
        """
            Delete module instance
        """
        delete_instance = False
        try:
            url = (self.so_url + "/ecomp/mso/infra/serviceInstances/v4/" +
                   instance_id + "/vnfs/" + vnf_id + "/vfModules/" + module_id)

            self.logger.debug("SO request: %s", url)
            response = requests.delete(url, headers=self.so_headers,
                                       proxies=self.proxy, verify=False,
                                       data=so_module_payload)
            if "202" in response.text:
                delete_instance = True
        except TypeError:
            self.logger.error("Vnf ID not defined")
        except Exception as err:  # pylint: disable=broad-except
            self.logger.error("Impossible to delete the vnf %s: %s",
                              (vnf_id, str(err)))
        return delete_instance

    def get_so_request_log(self):
        """
            Get Info on previous request
        """
        url = self.so_url + "/ecomp/mso/infra/orchestrationRequests/v5/"
        self.logger.debug("SO request: %s", url)
        return onap_test_utils.get_simple_request(url,
                                                  self.so_headers,
                                                  self.proxy)
