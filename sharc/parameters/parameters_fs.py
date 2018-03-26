# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 19:35:52 2017

@author: edgar
"""

import configparser

from sharc.parameters.parameter_handler import ParameterHandler


class ParametersFs(ParameterHandler):
    """
    Simulation parameters for Fixed Services
    """

    def __init__(self):
        super().__init__('FS')
