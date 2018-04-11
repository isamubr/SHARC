# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 16:05:58 2017

@author: edgar
"""

import pandas as pd
import geopandas as gpd
import sys
import os
from glob import glob
import configparser
from sharc.parameters.parameter_handler import ParameterHandler
from collections import OrderedDict


class ParametersImt(ParameterHandler):

    def __init__(self):
        super().__init__('IMT')
