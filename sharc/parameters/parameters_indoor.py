# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 17:50:05 2017

@author: edgar
"""
import configparser
from collections import OrderedDict

from sharc.parameters.parameter_handler import ParameterHandler


class ParametersIndoor(ParameterHandler):
    """
    Simulation parameters for indoor network topology.
    """

    def __init__(self):
        super().__init__()

        self.default_values = \
            OrderedDict([('basic_path_loss', 'FSPL'),
                         ('n_rows', 3),
                         ('n_colums', 2),
                         ('street_width', 30),
                         ('ue_indoor_percent', .95),
                         ('building_class', 'TRADITIONAL')])

        self.valid_options = {
            "basic_path_loss": ["FSPL", "INH_OFFICE"],
            "building_class": ["TRADITIONAL", "THERMALLY_EFFICIENT"]
        }

        self.basic_path_loss = ""
        self.n_rows = 0
        self.n_colums = 0
        self.street_width = 0
        self.ue_indoor_percent = 0.0
        self.building_class = ""

    def read_params(self, config_file: str):

        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')

        self.basic_path_loss = config.get("INDOOR", "basic_path_loss")
        self.check_param_option("INDOOR", "basic_path_loss")

        self.n_rows = config.getint("INDOOR", "n_rows")
        self.n_colums = config.getint("INDOOR", "n_colums")
        self.street_width = config.getint("INDOOR", "street_width")
        self.ue_indoor_percent = config.getfloat("INDOOR", "ue_indoor_percent")

        self.building_class = config.get("INDOOR", "building_class")
        self.check_param_option("INDOOR", "building_class")
