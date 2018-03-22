# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 12:32:30 2017

@author: edgar
"""

import configparser
from collections import OrderedDict

from sharc.parameters.parameter_handler import ParameterHandler


class ParametersHaps(ParameterHandler):
    """
    Simulation parameters for HAPS (airbone) platform.
    """

    def __init__(self):
        super().__init__()

        self.default_options = \
            OrderedDict([('frequency', 27250),
                         ('bandwidth', 200),
                         ('altitude', 20000),
                         ('lat_deg', 0),
                         ('elevation', 270),
                         ('azimuth', 0),
                         ('eirp_density', 4.4),
                         ('inr_scaling', 1),
                         ('antenna_gain', 28.1),
                         ('antenna_pattern', 'ITU-R F.1891'),
                         ('imt_altitude', 0),
                         ('imt_lat_deg', 0),
                         ('imt_long_diff_deg', 0),
                         ('season', 'SUMMER'),
                         ('channel_model', 'P619'),
                         ('antenna_l_n', -25),
                         ('boltzmann_constant', 1.38064852e-23),
                         ('earth_radius', 6371000)])

        self.valid_options = {
            "antenna_pattern": ["ITU-R F.1891", "OMNI"],
            "channel_model": ["FSPL", "SatelliteSimple", "P619"],
            "season": ["SUMMER", "WINTER"]
        }

        # Initialize class attributes to the default values
        for key in self.default_options:
            setattr(self, key, self.default_options[key])

    def read_params(self, config_file):

        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')

        self.frequency = config.getfloat("HAPS", "frequency")
        self.bandwidth = config.getfloat("HAPS", "bandwidth")
        self.antenna_gain = config.getfloat("HAPS", "antenna_gain")
        self.tx_power_density = config.getfloat("HAPS", "eirp_density") - self.antenna_gain - 60
        self.altitude = config.getfloat("HAPS", "altitude")
        self.lat_deg = config.getfloat("HAPS", "lat_deg")
        self.elevation = config.getfloat("HAPS", "elevation")
        self.azimuth = config.getfloat("HAPS", "azimuth")
        self.inr_scaling = config.getfloat("HAPS", "inr_scaling")

        self.antenna_pattern = config.get("HAPS", "antenna_pattern")
        self.check_param_option("HAPS", "antenna_pattern")

        self.imt_altitude = config.getfloat("HAPS", "imt_altitude")
        self.imt_lat_deg = config.getfloat("HAPS", "imt_lat_deg")
        self.imt_long_diff_deg = config.getfloat("HAPS", "imt_long_diff_deg")

        self.channel_model = config.get("HAPS", "channel_model")
        self.check_param_option("HAPS", "channel_model")

        if self.channel_model == "P619":
            self.season = config.get("HAPS", "season")
            self.check_param_option("HAPS", "season")

        self.antenna_l_n = config.getfloat("HAPS", "antenna_l_n")
        self.BOLTZMANN_CONSTANT = config.getfloat("HAPS", "BOLTZMANN_CONSTANT")
        self.EARTH_RADIUS = config.getfloat("HAPS", "EARTH_RADIUS")
