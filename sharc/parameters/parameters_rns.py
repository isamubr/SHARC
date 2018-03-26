# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 16:27:43 2017

@author: edgar
"""

import configparser
from collections import OrderedDict

from sharc.parameters.parameter_handler import ParameterHandler


class ParametersRns(ParameterHandler):
    """
    Simulation parameters for radionavigation service
    """

    def __init__(self):
        super().__init__('RNS')

