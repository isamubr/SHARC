# -*- coding: utf-8 -*-
"""
Created on Wed May 17 15:47:05 2017

@author: edgar
"""
import configparser
from collections import OrderedDict
from sharc.parameters.parameter_handler import ParameterHandler


class ParametersHotspot(ParameterHandler):

    def __init__(self):
        super().__init__()
        self.default_values = OrderedDict([
            ('num_hotspots_per_cell', 1),
            ('max_dist_hotspot_ue', 100),
            ('min_dist_bs_hotspot', 0),
            ('min_dist_hotspots', 200)]
        )

        for key in self.default_values:
            setattr(self, key, self.default_values[key])

    def read_params(self, config_file: str):

        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')

        self.num_hotspots_per_cell = config.getint("HOTSPOT", "num_hotspots_per_cell")
        self.max_dist_hotspot_ue   = config.getfloat("HOTSPOT", "max_dist_hotspot_ue")
        self.min_dist_bs_hotspot   = config.getfloat("HOTSPOT", "min_dist_bs_hotspot")
        self.min_dist_hotspots     = config.getfloat("HOTSPOT", "min_dist_hotspots")
