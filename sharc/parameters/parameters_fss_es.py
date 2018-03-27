# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 15:30:49 2017

@author: edgar
"""

import configparser
from collections import OrderedDict

from sharc.parameters.parameter_handler import ParameterHandler


class ParametersFssEs(ParameterHandler):
    """
    Simulation parameters for FSS Earth Station.
    """

    def __init__(self):
        super().__init__('FSS_ES')
