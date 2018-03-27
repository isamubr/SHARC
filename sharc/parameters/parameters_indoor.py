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
        super().__init__('INDOOR')
