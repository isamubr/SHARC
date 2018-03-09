# -*- coding: utf-8 -*-
"""
Created on Wed May 17 15:47:05 2017

@author: edgar
"""
import configparser
from sharc.parameters.parameter_handler import ParameterHandler


class ParametersHotspot(ParameterHandler):

    def __init__(self):
        super().__init__()
        self.num_hotspots_per_cell = 0
        self.max_dist_hotspot_ue = 0.0
        self.min_dist_bs_hotspot = 0.0
        self.min_dist_hotspots = 0.0

    def get_params(self, config: configparser.ConfigParser):

        self.num_hotspots_per_cell = config.getint("HOTSPOT", "num_hotspots_per_cell")
        self.max_dist_hotspot_ue   = config.getfloat("HOTSPOT", "max_dist_hotspot_ue")
        self.min_dist_bs_hotspot   = config.getfloat("HOTSPOT", "min_dist_bs_hotspot")
        self.min_dist_hotspots     = config.getfloat("HOTSPOT", "min_dist_hotspots")
