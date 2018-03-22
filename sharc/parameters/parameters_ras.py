# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 17:11:06 2017

@author: Calil
"""

import configparser
from collections import OrderedDict

from sharc.parameters.parameter_handler import ParameterHandler


class ParametersRas(ParameterHandler):
    """
    Simulation parameters for Radio Astronomy Service
    """

    def __init__(self):
        super().__init__()

        self.default_options = \
            OrderedDict([('x', 5000),
                         ('y', 0),
                         ('height', 10),
                         ('elevation', 20),
                         ('azimuth', 180),
                         ('frequency', 43000),
                         ('bandwidth', 1000),
                         ('antenna_noise_temperature', 25),
                         ('receiver_noise_temperature', 65),
                         ('adjacent_ch_selectivity', 20),
                         ('inr_scaling', 1),
                         ('antenna_efficiency', 1),
                         ('antenna_pattern', 'ITU-R SA.509'),
                         ('antenna_gain', 0),
                         ('diameter', 10),
                         ('line_of_sight_prob', 1),
                         ('boltzmann_constant', 1.38064852e-23),
                         ('earth_radius', 6371000),
                         ('speed_of_light', 299792458),
                         ('channel_model', 'P452'),
                         ('atmospheric_pressure', 1013),
                         ('air_temperature', 288),
                         ('water_vapour', 3),
                         ('theta_tx', 20),
                         ('theta_rx', 20),
                         ('n0', 355),
                         ('delta_n', 60),
                         ('percentage_p', 40),
                         ('dlt', 30),
                         ('dlr', 10),
                         ('dct', 10),
                         ('dcr', 10),
                         ('hts', 120),
                         ('hrs', 103),
                         ('hst', 100),
                         ('hsr', 100),
                         ('h0', 20),
                         ('hn', 3),
                         ('hte', 20),
                         ('hre', 3),
                         ('omega', 0),
                         ('phi', 30),
                         ('dtm', 0.8),
                         ('dlm', 0.8),
                         ('epsilon', 3.5),
                         ('hm', 15),
                         ('elevation_angle_facade', 0),
                         ('probability_loss_notexceeded', 0.9),
                         ('thetaj', 0.3),
                         ('par_ep', 0.8),
                         ('clutter_loss', 'true'),
                         ('beta_0', 60)])

        self.valid_options = {
            'antenna_pattern': ['ITU-R SA.509', 'OMNI'],
            'channel_model': ['FSPL', 'TerrestrialSimple', 'P452']

        }

        # Initialize class attributes to the default values
        for key in self.default_options:
            setattr(self, key, self.default_options[key])

    def read_params(self, config_file: str):

        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')

        self.x                          = config.getfloat("RAS", "x")
        self.y                          = config.getfloat("RAS", "y")
        self.height                     = config.getfloat("RAS", "height")
        self.elevation                  = config.getfloat("RAS", "elevation")
        self.azimuth                    = config.getfloat("RAS", "azimuth")
        self.frequency                  = config.getfloat("RAS", "frequency")
        self.bandwidth                  = config.getfloat("RAS", "bandwidth")
        self.antenna_noise_temperature  = config.getfloat("RAS", "antenna_noise_temperature")
        self.receiver_noise_temperature = config.getfloat("RAS", "receiver_noise_temperature")
        self.adjacent_ch_selectivity    = config.getfloat("FSS_ES", "adjacent_ch_selectivity")
        self.inr_scaling                = config.getfloat("RAS", "inr_scaling")
        self.antenna_efficiency         = config.getfloat("RAS", "antenna_efficiency")
        self.antenna_gain               = config.getfloat("RAS", "antenna_gain")
        self.antenna_pattern            = config.get("RAS", "antenna_pattern")
        self.check_param_option('RAS', 'antenna_pattern')
        self.diameter                   = config.getfloat("RAS", "diameter")
        self.channel_model              = config.get("RAS", "channel_model")
        self.check_param_option("RAS", "channel_model")
        self.line_of_sight_prob         = config.getfloat("RAS", "line_of_sight_prob")
        self.BOLTZMANN_CONSTANT         = config.getfloat("RAS", "BOLTZMANN_CONSTANT")
        self.EARTH_RADIUS               = config.getfloat("RAS", "EARTH_RADIUS")
        self.SPEED_OF_LIGHT             = config.getfloat("RAS", "SPEED_OF_LIGHT")

        # P452 parameters
        self.atmospheric_pressure = config.getfloat("RAS", "atmospheric_pressure")
        self.air_temperature = config.getfloat("RAS", "air_temperature")
        self.water_vapour = config.getfloat("RAS", "water_vapour")
        self.theta_tx = config.getfloat("RAS", "theta_tx")
        self.theta_rx = config.getfloat("RAS", "theta_rx")
        self.N0 = config.getfloat("RAS", "N0")
        self.delta_N = config.getfloat("RAS", "delta_N")
        self.percentage_p = config.getfloat("RAS", "percentage_p")
        self.Dlt = config.getfloat("RAS", "Dlt")
        self.Dlr = config.getfloat("RAS", "Dlr")
        self.Dct = config.getfloat("RAS", "Dct")
        self.Dcr = config.getfloat("RAS", "Dcr")
        self.Hts = config.getfloat("RAS", "Hts")
        self.Hrs = config.getfloat("RAS", "Hrs")
        self.Hst = config.getfloat("RAS", "Hst")
        self.Hsr = config.getfloat("RAS", "Hsr")
        self.H0 = config.getfloat("RAS", "H0")
        self.Hn = config.getfloat("RAS", "Hn")
        self.Hte = config.getfloat("RAS", "Hte")
        self.Hre = config.getfloat("RAS", "Hre")
        self.omega = config.getfloat("RAS", "omega")
        self.phi = config.getfloat("RAS", "phi")
        self.dtm = config.getfloat("RAS", "dtm")
        self.dlm = config.getfloat("RAS", "dlm")
        self.epsilon = config.getfloat("RAS", "epsilon")
        self.hm = config.getfloat("RAS", "hm")
        self.elevation_angle_facade = config.getfloat("RAS", "elevation_angle_facade")
        self.probability_loss_notExceeded = config.getfloat("RAS", "probability_loss_notExceeded")
        self.thetaJ = config.getfloat("RAS", "thetaJ")
        self.par_ep = config.getfloat("RAS", "par_ep")
        self.Beta_0 = config.getfloat("RAS", "Beta_0")
        self.clutter_loss = config.getboolean("RAS", "clutter_loss")
