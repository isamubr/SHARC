# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 19:35:52 2017

@author: edgar
"""

import configparser

from sharc.parameters.parameter_handler import ParameterHandler


class ParametersFs(ParameterHandler):
    """
    Simulation parameters for Fixed Services
    """

    def __init__(self):
        super().__init__()

        self.valid_options = {
            "antenna_pattern": ["ITU-R F.699", "OMNI"],
            "channel_model": ["FSPL", "TerrestrialSimple"]
        }

        self.x = 0.0
        self.y = 0.0
        self.height = 0.0
        self.elevation = 0.0
        self.azimuth = 0.0
        self.frequency = 0.0
        self.bandwidth = 0.0
        self.noise_temperature = 0.0
        self.tx_power_density = 0.0
        self.inr_scaling = 0.0
        self.antenna_gain = 0.0

        self.antenna_pattern = ""
        self.diameter = 0.0
        self.channel_model = ""
        self.line_of_sight_prob = 0.0
        self.BOLTZMANN_CONSTANT = 1.38064852e-23
        self.EARTH_RADIUS = 6371000.0

    def get_params(self, config: configparser.ConfigParser):

        self.x = config.getfloat("FS", "x")
        self.y = config.getfloat("FS", "y")
        self.height = config.getfloat("FS", "height")
        self.elevation = config.getfloat("FS", "elevation")
        self.azimuth = config.getfloat("FS", "azimuth")
        self.frequency = config.getfloat("FS", "frequency")
        self.bandwidth = config.getfloat("FS", "bandwidth")
        self.noise_temperature = config.getfloat("FS", "noise_temperature")
        self.tx_power_density = config.getfloat("FS", "tx_power_density")
        self.inr_scaling = config.getfloat("FS", "inr_scaling")
        self.antenna_gain = config.getfloat("FS", "antenna_gain")

        self.antenna_pattern = config.get("FS", "antenna_pattern")
        self.check_param_option("FS", "antenna_pattern")

        self.diameter = config.getfloat("FS", "diameter")

        self.channel_model = config.get("FS", "channel_model")
        self.check_param_option("FS", "channel_model")

        self.line_of_sight_prob = config.getfloat("FS", "line_of_sight_prob")
        self.BOLTZMANN_CONSTANT = config.getfloat("FS", "BOLTZMANN_CONSTANT")
        self.EARTH_RADIUS = config.getfloat("FS", "EARTH_RADIUS")
