# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 15:30:49 2017

@author: edgar
"""

import configparser
from collections import OrderedDict

from sharc.parameters.parameter_handler import ParameterHandler


class ParametersFssEs(ParameterHandler):
    """
    Simulation parameters for FSS Earth Station.
    """

    def __init__(self):
        super().__init__()

        self.default_options = \
            OrderedDict([('x', 5000),
                         ('y', 0),
                         ('height', 3),
                         ('elevation', 20),
                         ('azimuth', 180),
                         ('frequency', 27250),
                         ('bandwidth', 200),
                         ('noise_temperature', 950),
                         ('inr_scaling', 1),
                         ('tx_power_density', -68.3),
                         ('antenna_gain', 62.8),
                         ('antenna_pattern', 'ITU-R S.465'),
                         ('diameter', 1.8),
                         ('channel_model', 'TerrestrialSimple'),
                         ('line_of_sight_prob', 1),
                         ('boltzmann_constant', 1.38064852e-23),
                         ('earth_radius', 6371000)])

        self.valid_options = {
            "antenna_pattern": ["ITU-R S.1855", "ITU-R S.465", "ITU-R S.580", "OMNI"],
            "channel_model": ["FSPL", "TerrestrialSimple"],
        }

        # Initialize class attributes with default values
        for key in self.default_options:
            setattr(self, key, self.default_options[key])

    def read_params(self, config_file: str):

        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')

        self.x = config.getfloat("FSS_ES", "x")
        self.y = config.getfloat("FSS_ES", "y")
        self.height = config.getfloat("FSS_ES", "height")
        self.elevation = config.getfloat("FSS_ES", "elevation")
        self.azimuth = config.getfloat("FSS_ES", "azimuth")
        self.frequency = config.getfloat("FSS_ES", "frequency")
        self.bandwidth = config.getfloat("FSS_ES", "bandwidth")
        self.tx_power_density = config.getfloat("FSS_ES", "tx_power_density")
        self.noise_temperature = config.getfloat("FSS_ES", "noise_temperature")
        self.inr_scaling = config.getfloat("FSS_ES", "inr_scaling")
        self.antenna_gain = config.getfloat("FSS_ES", "antenna_gain")

        self.antenna_pattern = config.get("FSS_ES", "antenna_pattern")
        self.check_param_option("FSS_ES", "antenna_pattern")

        self.diameter = config.getfloat("FSS_ES", "diameter")

        self.channel_model = config.get("FSS_ES", "channel_model")
        self.check_param_option("FSS_ES", "channel_model")

        self.line_of_sight_prob = config.getfloat("FSS_ES", "line_of_sight_prob")
        self.BOLTZMANN_CONSTANT = config.getfloat("FSS_ES", "BOLTZMANN_CONSTANT")
        self.EARTH_RADIUS = config.getfloat("FSS_ES", "EARTH_RADIUS")
