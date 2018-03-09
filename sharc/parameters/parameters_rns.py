# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 16:27:43 2017

@author: edgar
"""

import configparser

from sharc.parameters.parameter_handler import ParameterHandler


class ParametersRns(ParameterHandler):
    """
    Simulation parameters for radionavigation service
    """

    def __init__(self):
        super().__init__()

        self.valid_options = {
            "antenna_pattern": ["ITU-R M.1466", "OMNI"],
            "channel_model": ["FSPL", "SatelliteSimple", "P619"],
            "season": ["SUMMER", "WINTER"]
        }

        self.x = 0.0
        self.y = 0.0
        self.altitude = 0.0
        self.frequency = 0.0
        self.bandwidth = 0.0
        self.noise_temperature = 0.0
        self.inr_scaling = 0.0
        self.tx_power_density = 0.0
        self.antenna_gain = 0.0
        self.antenna_pattern = ""
        self.imt_altitude = 0.0
        self.imt_lat_deg = 0.0
        self.channel_model = ""
        self.season = ""
        self.BOLTZMANN_CONSTANT = 1.38064852e-23
        self.EARTH_RADIUS = 6371000.0

    def get_params(self, config: configparser.ConfigParser):

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
