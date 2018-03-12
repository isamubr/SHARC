# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 19:35:52 2017

@author: edgar
"""

import configparser

from sharc.parameters.parameters_general import ParametersGeneral
from sharc.parameters.parameters_imt import ParametersImt
from sharc.parameters.parameters_hotspot import ParametersHotspot
from sharc.parameters.parameters_indoor import ParametersIndoor
from sharc.parameters.parameters_antenna_imt import ParametersAntennaImt
from sharc.parameters.parameters_fs import ParametersFs
from sharc.parameters.parameters_fss_ss import ParametersFssSs
from sharc.parameters.parameters_fss_es import ParametersFssEs
from sharc.parameters.parameters_haps import ParametersHaps
from sharc.parameters.parameters_rns import ParametersRns


class Parameters(object):
    """
    Reads parameters from input file.
    """

    def __init__(self):
        self.file_name = None

        self.general = ParametersGeneral()
        self.imt = ParametersImt()
        self.antenna_imt = ParametersAntennaImt()
        self.hotspot = ParametersHotspot()
        self.indoor = ParametersIndoor()
        self.fss_ss = None
        self.fss_es = None
        self.fs = None
        self.haps = None
        self.rns = None

    def set_file_name(self, file_name: str):
        self.file_name = file_name

    def read_params(self):
        config_general = configparser.ConfigParser()
        config_general.read(self.file_name, encoding='utf-8')

        #######################################################################
        # GENERAL
        #######################################################################
        self.general.get_params(config_general)

        #######################################################################
        # Read the configuration files for the systems to be studied
        #######################################################################
        config_imt = configparser.ConfigParser()

        config_imt.read(self.general.imt_config_file, encoding='utf-8')

        #######################################################################
        # IMT
        #######################################################################
        self.imt.get_params(config_imt)

        #######################################################################
        # IMT ANTENNA
        #######################################################################

        self.antenna_imt.get_params(config_imt)

        #######################################################################
        # HOTSPOT
        #######################################################################

        self.hotspot.get_params(config_imt)

        #######################################################################
        # INDOOR
        #######################################################################

        self.indoor.get_params(config_imt)

        #######################################################################
        # SYSTEM PARAMETERS
        #######################################################################
        config_system = configparser.ConfigParser()

        config_system.read(self.general.system_config_file, encoding='utf-8')
        self.general.set_system(config_system)

        if self.general.system == "FSS_SS":
            #######################################################################
            # FSS space station
            #######################################################################
            self.fss_ss = ParametersFssSs()
            self.fss_ss.get_params(config_system)

        elif self.general.system == "FSS_ES":
            #######################################################################
            # FSS earth station
            #######################################################################
            self.fss_es = ParametersFssEs()
            self.fss_es.get_params(config_system)

        elif self.general.system == "FS":
            #######################################################################
            # Fixed wireless service
            #######################################################################
            self.fs = ParametersFs()
            self.fs.get_params(config_system)

        elif self.general.system == "HAPS":
            #######################################################################
            # HAPS (airbone) station
            #######################################################################
            self.haps = ParametersHaps()
            self.haps.get_params(config_system)

        elif self.general.system == "RNS":
            #######################################################################
            # RNS
            #######################################################################
            self.rns = ParametersRns()
            self.rns.get_params(config_system)
