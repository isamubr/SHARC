# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 12:32:30 2017

@author: edgar
"""

import configparser

from sharc.parameters.parameter_handler import ParameterHandler


class ParametersHaps(ParameterHandler):
    """
    Simulation parameters for HAPS (airbone) platform.
    """

    def __init__(self):
        super().__init__()

        self.valid_options = {
            "antenna_pattern": ["ITU-R F.1891", "OMNI"],
            "channel_model": ["FSPL", "SatelliteSimple", "P619"],
            "season": ["SUMMER", "WINTER"]
        }

        self.frequency = 0.0
        self.bandwidth = 0.0
        self.antenna_gain = 0.0
        self.tx_power_density = 0.0
        self.altitude = 0.0
        self.lat_deg = 0.0
        self.elevation = 0.0
        self.azimuth = 0.0
        self.inr_scaling = 0.0
        self.antenna_pattern = ""
        self.imt_altitude = 0.0
        self.imt_lat_deg = 0.0
        self.imt_long_diff_deg = 0.0
        self.channel_model = ""
        self.season = ""
        self.antenna_l_n = 0.0
        self.BOLTZMANN_CONSTANT = 1.38064852e-23
        self.EARTH_RADIUS = 6371000.0

    def get_params(self, config: configparser.ConfigParser):

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
