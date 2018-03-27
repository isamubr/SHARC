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
        super().__init__('HOTSPOT')
