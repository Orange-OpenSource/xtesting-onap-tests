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
import time

import onap_tests.components.aai as aai
import onap_tests.components.so as so
import onap_tests.components.sdnc as sdnc
import onap_tests.utils.stack_checker as sc
import onap_tests.utils.utils as onap_utils

PROXY = onap_utils.get_config("general.proxy")
LOG_LEVEL = onap_utils.get_config("general.log.log_level")
logging.basicConfig()
LOGGER = logging.getLogger(__name__)
logging.getLogger().setLevel(LOG_LEVEL)


class Vnf(object):
    """
    VNF: Class to automate the instantiation of a VNF
    It is assumed that the Design phase has been already done
    The yaml template is available and stored in the template directory
    TODO: automate the design phase
    """
    def __init__(self, **kwargs):
        """Initialize Vnf object."""
        super(Vnf, self).__init__()
        self.vnf_config = {}
        if "case" not in kwargs:
            # by convention is VNF is not precised we set mrf
            kwargs["case"] = "mrf"

        self.vnf_config["vnf"] = kwargs["case"]

        # can be useful to destroy resources, sdnc module name shall be given
        if "sdnc_vnf_name" in kwargs:
            self.vnf_config["sdnc_vnf_name"] = kwargs["sdnc_vnf_name"]
            # Random part = 6 last char of the the vnf name
            self.vnf_config["random_string"] = kwargs["sdnc_vnf_name"][-6:]
        else:
            self.vnf_config["random_string"] = (
                onap_utils.random_string_generator())
            self.vnf_config["sdnc_vnf_name"] = (
                onap_utils.get_config("onap.service.name") + "_" +
                kwargs["case"] + "_" + self.vnf_config["random_string"])

        self.set_service_instance_var()
        self.set_vnf_var()
        self.set_module_var()
        self.set_onap_components()

    def set_service_instance_var(self):
        """
        set service instance variables from the config file
        """
        self.vnf_config["vnf_name"] = onap_utils.get_template_param(
            self.vnf_config["vnf"], "metadata.name")
        self.vnf_config["invariant_uuid"] = onap_utils.get_template_param(
            self.vnf_config["vnf"], "metadata.invariantUUID")
        self.vnf_config["uuid"] = onap_utils.get_template_param(
            self.vnf_config["vnf"], "metadata.UUID")

    def set_vnf_var(self):
        """
        set vnf variables from the config file
        """
        self.vnf_config["vnf_customization_name"] = list(
            onap_utils.get_template_param(
                self.vnf_config["vnf"],
                "topology_template.node_templates"))[0]
        self.vnf_config["vnf_model_name"] = onap_utils.get_template_param(
            self.vnf_config["vnf"], "topology_template.node_templates." +
            self.vnf_config["vnf_customization_name"] + ".metadata.name")
        self.vnf_config["vnf_invariant_id"] = onap_utils.get_template_param(
            self.vnf_config["vnf"], "topology_template.node_templates." +
            self.vnf_config["vnf_customization_name"] +
            ".metadata.invariantUUID")
        self.vnf_config["vnf_version_id"] = onap_utils.get_template_param(
            self.vnf_config["vnf"], "topology_template.node_templates." +
            self.vnf_config["vnf_customization_name"] + ".metadata.UUID")
        self.vnf_config["vnf_customization_id"] = (
            onap_utils.get_template_param(
                self.vnf_config["vnf"], "topology_template.node_templates." +
                self.vnf_config["vnf_customization_name"] +
                ".metadata.customizationUUID"))
        self.vnf_config["vnf_type"] = list(onap_utils.get_template_param(
            self.vnf_config["vnf"], "topology_template.groups"))[0]
        self.vnf_config["vnf_generic_name"] = (
            self.vnf_config["vnf_name"] + "-service-instance-" +
            self.vnf_config["random_string"])
        self.vnf_config["vnf_generic_type"] = (
            self.vnf_config["vnf_name"] + "/" +
            self.vnf_config["vnf_customization_name"])

    def set_module_var(self):
        """
        set module variables from the config file
        """
        self.vnf_config["sdnc_vnf_type"] = onap_utils.get_template_param(
            self.vnf_config["vnf"], "topology_template.groups." +
            self.vnf_config["vnf_type"] + ".metadata.vfModuleModelName")
        vnf_param = self.vnf_config["vnf"] + ".vnf_parameters"
        self.vnf_config["vnf_parameters"] = onap_utils.get_config(vnf_param)

        self.vnf_config["module_invariant_id"] = onap_utils.get_template_param(
            self.vnf_config["vnf"], "topology_template.groups." +
            self.vnf_config["vnf_type"] +
            ".metadata.vfModuleModelInvariantUUID")
        self.vnf_config["module_name_version_id"] = (
            onap_utils.get_template_param(
                self.vnf_config["vnf"], "topology_template.groups." +
                self.vnf_config["vnf_type"] +
                ".metadata.vfModuleModelUUID"))
        self.vnf_config["module_customization_id"] = (
            onap_utils.get_template_param(
                self.vnf_config["vnf"], "topology_template.groups." +
                self.vnf_config["vnf_type"] +
                ".metadata.vfModuleModelCustomizationUUID"))
        self.vnf_config["module_version_id"] = onap_utils.get_template_param(
            self.vnf_config["vnf"], "topology_template.groups." +
            self.vnf_config["vnf_type"] +
            ".metadata.vfModuleModelUUID")

    def set_onap_components(self):
        """
        Set ONAP component objects
        """
        self.my_aai = aai.Aai(PROXY, LOGGER)
        self.my_so = so.So(PROXY, LOGGER)
        self.my_sdnc = sdnc.Sdnc(PROXY, LOGGER)

    def instantiate(self):
        """
        Instantiate a VNF with ONAP
          * Create the service instance (SO)
          * Create the VNF instance (SO)
          * preload the VNF in the SDNC
          * Create the VF module instance (SO)
        """
        instance_info = {"instance_id": ""}
        vnf_info = {"vnf_id": ""}
        module_info = {}
        module_ref = {"instanceId": ""}
        module_ok = False
        check_vnf = False
        LOGGER.info("Start the instantiation of the VNF")
        instance_info = self.create_service_instance()
        service_ok = self.my_aai.check_service_instance(
            self.vnf_config["vnf_name"],
            instance_info["instance_id"])
        if service_ok:
            vnf_info = self.create_vnf_instance(instance_info)
            vnf_ok = self.my_aai.check_vnf_instance(vnf_info["vnf_id"])
            if vnf_ok:
                self.preload(instance_info["instance_id"])
                time.sleep(10)
                module_info = self.create_module_instance(instance_info,
                                                          vnf_info)
                module_ref = module_info["module_id"]["requestReferences"]
                module_ok = self.my_aai.check_module_instance(
                    vnf_info["vnf_id"],
                    module_ref["instanceId"])
                check_vnf = self.check_vnf(
                    self.vnf_config["vnf"] + "-vfmodule-instance-" +
                    self.vnf_config['random_string'])
                if check_vnf:
                    LOGGER.info("Stack successfully checked")
        return {"status": module_ok,
                "instance_id": instance_info["instance_id"],
                "vnf_id": vnf_info["vnf_id"],
                "module_id": module_ref["instanceId"],
                "preload_id": (self.vnf_config["vnf"] + "-vfmodule-instance-" +
                               self.vnf_config['random_string']),
                "check_heat": check_vnf}

    def clean(self, instance_id, vnf_id, module_id):
        """
        Clean VNF from ONAP

         Args:
            instance_id: The ID of the VNF service instance
            vnf_id: The ID of the VNF instance
            module_id: The ID of the VF module instance
        """
        clean_service_ok = False
        self.clean_module(instance_id, vnf_id, module_id)
        clean_module_ok = self.my_aai.check_module_cleaned(vnf_id,
                                                           module_id)
        if clean_module_ok:
            self.clean_vnf(instance_id, vnf_id)
            clean_vnf_ok = self.my_aai.check_vnf_cleaned(vnf_id)
            if clean_vnf_ok:
                self.clean_instance(instance_id)
                clean_service_ok = self.my_aai.check_service_instance_cleaned(
                    self.vnf_config["vnf_name"], instance_id)
        time.sleep(10)
        if clean_service_ok:
            self.clean_preload()
        return clean_service_ok

    def create_service_instance(self):
        """
        Create service instance
        """
        instance_id = None
        LOGGER.info("1) Create Service instance in SO")
        LOGGER.info("********************************")
        request_info = self.my_so.get_request_info(
            self.vnf_config["vnf"] + "-service-instance-" +
            self.vnf_config['random_string'])
        model_info = self.my_so.get_service_model_info(
            self.vnf_config['invariant_uuid'], self.vnf_config['uuid'])
        service_payload = self.my_so.get_service_payload(
            self.vnf_config["vnf"],
            request_info,
            model_info)
        instance_id = self.my_so.create_instance(service_payload)
        service_instance_info = {"instance_id": instance_id,
                                 "request_info": request_info,
                                 "service_payload": service_payload}
        LOGGER.info("Service instance created: %s", service_instance_info)
        return service_instance_info

    def create_vnf_instance(self, instance_info):
        """
        Create VNF instance

        Args:
          * instance_info: dict including the instance_id, the request_info and
          the service payload
        """
        vnf_id = None
        LOGGER.info("2) Create VNF instance in SO")
        LOGGER.info("****************************")

        model_info = self.my_so.get_vnf_model_info(
            self.vnf_config['vnf_invariant_id'],
            self.vnf_config['vnf_version_id'],
            self.vnf_config['vnf_model_name'],
            self.vnf_config['vnf_customization_id'],
            self.vnf_config['vnf_customization_name'])

        vnf_related_instance = self.my_so.get_vnf_related_instance(
            instance_info["instance_id"],
            self.vnf_config['invariant_uuid'],
            self.vnf_config['uuid'])

        request_info = self.my_so.get_request_info(
            self.vnf_config["vnf"] + "-vnf-instance-" +
            self.vnf_config['random_string'])

        vnf_payload = self.my_so.get_vnf_payload(self.vnf_config["vnf"],
                                                 request_info,
                                                 model_info,
                                                 vnf_related_instance)
        # LOGGER.debug("VNF payload: %s", vnf_payload)
        vnf_id = self.my_so.create_vnf(instance_info["instance_id"],
                                       vnf_payload)
        vnf_info = {"vnf_id": vnf_id,
                    "vnf_payload": vnf_payload,
                    "vnf_related_instance": vnf_related_instance}
        LOGGER.info("SO vnf instance created %s", vnf_info)
        return vnf_info

    def preload(self, instance_id):
        """
        Preload VNF in SDNC

        Args:
          * instance_id: the service instance ID
        """
        LOGGER.info("3) Preload VNF in SDNC")
        LOGGER.info("***********************")
        vnf_topology_identifier = {
            "generic-vnf-name": (self.vnf_config["vnf"] + "-vnf-instance-" +
                                 self.vnf_config['random_string']),
            "generic-vnf-type": self.vnf_config['vnf_generic_type'],
            "service-type": instance_id,
            "vnf-name": (self.vnf_config["vnf"] + "-vfmodule-instance-" +
                         self.vnf_config['random_string']),
            "vnf-type": self.vnf_config['sdnc_vnf_type']}
        sdnc_payload = self.my_sdnc.get_preload_payload(
            self.vnf_config['vnf_parameters'],
            vnf_topology_identifier)
        LOGGER.info("SDNC preloadpayload %s", sdnc_payload)
        sdnc_preload = self.my_sdnc.preload(sdnc_payload)
        LOGGER.debug("SDNC preload answer: %s", sdnc_preload)
        return {"vnf_name": self.vnf_config['sdnc_vnf_name'],
                "vnf-type": self.vnf_config['sdnc_vnf_type'],
                "sdnc_preload": sdnc_preload}

    def create_module_instance(self, instance_info, vnf_info):
        """
        Create module instance

        Args:
          * instance_info: dict including the instance_id, the request_info and
          the service payload
          * vnf_info: dict including the vnf_id, vnf_related_instance and the
          vnf payload
        """
        LOGGER.info("4) Create MODULE instance in SO")
        LOGGER.info("*******************************")

        module_model_info = self.my_so.get_module_model_info(
            self.vnf_config['module_invariant_id'],
            self.vnf_config['module_name_version_id'],
            self.vnf_config['sdnc_vnf_type'],
            self.vnf_config['module_customization_id'],
            self.vnf_config['module_version_id'])
        module_related_instance = self.my_so.get_module_related_instance(
            vnf_info["vnf_id"],
            self.vnf_config['vnf_invariant_id'],
            self.vnf_config['vnf_version_id'],
            self.vnf_config['vnf_model_name'],
            self.vnf_config['vnf_customization_id'],
            self.vnf_config['vnf_customization_name'])

        request_info = self.my_so.get_request_info(
            self.vnf_config["vnf"] + "-vfmodule-instance-" +
            self.vnf_config['random_string'])

        module_payload = self.my_so.get_module_payload(
            self.vnf_config["vnf"],
            request_info,
            module_model_info,
            vnf_info["vnf_related_instance"],
            module_related_instance)

        LOGGER.debug("Module payload %s", module_payload)
        module_instance = self.my_so.create_module(
            instance_info["instance_id"],
            vnf_info["vnf_id"],
            module_payload)
        LOGGER.info("Module instance created %s", module_instance)
        return {"module_id": module_instance,
                "module_payload": module_payload}

    @staticmethod
    def check_vnf(stack_name):
        """
        Check VNF stack has been properly started
        """
        check_vnf = False
        try:
            my_stack_checker = sc.StackChecker()
            if my_stack_checker.check_stack_is_complete(stack_name):
                check_vnf = True
        except Exception:  # pylint: disable=broad-except
            LOGGER.error("Impossible to find the stack %s in OpenStack",
                         stack_name)
        return check_vnf

    def clean_instance(self, instance_id):
        """
        Clean VNF instance

        Args:
          * instance_id: The service instance of the VNF
        """
        LOGGER.info(" Clean Service Instance ")
        service_payload = self.my_so.get_service_payload(
            self.vnf_config["vnf"],
            self.my_so.get_request_info(self.vnf_config['sdnc_vnf_name']),
            self.my_so.get_service_model_info(
                self.vnf_config['invariant_uuid'],
                self.vnf_config['uuid']))
        self.my_so.delete_instance(instance_id,
                                   service_payload)

    def clean_vnf(self, instance_id, vnf_id):
        """
        Clean  VNF

        Args:
          * instance_id: The service instance of the VNF
          * vnf_id:The VNF id of the VNF
        """
        LOGGER.info(" Clean vnf Instance ")
        vnf_payload = self.my_so.get_vnf_payload(
            self.vnf_config["vnf"],
            self.my_so.get_request_info(self.vnf_config['sdnc_vnf_name']),
            self.my_so.get_vnf_model_info(
                self.vnf_config['vnf_invariant_id'],
                self.vnf_config['vnf_version_id'],
                self.vnf_config['vnf_model_name'],
                self.vnf_config['vnf_customization_id'],
                self.vnf_config['vnf_customization_name']),
            self.my_so.get_vnf_related_instance(
                instance_id,
                self.vnf_config['invariant_uuid'],
                self.vnf_config['uuid']))
        self.my_so.delete_vnf(instance_id,
                              vnf_id,
                              vnf_payload)

    def clean_module(self, instance_id, vnf_id, module_id):
        """
        Clean VNF Module

        Args:
          * instance_id: The service instance id of the VNF
          * vnf_id:The VNF id of the VNF
          * module_id: the VF module id of the VNF
        """
        LOGGER.info(" Clean Module Instance ")

        module_payload = self.my_so.get_module_payload(
            self.vnf_config["vnf"],
            self.my_so.get_request_info(self.vnf_config["vnf"] +
                                        "-vfmodule-instance-" +
                                        self.vnf_config['random_string']),
            self.my_so.get_module_model_info(
                self.vnf_config['module_invariant_id'],
                self.vnf_config['module_name_version_id'],
                self.vnf_config['sdnc_vnf_type'],
                self.vnf_config['module_customization_id'],
                self.vnf_config['module_version_id']),
            self.my_so.get_vnf_related_instance(
                instance_id,
                self.vnf_config['invariant_uuid'],
                self.vnf_config['uuid']),
            self.my_so.get_module_related_instance(
                vnf_id,
                self.vnf_config['vnf_invariant_id'],
                self.vnf_config['vnf_version_id'],
                self.vnf_config['vnf_model_name'],
                self.vnf_config['vnf_customization_id'],
                self.vnf_config['vnf_customization_name']))

        self.my_so.delete_module(module_payload,
                                 instance_id,
                                 vnf_id,
                                 module_id)

    def clean_preload(self):
        """
        Clean VNF SDNC preload
        """
        LOGGER.info(" Clean Preload ")
        return self.my_sdnc.delete_preload(
            self.vnf_config["vnf"] + "-vfmodule-instance-" +
            self.vnf_config['random_string'],
            self.vnf_config['sdnc_vnf_type'])

    def get_info(self):
        """
        Get VNFs Info
        """
        LOGGER.info("Class to manage VNFs")
        LOGGER.info("VNF type: %s", self.vnf_config['vnf_type'])
        LOGGER.info("VNF config: %s", self.vnf_config)
