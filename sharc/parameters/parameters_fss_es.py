# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 15:30:49 2017

@author: edgar
"""

import configparser

from sharc.parameters.parameter_handler import ParameterHandler


class ParametersFssEs(ParameterHandler):
    """
    Simulation parameters for FSS Earth Station.
    """

    def __init__(self):
        super().__init__()

        self.valid_options = {
            "antenna_pattern": ["ITU-R S.1855", "ITU-R S.465", "ITU-R S.580", "OMNI"],
            "channel_model": ["FSPL", "TerrestrialSimple"],
        }

        self.x = 0.0
        self.y = 0.0
        self.height = 0.0
        self.elevation = 0.0
        self.azimuth = 0.0
        self.frequency = 0.0
        self.bandwidth = 0.0
        self.tx_power_density = 0.0
        self.noise_temperature = 0.0
        self.inr_scaling = 0.0
        self.antenna_gain = 0.0

        self.antenna_pattern = ""
        self.diameter = 0.0
        self.channel_model = ""
        self.line_of_sight_prob = 0.0
        self.BOLTZMANN_CONSTANT = 1.38064852e-23
        self.EARTH_RADIUS = 6371000.0

    def get_params(self, config: configparser.ConfigParser):

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
