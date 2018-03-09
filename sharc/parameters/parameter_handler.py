# -*- coding: utf-8 -*-
"""
Created on Mar 09 12:33 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""

import sys
import configparser
from abc import ABC, abstractmethod

class ParameterHandler(ABC):
    """
    Handle parameter input.
    """

    valid_options = {}

    def __init__(self):
        pass

    def check_param_option(self, section: str, param_name: str):
        """
        Check if a parameter is valid
        :param section: config file section name
        :param param_name: parameter name
        :return: None
        """

        param_val = getattr(self, param_name)

        if param_val not in self.valid_options[param_name]:
            err_msg = "PARAMETER ERROR [{}]: Invalid {} option {}\n" \
                      "Please choose between {}".format(section, param_name, param_val, self.valid_options[param_name])
            sys.stderr.write(err_msg)
            sys.exit(1)

    @abstractmethod
    def get_params(self, config: configparser.ConfigParser):
        """
        Get parameters from configuration
        :param config: configparser object
        :return: None
        """
        pass
