#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# pylint: disable=missing-docstring
# pylint: disable=duplicate-code
import logging
import time

import onap_tests.components.aai as aai
import onap_tests.components.so as so
import onap_tests.components.sdnc as sdnc
import onap_tests.components.nbi as nbi
import onap_tests.utils.stack_checker as sc
import onap_tests.utils.utils as onap_utils

PROXY = onap_utils.get_config("general.proxy")


class Solution(object):
    """
    VNF: Class to automate the instantiation of a VNF
    It is assumed that the Design phase has been already done
    The yaml template is available and stored in the template directory
    TODO: automate the design phase
    """
    __logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        """Initialize Solution object."""
        super(Solution, self).__init__()
        self.vnf_config = {}
        self.components = {}
        if "case" not in kwargs:
            # by convention is VNF is not precised we set mrf
            kwargs["case"] = "mrf"
        self.vnf_config["vnf"] = kwargs["case"]
        if "nbi" in kwargs:
            self.vnf_config["nbi"] = kwargs["nbi"]

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

        vnf_list = list(onap_utils.get_template_param(
            self.vnf_config["vnf"],
            "topology_template.node_templates"))
        vf_module_list = list(onap_utils.get_template_param(
            self.vnf_config["vnf"],
            "topology_template.groups"))
        # Class attributes for instance, vnf and module VF
        self.service_infos = {}
        self.vnf_infos = {'list': vnf_list}
        self.module_infos = {'list': vf_module_list}

        # retrieve infos from the configuration files
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
        for i, elt in enumerate(self.vnf_infos['list']):
            vnf_config = {}
            self.__logger.info("get VNF %s info", elt)
            vnf_config["vnf_customization_name"] = elt
            vnf_config["vnf_model_name"] = onap_utils.get_template_param(
                self.vnf_config["vnf"], "topology_template.node_templates." +
                vnf_config["vnf_customization_name"] + ".metadata.name")
            vnf_config["vnf_invariant_id"] = onap_utils.get_template_param(
                self.vnf_config["vnf"], "topology_template.node_templates." +
                vnf_config["vnf_customization_name"] +
                ".metadata.invariantUUID")
            vnf_config["vnf_version_id"] = onap_utils.get_template_param(
                self.vnf_config["vnf"], "topology_template.node_templates." +
                vnf_config["vnf_customization_name"] + ".metadata.UUID")
            vnf_config["vnf_customization_id"] = (
                onap_utils.get_template_param(
                    self.vnf_config["vnf"],
                    "topology_template.node_templates." +
                    vnf_config["vnf_customization_name"] +
                    ".metadata.customizationUUID"))
            vnf_config["vnf_type"] = list(onap_utils.get_template_param(
                self.vnf_config["vnf"], "topology_template.groups"))[i]
            vnf_config["vnf_generic_name"] = (
                self.vnf_config["vnf_name"] + "-service-instance-" +
                self.vnf_config["random_string"])
            vnf_config["vnf_generic_type"] = (
                self.vnf_config["vnf_name"] + "/" +
                vnf_config["vnf_customization_name"])
            self.vnf_config[elt] = vnf_config

    def set_module_var(self):
        """
        set module variables from the config file
        """
        for elt in self.vnf_infos['list']:
            vf_config = {}

            # we cannot be sure that the modules are in teh same order
            # than the vnf
            vf_index = onap_utils.get_vf_module_index(
                self.module_infos['list'],
                elt)
            vnf_type = list(onap_utils.get_template_param(
                self.vnf_config["vnf"],
                "topology_template.groups"))[vf_index]
            self.__logger.info("Complete Module info for VNF %s", elt)
            vf_config["sdnc_vnf_type"] = onap_utils.get_template_param(
                self.vnf_config["vnf"], "topology_template.groups." +
                vnf_type +
                ".metadata.vfModuleModelName")
            vnf_param = (self.vnf_config["vnf"] + "." +
                         str(elt) + ".vnf_parameters")
            vf_config["vnf_parameters"] = onap_utils.get_config(vnf_param)

            vf_config["module_invariant_id"] = onap_utils.get_template_param(
                self.vnf_config["vnf"], "topology_template.groups." +
                vnf_type + ".metadata.vfModuleModelInvariantUUID")
            vf_config["module_name_version_id"] = (
                onap_utils.get_template_param(
                    self.vnf_config["vnf"], "topology_template.groups." +
                    vnf_type + ".metadata.vfModuleModelUUID"))
            vf_config["module_customization_id"] = (
                onap_utils.get_template_param(
                    self.vnf_config["vnf"], "topology_template.groups." +
                    vnf_type + ".metadata.vfModuleModelCustomizationUUID"))
            vf_config["module_version_id"] = onap_utils.get_template_param(
                self.vnf_config["vnf"], "topology_template.groups." +
                vnf_type + ".metadata.vfModuleModelUUID")
            self.vnf_config[elt].update(vf_config)

    def set_onap_components(self):
        """
        Set ONAP component objects
        """
        self.components["aai"] = aai.Aai(PROXY, self.__logger)
        self.components["so"] = so.So(PROXY, self.__logger)
        self.components["sdnc"] = sdnc.Sdnc(PROXY, self.__logger)
        self.components["nbi"] = nbi.Nbi(PROXY, self.__logger)

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
        self.__logger.info("Start the instantiation of the VNF")
        instance_info = self.create_service_instance()
        service_ok = self.components["aai"].check_service_instance(
            self.vnf_config["vnf_name"],
            instance_info["instance_id"])
        if service_ok:
            # create VNF instance(s)
            for elt in self.vnf_infos['list']:
                vnf_info = self.create_vnf_instance(elt)
                self.__logger.info("Check vnf %s ....", elt)
                vnf_ok = True
                self.__logger.info("Check vnf %s ....", elt)
                if not self.components["aai"].check_vnf_instance(
                        vnf_info["vnf_id"]):
                    vnf_ok = False
                    break
                else:
                    # preload VNF(s) in SDNC
                    self.preload(elt)
                time.sleep(10)

            if vnf_ok:
                # create VF module(s)
                for elt in self.vnf_infos['list']:
                    module_info = self.create_module_instance(elt)
                    module_ok = True
                    module_ref = module_info['module_instance']
                    if not self.components["aai"].check_module_instance(
                            vnf_info["vnf_id"],
                            module_ref["requestReferences"]["instanceId"]):
                        module_ok = False
                        break
                    else:
                        # check VNF using OpenStack directly
                        check_vnf = self.check_vnf(
                            self.module_infos[elt]["module_instance_name"])
                        if check_vnf:
                            self.__logger.info("Stack successfully checked")
        return {"status": module_ok,
                "instance_id": instance_info,
                "vnf_info": vnf_info,
                "module_info": module_info,
                "check_heat": check_vnf}

    def clean(self):
        """
        Clean VNF from ONAP

         Args:
            instance_id: The ID of the VNF service instance
            vnf_id: The ID of the VNF instance
            module_id: The ID of the VF module instance
        """
        instance_id = self.service_infos['instance_id']
        for elt in self.vnf_infos['list']:
            vnf_id = self.vnf_infos[elt]["vnf_id"]
            module_id = (self.module_infos[elt]["module_instance"]
                         ["requestReferences"]["instanceId"])
            self.clean_module(elt)
            if not self.components["aai"].check_module_cleaned(vnf_id,
                                                               module_id):
                return False
            else:
                self.clean_vnf(elt)
                if not self.components["aai"].check_vnf_cleaned(vnf_id):
                    return False
                else:
                    self.clean_instance(instance_id)
                    if self.components["aai"].check_service_instance_cleaned(
                            self.vnf_config["vnf_name"], instance_id):
                        self.__logger.debug("Instance still in AAI DB")
                    else:
                        return False
            time.sleep(10)
            self.clean_preload(elt)
        return True

    def create_service_instance(self):
        """
        Create service instance
        2 options to create the instance
          * with SO
          * with NBI
        """
        instance_id = None
        model_info = self.components["so"].get_service_model_info(
            self.vnf_config['invariant_uuid'], self.vnf_config['uuid'])

        if self.vnf_config["nbi"]:
            self.__logger.info("1) Create Service instance from NBI")
            self.__logger.info("***********************************")
            request_info = self.components["nbi"].get_request_info()
            service_payload = (
                self.components["nbi"].get_nbi_service_order_payload())
            nbi_info = self.components["nbi"].create_service_order_nbi(
                service_payload)
            time.sleep(5)
            instance_id = (
                self.components["nbi"].get_service_instance_id_from_order(
                    nbi_info["id"]))
        else:
            self.__logger.info("1) Create Service instance in SO")
            self.__logger.info("********************************")
            request_info = self.components["so"].get_request_info(
                self.vnf_config["vnf"] + "-service-instance-" +
                self.vnf_config['random_string'])
            service_payload = self.components["so"].get_service_payload(
                self.vnf_config["vnf"],
                request_info,
                model_info)
            instance_id = self.components["so"].create_instance(
                service_payload)

        service_instance_info = {"instance_id": instance_id,
                                 "request_info": request_info,
                                 "service_payload": service_payload}
        self.__logger.info("Service instance created: %s",
                           service_instance_info)
        self.service_infos = service_instance_info
        return service_instance_info

    def create_vnf_instance(self, elt):
        """
        Create VNF instance

        Args:
          * elt: the VNF
        """
        vnf_id = None
        self.__logger.info("2) Create VNF instance in SO")
        self.__logger.info("****************************")

        model_info = self.components["so"].get_vnf_model_info(
            self.vnf_config[elt]['vnf_invariant_id'],
            self.vnf_config[elt]['vnf_version_id'],
            self.vnf_config[elt]['vnf_model_name'],
            self.vnf_config[elt]['vnf_customization_id'],
            self.vnf_config[elt]['vnf_customization_name'])

        vnf_related_instance = self.components["so"].get_vnf_related_instance(
            self.service_infos["instance_id"],
            self.vnf_config['invariant_uuid'],
            self.vnf_config['uuid'])

        vnf_instance_name = (self.vnf_config["vnf"] + "-vnf-instance-" +
                             str(elt).replace(" ", "_") + ("_") +
                             self.vnf_config['random_string'])

        request_info = self.components["so"].get_request_info(
            vnf_instance_name)

        vnf_payload = self.components["so"].get_vnf_payload(
            self.vnf_config["vnf"],
            request_info,
            model_info,
            vnf_related_instance)
        # self.__logger.debug("VNF payload: %s", vnf_payload)
        vnf_id = self.components["so"].create_vnf(
            self.service_infos["instance_id"],
            vnf_payload)
        vnf_info = {"vnf_id": vnf_id,
                    "vnf_instance_name": vnf_instance_name,
                    "vnf_payload": vnf_payload,
                    "vnf_related_instance": vnf_related_instance}
        self.__logger.info(">>>> SO vnf instance created %s", vnf_info)
        self.vnf_infos[elt] = vnf_info
        return vnf_info

    def preload(self, elt):
        """
        Preload VNF in SDNC

        Args:
          * elt: the VNF
        """
        vnf_preload_infos = {}
        self.__logger.info("3) Preload VNF %s in SDNC", elt)
        self.__logger.info("*******************************")
        vnf_name = (self.vnf_config["vnf"] +
                        "-vfmodule-instance-" +
                        str(elt).replace(" ", "_") + "_" +
                        self.vnf_config['random_string'])

        vnf_topology_identifier = {
            "generic-vnf-name": vnf_name,
            "generic-vnf-type": (
                self.vnf_config[elt]['vnf_generic_type']),
            "service-type": self.service_infos["instance_id"],
            "vnf-name": vnf_name,
            "vnf-type": self.vnf_config[elt]['sdnc_vnf_type']}

        sdnc_payload = self.components["sdnc"].get_preload_payload(
            self.vnf_config[elt]['vnf_parameters'],
            vnf_topology_identifier)
        self.__logger.info("SDNC preload payload %s", sdnc_payload)
        sdnc_preload = self.components["sdnc"].preload(sdnc_payload)
        self.__logger.debug("SDNC preload answer: %s", sdnc_preload)
        vnf_preload_infos[elt] = ({"sdnc_payload": sdnc_payload,
                                   "sdnc_preload": sdnc_preload})

        return vnf_preload_infos[elt]

    def create_module_instance(self, elt):
        """
        Create module instance

        Args:
          * instance_info: dict including the instance_id, the request_info and
          the service payload
          * vnf_info: dict including the vnf_id, vnf_related_instance and the
          vnf payload
        """
        module_info = {}
        self.__logger.info("4) Create MODULE %s instance in SO", elt)
        self.__logger.info("***************************************")

        module_model_info = self.components["so"].get_module_model_info(
            self.vnf_config[elt]['module_invariant_id'],
            self.vnf_config[elt]['module_name_version_id'],
            self.vnf_config[elt]['sdnc_vnf_type'],
            self.vnf_config[elt]['module_customization_id'],
            self.vnf_config[elt]['module_version_id'])
        module_related_instance = (
            self.components["so"].get_module_related_instance(
                self.vnf_infos[elt]["vnf_id"],
                self.vnf_config[elt]['vnf_invariant_id'],
                self.vnf_config[elt]['vnf_version_id'],
                self.vnf_config[elt]['vnf_model_name'],
                self.vnf_config[elt]['vnf_customization_id'],
                self.vnf_config[elt]['vnf_customization_name']))

        module_instance_name = (self.vnf_config["vnf"] +
                                "-vfmodule-instance-" +
                                str(elt).replace(" ", "_") + "_" +
                                self.vnf_config['random_string'])

        request_info = self.components["so"].get_request_info(
            module_instance_name)

        module_payload = self.components["so"].get_module_payload(
            self.vnf_config["vnf"],
            request_info,
            module_model_info,
            self.vnf_infos[elt]["vnf_related_instance"],
            module_related_instance)

        self.__logger.debug("Module payload %s", module_payload)
        module_instance = self.components["so"].create_module(
            self.service_infos["instance_id"],
            self.vnf_infos[elt]["vnf_id"],
            module_payload)
        self.__logger.info(">>>> Module instance created: %s", module_instance)
        module_info = (
            {'module_instance': module_instance,
             'module_instance_name': module_instance_name,
             'module_payload': module_payload,
             'module_model_info': module_model_info,
             'module_related_instance': module_related_instance})
        self.__logger.info("SO module vf(s) created: %s", module_info)
        self.module_infos[elt] = module_info
        return module_info

    def check_vnf(self, stack_name):
        """
        Check VNF stack has been properly started
        """
        check_vnf = False
        try:
            my_stack_checker = sc.StackChecker()
            if my_stack_checker.check_stack_is_complete(stack_name):
                check_vnf = True
        except Exception:  # pylint: disable=broad-except
            self.__logger.error("Impossible to find the stack %s in OpenStack",
                                stack_name)
        return check_vnf

    def clean_instance(self, instance_id):
        """
        Clean VNF instance

        Args:
          * instance_id: The service instance of the VNF
        """
        self.__logger.info(" Clean Service Instance ")
        service_payload = self.components["so"].get_service_payload(
            self.vnf_config["vnf"],
            self.components["so"].get_request_info(
                self.vnf_config['sdnc_vnf_name']),
            self.components["so"].get_service_model_info(
                self.vnf_config['invariant_uuid'],
                self.vnf_config['uuid']))
        self.components["so"].delete_instance(instance_id, service_payload)

    def clean_vnf(self, elt):
        """
        Clean  VNF

        Args:
          * instance_id: The service instance of the VNF
          * vnf_id:The VNF id of the VNF
        """
        self.__logger.info(" Clean vnf Instance %s ", elt)
        self.components["so"].delete_vnf(
            self.service_infos["instance_id"],
            self.vnf_infos[elt]["vnf_id"],
            self.vnf_infos[elt]["vnf_payload"])

    def clean_module(self, elt):
        """
        Clean VNF Module

        Args:
          * instance_id: The service instance id of the VNF
          * vnf_id:The VNF id of the VNF
          * module_id: the VF module id of the VNF
        """
        self.__logger.info(" Clean Module VF Instance %s ", elt)
        instance_id = self.service_infos["instance_id"]
        vnf_id = self.vnf_infos[elt]["vnf_id"]
        module_id = (self.module_infos[elt]["module_instance"]
                     ["requestReferences"]["instanceId"])
        module_payload = self.module_infos[elt]["module_payload"]
        self.components["so"].delete_module(
            module_payload,
            instance_id,
            vnf_id,
            module_id)

    def clean_preload(self, elt):
        """
        Clean VNF SDNC preload
        """
        self.__logger.info(" Clean Preload of %s ", elt)
        # if 1 of the expected preload clean is FAIL we return False
        clean_preload = self.components["sdnc"].delete_preload(
            self.module_infos[elt]["module_instance_name"],
            self.vnf_config[elt]["sdnc_vnf_type"])
        return clean_preload

    def clean_all_preload(self):
        """
        Clean VNF SDNC preload with the preload id
        """
        self.__logger.info(" Clean Preload ")
        for elt in self.vnf_infos['list']:
            clean_preload = self.components["sdnc"].delete_preload(
                self.module_infos[elt]["module_instance_name"],
                self.vnf_config[elt]['sdnc_vnf_type'])
        return clean_preload

    def get_info(self):
        """
        Get VNFs Info
        """
        self.__logger.info("Class to manage VNFs")
        self.__logger.info("VNF config: %s", self.vnf_config)
