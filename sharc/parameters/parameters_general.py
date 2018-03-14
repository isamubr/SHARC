# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 16:05:46 2017

@author: edgar
"""

import configparser
import sys
import os

from sharc.parameters.parameter_handler import ParameterHandler


class ParametersGeneral(ParameterHandler):

    def __init__(self):
        super().__init__()

        self.valid_options = {
            "imt_link": ["DOWNLINK", "UPLINK"],
            "system": ["FSS_SS", "FSS_ES", "FS", "HAPS", "RNS"]
        }
        self.mandatory_options = {
            "num_snapshots",
            "imt_link",
            "imt_config_file",
            "system_config_file"
        }

        self.num_snapshots = 0
        self.imt_link = ""
        self.system = ""
        self.imt_config_file = ""
        self.system_config_file = ""

    def read_params(self, config_file: str):

        config_general = configparser.ConfigParser()
        config_general.read(config_file, encoding='utf-8')

        config_options = set(config_general.options("GENERAL"))
        if not self.mandatory_options.issubset(config_options):
            err_msg = "PARAMETER ERROR [GENERAL]: " \
                      "Mandatory option(s) {} not set!\n".format(self.mandatory_options - config_options)
            sys.stderr.write(err_msg)
            sys.exit(1)

        self.num_snapshots = config_general.getint("GENERAL", "num_snapshots")

        self.imt_link = config_general.get("GENERAL", "imt_link")
        self.check_param_option("GENERAL", "imt_link")

        if config_general.has_option("GENERAL", "imt_config_file"):
            self.imt_config_file = config_general.get("GENERAL", "imt_config_file")
            if not os.path.exists(self.imt_config_file):
                err_msg = "PARAMETER ERROR [GENERAL]: " \
                          "Configuration file {} does not exist!\n".format(self.imt_config_file)
                sys.stderr.write(err_msg)
                sys.exit(1)
        else:
            err_msg = "PARAMETER ERROR [GENERAL]: IMT configuration file parameter [imt_config_file] not set in the" \
                      "general section!\n"
            sys.stderr.write(err_msg)
            sys.exit(1)

        if config_general.has_option("GENERAL", "system_config_file"):
            self.system_config_file = config_general.get("GENERAL", "system_config_file")
            if not os.path.exists(self.system_config_file):
                err_msg = "PARAMETER ERROR [GENERAL]: " \
                          "Configuration file {} does not exist!\n".format(self.system_config_file)
                sys.stderr.write(err_msg)
                sys.exit(1)
            self.set_system()
        else:
            err_msg = "PARAMETER ERROR [GENERAL]: System configuration file parameter [system_config_file] not set " \
                      "in the general section!\n"
            sys.stderr.write(err_msg)
            sys.exit(1)

    def set_system(self):
        """
        Sets the system attribute based on the system's configuration file
        """
        # TODO: We're being lazy and reading all the configuration file to get just the first section name
        system_config = configparser.ConfigParser()
        system_config.read(self.system_config_file, encoding='utf-8')

        # Config file must begin with system general section
        self.system = system_config.sections()[0]
        self.check_param_option("GENERAL", "system")
