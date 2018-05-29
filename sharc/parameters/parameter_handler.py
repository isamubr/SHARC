# -*- coding: utf-8 -*-
"""
Created on Mar 09 12:33 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""

import sys
import os
import json
import configparser
from abc import ABC


class ParameterHandler(ABC):
    """
    Handle parameter input.
    """
    def __init__(self, param_section: str):
        """
        Read the parameters_definitions.json file and construct the parameter object with the default values
        """
        self.param_section = param_section
        self.param_definitions = {}
        param_def_file = os.path.join(os.path.dirname(__file__), 'parameters_definitions.json')
        with open(param_def_file, 'r', encoding='utf-8') as f:
            param = json.load(f)

        if self.param_section not in param.keys():
            err_msg = "PARAMETER ERROR[{}]: Section [{}] is not defined in the " \
                      "parameters_definitions.json file\n".format(self.__class__.__name__, self.param_section)
            sys.stderr.write(err_msg)
            sys.exit(1)

        self.param_definitions[self.param_section] = param[self.param_section].copy()

        # Initialize class attributes with the default values
        for param_name in self.param_definitions[self.param_section].keys():
            setattr(self, param_name, self.param_definitions[self.param_section][param_name]['default_value'])

    def read_params(self, config_file: str):
        """
        Get parameters from configuration file
        :param config_file: configuration file name
        :return: None
        """
        config = configparser.ConfigParser()
        # Prevent from lowercasing all section keys
        config.optionxform = lambda option: option
        try:
            with open(config_file) as f:
                config.read_file(f)
        except IOError:
            err_msg = "PARAMETER ERROR [{}]: Could not find " \
                      "configuration file {}".format(self.__class__.__name__, config_file)
            sys.stderr.write(err_msg)
            sys.exit(1)

        if self.param_section not in config.sections():
            err_msg = "PARAMETER ERROR[{}]: Configuration file \'{}\' does not contain\n" \
                      "the '{}' section".format(self.__class__.__name__, config_file, self.param_section)
            sys.stderr.write(err_msg)
            sys.exit(1)

        for param_name, param_val in config.items(self.param_section):
            if param_name not in self.param_definitions[self.param_section].keys():
                err_msg = "PARAMETER ERROR[{}]: Parameter {} is not defined in the " \
                          "parameters_definitions.json file\n".format(self.__class__.__name__, param_name)
                sys.stderr.write(err_msg)
                sys.exit(1)

            # Check if the parameter is valid
            param_type = self.param_definitions[self.param_section][param_name]['data_type']
            param_options = self.param_definitions[self.param_section][param_name]['param_options']
            if param_type == 'str':
                param_val = config.get(self.param_section, param_name)
                param_options = [opt.lower() for opt in param_options]
                if param_options and param_val.lower() not in param_options:
                    err_msg = "PARAMETER ERROR [{}]: Invalid \'{}\' option \'{}\'\n" \
                              "Please choose between {}\n".format(self.__class__.__name__,
                                                                  param_name,
                                                                  param_val,
                                                                  self.param_definitions[self.param_section]
                                                                                        [param_name]
                                                                                        ['param_options'])
                    sys.stderr.write(err_msg)
                    sys.exit(1)

            elif param_type == 'int':
                param_val = config.getint(self.param_section, param_name)
            elif param_type == 'float':
                param_val = config.getfloat(self.param_section, param_name)
            elif param_type == 'bool':
                param_val = config.getboolean(self.param_section, param_name)
            else:
                err_msg = "PARAMETER ERROR [{}]: Invalid data type for parameter \'{}\'\n" \
                          "Check parameter_definitions.json file\n".format(self.__class__.__name__,
                                                                           param_name)
                sys.stderr.write(err_msg)
                sys.exit(1)

            setattr(self, param_name, param_val)







