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
        super().__init__('GENERAL')

    def set_system(self):
        """
        Sets the system attribute based on the system's configuration file
        """
        # TODO: We're being lazy and reading all the configuration file to get just the first section name
        system_config = configparser.ConfigParser()
        system_config.read(self.system_config_file, encoding='utf-8')

        # Config file must begin with system general section
        self.system = system_config.sections()[0]
