# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 12:32:30 2017

@author: edgar
"""

import configparser
from collections import OrderedDict

from sharc.parameters.parameter_handler import ParameterHandler


class ParametersHaps(ParameterHandler):
    """
    Simulation parameters for HAPS (airbone) platform.
    """

    def __init__(self):
        super().__init__('HAPS')

