# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 13:16:02 2017

@author: edgar
"""

import configparser
from collections import OrderedDict
from sharc.parameters.parameter_handler import ParameterHandler


class ParametersFssSs(ParameterHandler):

    def __init__(self):
        super().__init__()

        self.default_options = \
            OrderedDict([('frequency', 27250),
                         ('bandwidth', 200),
                         ('altitude', 35780000),
                         ('lat_deg', 0),
                         ('elevation', 270),
                         ('azimuth', 0),
                         ('tx_power_density', -5),
                         ('noise_temperature', 950),
                         ('inr_scaling', 14.95),
                         ('antenna_gain', 46.6),
                         ('antenna_pattern', 'FSS_SS'),
                         ('imt_altitude', 0),
                         ('imt_lat_deg', 0),
                         ('imt_long_diff_deg', 0),
                         ('season', 'SUMMER'),
                         ('channel_model', 'FSPL'),
                         ('antenna_l_s', -20),
                         ('antenna_3_db', 0.65),
                         ('boltzmann_constant', 1.38064852e-23),
                         ('earth_radius', 6371000)])

        self.valid_options = {
            "antenna_pattern": ["ITU-R S.672", "ITU-R S.1528", "FSS_SS", "OMNI"],
            "channel_model": ["FSPL", "SatelliteSimple", "P619"],
            "season": ["SUMMER", "WINTER"]
        }

        # Initialize class attributes to the default values
        for key in self.default_options:
            setattr(self, key, self.default_options[key])

    def read_params(self, config_file: str):

        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')

        self.frequency = config.getfloat("FSS_SS", "frequency")
        self.bandwidth = config.getfloat("FSS_SS", "bandwidth")
        self.tx_power_density = config.getfloat("FSS_SS", "tx_power_density")
        self.altitude = config.getfloat("FSS_SS", "altitude")
        self.lat_deg = config.getfloat("FSS_SS", "lat_deg")
        self.elevation = config.getfloat("FSS_SS", "elevation")
        self.azimuth = config.getfloat("FSS_SS", "azimuth")
        self.noise_temperature = config.getfloat("FSS_SS", "noise_temperature")
        self.inr_scaling = config.getfloat("FSS_SS", "inr_scaling")
        self.antenna_gain = config.getfloat("FSS_SS", "antenna_gain")

        self.antenna_pattern = config.get("FSS_SS", "antenna_pattern")
        self.check_param_option("FSS_SS", "antenna_pattern")

        self.imt_altitude = config.getfloat("FSS_SS", "imt_altitude")
        self.imt_lat_deg = config.getfloat("FSS_SS", "imt_lat_deg")
        self.imt_long_diff_deg = config.getfloat("FSS_SS", "imt_long_diff_deg")

        self.channel_model = config.get("FSS_SS", "channel_model")
        self.check_param_option("FSS_SS", "channel_model")

        if self.channel_model == "P619":
            self.season = config.get("FSS_SS", "season")
            self.check_param_option("FSS_SS", "season")

        self.antenna_l_s = config.getfloat("FSS_SS", "antenna_l_s")
        self.antenna_3_dB = config.getfloat("FSS_SS", "antenna_3_dB")
        self.BOLTZMANN_CONSTANT = config.getfloat("FSS_SS", "BOLTZMANN_CONSTANT")
        self.EARTH_RADIUS = config.getfloat("FSS_SS", "EARTH_RADIUS")
