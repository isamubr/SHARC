# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 13:16:02 2017

@author: edgar
"""

import configparser
from collections import OrderedDict
from sharc.parameters.parameter_handler import ParameterHandler


class ParametersFssSs(ParameterHandler):

    def __init__(self):
        super().__init__('FSS_SS')
