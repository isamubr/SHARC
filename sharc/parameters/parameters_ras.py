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
        super().__init__('RAS')
