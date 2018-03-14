# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 16:27:43 2017

@author: edgar
"""

import configparser
from collections import OrderedDict

from sharc.parameters.parameter_handler import ParameterHandler


class ParametersRns(ParameterHandler):
    """
    Simulation parameters for radionavigation service
    """

    def __init__(self):
        super().__init__()

        self.default_options = \
            OrderedDict([('x', '660'),
                         ('y', '-370'),
                         ('altitude', '150'),
                         ('frequency', '32000'),
                         ('bandwidth', '60'),
                         ('noise_temperature', '1154'),
                         ('inr_scaling', '1'),
                         ('tx_power_density', '-70.79'),
                         ('antenna_gain', '30'),
                         ('antenna_pattern', 'ITU-R M.1466'),
                         ('channel_model', 'P619'),
                         ('season', 'SUMMER'),
                         ('imt_altitude', '0'),
                         ('imt_lat_deg', '0'),
                         ('boltzmann_constant', '1.38064852e-23'),
                         ('earth_radius', '6371000')])

        self.valid_options = {
            "antenna_pattern": ["ITU-R M.1466", "OMNI"],
            "channel_model": ["FSPL", "SatelliteSimple", "P619"],
            "season": ["SUMMER", "WINTER"]
        }

        # Initialize class attributes to the default values
        for key in self.default_options:
            setattr(self, key, self.default_options[key])

    def read_params(self, config_file: str):

        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')

        self.x = config.getfloat("RNS", "x")
        self.y = config.getfloat("RNS", "y")
        self.altitude = config.getfloat("RNS", "altitude")
        self.frequency = config.getfloat("RNS", "frequency")
        self.bandwidth = config.getfloat("RNS", "bandwidth")
        self.noise_temperature = config.getfloat("RNS", "noise_temperature")
        self.inr_scaling = config.getfloat("RNS", "inr_scaling")
        self.tx_power_density = config.getfloat("RNS", "tx_power_density")
        self.antenna_gain = config.getfloat("RNS", "antenna_gain")

        self.antenna_pattern = config.get("RNS", "antenna_pattern")
        self.check_param_option("RNS", "antenna_pattern")

        self.imt_altitude = config.getfloat("RNS", "imt_altitude")
        self.imt_lat_deg = config.getfloat("RNS", "imt_lat_deg")
        self.channel_model = config.get("RNS", "channel_model")
        self.check_param_option("RNS", "channel_model")

        if self.channel_model == "P619":
            self.season = config.get("RNS", "season")
            self.check_param_option("RNS", "season")

        self.BOLTZMANN_CONSTANT = config.getfloat("RNS", "BOLTZMANN_CONSTANT")
        self.EARTH_RADIUS = config.getfloat("RNS", "EARTH_RADIUS")
