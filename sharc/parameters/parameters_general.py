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

        self.num_snapshots = 0
        self.imt_link = ""
        self.system = ""
        self.config_files = []

    def get_params(self, config_general: configparser.ConfigParser):

        self.num_snapshots = config_general.getint("GENERAL", "num_snapshots")

        self.imt_link = config_general.get("GENERAL", "imt_link")
        self.check_param_option("GENERAL", "imt_link")

        self.system = config_general.get("GENERAL", "system")
        self.check_param_option("GENERAL", "system")

        if config_general.has_option("GENERAL", "imt_config_file") and \
                config_general.has_option("GENERAL", 'system_config_file'):

            self.config_files = []
            self.config_files.append(config_general.get("GENERAL", 'imt_config_file'))
            self.config_files.append(config_general.get("GENERAL", 'system_config_file'))
            for path in self.config_files:
                if not os.path.exists(path):
                    err_msg = "PARAMETER ERROR [GENERAL]: Configuration file {} does not exist!".format(path)
                    sys.stderr.write(err_msg)
                    sys.exit(1)
        else:
            err_msg = "PARAMETER ERROR [GENERAL]: Configuration file(s) not set!" \
                      "Please set imt_config_file and system_config_file to a valid" \
                      "configuration file."
            sys.stderr.write(err_msg)
            sys.exit(1)

